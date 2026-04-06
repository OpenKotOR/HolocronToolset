# Level Layout Formats

The KotOR engine assembles playable areas from three complementary data files. **LYT** (Layout) files define the spatial arrangement of rooms within a module — which [models](MDL-MDX-File-Format) go where, how they are positioned and oriented, and where door hooks connect adjacent spaces ([`LYTRoom` L182](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L182), [reone `lytreader.cpp` L27](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/lytreader.cpp#L27), [xoreos `lytfile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/lytfile.cpp)). **VIS** (Visibility) files tell the renderer which rooms can see which other rooms, enabling the engine to skip drawing geometry that the player cannot observe ([`vis_data.py` `VIS` L56](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/vis/vis_data.py#L56), [reone `visreader.cpp` L29](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/visreader.cpp#L29)). **BWM** (Binary Walkmesh) files — also known as WOK files — define the walkable surfaces, material types, and adjacent-face connectivity that the pathfinding and collision systems use to move characters through the world ([`bwm_data.py` `BWM` L145](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py#L145), [KotOR.js `OdysseyWalkMesh.ts` L301](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/odyssey/OdysseyWalkMesh.ts#L301)). xoreos's KotOR engine status page and its pathfinding research notes are especially useful external checks on this trio because they call out initial module and area loading, evaluation of room-to-room visibility data, and walkmesh-driven navigation/path smoothing as separate parts of the same subsystem [[Knights of the Old Republic](https://wiki.xoreos.org/index.php?title=Knights_of_the_Old_Republic), [Pathfinding](https://wiki.xoreos.org/index.php?title=Pathfinding)].

## Contents

- [LYT — Level Layout](#lyt)
- [VIS — Visibility Data](#vis)
- [BWM — Binary Walkmesh](#bwm)

---

<a id="lyt"></a>

# LYT — Level Layout

LYT (Layout) files define how the rooms that make up a playable area are positioned in 3D space ([`LYTRoom` L182](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L182), [KotOR.js `LYTObject.ts` L19](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/LYTObject.ts#L19)). Each entry in the layout specifies a room [model](MDL-MDX-File-Format) name and its world-space coordinates, so the engine knows where to place the geometry when loading a module ([`LYTAsciiReader.load` L60](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/io_lyt.py#L60), [reone `lytreader.cpp` `processLine` L37](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/lytreader.cpp#L37)). Beyond rooms, LYT files also describe swoop-track props ([`LYTTrack` L259](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L259)), obstacles ([`LYTObstacle` L306](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L306)), and door-hook transforms ([`LYTDoorHook` L353](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L353)) that connect adjacent spaces. The format is plain text with a deterministic section order, making it straightforward to inspect and edit.

The engine combines LYT spatial data with [MDL/MDX](MDL-MDX-File-Format) geometry, [VIS](Level-Layout-Formats#vis) visibility culling, and [BWM](Level-Layout-Formats#bwm) walkmesh navigation to assemble the final area. LYT files are resolved through the standard [resource resolution order](Concepts#resource-resolution-order) (override → MOD/SAV → KEY/BIF). xoreos's KotOR engine notes treat that combined area-loading pipeline as a milestone in its own right, which is a useful reminder that LYT is not an isolated helper file: it is part of the core room-loading path [[Knights of the Old Republic](https://wiki.xoreos.org/index.php?title=Knights_of_the_Old_Republic)]. For area modding workflows, see [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide) and [HoloPatcher](HoloPatcher#mod-developers). Related GFF data lives in [ARE](GFF-Module-and-Area#are) area definitions.

## Table of Contents

- LYT — Level Layout
  - Table of Contents
  - [Format overview](#format-overview)
  - [Syntax](#syntax)
    - [Room Definitions](#room-definitions)
    - [Track Definitions](#track-definitions)
    - [Obstacle Definitions](#obstacle-definitions)
    - [Door Hooks](#door-hooks)
  - [Coordinate system](#coordinate-system)
  - [Cross-reference: implementations](#cross-reference-implementations)

---

## Format overview

- LYT files are [ASCII](https://en.wikipedia.org/wiki/ASCII) text with a deterministic order: `beginlayout`, optional sections, then `donelayout`.  
- Every section declares a count and then lists entries on subsequent lines.  
- Implementations that parse the same token stream: [reone `lytreader.cpp` L27](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/lytreader.cpp#L27), [xoreos `lytfile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/lytfile.cpp), [KotOR.js `LYTObject.ts` L19](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/LYTObject.ts#L19), [Kotor.NET `LYT.cs` L11](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorLYT/LYT.cs#L11), and [KotOR-Unity](https://github.com/reubenduncan/KotOR-Unity).
- PyKotor reads via [`LYTAsciiReader.load` L60](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/io_lyt.py#L60) and writes via [`LYTAsciiWriter.write` L150](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/io_lyt.py#L150) against the [`LYT` data model L64](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L64).

### See also

- [MDL/MDX File Format](MDL-MDX-File-Format) - [room models](Level-Layout-Formats#room-definitions) referenced by LYT entries
- [BWM File Format](Level-Layout-Formats#bwm) - Walkmeshes ([WOK](Level-Layout-Formats#bwm) files) loaded alongside LYT rooms
- [VIS File Format](Level-Layout-Formats#vis) - Visibility graph for areas with LYT rooms
- [GFF-ARE](GFF-Module-and-Area#are) - [area files](GFF-File-Format#are-area) that load LYT layouts
- [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide) - Uses LYT format for generated modules

---

## Syntax

```plaintext
beginlayout
roomcount <N>
  <room_model> <x> <y> <z>
trackcount <N>
  <track_model> <x> <y> <z>
obstaclecount <N>
  <obstacle_model> <x> <y> <z>
doorhookcount <N>
  <room_name> <door_name> <x> <y> <z> <qx> <qy> <qz> <qw> [optional floats]
donelayout
```

### Room Definitions

| Token | Description |
| ----- | ----------- |
| `roomcount` | Declares how many rooms follow. |
| `<room_model>` | *ResRef* of the [MDL](MDL-MDX-File-Format), [MDX](MDL-MDX-File-Format), and [WOK](Level-Layout-Formats#bwm) triple (max 16 chars, no spaces). |
| `<x y z>` | World-space position for the room’s origin. |

Rooms are case-insensitive; PyKotor lowercases entries for caching and resource lookup ([`LYTAsciiReader` rooms parsing L60](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/io_lyt.py#L60)). **Room order in the LYT defines the 0-based room index** used as the **transition ID** in [BWM](Level-Layout-Formats#bwm) perimeter edges ([reone `lytreader.cpp` L37–L77](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/lytreader.cpp#L37-L77)). Changing room order or adding/removing rooms invalidates existing transition indices in walkmeshes; see [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions).

**For mod developers:**

- Loading a **layout** (LYT, optionally with [VIS](Level-Layout-Formats#vis) and room models) establishes the room context needed for placement and **roomlink/transition editing**. Loading only individual room models without the layout does not provide that context.
- For more on room crossing and reassigning roomlinks, see [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions).

### Track Definitions

Tracks ([`LYTTrack` L259](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L259)) are booster elements used exclusively in swoop racing mini-games, primarily in KotOR II. Each track entry defines a booster element that can be placed along a racing track to provide speed boosts or other gameplay effects.

**format:**

```plaintext
trackcount <N>
  <track_model> <x> <y> <z>
```

| Token | Description |
| ----- | ----------- |
| `trackcount` | Declares how many track elements follow |
| `<track_model>` | *ResRef* of the track booster model ([MDL](MDL-MDX-File-Format) file, max 16 chars) |
| `<x y z>` | World-space position for the track element |

**Usage:**

- Tracks are optional - most modules omit this section entirely
- Primarily used in KotOR II swoop racing modules (e.g., Telos surface racing) [[`lyt_data.py` L72 — "Used in swoop racing mini-games (KotOR II)"](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L72)]
- Each track element represents a booster that can be placed along the racing track ([`LYTTrack` L296](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L296), [xoreos `lytfile.cpp` L98](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/lytfile.cpp#L98), [KotOR.js `LYTObject.ts` L73](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/LYTObject.ts#L73))
- The engine uses these positions to spawn track boosters during racing mini-games

### Obstacle Definitions

Obstacles ([`LYTObstacle` L306](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L306)) are hazard elements used exclusively in swoop racing mini-games, primarily in KotOR II. Each obstacle entry defines a hazard element that can be placed along a racing track to create challenges or obstacles for the player.

**format:**

```plaintext
obstaclecount <N>
  <obstacle_model> <x> <y> <z>
```

| Token | Description |
| ----- | ----------- |
| `obstaclecount` | Declares how many obstacle elements follow |
| `<obstacle_model>` | *ResRef* of the obstacle model ([MDL](MDL-MDX-File-Format) file, max 16 chars) |
| `<x y z>` | World-space position for the obstacle element |

**Usage:**

- Obstacles are optional - most modules omit this section entirely
- Typically only present in KotOR II racing modules (e.g., Telos surface racing) [[`lyt_data.py` L72](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L72)]
- Each obstacle element represents a hazard that can be placed along the racing track ([`LYTObstacle` L354](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L354), [xoreos `lytfile.cpp` L109](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/lytfile.cpp#L109), [KotOR.js `LYTObject.ts` L79](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/LYTObject.ts#L79))
- The engine uses these positions to spawn obstacles during racing mini-games
- Mirrors the track format but represents hazards instead of boosters

### Door Hooks

Door hooks ([`LYTDoorHook` L353](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L353)) bind door models (DYN or placeable) to rooms. Each entry defines a position and orientation where a door can be placed, enabling area transitions and room connections ([`LYTDoorHook` L412](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L412), [xoreos `lytfile.cpp` L161](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/lytfile.cpp#L161), [KotOR.js `LYTObject.ts` L85](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/LYTObject.ts#L85)).

**format:**

```plaintext
doorhookcount <N>
  <room_name> <door_name> <x> <y> <z> <qx> <qy> <qz> <qw> [optional floats]
```

| Token | Description |
| ----- | ----------- |
| `doorhookcount` | Declares how many door hooks follow |
| `<room_name>` | Target room (must match a `roomcount` entry, case-insensitive) |
| `<door_name>` | Hook identifier (used in module files to reference this door, case-insensitive) |
| `<x y z>` | position of door origin in world space |
| `<qx qy qz qw>` | [Quaternion](https://en.wikipedia.org/wiki/Quaternion) orientation for door rotation |
| `[optional floats]` | Some builds (notably xoreos/KotOR-Unity) record five extra floats; PyKotor ignores them while preserving compatibility |

**Usage:**

- Door hooks define where doors are placed in rooms to create area transitions
- Each door hook specifies which room it belongs to and a unique door name
- The engine uses door hooks to position door [models](MDL-MDX-File-Format) and enable transitions between areas
- Door hooks are separate from [BWM](Level-Layout-Formats#bwm) hooks (see [BWM File Format](Level-Layout-Formats#wok-vs-pwk-vs-dwk-summary)) - [BWM](Level-Layout-Formats#bwm) hooks define interaction points, while LYT doorhooks define door placement

**Relationship to [BWM](Level-Layout-Formats#bwm):**

- Door hooks in LYT files define where doors are placed in the layout
- [BWM](Level-Layout-Formats#bwm) [walkmeshes](Level-Layout-Formats#bwm) may have [edge](Level-Layout-Formats#edges-wok-only) transitions that reference these door hooks
- The engine combines LYT doorhook positions with [BWM](Level-Layout-Formats#bwm) transition data to create functional doorways

---

## Coordinate system

- Units are world-space floats (same scale as [MDL](MDL-MDX-File-Format) model coordinates, by community convention).  
- PyKotor validates that room ResRefs and hook targets are lowercase and conform to resource naming restrictions ([`lyt_data.py` L150–L267](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py#L150-L267)).  
- The engine expects rooms to be pre-aligned so that adjoining doors share positions/rotations
- [VIS files](Level-Layout-Formats#vis) then control visibility between those rooms.

---

## Cross-reference: implementations

- **Parser:** [`Libraries/PyKotor/src/pykotor/resource/formats/lyt/io_lyt.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lyt/io_lyt.py)  
- **data [model](MDL-MDX-File-Format):** [`Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lyt/lyt_data.py)  
- **Reference Implementations:**  
  - **[reone](https://github.com/seedhartha/reone)**: [`lytreader.cpp` L27+](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/lytreader.cpp#L27)  
  - **[xoreos](https://github.com/xoreos/xoreos)**: [`lytfile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/lytfile.cpp)  
  - **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`LYTObject.ts` L19+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/LYTObject.ts#L19)  
  - **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`LYT.cs` L11+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorLYT/LYT.cs#L11)  

All of the projects listed above agree on the plain-text token sequence; KotOR-Unity and NorthernLights consume the same format without introducing additional metadata.

### See also

- [MDL/MDX File Format](MDL-MDX-File-Format) - Room models referenced by LYT entries
- [BWM File Format](Level-Layout-Formats#bwm) - Walkmeshes (WOK) loaded alongside LYT rooms
- [VIS File Format](Level-Layout-Formats#vis) - Visibility graph for areas with LYT rooms
- [GFF-ARE](GFF-Module-and-Area#are) - Area files that load LYT layouts
- [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide) - Uses LYT for generated modules


---

<a id="vis"></a>

# VIS — Visibility

VIS files define room-to-room visibility for the engine's occlusion culling ([`vis_data.py` `VIS` L56](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/vis/vis_data.py#L56), [reone `visreader.cpp` L29](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/visreader.cpp#L29), [xoreos `visfile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/visfile.cpp)). Each entry names a parent room followed by the rooms visible from it, so the renderer only draws geometry the player can actually see — cutting draw calls and overdraw significantly in indoor areas. The format is plain ASCII text, one parent per block, with child rooms indented below ([`VISAsciiReader.load` L45](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/vis/io_vis.py#L45), [KotOR.js `VISObject.ts` L71](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/VISObject.ts#L71)).

VIS pairs with [LYT](Level-Layout-Formats#lyt) (which defines room placement) and [BWM](Level-Layout-Formats#bwm) walkmeshes (which handle collision and pathfinding). Room names in the VIS file must exactly match the room model names declared in the LYT.

## Table of Contents

- VIS — Visibility
  - Table of Contents
  - [Format overview](#format-overview)
  - [File layout](#file-layout)
    - [Parent Lines](#parent-lines)
    - [Child Lines](#child-lines)
  - [Runtime Behavior](#runtime-behavior)
  - [Cross-reference: implementations](#cross-reference-implementations-1)

---



## Format overview

- VIS files are plain [ASCII](https://en.wikipedia.org/wiki/ASCII) text; each parent room line lists how many child rooms follow.  
- Child room lines are indented by two spaces. Empty lines are ignored and names are case-insensitive.  
- files usually ship as `moduleXXX.vis` pairs; the `moduleXXXs.vis` (or `.vis` appended inside [ERF](Container-Formats#erf)) uses the same syntax.  

**Modding note:** When debugging room layout or first testing new rooms, VIS can be omitted (or simplified) to reduce variables; VIS adds complexity on top of [LYT](Level-Layout-Formats#lyt) and walkmesh setup.

Parsers that share this format: PyKotor ([`VISAsciiReader.load` L45–L88](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/vis/io_vis.py#L45-L88), write [`VISAsciiWriter.write` L97](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/vis/io_vis.py#L97), data [`VIS` L56](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/vis/vis_data.py#L56)), [reone `visreader.cpp` L29–L61](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/visreader.cpp#L29-L61), [xoreos `visfile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/visfile.cpp), [KotOR.js `VISObject.ts` L71–L126](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/VISObject.ts#L71-L126), [KotOR-Unity `VISObject.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/VISObject.cs).

### See also

- [LYT File Format](Level-Layout-Formats#lyt) - [layout files](Level-Layout-Formats#lyt) defining room positions
- [MDL/MDX File Format](MDL-MDX-File-Format) - [room models](Level-Layout-Formats#room-definitions) controlled by VIS
- [BWM File Format](Level-Layout-Formats#bwm) - [walkmeshes](Level-Layout-Formats#bwm) for room collision/pathfinding
- [GFF-ARE](GFF-Module-and-Area#are) - [area files](GFF-File-Format#are-area) that load VIS visibility graphs
- [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide) - Generates VIS files for created areas  

---

## File layout

### Parent Lines

```vis
ROOM_NAME CHILD_COUNT
```

| Token | Description |
| ----- | ----------- |
| `ROOM_NAME` | Room label (typically the [MDL](MDL-MDX-File-Format) *ResRef* of the room). |
| `CHILD_COUNT` | Number of child lines that follow immediately. |

Example:

```vis
room012 3
  room013
  room014
  room015
```

### Child Lines

- Each child line begins with two spaces followed by the visible room name.  
- There is no explicit delimiter; the parser trims whitespace.  
- A parent can list itself to force always-rendered rooms (rare but valid) ([`VISAsciiReader.load` L45-L88](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/vis/io_vis.py#L45-L88), [reone `visreader.cpp` L29-L61](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/visreader.cpp#L29-L61)).

---

## Runtime Behavior

- When the player stands in room `A`, the engine renders any room listed under `A` and recursively any linked lights or effects.  
- VIS files only control visibility; collision and pathfinding still rely on [walkmeshes](Level-Layout-Formats#bwm) and module [GFF](GFF-File-Format) data.  
- Editing VIS entries is a common optimization: removing unnecessary pairs prevents the renderer from drawing walls behind closed doors, while adding entries can fix disappearing [geometry](MDL-MDX-File-Format#geometry-header) when doorways are wide open.

**NOTE**: VIS are NOT required by the game. Most modern hardware can run KotOR without them. The game does not appear to implement frustum culling independently of VIS (community-observed behavior; no confirmed engine binary source), so VIS definitions are recommended for rendering correctness.

**Performance Impact:**

VIS files are crucial for performance in large areas:

- **Without VIS**: Engine renders all rooms, even those behind walls/doors (thousands of unnecessary polygons)
- **With VIS**: Only visible rooms are submitted to the renderer (fewer draw calls)
- **Overly Restrictive VIS**: Causes pop-in where rooms suddenly appear when entering adjacent areas
- **Too Permissive VIS**: Wastes GPU resources rendering unseen [geometry](MDL-MDX-File-Format#geometry-header)

**Common Issues:**

- **Missing Room**: Room not in any VIS list --> never renders --> appears invisible
- **One-way Visibility**: Room A lists B, but B doesn't list A --> asymmetric rendering
- **Performance Problems**: All rooms list each other --> defeats purpose of VIS optimization
- **Doorway Artifacts**: Door rooms not mutually visible --> walls clip during door [animations](MDL-MDX-File-Format#animation-header)

Module designers balance between performance (fewer visible rooms) and visual quality (no pop-in/clipping). Testing VIS changes in-game is essential.  

PyKotor’s `VIS` class stores the data as a `dict[str, set[str]]`, exposing helpers like `set_visible()` and `set_all_visible()` for tooling (see [`vis_data.py:52-294`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/vis/vis_data.py#L52-L294)).

---

## Cross-reference: implementations

| Layer | PyKotor (`master`) | Other repos |
| ----- | ------------------- | ----------- |
| Parser | [`io_vis.py` `VISAsciiReader` L45–L88](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/vis/io_vis.py#L45-L88) | [reone `visreader.cpp` L29–L61](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/visreader.cpp#L29-L61) |
| | | [KotOR.js `VISObject.ts` L71–L126](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/VISObject.ts#L71-L126) |
| Writer | [`io_vis.py` `VISAsciiWriter` L97–L101](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/vis/io_vis.py#L97-L101) | — |
| Data model | [`vis_data.py` L52–L294](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/vis/vis_data.py#L52-L294) | — |

The ASCII grammar in [File layout](#file-layout) matches these parsers; always round-trip test new rooms in-game because whitespace and version header lines differ slightly between toolchains.

### See also

- [LYT File Format](Level-Layout-Formats#lyt) - Layout files defining room positions
- [MDL/MDX File Format](MDL-MDX-File-Format) - Room models controlled by VIS
- [BWM File Format](Level-Layout-Formats#bwm) - Walkmeshes for room collision and pathfinding
- [GFF-ARE](GFF-Module-and-Area#are) - Area files that load VIS visibility graphs
- [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide) - Generates VIS files for areas

---


---

<a id="bwm"></a>

# BWM File Format

Binary WalkMesh (BWM) format used by the Odyssey engine (KotOR 1 & 2) for walkmesh data. This page describes only the **on-disk layout and format-specific semantics** for BWM/WOK/PWK/DWK files.

## What is a BWM file?

A BWM file stores a triangular mesh used for collision, pathfinding, and spatial queries. Three resource types share this format:

| Type | Extension | Use | Coordinates | AABB / adjacency / edges |
|------|-----------|-----|-------------|---------------------------|
| **WOK** | .wok | Area/room walkmesh | World | Yes |
| **PWK** | .pwk | Placeable walkmesh | Local | No (collision only) |
| **DWK** | .dwk | Door walkmesh | Local | No (collision only) |

- **WOK**: Vertices in world space; includes AABB tree, adjacencies, edges, and perimeters for pathfinding and transitions.
- **PWK/DWK**: Vertices in local (object) space; no AABB tree, adjacencies, or perimeters.

## Glossary (format-only)

- **BWM** — Binary/BioWare WalkMesh; the file format and its header.
- **World Coordinates** — Header field at 0x08: `0` = local (PWK/DWK), `1` = world (WOK).
- **AABB Tree** — Axis-aligned bounding box tree; present only in WOK; used for spatial queries; root index stored in header.
- **Adjacency** — For each walkable face edge, the index of the neighboring face/edge or -1; stored as `face_index*3 + edge_index`.
- **Edge** — Boundary edge with optional transition ID; 8 bytes (encoded edge index + transition).
- **Perimeter** — Closed loop of edges; stored as 1-based end indices into the edge array.
- **Transition ID** — Integer in the edge record; semantics (e.g. room/door mapping) are defined by the engine and LYT, not by the BWM file itself.
- **Material index** — Per-face surface material ID; used as bit position in engine material masks; walkability comes from 2DA, not from BWM.

## Data types and conventions

- **Byte order**: Little-endian.
- **Magic**: `"BWM "` (4 bytes).
- **Version**: `"V1.0"` (4 bytes); no other version variants documented for Odyssey.
- **Header size**: 136 bytes (0x88).

## File structure overview

1. **Header** (136 bytes) — Magic, version, flags, and offsets/counts for all following tables.
2. **Vertices** — Array of float3 (x, y, z); count and file offset in header.
3. **Faces** — Array of uint32 triplets (vertex indices per triangle); count and offset in header.
4. **Materials** — Array of uint32 (one per face); offset in header.
5. **Normals** — Array of float3 (face normal per face); offset in header.
6. **Distances** — Array of float32 (planar distance per face); offset in header.
7. **AABB tree** (WOK only) — Array of AABB nodes; count, offset, and root index in header.
8. **Adjacencies** (WOK only) — Flat int32 array: `walkable_face_count * 3` entries; index = `face_index*3 + edge_index`.
9. **Edges** (WOK only) — Array of 8-byte records (edge index + transition ID).
10. **Perimeters** (WOK only) — Array of uint32: 1-based loop end indices into the edge array.

## Header layout

| Name | Type | Offset (hex) | Offset (dec) | Description |
|------|------|--------------|--------------|-------------|
| magic | char[4] | 0x00 | 0 | `"BWM "` |
| version | char[4] | 0x04 | 4 | `"V1.0"` |
| world_coords | int32 | 0x08 | 8 | 0 = local, 1 = world |
| relative_use_positions[0] | float3 | 0x0C | 12 | Use position 1 |
| relative_use_positions[1] | float3 | 0x18 | 24 | Use position 2 |
| absolute_use_positions[0] | float3 | 0x24 | 36 | Absolute use 1 |
| absolute_use_positions[1] | float3 | 0x30 | 48 | Absolute use 2 |
| position | float3 | 0x3C | 60 | Mesh position (x,y,z) |
| vertex_count | uint32 | 0x48 | 72 | Number of vertices |
| vertex_offset | uint32 | 0x4C | 76 | File offset to vertices |
| face_count | uint32 | 0x50 | 80 | Number of faces |
| face_offset | uint32 | 0x54 | 84 | File offset to face indices |
| materials_offset | uint32 | 0x58 | 88 | File offset to materials |
| normals_offset | uint32 | 0x5C | 92 | File offset to normals |
| distances_offset | uint32 | 0x60 | 96 | File offset to distances |
| aabb_count | uint32 | 0x64 | 100 | Number of AABB nodes |
| aabb_offset | uint32 | 0x68 | 104 | File offset to AABB array |
| aabb_root | uint32 | 0x6C | 108 | Root node index (0-based) |
| adjacency_count | uint32 | 0x70 | 112 | Walkable face count |
| adjacency_offset | uint32 | 0x74 | 116 | File offset to adjacencies |
| edge_count | uint32 | 0x78 | 120 | Number of edges |
| edge_offset | uint32 | 0x7C | 124 | File offset to edges |
| perimeter_count | uint32 | 0x80 | 128 | Number of perimeter entries |
| perimeter_offset | uint32 | 0x84 | 132 | File offset to perimeters |

## Vertices

- **Format**: Consecutive float3 (x, y, z), 12 bytes per vertex.
- **Count**: `vertex_count` in header; offset `vertex_offset`.
- **Coordinate space**: If `world_coords == 1` (WOK), vertices are in world space; if `world_coords == 0` (PWK/DWK), vertices are in local space.

## Faces

- **Format**: Consecutive uint32 triplets (v0, v1, v2) per triangle; 12 bytes per face.
- **Count**: `face_count`; offset `face_offset`.
- **Vertex indices**: 0-based into the vertex array.

## Materials, normals, distances

- **Materials**: One uint32 per face; offset `materials_offset`. Material ID is used as bit position in engine masks; walkability is defined by 2DA, not BWM.
- **Normals**: One float3 per face; offset `normals_offset`.
- **Distances**: One float32 per face; offset `distances_offset`.

## AABB tree (WOK only)

- **Node size**: 44 bytes (0x2C) per node.
- **Layout per node**: min bounds (float3), max bounds (float3), right child index (uint32), left child index (uint32), most significant plane (int32). Child indices are 0-based; no child = 0xFFFFFFFF.
- **Root**: Header field `aabb_root` is the 0-based index of the root node in the AABB array.
- **Leaf**: When both children are -1 (or equivalent), the node is a leaf (face index encoded in engine-specific way; see engine docs).

## Adjacencies (WOK only)

- **Format**: Flat int32 array; size = `adjacency_count * 3` (4 bytes per entry).
- **Indexing**: `adjacency[face_index * 3 + edge_index]` = encoded neighbor (adjacent_face_index * 3 + adjacent_edge_index), or -1 if no neighbor.
- **Bidirectional**: If face A edge 0 adjoins face B edge 2, both entries must be set consistently.

## Edges (WOK only)

- **Format**: 8 bytes per edge: encoded edge index (uint32) and transition ID (int32). Encoded edge = `face_index * 3 + local_edge_index`.
- **Count / offset**: `edge_count`, `edge_offset`.

## Perimeters (WOK only)

- **Format**: Array of uint32; each value is a 1-based end index for a closed loop of edges.
- **Interpretation**: `perimeters[0] = N` means loop 1 contains edges 0..N-1
- `perimeters[1] = M` means loop 2 contains edges N..M-1; etc.

## Load / write order

Data tables are stored in this order (offsets in header must match):

1. Vertices  
2. Faces  
3. Materials  
4. Normals  
5. Distances  
6. AABB nodes  
7. Adjacencies  
8. Edges  
9. Perimeters  

## Transitions and door placement

Door and room transitions are expressed using area layout data, including:

- [LYT-File-Format](Level-Layout-Formats#lyt)
- [GFF-ARE](GFF-Module-and-Area#are)
- Related module and area resources

In the BWM file, each **edge** record carries only a **transition ID** integer; interpreting that ID is engine and layout specific, not defined further by the BWM binary layout alone. See the next section for the on-disk field.

## Transition ID (format only)

The edge record contains a **transition ID** (int32). In the file it is only an integer; its meaning (e.g. which room or door) is defined by the engine and by LYT/area data, not by the BWM format. See [LYT-File-Format](Level-Layout-Formats#lyt) and area/module docs for semantics.

## WOK vs PWK vs DWK (summary)

| Feature | WOK | PWK | DWK |
|---------|-----|-----|-----|
| world_coords | 1 | 0 | 0 |
| Vertices | World | Local | Local |
| AABB tree | Yes | No | No |
| Adjacencies | Yes | No | No |
| Edges / perimeters | Yes | No | No |

### Implementation (PyKotor) — non-normative

Library read/write code for tooling alignment only; **normative** layout and engine semantics remain RE + pipelines on this page and in [reverse_engineering_findings — BWM / AABB](reverse_engineering_findings#bwm-walkmesh-aabb-engine-implementation-analysis).

| Artifact | Location |
| -------- | -------- |
| Package | [`Libraries/PyKotor/src/pykotor/resource/formats/bwm/`](https://github.com/OpenKotOR/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm) |
| Binary read | [`BWMBinaryReader.load` L97+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py#L97) in [`io_bwm.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py) |
| Binary write | [`BWMBinaryWriter.write` L220+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py#L220) in [`io_bwm.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py) |
| In-memory model | [`BWM` L145+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py#L145) in [`bwm_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py) |

**KotOR.js:** [OdysseyWalkMesh.ts](https://github.com/KobaltBlu/KotOR.js/blob/master/src/odyssey/OdysseyWalkMesh.ts) — binary read [`readBinary` L301–L395](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/odyssey/OdysseyWalkMesh.ts#L301-L395), header parse [`readHeader` L492–L514](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/odyssey/OdysseyWalkMesh.ts#L492-L514), export [`toExportBuffer` ~L834+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/odyssey/OdysseyWalkMesh.ts#L834). Layout differs from PyKotor (KotOR.js reserves 48 bytes in header; no hook vectors in file per PyKotor `io_bwm.py` L131 comment).

CLI helper: [`pykotor walkmesh-rebuild`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/CLI_QUICKSTART.md#L98-L104) for rebuilding walkmesh data from the command line.

## Edge cases and validation

- **Empty mesh**: face_count 0; vertex_count 0; no AABB/adjacency/edge/perimeter data for WOK.
- **PWK/DWK**: aabb_count, adjacency_count, edge_count, perimeter_count should be 0; corresponding offsets typically 0 or unused.
- **Walkable ordering**: Engine may expect walkable faces first in the face array; adjacency_count equals number of walkable faces. See engine and 2DA docs.

### See also

- [Reverse Engineering Findings — BWM / walkmesh / AABB](reverse_engineering_findings#bwm-walkmesh-aabb-engine-implementation-analysis) — Engine behavior, coordinate handling, AABB traversal.
- [2DA-surfacemat](2DA-File-Format#surfacemat2da) — Material IDs and walkability.
- [GFF-ARE](GFF-Module-and-Area#are) — Area files that reference WOK/PWK/DWK.
- [LYT-File-Format](Level-Layout-Formats#lyt) — Room layout; transition ID semantics.
- [MDL-MDX-File-Format](MDL-MDX-File-Format) — Room MDLs can contain separate AABB/walkmesh data for camera collision.


---

