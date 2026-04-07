"""GIT editor controls: key bindings and mode switching."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import qtpy

from qtpy.QtCore import Qt

from loggerplus import RobustLogger  # pyright: ignore[reportMissingTypeStubs]
from pykotor.resource.generics.git import (
    GITCamera,
    GITCreature,
    GITDoor,
    GITPlaceable,
    GITStore,
    GITWaypoint,
)
from toolset.data.misc import ControlItem
from toolset.gui.common.base_2d_controls import Base2DControlScheme
from toolset.gui.common.viewport_2d_nav import Viewport2DNavigationHelper, aabb_from_points
from toolset.gui.widgets.settings.editor_settings.git import GITSettings
from toolset.gui.widgets.settings.widgets.module_designer import ModuleDesignerSettings
from utility.common.geometry import Vector2, Vector3

if qtpy.QT5:
    from qtpy.QtWidgets import QUndoStack
elif qtpy.QT6:
    from qtpy.QtGui import QUndoStack

if TYPE_CHECKING:
    from pykotor.resource.generics.git import (
        GITInstance,
        GITObject,
    )
    from toolset.gui.editors.git.git import GITEditor
    from utility.common.geometry import Vector4


from toolset.gui.common.interaction.transforms import TransformInteractionState


class GITControlScheme(Base2DControlScheme):
    _ROTATABLE_INSTANCE_TYPES: tuple[type[GITObject], ...] = (
        GITCamera,
        GITCreature,
        GITDoor,
        GITPlaceable,
        GITStore,
        GITWaypoint,
    )

    def __init__(self, editor: GITEditor):
        self.settings: GITSettings = GITSettings()
        self.undo_stack: QUndoStack = QUndoStack(editor)
        transform_state: TransformInteractionState = TransformInteractionState(
            self.undo_stack, editor
        )
        super().__init__(
            editor=editor, renderer=editor.ui.renderArea, transform_state=transform_state
        )
        self.editor: GITEditor
        self.renderer = editor.ui.renderArea
        self._nav_helper = Viewport2DNavigationHelper(
            self.renderer,
            get_content_bounds=lambda: aabb_from_points(
                (inst.position.x, inst.position.y) for inst in self.editor._git.instances()
            ),
            get_selection_bounds=lambda: aabb_from_points(
                (inst.position.x, inst.position.y)
                for inst in self.renderer.instance_selection.all()
            ),
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
        if self._nav_helper.handle_mouse_scroll(
            delta, buttons, keys, zoom_sensitivity=self.zoom_sensitivity()
        ):
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
        # sourcery skip: extract-duplicate-method, remove-redundant-if, split-or-ifs
        from toolset.gui.editors.git.mode import _InstanceMode, _SpawnMode

        is_instance_mode: bool = isinstance(self.editor._mode, _InstanceMode)  # noqa: SLF001
        is_spawn_mode: bool = isinstance(self.editor._mode, _SpawnMode)  # noqa: SLF001

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

        if self.move_selected.satisfied(buttons, keys):
            if not self.transform_state.is_drag_moving and is_instance_mode:
                selection: list[GITObject] = self.editor._mode.renderer2d.instance_selection.all()  # noqa: SLF001
                self.capture_move_transform(selection)
            if not self.transform_state.is_drag_moving_spawn and is_spawn_mode:
                sp_selection = self.editor._mode.renderer2d.spawn_selection.all()  # noqa: SLF001
                self.transform_state.initial_spawn_positions = {
                    sp_ref.spawn: Vector3(sp_ref.spawn.x, sp_ref.spawn.y, sp_ref.spawn.z)
                    for sp_ref in sp_selection
                }
                self.transform_state.is_drag_moving_spawn = True
            self.editor.move_selected(adjusted_world_delta.x, adjusted_world_delta.y)
        if self.rotate_selected_to_point.satisfied(buttons, keys):
            if (
                not self.transform_state.is_drag_rotating
                and not self.editor.ui.lockInstancesCheck.isChecked()
                and is_instance_mode
            ):
                RobustLogger().debug("rotateSelected instance in GITControlScheme")
                selection = self.editor._mode.renderer2d.instance_selection.all()  # noqa: SLF001
                self.capture_rotate_transform(
                    cast("list[GITInstance]", selection),
                    is_rotatable=self._is_rotatable_instance,
                    get_rotation=self._get_instance_rotation,
                )
            if not self.transform_state.is_drag_rotating_spawn and is_spawn_mode:
                sp_selection = self.editor._mode.renderer2d.spawn_selection.all()  # noqa: SLF001
                self.transform_state.initial_spawn_rotations = {
                    sp_ref.spawn: float(sp_ref.spawn.orientation) for sp_ref in sp_selection
                }
                self.transform_state.is_drag_rotating_spawn = True
            self.editor.rotate_selected_to_point(world.x, world.y)

    def _move_camera(self, world_delta: Vector2) -> None:
        move_sens: float = ModuleDesignerSettings().moveCameraSensitivity2d / 100
        self.editor.move_camera(-world_delta.x * move_sens, -world_delta.y * move_sens)

    @staticmethod
    def _is_rotatable_instance(instance: GITObject) -> bool:
        """Return whether this instance supports rotation editing."""
        return isinstance(instance, GITControlScheme._ROTATABLE_INSTANCE_TYPES)

    @staticmethod
    def _get_instance_rotation(instance: GITInstance) -> float | Vector4:
        """Return the current rotation payload for transform-undo capture."""
        if isinstance(instance, GITCamera):
            return instance.orientation
        return instance.bearing

    def _rotate_camera(self, screen_delta: Vector2) -> None:
        delta_magnitude = abs(screen_delta.x)
        direction = -1 if screen_delta.x < 0 else 1 if screen_delta.x > 0 else 0
        rotate_sens = ModuleDesignerSettings().rotateCameraSensitivity2d / 1000
        rotate_amount = delta_magnitude * rotate_sens * direction
        self.editor.rotate_camera(rotate_amount)

    def handle_undo_redo_from_long_action_finished(self):
        self.finalize_transform_actions()

    def on_mouse_pressed(self, screen: Vector2, buttons: set[Qt.MouseButton], keys: set[Qt.Key]):
        if self.duplicate_selected.satisfied(buttons, keys):
            position = self.editor.ui.renderArea.to_world_coords(screen.x, screen.y)
            self.editor.duplicate_selected(position)
        elif self.select_underneath.satisfied(buttons, keys):
            if self.editor.ui.renderArea.instances_under_mouse():
                self.editor.select_underneath()
            else:
                self.editor.ui.renderArea.start_marquee(screen)

    def on_mouse_released(
        self,
        screen: Vector2,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
    ):
        self.handle_undo_redo_from_long_action_finished()

    def on_keyboard_pressed(
        self,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
    ):
        from toolset.gui.editors.git.mode import _InstanceMode, _SpawnMode
        from toolset.gui.editors.git.undo import DeleteCommand, SpawnPointDeleteCommand

        if self.delete_selected.satisfied(buttons, keys):
            is_instance_mode = isinstance(self.editor._mode, _InstanceMode)  # noqa: SLF001
            is_spawn_mode = isinstance(self.editor._mode, _SpawnMode)  # noqa: SLF001
            if is_instance_mode:
                selection = self.editor._mode.renderer2d.instance_selection.all()  # noqa: SLF001
                if isinstance(selection, list):
                    self.undo_stack.push(
                        DeleteCommand(
                            self.editor._git, cast("list[GITObject]", selection.copy()), self.editor
                        )
                    )  # noqa: SLF001
            elif is_spawn_mode:
                sp_ref = self.editor._mode.renderer2d.spawn_selection.last()  # noqa: SLF001
                if sp_ref is not None and sp_ref.spawn in sp_ref.encounter.spawn_points:
                    self.undo_stack.push(
                        SpawnPointDeleteCommand(sp_ref.encounter, sp_ref.spawn, self.editor)
                    )
            self.editor.delete_selected(no_undo_stack=True)

        if self.toggle_instance_lock.satisfied(buttons, keys):
            self.editor.ui.lockInstancesCheck.setChecked(
                not self.editor.ui.lockInstancesCheck.isChecked()
            )

        if self._nav_helper.handle_key_pressed(
            keys, buttons=buttons, pan_step=ModuleDesignerSettings().moveCameraSensitivity2d / 10
        ):
            return

    def on_keyboard_released(
        self,
        buttons: set[Qt.MouseButton],
        keys: set[Qt.Key],
    ):
        self.handle_undo_redo_from_long_action_finished()

    # Use @property decorators to allow users to change settings without restarting the editor.
    @property
    def pan_camera(self) -> ControlItem:
        return ControlItem(self.settings.moveCameraBind)

    @property
    def rotate_camera(self) -> ControlItem:
        return ControlItem(self.settings.rotateCameraBind)

    @property
    def zoom_camera(self) -> ControlItem:
        return ControlItem(self.settings.zoomCameraBind)

    @property
    def rotate_selected_to_point(self) -> ControlItem:
        return ControlItem(self.settings.rotateSelectedToPointBind)

    @property
    def move_selected(self) -> ControlItem:
        return ControlItem(self.settings.moveSelectedBind)

    @property
    def select_underneath(self) -> ControlItem:
        return ControlItem(self.settings.selectUnderneathBind)

    @property
    def delete_selected(self) -> ControlItem:
        return ControlItem(self.settings.deleteSelectedBind)

    @property
    def duplicate_selected(self) -> ControlItem:
        return ControlItem(self.settings.duplicateSelectedBind)

    @property
    def toggle_instance_lock(self) -> ControlItem:
        return ControlItem(self.settings.toggleLockInstancesBind)
