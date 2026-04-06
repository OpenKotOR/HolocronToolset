# GFF Types: Items and Economy

Items, merchants, journals, and factions form the game’s economy and progression systems. UTI defines every equippable or consumable object [[`UTI`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L22)], UTM describes store inventories and pricing, JRL tracks quest progress visible to the player, and FAC controls inter-faction hostility and friendship.

## Contents

- [UTI — Item](#uti)
- [UTM — Store / Merchant](#utm)
- [JRL — Journal](#jrl)
- [FAC — Faction](#fac)

---

<a id="uti"></a>

# UTI (Item)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTI files define [item templates](GFF-File-Format#uti-item) for all objects in creature inventories, containers, and stores. Items range from weapons and armor to quest items, upgrades, and consumables. UTI files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Item format specification, see [Bioware Aurora Item Format](Bioware-Aurora-Items-Economy-and-Narrative#item).

**For mod developers:**

- To modify GFF/UTI files in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFF-Syntax#gfflist-syntax).
- For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers).

**Related formats:**

- [2DA files](2DA-File-Format):

  - [baseitems.2da](2DA-File-Format#baseitems2da)
  - [itempropdef.2da](2DA-File-Format#itempropdef2da)

- [TLK](Audio-and-Localization-Formats#tlk) — localized names
- Visual variants resolve through:

  - [MDL](MDL-MDX-File-Format) ([model](MDL-MDX-File-Format) geometry)
  - [TPC](Texture-Formats#tpc) ([texture](Texture-Formats#tpc) data)

PyKotor models UTI templates with the dedicated [`UTI` data class and `read_uti` / `write_uti` helpers](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L22) on top of the shared binary [`GFFBinaryReader.load`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) pipeline, while Holocron Toolset exposes the same item fields through its [`uti.py` editor](https://github.com/OpenKotOR/HolocronToolset/src/toolset/gui/editors/uti.py). Other toolchains keep UTI in the generic GFF family as well, including reone's [`gff.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/gff.cpp) and [`gffreader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/gffreader.cpp), KotOR.js's [`GFFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), Kotor.NET's [`GFF.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18), and xoreos's Aurora GFF stack.

## Core Identity fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | Template identifier for this item |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique tag for script references |
| `LocalizedName` | [CExoLocString](GFF-File-Format#gff-data-types) | Item name (localized) |
| `Description` | [CExoLocString](GFF-File-Format#gff-data-types) | Generic description |
| `DescIdentified` | [CExoLocString](GFF-File-Format#gff-data-types) | Description when identified |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment/notes |

## Base Item Configuration

| Field | Type | Description |
| ----- | ---- | ----------- |
| `BaseItem` | [int32](GFF-File-Format#gff-data-types) | Index into [`baseitems.2da`](2DA-File-Format#baseitems2da) (defines item type) |
| `Cost` | UInt32 | Base value in credits |
| `AddCost` | UInt32 | Additional cost from properties |
| `Plot` | [byte](GFF-File-Format#gff-data-types) | Plot-critical item (cannot be sold/destroyed) |
| `Charges` | [byte](GFF-File-Format#gff-data-types) | Number of uses remaining |
| `StackSize` | [word](GFF-File-Format#gff-data-types) | Current stack quantity |
| `ModelVariation` | [byte](GFF-File-Format#gff-data-types) | [model](MDL-MDX-File-Format) variation index [[`uti.py` L82](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L82)] |
| `BodyVariation` | [byte](GFF-File-Format#gff-data-types) | Body variation for armor [[`uti.py` L81](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L81)] |
| `TextureVar` | [byte](GFF-File-Format#gff-data-types) | [texture](Texture-Formats#tpc) variation for armor [[`uti.py` L83](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L83)] |

**BaseItem types** (from [`baseitems.2da`](2DA-File-Format#baseitems2da)); row index into the 2DA defines item type.

## Item Properties

| Field | Type | Description |
| ----- | ---- | ----------- |
| `PropertiesList` | [List](GFF-File-Format#gff-data-types) | Item properties and enchantments |
| `Upgradable` | [byte](GFF-File-Format#gff-data-types) | Can accept upgrades (KotOR1 only) |
| `UpgradeLevel` | [byte](GFF-File-Format#gff-data-types) | Current upgrade tier (KotOR2 only) |

**PropertiesList Struct fields:**

- `PropertyName` ([word](GFF-File-Format#gff-data-types)): Index into [`itempropdef.2da`](2DA-File-Format#itempropdef2da)
- `Subtype` ([word](GFF-File-Format#gff-data-types)): Property subtype/category
- `CostTable` ([byte](GFF-File-Format#gff-data-types)): Cost table index
- `CostValue` ([word](GFF-File-Format#gff-data-types)): Cost value
- `Param1` ([byte](GFF-File-Format#gff-data-types)): First parameter
- `Param1Value` ([byte](GFF-File-Format#gff-data-types)): First parameter value
- `ChanceAppear` ([byte](GFF-File-Format#gff-data-types)): Percentage chance to appear on randomly generated loot; default 100 [[`uti.py` L169](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L169)]

**Property types** are defined entirely in [`itempropdef.2da`](2DA-File-Format#itempropdef2da); the `PropertyName` field indexes into this table which maps each row to its subtype table, cost table, and parameter tables. PyKotor serializes each `UTIProperty` without enumerating property-type names in code — all valid property names derive from the 2DA at runtime [[`uti.py` L165–L176](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L165)].

## Weapon-Specific fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `WeaponColor` (KotOR2) | [byte](GFF-File-Format#gff-data-types) | Blade color for lightsabers |
| `WeaponWhoosh` (KotOR2) | [byte](GFF-File-Format#gff-data-types) | Whoosh sound type |

**Lightsaber colors** (KotOR2 `WeaponColor`):

- 0: Blue, 1: Yellow, 2: Green, 3: Red
- 4: Violet, 5: Orange, 6: Cyan, 7: Silver
- 8: White, 9: Viridian, 10: Bronze

## Armor-Specific fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `BodyVariation` | [byte](GFF-File-Format#gff-data-types) | Body [model](MDL-MDX-File-Format) variation [[`uti.py` L81](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L81)] |
| `TextureVar` | [byte](GFF-File-Format#gff-data-types) | [texture](Texture-Formats#tpc) variation [[`uti.py` L83](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L83)] |
| `ModelVariation` | [byte](GFF-File-Format#gff-data-types) | [model](MDL-MDX-File-Format) type [[`uti.py` L82](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L82)] |
| `ArmorRulesType` (KotOR2) | [byte](GFF-File-Format#gff-data-types) | Armor class category |

**Armor [model](MDL-MDX-File-Format) Variations:**

- **Body + [texture](Texture-Formats#tpc) Variation**: Creates visual diversity
- Armor adapts to wearer's body type and gender
- `appearance.2da` defines valid combinations

## Quest & Special Items

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Plot` | [byte](GFF-File-Format#gff-data-types) | Cannot be sold or destroyed |
| `Stolen` | [byte](GFF-File-Format#gff-data-types) | Marked as stolen |
| `Cursed` | [byte](GFF-File-Format#gff-data-types) | Cannot be unequipped |
| `Identified` | [byte](GFF-File-Format#gff-data-types) | Player has identified the item |

**Plot Item Behavior:**

- Immune to destruction/selling
- Often required for quest completion
- Can have special script interactions

## Upgrade System (KotOR1)

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Upgradable` | [byte](GFF-File-Format#gff-data-types) | Item accepts upgrade items |

**Upgrade Mechanism:**

- Weapon/armor can have upgrade slots
- Player applies upgrade items to base item
- Properties from upgrade merge into base
- Referenced in `upgradetypes.2da`

## Upgrade System (KotOR2 Enhanced)

| Field | Type | Description |
| ----- | ---- | ----------- |
| `UpgradeLevel` | [byte](GFF-File-Format#gff-data-types) | Current upgrade tier (0-2) |
| `WeaponColor` | [byte](GFF-File-Format#gff-data-types) | Lightsaber blade color |
| `WeaponWhoosh` | [byte](GFF-File-Format#gff-data-types) | Swing sound type |
| `ArmorRulesType` | [byte](GFF-File-Format#gff-data-types) | Armor restriction category |

**KotOR2 Upgrade Slots:**

Weapons and armor may have upgrade slots defined in [`baseitems.2da`](2DA-File-Format#baseitems2da).

## Visual & Audio

| Field | Type | Description |
| ----- | ---- | ----------- |
| `ModelVariation` | [byte](GFF-File-Format#gff-data-types) | Base [model](MDL-MDX-File-Format) index [[`uti.py` L82](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L82)] |
| `BodyVariation` | [byte](GFF-File-Format#gff-data-types) | Body [model](MDL-MDX-File-Format) for armor [[`uti.py` L81](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L81)] |
| `TextureVar` | [byte](GFF-File-Format#gff-data-types) | [texture](Texture-Formats#tpc) variant [[`uti.py` L83](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L83)] |

**[model](MDL-MDX-File-Format) Resolution:**

Item model names are derived from the `ModelResRef` column in [`baseitems.2da`](2DA-File-Format#baseitems2da), combined with the `ModelVariation` index. [textures](Texture-Formats#tpc) follow the same naming convention.

## Palette & Editor

| Field | Type | Description |
| ----- | ---- | ----------- |
| `PaletteID` | [byte](GFF-File-Format#gff-data-types) | Toolset palette category |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Designer notes/documentation |

**Toolset Integration:**

- `PaletteID` organizes items in editor
- Does not affect gameplay
- Used for content creation workflow

## Implementation Notes

PyKotor parses UTI via `construct_uti` [[`uti.py` L128](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L128)], which deserializes each GFF field into the `UTI` data object.

Armor identification uses the `ARMOR_BASE_ITEMS` frozenset (`{35,36,37,38,39,40,41,42,43,53,58,63,64,65,69,71,85,89,98,100,102,103}`) defined in [[`uti.py` L19](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L19)] to distinguish armor from weapons when computing visual variants. `PaletteID` and `Comment` are toolset-only fields not used at game runtime.

## See also

- [GFF File Format](GFF-File-Format) - Binary layout and data types
- [GFF Creature and Dialogue](GFF-Creature-and-Dialogue) - UTC and DLG types
- [GFF Spatial Objects](GFF-Spatial-Objects) - UTD, UTP, UTT, UTE, UTS, UTW, PTH types
- [GFF Module and Area](GFF-Module-and-Area) - ARE, GIT, IFO types
- [baseitems.2da](2DA-File-Format#baseitems2da) - Item type definitions
- [TSLPatcher GFFList Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax) - Modding GFF/UTI with TSLPatcher
- [Bioware Aurora Item Format](Bioware-Aurora-Items-Economy-and-Narrative#item) - Official BioWare specification


---

<a id="utm"></a>

# UTM (Merchant)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTM files are GFF resources with root content type **`UTM`** ([`GFFContent.UTM`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L156)) that define **merchant templates**: localized name, pricing (mark up / mark down), buy/sell flags, optional `OnOpenStore` script hook, and an **`ItemList`** of stock lines. Module **store instances** in the [**GIT**](GFF-Module-and-Area#git) reference a UTM template via the area’s store list (PyKotor maps GIT stores to [`ResourceType.UTM`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/git.py#L107); instance wrapper [`GITStore` L967–L1000](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/git.py#L967-L1000)). UTMs resolve like other resources: [override → MOD/SAV → KEY/BIF](Concepts#resource-resolution-order).

**Official Bioware Documentation:** See [Bioware Aurora Store Format](Bioware-Aurora-Items-Economy-and-Narrative#store) for Aurora-era store semantics; KotOR field names below match PyKotor’s `construct_utm` / `dismantle_utm` and the class docstring’s `LoadStore` notes.

**For mod developers:**

- [TSLPatcher GFFList Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax)
- [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers)

Global merchant metadata also lives in **[merchants.2da](2DA-File-Format)** (data table, not the per-template GFF).

## Root struct fields

| Field | GFF type | Role |
| ----- | -------- | ---- |
| `ResRef` | ResRef | Template resref (file stem). |
| `LocName` | CExoLocString | Localized merchant name. |
| `Tag` | CExoString | Tag for scripts / identification. |
| `MarkUp` | int32 | Markup when selling **to** the player (integer; divide by 100 for percentage multiplier [[`ModuleStore.ts` L56](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleStore.ts#L56)]). |
| `MarkDown` | int32 | Markdown when buying **from** the player (integer; divide by 100 for percentage multiplier [[`ModuleStore.ts` L52](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleStore.ts#L52)]). |
| `OnOpenStore` | ResRef | Script executed when the store UI opens. |
| `Comment` | CExoString | Authoring comment. |
| `BuySellFlag` | byte | Bit 0 = can buy from player; bit 1 = can sell to player [[`construct_utm` L127–L128](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L127-L128)]. |
| `ItemList` | List | Stock entries (see below). |
| `ID` | byte | Legacy field; default 5 in PyKotor [[`utm.py` L83](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L83)]; emitted only when `use_deprecated=True` in [`dismantle_utm` L172](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L172). |

## ItemList element struct

Each list element is a struct with (at minimum) the fields PyKotor reads and writes:

| Field | GFF type | Role |
| ----- | -------- | ---- |
| `InventoryRes` | ResRef | Item template ([UTI](GFF-Items-and-Economy#uti)) resref. |
| `Infinite` | byte | Infinite stock when non-zero. |
| `Dropable` | byte | Droppable flag (PyKotor writes the field only when true — [`dismantle_utm` L213–L214](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L213-L214)). |
| `Repos_PosX` | uint16 | Repository grid X (writer uses slot index — [`dismantle_utm` L164](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L164)). |
| `Repos_PosY` | uint16 | Repository grid Y (writer uses `0` — [`dismantle_utm` L165](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L165)). Note: reone reads this field as `Repos_Posy` (lowercase 'y'); PyKotor writes `Repos_PosY` (capital 'Y'). |

PyKotor documents and round-trips merchant templates through [`UTM`, `construct_utm`, `dismantle_utm`, `read_utm`, and `write_utm`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L18) on top of the shared [`GFFBinaryReader.load`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) path, and the same merchant-root-as-GFF approach appears in reone's [`gffreader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/gffreader.cpp) and [`gff.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/gff.cpp), KotOR.js's [`GFFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), Kotor.NET's [`UTM.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Resources/KotorUTM/UTM.cs#L13-L35) plus [`GFF.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18), and xoreos's Aurora GFF loader stack.

### See also

- [GFF-File-Format](GFF-File-Format) — container layout
- [GFF-GIT](GFF-Module-and-Area#git) — store **instances** in areas
- [GFF-UTI](GFF-Items-and-Economy#uti) — item templates referenced by `InventoryRes`
- [Bioware-Aurora-Store](Bioware-Aurora-Items-Economy-and-Narrative#store) — Aurora store documentation
- [Container-Formats#key](Container-Formats#key) — resource resolution


---

<a id="jrl"></a>

# JRL (Journal)

Part of the [GFF File Format Documentation](GFF-File-Format).

[JRL files](GFF-File-Format#jrl-journal) define the structure of the player's [quest journal](GFF-File-Format#jrl-journal). They organize [quests](GFF-File-Format#jrl-journal) into categories and track progress through individual [journal entries](GFF-File-Format#jrl-journal). JRL files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Journal format specification, see [Bioware Aurora Journal Format](Bioware-Aurora-Items-Economy-and-Narrative#journal).

**For mod developers:**

- Journal updates are typically driven by [DLG](GFF-Creature-and-Dialogue#dlg) Quest/QuestEntry and scripts (`AddJournalQuestEntry`).

**See also:**

- [TSLPatcher GFFList Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax)
- [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers)

**Related formats:**

- [DLG](GFF-Creature-and-Dialogue#dlg) (Quest, QuestEntry)
- [NCS](NCS-File-Format) (journal API)
- [2DA](2DA-File-Format) (e.g. journal.2da for XP)

PyKotor represents journals through [`JRL`, `JRLQuest`, `JRLEntry`, `construct_jrl`, `read_jrl`, and `write_jrl`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/jrl.py#L18), tags them as [`GFFContent.JRL`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L166), and decodes them through the same shared [`GFFBinaryReader.load`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) path that Holocron Toolset builds on in its dialogue and module editors. Other implementations also keep JRL inside the generic GFF family, including reone's [`gff.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/gff.cpp) and [`gffreader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/gffreader.cpp), KotOR.js's [`GFFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), Kotor.NET's [`GFF.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18), and xoreos's Aurora reader stack.

## Quest structure

[JRL](GFF-File-Format#jrl-journal) files contain a list of `Categories` (Quests), each containing a list of `EntryList` (States).

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Categories` | [List](GFF-File-Format#gff-data-types) | List of quests |

## Quest Category (JRLQuest)

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique quest identifier |
| `Name` | [CExoLocString](GFF-File-Format#gff-data-types) | Quest title |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment |
| `Priority` | [uint32](GFF-File-Format#gff-data-types) | Sorting priority (0=Highest, 4=Lowest) [[`JRLQuestPriority` L93–98](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/jrl.py#L93)]; default LOWEST when constructing a new `JRLQuest` object [[`jrl.py` L64](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/jrl.py#L64)] |
| `PlotIndex` | [int32](GFF-File-Format#gff-data-types) | Legacy plot index |
| `PlanetID` | [int32](GFF-File-Format#gff-data-types) | Planet association (unused) |
| `EntryList` | [List](GFF-File-Format#gff-data-types) | List of quest states |

**Priority Levels:**

- **0 (Highest)**: Main quest line
- **1 (High)**: Important side quests
- **2 (Medium)**: Standard side quests
- **3 (Low)**: Minor tasks
- **4 (Lowest)**: Completed/Container

## Quest Entry (JRLEntry)

| Field | Type | Description |
| ----- | ---- | ----------- |
| `ID` | [uint32](GFF-File-Format#gff-data-types) | State identifier (referenced by scripts/dialogue) |
| `Text` | [CExoLocString](GFF-File-Format#gff-data-types) | [Journal](GFF-File-Format#jrl-journal) text displayed for this state |
| `End` | [uint16](GFF-File-Format#gff-data-types) | 1 if this state completes the quest [[`jrl.py` L153](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/jrl.py#L153)] |
| `XP_Percentage` | [float (single)](GFF-File-Format#gff-data-types) | XP reward multiplier for reaching this state [[`jrl.py` L155](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/jrl.py#L155)] |

**Quest Updates:**

- Scripts use `AddJournalQuestEntry("Tag", ID)` to update quests.
- Dialogues use `Quest` and `QuestEntry` fields.
- Only the highest ID reached is typically displayed (unless `AllowOverrideHigher` is set in `global.jrl` logic).
- `End=1` moves the quest to the "Completed" tab.

## Implementation Notes

- **global.jrl**: The master [journal files](GFF-File-Format#jrl-journal) for the entire game.
- **Module JRLs**: Not typically used; most quests are global.
- **XP Rewards**: `XP_Percentage` scales the `journal.2da` XP value for the quest.

### See also

- [GFF-File-Format](GFF-File-Format) -- Generic format underlying JRL
- [GFF-DLG (Dialogue)](GFF-Creature-and-Dialogue#dlg) - Quest/QuestEntry updates from conversations
- [NCS File Format](NCS-File-Format) - Scripts that call journal API
- [Bioware Aurora Journal Format](Bioware-Aurora-Items-Economy-and-Narrative#journal) - Official journal specification


---

<a id="fac"></a>

# FAC (Faction) File Format

FAC files are GFF-based format files that store faction definitions and reputation relationships between factions in KotOR modules. The file is typically named `repute.fac` in modules. FAC files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official BioWare Documentation:** For the authoritative BioWare Aurora Engine Faction Format specification, see [Bioware Aurora Faction Format](Bioware-Aurora-Items-Economy-and-Narrative#faction).

**Source:** This documentation is based on the official BioWare Aurora Engine Faction Format PDF, contained in **[xoreos-docs](https://github.com/xoreos/xoreos-docs)**: [`specs/bioware/Faction_Format.pdf`](https://github.com/xoreos/xoreos-docs/blob/master/specs/bioware/Faction_Format.pdf).

---

## Overview

A Faction is a control system for determining how game objects interact with each other in terms of friendly, neutral, and hostile reactions. Faction information is stored in the `repute.fac` file in a module or savegame. This file uses BioWare's Generic File Format (GFF), and the GFF FileType string in the header of `repute.fac` is `"FAC "`.

**Related Files:**

- `repute.2da` - Default faction standings (see [2DA File Format](2DA-File-Format))
- `repadjust.2da` - Reputation adjustment values (see [2DA File Format](2DA-File-Format))

PyKotor describes module faction state with [`FACFaction`, `FACReputation`, `FAC`, `construct_fac`, `read_fac`, and `write_fac`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/fac.py#L16), labels the root as [`GFFContent.FAC`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L161), and parses it through the shared [`GFFBinaryReader.load`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82); Holocron Toolset exposes the same `repute.fac` data where its module and generic GFF workflows surface faction editing. Other engines again keep FAC as ordinary GFF, including reone's [`gff.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/gff.cpp) and [`gffreader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/gffreader.cpp), KotOR.js's [`GFFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), Kotor.NET's [`GFF.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18), and xoreos's Aurora stack.

---

## Top Level Struct

The top-level GFF struct contains two lists:

| Label      | Type | Description                                                          |
| ---------- | ---- | -------------------------------------------------------------------- |
| FactionList | List | List of Faction Structs (StructID = list index). Defines what Factions exist in the module. |
| RepList    | List | List of Reputation Structs (StructID = list index). Defines how each Faction stands with every other Faction. |

---

## Faction Struct

Each Faction Struct in the FactionList defines a single faction. The StructID corresponds to the faction's index in the list, which is used as the faction ID in reputation relationships.

| Label          | Type      | Description                                                                                                 |
| -------------- | --------- | ----------------------------------------------------------------------------------------------------------- |
| FactionName    | CExoString | Name of the Faction.                                                                                        |
| FactionGlobal  | WORD      | Global Effect flag. 1 if all members of this faction immediately change their standings with respect to another faction if just one member of this faction changes it standings. 0 if other members of a faction do not change their standings in response to a change in a single member. |
| FactionParentID | DWORD     | Index into the Top Level Struct's FactionList specifying the Faction from which this Faction was derived. The first four standard factions (PC, Hostile, Commoner, and Merchant) have no parents, and use `0xFFFFFFFF` as their FactionParentID. No other Factions can use this value. |

### Standard Factions

KotOR modules typically contain the following standard factions (in order):

1. **PC (Player)** - Index 0, Parent: `0xFFFFFFFF`
2. **Hostile** - Index 1, Parent: `0xFFFFFFFF`
3. **Commoner** - Index 2, Parent: `0xFFFFFFFF`
4. **Merchant** - Index 3, Parent: `0xFFFFFFFF`
5. **Defender** - Index 4, Parent: `0xFFFFFFFF` (KotOR 2 only)

---

## Reputation Struct

Each Reputation Struct in the RepList describes how one faction feels about another faction. Feelings need not be mutual. For example, Exterminators might be hostile to Rats, but Rats may be neutral to Exterminators, so that a Rat would only attack a Hunter or run away from a Hunter if a Hunter attacked the Rat first.

| Label     | Type  | Description                                                                                    |
| --------- | ----- | ---------------------------------------------------------------------------------------------- |
| FactionID1 | DWORD | Index into the Top-Level Struct's FactionList. "Faction1"                                    |
| FactionID2 | DWORD | Index into the Top-Level Struct's FactionList. "Faction2"                                    |
| FactionRep | DWORD | How Faction2 perceives Faction1. 0–10 = Faction2 is hostile to Faction1, 11–89 = Faction2 is neutral to Faction1, 90–100 = Faction2 is friendly to Faction1 [[`FactionManager.ts` L131–L141](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/managers/FactionManager.ts#L131)]; default 50 when field absent [[`fac.py` L134](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/fac.py#L134)] |

### Reputation Values

| Range | Relationship              | Description                                                                 |
| ----- | ------------------------- | --------------------------------------------------------------------------- |
| 0–10  | Hostile                   | Faction2 will attack Faction1 on sight [[`IsHostile` L132](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/managers/FactionManager.ts#L132)]. |
| 11–89 | Neutral                   | Faction2 is neutral to Faction1. No automatic aggression [[`IsNeutral` L136](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/managers/FactionManager.ts#L136)]. |
| 90–100| Friendly                  | Faction2 is friendly to Faction1. Will not attack and may assist [[`IsFriendly` L140](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/managers/FactionManager.ts#L140)]. |

### RepList Completeness

For the RepList to be exhaustively complete, it requires N*N elements, where N = the number of elements in the FactionList. However, the way that the PC Faction (FactionID2 == 0) feels about any other faction is actually meaningless, because PCs are player-controlled and not subject to faction-based AI reactions. Therefore, any Reputation Struct where FactionID2 == 0 (i.e., PC) is not strictly necessary, and can therefore be omitted from the RepList.

Thus, for the RepList to be sufficiently complete, it requires N*N - N elements, where N = the number of elements in the FactionList, assuming that one of those Factions is the PC Faction.

In practice, however, the RepList may contain anywhere from (N*N - N) to (N*N - 1) elements, due to a small idiosyncrasy in how the toolset generates and saves the list. When a new faction is created, up to two new entries may appear for the PC Faction.

From all the above, it follows that a module that contains no user-defined factions will have exactly N*N - N Faction Structs, where N = 5. Modules containing user-defined factions will have more. The maximum number of Faction Structs in the RepList is N*N - 1, because the Player Faction itself can never be a parent faction.

---

## Related 2DA Files

### repute.2da

The `repute.2da` file defines default faction standings. Each row corresponds to a faction ID, and columns represent how that faction feels about other factions.

**Rows (by faction ID):**

- Row 0: Player
- Row 1: Hostile
- Row 2: Commoner
- Row 3: Merchant
- Row 4: Defender (KotOR 2 only)

**Columns:**

- `LABEL` - String: Programmer label; name of faction being considered by the faction named in each of the other columns. Row number is the faction ID.
- `HOSTILE` - Integer: How the Hostile faction feels about the other factions
- `COMMONER` - Integer: How the Commoner faction feels about the other factions
- `MERCHANT` - Integer: How the Merchant faction feels about the other factions
- `DEFENDER` - Integer: How the Defender faction feels about the other factions

**Note:** Do not add new rows to `repute.2da`. They will be ignored.

### repadjust.2da

The `repadjust.2da` file describes how faction reputation standings change in response to different faction-affecting actions, how the presence of witnesses affects the changes, and by how much the changes occur.

**Rows (action types - hardcoded, do not change order):**

- Attack
- Theft
- Kill
- Help

**Columns:**

- `LABEL` - String: Programmer label; name of an action.
- `PERSONALREP` - Integer: Personal reputation adjustment of how the target feels about the perpetrator of the action named in the LABEL.
- `FACTIONREP` - Integer: Base faction reputation adjustment in how the target's Faction feels about the perpetrator. This reputation adjustment is modified further by the effect of witnesses, as controlled by the columns described below. Note that a witness only affects faction standing if the witness belongs to a Global faction.
- `WITFRIA` - Integer: Friendly witness target faction reputation adjustment.
- `WITFRIB` - Integer: Friendly witness personal reputation adjustment.
- `WITFRIC` - Integer: Friendly witness faction reputation adjustment.
- `WITNEUA` - Integer: Neutral witness target faction reputation adjustment.
- `WITNEUB` - Integer: Neutral witness personal reputation adjustment.
- `WITNEUC` - Integer: Neutral witness faction reputation adjustment.
- `WITENEA` - Integer: Enemy witness target faction reputation adjustment.
- `WITENEB` - Integer: Enemy witness personal reputation adjustment.
- `WITENEC` - Integer: Enemy witness faction reputation adjustment.

**Note:** Do not change the order of rows in `repadjust.2da`. Adding new rows will have no effect.

---

## Usage Examples

### Reading a FAC File

```python
from pykotor.resource.generics.fac import read_fac

# Read from file
fac = read_fac("module/repute.fac")

# Access factions
for i, faction in enumerate(fac.factions):
    print(f"Faction {i}: {faction.name}")
    print(f"  Global Effect: {faction.global_effect}")
    print(f"  Parent ID: {faction.parent_id}")

# Access reputations
for rep in fac.reputations:
    print(f"Faction {rep.faction_id2} perceives Faction {rep.faction_id1} as: {rep.reputation}")
```

### Creating a FAC File

```python
from pykotor.resource.generics.fac import FAC, FACFaction, FACReputation, write_fac

fac = FAC()

# Add standard factions
pc = FACFaction()
pc.name = "PC"
pc.global_effect = False
pc.parent_id = 0xFFFFFFFF
fac.factions.append(pc)

hostile = FACFaction()
hostile.name = "Hostile"
hostile.global_effect = True
hostile.parent_id = 0xFFFFFFFF
fac.factions.append(hostile)

# Add reputation relationship
rep = FACReputation()
rep.faction_id1 = 1  # Hostile
rep.faction_id2 = 0  # PC
rep.reputation = 5   # Hostile (0-10 range)
fac.reputations.append(rep)

# Write to file
write_fac(fac, "output/repute.fac")
```

---

## Implementation Notes

- Faction IDs correspond to list indices in the FactionList
- The PC faction (index 0) typically has no reputation entries where FactionID2 == 0, as PC reactions are player-controlled
- Standard factions use `0xFFFFFFFF` as their parent ID
- Reputation values outside the 0-100 range may cause undefined behavior
- Global factions propagate reputation changes across all members when one member's reputation changes

### See also

- [GFF File Format](GFF-File-Format) - Parent GFF format
- [2DA-repute](2DA-File-Format#repute2da) - Default faction standings table
- [2DA File Format](2DA-File-Format) - repadjust.2da and repute.2da structure
- [Bioware Aurora Faction](Bioware-Aurora-Items-Economy-and-Narrative#faction) - Official faction specification


---

### See also

- [GFF File Format](GFF-File-Format) -- Binary container format and GFF family overview
- [GFF Creature and Dialogue](GFF-Creature-and-Dialogue) -- UTC and DLG types
- [GFF Spatial Objects](GFF-Spatial-Objects) -- Placeables, doors, triggers, encounters, waypoints
- [GFF Module and Area](GFF-Module-and-Area) -- ARE, GIT, IFO module data
- [Bioware Aurora Items Economy and Narrative](Bioware-Aurora-Items-Economy-and-Narrative) -- Official specification
- [Concepts](Concepts) -- Resource resolution and shared vocabulary

