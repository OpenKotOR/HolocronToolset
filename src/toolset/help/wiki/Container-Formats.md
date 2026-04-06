# Container Formats

The KotOR engine organizes game resources into a layered archive system. At the base layer, **KEY** files provide a master index that maps resource names and types to locations inside **BIF** archives — this is how the engine finds shipped game data. Above that, **ERF** files (and their **MOD** and **SAV** variants) act as self-contained capsules for module-specific or save-specific content. **RIM** files serve a similar purpose for the stock module data shipped on the original discs. Together, these four formats implement the storage side of the [resource resolution order](Concepts#resource-resolution-order) described on [Concepts](Concepts). xoreos-tools exposes the same split operationally: `unkeybif` treats KEY and BIF as a linked index-plus-payload unit, while `unerf` and `unrim` treat ERF/MOD/SAV and RIM as separate archive families with different feature sets [[Running xoreos-tools](https://wiki.xoreos.org/index.php/Running_xoreos-tools), [Unkeybif](https://wiki.xoreos.org/index.php?title=Unkeybif), [Unerf](https://wiki.xoreos.org/index.php?title=Unerf), [Unrim](https://wiki.xoreos.org/index.php?title=Unrim)].

## Contents

- [KEY — Resource Key Index](#key)
- [BIF — Binary Resource Archive](#bif)
- [ERF — Encapsulated Resource File](#erf)
- [RIM — Resource Image](#rim)

---

<a id="key"></a>

# KEY — Resource Key Index

The KEY file is the master index for the game's base resource system. A single file — `chitin.key` — maps every resource name ([ResRef](Concepts#resref-resource-reference)) and resource type to a specific entry inside one of the game's [BIF archives](Container-Formats#bif). When the engine needs a vanilla resource that is not shadowed by the [override folder](Concepts#override-folder) or an active [MOD/ERF](Container-Formats#erf), it consults this index to find the correct BIF and the offset within it. xoreos's `unkeybif` documentation describes the same division explicitly: the KEY holds filenames and type IDs, the BIF holds file data, one KEY can control several BIFs, listing needs only the KEY, and full extraction needs the referenced BIFs as well [[Unkeybif](https://wiki.xoreos.org/index.php?title=Unkeybif)].

Mods do not normally edit the KEY file. Instead, they place content in the override folder or inside a module `.mod` capsule so the engine finds it before falling back to the KEY/BIF baseline. See [Concepts — Resource Resolution Order](Concepts#resource-resolution-order) and [Mod Creation Best Practices — File Priority](Mod-Creation-Best-Practices#file-priority-and-where-to-put-your-files).

## Table of Contents

- KEY — Resource Key Index
  - Table of Contents
  - [File structure overview](#file-structure-overview)
    - [KEY File Purpose](#key-file-purpose)
  - [Binary Format](#binary-format)
    - [File Header](#file-header)
    - [File Table](#file-table)
    - [Filename Table](#filename-table)
    - [KEY Table](#key-table)
  - [Resource ID Encoding](#resource-id-encoding)
  - [Cross-reference: implementations](#cross-reference-implementations)

---

## File structure overview

KEY files map resource names ([ResRefs](Concepts#resref-resource-reference)) and types to specific locations within [BIF containers](Container-Formats#bif). KotOR uses `chitin.key` as the main KEY file which references all game [BIF files](Container-Formats#bif). **Modder note:** Mods do not edit the KEY; they add content via the [override folder](Concepts#override-folder) or [MOD/ERF](Concepts#mod-erf-rim) so the engine finds their resources first.

See:

- [Concepts](Concepts)
- [Mod-Creation-Best-Practices — file priority](Mod-Creation-Best-Practices#file-priority-and-where-to-put-your-files)

### KEY File Purpose

The *KEY* file, specifically `chitin.key` in KotOR, serves as the master index for the game's resource system:

1. **Resource Lookup**: Maps *ResRef* + *Resource Type* ([hex IDs and labels](Resource-Formats-and-Resolution#resource-type-identifiers)) → [BIF](Container-Formats#bif) location
2. **[BIF](Container-Formats#bif) Registration**: Tracks all [BIF files](Container-Formats#bif) and their install paths
3. **Resource Naming**: Provides the filename (*ResRef*) missing from [BIF files](Container-Formats#bif)
4. **Drive Mapping**: Historical feature indicating which media held each [BIF](Container-Formats#bif):
   - [CD](https://en.wikipedia.org/wiki/Compact_disc)
   - [HD](https://en.wikipedia.org/wiki/Hard_disk_drive)

**Resource resolution (conceptual):** The full search order (override → MOD/ERF → save → KEY/BIF → defaults) and how the resource manager satisfies a demand are documented on [Concepts](Concepts#resource-resolution-order).

The *KEY* indexes [BIF](Container-Formats#bif) entries only (step 4 in that order). Higher-priority sources can shadow *KEY*-indexed assets without editing the *KEY*; using override or MOD for that is normal modding practice.

**Implementation:** [`Libraries/PyKotor/src/pykotor/resource/formats/key/`](https://github.com/OpenKotOR/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/key/)

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **PyKotor**

  - Layout spec: [`key_data.py` L1–L55](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py#L1-L55)
  - Binary I/O: [`KEYBinaryReader.load`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/key/io_key.py#L65-L128)
  - Binary I/O: [`KEYBinaryWriter`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/key/io_key.py#L143-L195) (`io_key.py`)
  - Data model: [`BifEntry`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py#L66-L152)
  - Data model: [`KeyEntry`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py#L154-L288)
  - Data model: [`KEY`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py#L291-L473)

- **[reone](https://github.com/modawan/reone)** ([historical upstream / mirror: seedhartha/reone](https://github.com/modawan/reone))

  - [`keyreader.cpp` `KeyReader::load`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/keyreader.cpp#L29-L39)
  - [`loadFiles` / `readFileEntry`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/keyreader.cpp#L41-L66)
  - [`loadKeys` / `readKeyEntry`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/keyreader.cpp#L68-L86)
  - Notes: reone lowercases ResRefs and splits `resource_id` into BIF index and resource index. It reads the 8-byte `"KEY V1 "` signature as one block, then the four table counts/offsets; it does not surface build year/day in this reader (those bytes are still present in KotOR `chitin.key` after the offsets).

- **[xoreos](https://github.com/xoreos/xoreos)**

  - Aurora *KEY*: `src/aurora/keyfile.cpp` (shared across Aurora-family games)
  - [xoreos-tools](https://github.com/xoreos/xoreos-tools) (tooling mirror)

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**

  - [`KEYObject.ts` `loadFile`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/KEYObject.ts#L39-L89) (header, BIF table, filename resolution, key entries)
  - Resource id helpers: [`getBIFIndex` / `getBIFResourceIndex`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/KEYObject.ts#L139-L147) (note: `getBIFResourceIndex` masks with `0x3FFF` in this file — the on-disk encoding uses **20** low bits; prefer `resId & 0xFFFFF` to match PyKotor/reone and the table below)
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**:

  - [`KEYBinaryStructure.cs` L17–L114](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorKEY/KEYBinaryStructure.cs#L17-L114) (`FileRoot`, `FileHeader`, `BIFInfo`, `Key` with `IndexIntoFileTable` / `IndexIntoResourceTable` properties)
- **Andastra / sotor (Rust)**:

  - local parser: `vendor/sotor/core/src/formats/key/read.rs`
  - local model/tests: `vendor/sotor/core/src/formats/key/mod.rs`
  - notes: accepts `KEY V1  ` and `KEY V1.1`, then decodes `resource_id` with the documented 12-bit BIF index / 20-bit resource index split

---

## [Binary Format](https://en.wikipedia.org/wiki/Binary_file)

### File Header

The file header is 64 bytes in size:

| Name                | type    | offset | size | Description                                    |
| ------------------- | ------- | ------ | ---- | ---------------------------------------------- |
| File Type           | [Char](https://en.wikipedia.org/wiki/Character_(computer_science)) | `0` (`0x00`) | `4`    | Always `"KEY "` (space-padded)                 |
| File Version        | [Char](https://en.wikipedia.org/wiki/Character_(computer_science)) | `4` (`0x04`) | `4`    | `"V1  "` or `"V1.1"`                           |
| [BIF](Container-Formats#bif) count           | UInt32  | `8` (`0x08`) | `4`    | Number of [BIF files](Container-Formats#bif) referenced                 |
| KEY count           | UInt32  | `12` (`0x0C`) | `4`    | Number of *Resource Entries*                     |
| Offset to File Table | UInt32 | `16` (`0x10`) | `4`    | Offset to [BIF File](Container-Formats#bif) Entries* Array               |
| Offset to KEY Table | UInt32 | `20` (`0x14`) | `4`    | Offset to *Resource Entries* Array               |
| Build Year          | UInt32  | `24` (`0x18`) | `4`    | Build Year (years since 1900)                  |
| Build Day           | UInt32  | `28` (`0x1C`) | `4`    | Build Day (days since Jan 1)                   |
| Reserved            | [Byte](https://en.wikipedia.org/wiki/Byte) | `32` (`0x20`) | `32`   | Padding (usually zeros)                        |

**Note on Header Variations**: **[xoreos-docs](https://github.com/xoreos/xoreos-docs)**: [`specs/torlack/key.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/key.html) (Tim Smith/Torlack's reverse-engineered documentation) shows the header ending at offset `0x0040` with unknown values at offset `0x0018`. The structure shown here (with *Build Year*/*Build Day* and *Reserved* fields) matches the actual *KotOR KEY* File Format.

The same overall KEY layout is also visible in Kotor.NET's binary structure reader ([KEYBinaryStructure.cs L17-L114](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorKEY/KEYBinaryStructure.cs#L17-L114)) and the Torlack/xoreos historical notes ([specs/torlack/key.html](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/key.html)); the local Andastra `vendor/sotor/core` Rust reader now follows the same header shape and explicitly accepts both `V1  ` and `V1.1`.

### File Table

Each file entry is 12 bytes:

| Name            | Type   | Offset | Size | Description                                                      |
| --------------- | ------ | ------ | ---- | ---------------------------------------------------------------- |
| File Size       | UInt32 | `0` (0x00) | `4`    | Size of [BIF](Container-Formats#bif) file on disk                                         |
| Filename Offset | UInt32 | `4` (0x04) | `4`    | Offset into filename table                                       |
| Filename Length | [UInt16](GFF-File-Format#gff-data-types) | `8` (0x08) | `2`    | Length of filename in bytes                                      |
| Drives          | [UInt16](GFF-File-Format#gff-data-types) | `10` (0x0A) | `2`    | Drive flags (`0x0001=HD0`, `0x0002=CD1`, etc.)                      |

**Drive Flags Explained:**

*Drive Flags* are a legacy feature from the multi-[CD](https://en.wikipedia.org/wiki/Compact_disc) distribution era:

| Flag Value | Meaning | Description |
| ---------- | ------- | ----------- |
| `0x0001` | `HD` ([Hard Drive](https://en.wikipedia.org/wiki/Hard_disk_drive)) | [BIF](Container-Formats#bif) is installed on the hard drive |
| `0x0002` | `CD1` ([CD](https://en.wikipedia.org/wiki/Compact_disc) 1) | [BIF](Container-Formats#bif) is on the first game disc |
| `0x0004` | `CD2` ([CD](https://en.wikipedia.org/wiki/Compact_disc) 2) | [BIF](Container-Formats#bif) is on the second game disc |
| `0x0008` | `CD3` ([CD](https://en.wikipedia.org/wiki/Compact_disc) 3) | [BIF](Container-Formats#bif) is on the third game disc |
| `0x0010` | `CD4` ([CD](https://en.wikipedia.org/wiki/Compact_disc) 4) | [BIF](Container-Formats#bif) is on the fourth game disc |

**Modern Usage:**

In contemporary distributions:

- [Steam](https://store.steampowered.com/)
- [GOG](https://www.gog.com/)
- [digital](https://en.wikipedia.org/wiki/Digital_distribution)

**Typical PC installs:**

- All [BIF files](Container-Formats#bif) use `0x0001` (`HD` Flag) since everything is installed locally
- The engine doesn't prompt for disc swapping
- Multiple flags can be combined (bitwise OR) if a [BIF](Container-Formats#bif) could be on multiple sources (e.g. `0x0001 | 0x0002` ([HD](https://en.wikipedia.org/wiki/Hard_disk_drive) Flag | [CD1](https://en.wikipedia.org/wiki/Compact_disc) Flag) for a [BIF](Container-Formats#bif) that is on both the hard drive and the first game disc)
- Mod tools typically set this to `0x0001` (`HD` Flag) for all files

The drive system was originally designed so the engine could:

- Prompt users to insert specific [CD](https://en.wikipedia.org/wiki/Compact_disc)s when needed resources weren't on the hard drive
- Optimize installation by allowing users to choose what to install vs. run from [CD](https://en.wikipedia.org/wiki/Compact_disc)
- Support partial installs to save disk space (common in the early 2000s)

That filename-table and drive-flag record layout is directly reflected in reone's KEY reader ([keyreader.cpp `loadFiles` / `readFileEntry` L41-L66](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/keyreader.cpp#L41-L66)).

### Filename Table

The *Filename Table* contains [null-terminated](https://en.cppreference.com/w/c/string/byte) strings:

| Name      | Type   | Description                                                      |
| --------- | ------ | ---------------------------------------------------------------- |
| Filenames | [char](GFF-File-Format#gff-data-types)[] | [null-terminated](https://en.cppreference.com/w/c/string/byte) [BIF](Container-Formats#bif) Filenames (e.g., `data/[models](MDL-MDX-File-Format).bif`)         |

### *KEY* Table

Each *KEY* entry is `22` (`0x16`) bytes in size:

| Name        | Type     | Offset | Size | Description                                                      |
| ----------- | -------- | ------ | ---- | ---------------------------------------------------------------- |
| *ResRef*      | [char](GFF-File-Format#gff-data-types) | `0` (`0x00`) | `16`   | Resource Filename (null-padded, max 16 characters)                   |
| Resource Type | [UInt16](GFF-File-Format#gff-data-types) | `16` (`0x10`) | `2`    | Numeric resource type ID ([wiki table](Resource-Formats-and-Resolution#resource-type-identifiers); PyKotor [`ResourceType`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py))                                         |
| Resource ID | UInt32   | `18` (`0x12`) | `4`    | Encoded Resource Location (see [Resource ID Encoding](#resource-id-encoding)) (e.g. `0x00000005` for the 5th Resource in the 1st [BIF](Container-Formats#bif)) |

**Critical Structure Packing Note:**

  The *KEY* entry structure must use **[byte](https://en.wikipedia.org/wiki/Byte) or [word](https://en.wikipedia.org/wiki/Word_(computer_architecture)) alignment** (1-[byte](https://en.wikipedia.org/wiki/Byte) or 2-[byte](https://en.wikipedia.org/wiki/Byte) packing). If the structure is packed with `4-[byte](https://en.wikipedia.org/wiki/Byte)` or `8-[byte](https://en.wikipedia.org/wiki/Byte)` alignment, the `UInt32` at offset `0x0012` (`18`) will be incorrectly placed at offset `0x0014` (`20`), causing incorrect *Resource ID* decoding.

On non-Intel platforms, this alignment requirement may cause alignment faults unless the compiler provides an "unaligned" type or special care is taken when accessing the `UInt32` field. The structure should be explicitly packed to ensure the `UInt32` starts at offset `18` (`0x12`) rather than being aligned to a `4-[byte](https://en.wikipedia.org/wiki/Byte)` or `8-[byte](https://en.wikipedia.org/wiki/Byte)` boundary.

That byte-level layout matches reone's [`loadKeys` / `readKeyEntry`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/keyreader.cpp#L68-L86), which reads a 16-byte ResRef, a `uint16` type, and the unaligned `uint32` resource id before splitting it with `>> 20` and `& 0xFFFFF`.

---

## Resource ID Encoding

The *Resource ID* field encodes both the [BIF](Container-Formats#bif) index and resource index within that [BIF](Container-Formats#bif):

- **bits `31-20`**: [BIF](Container-Formats#bif) Index (top 12 bits) - index into file table
- **bits `19-0`**: Resource Index (bottom 20 bits) - index within the [BIF](Container-Formats#bif) file

**Decoding:**

```python
bif_index = (resource_id >> 20) & 0xFFF  # top 12 bits
resource_index = resource_id & 0xFFFFF   # bottom 20 bits
```

**Encoding:**

```python
resource_id = (bif_index << 20) | resource_index
```

**Practical Limits:**

- Maximum [BIF](Container-Formats#bif) Files: `4,096` (12-bit [BIF](Container-Formats#bif) index)
- Maximum Resources per [BIF](Container-Formats#bif) File: `1,048,576` (20-bit resource index)

These limits are more than sufficient for KotOR, which typically has:

- `~50-100` [BIF](Container-Formats#bif) Files in a full installation
- `~100-10,000` Resources per [BIF](Container-Formats#bif) File (largest [BIF](Container-Formats#bif) Files are [texture](Texture-Formats#tpc) packs)

**Example:**

Given *Resource ID* `0x00123456`:

```plaintext
Binary: 0000 0000 0001 0010 0011 0100 0101 0110
        |---- 12 bits -----|------ 20 bits ------|
BIF Index:     0x001 (BIF Index: `1`)
Resource Index: 0x23456 (Resource Index: `144,470` within that [BIF](Container-Formats#bif) file)
```

The encoding allows a single 32-bit integer to precisely locate any resource in the entire [BIF](Container-Formats#bif) system (e.g. `0x00123456` for the 5th resource in the 1st [BIF](Container-Formats#bif) file).

This split is implemented directly in reone's [`readKeyEntry`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/keyreader.cpp#L82-L84) as `bifIdx = resId >> 20` and `resIdx = resId & 0xfffff`, and Torlack's historical [`key.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/key.html) documents the same packed-ID interpretation with worked examples.

---

PyKotor's KEY coverage is split between [`KEYBinaryReader.load`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/key/io_key.py#L65-L128), [`KEYBinaryWriter`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/key/io_key.py#L143-L195), and the structural notes plus data models in [`key_data.py`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py#L1-L473); the broader cross-tool comparison remains summarized under [File structure overview](#file-structure-overview).

### See also

- [BIF File Format](Container-Formats#bif) - Container format indexed by KEY
- [ERF File Format](Container-Formats#erf) - Self-contained containers (MOD/SAV/ERF) and resolution order
- [RIM File Format](Container-Formats#rim) - Stock module archives (resource image)
- [RIM versus ERF](Container-Formats#rim-versus-erf)
- [GFF File Format](GFF-File-Format) - Common content type resolved via KEY/BIF
- [Bioware Aurora KeyBIF](Bioware-Aurora-Core-Formats#keybif) - Official BioWare KEY/BIF specification
- [Concepts](Concepts) - Resource resolution order, override folder
- [Resource formats and resolution](Resource-Formats-and-Resolution#resource-type-identifiers) - Hex resource type IDs (SSOT table)
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, forums for override and resolution troubleshooting

---


---

<a id="bif"></a>

# BIF — BioWare Index File

BIF files hold the bulk of the game's read-only resources — models, textures, scripts, templates, and two-dimensional arrays. A single BIF can contain thousands of entries of mixed types, packed sequentially with a lightweight variable-resource table at the front. BIF files never store filenames; the companion [KEY file](Container-Formats#key) maps each ResRef and ResourceType pair to a BIF index and resource offset, so the engine can locate any asset with one KEY lookup followed by a single BIF seek.

## Table of Contents

- BIF — BioWare Index File
  - Table of Contents
  - [File structure overview](#file-structure-overview)
    - [BIF Usage in KotOR](#bif-usage-in-kotor)
  - [Binary Format](#binary-format)
    - [File Header](#file-header)
    - [Variable resource table](#variable-resource-table)
    - [Resource data](#resource-data)
  - [BZF Compression](#bzf-compression)
    - [BZF format details](#bzf-format-details)
  - [KEY file Relationship](#key-file-relationship)
  - [Cross-reference: implementations](#cross-reference-implementations)

---

## File structure overview

BIF files work in tandem with [KEY files](Container-Formats#key) which provide the filename-to-resource mappings. BIF files contain only resource IDs, types, and data - the actual filenames ([ResRefs](Concepts#resref-resource-reference)) are stored in the [KEY file](Container-Formats#key). BIF files are [containers](Container-Formats#erf) that store the bulk of game resources.

### BIF Usage in KotOR

BIF containers are the primary storage mechanism for game assets. The game organizes resources into multiple BIF files by category:

- `data/models.bif`: 3D [model](MDL-MDX-File-Format) files ([MDL/MDX](MDL-MDX-File-Format))
- `data/textures_*.bif`: [texture](Texture-Formats#tpc) data — companion files include [TPC](Texture-Formats#tpc) and [TXI](Texture-Formats#txi) — split across multiple containers
- `data/sounds.bif`: Audio files ([WAV](Audio-and-Localization-Formats#wav))
- `data/2da.bif`: Game data tables ([2DA files](2DA-File-Format))
- `data/scripts.bif`: Compiled scripts ([NCS](NCS-File-Format))
- `data/dialogs.bif`: Conversation files ([DLG](GFF-Creature-and-Dialogue#dlg))
- `data/lips.bif`: [LIP](Audio-and-Localization-Formats#lip)-sync [animation](MDL-MDX-File-Format#animation-header) data ([LIP](Audio-and-Localization-Formats#lip))
- Additional platform-specific BIFs (e.g., `dataxbox/`, `data_mac/`)

The [modular structure](https://en.wikipedia.org/wiki/Modular_programming) allows for efficient loading and potential platform-specific optimizations. Resources in BIF files are read-only at runtime; mods override them via the `override/` directory or custom [MOD](Container-Formats#erf) or [ERF](Container-Formats#erf) files. The engine loads from BIF only when the resource is not found in [override](Concepts#override-folder), loaded MOD, or save (see [resource resolution order](Concepts#resource-resolution-order)); the [KEY file](Container-Formats#key) supplies the mapping from ResRef to the correct BIF and offset.

**Implementation:** [`Libraries/PyKotor/src/pykotor/resource/formats/bif/`](https://github.com/OpenKotOR/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/)

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **PyKotor**:

  - layout (header + variable entries + BZF note): [`bif_data.py` module docstring L1–L40](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py#L1-L40)
  - `BIFType` / `BIFResource` / `BIF`: [`bif_data.py` L60–L569](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py#L60-L569)
  - binary I/O: [`BIFBinaryReader`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L51-L180) (`load` L83–L89, signature L91–L109, header L111–L120, resource table L122–L155, payload L157–L179)
  - [`BIFBinaryWriter`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L183-L256)
  - raw LZMA helper for BZF: [`_decompress_bzf_payload` L20–L48](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L20-L48)
- **[reone](https://github.com/modawan/reone)** ([historical upstream / mirror: seedhartha/reone](https://github.com/modawan/reone)):

  - [`bifreader.cpp` `BifReader::load` L27–L31](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/bifreader.cpp#L27-L31) (expects an 8-byte signature: `BIFFV1` plus one trailing ASCII space)
  - [`loadHeader` L34–L41](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/bifreader.cpp#L34-L41)
  - [`loadResources` L43–L50](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/bifreader.cpp#L43-L50)
  - [`readResourceEntry` L52–L67](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/bifreader.cpp#L52-L67)
- **[xoreos](https://github.com/xoreos/xoreos)** — [`biffile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/biffile.cpp) (Aurora-family BIF: fixed vs variable resource handling, KEY merge helpers)
- **[xoreos-tools](https://github.com/xoreos/xoreos-tools)** — [`biffile.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/aurora/biffile.cpp) (CLI / tooling)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**:

  - [`BIFObject.ts` `readFromDisk` L84–L115](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/BIFObject.ts#L84-L115) — reads 20-byte header and 16-byte variable rows
  - [`getResourceBuffer` L164–L177](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/BIFObject.ts#L164-L177).
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`BIFBinaryStructure.cs` `FileRoot` / `FileHeader` / `VariableResource` L16–L65](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs#L16-L65) — header skips the fixed-resource `uint32` with `BaseStream.Position += 4` before reading `OffsetToResources` (same on-disk layout as PyKotor/reone).
- **Andastra / sotor (Rust)**:

  - local parser: `vendor/sotor/core/src/formats/bif/read.rs`
  - local model/tests: `vendor/sotor/core/src/formats/bif/mod.rs`
  - notes: accepts `BIFF V1  ` and `BIFF V1.1`, validates that the fixed-resource count is `0`, and reads requested 16-byte variable-resource rows by absolute payload offset
- **[bioware-kaitai-formats](https://github.com/OpenKotOR/bioware-kaitai-formats)** — Kaitai Struct specs for BIF and related BioWare containers.

---

## [Binary Format](https://en.wikipedia.org/wiki/Binary_file)

### File Header

The file header is 20 bytes in size:

| Name                      | type    | offset | size | Description                                    |
| ------------------------- | ------- | ------ | ---- | ---------------------------------------------- |
| File Type                 | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 4    | `"BIFF"` for BIF, `"BZF "` for compressed BIF  |
| File Version              | [char](GFF-File-Format#gff-data-types) | 4 (0x04) | 4    | `"V1  "` for BIF, `"V1.0"` for BZF             |
| Variable Resource count   | UInt32  | 8 (0x08) | 4    | Number of variable-size resources              |
| Fixed Resource count      | UInt32  | 12 (0x0C) | 4    | Number of fixed-size resources (unused, always 0) |
| Offset to Variable Resource Table | UInt32 | 16 (0x10) | 4 | offset to variable resource entries            |

**Note on Fixed Resources:** The "Fixed Resource count" field is a legacy holdover from *Neverwinter Nights* (not used in *KotOR*) where some resource types had predetermined sizes. In *KotOR*, this field is always `0` and fixed resource tables are never used. All resources are stored in the variable resource table regardless of their size.

**Note on header Variations**: [xoreos-docs Torlack `bif.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/bif.html) shows the field at offset `0x000C` as “Unknown value” rather than “Fixed Resource count”. In *KotOR* it is always `0`; PyKotor **rejects** `fixed_res_count > 0` ([`io_bif.py` L117–L120](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L117-L120)), and the local Andastra `vendor/sotor/core` Rust reader now enforces the same constraint.

**References:**

- [xoreos `biffile.cpp` L64–L67](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/biffile.cpp#L64-L67) (fixed count must be 0)
- [reone `loadHeader` L34–L41](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/bifreader.cpp#L34-L41)
- [Kotor.NET `FileHeader` L35–L47](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs#L35-L47)
- [Torlack `bif.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/bif.html).

### Variable Resource Table

Each variable resource entry is 16 bytes:

| Name        | type   | offset | size | Description                                                      |
| ----------- | ------ | ------ | ---- | ---------------------------------------------------------------- |
| Resource ID | `UInt32` | 0 (0x00) | 4    | Resource ID (matches [KEY file](Container-Formats#key) entry, encodes BIF index and resource index) |
| Offset      | `UInt32` | 4 (0x04) | 4    | Offset to resource data in file (absolute file offset)                    |
| File Size   | `UInt32` | 8 (0x08) | 4    | Uncompressed size of resource data (bytes)                                 |
| Resource type | `UInt32` | 12 (0x0C) | 4    | Resource type identifier (hex IDs and labels: [Resource Type Identifiers](Resource-Formats-and-Resolution#resource-type-identifiers); PyKotor: `ResourceType` enum)                          |

**Entry Reading Order:**

Entries are read sequentially from the variable resource table. The table is located at the offset specified in the file header. Each entry is exactly 16 bytes, allowing efficient sequential reading.

**References:**

- [reone `readResourceEntry` L52–L67](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/bifreader.cpp#L52-L67)
- [Kotor.NET `VariableResource` L49–L64](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs#L49-L64)
- [xoreos `biffile.cpp` L84–L96](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/biffile.cpp#L84-L96)
- PyKotor table loop [`io_bif.py` L122–L141](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L122-L141).

### Resource Data

*Resource Data* is stored at the offsets specified in the resource table:

| Name         | type   | Description                                                      |
| ------------ | ------ | ---------------------------------------------------------------- |
| Resource Data | [byte](https://en.wikipedia.org/wiki/Byte)[] | Raw binary data for each resource                               |

**Resource Storage Details:**

- Resources are stored sequentially but not necessarily contiguously (gaps may exist between resources)
- Each resource's size is specified in the variable resource table entry
- *Resource Data* is stored in its native format (no additional BIF-specific wrapping or metadata)
- Offsets in the variable resource table are absolute file offsets (relative to start of file)
- *Resource Data* begins immediately at the specified offset

**Resource Access Flow:**

The engine reads resources through the following process:

1. **KEY Lookup**: Look up the ResRef (and optionally *ResourceType*) in the [KEY file](Container-Formats#key) to get the Resource ID
2. **ID Decoding**: Extract the BIF index (upper 12 bits) and resource index (lower 20 bits) from the *Resource ID*
3. **BIF Selection**: Use the BIF index to identify which *BIF* file contains the resource
4. **Table Access**: Read the *BIF* file header to find the offset to the variable resource table
5. **Entry Lookup**: Find the resource entry at the specified index in the *variable resource table*
6. **Data Reading**: Seek to the offset specified in the entry and read the number of bytes specified by the file size

That lookup flow matches xoreos's [`biffile.cpp`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/biffile.cpp#L84-L123), which reads each variable-resource row and merges the result with KEY metadata, reone's [`loadResources`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/bifreader.cpp#L43-L50), and Torlack's [`bif.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/bif.html) description of the row semantics.

**Resource IDs:**

The *Resource ID* in the *BIF* file's *variable resource table* must match the *Resource ID* stored in the [KEY file](Container-Formats#key). The *Resource ID* is a 32-bit value that encodes two pieces of information:

- **Lower 20 bits (bits 0-19)**: Resource index within the *BIF* file (0-based index into the variable resource table)
- **Upper 12 bits (bits 20-31)**: BIF index in the [KEY file](Container-Formats#key)'s *BIF* table (identifies which *BIF* file contains this resource)

**Example:** A *Resource ID* of `0x00400029` decodes as:

- Resource index: `0x29` (41st resource in the *BIF*)
- BIF index: `0x004` (4th *BIF* file in the [KEY](Container-Formats#key)'s *BIF* table)

**References:**

- [KEY File Format](Container-Formats#resource-id-encoding)
- [Torlack `key.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/key.html) (worked examples)
- [reone `readResourceEntry` L54–L56](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/bifreader.cpp#L54-L56) (reads `id` field from each 16-byte row).

---

## BZF [Compression](https://en.wikipedia.org/wiki/Data_compression)

*BZF* files are LZMA-compressed *BIF* files used primarily in iOS (and maybe Android) ports of *KotOR*. The *BZF* header contains `"BZF "` + `"V1.0"`, followed by LZMA-compressed *BIF* data. Decompression reveals a standard *BIF* structure.

### BZF format details

The *BZF* format wraps a complete *BIF* file in LZMA compression:

1. **BZF header** (8 bytes): `"BZF "` + `"V1.0"` signature
2. **LZMA Stream**: Compressed *BIF* file data using LZMA algorithm
3. **Decompressed Result**: Standard *BIF* file structure (as described above)

**compression Details:**

- The entire *BIF* file (after the 8-[byte](https://en.wikipedia.org/wiki/Byte) header) is compressed using LZMA (Lempel-Ziv-Markov chain Algorithm)
- LZMA provides high compression ratios with good decompression speed
- The compressed stream follows immediately after the BZF header
- Decompression yields a standard *BIF* file that can be read normally

**Benefits of BZF:**

- Significantly reduced file sizes (typically 40-60% compression ratio)
- Faster download times for mobile platforms
- Reduced storage requirements
- Identical resource access after decompression
- No performance penalty during gameplay (decompressed once at load time)

**Platform Usage:**

- PC releases use uncompressed *BIF* files for faster access
- Mobile releases (iOS/Android) use *BZF* for storage efficiency
- Modding tools can (and should) convert between *BIF* and *BZF* formats freely

**Implementation Notes:**

The *BZF* wrapper is completely transparent to the game engine - once decompressed in memory, the resource access patterns are identical to standard BIF files. Tools should decompress *BZF* files before reading resource entries, as the variable resource table offsets are relative to the decompressed BIF structure.

**References:**

- PyKotor BZF wrapper layout — [`bif_data.py` L35–L39](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py#L35-L39)
- PyKotor BZF decompression entry — [`io_bif.py` L162–L169](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L162-L169)
- PyKotor LZMA payload decode — [`_decompress_bzf_payload` L20–L48](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L20-L48)
- PyKotor **version string** (`BIFBinaryReader` accepts `V1` + two ASCII spaces or `V1.1` in the 8-byte signature for **both** BIF and BZF) — [`io_bif.py` L107–L109](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L107-L109)
- Some distributions describe mobile BZF as `V1.0` in prose—verify against real headers if a file fails to load.
- [xoreos `biffile.h` L56–L60](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/biffile.h#L56-L60)
- [reone `BifReader::load` L27–L31](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/bifreader.cpp#L27-L31)

---

## [KEY](Container-Formats#key) File Relationship

*BIF* files require a [KEY file](Container-Formats#key) to map resource IDs to filenames (ResRefs). The [KEY file](Container-Formats#key) contains:

- *BIF* file entries (filename, size, location)
- [KEY](Container-Formats#key) entries mapping *ResRef* + *ResourceType* (see [Resource Type Identifiers](Resource-Formats-and-Resolution#resource-type-identifiers)) to *Resource ID*

The *Resource ID* in the *BIF* file matches the *Resource ID* in the [KEY File](Container-Formats#key)'s [KEY](Container-Formats#key) entries.

See [KEY File Format](Container-Formats#key) for the matching KEY-side lookup and BIF index encoding.

---

PyKotor's BIF implementation is centered in [`io_bif.py`](https://github.com/OpenKotOR/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py) for binary read and write paths and [`bif_data.py`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py#L100-L575) for the in-memory model.

### See also

- [Resource formats and resolution](Resource-Formats-and-Resolution#resource-type-identifiers) -- Hex resource type IDs
- [Container-Formats#key](Container-Formats#key) -- *BIF* indexing and resource resolution
- [Container-Formats#erf](Container-Formats#erf) -- *ERF/MOD* containers
- [GFF-File-Format](GFF-File-Format) -- *GFF* resources in *BIF*
- [RIM File Format](Container-Formats#rim) — Resource image module archives ([contrast with ERF](Container-Formats#rim-versus-erf))
- [Bioware-Aurora-KeyBIF](Bioware-Aurora-Core-Formats#keybif) -- *Aurora* *KEY/BIF* specification

---


---

<a id="erf"></a>

# ERF — Encapsulated Resource File

ERF is a self-contained resource archive: every entry carries its own ResRef and type, so no external KEY file is needed. The engine uses ERF (and its signature variants MOD, SAV) for module content, saved games, override packs, and any other bundle that must travel as a single file. The header includes an optional localized-string list — primarily used in SAV files to store the save-game description — followed by a key list pointing into a contiguous data block. Shipped modules also use **[RIM](Container-Formats#rim)** archives, which solve the same naming problem with a simpler binary layout; see [RIM versus ERF](#rim-versus-erf) and the dedicated [RIM section](Container-Formats#rim).

## Table of Contents

- ERF — Encapsulated Resource File
  - Table of Contents
  - [File Structure Overview](#file-structure-overview)
  - [RIM versus ERF](#rim-versus-erf)
  - [Binary Format](#binary-format)
    - [File Header](#file-header)
    - [Localized String List](#localized-string-list)
    - [KEY List](#key-list)
    - [Resource List](#resource-list)
    - [Resource Data](#resource-data)
    - [MOD/NWM File Format Quirk: Blank Data Block](#modnwm-file-format-quirk-blank-data-block)
  - [ERF Variants](#erf-variants)
    - [MOD Files (module containers)](#mod-files-module-containers)
    - [SAV Files (save game containers)](#sav-files-save-game-containers)
    - [RIM files (resource image)](#rim-files-resource-image)
    - [ERF Files (Generic Containers)](#erf-files-generic-containers)
  - [Cross-reference: implementations](#cross-reference-implementations)

---

## File Structure Overview

*ERF* files are self-contained containers that store both resource names ([ResRefs](Concepts#resref-resource-reference)) and data in the same file. Unlike [BIF files](Container-Formats#bif) which require a [KEY file](Container-Formats#key) for filename lookups, *ERF* files include *ResRef* information directly in the container. When the engine resolves a resource request, it can service from encapsulated containers (*MOD/ERF* and stock [RIM](Container-Formats#rim) module archives) before falling back to *KEY/BIF*; see [resource resolution order](Concepts#resource-resolution-order).

**For mod developers:**

- *MOD* files are built with Holocron Toolset or other packers.
- See [Installing Mods with HoloPatcher](HoloPatcher#installing-mods).
- See [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers).
- Vanilla modules ship as `.rim` / `_s.rim` ([RIM](Container-Formats#rim)); a `.mod` in `modules/` overrides the same module’s RIM set when present.

**Related formats:**

- *ERF* containers commonly hold:

  - [GFF](GFF-File-Format)
  - [2DA](2DA-File-Format)
  - [TPC](Texture-Formats#tpc)
  - [NCS](NCS-File-Format)
  - other resource types

- Alternative storage:

  - [KEY](Container-Formats#key)
  - [BIF](Container-Formats#bif)

**Modder note:** Use *MOD*s for module-specific content (area GFFs, module 2DAs); use [override](Concepts#override-folder) for global replacements.

See:

- [Concepts — MOD / ERF / RIM](Concepts#mod-erf-rim)
- [Mod-Creation-Best-Practices — file priority](Mod-Creation-Best-Practices#file-priority-and-where-to-put-your-files)

**Implementation (PyKotor):**

- package: [`Libraries/PyKotor/src/pykotor/resource/formats/erf/`](https://github.com/OpenKotOR/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/)
- layout table in [`erf_data.py`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L19-L54) docstring
- read path [`ERFBinaryReader.load`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L51-L169)
- write path [`ERFBinaryWriter.write`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L186-L256)

Other engines and tools cover the same container family in parallel: reone's [`erfreader.cpp`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/erfreader.cpp#L29-L92) and [`erfreader.h`](https://github.com/modawan/reone/blob/master/include/reone/resource/format/erfreader.h) parse `ERF V1.0` and `MOD V1.0` but intentionally skip localized strings and do not expose explicit `SAV` fourcc handling; KotOR.js's [`ERFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/ERFObject.ts#L69-L346) covers header, localized strings, keys, resource records, and serialization; Kotor.NET's [`ERFBinaryStructure.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L25-L161) reads the core structures but skips the description StrRef and reserved tail; the local Andastra `vendor/sotor/core` Rust implementation covers the same header, localized-string, key-list, and resource-list read path in `src/formats/erf/read.rs` with matching in-memory structures in `src/formats/erf/mod.rs`; xoreos and xoreos-tools both use [`erffile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/erffile.cpp) style Aurora readers; KotOR-Unity ships its own [`ERFObject.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/ERFObject.cs); and the [`bioware-kaitai-formats`](https://github.com/OpenKotOR/bioware-kaitai-formats) project provides declarative ERF specs for code generation. More repo cross-links are cataloged on [Home — Cross-reference: other tools and engines](Home#cross-reference-other-tools-and-engines).

---

## RIM versus ERF

[RIM](Container-Formats#rim) (**resource image**) files are the **stock** module archives under `modules/`. They are **encapsulated** containers like ERF/MOD (ResRef + type + bytes in one file) but **not** the same on-disk structure as this document’s 160-byte **ERF** header. Tools that only parse ERF must convert or use a RIM-aware reader.

| Feature | RIM ([RIM File Format](Container-Formats#rim)) | ERF / MOD / SAV (this page) |
| ------- | ---------------------------------------- | ---------------------------------- |
| Signature | `RIM` + `V1.0` | `ERF` / `MOD` / `SAV` + `V1.0` |
| Header size | **120** bytes | **160** bytes |
| Localized strings, build date, description StrRef | Absent | Present (strings optional) |
| Index layout | One **32-byte** record per resource (includes **UInt32** type, offset, size) | **24-byte** [KEY](Container-Formats#key)-style list + separate **8-byte** offset/size list |
| MOD-only gap | N/A | Optional **8-byte × entry_count** zero block between key list and resource list ([quirk](#modnwm-file-format-quirk-blank-data-block)) |

**Engine and tooling:** Both families are loaded as module-side capsules ahead of [KEY](Container-Formats#key) and [BIF](Container-Formats#bif) for resources they contain; see [resource resolution order](Concepts#resource-resolution-order). PyKotor can turn a loaded RIM into an in-memory ERF via `RIM.to_erf()` for writing MOD/ERF output.

**Normative RIM layout:** Field sizes, implicit offset `0` → table at byte 120, and padding behavior are specified on [RIM File Format](Container-Formats#rim).

---

## [Binary Format](https://en.wikipedia.org/wiki/Binary_file)

Everything in this section applies to **ERF**, **MOD**, and **SAV** signatures only. **[RIM](Container-Formats#rim)** uses a shorter header and a different index record layout; do not treat these tables as the [RIM](Container-Formats#rim) specification.

### File Header

The *file header* is **160 bytes** in size:

| Name                      | Type    | Offset | Size | Description                                    |
| ------------------------- | ------- | ------ | ---- | ---------------------------------------------- |
| File Type                 | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 4    | `"ERF "`, `"MOD "`, `"SAV "` |
| File Version              | [char](GFF-File-Format#gff-data-types) | 4 (0x04) | 4    | Always `"V1.0"`                                 |
| Language count            | UInt32  | 8 (0x08) | 4    | Number of localized string entries             |
| Localized string size     | UInt32  | 12 (0x0C) | 4    | Total size of localized string data in bytes   |
| Entry count               | UInt32  | 16 (0x10) | 4    | Number of resources in the container              |
| Offset to Localized string List | UInt32 | 20 (0x14) | 4 | Offset to localized string entries             |
| Offset to [KEY](Container-Formats#key) List        | UInt32  | 24 (0x18) | 4    | Offset to [KEY](Container-Formats#key) entries array                    |
| Offset to Resource List   | UInt32  | 28 (0x1C) | 4    | Offset to resource entries array                |
| Build Year                | UInt32  | 32 (0x20) | 4    | Build year (years since 1900)                   |
| Build Day                 | UInt32  | 36 (0x24) | 4    | Build day (days since Jan 1)                   |
| Description [StrRef](Audio-and-Localization-Formats#string-references-strref)        | UInt32  | 40 (0x28) | 4    | [TLK](Audio-and-Localization-Formats#tlk) string reference for description           |
| Reserved                  | [byte](https://en.wikipedia.org/wiki/Byte) | 44 (0x2C)  | 116  | Padding (usually zeros)                         |

**Build Date Fields:**

The *Build Year* and *Build Day* fields timestamp when the [ERF](Container-Formats#erf) file was created:

- **Build Year**: Years since 1900 (e.g., 103 = year 2003)
- **Build Day**: Day of year (1-365/366, with January 1 = day 1)

These timestamps are primarily informational and used by development tools to track module versions. The game engine doesn't rely on them for functionality.

**Example Calculation:**

```plaintext
Build Year: 103 --> 1900 + 103 = 2003
Build Day: 247 --> September 4th (the 247th day of 2003)
```

Most mod tools either zero out these fields or set them to the current date when creating/modifying ERF files.

**Description [StrRef](Audio-and-Localization-Formats#string-references-strref) values by file type:**

The Description [StrRef](Audio-and-Localization-Formats#string-references-strref) field (offset 0x0028 / 0x28) varies depending on the ERF variant:

- **MOD files**: `0xFFFFFFFF` (-1) is the standard for BioWare modules.
  - *Exception*: TSL LIPS files consistently use `0xCDCDCDCD` (Debug Fill).
  - *Exception*: Some KOTOR 1 modules (e.g. `unk_m41` series) use `0`.
- **SAV files**: `0` (typically no description)
- **NWM files**: `-1` (**Neverwinter Nights module format, NOT used in KotOR**)
- **ERF files**: Unpredictable (may contain valid [StrRef](Audio-and-Localization-Formats#string-references-strref) or `-1`)

**Technical Note**: The engine determines if a file is a Save Game based on context (loading from `saves/` vs `modules/` and presence of `SAVES:` resource alias), **NOT** by any flag or value in the ERF header; that matches PyKotor's full 160-byte header read and layout table, KotOR.js's `ERFObject.parseHeader`, Kotor.NET's partial header reader, and the historical Torlack RE notes in xoreos-docs ([`io_erf.py` L70-L96](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L70-L96), [`erf_data.py` L19-L36](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L19-L36), [`ERFObject.ts` L69-L85](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/ERFObject.ts#L69-L85), [`ERFBinaryStructure.cs` L86-L97](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L86-L97), [xoreos-docs `specs/torlack/mod.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/mod.html)).

### Localized String List

Localized strings provide descriptions in multiple languages:

| Name         | type    | size | Description                                                      |
| ------------ | ------- | ---- | ---------------------------------------------------------------- |
| Language ID  | UInt32  | 4    | Language identifier ([Concepts](Concepts#language-ids-kotor))                          |
| string size  | UInt32  | 4    | Length of string in bytes                                       |
| string data  | [char](GFF-File-Format#gff-data-types)[]  | N    | `windows-1252` encoded text                     |

**Localized string Usage:**

ERF localized strings provide multi-language descriptions for the container itself. These are primarily used in MOD files to display module names and descriptions in the game's module selection screen.

**Language IDs:** Use the shared Aurora numeric enum and encodings on [Concepts](Concepts#language-ids-kotor) (same values as TLK and GFF localized strings).

**Important Notes:**

- Most ERF files have zero localized strings (Language count = 0)
- MOD files may include localized module names for the load screen
- **Engine Behavior**: The game engine's resource loader (`CExoKeyTable::AddEncapsulatedContents`) **ignores** these fields. They are likely used only by the specific UI components (like the Module Selection screen).
- **Encoding**: Strings should be encoded as `windows-1252` (CP1252) to support legacy BioWare character sets.
- The Description [StrRef](Audio-and-Localization-Formats#string-references-strref) field (in header) provides an alternative via [TLK](Audio-and-Localization-Formats#tlk) reference

PyKotor's localized-string block reader and writer and KotOR.js's `parseStructures` confirm that this list is a simple `language id + byte length + text` sequence, while reone's `ErfReader` omits localized-string parsing entirely, so PyKotor and KotOR.js are the better implementation references for this subsection ([`io_erf.py` L122-L143](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L122-L143), [`io_erf.py` L235-L240](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L235-L240), [`ERFObject.ts` L91-L97](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/ERFObject.ts#L91-L97)).

### [KEY](Container-Formats#key) List

Each [KEY](Container-Formats#key) entry is 24 bytes and maps ResRefs to resource indices:

| Name        | type     | offset | size | Description                                                      |
| ----------- | -------- | ------ | ---- | ---------------------------------------------------------------- |
| *ResRef*      | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 16   | Resource filename (null-padded, max 16 chars)                    |
| Resource ID | UInt32   | 16 (0x10) | 4    | index into resource list                                         |
| Resource type | [uint16](GFF-File-Format#gff-data-types) | 20 (0x14) | 2    | Resource type ID ([table](Resource-Formats-and-Resolution#resource-type-identifiers))                                         |
| Unused      | [uint16](GFF-File-Format#gff-data-types)   | 22 (0x16) | 2    | Padding                                                           |

***ResRef* Padding Notes:**

Resource names are padded with NULL bytes to 16 characters, but are not necessarily [null-terminated](https://en.cppreference.com/w/c/string/byte). If a resource name is exactly 16 characters long, no [null terminator](https://en.cppreference.com/w/c/string/byte) exists. Resource names can be mixed case, though most are lowercase in practice.

PyKotor's reader and writer, KotOR.js's key loop, Kotor.NET's `KeyEntry` reader, reone's `readKeyEntry`, and Torlack's padding notes all agree on the 24-byte layout; the main behavioral difference is casing, because PyKotor preserves the stored ResRef while reone lowercases it during import ([`io_erf.py` L148-L155](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L148-L155), [`io_erf.py` L242-L246](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L242-L246), [`ERFObject.ts` L101-L108](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/ERFObject.ts#L101-L108), [`ERFBinaryStructure.cs` L128-L134](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L128-L134), [`erfreader.cpp` L62-L71](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/erfreader.cpp#L62-L71), [xoreos-docs `specs/torlack/mod.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/mod.html)).

### Resource List

Each resource entry is 8 bytes:

| Name          | type   | offset | size | Description                                                      |
| ------------- | ------ | ------ | ---- | ---------------------------------------------------------------- |
| offset to data | UInt32 | 0 (0x00) | 4    | offset to resource data in file                                  |
| Resource size | UInt32 | 4 (0x04) | 4    | size of resource data in bytes                                   |

PyKotor, KotOR.js, Kotor.NET, and reone all implement the resource list as a compact `(offset, size)` array and then use those pairs to seek into the payload region, with PyKotor also mirroring the layout on write ([`io_erf.py` L159-L162](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L159-L162), [`io_erf.py` L248-L252](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L248-L252), [`ERFObject.ts` L112-L116](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/ERFObject.ts#L112-L116), [`ERFBinaryStructure.cs` L157-L161](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L157-L161), [`erfreader.cpp` L84-L92](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/erfreader.cpp#L84-L92)).

### Resource data

Resource data is stored at the offsets specified in the resource list:

| Name         | type   | Description                                                      |
| ------------ | ------ | ---------------------------------------------------------------- |
| Resource data | [byte](https://en.wikipedia.org/wiki/Byte)[] | Raw binary data for each resource                               |

### MOD/NWM file format Quirk: Blank data Block

**Note**: For MOD and NWM files only, there exists an unusual block of data between the resource structures ([KEY](Container-Formats#key) List) and the position structures (Resource List). This block is 8 bytes per resource and appears to be all NULL bytes in practice. This data block is not referenced by any offset in the ERF file header, which is uncharacteristic of BioWare's file format design.

The best published description of this odd padding region is still Torlack's historical `Strange Blank data` note preserved in xoreos-docs, which is why most modern implementations mention it but do not assign it semantic meaning ([xoreos-docs `specs/torlack/mod.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/mod.html)).

---

## ERF Variants

ERF files come in several variants based on file type:

| file type | Extension | Description                                                      |
| --------- | --------- | ---------------------------------------------------------------- |
| ERF       | `.erf`    | Generic encapsulated resource file                               |
| MOD       | `.mod`    | Module file (contains area resources)                            |
| SAV       | `.sav`    | Save game file (contains saved game state)                       |

The **on-disk** 160-byte layout is the same family for shipped KotOR capsules; the **first four bytes** are not always a distinct `SAV` type code—PyKotor treats many `.sav` files as the `MOD` / `V1.0` header pair for typing purposes ([`ERFType.from_extension`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L128-L135)). `ERF` (and `SAV` when present) are still valid Aurora signatures when they appear.

### MOD Files (module containers)

MOD files package all resources needed for a game module (level/area):

**Typical Contents:**

- Area layouts (`.are`, `.git`)
- Module information (`.ifo`)
- Dialogs and scripts (`.dlg`, `.ncs`)
- Module-specific [2DA](2DA-File-Format) overrides
- Character templates (`.utc`, `.utp`, `.utd`)
- Waypoints and triggers (`.utw`, `.utt`)

The game loads MOD files from the `modules/` directory. When entering a module, the engine mounts the MOD container and prioritizes its resources over [BIF files](Container-Formats#bif) but below the `override/` folder.

### SAV Files (save game containers)

SAV files store complete game state:

**Contents:**

- Party member data (inventory, stats, equipped items)
- Module state (spawned creatures, opened containers)
- Global variables and plot flags
- Area layouts with modifications
- Quick bar configurations
- Portrait images

Save files preserve the state of all modified resources. When a placeable is looted or a door opened, the updated `.git` resource is stored in the SAV file.

### RIM files (resource image)

`.rim` files are **not** ERF binaries: they use a **120-byte** header and **32-byte** resource records. Compare:

- [RIM File Format](Container-Formats#rim)
- [RIM versus ERF](#rim-versus-erf)

They are the usual shipped module capsules under `modules/`; [MOD](Container-Formats#mod-files-module-containers) overrides the same module when both exist.

### ERF Files (Generic Containers)

Generic ERF files serve miscellaneous purposes:

- [texture](Texture-Formats#tpc) packs
- Audio replacement packs
- Campaign-specific resources
- Developer test containers

reone's `ErfReader::checkSignature` shows the usual practical acceptance rule used by tooling: treat `ERF V1.0` and `MOD V1.0` as the expected shipped signatures once the stream is open, then dispatch the rest of the parse from the shared container layout ([`erfreader.cpp` L42-L52](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/erfreader.cpp#L42-L52)).

---

## Engine Internal Behavior

Reverse engineering of the game engine (specifically `CExoKeyTable::AddEncapsulatedContents` at `0x0040f3c0` in `swkotor.exe`) reveals how the engine actually parses these files.

### Critical vs. Metadata Fields

The engine's resource manager is surprisingly strict, reading the 160-byte header but **ignoring** most fields. It only validates/uses:

- **file type** and **Version** (Verified against expected values)
- **Entry Count** (Used to allocate memory for the key table)
- **offset to [KEY](Container-Formats#key) List** (Used to seek to the key data)

The following fields are **parsed but ignored** by the resource manager (though they may be used by the UI/Menus):

- `Language count` and `Localized string size`
- `offset to Localized string List`
- `Build Year` and `Build Day`
- `Description [StrRef](Audio-and-Localization-Formats#string-references-strref)`

### Save Game Detection

Contrary to popular belief, the engine does **not** identify Save Games based on the file type signature (`SAV` vs `ERF`) or the `Description StrRef` being `0`.

- **Mechanism**: The engine distinguishes save games based on **file context** (loading from the `saves/` directory) and the resource system usage (aliasing `SAVES:` path).
- **Implication**: Setting `Description StrRef` to `0` in a `MOD` file does *not* make it a save file. Legitimate modules (e.g., `unk_m41` series) use `0` as their StrRef.

### TSL Specific Quirks

- **LIPS MODs**: In *Knights of the Old Republic II: The Sith Lords*, MOD files related to lip-syncing (`lips_*.mod`) consistently use `0xCDCDCDCD` for the `Description StrRef`. This value (`-842150451`) is a common "uninitialized memory" fill pattern in Microsoft C++ debug runtimes, suggesting these files were built with a debug version of the toolset.

---

## Cross-reference: implementations

| Component | PyKotor (line anchors) |
| --------- | ------------------------ |
| Layout / types (docstring) | [`erf_data.py` L19–L54](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L19-L54) |
| `ERFType` | [`erf_data.py` L107–L137](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L107-L137) |
| `ERF` archive | [`erf_data.py` L140–L253](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L140-L253) |
| Binary read | [`ERFBinaryReader.load` L51–L169](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L51-L169) |
| Binary write | [`ERFBinaryWriter.write` L186–L256](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L186-L256) |

See also **Cross-reference** at the [top of this page](#file-structure-overview) for KotOR.js, Kotor.NET, reone, and xoreos.

### See also

- [Concepts](Concepts#language-ids-kotor) - Language ID enum and encodings (ERF localized strings, TLK, GFF)
- [BIF File Format](Container-Formats#bif) - Container format used with [KEY](Container-Formats#key) files
- [KEY File Format](Container-Formats#key) - Index for [BIF containers](Container-Formats#bif) and resource resolution
- [GFF File Format](GFF-File-Format) - Common content type stored in ERF containers
- [RIM File Format](Container-Formats#rim) — Resource image containers (distinct binary layout
- [comparison](Container-Formats#rim-versus-erf))

---


---

<a id="rim"></a>

# RIM — Resource Image

RIM is the lightweight module archive shipped with the base game. Like [ERF](Container-Formats#erf), each entry carries a ResRef and type, but the binary layout is intentionally simpler: no localized-string list, no compression, just a flat resource table and contiguous data. The engine loads RIM files from `modules/` and treats them identically to ERF during [resource resolution](Concepts#resource-resolution-order) — a `.mod` in the same directory shadows the corresponding `.rim` pair when present. Typical capsule contents include:

- [GFF](GFF-File-Format)
- [2DA](2DA-File-Format)
- [TPC](Texture-Formats#tpc)
- [NCS](NCS-File-Format)
- Models and walkmeshes
- Other game resources packed in module archives

## Table of contents

- [Role in the game and modding](#role-in-the-game-and-modding)
- [File structure overview](#file-structure-overview)
- [Binary format](#binary-format)
  - [File header](#file-header)
  - [Resource entries](#resource-entries)
  - [Resource data and padding](#resource-data-and-padding)
- [Module file sets (rim, _s, dlg)](#module-file-sets-rim-_s-dlg)
- [Relationship to ERF and MOD](#relationship-to-erf-and-mod)
- [Cross-reference: implementations](#cross-reference-implementations)

---

## Role in the game and modding

Vanilla modules are usually split across one or more `.rim` files (for example a main archive and a `_s` supplementary archive). The engine resolves resources using the same high-level rules as for MOD/ERF: module-scoped containers participate in the pipeline described in [resource resolution order](Concepts#resource-resolution-order). A `module_name.mod` file in `modules/` typically **shadows** the corresponding `.rim` pair when present. For MOD versus RIM priority and practical editing notes, see:

- [Concepts](Concepts#mod-erf-rim)
- [Holocron Toolset module resources](Holocron-Toolset-Module-Resources)

RIM is appropriate to read and edit when you are working directly with shipped module archives or building tools that must round-trip vanilla layout. Many modders ship changes as `.mod` ([ERF](Container-Formats#erf) variant) instead so the game loads a single encapsulated file without replacing base RIMs.

---

## File structure overview

A RIM file is a **self-contained** archive: each stored resource has a [ResRef](Concepts#resref-resource-reference), a **resource type** id, and raw **payload bytes**. There is **no** separate [KEY](Container-Formats#key) file and **no** localized description block like ERF's optional string list.

At a high level:

1. Fixed **120-byte** header (`RIM` + `V1.0` + counts and offsets).
2. **Resource table**: one **32-byte** record per resource (ResRef, type, index, offset, size).
3. **Resource blobs** concatenated after the table, with alignment and trailing padding as used by vanilla-style writers.

Unlike [ERF](Container-Formats#erf), RIM does **not** split “key” and “resource list” into two parallel arrays of different record sizes: **offset and size live in the same 32-byte entry** as the name and type.

---

## Binary format

Offsets are from the **start of the file** unless noted.

### File header

The header is **120 bytes**.

| Name | Type | Offset | Size | Description |
| ---- | ---- | ------ | ---- | ----------- |
| File type | char[4] | 0 | 4 | Always `RIM` (space-padded fourCC). |
| File version | char[4] | 4 | 4 | Always `V1.0`. |
| Unknown | UInt32 | 8 | 4 | Observed as `0` in vanilla-style files; treat as reserved. |
| Entry count | UInt32 | 12 | 4 | Number of resources in the archive. |
| Offset to resource table | UInt32 | 16 | 4 | Byte offset to the first resource entry. If **0**, tools treat this as **120** (table immediately after the header). |
| Offset to resources / reserved | UInt32 | 20 | 4 | PyKotor’s writer records **`0` here** (“implicit” layout: data follows the table and alignment padding). Older descriptions sometimes treat parts of the tail of the header as opaque padding; readers should not depend on undocumented flags without verification. |
| Reserved | byte[] | 24 | 96 | Padding (typically zeros) to complete 120 bytes. |

**Implicit offset:** If the offset at **0x10** is `0`, compliant readers assume the resource table starts at byte **120**.

### Resource entries

Each entry is **32 bytes**. Field order matches the reader in PyKotor’s `RIMBinaryReader` (ResRef, then **type**, then **id**, then offset, then size).

| Name | Type | Offset | Size | Description |
| ---- | ---- | ------ | ---- | ----------- |
| ResRef | char[16] | 0 | 16 | Resource name, null-padded to 16 bytes; not necessarily null-terminated if length is 16. |
| Resource type | UInt32 | 16 | 4 | Numeric resource type id (same family of ids as elsewhere in KotOR; see [Resource Type Identifiers](Resource-Formats-and-Resolution#resource-type-identifiers)). |
| Resource id | UInt32 | 20 | 4 | Index or slot id; vanilla writers typically use **0 .. n−1** in order. |
| Offset to data | UInt32 | 24 | 4 | File offset to the first byte of this resource’s payload. |
| Resource size | UInt32 | 28 | 4 | Length of the payload in bytes. |

**Contrast with ERF:** In [ERF](Container-Formats#erf), the parallel “key” record uses a **UInt16** resource type plus **2 bytes** padding, and **offsets/sizes** live in a **separate** 8-byte-per-entry resource list. RIM folds metadata and locating information into this single 32-byte record.

### Resource data and padding

Payloads are stored at the offsets given in the table. PyKotor’s `RIMBinaryWriter` reproduces a **vanilla-style** layout:

- After the last resource entry, the writer may insert **padding** so the start of the first blob aligns to a **16-byte** boundary.
- After each resource’s bytes, the writer appends **0–3** padding bytes so the stream is **4-byte aligned**, then writes **16** additional **zero** bytes before the next resource (including after the last resource, so the on-disk file size reflects that trailing region).

Other tools may emit slightly different padding; parsers should trust **only** the offset/size fields in the table for the extent of each resource.

---

## Module file sets (rim, _s, dlg)

A single logical module often spans **multiple** archives:

| Pattern | Typical role |
| ------- | ------------ |
| `module.rim` | Main module payload (areas, templates, scripts, textures, etc.). |
| `module_s.rim` | **S**upplementary resources for the same module (split for size or organization). |
| `module_dlg.erf` | (TSL especially) Dialog and related resources in a separate [ERF](Container-Formats#erf) capsule. |

Exact splits vary by module. Kit and extraction tooling that scans `modules/` treats `.mod` as highest priority, then `.rim` / `_s.rim`, then other ERFs; see [Kit structure documentation](Kit-Structure-Documentation).

---

## Relationship to ERF and MOD

RIM and ERF solve the same problem—**named, typed resources in one file**—but they are **not** bit-identical layouts.

| Topic | RIM | ERF / MOD / SAV |
| ----- | --- | --------------------- |
| Header Size | **120** bytes | **160** bytes |
| File type Tag | `RIM` | `ERF`, `MOD`, `SAV` |
| Localized Description Strings | **No** | Optional block (language id + CP1252 text) |
| Build year/day, Description StrRef | **No** | Present in ERF header |
| Per-resource Metadata | One **32-byte** entry (includes offset + size) | **24-byte** key + **8-byte** resource entry |
| Resource Type in Entry | **UInt32** | **UInt16** + 2 unused bytes |
| MOD “blank block” Quirk | **No** | Documented between key list and resource list for MOD/NWM in [ERF File Format](Container-Formats#erf) |

For a side-by-side narrative aimed at ERF readers, see [RIM versus ERF](Container-Formats#rim-versus-erf) on the ERF page.

**Conversion:** PyKotor exposes `RIM.to_erf()` to build an in-memory [ERF](Container-Formats#erf) with the same resources, which can then be serialized as MOD/ERF for tools that only speak the ERF layout.

---

## Cross-reference: implementations

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **PyKotor**:

  - on-disk layout (120-byte header, 32-byte keys): [`rim_data.py` module docstring L1–L45](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/rim/rim_data.py#L1-L45)
  - `RIMResource` / `RIM`: [`rim_data.py` L59–L173](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/rim/rim_data.py#L59-L173)
  - Kaitai load: [`io_rim.py` `_load_rim_from_kaitai` L22–L35](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/rim/io_rim.py#L22-L35)
  - legacy reader (implicit table offset **120**, row order **ResRef, UInt32 type, id, offset, size**): [`_load_rim_legacy` L38–L61](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/rim/io_rim.py#L38-L61)
  - [`_read_rim_entries` L64–L88](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/rim/io_rim.py#L64-L88)
  - `RIMBinaryReader.load` L120–L127
  - vanilla-style writer: [`RIMBinaryWriter.write` L142–L198](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/rim/io_rim.py#L142-L198)
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`RIMBinaryStructure.cs` `FileRoot` / `FileHeader` / `ResourceEntry` L16–L116](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorRIM/RIMBinaryStructure.cs#L16-L116) — reads the **20-byte** logical header then seeks `OffsetToResources` (vanilla **120**).
- **[reone](https://github.com/modawan/reone)** ([historical upstream / mirror: seedhartha/reone](https://github.com/modawan/reone)):

  - [`rimreader.cpp` `RimReader::load` L27–L35](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/rimreader.cpp#L27-L35)
  - [`readResource` L47–L58](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/rimreader.cpp#L47-L58) — **`UInt16` type** plus **`skipBytes(6)`**; **not** the same 32-byte KotOR row as PyKotor/Kotor.NET
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**:

  - [`RIMObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/RIMObject.ts) — uses **`UInt16` + `UInt16`** after ResRef
  - **`RIM_HEADER_LENGTH = 160`** ([L9](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/RIMObject.ts#L9))
  - **`34` bytes × row count** for `rimDataOffset` ([L84–L95](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/RIMObject.ts#L84-L95))
  - retail **KotOR** RIMs follow **120** / **32** as on this page
- **Andastra / sotor (Rust)**:

  - local parser: `vendor/sotor/core/src/formats/rim/read.rs`
  - local model/tests: `vendor/sotor/core/src/formats/rim/mod.rs`
  - notes: uses the retail KotOR `120`-byte header / `32`-byte entry layout, including the implicit `0 -> 120` resource-table offset fallback documented on this page

Community tools and installers (TSLPatcher, HoloPatcher) support inserting or patching files inside RIM capsules as well as ERF/MOD. See:

- [TSLPatcher’s official readme](TSLPatcher's-Official-Readme)
- [HoloPatcher internal logic](HoloPatcher#internal-logic)

The KotOR **RIM** container stores module resources without compression. For ERF-specific fields and engine behavior around MOD/SAV, see [ERF File Format](Container-Formats#erf).

### See also

- [ERF File Format](Container-Formats#erf) — Encapsulated resource format (MOD, SAV, generic ERF). Compare RIM layout under:

  - [RIM versus ERF](Container-Formats#rim-versus-erf)
- [Concepts](Concepts) — Resource resolution, override, MOD versus RIM priority
- [KEY File Format](Container-Formats#key) — Index format for BIF storage (contrast with self-contained RIM)
- [BIF File Format](Container-Formats#bif) — Vanilla bulk storage with KEY
- [Holocron Toolset module resources](Holocron-Toolset-Module-Resources) — Practical module/RIM editing notes


---
