"""GIT trigger instance editor (geometry uses editor geometry mode)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QMessageBox

from pykotor.resource.generics.git import GITModuleLink, GITTrigger
from toolset.data.installation import HTInstallation
from toolset.gui.common.localization import translate as tr
from toolset.gui.dialogs.instance._util import parse_resref_field

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class TriggerDialog(QDialog):
    def __init__(self, parent: QWidget | None, instance: GITTrigger, installation: HTInstallation):
        super().__init__(parent)
        self._instance: GITTrigger = instance
        self._installation: HTInstallation = installation

        from toolset.uic.qtpy.dialogs.instance.trigger import Ui_Dialog

        self.ui: Ui_Dialog = Ui_Dialog()
        self.ui.setupUi(self)
        self._populate_link_combo()
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
        self.ui.tagEdit.setText(self._instance.tag)
        self.ui.linkedToEdit.setText(self._instance.linked_to)
        v = int(self._instance.linked_to_flags)
        idx = self.ui.linkedToFlagsCombo.findData(v, Qt.ItemDataRole.UserRole)
        self.ui.linkedToFlagsCombo.setCurrentIndex(max(0, idx))
        self.ui.linkedToModuleEdit.setText(str(self._instance.linked_to_module))
        self.ui.transitionStrRefSpin.setValue(self._instance.transition_destination.stringref)

    def accept(self) -> None:
        resref, err = parse_resref_field(self.ui.resrefEdit.text())
        if err:
            QMessageBox.critical(self, tr("Invalid resref"), err)
            return
        assert resref is not None
        mod_rr, mod_err = parse_resref_field(self.ui.linkedToModuleEdit.text())
        if mod_err:
            QMessageBox.critical(self, tr("Invalid module resref"), mod_err)
            return
        assert mod_rr is not None

        self._instance.resref = resref
        self._instance.position.x = self.ui.xPosSpin.value()
        self._instance.position.y = self.ui.yPosSpin.value()
        self._instance.position.z = self.ui.zPosSpin.value()
        self._instance.tag = self.ui.tagEdit.text().strip()
        self._instance.linked_to = self.ui.linkedToEdit.text().strip()
        raw_flags = self.ui.linkedToFlagsCombo.currentData(Qt.ItemDataRole.UserRole)
        self._instance.linked_to_flags = GITModuleLink(int(raw_flags))
        self._instance.linked_to_module = mod_rr
        self._instance.transition_destination.stringref = self.ui.transitionStrRefSpin.value()
        super().accept()
