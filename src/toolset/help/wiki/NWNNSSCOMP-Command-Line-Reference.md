# nwnnsscomp.exe Command-Line Argument Reference

Authoritative list of command-line conventions for **nwnnsscomp** (KotOR NWScript compiler) across known variants, for building a single unified CLI that can accept or emulate any of them without discrepancy.

**Primary source for exact argv forms:** PyKotor `Libraries/PyKotor/src/pykotor/resource/formats/ncs/compilers.py` (`KnownExternalCompilers`), verified against TSLPatcher readme and community docs.

---

## Placeholders used below

| Placeholder     | Meaning |
|----------------|--------|
| `{source}`     | Path to input file (NSS for compile, NCS for decompile) |
| `{output}`     | Full path to output file |
| `{output_dir}`  | Directory of output (parent of output file) |
| `{output_name}`| Filename only of output file |
| `{game_value}` | `"1"` = KotOR 1, `"2"` = TSL |

Executable is always the first argument (e.g. `nwnnsscomp.exe`); the tables list **arguments only** (argv[1:]).

---

## 1. V1 (original ~2003, Edward T. Smith / “v1.3 first public release”)

**Identification:** SHA256 `EC3E657C18A32AD13D28DA0AA3A77911B32D9661EA83CF0D9BCE02E1C4D8499D`  
**Reference:** PyKotor `KnownExternalCompilers.V1` (name: `"v1.3 first public release"`, release_date: 2003-12-31).

### Compile

| Order | Argument |
|-------|----------|
| 1 | `-c` |
| 2 | `{source}` |
| 3 | `{output}` |

**Example:**  
`nwnnsscomp.exe -c "C:\mod\script.nss" "C:\override\script.ncs"`

### Decompile

| Order | Argument |
|-------|----------|
| 1 | `-d` |
| 2 | `{source}` |
| 3 | `{output}` |

**Note:** No `-o` flag; output is a **positional** argument. No game flag; game/version is typically implied by which nwscript.nss is in the working directory or Override.

### Alternative / batch style (community docs)

Some readmes and forum posts describe an older or alternate style:

- **Version:** `-v1.00` (KotOR 1) or similar for game version.
- **Batch compile:** `-co` with positional arguments, e.g.  
  `nwnnsscomp -v1.00 -co Override\* Override\`  
  (compile all NSS in `Override\`, output to `Override\`).

This “-v1.00 / -co” form is **not** the same as the PyKotor V1 config above; it may correspond to an earlier Edward T. Smith build or a different variant. A unified CLI that aims to support “all” forms may need to accept both:

- **Modern V1 (PyKotor):** `-c` / `-d` with positional `source` and `output`.
- **Legacy/batch:** `-v1.00`, `-co`, and positional path(s).

---

## 2. TSLPatcher (tk102 custom, ~2006)

**Identification:** SHA256 `539EB689D2E0D3751AEED273385865278BEF6696C46BC0CAB116B40C3B2FE820`  
**Reference:**

- PyKotor `KnownExternalCompilers.TSLPATCHER`
- TSLPatcher’s Official Readme (tk102’s modified nwnnsscomp for TSLPatcher 1.2.7b4+)

### Compile

| Order | Argument |
|-------|----------|
| 1 | `-c` |
| 2 | `{source}` |
| 3 | `-o` |
| 4 | `{output}` |

**Example:**  
`nwnnsscomp.exe -c "C:\tslpatchdata\script.nss" -o "C:\override\script.ncs"`

### Decompile

| Order | Argument |
|-------|----------|
| 1 | `-d` |
| 2 | `{source}` |
| 3 | `-o` |
| 4 | `{output}` |

**Notes:**

- Output is specified with **`-o`** (not positional).
- No `-g` or `--outputdir`; TSLPatcher places nwscript.nss and NSS in tslpatchdata and calls the compiler from that context. Optional extra parameters can be passed via the INI key **ScriptCompilerFlags** (Settings section) -- see TSLPatcher’s Official Readme (change log 2006-01-14).

---

## 3. KOTOR Tool (Fred Tetra)

**Identification:** SHA256 `E36AA3172173B654AE20379888EDDC9CF45C62FBEB7AB05061C57B52961C824D`  
**Reference:**

- PyKotor `KnownExternalCompilers.KOTOR_TOOL`
- SourceForge kotortoolset (nwnnsscomp-kotor 1.02 / 1.05)
- Fred Tetra, v1.02 (March 2005) added game selection

### Compile

| Order | Argument    |
|-------|-------------|
| 1 | `-c` |
| 2 | `--outputdir` |
| 3 | `{output_dir}` |
| 4 | `-o` |
| 5 | `{output_name}` |
| 6 | `-g` |
| 7 | `{game_value}` |
| 8 | `{source}` |

**Example:**  
`nwnnsscomp.exe -c --outputdir "C:\override" -o "script.ncs" -g 1 "C:\mod\script.nss"`

### Decompile

| Order | Argument    |
|-------|-------------|
| 1 | `-d` |
| 2 | `--outputdir` |
| 3 | `{output_dir}` |
| 4 | `-o` |
| 5 | `{output_name}` |
| 6 | `-g` |
| 7 | `{game_value}` |
| 8 | `{source}` |

**Notes:**

- **`--outputdir`** + **`-o`** (output filename only) + **`-g`** (game: 1 = K1, 2 = TSL).  
- This variant expects nwscript.nss in Override (or similar); HoloPatcher’s “prepare CompileList” step installs nwscript.nss to Override when using non-TSLPatcher nwnnsscomp for this reason.

---

## 4. KOTOR Scripting Tool (James Goad / KobaltBlu)

**Identification:** SHA256 `B7344408A47BE8780816CF68F5A171A09640AB47AD1A905B7F87DE30A50A0A92`  
**Reference:**

- PyKotor `KnownExternalCompilers.KOTOR_SCRIPTING_TOOL`
- GitHub KobaltBlu/KotOR-Scripting-Tool (GUI around nwnnsscomp)

### Compile / Decompile

**Same as KOTOR Tool:** `-c` / `-d`, `--outputdir` `{output_dir}`, `-o` `{output_name}`, `-g` `{game_value}`, `{source}`.

So: same flags and argument order as Fred Tetra’s KOTOR Tool; only the binary (and thus SHA256) differs.

---

## Summary table (compile)

| Variant            | Compile argv (after executable) |
|--------------------|----------------------------------|
| **V1 (v1.3)**      | `-c` `{source}` `{output}` |
| **TSLPatcher**     | `-c` `{source}` `-o` `{output}` |
| **KOTOR Tool**     | `-c` `--outputdir` `{output_dir}` `-o` `{output_name}` `-g` `{game_value}` `{source}` |
| **KOTOR Scripting Tool** | Same as KOTOR Tool |

---

## Summary table (decompile)

| Variant            | Decompile argv (after executable) |
|--------------------|-----------------------------------|
| **V1 (v1.3)**      | `-d` `{source}` `{output}` |
| **TSLPatcher**     | `-d` `{source}` `-o` `{output}` |
| **KOTOR Tool**     | `-d` `--outputdir` `{output_dir}` `-o` `{output_name}` `-g` `{game_value}` `{source}` |
| **KOTOR Scripting Tool** | Same as KOTOR Tool |

---

## Unified CLI design notes

1. **Detection:** Identify variant by SHA256 of the binary (as in PyKotor `KnownExternalCompilers.from_sha256`) or by path (e.g. “KotOR Scripting Tool” dir vs “tslpatchdata” vs “Kotor Tool”).
2. **Single CLI that “accepts any”:** Either:
   - **Invoke existing binaries:** Use the correct argv for the detected compiler (as in `NwnnsscompConfig.get_compile_args` / `get_decompile_args`), or  
   - **Unified wrapper:** Accept multiple styles (e.g. both `-o path` and positional output, and both `-g 1|2` and `--outputdir`/`-o`) and map them to one internal representation, then emit the form required by the compiler you call.
3. **Game:** Only KOTOR Tool and KOTOR Scripting Tool use `-g`; TSLPatcher and V1 rely on working directory / nwscript.nss location.
4. **ScriptCompilerFlags:** TSLPatcher’s INI allows extra command-line parameters for nwnnsscomp; a unified CLI could support an “extra args” option that is appended after the canonical argv for the chosen variant.

---

## Primary sources

- **PyKotor:** `Libraries/PyKotor/src/pykotor/resource/formats/ncs/compilers.py` -- `ExternalCompilerConfig`, `KnownExternalCompilers`, `NwnnsscompConfig.get_compile_args` / `get_decompile_args`.
- **TSLPatcher:** `wiki/TSLPatcher's-Official-Readme.md` -- nwscript.nss + nwnnsscomp in tslpatchdata, tk102 custom build, ScriptCompilerFlags (Settings), CompileList behavior.
- **Community:** Deadly Stream “NWNNSSCOMP versions”; LucasForums/MixnMojo threads on nwnnsscomp -v1.00, -co, batch compile; SourceForge kotortoolset (nwnnsscomp-kotor 1.05); Hazard’s “KotOR Script Compiler Sourcecode”; KobaltBlu KotOR-Scripting-Tool (GUI, same CLI as KOTOR Tool for the bundled nwnnsscomp).

---

## Other variants (no argv in this doc)

- **DeNCS:** Same SHA256 as TSLPatcher in PyKotor; `commandline={}` (decompiler-only or different interface).
- **Xoreos Tools / knsscomp:** knsscomp uses `-c` `{source}` `-o` `{output}` for compile; no decompile. Xoreos has no commandline template in PyKotor.

### See also

- [NSS scripting reference](NSS-File-Format) — NWScript source language and function reference
- [NCS bytecode format](NCS-File-Format) — Compiled script format that nwnnsscomp produces
- [HoloPatcher — PatchLists](Explanations-on-HoloPatcher-Internal-Logic#patchlists) — Patcher-driven script compilation workflow
- [Mod creation best practices](Mod-Creation-Best-Practices) — Packaging compiled scripts for distribution
