# GFF Types: Items and Economy

Items, merchants, journals, and factions form the game’s economy and progression systems. UTI defines every equippable or consumable object [[`UTI`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L22)], UTM describes store inventories and pricing, JRL tracks quest progress visible to the player, and FAC controls inter-faction hostility and friendship.

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

PyKotor models UTI templates with the dedicated [`UTI` data class and `read_uti` / `write_uti` helpers](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L22) on top of the shared binary [`GFFBinaryReader.load`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) pipeline, while Holocron Toolset exposes the same item fields through its [`uti.py` editor](https://github.com/OldRepublicDevs/HolocronToolset/src/toolset/gui/editors/uti.py). Other toolchains keep UTI in the generic GFF family as well, including reone's [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp) and [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp), KotOR.js's [`GFFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), Kotor.NET's [`GFF.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18), and xoreos's Aurora GFF stack.

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
| `ModelVariation` | [byte](GFF-File-Format#gff-data-types) | [model](MDL-MDX-File-Format) variation index (1-99) |
| `BodyVariation` | [byte](GFF-File-Format#gff-data-types) | Body variation for armor (1-9) |
| `TextureVar` | [byte](GFF-File-Format#gff-data-types) | [texture](Texture-Formats#tpc) variation for armor (1-9) |

**BaseItem types** (from [`baseitems.2da`](2DA-File-Format#baseitems2da)):

- **0-10**: Various weapon types (shortsword, longsword, blaster, etc.)
- **11-30**: Armor types and shields
- **31-50**: Quest items, grenades, medical supplies
- **51-70**: Upgrades, armbands, belts
- **71-90**: Droid equipment, special items
- **91+**: KotOR2-specific items

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
- `ChanceAppear` ([byte](GFF-File-Format#gff-data-types)): Percentage chance to appear (random loot)
- `UsesPerDay` ([byte](GFF-File-Format#gff-data-types)): Daily usage limit (0 = unlimited)
- `UsesLeft` ([byte](GFF-File-Format#gff-data-types)): Remaining uses for today

**Common Item Properties:**

- **Attack Bonus**: +1 to +12 attack rolls
- **Damage Bonus**: Additional damage dice
- **Ability Bonus**: +1 to +12 to ability scores
- **Damage Resistance**: Reduce damage by amount/percentage
- **Saving Throw Bonus**: +1 to +20 to saves
- **Skill Bonus**: +1 to +50 to skills
- **Immunity**: Immunity to damage type or condition
- **On Hit**: Cast spell/effect on successful hit
- **Keen**: Expanded critical threat range
- **Massive Criticals**: Bonus damage on critical hit

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
| `BodyVariation` | [byte](GFF-File-Format#gff-data-types) | Body [model](MDL-MDX-File-Format) variation (1-9) |
| `TextureVar` | [byte](GFF-File-Format#gff-data-types) | [texture](Texture-Formats#tpc) variation (1-9) |
| `ModelVariation` | [byte](GFF-File-Format#gff-data-types) | [model](MDL-MDX-File-Format) type (typically 1-3) |
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

- Weapons can have multiple upgrade slots
- Each slot has specific type restrictions
- Lightsabers get color customization
- Armor upgrades affect appearance

## Visual & Audio

| Field | Type | Description |
| ----- | ---- | ----------- |
| `ModelVariation` | [byte](GFF-File-Format#gff-data-types) | Base [model](MDL-MDX-File-Format) index |
| `BodyVariation` | [byte](GFF-File-Format#gff-data-types) | Body [model](MDL-MDX-File-Format) for armor |
| `TextureVar` | [byte](GFF-File-Format#gff-data-types) | [texture](Texture-Formats#tpc) variant |

**[model](MDL-MDX-File-Format) Resolution:**

1. Engine looks up `BaseItem` in [`baseitems.2da`](2DA-File-Format#baseitems2da)
2. Retrieves [model](MDL-MDX-File-Format) prefix (e.g., `w_lghtsbr`)
3. Appends variations: `w_lghtsbr_001.mdl`
4. [textures](Texture-Formats#tpc) follow similar pattern

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

**Item Instantiation:**

1. **Template Loading**: [GFF](GFF-File-Format) structure parsed from [UTI](GFF-File-Format#uti-item)
2. **Property Application**: PropertiesList merged into item
3. **Cost Calculation**: Base cost + AddCost + property costs
4. **Visual Setup**: resolve [model](MDL-MDX-File-Format) variants and [texture](Texture-Formats#tpc) variants
5. **Stack Handling**: StackSize determines inventory behavior

**Property System:**

- Properties defined in [`itempropdef.2da`](2DA-File-Format#itempropdef2da)
- Each property has cost formula
- Properties stack or override based on type
- Engine recalculates effects when equipped

**Performance Optimization:**

- Simple items (no properties) load fastest
- Complex property lists increase spawn time
- Stack-based items share template data
- Unique items (non-stackable) require instance data

**Common Item Categories:**

**Weapons:**

- Melee: lightsabers, swords, vibroblades
- Ranged: blasters, rifles, heavy weapons
- Properties: damage, attack bonus, critical

**Armor:**

- Light, Medium, Heavy classes
- Robes (Force user specific)
- Properties: AC bonus, resistance, ability boosts

**Upgrades:**

- Weapon: Power crystals, energy cells, lens
- Armor: Overlays, underlays, plates
- Applied via crafting interface

**Consumables:**

- Medpacs: Restore health
- Stimulants: Temporary bonuses
- Grenades: Area damage/effects
- Single-use or limited charges

**Quest Items:**

- Plot-flagged, cannot be lost
- Often no combat value
- Trigger scripted events

**Droid Equipment:**

- Special items for droid party members
- Sensors, shields, weapons
- Different slot types than organic characters

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

UTM files are GFF resources with root content type **`UTM`** ([`GFFContent.UTM`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L156)) that define **merchant templates**: localized name, pricing (mark up / mark down), buy/sell flags, optional `OnOpenStore` script hook, and an **`ItemList`** of stock lines. Module **store instances** in the [**GIT**](GFF-Module-and-Area#git) reference a UTM template via the area’s store list (PyKotor maps GIT stores to [`ResourceType.UTM`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/git.py#L107); instance wrapper [`GITStore` L967–L1000](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/git.py#L967-L1000)). UTMs resolve like other resources: [override → MOD/SAV → KEY/BIF](Concepts#resource-resolution-order).

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
| `MarkUp` | int32 | Markup when selling **to** the player (percent). |
| `MarkDown` | int32 | Markdown when buying **from** the player (percent). |
| `OnOpenStore` | ResRef | Script executed when the store UI opens. |
| `Comment` | CExoString | Authoring comment. |
| `BuySellFlag` | byte | Bit 0 = can buy from player; bit 1 = can sell to player ([`construct_utm` L173–L174](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L173-L174)). |
| `ItemList` | List | Stock entries (see below). |
| `ID` | byte | Legacy / unused in practice; PyKotor can still emit it when `use_deprecated=True` in [`dismantle_utm` L218–L219](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L218-L219). |

## ItemList element struct

Each list element is a struct with (at minimum) the fields PyKotor reads and writes:

| Field | GFF type | Role |
| ----- | -------- | ---- |
| `InventoryRes` | ResRef | Item template ([UTI](GFF-Items-and-Economy#uti)) resref. |
| `Infinite` | byte | Infinite stock when non-zero. |
| `Dropable` | byte | Droppable flag (PyKotor writes the field only when true — [`dismantle_utm` L213–L214](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L213-L214)). |
| `Repos_PosX` | uint16 | Repository grid X (writer uses slot index — [`dismantle_utm` L211](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L211)). |
| `Repos_PosY` | uint16 | Repository grid Y (writer uses `0` — same block). |

PyKotor documents and round-trips merchant templates through [`UTM`, `construct_utm`, `dismantle_utm`, `read_utm`, and `write_utm`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L18) on top of the shared [`GFFBinaryReader.load`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) path, and the same merchant-root-as-GFF approach appears in reone's [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp) and [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp), KotOR.js's [`GFFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), Kotor.NET's [`UTM.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Resources/KotorUTM/UTM.cs#L13-L35) plus [`GFF.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18), and xoreos's Aurora GFF loader stack.

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

PyKotor represents journals through [`JRL`, `JRLQuest`, `JRLEntry`, `construct_jrl`, `read_jrl`, and `write_jrl`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/jrl.py#L18), tags them as [`GFFContent.JRL`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L166), and decodes them through the same shared [`GFFBinaryReader.load`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) path that Holocron Toolset builds on in its dialogue and module editors. Other implementations also keep JRL inside the generic GFF family, including reone's [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp) and [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp), KotOR.js's [`GFFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), Kotor.NET's [`GFF.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18), and xoreos's Aurora reader stack.

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
| `Priority` | [int32](GFF-File-Format#gff-data-types) | Sorting priority (0=Highest, 4=Lowest) |
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
| `ID` | [int32](GFF-File-Format#gff-data-types) | State identifier (referenced by scripts/dialogue) |
| `Text` | [CExoLocString](GFF-File-Format#gff-data-types) | [Journal](GFF-File-Format#jrl-journal) text displayed for this state |
| `End` | [byte](GFF-File-Format#gff-data-types) | 1 if this state completes the quest |
| `XP_Percentage` | float | XP reward multiplier for reaching this state |

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

PyKotor describes module faction state with [`FACFaction`, `FACReputation`, `FAC`, `construct_fac`, `read_fac`, and `write_fac`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/fac.py#L16), labels the root as [`GFFContent.FAC`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L161), and parses it through the shared [`GFFBinaryReader.load`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82); Holocron Toolset exposes the same `repute.fac` data where its module and generic GFF workflows surface faction editing. Other engines again keep FAC as ordinary GFF, including reone's [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp) and [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp), KotOR.js's [`GFFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), Kotor.NET's [`GFF.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18), and xoreos's Aurora stack.

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
| FactionRep | DWORD | How Faction2 perceives Faction1. 0-10 = Faction2 is hostile to Faction1, 11-89 = Faction2 is neutral to Faction1, 90-100 = Faction2 is friendly to Faction1 |

### Reputation Values

| Range | Relationship              | Description                                                                 |
| ----- | ------------------------- | --------------------------------------------------------------------------- |
| 0-10  | Hostile                   | Faction2 will attack Faction1 on sight.                                    |
| 11-89 | Neutral                   | Faction2 is neutral to Faction1. No automatic aggression.                  |
| 90-100| Friendly                  | Faction2 is friendly to Faction1. Will not attack and may assist.          |

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
