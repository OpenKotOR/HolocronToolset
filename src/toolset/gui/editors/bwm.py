"""BWM (walkmesh) editor: face list, materials, and 2D camera for module designer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QListWidgetItem

from pykotor.resource.formats.bwm import (  # pyright: ignore[reportMissingImports]
    read_bwm,
    write_bwm,
)
from pykotor.resource.type import ResourceType  # pyright: ignore[reportMissingImports]
from toolset.gui.common.viewport_2d_nav import Viewport2DNavigationHelper, aabb_from_points
from toolset.gui.common.interaction.camera import (
    handle_standard_2d_camera_movement,
)
from toolset.gui.common.walkmesh_materials import (
    get_walkmesh_material_colors,
    populate_material_list_widget,
)
from toolset.gui.editor import Editor
from toolset.gui.widgets.settings.widgets.module_designer import ModuleDesignerSettings

if TYPE_CHECKING:
    import os

    from qtpy.QtGui import QColor
    from qtpy.QtWidgets import QWidget

    from pykotor.resource.formats.bwm import BWM, BWMFace  # pyright: ignore[reportMissingImports]
    from toolset.data.installation import HTInstallation
    from utility.common.geometry import SurfaceMaterial, Vector2, Vector3

_TRANS_FACE_ROLE = Qt.ItemDataRole.UserRole + 1  # type: ignore[attr-defined]
_TRANS_EDGE_ROLE = Qt.ItemDataRole.UserRole + 2  # type: ignore[attr-defined]


class BWMEditor(Editor):
    def __init__(self, parent: QWidget | None, installation: HTInstallation | None = None):
        """Initializes the walkmesh painter window.

        Args:
        ----
            parent: QWidget | None: The parent widget
            installation: HTInstallation | None: The installation

        Processing Logic:
        ----------------
        Initializes UI components and connects signals:
            - Sets up UI from designer file
            - Sets up menus
            - Sets up signal connections
            - Initializes default material colors
            - Rebuilds material dropdown
            - Creates new empty walkmesh.
        """
        supported = [ResourceType.WOK, ResourceType.DWK, ResourceType.PWK]
        self._bwm: BWM | None = None
        super().__init__(parent, "Walkmesh Painter", "walkmesh", supported, supported, installation)

        from toolset.uic.qtpy.editors.bwm import Ui_MainWindow

        self.ui: Ui_MainWindow = Ui_MainWindow()
        self.ui.setupUi(self)

        self._setup_menus()
        self._add_help_action()
        self._setup_signals()

        self.material_colors: dict[SurfaceMaterial, QColor] = get_walkmesh_material_colors()
        self.ui.renderArea.material_colors = self.material_colors
        self.ui.renderArea.show_room_boundaries = True
        self.ui.renderArea.show_grid = False
        self._nav_helper = Viewport2DNavigationHelper(
            self.ui.renderArea,
            get_content_bounds=self._content_bounds,
            settings=ModuleDesignerSettings(),
        )
        self.rebuild_materials()

        self.new()

    def _setup_signals(self) -> None:
        self.ui.renderArea.sig_mouse_moved.connect(self.on_mouse_moved)
        self.ui.renderArea.sig_mouse_scrolled.connect(self.on_mouse_scrolled)
        self.ui.renderArea.sig_key_pressed.connect(self.on_key_pressed)
        self.ui.actionShowRoomBoundaries.toggled.connect(
            lambda value: setattr(self.ui.renderArea, "show_room_boundaries", value)
        )
        self.ui.actionShowRoomBoundaries.toggled.connect(lambda _: self.ui.renderArea.update())
        self.ui.actionShowGrid.toggled.connect(
            lambda value: setattr(self.ui.renderArea, "show_grid", value)
        )
        self.ui.actionShowGrid.toggled.connect(lambda _: self.ui.renderArea.update())

    def _content_bounds(self):
        if self._bwm is None:
            return None
        return aabb_from_points(
            (vertex.x, vertex.y)
            for face in self._bwm.faces
            for vertex in (face.v1, face.v2, face.v3)
        )

    def frame_all(self) -> None:
        if not self._nav_helper.frame_all():
            self.ui.renderArea.center_camera()

    def rebuild_materials(self):
        """Rebuild the material list.

        Processing Logic:
        ----------------
            - Clear existing items from the material list
            - Loop through all material colors
            - Create image from color and set as icon
            - Format material name as title
            - Create list item with icon and text
            - Add item to material list.
        """
        populate_material_list_widget(self.ui.materialList, self.material_colors)

    def load(
        self,
        filepath: os.PathLike | str,
        resref: str,
        restype: ResourceType,
        data: bytes,
    ):
        """Loads a resource into the editor.

        Args:
        ----
            filepath: The path to the resource file
            resref: The resource reference
            restype: The resource type
            data: The raw resource data

        Processing Logic:
        ----------------
            - Reads the bwm data from the resource data
            - Sets the loaded bwm on the render area
            - Clears any existing transition items
            - Loops through faces and adds a transition item for each transition
        """
        super().load(filepath, resref, restype, data)

        self._bwm = read_bwm(data)
        self.ui.renderArea.set_walkmeshes([self._bwm])

        def add_trans_item(face: BWMFace, edge: int, transition: int | None):
            if transition is not None:
                item = QListWidgetItem(f"Transition to: {transition}")
                item.setData(_TRANS_FACE_ROLE, face)
                item.setData(_TRANS_EDGE_ROLE, edge)
                self.ui.transList.addItem(item)

        self.ui.transList.clear()
        for face in self._bwm.faces:
            add_trans_item(face, 1, face.trans1)
            add_trans_item(face, 2, face.trans2)
            add_trans_item(face, 3, face.trans3)

    def build(self) -> tuple[bytes, bytes]:
        assert self._bwm is not None
        data = bytearray()
        write_bwm(self._bwm, data)
        return bytes(data), b""

    def on_mouse_moved(self, screen: Vector2, delta: Vector2, buttons: set[int], keys: set[int]):
        """Handles mouse movement events in the viewer.

        Args:
        ----
            screen: Vector2 - Current mouse screen position
            delta: Vector2 - Mouse movement since last event
            buttons: set[int] - Currently pressed mouse buttons
            keys: set[int] - Currently pressed keyboard keys

        Processing Logic:
        ----------------
            - Converts mouse position to world and render coordinates
            - Pans/rotates camera if Ctrl + mouse buttons pressed
            - Changes face material if left button pressed
            - Displays coordinates, face index in status bar.
        """
        world: Vector3 = self.ui.renderArea.to_world_coords(screen.x, screen.y)
        world_data: Vector2 = self.ui.renderArea.to_world_delta(delta.x, delta.y)
        assert self._bwm is not None
        face: BWMFace | None = self._bwm.faceAt(world.x, world.y)

        handled_cam = handle_standard_2d_camera_movement(
            self.ui.renderArea,
            screen,
            delta,
            world_data,
            buttons,
            keys,
            settings=ModuleDesignerSettings(),
        )

        # Paint with left-drag unless camera movement consumed the input.
        if not handled_cam and Qt.MouseButton.LeftButton in buttons and face is not None:  # type: ignore[attr-defined]
            self.change_face_material(face)

        coords_text = f"x: {world.x:.2f}, {world.y:.2f}"
        face_text = f", face: {'None' if face is None else self._bwm.faces.index(face)}"

        screen = self.ui.renderArea.to_render_coords(world.x, world.y)
        xy = f" || x: {screen.x:.2f}, " + f"y: {screen.y:.2f}, "

        status_bar = self.statusBar()  # pyright: ignore[reportGeneralTypeIssues, attr-defined]
        if status_bar is None:
            return
        status_bar.showMessage(coords_text + face_text + xy)  # pyright: ignore[reportCallIssue]

    def on_mouse_scrolled(self, delta: Vector2, buttons: set[int], keys: set[int]):
        if self._nav_helper.handle_mouse_scroll(
            delta, buttons, keys, zoom_sensitivity=ModuleDesignerSettings().zoomCameraSensitivity2d
        ):
            self.ui.renderArea.update()
            return

    def on_key_pressed(self, buttons: set[int], keys: set[int]):
        self._nav_helper.handle_key_pressed(
            keys, buttons=buttons, pan_step=ModuleDesignerSettings().moveCameraSensitivity2d / 10
        )

    def change_face_material(self, face: BWMFace):
        """Change material of a face.

        Args:
        ----
            face (BWMFace): The face object to change material

        Processing Logic:
        ----------------
            - Check if a face is provided. Perhaps this can be called from an ambiguous/generalized function/event somewhere.
            - Check if the current face material is different than the selected material
            - Assign the selected material to the provided face.
        """
        current: QListWidgetItem | None = self.ui.materialList.currentItem()
        if current is None:
            return
        new_material = current.data(Qt.ItemDataRole.UserRole)  # type: ignore[union-attr]  # pyright: ignore[reportOptionalMemberAccess]
        if face.material == new_material:
            return
        face.material = new_material

    def onTransitionSelect(self):
        if self.ui.transList.currentItem():
            item: QListWidgetItem | None = self.ui.transList.currentItem()  # type: ignore[union-attr]  # pyright: ignore[reportOptionalMemberAccess]
            if item is None:
                return
            face: BWMFace | None = item.data(_TRANS_FACE_ROLE)
            edge: int | None = item.data(_TRANS_EDGE_ROLE)
            self.ui.renderArea.setHighlightedTrans(face, edge)
        else:
            self.ui.renderArea.setHighlightedTrans(None, None)


if __name__ == "__main__":
    import sys

    from toolset.gui.editors.standalone import launch_editor_cli

    sys.exit(launch_editor_cli("bwm"))
