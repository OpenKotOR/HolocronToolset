# Indoor Map Builder — Implementation Guide

The Indoor Map Builder emits a complete module from a visual room layout: LYT, VIS, ARE, GIT, IFO, walkmeshes, and a MOD/RIM capsule. The sections below cover what files it produces, how they relate to engine formats, and where to read the code. For end-user workflow, see the [Indoor Map Builder User Guide](Indoor-Map-Builder-User-Guide).

## Outputs and formats

A typical build produces module resources consistent with engine expectations:

- **[LYT](Level-Layout-Formats#lyt)** — Room list, transforms, and door hooks; room **index** matches **walkmesh transition IDs** (see [BWM](Level-Layout-Formats#transitions-and-door-placement)).
- **[VIS](Level-Layout-Formats#vis)** — Parent/child visibility between rooms.
- **Walkmeshes ([BWM](Level-Layout-Formats#bwm))** — Per-room WOK with materials, adjacency, and transition edges.
- **[GFF ARE](GFF-Module-and-Area#are)** and related module resources — Area metadata used with the layout.
- **Textures** — Often emitted as TGA (and related TXI) where the pipeline expects uncompressed sources; see PyKotor and toolset texture helpers under `pykotor.tools`.

Packaging into a playable override or module follows normal archive conventions:

- **[ERF](Container-Formats#erf)**
- **[RIM](Container-Formats#rim)**
- MOD (see [ERF](Container-Formats#erf))

See [Resource Formats and Resolution](Resource-Formats-and-Resolution).

## Kit and template layout

Authoring kits (room templates, hooks, metadata) are described in [Kit Structure Documentation](Kit-Structure-Documentation).

## Code and tooling

- **PyKotor** readers/writers: `Libraries/PyKotor/src/pykotor/resource/formats/` for LYT, BWM, VIS, GFF, ERF/RIM, and related types.
- **HolocronToolset** GUI: module / indoor editors under `Tools/HolocronToolset/src/toolset/gui/` (e.g. layout, walkmesh, and area editors). Prefer the shipped help bundle for UI specifics.

### See also

- [Indoor Map Builder User Guide](Indoor-Map-Builder-User-Guide)
- [Indoor Area Room Layout and Walkmesh Guide](Indoor-Area-Room-Layout-and-Walkmesh-Guide)
- [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions)
- [Blender Integration](Blender-Integration) — limitations for roomlink authoring in Blender
- [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers)
