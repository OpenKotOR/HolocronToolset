# Holocron Toolset: Map Builder (Indoor Map Builder)

The Map Builder creates new playable indoor areas from existing room models, without requiring Blender or any other external 3D modeling tool. Use it when you want to build a new interior area — a Sith tomb, a space station corridor, a cantina back room — by snapping together pre-made room pieces from the game's own model library.

Open it from the Main Window via **Tools** → **Indoor Map Builder**.

**Typical workflow:** Select a kit (a set of room models from a specific game area) → place rooms on the canvas → snap connections between them (shown as green lines) → **File** → **Build** to output a ready-to-play module to the game's `Modules/` folder.

## Kits

Kits are collections of room models extracted from specific game areas. The toolset does not ship with kits; download them when first prompted (or via **File** → **Download Kits**). See [Kit Structure Documentation](Kit-Structure-Documentation) for the file format details.

## Controls

| Action                  | Keys                                |
|-------------------------|-------------------------------------|
| Move Camera             | Hold **CTRL** and drag **LMB**      |
| Zoom Camera             | Hold **CTRL** and **Scroll**        |
| Rotate Camera           | Hold **CTRL** and drag **MMB**      |
| Place Model at Cursor   | **RMB**                             |
| Rotate Model at Cursor  | **Scroll**                          |
| Flip Model at Cursor    | **MMB**                             |
| Select Model            | **LMB** on model                    |
| Multi-Select            | Hold **SHIFT** and **LMB**          |
| Move Model              | Drag **LMB**                        |
| Open Context Menu       | **RMB**                             |

### See also

- [Holocron Toolset: Module editor](Holocron-Toolset-Module-Editor) -- Editing module contents
- [Holocron Toolset: Getting started](Holocron-Toolset-Getting-Started) -- Installation and first launch
- [Indoor Map Builder User Guide](Indoor-Map-Builder-User-Guide) -- Full guide: rooms, doors, walkmeshes, building
- [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide) -- Technical details
- [Kit Structure Documentation](Kit-Structure-Documentation) -- Kit layout and generation
- [Level-Layout-Formats#bwm](Level-Layout-Formats#bwm) -- Walkmesh format used by built modules
