# Blender Integration

Holocron Toolset uses Blender with the **kotorblender** add-on (canonical **[OpenKotOR/kotorblender](https://github.com/OpenKotOR/kotorblender)**; **th3w1zard1** hosts a mirror) for 3D model import/export.

- Upstream (OpenKotOR/kotorblender): <https://github.com/OpenKotOR/kotorblender/tree/404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4>
- Mirror (th3w1zard1/kotorblender): <https://github.com/th3w1zard1/kotorblender/tree/afae04c9172f30ab765891315d9d11224ab57426>

## Goals

The Blender integration exists to give Toolset users a second editing path for 3D-heavy workflows:

- Inspect and Edit **LYT Room Layouts**
- Inspect and Edit **GIT Instances** (Creatures, Placeables, Doors, Waypoints, etc.)
- Preview real *room*/walkmesh geometry in *Blender* instead of relying entirely on the built-in Python viewport
- Bring in external royalty-free assets through *Blender’s* native importers before converting/exporting them into *KotOR*-compatible resources

## Supported Blender / Add-On Versions

- **Recommended Blender version:** `4.2 LTS`
- **Other upstream-supported versions:** `3.6`, `5.0`
- **Upstream add-on:** `kotorblender 4.0.4`

## How the Toolset Integration Works

The Toolset no longer assumes a bundled vendor checkout of `kotorblender`.

Instead it now supports the following source discovery order:

1. A custom `io_scene_kotor` source path from the `KOTORBLENDER_SOURCE_PATH` environment variable
2. A local checkout of [kotorblender](https://github.com/OpenKotOR/kotorblender) (for example `io_scene_kotor/` at repo root)
3. An adjacent checkout such as `kotorblender/io_scene_kotor`
4. An auto-downloaded cache of the upstream [kotorblender](https://github.com/OpenKotOR/kotorblender) GitHub repository (same upstream / mirror permalinks as in the intro above).

When the Toolset installs the add-on, it also injects a **Holocron IPC overlay** into the installed
`io_scene_kotor` package. This overlay hosts the Toolset’s JSON-RPC bridge inside *Blender* without
requiring Blender to import the Toolset’s full Python environment directly.

## What the Live Bridge Currently Supports

The Toolset <--> Blender bridge supports:

- Blender process launch and add-on enablement
- JSON-RPC ping/version negotiation
- loading a Toolset session into Blender
- creating/removing/updating GIT instances
- room / door hook / track / obstacle sync
- selection synchronization
- transform synchronization
- save/export of updated LYT + GIT state back through the bridge
- background-mode smoke testing for the bridge runtime

## External Asset Import Pipeline

While *Blender* mode is active, dropping supported external files onto the Toolset’s 3D renderer will
forward them into the active Blender session.

### Supported External Imports

#### 3D Asset Formats

- `.obj`
- `.fbx`
- `.gltf`
- `.glb`
- `.dae`

#### Texture/Image Formats

- `.png`
- `.jpg`
- `.jpeg`
- `.tga`
- `.tif`
- `.tiff`
- `.bmp`
- `.webp`

### Important Note

The current Toolset integration handles **import into *Blender***. Converting the edited result into *KotOR* runtime resources still relies on the normal `kotorblender` export flow (for example `kb.mdlexport`) plus *PyKotor* packaging/conversion steps for textures and module resources.

In other words:

- **Drag/Drop into Blender:** supported
- **Edit in Blender with Toolset session active:** supported
- **Export imported meshes back out as *KotOR* MDL/MDX:** supported through the live bridge for minimal trimesh-style exports
- **Full packaging back into modules/kits:** still uses the standard `kotorblender` exporters plus *PyKotor* packaging/conversion steps

### Minimal Model Export Support

The bridge can now take an imported mesh object (for example from `.obj`) and wrap it in a minimal
*KotOR* model root so it can be exported as:

- `.mdl`
- `.mdx`

This path is intended for simple trimesh-style content and automated validation, not as a substitute
for all manual authoring features inside *Blender*.

## Walkmesh Generation Behavior

The Toolset’s procedural walkmesh generation path was upgraded so that it now prefers **real *room*
walkmesh *templates*** whenever they are available.

### Current Behavior

When generating a *layout* walkmesh:

1. The Toolset looks for matching `WOK` resources by *room* model name
2. If a template exists, it deep-copies that walkmesh and **re-anchors** it at the requested *room* position
3. If no template exists, the Toolset falls back to the older placeholder floor quad

This means the "procedural" path now preserves:

- Real *face* materials
- Real *room* extents
- Real per-*face* transition metadata

instead of always synthesizing a generic square floor.

## Testing

### Toolset Unit Tests

```bash
QT_QPA_PLATFORM=offscreen uv run pytest --import-mode=importlib \
  Tools/HolocronToolset/tests/blender/test_blender_integration.py -q
```

### Live Bridge Runtime Smoke Tests

Set `BLENDER_BIN` to a usable *Blender* executable and run:

```bash
QT_QPA_PLATFORM=offscreen BLENDER_BIN="/path/to/blender" uv run pytest --import-mode=importlib \
  Tools/HolocronToolset/tests/blender/test_blender_runtime_bridge.py -q
```

These runtime tests validate:

- Bridge Launch
- Ping/Version handshake
- Module/session roundtrip
- External `.obj` import into *Blender*

### Walkmesh Renderer Tests

```bash
QT_QPA_PLATFORM=offscreen uv run pytest --import-mode=importlib \
  Tools/HolocronToolset/tests/gui/widgets/test_walkmesh_renderer.py -q
```

## Current Limitations

- **Room-to-room transition (roomlink) authoring** is not fully supported or tested in KOTORBlender; vertex painting and mesh alignment alone do not set perimeter transition IDs. For **finalizing room crossing** (reassigning roomlinks after layout changes), use a workflow that supports roomlink/transition editing (e.g. [Indoor Map Builder](Indoor-Map-Builder-User-Guide) or community tools such as KOTORMax). For more information, see [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions).
- The bridge is focused on the **Toolset editing session**, not on replacing every *Blender*-native workflow.
- External asset import is supported, but end-to-end "import arbitrary asset --> automatically ship as final *KotOR*-compatible resource" is still a guided pipeline rather than a one-click conversion path.
- Engine-level documentation updates that require direct *K1* + *TSL* binary analysis were **not** added here, because those binaries were not available in the current environment during this work.

### See also

- [Indoor Map Builder User Guide](Indoor-Map-Builder-User-Guide) -- User workflow for Indoor Maps
- [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide) -- Implementation Details
- [BWM File Format](Level-Layout-Formats#bwm) -- Walkmesh Format
- [MDL/MDX File Format](MDL-MDX-File-Format) -- Model Format
- [LYT-File-Format](Level-Layout-Formats#lyt) -- Room Layout
- [GFF-GIT](GFF-Module-and-Area#git) -- Instance Data
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, forums for *MDL/LYT* workflows and *kotorblender*
