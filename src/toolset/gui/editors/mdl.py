"""MDL (model) editor: load/save from installation or archive, no 3D preview."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QMessageBox

from pykotor.extract.installation import SearchLocation
from pykotor.resource.formats.erf import read_erf
from pykotor.resource.formats.mdl.mdl_auto import write_mdl
from pykotor.resource.formats.mdl.mdl_data import MDL
from pykotor.resource.formats.rim import read_rim
from pykotor.resource.type import ResourceType
from pykotor.tools.misc import is_any_erf_type_file, is_bif_file, is_rim_file
from toolset.gui.editor import Editor

if TYPE_CHECKING:
    import os

    from qtpy.QtWidgets import QWidget

    from toolset.data.installation import HTInstallation


class MDLEditor(Editor):
    def __init__(self, parent: QWidget | None, installation: HTInstallation | None = None):
        supported: list[ResourceType] = [ResourceType.MDL]
        super().__init__(parent, "Model Viewer", "none", supported, supported, installation)

        self._mdl: MDL = MDL()
        self._installation = installation

        from toolset.uic.qtpy.editors.mdl import Ui_MainWindow

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Setup event filter to prevent scroll wheel interaction with controls
        from toolset.gui.common.filters import NoScrollEventFilter

        self._no_scroll_filter = NoScrollEventFilter(self)
        self._no_scroll_filter.setup_filter(parent_widget=self)

        self._setup_menus()
        self._add_help_action()
        self._setup_signals()

        self.ui.modelRenderer.installation = installation

        self.new()

    def _setup_signals(self): ...

    def load(self, filepath: os.PathLike | str, resref: str, restype: ResourceType, data: bytes | bytearray):
        """Loads a model resource and its associated data.

        Args:
        ----
            filepath: {Path to the resource file}
            resref: {Resource reference string}
            restype: {Resource type (MDL or MDX)}
            data: {Binary data of the resource}

        Loads associated MDL/MDX data:
            - Checks file extension and loads associated data from file
            - Loads associated data from Erf, Rim or Bif files if present
            - Sets model data on renderer if both MDL and MDX found
            - Displays error if unable to find associated data.
        """
        p_filepath: Path = Path(filepath)
        super().load(p_filepath, resref, restype, data)

        try:
            from toolset.utils.mdl_io_aabb_patch_standalone import apply_force_io_mdl_walkmesh_disk_fix

            apply_force_io_mdl_walkmesh_disk_fix()
        except Exception:
            pass
        try:
            from toolset.utils.mdl_io_aabb_monkeypatch import ensure_mdl_binary_reader_walkmesh_fixed

            ensure_mdl_binary_reader_walkmesh_fixed()
        except Exception:
            pass

        mdl_data: bytes | None = None
        mdx_data: bytes | None = None

        if restype == ResourceType.MDL:
            mdl_data = data
            mdl_filepath = p_filepath.with_suffix(".mdl")
            mdx_filepath = p_filepath.with_suffix(".mdx")
            if p_filepath.suffix.lower() == ".mdl" and mdx_filepath.exists() and mdx_filepath.is_file():
                mdx_data = mdx_filepath.read_bytes()
            elif is_any_erf_type_file(p_filepath.name):
                erf = read_erf(filepath)
                mdx_data = erf.get(resref, ResourceType.MDX)
            elif is_rim_file(p_filepath.name):
                rim = read_rim(filepath)
                mdx_data = rim.get(resref, ResourceType.MDX)
            elif is_bif_file(p_filepath.name):
                mdx_data = self._installation.resource(resref, ResourceType.MDX, [SearchLocation.CHITIN]).data
        elif restype == ResourceType.MDX:
            mdx_data = data
            if p_filepath.suffix.lower() == ".mdx" and mdl_filepath.exists() and mdl_filepath.is_file():
                mdl_data = mdl_filepath.read_bytes()
            elif is_any_erf_type_file(p_filepath.name):
                erf = read_erf(filepath)
                mdl_data = erf.get(resref, ResourceType.MDL)
            elif is_rim_file(p_filepath.name):
                rim = read_rim(filepath)
                mdl_data = rim.get(resref, ResourceType.MDL)
            elif is_bif_file(p_filepath.name):
                mdl_data = self._installation.resource(resref, ResourceType.MDL, [SearchLocation.CHITIN]).data

        if mdl_data is None or mdx_data is None:
            QMessageBox(QMessageBox.Icon.Critical, f"Could not find the '{p_filepath.stem}' MDL/MDX", "").exec()
            return

        # Patch site-packages io_mdl if an older pykotor wheel is installed, then reload so
        # set_model/read_mdl use fixed MDLBinaryReader (stale imports would still crash).
        import importlib

        from toolset.utils.pykotor_mdl_aabb_hotfix import (
            ensure_mdl_aabb_hotfix,
            reload_mdl_modules_after_hotfix,
        )

        ensure_mdl_aabb_hotfix()
        reload_mdl_modules_after_hotfix()
        mdl_auto = importlib.import_module("pykotor.resource.formats.mdl.mdl_auto")

        self.ui.modelRenderer.set_model(mdl_data, mdx_data)
        try:
            self._mdl = mdl_auto.read_mdl(mdl_data, 0, 0, mdx_data, 0, 0)
        except OSError as exc:
            err = str(exc).lower()
            if "seek" not in err or ("negative" not in err and "cannot seek" not in err):
                raise
            if ensure_mdl_aabb_hotfix():
                reload_mdl_modules_after_hotfix()
                mdl_auto = importlib.import_module("pykotor.resource.formats.mdl.mdl_auto")
                importlib.reload(mdl_auto)
                self._mdl = mdl_auto.read_mdl(mdl_data, 0, 0, mdx_data, 0, 0)
            else:
                from pykotor.resource.formats.mdl.io_mdl import MDLBinaryReader

                try:
                    self._mdl = MDLBinaryReader(
                        mdl_data,
                        0,
                        0,
                        mdx_data,
                        0,
                        0,
                        skip_aabb=True,
                    ).load()
                except TypeError:
                    raise exc from None

    def _loadMDL(self, mdl: MDL):
        """Load an MDL model into the editor.

        Args:
        ----
            mdl: {MDL}: The MDL model to load
        """
        self._mdl = mdl

    def build(self) -> tuple[bytes, bytes]:
        data = bytearray()
        data_ext = bytearray()
        write_mdl(self._mdl, data, ResourceType.MDL, data_ext)
        return bytes(data), bytes(data_ext)

    def new(self):
        super().new()
        self._mdl = MDL()
        self.ui.modelRenderer.clear_model()

if __name__ == "__main__":
    import sys

    from toolset.gui.editors.standalone import launch_editor_cli

    sys.exit(launch_editor_cli("mdl"))
