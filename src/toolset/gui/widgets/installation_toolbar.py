"""Reusable standalone installation/folder-path toolbar for editor windows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, ClassVar

from qtpy.QtCore import Signal  # pyright: ignore[reportPrivateImportUsage]
from qtpy.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from loggerplus import RobustLogger
from toolset.data.installation import HTInstallation
from toolset.gui.dialogs.asyncloader import AsyncLoader
from toolset.gui.widgets.settings.installations import (
    GlobalSettings,
    InstallationsWidget,
    is_valid_installation_path,
)
from toolset.uic.qtpy.widgets.installation_toolbar import Ui_Form


# Path row widgets from installation_toolbar.ui (pathLabel0-3, pathEdit0-3, pathBrowse0-3)
def _path_row_widgets(ui):
    return [
        (ui.pathLabel0, ui.pathEdit0, ui.pathBrowse0),
        (ui.pathLabel1, ui.pathEdit1, ui.pathBrowse1),
        (ui.pathLabel2, ui.pathEdit2, ui.pathBrowse2),
        (ui.pathLabel3, ui.pathEdit3, ui.pathBrowse3),
    ]


@dataclass(frozen=True)
class FolderPathSpec:
    key: str
    label: str
    tooltip: str
    required: bool = False


def open_manage_installations_dialog(
    parent: QWidget,
    *,
    on_save: Callable[[], None] | None = None,
) -> None:
    """Open the shared Manage Installations dialog. Call on_save after user accepts."""
    from toolset.uic.qtpy.dialogs.manage_installations import Ui_Dialog

    dialog = QDialog(parent)
    dialog.setWindowTitle("Manage Installations")
    ui = Ui_Dialog()
    ui.setupUi(dialog)
    widget = InstallationsWidget(ui.installationsWidgetPlaceholder)
    layout = QVBoxLayout(ui.installationsWidgetPlaceholder)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(widget)

    def on_accept() -> None:
        valid, msg = widget.validate_can_save()
        if not valid:
            QMessageBox.warning(dialog, "Invalid installation(s)", msg)
            return
        dialog.accept()

    try:
        ui.buttonBox.accepted.disconnect(dialog.accept)
    except (TypeError, RuntimeError):
        pass
    ui.buttonBox.accepted.connect(on_accept)
    ui.buttonBox.rejected.connect(dialog.reject)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        widget.save()
        if on_save is not None:
            on_save()


class InstallationToolbar(QWidget):
    """Reusable installation/folder-path strip; layout from installation_toolbar.ui."""

    installation_changed = Signal(object)  # HTInstallation | None
    folder_paths_changed = Signal(object)  # dict[str, Path | None]

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        folder_path_specs: list[FolderPathSpec] | None = None,
        requires_installation: bool = False,
    ):
        super().__init__(parent)
        self._log = RobustLogger()
        self._specs: list[FolderPathSpec] = folder_path_specs or []
        self._requires_installation: bool = requires_installation
        self._settings = GlobalSettings()
        self._installation_cache: dict[str, HTInstallation] = {}
        self._override_installation: HTInstallation | None = None
        self._saved_installations: dict[str, dict[str, str | bool]] = {}
        self._in_update = False
        # Map spec key -> row index (0.._MAX_PATH_ROWS-1) for UI path rows from .ui
        self._path_row_index: dict[str, int] = {}

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        if not self._specs:
            self.ui.modeFullRadio.setChecked(True)
            self.ui.modeFolderRadio.hide()
            self.ui.modeFullRadio.hide()
            self.ui.pathsWidget.hide()
        elif self._requires_installation:
            self.ui.modeFullRadio.setChecked(True)
            self.ui.modeFolderRadio.setEnabled(False)
            self.ui.modeFolderRadio.setToolTip("This window requires a full installation.")
            self.ui.pathsWidget.hide()
        else:
            self.ui.modeFullRadio.setChecked(True)
            self.ui.pathsWidget.hide()

        # Configure path rows from .ui (pathLabel0-3, pathEdit0-3, pathBrowse0-3)
        path_rows = _path_row_widgets(self.ui)
        for i, (label, edit, browse) in enumerate(path_rows):
            if i < len(self._specs):
                spec = self._specs[i]
                self._path_row_index[spec.key] = i
                label.setText(f"{spec.label}:")
                edit.setPlaceholderText("Optional folder path..." if not spec.required else "Required folder path...")
                edit.setToolTip(spec.tooltip)
                edit.textChanged.connect(self._emit_current_state)
                browse.clicked.connect(lambda _=False, key=spec.key: self._browse_for_path(key))
                label.show()
                edit.show()
                browse.show()
            else:
                label.hide()
                edit.hide()
                browse.hide()

        self.ui.modeFullRadio.toggled.connect(self._on_mode_toggled)
        self.ui.modeFolderRadio.toggled.connect(self._on_mode_toggled)
        self.ui.installationCombo.currentIndexChanged.connect(self._on_installation_selection_changed)
        self.ui.reloadBtn.clicked.connect(self.reload_installations)
        self.ui.manageBtn.clicked.connect(self._open_installations_settings)

        self.reload_installations()
        self._emit_current_state()

    @property
    def installation_combo(self):
        """Backward-compatible alias for installationCombo (e.g. indoor_builder sync)."""
        return self.ui.installationCombo

    @property
    def installationCombo(self):
        """Expose for code that expects InstallationToolbar.installationCombo."""
        return self.ui.installationCombo

    def set_override_installation(self, installation: HTInstallation | None) -> None:
        """Set an installation passed from CLI (e.g. --game-path). Shows in combo and emits so the window uses it."""
        self._override_installation = installation
        self.reload_installations()
        if installation is not None:
            self._installation_cache["__override__"] = installation
        # reload_installations() already called _emit_current_state(), which emits the selected installation

    def reload_installations(self) -> None:
        current_key = self.ui.installationCombo.currentData()
        self._saved_installations = {name: {"path": config.path, "tsl": config.tsl, "name": name} for name, config in self._settings.installations().items()}
        self._in_update = True
        try:
            self.ui.installationCombo.clear()
            if self._override_installation is not None:
                path_str = str(self._override_installation.path())
                self.ui.installationCombo.addItem(f"Current: {path_str}", "__override__")
                self._installation_cache["__override__"] = self._override_installation
            self.ui.installationCombo.addItem("(None)", None)
            for name, config in sorted(self._saved_installations.items()):
                path_str = (config.get("path") or "").strip()
                if not path_str or not is_valid_installation_path(path_str):
                    continue
                self.ui.installationCombo.addItem(f"{name} ({config['path']})", name)
            if current_key is not None:
                idx = self.ui.installationCombo.findData(current_key)
                if idx >= 0:
                    self.ui.installationCombo.setCurrentIndex(idx)
            elif self._override_installation is not None:
                self.ui.installationCombo.setCurrentIndex(0)
        finally:
            self._in_update = False
        self._emit_current_state()

    def _browse_for_path(self, key: str) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not directory or key not in self._path_row_index:
            return
        idx = self._path_row_index[key]
        _path_row_widgets(self.ui)[idx][1].setText(directory)

    def _open_installations_settings(self) -> None:
        open_manage_installations_dialog(self, on_save=self.reload_installations)

    def _on_mode_toggled(self, _checked: bool) -> None:
        use_paths = self.ui.modeFolderRadio.isChecked() and bool(self._specs) and not self._requires_installation
        self.ui.pathsWidget.setVisible(use_paths)
        self._emit_current_state()

    def _on_installation_selection_changed(self, _index: int) -> None:
        if self._in_update:
            return
        use_paths = self.ui.modeFolderRadio.isChecked() and bool(self._specs) and not self._requires_installation
        if use_paths:
            self._emit_current_state()
            return
        selected_name = self.ui.installationCombo.currentData()
        if selected_name == "__override__":
            self.installation_changed.emit(self._installation_cache.get("__override__"))
            return
        if selected_name is None:
            self.installation_changed.emit(None)
            return
        cache_key = str(selected_name)
        if cache_key in self._installation_cache:
            self.installation_changed.emit(self._installation_cache[cache_key])
            return
        config = self._saved_installations.get(cache_key)
        if config is None:
            self.installation_changed.emit(None)
            return
        # Cache miss: load installation in background and show AsyncLoader
        parent_window = self.window()
        if parent_window is None:
            parent_window = self

        def task() -> HTInstallation | None:
            try:
                inst = HTInstallation(
                    str(config["path"]),
                    str(config["name"]),
                    tsl=bool(config.get("tsl")),
                )
                return inst
            except Exception as exc:  # noqa: BLE001
                self._log.exception("Failed to create installation '%s': %s", cache_key, exc)
                raise

        loader = AsyncLoader(
            parent_window,
            "Loading installation...",
            task,
            error_title="Invalid Installation",
            start_immediately=True,
            initial_message="Loading installation... Please wait.",
        )

        def on_finish(inst: HTInstallation | None) -> None:
            if inst is not None:
                self._installation_cache[cache_key] = inst
            self.installation_changed.emit(inst)

        loader.optional_finish_hook.connect(on_finish)
        prev_index = self.ui.installationCombo.currentIndex()
        loader.exec()
        if loader.dialog_result_code() != QDialog.DialogCode.Accepted:
            self._in_update = True
            try:
                self.ui.installationCombo.setCurrentIndex(prev_index)
            finally:
                self._in_update = False
            self.installation_changed.emit(self._get_selected_installation())

    def _get_selected_installation(self) -> HTInstallation | None:
        selected_name = self.ui.installationCombo.currentData()
        if selected_name is None:
            return None
        if selected_name == "__override__":
            return self._installation_cache.get("__override__")

        cache_key = str(selected_name)
        if cache_key in self._installation_cache:
            return self._installation_cache[cache_key]

        config = self._saved_installations.get(cache_key)
        if config is None:
            return None
        try:
            installation = HTInstallation(
                str(config["path"]),
                str(config["name"]),
                tsl=bool(config.get("tsl")),
            )
            self._installation_cache[cache_key] = installation
            return installation
        except Exception as exc:  # noqa: BLE001
            self._log.exception("Failed to create installation '%s': %s", cache_key, exc)
            QMessageBox.warning(self, "Invalid Installation", f"Could not load installation '{cache_key}'.")
            return None

    def get_folder_paths(self) -> dict[str, Path | None]:
        result: dict[str, Path | None] = {}
        path_rows = _path_row_widgets(self.ui)
        for spec in self._specs:
            idx = self._path_row_index.get(spec.key)
            if idx is not None:
                edit = path_rows[idx][1]
                raw = edit.text().strip()
                result[spec.key] = Path(raw) if raw else None
            else:
                result[spec.key] = None
        return result

    def _emit_current_state(self) -> None:
        use_paths = self.ui.modeFolderRadio.isChecked() and bool(self._specs) and not self._requires_installation
        selected_installation = None if use_paths else self._get_selected_installation()
        self.installation_changed.emit(selected_installation)
        if use_paths:
            self.folder_paths_changed.emit(self.get_folder_paths())


class StandaloneWindowMixin:
    STANDALONE_FOLDER_PATHS: ClassVar[list[FolderPathSpec]] = []
    STANDALONE_REQUIRES_INSTALLATION: ClassVar[bool] = False

    _installation_toolbar: InstallationToolbar | None = None
    _standalone_folder_paths: dict[str, Path | None]

    def enable_standalone_mode(self) -> None:
        if self._installation_toolbar is not None:
            return
        if not hasattr(self, "centralWidget"):
            return
        main_window = self
        if not isinstance(main_window, QWidget):  # runtime safety for pyright/mixin
            return
        central = main_window.centralWidget()
        if central is None:
            return

        self._standalone_folder_paths = {}
        self._installation_toolbar = InstallationToolbar(
            main_window,
            folder_path_specs=list(self.STANDALONE_FOLDER_PATHS),
            requires_installation=self.STANDALONE_REQUIRES_INSTALLATION,
        )
        self._installation_toolbar.installation_changed.connect(self._handle_installation_changed)
        self._installation_toolbar.folder_paths_changed.connect(self._handle_folder_paths_changed)

        container = QWidget(main_window)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._installation_toolbar)
        layout.addWidget(central, 1)
        main_window.setCentralWidget(container)

    def set_installation(self, installation: HTInstallation | None) -> None:
        self._installation = installation
        self._on_installation_changed(installation)

    def _handle_installation_changed(self, installation: HTInstallation | None) -> None:
        self._installation = installation
        self._on_installation_changed(installation)

    def _handle_folder_paths_changed(self, paths: dict[str, Path | None]) -> None:
        self._standalone_folder_paths = paths
        self._on_folder_paths_changed(paths)

    def _on_installation_changed(self, installation: HTInstallation | None) -> None:  # noqa: ARG002
        """Override in subclasses that need runtime installation switching."""

    def _on_folder_paths_changed(self, paths: dict[str, Path | None]) -> None:  # noqa: ARG002
        """Override in subclasses that support folder-path mode."""
