# HolocronToolset ↔ PyKotor library (`pykotor.tools`)

Holocron should call **headless** APIs in the installable `pykotor` package (same tree as [Libraries/PyKotor/src/pykotor/](../../../../Libraries/PyKotor/src/pykotor/) in a full PyKotor checkout, or **`C:/GitHub/PyKotor`**).

- **TPC batch + editor bytes load:** `pykotor.tools.texture_batch` (`read_tpc_for_editor`, `convert_single_texture`, `batch_convert_textures`).
- **Single-file path converts:** `pykotor.tools.resources` (`convert_tpc_to_tga`, `convert_tga_to_tpc`).
- **Blender:** `io_scene_kotor` operators import **`pykotor.tools.texture_batch`** the same way.

## KotorBlender documentation

From the KotorBlender repo (or this tree when vendored):

- [docs/specs/holocron-toolset-migration-inventory.md](../../../../docs/specs/holocron-toolset-migration-inventory.md)
- [AGENTS.md](../../../../AGENTS.md) — `PYKOTOR_WHEEL_SRC`, `make wheel-download`

## Minimal example

```python
from pathlib import Path
from pykotor.tools.texture_batch import convert_single_texture

out = convert_single_texture(Path(user_selected_path), overwrite=True)
```
