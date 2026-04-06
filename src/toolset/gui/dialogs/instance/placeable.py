"""GIT placeable instance editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtWidgets import QDialog, QMessageBox

from pykotor.common.misc import Color
from pykotor.resource.generics.git import GITPlaceable
from toolset.gui.common.localization import translate as tr
from toolset.gui.dialogs.instance._util import parse_resref_field
from toolset.gui.helpers.callback import BetterMessageBox

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class PlaceableDialog(QDialog):
    def __init__(self, parent: QWidget | None, instance: GITPlaceable):
        super().__init__(parent)
        self._instance: GITPlaceable = instance

        from toolset.uic.qtpy.dialogs.instance.placeable import Ui_Dialog

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.useTweakColorCheck.toggled.connect(self.ui.tweakBgrSpin.setEnabled)
        self._load_from_instance()

    def _load_from_instance(self) -> None:
        self.ui.resrefEdit.setText(str(self._instance.resref))
        self.ui.xPosSpin.setValue(self._instance.position.x)
        self.ui.yPosSpin.setValue(self._instance.position.y)
        self.ui.zPosSpin.setValue(self._instance.position.z)
        self.ui.bearingSpin.setValue(self._instance.bearing)
        self.ui.tagEdit.setText(self._instance.tag)
        use_color: bool = self._instance.tweak_color is not None
        self.ui.useTweakColorCheck.setChecked(use_color)
        self.ui.tweakBgrSpin.setEnabled(use_color)
        if self._instance.tweak_color is not None:
            self.ui.tweakBgrSpin.setValue(self._instance.tweak_color.bgr_integer())
        else:
            self.ui.tweakBgrSpin.setValue(0)

    def accept(self) -> None:
        resref, err = parse_resref_field(self.ui.resrefEdit.text())
        if err:
            BetterMessageBox(tr("Invalid resref"), err, icon=QMessageBox.Icon.Critical).exec()
            return
        assert resref is not None
        self._instance.resref = resref
        self._instance.position.x = self.ui.xPosSpin.value()
        self._instance.position.y = self.ui.yPosSpin.value()
        self._instance.position.z = self.ui.zPosSpin.value()
        self._instance.bearing = self.ui.bearingSpin.value()
        self._instance.tag = self.ui.tagEdit.text().strip()
        if self.ui.useTweakColorCheck.isChecked():
            self._instance.tweak_color = Color.from_bgr_integer(self.ui.tweakBgrSpin.value())
        else:
            self._instance.tweak_color = None
        super().accept()
