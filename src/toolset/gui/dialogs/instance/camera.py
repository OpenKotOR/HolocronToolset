"""GIT camera instance editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtWidgets import QDialog

from pykotor.resource.generics.git import GITCamera
from utility.common.geometry import Vector4

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class CameraDialog(QDialog):
    def __init__(self, parent: QWidget | None, instance: GITCamera):
        super().__init__(parent)
        self._instance: GITCamera = instance

        from toolset.uic.qtpy.dialogs.instance.camera import Ui_Dialog

        self.ui: Ui_Dialog = Ui_Dialog()
        self.ui.setupUi(self)
        self._load_from_instance()

    def _load_from_instance(self) -> None:
        self.ui.xPosSpin.setValue(self._instance.position.x)
        self.ui.yPosSpin.setValue(self._instance.position.y)
        self.ui.zPosSpin.setValue(self._instance.position.z)
        self.ui.cameraIdSpin.setValue(int(self._instance.camera_id))
        self.ui.fovSpin.setValue(self._instance.fov)
        self.ui.heightSpin.setValue(self._instance.height)
        self.ui.micRangeSpin.setValue(self._instance.mic_range)
        self.ui.pitchSpin.setValue(self._instance.pitch)
        self.ui.oriXSpin.setValue(self._instance.orientation.x)
        self.ui.oriYSpin.setValue(self._instance.orientation.y)
        self.ui.oriZSpin.setValue(self._instance.orientation.z)
        self.ui.oriWSpin.setValue(self._instance.orientation.w)

    def accept(self) -> None:
        self._instance.position.x = self.ui.xPosSpin.value()
        self._instance.position.y = self.ui.yPosSpin.value()
        self._instance.position.z = self.ui.zPosSpin.value()
        self._instance.camera_id = int(self.ui.cameraIdSpin.value())
        self._instance.fov = self.ui.fovSpin.value()
        self._instance.height = self.ui.heightSpin.value()
        self._instance.mic_range = self.ui.micRangeSpin.value()
        self._instance.pitch = self.ui.pitchSpin.value()
        self._instance.orientation = Vector4(
            self.ui.oriXSpin.value(),
            self.ui.oriYSpin.value(),
            self.ui.oriZSpin.value(),
            self.ui.oriWSpin.value(),
        )
        super().accept()
