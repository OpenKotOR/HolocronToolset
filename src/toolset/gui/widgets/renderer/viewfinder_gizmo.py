"""Blender-style 3D axis view finder gizmo overlay for the model renderer."""
from __future__ import annotations

import math

from typing import TYPE_CHECKING

from qtpy.QtCore import QPoint, QPointF, QRectF, Qt, Signal
from qtpy.QtGui import QBrush, QColor, QFont, QMouseEvent, QPainter, QPainterPath, QPen
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from qtpy.QtGui import QPaintEvent


# Axis view presets: (yaw, pitch)
_AXIS_VIEWS: dict[str, tuple[float, float]] = {
    "+X": (0.0, math.pi / 2),
    "-X": (math.pi, math.pi / 2),
    "+Y": (math.pi / 2, math.pi / 2),
    "-Y": (-math.pi / 2, math.pi / 2),
    "+Z": (math.pi / 2, math.pi - 0.001),
    "-Z": (math.pi / 2, 0.001),
}

# Colors matching Blender's convention
_AXIS_COLORS = {
    "X": QColor(230, 60, 60),     # Red
    "Y": QColor(100, 190, 60),    # Green
    "Z": QColor(60, 120, 230),    # Blue
}
_AXIS_BACK_COLORS = {
    "X": QColor(140, 50, 50),
    "Y": QColor(60, 110, 40),
    "Z": QColor(40, 70, 140),
}


class ViewfinderGizmo(QWidget):
    """A Blender-style axis gizmo that shows orientation and allows clicking to snap to axis views."""

    viewChanged = Signal(float, float)  # yaw, pitch
    dragRotate = Signal(float, float)  # delta_yaw, delta_pitch

    GIZMO_SIZE = 130
    AXIS_LENGTH = 44
    BALL_RADIUS = 10
    BACK_BALL_RADIUS = 5
    BG_RADIUS = 56

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedSize(self.GIZMO_SIZE, self.GIZMO_SIZE)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)

        self._yaw: float = math.pi / 16 * 7
        self._pitch: float = math.pi / 16 * 9
        self._hoveredAxis: str | None = None
        self._dragging: bool = False
        self._dragPrev: QPointF | None = None

        # Precompute hit zones on each paint
        self._hitZones: list[tuple[str, QPointF, float]] = []  # (axisLabel, center, radius)

    def setCameraAngles(self, yaw: float, pitch: float):
        """Update gizmo orientation to match camera."""
        self._yaw = yaw
        self._pitch = pitch
        self.update()

    def _project(self, x3d: float, y3d: float, z3d: float) -> tuple[float, float, float]:
        """Project a 3D point to 2D gizmo space matching the camera's view rotation.

        The camera view matrix applies:
          1. Rotate by (yaw + π/2) around Z
          2. Rotate by (π - pitch) around X
        The inverse (view rotation) is:
          R_x(pitch - π) * R_z(-(yaw + π/2))

        Returns (screen_x, screen_y, depth) where depth is used for sorting.
        """
        sy, cy = math.sin(self._yaw), math.cos(self._yaw)
        sp, cp = math.sin(self._pitch), math.cos(self._pitch)

        # Step 1: Rotate by -(yaw + π/2) around Z axis
        # cos(-(yaw+π/2)) = -sin(yaw), sin(-(yaw+π/2)) = -cos(yaw)
        x1 = -sy * x3d + cy * y3d
        y1 = -cy * x3d - sy * y3d
        z1 = z3d

        # Step 2: Rotate by (pitch - π) around X axis
        # cos(pitch-π) = -cos(pitch), sin(pitch-π) = -sin(pitch)
        x2 = x1
        y2 = -cp * y1 + sp * z1
        z2 = -sp * y1 - cp * z1

        cx = self.GIZMO_SIZE / 2
        cy_c = self.GIZMO_SIZE / 2
        return (cx + x2, cy_c - y2, z2)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        cx = self.GIZMO_SIZE / 2
        cy = self.GIZMO_SIZE / 2

        # Clip to the circular region so nothing draws outside it
        clipPath = QPainterPath()
        clipPath.addEllipse(QPointF(cx, cy), self.BG_RADIUS, self.BG_RADIUS)
        painter.setClipPath(clipPath)

        # Draw fully opaque background circle
        painter.setPen(QPen(QColor(80, 80, 80), 1.5))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawEllipse(QPointF(cx, cy), self.BG_RADIUS, self.BG_RADIUS)

        # Define axes in 3D space (unit vectors scaled by AXIS_LENGTH)
        axes_3d = {
            "+X": (self.AXIS_LENGTH, 0, 0),
            "-X": (-self.AXIS_LENGTH, 0, 0),
            "+Y": (0, self.AXIS_LENGTH, 0),
            "-Y": (0, -self.AXIS_LENGTH, 0),
            "+Z": (0, 0, self.AXIS_LENGTH),
            "-Z": (0, 0, -self.AXIS_LENGTH),
        }

        # Project all endpoints and sort by depth (back to front)
        projected: list[tuple[str, float, float, float]] = []
        for label, (ax, ay, az) in axes_3d.items():
            sx, sy, depth = self._project(ax, ay, az)
            projected.append((label, sx, sy, depth))

        # Sort by depth - draw farthest first (most positive z2 = behind camera)
        projected.sort(key=lambda item: -item[3])

        self._hitZones.clear()

        for label, sx, sy, depth in projected:
            axis_letter = label[1]  # "X", "Y", or "Z"
            is_positive = label.startswith("+")
            color = _AXIS_COLORS[axis_letter] if is_positive else _AXIS_BACK_COLORS[axis_letter]
            ball_r = self.BALL_RADIUS if is_positive else self.BACK_BALL_RADIUS

            # Draw axis line from center to endpoint
            pen = QPen(color, 2.0 if is_positive else 1.0)
            painter.setPen(pen)
            painter.drawLine(QPointF(cx, cy), QPointF(sx, sy))

            # Draw axis ball
            is_hovered = self._hoveredAxis == label
            if is_hovered:
                hover_color = QColor(color)
                hover_color.setAlpha(255)
                painter.setBrush(QBrush(hover_color.lighter(140)))
            else:
                painter.setBrush(QBrush(color))

            painter.setPen(QPen(QColor(30, 30, 30), 1.0))
            painter.drawEllipse(QPointF(sx, sy), ball_r, ball_r)

            # Draw axis label (only on positive axes - negative are small dots like Blender)
            if is_positive:
                font = QFont("Arial", 8, QFont.Weight.Bold)
                painter.setFont(font)
                painter.setPen(QPen(QColor(255, 255, 255)))
                text_rect = QRectF(sx - ball_r, sy - ball_r, ball_r * 2, ball_r * 2)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, axis_letter)

            # Store hit zone
            self._hitZones.append((label, QPointF(sx, sy), ball_r + 3))

        # Draw center dot
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawEllipse(QPointF(cx, cy), 3, 3)

        painter.end()

    def _isInCircle(self, pos: QPointF) -> bool:
        cx = self.GIZMO_SIZE / 2
        cy = self.GIZMO_SIZE / 2
        dx = pos.x() - cx
        dy = pos.y() - cy
        return dx * dx + dy * dy <= self.BG_RADIUS * self.BG_RADIUS

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = QPointF(event.pos())

        # Handle drag-to-rotate
        if self._dragging and self._dragPrev is not None:
            dx = pos.x() - self._dragPrev.x()
            dy = pos.y() - self._dragPrev.y()
            self._dragPrev = pos
            # Convert pixel delta to rotation (scale factor for sensitivity)
            self.dragRotate.emit(-dx * 0.01, dy * 0.01)
            return

        self._hoveredAxis = None
        # Check hit zones in reverse (front-most first)
        for label, center, radius in reversed(self._hitZones):
            ddx = pos.x() - center.x()
            ddy = pos.y() - center.y()
            if ddx * ddx + ddy * ddy <= radius * radius:
                self._hoveredAxis = label
                break

        if self._hoveredAxis:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        elif self._isInCircle(pos):
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = QPointF(event.pos())
        # Check hit zones in reverse (front-most first) for axis click
        for label, center, radius in reversed(self._hitZones):
            dx = pos.x() - center.x()
            dy = pos.y() - center.y()
            if dx * dx + dy * dy <= radius * radius:
                yaw, pitch = _AXIS_VIEWS[label]
                self.viewChanged.emit(yaw, pitch)
                return
        # If clicked inside the circle background, start drag rotation
        if self._isInCircle(pos):
            self._dragging = True
            self._dragPrev = pos
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self._dragPrev = None
            pos = QPointF(event.pos())
            if self._isInCircle(pos):
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def leaveEvent(self, event):
        self._hoveredAxis = None
        self._dragging = False
        self._dragPrev = None
        self.update()


class ViewfinderOverlay(QWidget):
    """Container for the gizmo + ortho/perspective toggle, positioned in the top-right corner."""

    viewChanged = Signal(float, float)
    projectionToggled = Signal(bool)  # True = orthographic
    dragRotate = Signal(float, float)  # delta_yaw, delta_pitch
    dragPan = Signal(float, float)  # delta_x, delta_y (screen pixels)
    zoomIn = Signal()
    zoomOut = Signal()
    wireframeToggled = Signal(bool)
    texturesToggled = Signal(bool)
    gridToggled = Signal(bool)
    resetClicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.gizmo = ViewfinderGizmo(self)
        self.gizmo.viewChanged.connect(self.viewChanged.emit)
        self.gizmo.dragRotate.connect(self.dragRotate.emit)
        layout.addWidget(self.gizmo)

        # Button row
        btnRow = QWidget(self)
        btnRow.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        btnLayout = QHBoxLayout(btnRow)
        btnLayout.setContentsMargins(0, 0, 0, 0)
        btnLayout.setSpacing(3)

        _BTN_STYLE = (
            "QPushButton {"
            "  background-color: rgba(60, 60, 60, 200);"
            "  color: #cccccc;"
            "  border: 1px solid #555555;"
            "  border-radius: 3px;"
            "  font-size: 9px;"
            "  font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "  background-color: rgba(80, 80, 80, 220);"
            "}"
            "QPushButton:checked {"
            "  background-color: rgba(50, 100, 160, 220);"
            "  border-color: #6688bb;"
            "}"
        )

        self._orthoBtn = QPushButton("Persp", self)
        self._orthoBtn.setFixedSize(50, 20)
        self._orthoBtn.setCheckable(True)
        self._orthoBtn.setStyleSheet(_BTN_STYLE)
        self._orthoBtn.clicked.connect(self._onToggle)
        btnLayout.addWidget(self._orthoBtn)

        self._moveBtn = _DragButton("Move", self)
        self._moveBtn.setFixedSize(50, 20)
        self._moveBtn.setStyleSheet(_BTN_STYLE)
        self._moveBtn.dragDelta.connect(self.dragPan.emit)
        btnLayout.addWidget(self._moveBtn)

        layout.addWidget(btnRow, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Zoom button row
        zoomRow = QWidget(self)
        zoomRow.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        zoomLayout = QHBoxLayout(zoomRow)
        zoomLayout.setContentsMargins(0, 0, 0, 0)
        zoomLayout.setSpacing(3)

        self._zoomInBtn = QPushButton("+", self)
        self._zoomInBtn.setFixedSize(30, 20)
        self._zoomInBtn.setStyleSheet(_BTN_STYLE)
        self._zoomInBtn.setAutoRepeat(True)
        self._zoomInBtn.setAutoRepeatInterval(80)
        self._zoomInBtn.clicked.connect(self.zoomIn.emit)
        zoomLayout.addWidget(self._zoomInBtn)

        self._zoomOutBtn = QPushButton("-", self)
        self._zoomOutBtn.setFixedSize(30, 20)
        self._zoomOutBtn.setStyleSheet(_BTN_STYLE)
        self._zoomOutBtn.setAutoRepeat(True)
        self._zoomOutBtn.setAutoRepeatInterval(80)
        self._zoomOutBtn.clicked.connect(self.zoomOut.emit)
        zoomLayout.addWidget(self._zoomOutBtn)

        layout.addWidget(zoomRow, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Render mode row
        modeRow = QWidget(self)
        modeRow.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        modeLayout = QHBoxLayout(modeRow)
        modeLayout.setContentsMargins(0, 0, 0, 0)
        modeLayout.setSpacing(3)

        self._wireBtn = QPushButton("Wire", self)
        self._wireBtn.setFixedSize(50, 20)
        self._wireBtn.setCheckable(True)
        self._wireBtn.setStyleSheet(_BTN_STYLE)
        self._wireBtn.toggled.connect(self.wireframeToggled.emit)
        modeLayout.addWidget(self._wireBtn)

        self._texBtn = QPushButton("Tex", self)
        self._texBtn.setFixedSize(50, 20)
        self._texBtn.setCheckable(True)
        self._texBtn.setChecked(True)
        self._texBtn.setStyleSheet(_BTN_STYLE)
        self._texBtn.toggled.connect(self.texturesToggled.emit)
        modeLayout.addWidget(self._texBtn)

        layout.addWidget(modeRow, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Grid/reset row
        gridRow = QWidget(self)
        gridRow.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        gridLayout = QHBoxLayout(gridRow)
        gridLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.setSpacing(3)

        self._gridBtn = QPushButton("Grid", self)
        self._gridBtn.setFixedSize(50, 20)
        self._gridBtn.setCheckable(True)
        self._gridBtn.setChecked(True)
        self._gridBtn.setStyleSheet(_BTN_STYLE)
        self._gridBtn.toggled.connect(self.gridToggled.emit)
        gridLayout.addWidget(self._gridBtn)

        self._resetBtn = QPushButton("Reset", self)
        self._resetBtn.setFixedSize(50, 20)
        self._resetBtn.setStyleSheet(_BTN_STYLE)
        self._resetBtn.clicked.connect(self.resetClicked.emit)
        gridLayout.addWidget(self._resetBtn)

        layout.addWidget(gridRow, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._isOrtho = False
        self.setFixedSize(ViewfinderGizmo.GIZMO_SIZE, ViewfinderGizmo.GIZMO_SIZE + 98)

    def _onToggle(self):
        self._isOrtho = self._orthoBtn.isChecked()
        self._orthoBtn.setText("Ortho" if self._isOrtho else "Persp")
        self.projectionToggled.emit(self._isOrtho)

    def setCameraAngles(self, yaw: float, pitch: float):
        self.gizmo.setCameraAngles(yaw, pitch)


class _DragButton(QPushButton):
    """A button that emits drag deltas when dragged, for camera panning."""

    dragDelta = Signal(float, float)

    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(text, parent)
        self._dragging = False
        self._dragPrev: QPointF | None = None
        self.setMouseTracking(True)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._dragPrev = QPointF(event.pos())
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging and self._dragPrev is not None:
            pos = QPointF(event.pos())
            dx = pos.x() - self._dragPrev.x()
            dy = pos.y() - self._dragPrev.y()
            self._dragPrev = pos
            self.dragDelta.emit(dx, dy)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._dragPrev = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)
