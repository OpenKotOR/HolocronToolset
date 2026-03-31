"""Preview panel widget for the main toolset window.

Displays a preview of the currently selected resource with file information below.
Supports: Images (TPC/TGA), 2DA tables, 3D Models (MDL), and UTC creatures.
"""
from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from loggerplus import RobustLogger
from qtpy.QtCore import Qt
from qtpy.QtGui import QFont, QImage, QPixmap
from qtpy.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from pykotor.resource.formats.tpc import TPCTextureFormat, read_tpc
from pykotor.resource.formats.twoda import TwoDA, read_2da
from pykotor.resource.type import ResourceType

if TYPE_CHECKING:
    from pykotor.extract.file import FileResource
    from toolset.data.installation import HTInstallation


class PreviewPanel(QWidget):
    """A panel that shows a preview of the selected resource and file information."""

    MAX_2DA_PREVIEW_ROWS = 20

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._installation: HTInstallation | None = None
        self._currentResource: FileResource | None = None
        self._modelRenderer = None  # Lazy-loaded to avoid OpenGL issues
        self._setupUi()

    def _setupUi(self):
        # Top-level horizontal layout: preview content (left) | sidebar (right)
        outerLayout = QHBoxLayout(self)
        outerLayout.setContentsMargins(0, 0, 0, 0)
        outerLayout.setSpacing(0)

        # Left side: preview content
        leftWidget = QWidget()
        leftWidget.setStyleSheet(
            "QWidget { background-color: #1e1e1e; }"
        )
        layout = QVBoxLayout(leftWidget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Preview type label (e.g. "Model Preview:", "2DA Preview:")
        self._previewTypeLabel = QLabel("")
        self._previewTypeLabel.setStyleSheet("color: #cccccc; font-weight: bold; font-size: 9pt;")
        layout.addWidget(self._previewTypeLabel)

        # Preview content area (stacked widget)
        self._stack = QStackedWidget()
        self._stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Page 0: Placeholder (no preview)
        self._placeholderLabel = QLabel("Select a resource to preview")
        self._placeholderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholderLabel.setStyleSheet("color: #666666; font-size: 10pt; background: transparent;")
        self._stack.addWidget(self._placeholderLabel)

        # Page 1: Image preview
        self._imageLabel = QLabel()
        self._imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._imageLabel.setScaledContents(False)
        self._stack.addWidget(self._imageLabel)

        # Page 2: 2DA table preview
        self._tableWidget = QTableWidget()
        self._tableWidget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tableWidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._tableWidget.setAlternatingRowColors(True)
        self._tableWidget.verticalHeader().setDefaultSectionSize(20)
        self._stack.addWidget(self._tableWidget)

        # Page 3: 3D model preview (placeholder - will be replaced with ModelRenderer)
        self._modelPlaceholder = QLabel("3D Model Preview")
        self._modelPlaceholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stack.addWidget(self._modelPlaceholder)

        # Page 4: Text info preview (for UTC and other text-based previews)
        self._textLabel = QLabel()
        self._textLabel.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._textLabel.setWordWrap(True)
        self._textLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._stack.addWidget(self._textLabel)

        layout.addWidget(self._stack, stretch=1)

        # Bottom file information area
        bottomInfoFrame = QFrame()
        bottomInfoFrame.setStyleSheet(
            "QFrame {"
            "  background-color: #252525;"
            "  border: 1px solid #3f3f3f;"
            "  border-radius: 3px;"
            "}"
            "QLabel {"
            "  background: transparent;"
            "  border: none;"
            "  color: #cccccc;"
            "}"
        )
        bottomInfoLayout = QVBoxLayout(bottomInfoFrame)
        bottomInfoLayout.setContentsMargins(8, 6, 8, 6)
        bottomInfoLayout.setSpacing(2)

        self._bottomInfoLabels: dict[str, QLabel] = {}
        for field in ("Resource Name", "Source File", "Type", "Category", "Size"):
            lbl = QLabel("")
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            bottomInfoLayout.addWidget(lbl)
            self._bottomInfoLabels[field] = lbl

        # Extra info label (for type-specific info like "2DA rows: X, columns: Y")
        self._extraInfoLabel = QLabel("")
        bottomInfoLayout.addWidget(self._extraInfoLabel)

        layout.addWidget(bottomInfoFrame)

        outerLayout.addWidget(leftWidget, stretch=1)

    def setInstallation(self, installation: HTInstallation):
        self._installation = installation
        if self._modelRenderer is not None:
            self._modelRenderer.setInstallation(installation)

    def _getOrCreateModelRenderer(self):
        """Lazy-create the ModelRenderer to avoid OpenGL issues at startup."""
        if self._modelRenderer is None:
            try:
                from toolset.gui.widgets.renderer.model import ModelRenderer
                self._modelRenderer = ModelRenderer(self)
                # Replace the placeholder at index 3
                old = self._stack.widget(3)
                self._stack.removeWidget(old)
                old.deleteLater()
                self._stack.insertWidget(3, self._modelRenderer)
                if self._installation is not None:
                    self._modelRenderer.setInstallation(self._installation)
            except Exception:
                RobustLogger().exception("Failed to create ModelRenderer for preview")
                self._modelRenderer = None
        return self._modelRenderer

    def clearPreview(self):
        """Reset to placeholder state."""
        self._stack.setCurrentIndex(0)
        self._placeholderLabel.setText("Select a resource to preview")
        self._currentResource = None
        for label in self._bottomInfoLabels.values():
            label.setText("")
        self._extraInfoLabel.setText("")
        self._previewTypeLabel.setText("")

    def _setFileInfo(self, resource: FileResource):
        """Set both top and bottom file info sections."""
        size = resource.size()
        if size < 1024:
            sizeStr = f"{size} bytes"
        elif size < 1024 * 1024:
            sizeStr = f"{size / 1024:.1f} KB"
        else:
            sizeStr = f"{size / (1024 * 1024):.2f} MB"

        info = {
            "Resource Name": resource.resname(),
            "Source File": str(resource.filepath().name) if resource.filepath() else "N/A",
            "Type": resource.restype().extension.upper(),
            "Category": resource.restype().category,
            "Size": sizeStr,
        }
        for field, value in info.items():
            self._bottomInfoLabels[field].setText(f"<b>{field}:</b> {value}")

    def updatePreview(self, resource: FileResource):
        """Update the preview panel with the given resource."""
        self._currentResource = resource
        self._setFileInfo(resource)

        # Load and display preview based on type
        restype = resource.restype()
        try:
            if restype in (ResourceType.TPC, ResourceType.TGA, ResourceType.JPG, ResourceType.PNG, ResourceType.BMP):
                self._previewImage(resource)
            elif restype is ResourceType.TwoDA:
                self._preview2DA(resource)
            elif restype in (ResourceType.MDL, ResourceType.MDX):
                self._previewModel(resource)
            elif restype is ResourceType.UTC:
                self._previewUTC(resource)
            else:
                self._previewGeneric(resource)
        except Exception:
            RobustLogger().exception("Failed to load preview")
            self._stack.setCurrentIndex(0)
            self._placeholderLabel.setText("Preview failed to load")
            self._extraInfoLabel.setText("")

    def _previewImage(self, resource: FileResource):
        """Preview TPC/TGA/image resources."""
        self._previewTypeLabel.setText("Image Preview:")
        data = resource.data()
        restype = resource.restype()

        if restype in (ResourceType.TPC, ResourceType.TGA):
            tpc = read_tpc(data)
            fmt = tpc.format()
            width, height, img_bytes = tpc.convert(TPCTextureFormat.RGBA, 0)
            image = QImage(img_bytes, width, height, QImage.Format.Format_RGBA8888)
            if fmt is not TPCTextureFormat.RGB:
                image = image.mirrored(False, True)
            self._extraInfoLabel.setText(f"Dimensions: {width} x {height}")
        else:
            image = QImage()
            image.loadFromData(data)
            self._extraInfoLabel.setText(f"Dimensions: {image.width()} x {image.height()}")

        if image.isNull():
            self._stack.setCurrentIndex(0)
            self._placeholderLabel.setText("Could not decode image")
            return

        pixmap = QPixmap.fromImage(image)
        # Scale to fit the label while maintaining aspect ratio
        avail = self._imageLabel.size()
        scaled = pixmap.scaled(avail, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self._imageLabel.setPixmap(scaled)
        self._stack.setCurrentIndex(1)

    def _preview2DA(self, resource: FileResource):
        """Preview 2DA table resources."""
        self._previewTypeLabel.setText("2DA Preview:")
        data = resource.data()
        twoda: TwoDA = read_2da(data)

        headers = twoda.get_headers()
        num_rows = twoda.get_height()

        self._tableWidget.clear()
        self._tableWidget.setColumnCount(len(headers))
        self._tableWidget.setRowCount(num_rows)
        self._tableWidget.setHorizontalHeaderLabels(headers)

        for row_idx in range(num_rows):
            for col_idx, header in enumerate(headers):
                with suppress(Exception):
                    val = twoda.get_cell(row_idx, header)
                    item = QTableWidgetItem(val)
                    self._tableWidget.setItem(row_idx, col_idx, item)

        # Set row numbers as vertical headers
        self._tableWidget.setVerticalHeaderLabels([str(i) for i in range(num_rows)])

        # Auto-resize columns
        h = self._tableWidget.horizontalHeader()
        if h is not None:
            h.setDefaultSectionSize(60)
            h.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        self._extraInfoLabel.setText(f"2DA rows: {num_rows}, columns: {len(headers)}")
        self._stack.setCurrentIndex(2)

    def _previewModel(self, resource: FileResource):
        """Preview MDL/MDX model resources."""
        self._previewTypeLabel.setText("Model Preview:")
        renderer = self._getOrCreateModelRenderer()
        if renderer is None:
            self._stack.setCurrentIndex(0)
            self._placeholderLabel.setText("3D preview unavailable")
            self._extraInfoLabel.setText("")
            return

        restype = resource.restype()
        resname = resource.resname()

        # Determine MDL and MDX data based on which file was selected
        mdl_data = bytes()
        mdx_data = bytes()

        if restype is ResourceType.MDL:
            mdl_data = resource.data()
            # Look up the corresponding MDX
            if self._installation is not None:
                try:
                    mdx_result = self._installation.resource(resname, ResourceType.MDX)
                    if mdx_result is not None:
                        mdx_data = mdx_result.data
                except Exception:
                    RobustLogger().warning(f"Could not find MDX for {resname}")
        elif restype is ResourceType.MDX:
            mdx_data = resource.data()
            # Look up the corresponding MDL
            if self._installation is not None:
                try:
                    mdl_result = self._installation.resource(resname, ResourceType.MDL)
                    if mdl_result is not None:
                        mdl_data = mdl_result.data
                except Exception:
                    RobustLogger().warning(f"Could not find MDL for {resname}")

        if not mdl_data:
            self._stack.setCurrentIndex(0)
            self._placeholderLabel.setText(f"Could not find MDL data for {resname}")
            self._extraInfoLabel.setText("")
            return

        try:
            renderer.setModel(mdl_data, mdx_data)
            # Show the renderer page first so initializeGL fires, then paintGL will load & resetCamera
            self._stack.setCurrentIndex(3)
            self._extraInfoLabel.setText(f"Model: {resname}")
        except Exception:
            RobustLogger().exception(f"Failed to render model {resname}")
            self._stack.setCurrentIndex(0)
            self._placeholderLabel.setText("Failed to render model")
            self._extraInfoLabel.setText("")

    def _previewUTC(self, resource: FileResource):
        """Preview UTC creature resources."""
        self._previewTypeLabel.setText("Creature Preview:")
        try:
            from pykotor.resource.generics.utc import UTC, read_utc
            data = resource.data()
            utc: UTC = read_utc(data)

            lines = []
            # Basic creature info
            if self._installation is not None:
                first = self._installation.string(utc.first_name, "")
                last = self._installation.string(utc.last_name, "")
                name = f"{first} {last}".strip()
                if name:
                    lines.append(f"<b>Name:</b> {name}")
            lines.append(f"<b>Tag:</b> {utc.tag}")
            lines.append(f"<b>Template:</b> {utc.resref}")
            lines.append(f"<b>Race:</b> {utc.race_id}")
            lines.append(f"<b>Appearance:</b> {utc.appearance_id}")
            lines.append(f"<b>HP:</b> {utc.current_hp}/{utc.hp}")
            lines.append(f"<b>Level:</b> {sum(cl.level for cl in utc.classes)}")

            if utc.classes:
                class_names = ", ".join(f"Class {cl.class_id} (Lv {cl.level})" for cl in utc.classes)
                lines.append(f"<b>Classes:</b> {class_names}")

            lines.append("")
            lines.append(f"<b>STR:</b> {utc.strength}  <b>DEX:</b> {utc.dexterity}  <b>CON:</b> {utc.constitution}")
            lines.append(f"<b>INT:</b> {utc.intelligence}  <b>WIS:</b> {utc.wisdom}  <b>CHA:</b> {utc.charisma}")

            self._textLabel.setText("<br>".join(lines))
            self._extraInfoLabel.setText("")
            self._stack.setCurrentIndex(4)

            # Also try to show the 3D model if possible
            renderer = self._getOrCreateModelRenderer()
            if renderer is not None:
                renderer.setCreature(utc)
                self._stack.setCurrentIndex(3)
        except Exception:
            RobustLogger().exception("Failed to preview UTC")
            self._stack.setCurrentIndex(0)
            self._placeholderLabel.setText("Could not preview creature")

    def _previewGeneric(self, resource: FileResource):
        """Show placeholder for unsupported types."""
        self._previewTypeLabel.setText("")
        self._stack.setCurrentIndex(0)
        ext = resource.restype().extension.upper()
        self._placeholderLabel.setText(f"No preview available for {ext} files")
        self._extraInfoLabel.setText("")
