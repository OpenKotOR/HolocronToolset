# GFF Types: Creature and Dialogue

Creature templates and dialogue trees are the two GFF types that most directly define how characters behave and speak. A UTC stores everything about a creature — stats, appearance, inventory, scripts [[`UTC`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L36)] — while DLG encodes branching conversation logic with conditions, animations, and voice-over references [[`DLG`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/dlg/base.py#L36)].

## Contents

- [UTC — Creature](#utc)
- [DLG — Dialogue / Conversation](#dlg)

---

<a id="utc"></a>

# UTC (Creature)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTC files define [creature templates](GFF-File-Format#utc-creature) including NPCs, party members, enemies, and the player character. They are comprehensive [GFF files](GFF-File-Format) containing all data needed to spawn and control a creature in the game world. UTC files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Creature format specification, see [Bioware Aurora Creature Format](Bioware-Aurora-Creature).

**For mod developers:**

- To modify creature templates in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFF-Syntax#gfflist-syntax).
- For general modding, see [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers).

**Related formats:**

- [2DA](2DA-File-Format) (appearance, portraits, classes, feats, racialtypes, creaturespeed)
- [SSF](Audio-and-Localization-Formats#ssf)
- [TLK](Audio-and-Localization-Formats#tlk)
- [MDL](MDL-MDX-File-Format)
- [TPC](Texture-Formats#tpc)
- [GFF-UTI](GFF-Items-and-Economy#uti) (inventory items)

UTC support in PyKotor is implemented by the in-memory `UTC` model and GFF reader/writer pipeline ([`utc.py` L36+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L36), [`construct_utc` L494+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L494), [`read_utc` L982+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L982), [`write_utc` L992+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L992)). UTC is identified as `GFFContent.UTC` in the shared GFF type map and uses the common binary GFF loader ([`gff_data.py` L150](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L150), [`io_gff.py` L82+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82)). The Holocron Toolset exposes these fields in its creature editor ([`toolset/gui/editors/utc.py`](https://github.com/OpenKotOR/HolocronToolset/src/toolset/gui/editors/utc.py)), and other engines parse UTC through their generic GFF stacks ([reone `gff.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/gff.cpp), [reone `gffreader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/gffreader.cpp), [KotOR.js `GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), [Kotor.NET `GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18)). For practical creature-editing workflow examples and troubleshooting, the community index at [Home](Home#community-sources-and-archives) links to current forum threads.

## Core Identity fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | Template identifier for this creature (max 16 characters; should match UTC filename without extension) |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique tag for script/conversation references |
| `FirstName` | [CExoLocString](GFF-File-Format#gff-data-types) | Creature's first name (localized) |
| `LastName` | [CExoLocString](GFF-File-Format#gff-data-types) | Creature's last name (localized) |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment/notes |

## Appearance & Visuals

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Appearance_Type` | UInt32 | Index into [`appearance.2da`](2DA-File-Format#appearance2da) |
| `PortraitId` | [word](GFF-File-Format#gff-data-types) | Index into [`portraits.2da`](2DA-File-Format#portraits2da); 65535 (0xFFFF) = use Portrait ResRef instead |
| `Gender` | [byte](GFF-File-Format#gff-data-types) | 0=Male, 1=Female, 2=Both, 3=Other, 4=None [[`utc.py` L221](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L221)] |
| `Race` | [byte](GFF-File-Format#gff-data-types) | Index into [`racialtypes.2da`](2DA-File-Format#racialtypes2da) [[`utc.py` L219](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L219)]. |
| `SubraceIndex` | [byte](GFF-File-Format#gff-data-types) | Index into subrace.2da; refines race (e.g. subspecies). |
| `BodyVariation` | [byte](GFF-File-Format#gff-data-types) | Body [model](MDL-MDX-File-Format) variation index [[`utc.py` L231](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L231)] |
| `TextureVar` | [byte](GFF-File-Format#gff-data-types) | [texture](Texture-Formats#tpc) variation index [[`utc.py` L232](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L232)] |
| `SoundSetFile` | [word](GFF-File-Format#gff-data-types) | Index into [sound set table](Audio-and-Localization-Formats#ssf) |

## Core Stats & Attributes

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Str` | [byte](GFF-File-Format#gff-data-types) | Strength score (3-255) |
| `Dex` | [byte](GFF-File-Format#gff-data-types) | Dexterity score (3-255) |
| `Con` | [byte](GFF-File-Format#gff-data-types) | Constitution score (3-255) |
| `Int` | [byte](GFF-File-Format#gff-data-types) | Intelligence score (3-255) |
| `Wis` | [byte](GFF-File-Format#gff-data-types) | Wisdom score (3-255) |
| `Cha` | [byte](GFF-File-Format#gff-data-types) | Charisma score (3-255) |
| `HitPoints` | [int16](GFF-File-Format#gff-data-types) | Current hit points |
| `CurrentHitPoints` | [int16](GFF-File-Format#gff-data-types) | Alias for hit points |
| `MaxHitPoints` | [int16](GFF-File-Format#gff-data-types) | Maximum hit points |
| `ForcePoints` | [int16](GFF-File-Format#gff-data-types) | Current Force points (KotOR specific) |
| `CurrentForce` | [int16](GFF-File-Format#gff-data-types) | Alias for Force points |
| `MaxForcePoints` | [int16](GFF-File-Format#gff-data-types) | Maximum Force points |

## Character Progression

| Field | Type | Description |
| ----- | ---- | ----------- |
| `ClassList` | [List](GFF-File-Format#gff-data-types) | List of character classes with levels |
| `Experience` | UInt32 | Total experience points |
| `LevelUpStack` | [List](GFF-File-Format#gff-data-types) | Pending level-up choices |
| `SkillList` | [List](GFF-File-Format#gff-data-types) | Skill ranks (index + rank) |
| `FeatList` | [List](GFF-File-Format#gff-data-types) | Acquired feats |
| `SpecialAbilityList` | [List](GFF-File-Format#gff-data-types) | Special abilities/powers |

**ClassList Struct fields:**

- `Class` ([int32](GFF-File-Format#gff-data-types)): Index into [`classes.2da`](2DA-File-Format#classes2da) ([class definitions](2DA-File-Format#classes2da))
- `ClassLevel` ([int16](GFF-File-Format#gff-data-types)): Levels in this class

**SkillList Struct fields:**

- `Rank` ([byte](GFF-File-Format#gff-data-types)): Skill rank value

**FeatList Struct fields:**

- `Feat` ([word](GFF-File-Format#gff-data-types)): Index into [`feat.2da`](2DA-File-Format#feat2da) ([feat definitions](2DA-File-Format#feat2da))

## Combat & Behavior

| Field | Type | Description |
| ----- | ---- | ----------- |
| `FactionID` | [word](GFF-File-Format#gff-data-types) | Faction identifier (determines hostility) |
| `NaturalAC` | [byte](GFF-File-Format#gff-data-types) | Natural armor class bonus |
| `ChallengeRating` | float | CR for encounter calculations |
| `PerceptionRange` | [byte](GFF-File-Format#gff-data-types) | Perception distance category |
| `WalkRate` | [int32](GFF-File-Format#gff-data-types) | Row index into creaturespeed.2da; sets walk/run movement speed used for pathfinding and animation. |
| `Interruptable` | [byte](GFF-File-Format#gff-data-types) | Can be interrupted during actions |
| `NoPermDeath` | [byte](GFF-File-Format#gff-data-types) | Cannot permanently die |
| `IsPC` | [byte](GFF-File-Format#gff-data-types) | Is player character |
| `Plot` | [byte](GFF-File-Format#gff-data-types) | Plot-critical (cannot die) |
| `MinOneHP` | [byte](GFF-File-Format#gff-data-types) | Cannot drop below 1 HP |
| `PartyInteract` | [byte](GFF-File-Format#gff-data-types) | Shows party selection interface |
| `Hologram` | [byte](GFF-File-Format#gff-data-types) | Rendered as hologram |

## Equipment & Inventory

| Field | Type | Description |
| ----- | ---- | ----------- |
| `ItemList` | [List](GFF-File-Format#gff-data-types) | Inventory items |
| `Equip_ItemList` | [List](GFF-File-Format#gff-data-types) | Equipped items with slots |
| `EquippedRes` | *ResRef* | Deprecated equipment field |

**ItemList Struct fields:**

- `InventoryRes` (*ResRef*): [UTI](GFF-File-Format#uti-item) template *ResRef*
- `Repos_PosX` ([word](GFF-File-Format#gff-data-types)): Inventory grid X position
- `Repos_Posy` ([word](GFF-File-Format#gff-data-types)): Inventory grid Y position
- `Dropable` ([byte](GFF-File-Format#gff-data-types)): Can be dropped/removed

**Equip_ItemList Struct fields:**

- `EquippedRes` (*ResRef*): [UTI](GFF-File-Format#uti-item) template *ResRef*
- Equipment slots reference `equipmentslots.2da`

## Script Hooks

| Field | Type | Description |
| ----- | ---- | ----------- |
| `ScriptAttacked` | *ResRef* | Fires when attacked |
| `ScriptDamaged` | *ResRef* | Fires when damaged |
| `ScriptDeath` | *ResRef* | Fires on death |
| `ScriptDialogue` | *ResRef* | Fires when conversation starts |
| `ScriptDisturbed` | *ResRef* | Fires when inventory disturbed |
| `ScriptEndRound` | *ResRef* | Fires at combat round end |
| `ScriptEndDialogue` | *ResRef* | Fires when conversation ends |
| `ScriptHeartbeat` | *ResRef* | Fires periodically |
| `ScriptOnBlocked` | *ResRef* | Fires when movement blocked |
| `ScriptOnNotice` | *ResRef* | Fires when notices something |
| `ScriptRested` | *ResRef* | Fires after rest |
| `ScriptSpawn` | *ResRef* | Fires on spawn |
| `ScriptSpellAt` | *ResRef* | Fires when spell cast at creature |
| `ScriptUserDefine` | *ResRef* | Fires on user-defined events |

## KotOR-Specific Features

**Alignment:**

- `GoodEvil` ([byte](GFF-File-Format#gff-data-types)): 0-100 scale (0=Dark, 100=Light)
- `LawfulChaotic` ([byte](GFF-File-Format#gff-data-types)): Unused in KotOR

**Multiplayer (Unused in KotOR):**

- `Deity` ([CExoString](GFF-File-Format#gff-data-types))
- `Subrace` ([CExoString](GFF-File-Format#gff-data-types))
- `Morale` ([byte](GFF-File-Format#gff-data-types))
- `MorealBreak` ([byte](GFF-File-Format#gff-data-types))

**Special Abilities:**

- Stored in `SpecialAbilityList` referencing `spells.2da` or feat-based abilities

## Editor reference (min/max and usage)

When editing UTCs in the Holocron Toolset, numeric fields use the following ranges (from GFF types and engine behavior):

- **TemplateResRef, Conversation, script ResRefs:** Max 16 characters (engine ResRef limit).
- **Tag:** No engine-enforced max length; keep unique per module for script lookups (e.g. `GetObjectByTag`).
- **FirstName, LastName, Comment:** Localized or plain string; no fixed max in GFF.
- **Appearance_Type, PortraitId, SoundSetFile, FactionID:** WORD (0–65535); use valid 2DA row indices.
- **Race, Gender, SubraceIndex, PerceptionRange, NaturalAC, ability scores (Str–Cha), skill Rank:** BYTE (0–255). **Race:** row index into `racialtypes.2da` (0 to row count − 1). Save bonuses (fortbonus, refbonus, willbonus): SHORT (-32768–32767).
- **WalkRate:** INT; row index into creaturespeed.2da (0 to row count − 1). Invalid index can cause default or broken movement.
- **HitPoints, CurrentHitPoints, MaxHitPoints, CurrentForce, ForcePoints:** SHORT (0–32767 typical; game does not use negative HP/FP).
- **ChallengeRating:** Float (0–100 typical). **GoodEvil (alignment):** 0–100 (0=Dark, 100=Light).
- **ClassLevel:** SHORT (0–32767); typical level 1–20. **MultiplierSet (K2):** INT32; 0 = default.
- **BlindSpot (K2):** Float 0–360 degrees.

All script hooks store a ResRef to an NCS file; leave blank for no script. The toolset provides tooltips on each field describing how the game uses it and how modders can change it.

## Implementation Notes

[UTC](GFF-File-Format#utc-creature) files are loaded during module initialization or creature spawning. PyKotor reads a UTC via `construct_utc`, which deserializes each GFF field into the [`UTC`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L354) data object [[`utc.py` L354](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L354)].

**Common Use Cases:**

- **Party Members**: Full [UTC](GFF-File-Format#utc-creature) with all progression data, complex equipment
- **Plot NPCs**: Basic stats, specific appearance, dialogue scripts
- **Generic Enemies**: Minimal data, shared appearance, basic AI scripts
- **Vendors**: Specialized with store inventory, merchant scripts
- **Placeables As Creatures**: Invisible creatures for complex scripting

## See also

- [GFF File Format](GFF-File-Format) - Generic format underlying UTC
- [GFF-UTI (Item)](GFF-Items-and-Economy#uti) - Item templates in creature inventory
- Common lookup tables:

  - [2DA appearance](2DA-File-Format#appearance2da)
  - [classes](2DA-File-Format#classes2da)
  - [feat](2DA-File-Format#feat2da)
  - [racialtypes](2DA-File-Format#racialtypes2da)
- [Bioware Aurora Creature Format](Bioware-Aurora-Creature) - Official creature specification


---

<a id="dlg"></a>

# DLG (Dialogue)

Part of the [GFF File Format Documentation](GFF-File-Format).

[DLG files](GFF-File-Format#dlg-dialogue) store conversation trees, forming the core of KotOR's narrative interaction. A [dialogue](GFF-File-Format#dlg-dialogue) consists of a hierarchy of Entry nodes (NPC lines) and Reply nodes (Player options), connected by Links.

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Conversation format specification, see [Bioware Aurora Conversation Format](Bioware-Aurora-Conversation).

DLG files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources:

- [override](Concepts#override-folder)
- MOD/SAV (see [ERF](Container-Formats#erf))
- [KEY/BIF](Container-Formats#key)

**For mod developers:**

- To edit dialogues in the toolset, use the DLG editor.
- For mod patches, see [TSLPatcher GFFList Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax).
- [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers).

**Related formats:**

- [TLK](Audio-and-Localization-Formats#tlk) / [StrRef](Audio-and-Localization-Formats#string-references-strref) — displayed text
- [WAV](Audio-and-Localization-Formats#wav) — voice-over
- [NCS](NCS-File-Format) — scripts
- [GFF-JRL](GFF-Items-and-Economy#jrl) — journal updates
- [MDL](MDL-MDX-File-Format) — camera models

PyKotor implements DLG as a graph of entries, replies, and links with GFF-based read/write support ([`dlg/base.py` L36+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/dlg/base.py#L36), [`construct_dlg` L29+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/gff.py#L29), [`read_dlg` L566+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/gff.py#L566), [`write_dlg` L593+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/gff.py#L593)). DLG is identified as `GFFContent.DLG` and decoded by the shared GFF binary reader ([`gff_data.py` L160](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L160), [`io_gff.py` L82+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82)). PyKotor also supports optional Twine interchange for dialogue authoring flows ([`dlg/io/twine.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/twine.py)). The Holocron Toolset exposes DLG editing in the GUI workflow ([Holocron Toolset: Getting Started](Holocron-Toolset-Getting-Started)), and other engines/tools load DLG through generic GFF or dialogue-specific wrappers ([reone `gff.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/gff.cpp), [reone `gffreader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/gffreader.cpp), [KotOR.js `DLGObject.ts` L31+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/DLGObject.ts#L31), [KotOR.js `GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), [Kotor.NET `GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18)).

## Conversation Properties

| Field | Type | Description |
| ----- | ---- | ----------- |
| `DelayEntry` | [int32](GFF-File-Format#gff-data-types) | Delay before conversation starts |
| `DelayReply` | [int32](GFF-File-Format#gff-data-types) | Delay before player reply options appear |
| `NumWords` | [int32](GFF-File-Format#gff-data-types) | Total word count (unused) |
| `PreventSkipping` | [byte](GFF-File-Format#gff-data-types) | Prevents skipping dialogue lines |
| `Skippable` | [byte](GFF-File-Format#gff-data-types) | Allows skipping dialogue |
| `Sound` | *ResRef* | Background sound loop |
| `AmbientTrack` | [int32](GFF-File-Format#gff-data-types) | Background music track ID |
| `CameraModel` | *ResRef* | Camera [model](MDL-MDX-File-Format) for cutscenes |
| `ComputerType` | [byte](GFF-File-Format#gff-data-types) | Interface style (0=Modern, 1=Ancient) |
| `ConversationType` | [byte](GFF-File-Format#gff-data-types) | 0=Human, 1=Computer, 2=Other |
| `OldHitCheck` | [byte](GFF-File-Format#gff-data-types) | Legacy hit check flag (unused) |

**Conversation types:**

- **Human**: Cinematic camera, [voice-over](Audio-and-Localization-Formats#wav) support, standard UI
- **Computer**: Full-screen terminal interface, no [voice-over](Audio-and-Localization-Formats#wav), green text
- **Other**: Overhead text bubbles (bark strings)

## Script Hooks

| Field | Type | Description |
| ----- | ---- | ----------- |
| `EndConversation` | *ResRef* | Fires when conversation ends normally |
| `EndConverAbort` | *ResRef* | Fires when conversation is aborted |

## [node](MDL-MDX-File-Format#node-structures) Lists

[DLG](GFF-File-Format#dlg-dialogue) files use two main lists for [nodes](MDL-MDX-File-Format#node-structures) and one for starting points:

| List field | Contains | Description |
| ---------- | -------- | ----------- |
| `EntryList` | DLGEntry | NPC dialogue lines |
| `ReplyList` | DLGReply | Player response options |
| `StartingList` | DLGLink | Entry points into the [dialogue tree](GFF-File-Format#dlg-dialogue) |

**Graph structure:**

- **StartingList** links to **EntryList** nodes (NPC starts)
- **EntryList** [nodes](MDL-MDX-File-Format#node-structures) link to **ReplyList** nodes (Player responds)
- **ReplyList** [nodes](MDL-MDX-File-Format#node-structures) link to **EntryList** nodes (NPC responds)
- Links can be conditional (Script checks)

## DLGNode Structure (Entries & Replies)

Both Entry and Reply [nodes](MDL-MDX-File-Format#node-structures) share common fields:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Text` | [CExoLocString](GFF-File-Format#gff-data-types) | Dialogue text |
| `VO_ResRef` | *ResRef* | Voice-over audio file |
| `Sound` | *ResRef* | Sound effect *ResRef* |
| `Script` | *ResRef* | Script to execute (Action) |
| `Delay` | [int32](GFF-File-Format#gff-data-types) | Delay before text appears |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment |
| `Speaker` | [CExoString](GFF-File-Format#gff-data-types) | Speaker tag (Entry only) |
| `Listener` | [CExoString](GFF-File-Format#gff-data-types) | Listener tag (unused) |
| `Quest` | [CExoString](GFF-File-Format#gff-data-types) | Journal tag to update |
| `QuestEntry` | [int32](GFF-File-Format#gff-data-types) | [journal entry](GFF-File-Format#jrl-journal) ID |
| `PlotIndex` | [int32](GFF-File-Format#gff-data-types) | Plot index (legacy) |
| `PlotXPPercentage` | float | XP reward percentage |

**Cinematic fields:**

- `CameraAngle`: Camera angle ID
- `CameraID`: Specific camera ID
- `CameraAnimation`: [animation](MDL-MDX-File-Format#animation-header) to play
- `CamFieldOfView`: Camera FOV
- `CamHeightOffset`: Camera height
- `CamVidEffect`: Video effect ID

**[animation](MDL-MDX-File-Format#animation-header) List:**

- List of [animations](MDL-MDX-File-Format#animation-header) to play on participants
- `Participant`: Tag of object to animate
- `Animation`: [animation](MDL-MDX-File-Format#animation-header) ID

## DLGLink structure

Links connect [nodes](MDL-MDX-File-Format#node-structures) and define flow control:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Index` | [int32](GFF-File-Format#gff-data-types) | Index of target [node](MDL-MDX-File-Format#node-structures) in Entry/Reply list |
| `Active` | *ResRef* | Conditional script (returns TRUE/FALSE) |
| `Script` | *ResRef* | Action script (executed on transition) |
| `IsChild` | [byte](GFF-File-Format#gff-data-types) | 1 if linking to [node](MDL-MDX-File-Format#node-structures) in list, 0 if logic link |
| `LinkComment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment |

**Conditional Logic:**

- **Active** script determines if link is available
- If script returns FALSE, link is skipped
- Engine evaluates links top-to-bottom
- First valid link is taken (for NPC lines)
- All valid links displayed (for Player replies)

**KotOR 2 Logic Extensions:**

- `Logic`: 0=AND, 1=OR (combines Active conditions)
- `Not`: Negates condition result

## Implementation Notes

**Flow Evaluation:**

1. Conversation starts
2. Engine evaluates `StartingList` links
3. First link with valid `Active` condition is chosen
4. Transition to target `EntryList` [node](MDL-MDX-File-Format#node-structures)
5. Execute Entry `Script`, play `VO`, show `Text`
6. Evaluate Entry's links to `ReplyList`
7. Display all valid Replies to player
8. Player selects Reply
9. Transition to target `ReplyList` [node](MDL-MDX-File-Format#node-structures)
10. Evaluate Reply's links to `EntryList`
11. Loop until no links remain or `EndConversation` called

**Computer Dialogues:**

- `ComputerType=1` (Ancient) changes font/background
- No cinematic cameras
- Used for terminals and datapads

**Bark strings:**

- `ConversationType=2`
- No cinematic mode, text floats over head
- Non-blocking interaction

**Journal Integration:**

- `Quest` and `QuestEntry` fields update [journal entries](GFF-File-Format#jrl-journal) directly
- Eliminates need for scripts to update quests

## Twine Interoperability

PyKotor exposes a Twine bridge for DLGs to support authoring and visualization in story tools:

- Export uses `Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/twine.py::_dlg_to_story` to turn starters, entries, and replies into `TwinePassage` objects. It emits unique names for duplicate speakers, preserves `is_child` and `Active` script on links, and writes KotOR metadata into `PassageMetadata.custom` (camera anim/angle/id, fade type, quest, sound, VO, plus `text_<language>_<gender>` variants).
- Import uses `Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/twine.py::_story_to_dlg` together with `FormatConverter.restore_kotor_metadata` to hydrate `DLGEntry`/`DLGReply` objects, restoring multilingual text from `custom` keys and mapping camera/sound/quest metadata back onto the [nodes](MDL-MDX-File-Format#node-structures).
- Twine-only data (style, script, tag colors, format info, zoom, creator metadata) is stored in `[DLG](GFF-File-Format#dlg-dialogue).comment` as JSON via `FormatConverter.store_twine_metadata` and restored on export
- `tag_colors` are kept as `Color` values (see `Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/twine_data.py`).
- Start [node](MDL-MDX-File-Format#node-structures) selection mirrors engine behavior: first starter becomes `startnode` when exporting, and missing `startnode` on import falls back to the first entry passage.

### See also

- [GFF File Format](GFF-File-Format) - Generic format underlying DLG
- [TLK File Format](Audio-and-Localization-Formats#tlk) -- Talk table container
- [StrRef](Audio-and-Localization-Formats#string-references-strref) -- String index semantics used by DLG fields
- [GFF-JRL (Journal)](GFF-Items-and-Economy#jrl) - Journal entries referenced by Quest/QuestEntry
- [Bioware Aurora Conversation Format](Bioware-Aurora-Conversation) - Official conversation specification


---

