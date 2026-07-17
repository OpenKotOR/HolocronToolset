"""Toolset compatibility wrapper: ThemeSelectorDialog with Toolset tr and theme manager."""

from __future__ import annotations

from typing import TYPE_CHECKING

from toolset.gui.common.localization import translate as tr

try:
    from qtpy_theme_manager import ThemeSelectorDialog as UtilityThemeSelectorDialog
except ImportError:  # pragma: no cover - fallback while pykotor still vendors utility.theme
    from utility.gui.qt.widgets.theme import ThemeSelectorDialog as UtilityThemeSelectorDialog

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget

    from toolset.gui.common.style.theme_manager import ThemeManager


class ThemeSelectorDialog(UtilityThemeSelectorDialog):
    """Toolset theme selector: qtpy-theme-manager dialog with Toolset localization.

    Prefer importing from ``qtpy_theme_manager`` for new code.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        theme_manager: ThemeManager | None = None,
        available_themes: list[str] | None = None,
        available_styles: list[str] | None = None,
        current_theme: str | None = None,
        current_style: str | None = None,
    ):
        super().__init__(
            parent=parent,
            theme_manager=theme_manager,
            available_themes=available_themes,
            available_styles=available_styles,
            current_theme=current_theme,
            current_style=current_style,
            tr=tr,
            install_no_scroll_filter=True,
        )
