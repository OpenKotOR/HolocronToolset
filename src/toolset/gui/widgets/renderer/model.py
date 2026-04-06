"""Single-model preview widget (OpenGL) for GIT instances in the module designer."""

from __future__ import annotations

import math

from typing import TYPE_CHECKING, cast

import qtpy

from qtpy.QtCore import (
    Signal,  # pyright: ignore[reportPrivateImportUsage]
)

from loggerplus import RobustLogger
from pykotor.gl import vec3
from pykotor.gl.models.read_mdl import gl_load_mdl
from pykotor.gl.scene import RenderObject, Scene
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
        QResizeEvent,
        QWheelEvent,
    )
    from qtpy.QtWidgets import QWidget

    from pykotor.extract.installation import Installation
    from pykotor.resource.generics.utc import UTC
    from pykotor.resource.generics.uti import UTI


class ModelRenderer(OpenGLSceneRenderer):
    # Signal emitted when textures/models finish loading
    resourcesLoaded = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent, initial_mouse_prev=Vector2(0, 0), loop_interval_ms=33)
        self._last_texture_count: int = 0
        self._last_pending_texture_count: int = 0
        self._last_requested_texture_count: int = 0

        self._installation: Installation | None = None  # Use private attribute with property
        self._model_to_load: tuple[bytes, bytes] | None = None
        self._creature_to_load: UTC | None = None
        self._pending_camera_reset: bool = False

        self._controls = ModelRendererControls()

    def _on_loop_timer_timeout(self) -> None:
        if not self.isVisible() or self.scene is None:
            return
        self.update()

    @property
    def installation(self) -> Installation | None:
        return self._installation

    @installation.setter
    def installation(self, value: Installation | None):
        self._installation = value
        # If scene already exists, update its installation and load 2DA tables.
        # set_installation() loads appearance.2da etc. that the renderer needs.
        if self.scene is not None and value is not None and self.scene.installation is None:
            self.scene.installation = value
            self.scene.set_installation(value)
            RobustLogger().debug("ModelRenderer.installation setter: Updated existing scene with installation")

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

        self.loop_timer.start()

    def paintGL(self):
        if self.scene is None:
            return

        ctx = self.context()
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
            self.scene.objects["model"] = self.scene.get_creature_render_object(None, self._creature_to_load, sync=True)
            # Scene caches object lists; invalidate so swapped render objects take effect.
            if hasattr(self.scene, "_invalidate_object_cache"):
                self.scene._invalidate_object_cache()  # noqa: SLF001
            self._creature_to_load = None
            # Reset camera immediately since we loaded synchronously
            self.reset_camera()

        # Render first to poll async resources
        # THIS IS WHERE scene.texture() GETS CALLED DURING MESH RENDERING
        self.scene.render()

        # Check if textures/models FINISHED LOADING this frame (not just requested)
        # Only emit signal when textures are ACTUALLY LOADED - not when they're first requested
        texture_lookup_info = getattr(self.scene, "texture_lookup_info", {})
        requested_texture_names_obj: object = getattr(self.scene, "requested_texture_names", set())
        requested_texture_names: set[str] = cast("set[str]", requested_texture_names_obj)
        current_texture_count = len(texture_lookup_info)
        pending_textures = getattr(self.scene, "_pending_texture_futures", {})
        previous_pending_count = getattr(self, "_last_pending_texture_count", len(pending_textures))
        current_pending_count = len(pending_textures)
        current_requested_count = len(requested_texture_names)

        # ONLY emit signal when textures FINISH loading:
        # 1. texture_lookup_info count increased (new textures have lookup info stored)
        # 2. OR pending count decreased (async loads completed)
        # DO NOT emit just because requested count increased - that means textures are still loading!
        textures_finished_loading = current_texture_count > self._last_texture_count or (current_pending_count < previous_pending_count and previous_pending_count > 0)

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
        pending_reset = getattr(self, "_pending_camera_reset", False)
        if pending_reset and "model" in self.scene.objects:
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
        ht_get = getattr(self._installation, "ht_get_cache_2da", None)
        baseitems_name = getattr(self._installation, "TwoDA_BASEITEMS", "baseitems")
        if ht_get is not None:
            baseitems = ht_get(baseitems_name)
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
        # Check if this model is still loading
        if obj.model in self.scene._pending_model_futures:
            return False
        # Check if the model exists and is not the empty placeholder
        if obj.model not in self.scene.models:
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
        if self._controls.moveZCameraControl.satisfied(self._mouse_down, self._keys_down):
            # Ctrl+wheel (default) vertical camera move was far too sensitive; reduce by 5x.
            strength: float = self._controls.moveCameraSensitivity3d / 100000
            self.scene.camera.z -= -e.angleDelta().y() * strength
            return

        if self._controls.zoomCameraControl.satisfied(self._mouse_down, self._keys_down):
            strength = self._controls.zoomCameraSensitivity3d / 30000
            self.scene.camera.distance += -e.angleDelta().y() * strength

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
        else:
            if self._controls.moveXYCameraControl.satisfied(self._mouse_down, self._keys_down):
                self.do_cursor_lock(screen)
                forward: vec3 = -screen_delta.y * self.scene.camera.forward()
                sideward: vec3 = screen_delta.x * self.scene.camera.sideward()
                strength = self._controls.moveCameraSensitivity3d / 10000
                self.scene.camera.x -= (forward.x + sideward.x) * strength
                self.scene.camera.y -= (forward.y + sideward.y) * strength

            if self._controls.rotateCameraControl.satisfied(self._mouse_down, self._keys_down):
                self.do_cursor_lock(screen)
                strength = self._controls.rotateCameraSensitivity3d / 10000
                self.rotate_camera(-screen_delta.x * strength, screen_delta.y * strength)

        self._mouse_prev = screen  # Always assign mouse_prev after emitting, in order to do cursor lock properly.

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
        new_rotation = vec3(current_rotation.x + pitch, current_rotation.y + roll, current_rotation.z + yaw)
        obj.set_rotation(new_rotation.x, new_rotation.y, new_rotation.z)

    def keyPressEvent(self, e: QKeyEvent):  # pyright: ignore[reportIncompatibleMethodOverride]
        key: int = e.key()
        self._keys_down.add(key)

        rotate_strength = self._controls.rotateCameraSensitivity3d / 1000
        if "model" in self.scene.objects:
            model = self.scene.objects["model"]
            if self._controls.rotateCameraLeftControl.satisfied(self._mouse_down, self._keys_down):
                self.rotate_object(model, 0, math.pi / 4 * rotate_strength, 0)
            if self._controls.rotateCameraRightControl.satisfied(self._mouse_down, self._keys_down):
                self.rotate_object(model, 0, -math.pi / 4 * rotate_strength, 0)
            if self._controls.rotateCameraUpControl.satisfied(self._mouse_down, self._keys_down):
                self.rotate_object(model, math.pi / 4 * rotate_strength, 0, 0)
            if self._controls.rotateCameraDownControl.satisfied(self._mouse_down, self._keys_down):
                self.rotate_object(model, -math.pi / 4 * rotate_strength, 0, 0)

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
