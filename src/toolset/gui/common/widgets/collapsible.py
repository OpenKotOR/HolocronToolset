"""Collapsible widgets for use in Qt applications.

Provides QGroupBox-based collapsible containers that can be expanded/collapsed
by double-clicking the title. No checkbox is shown; state is tracked internally.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QSizePolicy, QWidget

if TYPE_CHECKING:
    from qtpy.QtGui import QMouseEvent


class CollapsibleGroupBox(QGroupBox):
    """A QGroupBox that collapses/expands its contents when toggled.

    Contents are shown when expanded and hidden when collapsed. No checkbox
    is drawn; toggle by double-clicking the title. Compatible with UI files
    that set checkable/checked (checked = expanded).

    Usage:
        groupbox = CollapsibleGroupBox("Section Title")
        groupbox.setChecked(True)  # Start expanded
        layout = QVBoxLayout(groupbox)
        layout.addWidget(some_widget)
    """

    def __init__(self, title: str | QWidget = "", parent: QWidget | None = None):
        # Handle case where pyuic5 generates: CollapsibleGroupBox(parent)
        # In that case, title is actually the parent widget
        if isinstance(title, QWidget) and parent is None:
            parent = title
            title = ""

        super().__init__(title, parent)

        # Store the original size policy before any collapse
        self._original_size_policy: QSizePolicy = self.sizePolicy()

        # Track expanded state without using checkable (no checkbox drawn)
        self._expanded: bool = True

        # Apply initial expanded state (content visible)
        self._on_toggled(True)

    def setCheckable(self, checkable: bool) -> None:
        """Ignore so we never show a checkbox; collapse is title double-click only."""
        # No-op: we keep the group box non-checkable for appearance.

    def _on_toggled(self, checked: bool):
        """Handle the toggled signal to collapse/expand contents."""
        # Iterate through all child widgets and hide/show them
        for i in range(self.layout().count()) if self.layout() else []:
            item = self.layout().itemAt(i)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.setVisible(checked)
            # Also handle nested layouts
            nested_layout = item.layout()
            if nested_layout is not None:
                self._set_layout_visible(nested_layout, checked)

        # Adjust size policy when collapsed
        if checked:
            # Restore original size policy if it exists, otherwise use current
            if hasattr(self, "_original_size_policy"):
                self.setSizePolicy(self._original_size_policy)
            else:
                # Fallback: store current policy as original
                self._original_size_policy = self.sizePolicy()
        else:
            policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
            self.setSizePolicy(policy)

        # Update geometry
        self.updateGeometry()
        if self.parent() is not None:
            parent = self.parent()
            if isinstance(parent, QWidget):
                parent.updateGeometry()

    def _set_layout_visible(self, layout, visible: bool):
        """Recursively set visibility of layout items."""
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.setVisible(visible)
            nested = item.layout()
            if nested is not None:
                self._set_layout_visible(nested, visible)

    def setChecked(self, b: bool) -> None:  # noqa: N802
        """Set expanded state (True = expanded, False = collapsed). No checkbox drawn."""
        self._expanded = b
        self._on_toggled(b)

    def isChecked(self) -> bool:  # noqa: N802
        """Return whether the section is expanded (True) or collapsed (False)."""
        return self._expanded

    def _is_title_region(self, pos) -> bool:
        """True if the position is in the title/header area (click target for expand/collapse)."""
        return pos.y() < 30  # Approximate title bar height

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        """Toggle expand/collapse on single-click in the title region for discoverability."""
        if a0.button() == Qt.MouseButton.LeftButton and self._is_title_region(a0.pos()):
            self._expanded = not self._expanded
            self._on_toggled(self._expanded)
            a0.accept()
            return
        super().mousePressEvent(a0)

    def mouseDoubleClickEvent(self, a0: QMouseEvent) -> None:
        """Toggle expand/collapse when double-clicking the title area."""
        if self._is_title_region(a0.pos()):
            self._expanded = not self._expanded
            self._on_toggled(self._expanded)
        super().mouseDoubleClickEvent(a0)
