# Audio and Localization Formats

The KotOR engine handles text, voice, and character sound effects through a set of interconnected formats. **TLK** (Talk Table) files store every localized string the game displays or speaks — dialogue lines, item names, journal entries, feedback messages [[`tlk_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L1-L10)]. **SSF** (Sound Set File) files map character combat and movement sounds to TLK entries. **LIP** files drive facial animation timing to match spoken dialogue. **WAV** files provide the raw audio data. Together, these formats implement the localization and voice-over pipeline that runs from authored content through to in-game playback. xoreos-tools mirrors that workflow from the tooling side with dedicated TLK conversion utilities and an explicit language-ID/encoding matrix for Aurora/Odyssey talk tables, which makes it a useful external corroboration source for KotOR localization behavior [[Running xoreos-tools](https://wiki.xoreos.org/index.php/Running_xoreos-tools), [Tlk2xml](https://wiki.xoreos.org/index.php?title=Tlk2xml), [TLK language IDs and encodings](https://wiki.xoreos.org/index.php?title=TLK_language_IDs_and_encodings)].

## Contents

- [TLK — Talk Table](#tlk)
- [SSF — Sound Set File](#ssf)
- [LIP — Lip Sync](#lip)
- [WAV — Waveform Audio](#wav)

---

<a id="tlk"></a>

# TLK — Talk Table

The Talk Table is the game's central string database. Every piece of text the player sees — dialogue, item descriptions, journal entries, feedback messages, character names — is stored in `dialog.tlk` and accessed by a numeric index called a [StrRef](Audio-and-Localization-Formats#string-references-strref) [[`tlk_data.py` L1–L35](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L1-L35)]. This design makes localization straightforward: translating the game means replacing one file rather than hunting through thousands of individual resources. Each entry can also reference a voice-over sound file ([ResRef](Concepts#resref-resource-reference)), so the engine can play spoken audio alongside the displayed text [[`TLKEntry`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L54)]. xoreos's `tlk2xml` page is also useful here because it describes why TLK tooling cannot rely on the header alone to infer text encoding: the format family reuses language IDs differently across games, and tools often need either an explicit game target or an explicit code page [[Tlk2xml](https://wiki.xoreos.org/index.php?title=Tlk2xml), [TLK language IDs and encodings](https://wiki.xoreos.org/index.php?title=TLK_language_IDs_and_encodings)].

To modify TLK entries in a mod, use [TSLPatcher/HoloPatcher TLKList syntax](TSLPatcher-Data-Syntax#tlklist-syntax) — this appends new entries or patches existing ones without replacing the entire file, which is critical for mod compatibility. TLK entries are referenced from [GFF](GFF-File-Format) resources (especially [DLG](GFF-File-Format#dlg-dialogue) dialogue files), [2DA](2DA-File-Format) tables, and [SSF](Audio-and-Localization-Formats#ssf) sound sets.

## Table of Contents

- TLK — Talk Table
  - [File Structure Overview](#file-structure-overview)
  - [Binary Format](#binary-format)
    - [File Header](#file-header)
    - [String Data Table](#string-data-table)
    - [String Entries](#string-entries)
  - [TLKEntry Structure](#tlkentry-structure)
  - [String References (StrRef)](#string-references-strref)
    - [Custom TLK Files](#custom-tlk-files)
  - [Localization](#localization)
  - [Cross-reference: implementations](#cross-reference-implementations)

---

## File structure overview

TLK files store localized strings in a binary format. The game loads `dialog.tlk` at startup and references strings throughout the game using [StrRef](Audio-and-Localization-Formats#string-references-strref) numbers (array indices). String lookups use the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, then module/SAV, then KEY/BIF), so custom TLKs in override or in a MOD take precedence over the base game `dialog.tlk`. External tooling reflects the same constraints: xoreos's `tlk2xml` can read the classic `V3.0`/`V4.0` talk-table families and exposes game-specific switches such as `--kotor` and `--kotor2` precisely because the encoding cannot be safely autodetected from TLK content alone [[Tlk2xml](https://wiki.xoreos.org/index.php?title=Tlk2xml)].

**Implementation:** [`Libraries/PyKotor/src/pykotor/resource/formats/tlk/`](https://github.com/OpenKotOR/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/)

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **PyKotor**:

  - binary layout in module docstring: [`tlk_data.py` L1–L39](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L1-L39)
  - `TLK` / `TLKEntry`: [`tlk_data.py` L54–L282](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L54-L282)
  - [`tlk_data.py` L285–L420](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L285-L420)
  - read path (Kaitai + legacy 40-byte rows): [`io_tlk.py` `_load_tlk_from_kaitai` L32–L63](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L32-L63)
  - [`_load_tlk_legacy` L66–L120](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L66-L120)
  - [`TLKBinaryReader.load` L149–L156](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L149-L156)
  - write path: [`TLKBinaryWriter` L168–L219](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L168-L219) (`_write_file_header` L183–L192, `_write_entry` L194–L219)
- **[reone](https://github.com/modawan/reone)** ([historical upstream / mirror: seedhartha/reone](https://github.com/modawan/reone)):

  - [`tlkreader.cpp` `TlkReader::load` L34–L43](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/tlkreader.cpp#L34-L43) (8-byte `"TLK V3.0"` signature + language/count/offset)
  - [`loadStrings` L45–L71](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/tlkreader.cpp#L45-L71) (40-byte rows, **lowercases** sound ResRef)
  - flag constants L28–L32
- **[xoreos](https://github.com/xoreos/xoreos)** — [`talktable.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/talktable.cpp) (Aurora talk table shared with other Aurora titles)
- **[xoreos-tools](https://github.com/xoreos/xoreos-tools)** — [`talktable.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/aurora/talktable.cpp) (CLI / tooling)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`TLKObject.ts` `LoadFromBuffer` L51–L96](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/TLKObject.ts#L51-L96) — 20-byte header then per-entry metadata; note the last field before text is read with `readUInt32()` while the on-disk field is a **float** sound length—compare PyKotor [`struct.unpack("<f", ...)` L106](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L106).
- **[KotOR-Unity](https://github.com/reubenduncan/KotOR-Unity)**: [`TLKObject.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/TLKObject.cs).
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`TLKBinaryStructure.cs` `FileHeader` / `StringData` / `FileRoot` L16–L130](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorTLK/TLKBinaryStructure.cs#L16-L130).

### See also

- [2DA File Format](2DA-File-Format) - Game tables with name/description StrRefs
- [GFF File Format](GFF-File-Format) - Dialogue and templates that reference TLK strings
- [SSF File Format](Audio-and-Localization-Formats#ssf) - Sound sets that reference TLK entries
- [TSLPatcher TLKList Syntax](TSLPatcher-Data-Syntax#tlklist-syntax) - Modding TLK files with TSLPatcher

---

## Binary format

### File Header

The file header is 20 bytes in size:

| Name                | type    | offset | size | Description                                    |
| ------------------- | ------- | ------ | ---- | ---------------------------------------------- |
| file type           | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 4    | Always `"TLK "` (space-padded)                  |
| file Version        | [char](GFF-File-Format#gff-data-types) | 4 (0x04) | 4    | `"V3.0"` for KotOR, `"V4.0"` for Jade Empire  |
| Language ID         | [int32](GFF-File-Format#gff-data-types)   | 8 (0x08) | 4    | Language identifier (see [Concepts](Concepts#language-ids-kotor); [TLK-specific notes](#localization)) |
| string count        | [int32](GFF-File-Format#gff-data-types)   | 12 (0x0C) | 4    | Number of string entries in the file           |
| string Entries offset | [int32](GFF-File-Format#gff-data-types) | 16 (0x10) | 4    | offset to string entries array (typically 20)  |

**References:**

- [reone `TlkReader::load` L34–L43](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/tlkreader.cpp#L34-L43)
- PyKotor header parse — [`_load_tlk_legacy` L71–L75](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L71-L75)
- PyKotor Kaitai path — [`_load_tlk_from_kaitai` L35–L44](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L35-L44)
- [Kotor.NET `FileHeader` L66–L76](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorTLK/TLKBinaryStructure.cs#L66-L76)
- [KotOR.js `LoadFromBuffer` L59–L64](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/TLKObject.ts#L59-L64).

### String data table

The string data table contains metadata for each string entry. Each entry is 40 bytes:

| Name              | type      | offset | size | Description                                                      |
| ----------------- | --------- | ------ | ---- | ---------------------------------------------------------------- |
| flags             | UInt32    | 0 (0x00) | 4    | bit flags: bit 0=text present, bit 1=sound present, bit 2=sound length present |
| Sound *ResRef*      | [char](GFF-File-Format#gff-data-types)  | 4 (0x04) | 16   | Voice-over audio filename ([null-terminated](https://en.cppreference.com/w/c/string/byte), max 16 chars)        |
| Volume Variance   | UInt32    | 20 (0x14) | 4    | Unused in KotOR (always 0)                                      |
| Pitch Variance    | UInt32    | 24 (0x18) | 4    | Unused in KotOR (always 0)                                      |
| offset to string  | UInt32    | 28 (0x1C) | 4    | offset to string text (relative to string Entries offset)       |
| string size       | UInt32    | 32 (0x20) | 4    | Length of string text in bytes                                  |
| Sound Length      | float     | 36 (0x24) | 4    | Duration of voice-over audio in seconds                         |

**References:**

- [Kotor.NET `StringData` L92–L129](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorTLK/TLKBinaryStructure.cs#L92-L129)
- PyKotor row decode [`_load_tlk_legacy` L96–L112](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L96-L112)
- [reone `loadStrings` L45–L69](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/tlkreader.cpp#L45-L69)
- [KotOR.js `LoadFromBuffer` L65–L75](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/TLKObject.ts#L65-L75).

**flag bits:**

- **bit 0 (0x0001)**: Text present - string has text content
- **bit 1 (0x0002)**: Sound present - string has associated voice-over audio
- **bit 2 (0x0004)**: Sound length present - sound length field is valid

**flag Combinations:**

Common flag patterns in KotOR TLK files:

| flags | Hex | Description | Usage |
| ----- | --- | ----------- | ----- |
| `0x0001` | `0x01` | Text only | Menu options, item descriptions, non-voiced dialog |
| `0x0003` | `0x03` | Text + Sound | Voiced dialog lines (most common for party/NPC speech) |
| `0x0007` | `0x07` | Text + Sound + Length | Fully voiced with duration data (cutscenes, important dialog) |
| `0x0000` | `0x00` | Empty entry | Unused [StrRef](Audio-and-Localization-Formats#string-references-strref) slots |

The engine uses these flags to decide:

- Whether to display subtitles (Text present flag)
- Whether to play voice-over audio (Sound present flag)
- How long to wait before auto-advancing dialog (Sound length present flag)

Missing flags are treated as `false` - if Text present is not set, the string is treated as empty even if text data exists.

### String entries

String entries follow the string data table:

| Name         | type   | Description                                                      |
| ------------ | ------ | ---------------------------------------------------------------- |
| string Text  | [char](GFF-File-Format#gff-data-types)[] | [null-terminated string](https://en.cppreference.com/w/c/string/byte) data (UTF-8 or Windows-1252 encoded)     |

string text is stored at the offset specified in the string data table entry. The encoding depends on the language ID; see:

- [Concepts — Language IDs](Concepts#language-ids-kotor)
- [Localization](#localization) below

---

## TLKEntry structure

Each TLK entry contains:

**References:**

- PyKotor `TLK` / `TLKEntry` — [`tlk_data.py` L54–L420](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L54-L420)
- entry serialization — [`io_tlk.py` `_write_entry` L194–L219](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L194-L219).

| Attribute        | type   | Description                                                      |
| ---------------- | ------ | ---------------------------------------------------------------- |
| `text`           | str    | Localized text string                                            |
| `voiceover`      | *ResRef* | Voice-over audio filename ([WAV file](Audio-and-Localization-Formats#wav))                            |
| `text_present`   | bool   | Whether text content exists                                      |
| `sound_present`  | bool   | Whether voice-over audio exists                                  |
| `soundlength_present` | bool | Whether sound length is valid                                    |
| `sound_length`   | float  | Duration of voice-over audio in seconds                         |

---

## string References (StrRef)

string references (StrRef) are integer indices into the TLK file's entry array:

- **StrRef 0**: First entry in the TLK file
- **StrRef -1**: No string reference (used to indicate missing/empty strings)
- **StrRef N**: Nth entry (0-based indexing)

The game uses StrRef values throughout [GFF files](GFF-File-Format), scripts, and other resources to reference localized text. When displaying text, the game looks up the StrRef in `dialog.tlk` and displays the corresponding text.

### Custom TLK files

Mods can add custom TLK files to extend available strings:

**dialog.tlk structure:**

- Base game: `dialog.tlk` (read-only, ~50,000-100,000 entries)
- Custom content: `dialogf.tlk` or custom TLK files placed in override

**[StrRef](Audio-and-Localization-Formats#string-references-strref) Ranges:**

- `0` to `~50,000`: Base game strings (varies by language)
- `16,777,216` (`0x01000000`) and above: Custom TLK range (TSLPatcher convention)
- Negative values: Invalid/missing references

**Mod Tools Approach:**

TSLPatcher and similar tools use high [StrRef](Audio-and-Localization-Formats#string-references-strref) ranges for custom strings:

```plaintext
Base [StrRef](Audio-and-Localization-Formats#string-references-strref):   0 - 50,000 (dialog.tlk)
Custom Range:  16777216+ (custom TLK files)
```

This avoids conflicts with base game strings and allows mods to add thousands of custom text entries without overwriting existing content.

**Multiple TLK files:**

The game can load multiple TLK files:

1. `dialog.tlk` - Primary game text
2. `dialogf.tlk` - Female-specific variants (polish K1 only)

Priority: Custom TLKs --> dialogf.tlk --> `dialog.tlk`

---

## Localization

Numeric **language IDs** and typical encodings (0–8) are defined on [Concepts](Concepts#language-ids-kotor). The notes below focus on **TLK-specific** behavior.

**KotOR:** Retail builds usually install one `dialog.tlk` per language; the file header’s Language ID is often ignored at runtime and is mainly useful for tools tagging which language a TLK was built for.

**Encoding:** Western languages (IDs 0–4) normally use Windows-1252 in legacy tooling; Polish (5) uses Windows-1250. IDs 6–8 use UTF-8 in the wider Aurora spec. String payloads may still be UTF-8 or Windows-1252 depending on the tool and target game—see the string entry description above.

Windows-1252 is a single-byte encoding (256 code points) and is often loosely called "ISO-8859-1" or *cp1252*.

---

## Cross-reference: implementations

| Layer | PyKotor (`master`) |
| ----- | ------------------- |
| Layout spec (docstring) | [`tlk_data.py` L1–L39](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L1-L39) |
| `TLK` / `TLKEntry` | [`tlk_data.py` L54–L420](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L54-L420) |
| Binary read | [`io_tlk.py` L32–L156](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L32-L156) (`TLKBinaryReader` L123–L156) |
| Binary write | [`io_tlk.py` L159–L219](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L159-L219) |

**Kotor.NET:** [`TLKBinaryStructure.cs` L16–L130](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorTLK/TLKBinaryStructure.cs#L16-L130).

See **Cross-reference implementations** under [File structure overview](#file-structure-overview) for reone, xoreos, KotOR.js, and KotOR-Unity.

### See also

- [Concepts](Concepts#language-ids-kotor) -- Language IDs and encodings
- [TSLPatcher TLKList Syntax](TSLPatcher-Data-Syntax#tlklist-syntax) -- Modifying TLK via HoloPatcher/TSLPatcher
- [2DA-File-Format](2DA-File-Format)
- [GFF-File-Format](GFF-File-Format) -- StrRef consumers
- [NSS-File-Format](NSS-File-Format) -- Script strings
- [Bioware-Aurora-TalkTable](Bioware-Aurora-Core-Formats#talktable) -- Aurora talk table spec
- [Concepts](Concepts#resource-resolution-order) -- Resource resolution
- [Container-Formats#key](Container-Formats#key) -- KEY/BIF index
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, forums for TLK/StrRef modding

---


---

<a id="ssf"></a>

# SSF — Sound Set File

SSF files map 28 creature sound events — battle cries, selection acknowledgements, pain grunts, death screams — to [StrRef](Audio-and-Localization-Formats#string-references-strref) indices into [`dialog.tlk`](Audio-and-Localization-Formats#tlk). Each creature template references an SSF by ResRef, and the engine plays the associated voice-over line whenever the corresponding event fires. Slots that store `-1` (`0xFFFFFFFF`) produce no sound.

To modify SSF files in mods, see the [TSLPatcher SSFList syntax guide](TSLPatcher-GFF-Syntax#ssflist-syntax). SSF StrRefs resolve through the same [TLK](Audio-and-Localization-Formats#tlk) string table used for dialogue and UI text.

## Table of Contents

- SSF — Sound Set File
  - Table of Contents
  - [File structure overview](#file-structure-overview)
  - [Binary Format](#binary-format)
    - [File Header](#file-header)
    - [Sound Table](#sound-table)
  - [Sound event types](#sound-event-types)
  - [Cross-reference: implementations](#cross-reference-implementations)

---



## File structure overview

SSF files define **28** logical sound slots (indices `0`–`27`) that creatures use for battle cries, selection lines, grunts, UI feedback, etc. Each slot holds a [StrRef](Audio-and-Localization-Formats#string-references-strref) into [`dialog.tlk`](Audio-and-Localization-Formats#tlk) (or `-1` / `0xFFFFFFFF` for “no sound”). SSF files load through the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**On-disk size:**

- The header is **12** bytes; the **semantic** KotOR table is **28** × 4 = **112** bytes.
- Some writers emit **40** × 4 = **160** bytes after the header (28 mapped slots plus **12** extra `0xFFFFFFFF` words).
- PyKotor’s writer does this ([`io_ssf.py` L177–L181](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py#L177-L181)).
- Kotor.NET models a 40-entry table in [`SSFBinaryStructure.cs` `SoundTable` L61–L77](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorSSF/SSFBinaryStructure.cs#L61-L77).
- Readers that only consume the first 28 entries after `offset` still match vanilla behavior.
- KotOR.js [`SSFObject.Open`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/SSFObject.ts#L31-L49) derives `soundCount = (length - 12) / 4` and therefore accepts either width.

**Implementation (PyKotor):** [`Libraries/PyKotor/src/pykotor/resource/formats/ssf/`](https://github.com/OpenKotOR/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/)

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **PyKotor**:

  - format notes in module docstring: [`io_ssf.py` L1–L42](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py#L1-L42)
  - legacy load path (28 slots, order fixed): [`_load_ssf_legacy` L63–L112](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py#L63-L112)
  - reader dispatch: [`SSFBinaryReader.load` L152–L159](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py#L152-L159)
  - writer: [`SSFBinaryWriter.write` L171–L181](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py#L171-L181)
  - enum + semantics: [`SSFSound` L123–L234](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ssf/ssf_data.py#L123-L234)
- **[reone](https://github.com/modawan/reone)** — [`ssfreader.cpp` `SsfReader::load` L28–L36](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/ssfreader.cpp#L28-L36) (validates `SSF V1.1`, seeks to table offset, reads **all** remaining `int32`s into an array — works for 28- or 40-word tables).
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora SSF (`src/aurora/ssffile.cpp`), shared with other Aurora titles.
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**:

  - [`SSFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/SSFObject.ts#L31-L49)
  - slot names: [`SSFType` enum L14–L43](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/enums/resource/SSFType.ts#L14-L43) (same indices as PyKotor `SSFSound`; identifier spellings differ slightly — see table below)
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**:

  - header + 40-slot table: [`SSFBinaryStructure.cs` L29–L77](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorSSF/SSFBinaryStructure.cs#L29-L77)
  - high-level read loop (28 creature sounds): [`SSFBinaryReader.Read` L31–L45](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorSSF/SSFBinaryReader.cs#L31-L45)

### See also

- [TSLPatcher SSFList Syntax](TSLPatcher-GFF-Syntax#ssflist-syntax) - Modding SSF files with TSLPatcher
- [TLK File Format](Audio-and-Localization-Formats#tlk) - [Talk Table](Audio-and-Localization-Formats#tlk) containing actual sound references
- [Bioware Aurora SSF Format](Bioware-Aurora-Core-Formats#ssf) - Official BioWare specification
- [GFF-UTC](GFF-Creature-and-Dialogue#utc) - [creature templates](GFF-File-Format#utc-creature) that reference SSF files
- [2DA-soundset](2DA-File-Format#soundset2da) - Sound set definitions table

---

## Binary format

### File Header

The file header is 12 bytes in size:

| Name                | type    | offset | size | Description                                    |
| ------------------- | ------- | ------ | ---- | ---------------------------------------------- |
| file type           | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 4    | Always `"SSF "` (space-padded)                 |
| file Version        | [char](GFF-File-Format#gff-data-types) | 4 (0x04) | 4    | Always `"V1.1"`                                 |
| offset to Sound Table | UInt32 | 8 (0x08) | 4    | Byte offset to the first StrRef (almost always **12**)          |

### Sound Table

After the header, the file contains a contiguous array of **little-endian int32** StrRefs. **KotOR uses the first 28 entries** (indices `0`–`27`) as in the **Sound event types** table below. `-1` or `0xFFFFFFFF` means “no sound” for that slot.

Some files and tools use **40** uint32 entries (extra trailing `-1` words). Treat anything beyond index **27** as padding unless you have a specific toolchain that assigns meaning to it.

---

## Sound event types

Indices are fixed; **do not reorder**. PyKotor names are authoritative for this repo; [KotOR.js `SSFType`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/enums/resource/SSFType.ts#L14-L43) uses the same numeric values with different spellings on a few rows (noted in the third column).

| Index | PyKotor `SSFSound` | KotOR.js `SSFType` (if different) | Role |
| ----- | ------------------ | ----------------------------------- | ---- |
| 0–5 | `BATTLE_CRY_1` … `BATTLE_CRY_6` | (same) | Combat entry / battle cries |
| 6–8 | `SELECT_1` … `SELECT_3` | (same) | Creature selected |
| 9–11 | `ATTACK_GRUNT_1` … `ATTACK_GRUNT_3` | `ATTACK_1` … `ATTACK_3` | Attack animation grunts |
| 12–13 | `PAIN_GRUNT_1` … `PAIN_GRUNT_2` | `PAIN_1` … `PAIN_2` | Damage reactions |
| 14 | `LOW_HEALTH` | (same) | Low HP warning |
| 15 | `DEAD` | (same) | Death |
| 16 | `CRITICAL_HIT` | (same) | Critical hit feedback |
| 17 | `TARGET_IMMUNE` | (same) | Immune target |
| 18 | `LAY_MINE` | (same) | Place mine |
| 19 | `DISARM_MINE` | (same) | Disarm mine |
| 20 | `BEGIN_STEALTH` | `STEALTH` | Enter stealth |
| 21 | `BEGIN_SEARCH` | `SEARCH` | Search mode |
| 22 | `BEGIN_UNLOCK` | `UNLOCK` | Start unlock |
| 23 | `UNLOCK_FAILED` | `UNLOCK_FAIL` | Unlock failed |
| 24 | `UNLOCK_SUCCESS` | (same) | Unlock succeeded |
| 25 | `SEPARATED_FROM_PARTY` | `SOLO_MODE` | Left party / solo |
| 26 | `REJOINED_PARTY` | `PARTY_MODE` | Rejoined party |
| 27 | `POISONED` | (same) | Poisoned |

**Primary references:**

- [`ssf_data.py` `SSFSound` L123–L234](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ssf/ssf_data.py#L123-L234)
- [`io_ssf.py` `_load_ssf_legacy` L80–L110](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py#L80-L110)
- [KotOR.js `SSFType.ts` L14–L43](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/enums/resource/SSFType.ts#L14-L43)

---

## Cross-reference: implementations

| Component | Location |
| --------- | -------- |
| SSF data model (`SSF`) | [`ssf_data.py` `SSF` L26–L121](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ssf/ssf_data.py#L26-L121) |
| SSF data model (`SSFSound`) | [`SSFSound` L123–L234](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ssf/ssf_data.py#L123-L234) |
| Binary I/O | [`io_ssf.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py) (see [File structure overview](#file-structure-overview) for line-level anchors) |

---


---

<a id="lip"></a>

# LIP — Lip Synchronization

LIP files drive mouth animation for voiced dialogue. Each file stores a compact series of keyframes that pair a timestamp (in seconds) with a viseme index (0–15), and the engine interpolates between them while playing the companion [WAV](Audio-and-Localization-Formats#wav) voice line. The LIP `length` field must match the WAV playback duration exactly, or the mouth animation will desynchronize. LIP files load through the same [resource resolution order](Concepts#resource-resolution-order) as other game assets.

LIP is always paired with a [WAV](Audio-and-Localization-Formats#wav) of matching ResRef. Dialogue nodes in [DLG](GFF-Creature-and-Dialogue#dlg) trigger the voice line, which in turn triggers the LIP animation on the speaking creature model.

## Table of Contents

- LIP — Lip Synchronization
  - Table of Contents
  - [File Structure Overview](#file-structure-overview)
  - [Binary format](#binary-format)
    - [Header](#header)
    - [Keyframe Table](#keyframe-table)
  - [Mouth Shapes (Viseme Table)](#mouth-shapes-viseme-table)
  - [Animation Rules](#animation-rules)
  - [Cross-reference: implementations](#cross-reference-implementations)

---


## File structure overview

- LIP files are always binary (`"LIP V1.0"` signature) and contain only [animation](MDL-MDX-File-Format#animation-header) data.  
- They are paired with [WAV](Audio-and-Localization-Formats#wav) voice-over resources of identical duration; the LIP `length` field must match the [WAV](Audio-and-Localization-Formats#wav) `data` playback time for glitch-free [animation](MDL-MDX-File-Format#animation-header).  
- [keyframes](MDL-MDX-File-Format#controller-structure) are sorted chronologically and store a timestamp (float seconds) plus a 1-[byte](https://en.wikipedia.org/wiki/Byte) viseme index (0–15).  
- The layout is identical across these implementations (header / [keyframe](MDL-MDX-File-Format#controller-structure) offsets below are cross-confirmed):

  - [reone](https://github.com/modawan/reone)
  - [xoreos](https://github.com/xoreos/xoreos)
  - [Kotor.NET](https://github.com/NickHugi/Kotor.NET)
  - [KotOR.js](https://github.com/KobaltBlu/KotOR.js)
  - [mdlops](https://github.com/ndixUR/mdlops) (Perl reference implementation)  

**Implementation (PyKotor):**

- package: [`resource/formats/lip/`](https://github.com/OpenKotOR/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/lip/)
- binary read [`LIPBinaryReader.load` L95+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lip/io_lip.py#L95)
- write [`LIPBinaryWriter.write` L117+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lip/io_lip.py#L117)
- data model in `lip_data.py`
- XML/JSON in `io_lip_xml`, `io_lip_json`

Comparable LIP implementations include reone's C++ parser ([lipreader.cpp L27+](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/lipreader.cpp#L27)), xoreos's Aurora reader ([lipfile.cpp](https://github.com/xoreos/xoreos/blob/master/src/aurora/lipfile.cpp)), KotOR.js's LIP object and binary reader ([LIPObject.ts L26+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/LIPObject.ts#L26), [`readBinary` L112-L136](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/LIPObject.ts#L112-L136)), and Kotor.NET's in-memory DTO layer ([LIP.cs L11+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorLIP/LIP.cs#L11)).

### See also

- [TLK File Format](Audio-and-Localization-Formats#tlk) - [Talk Table](Audio-and-Localization-Formats#tlk) containing voice-over references
- [WAV File Format](Audio-and-Localization-Formats#wav) - Audio format paired with LIP files
- [GFF-DLG](GFF-Creature-and-Dialogue#dlg) - [dialogue files](GFF-File-Format#dlg-dialogue) that trigger LIP [animations](MDL-MDX-File-Format#animation-header)

---

## Binary format

### Header

| Name          | type    | offset | size | Description |
| ------------- | ------- | ------ | ---- | ----------- |
| file type     | [char](GFF-File-Format#gff-data-types) | 0 (0x00)   | 4    | Always `"LIP "` |
| file Version  | [char](GFF-File-Format#gff-data-types) | 4 (0x04)   | 4    | Always `"V1.0"` |
| Sound Length  | [float32](GFF-File-Format#gff-data-types) | 8 (0x08)   | 4    | Duration in seconds (must equal [WAV](Audio-and-Localization-Formats#wav) length) |
| Entry count   | UInt32  | 12 (0x0C)   | 4    | Number of [keyframes](MDL-MDX-File-Format#controller-structure) immediately following |

The LIP header layout is corroborated by reone's parser ([lipreader.cpp L27-L42](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/lipreader.cpp#L27-L42)).

### [keyframe](MDL-MDX-File-Format#controller-structure) Table

[keyframes](MDL-MDX-File-Format#controller-structure) follow immediately after the header; there is no padding.

| Name       | type    | Offset (per entry) | size | Description |
| ---------- | ------- | ------------------ | ---- | ----------- |
| Timestamp  | [float32](GFF-File-Format#gff-data-types) | 0 (0x00)               | 4    | Seconds from [animation](MDL-MDX-File-Format#animation-header) start |
| Shape      | [uint8](GFF-File-Format#gff-data-types)   | 4 (0x04)               | 1    | Viseme index (`0–15`) |

- Entries are stored sequentially and **must** be sorted ascending by timestamp.  
- Libraries average multiple implementations to validate this layout:

  - [reone](https://github.com/modawan/reone)
  - [xoreos](https://github.com/xoreos/xoreos)
  - [KotOR.js](https://github.com/KobaltBlu/KotOR.js)
  - [Kotor.NET](https://github.com/NickHugi/Kotor.NET)

KotOR.js's binary reader shows the same contiguous keyframe-table decode ([`LIPObject.ts` `readBinary` L112-L136](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/LIPObject.ts#L112-L136)).

---

## Mouth Shapes (Viseme Table)

KotOR reuses the 16-shape Preston Blair [phoneme](https://en.wikipedia.org/wiki/Phoneme) set. Every implementation agrees on the [byte](https://en.wikipedia.org/wiki/Byte) value assignments; KotOR.js only renames a few labels but the indices match.

| value | Shape | Description |
| ----- | ----- | ----------- |
| 0 | **NEUTRAL** | Rest/closed mouth |
| 1 | **EE** | Teeth apart, wide smile (long "ee") |
| 2 | **EH** | Relaxed mouth ("eh") |
| 3 | **AH** | Mouth open ("ah/aa") |
| 4 | **OH** | Rounded lips ("oh") |
| 5 | **OOH** | Pursed lips ("oo", "w") |
| 6 | **Y** | Slight smile ("y") |
| 7 | **STS** | Teeth touching ("s", "z", "ts") |
| 8 | **FV** | Lower LIP touches teeth ("f", "v") |
| 9 | **NG** | Tongue raised ("n", "ng") |
| 10 | **TH** | Tongue between teeth ("th") |
| 11 | **MPB** | Lips closed ("m", "p", "b") |
| 12 | **TD** | Tongue up ("t", "d") |
| 13 | **SH** | Rounded relaxed ("sh", "ch", "j") |
| 14 | **L** | Tongue forward ("l", "r") |
| 15 | **KG** | Back of tongue raised ("k", "g", "h") |

PyKotor's [`LIPShape` table and related phoneme helpers](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py#L50-L169) define the same core viseme set used throughout the surrounding LIP tooling ecosystem.

---

## [animation](MDL-MDX-File-Format#animation-header) Rules

- **[Interpolation](https://en.wikipedia.org/wiki/Interpolation):** The engine interpolates between consecutive [keyframes](https://en.wikipedia.org/wiki/Key_frame), and PyKotor's [`LIP.get_shapes()`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py#L342-L385) computes the left and right [visemes](https://en.wikipedia.org/wiki/Viseme) plus blend factor from that timeline.
- **Sorting:** When adding frames, PyKotor [removes existing entries at the same timestamp and keeps the list sorted](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py#L305-L323).
- **Duration Alignment:** PyKotor updates [`LIP.length` to the maximum timestamp](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py#L267-L323) so exported [animations](MDL-MDX-File-Format#animation-header) stay aligned with their [WAV](Audio-and-Localization-Formats#wav) line.
- **Generation:** Automated pipelines (MDLOps, KotORBlender) map phonemes to visemes via `LIPShape.from_phoneme()`, and the same mapping table appears in the vendor projects referenced above to keep authoring tools consistent.  

---

PyKotor's LIP reader and data model ([io_lip.py](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lip/io_lip.py), [lip_data.py](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py)) stay aligned with the same header and keyframe encoding used by reone ([lipreader.cpp L27+](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/graphics/format/lipreader.cpp#L27)), xoreos ([lipfile.cpp](https://github.com/xoreos/xoreos/blob/master/src/aurora/lipfile.cpp)), KotOR.js ([LIPObject.ts L26+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/LIPObject.ts#L26)), and Kotor.NET ([LIP.cs L11+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorLIP/LIP.cs#L11)).


---

<a id="wav"></a>

# KotOR WAV file format Documentation

KotOR stores both standard WAV voice-over lines and Bioware-obfuscated sound-effect files. Voice-over assets are regular RIFF containers with PCM headers, while SFX assets prepend a 470-[byte](https://en.wikipedia.org/wiki/Byte) custom block before the RIFF data. PyKotor handles both variants transparently. WAV files are resolved using the same [resource resolution order](Concepts#resource-resolution-order) as other resources:

- [override](Concepts#override-folder)
- [MOD/ERF/SAV](Container-Formats#erf)
- [KEY/BIF](Container-Formats#key)

Hex type id **`0x0004`** is listed under [Resource type identifiers](Resource-Formats-and-Resolution#resource-type-identifiers).

**Implementation (PyKotor)**

- **Binary reader/writer:**

  - [`io_wav.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/wav/io_wav.py)
  - [`WAVBinaryReader` L100+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/wav/io_wav.py#L100)
  - [`load` L148+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/wav/io_wav.py#L148) (SFX obfuscation + RIFF)
  - [`WAVBinaryWriter` L302+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/wav/io_wav.py#L302)
  - RIFF parse helper [`_parse_riff_wave_from_kaitai` L56+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/wav/io_wav.py#L56)
- **Data model:** [`wav_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/wav/wav_data.py).

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **[reone](https://github.com/modawan/reone)** ([historical upstream / mirror: seedhartha/reone](https://github.com/modawan/reone)) — [`wavreader.cpp` — `WavReader::load` L32+](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/audio/format/wavreader.cpp#L32) (470-byte SFX signature `FF F3 60 C4` then seek `0x1DA`, RIFF/`fmt`/`data`, MP3-in-WAV edge case).
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** — [`AudioFile.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/audio/AudioFile.ts) — SFX probe [`fakeHeaderTest` / `riffHeaderTest` L12-L13](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/audio/AudioFile.ts#L12-L13), strip 470-byte prefix [`processFile` L118-L124](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/audio/AudioFile.ts#L118-L124), MP3-in-WAV `riffSize == 50` branch [L131-L137](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/audio/AudioFile.ts#L131-L137).
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — no dedicated `KotorWAV` reader on the default branch; creature sound **StrRefs** (resolved to `.wav` via [TLK](Audio-and-Localization-Formats#tlk) at runtime) are modeled in [`Kotor.NET/Formats/KotorSSF/SSF.cs` L12+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorSSF/SSF.cs#L12). For byte-level RIFF/SFX layout, prefer the implementations above:

  - PyKotor (`io_wav.py` in this section)
  - [reone](https://github.com/modawan/reone)
  - [KotOR.js](https://github.com/KobaltBlu/KotOR.js)

**For mod developers:** WAV files are referenced from:

- [TLK](Audio-and-Localization-Formats#tlk) (voice-over)
- [SSF](Audio-and-Localization-Formats#ssf)

See [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers).

**Related formats:**

- [TLK](Audio-and-Localization-Formats#tlk) (StrRef → sound)
- [SSF](Audio-and-Localization-Formats#ssf)
- [LIP](Audio-and-Localization-Formats#lip)
- [DLG](GFF-Creature-and-Dialogue#dlg) (`VO_ResRef`)

## Table of Contents

- WAV — Audio
  - Table of Contents
  - File Types
  - [Standard RIFF/WAVE Structure](#standard-riffwave-structure)
    - [Format Chunk](#format-chunk)
    - [Data Chunk](#data-chunk)
  - [KotOR SFX Header](#kotor-sfx-header)
  - [Encoding Details](#encoding-details)
  - [Cross-reference: implementations](#cross-reference-implementations)

---

## File types

| type | Usage | Description |
| ---- | ----- | ----------- |
| **VO (Voice-over)** | Dialogue lines (`*.wav` referenced by [TLK](Audio-and-Localization-Formats#tlk) [StrRefs](Audio-and-Localization-Formats#string-references-strref)). | Plain RIFF/WAVE PCM files readable by any media player. |
| **SFX (Sound effects)** | Combat, UI, ambience, `.wav` files under `StreamSounds`/`SFX`. | Contains a Bioware 470-[byte](https://en.wikipedia.org/wiki/Byte) obfuscation header followed by the same RIFF data. |

PyKotor exposes these via the `WAVType` enum (`VO` vs. `SFX`) so tools know whether to insert/remove the proprietary header (`io_wav.py:52-121`).

---

## Standard RIFF/WAVE structure

KotOR sticks to the canonical RIFF chunk order:

| offset | field | Description |
| ------ | ----- | ----------- |
| 0 (0x00) | `"RIFF"` | Chunk ID |
| 4 (0x04) | `<uint32>` | file size minus 8 |
| 8 (0x08) | `"WAVE"` | format tag |
| 12 (0x0C) | `"fmt "` | format chunk ID |
| 16 (0x10) | `<uint32>` | format chunk size (usually 0x10) |
| … | See below | |

### Format chunk

| Field | Type | Description |
| ----- | ---- | ----------- |
| `audio_format` | uint16 | `0x0001` for PCM, `0x0011` for IMA ADPCM. |
| `channels` | uint16 | 1 (mono) or 2 (stereo). |
| `sample_rate` | uint32 | Typically 22050 Hz (SFX) or 44100 Hz (VO). |
| `bytes_per_sec` | uint32 | `sample_rate × block_align`. |
| `block_align` | uint16 | Bytes per sample frame. |
| `bits_per_sample` | uint16 | 8 or 16 for PCM. |
| `extra_bytes` | … | Present only when `fmt_size > 0x10` (e.g., ADPCM coefficients). |

### Data chunk

After the `fmt` chunk (and any optional `fact` chunk), the `"data"` chunk begins:

| field | Description |
| ----- | ----------- |
| `"data"` | Chunk ID. |
| `<uint32>` | Number of bytes of raw audio. |
| `<byte[]>` | PCM/ADPCM sample data. |

KotOR voice-over WAVs add a `"fact"` chunk with a 32-bit sample count, which PyKotor writes for compatibility (`io_wav.py:182-186`).

---

## KotOR SFX header

- SFX assets start with 470 bytes of obfuscated metadata (magic numbers plus filler `0x55`).  
- After this header, the file resumes at the `"RIFF"` signature described above.  
- When exporting SFX, PyKotor recreates the header verbatim so the game recognizes the asset (`io_wav.py:150-163`).  

*(See **Cross-reference implementations** above for reone / KotOR.js / Kotor.NET line anchors.)*

---

## Encoding Details

- **PCM (`audio_format = 0x0001`)**: Most dialogue is 16-bit mono PCM, which streams directly through the engine mixer.  
- **IMA ADPCM (`audio_format = 0x0011`)**: Some ambient SFX use compressed ADPCM frames; when present, the `fmt` chunk includes the extra coefficient block defined by the WAV spec.  
- KotOR requires `block_align` and `bytes_per_sec` to match the values implied by the codec; mismatched headers can crash the in-engine decoder.  

External tooling such as SithCodec and `SWKotOR-Audio-Encoder` implement the same formats; PyKotor simply exposes the metadata so conversions stay lossless.

### Community context (workflow)

- Deadly Stream — [SithCodec](https://deadlystream.com/files/file/1716-sithcodec/) (Windows tool for KotOR audio header strip/add; pair with PyKotor `io_wav` when verifying bytes).
- Deadly Stream — [Extracting dialogue](https://deadlystream.com/topic/9437-extracting-dialogue/) — **community-reported** layout notes (e.g. some assets under `StreamWaves` / `StreamVoice`); treat thread as **workflow hints**, not normative RIFF layout—verify against **PyKotor** / **reone** / **KotOR.js** above.

### Historical context (LucasForums Archive)

TSLPatcher-era threads discuss **Streamsounds** / **Streamwaves** paths, codec issues in Miles-based workflows, and DLG-related **`StreamVoice`** layout (e.g. `alienvo.2da` → `StreamVoice\AVO\`). Treat these as **dated player/modder reports**, not engine specifications—pair with **SithCodec**, **PyKotor `io_wav`**, and the cross-refs at the top of this page.

- [Convert KOTOR sounds to a usable audio file](https://www.lucasforumsarchive.com/thread/208881-convert-kotor-sounds-to-a-usable-audio-file)
- [Editing KotOR voiceover files — which program?](https://www.lucasforumsarchive.com/thread/208744-editing-kotor-voiceover-files-program)
- [Listening and editing KotOR I & II audio](https://www.lucasforumsarchive.com/thread/174967-listening-and-editing-kotor-i-amp-ii-audio)
- [KotOR/TSL GUI Dialog Editor (DLGEditor) — `StreamVoice` / `alienvo` discussion (e.g. p.2)](https://www.lucasforumsarchive.com/thread/135639-kotortsl-gui-dialog-editor-dlgeditor-current-version-232/page/2)

---

## Cross-reference: implementations

- **Reference implementations (engines):** same as **Cross-reference implementations** at the top of this page (PyKotor `io_wav.py`, reone `wavreader.cpp`, KotOR.js `AudioFile.ts`).
- **Community tooling (not normative):** **[SithCodec](https://github.com/BBBrassil/SithCodec)** — encode/decode helper; **[SWKotOR-Audio-Encoder](https://github.com/LoranRendel/SWKotOR-Audio-Encoder)** — batch-friendly encoder. Prefer verifying headers against **PyKotor** / **reone** / **KotOR.js** when debugging engine mismatches.

With this structure, WAV assets authored in PyKotor will play identically in the base game and in the other vendor tools.

### See also

- [Resource formats and resolution](Resource-Formats-and-Resolution) - [Resource type identifiers](Resource-Formats-and-Resolution#resource-type-identifiers) (`WAV` / `0x0004`)
- [TLK File Format](Audio-and-Localization-Formats#tlk) - Talk table that references WAV voice-over
- [SSF File Format](Audio-and-Localization-Formats#ssf) - Sound set files that reference WAV via StrRef
- [LIP File Format](Audio-and-Localization-Formats#lip) - Lip-sync paired with WAV dialogue
- [GFF-DLG](GFF-Creature-and-Dialogue#dlg) - Dialogue files that reference WAV (VO_ResRef)

---


---
