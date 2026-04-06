# Indoor Area — Room Layout and Walkmesh Guide

This page is the high-level workflow overview for building or restructuring an indoor module. If your layout already exists and the specific problem is "the player cannot cross between rooms," use [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions) for the seam, roomlink, and transition-ID details.

Building an indoor module requires coordinating several subsystems: **room layout**, **walkmesh transitions**, **visibility**, and **packaging**. The format specifics live on the linked format pages; the workflow below shows how they fit together.

## Workflow overview

1. **Layout** — Define rooms and transforms in **[LYT](Level-Layout-Formats#lyt)**. Room order determines indices used elsewhere.
2. **Walkmesh** — Each room needs a **[BWM](Level-Layout-Formats#bwm)** (WOK) with correct **transition** indices matching the LYT room index for doorways and crossings. See [Transitions and Door Placement](Level-Layout-Formats#transitions-and-door-placement).
3. **Visibility** — **[VIS](Level-Layout-Formats#vis)** describes which rooms can see which; keep it in sync with the LYT room names.
4. **Area data** — **[GFF ARE](GFF-Module-and-Area#are)** and the rest of the module set follow normal module layout. Resolution order is described under:

   - [Concepts — Resource resolution](Concepts#resource-resolution-order)
   - [Resource Formats and Resolution](Resource-Formats-and-Resolution)

## Tooling

- **Holocron Indoor Map Builder**
  - [User Guide](Indoor-Map-Builder-User-Guide)
  - [Implementation Guide](Indoor-Map-Builder-Implementation-Guide)
- **Community tools** — KOTORMax, kotorblender, kaurora; tradeoffs and links are summarized in:

  - [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions)
  - [Blender Integration](Blender-Integration)

## Troubleshooting

- **Cannot walk between rooms** — Usually transition IDs on walkmesh edges, LYT order, or missing/incorrect VIS. Use [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions) as the dedicated troubleshooting reference, then compare your workflow against [Room crossing and walkmesh](Indoor-Map-Builder-User-Guide#room-crossing-and-walkmesh).
- **Kit / template structure** — [Kit Structure Documentation](Kit-Structure-Documentation).

### See also

- [BWM File Format](Level-Layout-Formats#bwm)
- [LYT File Format](Level-Layout-Formats#lyt)
- [VIS File Format](Level-Layout-Formats#vis)
- [Reverse Engineering Findings — BWM / walkmesh / AABB](reverse_engineering_findings#bwm-walkmesh-aabb-engine-implementation-analysis) — engine-side walkmesh tree behavior
