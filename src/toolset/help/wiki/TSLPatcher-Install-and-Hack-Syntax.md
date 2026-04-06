# TSLPatcher Install and Hack Syntax

TSLPatcher's file-copy and binary-patch sections are now documented on dedicated pages. Use this page as the stable entry point for links that refer to `[InstallList]` and `[HACKList]` syntax.

## Contents

- [InstallList Syntax](#installlist-syntax)
- [HACKList Syntax](#hacklist-syntax)

## When to use this page

Use this hub when you need to decide whether a change belongs in `[InstallList]` or `[HACKList]`, or when an older wiki link brought you here. For exact folder rules, replacement behavior, offset syntax, and examples, follow the dedicated guides below.

<a id="installlist-syntax"></a>

## InstallList Syntax

Use `[InstallList]` when a mod needs to copy files from `tslpatchdata` into the game directory or into containers such as [ERF](Container-Formats#erf) or [RIM](Container-Formats#rim). The standalone guide covers folder sections, `File#` versus `Replace#`, source-folder handling, renaming, override behavior, and HoloPatcher's execution-order notes.

Canonical page:

- [TSLPatcher InstallList Syntax](TSLPatcher-InstallList-Syntax)

Typical uses:

- copying loose files into `override`, `modules`, `streamvoice`, or other game folders
- installing resources into existing module capsules
- renaming installed files or changing source-folder layout within `tslpatchdata`

<a id="hacklist-syntax"></a>

## HACKList Syntax

Use `[HACKList]` when a mod needs to write binary values directly into an [NCS](NCS-File-Format) script at fixed offsets. The standalone guide covers offset notation, supported value sources, `StrRef#` and `2DAMEMORY#` token usage, risks, and the documented HoloPatcher behavior for this historically under-documented feature.

Canonical page:

- [TSLPatcher HACKList Syntax](TSLPatcher-HACKList-Syntax)

Typical uses:

- rewriting compiled-script constants after earlier patch steps generate dynamic values
- inserting `StrRef#` or `2DAMEMORY#` output into known word offsets
- preserving compatibility where shipping a full replacement script would be too coarse

## Related sections

- [TSLPatcher 2DAList Syntax](TSLPatcher-2DAList-Syntax)
- [TSLPatcher TLKList Syntax](TSLPatcher-TLKList-Syntax)
- [TSLPatcher GFFList Syntax](TSLPatcher-GFFList-Syntax)
- [TSLPatcher SSFList Syntax](TSLPatcher-SSFList-Syntax)
- [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers)
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme)
