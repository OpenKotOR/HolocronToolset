"""Prefer standalone github-app-updater; fall back to in-tree utility.updater."""

from __future__ import annotations

try:
    from github_app_updater.github import (
        Asset,
        CompleteRepoData,
        GithubRelease,
        TreeInfoData,
        download_github_file,
        download_github_release_asset,
        extract_owner_repo,
        get_api_url,
        get_forks_url,
        get_main_url,
    )
    from github_app_updater.update import AppUpdate, LibUpdate
except ImportError:  # pragma: no cover - fallback while pykotor still vendors utility.updater
    from utility.updater.github import (
        Asset,
        CompleteRepoData,
        GithubRelease,
        TreeInfoData,
        download_github_file,
        download_github_release_asset,
        extract_owner_repo,
        get_api_url,
        get_forks_url,
        get_main_url,
    )
    from utility.updater.update import AppUpdate, LibUpdate

__all__ = [
    "AppUpdate",
    "Asset",
    "CompleteRepoData",
    "GithubRelease",
    "LibUpdate",
    "TreeInfoData",
    "download_github_file",
    "download_github_release_asset",
    "extract_owner_repo",
    "get_api_url",
    "get_forks_url",
    "get_main_url",
]
