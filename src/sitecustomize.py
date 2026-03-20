"""Holocron wheel installs this as ``site-packages/sitecustomize.py`` (py-modules).

Patches every ``io_mdl.py`` (purelib, ``sys.path``, site-packages) before imports.
Mirror: ``scripts/sitecustomize_koq_mdl.py``. Disable: ``PYKOTOR_SKIP_MDL_PATCH=1``.
"""
from __future__ import annotations

import os
import re
import site
import stat
import subprocess
import sys
import time
from pathlib import Path

_koq_disk_done = False


def _force_write(path: Path, data: str) -> bool:
    p = Path(path)
    for _ in range(6):
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["cmd", "/c", "attrib", "-R", str(p)],
                    capture_output=True,
                    timeout=20,
                    check=False,
                )
            try:
                os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
            tmp = p.parent / f".{p.name}.koq_tmp"
            tmp.write_text(data, encoding="utf-8", newline="\n")
            os.replace(tmp, p)
            return True
        except OSError:
            time.sleep(0.2)
    return False


def _patch_io_mdl_source(text: str) -> str | None:
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


_REL_IOMDL = Path("pykotor/resource/formats/mdl/io_mdl.py")


def _iter_io_mdl_files() -> list[Path]:
    seen: set[str] = set()
    out: list[Path] = []

    def add(base: str | Path) -> None:
        try:
            p = Path(base) / _REL_IOMDL
        except OSError:
            return
        if not p.is_file():
            return
        try:
            key = str(p.resolve())
        except OSError:
            key = str(p)
        if key in seen:
            return
        seen.add(key)
        out.append(p)

    for entry in sys.path:
        if entry:
            add(entry)
    try:
        import sysconfig

        pl = sysconfig.get_path("purelib")
        if pl:
            add(pl)
    except Exception:
        pass
    try:
        for sp in site.getsitepackages():
            add(sp)
    except Exception:
        pass
    try:
        from site import getusersitepackages

        u = getusersitepackages()
        if u:
            add(u)
    except Exception:
        pass
    return out


def _apply_koq_mdl_fix() -> None:
    global _koq_disk_done
    if _koq_disk_done:
        return
    if os.environ.get("PYKOTOR_SKIP_MDL_PATCH", "").lower() in ("1", "true", "yes"):
        _koq_disk_done = True
        return

    write_failed = False
    for p in _iter_io_mdl_files():
        try:
            raw = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if "_aabb_child_ok" in raw:
            continue
        updated = _patch_io_mdl_source(raw)
        if updated is None:
            continue
        if not _force_write(p, updated):
            write_failed = True
    if not write_failed:
        _koq_disk_done = True


_apply_koq_mdl_fix()
