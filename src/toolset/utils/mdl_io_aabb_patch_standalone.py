"""Patch pykotor ``io_mdl.py`` on disk (stdlib only). Called from ``toolset.__main__`` *before* ``setup_paths``.

Holocron prepends repo PyKotor src first; that can shadow a patched site-packages copy with an
old editable tree. Patching **before** path setup fixes the wheel under ``site-packages``.
"""

from __future__ import annotations

import sys

from pathlib import Path


def patch_io_mdl_source_text(text: str) -> str | None:
    """Return patched source, or None if already fixed / unchanged."""
    import re

    text = text.replace("\r\n", "\n")
    if "_aabb_child_ok" in text:
        return None
    orig = text

    text, _ = re.subn(
        r"(\s)if offset == 0 or offset >= reader\.size\(\) or offset \+ 40 > reader\.size\(\):",
        r"\1if offset <= 0 or offset >= reader.size() or offset + 40 > reader.size():",
        text,
        count=1,
    )

    old_seek = """                    reader.seek(offset)
                    # Read 6 floats (bounding box min/max)
                    bbox_min: Vector3 = reader.read_vector3()
                    bbox_max: Vector3 = reader.read_vector3()
                    # Read 4 int32s: left child offset, right child offset, face index, unknown
                    # NOTE: Child offsets in the file are stored as (absolute_offset - 12), but since
                    # BinaryReader has set_offset(+12) applied, these can be used directly.
                    left_child: int = reader.read_int32()
                    right_child: int = reader.read_int32()
                    face_index: int = reader.read_int32()
                    unknown: int = reader.read_int32()

                    aabb_node = MDLAABBNode("""
    new_seek = """                    try:
                        reader.seek(offset)
                        # Read 6 floats (bounding box min/max)
                        bbox_min: Vector3 = reader.read_vector3()
                        bbox_max: Vector3 = reader.read_vector3()
                        # Read 4 int32s: left child offset, right child offset, face index, unknown
                        # NOTE: Child offsets in the file are stored as (absolute_offset - 12), but since
                        # BinaryReader has set_offset(+12) applied, these can be used directly.
                        left_child: int = reader.read_int32()
                        right_child: int = reader.read_int32()
                        face_index: int = reader.read_int32()
                        unknown: int = reader.read_int32()
                    except OSError:
                        return (0, [])

                    aabb_node = MDLAABBNode("""
    if old_seek in text and "except OSError:\n                        return (0, [])" not in text:
        text = text.replace(old_seek, new_seek, 1)

    child_block = re.compile(
        r"(?m)^(?P<ind>[ \t]+)if face_index == -1:\s*\n"
        r"(?P<il>[ \t]+)if left_child != 0:\s*\n"
        r"(?P<bl>[ \t]+)child_count, child_nodes = _read_aabb_recursive\(reader, left_child\)\s*\n"
        r"(?P<cl>[ \t]+)count \+= child_count\s*\n"
        r"(?P<dl>[ \t]+)nodes\.extend\(child_nodes\)\s*\n"
        r"(?P<ir>[ \t]+)if right_child != 0:\s*\n"
        r"(?P<br>[ \t]+)child_count, child_nodes = _read_aabb_recursive\(reader, right_child\)\s*\n"
        r"(?P<cr>[ \t]+)count \+= child_count\s*\n"
        r"(?P<dr>[ \t]+)nodes\.extend\(child_nodes\)\s*\n",
    )
    m = child_block.search(text)
    if m:
        ind = m.group("ind")
        il, bl, cl, dl = m.group("il"), m.group("bl"), m.group("cl"), m.group("dl")
        ir, br, cr, dr = m.group("ir"), m.group("br"), m.group("cr"), m.group("dr")
        replacement = (
            f"{ind}def _aabb_child_ok(off: int) -> bool:\n"
            f"{ind}    return 0 < off < reader.size() and off + 40 <= reader.size()\n"
            f"\n"
            f"{ind}if face_index == -1:\n"
            f"{il}if _aabb_child_ok(left_child):\n"
            f"{bl}child_count, child_nodes = _read_aabb_recursive(reader, left_child)\n"
            f"{cl}count += child_count\n"
            f"{dl}nodes.extend(child_nodes)\n"
            f"{ir}if _aabb_child_ok(right_child):\n"
            f"{br}child_count, child_nodes = _read_aabb_recursive(reader, right_child)\n"
            f"{cr}count += child_count\n"
            f"{dr}nodes.extend(child_nodes)\n"
        )
        text = text[: m.start()] + replacement + text[m.end() :]

    if text == orig:
        lo = "if offset == 0 or offset >= reader.size() or offset + 40 > reader.size():"
        if lo in text:
            text = text.replace(
                lo,
                "if offset <= 0 or offset >= reader.size() or offset + 40 > reader.size():",
                1,
            )

    return text if text != orig else None


def force_write_io_mdl_file(path: Path, text: str) -> bool:
    """Write ``io_mdl.py`` even when marked read-only (uv cache on Windows)."""
    import os
    import stat
    import subprocess
    import sys
    import time

    p = Path(path)
    for _ in range(5):
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["cmd", "/c", "attrib", "-R", str(p)],
                    capture_output=True,
                    timeout=15,
                    check=False,
                )
            try:
                os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
            tmp = p.parent / f".{p.name}.aabb_new"
            tmp.write_text(text, encoding="utf-8", newline="\n")
            os.replace(tmp, p)
            return True
        except OSError:
            time.sleep(0.25)
    return False


def apply_force_io_mdl_walkmesh_disk_fix() -> bool:
    """Patch the *loaded* ``io_mdl.py`` (``iom.__file__``), force-write, reload, rebind.

    Do not guess paths from ``sys.path`` (``''`` + cwd can match the wrong file or miss site-packages).
    """
    import importlib
    import os

    if os.environ.get("PYKOTOR_SKIP_MDL_PATCH", "").lower() in ("1", "true", "yes"):
        return False
    name = "pykotor.resource.formats.mdl.io_mdl"
    try:
        import pykotor.resource.formats.mdl.io_mdl as iom
    except ImportError:
        return False
    try:
        mf = getattr(iom, "__file__", None) or ""
        p = Path(mf).resolve()
    except OSError:
        return False
    if not p.is_file():
        return False
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError:
        return False
    if "_aabb_child_ok" in raw:
        rebind_mdl_binary_reader_from_loaded_io_mdl()
        return True
    updated = patch_io_mdl_source_text(raw)
    if updated is None:
        return False
    if not force_write_io_mdl_file(p, updated):
        return False
    if name in sys.modules:
        importlib.reload(sys.modules[name])
    rebind_mdl_binary_reader_from_loaded_io_mdl()
    return True


def rebind_mdl_binary_reader_from_loaded_io_mdl() -> None:
    """Point mdl_auto (and mdl package) at the current io_mdl.MDLBinaryReader (fixes stale refs)."""
    import sys

    name = "pykotor.resource.formats.mdl.io_mdl"
    iom = sys.modules.get(name)
    if iom is None or not hasattr(iom, "MDLBinaryReader"):
        return
    cls = iom.MDLBinaryReader
    for mod_name in ("pykotor.resource.formats.mdl.mdl_auto", "pykotor.resource.formats.mdl"):
        m = sys.modules.get(mod_name)
        if m is not None and hasattr(m, "MDLBinaryReader"):
            m.MDLBinaryReader = cls


def ensure_injected_io_mdl_walkmesh() -> None:
    """Patch ``io_mdl`` on disk (attrib/chmod + atomic replace) and rebind ``mdl_auto``."""
    apply_force_io_mdl_walkmesh_disk_fix()


def patch_all_io_mdl_files_on_disk() -> None:
    import os
    import site
    import sys

    if os.environ.get("PYKOTOR_SKIP_MDL_PATCH", "").lower() in ("1", "true", "yes"):
        return

    seen: set[str] = set()
    roots: list[str] = []
    try:
        import sysconfig

        pl = sysconfig.get_path("purelib")
        if pl:
            roots.append(pl)
    except Exception:
        pass
    try:
        roots.extend(site.getsitepackages())
    except Exception:
        pass
    try:
        from site import getusersitepackages

        u = getusersitepackages()
        if u:
            roots.append(u)
    except Exception:
        pass
    roots.extend(x for x in sys.path if x)
    for root in roots:
        try:
            p = Path(root) / "pykotor/resource/formats/mdl/io_mdl.py"
        except OSError:
            continue
        if not p.is_file():
            continue
        try:
            key = str(p.resolve())
        except OSError:
            key = str(p)
        if key in seen:
            continue
        seen.add(key)
        try:
            raw = p.read_text(encoding="utf-8")
        except OSError:
            continue
        updated = patch_io_mdl_source_text(raw)
        if updated is None:
            continue
        if not force_write_io_mdl_file(p, updated):
            try:
                p.write_text(updated, encoding="utf-8", newline="\n")
            except OSError:
                continue
