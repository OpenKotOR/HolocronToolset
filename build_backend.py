"""Build backend hooks for setuptools with wiki sanitization.

This backend proxies all setuptools PEP 517 hooks and strips the copied wiki
git metadata before any build/editable hook runs. Without proxying editable
hooks, tools like uv can miss script entry-point metadata for editable installs.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from setuptools.build_meta import build_editable as _build_editable
from setuptools.build_meta import build_sdist as _build_sdist
from setuptools.build_meta import build_wheel as _build_wheel
from setuptools.build_meta import get_requires_for_build_editable as _get_requires_for_build_editable
from setuptools.build_meta import get_requires_for_build_sdist as _get_requires_for_build_sdist
from setuptools.build_meta import get_requires_for_build_wheel as _get_requires_for_build_wheel
from setuptools.build_meta import prepare_metadata_for_build_editable as _prepare_metadata_for_build_editable
from setuptools.build_meta import prepare_metadata_for_build_wheel as _prepare_metadata_for_build_wheel


def _remove_wiki_git() -> None:
    """Remove .git from src/toolset/wiki to avoid build failures (e.g. WinError 5 on Windows)."""
    wiki_git = Path(__file__).resolve().parent / "src" / "toolset" / "wiki" / ".git"
    if wiki_git.exists():
        try:
            shutil.rmtree(wiki_git)
        except OSError:
            pass


def build_wheel(wheel_directory: str, config_settings: object = None, metadata_directory: str | None = None) -> str:
    _remove_wiki_git()
    return _build_wheel(wheel_directory, config_settings, metadata_directory)


def build_sdist(sdist_directory: str, config_settings: object = None) -> str:
    _remove_wiki_git()
    return _build_sdist(sdist_directory, config_settings)


def build_editable(
    wheel_directory: str,
    config_settings: object = None,
    metadata_directory: str | None = None,
) -> str:
    _remove_wiki_git()
    return _build_editable(wheel_directory, config_settings, metadata_directory)


def get_requires_for_build_wheel(config_settings: object = None) -> list[str]:
    return _get_requires_for_build_wheel(config_settings)


def get_requires_for_build_sdist(config_settings: object = None) -> list[str]:
    return _get_requires_for_build_sdist(config_settings)


def get_requires_for_build_editable(config_settings: object = None) -> list[str]:
    return _get_requires_for_build_editable(config_settings)


def prepare_metadata_for_build_wheel(metadata_directory: str, config_settings: object = None) -> str:
    _remove_wiki_git()
    return _prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def prepare_metadata_for_build_editable(metadata_directory: str, config_settings: object = None) -> str:
    _remove_wiki_git()
    return _prepare_metadata_for_build_editable(metadata_directory, config_settings)
