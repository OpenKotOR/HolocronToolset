# Tutorial: Creating a new store

This tutorial adds a new store the player can buy from or sell to by creating a merchant (UTM), an NPC with dialog, a dialog file (DLG), and a script that opens the store. The NPC is placed on the Ebon Hawk.

## Step 1: Create the merchant file (UTM)

Create a new merchant. Set **Tag** and **ResRef** to match the filename (e.g. **aarn_store**). **Mark Up** / **Mark Down** control pricing (e.g. Mark Down 50 = player sells at half base price). Use **Edit Inventory** to add items and right-click to toggle infinite stock. Save; filename must match ResRef/Tag.

![Merchant](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2a.png)
![Inventory](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2b.png)
![Edit inventory](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2c.png)

## Step 2: Create the NPC (UTC)

Base the NPC on **c_jawa** (Core tab). Set **Tag** and **ResRef** to match the filename (e.g. **aarn**). Set the **Conversation** field to **aarn** (same as the DLG we will create). Give a name via the ellipsis → None → type **aarn**. Save.

![NPC from template](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2d.png)
![Conversation link](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2e.png)

## Step 3: Create the dialog (DLG)

Create a simple dialog: NPC says hello; options "Browse Aarn's wares" and "Leave". For the option that opens the store, set **Script #1** ResRef to `aarn_openstore`. Save as `aarn`.

![Dialog](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2f.png)
![Script link](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2g.png)

## Step 4: Create the Open-Store Script (NSS)

Create script ***aarn_openstore*** with:

```nwscript
void main()
{
    object oStore = GetObjectByTag("aarn_store");
    object oSpeaker = GetPCSpeaker();

    if (GetIsObjectValid(oStore))
    {
        DelayCommand(0.5, OpenStore(oStore, oSpeaker));
    }
}
```

The tag in `GetObjectByTag()` must match the UTM *Tag*. Save and **File** → **Compile**.

![Compile](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2z.png)

## Step 5: Place the NPC and store on the Ebon Hawk

In the **Modules** tab select **Ebon Hawk [ebo_m12aa.rim]** (or the .mod if you use K1CP). Open the GIT `m12aa` under **Module Data**. Add a **Creature** and a **Store** in the central room; **Edit Instance** on each and set their resrefs to `aarn` and `aarn_store`. Save the GIT (it writes into the module).

![Select module](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2h.png)
![Place creature and store](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2i.png)
![Edit instance](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2j.png)
![Link files](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2k.png)

## Step 6: Test

Use a save from before escaping Taris (or `warp ebo_m12aa` with cheats). Talk to the NPC and choose to browse; the store should open.

![Override Layout](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2x.png)
![In-Game](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2l.png)
![Store](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2m.png)
![Result](https://raw.githubusercontent.com/OpenKotOR/HolocronToolset/refs/heads/master/src/toolset/help/tutorials/2n.png)

### See also

- [Tutorial: Creating custom robes](Tutorial-Creating-Custom-Robes) -- Item creation and texture workflow
- [Tutorial: Creating static cameras](Tutorial-Creating-Static-Cameras) -- Camera placement in modules
- [Tutorial: Area transitions](Tutorial-Area-Transitions) -- Connecting areas with doors and triggers
- [GFF-UTM](GFF-File-Format#utm-merchant) -- Merchant (UTM) Format
- [GFF-UTC](GFF-Creature-and-Dialogue#utc) -- Creature (UTC) Format
- [GFF-DLG](GFF-Creature-and-Dialogue#dlg) -- Dialogue (DLG) Format
- [Mod Creation Best Practices](Mod-Creation-Best-Practices) -- Testing, merges, compatibility
