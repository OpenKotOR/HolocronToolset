"""GIT (module instances) settings widget: walkmesh material colors and instance display options."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy import QtCore
from qtpy.QtCore import Qt

from toolset.gui.common.filters import NoScrollEventFilter
from toolset.gui.widgets.settings.editor_settings.git import GITSettings
from toolset.gui.widgets.settings.widgets.base import SettingsWidget

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


STANDARD_BINDINGS: dict[str, tuple] = {
    "moveCameraBind": (set(), {Qt.MouseButton.MiddleButton}),
    "rotateCameraBind": ({Qt.Key.Key_Control}, {Qt.MouseButton.MiddleButton}),
    "zoomCameraBind": (set(), set()),
    "rotateSelectedToPointBind": ({Qt.Key.Key_Alt}, {Qt.MouseButton.MiddleButton}),
    "moveCameraToSelected2dBind": ({Qt.Key.Key_Period}, set()),
    "frameAll2dBind": ({Qt.Key.Key_Home}, set()),
    "resetCameraView2dBind": ({Qt.Key.Key_Control, Qt.Key.Key_0}, set()),
    "zoomCameraIn2dBind": ({Qt.Key.Key_Equal}, None),
    "zoomCameraOut2dBind": ({Qt.Key.Key_Minus}, None),
    "moveCameraLeft2dBind": ({Qt.Key.Key_Left}, None),
    "moveCameraRight2dBind": ({Qt.Key.Key_Right}, None),
    "moveCameraUp2dBind": ({Qt.Key.Key_Up}, None),
    "moveCameraDown2dBind": ({Qt.Key.Key_Down}, None),
}

LEGACY_BINDINGS: dict[str, tuple] = {
    "moveCameraBind": ({Qt.Key.Key_Control}, {Qt.MouseButton.LeftButton}),
    "rotateCameraBind": ({Qt.Key.Key_Control}, {Qt.MouseButton.MiddleButton}),
    "zoomCameraBind": ({Qt.Key.Key_Control}, set()),
    "rotateSelectedToPointBind": (set(), {Qt.MouseButton.MiddleButton}),
    "moveCameraToSelected2dBind": ({Qt.Key.Key_Z}, set()),
    "frameAll2dBind": ({Qt.Key.Key_Home}, set()),
    "resetCameraView2dBind": ({Qt.Key.Key_Control, Qt.Key.Key_0}, set()),
    "zoomCameraIn2dBind": ({Qt.Key.Key_Equal}, None),
    "zoomCameraOut2dBind": ({Qt.Key.Key_Minus}, None),
    "moveCameraLeft2dBind": ({Qt.Key.Key_Left}, None),
    "moveCameraRight2dBind": ({Qt.Key.Key_Right}, None),
    "moveCameraUp2dBind": ({Qt.Key.Key_Up}, None),
    "moveCameraDown2dBind": ({Qt.Key.Key_Down}, None),
}


def normalize_control_scheme(scheme: str | None) -> str:
    if scheme in {None, "", "blender"}:
        return "standard"
    return scheme


class GITWidget(SettingsWidget):
    sig_settings_edited = QtCore.Signal()  # pyright: ignore[reportPrivateImportUsage]

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.settings: GITSettings = GITSettings()

        from toolset.uic.qtpy.widgets.settings.git import Ui_Form

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        from qtpy.QtWidgets import QComboBox, QHBoxLayout, QLabel

        if not hasattr(self.ui, "controlSchemeCombo"):
            scheme_row = QHBoxLayout()
            scheme_label = QLabel("Control Scheme", self.ui.groupBox)
            scheme_label.setObjectName("controlSchemeLabel")
            self.ui.controlSchemeCombo = QComboBox(self.ui.groupBox)
            self.ui.controlSchemeCombo.setObjectName("controlSchemeCombo")
            self.ui.controlSchemeCombo.addItem("Standard (default)", "standard")
            self.ui.controlSchemeCombo.addItem("Classic (legacy)", "classic")
            scheme_row.addWidget(scheme_label)
            scheme_row.addWidget(self.ui.controlSchemeCombo)
            self.ui.verticalLayout_2.insertLayout(1, scheme_row)

        from toolset.gui.widgets.set_bind import SetBindWidget

        extra_binds: list[tuple[str, str]] = [
            ("moveCameraToSelected2dBindEdit", "Frame Selected 2D"),
            ("frameAll2dBindEdit", "Frame All 2D"),
            ("resetCameraView2dBindEdit", "Reset View 2D"),
            ("zoomCameraIn2dBindEdit", "Zoom In 2D"),
            ("zoomCameraOut2dBindEdit", "Zoom Out 2D"),
            ("moveCameraLeft2dBindEdit", "Pan Left 2D"),
            ("moveCameraRight2dBindEdit", "Pan Right 2D"),
            ("moveCameraUp2dBindEdit", "Pan Up 2D"),
            ("moveCameraDown2dBindEdit", "Pan Down 2D"),
        ]
        for attr_name, label_text in extra_binds:
            if hasattr(self.ui, attr_name):
                continue
            row = self.ui.formLayout.rowCount()
            bind_label = QLabel(label_text, self.ui.widget)
            bind_label.setObjectName(f"{attr_name}Label")
            bind_widget = SetBindWidget(self.ui.widget)
            bind_widget.setObjectName(attr_name)
            setattr(self.ui, attr_name, bind_widget)
            self.ui.formLayout.setWidget(row, self.ui.formLayout.LabelRole, bind_label)
            self.ui.formLayout.setWidget(row, self.ui.formLayout.FieldRole, bind_widget)

        self.ui.controlSchemeCombo.currentIndexChanged.connect(self._on_scheme_changed)

        self.ui.undefinedMaterialColourEdit.allowAlpha = True
        self.ui.dirtMaterialColourEdit.allowAlpha = True
        self.ui.obscuringMaterialColourEdit.allowAlpha = True
        self.ui.grassMaterialColourEdit.allowAlpha = True
        self.ui.stoneMaterialColourEdit.allowAlpha = True
        self.ui.woodMaterialColourEdit.allowAlpha = True
        self.ui.waterMaterialColourEdit.allowAlpha = True
        self.ui.nonWalkMaterialColourEdit.allowAlpha = True
        self.ui.transparentMaterialColourEdit.allowAlpha = True
        self.ui.carpetMaterialColourEdit.allowAlpha = True
        self.ui.metalMaterialColourEdit.allowAlpha = True
        self.ui.puddlesMaterialColourEdit.allowAlpha = True
        self.ui.swampMaterialColourEdit.allowAlpha = True
        self.ui.mudMaterialColourEdit.allowAlpha = True
        self.ui.leavesMaterialColourEdit.allowAlpha = True
        self.ui.lavaMaterialColourEdit.allowAlpha = True
        self.ui.bottomlessPitMaterialColourEdit.allowAlpha = True
        self.ui.deepWaterMaterialColourEdit.allowAlpha = True
        self.ui.doorMaterialColourEdit.allowAlpha = True
        self.ui.nonWalkGrassMaterialColourEdit.allowAlpha = True

        self.ui.coloursResetButton.clicked.connect(self.resetColours)
        self.ui.controlsResetButton.clicked.connect(self.resetControls)

        self.setup_values()

        # Install the event filter on all child widgets
        self.noScrollEventFilter: NoScrollEventFilter = NoScrollEventFilter(self)
        self.installEventFilters(self, self.noScrollEventFilter)

    def _setupColourValues(self):
        for colorEdit in [widget for widget in dir(self.ui) if "ColourEdit" in widget]:
            self._registerColour(getattr(self.ui, colorEdit), colorEdit[:-4])

    def _setupBindValues(self):
        for bindEdit in [widget for widget in dir(self.ui) if "BindEdit" in widget]:
            self._registerBind(getattr(self.ui, bindEdit), bindEdit[:-4])

    def setup_values(self):
        if hasattr(self.ui, "controlSchemeCombo"):
            saved_scheme = normalize_control_scheme(self.settings.controlScheme)
            idx = self.ui.controlSchemeCombo.findData(saved_scheme)
            self.ui.controlSchemeCombo.blockSignals(True)
            self.ui.controlSchemeCombo.setCurrentIndex(max(0, idx))
            self.ui.controlSchemeCombo.blockSignals(False)
        self._setupColourValues()
        self._setupBindValues()

    def _on_scheme_changed(self, index: int) -> None:
        scheme = normalize_control_scheme(self.ui.controlSchemeCombo.itemData(index))
        if scheme == "standard":
            bindings = STANDARD_BINDINGS
        elif scheme == "classic":
            bindings = LEGACY_BINDINGS
        else:
            return
        self.settings.controlScheme = scheme
        for attr_name, value in bindings.items():
            setattr(self.settings, attr_name, value)
        self._setupBindValues()

    def resetColours(self):
        self.settings.resetMaterialColors()
        self._setupColourValues()

    def resetControls(self):
        self.settings.resetControls()
        self._setupBindValues()
