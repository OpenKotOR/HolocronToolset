# Tutorial: Area transitions

This tutorial shows how to link two modules with area transitions. You will:

- Create a new module with the Map Builder
- Add a door transition from the new module to the Jedi Enclave
- Add a trigger transition from the Jedi Enclave to the new module
- Create waypoints that the transitions use

---

## 1. Create a module with the Map Builder

Open **File** → **Indoor Map Builder**. Download the **Enclave Surface** kit if needed (**File** → **Download Kits**). Create a simple layout.

![Layout](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3a.png)

Open **File** → **Settings** and set the warp code (e.g. **nthenc**). Build via **File** → **Build**. Test in-game with **warp nthenc**.

![Settings](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3b.png)
![Build](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3c.png)

---

## 2. Configure the door (new module → Jedi Enclave)

In the main window **Modules** tab click **Refresh**, find your module, and open its GIT. Select the door between the two hallway models; right-click → **Edit Instance**.

![Modules tab](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3d.png)
![Edit door](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3e.png)

Set:

- **Links To Waypoint** -- transition will teleport to a waypoint in the target module
- **Link To Module** -- **danm13** (Jedi Enclave warp code)
- **Link To Tag** -- tag of the waypoint in the *target* module we will teleport to (e.g. **from_nthenc**)
- **Transition Name** -- text shown when facing the transition

![Door settings](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3f.png)

---

## 3. Waypoint in the new module (arrival from Enclave)

Right-click in the new module → **Insert Instance** → add a waypoint in front of the door. Right-click it → **Edit Instance**. Set **ResRef** and **Tag** (e.g. **from_danm13**). Right-click → **Edit Resource** to create the waypoint file; match ResRef/Tag. Save the GIT.

![Waypoint](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3g.png)
![Waypoint instance](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3h.png)
![Waypoint resource](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3i.png)

---

## 4. Trigger in the Jedi Enclave (Enclave → new module)

Open the **Jedi Enclave** module GIT (e.g. danm13).

![Enclave module](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3j.png)

Right-click behind the Ebon Hawk → **Insert Trigger**. Right-click the trigger → **Edit Instance**. Set:

- **ResRef** and **Tag** -- e.g. **from_nthenc** (Tag must match the door’s **Link To Tag** in the new module)
- **Links To Waypoint**
- **Link To Module** -- **nthenc** (your new module)
- **Link To Tag** -- **from_danm13** (waypoint in the new module)
- **Transition Name**

![Trigger instance](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3l.png)

Right-click trigger → **Edit Resource**; set **Type** to **Transition**. Use **Edit Geometry** to draw the trigger volume (right-click → Insert vertices, drag, then Finish Editing).

![Trigger resource](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3m.png)
![Trigger geometry](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3n.png)

---

## 5. Waypoint in the Enclave (arrival from new module)

Right-click → **Insert Waypoint** in front of the trigger (away from the door). **Edit Instance**: set **Tag** and **ResRef** to **from_nthenc**. **Edit Resource** to create the waypoint file with the same values. Save the GIT.

![Waypoint in Enclave](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3o.png)
![Waypoint resource](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3p.png)

---

## 6. Test

You should be able to move between the Jedi Enclave and the new module via the door and the trigger.

![Result](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3q.png)
![Result](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/3r.png)

### See also

- [Tutorial: Creating a new store](Tutorial-Creating-a-New-Store) -- Store and dialogue workflow
- [Tutorial: Creating static cameras](Tutorial-Creating-Static-Cameras) -- Camera placement in modules
- [Tutorial: Creating custom robes](Tutorial-Creating-Custom-Robes) -- Item creation and texture workflow
- [Indoor Map Builder User Guide](Indoor-Map-Builder-User-Guide) -- Building Modules
- [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions) -- LYT/VIS/WOK concepts; Deadly Stream workflows (e.g. [Adding Rooms to a Module](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/)) are **community context**, not engine SSOT
- [GFF-UTD](GFF-File-Format#utd-door) -- Door instances and links
- [GFF-UTT](GFF-Spatial-Objects#utt) -- Trigger format
- [GFF-GIT](GFF-File-Format#git-game-instance-template) -- Placing instances
