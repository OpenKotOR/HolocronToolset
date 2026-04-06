# Tutorial: Creating static cameras

Static cameras are fixed viewpoints you can place in an area to control dialogue and cutscene framing. This tutorial covers static cameras only; animated cameras are not covered. They make in-game dialogue more than just a sequence of talking heads.

## Prerequisites

1. **Holocron Toolset** (or KotOR Tool for extraction if you prefer).
2. **K1 Utility Armbands** mod -- provides an in-game "orientation armband" that outputs position and quaternion values needed for camera orientation. Install via [TSLPatcher](TSLPatcher's-Official-Readme). (A modified version that adds quaternion X/Y for cameras may be referenced in the original tutorial; the armband gives player position and orientation.)
3. **Cheats enabled** in-game.

---

## Overview of camera data (GIT)

Camera information is stored in the module's [GIT (Game Instance Template)](GFF-File-Format#git-game-instance-template). The GIT holds a **CameraList**: a list of camera structs. Each camera has six main fields:

| Field         | Description |
|---------------|-------------|
| **CameraID**  | Numeric ID used in [dialogue (DLG)](GFF-Creature-and-Dialogue#dlg) to reference this camera. Must be unique in the module (e.g. 1–100). |
| **FieldOfView** | Like a zoom setting; larger values show more space. Typically keep in the 55–65 range; extremes can look odd. |
| **Height**    | Added to the Z coordinate of `Position`. Average person height in KotOR is ~1.5; set cameras near that if you want eye-level. |
| **Orientation** | Two numbers (quaternion X and Y). KotOR uses quaternions for static camera orientation; the orientation armband from K1 Utility Armbands can output the correct values from in-game. |
| **Pitch**     | 0 = straight down, 90 = straight ahead, 180 = directly up. |
| **Position**  | X, Y, Z coordinates in the area (top = X, middle = Y, bottom = Z). |

**Tip:** To add a camera, copy an existing camera struct in the [GIT](GFF-File-Format#git-game-instance-template), paste it under `CameraList`, then change the `CameraID` (and other fields) so you don't overwrite an existing camera.

---

## Step 1: Open the module and GIT

- **With Holocron Toolset:** In the **Modules** tab, select the module (e.g. Manaan Ahto West: `manm26aa.rim` or the corresponding `.mod`). Open the **GIT** file listed under Module Data (e.g. **manm26aa**). You can edit the [GIT](GFF-File-Format#git-game-instance-template) directly; saving will write back to the module or override as configured.
- **With KotOR Tool:** Expand [RIM](Container-Formats#rim) archives → Modules → your module (e.g. `manm26aa.rim`, not the `_s` one `manm26aa_s.rim`). Expand Dynamic Area Info, extract the GIT to a folder, then open it in K-GFF (or another GFF editor).

In the GIT, open or expand **CameraList** to see existing cameras.

---

## Step 2: Get position and orientation from in-game

1. Enter the area in-game where you want the camera. Use the cheat **giveitem sa_ori_arm** to get the orientation armband.
2. Move your **player character** to the exact spot and face the direction you want the camera to face. The armband reports the **player's** position and orientation, not the third-person camera. First-person view (e.g. Caps Lock) helps aim.
3. Use the armband. Then open the **Feedback** screen (Messages → Show Feedback) to read the output. You need:
   - **Player position** (X, Y, Z)
   - **Quaternion X** and **Quaternion Y** (for the Orientation field; a custom armband script may be needed for these two values specifically)

Note the three position numbers (e.g. -67.875, -3.850, 57.50) and the two quaternion values.

---

## Step 3: Create or edit the camera in the GIT

1. Copy an existing camera struct under `CameraList` and paste a new one (or add a new struct if your editor supports it).
2. Set **Position**: X in the top slot, Y in the middle, Z in the bottom.
3. Set **Orientation**: quaternion X in the top box, quaternion Y in the bottom.
4. Set **CameraID** to a unique number (e.g. one higher than the last camera in the list).
5. Set **FieldOfView** (e.g. 55–65).
6. Set **Height** (e.g. 1.5 for eye-level).
7. Set **Pitch** (e.g. 90 for straight ahead).

Save the [GIT](GFF-File-Format#git-game-instance-template). With Holocron Toolset, saving from the Module tab writes the change into the module/override as appropriate.

---

## Step 4: Use the camera in dialogue (DLG)

In your [DLG](GFF-Creature-and-Dialogue#dlg) editor, for the node where you want this camera:

- Set **`CameraID`** to the ID you gave the camera in the [GIT](GFF-File-Format#git-game-instance-template).
- Set **Camera angle** to **6** (required for static cameras).

You can add a delay if needed. Save the [Dialogue File (DLG)](GFF-Creature-and-Dialogue#dlg) file.

---

## Step 5: Packaging (if not using Holocron Toolset save)

If you extracted the [GIT](GFF-File-Format#git-game-instance-template) and edited it externally, you need to put the modified [GIT](GFF-File-Format#git-game-instance-template) (and any modified [DLG](GFF-Creature-and-Dialogue#dlg)) back into the game:

1. **Option A -- Override:** Place modified resources in the **override** folder with the correct names:

   - [GIT](GFF-File-Format#git-game-instance-template)
   - [DLG](GFF-Creature-and-Dialogue#dlg) if you edited dialogue

   The engine may load them for the module depending on how the game resolves resources (override can override module resources in some setups).

2. **Option B -- MOD file:** Create a `.mod` that contains the original module files plus your modified GIT and DLG. The game loads a `.mod` in place of the `.rim` pair when present. Compare:

   - [ERF](Container-Formats#erf) (MOD capsule layout)
   - [RIM](Container-Formats#rim) (stock module archives)

   You can use an ERF/MOD editor to create the `.mod`, add all files from the original [RIM](Container-Formats#rim) archives, then add/replace with your modified GIT and DLG. Place the `.mod` in the game's **modules** folder.

With **Holocron Toolset**, editing the [GIT](GFF-File-Format#git-game-instance-template) (and [DLG](GFF-Creature-and-Dialogue#dlg)) from the Modules tab and saving usually updates the module or writes to override, so you may not need a separate packaging step.

---

## Step 6: Test

Load a save from **before** you entered the area (so the module/[GIT](GFF-File-Format#git-game-instance-template) is reloaded). Enter the area and trigger the dialogue that uses your camera. The static camera should appear when that node plays.

---

### See also

- [Tutorial: Creating a new store](Tutorial-Creating-a-New-Store) -- Store and dialogue workflow
- [Tutorial: Area transitions](Tutorial-Area-Transitions) -- Connecting areas with doors and triggers
- [Tutorial: Creating custom robes](Tutorial-Creating-Custom-Robes) -- Item creation and texture workflow
- [GFF-GIT](GFF-File-Format#git-game-instance-template) -- Game Instance Template (`CameraList` and `camera` structs)
- [GFF-DLG](GFF-Creature-and-Dialogue#dlg) -- Dialogue format (`CameraID` and camera angle)
- [Holocron Toolset: Module Editor](Holocron-Toolset-Module-Editor) -- Opening and editing modules
