"""Blender-style orientation / view compass gizmo overlay for 3-D viewports.

The compass widget is a small QWidget that overlays one corner of a 3-D
renderer.  It shows the six world-axis directions (+X/-X, +Y/-Y, +Z/-Z) as
coloured circles rendered with QPainter.  The position of each dot changes in
real-time as the camera orbits, giving the user a constant reminder of world
orientation.  Clicking a dot snaps the camera to the corresponding orthographic
view angle.

Coordinate conventions (same as the GL camera in
``pykotor.gl.scene.camera``):
  * World X  = right  (red)
  * World Y  = forward / "north"  (green)
  * World Z  = up  (blue)
  * Positive pitch ≈ 0        → bottom view (camera below scene, looking up)
  * Positive pitch ≈ π        → top view (camera above scene, looking down)
  * pitch = π/2               → horizontal views
"""

from __future__ import annotations

import math

from typing import TYPE_CHECKING, Callable

from qtpy.QtCore import QPoint, QRect, QSize, QTimer, Qt, Signal
from qtpy.QtGui import QColor, QFont, QPainter, QPen
from qtpy.QtWidgets import QWidget

if TYPE_CHECKING:
    from qtpy.QtGui import QMouseEvent, QPaintEvent, QResizeEvent


# ---------------------------------------------------------------------------
# Axis definitions
# ---------------------------------------------------------------------------

# Each entry: (axis_id, world_direction (x,y,z), front_color, back_color, snap_yaw, snap_pitch)
# snap_yaw and snap_pitch match the values used in designer_controls.py numpad snaps.
_AXES: list[tuple[str, tuple[float, float, float], QColor, QColor, float, float]] = [
    ("+X", (1.0, 0.0, 0.0), QColor(220, 60, 60), QColor(110, 30, 30), 0.0, math.pi / 2),
    ("-X", (-1.0, 0.0, 0.0), QColor(110, 30, 30), QColor(70, 15, 15), math.pi, math.pi / 2),
    ("+Y", (0.0, 1.0, 0.0), QColor(60, 200, 60), QColor(30, 100, 30), -math.pi / 2, math.pi / 2),
    ("-Y", (0.0, -1.0, 0.0), QColor(30, 100, 30), QColor(15, 50, 15), math.pi / 2, math.pi / 2),
    ("+Z", (0.0, 0.0, 1.0), QColor(80, 120, 220), QColor(40, 60, 110), 0.0, 0.01),
    ("-Z", (0.0, 0.0, -1.0), QColor(40, 60, 110), QColor(20, 30, 55), 0.0, math.pi - 0.01),
]

# Radius of the full compass circle (as fraction of widget half-size).
_COMPASS_RADIUS = 0.82
# Radius of each axis dot.
_DOT_RADIUS = 0.18
# Text font size (in pixels, relative to widget size).
_LABEL_FONT_FRACTION = 0.20


def _project_axis(
    dx: float,
    dy: float,
    dz: float,
    yaw: float,
    pitch: float,
) -> tuple[float, float, float]:
    """Project a world-space direction (dx,dy,dz) onto the screen plane.

    Returns (screen_x, screen_y, depth) where:
      * screen_x > 0  → right side of the compass
      * screen_y > 0  → bottom of the compass (widget Y-down convention)
      * depth > 0     → axis faces *toward* the viewer (draw on top)

    Math derivation (see module docstring):
      Camera world matrix rotation columns from
      ``Rz(yaw+π/2) * Rx(π-pitch)``::

        col0 (right) = (-sin_yaw,  cos_yaw, 0)
        col1 (up)    = ( cos_pitch*cos_yaw,  cos_pitch*sin_yaw,  sin_pitch)
        col2 (back)  = ( sin_pitch*cos_yaw,  sin_pitch*sin_yaw, -cos_pitch)

    Screen projection:
      screen_x =  dot(d, right)
      screen_y = -dot(d, up)      (negate: widget Y increases downward)
      depth    =  dot(d, back)    (positive = toward viewer)
    """
    cos_yaw = math.cos(yaw)
    sin_yaw = math.sin(yaw)
    cos_pitch = math.cos(pitch)
    sin_pitch = math.sin(pitch)

    # camera right column
    rx = -sin_yaw
    ry = cos_yaw
    rz = 0.0

    # camera up column
    ux = cos_pitch * cos_yaw
    uy = cos_pitch * sin_yaw
    uz = sin_pitch

    # camera back column (points FROM scene TOWARD camera → positive = facing viewer)
    bx = sin_pitch * cos_yaw
    by = sin_pitch * sin_yaw
    bz = -cos_pitch

    sx = dx * rx + dy * ry + dz * rz
    sy = -(dx * ux + dy * uy + dz * uz)
    depth = dx * bx + dy * by + dz * bz

    return sx, sy, depth


class ViewCompassWidget(QWidget):
    """Blender-style orientation gizmo overlay.

    Usage::

        compass = ViewCompassWidget(renderer_widget)
        compass.set_camera_source(lambda: (renderer.scene.camera.yaw,
                                            renderer.scene.camera.pitch))
        compass.sig_snap_view.connect(controls.apply_numpad_view)

    The widget is a *child* of *renderer_widget* and is positioned in the
    top-right corner automatically.  Call :meth:`update_position` whenever
    the parent is resized.
    """

    #: Emitted when an axis is clicked.  Arguments: yaw (float), pitch (float).
    sig_snap_view: Signal = Signal(float, float)  # pyright: ignore[reportPrivateImportUsage]

    # Widget dimensions (square)
    _SIZE = 96  # pixels

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setFixedSize(QSize(self._SIZE, self._SIZE))
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._yaw: float = 0.0
        self._pitch: float = math.pi / 2
        # Optional callable: () -> (yaw, pitch)
        self._camera_source: Callable[[], tuple[float, float]] | None = None
        self._hovered_axis: str | None = None
        self._last_parent_size: tuple[int, int] = (-1, -1)

        # Repaint timer — runs at ~30 Hz to keep the gizmo in sync with the camera.
        self._repaint_timer: QTimer = QTimer(self)
        self._repaint_timer.setInterval(50)
        self._repaint_timer.timeout.connect(self._on_timer)
        self._repaint_timer.start()

        self.update_position()
        self.raise_()
        self.show()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_camera_source(self, fn: Callable[[], tuple[float, float]]) -> None:
        """Provide a callable that returns ``(yaw, pitch)`` from the live camera."""
        self._camera_source = fn

    def refresh(self) -> None:
        """Pull latest camera orientation and repaint."""
        old_yaw = self._yaw
        old_pitch = self._pitch
        if self._camera_source is not None:
            try:
                self._yaw, self._pitch = self._camera_source()
            except Exception:  # noqa: BLE001
                pass
        if abs(self._yaw - old_yaw) > 1e-4 or abs(self._pitch - old_pitch) > 1e-4:
            self.update()

    def update_position(self) -> None:
        """Reposition the widget in the top-right corner of the parent widget."""
        parent = self.parent()
        if not isinstance(parent, QWidget):
            return
        margin = 8
        x = parent.width() - self._SIZE - margin
        y = margin
        self.move(x, y)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _on_timer(self) -> None:
        """Periodic tick: re-read camera and repaint if parent is visible."""
        parent = self.parent()
        if parent is not None and isinstance(parent, QWidget) and parent.isVisible():
            parent_size = (parent.width(), parent.height())
            if parent_size != self._last_parent_size:
                self._last_parent_size = parent_size
                self.update_position()
            self.refresh()

    # ------------------------------------------------------------------
    # Qt overrides
    # ------------------------------------------------------------------

    def paintEvent(self, event: QPaintEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0
        r = min(w, h) / 2.0 * _COMPASS_RADIUS

        # Semi-transparent background circle
        painter.setPen(Qt.PenStyle.NoPen)
        bg = QColor(30, 30, 30, 140)
        painter.setBrush(bg)
        painter.drawEllipse(QRect(0, 0, w, h))

        dot_r = r * _DOT_RADIUS
        font_px = max(7, int(r * _LABEL_FONT_FRACTION))
        font = QFont("Arial", font_px)
        font.setBold(True)
        painter.setFont(font)

        # Collect axis projections so we can sort by depth (back-to-front)
        projected: list[tuple[float, float, float, str, QColor, float, float]] = []
        for axis_id, (dx, dy, dz), col_front, col_back, snap_yaw, snap_pitch in _AXES:
            sx, sy, depth = _project_axis(dx, dy, dz, self._yaw, self._pitch)
            color = col_front if depth >= 0 else col_back
            projected.append((sx, sy, depth, axis_id, color, snap_yaw, snap_pitch))

        # Sort back-to-front so foreground axes overdraw background ones
        projected.sort(key=lambda p: p[2])

        # Draw axis lines (from center to each dot)
        for sx, sy, depth, axis_id, color, _, _ in projected:
            px = cx + sx * r
            py = cy + sy * r
            alpha = 220 if depth >= 0 else 100
            line_color = QColor(color.red(), color.green(), color.blue(), alpha)
            painter.setPen(QPen(line_color, 1.5))
            painter.drawLine(QPoint(int(cx), int(cy)), QPoint(int(px), int(py)))

        # Draw dots and labels
        for sx, sy, depth, axis_id, color, _, _ in projected:
            px = cx + sx * r
            py = cy + sy * r
            alpha = 230 if depth >= 0 else 110
            dot_color = QColor(color.red(), color.green(), color.blue(), alpha)
            is_hovered = axis_id == self._hovered_axis
            draw_r = dot_r * (1.25 if is_hovered else 1.0)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(dot_color)
            painter.drawEllipse(
                QRect(int(px - draw_r), int(py - draw_r), int(draw_r * 2), int(draw_r * 2)),
            )

            # Label (only for positive/front-facing axes, or all if large enough)
            if depth >= -0.3:
                text_color = QColor(255, 255, 255, min(255, int(alpha * 1.1)))
                painter.setPen(QPen(text_color))
                fm = painter.fontMetrics()
                text_w = fm.horizontalAdvance(axis_id)
                text_h = fm.height()
                painter.drawText(
                    QPoint(int(px - text_w / 2 + 1), int(py + text_h / 4)),
                    axis_id,
                )

        painter.end()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        axis = self._axis_at(event.pos())
        if axis != self._hovered_axis:
            self._hovered_axis = axis
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: object) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if self._hovered_axis is not None:
            self._hovered_axis = None
            self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if event.button() == Qt.MouseButton.LeftButton:
            axis = self._axis_at(event.pos())
            if axis is not None:
                for axis_id, _, _, _, snap_yaw, snap_pitch in _AXES:
                    if axis_id == axis:
                        self.sig_snap_view.emit(snap_yaw, snap_pitch)
                        break
        super().mousePressEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        super().resizeEvent(event)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _axis_at(self, pos: QPoint) -> str | None:
        """Return the axis id whose dot is closest to *pos*, or None."""
        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0
        r = min(w, h) / 2.0 * _COMPASS_RADIUS
        dot_r = r * _DOT_RADIUS * 1.5  # slightly larger hit area

        mx = pos.x()
        my = pos.y()

        best_axis: str | None = None
        best_depth = -1e9
        for axis_id, (dx, dy, dz), _, _, _, _ in _AXES:
            sx, sy, depth = _project_axis(dx, dy, dz, self._yaw, self._pitch)
            px = cx + sx * r
            py = cy + sy * r
            dist2 = (mx - px) ** 2 + (my - py) ** 2
            if dist2 <= dot_r**2:
                # Among overlapping dots prefer the one with greater depth (facing viewer)
                if depth > best_depth:
                    best_depth = depth
                    best_axis = axis_id
        return best_axis
