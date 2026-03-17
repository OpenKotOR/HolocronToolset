"""Installation list widget: add/edit/remove KotOR installations and default game selection."""

from __future__ import annotations

import os
import re
import uuid

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from qtpy.QtCore import (
    QModelIndex,
    QSettings,
    Signal,  # pyright: ignore[reportPrivateImportUsage]
)
from qtpy.QtGui import QIcon, QStandardItem, QStandardItemModel
from qtpy.QtWidgets import QApplication, QFileDialog, QStyle, QWidget

from loggerplus import RobustLogger, get_log_directory
from pykotor.common.misc import Game
from pykotor.tools.path import CaseAwarePath, find_kotor_paths_from_default
from toolset.data.settings import Settings

if TYPE_CHECKING:
    from qtpy.QtCore import QItemSelectionModel, QModelIndex
    from typing_extensions import (  # pyright: ignore[reportMissingModuleSource]
        Literal,
        TypedDict,
    )

    from toolset.data.installation import HTInstallation  # noqa: F401
    from toolset.data.settings import SettingsProperty

    class InstallationDetailDict(TypedDict):
        name: str
        path: str
        tsl: bool

    class InstallationsDict(TypedDict):
        installations: dict[str, InstallationDetailDict]


def is_valid_installation_path(path: str) -> bool:
    """Return True if path is a directory containing chitin.key (same as Installation/HTInstallation)."""
    raw = (path or "").strip()
    if not raw:
        return False
    try:
        p = Path(raw)
        if not p.is_dir():
            return False
        return (p / "chitin.key").is_file()
    except (OSError, RuntimeError):
        return False


class InstallationsWidget(QWidget):
    sig_settings_edited: ClassVar[Signal] = Signal()  # pyright: ignore[reportPrivateImportUsage]

    def __init__(
        self,
        parent: QWidget,
    ):
        super().__init__(parent)

        self.installations_model: QStandardItemModel = QStandardItemModel()
        self.settings: GlobalSettings = GlobalSettings()
        self._merge_found_kotor_paths_into_settings()

        from toolset.uic.qtpy.widgets.settings.installations import Ui_Form

        self.ui: Ui_Form = Ui_Form()
        self.ui.setupUi(self)
        self.setup_values()
        self.setup_signals()

    @staticmethod
    def _normalize_path_for_dedup(raw: str) -> str | None:
        """Return a comparable path string for deduplication, or None if invalid."""
        s = (raw or "").strip()
        if not s:
            return None
        try:
            return os.path.normcase(str(Path(s).resolve()))
        except (OSError, RuntimeError):
            return None

    def _merge_found_kotor_paths_into_settings(self) -> None:
        """Merge paths from find_kotor_paths_from_default() into settings.

        Deduplicates existing installations by normalized path (keeps first per path),
        then adds only paths from find_kotor_paths_from_default that are not already
        present, with unique names.
        """
        raw_installations: dict[str, dict[str, Any]] = dict(
            self.settings.settings.value("installations", {}) or {},
        )
        # Deduplicate: keep one installation per normalized path (first occurrence wins)
        seen_paths: set[str] = set()
        installations: dict[str, dict[str, Any]] = {}
        for name, inst in raw_installations.items():
            norm = self._normalize_path_for_dedup(inst.get("path") or "")
            if norm is not None and norm in seen_paths:
                continue
            if norm is not None:
                seen_paths.add(norm)
            installations[name] = inst

        existing_paths: set[str] = set(seen_paths)

        def _next_counter(g: Game, names: dict[str, Any]) -> int:
            base = "KotOR" if g.is_k1() else "TSL"
            n = 1
            if base in names:
                n = 2
            pattern = re.compile(re.escape(base) + r"\s*\((\d+)\)\Z")
            for key in names:
                m = pattern.match(key)
                if m:
                    n = max(n, int(m.group(1), 10) + 1)
            return n

        counters: dict[Game, int] = {
            Game.K1: _next_counter(Game.K1, installations),
            Game.K2: _next_counter(Game.K2, installations),
        }
        added_any = False
        for game, paths in find_kotor_paths_from_default().items():
            for path in paths:
                if not CaseAwarePath.is_dir(path):
                    continue
                norm = self._normalize_path_for_dedup(str(path))
                if norm is None or norm in existing_paths:
                    continue
                base_name: str = "KotOR" if game.is_k1() else "TSL"
                name = base_name
                while name in installations:
                    name = f"{base_name} ({counters[game]})"
                    counters[game] += 1
                installations[name] = {
                    "name": name,
                    "path": str(path),
                    "tsl": game.is_k2(),
                }
                existing_paths.add(norm)
                added_any = True

        # Persist if we removed duplicates or added new installations
        deduped = len(installations) < len(raw_installations)
        if added_any or deduped:
            self.settings.settings.setValue("installations", installations)

    def _warning_icon(self) -> QIcon | None:
        style = self.style() or (QApplication.instance() and QApplication.instance().style())
        if style is None:
            return None
        return style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)

    def _is_valid_installation_path(self, path: str) -> bool:
        return is_valid_installation_path(path)

    def _apply_installation_validation(self, item: QStandardItem) -> None:
        """Set warning icon and tooltip on item if path is missing or invalid."""
        from toolset.gui.common.localization import translate as tr

        data: dict[str, Any] = item.data() or {}
        path: str = (data.get("path") or "").strip()
        valid = self._is_valid_installation_path(path)
        icon = self._warning_icon()
        if valid:
            item.setIcon(QIcon())
            item.setToolTip("")
        elif icon is not None:
            item.setIcon(icon)
            item.setToolTip(tr("The path does not appear to be a valid KotOR installation."))

    def setup_values(self):
        self.installations_model.clear()
        for installation in self.settings.installations().values():
            item = QStandardItem(installation.name)
            item.setData({"path": installation.path, "tsl": installation.tsl})
            self._apply_installation_validation(item)
            self.installations_model.appendRow(item)

    def setup_signals(self):
        self.ui.pathList.setModel(self.installations_model)

        self.ui.addPathButton.clicked.connect(self.add_new_installation)
        self.ui.removePathButton.clicked.connect(self.remove_selected_installation)
        self.ui.pathBrowseButton.clicked.connect(self.browse_installation_path)
        self.ui.pathNameEdit.textEdited.connect(self.update_installation)
        self.ui.pathDirEdit.textEdited.connect(self.update_installation)
        self.ui.pathTslCheckbox.stateChanged.connect(self.update_installation)
        select_model: QItemSelectionModel | None = self.ui.pathList.selectionModel()
        assert select_model is not None, "select_model cannot be None in setup_signals"
        select_model.selectionChanged.connect(self.installation_selected)

    def validate_can_save(self) -> tuple[bool, str]:
        """Return (True, '') if all entries with a non-empty path are valid; else (False, message)."""
        from toolset.gui.common.localization import translate as tr

        invalid: list[str] = []
        for row in range(self.installations_model.rowCount()):
            item: QStandardItem | None = self.installations_model.item(row, 0)
            if item is None:
                continue
            data: dict[str, Any] = item.data() or {}
            path: str = (data.get("path") or "").strip()
            if path and not self._is_valid_installation_path(path):
                invalid.append(f"{item.text()!r}: {path}")

        if not invalid:
            return True, ""
        return False, tr(
            "The following installation(s) do not have a valid game path (directory must contain chitin.key). "
            "Fix or remove them before saving:\n\n",
        ) + "\n".join(invalid)

    def save(self):
        installations: dict[str, dict[str, str]] = {}

        for row in range(self.installations_model.rowCount()):
            item: QStandardItem | None = self.installations_model.item(row, 0)
            if item is None:
                continue
            item_text: str = item.text()
            installations[item_text] = item.data()
            installations[item_text]["name"] = item_text

        self.settings.settings.setValue("installations", installations)

    def add_new_installation(self):
        from toolset.gui.common.localization import translate as tr

        item: QStandardItem = QStandardItem(tr("New"))
        item.setData({"path": "", "tsl": False})
        self._apply_installation_validation(item)
        self.installations_model.appendRow(item)
        self.sig_settings_edited.emit()

    def browse_installation_path(self) -> None:
        """Open a directory dialog and set the Path field to the selected folder."""
        from toolset.gui.common.localization import translate as tr

        start_dir = self.ui.pathDirEdit.text().strip() or None
        directory = QFileDialog.getExistingDirectory(
            self,
            tr("Select KotOR/TSL Game Directory"),
            start_dir or "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )
        if directory:
            self.ui.pathDirEdit.setText(directory)
            self.update_installation()

    def remove_selected_installation(self):
        if len(self.ui.pathList.selectedIndexes()) > 0:
            index: QModelIndex = self.ui.pathList.selectedIndexes()[0]
            item: QStandardItem | None = self.installations_model.itemFromIndex(index)
            assert item is not None, (
                "Item should not be None in remove_selected_installation"
            )
            self.installations_model.removeRow(item.row())
            self.sig_settings_edited.emit()

        if len(self.ui.pathList.selectedIndexes()) == 0:
            self.ui.pathFrame.setEnabled(False)

    def update_installation(self):
        index: QModelIndex = self.ui.pathList.selectedIndexes()[0]
        item: QStandardItem | None = self.installations_model.itemFromIndex(index)
        assert item is not None, "Item should not be None in update_installation"

        data: dict[str, Any] = item.data()
        data["path"] = self.ui.pathDirEdit.text()
        data["tsl"] = self.ui.pathTslCheckbox.isChecked()
        item.setData(data)

        item.setText(self.ui.pathNameEdit.text())
        self._apply_installation_validation(item)

        self.sig_settings_edited.emit()

    def installation_selected(self):
        if len(self.ui.pathList.selectedIndexes()) > 0:
            self.ui.pathFrame.setEnabled(True)

        index: QModelIndex = self.ui.pathList.selectedIndexes()[0]
        item: QStandardItem | None = self.installations_model.itemFromIndex(index)
        assert item is not None, "Item should not be None in installation_selected"
        item_text: str = item.text()
        item_data: dict[str, Any] = item.data()

        self.ui.pathNameEdit.setText(item_text)
        self.ui.pathDirEdit.setText(item_data["path"])
        self.ui.pathTslCheckbox.setChecked(bool(item_data["tsl"]))


class InstallationConfig:
    def __init__(
        self,
        name: str,
    ):
        from toolset.utils.misc import get_qsettings_organization

        self._settings: QSettings = QSettings(
            get_qsettings_organization("HolocronToolsetV4"), "Global",
        )
        self._name: str = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(
        self,
        value: str,
    ):
        installations: dict[str, dict[str, Any]] = self._settings.value(
            "installations", {}, dict,
        )
        installation: dict[str, Any] = installations[self._name]

        del installations[self._name]
        installations[value] = installation
        installations[value]["name"] = value

        self._settings.setValue("installations", installations)
        self._name = value

    @property
    def path(self) -> str:
        try:
            installation: dict[str, Any] = self._settings.value("installations", {})[
                self._name
            ]
        except Exception:  # noqa: BLE001
            return ""
        else:
            return installation.get("path", "")

    @path.setter
    def path(
        self,
        value: str,
    ):
        try:
            installations: dict[str, dict[str, str]] = self._settings.value(
                "installations", {},
            )
            installations[self._name] = installations.get(self._name, {})
            installations[self._name]["path"] = value
            self._settings.setValue("installations", installations)
        except Exception:
            log = RobustLogger()
            log.exception("InstallationConfig.path property raised an exception.")

    @property
    def tsl(self) -> bool:
        all_installs: dict[str, dict[str, Any]] = self._settings.value(
            "installations", {},
        )
        installation: dict[str, Any] = all_installs.get(self._name, {})
        return installation.get("tsl", False)

    @tsl.setter
    def tsl(
        self,
        value: bool,
    ):
        installations: dict[str, dict[str, Any]] = self._settings.value(
            "installations", {},
        )
        installations[self._name] = installations.get(self._name, {})
        installations[self._name]["tsl"] = value
        self._settings.setValue("installations", installations)


class GlobalSettings(Settings):
    def __init__(self):
        super().__init__("Global")

    def installations(self) -> dict[str, InstallationConfig]:
        """Retrieve the current installations from settings as a dict of InstallationConfig."""
        installations: dict[str, dict[str, Any]] = self.settings.value("installations")
        if installations is None:
            installations = {}

        if self.firstTime:
            self.firstTime = False
            self._handle_firsttime_user(installations)
        self.settings.setValue("installations", installations)

        return {name: InstallationConfig(name) for name in installations}

    def set_installations(
        self,
        installations: dict[str, InstallationConfig | dict[str, Any]],
    ) -> None:
        """Sets the collection of installations in the settings.

        Args:
            installations: A mapping from installation name to InstallationConfig or dict with compatible fields.
        """
        # Convert InstallationConfig objects to dict if provided as such
        installations_data: dict[str, dict[str, Any]] = {}
        for name, config in installations.items():
            if isinstance(config, InstallationConfig):
                # Convert InstallationConfig to dict representation via settings persistence
                installations_data[name] = {
                    "name": config.name,
                    "path": config.path,
                    "tsl": config.tsl,
                }
            elif isinstance(config, dict):
                installations_data[name] = dict(config)
            else:
                raise ValueError(
                    f"Invalid type for installation config value: {type(config)}",
                )
        self.settings.setValue("installations", installations_data)

    def _handle_firsttime_user(
        self,
        installations: dict[str, dict[str, Any]],
    ):
        """Finds KotOR installation paths on the system, checks for duplicates, and records the paths and metadata in the user settings.

        Paths are filtered to only existing ones. Duplicates are detected by path and the game name is incremented with a number.
        Each new installation is added to the installations dictionary with its name, path, and game (KotOR 1 or 2) specified.
        The installations dictionary is then saved back to the user settings.
        """
        self.firstTime = False
        RobustLogger().info(
            "First time user, attempt auto-detection of currently installed KOTOR paths.",
        )
        self.extractPath = str(get_log_directory(f"{uuid.uuid4().hex[:7]}_extract"))
        counters: dict[Game, int] = {Game.K1: 1, Game.K2: 1}
        # Create a set of existing paths
        existing_paths: set[Path] = {
            Path(inst["path"]) for inst in installations.values()
        }

        for game, paths in find_kotor_paths_from_default().items():
            for path in filter(CaseAwarePath.is_dir, paths):
                RobustLogger().info(f"Autodetected game {game!r} path {path}")
                if path in existing_paths:
                    continue
                game_name: Literal["KotOR", "TSL"] = "KotOR" if game.is_k1() else "TSL"
                base_game_name: Literal["KotOR", "TSL"] = game_name
                while game_name in installations:
                    counters[game] += 1
                    game_name = f"{base_game_name} ({counters[game]})"  # type: ignore[assignment]
                installations[game_name] = {
                    "name": game_name,
                    "path": str(path),
                    "tsl": game.is_k2(),
                }
                existing_paths.add(path)

    # region Strings
    recentFiles: SettingsProperty[list[str]] = Settings.addSetting(
        "recentFiles",
        [],
    )
    extractPath: SettingsProperty[str] = Settings.addSetting(
        "extractPath",
        "",
    )
    nssCompilerPath: SettingsProperty[str] = Settings.addSetting(
        "nssCompilerPath",
        "ext/nwnnsscomp.exe" if os.name == "nt" else "ext/nwnnsscomp",
    )
    ncsDecompilerPath: SettingsProperty[str] = Settings.addSetting(
        "ncsDecompilerPath",
        "",
    )
    selectedTheme: SettingsProperty[str] = Settings.addSetting(
        "selectedTheme",
        "sourcegraph-dark",  # Default theme
    )
    selectedStyle: SettingsProperty[str] = Settings.addSetting(
        "selectedStyle",
        "Fusion",  # Default style
    )
    selectedLanguage: SettingsProperty[int] = Settings.addSetting(
        "selectedLanguage",
        0,  # Default to English (ToolsetLanguage.ENGLISH)
    )
    # endregion

    # region Numbers
    moduleSortOption: SettingsProperty[int] = Settings.addSetting(
        "moduleSortOption",
        2,
    )
    # endregion

    # region Bools
    loadEntireInstallation: SettingsProperty[bool] = Settings.addSetting(
        "load_entire_installation",
        False,
    )
    disableRIMSaving: SettingsProperty[bool] = Settings.addSetting(
        "disableRIMSaving",
        True,
    )
    useLegacyLayout: SettingsProperty[bool] = Settings.addSetting(
        "useLegacyLayout",
        False,
    )
    attemptKeepOldGFFFields: SettingsProperty[bool] = Settings.addSetting(
        "attemptKeepOldGFFFields",
        False,
    )
    useBetaChannel: SettingsProperty[bool] = Settings.addSetting(
        "useBetaChannel",
        True,
    )
    firstTime: SettingsProperty[bool] = Settings.addSetting(
        "firstTime",
        True,
    )
    maxChildProcesses: SettingsProperty[int] = Settings.addSetting(
        "maxChildProcesses",
        1,
    )
    gffSpecializedEditors: SettingsProperty[bool] = Settings.addSetting(
        "gffSpecializedEditors",
        True,
    )
    joinRIMsTogether: SettingsProperty[bool] = Settings.addSetting(
        "joinRIMsTogether",
        True,
    )
    useModuleFilenames: SettingsProperty[bool] = Settings.addSetting(
        "useModuleFilenames",
        False,
    )
    greyRIMText: SettingsProperty[bool] = Settings.addSetting(
        "greyRIMText",
        True,
    )
    showPreviewUTC: SettingsProperty[bool] = Settings.addSetting(
        "showPreviewUTC",
        True,
    )
    showPreviewUTP: SettingsProperty[bool] = Settings.addSetting(
        "showPreviewUTP",
        True,
    )
    showPreviewUTD: SettingsProperty[bool] = Settings.addSetting(
        "showPreviewUTD",
        True,
    )
    showPreviewUTI: SettingsProperty[bool] = Settings.addSetting(
        "showPreviewUTI",
        True,
    )
    # endregion


class NoConfigurationSetError(Exception): ...
