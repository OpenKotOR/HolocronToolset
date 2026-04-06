from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any

from qtpy.QtCore import Qt

from toolset.data.misc import ControlItem
from toolset.gui.common.interaction.camera import calculate_zoom_strength

if TYPE_CHECKING:
    from utility.common.geometry import Vector2


AABB2D = tuple[float, float, float, float]


def aabb_from_points(points: Iterable[tuple[float, float]]) -> AABB2D | None:
    point_list = list(points)
    if not point_list:
        return None
    xs = [point[0] for point in point_list]
    ys = [point[1] for point in point_list]
    return min(xs), min(ys), max(xs), max(ys)


def zoom_to_fit_aabb(renderer: Any, aabb: AABB2D, *, padding: float = 0.15) -> None:
    min_x, min_y, max_x, max_y = aabb
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    world_width = max(max_x - min_x, 1.0) * (1.0 + padding * 2.0)
    world_height = max(max_y - min_y, 1.0) * (1.0 + padding * 2.0)
    screen_width = renderer.width() or 520
    screen_height = renderer.height() or 507
    zoom = min(screen_width / world_width, screen_height / world_height)
    renderer.camera.set_position(center_x, center_y)
    renderer.camera.set_zoom(zoom)
    renderer.mark_dirty()


class Viewport2DNavigationHelper:
    def __init__(
        self,
        renderer: Any,
        *,
        get_content_bounds: Callable[[], AABB2D | None],
        get_selection_bounds: Callable[[], AABB2D | None] | None = None,
        settings: object | None = None,
    ) -> None:
        self.renderer = renderer
        self._get_content_bounds = get_content_bounds
        self._get_selection_bounds = get_selection_bounds
        self._settings = settings

    def _bind(
        self, attr_name: str, default: tuple[set[Qt.Key], set[Qt.MouseButton] | None]
    ) -> ControlItem:
        bind = (
            getattr(self._settings, attr_name, default) if self._settings is not None else default
        )
        return ControlItem(bind)

    def frame_all(self) -> bool:
        bounds = self._get_content_bounds()
        if bounds is None:
            return False
        zoom_to_fit_aabb(self.renderer, bounds)
        return True

    def frame_selected(self) -> bool:
        if self._get_selection_bounds is None:
            return self.frame_all()
        bounds = self._get_selection_bounds()
        if bounds is None:
            return self.frame_all()
        zoom_to_fit_aabb(self.renderer, bounds)
        return True

    def reset_view(self) -> bool:
        return self.frame_all()

    def handle_mouse_scroll(
        self,
        delta: Vector2,
        buttons: set[int] | set[Qt.MouseButton],
        keys: set[int] | set[Qt.Key],
        *,
        zoom_sensitivity: int,
    ) -> bool:
        if not delta.y:
            return False
        if not self._bind("zoomCamera2dBind", (set(), set())).satisfied(buttons, keys):
            return False
        self.renderer.zoom_at_screen(calculate_zoom_strength(delta.y, zoom_sensitivity))
        return True

    def handle_key_pressed(
        self,
        keys: set[int] | set[Qt.Key],
        *,
        pan_step: float,
        buttons: set[int] | set[Qt.MouseButton] | None = None,
    ) -> bool:
        active_buttons: set[int] | set[Qt.MouseButton] = set() if buttons is None else buttons

        if self._bind("frameAll2dBind", ({Qt.Key.Key_Home}, set())).satisfied(active_buttons, keys):
            return self.frame_all()
        if self._bind("moveCameraToSelected2dBind", ({Qt.Key.Key_Period}, set())).satisfied(
            active_buttons, keys
        ):
            return self.frame_selected()
        if self._bind(
            "resetCameraView2dBind", ({Qt.Key.Key_Control, Qt.Key.Key_0}, set())
        ).satisfied(active_buttons, keys):
            return self.reset_view()
        if self._bind("zoomCameraIn2dBind", ({Qt.Key.Key_Equal}, None)).satisfied(
            active_buttons, keys
        ):
            self.renderer.zoom_at_screen(1.25)
            return True
        if self._bind("zoomCameraOut2dBind", ({Qt.Key.Key_Minus}, None)).satisfied(
            active_buttons, keys
        ):
            self.renderer.zoom_at_screen(0.8)
            return True
        if self._bind("moveCameraLeft2dBind", ({Qt.Key.Key_Left}, None)).satisfied(
            active_buttons, keys
        ):
            self.renderer.camera.nudge_position(-pan_step, 0.0)
            self.renderer.mark_dirty()
            return True
        if self._bind("moveCameraRight2dBind", ({Qt.Key.Key_Right}, None)).satisfied(
            active_buttons, keys
        ):
            self.renderer.camera.nudge_position(pan_step, 0.0)
            self.renderer.mark_dirty()
            return True
        if self._bind("moveCameraUp2dBind", ({Qt.Key.Key_Up}, None)).satisfied(
            active_buttons, keys
        ):
            self.renderer.camera.nudge_position(0.0, pan_step)
            self.renderer.mark_dirty()
            return True
        if self._bind("moveCameraDown2dBind", ({Qt.Key.Key_Down}, None)).satisfied(
            active_buttons, keys
        ):
            self.renderer.camera.nudge_position(0.0, -pan_step)
            self.renderer.mark_dirty()
            return True
        return False
