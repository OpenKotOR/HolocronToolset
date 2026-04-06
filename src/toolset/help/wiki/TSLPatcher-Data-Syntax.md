# TSLPatcher Data Syntax

TSLPatcher's data-oriented sections are now documented on dedicated pages so each syntax family can be maintained independently. Use this page as the stable entry point for links that refer to `[2DAList]` and `[TLKList]` syntax.

In PyKotor's current tooling pipeline, these are not abstract labels. `TSLPatcherINISerializer.serialize()` emits `changes.ini` in canonical section order beginning with `[TLKList]`, then `[InstallList]`, `[2DAList]`, `[GFFList]`, `[SSFList]`, and `[HACKList]`, while `TSLPatchDataGenerator.generate_all_files()` stages the companion files in `tslpatchdata` such as `append.tlk` and the source assets that later sections patch or install [[`TSLPatcherINISerializer.serialize()`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/tslpatcher/writer.py#L222-L285), [`_serialize_tlk_list`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/tslpatcher/writer.py#L878-L953), [`_serialize_2da_list`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/tslpatcher/writer.py#L339-L557), [`TSLPatchDataGenerator.generate_all_files()`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/tslpatcher/diff/generator.py#L93-L140), [`_generate_tlk_files`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/tslpatcher/diff/generator.py#L301-L350), [`_generate_2da_files`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/tslpatcher/diff/generator.py#L352-L404)].

That matches the historical design goal described by stoffe's original documentation: TLK and 2DA passes exist first so later stages can consume dynamically-assigned `StrRef#` and `2DAMEMORY#` values instead of forcing hardcoded row numbers or talk-table indices [[Deadly Stream TSLPatcher page](https://deadlystream.com/files/file/1039-tsl-patcher-tlked-and-accessories/)].

## Contents

- [2DAList Syntax](#2dalist-syntax)
- [TLKList Syntax](#tlklist-syntax)

## When to use this page

Use this hub when you need to decide whether a change belongs in `[2DAList]` or `[TLKList]`, or when an older wiki link brought you here. For exact directives, examples, processing notes, and token usage, follow the dedicated guides below.

If your mod needs to create data that other sections will later reference, start here first. `[TLKList]` is the normal source of dynamic `StrRef#` tokens, and `[2DAList]` is the normal source of dynamic `2DAMEMORY#` values that later flow into [GFF](GFF-File-Format), [SSF](Audio-and-Localization-Formats#ssf), and [NCS](NCS-File-Format) patches [[Deadly Stream TSLPatcher page](https://deadlystream.com/files/file/1039-tsl-patcher-tlked-and-accessories/), [TSLPatcher GFFList Syntax](TSLPatcher-GFFList-Syntax), [TSLPatcher HACKList Syntax](TSLPatcher-HACKList-Syntax)].

<a id="2dalist-syntax"></a>

## 2DAList Syntax

Use `[2DAList]` when a mod needs to merge changes into a [2DA](2DA-File-Format) table instead of replacing the whole file. The standalone guide covers row targeting, `ChangeRow`, `AddRow`, `CopyRow`, `AddColumn`, `2DAMEMORY` tokens, processing order, and troubleshooting.

Canonical page:

- [TSLPatcher 2DAList Syntax](TSLPatcher-2DAList-Syntax)

Typical uses:

- appending rows to `appearance.2da`, `spells.2da`, or similar tables
- storing row indices in `2DAMEMORY#` for later [GFF](GFF-File-Format), [SSF](Audio-and-Localization-Formats#ssf), or [NCS](NCS-File-Format) patches
- merging per-mod table edits without shipping whole-file overrides

<a id="tlklist-syntax"></a>

## TLKList Syntax

Use `[TLKList]` when a mod needs to append or patch [TLK](Audio-and-Localization-Formats#tlk) string entries. The standalone guide covers `StrRef#` creation, replacement behavior, processing order, and how those string references flow into later sections such as `[2DAList]`, `[GFFList]`, and `[SSFList]`.

Canonical page:

- [TSLPatcher TLKList Syntax](TSLPatcher-TLKList-Syntax)

Typical uses:

- adding new dialogue or item text to `dialog.tlk`
- creating `StrRef#` tokens for later use in [2DA](2DA-File-Format) and [GFF](GFF-File-Format) edits
- updating localized text without replacing the entire talk table

## Related sections

- [TSLPatcher GFFList Syntax](TSLPatcher-GFFList-Syntax)
- [TSLPatcher SSFList Syntax](TSLPatcher-SSFList-Syntax)
- [TSLPatcher InstallList Syntax](TSLPatcher-InstallList-Syntax)
- [TSLPatcher HACKList Syntax](TSLPatcher-HACKList-Syntax)
- [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers)
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme)
