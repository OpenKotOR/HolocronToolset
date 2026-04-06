from __future__ import annotations


def ensure_mdl_aabb_hotfix() -> bool:
    try:
        from toolset.utils.pykotor_mdl_aabb_hotfix import ensure_mdl_aabb_hotfix as _impl
    except ModuleNotFoundError as exc:
        if exc.name != "toolset.utils.pykotor_mdl_aabb_hotfix":
            raise
        return False
    return _impl()


def reload_mdl_modules_after_hotfix() -> None:
    try:
        from toolset.utils.pykotor_mdl_aabb_hotfix import reload_mdl_modules_after_hotfix as _impl
    except ModuleNotFoundError as exc:
        if exc.name != "toolset.utils.pykotor_mdl_aabb_hotfix":
            raise
        return
    _impl()
