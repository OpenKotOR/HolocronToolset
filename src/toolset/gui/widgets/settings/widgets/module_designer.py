"""Module Designer settings widget: camera, grid, instance labels, and key bindings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy import QtCore
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from pykotor.common.misc import Color
from toolset.data.settings import Settings, SettingsProperty
from toolset.gui.widgets.settings.widgets.base import SettingsWidget

# ---------------------------------------------------------------------------
# Preset binding tables for control scheme selection.
# ---------------------------------------------------------------------------
# These dicts map SettingsProperty attribute names → (keys, buttons) tuples.
# STANDARD_BINDINGS matches the current defaults in ModuleDesignerSettings;
# LEGACY_BINDINGS restores the legacy pre-standard-navigation values.
# ---------------------------------------------------------------------------

STANDARD_BINDINGS: dict[str, tuple] = {
    "duplicateObject3dBind": ({Qt.Key.Key_Shift}, {Qt.MouseButton.LeftButton}),
    "frameAll2dBind": ({Qt.Key.Key_Home}, set()),
    "moveCamera2dBind": (set(), {Qt.MouseButton.MiddleButton}),
    "moveCameraDown2dBind": ({Qt.Key.Key_Down}, None),
    "moveCameraLeft2dBind": ({Qt.Key.Key_Left}, None),
    "moveCameraPlane3dBind": ({Qt.Key.Key_Shift}, {Qt.MouseButton.MiddleButton}),
    "moveCameraRight2dBind": ({Qt.Key.Key_Right}, None),
    "moveCameraToSelected2dBind": ({Qt.Key.Key_Period}, set()),
    "moveCameraToSelected3dBind": ({Qt.Key.Key_Period}, None),
    "moveCameraUp2dBind": ({Qt.Key.Key_Up}, None),
    "moveCameraXY3dBind": ({Qt.Key.Key_Shift}, {Qt.MouseButton.MiddleButton}),
    "panCameraLMB3dBind": ({Qt.Key.Key_Control}, {Qt.MouseButton.LeftButton}),
    "resetCameraView2dBind": ({Qt.Key.Key_Control, Qt.Key.Key_0}, set()),
    "rotateCamera2dBind": ({Qt.Key.Key_Control}, {Qt.MouseButton.MiddleButton}),
    "rotateCamera3dBind": (set(), {Qt.MouseButton.MiddleButton}),
    "rotateObject3dBind": ({Qt.Key.Key_Control}, {Qt.MouseButton.LeftButton}),
    "rotateSelected3dBind": ({Qt.Key.Key_Alt}, {Qt.MouseButton.LeftButton}),
    "zoomCamera2dBind": (set(), set()),
    "zoomCameraIn2dBind": ({Qt.Key.Key_Equal}, None),
    "zoomCameraMM3dBind": ({Qt.Key.Key_Control}, {Qt.MouseButton.MiddleButton}),
    "zoomCameraOut2dBind": ({Qt.Key.Key_Minus}, None),
}

LEGACY_BINDINGS: dict[str, tuple] = {
    "duplicateObject3dBind": ({Qt.Key.Key_Alt}, {Qt.MouseButton.LeftButton}),
    "frameAll2dBind": ({Qt.Key.Key_Home}, set()),
    "moveCamera2dBind": ({Qt.Key.Key_Control}, {Qt.MouseButton.LeftButton}),
    "moveCameraDown2dBind": ({Qt.Key.Key_Down}, None),
    "moveCameraLeft2dBind": ({Qt.Key.Key_Left}, None),
    "moveCameraPlane3dBind": (set(), {Qt.MouseButton.MiddleButton}),
    "moveCameraRight2dBind": ({Qt.Key.Key_Right}, None),
    "moveCameraToSelected2dBind": ({Qt.Key.Key_Z}, set()),
    "moveCameraToSelected3dBind": ({Qt.Key.Key_Z}, None),
    "moveCameraUp2dBind": ({Qt.Key.Key_Up}, None),
    "moveCameraXY3dBind": ({Qt.Key.Key_Control}, {Qt.MouseButton.LeftButton}),
    "panCameraLMB3dBind": ({Qt.Key.Key_Control}, {Qt.MouseButton.LeftButton}),
    "resetCameraView2dBind": ({Qt.Key.Key_Control, Qt.Key.Key_0}, set()),
    "rotateCamera2dBind": ({Qt.Key.Key_Control}, {Qt.MouseButton.MiddleButton}),
    "rotateCamera3dBind": (set(), {Qt.MouseButton.LeftButton}),
    "rotateObject3dBind": ({Qt.Key.Key_Alt}, {Qt.MouseButton.LeftButton}),
    "rotateSelected3dBind": (set(), {Qt.MouseButton.MiddleButton}),
    "zoomCamera2dBind": ({Qt.Key.Key_Control}, set()),
    "zoomCameraIn2dBind": ({Qt.Key.Key_Equal}, None),
    "zoomCameraMM3dBind": (set(), {Qt.MouseButton.RightButton}),
    "zoomCameraOut2dBind": ({Qt.Key.Key_Minus}, None),
}


def normalize_control_scheme(scheme: str | None = None) -> str:
    if scheme in {None, "", "blender"}:
        return "standard"
    return (scheme or "").strip().lower()


def get_renderer_loop_interval_ms() -> int:
    """Return the render loop interval in ms from settings (0 = auto = primary screen Hz)."""
    settings = ModuleDesignerSettings()
    hz = settings.rendererRefreshRateHz
    if hz <= 0:
        screen = QApplication.primaryScreen()
        if screen and screen.refreshRate() > 0:
            hz = screen.refreshRate()
        else:
            hz = 60.0
    return max(1, round(1000 / hz))


if TYPE_CHECKING:
    from qtpy.QtGui import QScreen
    from qtpy.QtWidgets import QWidget

    from toolset.data.misc import Bind
    from toolset.gui.widgets.edit.color import ColorEdit
    from toolset.gui.widgets.set_bind import SetBindWidget


class ModuleDesignerWidget(SettingsWidget):
    sig_settings_edited = QtCore.Signal()  # pyright: ignore[reportPrivateImportUsage]

    def __init__(self, parent: QWidget):
        """Initializes the Module Designer UI.

        Args:
        ----
            parent (QWidget): The parent widget

        Processing Logic:
        ----------------
            - Initializes settings and binds lists
            - Loads UI from module_designer
            - Sets alpha channel for material colour pickers
            - Connects reset buttons to reset methods.
        """
        super().__init__(parent)

        self.settings: ModuleDesignerSettings = ModuleDesignerSettings()

        from qtpy.QtWidgets import QLabel

        from toolset.gui.widgets.set_bind import SetBindWidget
        from toolset.uic.qtpy.widgets.settings import module_designer

        self.ui = module_designer.Ui_Form()
        self.ui.setupUi(self)

        if not hasattr(self.ui, "walkmeshVertexDragXAxis3dBindEdit"):
            row = self.ui.formLayout.rowCount()

            x_label = QLabel("Walkmesh Vertex Drag X", self.ui.tab3DControls)
            x_label.setMinimumSize(110, 0)
            x_label.setStyleSheet("QLabel:hover { color: #555;}")
            x_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            x_label.setObjectName("walkmeshVertexDragXAxis3dLabel")
            self.ui.walkmeshVertexDragXAxis3dBindEdit = SetBindWidget(parent=self.ui.tab3DControls)
            self.ui.walkmeshVertexDragXAxis3dBindEdit.setObjectName(
                "walkmeshVertexDragXAxis3dBindEdit"
            )
            self.ui.formLayout.setWidget(row, self.ui.formLayout.ItemRole.LabelRole, x_label)
            self.ui.formLayout.setWidget(
                row,
                self.ui.formLayout.ItemRole.FieldRole,
                self.ui.walkmeshVertexDragXAxis3dBindEdit,
            )

            row += 1
            y_label = QLabel("Walkmesh Vertex Drag Y", self.ui.tab3DControls)
            y_label.setMinimumSize(110, 0)
            y_label.setStyleSheet("QLabel:hover { color: #555;}")
            y_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            y_label.setObjectName("walkmeshVertexDragYAxis3dLabel")
            self.ui.walkmeshVertexDragYAxis3dBindEdit = SetBindWidget(parent=self.ui.tab3DControls)
            self.ui.walkmeshVertexDragYAxis3dBindEdit.setObjectName(
                "walkmeshVertexDragYAxis3dBindEdit"
            )
            self.ui.formLayout.setWidget(row, self.ui.formLayout.ItemRole.LabelRole, y_label)
            self.ui.formLayout.setWidget(
                row,
                self.ui.formLayout.ItemRole.FieldRole,
                self.ui.walkmeshVertexDragYAxis3dBindEdit,
            )

            row += 1
            z_label = QLabel("Walkmesh Vertex Drag Z", self.ui.tab3DControls)
            z_label.setMinimumSize(110, 0)
            z_label.setStyleSheet("QLabel:hover { color: #555;}")
            z_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            z_label.setObjectName("walkmeshVertexDragZAxis3dLabel")
            self.ui.walkmeshVertexDragZAxis3dBindEdit = SetBindWidget(parent=self.ui.tab3DControls)
            self.ui.walkmeshVertexDragZAxis3dBindEdit.setObjectName(
                "walkmeshVertexDragZAxis3dBindEdit"
            )
            self.ui.formLayout.setWidget(row, self.ui.formLayout.ItemRole.LabelRole, z_label)
            self.ui.formLayout.setWidget(
                row,
                self.ui.formLayout.ItemRole.FieldRole,
                self.ui.walkmeshVertexDragZAxis3dBindEdit,
            )

        # --- Control Scheme selector (Standard / Classic) ---
        # Dynamically added so no .ui change is needed.
        if not hasattr(self.ui, "controlSchemeCombo"):
            from qtpy.QtWidgets import QComboBox, QHBoxLayout

            scheme_row = QHBoxLayout()
            scheme_label = QLabel("Control Scheme", self.ui.tab3DControls)
            scheme_label.setObjectName("controlSchemeLabel")
            self.ui.controlSchemeCombo = QComboBox(self.ui.tab3DControls)
            self.ui.controlSchemeCombo.setObjectName("controlSchemeCombo")
            self.ui.controlSchemeCombo.addItem("Standard (default)", "standard")
            self.ui.controlSchemeCombo.addItem("Classic (legacy)", "classic")
            scheme_row.addWidget(scheme_label)
            scheme_row.addWidget(self.ui.controlSchemeCombo)
            # Insert at the very top of the 3D controls tab layout (index 0)
            self.ui.verticalLayout_2.insertLayout(0, scheme_row)

        self.ui.controlSchemeCombo.currentIndexChanged.connect(self._on_scheme_changed)

        # --- Blender numpad view / frame navigation binds (3D) ---
        if not hasattr(self.ui, "viewFront3dBindEdit"):
            _nav_binds_3d: list[tuple[str, str]] = [
                ("viewFront3dBindEdit", "View Front (Numpad 1)"),
                ("viewBack3dBindEdit", "View Back (Ctrl+Num 1)"),
                ("viewRight3dBindEdit", "View Right (Numpad 3)"),
                ("viewLeft3dBindEdit", "View Left (Ctrl+Num 3)"),
                ("viewTop3dBindEdit", "View Top (Numpad 7)"),
                ("viewBottom3dBindEdit", "View Bottom (Ctrl+Num 7)"),
                ("viewToggleOrtho3dBindEdit", "Toggle Ortho (Numpad 5)"),
                ("viewCamera3dBindEdit", "Snap to Camera (Numpad 0)"),
                ("frameAll3dBindEdit", "Frame All (Home)"),
                ("frameSelected3dBindEdit", "Frame Selected (Numpad .)"),
            ]
            for attr_name, label_text in _nav_binds_3d:
                nav_row = self.ui.formLayout.rowCount()
                nav_lbl = QLabel(label_text, self.ui.tab3DControls)
                nav_lbl.setMinimumSize(110, 0)
                nav_lbl.setStyleSheet("QLabel:hover { color: #555;}")
                nav_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                nav_bind_widget = SetBindWidget(parent=self.ui.tab3DControls)
                nav_bind_widget.setObjectName(attr_name)
                setattr(self.ui, attr_name, nav_bind_widget)
                self.ui.formLayout.setWidget(
                    nav_row, self.ui.formLayout.ItemRole.LabelRole, nav_lbl
                )
                self.ui.formLayout.setWidget(
                    nav_row, self.ui.formLayout.ItemRole.FieldRole, nav_bind_widget
                )

        # --- Pan camera (LMB) bind (3D) ---
        if not hasattr(self.ui, "panCameraLMB3dBindEdit"):
            pan_lmb_row = self.ui.formLayout.rowCount()
            pan_lmb_lbl = QLabel("Pan Camera (LMB)", self.ui.tab3DControls)
            pan_lmb_lbl.setMinimumSize(110, 0)
            pan_lmb_lbl.setStyleSheet("QLabel:hover { color: #555;}")
            pan_lmb_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.panCameraLMB3dBindEdit = SetBindWidget(parent=self.ui.tab3DControls)
            self.ui.panCameraLMB3dBindEdit.setObjectName("panCameraLMB3dBindEdit")
            self.ui.formLayout.setWidget(
                pan_lmb_row, self.ui.formLayout.ItemRole.LabelRole, pan_lmb_lbl
            )
            self.ui.formLayout.setWidget(
                pan_lmb_row, self.ui.formLayout.ItemRole.FieldRole, self.ui.panCameraLMB3dBindEdit
            )

        # --- Frame-all bind (2D) ---
        if not hasattr(self.ui, "frameAll2dBindEdit"):
            d2_row = self.ui.formLayout_2.rowCount()
            d2_lbl = QLabel("Frame All 2D (Home)", self.ui.tab2DControls)
            d2_lbl.setMinimumSize(110, 0)
            d2_lbl.setStyleSheet("QLabel:hover { color: #555;}")
            d2_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.frameAll2dBindEdit = SetBindWidget(parent=self.ui.tab2DControls)
            self.ui.frameAll2dBindEdit.setObjectName("frameAll2dBindEdit")
            self.ui.formLayout_2.setWidget(d2_row, self.ui.formLayout_2.ItemRole.LabelRole, d2_lbl)
            self.ui.formLayout_2.setWidget(
                d2_row, self.ui.formLayout_2.ItemRole.FieldRole, self.ui.frameAll2dBindEdit
            )

        extra_2d_binds: list[tuple[str, str]] = [
            ("resetCameraView2dBindEdit", "Reset View 2D"),
            ("zoomCameraIn2dBindEdit", "Zoom In 2D"),
            ("zoomCameraOut2dBindEdit", "Zoom Out 2D"),
            ("moveCameraLeft2dBindEdit", "Pan Left 2D"),
            ("moveCameraRight2dBindEdit", "Pan Right 2D"),
            ("moveCameraUp2dBindEdit", "Pan Up 2D"),
            ("moveCameraDown2dBindEdit", "Pan Down 2D"),
        ]
        for attr_name, label_text in extra_2d_binds:
            if hasattr(self.ui, attr_name):
                continue
            row = self.ui.formLayout_2.rowCount()
            bind_label = QLabel(label_text, self.ui.tab2DControls)
            bind_label.setMinimumSize(110, 0)
            bind_label.setStyleSheet("QLabel:hover { color: #555;}")
            bind_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bind_widget = SetBindWidget(parent=self.ui.tab2DControls)
            bind_widget.setObjectName(attr_name)
            setattr(self.ui, attr_name, bind_widget)
            self.ui.formLayout_2.setWidget(row, self.ui.formLayout_2.ItemRole.LabelRole, bind_label)
            self.ui.formLayout_2.setWidget(
                row, self.ui.formLayout_2.ItemRole.FieldRole, bind_widget
            )

        self.ui.undefinedMaterialColourEdit.allow_alpha = True
        self.ui.dirtMaterialColourEdit.allow_alpha = True
        self.ui.obscuringMaterialColourEdit.allow_alpha = True
        self.ui.grassMaterialColourEdit.allow_alpha = True
        self.ui.stoneMaterialColourEdit.allow_alpha = True
        self.ui.woodMaterialColourEdit.allow_alpha = True
        self.ui.waterMaterialColourEdit.allow_alpha = True
        self.ui.nonWalkMaterialColourEdit.allow_alpha = True
        self.ui.transparentMaterialColourEdit.allow_alpha = True
        self.ui.carpetMaterialColourEdit.allow_alpha = True
        self.ui.metalMaterialColourEdit.allow_alpha = True
        self.ui.puddlesMaterialColourEdit.allow_alpha = True
        self.ui.swampMaterialColourEdit.allow_alpha = True
        self.ui.mudMaterialColourEdit.allow_alpha = True
        self.ui.leavesMaterialColourEdit.allow_alpha = True
        self.ui.lavaMaterialColourEdit.allow_alpha = True
        self.ui.bottomlessPitMaterialColourEdit.allow_alpha = True
        self.ui.deepWaterMaterialColourEdit.allow_alpha = True
        self.ui.doorMaterialColourEdit.allow_alpha = True
        self.ui.nonWalkGrassMaterialColourEdit.allow_alpha = True

        self.ui.controls3dResetButton.clicked.connect(self.resetControls3d)
        self.ui.controlsFcResetButton.clicked.connect(self.resetControlsFc)
        self.ui.controls2dResetButton.clicked.connect(self.resetControls2d)
        self.ui.coloursResetButton.clicked.connect(self.resetColours)

        self.setup_values()

        # Install the event filter on all child widgets
        self.installEventFilters(self, self.noScrollEventFilter)
        # self.installEventFilters(self, self.hoverEventFilter, include_types=[QWidget])

    def _load3dBindValues(self):
        self.ui.moveCameraSensitivity3dEdit.setValue(self.settings.moveCameraSensitivity3d)
        self.ui.rotateCameraSensitivity3dEdit.setValue(self.settings.rotateCameraSensitivity3d)
        self.ui.zoomCameraSensitivity3dEdit.setValue(self.settings.zoomCameraSensitivity3d)
        self.ui.boostedMoveCameraSensitivity3dEdit.setValue(
            self.settings.boostedMoveCameraSensitivity3d
        )

        for bindEdit in [widget for widget in dir(self.ui) if "3dBindEdit" in widget]:
            bindWidget: SetBindWidget = getattr(self.ui, bindEdit)
            self._registerBind(bindWidget, bindEdit[:-4])

    def _loadFcBindValues(self):
        self.ui.flySpeedFcEdit.setValue(self.settings.flyCameraSpeedFC)
        self.ui.rotateCameraSensitivityFcEdit.setValue(self.settings.rotateCameraSensitivity3d)
        self.ui.boostedFlyCameraSpeedFCEdit.setValue(self.settings.boostedFlyCameraSpeedFC)

        for bindEdit in [widget for widget in dir(self.ui) if "FcBindEdit" in widget]:
            bindWidget: SetBindWidget = getattr(self.ui, bindEdit)
            self._registerBind(bindWidget, bindEdit[:-4])

    def _load2dBindValues(self):
        self.ui.moveCameraSensitivity2dEdit.setValue(self.settings.moveCameraSensitivity2d)
        self.ui.rotateCameraSensitivity2dEdit.setValue(self.settings.rotateCameraSensitivity2d)
        self.ui.zoomCameraSensitivity2dEdit.setValue(self.settings.zoomCameraSensitivity2d)

        for bindEdit in [widget for widget in dir(self.ui) if "2dBindEdit" in widget]:
            bindWidget: SetBindWidget = getattr(self.ui, bindEdit)
            self._registerBind(bindWidget, bindEdit[:-4])

    def _loadColourValues(self):
        for colorEdit in [widget for widget in dir(self.ui) if "ColourEdit" in widget]:
            colorWidget: ColorEdit = getattr(self.ui, colorEdit)
            self._registerColour(colorWidget, colorEdit[:-4])

    def _populate_renderer_refresh_rate_combo(self) -> None:
        screen: QScreen | None = QApplication.primaryScreen()
        detected_hz: int = (
            round(screen.refreshRate()) if screen and screen.refreshRate() > 0 else 60
        )
        self.ui.rendererRefreshRateCombo.clear()
        self.ui.rendererRefreshRateCombo.addItem(
            f"Auto-Detect -- Match Refresh Rate ({detected_hz} Hz)",
            0,
        )
        for hz in (30, 60, 120, 144, 240):
            self.ui.rendererRefreshRateCombo.addItem(f"{hz} Hz", hz)
        saved = self.settings.rendererRefreshRateHz
        idx = self.ui.rendererRefreshRateCombo.findData(saved)
        self.ui.rendererRefreshRateCombo.setCurrentIndex(max(0, idx))

    def setup_values(self):
        self.ui.useBlenderCheckbox.setChecked(self.settings.useBlender)
        self.ui.fovSpin.setValue(self.settings.fieldOfView)
        self._populate_renderer_refresh_rate_combo()
        # Restore saved control scheme in combo (block signals to avoid applying the
        # scheme on load, since the stored bindings already reflect the saved state).
        if hasattr(self.ui, "controlSchemeCombo"):
            saved_scheme = normalize_control_scheme(self.settings.controlScheme)
            idx = self.ui.controlSchemeCombo.findData(saved_scheme)
            self.ui.controlSchemeCombo.blockSignals(True)
            self.ui.controlSchemeCombo.setCurrentIndex(max(0, idx))
            self.ui.controlSchemeCombo.blockSignals(False)
        self._load3dBindValues()
        self._loadFcBindValues()
        self._load2dBindValues()
        self._loadColourValues()

    def save(self):
        super().save()
        self.settings.useBlender = self.ui.useBlenderCheckbox.isChecked()
        self.settings.fieldOfView = self.ui.fovSpin.value()
        data = self.ui.rendererRefreshRateCombo.currentData()
        self.settings.rendererRefreshRateHz = data if data is not None else 0
        self.settings.flyCameraSpeedFC = self.ui.flySpeedFcEdit.value()
        self.settings.boostedFlyCameraSpeedFC = self.ui.boostedFlyCameraSpeedFCEdit.value()

        self.settings.moveCameraSensitivity3d = self.ui.moveCameraSensitivity3dEdit.value()
        self.settings.rotateCameraSensitivity3d = self.ui.rotateCameraSensitivity3dEdit.value()
        self.settings.zoomCameraSensitivity3d = self.ui.zoomCameraSensitivity3dEdit.value()
        self.settings.boostedMoveCameraSensitivity3d = (
            self.ui.boostedMoveCameraSensitivity3dEdit.value()
        )

        self.settings.moveCameraSensitivity2d = self.ui.moveCameraSensitivity2dEdit.value()
        self.settings.rotateCameraSensitivity2d = self.ui.rotateCameraSensitivity2dEdit.value()
        self.settings.zoomCameraSensitivity2d = self.ui.zoomCameraSensitivity2dEdit.value()

        if hasattr(self.ui, "controlSchemeCombo"):
            scheme = self.ui.controlSchemeCombo.currentData()
            if scheme:
                self.settings.controlScheme = normalize_control_scheme(scheme)

    def resetControls3d(self):
        self.settings.resetControls3d()
        self._load3dBindValues()

    def _on_scheme_changed(self, index: int) -> None:
        """Apply a control scheme preset when the combo selection changes."""
        if not hasattr(self.ui, "controlSchemeCombo"):
            return
        scheme: str = normalize_control_scheme(self.ui.controlSchemeCombo.itemData(index))
        if scheme == "standard":
            bindings = STANDARD_BINDINGS
        elif scheme == "classic":
            bindings = LEGACY_BINDINGS
        else:
            return
        self.settings.controlScheme = scheme
        for attr_name, value in bindings.items():
            setattr(self.settings, attr_name, value)
        self._load3dBindValues()
        self._load2dBindValues()

    def resetControlsFc(self):
        self.settings.resetControlsFc()
        self._loadFcBindValues()

    def resetControls2d(self):
        self.settings.resetControls2d()
        self._load2dBindValues()

    def resetColours(self):
        self.settings.resetMaterialColors()
        self._loadColourValues()


class ModuleDesignerSettings(Settings):
    def __init__(self):
        super().__init__("ModuleDesigner")

    def resetControls3d(self):
        for setting in dir(self):
            if not setting.endswith(("3d", "3dBind")):
                continue
            attr_value = getattr(self.__class__, setting)
            if isinstance(attr_value, SettingsProperty):
                attr_value.reset_to_default(self)
        self.get_property("toggleLockInstancesBind").reset_to_default(self)

    def resetControls2d(self):
        for setting in dir(self):
            if not setting.endswith(("2d", "2dBind")):
                continue
            attr_value = getattr(self.__class__, setting)
            if isinstance(attr_value, SettingsProperty):
                attr_value.reset_to_default(self)

    def resetControlsFc(self):
        for setting in dir(self):
            if not setting.endswith(("FC", "FcBind")):
                continue
            attr_value = getattr(self.__class__, setting)
            if isinstance(attr_value, SettingsProperty):
                attr_value.reset_to_default(self)

    def resetMaterialColors(self):
        for setting in dir(self):
            if not setting.endswith("Colour"):
                continue
            attr_value = getattr(self.__class__, setting)
            if isinstance(attr_value, SettingsProperty):
                attr_value.reset_to_default(self)

    # region Ints/Binds (Controls - 3D)
    moveCameraSensitivity3d: SettingsProperty[int] = Settings.addSetting(
        "moveCameraSensitivity3d",
        100,
    )
    rotateCameraSensitivity3d: SettingsProperty[int] = Settings.addSetting(
        "rotateCameraSensitivity3d",
        100,
    )
    zoomCameraSensitivity3d: SettingsProperty[int] = Settings.addSetting(
        "zoomCameraSensitivity3d",
        100,
    )
    boostedMoveCameraSensitivity3d: SettingsProperty[int] = Settings.addSetting(
        "boostedMoveCameraSensitivity3d",
        250,
    )
    speedBoostCamera3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "speedBoostCamera3dBind",
        ({Qt.Key.Key_Shift}, set()),
    )
    moveCameraXY3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraXY3dBind",
        ({Qt.Key.Key_Shift}, {Qt.MouseButton.MiddleButton}),
    )
    moveCameraZ3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraZ3dBind",
        ({Qt.Key.Key_Control}, set()),
    )
    moveCameraPlane3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraPlane3dBind",
        ({Qt.Key.Key_Shift}, {Qt.MouseButton.MiddleButton}),
    )
    rotateCamera3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateCamera3dBind",
        (set(), {Qt.MouseButton.MiddleButton}),
    )
    zoomCamera3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "zoomCamera3dBind",
        (set(), None),
    )
    zoomCameraMM3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "zoomCameraMM3dBind",
        ({Qt.Key.Key_Control}, {Qt.MouseButton.MiddleButton}),
    )
    rotateSelected3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateSelected3dBind",
        ({Qt.Key.Key_Alt}, {Qt.MouseButton.LeftButton}),
    )
    moveSelectedXY3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveSelectedXY3dBind",
        (set(), {Qt.MouseButton.LeftButton}),
    )
    moveSelectedZ3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveSelectedZ3dBind",
        ({Qt.Key.Key_Shift}, {Qt.MouseButton.LeftButton}),
    )
    rotateObject3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateObject3dBind",
        ({Qt.Key.Key_Control}, {Qt.MouseButton.LeftButton}),
    )
    panCameraLMB3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "panCameraLMB3dBind",
        ({Qt.Key.Key_Control}, {Qt.MouseButton.LeftButton}),
    )
    selectObject3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "selectObject3dBind",
        (set(), {Qt.MouseButton.LeftButton}),
    )
    toggleFreeCam3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "toggleFreeCam3dBind",
        ({Qt.Key.Key_F}, set()),
    )
    deleteObject3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "deleteObject3dBind",
        ({Qt.Key.Key_Delete}, None),
    )
    moveCameraToSelected3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraToSelected3dBind",
        ({Qt.Key.Key_Period}, None),
    )
    moveCameraToCursor3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraToCursor3dBind",
        ({Qt.Key.Key_X}, None),
    )
    moveCameraToEntryPoint3dBind = Settings.addSetting(
        "moveCameraToEntryPoint3dBind",
        ({Qt.Key.Key_C}, None),
    )
    rotateCameraLeft3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateCameraLeft3dBind",
        ({Qt.Key.Key_7}, None),
    )
    rotateCameraRight3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateCameraRight3dBind",
        ({Qt.Key.Key_9}, None),
    )
    rotateCameraUp3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateCameraUp3dBind",
        ({Qt.Key.Key_1}, None),
    )
    rotateCameraDown3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateCameraDown3dBind",
        ({Qt.Key.Key_3}, None),
    )
    moveCameraBackward3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraBackward3dBind",
        ({Qt.Key.Key_2}, None),
    )
    moveCameraForward3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraForward3dBind",
        ({Qt.Key.Key_8}, None),
    )
    moveCameraLeft3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraLeft3dBind",
        ({Qt.Key.Key_4}, None),
    )
    moveCameraRight3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraRight3dBind",
        ({Qt.Key.Key_6}, None),
    )
    moveCameraUp3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraUp3dBind",
        ({Qt.Key.Key_Q}, None),
    )
    moveCameraDown3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraDown3dBind",
        ({Qt.Key.Key_E}, None),
    )
    zoomCameraIn3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "zoomCameraIn3dBind",
        ({Qt.Key.Key_Plus}, None),
    )
    zoomCameraOut3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "zoomCameraOut3dBind",
        ({Qt.Key.Key_Minus}, None),
    )
    duplicateObject3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "duplicateObject3dBind",
        ({Qt.Key.Key_Shift}, {Qt.MouseButton.LeftButton}),
    )
    walkmeshVertexDragXAxis3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "walkmeshVertexDragXAxis3dBind",
        ({Qt.Key.Key_X}, set()),
    )
    walkmeshVertexDragYAxis3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "walkmeshVertexDragYAxis3dBind",
        ({Qt.Key.Key_Y}, set()),
    )
    walkmeshVertexDragZAxis3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "walkmeshVertexDragZAxis3dBind",
        ({Qt.Key.Key_Z}, set()),
    )
    resetCameraView3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "resetCameraView3dBind",
        ({Qt.Key.Key_Home}, set()),
    )
    # Standard numpad view presets
    viewFront3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "viewFront3dBind",
        ({Qt.Key.Key_1}, None),
    )
    viewRight3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "viewRight3dBind",
        ({Qt.Key.Key_3}, None),
    )
    viewTop3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "viewTop3dBind",
        ({Qt.Key.Key_7}, None),
    )
    viewBack3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "viewBack3dBind",
        ({Qt.Key.Key_Control, Qt.Key.Key_1}, None),
    )
    viewLeft3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "viewLeft3dBind",
        ({Qt.Key.Key_Control, Qt.Key.Key_3}, None),
    )
    viewBottom3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "viewBottom3dBind",
        ({Qt.Key.Key_Control, Qt.Key.Key_7}, None),
    )
    viewToggleOrtho3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "viewToggleOrtho3dBind",
        ({Qt.Key.Key_5}, None),
    )
    viewCamera3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "viewCamera3dBind",
        ({Qt.Key.Key_0}, None),
    )
    frameAll3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "frameAll3dBind",
        ({Qt.Key.Key_Home}, set()),
    )
    frameSelected3dBind: SettingsProperty[Bind] = Settings.addSetting(
        "frameSelected3dBind",
        ({Qt.Key.Key_Period}, None),
    )
    # endregion

    # region Int/Binds (Controls - 3D FreeCam)
    rotateCameraSensitivityFC = Settings.addSetting(
        "rotateCameraSensitivityFC",
        100,
    )
    flyCameraSpeedFC = Settings.addSetting(
        "flyCameraSpeedFC",
        100,
    )
    boostedFlyCameraSpeedFC = Settings.addSetting(
        "boostedFlyCameraSpeedFC",
        250,
    )

    speedBoostCameraFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "speedBoostCameraFcBind",
        ({Qt.Key.Key_Shift}, set()),
    )
    moveCameraForwardFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraForwardFcBind",
        ({Qt.Key.Key_W}, set()),
    )
    moveCameraBackwardFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraBackwardFcBind",
        ({Qt.Key.Key_S}, set()),
    )
    moveCameraLeftFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraLeftFcBind",
        ({Qt.Key.Key_A}, set()),
    )
    moveCameraRightFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraRightFcBind",
        ({Qt.Key.Key_D}, set()),
    )
    moveCameraUpFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraUpFcBind",
        ({Qt.Key.Key_Q}, set()),
    )
    moveCameraDownFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraDownFcBind",
        ({Qt.Key.Key_E}, set()),
    )
    rotateCameraLeftFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateCameraLeftFcBind",
        ({Qt.Key.Key_7}, None),
    )
    rotateCameraRightFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateCameraRightFcBind",
        ({Qt.Key.Key_9}, None),
    )
    rotateCameraUpFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateCameraUpFcBind",
        ({Qt.Key.Key_1}, None),
    )
    rotateCameraDownFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateCameraDownFcBind",
        ({Qt.Key.Key_3}, None),
    )
    zoomCameraInFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "zoomCameraInFcBind",
        ({Qt.Key.Key_Plus}, None),
    )
    zoomCameraOutFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "zoomCameraOutFcBind",
        ({Qt.Key.Key_Minus}, None),
    )
    moveCameraToEntryPointFcBind = Settings.addSetting(
        "moveCameraToEntryPointFcBind",
        ({Qt.Key.Key_C}, None),
    )
    moveCameraToCursorFcBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraToCursorFcBind",
        ({Qt.Key.Key_X}, None),
    )
    # endregion

    # region Int/Binds (Controls - 2D)
    moveCameraSensitivity2d: SettingsProperty[int] = Settings.addSetting(
        "moveCameraSensitivity2d",
        100,
    )
    rotateCameraSensitivity2d: SettingsProperty[int] = Settings.addSetting(
        "rotateCameraSensitivity2d",
        100,
    )
    zoomCameraSensitivity2d: SettingsProperty[int] = Settings.addSetting(
        "zoomCameraSensitivity2d",
        100,
    )

    moveCamera2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCamera2dBind",
        (set(), {Qt.MouseButton.MiddleButton}),
    )
    zoomCamera2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "zoomCamera2dBind",
        ({Qt.Key.Key_Control}, set()),
    )
    rotateCamera2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateCamera2dBind",
        ({Qt.Key.Key_Control}, {Qt.MouseButton.MiddleButton}),
    )
    selectObject2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "selectObject2dBind",
        (set(), {Qt.MouseButton.LeftButton}),
    )
    moveObject2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveObject2dBind",
        (set(), {Qt.MouseButton.LeftButton}),
    )
    rotateObject2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "rotateObject2dBind",
        (set(), {Qt.MouseButton.MiddleButton}),
    )
    deleteObject2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "deleteObject2dBind",
        ({Qt.Key.Key_Delete}, set()),
    )
    moveCameraToSelected2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "snapCameraToSelected2dBind",
        ({Qt.Key.Key_Period}, set()),
    )
    frameAll2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "frameAll2dBind",
        ({Qt.Key.Key_Home}, set()),
    )
    resetCameraView2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "resetCameraView2dBind",
        ({Qt.Key.Key_Control, Qt.Key.Key_0}, set()),
    )
    zoomCameraIn2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "zoomCameraIn2dBind",
        ({Qt.Key.Key_Equal}, None),
    )
    zoomCameraOut2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "zoomCameraOut2dBind",
        ({Qt.Key.Key_Minus}, None),
    )
    moveCameraLeft2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraLeft2dBind",
        ({Qt.Key.Key_Left}, None),
    )
    moveCameraRight2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraRight2dBind",
        ({Qt.Key.Key_Right}, None),
    )
    moveCameraUp2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraUp2dBind",
        ({Qt.Key.Key_Up}, None),
    )
    moveCameraDown2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "moveCameraDown2dBind",
        ({Qt.Key.Key_Down}, None),
    )
    duplicateObject2dBind: SettingsProperty[Bind] = Settings.addSetting(
        "duplicateObject2dBind",
        ({Qt.Key.Key_Alt}, {Qt.MouseButton.LeftButton}),
    )
    # endregion

    # region Binds (Controls - Both)
    toggleLockInstancesBind: SettingsProperty[Bind] = Settings.addSetting(
        "toggleLockInstancesBind",
        ({Qt.Key.Key_L}, set()),
    )
    # endregion

    # region Misc
    controlScheme: SettingsProperty[str] = Settings.addSetting(
        "controlScheme",
        "standard",
    )
    # endregion

    # region Ints (Material Colours)
    undefinedMaterialColour = Settings.addSetting(
        "undefinedMaterialColour",
        Color(0.400, 0.400, 0.400, 0.5).rgba_integer(),
    )
    dirtMaterialColour = Settings.addSetting(
        "dirtMaterialColour",
        Color(0.610, 0.235, 0.050, 0.5).rgba_integer(),
    )
    obscuringMaterialColour = Settings.addSetting(
        "obscuringMaterialColour",
        Color(0.100, 0.100, 0.100, 0.5).rgba_integer(),
    )
    grassMaterialColour = Settings.addSetting(
        "grassMaterialColour",
        Color(0.000, 0.600, 0.000, 0.5).rgba_integer(),
    )
    stoneMaterialColour = Settings.addSetting(
        "stoneMaterialColour",
        Color(0.162, 0.216, 0.279, 0.5).rgba_integer(),
    )
    woodMaterialColour = Settings.addSetting(
        "woodMaterialColour",
        Color(0.258, 0.059, 0.007, 0.5).rgba_integer(),
    )
    waterMaterialColour = Settings.addSetting(
        "waterMaterialColour",
        Color(0.000, 0.000, 1.000, 0.5).rgba_integer(),
    )
    nonWalkMaterialColour = Settings.addSetting(
        "nonWalkMaterialColour",
        Color(1.000, 0.000, 0.000, 0.5).rgba_integer(),
    )
    transparentMaterialColour = Settings.addSetting(
        "transparentMaterialColour",
        Color(1.000, 1.000, 1.000, 0.5).rgba_integer(),
    )
    carpetMaterialColour = Settings.addSetting(
        "carpetMaterialColour",
        Color(1.000, 0.000, 1.000, 0.5).rgba_integer(),
    )
    metalMaterialColour = Settings.addSetting(
        "metalMaterialColour",
        Color(0.434, 0.552, 0.730, 0.5).rgba_integer(),
    )
    puddlesMaterialColour = Settings.addSetting(
        "puddlesMaterialColour",
        Color(0.509, 0.474, 0.147, 0.5).rgba_integer(),
    )
    swampMaterialColour = Settings.addSetting(
        "swampMaterialColour",
        Color(0.216, 0.216, 0.000, 0.5).rgba_integer(),
    )
    mudMaterialColour = Settings.addSetting(
        "mudMaterialColour",
        Color(0.091, 0.147, 0.028, 0.5).rgba_integer(),
    )
    leavesMaterialColour = Settings.addSetting(
        "leavesMaterialColour",
        Color(0.000, 0.000, 0.216, 0.5).rgba_integer(),
    )
    doorMaterialColour = Settings.addSetting(
        "doorMaterialColour",
        Color(0.000, 0.000, 0.000, 0.5).rgba_integer(),
    )
    lavaMaterialColour = Settings.addSetting(
        "lavaMaterialColour",
        Color(0.300, 0.000, 0.000, 0.5).rgba_integer(),
    )
    bottomlessPitMaterialColour = Settings.addSetting(
        "bottomlessPitMaterialColour",
        Color(0.000, 0.000, 0.000, 0.5).rgba_integer(),
    )
    deepWaterMaterialColour = Settings.addSetting(
        "deepWaterMaterialColour",
        Color(0.000, 0.000, 0.216, 0.5).rgba_integer(),
    )
    nonWalkGrassMaterialColour = Settings.addSetting(
        "nonWalkGrassMaterialColour",
        Color(0.000, 0.600, 0.000, 0.5).rgba_integer(),
    )
    # endregion

    # region Ints
    fieldOfView = Settings.addSetting(
        "fieldOfView",
        70,
    )
    # 0 = auto-detect (match primary monitor Hz); otherwise target Hz (e.g. 60, 120)
    rendererRefreshRateHz: SettingsProperty[int] = Settings.addSetting(
        "rendererRefreshRateHz",
        0,
    )
    # endregion

    useBlender: SettingsProperty[bool] = Settings.addSetting(
        "useBlender",
        False,
    )
