# Welcome to the PyKotor Wiki

<a id="documentation"></a>

PyKotor is a source-available KotOR and TSL modding toolchain. It exists to make the ecosystem less fragmented: one place for file-format documentation, installer behavior, tool workflows, and implementation-backed reference material that can be improved by the community instead of disappearing into forum archaeology.

The documentation is organized around what you are trying to do, not around whichever executable or legacy tool you happened to open first. Start from the table below, then follow the deeper format and engine-reference pages when you need exact behavior.

## Start here

| If you need to... | Start here | Then read |
| ----------------- | ---------- | --------- |
| Install or troubleshoot a mod | [Installing Mods with HoloPatcher](HoloPatcher#installing-mods) | [Concepts](Concepts), [Mod Creation Best Practices](Mod-Creation-Best-Practices) |
| Author a patcher-based mod | [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers) | [TSLPatcher 2DAList Syntax Guide](TSLPatcher-Data-Syntax#2dalist-syntax), [TSLPatcher TLKList Syntax Guide](TSLPatcher-Data-Syntax#tlklist-syntax), [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFF-Syntax#gfflist-syntax) |
| Edit resources in a GUI | [Holocron Toolset: Getting Started](Holocron-Toolset-Getting-Started) | [Holocron Toolset: Core resources](Holocron-Toolset-Core-Resources), [Holocron Toolset: Module resources](Holocron-Toolset-Module-Resources) |
| Work headlessly or automate a workflow | [CLI quickstart](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/CLI_QUICKSTART.md) | [KotorDiff Integration](KotorDiff-Integration), [Explanations on HoloPatcher Internal Logic](HoloPatcher#internal-logic) |
| Understand why a file wins in-game | [Concepts](Concepts) | [Resource formats and resolution](Resource-Formats-and-Resolution), [KEY File Format](Container-Formats#key) |
| Look up a binary format or game resource type | [Resource formats and resolution](Resource-Formats-and-Resolution) | The relevant format page for that extension |

## Toolchain map

- **PyKotor** is the library and CLI foundation: parsers, writers, extraction helpers, automation commands, and format conversion.
- **HoloPatcher** is the safe installer layer for merge-sensitive resources like [2DA](2DA-File-Format), [TLK](Audio-and-Localization-Formats#tlk), and [GFF](GFF-File-Format).
- **Holocron Toolset** is the GUI editing layer for modules, resources, and area content.
- **KotorDiff** is the comparison layer for install state, emitted patch data, and regression checking.

That split is deliberate. The goal is not “use only PyKotor tools forever”; the goal is to make format knowledge and mod workflows portable across tools, while still giving you a modern stack when you want one.

## Core reference pages

- [Concepts](Concepts) explains resource resolution order, override behavior, BIF/KEY, MOD/ERF/RIM, ResRef, GFF, 2DA, and language IDs.
- [Resource formats and resolution](Resource-Formats-and-Resolution) is the wiki index for extensions, resource type IDs, and format entry pages.
- [Installing Mods with HoloPatcher](HoloPatcher#installing-mods) is the player-facing install and troubleshooting guide.
- [Mod Creation Best Practices](Mod-Creation-Best-Practices) is the author-facing compatibility and distribution guide.
- [Reverse Engineering Findings](reverse_engineering_findings) is the technical reference hub for engine behavior that matters to tool authors and advanced modders.

## Contributor maintenance

- [Wiki Conventions](Wiki-Conventions) defines editorial rules for structure, evidence placement, preserved-source handling, and link style.

## Learning paths

- **New player:** [Installing Mods with HoloPatcher](HoloPatcher#installing-mods) → [Concepts](Concepts#resource-resolution-order) → [Resource formats and resolution](Resource-Formats-and-Resolution)
- **First mod author:** [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers) → [Mod Creation Best Practices](Mod-Creation-Best-Practices) → [TSLPatcher data syntax](TSLPatcher-Data-Syntax)
- **Tool author or contributor:** [Resource formats and resolution](Resource-Formats-and-Resolution) → [Reverse Engineering Findings](reverse_engineering_findings) → the relevant archive or preserved-source page only when you need provenance

## Workflow guides

- [Installing Mods with HoloPatcher](HoloPatcher#installing-mods) for player-facing install and troubleshooting steps
- [Mod Creation Best Practices](Mod-Creation-Best-Practices) for compatibility, packaging, and release discipline
- [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers) for the modern patcher-authoring workflow
- [TSLPatcher data syntax](TSLPatcher-Data-Syntax), [TSLPatcher GFF syntax](TSLPatcher-GFF-Syntax), and [TSLPatcher install and hack syntax](TSLPatcher-Install-and-Hack-Syntax) when you need exact INI section behavior

## Preserved source documents

- The **Bioware Aurora** family preserves official BioWare Aurora Engine documentation: [Core Formats](Bioware-Aurora-Core-Formats), [Module & Area](Bioware-Aurora-Module-and-Area), [Creature](Bioware-Aurora-Creature), [Items, Economy & Narrative](Bioware-Aurora-Items-Economy-and-Narrative), [Spatial & Interactive](Bioware-Aurora-Spatial-and-Interactive), [Conversation](Bioware-Aurora-Conversation).
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) is the primary historical and technical source for TSLPatcher behavior.

## Cross-reference: other tools and engines

PyKotor is one part of a larger KotOR tooling ecosystem. This section is a compact directory to adjacent projects, not an attempt to duplicate their documentation.

### Engine reimplementations

- [xoreos](https://github.com/xoreos/xoreos) is a C++ Aurora/Odyssey/Eclipse reimplementation with KotOR support.
- [reone](https://github.com/seedhartha/reone) is a community-maintained modern C++ KotOR engine.
- [KotOR.js](https://github.com/KobaltBlu/KotOR.js) is a TypeScript/WebGL engine implementation.
- [NorthernLights](https://github.com/lachjames/NorthernLights) and [KotOR-Unity](https://github.com/reubenduncan/KotOR-Unity) are Unity/.NET-based engine projects.

### File-format libraries and related tooling

- [xoreos-tools](https://github.com/xoreos/xoreos-tools) provides CLI extraction and conversion tools for Aurora-family formats.
- [Kotor.NET](https://github.com/NickHugi/Kotor.NET), [BioWare.NET](https://github.com/th3w1zard1/BioWare.NET/tree/98dd9c47d1b1ccd7cc5f72a0bd4279c418359ec2), and [Rakata](https://codeberg.org/Synchro/rakata) are alternative format-parsing stacks.
- [kotorblender](https://github.com/OpenKotOR/kotorblender), [mdlops](https://github.com/ndixUR/mdlops), [tga2tpc](https://github.com/ndixUR/tga2tpc), [DLZ-Tool](https://github.com/LaneDibello/DLZ-Tool), and [WalkmeshVisualizer](https://github.com/glasnonck/WalkmeshVisualizer) cover common 3D and asset workflows.
- [HoloLSP](https://github.com/th3w1zard1/HoloLSP/tree/80f2e64bf508a6b487d8f3ecf9ab9cb6812222a2), [nwscript-mode.el](https://github.com/implicit-image/nwscript-mode.el), and [Vanilla_KOTOR_Script_Source](https://github.com/KOTORCommunityPatches/Vanilla_KOTOR_Script_Source) are useful script-development references.

### Community projects and tools

- [HoloPatcher.NET](https://github.com/th3w1zard1/HoloPatcher.NET/tree/600630e55e2b6a62e3ed84f8cd84a413baf7795d), [Kotor-Patch-Manager](https://github.com/LaneDibello/Kotor-Patch-Manager), [KotORModSync](https://github.com/th3w1zard1/KotORModSync/tree/c8b0d10ce3fd7525d593d34a3be8d151da7d3387), [StarForge](https://github.com/th3w1zard1/StarForge/tree/01afebab065c606980cebe9120702fce2c825e2d), and [KotorModTools](https://github.com/Box65535/KotorModTools) are adjacent modding tools.
- [sotor](https://github.com/StarfishXeno/sotor), [KSELinux](https://github.com/Bolche/KSELinux), [KotOR-Save-Editor](https://github.com/Fair-Strides/KotOR-Save-Editor), and [kotor-savegame-editor](https://github.com/nadrino/kotor-savegame-editor) cover save editing.
- [SithCodec](https://github.com/BBBrassil/SithCodec) and [SWKotOR-Audio-Encoder](https://github.com/LoranRendel/SWKotOR-Audio-Encoder) cover audio-focused workflows.
- [K1_Community_Patch](https://github.com/KOTORCommunityPatches/K1_Community_Patch), [TSL_Community_Patch](https://github.com/KOTORCommunityPatches/TSL_Community_Patch), [KOTOR-utils](https://github.com/JCarter426/KOTOR-utils), [KotOR-Bioware-Libs](https://github.com/Fair-Strides/KotOR-Bioware-Libs), [kotor_combat_faq](https://github.com/statsjedi/kotor_combat_faq), and [ds-kotor-modding-wiki](https://github.com/DeadlyStream/ds-kotor-modding-wiki) are useful adjacent references.

<a id="community-sources-and-archives"></a>

## Community sources and archives

Older communities still matter for release history, workflow pitfalls, and examples that never became formal documentation.

| Source | Why it matters | How to use it |
| ------ | -------------- | ------------- |
| [DeadlyStream](https://deadlystream.com) | Primary KotOR modding hub for releases, tutorials, tool discussions, and troubleshooting threads. | Use for workflow context, release history, and real-world modder reports; keep normative format semantics on this wiki. |
| [KOTOR Community Portal](https://kotor.neocities.org) | Community-maintained landing page for FAQs, troubleshooting links, and player-facing resource directories. | Use its FAQ and links pages for player support context and discovery. Exclude its mod-build recommendation lists when writing normative wiki guidance here. |
| [LucasForums Container](https://lucasforumscontainer.com) | Wayback-backed reconstruction of the original LucasForums communities. | Use for historical TSLPatcher, tool, and modding discussions when the wiki needs provenance or original author commentary. |
| [LucasForums Archive](https://lucasforumsarchive.com) | Alternate archive of Editing/Modding, Holowan Laboratories, and tutorial threads. | Use as historical support, especially when a thread is easier to cite or search here than in the container. |
| [PCGamingWiki for KotOR](https://www.pcgamingwiki.com/wiki/Star_Wars:_Knights_of_the_Old_Republic) and [KotOR II](https://www.pcgamingwiki.com/wiki/Star_Wars:_Knights_of_the_Old_Republic_II_-_The_Sith_Lords) | Player-facing path, launcher, widescreen, and install-layout guidance. | Use for player environment context only; cross-check binary or resource-system claims against [Concepts](Concepts), [KEY File Format](Container-Formats#key), and the relevant format pages. |
| [r/kotor](https://www.reddit.com/r/kotor/) | Large active player and mod-user community with install guides, troubleshooting posts, and community-maintained build notes. | Use as workflow context and to discover common failure cases; do not treat Reddit posts as authoritative for file formats or engine behavior. |
| Holowan Laboratories / MixNMojo mirrors | Early KotOR modding discussion history. | Use when newer documentation does not preserve the original context for a tool, technique, or format note. |
| Other general forums | Current troubleshooting and installation chatter. | Use as workflow context or discovery paths, not as the primary source for file-format or engine behavior. |

## External documentation

- [xoreos-docs](https://github.com/xoreos/xoreos-docs) preserves official BioWare specifications, Torlack reverse-engineered notes, and auxiliary format material used throughout Aurora-family reverse engineering.
- [nwn-docs](https://github.com/kucik/nwn-docs) is helpful for older Aurora-family background where KotOR behavior inherits the same storage conventions.
- [bioware-kaitai-formats](https://github.com/OpenKotOR/bioware-kaitai-formats) provides Kaitai Struct specifications for many BioWare and KotOR formats and is useful for parser cross-checking.

### See also

- [Concepts](Concepts)
- [Resource formats and resolution](Resource-Formats-and-Resolution)
- [Installing Mods with HoloPatcher](HoloPatcher#installing-mods)
- [Mod Creation Best Practices](Mod-Creation-Best-Practices)
- [Reverse Engineering Findings](reverse_engineering_findings)
- [Wiki Conventions](Wiki-Conventions)

