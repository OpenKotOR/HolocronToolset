# Concepts

The Odyssey engine resolves every resource request through a fixed priority chain: override folder, then module capsules (MOD/SAV/ERF/RIM), then KEY/BIF base archives [[`SearchLocation` enum](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/installation.py#L65-L110)]. Understanding this chain — along with ResRefs, resource types, and the difference between template data and instance data — is essential for any modding work. Other wiki pages reference the definitions here rather than re-explaining the rules. Open reimplementations describe the same shape from a different angle: xoreos's KotOR engine page lists initial module and area loading plus room-room visibility evaluation as core milestones, while xoreos-tools splits archive, GFF, TLK, and 2DA utilities along the same format boundaries modders work with daily [[Knights of the Old Republic](https://wiki.xoreos.org/index.php?title=Knights_of_the_Old_Republic), [Running xoreos-tools](https://wiki.xoreos.org/index.php/Running_xoreos-tools)].

## Cross-reference: source modules

The resolution behavior described here is reflected in these implementation starting points for tool authors:

- **PyKotor:** `pykotor.extract.installation`, `pykotor.extract.chitin`, `pykotor.resource.formats.key.io_key`, `pykotor.resource.formats.bif.io_bif`, `pykotor.resource.formats.erf.io_erf`, `pykotor.resource.formats.rim.io_rim`, `pykotor.resource.formats.tlk.io_tlk`, `pykotor.resource.formats.twoda.io_twoda`
- **reone:** `src/libs/resource/director.cpp`, `src/libs/resource/resources.cpp`, `src/libs/resource/format/keyreader.cpp`, `src/libs/resource/format/bifreader.cpp`, `src/libs/resource/format/erfreader.cpp`
- **KotOR.js:** `src/loaders/ResourceLoader.ts`, `src/resource/KEYObject.ts`, `src/resource/BIFObject.ts`, `src/managers/TwoDAManager.ts`, `src/managers/TLKManager.ts`
- **Kotor.NET:** `Kotor.NET/Formats/KotorKEY/KEYBinaryStructure.cs`, `Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs`, `Kotor.NET/Formats/KotorTLK/TLKBinaryStructure.cs`, `Kotor.NET/Formats/Kotor2DA/TwoDABinaryReader.cs`, `Kotor.NET/ResourceContainers/Chitin.cs`

## Resource Resolution Order

When the game needs a resource, it resolves a pair: **ResRef + resource type**. You may see this as 'file stem' + 'extension' e.g. `some_char.utc` is a `ResourceIdentifier("some_char", ResourceType.UTC)`. The search order is stable enough that most compatibility problems reduce to one question: which source is being searched first?

In normal play, the effective order is:

1. **Override folder** (`override/` in the game directory) [[`SearchLocation.OVERRIDE = 0`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/installation.py#L66-L68)]
2. **Currently loaded MOD/ERF/[RIM](Container-Formats#rim) module archives** (e.g. the module being played) [[`SearchLocation.MODULES = 1`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/installation.py#L70-L71)]
3. **Currently loaded save game** (when in-game; situational — often exposed as a loaded SAV / save-side container)
4. **patch.erf resources** This file exists in the root of the k1 installation at least on PC, containing mostly updated textures. Probably loaded at this stage but this is currently a guess.
5. **BIF files** indexed by **KEY** (vanilla game data) [[`SearchLocation.CHITIN = 2`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/installation.py#L73-L74)]
6. **Hardcoded defaults** (if the engine provides them)

Anything in `override/` or in the active module capsule wins before the game falls back to vanilla KEY/BIF data. That is why “just copy a file into override” works for quick tests, but also why it causes collisions when multiple mods ship the same ResRef and type.

### How the *resource manager* resolves a request

The engine first checks whether the resource is already loaded or cached. If not, it routes the request to the correct backend for that storage shape: directory, active module capsule, save-side data, or the KEY/BIF stack [[`Installation.resource()`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/installation.py#L1361)]. The [KEY](Container-Formats#key) only participates in that fourth step. It does not control override precedence, and it does not need to be edited for a mod to shadow a vanilla file.

### Role of the [**KEY**](Container-Formats#key) file

The [**KEY**](Container-Formats#key) file (normally `chitin.key`) is the master index for vanilla archive data [[`key_data.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py#L1-L55)]. It maps a ResRef and resource type to a specific BIF archive and an entry inside that archive. It does not define the whole resolution order; it only enables the vanilla-data fallback stage. xoreos's `unkeybif` page phrases the same idea in practical extraction terms: the KEY carries names and types, the BIF carries payloads, and extracting everything indexed by a KEY requires the corresponding BIF set to be treated as one unit [[Unkeybif](https://wiki.xoreos.org/index.php?title=Unkeybif)].

That distinction matters for authors. If your mod ships a file in `override/`, or a resource in a module `.mod`, the engine can find it before ever consulting `chitin.key`.

## ResRef (Resource Reference)

A **ResRef** is the resource's name: a short string (up to ***16 characters*** in *KotOR*) [[`ResRef.MAX_LENGTH = 16`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/misc.py#L75) · [Kotor.NET `ResRef.cs`](https://github.com/th3w1zard1/Kotor.NET/blob/master/Kotor.NET/Common/Data/ResRef.cs#L9-L72)], normally written without a filename extension. Together with a **Resource Type** (numeric ID; see [Resource Type Identifiers](Resource-Formats-and-Resolution#resource-type-identifiers) and [GFF-File-Format](GFF-File-Format#gff-data-types)), the engine uses the *ResRef* to look up the resource via the [resource resolution order](#resource-resolution-order) above.

## Override Folder

The **override** folder is the bluntest and most powerful mod-install location in the game. Loose files placed there are resolved before the vanilla KEY/BIF stack and before most stock content for the active module.

That makes override useful for rapid testing and for global replacements, but it also makes it the easiest place to create mod conflicts. Only one file for a given ResRef and resource type can win. For mergeable content such as [2DA](2DA-File-Format), [TLK](Audio-and-Localization-Formats#tlk), and many [GFF](GFF-File-Format) resources, patcher-based merging is usually safer than shipping a monolithic loose-file replacement.

Players have discussed loadout combinations and real-world conflict patterns in threads such as [Deadly Stream — What's in your Override folder?](https://deadlystream.com/topic/7279-whats-in-your-override-folder/). Pre-HoloPatcher discussions such as [LucasForums Archive — Load order?](https://www.lucasforumsarchive.com/thread/206128-load-order) and [Guide for the newbie: tools and how to install mods](https://www.lucasforumsarchive.com/thread/129789-guide-for-the-newbie-what-tools-do-i-need-to-mod-kotor-how-to-install-mods) document workflows that predate patcher-based installs; use [Installing Mods with HoloPatcher](HoloPatcher#installing-mods) for current player install guidance.

For Steam, GOG, and Aspyr folder layouts, widescreen patches, and common OS fixes, [PCGamingWiki — KotOR](https://www.pcgamingwiki.com/wiki/Star_Wars:_Knights_of_the_Old_Republic) and [KotOR II: The Sith Lords](https://www.pcgamingwiki.com/wiki/Star_Wars:_Knights_of_the_Old_Republic_II_-_The_Sith_Lords) provide player-environment context. They are not authoritative for KEY/BIF semantics or override precedence; those remain on this page and [Container Formats — KEY](Container-Formats#key).

## [**BIF**](Container-Formats#bif) and [**KEY**](Container-Formats#key)

[**BIF**](Container-Formats#bif) files store most of the shipped game data [[`bif_data.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py#L1-L10)]. [**KEY**](Container-Formats#key) tells the game which BIF contains a given ResRef and type, and which entry inside that BIF to read.

From a modder’s point of view, the important rule is simple: [**BIF**](Container-Formats#bif) and [**KEY**](Container-Formats#key) are the baseline, not the preferred mod target. Most mods leave them untouched and win by providing a higher-priority file in override or a module capsule.

## [**MOD**](Container-Formats#erf) / [**ERF**](Container-Formats#erf) / [**RIM**](Container-Formats#rim)

[**ERF**](Container-Formats#erf) is a general-purpose container format [[`erf_data.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L1-L10)]. [**MOD**](Container-Formats#erf) files are ERFs used as module capsules; [**SAV**](Container-Formats#erf) files are ERF-style save containers. [**RIM**](Container-Formats#rim) is the stock module archive format used by the shipped game data [[`rim_data.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/rim/rim_data.py#L1-L10)].

The practical rule is that module-scoped content belongs here, not in global override, when you want the resource to apply only to a specific area or module. In many common setups, a module `.mod` in `modules/` overrides the matching stock `.rim` pair for that module name.

### Module packaging for mod authors (override vs `modules/`)

| Delivery | Typical use | Notes |
| -------- | ----------- | ----- |
| **`override/`** | Global scripts, textures, 2DAs, TLK, GFF templates used in many modules | Highest precedence vs BIF; last writer wins if two mods use the same ResRef+type—prefer [2DAList](TSLPatcher-Data-Syntax#2dalist-syntax) / [TLKList](TSLPatcher-Data-Syntax#tlklist-syntax) merges |
| **`Modules/*.mod`** | Module-scoped capsule (ERF-type [MOD](Container-Formats#erf)) | Often overrides the vanilla `.rim` pair for that module name when present |
| **Vanilla `.rim` / `_s.rim` / `_dlg.erf`** | Stock module archives that together represent a singular Module. | Custom game changes will usually ship a singular `.mod` file per module which will override all of the vanilla resources (_s.rim, .rim, _dlg.erf) |

Choose scope first, then choose the packaging target. If the resource intends to affect many modules, ship it to `override/` or merge it through patch lists. If the resource belongs to one module, build or patch a `.mod` so the files stay capsule-scoped instead of leaking into the global override.

For distribution work, the usual failure modes are scope mistakes rather than format mistakes: shipping a module-only resource to `override/`, or reinstalling patcher options until duplicate [2DA rows](2DA-File-Format#twodarow-object) accumulate. Use [Installing Mods with HoloPatcher](HoloPatcher#installing-mods) for player-facing restore and troubleshooting guidance, and use the [resource resolution order](#resource-resolution-order) on this page to decide where the resource belongs.

## [**GFF** (Generic File Format)](GFF-File-Format)

[**GFF**](GFF-File-Format) is BioWare’s binary format for structured game data: areas (ARE), creatures (UTC), items (UTI), dialogues ([DLG](GFF-File-Format#dlg)), placeables ([UTP](GFF-File-Format#utp)), and many others [[`gff_data.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L1-L20)]. Files are hierarchical (structs, fields, lists). The same [GFF](GFF-File-Format) layout is used across Aurora/Odyssey games; KotOR and TSL use specific [GFF](GFF-File-Format) types and field meanings. Modders edit [GFF](GFF-File-Format) with tools (KotOR Tool, Holocron Toolset, K-GFF) or via [TSLPatcher/HoloPatcher `[GFFList]` implementation](TSLPatcher-GFFList-Syntax). See [GFF-File-Format](GFF-File-Format), [Bioware-Aurora-GFF](Bioware-Aurora-Core-Formats#gff).

## [**2DA** (Two-Dimensional Array)](2DA-File-Format)

[**2DA**](2DA-File-Format) files are tabular data: rows and columns used for items, [spells](2DA-File-Format#spells2da), [appearances](2DA-File-Format#appearance2da), and most game configuration. The engine and [GFF](GFF-File-Format) resources reference [*2DA*](2DA-File-Format) rows by index or label. Mods often add or edit rows (e.g. new appearance row, new spell); when multiple mods change the same [*2DA*](2DA-File-Format), merging (e.g. via [*TSLPatcher*'s](TSLPatcher's-Official-Readme) `[2DAList]` implementation) avoids overwriting. See [2DA-File-Format](2DA-File-Format), [TSLPatcher-2DAList-Syntax](TSLPatcher-Data-Syntax#2dalist-syntax).

**Historical forum example:** Veterans debated `spells.2da` edits vs multi-mod compatibility in [LucasForums Archive — spells.2da, compatibility and TSL Patcher](https://www.lucasforumsarchive.com/thread/205823-spells2da-compatibility-and-tsl-patcher) (2010); the takeaway for authors is still **merge-aware installers** and row-level patches, not dropping a monolithic override—see [2DA-spells](2DA-File-Format#spells2da) **Community context**.

**Campaign globals (scripting):** NWScript `GetGlobal*` / `SetGlobal*` identifiers are declared in [globalcat.2da](2DA-File-Format#globalcat2da). Value limits and usage patterns are summarized on [NSS — Global Variables](NSS-File-Format#global-variables). Treat forum threads on “quest globals” as **workflow hints**—verify names exist in `globalcat.2da` or your installer’s expectations.

## Resource Type Identifiers

The canonical **hex resource type ID** table (*Aurora* / *Odyssey* family, including rows unused in *KotOR*) lives on **[Resource formats and resolution — Resource Type Identifiers](Resource-Formats-and-Resolution#resource-type-identifiers)**. That page is the wiki SSOT for the numeric IDs and their four-character labels.

## Language IDs (*KotOR*)

Language IDs are a small integer enum [[`Language` enum](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/language.py#L13-L50) · [`tlk_data.py` binary spec](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L1-L35)] shared across *Infinity*/*Aurora*/*Odyssey*/*Eclipse*-era engines (TLK headers, [ERF](Container-Formats#erf) localized string lists, [GFF](GFF-File-Format) `LocalizedString` substrings, etc.). Newer *BioWare* titles added values but usually stay backward compatible with 0–5.

Use this table as the **wiki SSOT** for numeric IDs and typical text encodings. Official *BioWare* PDFs duplicate the same numbering in places like [Bioware-Aurora-TalkTable](Bioware-Aurora-Core-Formats#talktable) and [Bioware-Aurora-LocalizedStrings](Bioware-Aurora-Core-Formats#localizedstrings). xoreos's TLK language matrix reaches the same KotOR mapping and is worth keeping in view because its `tlk2xml` tool has to be told either the game or the encoding; the format family does not provide enough information to autodetect text encoding safely across BioWare titles [[TLK language IDs and encodings](https://wiki.xoreos.org/index.php?title=TLK_language_IDs_and_encodings), [Tlk2xml](https://wiki.xoreos.org/index.php?title=Tlk2xml)].

| Language | ID | Typical encoding | Description |
| -------- | -- | ---------------- | ----- |
| English  | 0  | cp1252     | |
| French   | 1  | cp1252     | |
| German   | 2  | cp1252     | |
| Italian  | 3  | cp1252     | |
| Spanish  | 4  | cp1252     | |
| Polish   | 5  | cp1250     | *KotOR 1 Polish* retail (**`cp-1250`**); see also **`dialogf.tlk`** in [TSLPatcher `[TLKList]` implementation](TSLPatcher-TLKList-Syntax) |

**Where the ID appears:** [Audio-and-Localization-Formats#tlk](Audio-and-Localization-Formats#tlk) file header and tooling; [Container-Formats#erf](Container-Formats#erf) localized description list per language; [GFF-File-Format](GFF-File-Format) `LocalizedString` embedded strings. KotOR often ignores the [TLK](Audio-and-Localization-Formats#tlk) header language field and loads the `dialog.tlk` that matches the installation—see [Audio-and-Localization-Formats#tlk](Audio-and-Localization-Formats#localization). Torlack’s Aurora basics notes, archived in [xoreos-docs](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/basics.html), cross-reference these IDs for NWN-era context that applies to KotOR.

### See also

- [Resource Formats and Resolution](Resource-Formats-and-Resolution) -- Format index, resolution order, hex resource type table
- [Home — community sources and archives](Home#community-sources-and-archives) -- Deadly Stream, LucasForums Archive, PCGamingWiki (player paths and forum context)
- [Home](Home) -- Wiki hub (formats, tools, tutorials)
- [Installing Mods with HoloPatcher](HoloPatcher#installing-mods) -- Reader-facing install and troubleshooting workflow
- [Container-Formats#key](Container-Formats#key) -- KEY file format (e.g. `chitin.key`)
- [GFF-File-Format](GFF-File-Format) -- GFF file format (e.g. `area.gff`)
- [Mod-Creation-Best-Practices](Mod-Creation-Best-Practices) -- Best practices for modding
- [Audio-and-Localization-Formats#tlk](Audio-and-Localization-Formats#tlk) -- TLK file format (e.g. `dialog.tlk`)
- [2DA-File-Format](2DA-File-Format) -- 2DA structure and table reference
