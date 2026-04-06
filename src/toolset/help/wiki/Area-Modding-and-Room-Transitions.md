# Area Modding and Room Transitions

This page focuses on one specific indoor-area problem: making room-to-room crossing actually work once a layout exists. If you need the broader module-building workflow, start with [Indoor Area - Room Layout and Walkmesh Guide](Indoor-Area-Room-Layout-and-Walkmesh-Guide).

For the player to walk between rooms in a module, several data files must agree: the LYT must place the rooms, the VIS must declare visibility, walkmeshes must provide navigable triangles at the doorway, and the GIT/ARE must reference the correct room models. When any of these are missing or mismatched, the player hits an invisible wall or falls through the floor.

## What must agree for room crossing

For the player to move from one room to another, all of the following must be consistent:

1. **Rooms positioned in the area layout** -- The [LYT](Level-Layout-Formats#lyt) file lists room models and their world positions.
2. **Walkmesh seam alignment** -- Each room has its own [WOK](Level-Layout-Formats#bwm) walkmesh; at the boundary between two rooms, the perimeter edges of both walkmeshes must align (same world-space seam).
3. **Roomlinks (transitions) reassigned** -- Perimeter edges in the walkmesh carry a *transition ID* that identifies the adjacent room. That ID is the 0-based index of the room in the LYT. If you add, remove, or reorder rooms, existing roomlinks no longer match and must be reassigned in a workflow that supports roomlink/transition editing.
4. **Area LYT and VIS** — both must include the new or changed rooms:

   - [LYT](Level-Layout-Formats#lyt)
   - [VIS](Level-Layout-Formats#vis)
5. **Exported room includes WOK** -- When you edit room geometry or walkmesh, the WOK must be exported/updated; many tools have an "Export WOK" option that is off by default.
6. **Binaries compiled** -- ASCII model edits (e.g. roomlinks in the model) must be compiled back to binary (MDL/MDX and WOK) for the game to use them.

## Why room crossing fails

Crossing fails when the engine does not see a valid transition at the seam. Common causes:

- **Roomlinks not reassigned** -- If you reuse or rearrange room models, the perimeter edges still point at the old LYT room indices. The only fix is to load the full layout and reassign which edge links to which room (see [BWM File Format](Level-Layout-Formats#transitions-and-door-placement)).
- **Layout vs model-only workflow** -- Loading a single room model without the area layout does not establish room order (transition ID = LYT room index). Reassigning roomlinks requires a layout-aware workflow (load LYT, then edit room models/walkmeshes in that context).
- **Walkmesh not exported** -- If you change the walkmesh but do not export WOK (or the tool does not write it), the game still uses the old walkmesh.

Do not merge walkmeshes across rooms: each room has its own WOK. Crossing is done via **paired perimeter transition edges** (reciprocal transition IDs on both sides). Combining walkmeshes or only repainting materials does not fix crossing.

## Doors (conceptual)

Real doors (that open and allow crossing) require: a door model, a door walkmesh (DWK) with closed/open states, the correct surface material on the threshold, and roomlinks connecting both rooms. Door walkmesh node naming (e.g. `_wg_closed`, `_wg_open1`, `_wg_open2`) matters for the engine. Dynamic elements (doors, placeables, creatures, triggers, transitions) are defined in the [GIT](GFF-Module-and-Area#git), not in the LYT; LYT door hooks only provide suggested positions for placing doors.

## Community tooling / Further reading

Use the wiki for the engine-facing concepts on this page, then use the following community and tool-specific guides for the concrete editing workflow.

- **KOTORMax** (Deadly Stream file by bead-v) — Plugin for 3ds Max and GMax; LYT/VIS import and export; Roomlink Editor; ASCII model workflow with [MDLEdit](https://deadlystream.com/forum/files/file/1150-mdledit/) or MDLOps.
  - [KOTORmax file](https://deadlystream.com/files/file/1151-kotormax/)
  - [KOTORmax topic](https://deadlystream.com/topic/5731-kotormax/)
- **Adding existing rooms to a module** (Deadly Stream) -- Explains roomlinks, reassigning in KOTORMax, and what must agree. [Topic 8517](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/).
- **[K1] Creating a new room in an existing module** (Deadly Stream) -- Workflow for new rooms and using KOTORMax for layout, visibility, and walkmesh edges. [Topic 11729](https://deadlystream.com/topic/11729-k1-creating-a-new-room-in-an-existing-module/).
- **KOTORBlender** -- Room transition/roomlink support is incomplete; fine for geometry, not reliable for finalizing room-to-room crossing. Alternatives:

  - [Blender Integration — current limitations](Blender-Integration#current-limitations)
  - [Indoor Map Builder](Indoor-Map-Builder-User-Guide)

### See also

- [BWM File Format](Level-Layout-Formats#bwm) -- WOK structure, perimeters, transition IDs
- [Transitions and Door Placement](Level-Layout-Formats#transitions-and-door-placement).
- [LYT File Format](Level-Layout-Formats#lyt) -- Room order and [room definitions](Level-Layout-Formats#room-definitions); room index = transition ID.
- [VIS File Format](Level-Layout-Formats#vis) -- Visibility graph for area rooms.
- [Indoor Map Builder User Guide](Indoor-Map-Builder-User-Guide) -- Building indoor modules and [troubleshooting room crossing](Indoor-Map-Builder-User-Guide#room-crossing-and-walkmesh).
- [Indoor Area - Room Layout and Walkmesh Guide](Indoor-Area-Room-Layout-and-Walkmesh-Guide) -- Higher-level indoor workflow before roomlink troubleshooting.
- [Blender Integration](Blender-Integration) -- Limitations for roomlink authoring.
- [2DA surfacemat](2DA-File-Format#surfacemat2da) -- Walkmesh face materials and walkability.
