_This page explains how to package and test a mod with HoloPatcher. If you are installing a mod as a player, see [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher)._

## Creating a HoloPatcher mod

HoloPatcher is PyKotor's modern implementation of the TSLPatcher workflow. For mod authors, the main promise is continuity: the patch format stays compatible with established TSLPatcher packaging, while the surrounding tooling is easier to inspect, test, and extend.

Start with [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) if you need the original syntax reference. Use this page for the practical author workflow, current PyKotor-backed behavior, and the places where HoloPatcher documents features more clearly than the historical readme did.

**Verified against source files:**

- `Libraries/PyKotor/src/pykotor/tslpatcher/` - core parser, patch model, and merge logic
- `Libraries/PyKotor/src/pykotor/tslpatcher/mods/` - per-format patch implementations
- `Tools/HoloPatcher/src/holopatcher/` - GUI flow, namespace handling, logging, and backup behavior

**Implementation:** [`Libraries/PyKotor/src/pykotor/tslpatcher/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/tslpatcher/)

**Other mod installers and managers:**

- **[TSLPatcher](https://github.com/Fair-Strides/TSLPatcher)** - Original Perl TSLPatcher by stoffe (reference implementation)
- **[Kotor-Patch-Manager](https://github.com/LaneDibello/Kotor-Patch-Manager)** - Alternative mod manager with different patching approach
- **KotORModSync** — Multi-mod workflows, profiles, and install orchestration (complements HoloPatcher; does not replace INI patch semantics)

  - Canonical (th3w1zard1/KotORModSync): <https://github.com/th3w1zard1/KotORModSync/tree/c8b0d10ce3fd7525d593d34a3be8d151da7d3387>

**KotORModSync in practice:** Use HoloPatcher (or equivalent) to **apply** each mod’s `tslpatchdata` to a game installation. Use **KotORModSync** when you need help **tracking**, ordering, or syncing many installs across folders or team members. It is **not** a drop-in substitute for reading `[2DAList]` / `[TLKList]` rules—those remain defined by TSLPatcher/HoloPatcher INI. Repository: **`th3w1zard1/KotORModSync`** (verify file paths on the repo default branch before adding deep `#L` links in the wiki).

**Community context:** End users and mod authors often coordinate around [Deadly Stream — HoloPatcher](https://deadlystream.com/files/file/2243-holopatcher/) (downloads + discussion). Large distributions such as [KOTOR 1 Community Patch](https://deadlystream.com/files/file/1258-kotor-1-community-patch/) show what real-world HoloPatcher packaging looks like. Use those releases for workflow examples and player expectations; use this wiki and the TSLPatcher syntax pages as the source of truth for INI semantics.

**Related PyKotor Tools:**

- [`Tools/HolocronToolset/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Tools/HolocronToolset) - Integrated HoloPatcher [GUI](GFF-File-Format#gui-graphical-user-interface)
- [`Libraries/PyKotor/src/pykotor/tslpatcher/mods/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/tslpatcher/mods) - Individual patching modules

### See also

- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) - Original documentation
- [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher) - Player-facing install and restore flow
- [TSLPatcher InstallList Syntax](TSLPatcher-InstallList-Syntax) - file installation
- [TSLPatcher TLKList Syntax](TSLPatcher-TLKList-Syntax) - [TLK](Audio-and-Localization-Formats#tlk) patching
- [TSLPatcher 2DAList Syntax](TSLPatcher-2DAList-Syntax) - [2DA](2DA-File-Format) patching
- [TSLPatcher GFFList Syntax](TSLPatcher-GFFList-Syntax) - [GFF](GFF-File-Format) patching
- [TSLPatcher SSFList Syntax](TSLPatcher-SSFList-Syntax) - [SSF](Audio-and-Localization-Formats#ssf) patching
- [TSLPatcher HACKList Syntax](TSLPatcher-HACKList-Syntax) - Advanced [NCS](NCS-File-Format) binary patching
- [Explanations on HoloPatcher Internal Logic](Explanations-on-HoloPatcher-Internal-Logic) - Internal component flow and patch-routine behavior
- [Mod Creation Best Practices](Mod-Creation-Best-Practices) - General modding guidelines

## Walkthrough: first HoloPatcher mod (TLK + 2DA + InstallList)

**Goal:** Ship a minimal TSLPatcher-compatible package that adds a dialog string, touches one [2DA](2DA-File-Format) row, and installs one loose file without replacing whole vanilla tables.

**Prerequisites:**

- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) (skim)
- Syntax references open while you work:
  - [InstallList](TSLPatcher-InstallList-Syntax)
  - [TLKList](TSLPatcher-TLKList-Syntax)
  - [2DAList](TSLPatcher-2DAList-Syntax)
- HoloPatcher pointed at a **test** game copy

**Steps:**

1. **Layout:** `YourMod/tslpatchdata/changes.ini` plus any side files (e.g. `mymod.tlk` fragment, source 2DA snippet, loose file to copy).
2. **TLK:** In `[TLKList]`, reference a TLK patch file and add or modify rows per [TSLPatcher TLKList Syntax](TSLPatcher-TLKList-Syntax). Prefer **merge** operations over replacing entire `dialog.tlk` unless you intend a total replacement (replace-style examples appear under **[TLK](Audio-and-Localization-Formats#tlk) replacements** in [HoloPatcher changes](#holopatcher-changes--new-features) below).
3. **2DA:** In `[2DAList]`, target a small change (e.g. append one row to a non-critical table in the test install) using [TSLPatcher 2DAList Syntax](TSLPatcher-2DAList-Syntax). Use `2DAMEMORY`/labels so later steps can reference row indices if needed.
4. **InstallList:** Add `[InstallList]` entries to copy **one** file (e.g. a test `.nss` or texture) into `override/` or `modules/` per [TSLPatcher InstallList Syntax](TSLPatcher-InstallList-Syntax).
5. **Namespaces:** If you offer variants, add `namespaces.ini`; otherwise one `changes.ini` is enough.
6. **Install and inspect:** Run HoloPatcher against a test install and read the log before you launch the game.

**Verify in-game:** Confirm the loose file appears where expected, then confirm the TLK and 2DA changes in a tool or test dialogue before shipping.

**Alternatives:** For learning GFF-only flows, follow [Tutorial: Creating a new store](Tutorial-Creating-a-New-Store) in Holocron. For headless builds, use [CLI quickstart](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/CLI_QUICKSTART.md).

**Common failures:** pointing the patcher at `override/` instead of the **game root**, reinstalling the same option without [restore backup](Installing-Mods-with-HoloPatcher), and shipping bad relative paths in InstallList. See [Mod Creation Best Practices](Mod-Creation-Best-Practices#tslpatcher-setup-and-2datlk-merging).

<a id="holopatcher-changes--new-features"></a>
## HoloPatcher changes & New Features

### [TLK](Audio-and-Localization-Formats#tlk) replacements

- This is not recommended under most scenarios. You usually want to append a new entry and update your DLGs to point to it using [StrRef](Audio-and-Localization-Formats#string-references-strref) in the ini. However for projects like the k1cp and mods that fix grammatical/spelling mistakes, this may be useful.

The basic syntax is:

```ini
[TLKList]
ReplaceFile0=tlk_modifications_file.tlk

[tlk_modifications_file.tlk]
StrRef0=2
```

This will replace `StrRef0` in [dialog.tlk](Audio-and-Localization-Formats#tlk) with `StrRef2` from `tlk_modifications_file.tlk`.

[See our tests](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/tests/test_tslpatcher/test_reader.py#L463) for more examples.
Don't use the 'ignore' syntax or the 'range' syntax, these won't be documented or supported until further notice.

### HACKList (Editing [NCS](NCS-File-Format) directly)

This is a TSLPatcher feature that was [not documented in the TSLPatcher readme](https://github.com/OldRepublicDevs/PyKotor/wiki/TSLPatcher's-Official-Readme). Public examples are rare. The main known references are [Stoffe's HLFP mod](https://deadlystream.com/files/file/832-high-level-force-powers/) and a few historical forum archives.

Due to this feature being highly undocumented and only one known usage, our implementation might not match exactly. If you happen to find an old TSLPatcher mod that produces different HACKList results than HoloPatcher, [please report them here](https://github.com/OldRepublicDevs/PyKotor/issues/24)

In continuation, HoloPatcher's [HACKList] will use the following syntax:

```ini
[HACKList]
File0=script_to_modify.NCS

[script_to_modify.ncs]
20=StrRef5
40=2DAMEMORY10
60=65535
```

This will:

- Modify offset dec 20 (hex 0x14) of `script_to_modify.ncs` and overwrite that offset with the value of StrRef5.
- Modify offset dec 40 (hex 0x28) of `script_to_modify.ncs` and overwrite that offset with the value of 2DAMEMORY10.
- Modify offset dec 60 (hex 0x3C) of `script_to_modify.ncs` and overwrite that offset with the value of dec 65535 (hex 0xFFFF) i.e. the maximum possible value.
In short, HACKList writes unsigned WORD values (two bytes each) to the [NCS](NCS-File-Format) offsets named in the INI.

### For more information on HoloPatcher's implementation

#### [pykotor.tslpatcher.reader](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tslpatcher/reader.py#L697)

#### [pykotor.tslpatcher.mods.ncs](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tslpatcher/mods/ncs.py)

### See also

- [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher) -- End-user installation
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) -- TSLPatcher syntax
- [TSLPatcher TLKList](TSLPatcher-TLKList-Syntax)
- [TSLPatcher SSFList](TSLPatcher-SSFList-Syntax) -- Other patch lists
- [Explanations on HoloPatcher Internal Logic](Explanations-on-HoloPatcher-Internal-Logic) -- Implementation
- [Container-Formats#key](Container-Formats#key) -- Resource resolution
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, LucasForums for patching workflows
