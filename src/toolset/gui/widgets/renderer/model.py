"""Single-model preview widget (OpenGL) for GIT instances in the module designer."""

from __future__ import annotations

import math
import time

from typing import TYPE_CHECKING, Any, cast

import qtpy

from qtpy.QtCore import (
    Signal,  # pyright: ignore[reportPrivateImportUsage]
)

from loggerplus import RobustLogger
from pykotor.gl import vec3
from pykotor.gl.models.read_mdl import gl_load_mdl
from pykotor.gl.scene import RenderObject, Scene
from pykotor.gl.scene.camera_controller import (
    CameraController,
    CameraControllerSettings,
    InputState,
)
from pykotor.resource.formats.twoda import read_2da
from pykotor.resource.generics.git import GIT
from pykotor.resource.type import ResourceType
from toolset.data.misc import ControlItem
from toolset.gui.widgets.renderer.base import OpenGLSceneRenderer
from toolset.gui.widgets.settings.widgets.module_designer import ModuleDesignerSettings
from utility.common.geometry import Vector2
from utility.error_handling import assert_with_variable_trace

if TYPE_CHECKING:
    from qtpy.QtGui import (
        QKeyEvent,
        QMouseEvent,
        QOpenGLContext,
        QResizeEvent,
        QWheelEvent,
    )
    from qtpy.QtWidgets import QWidget

    from pykotor.resource.generics.utc import UTC
    from pykotor.resource.generics.uti import UTI
    from toolset.data.installation import HTInstallation
    from toolset.gui.widgets.renderer.view_compass import ViewCompassWidget


class ModelRenderer(OpenGLSceneRenderer):
    # Signal emitted when textures/models finish loading
    resourcesLoaded = Signal()

    def __init__(self, parent: QWidget):
        from toolset.gui.widgets.settings.widgets.module_designer import (
            get_renderer_loop_interval_ms,
        )  # noqa: PLC0415

        super().__init__(
            parent,
            initial_mouse_prev=Vector2(0, 0),
            loop_interval_ms=get_renderer_loop_interval_ms(),
        )
        self._last_texture_count: int = 0
        self._last_pending_texture_count: int = 0
        self._last_requested_texture_count: int = 0

        self._installation: HTInstallation | None = None  # Use private attribute with property
        self._model_to_load: tuple[bytes, bytes] | None = None
        self._creature_to_load: UTC | None = None
        self._pending_camera_reset: bool = False
        self._view_compass: ViewCompassWidget | None = None
        self._camera_controller: CameraController | None = None
        self._camera_input_state: InputState = InputState()
        self._last_controller_update: float = time.monotonic()

        self._controls = ModelRendererControls()

    def _on_loop_timer_timeout(self) -> None:
        if not self.isVisible() or self.scene is None:
            return
        if self._camera_controller is not None:
            now = time.monotonic()
            delta_time = now - self._last_controller_update
            self._last_controller_update = now
            if self._camera_controller.has_pending_motion():
                self._camera_controller.update(self._camera_input_state, delta_time)
        pending_async_work = bool(
            self.scene._pending_texture_futures
            or self.scene._pending_model_futures
            or self._model_to_load is not None
            or self._creature_to_load is not None
            or self._pending_camera_reset
            or (
                self._camera_controller is not None and self._camera_controller.has_pending_motion()
            )
        )
        if pending_async_work or bool(self._mouse_down) or bool(self._keys_down):
            self.update()

    def _setup_view_compass(self) -> None:
        from toolset.gui.widgets.renderer.view_compass import ViewCompassWidget  # noqa: PLC0415

        scene = self.scene
        if self._view_compass is not None or scene is None:
            return
        self._view_compass = ViewCompassWidget(self)
        self._view_compass.set_camera_source(lambda: (scene.camera.yaw, scene.camera.pitch))
        self._view_compass.sig_snap_view.connect(self._apply_view_snap)

    def _apply_view_snap(self, yaw: float, pitch: float) -> None:
        if self.scene is None:
            return
        if self._camera_controller is not None:
            self._camera_controller.set_rotation(yaw, pitch)
        else:
            self.scene.camera.yaw = yaw
            self.scene.camera.pitch = pitch
        self.update()

    def frame_all(self) -> None:
        focus_state = self._model_focus_state()
        if focus_state is None:
            self.reset_camera()
            return
        center_x, center_y, center_z, distance = focus_state
        if self._camera_controller is not None:
            self._camera_controller.focus_on_point(center_x, center_y, center_z, distance)
            self._camera_controller.set_rotation(math.pi / 16 * 7, math.pi / 16 * 9)
        else:
            self.reset_camera()
        self.update()

    def frame_selected(self) -> None:
        self.frame_all()

    def _model_focus_state(self) -> tuple[float, float, float, float] | None:
        scene = self.scene
        if scene is None or "model" not in scene.objects:
            return None
        model = scene.objects["model"]
        if model.model not in scene.models or model.model in scene._pending_model_futures:
            return None
        cube = model.cube(scene)
        center_x = (cube.min_point.x + cube.max_point.x) / 2.0
        center_y = (cube.min_point.y + cube.max_point.y) / 2.0
        center_z = (cube.min_point.z + cube.max_point.z) / 2.0
        return center_x, center_y, center_z, max(2.0, model.radius(scene) + 2.0)

    @property
    def installation(self) -> HTInstallation | None:
        return self._installation

    @installation.setter
    def installation(self, value: HTInstallation | None):
        self._installation = value
        # If scene already exists, update its installation and load 2DA tables.
        # set_installation() loads appearance.2da etc. that the renderer needs.
        if self.scene is not None and value is not None and self.scene.installation is None:
            self.scene.installation = value
            self.scene.set_installation(value)
            RobustLogger().debug(
                "ModelRenderer.installation setter: Updated existing scene with installation"
            )

    def initializeGL(self):
        # Ensure OpenGL context is current
        self.makeCurrent()

        self.scene = Scene(installation=self._installation)
        self.scene.camera.fov = self._controls.fieldOfView
        self.scene.camera.distance = 0  # Set distance to 0

        self.scene.camera.yaw = math.pi / 2
        self._sync_camera_drawable_size()
        self.scene.show_cursor = False

        self.scene.git = GIT()

        # Standalone model/creature preview has no module - disable frustum culling
        # so objects are always rendered (culling relies on module layout which we don't have)
        if self.scene._module is None:
            self.scene.enable_frustum_culling = False

        self._camera_controller = CameraController(
            self.scene.camera,
            CameraControllerSettings(
                orbit_sensitivity=self._controls.rotateCameraSensitivity3d / 100,
                pan_sensitivity=self._controls.moveCameraSensitivity3d / 100,
                zoom_sensitivity=self._controls.zoomCameraSensitivity3d / 100,
            ),
        )
        self._camera_controller.sync_from_camera()
        self._last_controller_update = time.monotonic()

        self._setup_view_compass()
        self.loop_timer.start()

    def paintGL(self):
        if self.scene is None:
            return

        ctx: QOpenGLContext | None = self.context()
        if ctx is None or not ctx.isValid():
            return

        # Ensure OpenGL context is current before rendering
        self.makeCurrent()
        self._sync_camera_drawable_size()

        if self._model_to_load is not None:
            self.scene.models["model"] = gl_load_mdl(self.scene, *self._model_to_load)
            self.scene.objects["model"] = RenderObject("model")
            # Scene caches object lists; invalidate so new objects are rendered.
            if hasattr(self.scene, "_invalidate_object_cache"):
                self.scene._invalidate_object_cache()  # noqa: SLF001
            self._model_to_load = None
            self.reset_camera()

        elif self._creature_to_load is not None:
            # Use sync=True to force synchronous model loading for the preview renderer
            # This ensures hooks (headhook, rhand, lhand, gogglehook) are found correctly
            self.scene.objects["model"] = self.scene.get_creature_render_object(
                None, self._creature_to_load, sync=True
            )
            # Scene caches object lists; invalidate so swapped render objects take effect.
            self.scene._invalidate_object_cache()  # noqa: SLF001
            self._creature_to_load = None
            # Reset camera immediately since we loaded synchronously
            self.reset_camera()

        # Render first to poll async resources
        # THIS IS WHERE scene.texture() GETS CALLED DURING MESH RENDERING
        self.scene.render()

        # Check if textures/models FINISHED LOADING this frame (not just requested)
        # Only emit signal when textures are ACTUALLY LOADED - not when they're first requested
        texture_lookup_info: dict[str, dict[str, Any]] = self.scene.texture_lookup_info
        requested_texture_names_obj: set[str] = self.scene.requested_texture_names
        requested_texture_names: set[str] = cast("set[str]", requested_texture_names_obj)
        current_texture_count = len(texture_lookup_info)
        pending_textures = self.scene._pending_texture_futures
        current_pending_count = len(pending_textures)
        previous_pending_count = self._last_pending_texture_count or current_pending_count
        current_requested_count = len(requested_texture_names)

        # ONLY emit signal when textures FINISH loading:
        # 1. texture_lookup_info count increased (new textures have lookup info stored)
        # 2. OR pending count decreased (async loads completed)
        # DO NOT emit just because requested count increased - that means textures are still loading!
        textures_finished_loading = current_texture_count > self._last_texture_count or (
            current_pending_count < previous_pending_count and previous_pending_count > 0
        )

        if textures_finished_loading:
            self._last_texture_count = current_texture_count
            self._last_pending_texture_count = current_pending_count
            self._last_requested_texture_count = current_requested_count
            RobustLogger().debug(
                f"Textures FINISHED loading: lookup_info={current_texture_count}, pending={current_pending_count}, requested={current_requested_count} (names: {sorted(requested_texture_names)})",
            )
            self.resourcesLoaded.emit()
        else:
            # Track changes without emitting signal
            if current_pending_count != previous_pending_count:
                self._last_pending_texture_count = current_pending_count
            if current_requested_count != self._last_requested_texture_count:
                self._last_requested_texture_count = current_requested_count

        # After rendering, check if we need to reset camera and if model is ready
        if self._pending_camera_reset and "model" in self.scene.objects:
            model_obj: RenderObject = self.scene.objects["model"]
            # Check if the model (and all its child models) have finished loading
            model_ready = self._is_model_ready(model_obj)
            if model_ready:
                self.reset_camera()
                self._pending_camera_reset = False

    def shutdown_renderer(self):
        super().shutdown_renderer()
        if self.scene is not None:
            del self.scene

    def clear_model(self):
        if self.scene is not None and "model" in self.scene.objects:
            del self.scene.objects["model"]
            # Scene caches object lists; invalidate so removals take effect.
            if hasattr(self.scene, "_invalidate_object_cache"):
                self.scene._invalidate_object_cache()  # noqa: SLF001
        if hasattr(self, "_pending_camera_reset"):
            self._pending_camera_reset = False
        if self._camera_controller is not None:
            self._camera_controller.sync_from_camera()

    def set_model(
        self,
        data: bytes,
        data_ext: bytes,
    ):
        self._model_to_load = (data[12:], data_ext)

    def set_creature(self, utc: UTC):
        self._creature_to_load = utc

    def set_item(self, uti: UTI) -> None:
        """Load and display the item's model from baseitems.2da ModelName (for UTI editor preview)."""
        if self._installation is None:
            return
        baseitems = None
        ht_get = self._installation.ht_get_cache_2da
        if ht_get is not None:
            baseitems = ht_get(self._installation.TwoDA_BASEITEMS)
        else:
            res = self._installation.resource("baseitems", ResourceType.TwoDA)
            if res is not None and res.data is not None:
                baseitems = read_2da(res.data)
        if baseitems is None or uti.base_item < 0 or uti.base_item >= baseitems.get_height():
            return
        row = baseitems.get_row(uti.base_item)
        model_name = row.get_string("ModelName") if row else None
        if not model_name or not model_name.strip():
            return
        mdl_res = self._installation.resource(model_name.strip(), ResourceType.MDL)
        mdx_res = self._installation.resource(model_name.strip(), ResourceType.MDX)
        if mdl_res is None or mdl_res.data is None:
            return
        mdl_bytes = mdl_res.data
        mdx_bytes = mdx_res.data if mdx_res is not None and mdx_res.data is not None else b""
        self.set_model(mdl_bytes, mdx_bytes)

    def _is_model_ready(self, obj: RenderObject) -> bool:
        """Check if a RenderObject's model and all child models have finished loading."""
        scene = self.scene
        assert scene is not None, assert_with_variable_trace(scene is not None)
        # Check if this model is still loading
        if obj.model in scene._pending_model_futures:
            return False
        # Check if the model exists and is not the empty placeholder
        if obj.model not in scene.models:
            return False
        # Check all child models
        for child in obj.children:
            if not self._is_model_ready(child):
                return False
        return True

    def reset_camera(self):
        scene: Scene | None = self.scene
        assert scene is not None, assert_with_variable_trace(scene is not None)
        if "model" in scene.objects:
            model: RenderObject = scene.objects["model"]
            # Only reset camera if model is actually loaded (not empty placeholder)
            if model.model in scene.models and model.model not in scene._pending_model_futures:
                scene.camera.x = 0
                scene.camera.y = 0
                scene.camera.z = (model.cube(scene).max_point.z - model.cube(scene).min_point.z) / 2
                scene.camera.pitch = math.pi / 16 * 9
                scene.camera.yaw = math.pi / 16 * 7
                scene.camera.distance = model.radius(scene) + 2
                if self._camera_controller is not None:
                    self._camera_controller.sync_from_camera()

    def apply_render_overrides(
        self,
        *,
        field_of_view: float | None = None,
        show_cursor: bool | None = None,
    ):
        """Apply render/view overrides for parity with module renderer APIs."""
        if self.scene is None:
            return
        if field_of_view is not None:
            self.scene.camera.fov = field_of_view
        if show_cursor is not None:
            self.scene.show_cursor = show_cursor
        self.update()

    # snap_camera_to_point, pan_camera, move_camera, rotate_camera, zoom_camera,
    # do_cursor_lock, reset_all_down are all inherited from OpenGLSceneRenderer.

    # region Events
    def resizeEvent(self, e: QResizeEvent):  # pyright: ignore[reportIncompatibleMethodOverride]
        super().resizeEvent(e)

        if self.scene is not None:
            self._sync_camera_drawable_size()

    def wheelEvent(self, e: QWheelEvent):  # pyright: ignore[reportIncompatibleMethodOverride]
        scene = self.scene
        if scene is None:
            return
        if self._controls.moveZCameraControl.satisfied(self._mouse_down, self._keys_down):
            # Ctrl+wheel (default) vertical camera move was far too sensitive; reduce by 5x.
            strength: float = self._controls.moveCameraSensitivity3d / 100000
            scene.camera.z -= -e.angleDelta().y() * strength
            if self._camera_controller is not None:
                self._camera_controller.sync_from_camera()
            return

        if self._controls.zoomCameraControl.satisfied(self._mouse_down, self._keys_down):
            strength = self._controls.zoomCameraSensitivity3d / 30000
            scene.camera.distance += -e.angleDelta().y() * strength
            if self._camera_controller is not None:
                self._camera_controller.sync_from_camera()

    def mouseMoveEvent(self, e: QMouseEvent):  # pyright: ignore[reportIncompatibleMethodOverride]
        screen = (
            Vector2(e.x(), e.y())  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
            if qtpy.QT5
            else Vector2(e.position().toPoint().x(), e.position().toPoint().y())  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
        )
        screen_delta = Vector2(screen.x - self._mouse_prev.x, screen.y - self._mouse_prev.y)

        if self.scene is None:
            self._mouse_prev = screen
            return

        if self.free_cam:
            # Free-cam: lock cursor to its last position and rotate camera with the movement delta.
            self.do_cursor_lock(screen)
            strength = self._controls.rotateCameraSensitivity3d / 10000
            self.rotate_camera(-screen_delta.x * strength, screen_delta.y * strength)
            if self._camera_controller is not None:
                self._camera_controller.sync_from_camera()
        else:
            # Pan (Shift+MMB by default) takes priority over orbit (MMB alone) when
            # both ControlItems share the MMB button and pan has the extra Shift key.
            if self._controls.moveXYCameraControl.satisfied(self._mouse_down, self._keys_down):
                self.do_cursor_lock(screen)
                forward: vec3 = -screen_delta.y * self.scene.camera.forward()
                sideward: vec3 = screen_delta.x * self.scene.camera.sideward()
                strength = self._controls.moveCameraSensitivity3d / 10000
                self.scene.camera.x -= (forward.x + sideward.x) * strength
                self.scene.camera.y -= (forward.y + sideward.y) * strength
                if self._camera_controller is not None:
                    self._camera_controller.sync_from_camera()
            elif self._controls.rotateCameraControl.satisfied(self._mouse_down, self._keys_down):
                self.do_cursor_lock(screen)
                strength = self._controls.rotateCameraSensitivity3d / 10000
                self.rotate_camera(-screen_delta.x * strength, screen_delta.y * strength)
                if self._camera_controller is not None:
                    self._camera_controller.sync_from_camera()

        self._mouse_prev = (
            screen  # Always assign mouse_prev after emitting, in order to do cursor lock properly.
        )

    def mousePressEvent(self, e: QMouseEvent):  # pyright: ignore[reportIncompatibleMethodOverride]
        button = e.button()
        self._mouse_down.add(button)
        # RobustLogger().debug(f"ModelRenderer.mousePressEvent: {self._mouse_down}, e.button() '{button}'")

    def mouseReleaseEvent(self, e: QMouseEvent):  # pyright: ignore[reportIncompatibleMethodOverride]
        button = e.button()
        self._mouse_down.discard(button)
        # RobustLogger().debug(f"ModelRenderer.mouseReleaseEvent: {self._mouse_down}, e.button() '{button}'")

    def rotate_object(self, obj: RenderObject, pitch: float, yaw: float, roll: float):
        """Apply an incremental rotation to a RenderObject."""
        # I implore someone to explain why Z affects Yaw, and Y affects Roll...
        current_rotation = obj.rotation()
        new_rotation = vec3(
            current_rotation.x + pitch, current_rotation.y + roll, current_rotation.z + yaw
        )
        obj.set_rotation(new_rotation.x, new_rotation.y, new_rotation.z)

    def keyPressEvent(self, e: QKeyEvent):  # pyright: ignore[reportIncompatibleMethodOverride]
        if self.scene is None:
            return

        key: int = e.key()
        self._keys_down.add(key)

        if self._controls.frameAllControl.satisfied(self._mouse_down, self._keys_down):
            self.frame_all()
            return
        if self._controls.frameSelectedControl.satisfied(self._mouse_down, self._keys_down):
            self.frame_selected()
            return
        if self._controls.viewFrontControl.satisfied(self._mouse_down, self._keys_down):
            self._apply_view_snap(0.0, math.pi / 2)
            return
        if self._controls.viewBackControl.satisfied(self._mouse_down, self._keys_down):
            self._apply_view_snap(math.pi, math.pi / 2)
            return
        if self._controls.viewRightControl.satisfied(self._mouse_down, self._keys_down):
            self._apply_view_snap(-math.pi / 2, math.pi / 2)
            return
        if self._controls.viewLeftControl.satisfied(self._mouse_down, self._keys_down):
            self._apply_view_snap(math.pi / 2, math.pi / 2)
            return
        if self._controls.viewTopControl.satisfied(self._mouse_down, self._keys_down):
            self._apply_view_snap(0.0, 0.01)
            return
        if self._controls.viewBottomControl.satisfied(self._mouse_down, self._keys_down):
            self._apply_view_snap(0.0, math.pi - 0.01)
            return
        if self._controls.viewToggleOrthoControl.satisfied(self._mouse_down, self._keys_down):
            self.scene.camera.orthographic = not self.scene.camera.orthographic
            if self._camera_controller is not None:
                self._camera_controller.sync_from_camera()
            self.update()
            return
        if self._controls.viewCameraControl.satisfied(self._mouse_down, self._keys_down):
            self.frame_all()
            return

        rotate_strength = self._controls.rotateCameraSensitivity3d / 1000

        model = self.scene.objects.get("model")
        if model:
            if self._controls.rotateCameraLeftControl.satisfied(self._mouse_down, self._keys_down):
                self.rotate_object(model, 0, math.pi / 4 * rotate_strength, 0)
            if self._controls.rotateCameraRightControl.satisfied(self._mouse_down, self._keys_down):
                self.rotate_object(model, 0, -math.pi / 4 * rotate_strength, 0)
            if self._controls.rotateCameraUpControl.satisfied(self._mouse_down, self._keys_down):
                self.rotate_object(model, math.pi / 4 * rotate_strength, 0, 0)
            if self._controls.rotateCameraDownControl.satisfied(self._mouse_down, self._keys_down):
                self.rotate_object(model, -math.pi / 4 * rotate_strength, 0, 0)

        if self._controls.zoomCameraInControl.satisfied(self._mouse_down, self._keys_down):
            self.scene.camera.distance = max(0.5, self.scene.camera.distance * 0.9)
        if self._controls.zoomCameraOutControl.satisfied(self._mouse_down, self._keys_down):
            self.scene.camera.distance = self.scene.camera.distance * 1.1

        if self._controls.moveCameraUpControl.satisfied(self._mouse_down, self._keys_down):
            self.scene.camera.z += self._controls.moveCameraSensitivity3d / 500
        if self._controls.moveCameraDownControl.satisfied(self._mouse_down, self._keys_down):
            self.scene.camera.z -= self._controls.moveCameraSensitivity3d / 500
        if self._controls.moveCameraLeftControl.satisfied(self._mouse_down, self._keys_down):
            self.pan_camera(0, -(self._controls.moveCameraSensitivity3d / 500), 0)
        if self._controls.moveCameraRightControl.satisfied(self._mouse_down, self._keys_down):
            self.pan_camera(0, (self._controls.moveCameraSensitivity3d / 500), 0)
        if self._controls.moveCameraForwardControl.satisfied(self._mouse_down, self._keys_down):
            self.pan_camera((self._controls.moveCameraSensitivity3d / 500), 0, 0)
        if self._controls.moveCameraBackwardControl.satisfied(self._mouse_down, self._keys_down):
            self.pan_camera(-(self._controls.moveCameraSensitivity3d / 500), 0, 0)
        if self._camera_controller is not None:
            self._camera_controller.sync_from_camera()
        # IMPORTANT: Do not perform wheel-style zoom on key presses.
        # If the zoom bind is configured as "any keys", `ControlItem.satisfied()` becomes
        # true for *every* keypress, which caused a spurious "zoom out one tick" behavior.
        # key_name = get_qt_key_string_localized(key)
        # RobustLogger().debug(f"ModelRenderer.keyPressEvent: {self._keys_down}, e.key() '{key_name}'")

    def keyReleaseEvent(self, e: QKeyEvent):  # pyright: ignore[reportIncompatibleMethodOverride]
        key: int = e.key()
        self._keys_down.discard(key)
        # key_name = get_qt_key_string_localized(key)
        # RobustLogger().debug(f"ModelRenderer.keyReleaseEvent: {self._keys_down}, e.key() '{key_name}'")

    # endregion


class ModelRendererControls:
    @property
    def moveCameraSensitivity3d(self) -> float:
        return cast("float", ModuleDesignerSettings().moveCameraSensitivity3d)

    @moveCameraSensitivity3d.setter
    def moveCameraSensitivity3d(self, value: float): ...
    @property
    def zoomCameraSensitivity3d(self) -> float:
        return cast("float", ModuleDesignerSettings().zoomCameraSensitivity3d)

    @zoomCameraSensitivity3d.setter
    def zoomCameraSensitivity3d(self, value: float): ...
    @property
    def rotateCameraSensitivity3d(self) -> float:
        return cast("float", ModuleDesignerSettings().rotateCameraSensitivity3d)

    @rotateCameraSensitivity3d.setter
    def rotateCameraSensitivity3d(self, value: float): ...
    @property
    def fieldOfView(self) -> float:
        return ModuleDesignerSettings().fieldOfView

    @fieldOfView.setter
    def fieldOfView(self, value: float): ...

    @property
    def moveXYCameraControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().moveCameraXY3dBind)

    @moveXYCameraControl.setter
    def moveXYCameraControl(self, value): ...

    @property
    def moveZCameraControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().moveCameraZ3dBind)

    @moveZCameraControl.setter
    def moveZCameraControl(self, value): ...

    @property
    def zoomCameraControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().zoomCamera3dBind)

    @zoomCameraControl.setter
    def zoomCameraControl(self, value): ...

    @property
    def rotateCameraLeftControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().rotateCameraLeft3dBind)

    @rotateCameraLeftControl.setter
    def rotateCameraLeftControl(self, value): ...

    @property
    def rotateCameraRightControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().rotateCameraRight3dBind)

    @rotateCameraRightControl.setter
    def rotateCameraRightControl(self, value): ...

    @property
    def rotateCameraUpControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().rotateCameraUp3dBind)

    @rotateCameraUpControl.setter
    def rotateCameraUpControl(self, value): ...

    @property
    def rotateCameraDownControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().rotateCameraDown3dBind)

    @rotateCameraDownControl.setter
    def rotateCameraDownControl(self, value): ...

    @property
    def moveCameraUpControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().moveCameraUp3dBind)

    @moveCameraUpControl.setter
    def moveCameraUpControl(self, value): ...

    @property
    def moveCameraDownControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().moveCameraDown3dBind)

    @moveCameraDownControl.setter
    def moveCameraDownControl(self, value): ...

    @property
    def moveCameraForwardControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().moveCameraForward3dBind)

    @moveCameraForwardControl.setter
    def moveCameraForwardControl(self, value): ...

    @property
    def moveCameraBackwardControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().moveCameraBackward3dBind)

    @moveCameraBackwardControl.setter
    def moveCameraBackwardControl(self, value): ...

    @property
    def moveCameraLeftControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().moveCameraLeft3dBind)

    @moveCameraLeftControl.setter
    def moveCameraLeftControl(self, value): ...

    @property
    def moveCameraRightControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().moveCameraRight3dBind)

    @moveCameraRightControl.setter
    def moveCameraRightControl(self, value): ...

    @property
    def zoomCameraInControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().zoomCameraIn3dBind)

    @zoomCameraInControl.setter
    def zoomCameraInControl(self, value): ...

    @property
    def zoomCameraOutControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().zoomCameraOut3dBind)

    @zoomCameraOutControl.setter
    def zoomCameraOutControl(self, value): ...

    @property
    def toggleInstanceLockControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().toggleLockInstancesBind)

    @toggleInstanceLockControl.setter
    def toggleInstanceLockControl(self, value): ...

    @property
    def rotateCameraControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().rotateCamera3dBind)

    @rotateCameraControl.setter
    def rotateCameraControl(self, value): ...

    @property
    def viewFrontControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().viewFront3dBind)

    @property
    def viewBackControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().viewBack3dBind)

    @property
    def viewRightControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().viewRight3dBind)

    @property
    def viewLeftControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().viewLeft3dBind)

    @property
    def viewTopControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().viewTop3dBind)

    @property
    def viewBottomControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().viewBottom3dBind)

    @property
    def viewToggleOrthoControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().viewToggleOrtho3dBind)

    @property
    def viewCameraControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().viewCamera3dBind)

    @property
    def frameSelectedControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().frameSelected3dBind)

    @property
    def frameAllControl(self) -> ControlItem:
        return ControlItem(ModuleDesignerSettings().frameAll3dBind)
