#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


def _patch_mdl_io_before_path_setup() -> None:
    """Fix KOQ200 AABB seek(-1) in site-packages *before* setup_paths prepends repo PyKotor."""
    try:
        patch_py = Path(__file__).resolve().parent / "utils" / "mdl_io_aabb_patch_standalone.py"
        if not patch_py.is_file():
            return
        spec = importlib.util.spec_from_file_location("_holocron_mdl_aabb", patch_py)
        if spec is None or spec.loader is None:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.patch_all_io_mdl_files_on_disk()
        # Before setup_paths prepends repo: fix uv-only installs (must not use find_spec — loads stale mdl_auto).
        mod.ensure_injected_io_mdl_walkmesh()
    except Exception:
        pass


_patch_mdl_io_before_path_setup()


# Set up paths BEFORE importing anything that might import loggerplus (which depends on utility)
# This is critical for both frozen and non-frozen builds
def setup_paths():
    """Set up sys.path for local modules."""
    file_path = Path(__file__).resolve()
    repo_root = file_path.parents[4]  # Go up to repo root

    paths_to_add = [
        file_path.parent.parent,  # ./Tools/HolocronToolset/src/
        repo_root / "Tools" / "KotorDiff" / "src",  # ./Tools/KotorDiff/src/
        repo_root
        / "Libraries"
        / "PyKotor"
        / "src",  # ./Libraries/PyKotor/src/ (contains both pykotor and utility namespaces)
    ]

    for path in paths_to_add:
        path_str = str(path)
        if path.exists() and path_str not in sys.path:
            sys.path.insert(0, path_str)


# After prepending repo src, patch any second io_mdl (e.g. editable tree) if still vulnerable
setup_paths()
try:
    spec = importlib.util.spec_from_file_location(
        "_holocron_mdl_aabb2",
        Path(__file__).resolve().parent / "utils" / "mdl_io_aabb_patch_standalone.py",
    )
    if spec and spec.loader:
        mod2 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod2)
        mod2.patch_all_io_mdl_files_on_disk()
except Exception:
    pass

try:
    from toolset.utils.mdl_io_aabb_patch_standalone import ensure_injected_io_mdl_walkmesh

    ensure_injected_io_mdl_walkmesh()
except Exception:
    pass

from toolset.utils import ensure_mdl_aabb_hotfix  # noqa: E402

ensure_mdl_aabb_hotfix()
os.environ["QT_QPA_PLATFORM"] = ""

try:
    from toolset.main_app import main
except ImportError:
    # If import fails, paths might not be set correctly, try again
    setup_paths()
    from toolset.main_app import main

from toolset.main_init import main_init  # noqa: E402

if __name__ == "__main__":
    main_init()
    main()
