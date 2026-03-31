"""GIT waypoint instance editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtWidgets import QDialog, QMessageBox

from pykotor.common.language import LocalizedString
from pykotor.resource.generics.git import GITWaypoint
from toolset.data.installation import HTInstallation
from toolset.gui.common.localization import translate as tr
from toolset.gui.dialogs.instance._util import parse_resref_field

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class WaypointDialog(QDialog):
    def __init__(self, parent: QWidget | None, instance: GITWaypoint, installation: HTInstallation):
        super().__init__(parent)
        self._instance: GITWaypoint = instance
        self._installation: HTInstallation = installation

        from toolset.uic.qtpy.dialogs.instance.waypoint import Ui_Dialog

        self.ui: Ui_Dialog = Ui_Dialog()
        self.ui.setupUi(self)
        self._load_from_instance()

    def _load_from_instance(self) -> None:
        self.ui.resrefEdit.setText(str(self._instance.resref))
        self.ui.xPosSpin.setValue(self._instance.position.x)
        self.ui.yPosSpin.setValue(self._instance.position.y)
        self.ui.zPosSpin.setValue(self._instance.position.z)
        self.ui.bearingSpin.setValue(self._instance.bearing)
        self.ui.tagEdit.setText(self._instance.tag)
        self.ui.nameStrRefSpin.setValue(self._instance.name.stringref)
        if self._instance.map_note is None:
            self.ui.mapNoteStrRefSpin.setValue(-1)
        else:
            self.ui.mapNoteStrRefSpin.setValue(self._instance.map_note.stringref)
        self.ui.mapNoteEnabledCheck.setChecked(self._instance.map_note_enabled)
        self.ui.hasMapNoteCheck.setChecked(self._instance.has_map_note)

    def accept(self) -> None:
        resref, err = parse_resref_field(self.ui.resrefEdit.text())
        if err:
            QMessageBox.critical(self, tr("Invalid resref"), err)
            return
        assert resref is not None
        self._instance.resref = resref
        self._instance.position.x = self.ui.xPosSpin.value()
        self._instance.position.y = self.ui.yPosSpin.value()
        self._instance.position.z = self.ui.zPosSpin.value()
        self._instance.bearing = self.ui.bearingSpin.value()
        self._instance.tag = self.ui.tagEdit.text().strip()
        self._instance.name.stringref = self.ui.nameStrRefSpin.value()
        note_sr = self.ui.mapNoteStrRefSpin.value()
        if note_sr < 0:
            self._instance.map_note = None
        elif self._instance.map_note is None:
            self._instance.map_note = LocalizedString(note_sr)
        else:
            self._instance.map_note.stringref = note_sr
        self._instance.map_note_enabled = self.ui.mapNoteEnabledCheck.isChecked()
        self._instance.has_map_note = self.ui.hasMapNoteCheck.isChecked()
        super().accept()
