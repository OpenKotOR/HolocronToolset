"""Module designer controls: tool buttons and mode toggles for the 2D view."""

from __future__ import annotations

import math
import time

from copy import deepcopy
from typing import TYPE_CHECKING

from qtpy import QtCore
from qtpy.QtCore import QPoint, Qt

from loggerplus import RobustLogger  # pyright: ignore[reportMissingTypeStubs]
from pykotor.gl.scene.camera_controller import (
    CameraController,
    CameraControllerSettings,
    InputState,
)
from pykotor.resource.generics.git import GITCamera
from toolset.data.misc import ControlItem
from toolset.gui.common.base_2d_controls import Base2DControlScheme
from toolset.gui.editors.git import DuplicateCommand, _GeometryMode, _InstanceMode
from toolset.gui.widgets.settings.widgets.module_designer import ModuleDesignerSettings
from toolset.gui.common.viewport_2d_nav import Viewport2DNavigationHelper, aabb_from_points
from toolset.utils.misc import BUTTON_TO_INT
from utility.common.geometry import Vector2, Vector3

if TYPE_CHECKING:
    from pykotor.resource.generics.git import GITInstance, GITObject
    from toolset.gui.editors.git import _SpawnMode
    from toolset.gui.widgets.renderer.module import ModuleRenderer
    from toolset.gui.widgets.renderer.walkmesh import WalkmeshRenderer
    from toolset.gui.windows.module_designer import ModuleDesigner


class InputSmoother:
    """Provides input smoothing for mouse movements.

    Uses exponential moving average to smooth out jerky mouse input
    while maintaining responsiveness.
    """

    def __init__(self, smoothing_factor: float = 0.3):
        """Initialize the smoother.

        Args:
            smoothing_factor: Value between 0 and 1. Higher = more smoothing.
        """
        self.smoothing_factor = smoothing_factor
        self._prev_x: float = 0.0
        self._prev_y: float = 0.0
        self._initialized: bool = False

    def smooth(self, x: float, y: float) -> tuple[float, float]:
        """Apply smoothing to input values.

        Args:
            x: Raw X input.
            y: Raw Y input.

        Returns:
            Smoothed (x, y) tuple.
        """
        if not self._initialized:
            self._prev_x = x
            self._prev_y = y
            self._initialized = True
            return (x, y)

        # Exponential moving average
        smoothed_x = self._prev_x * self.smoothing_factor + x * (1.0 - self.smoothing_factor)
        smoothed_y = self._prev_y * self.smoothing_factor + y * (1.0 - self.smoothing_factor)

        self._prev_x = smoothed_x
        self._prev_y = smoothed_y

        return (smoothed_x, smoothed_y)

    def reset(self) -> None:
        """Reset the smoother state."""
        self._initialized = False


class InputAccelerator:
    """Provides acceleration curves for input.

    Makes precise movements easier while allowing fast movements
    when needed. Uses a power curve.
    """

    def __init__(self, power: float = 1.5, threshold: float = 2.0):
        """Initialize the accelerator.

        Args:
            power: Power for the acceleration curve. >1 = acceleration.
            threshold: Input values below this use linear response.
        """
        self.power = power
        self.threshold = threshold

    def accelerate(self, value: float) -> float:
        """Apply acceleration to an input value.

        Args:
            value: Raw input value.

        Returns:
            Accelerated value.
        """
        sign = 1.0 if value >= 0 else -1.0
        magnitude = abs(value)

        # Below threshold: linear response for precise control
        if magnitude < self.threshold:
            return value

        # Above threshold: power curve for fast movements
        excess = magnitude - self.threshold
        accelerated_excess = math.pow(excess, self.power)

        return sign * (self.threshold + accelerated_excess)


class ModuleDesignerControls3d:
    """Enhanced 3D camera controls for the Module Designer.

    Provides intuitive camera controls inspired by professional 3D software:

    Camera Controls:
    - **Middle Mouse + Drag**: Pan camera parallel to view plane
    - **Right Mouse + Drag**: Zoom in/out (forward/back)
    - **Left Mouse + Drag**: Rotate camera (orbit mode)
    - **Scroll Wheel**: Zoom in/out
    - **Ctrl + Left Mouse + Drag**: Pan camera (alternative)

    Instance Controls:
    - **Left Mouse Click**: Select instance
    - **Left Mouse + Drag on Instance**: Move instance
    - **Shift + Left Mouse + Drag**: Move instance on Z axis
    - **Middle Mouse + Drag on Instance**: Rotate instance

    The controls feature input smoothing and acceleration for a more
    professional feel. Small movements are precise, while fast movements
    cover more ground.
    """

    def __init__(
        self,
        editor: ModuleDesigner,
        renderer: ModuleRenderer,
    ):
        self.editor: ModuleDesigner = editor
        self.renderer: ModuleRenderer = renderer
        # Ensure renderer is in non-free-cam mode when using standard 3D controls
        # so that input deltas and loop behaviour are correct.
        # Related implementation: `ModuleRenderer.free_cam` (see
        # `Tools/HolocronToolset/src/toolset/gui/widgets/renderer/module.py`).
        self.renderer.free_cam = False
        self.renderer.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        if self.renderer.scene is not None:  # noqa: SLF001
            self.renderer.scene.show_cursor = True  # noqa: SLF001

        # Input processing
        self._input_smoother: InputSmoother = InputSmoother(smoothing_factor=0.2)
        self._input_accelerator: InputAccelerator = InputAccelerator(power=1.3, threshold=3.0)

        # Initialize camera controller with settings
        self._camera_controller: CameraController | None = None
        self._last_input_state: InputState = InputState()
        self._accumulated_mouse_dx: float = 0.0
        self._accumulated_mouse_dy: float = 0.0
        self._last_camera_buttons: set[Qt.MouseButton] = set()
        self._last_camera_keys: set[Qt.Key] = set()
        # Last mouse position in renderer-local pixels (for zoom-to-cursor)
        self._last_mouse_screen: Vector2 = Vector2(0.0, 0.0)

    def _get_camera_controller(self) -> CameraController:
        """Get or create the camera controller."""
        if self._camera_controller is None:
            settings = CameraControllerSettings(
                orbit_sensitivity=self.settings.rotateCameraSensitivity3d / 100.0,
                pan_sensitivity=self.settings.moveCameraSensitivity3d / 100.0,
                zoom_sensitivity=self.settings.zoomCameraSensitivity3d / 100.0,
                enable_smoothing=True,
                smoothing_factor=0.1,
                enable_acceleration=True,
                speed_boost_multiplier=self.settings.boostedMoveCameraSensitivity3d / self.settings.moveCameraSensitivity3d,
                shift_for_fine_control=True,
                fine_control_multiplier=0.25,
            )
            assert self.renderer.scene is not None, "self.renderer.scene is None"
            self._camera_controller = CameraController(
                self.renderer.scene.camera,
                settings,
            )
        return self._camera_controller

    def _process_input(self, screen_delta: Vector2) -> tuple[float, float]:
        """Process raw input through smoothing and acceleration.

        Args:
            screen_delta: Raw mouse delta.

        Returns:
            Processed (dx, dy) tuple.
        """
        # Apply smoothing
        dx, dy = self._input_smoother.smooth(screen_delta.x, screen_delta.y)

        # Apply acceleration
        dx = self._input_accelerator.accelerate(dx)
        dy = self._input_accelerator.accelerate(dy)

        return (dx, dy)

    def on_mouse_scrolled(
        self,
        delta: Vector2,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
    ):
        if self.zoom_camera.satisfied(buttons, keys):
            # Route scroll zoom through CameraController so zoom-to-cursor works.
            assert self.renderer.scene is not None, "self.renderer.scene is None"
            ctrl: CameraController = self._get_camera_controller()
            ctrl.update(
                InputState(
                    scroll_delta=delta.y / 120.0,
                    mouse_x=self._last_mouse_screen.x,
                    mouse_y=self._last_mouse_screen.y,
                    viewport_width=float(self.renderer.width()),
                    viewport_height=float(self.renderer.height()),
                    shift_held=Qt.Key.Key_Shift in keys,
                    ctrl_held=Qt.Key.Key_Control in keys,
                    alt_held=Qt.Key.Key_Alt in keys,
                )
            )

        elif self.move_z_camera.satisfied(buttons, keys):
            # Ctrl+wheel (default) vertical camera move was far too sensitive; reduce by 5x.
            strength = float(self.settings.moveCameraSensitivity3d) / 50000
            assert self.renderer.scene is not None, "self.renderer.scene is None"
            self.renderer.scene.camera.z -= -delta.y * strength

    def _any_modifier_held(self, keys: set[Qt.Key]) -> bool:
        """Return True if any modifier key (Ctrl, Shift, Alt) is currently held."""
        _MODIFIER_KEYS = {
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Meta,
        }
        return bool(keys & _MODIFIER_KEYS)

    def on_mouse_moved(
        self,
        screen: Vector2,
        screen_delta: Vector2,
        world: Vector3,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
    ):
        self._last_camera_buttons = set(buttons)
        self._last_camera_keys = set(keys)
        self._last_mouse_screen = screen

        # Process input through smoothing and acceleration
        processed_dx, processed_dy = self._process_input(screen_delta)
        _processed_delta = Vector2(processed_dx, processed_dy)

        # Evaluate camera control bindings FIRST.
        # Camera bindings that require modifier keys (e.g. Ctrl+Left = pan) must take
        # priority over generic instance manipulation bindings (e.g. Left = move instance)
        # which have no required modifier keys and would otherwise shadow them.
        move_xy_camera_satisfied = self.move_xy_camera.satisfied(buttons, keys)
        move_camera_plane_satisfied = self.move_camera_plane.satisfied(buttons, keys)
        rotate_camera_satisfied = self.rotate_camera.satisfied(buttons, keys)
        zoom_camera_satisfied = self.zoom_camera_mm.satisfied(buttons, keys)

        # When a modifier key is held, camera controls always win over instance manipulation.
        # This prevents e.g. Ctrl+LeftDrag (pan camera) from being eaten by the instance
        # move handler whose binding is just LeftButton with no required modifiers.
        modifier_held = self._any_modifier_held(keys)
        camera_wants_input = move_xy_camera_satisfied or move_camera_plane_satisfied or zoom_camera_satisfied or (rotate_camera_satisfied and modifier_held)

        # Instance manipulation - only when no camera control with modifiers claims the input.
        # When the user has a selection and is left-dragging (move_xy_selected), always prefer
        # moving the instance over rotating the camera, even if the active tool is Select.
        _TOOL_SELECT = 0
        _TOOL_MOVE = 1
        _TOOL_ROTATE = 2
        active_tool: int = self.editor._active_tool  # noqa: SLF001
        instance_drag_ok = active_tool != _TOOL_SELECT or self.move_xy_selected.satisfied(buttons, keys)

        if not camera_wants_input and instance_drag_ok and not self.editor.ui.lockInstancesCheck.isChecked() and self.editor.selected_instances:
            # Check instance manipulation bindings (most specific first)
            if self.move_z_selected.satisfied(buttons, keys):
                if not self.editor.transform_state.is_drag_moving:
                    self.editor.transform_state.initial_positions = {instance: instance.position for instance in self.editor.selected_instances}
                    self.editor.transform_state.is_drag_moving = True
                for instance in self.editor.selected_instances:
                    instance.position.z -= processed_dy / 40
                return

            # ROTATE tool: redirect left-drag to rotation instead of XY move
            if active_tool == _TOOL_ROTATE and self.move_xy_selected.satisfied(buttons, keys):
                if not self.editor.transform_state.is_drag_rotating:
                    self.editor.transform_state.is_drag_rotating = True
                    for instance in self.editor.selected_instances:
                        if not self.editor._is_rotatable_instance(instance):  # noqa: SLF001
                            continue
                        self.editor._capture_initial_rotation_for_transform(instance)  # noqa: SLF001
                self.editor.rotate_selected(processed_dx, processed_dy)
                return

            if self.rotate_selected.satisfied(buttons, keys):
                if not self.editor.transform_state.is_drag_rotating:
                    self.editor.transform_state.is_drag_rotating = True
                    for instance in self.editor.selected_instances:
                        if not self.editor._is_rotatable_instance(instance):  # noqa: SLF001
                            continue
                        self.editor._capture_initial_rotation_for_transform(instance)  # noqa: SLF001
                self.editor.rotate_selected(processed_dx, processed_dy)
                return

            # MOVE tool (or default): left-drag moves XY
            if active_tool != _TOOL_ROTATE and self.move_xy_selected.satisfied(buttons, keys):
                if not self.editor.transform_state.is_drag_moving:
                    self.editor.transform_state.initial_positions = {instance: instance.position for instance in self.editor.selected_instances}
                    self.editor.transform_state.is_drag_moving = True
                for instance in self.editor.selected_instances:
                    x = float(world.x)
                    y = float(world.y)
                    z = float(instance.position.z) if isinstance(instance, GITCamera) else float(world.z)
                    instance.position = Vector3(x, y, z)
                return

        # Camera controls: accumulate raw deltas for CameraController.update() in the render loop (smoothing)
        plane_pan_satisfied = move_camera_plane_satisfied or move_xy_camera_satisfied
        if plane_pan_satisfied or rotate_camera_satisfied or zoom_camera_satisfied:
            self.editor.do_cursor_lock(screen, center_mouse=False, do_rotations=False)
            self._accumulated_mouse_dx += screen_delta.x
            self._accumulated_mouse_dy += screen_delta.y
            return

    def on_mouse_pressed(
        self,
        screen: Vector2,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
    ):
        if self.select_underneath.satisfied(buttons, keys):
            self.renderer.do_select = True  # auto-selects the instance under the mouse in the paint loop, and implicitly sets this back to False

        if self.duplicate_selected.satisfied(buttons, keys) and self.editor.selected_instances:
            self._duplicate_selected_instance()

    def on_mouse_released(
        self,
        screen: Vector2,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
        released_button: Qt.MouseButton | None = None,
    ):
        if released_button == Qt.MouseButton.RightButton:
            scene = self.renderer.scene
            if scene is not None:
                world = Vector3(*scene.cursor.position())
                self.editor.on_context_menu(world, self.renderer.mapToGlobal(QPoint(int(screen.x), int(screen.y))))
        self.editor.handle_undo_redo_from_long_action_finished()

    def on_keyboard_released(self, buttons: set[Qt.MouseButton], keys: set[Qt.Key]):
        self.editor.handle_undo_redo_from_long_action_finished()

    def update_camera_from_input(self, delta_time: float) -> bool:
        """Update camera via CameraController with accumulated mouse deltas (called from render loop)."""
        if self.renderer.scene is None:
            return False
        controller = self._get_camera_controller()
        delta_time = min(delta_time, 0.05)
        dx = self._accumulated_mouse_dx
        dy = self._accumulated_mouse_dy
        self._accumulated_mouse_dx = 0.0
        self._accumulated_mouse_dy = 0.0
        buttons = self._last_camera_buttons
        keys = self._last_camera_keys

        keyboard_motion_applied = False
        if self.renderer.underMouse():
            rotation_keys: dict[str, bool] = {
                "left": self.rotate_camera_left.satisfied(buttons, keys),
                "right": self.rotate_camera_right.satisfied(buttons, keys),
                "up": self.rotate_camera_up.satisfied(buttons, keys),
                "down": self.rotate_camera_down.satisfied(buttons, keys),
            }
            movement_keys: dict[str, bool] = {
                "up": self.move_camera_up.satisfied(buttons, keys),
                "down": self.move_camera_down.satisfied(buttons, keys),
                "left": self.move_camera_left.satisfied(buttons, keys),
                "right": self.move_camera_right.satisfied(buttons, keys),
                "forward": self.move_camera_forward.satisfied(buttons, keys),
                "backward": self.move_camera_backward.satisfied(buttons, keys),
                "in": self.zoom_camera_in.satisfied(buttons, keys),
                "out": self.zoom_camera_out.satisfied(buttons, keys),
            }
            if any(rotation_keys.values()) or any(movement_keys.values()):
                rotate_speed = (self.settings.rotateCameraSensitivity3d / 1000.0) * delta_time * 120.0
                angle_units_delta = (math.pi / 4.0) * rotate_speed
                if rotation_keys["left"]:
                    self.renderer.rotate_camera(angle_units_delta, 0.0)
                elif rotation_keys["right"]:
                    self.renderer.rotate_camera(-angle_units_delta, 0.0)
                if rotation_keys["up"]:
                    self.renderer.rotate_camera(0.0, angle_units_delta)
                elif rotation_keys["down"]:
                    self.renderer.rotate_camera(0.0, -angle_units_delta)

                speed_boost = self.speed_boost_control.satisfied(buttons, keys, exact_keys_and_buttons=False)
                move_units_delta = (
                    self.settings.boostedMoveCameraSensitivity3d
                    if speed_boost else self.settings.moveCameraSensitivity3d
                )
                move_units_delta = (move_units_delta / 500.0) * delta_time * 120.0

                if movement_keys["in"]:
                    self.renderer.zoom_camera(move_units_delta)
                if movement_keys["out"]:
                    self.renderer.zoom_camera(-move_units_delta)
                if movement_keys["up"]:
                    self.renderer.scene.camera.z += move_units_delta
                if movement_keys["down"]:
                    self.renderer.scene.camera.z -= move_units_delta
                if movement_keys["left"]:
                    self.renderer.pan_camera(0.0, -move_units_delta, 0.0)
                if movement_keys["right"]:
                    self.renderer.pan_camera(0.0, move_units_delta, 0.0)
                if movement_keys["forward"]:
                    self.renderer.pan_camera(move_units_delta, 0.0, 0.0)
                if movement_keys["backward"]:
                    self.renderer.pan_camera(-move_units_delta, 0.0, 0.0)
                keyboard_motion_applied = True

        input_state = InputState(
            mouse_delta_x=dx,
            mouse_delta_y=dy,
            left_button=Qt.MouseButton.LeftButton in buttons,
            middle_button=Qt.MouseButton.MiddleButton in buttons,
            right_button=Qt.MouseButton.RightButton in buttons,
            shift_held=Qt.Key.Key_Shift in keys,
            ctrl_held=Qt.Key.Key_Control in keys,
            alt_held=Qt.Key.Key_Alt in keys,
        )
        controller_active = (
            dx != 0.0
            or dy != 0.0
            or input_state.left_button
            or input_state.middle_button
            or input_state.right_button
            or controller.has_pending_motion()
        )
        if keyboard_motion_applied:
            controller.sync_from_camera()
        elif controller_active:
            controller.update(input_state, delta_time)
        return keyboard_motion_applied or controller.has_pending_motion() or controller_active

    def _duplicate_selected_instance(self):
        # TODO(th3w1zard1): Seems the code throughout is designed for multi-selections, yet nothing uses it. Probably disabled due to a bug or planned for later.
        instance: GITObject = deepcopy(self.editor.selected_instances[-1])
        if isinstance(instance, GITCamera) and self.editor._module is not None:
            instance.camera_id = self.editor._module.git().resource().next_camera_id()  # noqa: SLF001  # pyright: ignore[reportOptionalMemberAccess]
        RobustLogger().info(f"Duplicating {instance!r}")
        if self.editor._module is not None:
            self.editor.undo_stack.push(DuplicateCommand(self.editor._module.git().resource(), [instance], self.editor))  # noqa: SLF001  # pyright: ignore[reportArgumentType, reportOptionalMemberAccess]
        assert self.renderer.scene is not None, "self.renderer.scene is None"
        vect3 = self.renderer.scene.cursor.position()
        instance.position = Vector3(vect3.x, vect3.y, vect3.z)
        # self.editor.git().add(instance)  # Handled by the undoStack above.
        self.editor.rebuild_instance_list()
        self.editor.set_selection([instance])

    def _apply_numpad_view(self, yaw: float, pitch: float) -> None:
        """Snap camera to a canonical numpad view angle (Blender-style).

        Uses the CameraController.set_rotation() with smoothing so the
        transition is animated rather than instant.

        Args:
            yaw: Target yaw in radians.
            pitch: Target pitch in radians (0=top-down, pi/2=horizon).
        """
        if self.renderer.scene is None:
            return
        ctrl = self._get_camera_controller()
        ctrl.set_rotation(yaw, pitch, instant=False)

    def frame_selected(self) -> None:
        """Frame the selected instance(s) in the 3D viewport.

        Equivalent to Blender's Numpad Period.  Computes the bounding-centre of
        all selected instances then dolly-zooms the camera to a comfortable
        viewing distance with smooth interpolation.
        """
        if self.renderer.scene is None:
            return
        instances = self.editor.selected_instances
        if not instances:
            return
        xs = [float(inst.position.x) for inst in instances]
        ys = [float(inst.position.y) for inst in instances]
        zs = [float(inst.position.z) for inst in instances]
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2
        cz = (min(zs) + max(zs)) / 2
        # Viewing distance: half the bounding diagonal, clamped to sane range
        diag = math.sqrt((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2 + (max(zs) - min(zs)) ** 2)
        dist = max(2.0, min(50.0, diag * 1.5 + 3.0))
        ctrl = self._get_camera_controller()
        ctrl.focus_on_point(cx, cy, cz, dist)

    def frame_all(self) -> None:
        """Frame all visible instances in the 3D viewport.

        Equivalent to Blender's Home key in the viewport.  Collects all GIT
        instance positions and dolly-zooms to fit them with smooth
        interpolation.
        """
        if self.renderer.scene is None or self.editor._module is None:  # noqa: SLF001
            return
        git = self.editor._module.git()  # noqa: SLF001
        if git is None:
            return
        res = git.resource()
        if res is None:
            return
        all_instances = res.instances()
        if not all_instances:
            return
        xs = [float(inst.position.x) for inst in all_instances]
        ys = [float(inst.position.y) for inst in all_instances]
        zs = [float(inst.position.z) for inst in all_instances]
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2
        cz = (min(zs) + max(zs)) / 2
        diag = math.sqrt((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2 + (max(zs) - min(zs)) ** 2)
        dist = max(5.0, min(200.0, diag * 0.6 + 5.0))
        ctrl = self._get_camera_controller()
        ctrl.focus_on_point(cx, cy, cz, dist)

    def on_keyboard_pressed(
        self,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
    ):
        if self.toggle_free_cam.satisfied(buttons, keys):
            current_time = time.time()
            if current_time - self.editor.last_free_cam_time > 0.5:  # 0.5 seconds delay, prevents spamming  # noqa: PLR2004
                self.editor.toggle_free_cam()
                self.editor.last_free_cam_time = current_time  # Update the last toggle time
            return

        # Check camera movement keys
        move_camera_keys: dict[str, bool] = {
            "selected": self.move_camera_to_selected.satisfied(buttons, keys),
            "cursor": self.move_camera_to_cursor.satisfied(buttons, keys),
            "entry": self.move_camera_to_entry_point.satisfied(buttons, keys),
        }
        if any(move_camera_keys.values()):
            if move_camera_keys["selected"]:
                instance: GITObject | None = next(iter(self.editor.selected_instances), None)
                if instance is not None:
                    self.renderer.snap_camera_to_point(instance.position)
                    # Also sync 2D camera to the selected instance position
                    self.editor.ui.flatRenderer.snap_camera_to_point(instance.position)
            elif move_camera_keys["cursor"]:
                assert self.renderer.scene is not None, "self.renderer.scene is None"
                self.renderer.scene.camera.set_position(self.renderer.scene.cursor.position())
            elif move_camera_keys["entry"]:
                self.editor.snap_camera_to_entry_location()
            return

        # Blender numpad view presets ─────────────────────────────────────────
        # Numpad 1/Ctrl+1 → front/back  (yaw=0 / pi, pitch=pi/2 = horizon)
        # Numpad 3/Ctrl+3 → right/left  (yaw=-pi/2 / pi/2, pitch=pi/2)
        # Numpad 7/Ctrl+7 → top/bottom  (yaw=0, pitch≈0 / ≈pi)
        # Numpad 5        → toggle orthographic
        # Numpad 0        → snap to first GIT camera
        if self.view_front.satisfied(buttons, keys):
            self._apply_numpad_view(yaw=0.0, pitch=math.pi / 2)
            return
        if self.view_back.satisfied(buttons, keys):
            self._apply_numpad_view(yaw=math.pi, pitch=math.pi / 2)
            return
        if self.view_right.satisfied(buttons, keys):
            self._apply_numpad_view(yaw=-math.pi / 2, pitch=math.pi / 2)
            return
        if self.view_left.satisfied(buttons, keys):
            self._apply_numpad_view(yaw=math.pi / 2, pitch=math.pi / 2)
            return
        if self.view_top.satisfied(buttons, keys):
            self._apply_numpad_view(yaw=0.0, pitch=0.01)
            return
        if self.view_bottom.satisfied(buttons, keys):
            self._apply_numpad_view(yaw=0.0, pitch=math.pi - 0.01)
            return
        if self.view_toggle_ortho.satisfied(buttons, keys):
            if self.renderer.scene is not None:
                self.renderer.scene.camera.orthographic = not self.renderer.scene.camera.orthographic
            return
        if self.view_camera.satisfied(buttons, keys):
            # Snap viewport to the first GIT camera instance
            if self.editor._module is not None:  # noqa: SLF001
                git_res = self.editor._module.git()  # noqa: SLF001
                if git_res is not None:
                    cam_list = git_res.resource().cameras if git_res.resource() is not None else []  # pyright: ignore[reportOptionalMemberAccess]
                    if cam_list:
                        git_cam = cam_list[0]
                        assert self.renderer.scene is not None, "renderer.scene is None"
                        ctrl = self._get_camera_controller()
                        ctrl.set_focal_point(git_cam.position.x, git_cam.position.y, git_cam.position.z)
            return

        # Frame selected (Numpad . by default)
        if self.frame_selected_bind.satisfied(buttons, keys):
            self.frame_selected()
            return

        # Frame all (Home by default)
        if self.frame_all_bind.satisfied(buttons, keys):
            self.frame_all()
            return
        if self.toggle_instance_lock.satisfied(buttons, keys):
            self.editor.ui.lockInstancesCheck.setChecked(not self.editor.ui.lockInstancesCheck.isChecked())
        if not self.editor.selected_instances:
            return
        if self.delete_selected.satisfied(buttons, keys):
            self.editor.delete_selected()
            return
        if self.duplicate_selected.satisfied(buttons, keys):
            self._duplicate_selected_instance()
            return

    @property
    def move_xy_camera(self):
        return ControlItem(self.settings.moveCameraXY3dBind)

    @property
    def move_z_camera(self):
        return ControlItem(self.settings.moveCameraZ3dBind)

    @property
    def move_camera_plane(self):
        return ControlItem(self.settings.moveCameraPlane3dBind)

    @property
    def rotate_camera(self):
        return ControlItem(self.settings.rotateCamera3dBind)

    @property
    def zoom_camera(self):
        return ControlItem(self.settings.zoomCamera3dBind)

    @property
    def zoom_camera_mm(self):
        return ControlItem(self.settings.zoomCameraMM3dBind)

    @property
    def rotate_selected(self):
        return ControlItem(self.settings.rotateSelected3dBind)

    @property
    def move_xy_selected(self):
        return ControlItem(self.settings.moveSelectedXY3dBind)

    @property
    def move_z_selected(self):
        return ControlItem(self.settings.moveSelectedZ3dBind)

    @property
    def select_underneath(self):
        return ControlItem(self.settings.selectObject3dBind)

    @property
    def move_camera_to_selected(self):
        return ControlItem(self.settings.moveCameraToSelected3dBind)

    @property
    def move_camera_to_cursor(self):
        return ControlItem(self.settings.moveCameraToCursor3dBind)

    @property
    def move_camera_to_entry_point(self):
        return ControlItem(self.settings.moveCameraToEntryPoint3dBind)

    @property
    def toggle_free_cam(self):
        return ControlItem(self.settings.toggleFreeCam3dBind)

    @property
    def delete_selected(self):
        return ControlItem(self.settings.deleteObject3dBind)

    @property
    def duplicate_selected(self):
        return ControlItem(self.settings.duplicateObject3dBind)

    @property
    def open_context_menu(self):
        return ControlItem((set(), {BUTTON_TO_INT[Qt.MouseButton.RightButton]}))  # pyright: ignore[reportArgumentType]

    @property
    def rotate_camera_left(self):
        return ControlItem(self.settings.rotateCameraLeft3dBind)

    @property
    def rotate_camera_right(self):
        return ControlItem(self.settings.rotateCameraRight3dBind)

    @property
    def rotate_camera_up(self):
        return ControlItem(self.settings.rotateCameraUp3dBind)

    @property
    def rotate_camera_down(self):
        return ControlItem(self.settings.rotateCameraDown3dBind)

    @property
    def move_camera_up(self):
        return ControlItem(self.settings.moveCameraUp3dBind)

    @property
    def move_camera_down(self):
        return ControlItem(self.settings.moveCameraDown3dBind)

    @property
    def move_camera_forward(self):
        return ControlItem(self.settings.moveCameraForward3dBind)

    @property
    def move_camera_backward(self):
        return ControlItem(self.settings.moveCameraBackward3dBind)

    @property
    def move_camera_left(self):
        return ControlItem(self.settings.moveCameraLeft3dBind)

    @property
    def move_camera_right(self):
        return ControlItem(self.settings.moveCameraRight3dBind)

    @property
    def zoom_camera_in(self):
        return ControlItem(self.settings.zoomCameraIn3dBind)

    @property
    def zoom_camera_out(self):
        return ControlItem(self.settings.zoomCameraOut3dBind)

    @property
    def toggle_instance_lock(self):
        return ControlItem(self.settings.toggleLockInstancesBind)

    @property
    def speed_boost_control(self):
        return ControlItem(self.settings.speedBoostCamera3dBind)

    @property
    def view_front(self):
        return ControlItem(self.settings.viewFront3dBind)

    @property
    def view_back(self):
        return ControlItem(self.settings.viewBack3dBind)

    @property
    def view_right(self):
        return ControlItem(self.settings.viewRight3dBind)

    @property
    def view_left(self):
        return ControlItem(self.settings.viewLeft3dBind)

    @property
    def view_top(self):
        return ControlItem(self.settings.viewTop3dBind)

    @property
    def view_bottom(self):
        return ControlItem(self.settings.viewBottom3dBind)

    @property
    def view_toggle_ortho(self):
        return ControlItem(self.settings.viewToggleOrtho3dBind)

    @property
    def view_camera(self):
        return ControlItem(self.settings.viewCamera3dBind)

    @property
    def frame_selected_bind(self):
        return ControlItem(self.settings.frameSelected3dBind)

    @property
    def frame_all_bind(self):
        return ControlItem(self.settings.frameAll3dBind)

    @property
    def settings(self) -> ModuleDesignerSettings:
        return ModuleDesignerSettings()


class ModuleDesignerControlsFreeCam:
    def __init__(self, editor: ModuleDesigner, renderer: ModuleRenderer):
        self.editor: ModuleDesigner = editor
        self.renderer: ModuleRenderer = renderer
        # Clear any stale input state carried over from the regular 3D controls.
        # NOTE: `keys_down()` returns a copy, so we must use the explicit reset
        # helpers on the renderer.
        # Implementation reference:
        # - `reset_all_down` in `ModuleRenderer`
        #   (Tools/HolocronToolset/src/toolset/gui/widgets/renderer/module.py)
        self.renderer.reset_all_down()
        # Enable free-cam mode on the renderer so that:
        # - The render loop emits continuous keyboard events while keys are held
        # - Mouse movement uses the correct free-cam deltas
        self.renderer.free_cam = True
        assert self.renderer.scene is not None, "self.renderer.scene is None"
        self.controls3d_distance = self.renderer.scene.camera.distance
        self.renderer.scene.camera.distance = 0
        self.renderer.setCursor(QtCore.Qt.CursorShape.BlankCursor)
        self.renderer.scene.show_cursor = False

    def on_mouse_scrolled(self, delta: Vector2, buttons: set[Qt.MouseButton], keys: set[Qt.Key]): ...

    def on_mouse_moved(self, screen: Vector2, screen_delta: Vector2, world: Vector3, buttons: set[Qt.MouseButton], keys: set[Qt.Key]):  # noqa: PLR0913
        self.editor.do_cursor_lock(screen)

    def on_mouse_pressed(self, screen: Vector2, buttons: set[Qt.MouseButton], keys: set[Qt.Key]): ...

    def on_mouse_released(self, screen: Vector2, buttons: set[Qt.MouseButton], keys: set[Qt.Key], released_button: Qt.MouseButton | None = None): ...

    def on_keyboard_pressed(self, buttons: set[Qt.MouseButton], keys: set[Qt.Key]):
        current_time = time.time()
        if self.toggle_free_cam.satisfied(buttons, keys) and (current_time - self.editor.last_free_cam_time > 0.5):  # 0.5 seconds delay, prevents spamming
            # self.renderer.scene.camera.distance = self.controls3d_distance
            self.editor.toggle_free_cam()
            self.editor.last_free_cam_time = current_time  # Update the last toggle time

    def on_keyboard_released(self, buttons: set[Qt.MouseButton], keys: set[Qt.Key]): ...

    def update_camera_from_input(self, delta_time: float) -> bool:
        if self.renderer.scene is None:
            return False
        delta_time = min(delta_time, 0.05)
        buttons = self.renderer.mouse_down()
        keys = self.renderer.keys_down()

        rotate_delta = (math.pi / 4.0) * (self.settings.rotateCameraSensitivityFC / 1000.0) * delta_time * 120.0
        rotation_applied = False
        if self.rotate_camera_left.satisfied(buttons, keys):
            self.renderer.rotate_camera(rotate_delta, 0.0)
            rotation_applied = True
        elif self.rotate_camera_right.satisfied(buttons, keys):
            self.renderer.rotate_camera(-rotate_delta, 0.0)
            rotation_applied = True
        if self.rotate_camera_up.satisfied(buttons, keys):
            self.renderer.rotate_camera(0.0, rotate_delta)
            rotation_applied = True
        elif self.rotate_camera_down.satisfied(buttons, keys):
            self.renderer.rotate_camera(0.0, -rotate_delta)
            rotation_applied = True

        move_speed = self.settings.boostedFlyCameraSpeedFC if self.speed_boost_control.satisfied(buttons, keys, exact_keys_and_buttons=False) else self.settings.flyCameraSpeedFC
        move_units_delta = (move_speed / 500.0) * delta_time * 120.0
        moved = False
        if self.zoom_camera_in.satisfied(buttons, keys):
            self.renderer.zoom_camera(move_units_delta)
            moved = True
        if self.zoom_camera_out.satisfied(buttons, keys):
            self.renderer.zoom_camera(-move_units_delta)
            moved = True
        if self.move_camera_up.satisfied(buttons, keys):
            self.renderer.move_camera(0.0, 0.0, move_units_delta)
            moved = True
        if self.move_camera_down.satisfied(buttons, keys):
            self.renderer.move_camera(0.0, 0.0, -move_units_delta)
            moved = True
        if self.move_camera_left.satisfied(buttons, keys):
            self.renderer.move_camera(0.0, -move_units_delta, 0.0)
            moved = True
        if self.move_camera_right.satisfied(buttons, keys):
            self.renderer.move_camera(0.0, move_units_delta, 0.0)
            moved = True
        if self.move_camera_forward.satisfied(buttons, keys):
            self.renderer.move_camera(move_units_delta, 0.0, 0.0)
            moved = True
        if self.move_camera_backward.satisfied(buttons, keys):
            self.renderer.move_camera(-move_units_delta, 0.0, 0.0)
            moved = True
        return rotation_applied or moved or bool(buttons) or bool(keys)

    @property
    def toggle_free_cam(self):
        return ControlItem(self.settings.toggleFreeCam3dBind)

    @property
    def move_camera_up(self):
        return ControlItem(self.settings.moveCameraUpFcBind)

    @property
    def move_camera_down(self):
        return ControlItem(self.settings.moveCameraDownFcBind)

    @property
    def move_camera_forward(self):
        return ControlItem(self.settings.moveCameraForwardFcBind)

    @property
    def move_camera_backward(self):
        return ControlItem(self.settings.moveCameraBackwardFcBind)

    @property
    def move_camera_left(self):
        return ControlItem(self.settings.moveCameraLeftFcBind)

    @property
    def move_camera_right(self):
        return ControlItem(self.settings.moveCameraRightFcBind)

    @property
    def rotate_camera_left(self):
        return ControlItem(self.settings.rotateCameraLeftFcBind)

    @property
    def rotate_camera_right(self):
        return ControlItem(self.settings.rotateCameraRightFcBind)

    @property
    def rotate_camera_up(self):
        return ControlItem(self.settings.rotateCameraUpFcBind)

    @property
    def rotate_camera_down(self):
        return ControlItem(self.settings.rotateCameraDownFcBind)

    @property
    def zoom_camera_in(self):
        return ControlItem(self.settings.zoomCameraInFcBind)

    @property
    def zoom_camera_out(self):
        return ControlItem(self.settings.zoomCameraOutFcBind)

    @property
    def speed_boost_control(self):
        return ControlItem(self.settings.speedBoostCameraFcBind)

    @property
    def settings(self) -> ModuleDesignerSettings:
        return ModuleDesignerSettings()


class ModuleDesignerControls2d(Base2DControlScheme):
    def __init__(self, editor: ModuleDesigner, renderer: WalkmeshRenderer):
        self.settings: ModuleDesignerSettings = ModuleDesignerSettings()
        self._mode: _InstanceMode | _GeometryMode | _SpawnMode
        super().__init__(editor=editor, renderer=renderer, transform_state=editor.transform_state)
        self.editor: ModuleDesigner
        self.renderer: WalkmeshRenderer
        self._nav_helper = Viewport2DNavigationHelper(
            renderer,
            get_content_bounds=self._all_instance_bounds,
            get_selection_bounds=self._selected_instance_bounds,
            settings=self.settings,
        )

    def zoom_sensitivity(self) -> int:
        return ModuleDesignerSettings().zoomCameraSensitivity2d

    def on_mouse_scrolled(
        self,
        delta: Vector2,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
    ):
        if self._nav_helper.handle_mouse_scroll(delta, buttons, keys, zoom_sensitivity=self.zoom_sensitivity()):
            return
        self.handle_zoom_event(delta, buttons, keys, self.renderer.zoom_at_screen)

    def on_mouse_moved(
        self,
        screen: Vector2,
        screen_delta: Vector2,
        world: Vector2,
        world_delta: Vector2,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
    ):
        adjusted_world_delta: Vector2 = self.handle_camera_motion(
            screen,
            screen_delta,
            world_delta,
            buttons,
            keys,
            move_camera_callback=self._move_camera,
            rotate_camera_callback=self._rotate_camera,
            cursor_lock_callback=self.renderer.do_cursor_lock,
        )

        if self.editor.ui.lockInstancesCheck.isChecked():
            return
        if self.move_selected.satisfied(buttons, keys):
            if isinstance(self._mode, _GeometryMode):
                RobustLogger().debug("Move geometry point %s, %s", world_delta.x, world_delta.y)
                self._mode.move_selected(adjusted_world_delta.x, adjusted_world_delta.y)
                return

            # handle undo/redo for move_selected.
            if not self.editor.transform_state.is_drag_moving:
                RobustLogger().debug("move_selected instance in 2d")
                self.capture_move_transform(self.editor.selected_instances)
            self.editor.move_selected(adjusted_world_delta.x, adjusted_world_delta.y, no_undo_stack=True, no_z_coord=True)

        if self.rotate_selected.satisfied(buttons, keys) and isinstance(self._mode, _InstanceMode):
            if not self.editor.transform_state.is_drag_rotating:
                RobustLogger().debug("rotateSelected instance in 2d")
                selection: list[GITInstance] = self.editor.selected_instances  # noqa: SLF001
                self.capture_rotate_transform(
                    selection,
                    is_rotatable=self.editor._is_rotatable_instance,  # noqa: SLF001
                    get_rotation=self._get_instance_rotation,
                )
            self._mode.rotate_selected_to_point(world.x, world.y)

    def _move_camera(self, world_delta: Vector2) -> None:
        strength: float = self.settings.moveCameraSensitivity2d / 100
        self.renderer.camera.nudge_position(-world_delta.x * strength, -world_delta.y * strength)

    def _rotate_camera(self, screen_delta: Vector2) -> None:
        strength: float = self.settings.rotateCameraSensitivity2d / 100 / 50
        self.renderer.camera.nudge_rotation(screen_delta.x * strength)

    @staticmethod
    def _get_instance_rotation(instance: GITInstance):
        if isinstance(instance, GITCamera):
            return instance.orientation
        return instance.bearing

    def on_mouse_pressed(
        self,
        screen: Vector2,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
    ):
        world: Vector3 = self.renderer.to_world_coords(screen.x, screen.y)
        if self.duplicate_selected.satisfied(buttons, keys) and self.editor.selected_instances and isinstance(self._mode, _InstanceMode):
            self._mode.duplicate_selected(world)

        if self.select_underneath.satisfied(buttons, keys):
            if self._mode is not None and isinstance(self._mode, _GeometryMode):
                RobustLogger().debug("select_underneath_geometry?")
                self._mode.select_underneath()
            elif self.renderer.instances_under_mouse():
                RobustLogger().debug("on_mouse_pressed, select_underneath found one or more instances under mouse.")
                self.editor.set_selection([self.renderer.instances_under_mouse()[-1]])
            else:
                # Click on empty space: deselect and start marquee (drag will multi-select)
                self.editor.set_selection([])
                self.renderer.start_marquee(screen)

    def on_keyboard_pressed(
        self,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
    ):
        if self._nav_helper.handle_key_pressed(
            keys,
            buttons=buttons,
            pan_step=max(1.0, 48.0 / max(1.0, self.renderer.camera.zoom())),
        ):
            return

        if self.delete_selected.satisfied(buttons, keys):
            if isinstance(self._mode, _GeometryMode):
                self._mode.delete_selected()
            else:
                self.editor.delete_selected()
            return

        if self.snap_camera_to_selected.satisfied(buttons, keys):
            for instance in self.editor.selected_instances:
                self.renderer.snap_camera_to_point(instance.position)
                # Also sync 3D camera to the selected instance position
                self.editor.ui.mainRenderer.snap_camera_to_point(instance.position)
                break

        if self.frame_all_2d.satisfied(buttons, keys):
            self._frame_all_2d()
            return

        if self.toggle_instance_lock.satisfied(buttons, keys):
            self.editor.ui.lockInstancesCheck.setChecked(not self.editor.ui.lockInstancesCheck.isChecked())

    def _frame_all_2d(self) -> None:
        """Frame all visible GIT instances in the 2D flat renderer.

        Equivalent to Blender's Home key: centres the 2D camera on the
        module extents and adjusts zoom to fit.
        """
        if self.editor._module is None:  # noqa: SLF001
            return
        git = self.editor._module.git()  # noqa: SLF001
        if git is None:
            return
        res = git.resource()
        if res is None:
            return
        all_instances = list(res.instances())
        if not all_instances:
            return
        xs = [float(inst.position.x) for inst in all_instances]
        ys = [float(inst.position.y) for inst in all_instances]
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2
        w = max(1.0, max(xs) - min(xs))
        h = max(1.0, max(ys) - min(ys))
        # Fit the bounding box into the renderer viewport with 20 % padding
        padding = 1.2
        renderer_w = max(1, self.renderer.width())
        renderer_h = max(1, self.renderer.height())
        zoom_for_w = renderer_w / (w * padding)
        zoom_for_h = renderer_h / (h * padding)
        target_zoom = min(zoom_for_w, zoom_for_h)
        self.renderer.camera.set_position(cx, cy)
        self.renderer.camera.set_zoom(target_zoom)

    def _all_instance_bounds(self):
        if self.editor._module is None:  # noqa: SLF001
            return None
        git = self.editor._module.git()  # noqa: SLF001
        if git is None:
            return None
        res = git.resource()
        if res is None:
            return None
        return aabb_from_points((float(inst.position.x), float(inst.position.y)) for inst in res.instances())

    def _selected_instance_bounds(self):
        return aabb_from_points(
            (float(inst.position.x), float(inst.position.y))
            for inst in self.editor.selected_instances
        )

    def on_mouse_released(
        self,
        screen: Vector2,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
        released_button: Qt.MouseButton | None = None,
    ):
        if released_button == Qt.MouseButton.RightButton:
            world: Vector3 = self.renderer.to_world_coords(screen.x, screen.y)
            self.editor.on_context_menu(world, self.renderer.mapToGlobal(QPoint(int(screen.x), int(screen.y))))
        self.finalize_transform_actions()

    def on_keyboard_released(self, buttons: set[Qt.MouseButton], keys: set[Qt.Key]):
        self.finalize_transform_actions()

    @property
    def move_camera(self):
        return ControlItem(self.settings.moveCamera2dBind)

    @property
    def rotate_camera(self):
        return ControlItem(self.settings.rotateCamera2dBind)

    @property
    def zoom_camera(self):
        return ControlItem(self.settings.zoomCamera2dBind)

    @property
    def rotate_selected(self):
        return ControlItem(self.settings.rotateObject2dBind)

    @property
    def move_selected(self):
        return ControlItem(self.settings.moveObject2dBind)

    @property
    def select_underneath(self):
        return ControlItem(self.settings.selectObject2dBind)

    @property
    def delete_selected(self):
        return ControlItem(self.settings.deleteObject2dBind)

    @property
    def duplicate_selected(self):
        return ControlItem(self.settings.duplicateObject2dBind)

    @property
    def snap_camera_to_selected(self):
        return ControlItem(self.settings.moveCameraToSelected2dBind)

    @property
    def frame_all_2d(self):
        return ControlItem(self.settings.frameAll2dBind)

    @property
    def open_context_menu(self):
        return ControlItem((set(), {Qt.MouseButton.RightButton}))

    @property
    def toggle_instance_lock(self):
        return ControlItem(self.settings.toggleLockInstancesBind)
