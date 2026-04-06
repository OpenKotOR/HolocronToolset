# GFF Types: Module and Area

Every playable location is assembled from three core GFF files: ARE defines the area's static properties (rooms, ambient sound, lighting) [[`ARE`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/are.py#L21)], GIT holds all dynamic instance data (creature spawns, placeables, triggers placed in the area) [[`GIT`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/git.py#L57)], and IFO ties the module together with entry points, area references, and global module state.

## Contents

- [ARE — Area](#are)
- [GIT — Game Instance (Dynamic Area Data)](#git)
- [IFO — Module Info](#ifo)

---

<a id="are"></a>

# ARE (Area)

Part of the [GFF File Format Documentation](GFF-File-Format).

ARE files define static [area properties](GFF-File-Format#are-area) including lighting, weather, ambient audio, grass rendering, fog settings, script hooks, and minimap data. ARE files contain environmental and atmospheric data for game areas, while dynamic object placement is handled by [GIT](GFF-File-Format#git-game-instance-template) files. When the engine loads an area it reads the ARE for metadata and lighting, then loads the area [walkmesh (WOK)](Level-Layout-Formats#bwm). Associated resources often include:

- [GIT](GFF-Module-and-Area#git)
- [LYT](Level-Layout-Formats#lyt)
- [VIS](Level-Layout-Formats#vis)

Those resources use the usual [resource resolution order](Concepts#resource-resolution-order).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine ARE format specification, see [Bioware Aurora Area File Format](Bioware-Aurora-Module-and-Area#areafile).

**For mod developers:**

- To modify GFF/ARE files in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFF-Syntax#gfflist-syntax).
- For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers).

**Related formats:**

- [GIT](GFF-File-Format#git-game-instance-template)
- [BWM](Level-Layout-Formats#bwm)
- [LYT](Level-Layout-Formats#lyt)
- [VIS](Level-Layout-Formats#vis)
- [2DA](2DA-File-Format) (e.g. camerastyle, ambientmusic)
- [TLK](Audio-and-Localization-Formats#tlk)

Loading uses the same [resource resolution order](Concepts#resource-resolution-order).

PyKotor models areas through [`ARE`, `construct_are`, `read_are`, and `write_are`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/are.py#L21), identifies them as [`GFFContent.ARE`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L159), and decodes them through the shared [`GFFBinaryReader.load`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) pipeline; Holocron Toolset exposes the same fields in its [`are.py` area editor](https://github.com/OpenKotOR/HolocronToolset/src/toolset/gui/editors/are.py). Other implementations keep ARE in the generic GFF path too, including reone's [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp) and [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp), KotOR.js's [`GFFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), Kotor.NET's [`GFF.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18), and xoreos's Aurora pipeline, while workflow guidance for packing areas and their walkmeshes is best read alongside [Home — Community sources](Home#community-sources-and-archives), [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions), and the normative [BWM section](Level-Layout-Formats#bwm).

## Core Identity fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique area identifier |
| `Name` | [CExoLocString](GFF-File-Format#gff-data-types) | Area name (localized) |
| `Comments` | [CExoString](GFF-File-Format#gff-data-types) | Developer notes/documentation |
| `Creator_ID` | UInt32 | Toolset creator identifier (unused at runtime) |
| `ID` | UInt32 | Unique area ID (unused at runtime) |
| `Version` | UInt32 | Area version (unused at runtime) |
| `Flags` | UInt32 | Area flags (unused in KotOR) |

## Lighting & Sun

| Field | Type | Description |
| ----- | ---- | ----------- |
| `SunAmbientColor` | color | Ambient light color RGB |
| `SunDiffuseColor` | color | Sun diffuse light color RGB |
| `SunShadows` | [byte](GFF-File-Format#gff-data-types) | Enable shadow rendering |
| `ShadowOpacity` | [byte](GFF-File-Format#gff-data-types) | Shadow opacity (0-255) |
| `DynAmbientColor` | color | Dynamic ambient light RGB |

**Lighting System:**

- **SunAmbientColor**: Base ambient illumination (affects all surfaces)
- **SunDiffuseColor**: Directional sunlight color
- **SunShadows**: Enables real-time shadow casting
- **ShadowOpacity**: Controls shadow darkness
- **DynAmbientColor**: Secondary ambient for dynamic lighting

## Fog Settings

| Field | Type | Description |
| ----- | ---- | ----------- |
| `SunFogOn` | [byte](GFF-File-Format#gff-data-types) | Enable fog rendering |
| `SunFogNear` | float | Fog start distance |
| `SunFogFar` | float | Fog end distance |
| `SunFogColor` | color | Fog color RGB |

**Fog Rendering:**

- **SunFogOn=1**: Fog active
- **SunFogNear**: Distance where fog begins (world units)
- **SunFogFar**: Distance where fog is opaque
- **SunFogColor**: Fog tint color (atmosphere)

**Fog Calculation:**

- Linear interpolation from Near to Far
- Objects beyond Far fully obscured
- Creates depth perception and atmosphere

## Moon Lighting (Unused)

| Field | Type | Description |
| ----- | ---- | ----------- |
| `MoonAmbientColor` | color | Moon ambient light (unused) |
| `MoonDiffuseColor` | color | Moon diffuse light (unused) |
| `MoonFogOn` | [byte](GFF-File-Format#gff-data-types) | Moon fog toggle (unused) |
| `MoonFogNear` | float | Moon fog start (unused) |
| `MoonFogFar` | float | Moon fog end (unused) |
| `MoonFogColor` | color | Moon fog color (unused) |
| `MoonShadows` | [byte](GFF-File-Format#gff-data-types) | Moon shadows (unused) |
| `IsNight` | [byte](GFF-File-Format#gff-data-types) | Night time flag (unused) |

**Moon System:**

- Defined in file format but not used by KotOR engine
- Intended for day/night cycle (not implemented)
- Always use Sun settings for lighting

## Grass Rendering

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Grass_TexName` | *ResRef* | Grass [texture](Texture-Formats#tpc) name |
| `Grass_Density` | float | Grass blade density (0.0-1.0) |
| `Grass_QuadSize` | float | Size of grass patches |
| `Grass_Ambient` | color | Grass ambient color RGB |
| `Grass_Diffuse` | color | Grass diffuse color RGB |
| `Grass_Emissive` (KotOR2) | color | Grass emissive color RGB |
| `Grass_Prob_LL` | float | Spawn probability lower-left |
| `Grass_Prob_LR` | float | Spawn probability lower-right |
| `Grass_Prob_UL` | float | Spawn probability upper-left |
| `Grass_Prob_UR` | float | Spawn probability upper-right |

**Grass System:**

- **Grass_TexName**: [texture](Texture-Formats#tpc) for grass blades (TGA/[TPC](Texture-Formats#tpc))
- **Grass_Density**: Coverage density (1.0 = full coverage)
- **Grass_QuadSize**: Patch size in world units
- **Probability fields**: Control grass distribution across area

**Grass Rendering:**

1. Area divided into grid based on QuadSize
2. Each quad has spawn probability from corner interpolation
3. Density determines blades per quad
4. Grass billboards oriented to camera

## Weather System (KotOR2)

| Field | Type | Description |
| ----- | ---- | ----------- |
| `ChanceRain` (KotOR2) | [int32](GFF-File-Format#gff-data-types) | Rain probability (0-100) |
| `ChanceSnow` (KotOR2) | [int32](GFF-File-Format#gff-data-types) | Snow probability (0-100) |
| `ChanceLightning` (KotOR2) | [int32](GFF-File-Format#gff-data-types) | Lightning probability (0-100) |

**Weather Effects:**

- Random weather based on probability
- Particle effects for rain/snow
- Lightning provides flash and sound

## Dirty/Dust Settings (KotOR2)

| Field | Type | Description |
| ----- | ---- | ----------- |
| `DirtyARGBOne` (KotOR2) | UInt32 | First dust color ARGB |
| `DirtySizeOne` (KotOR2) | float | First dust particle size |
| `DirtyFormulaOne` (KotOR2) | [int32](GFF-File-Format#gff-data-types) | First dust formula type |
| `DirtyFuncOne` (KotOR2) | [int32](GFF-File-Format#gff-data-types) | First dust function |
| `DirtyARGBTwo` (KotOR2) | UInt32 | Second dust color ARGB |
| `DirtySizeTwo` (KotOR2) | float | Second dust particle size |
| `DirtyFormulaTwo` (KotOR2) | [int32](GFF-File-Format#gff-data-types) | Second dust formula type |
| `DirtyFuncTwo` (KotOR2) | [int32](GFF-File-Format#gff-data-types) | Second dust function |
| `DirtyARGBThree` (KotOR2) | UInt32 | Third dust color ARGB |
| `DirtySizeThree` (KotOR2) | float | Third dust particle size |
| `DirtyFormulaThre` (KotOR2) | [int32](GFF-File-Format#gff-data-types) | Third dust formula type |
| `DirtyFuncThree` (KotOR2) | [int32](GFF-File-Format#gff-data-types) | Third dust function |

**Dust Particle System:**

- Three independent dust layers
- Each layer has color, size, and behavior
- Creates atmospheric dust/smoke effects

## Environment & Camera

| Field | Type | Description |
| ----- | ---- | ----------- |
| `DefaultEnvMap` | *ResRef* | Default environment map [texture](Texture-Formats#tpc) |
| `CameraStyle` | [int32](GFF-File-Format#gff-data-types) | Camera behavior type |
| `AlphaTest` | [byte](GFF-File-Format#gff-data-types) | Alpha testing threshold |
| `WindPower` | [int32](GFF-File-Format#gff-data-types) | Wind strength for effects |
| `LightingScheme` | [int32](GFF-File-Format#gff-data-types) | Lighting scheme identifier (unused) |

**Environment Mapping:**

- `DefaultEnvMap`: Cubemap for reflective surfaces
- Applied to [models](MDL-MDX-File-Format) without specific envmaps

**Camera Behavior:**

- `CameraStyle`: Determines camera constraints
- Defines zoom, rotation, and collision behavior

## Area behavior flags

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Unescapable` | [byte](GFF-File-Format#gff-data-types) | Cannot use save/travel functions |
| `DisableTransit` | [byte](GFF-File-Format#gff-data-types) | Cannot travel to other modules |
| `StealthXPEnabled` | [byte](GFF-File-Format#gff-data-types) | Award stealth XP |
| `StealthXPLoss` | [int32](GFF-File-Format#gff-data-types) | Stealth detection XP penalty |
| `StealthXPMax` | [int32](GFF-File-Format#gff-data-types) | Maximum stealth XP per area |

**Stealth System:**

- **StealthXPEnabled**: Area rewards stealth gameplay
- **StealthXPMax**: Cap on XP from stealth
- **StealthXPLoss**: Penalty when detected

**Area Restrictions:**

- **Unescapable**: Prevents save/load menus (story sequences)
- **DisableTransit**: Locks player in current location

## Skill Check Modifiers

| Field | Type | Description |
| ----- | ---- | ----------- |
| `ModSpotCheck` | [int32](GFF-File-Format#gff-data-types) | Awareness skill modifier (unused) |
| `ModListenCheck` | [int32](GFF-File-Format#gff-data-types) | Listen skill modifier (unused) |

**Skill Modifiers:**

- Intended to modify detection checks area-wide
- Not implemented in KotOR engine

## Script Hooks

| Field | Type | Description |
| ----- | ---- | ----------- |
| `OnEnter` | *ResRef* | Fires when entering area |
| `OnExit` | *ResRef* | Fires when leaving area |
| `OnHeartbeat` | *ResRef* | Fires periodically |
| `OnUserDefined` | *ResRef* | Fires on user-defined events |

**Script Execution:**

- **OnEnter**: Area initialization, cinematics, spawns
- **OnExit**: Cleanup, state saving
- **OnHeartbeat**: Periodic updates (every 6 seconds)
- **OnUserDefined**: Custom event handling

## Minimap coordinate system

The ARE file contains a `Map` struct that defines how the minimap texture (`lbl_map<resname>`) aligns with the world space [walkmesh](Level-Layout-Formats#bwm). This coordinate system allows the game to display the player's position on the minimap and render map notes at correct locations.

### Map struct fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `MapPt1X` | float | First map point X coordinate (normalized 0.0-1.0) |
| `MapPt1Y` | float | First map point Y coordinate (normalized 0.0-1.0) |
| `MapPt2X` | float | Second map point X coordinate (normalized 0.0-1.0) |
| `MapPt2Y` | float | Second map point Y coordinate (normalized 0.0-1.0) |
| `WorldPt1X` | float | First world point X coordinate (world units) |
| `WorldPt1Y` | float | First world point Y coordinate (world units) |
| `WorldPt2X` | float | Second world point X coordinate (world units) |
| `WorldPt2Y` | float | Second world point Y coordinate (world units) |
| `NorthAxis` | [int32](GFF-File-Format#gff-data-types) | North direction orientation (0-3) |
| `MapZoom` | [int32](GFF-File-Format#gff-data-types) | Map zoom level |
| `MapResX` | [int32](GFF-File-Format#gff-data-types) | Map [texture](Texture-Formats#tpc) resolution X dimension |

**coordinate System:**

- **Map Points** (`MapPt1X/Y`, `MapPt2X/Y`): Normalized [texture](Texture-Formats#tpc) coordinates (0.0-1.0) that correspond to specific locations on the minimap [texture](Texture-Formats#tpc)
- **World Points** (`WorldPt1X/Y`, `WorldPt2X/Y`): World space coordinates (in game units) that correspond to the same locations in the 3D [walkmesh](Level-Layout-Formats#bwm)
- **NorthAxis**: Determines which axis is "north" and affects coordinate mapping (see below)

### coordinate [transformation](Level-Layout-Formats#adjacencies-wok-only)

The game engine uses a linear [transformation](Level-Layout-Formats#adjacencies-wok-only) to convert between world coordinates and map [texture](Texture-Formats#tpc) coordinates. This allows:

1. **Rendering the minimap [texture](Texture-Formats#tpc)** in world space (overlaying it on the [walkmesh](Level-Layout-Formats#bwm))
2. **Converting player position** to minimap coordinates for the minimap UI
3. **Placing map notes** at correct positions on the minimap

**Mathematical Formula (World --> Map [texture](Texture-Formats#tpc) coordinates):**

Reference: **[reone](https://github.com/modawan/reone)**: [`src/libs/game/gui/map.cpp`](https://github.com/modawan/reone/blob/master/src/libs/game/gui/map.cpp) - `getMapPosition()`

For **NorthAxis 0 or 1** (PositiveY or NegativeY):

```
scaleX = (MapPt1X - MapPt2X) / (WorldPt1X - WorldPt2X)
scaleY = (MapPt1Y - MapPt2Y) / (WorldPt1Y - WorldPt2Y)
mapPos.x = (world.x - WorldPt1X) * scaleX + MapPt1X
mapPos.y = (world.y - WorldPt1Y) * scaleY + MapPt1Y
```

For **NorthAxis 2 or 3** (PositiveX or NegativeX - swapped mapping):

```
scaleX = (MapPt1Y - MapPt2Y) / (WorldPt1X - WorldPt2X)
scaleY = (MapPt1X - MapPt2X) / (WorldPt1Y - WorldPt2Y)
mapPos.x = (world.y - WorldPt1Y) * scaleY + MapPt1X
mapPos.y = (world.x - WorldPt1X) * scaleX + MapPt1Y
```

**Inverse Transformation (Map [texture](Texture-Formats#tpc) --> World coordinates):**

For rendering the minimap [texture](Texture-Formats#tpc) in world space:

```
worldScaleX = (WorldPt1X - WorldPt2X) / (MapPt1X - MapPt2X)
worldScaleY = (WorldPt1Y - WorldPt2Y) / (MapPt1Y - MapPt2Y)
world.x = WorldPt1X + (mapPos.x - MapPt1X) * worldScaleX
world.y = WorldPt1Y + (mapPos.y - MapPt1Y) * worldScaleY
```

For [texture](Texture-Formats#tpc) origin (0,0) in world space:

```
originX = WorldPt1X - MapPt1X * worldScaleX
originY = WorldPt1Y - MapPt1Y * worldScaleY
```

### NorthAxis values

| value | Enum | Description | coordinate Mapping |
| ----- | ---- | ----------- | ------------------ |
| 0 | PositiveY | +Y is north | Direct X/Y mapping |
| 1 | NegativeY | -Y is north | Direct X/Y mapping |
| 2 | PositiveX | +X is north | Swapped: world.x --> map.y, world.y --> map.x |
| 3 | NegativeX | -X is north | Swapped: world.x --> map.y, world.y --> map.x |

**NorthAxis Usage:**

- Determines which direction is "north" for the minimap
- Affects how world coordinates map to [texture](Texture-Formats#tpc) coordinates
- Used for rotating the player arrow on the minimap
- Cases 0,1 use direct mapping; cases 2,3 swap X/Y axes

### Map [texture](Texture-Formats#tpc)

The minimap [texture](Texture-Formats#tpc) is loaded from [texture](Texture-Formats#tpc) resource:

- **Resource Name**: `lbl_map<resname>` (e.g., `lbl_maptat001` for area `tat001`)
- **format**: [TPC](Texture-Formats#tpc) ([texture](Texture-Formats#tpc) Pack Container)
- **Typical size**: 435x256 pixels (may vary)
- **Usage**: Displayed in minimap UI and overlaid on [walkmesh](Level-Layout-Formats#bwm) in editor

**Relationship to [walkmesh](Level-Layout-Formats#bwm):**

- The minimap [texture](Texture-Formats#tpc) represents a top-down view of the area's [walkmesh](Level-Layout-Formats#bwm)
- Map points correspond to specific [vertices](MDL-MDX-File-Format#vertex-structure) and [faces](MDL-MDX-File-Format#face-structure) in the walkmesh ([BWM file](Level-Layout-Formats#bwm))
- The blue walkable area shown in editors is rendered from the [walkmesh](Level-Layout-Formats#bwm) [faces](MDL-MDX-File-Format#face-structure)
- For proper gameplay these must align:

  - Minimap [texture](Texture-Formats#tpc)
  - [walkmesh](Level-Layout-Formats#bwm)
- Misalignment causes the walkable area to appear rotated/flipped relative to the minimap image

### Implementation Notes

**coordinate Precision:**

- Map points are normalized (0.0-1.0) and require high precision (6+ decimal places)
- Rounding errors can cause misalignment between [walkmesh](Level-Layout-Formats#bwm) and minimap [texture](Texture-Formats#tpc)
- Always preserve full precision when editing map coordinates

**Common Issues:**

1. **Misaligned Minimap**: Caused by incorrect coordinate [transformation](Level-Layout-Formats#adjacencies-wok-only) or NorthAxis handling
2. **Inverted Mapping**: Negative scales indicate inverted mapping ([texture](Texture-Formats#tpc) needs mirroring)
3. **Precision Loss**: Using insufficient decimal precision in UI spinboxes causes drift

**Editor Rendering:**

When rendering the minimap [texture](Texture-Formats#tpc) over the [walkmesh](Level-Layout-Formats#bwm) in editors:

- Calculate linear scale: `worldScale = worldDelta / mapDelta`
- Calculate origin: `origin = worldPoint1 - mapPoint1 * worldScale`
- Handle NorthAxis swapping for cases 2,3
- Mirror [texture](Texture-Formats#tpc) if scale is negative (inverted mapping)

**Reference Implementations:**

- **[reone](https://github.com/modawan/reone)**: [`src/libs/game/gui/map.cpp`](https://github.com/modawan/reone/blob/master/src/libs/game/gui/map.cpp) - `getMapPosition()` function
- **[reone](https://github.com/modawan/reone)**: [`src/libs/resource/parser/gff/are.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/parser/gff/are.cpp) - are parsing
- `Libraries/PyKotor/src/pykotor/resource/generics/are.py` - PyKotor are implementation
- `Tools/HolocronToolset/src/toolset/gui/widgets/renderer/[walkmesh](Level-Layout-Formats#bwm).py` - Minimap rendering

## Rooms & Audio Zones

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Rooms` | [List](GFF-File-Format#gff-data-types) | Room definitions for audio zones and minimap regions |

**Rooms Struct fields:**

- `RoomName` ([CExoString](GFF-File-Format#gff-data-types)): Room identifier (referenced by [VIS files](Level-Layout-Formats#vis))
- `EnvAudio` ([int32](GFF-File-Format#gff-data-types)): Environment audio index for room acoustics
- `AmbientScale` (float): Ambient audio volume scaling factor
- `DisableWeather` (KotOR2, [byte](GFF-File-Format#gff-data-types)): Disable weather effects in this room
- `ForceRating` (KotOR2, [int32](GFF-File-Format#gff-data-types)): Force rating modifier for this room

**Room System:**

- Defines minimap regions and audio zones
- Each room has audio properties (EnvAudio, AmbientScale)
- Audio transitions smoothly between rooms
- Minimap reveals room-by-room as player explores
- Rooms referenced by [VIS](Level-Layout-Formats#vis) (visibility) files for audio occlusion
- KotOR2: Rooms can disable weather and modify force rating

## Implementation Notes

### Area Loading Sequence

1. **Parse are**: Load static properties from [GFF](GFF-File-Format)
2. **Apply Lighting**: Set sun/ambient colors
3. **Setup Fog**: Configure fog parameters
4. **Load Grass**: Initialize grass rendering if configured
5. **Configure Weather**: Activate weather systems (KotOR2)
6. **Register Scripts**: Setup area event handlers
7. **Load [GIT](GFF-File-Format#git-game-instance-template)**: Spawn dynamic objects (separate file)
8. **Load Minimap**: Parse map coordinates and load minimap [texture](Texture-Formats#tpc)

### Minimap coordinate System Best Practices

**Precision Requirements:**

- Map coordinates (`MapPt1X/Y`, `MapPt2X/Y`) are normalized (0.0-1.0) and require **at least 6 decimal places** of precision
- Using insufficient precision (e.g., 2 decimals) causes coordinate drift during roundtrip operations
- Example: `0.6669999957084656` rounded to 2 decimals becomes `0.67`, causing misalignment

**Common Pitfalls:**

1. **Incorrect rotation**: Do NOT rotate map points around (0.5, 0.5) - use direct linear [transformation](Level-Layout-Formats#adjacencies-wok-only)
2. **Precision Loss**: Always use high-precision spinboxes (6+ decimals) for map coordinate editing
3. **NorthAxis Handling**: Remember that cases 2,3 swap X/Y coordinates in the [transformation](Level-Layout-Formats#adjacencies-wok-only)
4. **Negative Scales**: Negative scale values indicate inverted mapping - mirror the [texture](Texture-Formats#tpc) accordingly

**Validation:**

- Always validate map coordinates preserve exactly through save/load roundtrips
- Test minimap alignment visually in editor after coordinate changes
- Verify [walkmesh](Level-Layout-Formats#bwm) and minimap [texture](Texture-Formats#tpc) align correctly for all NorthAxis values

**Lighting Performance:**

- Ambient/Diffuse colors affect all area [geometry](MDL-MDX-File-Format#geometry-header)
- Shadow rendering is expensive (SunShadows=0 for performance)
- Dynamic lighting for special effects only

**Grass Optimization:**

- High density grass impacts framerate significantly
- Probability fields allow targeted grass placement
- Grass LOD based on camera distance

**Audio Zones:**

- Rooms define audio transitions
- EnvAudio from are and Rooms determines soundscape
- Smooth fade between zones

**Common Area Configurations:**

**Outdoor Areas:**

- Bright sunlight (high diffuse)
- Fog for horizon
- Grass rendering
- Wind effects

**Indoor Areas:**

- Low ambient lighting
- No fog (usually)
- No grass
- Controlled camera

**Dark Areas:**

- Minimal ambient
- Strong diffuse for dramatic shadows
- Fog for atmosphere

**Special Areas:**

- Unescapable for story sequences
- Custom camera styles for unique views
- Specific environment maps for mood

### Minimap Rendering Implementation Details

**World Space [texture](Texture-Formats#tpc) Rendering:**

When rendering the minimap [texture](Texture-Formats#tpc) over the [walkmesh](Level-Layout-Formats#bwm) in editors, the following steps are required:

1. **Calculate World scale Factors:**

   ```
   worldScaleX = (WorldPt1X - WorldPt2X) / (MapPt1X - MapPt2X)
   worldScaleY = (WorldPt1Y - WorldPt2Y) / (MapPt1Y - MapPt2Y)
   ```

   These represent world units per [texture](Texture-Formats#tpc) unit (inverse of reone's scale factors).

2. **Calculate [texture](Texture-Formats#tpc) Origin in World Space:**

   ```
   originX = WorldPt1X - MapPt1X * worldScaleX
   originY = WorldPt1Y - MapPt1Y * worldScaleY
   ```

   This finds where [texture](Texture-Formats#tpc) coordinate (0,0) maps to in world space.

3. **Calculate [texture](Texture-Formats#tpc) End in World Space:**

   ```
   endX = WorldPt1X + (1.0 - MapPt1X) * worldScaleX
   endY = WorldPt1Y + (1.0 - MapPt1Y) * worldScaleY
   ```

   This finds where [texture](Texture-Formats#tpc) coordinate (1,1) maps to in world space.

4. **Handle NorthAxis coordinate Swapping:**
   - For NorthAxis 2 or 3: Swap `originX/originY` and `endX/endY` ([texture](Texture-Formats#tpc) X maps to world Y, [texture](Texture-Formats#tpc) Y maps to world X)

5. **Handle Inverted Mappings:**
   - If `worldScaleX < 0` or `worldScaleY < 0`: Mirror the [texture](Texture-Formats#tpc) horizontally/vertically respectively
   - Negative scales indicate the mapping is inverted ([texture](Texture-Formats#tpc) is flipped relative to world space)

6. **Render [texture](Texture-Formats#tpc):**
   - Draw [texture](Texture-Formats#tpc) in world space rectangle from `(min(originX, endX), min(originY, endY))` to `(max(originX, endX), max(originY, endY))`
   - Apply mirroring if scales are negative

**Mathematical Derivation:**

The inverse [transformation](Level-Layout-Formats#adjacencies-wok-only) is derived from reone's forward [transformation](Level-Layout-Formats#adjacencies-wok-only):

Forward (World --> Map): `mapPos.x = (world.x - WorldPt1X) * scaleX + MapPt1X`

Solving for world.x:

```
mapPos.x - MapPt1X = (world.x - WorldPt1X) * scaleX
(mapPos.x - MapPt1X) / scaleX = world.x - WorldPt1X
world.x = WorldPt1X + (mapPos.x - MapPt1X) / scaleX
```

Substituting `scaleX = (MapPt1X - MapPt2X) / (WorldPt1X - WorldPt2X)`:

```
world.x = WorldPt1X + (mapPos.x - MapPt1X) * (WorldPt1X - WorldPt2X) / (MapPt1X - MapPt2X)
```

For [texture](Texture-Formats#tpc) origin (mapPos = 0):

```
world.x = WorldPt1X - MapPt1X * (WorldPt1X - WorldPt2X) / (MapPt1X - MapPt2X)
world.x = WorldPt1X - MapPt1X * worldScaleX
```

**Common Rendering Bugs:**

1. **rotation Around Center Bug:**
   - **Symptom**: Walkable area appears rotated/flipped ~180° relative to minimap [texture](Texture-Formats#tpc)
   - **Cause**: Incorrectly rotating map points around (0.5, 0.5) before calculating [texture](Texture-Formats#tpc) position
   - **Fix**: Use direct linear [transformation](Level-Layout-Formats#adjacencies-wok-only) without any rotation of map points
   - **Pattern**: `map_point = rotate(map_point - 0.5, angle) + 0.5` ❌ (WRONG)

2. **Precision Loss Bug:**
   - **Symptom**: coordinates drift during save/load (e.g., 0.667 --> 0.67)
   - **Cause**: UI spinboxes with insufficient decimal precision (default 2 decimals)
   - **Fix**: Set spinbox decimals to 6+ for normalized coordinates
   - **Impact**: Causes cumulative misalignment over multiple roundtrips

3. **NorthAxis Swapping Bug:**
   - **Symptom**: Minimap appears correct for NorthAxis 0,1 but wrong for 2,3
   - **Cause**: Not handling coordinate axis swapping for NorthAxis 2,3
   - **Fix**: Swap X/Y coordinates when NorthAxis is 2 or 3

4. **Inverted Mapping Bug:**
   - **Symptom**: Minimap [texture](Texture-Formats#tpc) appears flipped horizontally or vertically
   - **Cause**: Not detecting and handling negative scale values
   - **Fix**: Check scale signs and mirror [texture](Texture-Formats#tpc) accordingly

**[walkmesh](Level-Layout-Formats#bwm) Alignment:**

The blue walkable area rendered in editors comes from the walkmesh ([BWM file](Level-Layout-Formats#bwm)) [faces](MDL-MDX-File-Format#face-structure). The minimap [texture](Texture-Formats#tpc) must align with this [walkmesh](Level-Layout-Formats#bwm):

- **[walkmesh](Level-Layout-Formats#bwm) coordinates**: 3D world space coordinates (X, Y, Z)
- **Minimap [texture](Texture-Formats#tpc)**: 2D [texture](Texture-Formats#tpc) coordinates (0.0-1.0) mapped to world X/Y plane
- **Alignment**: Map points correspond to specific [walkmesh](Level-Layout-Formats#bwm) [vertices](MDL-MDX-File-Format#vertex-structure) and [faces](MDL-MDX-File-Format#face-structure)
- **Verification**: The walkable area outline should match the minimap [texture](Texture-Formats#tpc) boundaries

**Testing & Validation:**

1. **Roundtrip Validation:**
   - Load are file --> Save without changes --> Load saved file
   - Verify all map coordinates (`MapPt1X/Y`, `MapPt2X/Y`, `WorldPt1X/Y`, `WorldPt2X/Y`) preserve exactly (tolerance: 0.0001)
   - Verify NorthAxis, MapZoom, MapResX preserve exactly

2. **Visual Alignment Check:**
   - Open are in editor with [walkmesh](Level-Layout-Formats#bwm) loaded
   - Verify blue walkable area aligns with minimap [texture](Texture-Formats#tpc)
   - Check alignment for all NorthAxis values (0, 1, 2, 3)
   - Verify [texture](Texture-Formats#tpc) isn't flipped or rotated incorrectly

3. **coordinate [transformation](Level-Layout-Formats#adjacencies-wok-only) Test:**
   - Pick known world coordinates from [walkmesh](Level-Layout-Formats#bwm)
   - Convert to map coordinates using forward [transformation](Level-Layout-Formats#adjacencies-wok-only)
   - Verify map coordinates are within valid range (0.0-1.0)
   - Convert back to world coordinates using inverse [transformation](Level-Layout-Formats#adjacencies-wok-only)
   - Verify roundtrip accuracy (tolerance: 0.01 world units)

**Reference Code Locations:**

- **Reone Forward [transformation](Level-Layout-Formats#adjacencies-wok-only)**: **[reone](https://github.com/modawan/reone)**: [`src/libs/game/gui/map.cpp:174-199`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/game/gui/map.cpp#L174-L199) - `getMapPosition()`
- **Reone are Parsing**: **[reone](https://github.com/modawan/reone)**: [`src/libs/resource/parser/gff/are.cpp:284-297`](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/parser/gff/are.cpp#L284-L297) - Map struct parsing
- **PyKotor are Class**: `Libraries/PyKotor/src/pykotor/resource/generics/are.py:250-260` - Map coordinate storage
- **PyKotor Minimap Rendering**: `Tools/HolocronToolset/src/toolset/gui/widgets/renderer/[walkmesh](Level-Layout-Formats#bwm).py:555-603` - [texture](Texture-Formats#tpc) rendering implementation

## See also

- [GFF File Format](GFF-File-Format) - Generic format underlying ARE
- [GFF Creature and Dialogue](GFF-Creature-and-Dialogue) - UTC and DLG types
- [GFF Items and Economy](GFF-Items-and-Economy) - UTI, UTM, JRL, FAC types
- [GFF Spatial Objects](GFF-Spatial-Objects) - UTD, UTP, UTT, UTE, UTS, UTW types
- [BWM (Walkmesh)](Level-Layout-Formats#bwm) - Area walkable surfaces and minimap alignment
- [LYT](Level-Layout-Formats#lyt) — layout
- [VIS](Level-Layout-Formats#vis) — visibility
- [Bioware Aurora Area File Format](Bioware-Aurora-Module-and-Area#areafile) - Official ARE specification


---

<a id="git"></a>

# GIT ([game instance template](GFF-File-Format#git-game-instance-template))

Part of the [GFF File Format Documentation](GFF-File-Format).

[GIT files](GFF-File-Format#git-game-instance-template) store dynamic instance data for areas, defining where creatures, doors, placeables, triggers, waypoints, stores, encounters, sounds, and cameras are positioned in the game world. While [ARE](GFF-Module-and-Area#are) files define static environmental properties, [GIT files](GFF-File-Format#git-game-instance-template) hold **instance lists** and **root-level audio/music ints** used when the area loads. GIT files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

PyKotor carries area instance state through [`GIT`, its `GITCreature` / `GITDoor` / related subclasses, plus `construct_git`, `read_git`, and `write_git`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/git.py#L53), labels the resource as [`GFFContent.GIT`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L162), and parses it through [`GFFBinaryReader.load`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82); Holocron Toolset mirrors that data in its [`git.py` instance editor](https://github.com/OpenKotOR/HolocronToolset/src/toolset/gui/editors/git/git.py) and related module-resource workflows. The same generic-GFF treatment appears in reone's [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp) and [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp), KotOR.js's [`GFFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), Kotor.NET's [`GFF.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18), and xoreos's Aurora loader stack.

## Root properties (ambient audio and music)

These fields are stored on the **GIT root** (see PyKotor `construct_git` / `dismantle_git` around the `Properties` struct in [`git.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/git.py)). They overlap conceptually with music/ambient columns on [ARE](GFF-Module-and-Area#are); treat [ARE](GFF-Module-and-Area#are) as the place for **static area metadata** (lighting, fog, minimap, hooks) and this section as **GIT-carried ints** the engine reads with the instance template.

| Field | Type | Description |
| ----- | ---- | ----------- |
| `AmbientSndDay` | Int | Day ambient sound ID |
| `AmbientSndDayVol` | Int | Day ambient volume (0-127) |
| `AmbientSndNight` | Int | Night ambient sound ID |
| `AmbientSndNightVol` | Int | Night ambient volume |
| `EnvAudio` | Int | Environment audio type |
| `MusicBattle` | Int | Battle music track ID |
| `MusicDay` | Int | Standard/exploration music ID |
| `MusicNight` | Int | Night music track ID |
| `MusicDelay` | Int | Delay before music starts (seconds) |

**Audio Configuration:**

- **Ambient Sounds**: Looping background ambience
- **Music Tracks**: From `ambientmusic.2da` and `musicbattle.2da`
- **EnvAudio**: Reverb/echo type for area
- **MusicDelay**: Prevents instant music start

**Music System:**

- MusicDay plays during exploration
- MusicBattle triggers during combat
- MusicNight unused in KotOR (no day/night cycle)
- Smooth transitions between tracks

## Instance Lists

[GIT](GFF-File-Format#git-game-instance-template) files contain multiple lists defining object instances:

| List field | Contains | Description |
| ---------- | -------- | ----------- |
| `Creature List` | GITCreature | Spawned NPCs and enemies |
| `Door List` | GITDoor | Placed doors |
| `Placeable List` | GITPlaceable | Containers, furniture, objects |
| `Encounter List` | GITEncounter | Encounter spawn zones |
| `TriggerList` | GITTrigger | Trigger volumes |
| `WaypointList` | GITWaypoint | Waypoint markers |
| `StoreList` | GITStore | Merchant vendors |
| `SoundList` | GITSound | Positional audio emitters |
| `CameraList` | GITCamera | Camera definitions |

**Instance structure:**

Each instance type has common fields plus type-specific data:

**Common Instance fields:**

- Position (X, Y, Z coordinates)
- Orientation ([quaternion](MDL-MDX-File-Format#node-header) or Euler angles)
- Template ResRef (examples):

  - [UTC](GFF-File-Format#utc-creature)
  - [UTD](GFF-File-Format#utd-door)
  - [UTP](GFF-File-Format#utp-placeable)
  - Other UT* templates as needed
- Tag override (optional)

## GITCreature Instances

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | [UTC](GFF-File-Format#utc-creature) template to spawn |
| `XPosition` | Float | World X coordinate |
| `YPosition` | Float | World Y coordinate |
| `ZPosition` | Float | World Z coordinate |
| `XOrientation` | Float | orientation X component |
| `YOrientation` | Float | orientation Y component |

**Creature Spawning:**

- Engine loads [UTC](GFF-File-Format#utc-creature) template
- Applies position/orientation from [GIT](GFF-File-Format#git-game-instance-template)
- Creature initialized with template stats
- Scripts fire after spawn

## GITDoor Instances

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | [UTD](GFF-File-Format#utd-door) template |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Instance tag override |
| `LinkedToModule` | *ResRef* | Destination module |
| `LinkedTo` | [CExoString](GFF-File-Format#gff-data-types) | Destination waypoint tag |
| `LinkedToFlags` | Byte | Transition flags |
| `TransitionDestin` | [CExoLocString](GFF-File-Format#gff-data-types) | Destination label (UI) |
| `X`, `Y`, `Z` | Float | position coordinates |
| `Bearing` | Float | Door orientation |
| `TweakColor` | DWord | Door color tint |
| `Hitpoints` | Short | Current HP override |

**Door Linking:**

- **LinkedToModule**: Target module *ResRef*
- **LinkedTo**: Waypoint tag in target module
- **TransitionDestin**: Loading screen text
- Doors can teleport between modules

**Door Instances:**

- Inherit properties from [UTD](GFF-File-Format#utd-door) template
- [GIT](GFF-File-Format#git-game-instance-template) can override HP, tag, linked destination
- position/orientation instance-specific

## GITPlaceable Instances

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | [UTP](GFF-File-Format#utp-placeable) template |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Instance tag override |
| `X`, `Y`, `Z` | Float | position coordinates |
| `Bearing` | Float | rotation angle |
| `TweakColor` | DWord | color tint |
| `Hitpoints` | Short | Current HP override |
| `Useable` | Byte | Can be used override |

**Placeable Spawning:**

- Template defines behavior, appearance
- [GIT](GFF-File-Format#git-game-instance-template) defines placement and orientation
- Can override usability and HP at instance level

## GITTrigger Instances

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | [UTT](GFF-File-Format#utt-trigger) template |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Instance tag |
| `TransitionDestin` | [CExoLocString](GFF-File-Format#gff-data-types) | Transition label |
| `LinkedToModule` | *ResRef* | Destination module |
| `LinkedTo` | [CExoString](GFF-File-Format#gff-data-types) | Destination waypoint |
| `LinkedToFlags` | Byte | Transition flags |
| `X`, `Y`, `Z` | Float | Trigger position |
| `XPosition`, `YPosition`, `ZPosition` | Float | Position (alternate) |
| `XOrientation`, `YOrientation`, `ZOrientation` | Float | orientation |
| `Geometry` | List | Trigger volume [vertices](MDL-MDX-File-Format#vertex-structure) |

**[geometry](MDL-MDX-File-Format#geometry-header) Struct:**

- List of Vector3 points
- Defines trigger boundary polygon
- Planar geometry (Z-axis extrusion)

**Trigger types:**

- **Area Transition**: LinkedToModule set
- **Script Trigger**: Fires scripts from [UTT](GFF-File-Format#utt-trigger)
- **Generic Trigger**: Custom behavior

## GITWaypoint Instances

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | [UTW](GFF-File-Format#utw-waypoint) template |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Waypoint identifier |
| `Appearance` | DWord | Waypoint appearance type |
| `LinkedTo` | [CExoString](GFF-File-Format#gff-data-types) | Linked waypoint tag |
| `X`, `Y`, `Z` | Float | position coordinates |
| `XOrientation`, `YOrientation` | Float | orientation |
| `HasMapNote` | Byte | Has map note |
| `MapNote` | [CExoLocString](GFF-File-Format#gff-data-types) | Map note text |
| `MapNoteEnabled` | Byte | Map note visible |

**Waypoint Usage:**

- **Spawn Points**: Character entry locations
- **Pathfinding**: AI navigation targets
- **Script Targets**: "Go to waypoint X"
- **Map Notes**: Player-visible markers

## GITEncounter Instances

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | [UTE](GFF-File-Format#ute-encounter) template |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Encounter identifier |
| `X`, `Y`, `Z` | Float | Spawn position |
| `Geometry` | List | Spawn zone boundary |

**Encounter System:**

- [geometry](MDL-MDX-File-Format#geometry-header) defines trigger zone
- Engine spawns creatures from [UTE](GFF-File-Format#ute-encounter) when entered
- Respawn behavior from [UTE](GFF-File-Format#ute-encounter) template

## GITStore Instances

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | [UTM](GFF-File-Format#utm-merchant) template |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Store identifier |
| `X`, `Y`, `Z` | Float | Position (for UI, not physical) |
| `XOrientation`, `YOrientation` | Float | orientation |

**Store System:**

- Stores don't have physical presence
- position used for toolset only
- Accessed via conversations or scripts

## GITSound Instances

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | [UTS](GFF-File-Format#uts-sound) template |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Sound identifier |
| `X`, `Y`, `Z` | Float | Emitter position |
| `MaxDistance` | Float | Audio falloff distance |
| `MinDistance` | Float | Full volume radius |
| `RandomRangeX`, `RandomRangeY` | Float | position randomization |
| `Volume` | Byte | Volume level (0-127) |

**Positional Audio:**

- 3D sound emitter at position
- Volume falloff over distance
- Random offset for variation

## GITCamera Instances

| Field | Type | Description |
| ----- | ---- | ----------- |
| `CameraID` | Int | Camera identifier |
| `FOV` | Float | field of view (degrees) |
| `Height` | Float | Camera height |
| `MicRange` | Float | Audio capture range |
| `Orientation` | Vector4 | Camera rotation ([quaternion](MDL-MDX-File-Format#node-header)) |
| `Pitch` | Float | Camera pitch angle |
| `Position` | Vector3 | Camera position |

**Camera System:**

- Defines fixed camera angles
- Used for cutscenes and dialogue
- FOV controls zoom level

## Implementation Notes

**[GIT](GFF-File-Format#git-game-instance-template) Loading Process:**

1. **Parse [GIT](GFF-File-Format#git-game-instance-template)**: Read [GFF](GFF-File-Format) structure
2. **Load Templates**: Read template files such as:

   - [UTC](GFF-File-Format#utc-creature)
   - [UTD](GFF-File-Format#utd-door)
   - [UTP](GFF-File-Format#utp-placeable)
   - Other UT* templates as needed
3. **Instantiate Objects**: Create runtime objects from templates
4. **Apply Overrides**: [GIT](GFF-File-Format#git-game-instance-template) position, HP, tag overrides applied
5. **Link Objects**: Resolve LinkedTo references
6. **Execute Spawn Scripts**: Fire OnSpawn events
7. **Activate Triggers**: Register trigger [geometry](MDL-MDX-File-Format#geometry-header)

**Instance vs. Template:**

- **Template** (blueprint family such as [UTC](GFF-File-Format#utc-creature), [UTD](GFF-File-Format#utd-door), or [UTP](GFF-File-Format#utp-placeable)): Defines what the object is
- **Instance ([GIT](GFF-File-Format#git-game-instance-template) entry)**: Defines where the object is
- [GIT](GFF-File-Format#git-game-instance-template) can override specific template properties
- Multiple instances can share one template

**Performance Considerations:**

- Large instance counts impact load time
- Complex trigger [geometry](MDL-MDX-File-Format#geometry-header) affects collision checks
- Many sounds can overwhelm audio system
- Creature AI scales with creature count

**Dynamic vs. Static:**

- **[GIT](GFF-File-Format#git-game-instance-template)**: Dynamic, saved with game progress
- **are**: Static, never changes
- [GIT](GFF-File-Format#git-game-instance-template) instances can be destroyed, moved, modified
- are properties remain constant

**Save Game Integration:**

- [GIT](GFF-File-Format#git-game-instance-template) state saved in save files
- Instance positions, HP, inventory preserved
- Destroyed objects marked as deleted
- New dynamic objects added to save

**Common [GIT](GFF-File-Format#git-game-instance-template) Patterns:**

**Ambush Spawns:**

- Creatures placed outside player view
- Positioned for tactical advantage
- Often linked to trigger activation

**Progression Gates:**

- Locked doors requiring keys/skills
- Triggers that load new modules
- Waypoints marking objectives

**Interactive Areas:**

- Clusters of placeables (containers)
- NPCs for dialogue
- Stores for shopping
- Workbenches for crafting

**Navigation Networks:**

- Waypoints for AI pathfinding
- Logical connections via LinkedTo
- Map notes for player guidance

**Audio Atmosphere:**

- Ambient sound emitters positioned strategically
- Varied volumes and ranges
- Random offsets for natural feel

### See also

- [GFF-File-Format](GFF-File-Format) -- GFF structure
- [GFF-ARE](GFF-Module-and-Area#are) -- Area properties
- [GFF-UTC](GFF-Creature-and-Dialogue#utc)
- [GFF-UTD](GFF-Spatial-Objects#utd)
- [GFF-UTP](GFF-Spatial-Objects#utp)
- [GFF-UTT](GFF-Spatial-Objects#utt)
- [GFF-UTW](GFF-Spatial-Objects#utw) -- Instance types
- [TSLPatcher GFFList Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax) -- Patching GIT via mod installers
- [Container-Formats#key](Container-Formats#key) -- Resource resolution


---

<a id="ifo"></a>

# IFO ([module info](GFF-File-Format#ifo-module-info))

Part of the [GFF File Format Documentation](GFF-File-Format).

IFO files define module-level metadata including entry configuration, expansion requirements, area lists, and module-wide script hooks. [IFO](GFF-File-Format#ifo-module-info) files are the "main" descriptor for game modules, specifying where the player spawns and what scripts run at module scope. IFO files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine [IFO](GFF-File-Format#ifo-module-info) format specification, see [Bioware Aurora IFO Format](Bioware-Aurora-Module-and-Area#ifo).

**For mod developers:**

- To modify module metadata in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFF-Syntax#gfflist-syntax).
- For general modding, see [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers).

**Related formats:**

- [ARE](GFF-Module-and-Area#are)
- [GIT](GFF-File-Format#git-game-instance-template)
- [NCS](NCS-File-Format)
- [KEY](Container-Formats#key)
- [BIF](Container-Formats#bif)

PyKotor models module descriptors through [`IFO`, `construct_ifo`, `read_ifo`, and `write_ifo`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/ifo.py#L18), tags them as [`GFFContent.IFO`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L164), and decodes them through the same shared [`GFFBinaryReader.load`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) path that Holocron Toolset builds on for entry points, area lists, and module scripts in its getting-started, module-editor, and module-resources flows. Reone's [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp) and [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp), KotOR.js's [`GFFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), Kotor.NET's [`GFF.cs`](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18), and xoreos's Aurora loader likewise treat IFO as a typed GFF root rather than a separate binary dialect.

## Core Module Identity

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Mod_ID` | Void (16 bytes) | Unique module identifier (GUID) |
| `Mod_Tag` | [CExoString](GFF-File-Format#gff-data-types) | Module tag identifier |
| `Mod_Name` | [CExoLocString](GFF-File-Format#gff-data-types) | Module name (localized) |
| `Mod_Creator_ID` | UInt32 | Toolset creator ID |
| `Mod_Version` | UInt32 | Module version number |
| `Mod_VO_ID` | [CExoString](GFF-File-Format#gff-data-types) | Voice-over folder name |

**Module Identification:**

- **Mod_ID**: 16-[byte](GFF-File-Format#gff-data-types) GUID generated by toolset
- **Mod_Tag**: Script-accessible identifier
- **Mod_Name**: Displayed in load screens
- **Mod_VO_ID**: Subfolder in StreamVoice for voice files

## Entry Configuration

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Mod_Entry_Area` | *ResRef* | Starting [area](GFF-File-Format#are-area) *ResRef* |
| `Mod_Entry_X` | Float | Entry X coordinate |
| `Mod_Entry_Y` | Float | Entry Y coordinate |
| `Mod_Entry_Z` | Float | Entry Z coordinate |
| `Mod_Entry_Dir_X` | Float | Entry direction X (facing) |
| `Mod_Entry_Dir_Y` | Float | Entry direction Y (facing) |

**Player Spawn:**

- **Mod_Entry_Area**: Initial area to load (are/[GIT](GFF-File-Format#git-game-instance-template))
- **Entry position**: XYZ coordinates in world space
- **Entry Direction**: Player's initial facing angle
  - Direction computed as: `atan2(Dir_Y, Dir_X)`

**Module Start Sequence:**

1. Load [IFO](GFF-File-Format#ifo-module-info) to get entry configuration
2. Load Mod_Entry_Area (are + [GIT](GFF-File-Format#git-game-instance-template))
3. Spawn player character at Entry position
4. Set player orientation from Entry direction
5. Execute Mod_OnModStart script

## Area List

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Mod_Area_list` | [List](GFF-File-Format#gff-data-types) | Areas in this module |

**Mod_Area_list Struct fields:**

- `Area_Name` (*ResRef*): [Area](GFF-File-Format#are-area) *ResRef* (are file)

**Area Management:**

- Lists all areas accessible in module
- Areas loaded on-demand as player transitions
- KotOR modules typically have 1 area per module
- KotOR2 can have multiple areas per module

## Expansion Pack Requirements

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Expansion_Pack` | [word](GFF-File-Format#gff-data-types) | Required expansion bitfield |
| `Mod_MinGameVer` | [CExoString](GFF-File-Format#gff-data-types) | Minimum game version |

**Expansion Flags (Bitfield):**

- **0x01**: Requires expansion pack 1
- **0x02**: Requires expansion pack 2
- Additional bits for future expansions

**Version Requirements:**

- **Mod_MinGameVer**: Minimum executable version
- Prevents loading in older game versions
- format: "1.0", "1.03", "2.0", etc.

## Starting Movie & HAK files

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Mod_StartMovie` | *ResRef* | Starting movie file |
| `Mod_Hak` | [CExoString](GFF-File-Format#gff-data-types) | Required HAK file list |

**Module Initialization:**

- **Mod_StartMovie**: BIK movie played before module loads
- **Mod_Hak**: Semicolon-separated HAK file names
- HAKs loaded before module resources

**HAK System:**

- HAK files override base game resources
- Custom content may include:

  - [models](MDL-MDX-File-Format)
  - [textures](Texture-Formats#tpc)
  - Scripts
- Listed in load priority order

## Cache & XP Settings

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Mod_IsSaveGame` | [byte](GFF-File-Format#gff-data-types) | Module is from save file |
| `Mod_CacheNSSData` | [byte](GFF-File-Format#gff-data-types) | Cache compiled scripts |
| `Mod_XPScale` | [byte](GFF-File-Format#gff-data-types) | Experience point multiplier (0-200%) |

**Module flags:**

- **Mod_IsSaveGame**: Internal flag (always 0 in files)
- **Mod_CacheNSSData**: Performance optimization
- **Mod_XPScale**: 100 = normal, 200 = double XP

## DawnStar Property (Unused)

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Mod_DawnHour` | [byte](GFF-File-Format#gff-data-types) | Dawn start hour (unused) |
| `Mod_DuskHour` | [byte](GFF-File-Format#gff-data-types) | Dusk start hour (unused) |
| `Mod_MinPerHour` | UInt32 | Minutes per hour (unused) |

**Day/Night Cycle:**

- Defined but unused in KotOR
- Intended for time-based events
- No dynamic lighting/NPC schedules

## Module Script Hooks

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Mod_OnAcquirItem` | *ResRef* | Fires when item acquired |
| `Mod_OnActvtItem` | *ResRef* | Fires when item activated/used |
| `Mod_OnClientEntr` | *ResRef* | Fires on player enter (multiplayer) |
| `Mod_OnClientLeav` | *ResRef* | Fires on player leave (multiplayer) |
| `Mod_OnCutsnAbort` | *ResRef* | Fires when cutscene aborted |
| `Mod_OnHeartbeat` | *ResRef* | Fires periodically (~6 seconds) |
| `Mod_OnModLoad` | *ResRef* | Fires when module finishes loading |
| `Mod_OnModStart` | *ResRef* | Fires after player spawned |
| `Mod_OnPlrDeath` | *ResRef* | Fires when player dies |
| `Mod_OnPlrDying` | *ResRef* | Fires when player HP reaches 0 |
| `Mod_OnPlrEqItm` | *ResRef* | Fires when equipment changed |
| `Mod_OnPlrLvlUp` | *ResRef* | Fires on level up |
| `Mod_OnPlrRest` | *ResRef* | Fires when player rests |
| `Mod_OnPlrUnEqItm` | *ResRef* | Fires when equipment removed |
| `Mod_OnSpawnBtnDn` | *ResRef* | Fires on spawn button (multiplayer) |
| `Mod_OnUnAqreItem` | *ResRef* | Fires when item lost/sold |
| `Mod_OnUsrDefined` | *ResRef* | Fires on user-defined events |

**Script Execution:**

- Module scripts run in module context
- Can access/modify module-wide state
- Higher scope than area scripts

**Common Script Uses:**

**Mod_OnModLoad:**

- Initialize global variables
- Setup persistent data structures
- Load saved state

**Mod_OnModStart:**

- Start cinematics
- Give starting equipment
- Setup initial conversations

**Mod_OnHeartbeat:**

- Update timers
- Check global conditions
- Ambient system updates

**Mod_OnPlrDeath:**

- Game over sequence
- Respawn handling
- Load last save

## Implementation Notes

**Module Loading Sequence:**

1. **Read [IFO](GFF-File-Format#ifo-module-info)**: Parse module metadata
2. **Check Requirements**: Verify Expansion_Pack and MinGameVer
3. **Load HAKs**: Mount HAK files in order
4. **Play Movie**: Show Mod_StartMovie if set
5. **Load Entry Area**: Read are + [GIT](GFF-File-Format#git-game-instance-template) for Mod_Entry_Area
6. **Spawn Player**: Place at Entry position/direction
7. **Fire OnModLoad**: Execute module load script
8. **Fire OnModStart**: Execute module start script
9. **Start Gameplay**: Enable player control

**[IFO](GFF-File-Format#ifo-module-info) vs. are vs. GIT:**

- **[IFO](GFF-File-Format#ifo-module-info)**: Module-level metadata and entry config
- **are**: Static area properties (lighting, fog, grass)
- **[GIT](GFF-File-Format#git-game-instance-template)**: Dynamic object instances (creatures, doors, etc.)

**Save Game Integration:**

- [IFO](GFF-File-Format#ifo-module-info) saved with current state
- Entry position updated to save location
- Module scripts preserved
- Mod_IsSaveGame flag set

**Module Transitions:**

- When transitioning to new module:
  1. Current module [IFO](GFF-File-Format#ifo-module-info) updated with player position
  2. Current module saved to save game
  3. New module [IFO](GFF-File-Format#ifo-module-info) loaded
  4. Player spawned at new Entry position (or LinkedTo waypoint)

**Multi-Area Modules (KotOR2):**

- Mod_Area_list contains multiple areas
- Areas loaded as needed
- Transitions within module don't fire OnModStart
- Shared module-level state

**Single-Area Modules (KotOR1):**

- Typical KotOR1 pattern
- One area per [IFO](GFF-File-Format#ifo-module-info)
- Module transition = area transition
- Simpler resource management

**Script Scope Hierarchy:**

1. **Module Scripts** ([IFO](GFF-File-Format#ifo-module-info)): Highest scope, module-wide
2. **Area Scripts** (are): Area-specific events
3. **Object Scripts** (per blueprint type such as [UTC](GFF-File-Format#utc-creature) or [UTD](GFF-File-Format#utd-door)): Individual object events

**Common Module Configurations:**

**Story Modules:**

- Specific entry position for narrative flow
- StartMovie for cinematics
- OnModStart for dialogue/cutscenes
- Custom HAKs for unique content

**Hub Modules:**

- Central entry position (hub center)
- Multiple area transitions
- Vendors, NPCs, quest givers
- No start movie typically

**Combat Modules:**

- Entry position near enemies
- OnModStart spawns for ambush
- Battle music configured
- XPScale adjusted for difficulty

**Tutorial Modules:**

- Guided entry position
- OnModStart tutorial dialogue
- Reduced XPScale
- Special script hooks for teaching mechanics

### See also

- [GFF-File-Format](GFF-File-Format) -- Generic format underlying IFO
- [GFF-ARE (Area)](GFF-Module-and-Area#are) - Area properties; Mod_Entry_Area and Mod_Area_list
- [GIT (Game Instance Template)](GFF-File-Format#git-game-instance-template) - Dynamic area contents
- [Bioware Aurora IFO Format](Bioware-Aurora-Module-and-Area#ifo) - Official module info specification


---

<a id="pth"></a>

# PTH (Path)

PTH is a GFF-based module file that stores the NPC pathfinding graph for an area. It holds a list of 2D nodes (`Path_Points`) and directed edges (`Path_Connections`) that the AI uses to plan high-level movement routes across the area. Unlike the [BWM walkmesh](Level-Layout-Formats#bwm) (which handles per-step collision and surface types), PTH encodes a coarser connectivity graph for NPC route planning [[1](https://deadlystream.com/files/file/518-modhex)] [[2](https://lucasforumsarchive.com/thread/178681-kotor-i-ii-file-format-docs)] [[`pth.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/pth.py#L19)].

PTH is stored as a `.res` resource (resource type `0x0BBB`) inside the module package alongside `.are`, `.git`, and `.ifo` [[3](https://lucasforumsarchive.com/thread/178681-kotor-i-ii-file-format-docs)]. In the Holocron Toolset and KotOR Tool, it can be edited with Bead-V's PTH editor [[4](https://deadlystream.com/files/file/518-modhex)].

## Path points

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Path_Points` | List | List of 2D navigation nodes for this area |

**Path_Points struct fields:**

- `X` (Float): X world coordinate of the node.
- `Y` (Float): Y world coordinate of the node.
- `Connections` (Int): Number of outgoing edges from this node.
- `First_Conection` (Int): Index into `Path_Connections` of the first edge for this node.

## Path connections

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Path_Connections` | List | Directed edges between path nodes |

**Path_Connections struct fields:**

- `Destination` (Int): Index of the destination node in `Path_Points`.

## Notes

- `Path_Points` and `Path_Connections` may both be absent in retail modules; the game treats absent lists as empty [[`pth.py` L19-27](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/pth.py#L19)].
- The Z coordinate is not used in path movement; pathfinding is effectively 2D.
- PTH is **not** the same as the walkmesh. The walkmesh ([BWM](Level-Layout-Formats#bwm)) is a triangle mesh used for per-character collision and step-by-step movement. PTH is a separate high-level graph used for route planning.

### See also

- [GFF File Format](GFF-File-Format) - Parent GFF format
- [GFF-ARE](GFF-Module-and-Area#are) - Area properties
- [GFF-GIT](GFF-Module-and-Area#git) - Game instance template (creature and encounter placement)
- [BWM File Format](Level-Layout-Formats#bwm) - Walkmesh (distinct from PTH)
- [GFF-UTW](GFF-Spatial-Objects#utw) - Waypoints (used for NPC patrol scripts)
