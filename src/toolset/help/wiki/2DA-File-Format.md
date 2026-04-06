# 2DA — Two-Dimensional Array

The Two-Dimensional Array (2DA) format is the engine's primary configuration mechanism. Nearly every tunable game system — character classes, feats, Force powers, item properties, appearance models, sound sets, combat formulas — is driven by 2DA tables that the engine reads at startup [[`twoda_data.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py#L1-L10)]. Each 2DA file is a simple spreadsheet: rows indexed by number, columns indexed by label, and cell values that are either strings, integers, or the special `****` token meaning "no value" [[`twoda_data.py` L36](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py#L36)]. The format is compact enough to ship on disc and simple enough that modders can edit tables with a text editor, but the binary `V2.b` encoding used in shipped game data provides faster load times than the older ASCII `V2.0` format [[`twoda_data.py` binary spec](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py#L8-L50)]. xoreos-tools also keeps a dedicated `convert2da` utility in its baseline tool list, which is a useful external signal that 2DA remained a shared BioWare configuration-table family well beyond KotOR-specific tooling [[Running xoreos-tools](https://wiki.xoreos.org/index.php/Running_xoreos-tools)].

The [official BioWare 2DA specification](Bioware-Aurora-Core-Formats#2da) describes the format as Aurora introduced it. KotOR and TSL use that same foundation for per-table column semantics, game-specific enumerations, and [ResRef](Concepts#resref-resource-reference) lookups. To modify 2DA tables in a mod without overwriting the entire file, use [TSLPatcher/HoloPatcher 2DAList syntax](TSLPatcher-2DAList-Syntax). 2DA tables are referenced from [GFF](GFF-File-Format) resources such as [UTC](GFF-File-Format#utc-creature) creature templates, [UTI](GFF-File-Format#uti-item) item blueprints, and [UTP](GFF-File-Format#utp-placeable) placeable definitions, and they often store [StrRef](Audio-and-Localization-Formats#string-references-strref) indices into [TLK](Audio-and-Localization-Formats#tlk) string tables for player-visible text.

**Important**: While the 2DA binary layout is shared across BioWare's Aurora, Odyssey, and Eclipse engines, all column structures and engine usage descriptions on this page are specific to KotOR and KotOR II.

## Table of Contents

- 2DA — Two-Dimensional Array
  - Table of Contents
  - [file structure Overview](#file-structure-overview)
  - [Format](#format)
    - [File Header](#file-header)
    - [Column headers](#column-headers)
    - [Row Count](#row-count)
    - [Row Labels](#row-labels)
    - [Cell Data Offsets](#cell-data-offsets)
    - [Cell Data String Table](#cell-data-string-table)
  - [data structure](#data-structure)
    - [TwoDA Object](#twoda-object)
    - [TwoDARow Object](#twodarow-object)
  - [Cell Value Types](#cell-value-types)
  - [Confirmed Engine Usage](#confirmed-engine-usage)
  - [Known 2DA Files](#known-2da-files)
  - [Character \& Combat 2DA Files](#character-combat-2da-files)
    - [appearance.2da](#appearance2da)
    - [baseitems.2da](#baseitems2da)
    - [classes.2da](#classes2da)
    - [feat.2da](#feat2da)
    - [skills.2da](#skills2da)
    - [spells.2da](#spells2da)
  - [Items \& Properties 2DA Files](#items-properties-2da-files)
    - [itemprops.2da](#itemprops2da)
    - [iprp\_feats.2da](#iprp_feats2da)
    - [iprp\_spells.2da](#iprp_spells2da)
    - [iprp\_ammocost.2da](#iprp_ammocost2da)
    - [iprp\_damagecost.2da](#iprp_damagecost2da)
  - [Objects \& Area 2DA Files](#objects-area-2da-files)
    - [placeables.2da](#placeables2da)
    - [genericdoors.2da](#genericdoors2da)
    - [doortypes.2da](#doortypes2da)
    - [soundset.2da](#soundset2da)
  - [Visual Effects \& Animations 2DA Files](#visual-effects-animations-2da-files)
    - [visualeffects.2da](#visualeffects2da)
    - [portraits.2da](#portraits2da)
    - [heads.2da](#heads2da)
  - [Progression Tables 2DA Files](#progression-tables-2da-files)
    - [classpowergain.2da](#classpowergain2da)
    - [cls\_atk\_\*.2da](#cls_atk_2da)
    - [cls\_savthr\_\*.2da](#cls_savthr_2da)
  - [Name Generation 2DA Files](#name-generation-2da-files)
    - [humanfirst.2da](#humanfirst2da)
    - [humanlast.2da](#humanlast2da)
    - [Other Name Generation Files](#other-name-generation-files)
  - [Additional 2DA Files](#additional-2da-files)
    - [ambientmusic.2da](#ambientmusic2da)
    - [ambientsound.2da](#ambientsound2da)
    - [ammunitiontypes.2da](#ammunitiontypes2da)
    - [camerastyle.2da](#camerastyle2da)
    - [footstepsounds.2da](#footstepsounds2da)
    - [prioritygroups.2da](#prioritygroups2da)
    - [repute.2da](#repute2da)
    - [surfacemat.2da](#surfacemat2da)
    - [loadscreenhints.2da](#loadscreenhints2da)
    - [bodybag.2da](#bodybag2da)
    - [ranges.2da](#ranges2da)
    - [regeneration.2da](#regeneration2da)
    - [animations.2da](#animations2da)
    - [combatanimations.2da](#combatanimations2da)
    - [weaponsounds.2da](#weaponsounds2da)
    - [placeableobjsnds.2da](#placeableobjsnds2da)
    - [creaturespeed.2da](#creaturespeed2da)
    - [exptable.2da](#exptable2da)
    - [guisounds.2da](#guisounds2da)
    - [dialoganimations.2da](#dialoganimations2da)
    - [tilecolor.2da](#tilecolor2da)
    - [forceshields.2da](#forceshields2da)
    - [plot.2da](#plot2da)
    - [traps.2da](#traps2da)
    - [modulesave.2da](#modulesave2da)
    - [tutorial.2da](#tutorial2da)
    - [globalcat.2da](#globalcat2da)
    - [subrace.2da](#subrace2da)
    - [gender.2da](#gender2da)
    - [racialtypes.2da](#racialtypes2da)
    - [upgrade.2da](#upgrade2da)
    - [encdifficulty.2da](#encdifficulty2da)
    - [itempropdef.2da](#itempropdef2da)
    - [emotion.2da](#emotion2da)
    - [facialanim.2da](#facialanim2da)
    - [videoeffects.2da](#videoeffects2da)
    - [planetary.2da](#planetary2da)
    - [cursors.2da](#cursors2da)
  - [Item Property Parameter \& Cost Tables 2DA Files](#item-property-parameter-cost-tables-2da-files)
    - [iprp\_paramtable.2da](#iprp_paramtable2da)
    - [iprp\_costtable.2da](#iprp_costtable2da)
    - [iprp\_abilities.2da](#iprp_abilities2da)
    - [iprp\_aligngrp.2da](#iprp_aligngrp2da)
    - [iprp\_combatdam.2da](#iprp_combatdam2da)
    - [iprp\_damagetype.2da](#iprp_damagetype2da)
    - [iprp\_protection.2da](#iprp_protection2da)
    - [iprp\_acmodtype.2da](#iprp_acmodtype2da)
    - [iprp\_immunity.2da](#iprp_immunity2da)
    - [iprp\_saveelement.2da](#iprp_saveelement2da)
    - [iprp\_savingthrow.2da](#iprp_savingthrow2da)
    - [iprp\_onhit.2da](#iprp_onhit2da)
    - [iprp\_ammotype.2da](#iprp_ammotype2da)
    - [iprp\_mosterhit.2da](#iprp_mosterhit2da)
    - [iprp\_walk.2da](#iprp_walk2da)
    - [ai\_styles.2da](#ai_styles2da)
    - [iprp\_damagevs.2da](#iprp_damagevs2da)
    - [iprp\_attackmod.2da](#iprp_attackmod2da)
    - [iprp\_bonusfeat.2da](#iprp_bonusfeat2da)
    - [iprp\_lightcol.2da](#iprp_lightcol2da)
    - [iprp\_monstdam.2da](#iprp_monstdam2da)
    - [iprp\_skillcost.2da](#iprp_skillcost2da)
    - [iprp\_weightinc.2da](#iprp_weightinc2da)
    - [iprp\_traptype.2da](#iprp_traptype2da)
    - [iprp\_damagered.2da](#iprp_damagered2da)
    - [iprp\_spellres.2da](#iprp_spellres2da)
    - [rumble.2da](#rumble2da)
    - [musictable.2da](#musictable2da)
    - [difficultyopt.2da](#difficultyopt2da)
    - [xptable.2da](#xptable2da)
    - [featgain.2da](#featgain2da)
    - [effecticon.2da](#effecticon2da)
    - [itempropsdef.2da](#itempropsdef2da)
    - [pazaakdecks.2da](#pazaakdecks2da)
    - [acbonus.2da](#acbonus2da)
    - [keymap.2da](#keymap2da)
    - [soundeax.2da](#soundeax2da)
    - [poison.2da](#poison2da)
    - [feedbacktext.2da](#feedbacktext2da)
    - [creaturesize.2da](#creaturesize2da)
    - [appearancesndset.2da](#appearancesndset2da)
    - [texpacks.2da](#texpacks2da)
    - [videoquality.2da](#videoquality2da)
    - [loadscreens.2da](#loadscreens2da)
    - [phenotype.2da](#phenotype2da)
    - [palette.2da](#palette2da)
    - [bodyvariation.2da](#bodyvariation2da)
    - [textures.2da](#textures2da)
    - [merchants.2da](#merchants2da)
    - [actions.2da](#actions2da)
    - [aiscripts.2da](#aiscripts2da)
    - [bindablekeys.2da](#bindablekeys2da)
    - [crtemplates.2da](#crtemplates2da)
    - [environment.2da](#environment2da)
    - [fractionalcr.2da](#fractionalcr2da)
    - [gamespyrooms.2da](#gamespyrooms2da)
    - [hen\_companion.2da](#hen_companion2da)
    - [hen\_familiar.2da](#hen_familiar2da)
    - [masterfeats.2da](#masterfeats2da)
    - [movies.2da](#movies2da)
    - [stringtokens.2da](#stringtokens2da)
    - [tutorial\_old.2da](#tutorial_old2da)
    - [credits.2da](#credits2da)
    - [disease.2da](#disease2da)
    - [droiddischarge.2da](#droiddischarge2da)
    - [minglobalrim.2da](#minglobalrim2da)
    - [upcrystals.2da](#upcrystals2da)
    - [chargenclothes.2da](#chargenclothes2da)
    - [aliensound.2da](#aliensound2da)
    - [alienvo.2da](#alienvo2da)
    - [grenadesnd.2da](#grenadesnd2da)
    - [inventorysnds.2da](#inventorysnds2da)
    - [areaeffects.2da](#areaeffects2da)

---

<!-- Anchors for TOC links to 2DA files that do not have a dedicated subsection -->
<a id="actions2da"></a>
<a id="ai_styles2da"></a>
<a id="aiscripts2da"></a>
<a id="aliensound2da"></a>
<a id="alienvo2da"></a>
<a id="areaeffects2da"></a>
<a id="bodyvariation2da"></a>
<a id="chargenclothes2da"></a>
<a id="cls_atk_2da"></a>
<a id="cls_savthr_2da"></a>
<a id="creaturesize2da"></a>
<a id="credits2da"></a>
<a id="crtemplates2da"></a>
<a id="environment2da"></a>
<a id="gamespyrooms2da"></a>
<a id="hen_companion2da"></a>
<a id="hen_familiar2da"></a>
<a id="humanfirst2da"></a>
<a id="humanlast2da"></a>
<a id="iprp_ammocost2da"></a>
<a id="iprp_attackmod2da"></a>
<a id="iprp_bonusfeat2da"></a>
<a id="iprp_damagered2da"></a>
<a id="iprp_damagevs2da"></a>
<a id="iprp_feats2da"></a>
<a id="iprp_skillcost2da"></a>
<a id="iprp_spellres2da"></a>
<a id="iprp_spells2da"></a>
<a id="iprp_traptype2da"></a>
<a id="iprp_weightinc2da"></a>
<a id="itempropsdef2da"></a>
<a id="merchants2da"></a>
<a id="minglobalrim2da"></a>
<a id="musictable2da"></a>
<a id="palette2da"></a>
<a id="phenotype2da"></a>
<a id="rumble2da"></a>
<a id="soundeax2da"></a>
<a id="textures2da"></a>
<a id="tilecolor2da"></a>
<a id="tutorial_old2da"></a>
<a id="videoquality2da"></a>

## file structure Overview

2DA files are tabular game data; role in modding and merge workflows: see the **2DA** section on [Concepts](Concepts). On disk in game archives they use binary version **`V2.b`** and the `.2da` extension. The engine loads them with the same *[resource resolution order](Concepts#resource-resolution-order)* as other resources:

- override
- module [RIM](Container-Formats#rim)
- [MOD](Container-Formats#erf)
- save
- [KEY](Container-Formats#key)
- [BIF](Container-Formats#bif)

PyKotor's 2DA implementation is in `resource/formats/twoda/`, with binary `V2.b` reader/writer support in [`TwoDABinaryReader.load` L146+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py#L146) and [`TwoDABinaryWriter.write` L183+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py#L183), backed by [`TwoDA` L87+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py#L87) and [`TwoDARow` L915+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py#L915). Text and interchange formats (`V2.0`, CSV, JSON) are handled in `io_twoda_csv.py`, `io_twoda_json.py`, and [`twoda_auto.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py). Equivalent parsers exist in [reone `2dareader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/2dareader.cpp), [KotOR.js `TwoDAObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/TwoDAObject.ts), [Kotor.NET `TwoDA.cs` L16+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/Kotor2DA/TwoDA.cs#L16) and [`TwoDABinaryStructure.cs` L12+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/Kotor2DA/TwoDABinaryStructure.cs#L12), [xoreos `2dafile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/2dafile.cpp), [KotOR-Unity `2DAObject.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/2DAObject.cs), and [kotor `docs/2da.md`](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md).

### See also

- [TSLPatcher 2DAList Syntax](TSLPatcher-Data-Syntax#2dalist-syntax) - Modding 2DA files with *TSLPatcher*
- [GFF File Format](GFF-File-Format) - Related format that often references *2DA* data
- [TLK File Format](Audio-and-Localization-Formats#tlk) - Text strings referenced by *2DA* entries

---

## format

The sections below document the **binary `V2.b`** layout used by the KotOR engine in packed resources (see overview above for PyKotor module split).

### File Header

The file header is `9` bytes in size:

| Name         | type    | offset | size | Description                                    |
| ------------ | ------- | ------ | ---- | ---------------------------------------------- |
| file type    | [char](GFF-File-Format#gff-data-types) | `0` (0x00) | `4`    | Always `"2DA "` (space-padded) or `"2DA\t"` (tab-padded) |
| file Version | [char](GFF-File-Format#gff-data-types) | `4` (0x04) | `4`    | Always `"V2.b"`              |
| Line Break   | [uint8](GFF-File-Format#gff-data-types)   | `8` (0x08) | `1`    | Newline character (`\n`, value `0x0A`)        |

The file type can be either `"2DA "` (space-padded) or `"2DA\t"` (tab-padded), and both are accepted by the KotOR engine implementations in [PyKotor `io_twoda.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py), [reone `2dareader.cpp` L29-L32](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/2dareader.cpp#L29-L32), [xoreos `2dafile.cpp` L48-L51](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/2dafile.cpp#L48-L51), and [KotOR-Unity `2DAObject.cs` L25-L32](https://github.com/reubenduncan/KotOR-Unity/blob/da59c0e3b16e351479e543d455bb39b6811f7239/Assets/Scripts/FileObjects/2DAObject.cs#L25-L32).

### Column Headers

Column headers immediately follow the header, terminated by a [null byte](https://en.cppreference.com/w/c/string/byte):

| Name            | type    | Description                                                      |
| --------------- | ------- | ---------------------------------------------------------------- |
  | Column Headers  | [char](GFF-File-Format#gff-data-types)[]  | [Tab-separated](https://en.wikipedia.org/wiki/Tab-separated_values) column names (e.g., `"label\tname\tdescription"`) |
| [Null Terminator](https://en.cppreference.com/w/c/string/byte) | [uint8](GFF-File-Format#gff-data-types)   | Single [null byte](https://en.cppreference.com/w/c/string/byte) (`\0`) marking end of headers                   |

Each column name is terminated by a tab character (`0x09`), and the entire header list is terminated by a [null byte](https://en.cppreference.com/w/c/string/byte) (`0x00`). Column names are case-sensitive and are usually lowercase in KotOR files, consistent with [reone `2dareader.cpp` L72-L89](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/2dareader.cpp#L72-L89), [xoreos `2dafile.cpp` L260-L275](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/2dafile.cpp#L260-L275), [KotOR-Unity `2DAObject.cs` L36-L48](https://github.com/reubenduncan/KotOR-Unity/blob/da59c0e3b16e351479e543d455bb39b6811f7239/Assets/Scripts/FileObjects/2DAObject.cs#L36-L48), and [kotor `docs/2da.md` L32-L37](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md#L32-L37).

### Row Count

| Name      | type    | offset | size | Description                    |
| --------- | ------- | ------ | ---- | ------------------------------ |
| Row Count | UInt32  | varies | 4    | Number of data rows in the file ([little-endian](https://en.wikipedia.org/wiki/Endianness)) |

The row count is stored as a 32-bit unsigned integer in [little-endian](https://en.wikipedia.org/wiki/Endianness) order, and this value determines how many row labels and data rows follow, matching [reone `2dareader.cpp` L34](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/2dareader.cpp#L34), [xoreos `2dafile.cpp` L284](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/2dafile.cpp#L284), and [kotor `docs/2da.md` L39-L44](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md#L39-L44).

### Row Labels

Row labels immediately follow the row count:

| Name       | type    | Description                                                      |
| ---------- | ------- | ---------------------------------------------------------------- |
| Row Labels | [char](GFF-File-Format#gff-data-types)[]  | [Tab-separated](https://en.wikipedia.org/wiki/Tab-separated_values) row labels (one per row, typically numeric)       |

Each row label is read as a [tab-terminated](#column-headers) string (tab character `0x09`). Row labels are usually numeric (`"0"`, `"1"`, `"2"`...) but can be arbitrary strings.

**Important**: The row label list is **not** terminated by a [null byte](https://en.cppreference.com/w/c/string/byte) (`0x00`), so the reader must consume exactly `row_count` labels from the count field. This differs from column headers, which do use a [null terminator](https://en.cppreference.com/w/c/string/byte). Row labels are mainly for readability and tools; in-engine row indexing is positional, not label-based, as shown in [reone `2dareader.cpp` L35](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/2dareader.cpp#L35), [xoreos `2dafile.cpp` L277-L294](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/2dafile.cpp#L277-L294), [KotOR-Unity `2DAObject.cs` L56-L70](https://github.com/reubenduncan/KotOR-Unity/blob/da59c0e3b16e351479e543d455bb39b6811f7239/Assets/Scripts/FileObjects/2DAObject.cs#L56-L70), and [kotor `docs/2da.md` L39-L46](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md#L39-L46).

### Cell Data Offsets

After row labels, cell data offsets are stored:

| Name            | type     | size | Description                                                      |
| --------------- | -------- | ---- | ---------------------------------------------------------------- |
| Cell Offsets    | [uint16](GFF-File-Format#gff-data-types)[] | `2`×`N`  | [Array](https://en.wikipedia.org/wiki/Array_data_structure) of offsets into the cell data string table. Row-major size *N* uses:<br>- [row_count](#row-labels)<br>- [column_count](#column-headers)<br>Values are stored [little-endian](https://en.wikipedia.org/wiki/Endianness). |
| Cell Data Size  | [uint16](GFF-File-Format#gff-data-types)   | `2`    | Total size of cell data string table in bytes ([little-endian](https://en.wikipedia.org/wiki/Endianness))   |

Each cell has a 16-bit unsigned integer offset ([little-endian](https://en.wikipedia.org/wiki/Endianness)) pointing to its string value in the cell data string table. Offsets are stored in [row-major order](https://en.wikipedia.org/wiki/Row-_and_column-major_order) (all cells of row `0`, then all cells of row `1`, etc.). The cell data size field immediately follows the offset array and precedes the actual cell data.

**Important**: Offsets are relative to the start of the cell data string table (immediately after `cell_data_size`). Multiple cells can share one offset when they contain identical strings, enabling data *[deduplication](https://en.wikipedia.org/wiki/Data_deduplication)*, which is visible in [reone `2dareader.cpp` L47-L52](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/2dareader.cpp#L47-L52), [xoreos `2dafile.cpp` L314-L317](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/2dafile.cpp#L314-L317), [KotOR-Unity `2DAObject.cs` L72-L83](https://github.com/reubenduncan/KotOR-Unity/blob/da59c0e3b16e351479e543d455bb39b6811f7239/Assets/Scripts/FileObjects/2DAObject.cs#L72-L83), [reone `2dawriter.cpp` L63-L89](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/2dawriter.cpp#L63-L89), and [kotor `docs/2da.md` L48-L54](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md#L48-L54).

### Cell Data String Table

The cell data string table contains all cell values as *[null-terminated](https://en.cppreference.com/w/c/string/byte)* strings:

| Name         | type   | Description                                                      |
| ------------ | ------ | ---------------------------------------------------------------- |
| Cell strings | [char](GFF-File-Format#gff-data-types)[] | *[Null-terminated](https://en.cppreference.com/w/c/string/byte)* strings, *[deduplicated](https://en.wikipedia.org/wiki/Data_deduplication)* (same value shares offset) |

The cell data string table begins immediately after the `cell_data_size` field. Each string is *[null-terminated](https://en.cppreference.com/w/c/string/byte)* (`0x00`). Blank or empty cells are typically stored as empty strings (immediately *[null-terminated](https://en.cppreference.com/w/c/string/byte)*) or the string `"****"`. The string table is *[deduplicated](https://en.wikipedia.org/wiki/Data_deduplication)* - multiple cells with the same value share the same offset, reducing file size.

**Reading process**: For each cell, the reader retrieves the 16-bit offset from the offset array (`row_index × column_count + column_index`), seeks to `cell_data_start_position + offset`, and reads a *[null-terminated](https://en.cppreference.com/w/c/string/byte)* string at that location. This behavior and the `"****"` empty-cell convention are consistent across [reone `2dareader.cpp` L54-L65](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/2dareader.cpp#L54-L65), [xoreos `2dafile.cpp` L319-L335](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/2dafile.cpp#L319-L335) and [`2dafile.cpp` L63-L64](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/2dafile.cpp#L63-L64), [KotOR-Unity `2DAObject.cs` L85-L100](https://github.com/reubenduncan/KotOR-Unity/blob/da59c0e3b16e351479e543d455bb39b6811f7239/Assets/Scripts/FileObjects/2DAObject.cs#L85-L100), and [kotor `docs/2da.md` L57-L64](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md#L57-L64).

---

## Data Structure

### TwoDA Object

The `TwoDA` object represents a complete *2DA* file in memory ([`twoda_data.py:77–119`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py#L77-L119)):

**Attributes:**

- `_rows`: List of dictionaries, each mapping column headers to cell values
- `_headers`: List of column header names (case-sensitive, typically lowercase)
- `_labels`: List of row labels (usually numeric strings like `"0"`, `"1"`, `"2"`...)

**Methods:**

- `get_cell(row_index, column_header)`: Get cell value by row index and column header
- `set_cell(row_index, column_header, value)`: Set cell value
- `get_column(header)`: Get all values for a column
- `add_row(label)`: Add a new row
- `add_column(header)`: Add a new column

### TwoDARow Object

The `TwoDARow` object provides a convenient interface for accessing row data ([`twoda_data.py:850–950`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py#L850-L950)):

**Attributes:**

- `label`: Row label string (usually numeric strings like `"0"`, `"1"`, `"2"`...)
- `cells`: Dictionary mapping column headers to cell values

---

## Cell value types

All cell values are stored as strings in the *2DA* file, but are interpreted as different types by the KotOR game engine:

- **Integers**: Numeric strings parsed as [`int32`](https://en.wikipedia.org/wiki/Integer_(computer_science)) - used for numeric identifiers, counts, and enumerated values.
- **Floats**: Decimal strings parsed as [`float`](https://en.wikipedia.org/wiki/Single-precision_floating-point_format) - used for calculations like damage multipliers, timers, and percentages.
- **ResRefs**: [Resource references](Concepts#resref-resource-reference) point to other game resources such as:

  - [models](MDL-MDX-File-Format)
  - [textures](Texture-Formats#tpc)
  - [NCS](NCS-File-Format) scripts (and other resource types by ResRef)
- **StrRefs**: [String references](Audio-and-Localization-Formats#string-references-strref) into [`dialog.tlk`](Audio-and-Localization-Formats#tlk) (typically negative values like `-1` indicate no reference) - used for localized text display.
- **Boolean**: `"0"` or `"1"` (sometimes `"TRUE"`/`"FALSE"`) - control feature flags and settings
- **Empty Cells**: Represented as `"****"` - treated as null/undefined by the engine

The game engine parses cell values based on context and expected data type for each column. For example, the `appearance.2da` file uses integers for [model](MDL-MDX-File-Format) indices, [ResRefs](Concepts#resref-resource-reference) for [texture](Texture-Formats#tpc) names, and [StrRefs](Audio-and-Localization-Formats#string-references-strref) for race names.

---

## Confirmed Engine Usage

The following *2DA* files have been confirmed to be actively loaded and used by the KotOR game engine through comprehensive reverse engineering analysis of `swkotor.exe` and `swkotor2.exe` using Ghidra (via [AgentDecompile](https://github.com/bolabaden/AgentDecompile)). This analysis examined the actual game executables to identify all *2DA* files loaded via `Load2DArrays()`, `CResRef__CResRef()` calls, and related loading functions.

### Analysis Methodology

The game engine analysis was performed by:

1. Decompiling `swkotor.exe` (*KotOR* 1) and `swkotor2.exe` (*KotOR* 2/TSL) using Ghidra
2. Identifying all `Load2DArrays_*()` functions and their `CResRef()` calls
3. Tracing `C2DA::Load2DArray()` calls throughout the codebase
4. Verifying string references to *2DA* file names in the executable binaries

### KotOR 1 (`swkotor.exe`) - Confirmed *2DA* Files

**Core Game Systems:**

- `classes.2da` - `LoadClassInfo()` --> `CResRef("Classes")`
- `feat.2da` - `LoadFeatInfo()` --> `CResRef("Feat")`
- `featgain.2da` - `CSWClass::LoadFeatGain()` --> `CResRef("featgain")`
- `skills.2da` - `LoadSkillInfo()` --> `CResRef("Skills")`
- `spells.2da` - `Load2DArrays_Spells()` --> `CResRef("Spells")`
- `exptable.2da` - `CSWRules::CSWRules()` --> `CResRef("EXPTABLE")`
- `xptable.2da` - `Load2DArrays_XpBase()` --> `CResRef("XPTable")`

**Character & Appearance:**

- `appearance.2da` - `Load2DArrays_Appearance()` --> `CResRef("Appearance")`
- `racialtypes.2da` - `LoadRaceInfo()` --> `CResRef("RacialTypes")`
- `gender.2da` - `Load2DArrays_Gender()` --> `CResRef("GENDER")`
- `portraits.2da` - `Load2DArrays_Portrait()` --> `CResRef("Portraits")`
- `heads.2da` - `Load2DArrays_Heads()` --> `CResRef("Heads")`
- `creaturespeed.2da` - `Load2DArrays_CreatureSpeed()` --> `CResRef("CreatureSpeed")`
- `ranges.2da` - `CSWRules::CSWRules()` --> `CResRef("Ranges")`

**Items & Equipment:**

- `baseitems.2da` - `CSWBaseItemArray::Load()` --> `CResRef("BASEITEMS")`
- `itempropdef.2da` - `Load2DArrays_ItemPropDef()` --> `CResRef("ItemPropDef")`
- `itemprops.2da` - `HandleServerToPlayerDebugInfo_Item()` --> `CResRef("ITEMPROPS")`
- `upgrade.2da` - `CSWGuiUpgrade()` --> `CResRef("upgrade")`

**Objects & Areas:**

- `placeables.2da` - `Load2DArrays_Placeables()` --> `CResRef("Placeables")`
- `genericdoors.2da` - `Load2DArrays_GenericDoors()` --> `CResRef("GenericDoors")`
- `doortypes.2da` - `Load2DArrays_DoorTypes()` --> `CResRef("DoorTypes")`
- `traps.2da` - `Load2DArrays_Traps()` --> `CResRef("Traps")`
- `encdifficulty.2da` - `Load2DArrays_EncDifficulty()` --> `CResRef("EncDifficulty")`
- `loadscreens.2da` - `Load2DArrays_AreaTransition()` --> `CResRef("Loadscreens")`
- `modulesave.2da` - `StartNewModule()` --> `CResRef("modulesave")`

**Audio & Visual:**

- `ambientmusic.2da` - `Load2DArrays_AmbientMusic()` --> `CResRef("AmbientMusic")`
- `ambientsound.2da` - `Load2DArrays_AmbientSound()` --> `CResRef("AmbientSound")`
- `footstepsounds.2da` - `Load2DArrays_FootstepSounds()` --> `CResRef("FootstepSounds")`
- `appearancesndset.2da` - `Load2DArrays_AppearanceSounds()` --> `CResRef("AppearanceSounds")`
- `weaponsounds.2da` - `Load2DArrays_WeaponSounds()` --> `CResRef("WeaponSounds")`
- `placeablesounds.2da` - `Load2DArrays_PlaceableSounds()` --> `CResRef("PlaceableSounds")`
- `camerastyle.2da` - `Load2DArrays_CameraStyle()` --> `CResRef("CameraStyle")`
- `surfacemat.2da` - `Load2DArrays_SurfaceMaterial()` --> `CResRef("SurfaceMaterial")`
- `visualeffects.2da` - `Load2DArrays_VisualEffect()` --> `CResRef("VisualEffect")`
- `videoeffects.2da` - `Load2DArrays_VideoEffects()` --> `CResRef("VideoEffects")`
- `dialoganimations.2da` - `Load2DArrays_DialogAnimations()` --> `CResRef("DialogAnimations")`
- `cursors.2da` - `Load2DArrays_Cursor()` --> `CResRef("cursors")`

**Item Properties (IPRP):**

- `iprp_abilities.2da` - `Load2DArrays_IPRPAbilities()` --> `CResRef("IPRP_ABILITIES")`
- `iprp_acmodtype.2da` - `LoadIPRPCostTables()` --> `CResRef("IPRP_ACMODTYPE")`
- `iprp_aligngrp.2da` - `LoadIPRPCostTables()` --> `CResRef("IPRP_ALIGNGRP")`
- `iprp_ammotype.2da` - `LoadIPRPCostTables()` --> `CResRef("IPRP_AMMOTYPE")`
- `iprp_combatdam.2da` - `LoadIPRPCostTables()` --> `CResRef("IPRP_COMBATDAM")`
- `iprp_costtable.2da` - `LoadIPRPCostTables()` --> `CResRef("IPRP_COSTTABLE")`
- `iprp_damagecost.2da` - `Load2DArrays_IPRPDamage()` --> `CResRef("IPRP_DAMAGECOST")`
- `iprp_damagetype.2da` - `LoadIPRPCostTables()` --> `CResRef("IPRP_DAMAGETYPE")`
- `iprp_immunity.2da` - `LoadIPRPCostTables()` --> `CResRef("IPRP_IMMUNITY")`
- `iprp_lightcol.2da` - `Load2DArrays_LightColor()` --> `CResRef("LightColor")`
- `iprp_meleecost.2da` - `Load2DArrays_IPRPMelee()` --> `CResRef("IPRP_MeleeCost")`
- `iprp_mosterhit.2da` - `LoadIPRPCostTables()` --> `CResRef("IPRP_MONSTERHIT")`
- `iprp_onhit.2da` - `Load2DArrays_OnHit()` --> `CResRef("IPRP_ONHIT")`
- `iprp_paramtable.2da` - `LoadIPRPParamTables()` --> `CResRef("IPRP_PARAMTABLE")`
- `iprp_protection.2da` - `LoadIPRPCostTables()` --> `CResRef("IPRP_PROTECTION")`
- `iprp_saveelement.2da` - `LoadIPRPCostTables()` --> `CResRef("IPRP_SAVEELEMENT")`
- `iprp_savingthrow.2da` - `LoadIPRPCostTables()` --> `CResRef("IPRP_SAVINGTHROW")`
- `iprp_walk.2da` - `LoadIPRPCostTables()` --> `CResRef("IPRP_WALK")`

**Factions & Reputation:**

- `repute.2da` - `Load2DArrays_Repute()` --> `CResRef("Repute")`

**Game Systems:**

- `plot.2da` - `Load2DArrays_PlotXP()` --> `CResRef("Plot")`
- `planetary.2da` - `Load2DArrays_Planetary()` --> `CResRef("Planetary")`
- `loadscreenhints.2da` - `CClientExoAppInternal::GetNextLoadScreenHintSTRREF()` --> `CResRef("loadscreenhints")`
- `movies.2da` - `Load2DArrays_Movies()` --> `CResRef("Movies")`
- `globalcat.2da` - `CSWGlobalVariableTable::ReadCatalogue()` --> `CResRef("globalcat")`
- `tutorial.2da` - `Load2DArrays_Tutorial()` --> `CResRef("Tutorial")`
- `difficultyopt.2da` - `Load2DArrays_DifficultyOptions()` --> `CResRef("DifficultyOptions")`
- `gamma.2da` - `Load2DArrays_Gamma()` --> `CResRef("Gamma")`
- `statescripts.2da` - `Load2DArrays_StateScripts()` --> `CResRef("StateScripts")`
- `poison.2da` - `Load2DArrays_Poison()` --> `CResRef("Poison")`
- `disease.2da` - `Load2DArrays_Disease()` --> `CResRef("Disease")`
- `repaadjustments.2da` - `Load2DArrays_RepAdjustments()` --> `CResRef("RepAdjustments")`
- `fractionalcr.2da` - `Load2DArrays_FractionalCR()` --> `CResRef("FractionalCR")`
- `regeneration.2da` - `Load2DArrays_Regeneration()` --> `CResRef("Regeneration")`
- `ammunitiontypes.2da` - `Load2DArrays_AmmunitionTypes()` --> `CResRef("AmmunitionTypes")`
- `keymap.2da` - `Load2DArrays_Keymap()` --> `CResRef("Keymap")`
- `bindablekeys.2da` - `Load2DArrays_BindableKey()` --> `CResRef("BindableKey")`

### KotOR 2/TSL (swkotor2.exe) - Additional 2DA Files

The following 2DA files are loaded in KotOR 2 but not in KotOR 1:

- `emotion.2da` - `FUN_00612fb0()` --> `CResRef("Emotion")`
- `facialanim.2da` - `FUN_005e6ac0()` --> `CResRef("FacialAnim")`
- `subrace.2da` - `FUN_00612ab0()` --> `CResRef("Subrace")`
- `soundset.2da` - `FUN_006ce0c0()` --> `CResRef("SoundSet")`
- `pazaakdecks.2da` - `FUN_00754f60()` --> `CResRef("PazaakDecks")`
- `upcrystals.2da` - `FUN_00730970()` --> `CResRef("upcrystals")`
- `iprp_monstcost.2da` - `FUN_00611120()` --> `CResRef("IPRP_MONSTCOST")`
- `iprp_bonuscost.2da` - `FUN_006111c0()` --> `CResRef("IPRP_BONUSCOST")`
- `iprp_srcost.2da` - `FUN_00611260()` --> `CResRef("IPRP_SRCOST")`
- `iprp_neg5cost.2da` - `FUN_00611300()` --> `CResRef("IPRP_NEG5COST")`
- `iprp_onhitdur.2da` - `FUN_006114e0()` --> `CResRef("IPRP_ONHITDUR")`
- `iprp_pc.2da` - `FUN_00612b50()` --> `CResRef("IPRP_PC")`

**Note:** All files listed above have been verified through decompilation analysis of the game executables. Function names in `swkotor2.exe` are obfuscated (shown as `FUN_*` addresses), but the 2DA file loading calls have been confirmed. Files documented below that are not listed here may be remnants from Neverwinter Nights (NWN), unused by the game engine, or used in ways not yet identified.

## Known 2DA Files

KotOR and TSL ship a large set of 2DA tables. The sections below group them by system and call out engine usage, column definitions, and the data each table drives.

---

## Character & Combat *2DA* files

### `appearance.2da`

**Engine Usage**: The `appearance.2da` file is one of the most critical *2DA* files in the games. It maps appearance IDs (from [creature templates](GFF-File-Format#utc-creature) and character creation) into the data the renderer needs when loading creatures:

- 3D [model](MDL-MDX-File-Format) *ResRefs*
- [texture](Texture-Formats#tpc) assignments
- Race associations and physical properties
- Which [model](MDL-MDX-File-Format) to display
- Which [textures](Texture-Formats#tpc) to display
- Hit detection inputs
- [animations](MDL-MDX-File-Format#animation-header)

**Row index**: Appearance ID (*integer*, typically `0`-based)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* (optional) | Human-readable label for the appearance |
| `modeltype` | *String* | [model](MDL-MDX-File-Format) type identifier (e.g., "F", "B", "P") |
| `modela` through `modeln` | *ResRef* (optional) | [model](MDL-MDX-File-Format) *ResRefs* for different body parts or variations ([models](MDL-MDX-File-Format) a-n) |
| `texa` through `texn` | *ResRef* (optional) | [texture](Texture-Formats#tpc) *ResRefs* for different body parts ([textures](Texture-Formats#tpc) a-n) |
| `texaevil`, `texbevil`, `texievil`, `texlevil`, `texnevil` | *ResRef* (optional) | Dark side variant [textures](Texture-Formats#tpc) *ResRefs* |
| `race` | *ResRef* (optional) | Race identifier *ResRef* |
| `racetex` | *ResRef* (optional) | Race-specific [texture](Texture-Formats#tpc) *ResRef* |
| `racialtype` | *Integer* | Numeric racial type identifier |
| `normalhead` | *Integer* (optional) | Default head appearance ID |
| `backuphead` | *Integer* (optional) | Fallback head appearance ID |
| `portrait` | *ResRef* (optional) | Portrait image *ResRef* |
| `skin` | *ResRef* (optional) | Skin [texture](Texture-Formats#tpc) *ResRef* |
| `headtexe`, `headtexg`, `headtexve`, `headtexvg` | *ResRef* (optional) | Head [texture](Texture-Formats#tpc) *ResRefs* variations |
| `headbone` | *String* (optional) | Bone name for head attachment |
| `height` | [Float](https://en.wikipedia.org/wiki/Single-precision_floating-point_format) | Character height multiplier |
| `hitdist` | [Float](https://en.wikipedia.org/wiki/Single-precision_floating-point_format) | Hit detection distance |
| `hitradius` | [Float](https://en.wikipedia.org/wiki/Single-precision_floating-point_format) | Hit detection radius |
| `sizecategory` | *Integer* | size category (affects combat calculations) |
| `moverate` | *String* | Movement rate identifier |
| `walkdist` | *Float* | Walking distance threshold |
| `rundist` | *Float* | Running distance threshold |
| `prefatckdist` | *Float* | Preferred attack distance |
| `creperspace` | *Float* | Creature personal space radius |
| `perspace` | *Float* | Personal space radius |
| `cameraspace` | *Float* (optional) | Camera space offset |
| `cameraheightoffset` | *String* (optional) | Camera height offset |
| `targetheight` | *String* | Target height for combat |
| `perceptiondist` | *Integer* | Perception distance |
| `headArcH` | *Integer* | Head horizontal arc angle |
| `headArcV` | *Integer* | Head vertical arc angle |
| `headtrack` | *Boolean* | Whether head tracking is enabled |
| `hasarms` | *Boolean* | Whether creature has arms |
| `haslegs` | *Boolean* | Whether creature has legs |
| `groundtilt` | *Boolean* | Whether ground tilt is enabled |
| `footsteptype` | *Integer* (optional) | Footstep sound type |
| `footstepsound` | *ResRef* (optional) | Footstep sound *ResRef* |
| `footstepvolume` | *Boolean* | Whether footstep volume is enabled |
| `armorSound` | *ResRef* (optional) | Armor sound effect *ResRef* |
| `combatSound` | *ResRef* (optional) | Combat sound effect *ResRef* |
| `soundapptype` | *Integer* (optional) | Sound appearance type |
| `bloodcolr` | *String* | Blood color identifier |
| `deathvfx` | *Integer* (optional) | Death visual effect ID |
| `deathvfxnode` | *String* (optional) | Death VFX attachment [node](MDL-MDX-File-Format#node-structures) |
| `fadedelayondeath` | *Boolean* (optional) | Whether to fade on death |
| `destroyobjectdelay` | *Boolean* (optional) | Whether to delay object destruction |
| `disableinjuredanim` | *Boolean* (optional) | Whether to disable injured [animations](MDL-MDX-File-Format#animation-header) |
| `abortonparry` | *Boolean* | Whether to abort on parry |
| `freelookeffect` | *Integer* (optional) | Free look effect ID |
| `equipslotslocked` | *Integer* (optional) | Locked equipment slot flags |
| `weaponscale` | *String* (optional) | Weapon scale multiplier |
| `wingTailScale` | *Boolean* | Whether wing/tail scaling is enabled |
| `helmetScaleF` | *String* (optional) | Female helmet scale |
| `helmetScaleM` | *String* (optional) | Male helmet scale |
| `envmap` | *ResRef* (optional) | Environment map [texture](Texture-Formats#tpc) *ResRef* |
| `bodyBag` | *Integer* (optional) | Body bag appearance ID |
| `stringRef` | *Integer* (optional) | *String* reference for appearance name |
| `driveaccl` | *Integer* | Vehicle drive acceleration |
| `drivemaxspeed` | *Float* | Vehicle maximum speed |
| `driveanimwalk` | *Float* | Vehicle walk [animation](MDL-MDX-File-Format#animation-header) speed |
| `driveanimrunPc` | *Float* | PC vehicle run [animation](MDL-MDX-File-Format#animation-header) speed |
| `driveanimrunXbox` | *Float* | Xbox vehicle run [animation](MDL-MDX-File-Format#animation-header) speed |

**Column Details**:

The `appearance.2da` file contains a comprehensive set of columns for character appearance configuration. The complete column list is parsed by the game engine:

- [model](MDL-MDX-File-Format) columns: `modela` through `modeln` (14 [model](MDL-MDX-File-Format) variations)
- [texture](Texture-Formats#tpc) columns: `texa` through `texn` (14 [texture](Texture-Formats#tpc) variations)
- Evil [texture](Texture-Formats#tpc) columns: `texaevil`, `texbevil`, `texievil`, `texlevil`, `texnevil`
- Head [texture](Texture-Formats#tpc) columns: `headtexe`, `headtexg`, `headtexve`, `headtexvg`
- Movement: `walkdist`, `rundist`, `prefatckdist`, `moverate`
- Physical properties: `height`, `hitdist`, `hitradius`, `sizecategory`, `perceptiondist`
- Personal space: `perspace`, `creperspace`
- Camera: `cameraspace`, `cameraheightoffset`, `targetheight`
- Head tracking: `headArcH`, `headArcV`, `headtrack`
- Body parts: `hasarms`, `haslegs`, `groundtilt`, `wingTailScale`
- Footsteps: `footsteptype`, `footstepsound`, `footstepvolume`
- Sounds: `armorSound`, `combatSound`, `soundapptype`
- Visual effects: `deathvfx`, `deathvfxnode`, `fadedelayondeath`, `freelookeffect`
- Equipment: `equipslotslocked`, `weaponscale`, `helmetScaleF`, `helmetScaleM`
- [textures](Texture-Formats#tpc): `envmap`, `skin`, `portrait`, `race`, `racetex`, `racialtype`
- Heads: `normalhead`, `backuphead`, `headbone`
- Vehicle: `driveaccl`, `drivemaxspeed`, `driveanimwalk`, `driveanimrunPc`, `driveanimrunXbox`
- Other: `bloodcolr`, `bodyBag`, `stringRef`, `abortonparry`, `destroyobjectdelay`, `disableinjuredanim`

These `appearance.2da` columns are reflected in PyKotor's 2DA extraction metadata and registry mappings ([`twoda.py` L73](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L73), [`twoda.py` L155](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L155), [`twoda.py` L168](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L168), [`twoda.py` L213-L214](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L213-L214), [`twoda.py` L248](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L248), [`twoda.py` L456](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L456), [`twoda.py` L524](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L524)). The Holocron Toolset uses the same table for appearance selectors in UTC/UTP/UTD/UTE editors ([`installation.py` L55](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L55), [`utc.py`](https://github.com/OldRepublicDevs/HolocronToolset/src/toolset/gui/editors/utc.py), [`utp.py` L124-L131](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utp.py#L124-L131), [`utd.py`](https://github.com/OldRepublicDevs/HolocronToolset/src/toolset/gui/editors/utd.py), [`ute.py` L181](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/ute.py#L181)). Runtime usage and column parsing are visible in reone's table parser and creature systems ([`appearance.cpp` L28-L125](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/parser/2da/appearance.cpp#L28-L125), [`creature.cpp` L98-L107](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/creature.cpp#L98-L107), [`creature.cpp` L1156-L1228](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/creature.cpp#L1156-L1228)).

### [baseitems.2da](#baseitems2da)

**Engine Usage**: Defines base item types that form the foundation for all items in the game. Each row represents a base item type (*weapon*, *armor*, *shield*, etc.) with properties like damage dice, weapon categories, equipment slots, and item flags. The engine uses this file to determine item behavior, combat statistics, and equipment compatibility.

**Row index**: Base item ID (*integer*)

**Column structure** (columns accessed by reone):

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Item type label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for item type name |
| `basecost` | *Integer* | Base gold cost |
| `stacking` | *Integer* | Stack size limit |
| `invslotwidth` | *Integer* | Inventory slot width |
| `invslotheight` | *Integer* | Inventory slot height |
| `canrotateicon` | *Boolean* (optional) | Whether icon can be rotated in inventory |
| `itemclass` | *Integer* | Item class identifier |
| `weapontype` | *Integer* | Weapon type (if weapon) |
| `weaponsize` | *Integer* | Weapon size category |
| `weaponwield` | *Integer* | Wield type (one-handed, two-handed, etc.) |
| `damagedice` | *Integer* | Damage dice count |
| `damagedie` | *Integer* | Damage die size |
| `damagebonus` | *Integer* | Base damage bonus |
| `damagetype` | *Integer* | Damage type flags |
| `weaponmattype` | *Integer* | Weapon [material](MDL-MDX-File-Format#trimesh-header) type |
| `weaponsound` | *Integer* | Weapon sound type |
| `ammunitiontype` | *Integer* | Ammunition type required |
| `rangedweapon` | *Boolean* | Whether item is a ranged weapon |
| `maxattackrange` | *Integer* | Maximum attack range |
| `preferredattackrange` | *Integer* | Preferred attack range |
| `attackmod` | *Integer* | Attack modifier |
| `damagebonusfeat` | *Integer* | Feat ID for damage bonus |
| `weaponfocustype` | *Integer* | Weapon focus type |
| `weaponfocusfeat` | *Integer* | Weapon focus feat ID |
| `description` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for item description |
| `icon` | *ResRef* | Icon image *ResRef* |
| `equipableslots` | *Integer* | Equipment slot flags |
| `model1` through `model6` | *ResRef* (optional) | 3D [model](MDL-MDX-File-Format) *ResRefs* for different variations |
| `partenvmap` | *ResRef* (optional) | Partial environment map [texture](Texture-Formats#tpc) |
| `defaultmodel` | *ResRef* (optional) | Default [model](MDL-MDX-File-Format) *ResRef* |
| `defaulticon` | *ResRef* (optional) | Default icon *ResRef* |
| `container` | *Boolean* | Whether item is a container |
| `weapon` | *Boolean* | Whether item is a weapon |
| `armor` | *Boolean* | Whether item is armor |
| `chargesstarting` | *Integer* | Starting charges (for usable items) |
| `costpercharge` | *Integer* | Cost per charge to recharge |
| `addcost` | *Integer* | Additional cost modifier |
| `stolen` | *Boolean* | Whether item is marked as stolen |
| `minlevel` | *Integer* | Minimum level requirement |
| `stacking` | *Integer* | Maximum stack size |
| `reqfeat0` through `reqfeat3` | *Integer* (optional) | Required feat IDs |
| `reqfeatcount0` through `reqfeatcount3` | *Integer* (optional) | Required feat counts |
| `reqclass` | *Integer* (optional) | Required class ID |
| `reqrace` | *Integer* (optional) | Required race ID |
| `reqalign` | *Integer* (optional) | Required alignment |
| `reqdeity` | *Integer* (optional) | Required deity ID |
| `reqstr` | *Integer* (optional) | Required strength |
| `reqdex` | *Integer* (optional) | Required dexterity |
| `reqint` | *Integer* (optional) | Required intelligence |
| `reqwis` | *Integer* (optional) | Required wisdom |
| `reqcon` | *Integer* (optional) | Required constitution |
| `reqcha` | *Integer* (optional) | Required charisma |

**Column Details** (from reone implementation):

The following columns are accessed by the game engine:

- `maxattackrange`: Maximum attack range for ranged weapons
- `crithitmult`: Critical hit multiplier
- `critthreat`: Critical threat range
- `damageflags`: Damage type flags
- `dietoroll`: Damage die size
- `equipableslots`: Equipment slot flags (*hex integer*)
- `itemclass`: Item class identifier (*string*)
- `numdice`: Number of damage dice
- `weapontype`: Weapon type identifier
- `weaponwield`: Weapon wield type (*one-handed*, *two-handed*, etc.)
- `bodyvar`: Body variation for armor
- `ammunitiontype`: Ammunition type ID (used to look up `ammunitiontypes.2da`). These `baseitems.2da` columns are reflected in PyKotor's 2DA extraction metadata ([PyKotor L169](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L169), [L187](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L187), [L215](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L215), [L225](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L225), [L466](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L466), [L537](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L537)). The Holocron Toolset uses this table via its HTInstallation registry and inventory/item editor integration ([installation.py L65](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L65), [L594-L607](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L594-L607), [L609-L620](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L609-L620), [L630-L643](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L630-L643), [uti.py L107-L117](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L107-L117), [inventory.py L668-L704](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/dialogs/inventory.py#L668-L704)). Runtime engine implementations from the reone project ([item.cpp L126-L136](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/item.cpp#L126-L136), [L160-L171](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/item.cpp#L160-L171)) demonstrate base item column access and ammunition type lookup patterns.

---

### [classes.2da](#classes2da)

**Engine Usage**: Defines character classes with their progression tables, skill point calculations, hit dice, saving throw progressions, and feat access. The engine uses this file to determine class abilities, skill point allocation, and level progression mechanics.

**Row index**: Class ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Class label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for class name |
| `description` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for class description |
| `hitdie` | *Integer* | Hit dice size (d6, d8, d10, etc.) |
| `skillpointbase` | *Integer* | Base skill points per level |
| `skillpointbonus` | *Integer* | Intelligence bonus skill points |
| `attackbonus` | *String* | Attack bonus progression table reference |
| `savingthrow` | *String* | Saving throw progression table reference |
| `savingthrowtable` | *String* | Saving throw table filename |
| `spellgaintable` | *String* | Spell/Force power gain table reference |
| `spellknowntable` | *String* | Spell/Force power known table reference |
| `primaryability` | *Integer* | Primary ability score for class |
| `preferredalignment` | *Integer* | Preferred alignment |
| `alignrestrict` | *Integer* | Alignment restrictions |
| `classfeat` | *Integer* | Class-specific feat ID |
| `classskill` | *Integer* | Class skill flags |
| `skillpointmaxlevel` | *Integer* | Maximum level for skill point calculation |
| `spellcaster` | *Integer* | Spellcasting level (0 = non-caster) |
| `spellcastingtype` | *Integer* | Spellcasting type identifier |
| `spelllevel` | *Integer* | Maximum spell level |
| `spellbook` | *ResRef* (optional) | Spellbook *ResRef* |
| `icon` | *ResRef* | Class icon *ResRef* |
| `portrait` | *ResRef* (optional) | Class portrait *ResRef* |
| `startingfeat0` through `startingfeat9` | *Integer* (optional) | Starting feat IDs |
| `startingpack` | *Integer* (optional) | Starting equipment pack ID |
| `description` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | Class description string reference |

**Column Details** (from reone implementation):

The following columns are accessed by the game engine:

- `name`: *String* reference for class name
- `description`: *String* reference for class description
- `hitdie`: Hit dice size
- `skillpointbase`: Base skill points per level
- `str`, `dex`, `con`, `int`, `wis`, `cha`: Default ability scores
- `skillstable`: Skills table reference (used to check class skills in `skills.2da`)
- `savingthrowtable`: Saving throw table reference (e.g., `cls_savthr_jedi_guardian`)
- `attackbonustable`: Attack bonus table reference (e.g., `cls_atk_jedi_guardian`). PyKotor defines string-reference columns for class.2da across both games ([L75](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L75) for K1, [L250](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L250) for K2) and registers the table via TwoDARegistry.CLASSES ([L463](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L463)), with GFF mapping for creature class fields ([L531](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L531)). The Holocron Toolset caches and uses classes.2da in the UTC editor for class selection ([installation.py L62](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L62), [utc.py L242](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utc.py#L242), [L256](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utc.py#L256), [L291-L298](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utc.py#L291-L298)). The reone implementation demonstrates class loading ([class.cpp L34-L56](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/d20/class.cpp#L34-L56)) and progression table integration ([L58-L86](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/d20/class.cpp#L58-L86)).

---

### [feat.2da](#feat2da)

**Engine Usage**: Defines all feats available in the game, including combat feats, skill feats, Force feats, and class-specific abilities. The engine uses this file to determine feat prerequisites, effects, and availability during character creation and level-up.

**Row index**: Feat ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Feat label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for feat name |
| `description` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for feat description |
| `icon` | *ResRef* | Feat icon *ResRef* |
| `takentext` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for "feat taken" message |
| `prerequisite` | *Integer* (optional) | Prerequisite feat ID |
| `minattackbonus` | *Integer* (optional) | Minimum attack bonus requirement |
| `minstr` | *Integer* (optional) | Minimum strength requirement |
| `mindex` | *Integer* (optional) | Minimum dexterity requirement |
| `minint` | *Integer* (optional) | Minimum intelligence requirement |
| `minwis` | *Integer* (optional) | Minimum wisdom requirement |
| `mincon` | *Integer* (optional) | Minimum constitution requirement |
| `mincha` | *Integer* (optional) | Minimum charisma requirement |
| `minlevel` | *Integer* (optional) | Minimum character level |
| `minclasslevel` | *Integer* (optional) | Minimum class level |
| `minspelllevel` | *Integer* (optional) | Minimum spell level |
| `spellid` | *Integer* (optional) | Required spell ID |
| `successor` | *Integer* (optional) | Successor feat ID (for feat chains) |
| `maxrank` | *Integer* (optional) | Maximum rank for stackable feats |
| `minrank` | *Integer* (optional) | Minimum rank requirement |
| `masterfeat` | *Integer* (optional) | Master feat ID |
| `targetself` | *Boolean* | Whether feat targets self |
| `orreqfeat0` through `orreqfeat4` | *Integer* (optional) | Alternative prerequisite feat IDs |
| `reqskill` | *Integer* (optional) | Required skill ID |
| `reqskillrank` | *Integer* (optional) | Required skill rank |
| `constant` | *Integer* (optional) | Constant value for feat calculations |
| `toolscategories` | *Integer* (optional) | Tool categories flags |
| `effecticon` | *ResRef* (optional) | Effect icon *ResRef* |
| `effectdesc` | [StrRef](Audio-and-Localization-Formats#string-references-strref) (optional) | Effect description string reference |
| `effectcategory` | *Integer* (optional) | Effect category identifier |
| `allclassescanuse` | *Boolean* | Whether all classes can use this feat |
| `category` | *Integer* | Feat category identifier |
| `maxcr` | *Integer* (optional) | Maximum challenge rating |
| `spellid` | *Integer* (optional) | Associated spell ID |
| `usesperday` | *Integer* (optional) | Uses per day limit |
| `masterfeat` | *Integer* (optional) | Master feat ID for feat trees |

**Column Details** (from reone implementation):

The following columns are accessed by the reone engine:

- `name`: *String* reference for feat name
- `description`: *String* reference for feat description
- `icon`: Icon *ResRef*
- `mincharlevel`: Minimum character level (hex integer)
- `prereqfeat1`: Prerequisite feat ID 1 (hex integer)
- `prereqfeat2`: Prerequisite feat ID 2 (hex integer)
- `successor`: Successor feat ID (hex integer)
- `pips`: Feat pips/ranks (hex integer)
- `allclassescanuse`: Boolean - whether all classes can use this feat
- `masterfeat`: Master feat ID
- `orreqfeat0` through `orreqfeat4`: Alternative prerequisite feat IDs
- `hostilefeat`: Boolean - whether feat is hostile
- `category`: Feat category identifier. PyKotor provides comprehensive feat.2da column definitions for both games ([L82](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L82) for K1 string references, [L260](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L260) for K2), icons ([L227](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L227)), and GFF field mappings ([L561-L562](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L561-L562)), alongside UTC creature feat list documentation ([utc.py L321-L323](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L321-L323), [L432](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L432), [L762-L768](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L762-L768), [L907-L909](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L907-L909)). The Holocron Toolset includes feat.2da via TwoDARegistry ([installation.py L63](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L63)). Runtime implementations include reone's feat loading ([feats.cpp L32-L58](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/d20/feats.cpp#L32-L58)) and KotOR.js feat structures ([TalentFeat.ts L36-L53](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/talents/TalentFeat.ts#L36-L53), [L122-L132](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/talents/TalentFeat.ts#L122-L132)).

---

### [skills.2da](#skills2da)

**Engine Usage**: Defines all skills available in the game, including which classes can use them, their key ability scores, and skill descriptions. The engine uses this file to determine skill availability, skill point costs, and skill checks.

**Row index**: Skill ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Skill label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for skill name |
| `description` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for skill description |
| `keyability` | *Integer* | key ability score (STR, DEX, INT, etc.) |
| `armorcheckpenalty` | *Boolean* | Whether armor check penalty applies |
| `allclassescanuse` | *Boolean* | Whether all classes can use this skill |
| `category` | *Integer* | Skill category identifier |
| `maxrank` | *Integer* | Maximum skill rank |
| `untrained` | *Boolean* | Whether skill can be used untrained |
| `constant` | *Integer* (optional) | Constant modifier |
| `hostileskill` | *Boolean* | Whether skill is hostile |
| `icon` | *ResRef* (optional) | Skill icon *ResRef* |

**Column Details** (from reone implementation):

The following columns are accessed by the reone engine:

- `name`: *String* reference for skill name
- `description`: *String* reference for skill description
- `icon`: Icon *ResRef*
- Dynamic class skill columns: For each class, there is a column named `{classname}_class` (e.g., `jedi_guardian_class`) that contains `1` if the skill is a class skill for that class
- `droidcanuse`: Boolean - whether droids can use this skill
- `npccanuse`: Boolean - whether NPCs can use this skill. PyKotor defines skill.2da string-reference columns across both games ([L148](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L148) for K1, [L326](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L326) for K2), maintains TwoDARegistry.SKILLS ([L472](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L472)), and maps GFF skill references ([L563](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L563)). The Holocron Toolset integrates skills.2da through its HTInstallation registry ([installation.py L71](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L71)) and displays skill tables in the save game editor ([savegame.py L129](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/savegame.py#L129), [L511-L519](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/savegame.py#L511-L519), [L542-L543](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/savegame.py#L542-L543)). Vendor implementations include reone's skill loading with dynamic column name handling ([skills.cpp L32-L48](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/d20/skills.cpp#L32-L48), [class.cpp L58-L65](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/d20/class.cpp#L58-L65)) and KotOR.js skill loading ([TalentSkill.ts L38-L49](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/talents/TalentSkill.ts#L38-L49)).

---

### [spells.2da](#spells2da)

**Engine Usage**: Defines all Force powers (and legacy spell entries) in KotOR, including their costs, targeting modes, visual effects, and descriptions. The engine uses this file to determine Force power availability, casting requirements, and effects. Note: KotOR uses Force powers rather than traditional D&D spells, though the file structure is inherited from the Aurora engine (originally designed for Neverwinter Nights).

**Row index**: Spell ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Spell label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for spell name |
| `school` | *Integer* | Spell school identifier |
| `range` | *Integer* | Spell range type |
| `vs` | *Integer* | Versus type (self, touch, etc.) |
| `metamagic` | *Integer* | Metamagic flags |
| `targettype` | *Integer* | Target type flags |
| `impactscript` | *ResRef* (optional) | Impact script *ResRef* |
| `innate` | *Integer* | Innate Force power level (0 = not available) |
| `conjtime` | *Float* | Casting/conjuration time |
| `conjtimevfx` | *Integer* (optional) | Casting time visual effect |
| `conjheadvfx` | *Integer* (optional) | Casting head visual effect |
| `conjhandvfx` | *Integer* (optional) | Casting hand visual effect |
| `conjgrndvfx` | *Integer* (optional) | Casting ground visual effect |
| `conjcastvfx` | *Integer* (optional) | Casting visual effect |
| `conjimpactscript` | *ResRef* (optional) | Conjuration impact script |
| `conjduration` | *Float* | Conjuration duration |
| `conjrange` | *Integer* | Conjuration range |
| `conjca` | *Integer* | Conjuration casting [animation](MDL-MDX-File-Format#animation-header) |
| `conjca2` through `conjca50` | *Integer* (optional) | Additional casting animations (numbered 2-50) |
| `hostilesetting` | *Integer* | Hostile setting flags |
| `featid` | *Integer* (optional) | Associated feat ID |
| `counter1` | *Integer* (optional) | Counter spell ID 1 |
| `counter2` | *Integer* (optional) | Counter spell ID 2 |
| `counter3` | *Integer* (optional) | Counter spell ID 3 |
| `projectile` | *ResRef* (optional) | Projectile [model](MDL-MDX-File-Format) *ResRef* |
| `projectilesound` | *ResRef* (optional) | Projectile sound *ResRef* |
| `projectiletype` | *Integer* | Projectile type identifier |
| `projectileorient` | *Integer* | Projectile orientation |
| `projectilepath` | *Integer* | Projectile path type |
| `projectilehoming` | *Boolean* | Whether projectile homes on target |
| `projectilemodel` | *ResRef* (optional) | Projectile 3D [model](MDL-MDX-File-Format) *ResRef* |
| `projectilemodel2` through `projectilemodel50` | *ResRef* (optional) | Additional projectile models (numbered 2-50) |
| `icon` | *ResRef* | Spell icon *ResRef* |
| `icon2` through `icon50` | *ResRef* (optional) | Additional icons (numbered 2-50) |
| `description` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | Spell description string reference |
| `altmessage` | [StrRef](Audio-and-Localization-Formats#string-references-strref) (optional) | Alternative message string reference |
| `usewhencast` | *Integer* | Use when cast flags |
| `blood` | *Boolean* | Whether spell causes blood effects |
| `concentration` | *Integer* | Concentration check DC |
| `immunitytype` | *Integer* | Immunity type identifier |
| `immunitytype2` through `immunitytype50` | *Integer* (optional) | Additional immunity types (numbered 2-50) |
| `immunityitem` | *Integer* | Immunity item type |
| `immunityitem2` through `immunityitem50` | *Integer* (optional) | Additional immunity items (numbered 2-50) |

**Column Details** (from reone implementation):

The following columns are accessed by the reone engine:

- `name`: *String* reference for spell name
- `spelldesc`: *String* reference for spell description (note: column name is `spelldesc`, not `description`)
- `iconresref`: Icon ResRef (note: column name is `iconresref`, not `icon`)
- `pips`: Spell pips/ranks (hex integer)
- `conjtime`: Conjuration/casting time
- `casttime`: Cast time
- `catchtime`: Catch time
- `conjanim`: Conjuration [animation](MDL-MDX-File-Format#animation-header) type (e.g., "throw", "up")
- `hostilesetting`: Hostile setting flags
- `projectile`: Projectile *ResRef*
- `projectileHook`: Projectile hook point
- `projectileOrigin`: Projectile origin point
- `projectileTarget`: Projectile target point
- `projectileCurve`: Projectile curve type
- `projmodel`: Projectile [model](MDL-MDX-File-Format) *ResRef*
- `range`: Spell range
- `impactscript`: Impact script *ResRef*
- `casthandvisual`: Cast hand visual effect

**Note**: The `spells.2da` file contains many optional columns for projectile [models](MDL-MDX-File-Format), icons, and immunity types (numbered 1-50). These are used for spell variations and visual effects.

These spell column semantics are corroborated by PyKotor's K1/K2 schema mappings and registry entries ([`twoda.py` L149](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L149), [`twoda.py` L327](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L327), [`twoda.py` L239](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L239), [`twoda.py` L432](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L432), [`twoda.py` L709](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L709), [`twoda.py` L558-L560](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L558-L560), [`scriptdefs.py` L9380-L9381](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L9380-L9381), [`scriptlib.py` L5676](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptlib.py#L5676)) and by tool/runtime consumers in Holocron Toolset and open engines ([`installation.py` L110](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L110), [`spells.cpp` L32-L48](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/d20/spells.cpp#L32-L48), [`TalentSpell.ts` L16-L44](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/talents/TalentSpell.ts#L16-L44), [`TalentSpell.ts` L42-L53](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/talents/TalentSpell.ts#L42-L53)).

---

## Items & Properties 2DA files

### itemprops.2da

**Engine Usage**: Master table defining all item property types available in the game. Each row represents a property type (damage bonuses, ability score bonuses, skill bonuses, etc.) with their cost calculations and effect parameters. The engine uses this file to determine item property costs, effects, and availability.

**Row index**: Item property ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for property name |
| `costtable` | *String* | Cost calculation table reference |
| `param1` | *String* | Parameter 1 label |
| `param2` | *String* | Parameter 2 label |
| `subtype` | *Integer* | Property subtype identifier |
| `costvalue` | *Integer* | Base cost value |
| `param1value` | *Integer* | Parameter 1 default value |
| `param2value` | *Integer* | Parameter 2 default value |
| `description` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | Property description string reference |

The item property schema and behavior are evidenced by PyKotor K1/K2 field declarations plus editor/runtime consumers that load and resolve cost/parameter data from this table ([`twoda.py` L135](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L135), [`twoda.py` L313](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L313), [`installation.py` L74](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L74), [`uti.py` L107-L111](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L107-L111), [`uti.py` L278-L287](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L278-L287), [`uti.py` L449-L465](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L449-L465)).

---


### iprp_damagecost.2da

**Engine Usage**: Defines cost calculations for damage bonus item properties. Used to determine item property costs based on damage bonus values.

**Row index**: Damage bonus value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Damage bonus label |
| `cost` | *Integer* | Cost for this damage bonus value |

This table's naming and cost schema are tracked in both K1 and K2 column maps in PyKotor ([`twoda.py` L99](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L99), [`twoda.py` L277](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L277)).

---

## Objects & Area 2DA files

### [placeables.2da](#placeables2da)

**Engine Usage**: Defines placeable objects (containers, usable objects, interactive elements) with their [models](MDL-MDX-File-Format), properties, and behaviors. The engine uses this file when loading placeable objects in areas, determining their [models](MDL-MDX-File-Format), hit detection, and interaction properties.

**Row index**: Placeable type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | String (optional) | Placeable type label |
| `modelname` | *ResRef* (optional) | 3D [model](MDL-MDX-File-Format) *ResRef* |
| `strref` | *Integer* | *String* reference for placeable name |
| `bodybag` | *Boolean* | Whether placeable can contain bodies |
| `canseeheight` | *Float* | Can-see height for line of sight |
| `hitcheck` | *Boolean* | Whether hit detection is enabled |
| `hostile` | *Boolean* | Whether placeable is hostile |
| `ignorestatichitcheck` | *Boolean* | Whether to ignore static hit checks |
| `lightcolor` | String (optional) | Light color RGB values |
| `lightoffsetx` | String (optional) | Light X offset |
| `lightoffsety` | String (optional) | Light Y offset |
| `lightoffsetz` | String (optional) | Light Z offset |
| `lowgore` | String (optional) | Low gore [model](MDL-MDX-File-Format) *ResRef* |
| `noncull` | *Boolean* | Whether to disable culling |
| `preciseuse` | *Boolean* | Whether precise use is enabled |
| `shadowsize` | *Boolean* | Whether shadow size is enabled |
| `soundapptype` | *Integer* (optional) | Sound appearance type |
| `usesearch` | *Boolean* | Whether placeable can be searched |

**Column Details**:

The complete column structure is defined in reone's placeables parser:

- `label`: Optional label string
- `modelname`: 3D [model](MDL-MDX-File-Format) *ResRef*
- `strref`: *String* reference for placeable name
- `bodybag`: Boolean - whether placeable can contain bodies
- `canseeheight`: Float - can-see height for line of sight
- `hitcheck`: Boolean - whether hit detection is enabled
- `hostile`: Boolean - whether placeable is hostile
- `ignorestatichitcheck`: Boolean - whether to ignore static hit checks
- `lightcolor`: Optional string - light color RGB values
- `lightoffsetx`: Optional string - light X offset
- `lightoffsety`: Optional string - light Y offset
- `lightoffsetz`: Optional string - light Z offset
- `lowgore`: Optional string - low gore [model](MDL-MDX-File-Format) *ResRef*
- `noncull`: Boolean - whether to disable culling
- `preciseuse`: Boolean - whether precise use is enabled
- `shadowsize`: Boolean - whether shadow size is enabled
- `soundapptype`: Optional integer - sound appearance type
- `usesearch`: Boolean - whether placeable can be searched

Placeables column semantics and runtime usage are backed by PyKotor K1/K2 column/type definitions and registry mappings ([`twoda.py` L141](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L141), [`twoda.py` L170](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L170), [`twoda.py` L319](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L319), [`twoda.py` L349](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L349), [`twoda.py` L467](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L467), [`twoda.py` L542](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L542)), editor integration in Holocron Toolset ([`installation.py` L66](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L66), [`utp.py` L52](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utp.py#L52), [`utp.py` L62](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utp.py#L62), [`utp.py` L121-L131](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utp.py#L121-L131), [`utp.py` L471](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utp.py#L471)), and vendor parsing/loading in reone ([`placeables.cpp` L29-L49](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/parser/2da/placeables.cpp#L29-L49), [`placeable.cpp` L59-L60](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/placeable.cpp#L59-L60)).

---

### [genericdoors.2da](#genericdoors2da)

**Engine Usage**: Defines door types and how they behave in areas. The engine consults this file when loading doors to choose:

- [models](MDL-MDX-File-Format)
- [animations](MDL-MDX-File-Format#animation-header)
- Associated properties and which [model](MDL-MDX-File-Format) to display

**Row index**: Door type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Door type label |
| `modelname` | *ResRef* | 3D [model](MDL-MDX-File-Format) *ResRef* |
| `name` | String (optional) | Door type name |
| `strref` | *Integer* (optional) | *String* reference for door name |
| `blocksight` | *Boolean* | Whether door blocks line of sight |
| `nobin` | *Boolean* | Whether door has no bin (container) |
| `preciseuse` | *Boolean* | Whether precise use is enabled |
| `soundapptype` | *Integer* (optional) | Sound appearance type |
| `staticanim` | String (optional) | Static [animation](MDL-MDX-File-Format#animation-header) *ResRef* |
| `visiblemodel` | *Boolean* | Whether [model](MDL-MDX-File-Format) is visible |

**Column Details**:

The complete column structure is defined in reone's genericdoors parser:

- `label`: Door type label
- `modelname`: 3D [model](MDL-MDX-File-Format) *ResRef*
- `name`: Optional door type name string
- `strref`: Optional integer - *String* reference for door name
- `blocksight`: Boolean - whether door blocks line of sight
- `nobin`: Boolean - whether door has no bin (container)
- `preciseuse`: Boolean - whether precise use is enabled
- `soundapptype`: Optional integer - sound appearance type
- `staticanim`: Optional string - static [animation](MDL-MDX-File-Format#animation-header) *ResRef*
- `visiblemodel`: Boolean - whether [model](MDL-MDX-File-Format) is visible

Generic door semantics are validated by PyKotor's K1/K2 mappings for doortypes and genericdoors plus registry/GFF linkages ([`twoda.py` L78](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L78), [`twoda.py` L86](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L86), [`twoda.py` L177-L178](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L177-L178), [`twoda.py` L256-L264](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L256-L264), [`twoda.py` L356-L357](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L356-L357), [`twoda.py` L468](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L468), [`twoda.py` L543](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L543)); the same table is consumed by Toolset door editors and by reone's parser/runtime load path ([`installation.py` L67](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L67), [`utd.py` L60](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utd.py#L60), [`utd.py` L117-L123](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utd.py#L117-L123), [`utd.py` L409](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utd.py#L409), [`genericdoors.cpp` L29-L41](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/parser/2da/genericdoors.cpp#L29-L41), [`door.cpp` L66-L67](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/door.cpp#L66-L67)).

---

### [doortypes.2da](#doortypes2da)

**Engine Usage**: Defines door type configurations and their properties. The engine uses this file to determine door type names, [models](MDL-MDX-File-Format), and behaviors.

**Row index**: Door type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Door type label |
| `stringrefgame` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for door type name |
| `model` | *ResRef* | [model](MDL-MDX-File-Format) *ResRef* for the door type |
| Additional columns | Various | Door type properties |

The doortypes table itself is anchored in the same K1/K2 extraction mappings used by PyKotor's 2DA schema index ([`twoda.py` L78](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L78), [`twoda.py` L177](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L177)).

---

### [soundset.2da](#soundset2da)

**Engine Usage**: Maps sound set IDs to voice set assignments for characters. The engine uses this file to determine which voice lines to play for characters based on their sound set.

**Row index**: Sound set ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Sound set label |
| `resref` | *ResRef* | [sound set files](Audio-and-Localization-Formats#ssf) ResRef (e.g., `c_human_m_01`) |

This soundset schema is validated across PyKotor table mappings and UTC field usage ([`twoda.py` L143](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L143), [`twoda.py` L321](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L321), [`twoda.py` L459](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L459), [`twoda.py` L522](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L522), [`utc.py` L90-L92](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L90-L92), [`utc.py` L359](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L359), [`utc.py` L549-L550](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L549-L550), [`utc.py` L821](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L821)), Toolset bindings ([`installation.py` L58](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L58), [`utc.ui` L260-L267](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/ui/editors/utc.ui#L260-L267)), and runtime loading in reone ([`creature.cpp` L1347-L1354](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/creature.cpp#L1347-L1354)).

---

## Visual Effects & [animations](MDL-MDX-File-Format#animation-header) 2DA files

### [visualeffects.2da](#visualeffects2da)

**Engine Usage**: Defines visual effects (particle effects, impact effects, environmental effects) with their durations, [models](MDL-MDX-File-Format), and properties. The engine uses this file when playing visual effects for spells, combat, and environmental events.

**Row index**: Visual effect ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Visual effect label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for effect name |
| `model` | *ResRef* (optional) | Effect [model](MDL-MDX-File-Format) *ResRef* |
| `impactmodel` | *ResRef* (optional) | Impact [model](MDL-MDX-File-Format) *ResRef* |
| `impactorient` | *Integer* | Impact orientation |
| `impacttype` | *Integer* | Impact type identifier |
| `duration` | *Float* | Effect duration in seconds |
| `durationvariance` | *Float* | Duration variance |
| `loop` | *Boolean* | Whether effect loops |
| `render` | *Boolean* | Whether effect is rendered |
| `renderhint` | *Integer* | Render hint flags |
| `sound` | *ResRef* (optional) | Sound effect *ResRef* |
| `sounddelay` | *Float* | Sound delay in seconds |
| `soundvariance` | *Float* | Sound variance |
| `soundloop` | *Boolean* | Whether sound loops |
| `soundvolume` | *Float* | Sound volume (0.0-1.0) |
| `light` | *Boolean* | Whether effect emits light |
| `lightcolor` | *String* | Light color RGB values |
| `lightintensity` | *Float* | Light intensity |
| `lightradius` | *Float* | Light radius |
| `lightpulse` | *Boolean* | Whether light pulses |
| `lightpulselength` | *Float* | Light pulse length |
| `lightfade` | *Boolean* | Whether light fades |
| `lightfadelength` | *Float* | Light fade length |
| `lightfadestart` | *Float* | Light fade start time |
| `lightfadeend` | *Float* | Light fade end time |
| `lightshadow` | *Boolean* | Whether light casts shadows |
| `lightshadowradius` | *Float* | Light shadow radius |
| `lightshadowintensity` | *Float* | Light shadow intensity |
| `lightshadowcolor` | *String* | Light shadow color RGB values |
| `lightshadowfade` | *Boolean* | Whether light shadow fades |
| `lightshadowfadelength` | *Float* | Light shadow fade length |
| `lightshadowfadestart` | *Float* | Light shadow fade start time |
| `lightshadowfadeend` | *Float* | Light shadow fade end time |
| `lightshadowpulse` | *Boolean* | Whether light shadow pulses |
| `lightshadowpulselength` | *Float* | Light shadow pulse length |
| `lightshadowpulseintensity` | *Float* | Light shadow pulse intensity |
| `lightshadowpulsecolor` | *String* | Light shadow pulse color RGB values |
| `lightshadowpulsefade` | *Boolean* | Whether light shadow pulse fades |
| `lightshadowpulsefadelength` | *Float* | Light shadow pulse fade length |
| `lightshadowpulsefadestart` | *Float* | Light shadow pulse fade start time |
| `lightshadowpulsefadeend` | *Float* | Light shadow pulse fade end time |
| `lightshadowpulsefadeintensity` | *Float* | Light shadow pulse fade intensity |
| `lightshadowpulsefadecolor` | *String* | Light shadow pulse fade color RGB values |
| `lightshadowpulsefadepulse` | *Boolean* | Whether light shadow pulse fade pulses |
| `lightshadowpulsefadepulselength` | *Float* | Light shadow pulse fade pulse length |
| `lightshadowpulsefadepulseintensity` | *Float* | Light shadow pulse fade pulse intensity |
| `lightshadowpulsefadepulsecolor` | *String* | Light shadow pulse fade pulse color RGB values |
| `lightshadowpulsefadepulsefade` | *Boolean* | Whether light shadow pulse fade pulse fades |
| `lightshadowpulsefadepulsefadelength` | *Float* | Light shadow pulse fade pulse fade length |
| `lightshadowpulsefadepulsefadestart` | *Float* | Light shadow pulse fade pulse fade start time |
| `lightshadowpulsefadepulsefadeend` | *Float* | Light shadow pulse fade pulse fade end time |
| `lightshadowpulsefadepulsefadeintensity` | *Float* | Light shadow pulse fade pulse fade intensity |
| `lightshadowpulsefadepulsefadecolor` | *String* | Light shadow pulse fade pulse fade color RGB values |

**Note**: The `visualeffects.2da` file may contain many optional columns for advanced lighting and shadow effects.

Visual effect table linkage is implemented in PyKotor's GFF-to-2DA mapping (`VisualType` -> `visualeffects.2da`) ([`twoda.py` L593](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L593)).

---

### [portraits.2da](#portraits2da)

**Engine Usage**: Maps portrait IDs to portrait image ResRefs for character selection screens and character sheets. The engine uses this file to display character portraits in the UI.

**Row index**: Portrait ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Portrait label |
| `baseresref` | *ResRef* | Base portrait image *ResRef* |
| `appearancenumber` | *Integer* | Associated appearance ID |
| `appearance_s` | *Integer* | Small appearance ID |
| `appearance_l` | *Integer* | Large appearance ID |
| `forpc` | *Boolean* | Whether portrait is for player character |
| `sex` | *Integer* | Gender (0=male, 1=female) |

Portrait table semantics and usage are supported by PyKotor registry/mapping and save-data handling ([`twoda.py` L455](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L455), [`twoda.py` L523](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L523), [`savedata.py` L66](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L66), [`savedata.py` L226-L228](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L226-L228), [`savedata.py` L241](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L241), [`savedata.py` L391](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L391), [`savedata.py` L456](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L456), [`savedata.py` L2157](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L2157), [`savedata.py` L2309](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L2309), [`savedata.py` L2370](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L2370)), Toolset editor/UI integration ([`installation.py` L54](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L54), [`utc.py` L140-L152](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utc.py#L140-L152), [`utc.ui` L407](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/ui/editors/utc.ui#L407), [`savegame.py` L51](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/savegame.py#L51), [`savegame.ui` L94-L98](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/ui/editors/savegame.ui#L94-L98)), and vendor runtime loading ([`portraits.cpp` L33-L51](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/portraits.cpp#L33-L51)).

---

### heads.2da

**Engine Usage**: Defines head assets for player characters and NPCs. When loading character heads, the engine uses this file to choose:

- [models](MDL-MDX-File-Format)
- [textures](Texture-Formats#tpc)
- Which 3D [model](MDL-MDX-File-Format) to apply
- Which [textures](Texture-Formats#tpc) to apply

**Row index**: Head ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `head` | *ResRef* (optional) | Head [model](MDL-MDX-File-Format) *ResRef* |
| `headtexe` | *ResRef* (optional) | Head [texture](Texture-Formats#tpc) E *ResRef* |
| `headtexg` | *ResRef* (optional) | Head [texture](Texture-Formats#tpc) G *ResRef* |
| `headtexve` | *ResRef* (optional) | Head [texture](Texture-Formats#tpc) VE *ResRef* |
| `headtexvg` | *ResRef* (optional) | Head [texture](Texture-Formats#tpc) VG *ResRef* |
| `headtexvve` | *ResRef* (optional) | Head [texture](Texture-Formats#tpc) VVE *ResRef* |
| `headtexvvve` | *ResRef* (optional) | Head [texture](Texture-Formats#tpc) VVVE *ResRef* |
| `alttexture` | *ResRef* (optional) | Alternative [texture](Texture-Formats#tpc) *ResRef* |

**Column Details**:

The complete column structure is defined in reone's heads parser:

- `head`: Optional *ResRef* - head [model](MDL-MDX-File-Format) *ResRef*
- `alttexture`: Optional *ResRef* - alternative [texture](Texture-Formats#tpc) *ResRef*
- `headtexe`: Optional *ResRef* - head [texture](Texture-Formats#tpc) for evil alignment
- `headtexg`: Optional *ResRef* - head [texture](Texture-Formats#tpc) for good alignment
- `headtexve`: Optional *ResRef* - head [texture](Texture-Formats#tpc) for very evil alignment
- `headtexvg`: Optional *ResRef* - head [texture](Texture-Formats#tpc) for very good alignment
- `headtexvve`: Optional *ResRef* - head [texture](Texture-Formats#tpc) for very very evil alignment
- `headtexvvve`: Optional *ResRef* - head [texture](Texture-Formats#tpc) for very very very evil alignment

These head columns are reflected in reone's table parser and creature head-loading runtime path ([`heads.cpp` L29-L39](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/parser/2da/heads.cpp#L29-L39), [`creature.cpp` L1223-L1228](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/creature.cpp#L1223-L1228)).

---

## Progression Tables 2DA Files

### classpowergain.2da

**Engine Usage**: Defines Force power progression by class and level. The engine uses this file to determine which Force powers are available to each class at each level.

**Row index**: Level (integer, typically 1-20)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `level` | *Integer* | Character level |
| `jedi_guardian` | *Integer* | Jedi Guardian power gain |
| `jedi_consular` | *Integer* | Jedi Consular power gain |
| `jedi_sentinel` | *Integer* | Jedi Sentinel power gain |
| `soldier` | *Integer* | Soldier power gain |
| `scout` | *Integer* | Scout power gain |
| `scoundrel` | *Integer* | Scoundrel power gain |
| `jedi_guardian_prestige` | *Integer* (optional) | Jedi Guardian prestige power gain |
| `jedi_consular_prestige` | *Integer* (optional) | Jedi Consular prestige power gain |
| `jedi_sentinel_prestige` | *Integer* (optional) | Jedi Sentinel prestige power gain |

---

## Name Generation 2DA Files

### Other Name Generation files

Similar name generation files exist for other species:

- `catharfirst.2da` / `catharlast.2da`: Cathar names (KotOR 2)
- `droidfirst.2da` / `droidlast.2da`: Droid names
- `miracianfirst.2da` / `miracianlast.2da`: Miraluka names (KotOR 2, alternate spelling)
- `miralukafirst.2da` / `miralukalast.2da`: Miraluka names (KotOR 2)
- `rodianfirst.2da` / `rodianlast.2da`: Rodian names
- `twilekfirst.2da` / `twileklast.2da`: Twi'lek names
- `wookieefirst.2da` / `wookieelast.2da`: Wookiee names
- `zabrakfirst.2da` / `zabraklast.2da`: Zabrak names

---

## Additional 2DA Files

### ambientmusic.2da

**Engine Usage**: Defines ambient music tracks for areas. The engine uses this file to determine which music to play in different areas based on [area properties](GFF-File-Format#are-area).

**Row index**: Music ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Music label |
| `music` | *ResRef* | Music file *ResRef* |
| `resource` | *ResRef* | Music resource *ResRef* |
| `stinger1`, `stinger2`, `stinger3` | *ResRef* (optional) | Stinger music ResRefs |

Ambient music columns and their ARE field bindings are represented in PyKotor's K1/K2 extraction maps and GFF linkage definitions ([`twoda.py` L206](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L206), [`twoda.py` L398](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L398), [`twoda.py` L545-L548](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L545-L548)).

---

### ambientsound.2da

**Engine Usage**: Defines ambient sound effects for areas. The engine uses this file to play ambient sounds in areas.

**Row index**: Sound ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Sound label |
| `sound` | *ResRef* | Sound file *ResRef* |
| `resource` | *ResRef* | Sound resource *ResRef* |
| `description` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | Sound description string reference |

Ambient sound column semantics are documented in PyKotor's K1/K2 schema maps and script-level API comments ([`twoda.py` L72](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L72), [`twoda.py` L184](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L184), [`twoda.py` L247](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L247), [`twoda.py` L376](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L376), [`scriptdefs.py` L6986-L6988](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L6986-L6988)).

---

### ammunitiontypes.2da

**Engine Usage**: Defines ammunition types for ranged weapons, including their [models](MDL-MDX-File-Format) and sound effects. The engine uses this file when loading items to determine ammunition properties for ranged weapons.

**Row index**: Ammunition type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Ammunition type label |
| `model` | *ResRef* | Ammunition [model](MDL-MDX-File-Format) *ResRef* |
| `shotsound0` | *ResRef* (optional) | Shot sound effect ResRef (variant 1) |
| `shotsound1` | *ResRef* (optional) | Shot sound effect ResRef (variant 2) |
| `impactsound0` | *ResRef* (optional) | Impact sound effect ResRef (variant 1) |
| `impactsound1` | *ResRef* (optional) | Impact sound effect ResRef (variant 2) |

Ammunition type consumption in runtime item loading is visible in reone's object pipeline ([`item.cpp` L164-L171](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/item.cpp#L164-L171)).

---

### camerastyle.2da

**Engine Usage**: Defines camera styles for areas, including distance, pitch, view angle, and height settings. The engine uses this file to configure camera behavior in different areas.

**Row index**: Camera Style ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Camera style label |
| `name` | *String* | Camera style name |
| `distance` | *Float* | Camera distance from target |
| `pitch` | *Float* | Camera pitch angle |
| `viewangle` | *Float* | Camera view angle |
| `height` | *Float* | Camera height offset |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:497`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L497) - TwoDARegistry.CAMERAS constant definition
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:550`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L550) - [GFF](GFF-File-Format) field mapping: "CameraStyle" -> camerastyle.2da
- [`Libraries/PyKotor/src/pykotor/resource/generics/are.py:37`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/are.py#L37) - are camera_style field documentation
- [`Libraries/PyKotor/src/pykotor/resource/generics/are.py:123`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/are.py#L123) - Camera style index comment
- [`Libraries/PyKotor/src/pykotor/resource/generics/are.py:442`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/are.py#L442) - CameraStyle field parsing from are [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/are.py:579`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/are.py#L579) - CameraStyle field writing to are [GFF](GFF-File-Format)

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:96`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L96) - HTInstallation.TwoDA_CAMERAS constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/are.py:102`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/are.py#L102) - camerastyle.2da loading in are editor

**Vendor Implementations:**

- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/camerastyles.cpp:29-42`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/camerastyles.cpp#L29-L42) - Camera style loading from [2DA](2DA-File-Format)
- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/object/area.cpp:140-148`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/area.cpp#L140-L148) - Camera style usage in areas

---

### footstepsounds.2da

**Engine Usage**: Defines footstep sound effects for different surface types and footstep types. The engine uses this file to play appropriate footstep sounds based on the surface material and creature footstep type.

**Row index**: Footstep type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Footstep type label |
| `dirt0`, `dirt1`, `dirt2` | *ResRef* (optional) | Dirt surface footstep sounds |
| `grass0`, `grass1`, `grass2` | *ResRef* (optional) | Grass surface footstep sounds |
| `stone0`, `stone1`, `stone2` | *ResRef* (optional) | Stone surface footstep sounds |
| `wood0`, `wood1`, `wood2` | *ResRef* (optional) | Wood surface footstep sounds |
| `water0`, `water1`, `water2` | *ResRef* (optional) | Water surface footstep sounds |
| `carpet0`, `carpet1`, `carpet2` | *ResRef* (optional) | Carpet surface footstep sounds |
| `metal0`, `metal1`, `metal2` | *ResRef* (optional) | Metal surface footstep sounds |
| `leaves0`, `leaves1`, `leaves2` | *ResRef* (optional) | Leaves surface footstep sounds |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:188-198`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L188-L198) - Sound *ResRef* column definitions for footstepsounds.2da (K1: rolling, dirt0-2, grass0-2, stone0-2, wood0-2, water0-2, carpet0-2, metal0-2, puddles0-2, leaves0-2, force1-3)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:380-390`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L380-L390) - Sound *ResRef* column definitions for footstepsounds.2da (K2: rolling, dirt0-2, grass0-2, stone0-2, wood0-2, water0-2, carpet0-2, metal0-2, puddles0-2, leaves0-2, force1-3)

**Vendor Implementations:**

- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/footstepsounds.cpp:31-57`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/footstepsounds.cpp#L31-L57) - Footstep sounds loading from [2DA](2DA-File-Format)
- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/object/creature.cpp:106`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/creature.cpp#L106) - Footstep type usage from [appearance.2da](#appearance2da)

---

### prioritygroups.2da

**Engine Usage**: Defines priority groups for sound effects, determining which sounds take precedence when multiple sounds are playing. The engine uses this file to calculate sound priority values.

**Row index**: Priority Group ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Priority group label |
| `priority` | *Integer* | Priority value (higher = more important) |

**References**:

**Vendor Implementations:**

- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/object/sound.cpp:92-96`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/sound.cpp#L92-L96) - Priority group loading from [2DA](2DA-File-Format)

---

### repute.2da

**Engine Usage**: Defines reputation values between different factions. The engine uses this file to determine whether creatures are enemies, friends, or neutral to each other based on their faction relationships.

**Row index**: Faction ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Faction label |
| Additional columns | *Integer* | Reputation values for each faction (column names match faction labels) |

**Note**: The `repute.2da` file is a square [matrix](Level-Layout-Formats#adjacencies-wok-only) where each row represents a faction, and each column (after `label`) represents the reputation value toward another faction. Reputation values typically range from 0-100, where values below 50 are enemies, above 50 are friends, and 50 is neutral.

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:460`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L460) - TwoDARegistry.FACTIONS constant definition (maps to "repute")
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:526-527`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L526-L527) - [GFF](GFF-File-Format) field mapping: "FactionID" and "Faction" -> repute.2da
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:92`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L92) - REPUTE.fac documentation comment
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:1593`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L1593) - REPUTE.fac file check comment
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:1627`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L1627) - REPUTE.fac documentation
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:1667`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L1667) - REPUTE_IDENTIFIER constant definition
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:1683-1684`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L1683-L1684) - repute [GFF](GFF-File-Format) field initialization
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:1759-1761`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L1759-L1761) - REPUTE.fac parsing
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:1795-1796`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L1795-L1796) - REPUTE.fac writing

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:59`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L59) - HTInstallation.TwoDA_FACTIONS constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/utc.py:239`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utc.py#L239) - repute.2da included in batch cache for [UTC](GFF-File-Format#utc-creature) editor
- [`Tools/HolocronToolset/src/toolset/gui/editors/utc.py:253-280`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utc.py#L253-L280) - repute.2da usage in faction selection combobox
- [`Tools/HolocronToolset/src/toolset/gui/editors/utp.py:121-128`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utp.py#L121-L128) - repute.2da usage in [UTP](GFF-File-Format#utp-placeable) editor
- [`Tools/HolocronToolset/src/toolset/gui/editors/utd.py:117-124`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utd.py#L117-L124) - repute.2da usage in [UTD](GFF-File-Format#utd-door) editor
- [`Tools/HolocronToolset/src/toolset/gui/editors/ute.py:106-109`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/ute.py#L106-L109) - repute.2da usage in [UTE](GFF-File-Format#ute-encounter) editor
- [`Tools/HolocronToolset/src/toolset/gui/editors/utt.py:72-78`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utt.py#L72-L78) - repute.2da usage in [UTT](GFF-File-Format#utt-trigger) editor

**Vendor Implementations:**

- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/reputes.cpp:36-62`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/reputes.cpp#L36-L62) - Repute [matrix](Level-Layout-Formats#adjacencies-wok-only) loading from [2DA](2DA-File-Format)

---

### surfacemat.2da

**Engine Usage**: Defines surface material properties for [walkmesh](Level-Layout-Formats#bwm) surfaces, including walkability, line of sight blocking, and grass rendering. The engine uses this file to determine surface behavior during pathfinding and rendering.

**Row index**: surface material ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | surface material label |
| `walk` | *Boolean* | Whether surface is walkable |
| `walkcheck` | *Boolean* | Whether walk check applies |
| `lineofsight` | *Boolean* | Whether surface blocks line of sight |
| `grass` | *Boolean* | Whether surface has grass rendering |
| `sound` | *String* | Sound type identifier for footstep sounds |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py:21`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py#L21) - SurfaceMaterial import
- [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_types.py:9`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_types.py#L9) - SurfaceMaterial import
- [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_types.py:412`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_types.py#L412) - SurfaceMaterial.GRASS default value
- [`Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py:47`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py#L47) - SurfaceMaterial ID per [face](MDL-MDX-File-Format#face-structure) documentation
- [`Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py:784`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py#L784) - SurfaceMaterial ID field documentation
- [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_data.py:1578`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_data.py#L1578) - Comment referencing surfacemat.2da for [walkmesh](Level-Layout-Formats#bwm) surface material
- [`Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py:160`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py#L160) - SurfaceMaterial parsing from [BWM](Level-Layout-Formats#bwm)

**Vendor Implementations:**

- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/surfaces.cpp:29-44`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/surfaces.cpp#L29-L44) - surface material loading from [2DA](2DA-File-Format)

---

### loadscreenhints.2da

**Engine Usage**: Defines loading screen hints displayed during area transitions. The engine uses this file to show helpful tips and hints to players while loading.

**Row index**: Loading Screen Hint ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Hint label |
| `strref` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for hint text |

**References**:

**Vendor Implementations:**

- **[xoreos](https://github.com/xoreos/xoreos)**: [`src/engines/kotor/gui/loadscreen/loadscreen.cpp:45`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/engines/kotor/gui/loadscreen/loadscreen.cpp#L45) - Loading screen hints TODO comment (KotOR-specific)

---

### bodybag.2da

**Engine Usage**: Defines body bag appearances for creatures when they die. The engine uses this file to determine which appearance to use for the body bag container that appears when a creature is killed.

**Row index**: Body Bag ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Body bag label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for body bag name |
| `appearance` | *Integer* | Appearance ID for the body bag [model](MDL-MDX-File-Format) |
| `corpse` | *Boolean* | Whether the body bag represents a corpse |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:536`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L536) - [GFF](GFF-File-Format) field mapping: "BodyBag" -> bodybag.2da
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:296-298`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L296-L298) - [UTC](GFF-File-Format#utc-creature) bodybag_id field documentation (not used by game engine)
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:438`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L438) - [UTC](GFF-File-Format#utc-creature) bodybag_id field initialization
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:555-556`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L555-L556) - BodyBag field parsing from [UTC](GFF-File-Format#utc-creature) GFF (deprecated)
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:944`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L944) - BodyBag field writing to [UTC](GFF-File-Format#utc-creature) [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/utp.py:105`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L105) - [UTP](GFF-File-Format#utp-placeable) bodybag_id field documentation
- [`Libraries/PyKotor/src/pykotor/resource/generics/utp.py:179`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L179) - [UTP](GFF-File-Format#utp-placeable) bodybag_id field initialization
- [`Libraries/PyKotor/src/pykotor/resource/generics/utp.py:254`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L254) - BodyBag field parsing from [UTP](GFF-File-Format#utp-placeable) [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/utp.py:341`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L341) - BodyBag field writing to [UTP](GFF-File-Format#utp-placeable) [GFF](GFF-File-Format)

**Vendor Implementations:**

- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/object/creature.cpp:1357-1366`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/creature.cpp#L1357-L1366) - Body bag loading from [2DA](2DA-File-Format)

---

### ranges.2da

**Engine Usage**: Defines perception ranges for creatures, including sight and hearing ranges. The engine uses this file to determine how far creatures can see and hear.

**Row index**: Range ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Range label |
| `primaryrange` | *Float* | Primary perception range (sight range) |
| `secondaryrange` | *Float* | Secondary perception range (hearing range) |

**References**:

**Vendor Implementations:**

- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/object/creature.cpp:1398-1406`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/creature.cpp#L1398-L1406) - Perception range loading from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:3178-3187`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L3178-L3187) - Perception range access from [2DA](2DA-File-Format)

---

### regeneration.2da

**Engine Usage**: Defines regeneration rates for creatures in combat and non-combat states. The engine uses this file to determine how quickly creatures regenerate hit points and Force points.

**Row index**: Regeneration State ID (integer, 0=combat, 1=non-combat)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Regeneration state label |
| Additional columns | float | Regeneration rates for different resource types |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:759`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L759) - Regeneration rate loading from [2DA](2DA-File-Format)

---

### animations.2da

**Engine Usage**: Defines [animation](MDL-MDX-File-Format#animation-header) names and properties for creatures and objects. The engine uses this file to map [animation](MDL-MDX-File-Format#animation-header) IDs to [animation](MDL-MDX-File-Format#animation-header) names for playback.

**Row index**: [animation](MDL-MDX-File-Format#animation-header) ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | [animation](MDL-MDX-File-Format#animation-header) label |
| `name` | *String* | [animation](MDL-MDX-File-Format#animation-header) name (used to look up [animation](MDL-MDX-File-Format#animation-header) in [model](MDL-MDX-File-Format)) |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:1474-1482`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L1474-L1482) - [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModulePlaceable.ts:1063-1103`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModulePlaceable.ts#L1063-L1103) - Placeable [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleDoor.ts:1343-1365`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleDoor.ts#L1343-L1365) - Door [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)

### combatanimations.2da

**Engine Usage**: Defines combat-specific [animation](MDL-MDX-File-Format#animation-header) properties and mappings. The engine uses this file to determine which [animations](MDL-MDX-File-Format#animation-header) to play during combat actions.

**Row index**: Combat [animation](MDL-MDX-File-Format#animation-header) ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Combat [animation](MDL-MDX-File-Format#animation-header) label |
| Additional columns | Various | Combat [animation](MDL-MDX-File-Format#animation-header) properties |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:1482`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L1482) - Combat [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)

---

### weaponsounds.2da

**Engine Usage**: Defines sound effects for weapon attacks based on base item type. The engine uses this file to play appropriate weapon sounds during combat.

**Row index**: Base Item ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Base item label |
| Additional columns | *ResRef* | Sound effect ResRefs for different attack types |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:1819-1822`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L1819-L1822) - Weapon sound lookup from [2DA](2DA-File-Format)

---

### placeableobjsnds.2da

**Engine Usage**: Defines sound effects for placeable objects based on sound appearance type. The engine uses this file to play appropriate sounds when interacting with placeables.

**Row index**: Sound Appearance type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Sound appearance type label |
| Additional columns | *ResRef* | Sound effect ResRefs for different interaction types |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModulePlaceable.ts:387-389`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModulePlaceable.ts#L387-L389) - Placeable sound lookup from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleDoor.ts:239-241`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleDoor.ts#L239-L241) - Door sound lookup from [2DA](2DA-File-Format)

---

### creaturespeed.2da

**Engine Usage**: Defines movement speed rates for creatures based on walk rate ID. The engine uses this file to determine walking and running speeds.

**Row index**: Walk Rate ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Walk rate label |
| `walkrate` | *Float* | Walking speed rate |
| `runrate` | *Float* | Running speed rate |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:2875-2887`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L2875-L2887) - Creature speed lookup from [2DA](2DA-File-Format)

---

### exptable.2da

**Engine Usage**: Defines experience point requirements for each character level. The engine uses this file to determine when a character levels up based on accumulated experience.

**Row index**: Level (integer, typically 1-20)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Level label |
| Additional columns | *Integer* | Experience point requirements for leveling up |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:2926-2941`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L2926-L2941) - Experience table lookup from [2DA](2DA-File-Format)

---

### guisounds.2da

**Engine Usage**: Defines sound effects for [GUI](GFF-File-Format#gui-graphical-user-interface) interactions (button clicks, mouse enter events, etc.). The engine uses this file to play appropriate sounds when the player interacts with UI elements.

**Row index**: Sound ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Sound label (e.g., "Clicked_Default", "Entered_Default") |
| `soundresref` | *ResRef* | Sound effect *ResRef* |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:200`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L200) - Sound *ResRef* column definition for guisounds.2da (K1: soundresref)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:392`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L392) - Sound *ResRef* column definition for guisounds.2da (K2: soundresref)

**Vendor Implementations:**

- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/gui/sounds.cpp:31-45`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/gui/sounds.cpp#L31-L45) - [GUI](GFF-File-Format#gui-graphical-user-interface) sound loading from [2DA](2DA-File-Format)

---

### dialoganimations.2da

**Engine Usage**: Maps dialog [animation](MDL-MDX-File-Format#animation-header) ordinals to [animation](MDL-MDX-File-Format#animation-header) names for use in conversations. The engine uses this file to determine which [animation](MDL-MDX-File-Format#animation-header) to play when a dialog line specifies an [animation](MDL-MDX-File-Format#animation-header) ordinal.

**Row index**: [animation](MDL-MDX-File-Format#animation-header) Index (integer, ordinal - 10000)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | [animation](MDL-MDX-File-Format#animation-header) label |
| `name` | *String* | [animation](MDL-MDX-File-Format#animation-header) name (used to look up [animation](MDL-MDX-File-Format#animation-header) in [model](MDL-MDX-File-Format)) |

**References**:

**Vendor Implementations:**

- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/gui/dialog.cpp:302-315`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/gui/dialog.cpp#L302-L315) - Dialog [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)

---


### forceshields.2da

**Engine Usage**: Defines Force shield visual effects and properties. The engine uses this file to determine which visual effect to display when a Force shield is active.

**Row index**: Force Shield ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Force shield label |
| Additional columns | Various | Force shield visual effect properties |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/nwscript/NWScriptDefK1.ts:5552`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDefK1.ts#L5552) - Force shield lookup from [2DA](2DA-File-Format)

---

### plot.2da

**Engine Usage**: Defines journal/quest entries with their experience point rewards and labels. The engine uses this file to manage quest tracking, [journal entries](GFF-File-Format#jrl-journal), and experience point calculations for quest completion.

**Row index**: Plot ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Plot/quest label (used as quest identifier) |
| `xp` | *Integer* | Experience points awarded for quest completion |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:123-125`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L123-L125) - [UTC](GFF-File-Format#utc-creature) plot field documentation
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:375`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L375) - [UTC](GFF-File-Format#utc-creature) plot field initialization
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:579-580`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L579-L580) - Plot field parsing from [UTC](GFF-File-Format#utc-creature) [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:839`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L839) - Plot field writing to [UTC](GFF-File-Format#utc-creature) [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/uti.py:71-73`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L71-L73) - [UTI](GFF-File-Format#uti-item) plot field documentation
- [`Libraries/PyKotor/src/pykotor/resource/generics/uti.py:129`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L129) - [UTI](GFF-File-Format#uti-item) plot field initialization
- [`Libraries/PyKotor/src/pykotor/resource/generics/uti.py:256-258`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L256-L258) - Plot field parsing from [UTI](GFF-File-Format#uti-item) [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/uti.py:339`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L339) - Plot field writing to [UTI](GFF-File-Format#uti-item) [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/gff.py:89-92`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/gff.py#L89-L92) - Dialog [node](MDL-MDX-File-Format#node-structures) PlotIndex and PlotXPPercentage field parsing

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/managers/JournalManager.ts:58-64`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/managers/JournalManager.ts#L58-L64) - Plot/quest experience lookup from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/managers/JournalManager.ts:101-104`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/managers/JournalManager.ts#L101-L104) - Plot existence check from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/nwscript/NWScriptDefK1.ts:7845-7848`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDefK1.ts#L7845-L7848) - Plot table access for quest experience

---

### [traps.2da](#traps2da)

**Engine Usage**: Defines trap properties including [models](MDL-MDX-File-Format), sounds, and scripts. The engine uses this file when loading triggers with trap types to determine trap appearance and behavior.

**Row index**: Trap type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Trap type label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for trap name |
| `model` | *ResRef* | Trap [model](MDL-MDX-File-Format) *ResRef* |
| `explosionsound` | *ResRef* | Explosion sound effect *ResRef* |
| `resref` | *ResRef* | Trap script *ResRef* |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:150`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L150) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definitions for traps.2da (K1: trapname, name)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:328`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L328) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definitions for traps.2da (K2: trapname, name)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:470`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L470) - TwoDARegistry.TRAPS constant definition
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:568`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L568) - [GFF](GFF-File-Format) field mapping: "TrapType" -> traps.2da
- [`Libraries/PyKotor/src/pykotor/common/scriptdefs.py:6347-6348`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L6347-L6348) - VersusTrapEffect function comments
- [`Libraries/PyKotor/src/pykotor/common/scriptdefs.py:7975-7976`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L7975-L7976) - GetLastHostileActor function comment mentioning traps
- [`Libraries/PyKotor/src/pykotor/common/scriptlib.py:21692`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptlib.py#L21692) - Trap targeting comment

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:69`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L69) - HTInstallation.TwoDA_TRAPS constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/utt.py:73-87`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utt.py#L73-L87) - traps.2da loading and usage in trap type selection combobox
- [`Tools/HolocronToolset/src/toolset/gui/editors/utt.py:167`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utt.py#L167) - traps.2da usage for setting trap type index
- [`Tools/HolocronToolset/src/toolset/gui/editors/utt.py:216`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utt.py#L216) - traps.2da usage for getting trap type index
- [`Tools/HolocronToolset/src/ui/editors/utt.ui:252`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/ui/editors/utt.ui#L252) - Trap selection combobox in [UTT](GFF-File-Format#utt-trigger) editor UI

**Vendor Implementations:**

- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/object/trigger.cpp:75-78`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/object/trigger.cpp#L75-L78) - Trap type loading from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleTrigger.ts:605-611`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleTrigger.ts#L605-L611) - Trap loading from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleObject.ts:1822`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleObject.ts#L1822) - Trap lookup from [2DA](2DA-File-Format)

---

### modulesave.2da

**Engine Usage**: Defines which modules should be included in save games. The engine uses this file to determine whether a module's state should be persisted when saving the game.

**Row index**: Module Index (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Module label |
| `modulename` | *String* | Module filename (e.g., "001ebo") |
| `includeInSave` | *Boolean* | Whether module state should be saved (0 = false, 1 = true) |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/Module.ts:663-669`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/Module.ts#L663-L669) - Module save inclusion check from [2DA](2DA-File-Format)

---

### tutorial.2da

**Engine Usage**: Defines tutorial window tracking entries. The engine uses this file to track which tutorial windows have been shown to the player.

**Row index**: Tutorial ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Tutorial label |
| Additional columns | Various | Tutorial window properties |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/managers/PartyManager.ts:180-187`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/managers/PartyManager.ts#L180-L187) - Tutorial window tracker initialization from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/managers/PartyManager.ts:438`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/managers/PartyManager.ts#L438) - Tutorial table access

---

### globalcat.2da

**Engine Usage**: Defines global variables and their types for the game engine. The engine uses this file to initialize global variables at game start, determining which variables are integers, floats, or strings.

**Row index**: Global Variable Index (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Global variable label |
| `name` | *String* | Global variable name |
| `type` | *String* | Variable type ("Number", "Boolean", "string", etc.) |

**References**:

**Vendor Implementations:**

- [`NorthernLights/Assets/Scripts/Systems/StateSystem.cs:282-294`](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/Assets/Scripts/Systems/StateSystem.cs#L282-L294) - Global variable initialization from [2DA](2DA-File-Format)

---

### subrace.2da

**Engine Usage**: Defines subrace types for character creation and [creature templates](GFF-File-Format#utc-creature). The engine uses this file to determine subrace properties and restrictions.

**Row index**: Subrace ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Subrace label |
| Additional columns | Various | Subrace properties |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:457`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L457) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:56`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L56) - HTInstallation constant

---

### gender.2da

**Engine Usage**: Defines gender types for character creation and [creature templates](GFF-File-Format#utc-creature). The engine uses this file to determine gender-specific properties and restrictions.

**Row index**: Gender ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Gender label |
| Additional columns | Various | Gender properties |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:461`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L461) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:60`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L60) - HTInstallation constant

---

### [racialtypes.2da](#racialtypes2da)

**Engine Usage**: Defines racial types for character creation and [creature templates](GFF-File-Format#utc-creature). The engine uses this file to determine race-specific properties, restrictions, and bonuses.

**Row index**: Race ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Race label |
| Additional columns | Various | Race properties and bonuses |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:471`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L471) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:70`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L70) - HTInstallation constant

---

### upgrade.2da

**Engine Usage**: Defines item upgrade types and properties. The engine uses this file to determine which upgrades can be applied to items and their effects.

**Row index**: Upgrade type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Upgrade type label |
| Additional columns | Various | Upgrade properties and effects |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:473`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L473) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:72`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L72) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/uti.py:632-639`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L632-L639) - Upgrade selection in item editor

---

### encdifficulty.2da

**Engine Usage**: Defines encounter difficulty levels for area encounters. The engine uses this file to determine encounter scaling and difficulty modifiers.

**Row index**: Difficulty ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Difficulty label |
| Additional columns | Various | Difficulty modifiers and properties |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:474`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L474) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:73`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L73) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/ute.py:101-104`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/ute.py#L101-L104) - Encounter difficulty selection

---

### [itempropdef.2da](#itempropdef2da)

**Engine Usage**: Defines item property definitions and their base properties. This is the master table for all item properties in the game. The engine uses this file to determine item property types, costs, and effects.

**Row index**: Item Property ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property label |
| Additional columns | Various | Property definitions, costs, and parameters |

**Note**: This file may be the same as or related to `itemprops.2da` documented earlier. The exact relationship between these files may vary between KotOR 1 and 2.

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:475`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L475) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:74`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L74) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/uti.py:107-111`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L107-L111) - Item property loading in item editor

---

### emotion.2da

**Engine Usage**: Defines emotion [animations](MDL-MDX-File-Format#animation-header) for dialog conversations (KotOR 2 only). The engine uses this file to determine which emotion [animation](MDL-MDX-File-Format#animation-header) to play during dialog lines.

**Row index**: Emotion ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Emotion label |
| Additional columns | Various | Emotion [animation](MDL-MDX-File-Format#animation-header) properties |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:491`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L491) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:90`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L90) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/dlg/editor.py:1267-1319`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/dlg/editor.py#L1267-L1319) - Emotion loading in dialog editor (KotOR 2 only)

---

### facialanim.2da

**Engine Usage**: Defines facial [animation](MDL-MDX-File-Format#animation-header) expressions for dialog conversations (KotOR 2 only). The engine uses this file to determine which facial expression [animation](MDL-MDX-File-Format#animation-header) to play during dialog lines.

**Row index**: Expression ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Expression label |
| Additional columns | Various | Facial [animation](MDL-MDX-File-Format#animation-header) properties |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:492`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L492) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:91`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L91) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/dlg/editor.py:1267-1325`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/dlg/editor.py#L1267-L1325) - Expression loading in dialog editor (KotOR 2 only)

---

### videoeffects.2da

**Engine Usage**: Defines video/camera effects for dialog conversations. The engine uses this file to determine which visual effect to apply during dialog camera shots.

**Row index**: Video Effect ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Video effect label |
| Additional columns | Various | Video effect properties |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:493`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L493) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:92`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L92) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/dlg/editor.py:1263-1298`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/dlg/editor.py#L1263-L1298) - Video effect loading in dialog editor

---

### planetary.2da

**Engine Usage**: Defines planetary information for the galaxy map and travel system. The engine uses this file to determine planet names, descriptions, and travel properties.

**Row index**: Planet ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Planet label |
| Additional columns | Various | Planet properties and travel information |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:495`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L495) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:94`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L94) - HTInstallation constant

---

### cursors.2da

**Engine Usage**: Defines cursor types for different object interactions. The engine uses this file to determine which cursor to display when hovering over different object types.

**Row index**: Cursor ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Cursor label |
| Additional columns | Various | Cursor properties and ResRefs |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:469`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L469) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:68`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L68) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/utt.py:71-76`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utt.py#L71-L76) - Cursor selection in trigger editor

---

## Item Property Parameter & Cost Tables 2DA Files

The following 2DA files are used for item property parameter and cost calculations:

### iprp_paramtable.2da

**Engine Usage**: Master table listing all item property parameter tables. The engine uses this file to look up which parameter table to use for a specific item property type.

**Row index**: Parameter Table ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Parameter table label |
| Additional columns | Various | Parameter table ResRefs and properties |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_PARAMTABLE` L698](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L698) — `iprp_paramtable` (`LoadIPRPParamTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_PARAMTABLE` L99](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L99)
- [`Tools/HolocronToolset/src/toolset/gui/editors/uti.py:517-558`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L517-L558) - Parameter table lookup in item editor

---

### iprp_costtable.2da

**Engine Usage**: Master table listing all item property cost calculation tables. The engine uses this file to look up which cost table to use for calculating item property costs.

**Row index**: Cost Table ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Cost table label |
| Additional columns | Various | Cost table ResRefs and properties |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_COSTTABLE` L693](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L693) — `iprp_costtable` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_COSTTABLE` L94](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L94)
- [`Tools/HolocronToolset/src/toolset/gui/editors/uti.py:486-496`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L486-L496) - Cost table lookup in item editor

---

### iprp_abilities.2da

**Engine Usage**: Maps item property values to ability score bonuses. The engine uses this file to determine which ability score is affected by an item property.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Ability score mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_ABILITIES` L688](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L688) — `iprp_abilities` (`Load2DArrays_IPRPAbilities()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_ABILITIES` L89](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L89)

---

### iprp_aligngrp.2da

**Engine Usage**: Maps item property values to alignment group restrictions. The engine uses this file to determine alignment restrictions for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Alignment group mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_ALIGNGRP` L690](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L690) — `iprp_aligngrp` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_ALIGNGRP` L91](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L91)

---

### iprp_combatdam.2da

**Engine Usage**: Maps item property values to combat damage bonuses. The engine uses this file to determine damage bonus calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Combat damage mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_COMBATDAM` L692](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L692) — canonical `iprp_combatdam` resref (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_COMBATDAM` L93](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L93)

---

### iprp_damagetype.2da

**Engine Usage**: Maps item property values to damage type flags. The engine uses this file to determine damage type calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Damage type mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_DAMAGETYPE` L694](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L694) — `iprp_damagetype` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_DAMAGETYPE` L95](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L95)

---

### iprp_protection.2da

**Engine Usage**: Maps item property values to protection/immunity types. The engine uses this file to determine protection calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Protection type mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_PROTECTION` L699](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L699) — `iprp_protection` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_PROTECTION` L100](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L100)

---

### iprp_acmodtype.2da

**Engine Usage**: Maps item property values to armor class modifier types. The engine uses this file to determine AC modifier calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | AC modifier type mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_ACMODTYPE` L689](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L689) — `iprp_acmodtype` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_ACMODTYPE` L90](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L90)

---

### iprp_immunity.2da

**Engine Usage**: Maps item property values to immunity types. The engine uses this file to determine immunity calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Immunity type mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_IMMUNITY` L695](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L695) — `iprp_immunity` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_IMMUNITY` L96](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L96)

---

### iprp_saveelement.2da

**Engine Usage**: Maps item property values to saving throw element types. The engine uses this file to determine saving throw element calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Saving throw element mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_SAVEELEMENT` L700](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L700) — `iprp_saveelement` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_SAVEELEMENT` L101](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L101)

---

### iprp_savingthrow.2da

**Engine Usage**: Maps item property values to saving throw types. The engine uses this file to determine saving throw calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Saving throw type mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_SAVINGTHROW` L701](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L701) — `iprp_savingthrow` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_SAVINGTHROW` L102](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L102)

---

### iprp_onhit.2da

**Engine Usage**: Maps item property values to on-hit effect types. The engine uses this file to determine on-hit effect calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | On-hit effect mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_ONHIT` L697](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L697) — `iprp_onhit` (`Load2DArrays_OnHit()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_ONHIT` L98](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L98)

---

### iprp_ammotype.2da

**Engine Usage**: Maps item property values to ammunition type restrictions. The engine uses this file to determine ammunition type calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Ammunition type mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_AMMOTYPE` L691](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L691) — `iprp_ammotype` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_AMMOTYPE` L92](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L92)

---

### iprp_mosterhit.2da

**Engine Usage**: Maps item property values to monster hit effect types. The engine uses this file to determine monster hit effect calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Monster hit effect mappings |

**Note**: The filename contains a typo ("mosterhit" instead of "monsterhit") which is preserved in the game files.

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_MONSTERHIT` L696](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L696) — `iprp_mosterhit` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_MONSTERHIT` L97](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L97)

---

### iprp_walk.2da

**Engine Usage**: Maps item property values to movement/walk speed modifiers. The engine uses this file to determine movement speed calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Movement speed mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_WALK` L702](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L702) — `iprp_walk` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_WALK` L103](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L103)

---

### iprp_lightcol.2da

**Engine Usage**: Maps item property values to light color configurations. The engine uses this file to determine light color settings for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Light color mappings |

**References**:

**PyKotor:**

- [`_GFF_FIELD_TO_2DA` — `"LightColor"` → `iprp_lightcol` L774](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L774) — [GFF](GFF-File-Format) field wiring (UTI / item property context)
- [`TwoDARegistry` docstring — `iprp_lightcol` / `Load2DArrays_LightColor()` L600](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L600)

**HolocronToolset:**

- No `HTInstallation.TwoDA_IPRP_LIGHTCOL` in [`installation.py`](https://github.com/OldRepublicDevs/HolocronToolset/src/toolset/data/installation.py); cite PyKotor `twoda.py` above for resref proof.

---

### iprp_monstdam.2da

**Engine Usage**: Maps item property values to monster damage bonuses. The engine uses this file to determine damage bonus calculations for monster weapons.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Monster damage mappings |

**References**:

**PyKotor:**

- [`twoda.py` `_GFF_FIELD_TO_2DA` — `"MonsterDamage"` → `iprp_monstdam` L779](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L779)
- [`read_2da` L67+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67) — generic 2DA reader

**Note:** Unlike `iprp_combatdam`, there is no separate `TwoDARegistry.IPRP_MONSTDAM` constant—the file is reached via the **MonsterDamage** GFF field mapping above and via **[itemprops.2da](#itemprops2da)** cost-table wiring.

**See:** [2DA-iprp_monstdam](#iprp_monstdam2da) — expanded stub page (combat vs monster damage, cross-links).

---

### difficultyopt.2da

**Engine Usage**: Defines difficulty options and their properties. The engine uses this file to determine difficulty settings, modifiers, and descriptions.

**Row index**: Difficulty Option ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Difficulty option label |
| `desc` | *String* | Difficulty description (e.g., "Default") |
| Additional columns | Various | Difficulty modifiers and properties |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/engine/rules/SWRuleSet.ts:66-74`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/engine/rules/SWRuleSet.ts#L66-L74) - Difficulty options initialization from [2DA](2DA-File-Format)

---

### xptable.2da

**Engine Usage**: Defines experience point reward calculations for defeating enemies. The engine uses this file to calculate how much XP to grant when a creature is defeated, based on the defeated creature's level and properties.

**Row index**: XP Table Entry ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | XP table entry label |
| Additional columns | Various | XP calculation parameters |

**Note**: This is different from `exptable.2da` which defines XP requirements for leveling up. `xptable.2da` defines XP rewards for defeating enemies.

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/engine/rules/SWRuleSet.ts:89-95`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/engine/rules/SWRuleSet.ts#L89-L95) - XP table initialization from [2DA](2DA-File-Format)

---

### featgain.2da

**Engine Usage**: Defines feat gain progression by class and level. The engine uses this file to determine which feats are available to each class at each level.

**Row index**: Feat Gain Entry ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Feat gain entry label |
| Additional columns | Various | Feat gain progression by class and level |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/engine/rules/SWRuleSet.ts:101-105`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/engine/rules/SWRuleSet.ts#L101-L105) - Feat gain initialization from [2DA](2DA-File-Format)

---

### effecticon.2da

**Engine Usage**: Defines effect icons displayed on character portraits and character sheets. The engine uses this file to determine which icon to display for status effects, buffs, and debuffs.

**Row index**: Effect Icon ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Effect icon label |
| Additional columns | Various | Effect icon properties and ResRefs |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/engine/rules/SWRuleSet.ts:143-150`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/engine/rules/SWRuleSet.ts#L143-L150) - Effect icon initialization from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/nwscript/NWScriptDefK1.ts:6441-6446`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDefK1.ts#L6441-L6446) - SetEffectIcon function
- [`NorthernLights/nwscript.nss:4678`](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/nwscript.nss#L4678) - Comment referencing effecticon.2da

---

### pazaakdecks.2da

**Engine Usage**: Defines Pazaak card decks for the Pazaak mini-game. The engine uses this file to determine which cards are available in opponent decks and player decks.

**Row index**: Pazaak Deck ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Deck label |
| Additional columns | Various | Deck card definitions and properties |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/engine/rules/SWRuleSet.ts:178-185`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/engine/rules/SWRuleSet.ts#L178-L185) - Pazaak decks initialization from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/nwscript/NWScriptDefK1.ts:4438`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDefK1.ts#L4438) - StartPazaakGame function comment
- [`NorthernLights/nwscript.nss:3847`](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/nwscript.nss#L3847) - Comment referencing PazaakDecks.2da

---

### acbonus.2da

**Engine Usage**: Defines armor class bonus calculations. The engine uses this file to determine AC bonus values for different scenarios and calculations.

**Row index**: AC Bonus Entry ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | AC bonus entry label |
| Additional columns | Various | AC bonus calculation parameters |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/combat/CreatureClass.ts:302-304`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/combat/CreatureClass.ts#L302-L304) - AC bonus loading from [2DA](2DA-File-Format)
- [`Tools/HolocronToolset/src/toolset/data/installation.py:63`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L63) - HTInstallation.ACBONUS constant

---

### keymap.2da

**Engine Usage**: Defines keyboard and [controller](MDL-MDX-File-Format#controllers) key mappings for different game contexts (in-game, [GUI](GFF-File-Format#gui-graphical-user-interface), dialog, minigame, etc.). The engine uses this file to determine which keys trigger which actions in different contexts.

**Row index**: Keymap Entry ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Keymap entry label |
| Additional columns | Various | key mappings for different contexts (ingame, [GUI](GFF-File-Format#gui-graphical-user-interface), dialog, minigame, freelook, movie) |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/controls/KeyMapper.ts:293-299`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/controls/KeyMapper.ts#L293-L299) - Keymap initialization from [2DA](2DA-File-Format)

---

### poison.2da

**Engine Usage**: Defines poison effect types and their properties. The engine uses this file to determine poison effects, durations, and damage calculations.

**Row index**: Poison type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Poison type label |
| Additional columns | Various | Poison effect properties, damage, and duration |

**References**:

- [`NorthernLights/nwscript.nss:949`](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/nwscript.nss#L949) - Comment referencing poison.2da constants
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/nwscript/NWScriptDefK1.ts:3194-3199`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDefK1.ts#L3194-L3199) - EffectPoison function

---

### feedbacktext.2da

**Engine Usage**: Defines feedback text strings displayed to the player for various game events and actions. The engine uses this file to provide contextual feedback messages.

**Row index**: Feedback Text ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Feedback text label |
| Additional columns | Various | Feedback text strings and properties |

**References**:

- [`NorthernLights/nwscript.nss:3858`](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/nwscript.nss#L3858) - Comment referencing FeedBackText.2da
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/nwscript/NWScriptDefK1.ts:4464-4465`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDefK1.ts#L4464-L4465) - DisplayFeedBackText function

---

### appearancesndset.2da

**Engine Usage**: Defines sound appearance types for creature appearances. The engine uses this file to determine which sound appearance type to use based on the creature's appearance.

**Row index**: Sound Appearance type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Sound appearance type label |
| Additional columns | Various | Sound appearance type properties |

**References**:

- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`Appearance.cs` L56–L60](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Tables/Appearance.cs#L56-L60) — `SoundAppTypeID` maps into `appearancesndset.2da`

---

### texpacks.2da

**Engine Usage**: Defines [texture](Texture-Formats#tpc) pack configurations for graphics settings (KotOR 2 only). The engine uses this file to determine available [texture](Texture-Formats#tpc) pack options in the graphics menu.

**Row index**: [texture](Texture-Formats#tpc) Pack ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | [texture](Texture-Formats#tpc) pack label |
| `strrefname` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for [texture](Texture-Formats#tpc) pack name |
| Additional columns | Various | [texture](Texture-Formats#tpc) pack properties and settings |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/game/tsl/menu/MenuGraphicsAdvanced.ts:51-122`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/game/tsl/menu/MenuGraphicsAdvanced.ts#L51-L122) - [texture](Texture-Formats#tpc) pack loading from [2DA](2DA-File-Format) for graphics menu (KotOR 2 only)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/game/kotor/menu/MenuGraphicsAdvanced.ts:63-121`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/game/kotor/menu/MenuGraphicsAdvanced.ts#L63-L121) - [texture](Texture-Formats#tpc) pack usage in KotOR 1 graphics menu

---

### loadscreens.2da

**Engine Usage**: Defines loading screen configurations for area transitions. The engine uses this file to determine which loading screen image, music, and hints to display when transitioning between areas.

**Row index**: Loading Screen ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Loading screen label |
| `bmpresref` | *ResRef* | Loading screen background image *ResRef* |
| `musicresref` | *ResRef* | Music track *ResRef* to play during loading |
| Additional columns | Various | Other loading screen properties |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleArea.ts:210`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleArea.ts#L210) - Comment referencing loadscreens.2da for area loading screen index
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:549`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L549) - [GFF](GFF-File-Format) field mapping: "LoadScreenID" -> loadscreens.2da

---

### fractionalcr.2da

**Engine Usage**: Defines fractional challenge rating configurations. The engine uses this file to determine fractional CR display strings.

**Row index**: Fractional CR ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Fractional CR label |
| `displaystrref` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for fractional CR display text |
| Additional columns | Various | Fractional CR properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:84`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L84) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definition for fractionalcr.2da

---

### bindablekeys.2da

**Engine Usage**: Defines bindable key actions and their string references. The engine uses this file to determine key action names for the key binding interface.

**Row index**: Bindable key ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Bindable key label |
| `keynamestrref` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for key name |
| Additional columns | Various | key binding properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:74`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L74) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definition for bindablekeys.2da

---

### masterfeats.2da

**Engine Usage**: Defines master feat configurations. The engine uses this file to determine master feat names and properties.

**Row index**: Master Feat ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Master feat label |
| `strref` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for master feat name |
| Additional columns | Various | Master feat properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:138`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L138) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definition for masterfeats.2da

---

### movies.2da

**Engine Usage**: Defines movie/cutscene configurations. The engine uses this file to determine movie names and descriptions.

**Row index**: Movie ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Movie label |
| `strrefname` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for movie name |
| `strrefdesc` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for movie description |
| Additional columns | Various | Movie properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:140`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L140) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definitions for movies.2da

---

### stringtokens.2da

**Engine Usage**: Defines string token configurations. The engine uses this file to determine string token values for various game systems.

**Row index**: string Token ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | string token label |
| `strref1` through `strref4` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | string references for token values |
| Additional columns | Various | string token properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:144`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L144) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definitions for stringtokens.2da

---

### disease.2da

**Engine Usage**: Defines disease effect configurations. The engine uses this file to determine disease names, scripts, and properties.

**Row index**: Disease ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Disease label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for disease name (KotOR 2) |
| `end_incu_script` | *ResRef* | Script *ResRef* for end incubation period |
| `24_hour_script` | *ResRef* | Script *ResRef* for 24-hour disease effect |
| Additional columns | Various | Disease properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:255`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L255) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definition for disease.2da (KotOR 2)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:238,431`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L238) - Script *ResRef* column definitions for disease.2da

---

### droiddischarge.2da

**Engine Usage**: Defines droid discharge effect configurations. The engine uses this file to determine droid discharge properties.

**Row index**: Droid Discharge ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Droid discharge label |
| `>>##HEADER##<<` | *ResRef* | header [resource reference](GFF-File-Format#gff-data-types) |
| Additional columns | Various | Droid discharge properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:156`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L156) - *ResRef* column definition for droiddischarge.2da

---

### upcrystals.2da

**Engine Usage**: Defines upgrade crystal configurations. The engine uses this file to determine crystal [model](MDL-MDX-File-Format) variations for lightsaber upgrades.

**Row index**: Upgrade Crystal ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Upgrade crystal label |
| `shortmdlvar` | *ResRef* | Short [model](MDL-MDX-File-Format) variation *ResRef* |
| `longmdlvar` | *ResRef* | Long [model](MDL-MDX-File-Format) variation *ResRef* |
| `doublemdlvar` | *ResRef* | double-bladed [model](MDL-MDX-File-Format) variation *ResRef* |
| Additional columns | Various | Crystal properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:172`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L172) - [model](MDL-MDX-File-Format) *ResRef* column definitions for upcrystals.2da

---

### grenadesnd.2da

**Engine Usage**: Defines grenade sound configurations. The engine uses this file to determine grenade sound effects.

**Row index**: Grenade Sound ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Grenade sound label |
| `sound` | *ResRef* | Sound *ResRef* for grenade |
| Additional columns | Various | Grenade sound properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:199`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L199) - Sound *ResRef* column definition for grenadesnd.2da

---

### inventorysnds.2da

**Engine Usage**: Defines inventory sound configurations. The engine uses this file to determine inventory sound effects for item interactions.

**Row index**: Inventory Sound ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Inventory sound label |
| `inventorysound` | *ResRef* | Inventory sound *ResRef* |
| Additional columns | Various | Inventory sound properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:201`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L201) - Sound *ResRef* column definition for inventorysnds.2da
