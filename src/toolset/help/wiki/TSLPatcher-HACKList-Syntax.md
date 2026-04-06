# TSLPatcher HACKList Syntax Documentation

This guide explains how to modify [NCS files](NCS-File-Format) directly using TSLPatcher syntax. For the complete [NCS file](NCS-File-Format) format specification, see [NCS File Format](NCS-File-Format). For general TSLPatcher information, see [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme). For HoloPatcher-specific information, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers#hacklist-editing-ncs-directly).

## Overview

The `[HACKList]` section in TSLPatcher's `changes.ini` file enables you to modify compiled [NCS files](NCS-File-Format) (NWScript bytecode, historically called "Neverwinter Compiled Script" but used identically in **KotOR**) directly at the binary level. This advanced feature allows precise [byte](https://en.wikipedia.org/wiki/Byte)-level modifications to script files without recompiling from [NSS](NSS-File-Format) source code, making it ideal for:

In PyKotor's current implementation, HACKList is a first-class emitted section: `TSLPatcherINISerializer.serialize()` writes it explicitly via `_serialize_hack_list()` after the earlier data and structure passes, but `TSLPatchDataGenerator.generate_all_files()` does not synthesize NCS payloads the way it does TLK, 2DA, GFF, or SSF resources. In practice that means HACKList normally operates on compiled scripts that already exist in `tslpatchdata`, are copied in as install assets, or are produced by the compile-stage workflow before the binary patch pass runs [[`TSLPatcherINISerializer.serialize()`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/tslpatcher/writer.py#L222-L285), [`_serialize_hack_list`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/tslpatcher/writer.py#L1034-L1092), [`TSLPatchDataGenerator.generate_all_files()`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/tslpatcher/diff/generator.py#L93-L140), [Deadly Stream TSLPatcher page](https://deadlystream.com/files/file/1039-tsl-patcher-tlked-and-accessories/)].

- Patching numerical values in existing compiled scripts
- Injecting dynamically-generated string references ([StrRef](TLK-File-Format#string-references-strref)) and [2DA](2DA-File-Format) memory values ([2DAMEMORY](2DA-File-Format#2damemory-memory-tokens))
- Performing surgical modifications to hardcoded constants
- Updating scripts to reference new [TLK](TLK-File-Format) entries or [2DA](2DA-File-Format) row numbers/indexes

**Important:** HACKList is executed **after** [`[CompileList]`](TSLPatcher-CompileList-Syntax) during patcher execution, allowing compiled scripts to be modified after compilation if needed.

## Table of Contents

- [Overview](#overview)
- [Basic Structure](#basic-structure)
- [file-Level Configuration](#file-level-configuration)
  - [Top-Level Keys in `[HACKList]`](#top-level-keys-in-hacklist)
  - [File Section Configuration](#file-section-configuration)
- [Supported Value Syntaxes](#supported-value-syntaxes)
  - [Supported Numeric Types and Formats](#supported-numeric-types-and-formats)
  - [StrRef and 2DA Memory Reference Formats](#strref-and-2da-memory-reference-formats)
  - [Pointer/Offset Calculations](#pointeroffset-calculations)
- [Modifying Byte Sequences](#modifying-byte-sequences)
  - [Single Value Replacement](#single-value-replacement)
  - [Multi-Byte and Sequence Replacements](#multi-byte-and-sequence-replacements)
  - [Special Handling](#special-handling)
- [File and Offset Resolving](#file-and-offset-resolving)
  - [Source File Paths](#source-file-paths)
  - [Destination Overrides](#destination-overrides)
- [Usage Examples](#usage-examples)
- [Best Practices & Cautions](#best-practices--cautions)
- [Troubleshooting](#troubleshooting)
- [See Also](#see-also)

## Basic Structure

```ini
[HACKList]
!DefaultDestination=override
!DefaultSourceFolder=.  ; Note: `.` refers to the tslpatchdata folder (where changes.ini is located)
File0=myscript.ncs
Replace0=otherscript.ncs

[myscript.ncs]
!Destination=override
!SourceFile=source.ncs
!SaveAs=mypatched.ncs
ReplaceFile=0

; Byte-level modifications
0x15=12345
32=u16:2DAMEMORY1
64=u8:255
0x100=StrRef5
0x200=u32:2DAMEMORY10
```

The `[HACKList]` section declares [NCS files](NCS-File-Format) to modify. Each entry references another section with the same name as the filename.

## file-Level Configuration

### Top-Level Keys in [HACKList]

| key | type | Default | Description |
|-----|------|---------|-------------|
| `!DefaultDestination` | string | `override` | Default destination for all [NCS files](NCS-File-Format) in this section |
| `!DefaultSourceFolder` | string | `.` | Default source folder for [NCS files](NCS-File-Format). This is a relative path from `mod_path`, which is typically the `tslpatchdata` folder (the parent directory of the `changes.ini` file). The default value `.` refers to the `tslpatchdata` folder itself. Path resolution: `mod_path / !DefaultSourceFolder / filename` |

### file Section Configuration

Each [NCS file](NCS-File-Format) requires its own section (e.g., `[myscript.ncs]`).

| Key | type | Default | Description |
|-----|------|---------|-------------|
| `!Destination` | string | Inherited from `!DefaultDestination` | Where to save the modified file (`override` or `path\to\file.mod`) |
| `!SourceFolder` | string | Inherited from `!DefaultSourceFolder` | Source folder for the [NCS file](NCS-File-Format). Relative path from `mod_path` (typically the tslpatchdata folder). When `.`, refers to the tslpatchdata folder itself. |
| `!SourceFile` | string | Same as section name | Alternative source filename to load |
| `!SaveAs` or `!Filename` | string | Same as section name | Final filename to save as |
| `ReplaceFile` | 0/1 | 0 | **Note:** Unlike other patch lists, HACKList uses `ReplaceFile` (without exclamation point) |

**Destination values:**

- `override` or empty: Save to the Override folder
- `Modules\module.mod`: Insert into an [ERF](Container-Formats#erf)/MOD/[RIM](Container-Formats#rim) container
- Use backslashes for path separators

**Important:** The `ReplaceFile` key in HACKList does NOT use an exclamation point prefix. This is unique to HACKList compared to other patch lists.

## Token Types and Data Sizes Syntax

Each modification requires specifying an offset and a value. values can include type specifiers to control data size.

### Syntax

```ini
offset=value
offset=type:value
```

- **offset**: Decimal number (e.g., `32`) or hexadecimal (e.g., `0x20`)
- **type** (optional): One of `u8`, `u16`, or `u32` to specify data width
- **value**: Numeric value, token reference, or hex literal

### Supported value types

| value format | type | size | Description |
|--------------|------|------|-------------|
| Numeric (no prefix) | u16 | 2 bytes | 16-bit unsigned integer (default) |
| `u8:123` | u8 | 1 [byte](https://en.wikipedia.org/wiki/Byte) | 8-bit unsigned integer (0-255) |
| `u16:12345` | u16 | 2 bytes | 16-bit unsigned integer (0-65535) |
| `u32:123456` | u32 | 4 bytes | 32-bit unsigned integer |
| `StrRef0` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | Varies* | Reference to [TLK](Audio-and-Localization-Formats#tlk) string from memory |
| `StrRefN` | strref32 | 4 bytes | 32-bit signed [TLK](Audio-and-Localization-Formats#tlk) reference (CONSTI) |
| `2DAMEMORY1` | 2damemory | Varies* | Reference to [2DA](2DA-File-Format) memory value |
| `2DAMEMORYN` | 2damemory32 | 4 bytes | 32-bit signed [2DA](2DA-File-Format) reference (CONSTI) |

*`strref` and `2damemory` without explicit sizes default to `strref32` and `2damemory32` respectively in PyKotor's implementation.

### Endianness

All multi-[byte](https://en.wikipedia.org/wiki/Byte) values are written in **[big-endian](https://en.wikipedia.org/wiki/Endianness)** (network [byte](https://en.wikipedia.org/wiki/Byte) order), which is standard for KOTOR's binary formats.

### type Compatibility Notes

**Historical Background:** TSLPatcher originally distinguished between `strref` and `strref32` (and `2damemory` vs `2damemory32`), but PyKotor's implementation unifies these:

- `[StrRef](Audio-and-Localization-Formats#string-references-strref)#` tokens are automatically handled as 32-bit values
- `2DAMEMORY#` tokens are automatically handled as 32-bit values

If you need legacy 16-bit compatibility, use explicit type specifiers like `u16:StrRef5`, though this is not typically necessary.

## Memory Token Integration Syntax

`[HACKList]` section integrates seamlessly with TSLPatcher's memory token system, allowing dynamic value injection from other patch sections.

### [StrRef](Audio-and-Localization-Formats#string-references-strref) Tokens

Reference values stored in [`[TLKList]`](TSLPatcher-TLKList-Syntax) section memory:

```ini
; In TLKList section, this would define StrRef5
StrRef5=123456

; In HACKList, inject it into bytecode
[HACKList]
File0=myscript.ncs

[myscript.ncs]
; At offset 0x100, write the StrRef value
0x100=StrRef5
```

**Use Cases:**

- Injecting dynamically-added [dialog.tlk](Audio-and-Localization-Formats#tlk) string references
- Patching scripts to reference custom text entries
- Updating hardcoded string IDs to mod-added entries

### [2DA](2DA-File-Format) Memory Tokens ([`2DAMEMORY#`](TSLPatcher-2DAList-Syntax#2damemory-tokens))

Reference values stored in [`[2DAList]`](TSLPatcher-2DAList-Syntax) section memory tokens:

```ini
; In 2DAList section, this would store a row number
Add2DALine1=appearance.2da
[Add2DALine1]
2DAMEMORY1=RowIndex

; In HACKList, inject it into bytecode
[HACKList]
File0=myscript.ncs

[myscript.ncs]
; At offset 0x50, write the 2DA memory value
0x50=2DAMEMORY1
```

**Use Cases:**

- Injecting dynamically-added [2DA](2DA-File-Format) row numbers
- Patching appearance/spell IDs to reference new rows
- Updating hardcoded IDs to mod-added entries

**Important Limitation:** [`!FieldPath`](TSLPatcher-GFFList-Syntax#fieldpath-syntax) values are NOT supported in HACKList. Only numeric memory values can be used.

## Offset Calculation Syntax

Determining the correct [byte](https://en.wikipedia.org/wiki/Byte) offset is the most critical aspect of `[HACKList]` section usage.

### [NCS files](NCS-File-Format) structure ([`NCS` file](NCS-File-Format))

The structure of a [NCS](NCS-File-Format) file is as follows:

```ncs
Byte Offset  Description
-----------  --------------------------------------------
0x00-0x03    File signature: "NCS " (ASCII)
0x04-0x07    Version: "V1.0" (ASCII)
0x08         Magic byte: 0x42
0x09-0x0C    Total file size (4 bytes, big-endian)
0x0D+        Compiled bytecode instructions
```

The header is 13 bytes (0x0D), so the first instruction [byte](https://en.wikipedia.org/wiki/Byte) is at offset `0x0D`.

### Finding offsets with *DeNCS*

***DeNCS*** (Decompiler for [NCS](NCS-File-Format)) is a Java-based disassembler that can help you locate exact [byte](https://en.wikipedia.org/wiki/Byte) offsets in [NCS files](NCS-File-Format).

#### Using *DeNCS*

1. Load your [NCS](NCS-File-Format) file in *DeNCS*
2. Disassemble to view instruction-level operations
3. Identify the target instruction and note its [byte](https://en.wikipedia.org/wiki/Byte) offset
4. If modifying an instruction's operand, add to the instruction's offset:
   - For CONSTI operands: **offset + 1** (skip the opcode [byte](https://en.wikipedia.org/wiki/Byte))
   - For other operands: depends on instruction type

#### Example Disassembly

```plaintext
Offset  Inst                Args
------  ----                ----
0x0D    NOP
0x0E    CONSTI              10000
        (opcode at 0x0E, operand at 0x0F-0x12)
0x13    CPDOWNSP            -4
0x15    CONSTS              "Hello World"
        (opcode at 0x15, string offset at 0x16-0x19)
```

To modify the *CONSTI* value at `0x0E`, you'd patch bytes `0x0F-0x12`.

### Common Instruction Opcode Layouts

| Instruction | Opcode Size | Operand Size | Example Offset to Patch |
|-------------|-------------|--------------|-------------------------|
| `CONSTI` | 1 byte | 4 bytes | offset + 1 |
| `CONSTF` | 1 byte | 4 bytes | offset + 1 |
| `CONSTS` | 1 byte | 4 bytes | offset + 1 |
| `CPDOWNSP` | 1 byte | 4 bytes | offset + 1 |
| `ACTION` | 1 byte | 4 bytes | offset + 1 |
| `JMP` | 1 byte | 4 bytes | offset + 1 |
| `JZ` | 1 byte | 4 bytes | offset + 1 |

### Hex vs Decimal Offsets

Both formats are supported:

- **Hexadecimal**: `0x20`, `0x100`, `0xFF`
- **Decimal**: `32`, `256`, `255`

Use hexadecimal for convenience when working with [byte](https://en.wikipedia.org/wiki/Byte)-aligned operations (e.g. `0x50` is `80` in decimal).

## Examples Syntax

### Example 1: Modifying a Hardcoded Integer

Replace a hardcoded constant in a [NCS](NCS-File-Format) compiled script:

```ini
[HACKList]
File0=combat_script.ncs

[combat_script.ncs]
; At offset 0x50, change a damage value from 10 to 50
0x50=u16:50
```

### Example 2: Injecting Dynamic [TLK](Audio-and-Localization-Formats#tlk) Reference

Inject a dynamically-added [StrRef](TLK-File-Format#string-references-strref) value:

```ini
[TLKList]
StrRef1=My New Dialog Entry

[HACKList]
File0=dialog_script.ncs

[dialog_script.ncs]
; At offset 0x100, inject the StrRef value
0x100=StrRef1
```

### Example 3: Patching Multiple Values

Modify several offsets in the same file:

```ini
[HACKList]
File0=spell_script.ncs

[spell_script.ncs]
; Patch spell ID at 0x30
0x30=u16:123

; Patch damage amount at 0x50
0x50=u32:999

; Patch duration at 0x70
0x70=u16:60
```

### Example 4: Using [2DA](2DA-File-Format) Memory Values

Inject a dynamically-added [2DA](2DA-File-Format) row index:

```ini
[2DAList]
Add2DALine1=spells.2da

[Add2DALine1]
2DAMEMORY5=RowIndex

[HACKList]
File0=spell_handler.ncs

[spell_handler.ncs]
; Inject the row number at offset 0x88
0x88=2DAMEMORY5
```

### Example 5: Advanced Multi-Type Patching

Combine different data sizes and token/value types:

```ini
[HACKList]
File0=complex_script.ncs
Replace0=old_script.ncs

[complex_script.ncs]
ReplaceFile=1

; 8-bit flag value
0x20=u8:1

; 16-bit numeric literal
0x30=u16:4096

; 32-bit StrRef from memory
0x40=StrRef10

; 32-bit 2DA memory reference
0x50=2DAMEMORY3

; Direct hex value
0x60=u32:0xDEADBEEF
```

### Example 6: Saving to Container ([`!DefaultDestination`](TSLPatcher-InstallList-Syntax#defaultdestination-syntax))

Save modified scripts to a [module container](Container-Formats#erf):

```ini
[HACKList]
!DefaultDestination=Modules\mymod.mod
File0=modified_script.ncs

[modified_script.ncs]
!Destination=Modules\mymod.mod
ReplaceFile=1

; Multiple modifications
0x50=u16:100
0x60=StrRef5
```

Many vanilla scripts have hardcoded [StrRef](Audio-and-Localization-Formats#string-references-strref) values. HACKList lets you redirect them to mod-added entries:

```ini
[TLKList]
; Add your custom string
StrRef99=New Dialog Text

[HACKList]
File0=old_dialog.ncs

[old_dialog.ncs]
; Replace hardcoded StrRef 12345 with your new one
0x100=StrRef99
```

### 2. Patching Spell/Item Row IDs/Indexes

When adding new spells or items, existing scripts may need to reference them by row index or label:

```ini
[2DAList]
Add2DALine1=spells.2da

[Add2DALine1]
2DAMEMORY7=RowIndex

[HACKList]
File0=spell_handler.ncs

[spell_handler.ncs]
; Inject the new spell's row number
0x88=2DAMEMORY7
```

### 3. Adjusting Combat Values

Modify damage, duration, or other gameplay values without recompiling (e.g. `0x30=u16:50` is the damage value, `0x50=u16:60` is the duration value, `0x70=u16:10` is the cooldown value) in a [NCS](NCS-File-Format) compiled script:

```ini
[HACKList]
File0=combat_init.ncs

[combat_init.ncs]
; Change damage from 10 to 50
0x30=u16:50

; Change duration from 30 to 60 seconds
0x50=u16:60

; Change cooldown from 5 to 10 seconds
0x70=u16:10
```

### 4. Enabling Debug Flags

Some scripts have debug flags that can be enabled (e.g. `0x20=u8:1` is the debug flag):

```ini
[HACKList]
File0=debug_script.ncs

[debug_script.ncs]
; Enable debug flag (assuming it's a boolean at 0x20)
0x20=u8:1
```

### 5. Fixing Known Bugs

Patch bugs in vanilla scripts without distributing modified source:

```ini
[HACKList]
File0=buggy_script.ncs

[buggy_script.ncs]
; Fix incorrect check value
0x50=u16:1

; Fix incorrect comparison
0x70=u32:1000
```

## Troubleshooting Syntax

### Offset Calculation Errors

**Problem:** The patched value doesn't seem to take effect

**Solutions:**

1. Verify the offset using *DeNCS*
2. Check if you're modifying the correct bytes (instruction vs operand) (e.g. `CONSTI` is an opcode, `-4` is an operand)
3. Ensure you're not overwriting opcodes accidentally (e.g. `CONSTI` is an opcode, not a value, so `0x0E=u16:100` is incorrect, it should be `0x0E=u16:100`)
4. Verify big-endian [byte](https://en.wikipedia.org/wiki/Byte) order for multi-[byte](https://en.wikipedia.org/wiki/Byte) values (e.g. `u16:0x1234` is `0x12 0x34`, not `0x34 0x12`)

### Memory Token Not Defined ([`StrRefN`](TSLPatcher-TLKList-Syntax#strrefn-syntax)/[`2DAMEMORYN`](TSLPatcher-2DAList-Syntax#2damemoryn-syntax))

**Problem:** `StrRefN`/`2DAMEMORYN` was not defined before use

**Solutions:**

1. Ensure the token is defined in [`[TLKList]`](TSLPatcher-TLKList-Syntax)/[`[2DAList]`](TSLPatcher-2DAList-Syntax) **before** `[HACKList]` execution
2. Check the token number for typos (e.g. `StrRef1` instead of `StrRef10`)
3. Verify token definition syntax in the appropriate section

**Important:** `[HACKList]` executes **after** [`[CompileList]`](TSLPatcher-CompileList-Syntax) and **after** [`[TLKList]`](TSLPatcher-TLKList-Syntax) and [`[2DAList]`](TSLPatcher-2DAList-Syntax) in HoloPatcher, so memory tokens should be available.

### Wrong Data Size

**Problem:** Script crashes or behaves unexpectedly after patching

**Solutions:**

1. Verify you're using the correct data size (`u8`/`u16`/`u32`/`StrRefN`/`2DAMEMORYN`)
2. Check *DeNCS* output to confirm the operand size
3. Ensure you're not truncating large values with `u8`/`u16`
4. Verify signed vs unsigned behavior for large values (e.g. `u32:0x80000000` is a negative number)

### File Not Found ([`!SourceFile`](TSLPatcher-InstallList-Syntax#sourcefile-syntax))

**Problem:** `File not found` error during patching

**Solutions:**

1. Verify [`!SourceFile`](TSLPatcher-InstallList-Syntax#sourcefile-syntax) points to the correct filename (e.g. `source.ncs`)
2. Check [`!DefaultSourceFolder`](TSLPatcher-InstallList-Syntax#defaultsourcefolder-syntax) and [`!SourceFolder`](TSLPatcher-InstallList-Syntax#sourcefolder-syntax) paths (e.g. `tslpatchdata\source.ncs`)
3. Ensure the source file exists in the tslpatchdata folder (e.g. `tslpatchdata\source.ncs`)
4. Verify the file extension is `.ncs`

### Archival Insertion Issues ([`!Destination`](TSLPatcher-InstallList-Syntax#destination-syntax))

**Problem:** Modified script not appearing in [ERF](Container-Formats#erf)/MOD/[RIM](Container-Formats#rim) container

**Solutions:**

1. Verify [`!Destination`](TSLPatcher-InstallList-Syntax#destination-syntax) path uses backslashes
2. Check the bioware container exists before insertion (e.g. `Modules\mymod.mod`)
3. Ensure the destination folder structure is correct
4. Verify the [`ReplaceFile`](TSLPatcher-InstallList-Syntax#replacefile-syntax) setting (`0` = skip if exists, `1` = overwrite) (`0` = skip if the file exists, `1` = overwrite the existing file)

## Technical Details

### Execution Order

**HoloPatcher** processes patch lists in this order:

1. [`[InstallList]`](TSLPatcher-InstallList-Syntax) (install files)
2. [`[TLKList]`](TSLPatcher-TLKList-Syntax) (add [TLK](TLK-File-Format) text or sound entries or create [StrRef](TLK-File-Format#string-references-strref) memory tokens)
3. [`[2DAList]`](TSLPatcher-2DAList-Syntax) (modify [2DA](2DA-File-Format) files or create [2DAMEMORY](2DA-File-Format#2damemory-memory-tokens) memory tokens)
4. [`[GFFList]`](TSLPatcher-GFFList-Syntax) (modify [GFF](GFF-File-Format) files or create [2DAMEMORY](2DA-File-Format#2damemory-memory-tokens) memory tokens from [`!FieldPath`](TSLPatcher-GFFList-Syntax#fieldpath-syntax))
5. [`[CompileList]`](TSLPatcher-CompileList-Syntax) (compile [NSS](NSS-File-Format) to [NCS](NCS-File-Format))
6. [`[HACKList]`](TSLPatcher-HACKList-Syntax) (modify [NCS](NCS-File-Format) bytecode) ← **You are here**
7. [`[SSFList]`](TSLPatcher-SSFList-Syntax) (modify soundset files)

**Important:** This differs from TSLPatcher's original order, where [`[HACKList]`](TSLPatcher-HACKList-Syntax) executes before [`[CompileList]`](TSLPatcher-CompileList-Syntax). HoloPatcher runs [`[CompileList]`](TSLPatcher-CompileList-Syntax) first to allow scripts to be compiled and then potentially edited. This order change is intentional and should not affect mod compatibility in practice.

All memory tokens from [`[TLKList]`](TSLPatcher-TLKList-Syntax) and [`[2DAList]`](TSLPatcher-2DAList-Syntax) are available during [`[HACKList]`](TSLPatcher-HACKList-Syntax) processing.

### Byte-Level Writing

All multi-[byte](https://en.wikipedia.org/wiki/Byte) values are written in **[big-endian](https://en.wikipedia.org/wiki/Endianness)** format:

- `u16:0x1234` writes `12 34`
- `u32:0x12345678` writes `12 34 56 78`
- Bytes are written from most significant to least significant

### `ReplaceFile` Key Behavior

Unlike other patch lists, `[HACKList]`'s [`ReplaceFile`](TSLPatcher-InstallList-Syntax#replacefile-syntax) key does **not** use an exclamation point:

```ini
; CORRECT (`[HACKList]` syntax)
ReplaceFile=1

; INCORRECT (this is for other sections)
!ReplaceFile=1
```

`ReplaceFile=0` means **"skip if file exists"**, while `ReplaceFile=1` means ***"overwrite existing file"***.

This probably came about because HACKList was created well before TSLPatcher as we know it, and the syntax was not standardized. IIRC this is only used in High Level Force Powers mod.

### Compatibility Notes

- PyKotor's [`[HACKList]`](TSLPatcher-HACKList-Syntax) implementation is compatible with TSLPatcher v1.2.10b+
- All [NCS](NCS-File-Format) versions V1.0 are supported
- Container insertion works for [ERF](Container-Formats#erf), MOD, and [RIM](Container-Formats#rim) formats
- Memory tokens from TLKList and 2DAList are fully supported
- `!FieldPath` is **not** supported (only numeric values)

### See also

- [TSLPatcher GFFList Syntax](TSLPatcher-GFFList-Syntax) - [GFF](GFF-File-Format) modifications
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) - General TSLPatcher documentation
- [DeNCS Documentation](http://nwvault.ign.com/View.php?view=Other.Detail&id=416) - [NCS](NCS-File-Format) disassembler
- [NCS Instruction Reference](https://nwn.wiki/compiler/instructions) - Detailed bytecode documentation
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, LucasForums for [`[HACKList]`](TSLPatcher-HACKList-Syntax)/binary patching

## Advanced Topics

### Offset Alignment

When working with [NCS](NCS-File-Format) [bytecode](https://en.wikipedia.org/wiki/Bytecode), be aware of alignment requirements:

- Instructions start on any [byte](https://en.wikipedia.org/wiki/Byte) boundary (no alignment enforced)
- Operands follow immediately after opcodes
- Multi-[byte](https://en.wikipedia.org/wiki/Byte) values are written as-is without padding

### *Inserting* vs *Modifying*

**Important:** `[HACKList]` can only **modify existing bytes**. It cannot:

- Insert new bytes (files would shift offsets)
- Delete bytes (files would shrink)
- Resize instruction arrays

It can *only* overwrite existing bytes.

For structural changes, use [`[CompileList]`](TSLPatcher-CompileList-Syntax) to recompile from [NSS](NSS-File-Format) source.

### Debugging Tips

Enable verbose logging to see `[HACKList]` operations:

```ini
[Settings]
LogLevel=4
```

This will show detailed output like:

```shell
Loading `[HACKList]` patches from ini...
`[HACKList]` myscript.ncs: seeking to offset 0x20
`[HACKList]` myscript.ncs: writing unsigned WORD (16-bit) 12345 at offset 0x20
```

## Conclusion

`[HACKList]` provides powerful [byte](https://en.wikipedia.org/wiki/Byte)-level control over compiled [NCS](NCS-File-Format) scripts, enabling surgical modifications without source code access. While it requires understanding [NCS](NCS-File-Format) bytecode structure and careful offset calculation, it's essential for advanced modding scenarios involving dynamic value injection and hardcoded constant patching.

For most modding needs, [`[CompileList]`](TSLPatcher-CompileList-Syntax) ([NSS](NSS-File-Format) source compilation) is preferred. `[HACKList]` should be reserved for cases where source code is unavailable or where [byte](https://en.wikipedia.org/wiki/Byte)-level precision is required.
