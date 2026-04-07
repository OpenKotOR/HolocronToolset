"""Shared 2D control helpers for walkmesh-backed editors."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Sequence

from toolset.gui.common.interaction.camera import calculate_zoom_strength
from toolset.gui.common.interaction.transforms import TransformInteractionState
from utility.common.geometry import Vector2, Vector3

if TYPE_CHECKING:
    from pykotor.resource.generics.git import GITInstance, GITObject
    from toolset.data.misc import ControlItem
    from utility.common.geometry import Vector4


class Base2DControlScheme:
    """Common camera and transform-capture helpers for 2D editor controls."""

    def __init__(
        self,
        *,
        editor: object,
        renderer: object,
        transform_state: TransformInteractionState,
    ) -> None:
        self.editor: object = editor
        self.renderer: object = renderer
        self.transform_state: TransformInteractionState = transform_state

    @property
    def move_camera(self) -> ControlItem:
        raise NotImplementedError

    @property
    def rotate_camera(self) -> ControlItem:
        raise NotImplementedError

    @property
    def zoom_camera(self) -> ControlItem:
        raise NotImplementedError

    def zoom_sensitivity(self) -> int:
        raise NotImplementedError

    def handle_zoom_event(
        self,
        delta: Vector2,
        buttons: set,
        keys: set,
        zoom_callback: Callable[[float], None],
    ) -> None:
        if not self.zoom_camera.satisfied(buttons, keys):
            return
        if not delta.y:
            return
        zoom_factor: float = calculate_zoom_strength(delta.y, self.zoom_sensitivity())
        zoom_callback(zoom_factor)

    def handle_camera_motion(
        self,
        screen: Vector2,
        screen_delta: Vector2,
        world_delta: Vector2,
        buttons: set,
        keys: set,
        *,
        move_camera_callback: Callable[[Vector2], None],
        rotate_camera_callback: Callable[[Vector2], None],
        cursor_lock_callback: Callable[[Vector2], None],
    ) -> Vector2:
        should_move_camera: bool = self.move_camera.satisfied(buttons, keys)
        should_rotate_camera: bool = self.rotate_camera.satisfied(buttons, keys)
        adjusted_world_delta: Vector2 = world_delta
        if should_move_camera or should_rotate_camera:
            cursor_lock_callback(screen)
            adjusted_world_delta = Vector2(-world_delta.x, -world_delta.y)
        if should_move_camera:
            move_camera_callback(world_delta)
        if should_rotate_camera:
            rotate_camera_callback(screen_delta)
        return adjusted_world_delta

    def capture_move_transform(self, selection: Sequence[GITObject]) -> None:
        if self.transform_state.is_drag_moving:
            return
        self.transform_state.initial_positions = {
            instance: Vector3(*instance.position) for instance in selection
        }
        self.transform_state.is_drag_moving = True

    def capture_rotate_transform(
        self,
        selection: Sequence[GITInstance],
        *,
        is_rotatable: Callable[[GITObject], bool],
        get_rotation: Callable[[GITInstance], float | Vector4],
    ) -> None:
        if self.transform_state.is_drag_rotating:
            return
        self.transform_state.is_drag_rotating = True
        for instance in selection:
            if not is_rotatable(instance):
                continue
            self.transform_state.initial_rotations[instance] = get_rotation(instance)

    def finalize_transform_actions(self) -> None:
        self.transform_state.finalize_undo_actions()
