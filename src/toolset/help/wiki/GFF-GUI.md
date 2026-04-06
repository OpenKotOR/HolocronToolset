# GUI — Graphical User Interface

GUI files define the layout and behavior of every in-game interface screen — menus, HUD elements, dialog panels, and character sheets ([`GUI` L154](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L154), [`GFFContent.GUI` L163](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L163)). Each GUI is a [GFF](GFF-File-Format) tree describing a hierarchy of panels, buttons, labels, sliders, and other controls, with properties controlling position, size, textures, and event bindings ([`GUIControl` L100](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L100), [`construct_gui` L349](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L349), [`read_gui` L1060](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L1060), [GFF binary reader `io_gff.py` L82](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82)). Other implementations handle GUI as a standard GFF structure: [reone `gff.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/gff.cpp), [KotOR.js `GFFObject.ts` L24](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24), [Kotor.NET `GFF.cs` L18](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18).

GUI controls reference [TPC](Texture-Formats#tpc)/TGA textures for visual elements and use [TLK](Audio-and-Localization-Formats#tlk) string references for localizable text; the GUI editor in the [Holocron Toolset](Holocron-Toolset-Getting-Started) covers the full editing workflow.

## Core Identity fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique [GUI](GFF-File-Format#gui-graphical-user-interface) identifier |
| `ObjName` | [CExoString](GFF-File-Format#gff-data-types) | Object name (unused) |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment |

## Control structure

[GUI](GFF-File-Format#gui-graphical-user-interface) files contain a `Controls` list that holds the top-level UI elements ([`GUIControl` L100](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L100), [KotOR.js `GFFObject.ts` L24](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24)). Each control can contain child controls, forming a tree structure.

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Controls` | [List](GFF-File-Format#gff-data-types) | List of child controls |
| `Type` | [int32](GFF-File-Format#gff-data-types) | Control type identifier |
| `ID` | [int32](GFF-File-Format#gff-data-types) | Unique control ID |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Control tag |

**Control types** [[`gui.py` GUIControlType L23](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L23), [reone `types.h` L23](https://github.com/seedhartha/reone/blob/master/include/reone/gui/types.h#L23), [KotOR.js `GUIControlType.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/enums/gui/GUIControlType.ts)]:

> **⚠ Note:** PyKotor assigns 4=ProtoItem, 5=Label; reone and KotOR.js assign 4=Label, 5=ProtoItem/ImageButton. The discrepancy exists across implementations — use the `TAG` field for reliable control lookup.

| ID | Name (reone/KotOR.js) | Name (PyKotor) | Description |
| -- | --------------------- | -------------- | ----------- |
| -1 | Invalid | Invalid | Invalid control type |
| 0 | Control | Control | Base container |
| 2 | Panel | Panel | Background panel/container |
| 4 | Label | ProtoItem | Static text label (reone/KotOR.js); ProtoItem template (PyKotor) |
| 5 | ProtoItem/ImageButton | Label | ProtoItem template (reone/KotOR.js); Static text label (PyKotor) |
| 6 | Button | Button | Clickable button |
| 7 | ToggleButton/CheckBox | CheckBox | Toggle checkbox |
| 8 | Slider | Slider | Sliding value control |
| 9 | ScrollBar | ScrollBar | Scroll bar control |
| 10 | ProgressBar | Progress | Progress bar indicator |
| 11 | ListBox | ListBox | List of items with scrolling |

## Common Properties

All controls share these base properties:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `CONTROLTYPE` | [int32](GFF-File-Format#gff-data-types) | Control type identifier (see Control types) |
| `ID` | [int32](GFF-File-Format#gff-data-types) | Unique control ID for script references |
| `TAG` | [CExoString](GFF-File-Format#gff-data-types) | Control tag identifier |
| `Obj_Locked` | [byte](GFF-File-Format#gff-data-types) | Lock state (0=unlocked, 1=locked) |
| `Obj_Parent` | [CExoString](GFF-File-Format#gff-data-types) | Parent control tag (for hierarchy) |
| `Obj_ParentID` | [int32](GFF-File-Format#gff-data-types) | Parent control ID (for hierarchy) |
| `ALPHA` | float | Opacity/transparency (0.0=transparent, 1.0=opaque) |
| `COLOR` | vector | Control color modulation (RGB, 0.0-1.0) |
| `EXTENT` | Struct | position and size rectangle |
| `BORDER` | Struct | Border rendering properties |
| `HILIGHT` | Struct | Highlight appearance (hover state) |
| `TEXT` | Struct | Text display properties |
| `MOVETO` | Struct | D-pad navigation targets |

**EXTENT Struct:**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `LEFT` | [int32](GFF-File-Format#gff-data-types) | X position relative to parent (pixels) |
| `TOP` | [int32](GFF-File-Format#gff-data-types) | Y position relative to parent (pixels) |
| `WIDTH` | [int32](GFF-File-Format#gff-data-types) | Control width (pixels) |
| `HEIGHT` | [int32](GFF-File-Format#gff-data-types) | Control height (pixels) |

**Positioning System:**

- coordinates are relative to parent control
- Base resolution is 640x480, scaled for higher resolutions
- Negative values allowed for positioning outside parent bounds
- Root control ([GUI](GFF-File-Format#gui-graphical-user-interface)) uses screen-relative coordinates

**BORDER Struct:**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `CORNER` | *ResRef* | Corner texture ([TPC](Texture-Formats#tpc) or TGA) |
| `EDGE` | *ResRef* | [edge](Level-Layout-Formats#edges-wok-only) texture ([TPC](Texture-Formats#tpc) or TGA) |
| `FILL` | *ResRef* | Fill/background texture ([TPC](Texture-Formats#tpc) or TGA) |
| `FILLSTYLE` | [int32](GFF-File-Format#gff-data-types) | Fill rendering style integer; default 2 in BORDER [[`gui.py` L461](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L461)], 0 in HILIGHT/PROGRESS [[`gui.py` L408](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L408)]; reone and xoreos read as raw uint [[xoreos `widget.cpp` L532](https://github.com/xoreos/xoreos/blob/master/src/engines/odyssey/widget.cpp#L532)] |
| `DIMENSION` | [int32](GFF-File-Format#gff-data-types) | Border thickness in pixels |
| `INNEROFFSET` | [int32](GFF-File-Format#gff-data-types) | Inner padding X-axis (pixels) |
| `INNEROFFSETY` | [int32](GFF-File-Format#gff-data-types) | Inner padding Y-axis (pixels, optional) |
| `COLOR` | vector | Border color modulation (RGB, 0.0-1.0) |
| `PULSING` | [byte](GFF-File-Format#gff-data-types) | Pulsing [animation](MDL-MDX-File-Format#animation-header) flag (0=off, 1=on) |

**Border Rendering:**

- **CORNER**: 4 corner pieces (top-left, top-right, bottom-left, bottom-right)
- **[edge](Level-Layout-Formats#edges-wok-only)**: 4 [edge](Level-Layout-Formats#edges-wok-only) pieces (top, right, bottom, left)
- **FILL**: Center fill area (scaled to fit)
- **DIMENSION**: Thickness of border [edges](Level-Layout-Formats#edges-wok-only)
- **FILLSTYLE**: Raw integer read by engine; default 2 for BORDER [[`gui.py` L461](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L461)]; no named enum exists in reone or xoreos sources
- **CORNER/EDGE/FILL textures**: skipped if empty or if the value is the string `"0"` [[reone `control.cpp` `loadBorder`](https://github.com/seedhartha/reone/blob/master/src/libs/gui/control.cpp)]

**TEXT Struct:**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TEXT` | [CExoString](GFF-File-Format#gff-data-types) | Direct text content (overrides [StrRef](Audio-and-Localization-Formats#string-references-strref) if set) |
| `STRREF` | DWord | [TLK](Audio-and-Localization-Formats#tlk) string reference (0xFFFFFFFF = unused) |
| `FONT` | *ResRef* | Font [texture](Texture-Formats#tpc) resource ([TPC](Texture-Formats#tpc) or TGA) |
| `ALIGNMENT` | [int32](GFF-File-Format#gff-data-types) | Text alignment flags (bitfield) |
| `COLOR` | vector | Text color (RGB, 0.0-1.0) |
| `PULSING` | [byte](GFF-File-Format#gff-data-types) | Pulsing [animation](MDL-MDX-File-Format#animation-header) flag (0=off, 1=on) |

**Text Alignment values:**

- **1**: Top-Left
- **2**: Top-Center
- **3**: Top-Right
- **17**: Center-Left
- **18**: Center (most common)
- **19**: Center-Right
- **33**: Bottom-Left
- **34**: Bottom-Center
- **35**: Bottom-Right

**Text Resolution:**

- If both `TEXT` and `STRREF` are set, `TEXT` takes precedence
- Font [textures](Texture-Formats#tpc) contain character glyphs in fixed grid
- Text color modulates font texture (white = full color, black = no color)

**MOVETO Struct:**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `UP` | [int32](GFF-File-Format#gff-data-types) | Control ID to navigate to when pressing Up |
| `DOWN` | [int32](GFF-File-Format#gff-data-types) | Control ID to navigate to when pressing Down |
| `LEFT` | [int32](GFF-File-Format#gff-data-types) | Control ID to navigate to when pressing Left |
| `RIGHT` | [int32](GFF-File-Format#gff-data-types) | Control ID to navigate to when pressing Right |

**Navigation System:**

- Used for keyboard/D-pad navigation
- value of -1 or 0 indicates no navigation in that direction
- Essential for controller/keyboard-only gameplay

**HILIGHT Struct:**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `CORNER` | *ResRef* | Corner [texture](Texture-Formats#tpc) for highlight state |
| `EDGE` | *ResRef* | [edge](Level-Layout-Formats#edges-wok-only) [texture](Texture-Formats#tpc) for highlight state |
| `FILL` | *ResRef* | Fill [texture](Texture-Formats#tpc) for highlight state |
| `FILLSTYLE` | [int32](GFF-File-Format#gff-data-types) | Fill style for highlight |
| `DIMENSION` | [int32](GFF-File-Format#gff-data-types) | Border thickness |
| `INNEROFFSET` | [int32](GFF-File-Format#gff-data-types) | Inner padding X-axis |
| `INNEROFFSETY` | [int32](GFF-File-Format#gff-data-types) | Inner padding Y-axis (optional) |
| `COLOR` | vector | Highlight color modulation |
| `PULSING` | [byte](GFF-File-Format#gff-data-types) | Pulsing [animation](MDL-MDX-File-Format#animation-header) flag |

**Highlight Behavior:**

- Shown when mouse hovers over control
- Replaces or overlays BORDER when active
- Used for interactive feedback
- color typically brighter/more saturated than border

**SELECTED Struct:**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `CORNER` | *ResRef* | Corner [texture](Texture-Formats#tpc) for selected state |
| `EDGE` | *ResRef* | [edge](Level-Layout-Formats#edges-wok-only) [texture](Texture-Formats#tpc) for selected state |
| `FILL` | *ResRef* | Fill [texture](Texture-Formats#tpc) for selected state |
| `FILLSTYLE` | [int32](GFF-File-Format#gff-data-types) | Fill style for selected state |
| `DIMENSION` | [int32](GFF-File-Format#gff-data-types) | Border thickness |
| `INNEROFFSET` | [int32](GFF-File-Format#gff-data-types) | Inner padding X-axis |
| `INNEROFFSETY` | [int32](GFF-File-Format#gff-data-types) | Inner padding Y-axis (optional) |
| `COLOR` | vector | Selected state color modulation |
| `PULSING` | [byte](GFF-File-Format#gff-data-types) | Pulsing [animation](MDL-MDX-File-Format#animation-header) flag |

**HILIGHTSELECTED Struct:**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `CORNER` | *ResRef* | Corner [texture](Texture-Formats#tpc) for highlight+selected state |
| `EDGE` | *ResRef* | [edge](Level-Layout-Formats#edges-wok-only) [texture](Texture-Formats#tpc) for highlight+selected state |
| `FILL` | *ResRef* | Fill [texture](Texture-Formats#tpc) for highlight+selected state |
| `FILLSTYLE` | [int32](GFF-File-Format#gff-data-types) | Fill style |
| `DIMENSION` | [int32](GFF-File-Format#gff-data-types) | Border thickness |
| `INNEROFFSET` | [int32](GFF-File-Format#gff-data-types) | Inner padding X-axis |
| `INNEROFFSETY` | [int32](GFF-File-Format#gff-data-types) | Inner padding Y-axis (optional) |
| `COLOR` | vector | Combined state color modulation |
| `PULSING` | [byte](GFF-File-Format#gff-data-types) | Pulsing [animation](MDL-MDX-File-Format#animation-header) flag |

**State Priority:**

1. **HILIGHTSELECTED**: When control is both highlighted (hovered) and selected
2. **HILIGHT**: When control is highlighted (hovered) but not selected
3. **SELECTED**: When control is selected but not highlighted
4. **BORDER**: Default appearance

## Control-Specific fields

**ListBox (type 11):**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `PROTOITEM` | Struct | Template for list item appearance |
| `SCROLLBAR` | Struct | Embedded scrollbar control |
| `PADDING` | [int32](GFF-File-Format#gff-data-types) | Spacing between items (pixels) |
| `MAXVALUE` | [int32](GFF-File-Format#gff-data-types) | Maximum scroll value (total items - visible items) |
| `CURVALUE` | [int32](GFF-File-Format#gff-data-types) | Current scroll position |
| `LOOPING` | [byte](GFF-File-Format#gff-data-types) | Loop scrolling (0=no, 1=yes) |
| `LEFTSCROLLBAR` | [byte](GFF-File-Format#gff-data-types) | Scrollbar on left side (0=right, 1=left) |

**ListBox Behavior:**

- **PROTOITEM**: Defines appearance template for each list item
- **SCROLLBAR**: Embedded scrollbar for navigating long lists
- **PADDING**: Vertical spacing between items
- **MAXVALUE**: Maximum scroll offset (when all items visible, MAXVALUE=0)
- **LOOPING**: When enabled, scrolling past end wraps to beginning
- **LEFTSCROLLBAR**: positions scrollbar on left instead of right

**PROTOITEM Struct (for ListBox):**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `CONTROLTYPE` | [int32](GFF-File-Format#gff-data-types) | Always 4 (ProtoItem) |
| `EXTENT` | Struct | Item size and position |
| `BORDER` | Struct | Item border appearance |
| `HILIGHT` | Struct | Item highlight on hover |
| `HILIGHTSELECTED` | Struct | Item highlight when selected |
| `SELECTED` | Struct | Item appearance when selected |
| `TEXT` | Struct | Item text properties |
| `ISSELECTED` | [byte](GFF-File-Format#gff-data-types) | Default selected state |

**ScrollBar (type 9):**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `DIR` | Struct | Direction arrow buttons appearance |
| `THUMB` | Struct | Draggable thumb appearance |
| `MAXVALUE` | [int32](GFF-File-Format#gff-data-types) | Maximum scroll value |
| `VISIBLEVALUE` | [int32](GFF-File-Format#gff-data-types) | Number of visible items in viewport |
| `CURVALUE` | [int32](GFF-File-Format#gff-data-types) | Current scroll position |
| `DRAWMODE` | [byte](GFF-File-Format#gff-data-types) | Drawing mode (0=normal, other values unused) |

**ScrollBar Behavior:**

- **MAXVALUE**: Total scrollable range
- **VISIBLEVALUE**: size of visible area (determines thumb size)
- **CURVALUE**: Current scroll offset (0 to MAXVALUE)
- Thumb size = (VISIBLEVALUE / MAXVALUE) × track length

**DIR Struct (ScrollBar Direction Buttons):**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `IMAGE` | *ResRef* | Arrow button [texture](Texture-Formats#tpc) |
| `ALIGNMENT` | [int32](GFF-File-Format#gff-data-types) | Image alignment (typically 18=center) |
| `DRAWSTYLE` | [int32](GFF-File-Format#gff-data-types) | Drawing style (unused) |
| `FLIPSTYLE` | [int32](GFF-File-Format#gff-data-types) | Flip/rotation style (unused) |
| `ROTATE` | float | rotation angle (unused) |

**THUMB Struct (ScrollBar Thumb):**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `IMAGE` | *ResRef* | Thumb [texture](Texture-Formats#tpc) |
| `ALIGNMENT` | [int32](GFF-File-Format#gff-data-types) | Image alignment (typically 18=center) |
| `DRAWSTYLE` | [int32](GFF-File-Format#gff-data-types) | Drawing style (unused) |
| `FLIPSTYLE` | [int32](GFF-File-Format#gff-data-types) | Flip/rotation style (unused) |
| `ROTATE` | float | rotation angle (unused) |

**ProgressBar (type 10):**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `PROGRESS` | Struct | Progress fill appearance |
| `CURVALUE` | [int32](GFF-File-Format#gff-data-types) | Current progress value (0-100) |
| `MAXVALUE` | [int32](GFF-File-Format#gff-data-types) | Maximum value (typically 100) |
| `STARTFROMLEFT` | [byte](GFF-File-Format#gff-data-types) | Fill direction (0=right, 1=left) |

**ProgressBar Behavior:**

- **CURVALUE**: Current progress (0-100, or 0-MAXVALUE)
- **STARTFROMLEFT**: When 1, fills left-to-right; when 0, fills right-to-left
- Progress = (CURVALUE / MAXVALUE) × width

**PROGRESS Struct:**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `CORNER` | *ResRef* | Corner [texture](Texture-Formats#tpc) for progress fill |
| `EDGE` | *ResRef* | [edge](Level-Layout-Formats#edges-wok-only) [texture](Texture-Formats#tpc) for progress fill |
| `FILL` | *ResRef* | Fill [texture](Texture-Formats#tpc) for progress bar |
| `FILLSTYLE` | [int32](GFF-File-Format#gff-data-types) | Fill rendering style |
| `DIMENSION` | [int32](GFF-File-Format#gff-data-types) | Border thickness |
| `INNEROFFSET` | [int32](GFF-File-Format#gff-data-types) | Inner padding X-axis |
| `INNEROFFSETY` | [int32](GFF-File-Format#gff-data-types) | Inner padding Y-axis (optional) |
| `COLOR` | vector | Progress fill color modulation |
| `PULSING` | [byte](GFF-File-Format#gff-data-types) | Pulsing [animation](MDL-MDX-File-Format#animation-header) flag |

**CheckBox (type 7):**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `SELECTED` | Struct | Appearance when checked |
| `HILIGHTSELECTED` | Struct | Appearance when checked and hovered |
| `ISSELECTED` | [byte](GFF-File-Format#gff-data-types) | Default checked state (0=unchecked, 1=checked) |

**CheckBox Behavior:**

- Toggles between checked/unchecked on click
- **ISSELECTED**: Initial state
- **SELECTED**: Visual appearance when checked
- **HILIGHTSELECTED**: Visual appearance when checked and hovered

**Slider (type 8):**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `THUMB` | Struct | Slider thumb appearance |
| `CURVALUE` | [int32](GFF-File-Format#gff-data-types) | Current slider value |
| `MAXVALUE` | [int32](GFF-File-Format#gff-data-types) | Maximum slider value |
| `DIRECTION` | [int32](GFF-File-Format#gff-data-types) | Orientation (0=horizontal, 1=vertical) |

**Slider Behavior:**

- **CURVALUE**: Current position (0 to MAXVALUE)
- **MAXVALUE**: Maximum value (typically 100)
- **DIRECTION**: 0=horizontal (left-right), 1=vertical (top-bottom)
- Thumb position = (CURVALUE / MAXVALUE) × track length

**Slider THUMB Struct:**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `IMAGE` | *ResRef* | Thumb [texture](Texture-Formats#tpc) |
| `ALIGNMENT` | [int32](GFF-File-Format#gff-data-types) | Image alignment |
| `DRAWSTYLE` | [int32](GFF-File-Format#gff-data-types) | Drawing style (unused) |
| `FLIPSTYLE` | [int32](GFF-File-Format#gff-data-types) | Flip/rotation style (unused) |
| `ROTATE` | float | rotation angle (unused) |

**Button (type 6):**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `HILIGHT` | Struct | Hover state appearance |
| `MOVETO` | Struct | D-pad navigation targets |
| `TEXT` | Struct | Button label text |

**Button Behavior:**

- Clickable control with text label
- **HILIGHT**: Shown on mouse hover; hover event plays hardcoded sound `gui_actscroll` [[xoreos `button.cpp` L124](https://github.com/xoreos/xoreos/blob/master/src/engines/odyssey/button.cpp#L124)]
- Click event plays hardcoded sound `gui_actuse` [[xoreos `button.cpp` L148](https://github.com/xoreos/xoreos/blob/master/src/engines/odyssey/button.cpp#L148)]
- **TEXT**: Button label (can use [StrRef](Audio-and-Localization-Formats#string-references-strref) for localization)
- **MOVETO**: Keyboard/D-pad navigation

**Label (type 5):**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TEXT` | Struct | Text display properties |

**Label Behavior:**

- Static text display (non-interactive)
- **TEXT**: Text content, font, alignment, color
- Used for UI labels, descriptions, headers

**Panel (type 2):**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `CONTROLS` | [List](GFF-File-Format#gff-data-types) | Child controls list |
| `BORDER` | Struct | Panel border (optional background) |
| `COLOR` | vector | Panel color modulation |
| `ALPHA` | float | Panel transparency |

**Panel Behavior:**

- Container for child controls
- **CONTROLS**: List of child controls (any type)
- **BORDER**: Optional background/border
- Child controls positioned relative to panel

**ProtoItem (type 4):**

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TEXT` | Struct | Item label text |
| `BORDER` | Struct | Item border appearance |
| `HILIGHT` | Struct | Item highlight on hover |
| `HILIGHTSELECTED` | Struct | Item highlight when selected |
| `SELECTED` | Struct | Item appearance when selected |
| `ISSELECTED` | [byte](GFF-File-Format#gff-data-types) | Default selected state |

**ProtoItem Behavior:**

- Template for list items (used by ListBox)
- Defines appearance of individual list entries
- **ISSELECTED**: Initial selection state
- States: Normal, Highlighted, Selected, Highlighted+Selected

## Implementation Notes

**Control Hierarchy:**

- [GUI](GFF-File-Format#gui-graphical-user-interface) root contains `CONTROLS` list of top-level controls
- Controls can have child controls via `CONTROLS` list
- Child controls positioned relative to parent's EXTENT
- Parent visibility affects children (hidden parent hides children)
- Z-order: Children render above parents, and later controls render above earlier ones (rendering order is determined by control list order) ([reone `gui.cpp` L80-92](https://github.com/seedhartha/reone/blob/master/src/libs/gui/gui.cpp#L80-L92), [reone `control.cpp` L192-194](https://github.com/seedhartha/reone/blob/master/src/libs/gui/control.cpp#L192-L194)).

**Positioning System:**

- Base resolution: 640x480 pixels (engine default, scaled for higher resolutions) ([reone `gui.h` L38-39](https://github.com/seedhartha/reone/blob/master/include/reone/gui/gui.h#L38-L39)).
- coordinates are pixel-based, engine scales for higher resolutions
- EXTENT.LEFT/TOP: position relative to parent (or screen for root)
- Negative coordinates allowed (positioning outside parent bounds)
- Root control EXTENT defines [GUI](GFF-File-Format#gui-graphical-user-interface) bounds

**color System:**

- **color** (Vector3): RGB color modulation (0.0-1.0 range)
- **ALPHA** (float): Transparency (0.0=transparent, 1.0=opaque)
- colors multiply with textures (white=full color, black=no color)
- KotOR 1 default text color: RGB(0.0, 0.658824, 0.980392) — cyan [[KotOR.js `GUIControl.ts` L188](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/gui/GUIControl.ts#L188)]
- KotOR 2 default text color: RGB(0.102, 0.698, 0.549) — teal [[KotOR.js `GUIControl.ts` L192](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/gui/GUIControl.ts#L192)]
- KotOR 1 default highlight color: RGB(1.0, 1.0, 0.0) — yellow [[KotOR.js `GUIControl.ts` L189](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/gui/GUIControl.ts#L189)]
- KotOR 2 default highlight color: RGB(0.8, 0.8, 0.698) [[KotOR.js `GUIControl.ts` L193](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/gui/GUIControl.ts#L193)]

**Border Rendering:**

- Border consists of 9 pieces: 4 corners, 4 [edges](Level-Layout-Formats#edges-wok-only), 1 fill
- CORNER [textures](Texture-Formats#tpc): Top-left, top-right, bottom-left, bottom-right
- [edge](Level-Layout-Formats#edges-wok-only) [textures](Texture-Formats#tpc): Top, right, bottom, left (tiled along length)
- FILL [texture](Texture-Formats#tpc): Center area (scaled or tiled based on FILLSTYLE)
- DIMENSION: Thickness of border [edges](Level-Layout-Formats#edges-wok-only) in pixels
- INNEROFFSET: Padding between border and content

**Text Rendering:**

- Fonts are [texture](Texture-Formats#tpc)-based ([TPC](Texture-Formats#tpc) or TGA files with character grid)
- Each character has fixed width/height in font [texture](Texture-Formats#tpc)
- If STRREF is a valid index, the engine resolves it via TLK; if STRREF is absent/`0xFFFFFFFF`, the direct TEXT string is used [[xoreos `widget.cpp` `createText` L544](https://github.com/xoreos/xoreos/blob/master/src/engines/odyssey/widget.cpp#L544), [PyKotor `gui.py` L362](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L362)]
- [StrRef](Audio-and-Localization-Formats#string-references-strref) references [dialog.tlk](Audio-and-Localization-Formats#tlk) for localized strings
- ALIGNMENT uses bitfield: horizontal (1=left, 2=center, 3=right) + vertical (0=top, 16=center, 32=bottom) [[`gui.py` GUIAlignment](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L39)]
- Text color modulates font [texture](Texture-Formats#tpc)

**State Management:**

- **Normal**: BORDER struct defines appearance
- **Hover**: HILIGHT struct overlays/replaces BORDER
- **Selected**: SELECTED struct defines appearance (CheckBox, ListBox items)
- **Hover+Selected**: HILIGHTSELECTED struct (highest priority)

**Control IDs:**

- **ID** field: Unique control identifier read by PyKotor as `ID` int32 [[`gui.py` `construct_control`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L608)]; read by reone via `getTag`/`getId` [[reone `control.cpp` L48](https://github.com/seedhartha/reone/blob/master/src/libs/gui/control.cpp#L48)]
- **TAG** field: String identifier; used by reone for parent lookup via `Obj_Parent` [[reone `control.cpp` L52](https://github.com/seedhartha/reone/blob/master/src/libs/gui/control.cpp#L52)]

**Navigation:**

- **MOVETO** struct defines D-pad/keyboard navigation
- value is Control ID of target control
- -1 or 0 indicates no navigation in that direction
- Essential for [controller](MDL-MDX-File-Format#controllers)/keyboard-only gameplay

**ScrollBar Integration:**

- ListBox controls can embed SCROLLBAR struct [[xoreos `listbox.cpp` L70](https://github.com/xoreos/xoreos/blob/master/src/engines/odyssey/listbox.cpp#L70), [PyKotor `gui.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/gui.py)]
- `SCROLLBAR.MAXVALUE` default 99; `SCROLLBAR.VISIBLEVALUE` default 1 [[PyKotor `gui.py` `construct_control`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/gui.py)]
- `SCROLLBAR.CURVALUE` = current scroll offset
- Thumb size proportional to viewport: `(trackLength - 2 × arrowHeight) × (visibleValue / maxValue)` [[xoreos `scrollbar.cpp`](https://github.com/xoreos/xoreos/blob/master/src/engines/odyssey/scrollbar.cpp)]
- `LEFTSCROLLBAR`: positions scrollbar on left side [[xoreos `listbox.cpp` L71](https://github.com/xoreos/xoreos/blob/master/src/engines/odyssey/listbox.cpp#L71)]

**Pulsing [animation](MDL-MDX-File-Format#animation-header):**

- **PULSING** flag in BORDER, TEXT, HILIGHT, SELECTED structs [[`gui.py` GUIBorder.pulsing L65](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L65)]
- When enabled, control pulses (fades in/out)
- Used for attention-grabbing effects

**[texture](Texture-Formats#tpc) formats:**

- [GUI](GFF-File-Format#gui-graphical-user-interface) [textures](Texture-Formats#tpc) use TPC or TGA format; fields CORNER/EDGE/FILL are ResRef strings
- xoreos HILIGHT struct reads only the `FILL` field (no CORNER/EDGE for highlights) [[xoreos `widget.cpp` L580](https://github.com/xoreos/xoreos/blob/master/src/engines/odyssey/widget.cpp#L580)]
- Font [textures](Texture-Formats#tpc) contain character glyphs; each glyph rendered at fixed grid position [[xoreos `GUIFont.ts`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/gui/GUIFont.ts)]

**KotOR-Specific Notes:**

- GUIs are loaded from `.gui` files ([GFF](GFF-File-Format) format); entry function `construct_gui` [[PyKotor `gui.py` L353](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/gui.py#L353)]
- Base resolution 640×480; implementations scale to screen by aspect or center offset [[reone `gui.h` L37-38](https://github.com/seedhartha/reone/blob/master/include/reone/gui/gui.h#L37), [reone `gui.cpp` scaling L119-124](https://github.com/seedhartha/reone/blob/master/src/libs/gui/gui.cpp#L119)]
- Controls located by `TAG` string [[reone `control.cpp` L52](https://github.com/seedhartha/reone/blob/master/src/libs/gui/control.cpp#L52)] or `ID` integer [[PyKotor `gui.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/gui.py)]

### See also

- [GFF-File-Format](GFF-File-Format) -- Generic format underlying GUI
- [GFF Creature and Dialogue](GFF-Creature-and-Dialogue) -- UTC and DLG types
- [GFF Items and Economy](GFF-Items-and-Economy) -- UTI, UTM, JRL, FAC types
- [GFF Module and Area](GFF-Module-and-Area) -- ARE, GIT, IFO types
- [TPC File Format](Texture-Formats#tpc) — textures used by GUI controls
- [TLK File Format](Audio-and-Localization-Formats#tlk) - String references for GUI text
- [NCS File Format](NCS-File-Format) - Scripts that drive GUI behavior

