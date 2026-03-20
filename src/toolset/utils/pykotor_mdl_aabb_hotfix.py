"""Patch installed pykotor ``io_mdl.py`` AABB reader (fixes seek(-1) on some walkmeshes).

``uv sync`` can restore an older pykotor wheel. See ``mdl_aabb_patch_text`` for logic.
"""

from __future__ import annotations

import importlib
import sys

from toolset.utils.mdl_aabb_patch_text import apply_patch_to_all_io_mdl


def ensure_mdl_aabb_hotfix() -> bool:
    """Patch all discovered ``io_mdl.py`` copies. Returns True if any file was written."""
    try:
        n = apply_patch_to_all_io_mdl()
    except OSError:
        return False
    if n:
        for name in ("pykotor.resource.formats.mdl.io_mdl", "pykotor.resource.formats.mdl.mdl_auto"):
            mod = sys.modules.get(name)
            if mod is not None:
                try:
                    importlib.reload(mod)
                except Exception:
                    pass
    return n > 0


def reload_mdl_modules_after_hotfix() -> None:
    """Call after ensure_mdl_aabb_hotfix() when modules were already imported."""
    for name in ("pykotor.resource.formats.mdl.io_mdl", "pykotor.resource.formats.mdl.mdl_auto"):
        mod = sys.modules.get(name)
        if mod is not None:
            importlib.reload(mod)
