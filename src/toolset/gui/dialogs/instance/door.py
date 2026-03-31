"""GIT door instance editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QMessageBox

from pykotor.common.misc import Color
from pykotor.resource.generics.git import GITDoor, GITModuleLink
from toolset.data.installation import HTInstallation
from toolset.gui.common.localization import translate as tr
from toolset.gui.dialogs.instance._util import parse_resref_field

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class DoorDialog(QDialog):
    def __init__(self, parent: QWidget | None, instance: GITDoor, installation: HTInstallation):
        super().__init__(parent)
        self._instance: GITDoor = instance
        self._installation: HTInstallation = installation

        from toolset.uic.qtpy.dialogs.instance.door import Ui_Dialog

        self.ui: Ui_Dialog = Ui_Dialog()
        self.ui.setupUi(self)
        self._populate_link_combo()
        self.ui.useTweakColorCheck.toggled.connect(self.ui.tweakBgrSpin.setEnabled)
        self._load_from_instance()

    def _populate_link_combo(self) -> None:
        combo = self.ui.linkedToFlagsCombo
        combo.clear()
        combo.addItem("No link", int(GITModuleLink.NoLink))
        combo.addItem("To door", int(GITModuleLink.ToDoor))
        combo.addItem("To waypoint", int(GITModuleLink.ToWaypoint))

    def _load_from_instance(self) -> None:
        self.ui.resrefEdit.setText(str(self._instance.resref))
        self.ui.xPosSpin.setValue(self._instance.position.x)
        self.ui.yPosSpin.setValue(self._instance.position.y)
        self.ui.zPosSpin.setValue(self._instance.position.z)
        self.ui.bearingSpin.setValue(self._instance.bearing)
        self.ui.tagEdit.setText(self._instance.tag)
        self.ui.linkedToEdit.setText(self._instance.linked_to)
        v = int(self._instance.linked_to_flags)
        idx = self.ui.linkedToFlagsCombo.findData(v, Qt.ItemDataRole.UserRole)
        self.ui.linkedToFlagsCombo.setCurrentIndex(max(0, idx))
        self.ui.linkedToModuleEdit.setText(str(self._instance.linked_to_module))
        self.ui.transitionStrRefSpin.setValue(self._instance.transition_destination.stringref)
        use_color = self._instance.tweak_color is not None
        self.ui.useTweakColorCheck.setChecked(use_color)
        self.ui.tweakBgrSpin.setEnabled(use_color)
        if self._instance.tweak_color is not None:
            self.ui.tweakBgrSpin.setValue(self._instance.tweak_color.bgr_integer())
        else:
            self.ui.tweakBgrSpin.setValue(0)

    def accept(self) -> None:
        resref, err = parse_resref_field(self.ui.resrefEdit.text())
        if err:
            QMessageBox.critical(self, tr("Invalid resref"), err)
            return
        assert resref is not None
        mod_text = self.ui.linkedToModuleEdit.text()
        mod_rr, mod_err = parse_resref_field(mod_text)
        if mod_err:
            QMessageBox.critical(self, tr("Invalid module resref"), mod_err)
            return
        assert mod_rr is not None

        self._instance.resref = resref
        self._instance.position.x = self.ui.xPosSpin.value()
        self._instance.position.y = self.ui.yPosSpin.value()
        self._instance.position.z = self.ui.zPosSpin.value()
        self._instance.bearing = self.ui.bearingSpin.value()
        self._instance.tag = self.ui.tagEdit.text().strip()
        self._instance.linked_to = self.ui.linkedToEdit.text().strip()
        raw_flags = self.ui.linkedToFlagsCombo.currentData(Qt.ItemDataRole.UserRole)
        self._instance.linked_to_flags = GITModuleLink(int(raw_flags))
        self._instance.linked_to_module = mod_rr
        self._instance.transition_destination.stringref = self.ui.transitionStrRefSpin.value()
        if self.ui.useTweakColorCheck.isChecked():
            self._instance.tweak_color = Color.from_bgr_integer(self.ui.tweakBgrSpin.value())
        else:
            self._instance.tweak_color = None
        super().accept()
