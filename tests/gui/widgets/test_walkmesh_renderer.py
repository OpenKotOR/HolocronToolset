from __future__ import annotations

import pytest
from typing import TYPE_CHECKING
from qtpy.QtWidgets import QWidget

from pykotor.resource.formats.bwm import BWM
from pykotor.resource.formats.bwm.bwm_data import BWMFace
from pykotor.resource.formats.lyt import LYT, LYTRoom
from utility.common.geometry import SurfaceMaterial, Vector3

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


def _make_template_walkmesh() -> BWM:
    walkmesh = BWM()
    face1 = BWMFace(Vector3(-4.0, -1.0, 0.0), Vector3(4.0, -1.0, 0.0), Vector3(4.0, 1.0, 0.0))
    face1.material = SurfaceMaterial.GRASS
    face2 = BWMFace(Vector3(-4.0, -1.0, 0.0), Vector3(4.0, 1.0, 0.0), Vector3(-4.0, 1.0, 0.0))
    face2.material = SurfaceMaterial.GRASS
    walkmesh.faces.extend([face1, face2])
    return walkmesh


def test_generate_walkmeshes_reanchors_template(qtbot: QtBot):
    from toolset.gui.widgets.renderer.walkmesh import WalkmeshRenderer

    parent = QWidget()
    qtbot.addWidget(parent)
    renderer = WalkmeshRenderer(parent)
    qtbot.addWidget(renderer)

    layout = LYT()
    layout.rooms.append(LYTRoom(model="m_testroom", position=Vector3(12.0, 24.0, 0.0)))
    template = _make_template_walkmesh()

    renderer.generate_walkmeshes(layout, walkmesh_templates={"m_testroom": template})

    generated: BWM = renderer._walkmeshes[0]  # noqa: SLF001
    bbmin, bbmax = generated.box()
    center_x = (bbmin.x + bbmax.x) / 2.0
    center_y = (bbmin.y + bbmax.y) / 2.0

    assert center_x == pytest.approx(12.0)
    assert center_y == pytest.approx(24.0)
    assert all(face.material == SurfaceMaterial.GRASS for face in generated.faces)


def test_generate_walkmeshes_falls_back_to_default_floor(qtbot: QtBot):
    from toolset.gui.widgets.renderer.walkmesh import DEFAULT_ROOM_FLOOR_SIZE, WalkmeshRenderer

    parent = QWidget()
    qtbot.addWidget(parent)
    renderer: WalkmeshRenderer = WalkmeshRenderer(parent)
    qtbot.addWidget(renderer)

    layout = LYT()
    layout.rooms.append(LYTRoom(model="m_missing", position=Vector3(0.0, 0.0, 0.0)))

    renderer.generate_walkmeshes(layout, walkmesh_templates={})

    generated: BWM = renderer._walkmeshes[0]  # noqa: SLF001
    bbmin, bbmax = generated.box()

    assert bbmin.x == pytest.approx(-DEFAULT_ROOM_FLOOR_SIZE)
    assert bbmax.x == pytest.approx(DEFAULT_ROOM_FLOOR_SIZE)
    assert len(generated.faces) == 2
