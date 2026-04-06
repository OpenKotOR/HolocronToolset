"""Shared 2D renderer infrastructure for map-like editor canvases."""

from __future__ import annotations

import math

from typing import TYPE_CHECKING, ClassVar

import qtpy

from qtpy.QtCore import QPoint, QPointF, QTimer, Qt, Signal
from qtpy.QtGui import QColor, QCursor, QPainter, QPen, QTransform
from qtpy.QtWidgets import QApplication, QWidget

from toolset.gui.common.map_camera import MapCamera
from toolset.gui.common.marquee import (
    MARQUEE_MOVE_THRESHOLD_PIXELS,
    draw_marquee_rect,
)
from toolset.utils.misc import keyboard_modifiers_to_qt_keys
from utility.common.geometry import Vector2, Vector3

if TYPE_CHECKING:
    from qtpy.QtGui import QFocusEvent, QKeyEvent, QMouseEvent, QPaintEvent, QWheelEvent


class Base2DMapRenderer(QWidget):
    """Common camera, transform, grid, marquee, and render-loop infrastructure."""

    sig_mouse_moved: ClassVar[Signal] = Signal(object, object, object, object)  # pyright: ignore[reportPrivateImportUsage]
    sig_mouse_scrolled: ClassVar[Signal] = Signal(object, object, object)  # pyright: ignore[reportPrivateImportUsage]
    sig_mouse_released: ClassVar[Signal] = Signal(object, object, object, object)  # pyright: ignore[reportPrivateImportUsage]
    sig_mouse_pressed: ClassVar[Signal] = Signal(object, object, object)  # pyright: ignore[reportPrivateImportUsage]
    sig_marquee_select: ClassVar[Signal] = Signal(object, object)  # pyright: ignore[reportPrivateImportUsage]
    sig_key_pressed: ClassVar[Signal] = Signal(object, object)  # pyright: ignore[reportPrivateImportUsage]
    sig_key_released: ClassVar[Signal] = Signal(object, object)  # pyright: ignore[reportPrivateImportUsage]

    def __init__(
        self,
        parent: QWidget | None,
        *,
        min_zoom: float,
        max_zoom: float,
        transform_y_scale: float,
        flip_screen_y_for_world: bool,
        world_rotation_sign: float,
        world_delta_y_sign: float,
        render_interval_ms: int,
        always_repaint: bool,
        background_color: QColor | None = None,
    ) -> None:
        super().__init__(parent)
        self.camera: MapCamera = MapCamera(min_zoom=min_zoom, max_zoom=max_zoom)
        self.show_grid: bool = False
        self.grid_size: float = 1.0
        self._mouse_prev: Vector2 = Vector2.from_null()
        self._keys_down: set[int | Qt.Key] = set()
        self._mouse_down: set[int | Qt.MouseButton] = set()
        self._marquee_active: bool = False
        self._marquee_start: Vector2 = Vector2.from_null()
        self._marquee_end: Vector2 = Vector2.from_null()
        self._dirty: bool = True
        self._always_repaint: bool = always_repaint
        self._background_color: QColor = background_color or QColor(0, 0, 0, 255)
        self._transform_y_scale: float = transform_y_scale
        self._flip_screen_y_for_world: bool = flip_screen_y_for_world
        self._world_rotation_sign: float = world_rotation_sign
        self._world_delta_y_sign: float = world_delta_y_sign
        self._render_timer: QTimer = QTimer(self)
        self._render_timer.timeout.connect(self._on_render_timer)
        self._render_timer.setInterval(render_interval_ms)
        self._render_timer.start()
        self.destroyed.connect(self._on_destroyed)

    def keys_down(self) -> set[int | Qt.Key]:
        return self._keys_down

    def mouse_down(self) -> set[int | Qt.MouseButton]:
        return self._mouse_down

    def mark_dirty(self) -> None:
        self._dirty = True

    def reset_buttons_down(self) -> None:
        self._mouse_down.clear()

    def reset_keys_down(self) -> None:
        self._keys_down.clear()

    def reset_all_down(self) -> None:
        self._mouse_down.clear()
        self._keys_down.clear()

    def snap_camera_to_point(
        self,
        point: Vector2 | Vector3,
        zoom: int = 8,
    ) -> None:
        self.camera.set_position(point.x, point.y)
        self.camera.set_zoom(float(zoom))
        self.mark_dirty()

    def mouse_screen(self) -> Vector2:
        return self._mouse_prev.copy()

    def zoom_at_screen(self, zoom_factor: float, screen_pos: Vector2 | None = None) -> None:
        """Zoom toward the current mouse position using shared cursor-centered behavior."""
        target_screen = self._mouse_prev.copy() if screen_pos is None else screen_pos
        world = self.to_world_coords(target_screen.x, target_screen.y)
        self.camera.zoom_to_point(zoom_factor, world.x, world.y)
        self.mark_dirty()

    def do_cursor_lock(self, mutable_screen: Vector2) -> None:
        """Reset the cursor to the previous screen position during drag-camera operations."""
        global_old_pos: QPoint = self.mapToGlobal(
            QPoint(int(self._mouse_prev.x), int(self._mouse_prev.y))
        )
        QCursor.setPos(global_old_pos)
        local_old_pos: QPoint = self.mapFromGlobal(QPoint(global_old_pos.x(), global_old_pos.y()))
        mutable_screen.x = local_old_pos.x()
        mutable_screen.y = local_old_pos.y()

    def to_render_coords(self, x: float, y: float) -> Vector2:
        cos_theta: float = math.cos(self.camera.rotation())
        sin_theta: float = math.sin(self.camera.rotation())
        camera_position: Vector2 = self.camera.position()
        x -= camera_position.x
        y -= camera_position.y
        x2: float = (x * cos_theta - y * sin_theta) * self.camera.zoom() + self.width() / 2
        y2: float = (x * sin_theta + y * cos_theta) * self.camera.zoom() + self.height() / 2
        return Vector2(x2, y2)

    def to_world_coords(self, x: float, y: float) -> Vector3:
        if self._flip_screen_y_for_world:
            y = self.height() - y
        rotation: float = self.camera.rotation() * self._world_rotation_sign
        cos_theta: float = math.cos(rotation)
        sin_theta: float = math.sin(rotation)
        x = (x - self.width() / 2) / self.camera.zoom()
        y = (y - self.height() / 2) / self.camera.zoom()
        camera_position: Vector2 = self.camera.position()
        x2: float = x * cos_theta - y * sin_theta + camera_position.x
        y2: float = x * sin_theta + y * cos_theta + camera_position.y
        z_value: float = self.get_z_coord(x2, y2)
        return Vector3(x2, y2, z_value)

    def to_world_delta(self, x: float, y: float) -> Vector2:
        rotation: float = -self.camera.rotation()
        cos_theta: float = math.cos(rotation)
        sin_theta: float = math.sin(rotation)
        x /= self.camera.zoom()
        y /= self.camera.zoom()
        x2: float = x * cos_theta - y * sin_theta
        y2: float = x * sin_theta + y * cos_theta
        return Vector2(x2, y2 * self._world_delta_y_sign)

    def get_z_coord(self, x: float, y: float) -> float:
        return 0.0

    def _current_palette(self):
        app = QApplication.instance()
        if app is None or not isinstance(app, QApplication):
            return None
        return app.palette()

    def _grid_color(self) -> QColor:
        return QColor(90, 90, 90)

    def _grid_pen_width(self) -> float:
        return 1 / self.camera.zoom()

    def _create_world_transform(self) -> QTransform:
        transform: QTransform = QTransform()
        transform.translate(self.width() / 2, self.height() / 2)
        transform.rotate(math.degrees(self.camera.rotation()))
        transform.scale(self.camera.zoom(), self._transform_y_scale * self.camera.zoom())
        camera_position: Vector2 = self.camera.position()
        transform.translate(-camera_position.x, -camera_position.y)
        return transform

    def _apply_transformation(self) -> QTransform:
        return self._create_world_transform()

    def _fill_background(self, painter: QPainter) -> None:
        painter.setBrush(self._background_color)
        painter.drawRect(0, 0, self.width(), self.height())

    def _draw_grid(self, painter: QPainter) -> None:
        if not self.show_grid or self.grid_size <= 0:
            return
        top_left: Vector3 = self.to_world_coords(0, 0)
        bottom_right: Vector3 = self.to_world_coords(self.width(), self.height())
        min_x: float = math.floor(min(top_left.x, bottom_right.x) / self.grid_size) * self.grid_size
        max_x: float = math.ceil(max(top_left.x, bottom_right.x) / self.grid_size) * self.grid_size
        min_y: float = math.floor(min(top_left.y, bottom_right.y) / self.grid_size) * self.grid_size
        max_y: float = math.ceil(max(top_left.y, bottom_right.y) / self.grid_size) * self.grid_size
        painter.setPen(QPen(self._grid_color(), self._grid_pen_width()))
        x_value: float = min_x
        while x_value <= max_x:
            painter.drawLine(QPointF(x_value, min_y), QPointF(x_value, max_y))
            x_value += self.grid_size
        y_value: float = min_y
        while y_value <= max_y:
            painter.drawLine(QPointF(min_x, y_value), QPointF(max_x, y_value))
            y_value += self.grid_size

    def start_marquee(self, screen_pos: Vector2) -> None:
        self._marquee_active = True
        self._marquee_start = screen_pos
        self._marquee_end = screen_pos
        self.mark_dirty()

    def _draw_marquee(self, painter: QPainter) -> None:
        if not self._marquee_active:
            return
        painter.save()
        painter.resetTransform()
        draw_marquee_rect(painter, self._marquee_start, self._marquee_end)
        painter.restore()

    def _end_marquee_and_emit(self, additive: bool) -> None:
        if not self._marquee_active:
            return
        self._marquee_active = False
        if self._marquee_start.distance(self._marquee_end) <= MARQUEE_MOVE_THRESHOLD_PIXELS:
            self.mark_dirty()
            return
        start_world: Vector3 = self.to_world_coords(self._marquee_start.x, self._marquee_start.y)
        end_world: Vector3 = self.to_world_coords(self._marquee_end.x, self._marquee_end.y)
        min_x: float = min(start_world.x, end_world.x)
        max_x: float = max(start_world.x, end_world.x)
        min_y: float = min(start_world.y, end_world.y)
        max_y: float = max(start_world.y, end_world.y)
        self.sig_marquee_select.emit((min_x, min_y, max_x, max_y), additive)
        self.mark_dirty()

    def _event_coords(self, event: QMouseEvent) -> Vector2:
        if qtpy.QT5:
            return Vector2(event.x(), event.y())  # pyright: ignore[reportAttributeAccessIssue]
        point: QPoint = event.position().toPoint()
        return Vector2(point.x(), point.y())

    def _on_destroyed(self) -> None:
        if hasattr(self, "_render_timer"):
            self._render_timer.stop()

    def _on_render_timer(self) -> None:
        try:
            if not self.isVisible() and self.parent() is None:
                self._render_timer.stop()
                return
        except RuntimeError:
            self._render_timer.stop()
            return
        try:
            if self._always_repaint or self._dirty:
                self.repaint()
                self._dirty = False
        except (RuntimeError, AttributeError):
            self._render_timer.stop()

    def wheelEvent(self, e: QWheelEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        keys_to_emit: set[int | Qt.Key] = self._keys_down | keyboard_modifiers_to_qt_keys(
            e.modifiers()
        )
        self.sig_mouse_scrolled.emit(
            Vector2(e.angleDelta().x(), e.angleDelta().y()), self._mouse_down, keys_to_emit
        )
        self.mark_dirty()

    def mouseMoveEvent(self, e: QMouseEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        super().mouseMoveEvent(e)
        coords: Vector2 = self._event_coords(e)
        coords_delta: Vector2 = Vector2(
            coords.x - self._mouse_prev.x, coords.y - self._mouse_prev.y
        )
        self.sig_mouse_moved.emit(coords, coords_delta, self._mouse_down, self._keys_down)
        self._mouse_prev = coords
        if self._marquee_active:
            if Qt.MouseButton.LeftButton not in self._mouse_down:
                self._end_marquee_and_emit(additive=False)
                return
            self._marquee_end = coords
            self.mark_dirty()

    def mousePressEvent(self, e: QMouseEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        super().mousePressEvent(e)
        button: int | Qt.MouseButton = e.button()
        self._mouse_down.add(button)
        coords: Vector2 = self._event_coords(e)
        self.sig_mouse_pressed.emit(coords, self._mouse_down, self._keys_down)
        self.mark_dirty()

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        super().mouseReleaseEvent(e)
        button: int | Qt.MouseButton = e.button()
        self._mouse_down.discard(button)
        coords: Vector2 = self._event_coords(e)
        if self._marquee_active and button == Qt.MouseButton.LeftButton:
            additive: bool = Qt.Key.Key_Shift in self._keys_down
            self._end_marquee_and_emit(additive=additive)
        self.sig_mouse_released.emit(coords, self._mouse_down, self._keys_down, button)
        self.mark_dirty()

    def keyPressEvent(self, e: QKeyEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        super().keyPressEvent(e)
        key: int = e.key()
        if key == Qt.Key.Key_Escape and self._marquee_active:
            self._marquee_active = False
            self.mark_dirty()
            return
        self._keys_down.add(key)
        if self.underMouse():
            self.sig_key_pressed.emit(self._mouse_down, self._keys_down)
        self.mark_dirty()

    def keyReleaseEvent(self, e: QKeyEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        super().keyReleaseEvent(e)
        key: int = e.key()
        self._keys_down.discard(key)
        if self.underMouse():
            self.sig_key_released.emit(self._mouse_down, self._keys_down)
        self.mark_dirty()

    def focusOutEvent(self, e: QFocusEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if self._marquee_active:
            self._marquee_active = False
            self.mark_dirty()
        self.reset_all_down()
        super().focusOutEvent(e)

    def paintEvent(self, e: QPaintEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        painter: QPainter = QPainter(self)
        self._fill_background(painter)
        painter.setTransform(self._create_world_transform())
        self._draw_grid(painter)
        self._draw_marquee(painter)
