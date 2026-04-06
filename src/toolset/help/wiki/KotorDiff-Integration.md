# KotorDiff Integration in PyKotor CLI

The standalone KotorDiff tool now ships inside PyKotor CLI and follows the same headless-first pattern as other Holocron utilities.

## Behavior

- Supplying any diff paths keeps execution headless; omitting paths or passing `--gui` launches the Tkinter UI (`Libraries/PyKotor/src/pykotor/diff_tool/__main__.py` L20-L120).
- CLI arguments are shared between the dedicated scripts (`kotordiff`, `kotordiff`, `diff`) and the `pykotorcli diff` subcommand (`Libraries/PyKotor/src/pykotor/diff_tool/cli.py` L26-L147).
- Headless execution builds a `KotorDiffConfig` and routes to the n-way differ (`Libraries/PyKotor/src/pykotor/diff_tool/cli.py` L168-L238).

## CLI Usage

```bash
# Installation vs installation with filtering
pykotorcli diff --path1 "C:\Games\KOTOR" --path2 "C:\Games\KOTOR_Modded" --filter tat_m17ac --output-mode normal

# Generate incremental TSLPatcher output while diffing
pykotorcli diff "C:\Games\KOTOR" "C:\Games\KOTOR_Modded" --tslpatchdata .\tslpatchdata --ini changes.ini --incremental

# Compare specific .rim module capsule m13ab.rim with the composite module folder m13ab (see RIM File Format).
pykotorcli diff "D:\workspace\Ajunta_Paul\m13ab.rim" "C:\Program Files (x86)\Steam\steamapps\common\swkotor\Modules\m13ab"

# Compare composite module danm13 with an entire installation
pykotorcli diff "D:\workspace\Dantooine_Modifications\danm13" "C:\Program Files (x86)\Steam\steamapps\common\swkotor"

# Compare installation with basic folder (compares folder including subfolders, with the installation respecting its resolution order)
pykotorcli diff "C:\Program Files (x86)\Steam\steamapps\common\swkotor" "D:\workspace\folder_with_various_gffs_2das_etc\"
```

Module capsules may be `.rim` ([RIM File Format](Container-Formats#rim)), `.mod`/`.erf` ([ERF File Format](Container-Formats#erf)), or composite module folders.

## Headless pipeline: NSS → pack → diff (P1)

**Goal:** Automate compile, pack resources into a module or tree layout, then diff against a baseline installation to review what changed or to scaffold incremental TSLPatcher output.

**Prerequisites:** [CLI quickstart](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/CLI_QUICKSTART.md), configured NSS compiler if you compile outside Holocron (`uvx PyKotor config --global nssCompiler …`), two game roots or a workspace folder vs install.

**Steps:**

1. **Compile:** From the repo / venv, `uvx PyKotor compile --file yourscript.nss` (or batch compile per CLI quickstart) so `.ncs` matches what the game loads.
2. **Pack:** Use `uvx PyKotor pack` (or Holocron export) to place scripts, GFFs, and 2DAs into `override/` or a module layout under your staging directory—see quickstart **Pack** and **Compile** sections.
3. **Diff:** Run `pykotorcli diff` with `--path1` baseline install and `--path2` staged or modded install; add `--filter` for one module if scope is large. Use `--tslpatchdata` / `--ini` / `--incremental` when generating patcher-oriented output (examples above).

**Verify in-game:** Load the affected module; confirm the compiled script runs and resources resolve per [Concepts — resource resolution](Concepts#resource-resolution-order).

**Alternatives:** Holocron-only compile + manual copy; diff two ZIP backups without KotorDiff (slower, no TSLPatcher scaffold).

**Common failures:** Forgetting `--noCompile` vs compile when packing stale `.ncs`; diffing paths that are not both game roots or comparable trees; incremental INI conflicts—re-run after a [HoloPatcher restore](HoloPatcher#installing-mods) on the test install.

Key flags:

- `--path1/--path2/--path3/--path` for multi-path comparisons
- `--filter` to constrain resources/modules
- `--output-mode` (`full`, `normal`, `quiet`) + `--output-log`
- `--tslpatchdata` / `--ini` with optional `--incremental` writer
- `--compare-hashes/--no-compare-hashes`, `--log-level`, `--no-color`, `--use-profiler`, `--gui`

## Implementation Notes

- Diff orchestration, filtering, and incremental TSLPatcher generation live in `[Libraries/PyKotor/src/pykotor/diff_tool/app.py](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/diff_tool/app.py)` L40-L530. Incremental writer creation and [StrRef](Audio-and-Localization-Formats#string-references-strref) analysis are handled in `handle_diff` and `generate_tslpatcher_data` (L295-L529).
- CLI argument wiring and headless execution are defined in `[Libraries/PyKotor/src/pykotor/diff_tool/cli.py](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/diff_tool/cli.py)` L26-L238.
- [GUI](GFF-File-Format#gui-graphical-user-interface) fallback is implemented in `[Libraries/PyKotor/src/pykotor/diff_tool/gui.py](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/diff_tool/gui.py)` (headless when arguments are present, UI when omitted).

### See also

- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) -- TSLPatcher overview
- [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers) -- Patching workflow
- [Container-Formats#key](Container-Formats#key) -- Resource resolution
- [Container-Formats#erf](Container-Formats#erf)
- [Container-Formats#rim](Container-Formats#rim)
- [GFF-File-Format](GFF-File-Format) -- Diffed resources and module capsules
- [Audio-and-Localization-Formats#tlk](Audio-and-Localization-Formats#tlk) -- StrRef handling in incremental output
