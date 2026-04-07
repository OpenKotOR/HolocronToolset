"""Shared OpenGL widget infrastructure for toolset renderers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qtpy.QtCore import QPoint, QTimer, Qt
from qtpy.QtGui import QCursor
from qtpy.QtWidgets import QOpenGLWidget  # pyright: ignore[reportPrivateImportUsage]

from loggerplus import RobustLogger
from utility.common.geometry import Vector2, Vector3

if TYPE_CHECKING:
    from qtpy.QtGui import (
        QCloseEvent,
        QFocusEvent,
    )
    from qtpy.QtWidgets import QWidget

    from pykotor.gl.scene import Scene


class OpenGLSceneRenderer(QOpenGLWidget):
    """Shared OpenGL widget lifecycle helpers for scene-backed renderers."""

    def __init__(
        self,
        parent: QWidget,
        *,
        initial_mouse_prev: Vector2 | None = None,
        loop_interval_ms: int = 33,
    ) -> None:
        super().__init__(parent)
        self.scene: Scene | None = None
        self._keys_down: set[Any] = set()
        self._mouse_down: set[Any] = set()
        self._mouse_prev: Vector2 = (
            initial_mouse_prev if initial_mouse_prev is not None else Vector2(0, 0)
        )
        self.free_cam: bool = False

        # Accept keyboard focus when clicked so key events (e.g. WASD in fly
        # cam) reach the renderer directly instead of going to whichever
        # sibling widget happened to have focus.
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self._loop_timer: QTimer = QTimer(self)
        self._loop_timer.setInterval(loop_interval_ms)
        self._loop_timer.setSingleShot(False)
        self._loop_timer.timeout.connect(self._on_loop_timer_timeout)

    @property
    def loop_timer(self) -> QTimer:
        return self._loop_timer

    def _on_loop_timer_timeout(self) -> None:
        raise NotImplementedError

    def _drawable_size(self) -> tuple[int, int]:
        try:
            device_pixel_ratio = float(self.devicePixelRatioF())
        except AttributeError:
            device_pixel_ratio = float(self.devicePixelRatio())

        drawable_width: int = max(1, int(round(self.width() * device_pixel_ratio)))
        drawable_height: int = max(1, int(round(self.height() * device_pixel_ratio)))
        return drawable_width, drawable_height

    def _sync_camera_drawable_size(self) -> tuple[int, int]:
        drawable_width, drawable_height = self._drawable_size()
        if self.scene is not None:
            self.scene.camera.set_resolution(drawable_width, drawable_height)
        return drawable_width, drawable_height

    def _logical_to_drawable_coords(self, x: float, y: float) -> tuple[float, float]:
        drawable_width, drawable_height = self._drawable_size()
        logical_width = max(1, self.width())
        logical_height = max(1, self.height())
        return (
            x * drawable_width / logical_width,
            y * drawable_height / logical_height,
        )

    # region Input State

    def reset_buttons_down(self) -> None:
        """Clear all tracked mouse buttons."""
        self._mouse_down.clear()

    def reset_keys_down(self) -> None:
        """Clear all tracked keyboard keys."""
        self._keys_down.clear()

    def reset_all_down(self) -> None:
        """Clear all tracked mouse buttons and keyboard keys."""
        self._mouse_down.clear()
        self._keys_down.clear()

    # endregion

    # region Camera Transformations

    def pan_camera(self, forward: float, right: float, up: float) -> None:
        """Move the camera on the XY plane relative to its facing, plus an absolute Z shift.

        Args:
            forward: Signed units to move in the camera's forward (XY) direction.
            right:   Signed units to move in the camera's sideward (XY) direction.
            up:      Signed units to move along the world Z axis.
        """
        if self.scene is None:
            return
        forward_vec = forward * self.scene.camera.forward()
        sideways = right * self.scene.camera.sideward()
        self.scene.camera.x += forward_vec.x + sideways.x
        self.scene.camera.y += forward_vec.y + sideways.y
        self.scene.camera.z += up

    def move_camera(self, forward: float, right: float, up: float) -> None:
        """Move the camera in fully camera-relative 3D space (free-cam / fly-through style).

        All three axes are computed from the camera's current orientation vectors,
        including the vertical component.
        """
        if self.scene is None:
            return
        forward_vec = forward * self.scene.camera.forward(ignore_z=False)
        sideways = right * self.scene.camera.sideward(ignore_z=False)
        upward = -up * self.scene.camera.upward(ignore_xy=False)
        self.scene.camera.x += upward.x + sideways.x + forward_vec.x
        self.scene.camera.y += upward.y + sideways.y + forward_vec.y
        self.scene.camera.z += upward.z + sideways.z + forward_vec.z

    def rotate_camera(
        self,
        yaw: float,
        pitch: float,
        *,
        clamp_rotations: bool = True,
    ) -> None:
        """Apply an incremental yaw+pitch rotation to the scene camera."""
        if self.scene is None:
            return
        self.scene.camera.rotate(yaw, pitch, clamp=clamp_rotations)

    def zoom_camera(self, distance: float) -> None:
        """Adjust the camera's orbital distance; result is clamped to >= 0."""
        if self.scene is None:
            return
        self.scene.camera.distance -= distance
        self.scene.camera.distance = max(self.scene.camera.distance, 0)

    def snap_camera_to_point(
        self,
        point: Vector2 | Vector3,
        *,
        distance: float | None = None,
    ) -> None:
        """Reposition the camera focal point to *point* with an optional orbital distance."""
        if self.scene is None:
            return
        self.scene.camera.x = point.x
        self.scene.camera.y = point.y
        if isinstance(point, Vector3):
            self.scene.camera.z = point.z
        if distance is not None:
            self.scene.camera.distance = distance

    # endregion

    # region Cursor Lock

    def do_cursor_lock(self, mut_scr: Vector2) -> None:
        """Reset the OS cursor to the last known widget position to prevent it leaving the viewport.

        Mutates *mut_scr* to the locked screen position after the warp.
        Used during free-cam mode and drag-camera operations.
        """
        global_old_pos = self.mapToGlobal(QPoint(int(self._mouse_prev.x), int(self._mouse_prev.y)))
        QCursor.setPos(global_old_pos)
        local_old_pos = self.mapFromGlobal(QPoint(global_old_pos.x(), global_old_pos.y()))
        mut_scr.x = local_old_pos.x()
        mut_scr.y = local_old_pos.y()

    # endregion

    def focusOutEvent(self, event: QFocusEvent):  # pyright: ignore[reportIncompatibleMethodOverride]
        self._mouse_down.clear()
        self._keys_down.clear()
        super().focusOutEvent(event)
        RobustLogger().debug(
            "%s.focusOutEvent: clearing all keys/buttons held down.", self.__class__.__name__
        )

    def closeEvent(self, event: QCloseEvent):  # pyright: ignore[reportIncompatibleMethodOverride]
        self.shutdown_renderer()
        super().closeEvent(event)

    def shutdown_renderer(self) -> None:
        if self._loop_timer.isActive():
            self._loop_timer.stop()
        self.scene = None
