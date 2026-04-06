# Kit structure Documentation

Kits are collections of reusable indoor map components for the Holocron Toolset. They contain [room models](Level-Layout-Formats#room-definitions), [textures](Texture-Formats#tpc), lightmaps, doors, and other resources that can be assembled into complete game modules.

## Table of Contents

- Kit structure Documentation
  - Table of Contents
  - [Kit Overview](#kit-overview)
  - [Kit Directory structure](#kit-directory-structure)
  - [Kit JSON file](#kit-json-file)
  - [Components](#components)
  - [textures and Lightmaps](#textures-and-lightmaps)
    - [texture Extraction](#texture-extraction)
    - [Resource Resolution Priority](#resource-resolution-priority)
    - [TXI files](#txi-files)
    - [Shared Resources](#shared-resources)
  - [Always Folder](#always-folder)
  - [Doors](#doors)
    - [Door Walkmeshes (DWK)](#door-walkmeshes-dwk)
  - [Placeables](#placeables)
    - [Placeable Walkmeshes (PWK)](#placeable-walkmeshes-pwk)
  - [Skyboxes](#skyboxes)
  - [Doorway Padding](#doorway-padding)
  - [models Directory](#models-directory)
  - [Resource Extraction](#resource-extraction)
    - [Archive file Support](#archive-file-support)
    - [Component Identification](#component-identification)
    - [texture and Lightmap Extraction](#texture-and-lightmap-extraction)
    - [Door Extraction](#door-extraction)
    - [walkmesh Extraction](#walkmesh-extraction)
    - [BWM Re-centering](#bwm-re-centering)
    - [Minimap Generation](#minimap-generation)
    - [Doorhook Extraction](#doorhook-extraction)
  - [Implementation Details](#implementation-details)
    - [Kit Class structure](#kit-class-structure)
    - [Kit Loading](#kit-loading)
    - [Indoor Map Generation](#indoor-map-generation)
    - [coordinate System](#coordinate-system)
  - [Kit types](#kit-types)
    - [Component-Based Kits](#component-based-kits)
    - [texture-Only Kits](#texture-only-kits)
  - [Game Engine Compatibility](#game-engine-compatibility)
  - [Cross-reference: engine implementations](#cross-reference-engine-implementations)
    - [Door Walkmesh (DWK) Extraction](#door-walkmesh-dwk-extraction)
    - [Placeable Walkmesh (PWK) Extraction](#placeable-walkmesh-pwk-extraction)
    - [room model and Component Identification](#room-model-and-component-identification)
    - [Door model Resolution](#door-model-resolution)
    - [Placeable model Resolution](#placeable-model-resolution)
    - [Texture and Lightmap Extraction](#texture-and-lightmap-extraction)
    - [Resource Resolution Priority](#resource-resolution-priority)
    - [BWM/WOK walkmesh Handling](#bwmwok-walkmesh-handling)
    - [module archives Loading](#module-archives-loading)
    - [KEY Discrepancies and Rationale](#key-discrepancies-and-rationale)
  - [Test Comparison Precision](#test-comparison-precision)
    - [Exact Matching (1:1 byte-for-byte)](#exact-matching-11-byte-for-byte)
    - [Approximate Matching (Tolerance-Based)](#approximate-matching-tolerance-based)
    - [structure-Only Verification (No value Comparison)](#structure-only-verification-no-value-comparison)
    - [Recommended Test Improvements](#recommended-test-improvements)
  - [Best Practices](#best-practices)

---

## Kit Overview

A kit is a self-contained collection of resources that can be used to build indoor maps. Kits are stored in `Tools/HolocronToolset/src/toolset/kits/kits/` and consist of:

- **Components**: Room models ([MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format)/[WOK](Level-Layout-Formats#bwm)) with hook points for connecting to other rooms
- **[textures](Texture-Formats#tpc)**: TGA [texture files](Texture-Formats#tpc) with optional [TXI](Texture-Formats#txi) metadata
- **Lightmaps**: TGA lightmap files with optional [TXI](Texture-Formats#txi) metadata
- **Doors**: [UTD](GFF-File-Format#utd-door) door templates (K1 and K2 versions) with [DWK](Level-Layout-Formats#bwm) [walkmeshes](Level-Layout-Formats#bwm)
- **Placeables**: [UTP](GFF-File-Format#utp-placeable) [placeable templates](GFF-File-Format#utp-placeable) with [PWK](Level-Layout-Formats#bwm) walkmeshes (optional)
- **Skyboxes**: Optional [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format) [models](MDL-MDX-File-Format) for sky rendering
- **Always Resources**: Static resources included in every generated module
- **[models](MDL-MDX-File-Format)**: Additional [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format) [models](MDL-MDX-File-Format) referenced by the module but not used as components

This layout mirrors the Holocron Toolset indoor-kit data model and loader package structure ([`toolset/data/indoorkit/`](https://github.com/OpenKotOR/PyKotor/tree/master/Tools/HolocronToolset/src/toolset/data/indoorkit)).

---

## Kit Directory structure

```shell
kits/
├── {kit_id}/
│   ├── {kit_id}.json          # Kit definition file
│   ├── {component_id}.mdl     # Component model files
│   ├── {component_id}.mdx
│   ├── {component_id}.wok     # Component walkmesh (re-centered to origin)
│   ├── {component_id}.png     # Component minimap image (top-down view)
│   ├── textures/              # Texture files
│   │   ├── {texture_name}.tga
│   │   └── {texture_name}.txi
│   ├── lightmaps/             # Lightmap files
│   │   ├── {lightmap_name}.tga
│   │   └── {lightmap_name}.txi
│   ├── always/                # Always-included resources (optional)
│   │   └── {resource_name}.{ext}
│   ├── skyboxes/              # Skybox models (optional)
│   │   ├── {skybox_name}.mdl
│   │   └── {skybox_name}.mdx
│   ├── doorway/               # Door padding models (optional)
│   │   ├── {side|top}_{door_id}_size{size}.mdl
│   │   └── {side|top}_{door_id}_size{size}.mdx
│   ├── models/                # Additional models (optional)
│   │   ├── {model_name}.mdl
│   │   └── {model_name}.mdx
│   ├── {door_name}_k1.utd     # Door templates
│   ├── {door_name}_k2.utd
│   ├── {door_model}0.dwk      # Door walkmeshes (3 states: 0=closed, 1=open1, 2=open2)
│   ├── {door_model}1.dwk
│   ├── {door_model}2.dwk
│   └── {placeable_model}.pwk  # Placeable walkmeshes (optional)
```

**Example**: `jedienclave/` contains [textures](Texture-Formats#tpc) and lightmaps but no components ([texture](Texture-Formats#tpc)-only kit). `enclavesurface/` contains full components with [models](MDL-MDX-File-Format), [walkmeshes](Level-Layout-Formats#bwm), and minimaps.

---

## Kit JSON file

The kit JSON file (`{kit_id}.json`) defines the kit structure:

```json5
{
    "name": "Kit Display Name",
    "id": "kitid",
    "ht": "2.0.2",
    "version": 1,
    "components": [
        {
            "name": "Component Name",
            "id": "component_id",
            "native": 1,
            "doorhooks": [
                {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0,
                    "rotation": 90.0,
                    "door": 0,
                    "edge": 20
                }
            ]
        }
    ],
    "doors": [
        {
            "utd_k1": "door0_k1",
            "utd_k2": "door0_k2",
            "width": 2.0,
            "height": 3.0
        }
    ]
}
```

**fields**:

- `name`: Display name for the kit
- `id`: Unique kit identifier (matches folder name, must be lowercase, sanitized)
- `ht`: Holocron Toolset version compatibility string
- `version`: Kit version number (integer)
- `components`: List of room components (can be empty for [texture](Texture-Formats#tpc)-only kits)
- `doors`: List of door definitions

**Component fields**:

- `name`: Display name for the component
- `id`: Unique component identifier (matches [MDL](MDL-MDX-File-Format)/[WOK](Level-Layout-Formats#bwm) filename without extension)
- `native`: Always 1 (legacy field, indicates native format)
- `doorhooks`: List of door hook points extracted from [BWM](Level-Layout-Formats#bwm) [edges](Level-Layout-Formats#edges-wok-only) with transitions

**Door Hook fields**:

- `x`, `y`, `z`: World-space position of the hook point (midpoint of [BWM](Level-Layout-Formats#bwm) [edge](Level-Layout-Formats#edges-wok-only) with transition)
- `rotation`: rotation angle in degrees (0-360), calculated from [edge](Level-Layout-Formats#edges-wok-only) direction in XY plane
- `door`: index into the kit's `doors` array (mapped from [BWM](Level-Layout-Formats#bwm) [edge](Level-Layout-Formats#edges-wok-only) transition index)
- `edge`: Global [edge](Level-Layout-Formats#edges-wok-only) index in the BWM (face_index * 3 + local_edge_index)

**Door fields**:

- `utd_k1`: [ResRef](GFF-File-Format#gff-data-types) of K1 door [UTD](GFF-File-Format#utd-door) file (without `.utd` extension)
- `utd_k2`: [ResRef](GFF-File-Format#gff-data-types) of K2 door [UTD](GFF-File-Format#utd-door) file (without `.utd` extension)
- `width`: Door width in world units (default: 2.0)
- `height`: Door height in world units (default: 3.0)

All of these JSON fields are loaded and validated directly by the indoor-kit loader implementation ([`indoorkit_loader.py` L23-L260](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/indoorkit/indoorkit_loader.py#L23-L260)).

---

## Components

Components are reusable [room models](Level-Layout-Formats#room-definitions) that can be placed and connected to build indoor maps. They are identified during kit extraction as [MDL files](MDL-MDX-File-Format) that:

1. Are listed as [room models](Level-Layout-Formats#room-definitions) in the module's [LYT file](Level-Layout-Formats#lyt)
2. Have corresponding WOK ([walkmesh](Level-Layout-Formats#bwm)) files
3. Are not skyboxes (skyboxes have [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format) but no [WOK](Level-Layout-Formats#bwm))

**Component files**:

- `{component_id}.mdl`: 3D [model](MDL-MDX-File-Format) geometry (BioWare [MDL](MDL-MDX-File-Format) format)
- `{component_id}.mdx`: [material](MDL-MDX-File-Format#trimesh-header)/lightmap index data (BioWare [MDX](MDL-MDX-File-Format) format)
- `{component_id}.wok`: [walkmesh](Level-Layout-Formats#bwm) for pathfinding (BioWare [BWM](Level-Layout-Formats#bwm) format, re-centered to origin)
- `{component_id}.png`: Minimap image (top-down view of [walkmesh](Level-Layout-Formats#bwm), generated from [BWM](Level-Layout-Formats#bwm))

**Component Identification Process**:

1. Load module [LYT file](Level-Layout-Formats#lyt) to get list of [room model](Level-Layout-Formats#room-definitions) names
2. For each [room model](Level-Layout-Formats#room-definitions), resolve [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format)/[WOK](Level-Layout-Formats#bwm) using installation-wide resource resolution
3. Components are [room models](Level-Layout-Formats#room-definitions) that have both [MDL](MDL-MDX-File-Format) and [WOK files](Level-Layout-Formats#bwm)
4. Component IDs are mapped from [model](MDL-MDX-File-Format) names using `_get_component_name_mapping()` to create friendly names

**Component JSON structure**:

```json5
{
    "name": "Hall 1",
    "id": "hall_1",
    "native": 1,
    "doorhooks": [
        {
            "x": -4.476789474487305,
            "y": -17.959964752197266,
            "z": 3.8257503509521484,
            "rotation": 90.0,
            "door": 0,
            "edge": 25
        }
    ]
}
```

**[BWM](Level-Layout-Formats#bwm) Re-centering**: Component [WOK files](Level-Layout-Formats#bwm) are **re-centered to origin (0, 0, 0)** before saving. This is critical because:

- The Indoor Map Builder draws preview images centered at `room.position`
- The [walkmesh](Level-Layout-Formats#bwm) is translated BY `room.position` from its original coordinates
- For alignment, the [BWM](Level-Layout-Formats#bwm) must be centered around (0, 0) so both image and [walkmesh](Level-Layout-Formats#bwm) are at the same position after [transformation](Level-Layout-Formats#adjacencies-wok-only)

This re-centering behavior is implemented in the kit extraction flow that translates component walkmeshes and emits normalized component outputs ([`kit.py` L1538-L1588](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1538-L1588)).

**Door Hooks**:

- `x`, `y`, `z`: World-space position of the hook point (midpoint of [BWM](Level-Layout-Formats#bwm) [edge](Level-Layout-Formats#edges-wok-only) with transition)
- `rotation`: rotation angle in degrees (0-360), calculated from [edge](Level-Layout-Formats#edges-wok-only) direction using `atan2(dy, dx)`
- `door`: index into the kit's `doors` array (mapped from [BWM](Level-Layout-Formats#bwm) [edge](Level-Layout-Formats#edges-wok-only) transition index, clamped to valid range)
- `edge`: Global [edge](Level-Layout-Formats#edges-wok-only) index in the BWM (used for door placement during map generation)

**Hook Extraction**: Door hooks are extracted from [BWM](Level-Layout-Formats#bwm) [edges](Level-Layout-Formats#edges-wok-only) that have valid transitions (`edge.transition >= 0`). The transition index maps to the door index in the kit's doors array.

This edge-to-hook extraction and transition mapping logic is implemented in the same kit extraction path ([`kit.py` L1467-L1535](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1467-L1535)).

**Hook Connection Logic**: Components are connected when their hook points are within proximity. The toolset automatically links compatible hooks to form room connections.

Connection evaluation behavior is defined by the indoor-kit base model's hook compatibility logic ([`indoorkit_base.py` L88-L106](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/indoorkit/indoorkit_base.py#L88-L106)).

---

## [textures](Texture-Formats#tpc) and Lightmaps

Kits contain all [textures](Texture-Formats#tpc) and lightmaps referenced by their component [models](MDL-MDX-File-Format), plus any additional shared resources found in the module or installation.

### [texture](Texture-Formats#tpc) Extraction

[textures](Texture-Formats#tpc) are extracted from multiple sources using the game engine's resource resolution priority:

1. **Module RIM/[ERF](Container-Formats#erf) files**: [textures](Texture-Formats#tpc) directly in the [module archives](Container-Formats#erf)
2. **Installation-wide Resolution**: [textures](Texture-Formats#tpc) from:
   - `override/` (user mods, highest priority)
   - `modules/` (module-specific overrides, `.mod` files take precedence over `.rim` files)
   - `textures_gui/` ([GUI](GFF-File-Format#gui-graphical-user-interface) [textures](Texture-Formats#tpc))
   - `texturepacks/` (TPA/[ERF](Container-Formats#erf) [texture](Texture-Formats#tpc) packs)
   - `chitin/` (base game [BIF files](Container-Formats#bif), lowest priority)

**[texture](Texture-Formats#tpc) Identification**:

- [textures](Texture-Formats#tpc) are identified by scanning all [MDL files](MDL-MDX-File-Format) in the module using `iterate_textures()`
- This extracts [texture](Texture-Formats#tpc) references from [MDL](MDL-MDX-File-Format) [material](MDL-MDX-File-Format#trimesh-header) definitions
- All [models](MDL-MDX-File-Format) from `module.models()` are scanned, including those loaded from CHITIN

**[texture](Texture-Formats#tpc) Naming**:

- [textures](Texture-Formats#tpc): Standard names (e.g., `lda_wall02`, `i_datapad`)
- Lightmaps: Suffixed with `_lm` or prefixed with `l_` (e.g., `m13aa_01a_lm0`, `l_sky01`)

**[TPC](Texture-Formats#tpc) to TGA Conversion**: All [textures](Texture-Formats#tpc) are converted from TPC (BioWare's [texture](Texture-Formats#tpc) format) to TGA (Truevision Targa) format during extraction. The conversion process:

1. Reads [TPC file](Texture-Formats#tpc) data
2. Parses [TPC](Texture-Formats#tpc) structure (mipmaps, format, embedded [TXI](Texture-Formats#txi))
3. Converts mipmaps to RGBA format if needed
4. Writes TGA file with BGRA pixel order (TGA format requirement)

This conversion path is implemented directly in the kit extraction texture pipeline ([`kit.py` L926-L948](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L926-L948)).

### Resource Resolution Priority

The extraction process uses the same resource resolution priority as the game engine:

1. **OVERRIDE** (priority 0 - highest): User mods in `override/` folder
2. **MODULES** (priority 1-2): Module files
   - `.mod` files (priority 1) - take precedence over `.rim` files
   - `.rim` and `_s.rim` files (priority 2)
3. **TEXTURES_GUI** (priority 3): [GUI](GFF-File-Format#gui-graphical-user-interface) [textures](Texture-Formats#tpc)
4. **TEXTURES_TPA** (priority 4): [texture](Texture-Formats#tpc) packs
5. **CHITIN** (priority 5 - lowest): Base game [BIF files](Container-Formats#bif)

The exact priority ordering used here comes from the resource-location ranking logic in the kit tooling ([`kit.py` L74-L120](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L74-L120)).

**Batch Processing**: [texture](Texture-Formats#tpc)/lightmap lookups are batched for performance:

- Single `installation.locations()` call for all [textures](Texture-Formats#tpc)/lightmaps
- Results are pre-sorted by priority once to avoid repeated sorting
- [TPC](Texture-Formats#tpc)/TGA files are grouped by filepath for batch I/O operations

This batching behavior is implemented in the texture/lightmap lookup and extraction routines used by kit generation ([`kit.py` L814-L964](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L814-L964)).

### [TXI](Texture-Formats#txi) files

Each [texture](Texture-Formats#tpc)/lightmap can have an accompanying `.txi` file containing [texture](Texture-Formats#tpc) metadata (filtering, wrapping, etc.). [TXI files](Texture-Formats#txi) are extracted from:

1. **Embedded [TXI](Texture-Formats#txi) in [TPC](Texture-Formats#tpc) files**: [TPC files](Texture-Formats#tpc) can contain embedded [TXI](Texture-Formats#txi) data
2. **Standalone [TXI](Texture-Formats#txi) files**: [TXI files](Texture-Formats#txi) in the installation (same resolution priority as [textures](Texture-Formats#tpc))
3. **Empty [TXI](Texture-Formats#txi) placeholders**: If no [TXI](Texture-Formats#txi) is found, an empty [TXI file](Texture-Formats#txi) is created to match expected kit structure

**[TXI](Texture-Formats#txi) Extraction Process**:

1. Check for embedded [TXI](Texture-Formats#txi) in [TPC file](Texture-Formats#tpc) during conversion
2. If not found, lookup standalone [TXI file](Texture-Formats#txi) using batch location results
3. If still not found, create empty [TXI](Texture-Formats#txi) placeholder

The embedded-first then standalone fallback flow is implemented in the same extraction block that writes texture assets for kits ([`kit.py` L849-L1020](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L849-L1020)).

### Shared Resources

Some kits include [textures](Texture-Formats#tpc)/lightmaps from **other modules** that are not directly referenced by the kit's own [models](MDL-MDX-File-Format). These are typically:

- **Shared Lightmaps**: Lightmaps from other modules stored in `lightmaps3.bif` (CHITIN) that may be used by multiple areas
  - Example: `m03af_01a_lm13`, `m10aa_01a_lm13`, `m14ab_02a_lm13` from `jedienclave` kit
  - These are found in `data/lightmaps3.bif` as shared resources across multiple modules
  - They may be referenced by other modules that share resources with the kit's source module
- **Common [textures](Texture-Formats#tpc)**: [textures](Texture-Formats#tpc) from `swpc_tex_tpa.erf` ([texture](Texture-Formats#tpc) packs) used across multiple modules
  - Example: `lda_*` textures (lda_bark04, lda_flr07, etc.) from [texture](Texture-Formats#tpc) packs
  - These are shared resources that may be used by multiple areas
- **Module Resources**: [textures](Texture-Formats#tpc)/lightmaps found in the module's resource list but not directly referenced by [models](MDL-MDX-File-Format)
  - Some resources may be included even if not directly referenced
  - These ensure the kit is self-contained and doesn't depend on external resources

**Why Include Shared Resources?**:

- **Self-Containment**: Ensures the kit has all resources it might need
- **Compatibility**: Some resources may be referenced indirectly or by other systems
- **Convenience**: Manually curated collections of commonly used resources
- **Future-Proofing**: Resources that might be needed when the kit is used in different contexts

Investigation using `Installation.locations()` shows these resources are found in the following locations:

- `data/lightmaps3.bif` (CHITIN) for shared lightmaps
- `texturepacks/swpc_tex_tpa.erf` (TEXTURES_TPA) for common [textures](Texture-Formats#tpc)

This has been verified via `Installation.locations()` lookups that resolve shared lightmaps to CHITIN BIFs and common kit textures to TPA texturepacks under the standard priority model.

---

## Always Folder

The `always/` folder contains resources that are **always included** in the generated module, regardless of which components are used.

**Purpose**:

- **Static Resources**: Resources that should be included in every generated module using the kit
- **Common Assets**: Shared [textures](Texture-Formats#tpc), [models](MDL-MDX-File-Format), or other resources needed by all rooms
- **Override Resources**: Resources that override base game files and should be included in every room
- **Non-Component Resources**: Resources that don't belong to specific components but are needed for the kit to function

**Usage**: When a kit is used to generate a module, all files in the `always/` folder are automatically added to the mod's resource list via `add_static_resources()`. These resources are included in every room, even if they're not directly referenced by component [models](MDL-MDX-File-Format).

**Processing**: Resources in the `always/` folder are processed during indoor map generation:

1. Each file in `always/` is loaded into `kit.always[filename]` during kit loading
2. When a room is processed, `add_static_resources()` extracts the resource name and type from the filename
3. The resource is added to the mod with `mod.set_data(resname, restype, data)`
4. This happens for every room, ensuring the resource is always available

**Example**: The `sithbase` kit includes:

- `CM_asith.tpc`: Common [texture](Texture-Formats#tpc) used across all rooms
- `lsi_floor01b.tpc`, `lsi_flr03b.tpc`, `lsi_flr04b.tpc`: Floor [textures](Texture-Formats#tpc) for all rooms
- `lsi_win01bmp.tpc`: Window [texture](Texture-Formats#tpc) used throughout the base

These are added to every room when using the sithbase kit, ensuring consistent appearance across all generated rooms.

**When to Use**:

- Resources that should be available in every room (e.g., common floor [textures](Texture-Formats#tpc))
- Override resources that replace base game files
- Resources needed for kit functionality but not tied to specific components
- Shared assets that multiple components might reference

Always-folder resource injection is handled by the indoor map generation path that calls `add_static_resources()` during room processing ([`indoormap.py` L236-L256](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/indoormap.py#L236-L256)).

---

## Doors

Doors are defined in the kit JSON and have corresponding [UTD](GFF-File-Format#utd-door) files. Doors connect adjacent rooms at component hook points.

**Door files**:

- `{door_name}_k1.utd`: KotOR 1 door template ([UTD](GFF-File-Format#utd-door) format)
- `{door_name}_k2.utd`: KotOR 2 door template ([UTD](GFF-File-Format#utd-door) format)
- `{door_model}0.dwk`: Door [walkmesh](Level-Layout-Formats#bwm) for closed state
- `{door_model}1.dwk`: Door [walkmesh](Level-Layout-Formats#bwm) for open1 state
- `{door_model}2.dwk`: Door [walkmesh](Level-Layout-Formats#bwm) for open2 state

**Door JSON structure**:

```json5
{
    "utd_k1": "door0_k1",
    "utd_k2": "door0_k2",
    "width": 2.0,
    "height": 3.0
}
```

**Door Properties**:

- `utd_k1`, `utd_k2`: ResRefs of [UTD](GFF-File-Format#utd-door) files (without `.utd` extension)
- `width`: Door width in world units (default: 2.0)
- `height`: Door height in world units (default: 3.0)

**Door Extraction Process**:

1. [UTD](GFF-File-Format#utd-door) files are extracted from module RIM/[ERF](Container-Formats#erf) archives
2. Door [model](MDL-MDX-File-Format) names are resolved from [UTD](GFF-File-Format#utd-door) files using `genericdoors.2da`
3. [DWK](Level-Layout-Formats#bwm) [walkmeshes](Level-Layout-Formats#bwm) are extracted for each door model (3 states: 0=closed, 1=open1, 2=open2)
4. Door dimensions are set to fast defaults (2.0x3.0) to avoid expensive extraction

This door extraction path is implemented in the kit builder's door processing routine ([`kit.py` L1253-L1304](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1253-L1304)).

Doors are placed at component hook points and connect adjacent rooms. The [door templates](GFF-File-Format#utd-door) define appearance, locking, scripts, and other properties.

Door template semantics are documented in the UTD section of the GFF format documentation ([GFF UTD](GFF-File-Format#utd-door)).

### Door Walkmeshes ([DWK](Level-Layout-Formats#bwm))

Doors have 3 [walkmesh](Level-Layout-Formats#bwm) states that define pathfinding behavior:

- **State 0 (closed)**: `{door_model}0.dwk` - Door is closed, blocks pathfinding
- **State 1 (open1)**: `{door_model}1.dwk` - Door is open in first direction
- **State 2 (open2)**: `{door_model}2.dwk` - Door is open in second direction

**[DWK](Level-Layout-Formats#bwm) Extraction Process**:

1. Load `genericdoors.2da` to map [UTD](GFF-File-Format#utd-door) files to door [model](MDL-MDX-File-Format) names
2. For each door, resolve [model](MDL-MDX-File-Format) name from [UTD](GFF-File-Format#utd-door) using `door_tools.get_model()`
3. Batch lookup all [DWK](Level-Layout-Formats#bwm) files (3 states per door) using `installation.locations()`
4. Extract [DWK](Level-Layout-Formats#bwm) files from module first (fastest), then fall back to installation-wide resolution

This DWK lookup and extraction sequence is implemented in the door walkmesh path in the kit toolchain ([`kit.py` L1090-L1174](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1090-L1174)).

**Game Engine Reference (reone):** [`door.cpp` L80–L94](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/door.cpp#L80-L94) — attaches closed/open [DWK](Level-Layout-Formats#bwm) walkmeshes to the door model scene node

---

## Placeables

Placeables are interactive objects (containers, terminals, etc.) that can be placed in rooms. They are optional and may not be present in all kits.

**Placeable files**:

- `{placeable_model}.pwk`: Placeable [walkmesh](Level-Layout-Formats#bwm) for pathfinding

**Placeable Extraction Process**:

1. [UTP](GFF-File-Format#utp-placeable) files are extracted from module RIM/[ERF](Container-Formats#erf) archives
2. Placeable [model](MDL-MDX-File-Format) names are resolved from [UTP](GFF-File-Format#utp-placeable) files using `placeables.2da`
3. [PWK](Level-Layout-Formats#bwm) [walkmeshes](Level-Layout-Formats#bwm) are extracted for each placeable [model](MDL-MDX-File-Format)
4. [PWK](Level-Layout-Formats#bwm) files are written to kit directory root

This placeable extraction and PWK write flow is implemented in the corresponding kit extraction stage ([`kit.py` L1176-L1251](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1176-L1251)).

### Placeable Walkmeshes ([PWK](Level-Layout-Formats#bwm))

Placeables have [walkmeshes](Level-Layout-Formats#bwm) that define their collision boundaries for pathfinding.

**[PWK](Level-Layout-Formats#bwm) Extraction Process**:

1. Load `placeables.2da` to map [UTP](GFF-File-Format#utp-placeable) files to placeable [model](MDL-MDX-File-Format) names
2. For each placeable, resolve [model](MDL-MDX-File-Format) name from [UTP](GFF-File-Format#utp-placeable) using `placeable_tools.get_model()`
3. Batch lookup all [PWK](Level-Layout-Formats#bwm) files using `installation.locations()`
4. Extract [PWK](Level-Layout-Formats#bwm) files from module first (fastest), then fall back to installation-wide resolution

These PWK resolution rules are implemented in the same placeable walkmesh extraction routine ([`kit.py` L1176-L1251](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1176-L1251)).

**Game Engine Reference (reone):** [`placeable.cpp` L77–L80](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/placeable.cpp#L77-L80) — loads [PWK](Level-Layout-Formats#bwm) for the resolved placeable model (`ResType::Pwk`)

---

## Skyboxes

Skyboxes are optional [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format) [models](MDL-MDX-File-Format) used for outdoor area rendering. They are stored in the `skyboxes/` folder.

**Skybox Identification**: Skyboxes are identified as [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format) pairs that:

1. Are NOT listed as [room models](Level-Layout-Formats#room-definitions) in the [LYT file](Level-Layout-Formats#lyt)
2. Do NOT have corresponding [WOK files](Level-Layout-Formats#bwm)
3. Are found in the module's resource list

**Skybox files**:

- `{skybox_name}.mdl`: Skybox [model](MDL-MDX-File-Format) [geometry](MDL-MDX-File-Format#geometry-header)
- `{skybox_name}.mdx`: Skybox [material](MDL-MDX-File-Format#trimesh-header) data

Skyboxes are typically used for outdoor areas and provide the distant sky/background rendering. They are loaded separately from room components and don't have [walkmeshes](Level-Layout-Formats#bwm).

This skybox/component distinction is implemented by the model classification logic in the extraction pipeline ([`kit.py` L740-L744](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L740-L744)).

---

## Doorway Padding

The `doorway/` folder contains padding [models](MDL-MDX-File-Format) that fill gaps around doors:

**Padding files**:

- `side_{door_id}_size{size}.mdl`: Side padding for horizontal doors
- `top_{door_id}_size{size}.mdl`: Top padding for vertical doors
- Corresponding `.mdx` files

**Padding Purpose**: When doors are inserted into walls, gaps may appear. Padding [models](MDL-MDX-File-Format) fill these gaps to create seamless door transitions.

**Naming Convention**:

- `side_` or `top_`: Padding orientation
- `{door_id}`: Door identifier (matches door index in JSON, extracted using `get_nums()`)
- `size{size}`: Padding size in world units (e.g., `size650`, `size800`)

The doorway filename parsing and loader conventions are implemented in the indoor-kit loader's doorway section ([`indoorkit_loader.py` L127-L150](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/indoorkit/indoorkit_loader.py#L127-L150)).

---

## [models](MDL-MDX-File-Format) Directory

The `models/` directory contains additional [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format) [models](MDL-MDX-File-Format) that are referenced by the module but are not used as components or skyboxes. These are typically:

- **Decorative [models](MDL-MDX-File-Format)**: [models](MDL-MDX-File-Format) used for decoration or atmosphere
- **Non-[room models](Level-Layout-Formats#room-definitions)**: [models](MDL-MDX-File-Format) that don't have [walkmeshes](Level-Layout-Formats#bwm) and aren't room components
- **Referenced [models](MDL-MDX-File-Format)**: [models](MDL-MDX-File-Format) that are referenced by scripts or other systems

**[models](MDL-MDX-File-Format) Directory structure**:

```shell
models/
├── {model_name}.mdl
└── {model_name}.mdx
```

This extra-model export stage is handled by the kit extraction logic for non-component, non-skybox models ([`kit.py` L1311-L1324](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1311-L1324)).

---

## Resource Extraction

The kit extraction process (`extract_kit()`) extracts resources from module RIM or [ERF files](Container-Formats#erf) and generates a complete kit structure.

### Archive file Support

The extraction process supports multiple archive formats:

- **RIM files**: `.rim` (main module), `_s.rim` (supplementary data)
- **[ERF](Container-Formats#erf) files**: `.mod` (module override), `.erf` (generic [ERF](Container-Formats#erf)), `.hak` (hakpak), `.sav` (savegame)

**file Resolution Priority**:

1. `.mod` files take precedence over `.rim` files (as per KOTOR resolution order)
2. If extension is specified, use that format directly
3. If no extension, search for both RIM and [ERF files](Container-Formats#erf), prioritizing `.mod` files

This archive handling and precedence logic is implemented in the `extract_kit()` archive resolution flow ([`kit.py` L291-L550](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L291-L550)).

### Component Identification

Components are identified using the following process:

1. **Load Module [LYT files](Level-Layout-Formats#lyt)**: Parse [LYT file](Level-Layout-Formats#lyt) to get list of [room model](Level-Layout-Formats#room-definitions) names
2. **Batch Resource Resolution**: Batch lookup [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format)/[WOK](Level-Layout-Formats#bwm) for all [room models](Level-Layout-Formats#room-definitions) using `installation.locations()`
3. **Component Criteria**: A [model](MDL-MDX-File-Format) is a component if:
   - It's listed as a [room model](Level-Layout-Formats#room-definitions) in the [LYT file](Level-Layout-Formats#lyt)
   - It has both [MDL](MDL-MDX-File-Format) and [WOK files](Level-Layout-Formats#bwm)
   - It's not a skybox (skyboxes have [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format) but no [WOK](Level-Layout-Formats#bwm))
4. **Component Name Mapping**: Component IDs are mapped from [model](MDL-MDX-File-Format) names using `_get_component_name_mapping()` to create friendly names (e.g., `danm13_room01` → `room_01`)

This component-identification sequence is implemented in the model classification and mapping pass in the kit extraction code ([`kit.py` L600-L767](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L600-L767)).

### [texture](Texture-Formats#tpc) and Lightmap Extraction

[textures](Texture-Formats#tpc) and lightmaps are extracted using a comprehensive process:

1. **[model](MDL-MDX-File-Format) Scanning**: Scan all [MDL files](MDL-MDX-File-Format) from `module.models()` using `iterate_textures()` and `iterate_lightmaps()`
2. **Archive Scanning**: Also extract [TPC](Texture-Formats#tpc)/TGA files directly from RIM/[ERF](Container-Formats#erf) archives
3. **Module Resource Scanning**: Check `module.resources` for additional [textures](Texture-Formats#tpc)/lightmaps
4. **Batch Location Lookup**: Single `installation.locations()` call for all [textures](Texture-Formats#tpc)/lightmaps with search order:
   - OVERRIDE
   - MODULES (`.mod` files take precedence over `.rim` files)
   - TEXTURES_GUI
   - TEXTURES_TPA
   - CHITIN
5. **Priority Sorting**: Pre-sort all location results by priority once to avoid repeated sorting
6. **Batch I/O**: Group [TPC](Texture-Formats#tpc)/TGA files by filepath for batch reading operations
7. **TPC to TGA Conversion**: Convert all [TPC files](Texture-Formats#tpc) to TGA format during extraction
8. **TXI Extraction**: Extract [TXI files](Texture-Formats#txi) from embedded [TPC](Texture-Formats#tpc) data or standalone files

This full texture/lightmap extraction pipeline is implemented in the corresponding extraction stage in the kit tooling ([`kit.py` L769-L1020](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L769-L1020)).

### Door Extraction

Doors are extracted from module [UTD](GFF-File-Format#utd-door) files:

1. **UTD Extraction**: Extract all [UTD](GFF-File-Format#utd-door) files from module RIM/[ERF](Container-Formats#erf) archives
2. **Door [model](MDL-MDX-File-Format) Resolution**: Load `genericdoors.2da` once for all doors
3. **[model](MDL-MDX-File-Format) Name Resolution**: Resolve door [model](MDL-MDX-File-Format) names from [UTD](GFF-File-Format#utd-door) files using `door_tools.get_model()`
4. **[DWK](Level-Layout-Formats#bwm) Extraction**: Extract door walkmeshes (3 states per door) using batch lookup
5. **Door JSON Generation**: Generate door entries in kit JSON with fast defaults (2.0x3.0 dimensions)

This door extraction workflow and JSON emission are implemented in the door handling pass of the kit extractor ([`kit.py` L1253-L1304](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1253-L1304)).

### [walkmesh](Level-Layout-Formats#bwm) Extraction

[walkmeshes](Level-Layout-Formats#bwm) are extracted for components, doors, and placeables:

1. **Component [WOK](Level-Layout-Formats#bwm)**: Extracted from module or installation-wide resolution
2. **Door [DWK](Level-Layout-Formats#bwm)**: Extracted using batch lookup (3 states: 0, 1, 2)
3. **Placeable [PWK](Level-Layout-Formats#bwm)**: Extracted using batch lookup

These walkmesh extraction paths are implemented across the door/placeable/component extraction routines ([`kit.py` L1090-L1251](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1090-L1251)).

### [BWM](Level-Layout-Formats#bwm) Re-centering

Component [WOK files](Level-Layout-Formats#bwm) are **re-centered to origin (0, 0, 0)** before saving. This is critical for proper alignment in the Indoor Map Builder:

**Problem**: Without re-centering:

- Preview image is drawn centered at `room.position`
- [walkmesh](Level-Layout-Formats#bwm) is translated BY `room.position` from original coordinates
- If [BWM](Level-Layout-Formats#bwm) center is at (100, 200) and room.position = (0, 0):
  - Image would be centered at (0, 0)
  - [walkmesh](Level-Layout-Formats#bwm) would be centered at (100, 200) after translate
  - **MISMATCH**: Image and hitbox are in different places

**Solution**: After re-centering [BWM](Level-Layout-Formats#bwm) to (0, 0):

- Image is centered at `room.position`
- [walkmesh](Level-Layout-Formats#bwm) is centered at `room.position` after translate
- **MATCH**: Image and hitbox overlap perfectly

**Re-centering Process**:

1. Calculate [BWM](Level-Layout-Formats#bwm) bounding box (min/max X, Y, Z)
2. Calculate center point
3. Translate all [vertices](MDL-MDX-File-Format#vertex-structure) by negative center to move [BWM](Level-Layout-Formats#bwm) to origin
4. Save re-centered [WOK file](Level-Layout-Formats#bwm)

This recentering algorithm is implemented in the dedicated BWM translation helper in the kit tool ([`kit.py` L1538-L1588](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1538-L1588)).

### Minimap Generation

Component minimap images are generated from re-centered [BWM](Level-Layout-Formats#bwm) [walkmeshes](Level-Layout-Formats#bwm):

1. **Bounding Box Calculation**: Calculate [bounding box](MDL-MDX-File-Format#model-header) from [BWM](Level-Layout-Formats#bwm) [vertices](MDL-MDX-File-Format#vertex-structure)
2. **Image Dimensions**: scale to 10 pixels per world unit, minimum 256x256
3. **coordinate [transformation](Level-Layout-Formats#adjacencies-wok-only)**: Transform world coordinates to image coordinates (flip Y-axis)
4. **[face](MDL-MDX-File-Format#face-structure) Rendering**: Draw [walkable faces](Level-Layout-Formats#faces) in white, non-walkable in gray
5. **Image format**: PNG format, saved as `{component_id}.png`

**[walkable face](Level-Layout-Formats#faces) [materials](MDL-MDX-File-Format#trimesh-header)**: [faces](MDL-MDX-File-Format#face-structure) with [materials](MDL-MDX-File-Format#trimesh-header) 1, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 16, 18, 20, 21, 22 are considered walkable.

This minimap generation and walkable-material filtering logic is implemented in the component image rendering code ([`kit.py` L1348-L1465](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1348-L1465)).

### Doorhook Extraction

Door hooks are extracted from [BWM](Level-Layout-Formats#bwm) [edges](Level-Layout-Formats#edges-wok-only) that have valid transitions:

1. **[edge](Level-Layout-Formats#edges-wok-only) Processing**: Iterate through all [BWM](Level-Layout-Formats#bwm) [edges](Level-Layout-Formats#edges-wok-only)
2. **Transition Check**: Skip [edges](Level-Layout-Formats#edges-wok-only) without transitions (`edge.transition < 0`)
3. **Midpoint Calculation**: Calculate midpoint of [edge](Level-Layout-Formats#edges-wok-only) from [vertices](MDL-MDX-File-Format#vertex-structure)
4. **rotation Calculation**: Calculate rotation angle from [edge](Level-Layout-Formats#edges-wok-only) direction using `atan2(dy, dx)`
5. **Door index Mapping**: Map transition index to door index (clamped to valid range)
6. **Hook Generation**: Create doorhook entry with position, rotation, door index, and [edge](Level-Layout-Formats#edges-wok-only) index

**[edge](Level-Layout-Formats#edges-wok-only) index Calculation**: Global [edge](Level-Layout-Formats#edges-wok-only) index = `face_index * 3 + local_edge_index`

This hook extraction and edge-index mapping are implemented in the doorhook generation routine ([`kit.py` L1467-L1535](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1467-L1535)).

---

## Implementation Details

### Kit Class structure

The `Kit` class structure in memory:

```python
class Kit:
    name: str
    always: dict[Path, bytes]  # Static resources
    textures: CaseInsensitiveDict[bytes]  # Texture TGA data
    txis: CaseInsensitiveDict[bytes]  # TXI metadata (for textures and lightmaps)
    lightmaps: CaseInsensitiveDict[bytes]  # Lightmap TGA data
    skyboxes: CaseInsensitiveDict[MDLMDXTuple]  # Skybox models
    doors: list[KitDoor]  # Door definitions
    components: list[KitComponent]  # Room components
    side_padding: dict[int, dict[int, MDLMDXTuple]]  # Side padding by door_id and size
    top_padding: dict[int, dict[int, MDLMDXTuple]]  # Top padding by door_id and size

class KitComponent:
    kit: Kit
    name: str
    image: QImage  # Minimap image
    hooks: list[KitComponentHook]  # Door hook points
    bwm: BWM  # Walkmesh
    mdl: bytes  # Model geometry
    mdx: bytes  # Model extension

class KitComponentHook:
    position: Vector3  # Hook position
    rotation: float  # Rotation angle
    edge: str  # Edge identifier
    door: KitDoor  # Door reference

class KitDoor:
    utd_k1: UTD  # KotOR 1 door blueprint
    utd_k2: UTD  # KotOR 2 door blueprint
    width: float  # Door width
    height: float  # Door height
    utd: UTD  # Primary door blueprint alias (utd_k1)
```

  This in-memory data model is defined by Holocron Toolset's indoor-kit base classes ([`indoorkit_base.py`](https://github.com/OpenKotOR/HolocronToolset/src/toolset/data/indoorkit/indoorkit_base.py)).

### Kit Loading

Kits are loaded by `load_kits()` which:

1. **Scans Kits Directory**: Iterates through all `.json` files in the kits directory
2. **Validates JSON**: Skips invalid JSON files and non-dict structures
3. **Loads Kit Metadata**: Extracts `name` and `id` from JSON
4. **Loads Always Resources**: Loads all files from `always/` folder into `kit.always[filename]`
5. **Loads [textures](Texture-Formats#tpc)**: Loads TGA files from `textures/` folder, extracts [TXI files](Texture-Formats#txi)
6. **Loads Lightmaps**: Loads TGA files from `lightmaps/` folder, extracts [TXI files](Texture-Formats#txi)
7. **Loads Skyboxes**: Loads [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format) pairs from `skyboxes/` folder
8. **Loads Doorway Padding**: Parses padding filenames to extract door_id and size, loads [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format) pairs
9. **Loads Doors**: Loads [UTD](GFF-File-Format#utd-door) files for K1 and K2, creates `KitDoor` instances
10. **Loads Components**: Loads [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format)/[WOK files](Level-Layout-Formats#bwm) and PNG minimap images, creates `KitComponent` instances
11. **Populates Hooks**: Extracts doorhook data from JSON and creates `KitComponentHook` instances
12. **Error Handling**: Collects missing files instead of failing fast, returns list of missing files

This end-to-end load flow is implemented in the kit loader entry point and helper routines ([`indoorkit_loader.py` L23-L260](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/indoorkit/indoorkit_loader.py#L23-L260)).

### Indoor Map Generation

When generating an indoor map from kits:

1. **Component Placement**: Components are placed at specified positions with rotations/flips
2. **Hook Connection**: Hook points are matched to connect adjacent rooms
3. **[model](MDL-MDX-File-Format) [transformation](Level-Layout-Formats#adjacencies-wok-only)**: [models](MDL-MDX-File-Format) are flipped, rotated, and transformed based on room properties
4. **[texture](Texture-Formats#tpc)/Lightmap Renaming**: [textures](Texture-Formats#tpc) and lightmaps are renamed to module-specific names
5. **[walkmesh](Level-Layout-Formats#bwm) Merging**: Room [walkmeshes](Level-Layout-Formats#bwm) are combined into a single area [walkmesh](Level-Layout-Formats#bwm)
6. **Door Insertion**: Doors are inserted at hook points with appropriate padding
7. **Resource Generation**: are, [GIT](GFF-File-Format#git-game-instance-template), [LYT](Level-Layout-Formats#lyt), [VIS](Level-Layout-Formats#vis), [IFO](GFF-File-Format#ifo-module-info) files are generated
8. **Minimap Generation**: Minimap images are generated from component PNGs
9. **Static Resources**: Always resources are added to every room via `add_static_resources()`

This generation pipeline is implemented in the indoor map builder's assembly and serialization flow ([`indoormap.py`](https://github.com/OpenKotOR/HolocronToolset/src/toolset/data/indoormap.py)).

### coordinate System

- **World coordinates**: Meters in left-handed coordinate system (X=right, Y=forward, Z=up)
- **Hook positions**: World-space coordinates relative to component origin (after re-centering to 0,0,0)
- **rotations**: Degrees (0-360), counterclockwise from positive X-axis
- **Transforms**: Components can be flipped on X/Y axes and rotated around Z-axis
- **[BWM](Level-Layout-Formats#bwm) coordinates**: Re-centered to origin (0, 0, 0) for proper alignment in Indoor Map Builder

These coordinate and transform conventions are consistent with the room/walkmesh definitions described in the [BWM section](Level-Layout-Formats#bwm) and [LYT format notes](Level-Layout-Formats#lyt).

---

## Kit types

### Component-Based Kits

Kits with `components` array (e.g., `enclavesurface`, `endarspire`):

- Contain reusable [room models](Level-Layout-Formats#room-definitions) with [walkmeshes](Level-Layout-Formats#bwm)
- Have hook points for connecting rooms
- Include [textures](Texture-Formats#tpc)/lightmaps referenced by components
- Generate complete indoor maps with room layouts
- Include minimap images for component selection

### [texture](Texture-Formats#tpc)-Only Kits

Kits with empty `components` array (e.g., `jedienclave`):

- Contain only [textures](Texture-Formats#tpc) and lightmaps
- May include shared resources from multiple modules
- Used for [texture](Texture-Formats#tpc) packs or shared resource collections
- Don't generate room layouts (no components to place)
- Useful for [texture](Texture-Formats#tpc) libraries or resource packs

---

## Game Engine Compatibility

Kits are designed to be compatible with the KOTOR game engine's resource resolution and module structure:

**Resource Resolution**: Kits use the same resource resolution priority as the game engine:

1. OVERRIDE (user mods)
2. MODULES (`.mod` files take precedence over `.rim` files)
3. TEXTURES_GUI
4. TEXTURES_TPA
5. CHITIN (base game)

**Module structure**: Generated modules follow the same structure as game modules:

- are files for area definitions
- [GIT files](GFF-File-Format#git-game-instance-template) for instance data
- [LYT files](Level-Layout-Formats#lyt) for room layouts
- [VIS files](Level-Layout-Formats#vis) for visibility data
- [IFO](GFF-File-Format#ifo-module-info) files for module information

**file formats**: All kit resources use native game formats:

- [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format) for 3D [models](MDL-MDX-File-Format)
- [WOK](Level-Layout-Formats#bwm)/[BWM](Level-Layout-Formats#bwm) for [walkmeshes](Level-Layout-Formats#bwm)
- TGA for textures (converted from [TPC](Texture-Formats#tpc) during extraction)
- [TXI](Texture-Formats#txi) for [texture](Texture-Formats#tpc) metadata
- [UTD](GFF-File-Format#utd-door) for door blueprints
- [DWK](Level-Layout-Formats#bwm)/[PWK](Level-Layout-Formats#bwm) for [walkmeshes](Level-Layout-Formats#bwm)

The shared resource-priority and format assumptions are implemented in the kit priority helpers ([`kit.py` L74-L120](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L74-L120)).

---

## Cross-reference: engine implementations

The kit extraction process is aligned with open-source engine code ([reone](https://github.com/seedhartha/reone), [KotOR.js](https://github.com/KobaltBlu/KotOR.js)) and PyKotor’s kit tools. This section compares how those codebases handle the same operations and notes discrepancies.

### Door Walkmesh ([DWK](Level-Layout-Formats#bwm)) Extraction

**reone** ([`door.cpp` L80–L98](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/door.cpp#L80-L98)):

- Doors load 3 [walkmesh](Level-Layout-Formats#bwm) states: `{modelName}0.dwk` (closed), `{modelName}1.dwk` (open1), `{modelName}2.dwk` (open2)
- [walkmeshes](Level-Layout-Formats#bwm) are loaded via `_services.resource.walkmeshes.get(modelName + "0", ResType::Dwk)`
- Each [walkmesh](Level-Layout-Formats#bwm) state is stored as a separate `WalkmeshSceneNode` with enabled/disabled state based on door state
- **PyKotor Implementation**: Matches reone exactly - extracts all 3 [DWK](Level-Layout-Formats#bwm) states using the same naming convention

**KotOR.js** ([`ModuleDoor.ts` L990–L1003](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleDoor.ts#L990-L1003)):

- Only loads the closed state [walkmesh](Level-Layout-Formats#bwm): `ResourceLoader.loadResource(ResourceTypes['dwk'], resRef+'0')`
- Open states are handled dynamically through collision state updates, not separate [walkmesh](Level-Layout-Formats#bwm) files
- **Discrepancy**: KotOR.js only loads `{modelName}0.dwk`, while reone and PyKotor extract all 3 states
- **PyKotor Implementation**: Extracts all 3 states to match reone's comprehensive approach

The PyKotor DWK extraction behavior described above is implemented in the dedicated door walkmesh extraction path ([`kit.py` L1090-L1174](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1090-L1174)).

### Placeable Walkmesh ([PWK](Level-Layout-Formats#bwm)) Extraction

**reone** ([`placeable.cpp` L77–L80](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/placeable.cpp#L77-L80)):

- Placeables load a single [walkmesh](Level-Layout-Formats#bwm): `_services.resource.walkmeshes.get(modelName, ResType::Pwk)`
- [walkmesh](Level-Layout-Formats#bwm) is stored as a `WalkmeshSceneNode` attached to the placeable's scene [node](MDL-MDX-File-Format#node-structures)
- **PyKotor Implementation**: Matches reone exactly - extracts [PWK](Level-Layout-Formats#bwm) using [model](MDL-MDX-File-Format) name directly

**KotOR.js** ([`ModulePlaceable.ts` `loadWalkmesh` L665–L682](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModulePlaceable.ts#L665-L682)):

- Loads [walkmesh](Level-Layout-Formats#bwm): `ResourceLoader.loadResource(ResourceTypes['pwk'], resRef)`
- Creates `OdysseyWalkMesh` from binary data and attaches to [model](MDL-MDX-File-Format)
- Falls back to empty [walkmesh](Level-Layout-Formats#bwm) if loading fails
- **PyKotor Implementation**: Matches KotOR.js approach - extracts [PWK](Level-Layout-Formats#bwm) using [model](MDL-MDX-File-Format) name

The PyKotor PWK extraction behavior described above is implemented in the placeable walkmesh extraction path ([`kit.py` L1176-L1251](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1176-L1251)).

### [room model](Level-Layout-Formats#room-definitions) and Component Identification

**reone** ([`area.cpp` L305–L375](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/area.cpp#L305-L375)):

- Loads [LYT file](Level-Layout-Formats#lyt) via `_services.resource.layouts.get(_name)`
- Iterates through `layout->rooms` to get [room model](Level-Layout-Formats#room-definitions) names
- For each room, loads [MDL](MDL-MDX-File-Format) [model](MDL-MDX-File-Format): `_services.resource.models.get(lytRoom.name)`
- Loads [WOK](Level-Layout-Formats#bwm) [walkmesh](Level-Layout-Formats#bwm): `_services.resource.[walkmeshes](Level-Layout-Formats#bwm).get(lytRoom.name, ResType::Wok)`
- Rooms are identified as [MDL](MDL-MDX-File-Format) [models](MDL-MDX-File-Format) with corresponding [WOK files](Level-Layout-Formats#bwm) from [LYT](Level-Layout-Formats#lyt)
- **PyKotor Implementation**: Matches reone exactly - uses [LYT](Level-Layout-Formats#lyt) to identify [room models](Level-Layout-Formats#room-definitions), then resolves [MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format)/[WOK](Level-Layout-Formats#bwm)

**KotOR.js** ([`ModuleRoom.ts` L338–L342](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleRoom.ts#L338-L342); [`loadWalkmesh` L360–L367](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleRoom.ts#L360-L367)):

- Loads [walkmesh](Level-Layout-Formats#bwm): `ResourceLoader.loadResource(ResourceTypes['wok'], resRef)`
- Creates `OdysseyWalkMesh` from binary data and attaches to [room model](Level-Layout-Formats#room-definitions)
- Rooms are identified from [LYT file](Level-Layout-Formats#lyt) room definitions
- **PyKotor Implementation**: Matches KotOR.js approach - uses [LYT](Level-Layout-Formats#lyt) [room models](Level-Layout-Formats#room-definitions) to identify components

The corresponding PyKotor room/component detection logic is implemented in the component identification path ([`kit.py` L545-L767](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L545-L767)).

### Door [model](MDL-MDX-File-Format) Resolution

**reone** ([`door.cpp` `loadFromBlueprint` L59+](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/door.cpp#L59)):

- Door [models](MDL-MDX-File-Format) are resolved from [UTD](GFF-File-Format#utd-door) files using `genericdoors.2da`
- The `appearance_id` field in [UTD](GFF-File-Format#utd-door) maps to a row in `genericdoors.2da`
- The `modelname` column in that row provides the door [model](MDL-MDX-File-Format) name
- **PyKotor Implementation**: Matches reone exactly - uses `door_tools.get_model()` which reads `genericdoors.2da`

**KotOR.js** ([`ModuleDoor.ts` L1062–L1063](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleDoor.ts#L1062-L1063) — `GenericType` from [UTD](GFF-File-Format#utd-door); see also [`getGenericType` / appearance](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleDoor.ts#L224-L237)):

- Door [models](MDL-MDX-File-Format) are resolved similarly using `[genericdoors.2da](2DA-File-Format#genericdoors2da)`
- The appearance ID from [UTD](GFF-File-Format#utd-door) is used to lookup [model](MDL-MDX-File-Format) name
- **PyKotor Implementation**: Matches KotOR.js approach

PyKotor's door model-resolution helper is implemented in the door utility module ([`door.py` L25-L64](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/door.py#L25-L64)).

### Placeable [model](MDL-MDX-File-Format) Resolution

**reone** ([`placeable.cpp` `loadFromBlueprint` L50+](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/placeable.cpp#L50)):

- Placeable [models](MDL-MDX-File-Format) are resolved from [UTP](GFF-File-Format#utp-placeable) files using `placeables.2da`
- The `appearance_id` field in [UTP](GFF-File-Format#utp-placeable) maps to a row in `placeables.2da`
- The `modelname` column in that row provides the placeable [model](MDL-MDX-File-Format) name
- **PyKotor Implementation**: Matches reone exactly - uses `placeable_tools.get_model()` which reads `placeables.2da`

**KotOR.js** ([`ModulePlaceable.ts` L729–L732](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModulePlaceable.ts#L729-L732) — `Appearance` → `placeableAppearance`; [L575](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModulePlaceable.ts#L575) — `modelname`):

- Placeable [models](MDL-MDX-File-Format) are resolved similarly using `placeables.2da`
- The appearance ID from [UTP](GFF-File-Format#utp-placeable) is used to lookup [model](MDL-MDX-File-Format) name
- **PyKotor Implementation**: Matches KotOR.js approach

PyKotor's placeable model-resolution helper is implemented in the placeable utility module ([`placeable.py` L20-L50](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/placeable.py#L20-L50)).

### [texture](Texture-Formats#tpc) and Lightmap Extraction

**PyKotor Implementation** (`Libraries/PyKotor/src/pykotor/tools/model.py`):

- Uses `iterate_textures()` and `iterate_lightmaps()` to extract [texture](Texture-Formats#tpc)/lightmap references from [MDL files](MDL-MDX-File-Format)
- Scans all [MDL](MDL-MDX-File-Format) nodes ([mesh](MDL-MDX-File-Format#trimesh-header), skin, emitter) for [texture](Texture-Formats#tpc) references
- Lightmaps are identified by naming patterns (`_lm` suffix or `l_` prefix)
- **Vendor Comparison**: No direct equivalent in reone/KotOR.js - they load [textures](Texture-Formats#tpc) on-demand during rendering
- **Discrepancy**: PyKotor proactively extracts all [textures](Texture-Formats#tpc)/lightmaps, while engines load them lazily during rendering
- **Rationale**: Kit extraction needs all [textures](Texture-Formats#tpc) upfront for self-contained kit structure

This texture/lightmap reference scanning behavior is implemented in the model utility iterators ([`model.py` L99-L887](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/model.py#L99-L887)).

### Resource Resolution Priority

**reone** ([`src/libs/resource/provider/`](https://github.com/seedhartha/reone/tree/master/src/libs/resource/provider)):

- Resource resolution follows KOTOR priority: Override → Modules → Chitin
- `.mod` files take precedence over `.rim` files in Modules directory
- **PyKotor Implementation**: Matches reone exactly - uses same priority order via `_get_resource_priority()`

**KotOR.js** ([`ResourceLoader.ts` L22+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/loaders/ResourceLoader.ts#L22)):

- Resource resolution follows similar priority order
- Override folder checked first, then modules, then chitin
- **PyKotor Implementation**: Matches KotOR.js approach

PyKotor's implementation of this resource-priority behavior is defined in its kit resource-priority helpers ([`kit.py` L74-L120](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L74-L120)).

### [BWM](Level-Layout-Formats#bwm)/[WOK](Level-Layout-Formats#bwm) [walkmesh](Level-Layout-Formats#bwm) Handling

**reone** ([`walkmesh.cpp` L1+](https://github.com/seedhartha/reone/blob/master/src/libs/graphics/walkmesh.cpp#L1)):

- [walkmeshes](Level-Layout-Formats#bwm) are loaded from [WOK](Level-Layout-Formats#bwm)/[BWM files](Level-Layout-Formats#bwm)
- [face](MDL-MDX-File-Format#face-structure) [materials](MDL-MDX-File-Format#trimesh-header) determine walkability ([materials](MDL-MDX-File-Format#trimesh-header) 1, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 16, 18, 20, 21, 22 are walkable)
- [edge](Level-Layout-Formats#edges-wok-only) transitions indicate door connections
- **PyKotor Implementation**: Matches reone - uses same walkable [material](MDL-MDX-File-Format#trimesh-header) values for minimap generation

**KotOR.js** ([`OdysseyWalkMesh.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/odyssey/OdysseyWalkMesh.ts#L24)):

- [walkmeshes](Level-Layout-Formats#bwm) are loaded from [WOK](Level-Layout-Formats#bwm) binary data
- [face](MDL-MDX-File-Format#face-structure) [materials](MDL-MDX-File-Format#trimesh-header) and walk types determine walkability
- [edge](Level-Layout-Formats#edges-wok-only) transitions are stored in [walkmesh](Level-Layout-Formats#bwm) structure
- **PyKotor Implementation**: Matches KotOR.js - extracts doorhooks from [BWM](Level-Layout-Formats#bwm) [edges](Level-Layout-Formats#edges-wok-only) with transitions

PyKotor's corresponding minimap and doorhook logic is implemented in the relevant extraction helpers ([`kit.py` L1348-L1465](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1348-L1465), [`kit.py` L1467-L1535](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L1467-L1535)).

### [module archives](Container-Formats#erf) Loading

**reone** ([`src/libs/resource/provider/`](https://github.com/seedhartha/reone/tree/master/src/libs/resource/provider)):

- Supports RIM and [ERF file](Container-Formats#erf) formats
- `.mod` files ([ERF](Container-Formats#erf) format) take precedence over `.rim` files
- **PyKotor Implementation**: Matches reone exactly - prioritizes `.mod` files over `.rim` files

**KotOR.js** ([`ResourceLoader.ts` L22+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/loaders/ResourceLoader.ts#L22)):

- Supports RIM and [ERF file](Container-Formats#erf) formats
- Module loading follows same priority order
- **PyKotor Implementation**: Matches KotOR.js approach

PyKotor's module-archive loading implementation for this flow is in the extraction archive resolution code ([`kit.py` L291-L550](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/tools/kit.py#L291-L550)).

### Key Discrepancies and Rationale

1. **[DWK](Level-Layout-Formats#bwm) Extraction**:
   - **KotOR.js**: Only extracts closed state (`{modelName}0.dwk`)
   - **reone/PyKotor**: Extracts all 3 states (closed, open1, open2)
   - **Rationale**: PyKotor matches reone for comprehensive kit extraction

2. **[texture](Texture-Formats#tpc) Extraction**:
   - **Vendor Engines**: Load [textures](Texture-Formats#tpc) lazily during rendering
   - **PyKotor**: Proactively extracts all [textures](Texture-Formats#tpc)/lightmaps upfront
   - **Rationale**: Kits need self-contained resource collections, not lazy loading

3. **[BWM](Level-Layout-Formats#bwm) Re-centering**:
   - **Vendor Engines**: Use BWMs in world coordinates as-is
   - **PyKotor**: Re-centers BWMs to origin (0, 0, 0)
   - **Rationale**: Indoor Map Builder requires centered BWMs for proper image/[walkmesh](Level-Layout-Formats#bwm) alignment

4. **Component Name Mapping**:
   - **Vendor Engines**: Use [model](MDL-MDX-File-Format) names directly (e.g., `m09aa_01a`)
   - **PyKotor**: Maps to friendly names (e.g., `hall_1`) for better UX
   - **Rationale**: Kit components need human-readable identifiers for toolset UI

---

## Test Comparison Precision

The kit generation tests (`Tools/HolocronToolset/tests/data/test_kit_generation.py`) use different comparison strategies depending on the data type:

### Exact Matching (1:1 [byte](GFF-File-Format#gff-data-types)-for-[byte](GFF-File-Format#gff-data-types))

**Binary files** (SHA256 hash comparison):

- **[MDL](MDL-MDX-File-Format)/[MDX](MDL-MDX-File-Format)**: [model](MDL-MDX-File-Format) [geometry](MDL-MDX-File-Format#geometry-header) and [animations](MDL-MDX-File-Format#animation-header) - must be [byte](GFF-File-Format#gff-data-types)-for-[byte](GFF-File-Format#gff-data-types) identical
- **[WOK](Level-Layout-Formats#bwm)/[BWM](Level-Layout-Formats#bwm)**: [walkmesh](Level-Layout-Formats#bwm) data - must be [byte](GFF-File-Format#gff-data-types)-for-[byte](GFF-File-Format#gff-data-types) identical
- **[DWK](Level-Layout-Formats#bwm)/[PWK](Level-Layout-Formats#bwm)**: Door and placeable [walkmeshes](Level-Layout-Formats#bwm) - must be [byte](GFF-File-Format#gff-data-types)-for-[byte](GFF-File-Format#gff-data-types) identical
- **PNG**: Minimap images - must be [byte](GFF-File-Format#gff-data-types)-for-[byte](GFF-File-Format#gff-data-types) identical
- **[UTD](GFF-File-Format#utd-door)**: Door blueprints - must be [byte](GFF-File-Format#gff-data-types)-for-[byte](GFF-File-Format#gff-data-types) identical
- **[TXI](Texture-Formats#txi)**: [texture](Texture-Formats#tpc) metadata files - must be [byte](GFF-File-Format#gff-data-types)-for-[byte](GFF-File-Format#gff-data-types) identical

**Rationale**: These files contain critical game data that must match exactly for functional compatibility.

This exact-match behavior is asserted in the binary/hash comparison block of the kit generation tests ([`test_kit_generation.py` L912-L970](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/tests/data/test_kit_generation.py#L912-L970)).

### Approximate Matching (Tolerance-Based)

**Image files** (TGA/[TPC](Texture-Formats#tpc) - pixel-by-pixel comparison):

- **Dimensions**: Must match exactly (width × height)
- **Pixel data**: Allows tolerance for compression artifacts:
  - Up to **2 levels difference** per channel (R, G, B, A) per pixel
  - Up to **1% of pixels** can differ by more than 2 levels
  - Accounts for DXT compression artifacts in [TPC files](Texture-Formats#tpc)

**Rationale**: [TPC files](Texture-Formats#tpc) use DXT compression which can introduce small pixel differences even for identical source images.

This tolerance-based image comparison is implemented in the image assertion block of the same test module ([`test_kit_generation.py` L972-L1111](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/tests/data/test_kit_generation.py#L972-L1111)).

### structure-Only Verification (No value Comparison)

**JSON Metadata** (structure verification only):

- **Doorhook coordinates**: Only verifies that `x`, `y`, `z`, `rotation` fields exist - **does NOT compare actual values**
- **Door Dimensions**: Only verifies that `width`, `height` fields exist - **does NOT compare actual values**
- **Doorhook count**: Verifies count matches exactly
- **Component count**: Verifies count matches exactly
- **Door count**: Verifies count matches exactly
- **field Presence**: Verifies required fields exist (name, id, door, [edge](Level-Layout-Formats#edges-wok-only))

**Current Test Behavior**:

```python
# Lines 1229-1234: Only checks field existence, not values
self.assertIn("x", gen_hook, f"Component {i} hook {j} missing x")
self.assertIn("y", gen_hook, f"Component {i} hook {j} missing y")
self.assertIn("z", gen_hook, f"Component {i} hook {j} missing z")
self.assertIn("rotation", gen_hook, f"Component {i} hook {j} missing rotation")
# NO assertEqual or assertAlmostEqual for coordinate values!

# Lines 1182-1185: Only checks field existence, not values
if "width" in exp_door:
    self.assertIn("width", gen_door, f"Door {i} missing width")
if "height" in exp_door:
    self.assertIn("height", gen_door, f"Door {i} missing height")
# NO assertEqual or assertAlmostEqual for dimension values!
```

**Rationale**: Tests were designed to be lenient during initial development when doorhook extraction and door dimension calculation were incomplete. The comment on line 1114 states: "handling differences in components/doorhooks that may not be fully extracted yet."

**Implications**:

- **Doorhook coordinates are NOT validated** - tests will pass even if coordinates are completely wrong
- **Door dimensions are NOT validated** - tests will pass even if dimensions are incorrect
- **High granularity matching is NOT enforced** - coordinate precision is not verified
- **Error acceptability is currently 100%** - any coordinate values are accepted as long as fields exist

This structure-only behavior is visible in the later hook/door assertions that check field presence but do not compare values ([`test_kit_generation.py` L1113-L1234](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/tests/data/test_kit_generation.py#L1113-L1234)).

### Recommended Test Improvements

To achieve high granularity coordinate matching, the tests should be enhanced to:

1. **Compare Doorhook coordinates**:

   ```python
   # Use assertAlmostEqual with appropriate tolerance for floating-point comparison
   self.assertAlmostEqual(gen_hook.get("x"), exp_hook.get("x"), places=6, 
                          msg=f"Component {i} hook {j} x coordinate differs")
   self.assertAlmostEqual(gen_hook.get("y"), exp_hook.get("y"), places=6,
                          msg=f"Component {i} hook {j} y coordinate differs")
   self.assertAlmostEqual(gen_hook.get("z"), exp_hook.get("z"), places=6,
                          msg=f"Component {i} hook {j} z coordinate differs")
   self.assertAlmostEqual(gen_hook.get("rotation"), exp_hook.get("rotation"), places=2,
                          msg=f"Component {i} hook {j} rotation differs")
   ```

2. **Compare Door Dimensions**:

   ```python
   # Use assertAlmostEqual with appropriate tolerance
   if "width" in exp_door:
       self.assertAlmostEqual(gen_door.get("width"), exp_door.get("width"), places=2,
                              msg=f"Door {i} width differs")
   if "height" in exp_door:
       self.assertAlmostEqual(gen_door.get("height"), exp_door.get("height"), places=2,
                              msg=f"Door {i} height differs")
   ```

3. **Tolerance Levels**:
   - **Coordinates (x, y, z)**: 6 decimal places (0.000001 units) - matches Python float precision
   - **rotation**: 2 decimal places (0.01 degrees) - sufficient for door placement
   - **Dimensions (width, height)**: 2 decimal places (0.01 units) - sufficient for door sizing

**Current Status**: Tests are **NOT** performing 1:1 coordinate matching. They only verify structure, not values. This means tests can pass even if coordinates are incorrect, which may [mask](GFF-File-Format#gff-data-types) extraction bugs.

---

## Best Practices

1. **Component Naming**: Use descriptive, consistent naming (e.g., `hall_1`, `junction_2`)
2. **[texture](Texture-Formats#tpc) Organization**: Group related [textures](Texture-Formats#tpc) logically
3. **Always Folder**: Use sparingly for truly shared resources
4. **Door Definitions**: Ensure door [UTD](GFF-File-Format#utd-door) files match JSON definitions
5. **Hook Placement**: Place hooks at logical connection points (extracted from [BWM](Level-Layout-Formats#bwm) [edges](Level-Layout-Formats#edges-wok-only) with transitions)
6. **Minimap Images**: Generate accurate top-down views for component selection
7. **[BWM](Level-Layout-Formats#bwm) Re-centering**: Always re-center BWMs to origin for proper alignment
8. **Resource Resolution**: Respect game engine resource resolution priority
9. **Batch Processing**: Use batch I/O operations for performance
10. **Error Handling**: Collect missing files instead of failing fast
11. **Vendor Compatibility**: Follow reone/KotOR.js patterns for [walkmesh](Level-Layout-Formats#bwm) and [model](MDL-MDX-File-Format) handling
12. **Comprehensive Extraction**: Extract all [DWK](Level-Layout-Formats#bwm) states and all referenced [textures](Texture-Formats#tpc) for complete kits
13. **Test Precision**: Consider enhancing tests to verify coordinate values, not just structure

---

### See also

- [Indoor Map Builder User Guide](Indoor-Map-Builder-User-Guide) -- End-user guide for building indoor areas
- [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide) -- Code-level implementation details
- [Indoor Area Room Layout and Walkmesh Guide](Indoor-Area-Room-Layout-and-Walkmesh-Guide) -- LYT, VIS, BWM workflow
- [Level Layout Formats](Level-Layout-Formats) -- LYT, VIS, BWM binary format reference
- [Holocron Toolset Map Builder](Holocron-Toolset-Map-Builder) -- Map Builder tool documentation
- [Texture Formats](Texture-Formats) -- TPC, TGA, DDS texture handling

