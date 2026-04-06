# HoloPatcher

HoloPatcher is the cross-platform replacement for the Windows-only TSLPatcher installer, developed as part of [PyKotor](https://github.com/OpenKotOR/PyKotor/tree/master/Tools/HoloPatcher/src/holopatcher). It reads the standard `tslpatchdata` layout and applies merge-aware patching for [GFF](GFF-File-Format), [2DA](2DA-File-Format), [TLK](Audio-and-Localization-Formats#tlk), [SSF](Audio-and-Localization-Formats#ssf), and [NCS](NCS-File-Format) on Windows, macOS, and Linux.

Use this page as the entry point for HoloPatcher documentation. Detailed usage, authoring guidance, and implementation notes now live on dedicated pages so they can be maintained without duplication.

## Contents

- [HoloPatcher](#holopatcher)
  - [Contents](#contents)
  - [For mod users](#for-mod-users)
  - [For mod developers](#for-mod-developers)
  - [Internal architecture](#internal-architecture)
  - [Related syntax references](#related-syntax-references)
  - [Community adoption](#community-adoption)
    - [See also](#see-also)

<a id="installing-mods"></a>

## For mod users

If you are installing a mod, start with [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher). That page covers the player workflow: choosing the correct game root, handling namespace options, restoring backups before retries, and using the iOS case-sensitivity utility when mobile installs need it.

Use HoloPatcher against the game root, not the `override` folder by itself. If a mod offers multiple install options, restore the previous backup before switching variants or reinstalling the same option. For general conflict background, also see [Concepts](Concepts) and [Mod Creation Best Practices](Mod-Creation-Best-Practices).

<a id="mod-developers"></a>

## For mod developers

If you are packaging a mod, use [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers). That page covers the author workflow for `changes.ini`, `namespaces.ini`, test-install discipline, merge-oriented [TLK](Audio-and-Localization-Formats#tlk), [2DA](2DA-File-Format), and [InstallList](TSLPatcher-InstallList-Syntax) usage, plus HoloPatcher-specific notes such as current [HACKList](TSLPatcher-HACKList-Syntax) behavior and documented [TLK](Audio-and-Localization-Formats#tlk) replacement support.

Start there if you are building a first mod package, comparing HoloPatcher with classic TSLPatcher behavior, or deciding where KotORModSync fits into a larger mod distribution workflow.

<a id="internal-logic"></a>

## Internal architecture

If you need implementation detail rather than end-user instructions, use [Explanations on HoloPatcher Internal Logic](Explanations-on-HoloPatcher-Internal-Logic). That page breaks the tool into its major layers:

- the UI and CLI entry points in `Tools/HoloPatcher/src/holopatcher/` [[`app.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HoloPatcher/src/holopatcher/app.py) · [`cli.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HoloPatcher/src/holopatcher/cli.py)]
- the config reader that parses `changes.ini` [[`ConfigReader`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/tslpatcher/reader.py#L132)]
- the patcher that orders, applies, logs, and backs up each modification [[`ModInstaller`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/tslpatcher/patcher.py#L43)]

It also documents the patch routine, patch-list priority, override handling, and backup semantics that matter when you are debugging edge cases or comparing output against legacy TSLPatcher behavior.

## Related syntax references

HoloPatcher follows the broader TSLPatcher configuration model. Use these pages for exact list semantics:

- [TSLPatcher InstallList Syntax](TSLPatcher-InstallList-Syntax)
- [TSLPatcher TLKList Syntax](TSLPatcher-TLKList-Syntax)
- [TSLPatcher 2DAList Syntax](TSLPatcher-2DAList-Syntax)
- [TSLPatcher GFFList Syntax](TSLPatcher-GFFList-Syntax)
- [TSLPatcher SSFList Syntax](TSLPatcher-SSFList-Syntax)
- [TSLPatcher HACKList Syntax](TSLPatcher-HACKList-Syntax)
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme)

## Community adoption

HoloPatcher is used frequently in community releases, with release notes citing additional patching functionality, bug fixes, and cross-platform support as the reasons [[KOTOR 1 Community Patch](https://deadlystream.com/files/file/1258-kotor-1-community-patch/)].

### See also

- [Concepts](Concepts) explains override order, capsules, and resource resolution.
- [Home](Home#documentation) places HoloPatcher in the wider PyKotor toolchain.
- [Mod Creation Best Practices](Mod-Creation-Best-Practices) covers compatibility and release hygiene.
- [KotorDiff Integration](KotorDiff-Integration) is useful when you need to compare install outputs.
