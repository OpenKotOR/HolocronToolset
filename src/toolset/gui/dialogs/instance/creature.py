"""GIT creature instance editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtWidgets import QDialog, QMessageBox

from pykotor.resource.generics.git import GITCreature
from toolset.gui.common.localization import translate as tr
from toolset.gui.dialogs.instance._util import parse_resref_field

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class CreatureDialog(QDialog):
    def __init__(self, parent: QWidget | None, instance: GITCreature):
        super().__init__(parent)
        self._instance: GITCreature = instance

        from toolset.uic.qtpy.dialogs.instance.creature import Ui_Dialog

        self.ui: Ui_Dialog = Ui_Dialog()
        self.ui.setupUi(self)
        self._load_from_instance()

    def _load_from_instance(self) -> None:
        self.ui.resrefEdit.setText(str(self._instance.resref))
        self.ui.xPosSpin.setValue(self._instance.position.x)
        self.ui.yPosSpin.setValue(self._instance.position.y)
        self.ui.zPosSpin.setValue(self._instance.position.z)
        self.ui.bearingSpin.setValue(self._instance.bearing)

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
        super().accept()
