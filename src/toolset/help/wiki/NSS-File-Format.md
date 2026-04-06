# NSS — NWScript Source

NSS files contain human-readable NWScript source code — the scripting language that controls game logic in Knights of the Old Republic and The Sith Lords ([`NssParser` L80](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compiler/parser.py#L80), [xoreos-tools `src/nwscript/`](https://github.com/xoreos/xoreos-tools/tree/master/src/nwscript)). The engine does not execute NSS directly; source files are compiled to [NCS bytecode](NCS-File-Format) before they can run ([`InbuiltNCSCompiler.compile_script` L51](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compilers.py#L51), [KotOR-Scripting-Tool](https://github.com/KobaltBlu/KotOR-Scripting-Tool)). The master include file `nwscript.nss` defines all engine-exposed functions and constants available to scripts; KotOR and TSL each ship their own version with game-specific additions ([`KOTOR_FUNCTIONS` L3268](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L3268), [`KOTOR_CONSTANTS` L12](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L12), [Vanilla_KOTOR_Script_Source](https://github.com/KOTORCommunityPatches/Vanilla_KOTOR_Script_Source)).

NWScript is a C-like language with strong typing, automatic garbage collection for strings, and a fixed set of engine action routines ([reone `VirtualMachine` L41](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/include/reone/script/virtualmachine.h#L41), [xoreos `src/aurora/nwscript/`](https://github.com/xoreos/xoreos/tree/master/src/aurora/nwscript), [KotOR.js `NWScript` L39](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScript.ts#L39)). Scripts interact with the game world through these action routines — spawning creatures, modifying objects, running dialogue branches, applying effects — and are triggered from [GFF](GFF-File-Format) resources: [DLG](GFF-Creature-and-Dialogue#dlg) dialogue files, [UTC](GFF-File-Format#utc-creature) creatures, [UTD](GFF-Spatial-Objects#utd) doors, [UTP](GFF-Spatial-Objects#utp) placeables, and [IFO](GFF-Module-and-Area#ifo) module definitions. Scripts also commonly read [2DA](2DA-File-Format) configuration data at runtime. Like all resources, NSS files are resolved through the standard [resource resolution order](Concepts#resource-resolution-order) (override → MOD/SAV → KEY/BIF).

For community guidance, modding guides, and historical compile workflows, see the [Deadly Stream Tutorials forum](https://deadlystream.com/forum/25-tutorials/) and the hub on [Home — community sources and archives](Home#community-sources-and-archives). A nwnnsscomp-era compile tutorial is archived at [LucasForums: How to compile scripts?](https://www.lucasforumsarchive.com/thread/143681), and an introductory series at [KotOR Modding Tutorial Series on Deadly Stream](https://deadlystream.com/topic/6886-tutorial-kotor-modding-tutorial-series/) (some referenced tools are outdated — prefer Holocron Toolset and this wiki for current paths). The original shipped K1 scripts are preserved in [Vanilla_KOTOR_Script_Source](https://github.com/KOTORCommunityPatches/Vanilla_KOTOR_Script_Source). Forum posts are peer guidance; verify behavioral claims against the source implementations cited on this page.

## PyKotor Implementation

PyKotor implements `nwscript.nss` definitions in three Python modules:

### data structures

**`Libraries/PyKotor/src/pykotor/common/script.py`:**

- `ScriptFunction`: Represents a function signature with return type, name, parameters, description, and raw string
- `ScriptParam`: Represents a function parameter with type, name, and optional default value
- `ScriptConstant`: Represents a constant with type, name, and value
- `DataType`: Enumeration of all NWScript data types (INT, [float](GFF-File-Format), string, OBJECT, vector, etc.)

**`Libraries/PyKotor/src/pykotor/common/scriptdefs.py`:**

- `KOTOR_FUNCTIONS`: List of 772 `ScriptFunction` objects for KotOR 1
- `TSL_FUNCTIONS`: List of functions for KotOR 2 (The Sith Lords)
- `KOTOR_CONSTANTS`: List of 1489 `ScriptConstant` objects for KotOR 1
- `TSL_CONSTANTS`: List of constants for KotOR 2

**`Libraries/PyKotor/src/pykotor/common/scriptlib.py`:**

- `KOTOR_LIBRARY`: Dictionary mapping library file names to their source code content (e.g., `"k_inc_generic"`, `"k_inc_utility"`)
- `TSL_LIBRARY`: Dictionary for KotOR 2 library files

### Compilation Integration


1. **Parser Initialization**: The `NssParser` is created with game-specific functions and constants:

   ```python
   nss_parser = NssParser(
       functions=KOTOR_FUNCTIONS if game.is_k1() else TSL_FUNCTIONS,
       constants=KOTOR_CONSTANTS if game.is_k1() else TSL_CONSTANTS,
       library=KOTOR_LIBRARY if game.is_k1() else TSL_LIBRARY,
       library_lookup=lookup_arg,
   )
   ```

2. **Function Resolution**: When the parser encounters a function call, it:
   - Looks up the function name in the functions list
   - Validates parameter types and counts
   - Resolves the routine number (index in the functions list)
   - Generates an `ACTION` instruction with the routine number

3. **Constant Resolution**: When the parser encounters a constant:
   - Looks up the constant name in the constants list
   - Replaces the constant with its value
   - Generates appropriate `CONSTx` instruction

4. **Library Inclusion**: When the parser encounters `#include`:
   - Looks up the library name in the library dictionary
   - Parses the included source code
   - Merges functions and constants into the current scope

- [`script.py` L21+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/script.py#L21) (data structures)
- [`KOTOR_CONSTANTS` L12+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L12) (constants)
- [`KOTOR_FUNCTIONS` L3268+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L3268) (function signatures)
- [`scriptlib.py` L5+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptlib.py#L5) (`#include` library text)
- [`compilers.py` `InbuiltNCSCompiler` L28+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compilers.py#L28)
- [`parser.py` `NssParser` L80+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compiler/parser.py#L80)

---

## Shared Functions (K1 & TSL)

<!-- SHARED_FUNCTIONS_START -->

### Abilities and Stats

See [Abilities and Stats](NSS-File-Format#abilities-and-stats) for detailed documentation.

### Actions

See [Actions](NSS-File-Format#actions) for detailed documentation.

### Alignment System

See [Alignment System](NSS-File-Format#alignment-system) for detailed documentation.

### Class System

See [Class System](NSS-File-Format#class-system) for detailed documentation.

### Combat Functions

See [Combat Functions](NSS-File-Format#combat-functions) for detailed documentation.

### Dialog and Conversation Functions

See [Dialog and Conversation Functions](NSS-File-Format#dialog-and-conversation-functions) for detailed documentation.

### Effects System

See [Effects System](NSS-File-Format#effects-system) for detailed documentation.

### Global Variables

See [Global Variables](NSS-File-Format#global-variables) for detailed documentation.

### Item Management

See [Item Management](NSS-File-Format#item-management) for detailed documentation.

### Item Properties

See [Item Properties](NSS-File-Format#item-properties) for detailed documentation.

### Local Variables

See [Local Variables](NSS-File-Format#local-variables) for detailed documentation.

### Module and Area Functions

See [Module and Area Functions](NSS-File-Format#module-and-area-functions) for detailed documentation.

### Object Query and Manipulation

See [Object Query and Manipulation](NSS-File-Format#object-query-and-manipulation) for detailed documentation.

### Other Functions

See [Other Functions](NSS-File-Format#other-functions) for detailed documentation.

### Party Management

<a id="addavailablenpcbyobject"></a>


- `694. AddAvailableNPCByObject`
- This adds a NPC to the list of available party members using
- a game object as the template
- Returns if true if successful, false if the NPC had already
- been added or the object specified is invalid

- `nNPC`: int
- `oCreature`: object

<a id="addavailablenpcbytemplate"></a>


- `697. AddAvailableNPCByTemplate`
- This adds a NPC to the list of available party members using
- a template
- Returns if true if successful, false if the NPC had already
- been added or the template specified is invalid

- `nNPC`: int
- `sTemplate`: string

<a id="addpartymember"></a>


- `574. AddPartyMember`
- Adds a creature to the party
- Returns whether the addition was successful
- AddPartyMember

- `nNPC`: int
- `oCreature`: object

<a id="addtoparty"></a>


- `572. AddToParty`
- Add oPC to oPartyLeader's party.  This will only work on two PCs.
- - oPC: player to add to a party
- - oPartyLeader: player already in the party

- `oPC`: object
- `oPartyLeader`: object

<a id="getpartyaistyle"></a>

#### `GetPartyAIStyle()` - Routine 704

- `704. GetPartyAIStyle`
- Returns the party ai style

<a id="getpartymemberbyindex"></a>

#### `GetPartyMemberByIndex(nIndex)` - Routine 577

- `577. GetPartyMemberByIndex`
- Returns the party member at a given index in the party.
- The order of members in the party can vary based on
- who the current leader is (member 0 is always the current
- party leader).
- GetPartyMemberByIndex

- `nIndex`: int

<a id="getpartymembercount"></a>

#### `GetPartyMemberCount()` - Routine 126

- `126. GetPartyMemberCount`
- GetPartyMemberCount
- Returns a count of how many members [ARE](GFF-File-Format) in the party including the player character

<a id="isnpcpartymember"></a>


- `699. IsNPCPartyMember`
- Returns if a given NPC constant is in the party currently

- `nNPC`: int

<a id="isobjectpartymember"></a>


- `576. IsObjectPartyMember`
- Returns whether a specified creature is a party member
- IsObjectPartyMember

- `oCreature`: object

<a id="removefromparty"></a>


- `573. RemoveFromParty`
- Remove oPC from their current party. This will only work on a PC.
- - oPC: removes this player from whatever party they're currently in.

- `oPC`: object

<a id="removepartymember"></a>


- `575. RemovePartyMember`
- Removes a creature from the party
- Returns whether the removal was syccessful
- RemovePartyMember

- `nNPC`: int

<a id="setpartyaistyle"></a>

#### `SetPartyAIStyle(nStyle)` - Routine 706

- `706. SetPartyAIStyle`
- Sets the party ai style

- `nStyle`: int

<a id="setpartyleader"></a>

#### `SetPartyLeader(nNPC)` - Routine 13

- `13. SetPartyLeader`
- Sets (by NPC constant) which party member should be the controlled
- character

- `nNPC`: int

<a id="showpartyselectiongui"></a>


- `712. ShowPartySelectionGUI`
- ShowPartySelectionGUI
- Brings up the party selection [GUI](GFF-File-Format) for the player to
- select the members of the party from
- if exit script is specified, will be executed when
- the [GUI](GFF-File-Format) is exited

- `sExitScript`: string (default: ``)
- `nForceNPC1`: int
- `nForceNPC2`: int

<a id="switchplayercharacter"></a>


- `11. SwitchPlayerCharacter`
- Switches the main character to a specified NPC
- -1 specifies to switch back to the original PC

- `nNPC`: int

### Player Character Functions

See [Player Character Functions](NSS-File-Format#player-character-functions) for detailed documentation.

### Skills and Feats

See [Skills and Feats](NSS-File-Format#skills-and-feats) for detailed documentation.

### Sound and Music Functions

See [Sound and Music Functions](NSS-File-Format#sound-and-music-functions) for detailed documentation.

## K1-Only Functions

<!-- K1_ONLY_FUNCTIONS_START -->

### Other Functions

See [Other Functions](NSS-File-Format#other-functions) for detailed documentation.

## TSL-Only Functions

<!-- TSL_ONLY_FUNCTIONS_START -->

### Actions

See [Actions](NSS-File-Format#actions) for detailed documentation.

### Class System

See [Class System](NSS-File-Format#class-system) for detailed documentation.

### Combat Functions

Shared combat routines: [NSS-Shared-Functions-Combat-Functions](NSS-File-Format#combat-functions). TSL category index: [NSS-TSL-Only-Functions-Combat-Functions](NSS-File-Format#combat-functions).

### Dialog and Conversation Functions

See [Dialog and Conversation Functions](NSS-File-Format#dialog-and-conversation-functions) for detailed documentation.

### Effects System

See [Effects System](NSS-File-Format#effects-system) for detailed documentation.

### Global Variables

See [Global Variables](NSS-File-Format#global-variables) for detailed documentation.

### Item Management

See [Item Management](NSS-File-Format#item-management) for detailed documentation.

### Object Query and Manipulation

See [Object Query and Manipulation](NSS-File-Format#object-query-and-manipulation) for detailed documentation.

### Other Functions

See [Other Functions](NSS-File-Format#other-functions) for detailed documentation.

### Party Management

<a id="addavailablepupbyobject"></a>

#### `AddAvailablePUPByObject(nPUP, oPuppet)`

- 837
- RWT-OEI 07/17/04
- This function adds a Puppet to the Puppet Table by
- creature ID
- Returns 1 if successful, 0 if there was an error

- `nPUP`: int
- `oPuppet`: object

<a id="addavailablepupbytemplate"></a>

#### `AddAvailablePUPByTemplate(nPUP, sTemplate)`

- 836
- RWT-OEI 07/17/04
- This function adds a Puppet to the Puppet Table by
- template.
- Returns 1 if successful, 0 if there was an error

- `nPUP`: int
- `sTemplate`: string

<a id="addpartypuppet"></a>

#### `AddPartyPuppet(nPUP, oidCreature)`

- 840
- RWT-OEI 07/18/04
- This adds an existing puppet object to the party. The
- puppet object must already exist via SpawnAvailablePUP
- and must already be available via AddAvailablePUP*

- `nPUP`: int
- `oidCreature`: object

<a id="getispartyleader"></a>

#### `GetIsPartyLeader(oCharacter)`

- 844
- RWT-OEI 07/21/04
- Returns TRUE if the object ID passed is the character
- that the player is actively controlling at that point.
- Note that this function is *NOT* able to return correct

- `oCharacter`: object

<a id="getpartyleader"></a>

#### `GetPartyLeader()`

- 845
- RWT-OEI 07/21/04
- Returns the object ID of the character that the player
- is actively controlling. This is the 'Party Leader'.
- Returns object Invalid on error

<a id="removenpcfrompartytobase"></a>

#### `RemoveNPCFromPartyToBase(nNPC)`

- 846
- JAB-OEI 07/22/04
- Will remove the CNPC from the 3 person party, and remove
- him/her from the area, effectively sending the CNPC back
- to the base. The CNPC data is still stored in the

- `nNPC`: int

### Player Character Functions

See [Player Character Functions](NSS-File-Format#player-character-functions) for detailed documentation.

### Skills and Feats

See [Skills and Feats](NSS-File-Format#skills-and-feats) for detailed documentation.

### Sound and Music Functions

Shared routines: [NSS-Shared-Functions-Sound-and-Music](NSS-File-Format#sound-and-music-functions). This **TSL-Only** heading also covers UI-related symbols listed in the [table of contents](#tsl-only-functions) (`DisplayDatapad`, `DisplayMessageBox`, `PlayOverlayAnimation`); see [NSS-TSL-Only-Functions-Sound-and-Music-Functions](NSS-File-Format#sound-and-music-functions) for that index note.

## Shared Constants (K1 & TSL)

<!-- SHARED_CONSTANTS_START -->

### Ability Constants

See [Ability Constants](NSS-File-Format#ability-constants) for detailed documentation.

### Alignment Constants

See [Alignment Constants](NSS-File-Format#alignment-constants) for detailed documentation.

### Class type Constants

See [Class type Constants](NSS-File-Format#class-type-constants) for detailed documentation.

### Inventory Constants

See [Inventory Constants](NSS-File-Format#inventory-constants) for detailed documentation.

### NPC Constants

See [NPC Constants](NSS-File-Format#npc-constants) for detailed documentation.

### Object type Constants

See [Object type Constants](NSS-File-Format#object-type-constants) for detailed documentation.

### Other Constants

See [Other Constants](NSS-File-Format#other-constants) for detailed documentation.

### Planet Constants

See [Planet Constants](NSS-File-Format#planet-constants) for detailed documentation.

### Visual Effects (VFX)

Visual effect constants define particle effects, lighting, and environmental effects available through NWScript. Both K1 and TSL share a common set of VFX constants prefixed with `VFX_` that can be applied to objects, locations, and beams.

## K1-Only Constants

<!-- K1_ONLY_CONSTANTS_START -->

### NPC Constants

See [NPC Constants](NSS-File-Format#npc-constants) for detailed documentation.

### Other Constants

See [Other Constants](NSS-File-Format#other-constants) for detailed documentation.

### Planet Constants

See [Planet Constants](NSS-File-Format#planet-constants) for detailed documentation.

## TSL-Only Constants

<!-- TSL_ONLY_CONSTANTS_START -->

### Class type Constants

See [Class type Constants](NSS-File-Format#class-type-constants) for detailed documentation.

### Inventory Constants

See [Inventory Constants](NSS-File-Format#inventory-constants) for detailed documentation.

### NPC Constants

See [NPC Constants](NSS-File-Format#npc-constants) for detailed documentation.

### Other Constants

See [Other Constants](NSS-File-Format#other-constants) for detailed documentation.

### Planet Constants

See [Planet Constants](NSS-File-Format#planet-constants) for detailed documentation.

### Visual Effects (VFX)

TSL adds additional VFX constants beyond the shared set, including force power visual effects and expanded environmental effects specific to TSL areas.

## KOTOR Library files

<!-- KOTOR_LIBRARY_START -->

<a id="k_inc_cheat"></a>

#### `k_inc_cheat`

**Description**: :: k_inc_cheat

**Usage**: `#include "k_inc_cheat"`

**Source Code**:

```c
//:: k_inc_cheat
/*
    This will be localized area for all
    Cheat Bot scripting.
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
#include "k_inc_debug"
//Takes a PLANET_ Constant
void CH_SetPlanetaryGlobal(int nPlanetConstant);
//Makes the specified party member available to the PC
void CH_SetPartyMemberAvailable(int nNPC);
//::///////////////////////////////////////////////
//:: Set Planet Local
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
    VARIABLE = K_CURRENT_PLANET
        Endar Spire     5
        Taris           10
        Dantooine       15
        --Kashyyk       20
        --Manaan        25
        --Korriban      30
        --Tatooine      35
        Leviathan       40
        Unknown World   45
        Star Forge      50
*/
//:://////////////////////////////////////////////
//:: Created By: Preston Watamaniuk
//:: Created On: Oct 16, 2002
//:://////////////////////////////////////////////
void CH_SetPlanetaryGlobal(int nPlanetConstant)
{
    if(nPlanetConstant == PLANET_ENDAR_SPIRE)
    {
        SetGlobalNumber("K_CURRENT_PLANET", 5);
    }
    else if(nPlanetConstant == PLANET_TARIS)
    {
        SetGlobalNumber("K_CURRENT_PLANET", 10);
    }
    else if(nPlanetConstant == PLANET_DANTOOINE)
    {
        SetGlobalNumber("K_CURRENT_PLANET", 15);
    }
    else if(nPlanetConstant == PLANET_KASHYYYK)
    {
        SetGlobalNumber("K_CURRENT_PLANET", 20);
... (77 more lines)
```

<a id="k_inc_dan"></a>

#### `k_inc_dan`

**Description**: Dan

**Usage**: `#include "k_inc_dan"`

**Source Code**:

```c
#include "k_inc_generic"
#include "k_inc_utility"
int ROMANCE_DONE = 4;
int JUHANI_RESCUED = 1;
int JEDI_TRAINING_DONE = 7;
int JEDI_PATH_GUARDIAN = 1;
int JEDI_PATH_SENTINEL = 2;
int JEDI_PATH_CONSULAR = 3;
int DROID_STARTED = 1;
int DROID_DESTROYED = 2;
int DROID_DECEIVED = 3;
int DROID_RETURNED = 4;
int DROID_HELPED = 5;
int DROID_FINISHED = 6;
string sBastilaTag = "bastila";
string sCarthTag = "carth";
string sCouncilTag = "dan13_WP_council";
string SABER_BLUE = "g_w_lghtsbr01";
string SABER_GREEN = "g_w_lghtsbr03";
string SABER_GOLD = "g_w_lghtsbr04";
string WANDERING_HOUND_TAG = "dan_wanderhound";
//places an instance of a character based on the tag/template
// **TAG MUST BE THE SAME AS TEMPLATE**
void PlaceNPC(string sTag, string sLocation = "");
//Get Carth's Object
object GetCarth();
//Gets Bastila's object
object GetBastila();
//gets the center of the council chamber
vector GetChamberCenter();
// creature move along a waypoint path. Not interuptable.
void PlotMove(string sWayPointTag,int nFirst, int nLast, int nRun = FALSE);
// creature move along a waypoint path. Not interuptable. Destroys self at the end
void PlotLeave(string sWayPointTag,int nFirst, int nLast, int nRun = FALSE);
// returns true is a trigger has not been fired yet
// intended for one shot triggers
int HasNeverTriggered();
//returns true if, on Korriban, the player has convinced Yuthura to come to Dantooine.
int YuthuraHasDefected();
//Sets the progression of the Elise plot on Dantooine
void SetElisePlot(int nValue);
// returns true if the player has started the Elise plot
int ElisePlotStarted();
// returns true if the player has agreed to help the droid after it has returned to elise
int GetDroidHelped();
// returns true if c369 has been spoken to
int GetEliseDroidMet();
//  the Elise plot has not started yet
int GetElisePlotNeverStared();
// returns true if Elise has gone to the Jedi compund
... (283 more lines)
```

<a id="k_inc_debug"></a>

#### `k_inc_debug`

**Description**: ::///////////////////////////////////////////////

**Usage**: `#include "k_inc_debug"`

**Source Code**:

```c
//::///////////////////////////////////////////////
//:: KOTOR Debug Include
//:: k_inc_debug
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
    This contains the functions for inserting
    debug information into the scripts.
    This include will use Db as its two letter
    function prefix.
*/
//:://////////////////////////////////////////////
//:: Created By: Preston Watamaniuk
//:: Created On: June 12, 2002
//:://////////////////////////////////////////////
//Inserts a print string into the log file for debugging purposes.
void Db_MyPrintString(string sString);
//Makes the object running the script say a speak string.
void Db_MySpeakString(string sString);
//Makes the nearest PC say a speakstring.
void Db_AssignPCDebugString(string sString);
//Basically, a wrapper for AurPostString
void Db_PostString(string sString = "",int x = 5,int y = 5,float fShow = 1.0);
//::///////////////////////////////////////////////
//:: Debug Print String
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
    Inserts a print string into the log file for
    debugging purposes.
*/
//:://////////////////////////////////////////////
//:: Created By: Preston Watamaniuk
//:: Created On: June 12, 2002
//:://////////////////////////////////////////////
void Db_MyPrintString(string sString)
{
    if(!ShipBuild())
    {
        PrintString(sString);
    }
}
//::///////////////////////////////////////////////
//:: Debug Speak String
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
    Makes the object running the script say a
    speak string.
*/
... (47 more lines)
```

<a id="k_inc_drop"></a>

#### `k_inc_drop`

**Description**: ::///////////////////////////////////////////////

**Usage**: `#include "k_inc_drop"`

**Source Code**:

```c
//::///////////////////////////////////////////////
//:: KOTOR Treasure drop Include
//:: k_inc_drop
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
// Contains the functions for handling creatures dropping random treasure
//Only human creatures not of the beast subrace willdrop treasure dependant
//on their hit dice
//:://////////////////////////////////////////////
//:: Created By: Aidan Scanlan On: 02/06/03
//:://////////////////////////////////////////////
int DR_HIGH_LEVEL = 15;
int DR_MEDIUM_LEVEL = 10;
int DR_LOW_LEVEL = 5;
int DR_SUBRACE_BEAST = 2;
//Checks for treasure drop conditions. Returns True if treasure will drop
int DR_SpawnCreatureTreasure(object oTarget = OBJECT_SELF);
//Dependant on the level of a creature drops treasure from a list
void DR_CreateRandomTreasure(object oTarget = OBJECT_SELF);
// creates a low level treasure: med pack/repair, frag grenade, credits
void DR_CreateLowTreasure();
// creates midlevel treasure: adv-med/repair, any gredade, stims, credits
void DR_CreateMidTreasure();
// creates high treasure: adv stims, grenades, ultra med/repair, credits
void DR_CreateHighTreasure();
// Creates 1-4 credits
void DR_CreateFillerCredits();
/////////////////////////////////////////////////////////////////////////
//Checks for treasure drop conditions. Returns True if treasure will drop
int DR_SpawnCreatureTreasure(object oTarget = OBJECT_SELF)
{
    int nRace = GetRacialType(oTarget);
    int nFaction = GetStandardFaction(oTarget);
    int nSubRace = GetSubRace(oTarget);
    if(Random(4) == 0 &&
       nRace != RACIAL_TYPE_DROID &&
       nSubRace != DR_SUBRACE_BEAST)
    {
        //AurPostString("will drop",5,5,5.0);
        DR_CreateRandomTreasure(oTarget);
        return TRUE;
    }
    return FALSE;
}
//Dependant on the level of a creature drops treasure from a list
void DR_CreateRandomTreasure(object oTarget = OBJECT_SELF)
{
    int nLevel = GetHitDice(oTarget);
    if (nLevel > DR_HIGH_LEVEL)
    {
... (185 more lines)
```

<a id="k_inc_ebonhawk"></a>

#### `k_inc_ebonhawk`

**Description**: :: k_inc_ebonhawk

**Usage**: `#include "k_inc_ebonhawk"`

**Source Code**:

```c
//:: k_inc_ebonhawk
/*
     Ebon Hawk include file
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
//This checks the Star Map plot to see if it is at state 30.
int EBO_CheckStarMapPlot();
//Bastila intiates conversation with the PC
void EBO_BastilaStartConversation2();
//Should Bastila intiates conversation with the PC
int EBO_ShouldBastilaStartConversation();
//Bastila intiates conversation with the PC
void EBO_BastilaStartConversation2();
//Advances the state of the bounty hunters plot after galaxy map selections are made
void EBO_PlayBountyHunterCutScene();
//Play the current cutscene for taking off from the planet.
void EBO_PlayTakeOff(int nCurrentPlanet);
//Play the corrent cutscene for landing on the planet.
void EBO_PlayLanding(int nDestination);
//Creates items on the PC based on the NPC they are talking to.
void EBO_CreateEquipmentOnPC();
//Checks if the PC needs equipment based on the NPC they are talking to.
int EBO_GetIsEquipmentNeeded();
//Determines the number items held with specific tags
int EBO_CheckInventoryNumbers(string sTag1, string sTag2 = "", string sTag3 = "", string sTag4 = "");
//Returns the scripting constant for the current planet.
int EBO_GetCurrentPlanet();
//Returns the scripting constant for the future planet.
int EBO_GetFuturePlanet();
//Returns the correct K_CURRENT_PLANET value when a Planetary.2DA index is passed in.
int EBO_GetPlanetFrom2DA(int nPlanetIndex);
//Starts the correct sequence based on the planet being traveled to.
void EBO_PlayRenderSequence();
//::///////////////////////////////////////////////
//:: Check Star Map
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
    If the variable K_STAR_MAP is at 30 and
    the variable K_CAPTURED_LEV = 5 then
    run the leviathan module.
    K_CAPTURED_LEV States
    0 = Pre Leviathan
    5 = Captured
    10 = Escaped
*/
//:://////////////////////////////////////////////
//:: Created By: Preston Watamaniuk
//:: Created On: Oct 3, 2002
... (800 more lines)
```

<a id="k_inc_end"></a>

#### `k_inc_end`

**Description**: End

**Usage**: `#include "k_inc_end"`

**Source Code**:

```c
#include "k_inc_utility"
#include "k_inc_generic"
string sTraskTag = "end_trask";
string sTraskWP = "endwp_tarsk01";
string sCarthTag = "Carth";
string SOLDIER_WEAPON = "g_w_blstrrfl001";
string SOLDIER_ITEM01 = "g_i_adrnaline003";
string SOLDIER_ITEM02 = "";
string SCOUT_WEAPON = "g_w_blstrpstl001";
string SCOUT_ITEM01 = "g_i_adrnaline002";
string SCOUT_ITEM02 = "g_i_implant101";
string SCOUNDREL_WEAPON = "g_w_blstrpstl001";
string SCOUNDREL_ITEM01 = "g_i_secspike01";
string SCOUNDREL_ITEM02 = "g_i_progspike01";
int ROOM3_DEAD = 3;
int ROOM5_DEAD = 4;
int ROOM7_DEAD = 2;
int TRASK_DEFAULT = -1;
int TRASK_MUST_GET_GEAR = 0;
int TRASK_GEAR_DONE = 1;
int TRASK_TARGET_DONE = 2;
int TRASK_MUST_EQUIP = 3;
int TRASK_EQUIP_DONE = 4;
int TRASK_MUST_MAP = 5;
int TRASK_MAP_DONE = 6;
int TRASK_MUST_SWITCH = 7;
int TRASK_SWITCH_DONE = 8;
int TRASK_SWITCH_REMIND = 9;
int TRASK_CARTH_BRIDGE = 10;
int TRASK_BRIDGE_DONE = 11;
int TRASK_MUST_DOOR = 12;
int TRASK_DOOR_DONE = 13;
int TRASK_ROOM3_DONE = 14;
int TRASK_MUST_MEDPACK = 15;
int TRASK_COMBAT_WARNING = 16;
int TRASK_COMBAT_WARNING2 = 17;
int TRASK_COMPUTER_DONE = 18;
int TRASK_MUST_DROID = 19;
int TRASK_DROID_DONE = 20;
int TRASK_MUST_MAP_02 = 21;
int TRASK_NOTHING_02 = 22;
//int TRASK_COMBAT_WARNING = 27;
int TRASK_LEVEL_INIT = 28;
int TRASK_MUST_LEVEL = 29;
int TRASK_PARTY_LEVEL = 30;
int TRASK_LEVEL_DONE = 31;
string LOCKER_TAG = "end_locker01";
string STEALTH_UNIT = "g_i_belt010";
//returns Trask's object id
object GetTrask();
... (194 more lines)
```

<a id="k_inc_endgame"></a>

#### `k_inc_endgame`

**Description**: ::///////////////////////////////////////////////

**Usage**: `#include "k_inc_endgame"`

**Source Code**:

```c
//::///////////////////////////////////////////////
//:: Name k_inc_endgame
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
     This include houses all of the stunt/render
     calls for the end game. This will be for
     modules sta_m45ac and sta_m45ad.
*/
//:://////////////////////////////////////////////
//:: Created By: Brad Prince
//:: Created On: Mar 6, 2003
//:://////////////////////////////////////////////
///////////////////////
// LIGHT SIDE scenes //
///////////////////////
// SCENE 1 BO2 - Player kills Bastila on sta_m45ac
void ST_PlayBastilaLight();
// SCENE 2 C01 - Player returns after watching SCENE 1.
void ST_PlayReturnToStarForgeLight();
// SCENE 3 A - Star Forge under attack.
void ST_PlayStarForgeUnderAttack();
// SCENE 4 B - End game credits - Light.
void ST_PlayEndCreditsLight();
//////////////////////////////////////////////////
//////////////////////
// DARK SIDE scenes //
//////////////////////
// SCENE 1 B01 - Bastila leaves party to meditate before generator puzzle.
void ST_PlayBastilaDark();
// SCENE 2 C - Player returns after watching SCENE 1.
void ST_PlayReturnToStarForgeDark();
// SCENE 3 A - The Republic dies.
void ST_PlayRepublicDies();
// SCENE 4 B - The Sith Ceremony.
void ST_PlaySithCeremony();
// SCENE 5 C - End game credits - Dark.
void ST_PlayEndCreditsDark();
//////////////////////////////////////////////////
//                  FUNCTIONS                   //
//////////////////////////////////////////////////
///////////////////////
// LIGHT SIDE scenes //
///////////////////////
// SCENE 1 BO2 - Player kills Bastila on sta_m45ac
void ST_PlayBastilaLight()
{
    StartNewModule("STUNT_50a","", "50b");
}
// SCENE 2 C01 - Player returns after watching SCENE 1.
... (44 more lines)
```

<a id="k_inc_force"></a>

#### `k_inc_force`

**Description**: :: k_inc_force

**Usage**: `#include "k_inc_force"`

**Source Code**:

```c
//:: k_inc_force
/*
    v1.0
    Force Powers Include for KOTOR
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
float fLightningDuration = 1.0;
//These variables are set in the script run area.
int SWFP_PRIVATE_SAVE_TYPE;
int SWFP_PRIVATE_SAVE_VERSUS_TYPE;
int SWFP_DAMAGE;
int SWFP_DAMAGE_TYPE;
int SWFP_DAMAGE_VFX;
int SWFP_HARMFUL;
int SWFP_SHAPE;
//Runs the script section for the particular force power.
void  Sp_RunForcePowers();
//Immunity and Resist Spell check for the force power.
//The eDamage checks whether the target is immune to the damage effect
int Sp_BlockingChecks(object oTarget, effect eEffect, effect eEffect2, effect eDamage);
//Makes the necessary saving throws
int Sp_MySavingThrows(object oTarget);
//Remove an effect of a specific type
void Sp_RemoveSpecificEffect(int nEffectTypeID, object oTarget);
//Remove an effect from a specific force power.
void Sp_RemoveSpellEffects(int nSpell_ID, object oCaster, object oTarget);
// Delays the application of a spell effect by an amount determined by distance.
float Sp_GetSpellEffectDelay(location SpellTargetLocation, object oTarget);
//Randomly delays the effect application for a default of 0.0 to 0.75 seconds
float Sp_GetRandomDelay(float fMinimumTime = 0.0, float MaximumTime = 0.75);
//Gets a saving throw appropriate to the jedi using the force power.
int Sp_GetJediDCSave();
///Apply effects in a sphere shape.
void Sp_SphereSaveHalf(object oAnchor, float fSize, int nCounter, effect eLink1, float fDuration1, effect eLink2, float fDuration);
//Apply effects to a single target.
void Sp_SingleTarget(object oAnchor, effect eLink1, float fDuration1, effect eLink2, float fDuration2);
//Apply effect to an area and negate on a save.
void Sp_SphereBlocking(object oAnchor, float fSize, int nCounter, effect eLink1, float fDuration1, effect eLink2, float fDuration);
// /Apply effect to an object and negate on a save.
void Sp_SingleTargetBlocking(object oAnchor, effect eLink1, float fDuration1, effect eLink2, float fDuration2);
//Apply effects for a for power.
void Sp_ApplyForcePowerEffects(float fTime, effect eEffect, object oTarget);
//Apply effects to targets.
void Sp_ApplyEffects(int nBlocking, object oAnchor, float fSize, int nCounter, effect eLink1, float fDuration1, effect eLink2, float fDuration2, int nRacial = RACIAL_TYPE_ALL);
//Removes all effects from the spells , Knights Mind, Mind Mastery and Battle Meditation
void Sp_RemoveBuffSpell();
//Prints a string for the spell stript
void SP_MyPrintString(string sString);
//Posts a string for the spell script
... (2163 more lines)
```

<a id="k_inc_generic"></a>

#### `k_inc_generic`

**Description**: :: k_inc_generic

**Usage**: `#include "k_inc_generic"`

**Source Code**:

```c
//:: k_inc_generic
/*
    v1.5
    Generic Include for KOTOR
    Post Clean Up as of March 3, 2003
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
#include "k_inc_gensupport"
#include "k_inc_walkways"
#include "k_inc_drop"
struct tLastRound
{
    int nLastAction;
    int nLastActionID;
    int nLastTalentCode;
    object oLastTarget;
    int nTalentSuccessCode;
    int nIsLastTargetDebil;
    int nLastCombo;
    int nLastComboIndex;
    int nCurrentCombo;
    int nBossSwitchCurrent;
};
struct tLastRound tPR;
//LOCAL BOOLEANS RANGE FROM 0 to 96
int AMBIENT_PRESENCE_DAY_ONLY = 1;        //POSSIBLE CUT
int AMBIENT_PRESENCE_NIGHT_ONLY = 2;      //POSSIBLE CUT
int AMBIENT_PRESENCE_ALWAYS_PRESENT = 3;
int SW_FLAG_EVENT_ON_PERCEPTION =   20;
int SW_FLAG_EVENT_ON_ATTACKED   =   21;
int SW_FLAG_EVENT_ON_DAMAGED    =   22;
int SW_FLAG_EVENT_ON_FORCE_AFFECTED = 23;
int SW_FLAG_EVENT_ON_DISTURBED = 24;
int SW_FLAG_EVENT_ON_COMBAT_ROUND_END = 25;
int SW_FLAG_EVENT_ON_DIALOGUE    = 26;
int SW_FLAG_EVENT_ON_DEATH       = 27;
int SW_FLAG_EVENT_ON_HEARTBEAT   = 28;
//int SW_FLAG_AMBIENT_ANIMATIONS = 29;          located in k_inc_walkways
//int SW_FLAG_AMBIENT_ANIMATIONS_MOBILE = 30;   located in k_inc_walkways
int SW_FLAG_FAST_BUFF            = 31;   //POSSIBLE CUT
int SW_FLAG_ASC_IS_BUSY          = 32;   //POSSIBLE CUT
int SW_FLAG_ASC_AGGRESSIVE_MODE  = 33;   //POSSIBLE CUT
int SW_FLAG_AMBIENT_DAY_ONLY     = 40;   //POSSIBLE CUT
int SW_FLAG_AMBIENT_NIGHT_ONLY   = 43;   //POSSIBLE CUT
int SW_FLAG_EVENT_ON_SPELL_CAST_AT = 44;
int SW_FLAG_EVENT_ON_BLOCKED     = 45;
int SW_FLAG_ON_DIALOGUE_COMPUTER = 48;
int SW_FLAG_FORMATION_POSITION_0 = 49;   //POSSIBLE CUT
int SW_FLAG_FORMATION_POSITION_1 = 50;   //POSSIBLE CUT
... (2182 more lines)
```

<a id="k_inc_gensupport"></a>

#### `k_inc_gensupport`

**Description**: :: k_inc_gensupport

**Usage**: `#include "k_inc_gensupport"`

**Source Code**:

```c
//:: k_inc_gensupport
/*
    v1.0
    Support Include for k_inc_generic
    NOTE - To get these functions
    use k_inc_generic
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
//BOSS ATTACK TYPES
int SW_BOSS_ATTACK_TYPE_GRENADE = 1;
int SW_BOSS_ATTACK_TYPE_FORCE_POWER = 2;
int SW_BOSS_ATTACK_TYPE_NPC = 3;
int SW_BOSS_ATTACK_TYPE_PC = 4;
int SW_BOSS_ATTACK_ANY = 5;
int SW_BOSS_ATTACK_DROID = 6;
//LOCAL NUMBERS
int SW_NUMBER_COMBO_ROUTINE = 3;
int SW_NUMBER_COMBO_INDEX = 4;
int SW_NUMBER_LAST_COMBO = 5;
int SW_NUMBER_ROUND_COUNTER = 6;
int SW_NUMBER_COMBAT_ZONE = 7;
//COMBO CONSTANTS
int SW_COMBO_RANGED_FEROCIOUS = 1;
int SW_COMBO_RANGED_AGGRESSIVE = 2;
int SW_COMBO_RANGED_DISCIPLINED = 3;
int SW_COMBO_RANGED_CAUTIOUS = 4;
int SW_COMBO_MELEE_FEROCIOUS = 5;
int SW_COMBO_MELEE_AGGRESSIVE = 6;
int SW_COMBO_MELEE_DISCIPLINED = 7;
int SW_COMBO_MELEE_CAUTIOUS = 8;
int SW_COMBO_BUFF_PARTY = 9;
int SW_COMBO_BUFF_DEBILITATE = 10;
int SW_COMBO_BUFF_DAMAGE = 11;
int SW_COMBO_BUFF_DEBILITATE_DESTROY = 12;
int SW_COMBO_SUPRESS_DEBILITATE_DESTROY = 13;
int SW_COMBO_SITH_ATTACK = 14;
int SW_COMBO_BUFF_ATTACK = 15;
int SW_COMBO_SITH_CONFOUND = 16;
int SW_COMBO_JEDI_SMITE = 17;
int SW_COMBO_SITH_TAUNT = 18;
int SW_COMBO_SITH_BLADE = 19;
int SW_COMBO_SITH_CRUSH = 20;
int SW_COMBO_JEDI_CRUSH = 21;
int SW_COMBO_SITH_BRUTALIZE = 22;
int SW_COMBO_SITH_DRAIN = 23;
int SW_COMBO_SITH_ESCAPE = 24;
int SW_COMBO_JEDI_BLITZ = 25;
int SW_COMBO_SITH_SPIKE = 26;
int SW_COMBO_SITH_SCYTHE = 27;
... (3004 more lines)
```

<a id="k_inc_kas"></a>

#### `k_inc_kas`

**Description**: ::///////////////////////////////////////////////

**Usage**: `#include "k_inc_kas"`

**Source Code**:

```c
//::///////////////////////////////////////////////
//:: Include
//:: k_inc_kas
//:: Copyright (c) 2002 Bioware Corp.
//:://////////////////////////////////////////////
/*
    This is the include file for Kashyyyk.
*/
//:://////////////////////////////////////////////
//:: Created By: John Winski
//:: Created On: July 29, 2002
//:://////////////////////////////////////////////
#include "k_inc_utility"
#include "k_inc_generic"
int GetGorwookenSpawnGlobal()
{
    return GetGlobalBoolean("kas_SpawnGorwook");
}
void SetGorwookenSpawnGlobal(int bValue)
{
    if (bValue == TRUE || bValue == FALSE)
    {
        SetGlobalBoolean("kas_SpawnGorwook", bValue);
    }
    return;
}
int GetEliBeenKilledGlobal()
{
    return GetGlobalBoolean("kas_elikilled");
}
void SetEliBeenKilledGlobal(int bValue)
{
    if (bValue == TRUE || bValue == FALSE)
    {
        SetGlobalBoolean("kas_elikilled", bValue);
    }
    return;
}
int GetJaarakConfessedGlobal()
{
    return GetGlobalBoolean("kas_JaarakConfessed");
}
void SetJaarakConfessedGlobal(int bValue)
{
    if (bValue == TRUE || bValue == FALSE)
    {
        SetGlobalBoolean("kas_JaarakConfessed", bValue);
    }
    return;
}
... (1263 more lines)
```

<a id="k_inc_lev"></a>

#### `k_inc_lev`

**Description**: ::///////////////////////////////////////////////

**Usage**: `#include "k_inc_lev"`

**Source Code**:

```c
//::///////////////////////////////////////////////
//:: k_inc_lev
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
  include file for leviathan
*/
//:://////////////////////////////////////////////
//:: Created By: Jason Booth
//:: Created On: August 26, 2002
//:://////////////////////////////////////////////
#include "k_inc_debug"
#include "k_inc_utility"
//mark an object for cleanup by the LEV_CleanupDeadObjects function
void LEV_MarkForCleanup(object obj);
//destroy all objects whose PLOT_10 flag has been set
void LEV_CleanupDeadObjects(object oArea);
//mark object for cleanup and move to nearest exit
void LEV_LeaveArea(object obj = OBJECT_SELF, int bRun = FALSE);
//fill container with treasure from table
void LEV_AddTreasureToContainer(object oContainer,int iTable,int iAmount);
//strip inventory from oTarget and put it in oDest
void LEV_StripCharacter(object oTarget,object oDest);
//::///////////////////////////////////////////////
//:: LEV_MarkForCleanup
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
//mark an object for cleanup by the TAR_CleanupDeadObjects function
*/
//:://////////////////////////////////////////////
//:: Created By: Jason Booth
//:: Created On: August 26, 2002
//:://////////////////////////////////////////////
void LEV_MarkForCleanup(object obj)
{
  UT_SetPlotBooleanFlag(obj,SW_PLOT_BOOLEAN_10,TRUE);
}
//::///////////////////////////////////////////////
//:: LEV_CleanupDeadObjects
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
//destroy all objects whose PLOT_10 flag has been set
*/
//:://////////////////////////////////////////////
//:: Created By: Jason Booth
//:: Created On: August 15, 2002
//:://////////////////////////////////////////////
void LEV_CleanupDeadObjects(object oArea)
... (117 more lines)
```

<a id="k_inc_man"></a>

#### `k_inc_man`

**Description**: :: Name

**Usage**: `#include "k_inc_man"`

**Source Code**:

```c
//:: Name
/*
     Desc
*/
//:: Created By:
//:: Copyright (c) 2002 Bioware Corp.
#include "k_inc_generic"
#include "k_inc_utility"
int SHIP_TAKEOFF_CUTSCENE = 1;
int SHIP_LANDING_CUTSCENE = 2;
int NONE = 0;
int QUEEDLE = 1;
int CASSANDRA = 2;
int JAX = 3;
int QUEEDLE_CHAMP = 4;
int QUEEDLE_TIME = 3012;
int CASSANDRA_TIME = 2702;
int JAX_TIME = 2548;
int CHAMP_TIME = 2348;
int PLOT_HARVEST_STOPPED = 3;
int PLOT_KOLTO_DESTROYED = 4;
//effect EFFECT_STEAM = EffectDamage(15);
int STEAM_DAMAGE_AMOUNT = 25;
string RACE_DEFAULT = GetStringByStrRef(32289);
string STEAM_PLACEABLE = "man27_visstm0";
string ROLAND_TAG = "man26_repdip";
void PlaceShip(string sTag,location lLoc);
void RemoveShip(string sTag);
void PlaceNPC(string sTag);
// switches current player models to envirosuit models.
void DonSuits();
// switches the envirosuit model back to the regular player models
void RemoveSuits();
// deactivates all turrets on the map with the corresponding tag
// if no tag is given it will default to the tag of the calling object
void DeactivateTurrets(string sTag = "");
//used to make a given condition only fire once
//***note uses SW_PLOT_BOOLEAN_10***
int HasNeverTriggered();
// Sets a global to track who the player is racing
void SetOpponent(int nOpponent);
//Returns thte current race opponent
int GetOpponent();
//Sets a cutom token in racetime format
void SetTokenRaceTime(int nToken, int nRacerTime);
//returns the main plot global for Manaan
int GetManaanMainPlotVariable();
// returns true if poison has been released if the Hrakert rift
int KoltoDestroyed();
// Removes instances and deactives Selkath encounters
... (748 more lines)
```

<a id="k_inc_stunt"></a>

#### `k_inc_stunt`

**Description**: :: Stunt/Render Include

**Usage**: `#include "k_inc_stunt"`

**Source Code**:

```c
//:: Stunt/Render Include
/*
     This Include File runs
     the stunt and cutscenes
     for the game.
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
//INDIVIDUAL STUNT MODULE CALLS ******************************************************************************************************
//LEV_A: Pulled out of hyperspace by the Leviathan, load STUNT_16
void ST_PlayLevCaptureStunt();
//LEV_A: Capture by the Leviathan, load ebo_m40aa
void ST_PlayLevCaptureStunt02();
//Load Turret Module Opening 07_3
void ST_PlayStuntTurret_07_3();
//Plays the Bastila torture scene
void ST_PlayBastilaTorture();
//Load Turret Module Opening 07_4
void ST_PlayStuntTurret_07_4();
//Load Leviathan Bombardment Stunt_06 covered by Render 5
void ST_PlayTarisEscape();
//Load Stunt_07 covered by Render 6a and 05_1C
void ST_PlayTarisEscape02();
//Load the Fighter Mini-Game m12ab covered by Render 07_3
void ST_PlayTarisEscape03();
//Load Dantooine module covered by hyperspace and dant landing
void ST_PlayDantooineLanding();
//Leaving Dantooine for the first time, going to STUNT_12 covered by Dant takeoff and hyperspace
void ST_PlayDantooineTakeOff();
//Plays the correct vision based on the value of K_FUTURE_PLANET from a stunt module
void ST_PlayVisionStunt();
//Plays the correct vision based on the value of K_FUTURE_PLANET with a take-off
void ST_PlayVisionStunt02();
//Plays the starforge approach
void ST_PlayStarForgeApproach();
//Plays the Damage Ebon Hawk Stunt scene
void ST_PlayStunt35();
//Shows the crash landing on the Unknown World
void ST_PlayUnknownWorldLanding();
//Shows the take-off from the Unknown World
void ST_PlayUnknownWorldTakeOff();
//Landing on the Star Forge
void ST_PlayStarForgeLanding();
//Goes to the Leviathan Mini-Game covered by the Escape Render
void ST_PlayLeviathanEscape01();
//UBER FUNCTIONS *********************************************************************************************************************
//This determines what to play after a Fighter Mini Game is run
void ST_PlayPostTurret();
//Play the appropriate take off render
string ST_GetTakeOffRender();
... (685 more lines)
```

<a id="k_inc_switch"></a>

#### `k_inc_switch`

**Description**: :: k_inc_switch

**Usage**: `#include "k_inc_switch"`

**Source Code**:

```c
//:: k_inc_switch
/*
     A simple include defining all of the
     events in the game as constants.
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
//DEFAULT AI EVENTS
int KOTOR_DEFAULT_EVENT_ON_HEARTBEAT           = 1001;
int KOTOR_DEFAULT_EVENT_ON_PERCEPTION          = 1002;
int KOTOR_DEFAULT_EVENT_ON_COMBAT_ROUND_END    = 1003;
int KOTOR_DEFAULT_EVENT_ON_DIALOGUE            = 1004;
int KOTOR_DEFAULT_EVENT_ON_ATTACKED            = 1005;
int KOTOR_DEFAULT_EVENT_ON_DAMAGE              = 1006;
int KOTOR_DEFAULT_EVENT_ON_DEATH               = 1007;
int KOTOR_DEFAULT_EVENT_ON_DISTURBED           = 1008;
int KOTOR_DEFAULT_EVENT_ON_BLOCKED             = 1009;
int KOTOR_DEFAULT_EVENT_ON_FORCE_AFFECTED      = 1010;
int KOTOR_DEFAULT_EVENT_ON_GLOBAL_DIALOGUE_END = 1011;
int KOTOR_DEFAULT_EVENT_ON_PATH_BLOCKED        = 1012;
//HENCHMEN AI EVENTS
int KOTOR_HENCH_EVENT_ON_HEARTBEAT           = 2001;
int KOTOR_HENCH_EVENT_ON_PERCEPTION          = 2002;
int KOTOR_HENCH_EVENT_ON_COMBAT_ROUND_END    = 2003;
int KOTOR_HENCH_EVENT_ON_DIALOGUE            = 2004;
int KOTOR_HENCH_EVENT_ON_ATTACKED            = 2005;
int KOTOR_HENCH_EVENT_ON_DAMAGE              = 2006;
int KOTOR_HENCH_EVENT_ON_DEATH               = 2007;
int KOTOR_HENCH_EVENT_ON_DISTURBED           = 2008;
int KOTOR_HENCH_EVENT_ON_BLOCKED             = 2009;
int KOTOR_HENCH_EVENT_ON_FORCE_AFFECTED      = 2010;
int KOTOR_HENCH_EVENT_ON_GLOBAL_DIALOGUE_END = 2011;
int KOTOR_HENCH_EVENT_ON_PATH_BLOCKED        = 2012;
int KOTOR_HENCH_EVENT_ON_ENTER_5m            = 2013;
int KOTOR_HENCH_EVENT_ON_EXIT_5m             = 2014;
//MISC AI EVENTS
int KOTOR_MISC_DETERMINE_COMBAT_ROUND                = 3001;
int KOTOR_MISC_DETERMINE_COMBAT_ROUND_ON_PC          = 3002;
int KOTOR_MISC_DETERMINE_COMBAT_ROUND_ON_INDEX_ZERO  = 3003;

```

<a id="k_inc_tar"></a>

#### `k_inc_tar`

**Description**: ::///////////////////////////////////////////////

**Usage**: `#include "k_inc_tar"`

**Source Code**:

```c
//::///////////////////////////////////////////////
//:: k_inc_tar
//:: k_inc_tar
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
  include file for taris
*/
//:://////////////////////////////////////////////
//:: Created By: Jason Booth
//:: Created On: July 16, 2002
//:://////////////////////////////////////////////
#include "k_inc_debug"
#include "k_inc_utility"
//performs a standard creature transformation where the original creature
//is destroyed and a new creature is put in its place.  returns a reference
//to the new creature.
object TAR_TransformCreature(object oTarget = OBJECT_INVALID,string sTemplate = "");
//test routine for walking waypoints
void TAR_WalkWaypoints();
//mark an object for cleanup by the TAR_CleanupDeadObjects function
void TAR_MarkForCleanup(object obj = OBJECT_SELF);
//destroy all objects whose PLOT_10 flag has been set
void TAR_CleanupDeadObjects(object oArea);
//make object do an uninterruptible path move
void TAR_PlotMovePath(string sWayPointTag,int nFirst, int nLast, int nRun = FALSE);
//make object do an uninterruptible move to an object
void TAR_PlotMoveObject(object oTarget,int nRun = FALSE);
//make object do an uninterruptible move to a location
void TAR_PlotMoveLocation(location lTarget,int nRun = FALSE);
//check for rukil's apprentice journal
int TAR_PCHasApprenticeJournal();
//return number of promised land journals player has
int TAR_GetNumberPromisedLandJournals();
//toggle the state of sith armor
void TAR_ToggleSithArmor();
//fill container with treasure from table
void TAR_AddTreasureToContainer(object oContainer,int iTable,int iAmount);
//returns TRUE if object is wearing sith armor
int TAR_GetWearingSithArmor(object oTarget = OBJECT_INVALID);
//strip sith armor from party, equipping another appropriate item (if available)
//returns the sith armor object if it was being worn
object TAR_StripSithArmor();
//teleport party member
void TAR_TeleportPartyMember(object oPartyMember, location lDest);
//makes the sith armor equippable
void TAR_EnableSithArmor();
//strip all items from an object
void TAR_StripCharacter(object oTarget,object oDest);
//::///////////////////////////////////////////////
... (488 more lines)
```

<a id="k_inc_tat"></a>

#### `k_inc_tat`

**Description**: ::///////////////////////////////////////////////

**Usage**: `#include "k_inc_tat"`

**Source Code**:

```c
//::///////////////////////////////////////////////
//:: Include
//:: k_inc_tat
//:: Copyright (c) 2002 Bioware Corp.
//:://////////////////////////////////////////////
/*
    This is the include file for Tatooine.
*/
//:://////////////////////////////////////////////
//:: Created By: John Winski
//:: Created On: September 3, 2002
//:://////////////////////////////////////////////
#include "k_inc_utility"
#include "k_inc_generic"
// racer constants
int NONE = 0;
int GARM = 1;
int YUKA = 2;
int ZORIIS = 3;
// race time constants
int GARM_TIME = 2600;
int YUKA_TIME = 2470;
int ZORIIS_TIME = 2350;
string RACE_DEFAULT = GetStringByStrRef(32289);
int GetGammoreansDeadGlobal()
{
    return GetGlobalBoolean("tat_GammoreansDead");
}
void SetGammoreansDeadGlobal(int bValue)
{
    if (bValue == TRUE || bValue == FALSE)
    {
        SetGlobalBoolean("tat_GammoreansDead", bValue);
    }
    return;
}
int GetMetKomadLodgeGlobal()
{
    return GetGlobalBoolean("tat_MetKomadLodge");
}
void SetMetKomadLodgeGlobal(int bValue)
{
    if (bValue == TRUE || bValue == FALSE)
    {
        SetGlobalBoolean("tat_MetKomadLodge", bValue);
    }
    return;
}
int GetSharinaAccusedGurkeGlobal()
{
... (2055 more lines)
```

<a id="k_inc_treasure"></a>

#### `k_inc_treasure`

**Description**: :: k_inc_treasure

**Usage**: `#include "k_inc_treasure"`

**Source Code**:

```c
//:: k_inc_treasure
/*
     contains code for filling containers using treasure tables
*/
//:: Created By:  Jason Booth
//:: Copyright (c) 2002 Bioware Corp.
//
//  March 15, 2003  J.B.
//      removed parts and spikes from tables
//
//constants for container types
int SWTR_DEBUG = TRUE;  //set to false to disable console/file logging
int SWTR_TABLE_CIVILIAN_CONTAINER = 1;
int SWTR_TABLE_MILITARY_CONTAINER_LOW = 2;
int SWTR_TABLE_MILITARY_CONTAINER_MID = 3;
int SWTR_TABLE_MILITARY_CONTAINER_HIGH = 4;
int SWTR_TABLE_CORPSE_CONTAINER_LOW = 5;
int SWTR_TABLE_CORPSE_CONTAINER_MID = 6;
int SWTR_TABLE_CORPSE_CONTAINER_HIGH = 7;
int SWTR_TABLE_SHADOWLANDS_CONTAINER_LOW = 8;
int SWTR_TABLE_SHADOWLANDS_CONTAINER_MID = 9;
int SWTR_TABLE_SHADOWLANDS_CONTAINER_HIGH = 10;
int SWTR_TABLE_DROID_CONTAINER_LOW = 11;
int SWTR_TABLE_DROID_CONTAINER_MID = 12;
int SWTR_TABLE_DROID_CONTAINER_HIGH = 13;
int SWTR_TABLE_RAKATAN_CONTAINER = 14;
int SWTR_TABLE_SANDPERSON_CONTAINER = 15;
//Fill an object with treasure from the specified table
//This is the only function that should be used outside this include file
void SWTR_PopulateTreasure(object oContainer,int iTable,int iItems = 1,int bUnique = TRUE);
//for internal debugging use only, output string to the log file and console if desired
void SWTR_Debug_PostString(string sStr,int bConsole = TRUE,int x = 5,int y = 5,float fTime = 5.0)
{
  if(SWTR_DEBUG)
  {
    if(bConsole)
    {
      AurPostString("SWTR_DEBUG - " + sStr,x,y,fTime);
    }
    PrintString("SWTR_DEBUG - " + sStr);
  }
}
//return whether i>=iLow and i<=iHigh
int SWTR_InRange(int i,int iLow,int iHigh)
{
  if(i >= iLow && i <= iHigh)
  {
    return(TRUE);
  }
  else
... (773 more lines)
```

<a id="k_inc_unk"></a>

#### `k_inc_unk`

**Description**: ::///////////////////////////////////////////////

**Usage**: `#include "k_inc_unk"`

**Source Code**:

```c
//::///////////////////////////////////////////////
//:: k_inc_unk
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
  include file for unknown world
*/
//:://////////////////////////////////////////////
//:: Created By: Jason Booth
//:: Created On: Sept. 9, 2002
//:://////////////////////////////////////////////
#include "k_inc_debug"
#include "k_inc_utility"
#include "k_inc_generic"
//mark an object for cleanup by the UNK_CleanupDeadObjects function
void UNK_MarkForCleanup(object obj);
//destroy all objects whose PLOT_10 flag has been set
void UNK_CleanupDeadObjects(object oArea);
//mark object for cleanup and move to nearest exit
void UNK_LeaveArea(object obj = OBJECT_SELF, int bRun = FALSE);
//test if red rakata are hostile
int UNK_GetRedRakataHostile();
//test if black rakata are hostile
int UNK_GetBlackRakataHostile();
//make red rakatans hostile
void UNK_SetRedRakataHostile();
//make black rakatans hostile
void UNK_SetBlackRakataHostile();
//make black rakatans neutral
void UNK_SetBlackRakataNeutral();
//fill container with treasure from table
void UNK_AddTreasureToContainer(object oContainer,int iTable,int iAmount);
// unavoidable damage to all within radius
void UNK_RakDefence(string sObjectTag, float fDistance, int bIndiscriminant = TRUE);
//::///////////////////////////////////////////////
//:: UNK_MarkForCleanup
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
//mark an object for cleanup by the TAR_CleanupDeadObjects function
*/
//:://////////////////////////////////////////////
//:: Created By: Jason Booth
//:: Created On: August 26, 2002
//:://////////////////////////////////////////////
void UNK_MarkForCleanup(object obj)
{
  UT_SetPlotBooleanFlag(obj,SW_PLOT_BOOLEAN_10,TRUE);
}
//::///////////////////////////////////////////////
... (254 more lines)
```

<a id="k_inc_utility"></a>

#### `k_inc_utility`

**Description**: :: k_inc_utility

**Usage**: `#include "k_inc_utility"`

**Source Code**:

```c
//:: k_inc_utility
/*
    common functions used throughout various scripts
    Modified by Peter T. 17/03/03
    - Added UT_MakeNeutral2(), UT_MakeHostile1(), UT_MakeFriendly1() and UT_MakeFriendly2()
*/
//:: Created By: Jason Booth
//:: Copyright (c) 2002 Bioware Corp.
// Plot Flag Constants.
int SW_PLOT_BOOLEAN_01 = 0;
int SW_PLOT_BOOLEAN_02 = 1;
int SW_PLOT_BOOLEAN_03 = 2;
int SW_PLOT_BOOLEAN_04 = 3;
int SW_PLOT_BOOLEAN_05 = 4;
int SW_PLOT_BOOLEAN_06 = 5;
int SW_PLOT_BOOLEAN_07 = 6;
int SW_PLOT_BOOLEAN_08 = 7;
int SW_PLOT_BOOLEAN_09 = 8;
int SW_PLOT_BOOLEAN_10 = 9;
int SW_PLOT_HAS_TALKED_TO = 10;
int SW_PLOT_COMPUTER_OPEN_DOORS = 11;
int SW_PLOT_COMPUTER_USE_GAS = 12;
int SW_PLOT_COMPUTER_DEACTIVATE_TURRETS = 13;
int SW_PLOT_COMPUTER_DEACTIVATE_DROIDS = 14;
int SW_PLOT_COMPUTER_MODIFY_DROID = 15;
int SW_PLOT_REPAIR_WEAPONS = 16;
int SW_PLOT_REPAIR_TARGETING_COMPUTER = 17;
int SW_PLOT_REPAIR_SHIELDS = 18;
int SW_PLOT_REPAIR_ACTIVATE_PATROL_ROUTE = 19;
// UserDefined events
int HOSTILE_RETREAT = 1100;
//Alignment Adjustment Constants
int SW_CONSTANT_DARK_HIT_HIGH = -6;
int SW_CONSTANT_DARK_HIT_MEDIUM = -5;
int SW_CONSTANT_DARK_HIT_LOW = -4;
int SW_CONSTANT_LIGHT_HIT_LOW = -2;
int SW_CONSTANT_LIGHT_HIT_MEDIUM = -1;
int SW_CONSTANT_LIGHT_HIT_HIGH = 0;
// Returns a pass value based on the object's level and DC rating of 0, 1, or 2 (easy, medium, difficult)
// December 20 2001: Changed so that the difficulty is determined by the
// NPC's Hit Dice
int AutoDC(int DC, int nSkill, object oTarget);
//  checks for high charisma
int IsCharismaHigh();
//  checks for low charisma
int IsCharismaLow();
//  checks for normal charisma
int IsCharismaNormal();
//  checks for high intelligence
int IsIntelligenceHigh();
... (2759 more lines)
```

<a id="k_inc_walkways"></a>

#### `k_inc_walkways`

**Description**: :: k_inc_walkways

**Usage**: `#include "k_inc_walkways"`

**Source Code**:

```c
//:: k_inc_walkways
/*
    v1.0
    Walk Way Points Include
    used by k_inc_generic
    NOTE - To get these functions
    use k_inc_generic
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
int WALKWAYS_CURRENT_POSITION = 0;
int WALKWAYS_END_POINT = 1;
int WALKWAYS_SERIES_NUMBER = 2;
int    SW_FLAG_AMBIENT_ANIMATIONS    =    29;
int    SW_FLAG_AMBIENT_ANIMATIONS_MOBILE =    30;
int    SW_FLAG_WAYPOINT_WALK_ONCE    =    34;
int    SW_FLAG_WAYPOINT_WALK_CIRCULAR    =    35;
int    SW_FLAG_WAYPOINT_WALK_PATH    =    36;
int    SW_FLAG_WAYPOINT_WALK_STOP    =    37; //One to three
int    SW_FLAG_WAYPOINT_WALK_RANDOM    =    38;
int SW_FLAG_WAYPOINT_WALK_RUN    =   39;
int SW_FLAG_WAYPOINT_DIRECTION = 41;
int SW_FLAG_WAYPOINT_DEACTIVATE = 42;
int SW_FLAG_WAYPOINT_WALK_STOP_LONG = 46;
int SW_FLAG_WAYPOINT_WALK_STOP_RANDOM = 47;
//Makes OBJECT_SELF walk way points based on the spawn in conditions set out.
void GN_WalkWayPoints();
//Sets the series number from 01 to 99 on a creature so that the series number and not the creature's tag is used for walkway points
void GN_SetWalkWayPointsSeries(int nSeriesNumber);
//Sets Generic Spawn In Conditions
void GN_SetSpawnInCondition(int nFlag, int nState = TRUE);
//Gets the boolean state of a generic spawn in condition.
int GN_GetSpawnInCondition(int nFlag);
//Moves an object to the last waypoint in a series
void GN_MoveToLastWayPoint(object oToMove);
//Moves an object to a random point in the series
void GN_MoveToRandomWayPoint(object oToMove);
//Moves an object to a sepcific point in the series
void GN_MoveToSpecificWayPoint(object oToMove, int nArrayNumber);
//Determines the correct direction to proceed in a walkway points array.
int GN_GetWayPointDirection(int nEndArray, int nCurrentPosition);
//Should only be called from within SetListendingPatterns
void GN_SetUpWayPoints();
//Play an animation between way points.
void GN_PlayWalkWaysAnimation();
//Inserts a print string into the log file for debugging purposes for the walkways include.
void WK_MyPrintString(string sString);
//Are valid walkway points available
int GN_CheckWalkWays(object oTarget);
//::///////////////////////////////////////////////
... (566 more lines)
```

<a id="k_inc_zone"></a>

#### `k_inc_zone`

**Description**: :: k_inc_zones

**Usage**: `#include "k_inc_zone"`

**Source Code**:

```c
//:: k_inc_zones
/*
     Zone including for controlling
     the chaining of creatures
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
#include "k_inc_generic"
//Function run by the trigger to catalog the control nodes followers
void ZN_CatalogFollowers();
//Checks zone conditional on creature to if they belong to the zone
int ZN_CheckIsFollower(object oController, object oTarget);
//Checks the distance and creatures around the PC to see if it should return home.
int ZN_CheckReturnConditions();
//Gets the followers to move back to the controller object
void ZN_MoveToController(object oController, object oFollower);
//Checks to see if a specific individual needs to return to the controller.
int ZN_CheckFollowerReturnConditions(object oTarget);
//::///////////////////////////////////////////////
//:: Catalog Zone Followers
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
     Catalogs all creatures within
     the trigger area and marks
     them with an integer which
     is part of the creature's
     tag.
     Use local number SW_NUMBER_LAST_COMBO
     as a test. A new local number will
     be defined if the system works.
*/
//:://////////////////////////////////////////////
//:: Created By: Preston Watamaniuk
//:: Created On: April 7, 2003
//:://////////////////////////////////////////////
void ZN_CatalogFollowers()
{
    GN_PostString("FIRING", 10,10, 10.0);
    if(GetLocalBoolean(OBJECT_SELF, 10) == FALSE) //Has talked to boolean
    {
        string sZoneTag = GetTag(OBJECT_SELF);
        int nZoneNumber = StringToInt(GetStringRight(sZoneTag, 2));
        //Set up creature followers
        object oZoneFollower = GetFirstInPersistentObject();
        while(GetIsObjectValid(oZoneFollower))
        {
            SetLocalNumber(oZoneFollower, SW_NUMBER_COMBAT_ZONE, nZoneNumber);
            //GN_MyPrintString("ZONING DEBUG ***************** Setup Follower = " + GN_ReturnDebugName(oZoneFollower));
            //GN_MyPrintString("ZONING DEBUG ***************** Setup Follower Zone # = " + GN_ITS(GetLocalNumber(oZoneFollower, SW_NUMBER_COMBAT_ZONE)));
... (110 more lines)
```

<!-- KOTOR_LIBRARY_END -->

## TSL Library files

<!-- TSL_LIBRARY_START -->

<a id="a_global_inc"></a>

#### `a_global_inc`

**Description**: Global Inc

**Usage**: `#include "a_global_inc"`

**Source Code**:

```c

//:: a_global_inc
/*
    parameter 1 = string identifier for a global number
    parameter 2 = amount to increment GetGlobalNumber(param1)
*/
//:: Created By: Anthony Davis
#include "k_inc_debug"
void main()
{
    string tString = GetScriptStringParameter();
    int tInt = GetScriptParameter( 1 );
    SetGlobalNumber(tString, GetGlobalNumber(tString) + tInt);
}

```

<a id="a_influence_inc"></a>

#### `a_influence_inc`

**Description**: a_influence_inc

**Usage**: `#include "a_influence_inc"`

**Source Code**:

```c
// a_influence_inc
/* Parameter Count: 2
Increases an NPC's influence.
Param1 - The NPC value of the player whose influence is increased.
Param2 - magnitude of influence change:
    1 - low
    2 - medium
    3 - high
    all others - medium
NPC numbers, as specified in NPC.2da
0       Atton
1       BaoDur
2       Mand
3       g0t0
4       Handmaiden
5       hk47
6       Kreia
7       Mira
8       T3m4
9       VisasMarr
10      Hanharr
11      Disciple
*/
//
// KDS 06/16/04
void main()
{
int nInfluenceLow = 8;
int nInfluenceMedium = 8;
int nInfluenceHigh = 8;
int nNPC = GetScriptParameter(1);
int nImpact = GetScriptParameter(2);
int nInfluenceChange;
switch (nImpact)
{
    case 1:
        nInfluenceChange = nInfluenceLow;
        break;
    case 2:
        nInfluenceChange = nInfluenceMedium;
        break;
    case 3:
        nInfluenceChange = nInfluenceHigh;
        break;
    default:
        nInfluenceChange = nInfluenceMedium;
        break;
}
ModifyInfluence (nNPC, nInfluenceChange);
}
... (1 more lines)
```

<a id="a_localn_inc"></a>

#### `a_localn_inc`

**Description**: a_localn_inc

**Usage**: `#include "a_localn_inc"`

**Source Code**:

```c
// a_localn_inc
// Parameter Count: 2
// Param1 - The local number # to increment (range 12-31)
// Param2 - the amount to increment Param1 by (default = 1)
// Param3 - Optional string parameter to refer to another object's local #
//
// KDS 06/15/04
// Modified TDE 7/31/04
#include "k_inc_debug"
#include "k_inc_utility"
void main()
{
    int nLocalNumber = GetScriptParameter( 1 );
    int nValue = GetScriptParameter ( 2 );
    // Added optional string parameter to refer to another object's local #
    string sTag = GetScriptStringParameter();
    object oObject;
    // If sTag is empty, use the object that called the script
    if ( sTag == "" ) oObject = OBJECT_SELF;
    else oObject = GetObjectByTag(sTag);
    if (nValue == 0) nValue = 1;
    SetLocalNumber(oObject, nLocalNumber,
        GetLocalNumber(oObject, nLocalNumber) + nValue);
}

```

<a id="k_inc_cheat"></a>

#### `k_inc_cheat`

**Description**: :: k_inc_cheat

**Usage**: `#include "k_inc_cheat"`

**Source Code**:

```c
//:: k_inc_cheat
/*
    This will be localized area for all
    Cheat Bot scripting.
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
#include "k_inc_debug"
//Takes a PLANET_ Constant
void CH_SetPlanetaryGlobal(int nPlanetConstant);
//Makes the specified party member available to the PC
void CH_SetPartyMemberAvailable(int nNPC);
//::///////////////////////////////////////////////
//:: Set Planet Local
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
    VARIABLE = K_CURRENT_PLANET
        Endar Spire     5
        Taris           10
        Dantooine       15
        --Kashyyk       20
        --Manaan        25
        --Korriban      30
        --Tatooine      35
        Leviathan       40
        Unknown World   45
        Star Forge      50
*/
//:://////////////////////////////////////////////
//:: Created By: Preston Watamaniuk
//:: Created On: Oct 16, 2002
//:://////////////////////////////////////////////
void CH_SetPlanetaryGlobal(int nPlanetConstant)
{
/*
    if(nPlanetConstant == PLANET_ENDAR_SPIRE)
    {
        SetGlobalNumber("K_CURRENT_PLANET", 5);
    }
    else if(nPlanetConstant == PLANET_TARIS)
    {
        SetGlobalNumber("K_CURRENT_PLANET", 10);
    }
    else if(nPlanetConstant == PLANET_DANTOOINE)
    {
        SetGlobalNumber("K_CURRENT_PLANET", 15);
    }
    else if(nPlanetConstant == PLANET_KASHYYYK)
    {
... (81 more lines)
```

<a id="k_inc_debug"></a>

#### `k_inc_debug`

**Description**: ::///////////////////////////////////////////////

**Usage**: `#include "k_inc_debug"`

**Source Code**:

```c
//::///////////////////////////////////////////////
//:: KOTOR Debug Include
//:: k_inc_debug
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
    This contains the functions for inserting
    debug information into the scripts.
    This include will use Db as its two letter
    function prefix.
*/
//:://////////////////////////////////////////////
//:: Created By: Preston Watamaniuk
//:: Created On: June 12, 2002
//:://////////////////////////////////////////////
//Inserts a print string into the log file for debugging purposes.
void Db_MyPrintString(string sString);
//Makes the object running the script say a speak string.
void Db_MySpeakString(string sString);
//Makes the nearest PC say a speakstring.
void Db_AssignPCDebugString(string sString);
//Basically, a wrapper for AurPostString
void Db_PostString(string sString = "",int x = 5,int y = 5,float fShow = 1.0);
//::///////////////////////////////////////////////
//:: Debug Print String
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
    Inserts a print string into the log file for
    debugging purposes.
*/
//:://////////////////////////////////////////////
//:: Created By: Preston Watamaniuk
//:: Created On: June 12, 2002
//:://////////////////////////////////////////////
void Db_MyPrintString(string sString)
{
    if(!ShipBuild())
    {
        PrintString(sString);
    }
}
//::///////////////////////////////////////////////
//:: Debug Speak String
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
    Makes the object running the script say a
    speak string.
*/
... (47 more lines)
```

<a id="k_inc_disguise"></a>

#### `k_inc_disguise`

**Description**: :: k_inc_disguise

**Usage**: `#include "k_inc_disguise"`

**Source Code**:

```c
//:: k_inc_disguise
/*
    This script contains all functions necessary to add and
    remove disguises on all party members.
*/
void DonEnvironmentSuit() {
    object oPC;
    int nMax = GetPartyMemberCount();
    int nIdx;
    effect eChange = EffectDisguise(DISGUISE_TYPE_ENVIRONMENTSUIT);
    for(nIdx = 0;nIdx < nMax; nIdx++)
    {
        ApplyEffectToObject(DURATION_TYPE_PERMANENT,eChange,GetPartyMemberByIndex(nIdx));
    }
}
void DonSpaceSuit() {
    int nMax = GetPartyMemberCount();
    int nIdx;
    effect eChange = EffectDisguise(DISGUISE_TYPE_ENVIRONMENTSUIT_02);
    for(nIdx = 0;nIdx < nMax; nIdx++)
    {
        object oPartyMember = GetPartyMemberByIndex(nIdx);
        ApplyEffectToObject(DURATION_TYPE_PERMANENT,eChange,oPartyMember);
    }
}
void RemoveDisguises() {
    int nDisguise = EFFECT_TYPE_DISGUISE;
    object oPC;
    effect eEffect;
    int nMax = GetPartyMemberCount();
    int nIdx;
    for(nIdx = 0;nIdx < nMax; nIdx++)
    {
        oPC = GetPartyMemberByIndex(nIdx);
        eEffect = GetFirstEffect(oPC);
        while(GetIsEffectValid(eEffect))
        {
            if(GetEffectType(eEffect) == nDisguise)
            {
                RemoveEffect(oPC,eEffect);
            }
            eEffect = GetNextEffect(oPC);
        }
    }
}

```

<a id="k_inc_drop"></a>

#### `k_inc_drop`

**Description**: ::///////////////////////////////////////////////

**Usage**: `#include "k_inc_drop"`

**Source Code**:

```c
//::///////////////////////////////////////////////
//:: KOTOR Treasure drop Include
//:: k_inc_drop
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
// Contains the functions for handling creatures dropping random treasure
//Only human creatures not of the beast subrace willdrop treasure dependant
//on their hit dice
//:://////////////////////////////////////////////
//:: Created By: Aidan Scanlan On: 02/06/03
//:://////////////////////////////////////////////
int DR_HIGH_LEVEL = 15;
int DR_MEDIUM_LEVEL = 10;
int DR_LOW_LEVEL = 5;
int DR_SUBRACE_BEAST = 2;
//Checks for treasure drop conditions. Returns True if treasure will drop
int DR_SpawnCreatureTreasure(object oTarget = OBJECT_SELF);
//Dependant on the level of a creature drops treasure from a list
void DR_CreateRandomTreasure(object oTarget = OBJECT_SELF);
// creates a low level treasure: med pack/repair, frag grenade, credits
void DR_CreateLowTreasure();
// creates midlevel treasure: adv-med/repair, any gredade, stims, credits
void DR_CreateMidTreasure();
// creates high treasure: adv stims, grenades, ultra med/repair, credits
void DR_CreateHighTreasure();
// Creates 1-4 credits
void DR_CreateFillerCredits();
/////////////////////////////////////////////////////////////////////////
//Checks for treasure drop conditions. Returns True if treasure will drop
int DR_SpawnCreatureTreasure(object oTarget = OBJECT_SELF)
{
    int nRace = GetRacialType(oTarget);
    int nFaction = GetStandardFaction(oTarget);
    int nSubRace = GetSubRace(oTarget);
    if(Random(4) == 0 &&
       nRace != RACIAL_TYPE_DROID &&
       nSubRace != DR_SUBRACE_BEAST)
    {
        //AurPostString("will drop",5,5,5.0);
        DR_CreateRandomTreasure(oTarget);
        return TRUE;
    }
    return FALSE;
}
//Dependant on the level of a creature drops treasure from a list
void DR_CreateRandomTreasure(object oTarget = OBJECT_SELF)
{
    int nLevel = GetHitDice(oTarget);
    if (nLevel > DR_HIGH_LEVEL)
    {
... (185 more lines)
```

<a id="k_inc_fab"></a>

#### `k_inc_fab`

**Description**: k_inc_fab

**Usage**: `#include "k_inc_fab"`

**Source Code**:

```c
// k_inc_fab
/*
    Ferret's Wacky Include Script - YAY
    A running compilation of short cuts
    to make life easier
*/
// FAB 3/11
// This spawns in a creature with resref sCreature
// in waypoint location "sp_<sCreature><nInstance>"
object FAB_Spawn( string sCreature, int nInstance = 0 );
// This makes oAct face in the direction of oFace
// if oFace is left blank it defaults to the PC
void FAB_Face( object oAct, object oFace = OBJECT_INVALID );
// This function teleports the PC to oWP then any
// other CNPCs are teleported behind the PC.
// WARNING: Make sure that behind the waypoint there
// are valid points for the CNPCs to teleport to.
void FAB_PCPort( object oWP );
// This function returns a location directly behind the object
// you pass it. The float can be changed to determine how far
// behind the PC.
location FAB_Behind( object oTarg, float fMult = 2.5 );
// This spawns in a creature with resref sCreature
// in waypoint location "sp_<sCreature><nInstance>"
object FAB_Spawn( string sCreature, int nInstance = 0 )
{
    string sWP;
    if ( nInstance == 0 ) sWP = "sp_" + sCreature ;
    else sWP = "sp_" + sCreature + IntToString( nInstance );
    return CreateObject( OBJECT_TYPE_CREATURE, sCreature, GetLocation( GetObjectByTag( sWP ) ));
}
// This makes oAct face in the direction of oFace
// if oFace is left blank it defaults to the PC
void FAB_Face( object oAct, object oFace = OBJECT_INVALID )
{
    if ( oFace == OBJECT_INVALID ) oFace = GetFirstPC();
    AssignCommand( oAct, SetFacingPoint( GetPositionFromLocation(GetLocation(oFace)) ));
}
// This function teleports the PC to oWP then any
// other CNPCs are teleported behind the PC.
// WARNING: Make sure that behind the waypoint there
// are valid points for the CNPCs to teleport to.
void FAB_PCPort( object oWP )
{
    AurPostString("Testing!",5,4,2.0);
    //object oWP = GetObjectByTag( "tp_test" );
    //object oTarg = GetFirstPC();
    object oTarg = GetPartyMemberByIndex(0);
    DelayCommand( 0.1, AssignCommand( oTarg, ClearAllActions() ));
    DelayCommand( 0.2, AssignCommand( oTarg, ActionJumpToObject(oWP) ) );
... (72 more lines)
```

<a id="k_inc_fakecombat"></a>

#### `k_inc_fakecombat`

**Description**: :: k_inc_fakecombat

**Usage**: `#include "k_inc_fakecombat"`

**Source Code**:

```c
//:: k_inc_fakecombat
/*
     routines for doing fake combat
*/
//:: Created By: Jason Booth
//:: Copyright (c) 2002 Bioware Corp.
#include "k_inc_generic"
void FAI_EnableFakeMode(object oTarget,int iFaction);
void FAI_DisableFakeMode(object oTarget,int iFaction);
void FAI_PerformFakeAttack(object oAttacker,object oTarget,int bLethal = FALSE);
void FAI_PerformFakeTalent(object oAttacker,object oTarget,talent t,int bLethal = FALSE);
void FAI_EnableFakeMode(object oTarget,int iFaction)
{
  if(!GetIsObjectValid(oTarget))
  {
    return;
  }
  SetCommandable(TRUE,oTarget);
  AssignCommand(oTarget,ClearAllActions());
  SetLocalBoolean(oTarget,SW_FLAG_AI_OFF,TRUE);
  AurPostString("TURNING AI OFF - " + GetTag(oTarget),5,5,5.0);
  ChangeToStandardFaction(oTarget,iFaction);
  SetMinOneHP(oTarget,TRUE);
}
void FAI_DisableFakeMode(object oTarget,int iFaction)
{
  if(!GetIsObjectValid(oTarget))
  {
    return;
  }
  SetCommandable(TRUE,oTarget);
  SetLocalBoolean(oTarget,SW_FLAG_AI_OFF,FALSE);
  ChangeToStandardFaction(oTarget,iFaction);
  SetMinOneHP(oTarget,FALSE);
}
void DoFakeAttack(object oTarget,int bLethal)
{
  if(bLethal)
  {
    SetMinOneHP(oTarget,FALSE);
    ApplyEffectToObject(DURATION_TYPE_INSTANT,EffectDamage(GetCurrentHitPoints(oTarget)-1),
      oTarget);
    //CutsceneAttack(oTarget,ACTION_ATTACKOBJECT,ATTACK_RESULT_HIT_SUCCESSFUL,1000);
  }
  //else
  //{
    ApplyEffectToObject(DURATION_TYPE_TEMPORARY,EffectAssuredHit(),OBJECT_SELF,3.0);
    ActionAttack(oTarget);
 //}
}
... (28 more lines)
```

<a id="k_inc_force"></a>

#### `k_inc_force`

**Description**: :: k_inc_force

**Usage**: `#include "k_inc_force"`

**Source Code**:

```c
//:: k_inc_force
/*
    v1.0
    Force Powers Include for KOTOR
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
float fLightningDuration = 1.0;
//These variables are set in the script run area.
int SWFP_PRIVATE_SAVE_TYPE;
int SWFP_PRIVATE_SAVE_VERSUS_TYPE;
int SWFP_DAMAGE;
int SWFP_DAMAGE_TYPE;
int SWFP_DAMAGE_VFX;
int SWFP_HARMFUL;
int SWFP_SHAPE;
//Runs the script section for the particular force power.
void  Sp_RunForcePowers();
//Immunity and Resist Spell check for the force power.
//The eDamage checks whether the target is immune to the damage effect
int Sp_BlockingChecks(object oTarget, effect eEffect, effect eEffect2, effect eDamage);
//Makes the necessary saving throws
int Sp_MySavingThrows(object oTarget, int iSpellDC = 0);
//Remove an effect of a specific type
void Sp_RemoveSpecificEffect(int nEffectTypeID, object oTarget);
//Remove an effect from a specific force power.
void Sp_RemoveSpellEffects(int nSpell_ID, object oCaster, object oTarget);
// Delays the application of a spell effect by an amount determined by distance.
float Sp_GetSpellEffectDelay(location SpellTargetLocation, object oTarget);
//Randomly delays the effect application for a default of 0.0 to 0.75 seconds
float Sp_GetRandomDelay(float fMinimumTime = 0.0, float MaximumTime = 0.75);
//Gets a saving throw appropriate to the jedi using the force power.
int Sp_GetJediDCSave();
///Apply effects in a sphere shape.
void Sp_SphereSaveHalf(object oAnchor, float fSize, int nCounter, effect eLink1, float fDuration1, effect eLink2, float fDuration);
//Apply effects to a single target.
void Sp_SingleTarget(object oAnchor, effect eLink1, float fDuration1, effect eLink2, float fDuration2);
//Apply effect to an area and negate on a save.
void Sp_SphereBlocking(object oAnchor, float fSize, int nCounter, effect eLink1, float fDuration1, effect eLink2, float fDuration);
// /Apply effect to an object and negate on a save.
void Sp_SingleTargetBlocking(object oAnchor, effect eLink1, float fDuration1, effect eLink2, float fDuration2);
//Apply effects for a for power.
void Sp_ApplyForcePowerEffects(float fTime, effect eEffect, object oTarget);
//Apply effects to targets.
void Sp_ApplyEffects(int nBlocking, object oAnchor, float fSize, int nCounter, effect eLink1, float fDuration1, effect eLink2, float fDuration2, int nRacial = RACIAL_TYPE_ALL);
//Removes all effects from the spells , Knights Mind, Mind Mastery and Battle Meditation
void Sp_RemoveBuffSpell();
//Prints a string for the spell stript
void SP_MyPrintString(string sString);
//Posts a string for the spell script
... (6373 more lines)
```

<a id="k_inc_generic"></a>

#### `k_inc_generic`

**Description**: :: k_inc_generic

**Usage**: `#include "k_inc_generic"`

**Source Code**:

```c
//:: k_inc_generic
/*
    v1.5
    Generic Include for KOTOR
    Post Clean Up as of March 3, 2003
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
#include "k_inc_gensupport"
#include "k_inc_walkways"
#include "k_inc_drop"
struct tLastRound
{
    int nLastAction;
    int nLastActionID;
    int nLastTalentCode;
    object oLastTarget;
    int nTalentSuccessCode;
    int nIsLastTargetDebil;
    int nLastCombo;
    int nLastComboIndex;
    int nCurrentCombo;
    int nBossSwitchCurrent;
};
struct tLastRound tPR;
//LOCAL BOOLEANS RANGE FROM 0 to 96
int AMBIENT_PRESENCE_DAY_ONLY = 1;        //POSSIBLE CUT
int AMBIENT_PRESENCE_NIGHT_ONLY = 2;      //POSSIBLE CUT
int AMBIENT_PRESENCE_ALWAYS_PRESENT = 3;
int SW_FLAG_EVENT_ON_PERCEPTION =   20;
int SW_FLAG_EVENT_ON_ATTACKED   =   21;
int SW_FLAG_EVENT_ON_DAMAGED    =   22;
int SW_FLAG_EVENT_ON_FORCE_AFFECTED = 23;
int SW_FLAG_EVENT_ON_DISTURBED = 24;
int SW_FLAG_EVENT_ON_COMBAT_ROUND_END = 25;
int SW_FLAG_EVENT_ON_DIALOGUE    = 26;
int SW_FLAG_EVENT_ON_DEATH       = 27;
int SW_FLAG_EVENT_ON_HEARTBEAT   = 28;
//int SW_FLAG_AMBIENT_ANIMATIONS = 29;          located in k_inc_walkways
// DJS-OEI 3/31/2004
// Since I misinformed the designers early on about the
// number of local boolean the game was using internally,
// they started using flags 30 thru 64 for plot-related
// stuff. This started causing problems since it was signalling
// the AI to perform incorrect behaviors. I've set aside the
// 30-64 range for designer use and increased the values of
// the remaining flags (as well as the engine's total storage
// capacity) so their current scripts will still work. We need
// to recompile all global and MOD embedded scripts so they use
// the new values.
... (3672 more lines)
```

<a id="k_inc_gensupport"></a>

#### `k_inc_gensupport`

**Description**: :: k_inc_gensupport

**Usage**: `#include "k_inc_gensupport"`

**Source Code**:

```c
//:: k_inc_gensupport
/*
    v1.0
    Support Include for k_inc_generic
    NOTE - To get these functions
    use k_inc_generic
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
//BOSS ATTACK TYPES
int SW_BOSS_ATTACK_TYPE_GRENADE = 1;
int SW_BOSS_ATTACK_TYPE_FORCE_POWER = 2;
int SW_BOSS_ATTACK_TYPE_NPC = 3;
int SW_BOSS_ATTACK_TYPE_PC = 4;
int SW_BOSS_ATTACK_ANY = 5;
int SW_BOSS_ATTACK_DROID = 6;
//LOCAL NUMBERS
int SW_NUMBER_COMBO_ROUTINE = 3;
int SW_NUMBER_COMBO_INDEX = 4;
int SW_NUMBER_LAST_COMBO = 5;
int SW_NUMBER_ROUND_COUNTER = 6;
int SW_NUMBER_COMBAT_ZONE = 7;
int SW_NUMBER_HEALERAI_THRESHOLD = 8;
int SW_NUMBER_HEALERAI_PERCENTAGE = 9;
int SW_NUMBER_COOLDOWN = 10; // fak - oei, rounds before firing again
int SW_NUMBER_COOLDOWN_FIRE = 11; // fak - oei, threshold at which turret fires
//COMBO CONSTANTS
int SW_COMBO_RANGED_FEROCIOUS = 1;
int SW_COMBO_RANGED_AGGRESSIVE = 2;
int SW_COMBO_RANGED_DISCIPLINED = 3;
int SW_COMBO_RANGED_CAUTIOUS = 4;
int SW_COMBO_MELEE_FEROCIOUS = 5;
int SW_COMBO_MELEE_AGGRESSIVE = 6;
int SW_COMBO_MELEE_DISCIPLINED = 7;
int SW_COMBO_MELEE_CAUTIOUS = 8;
int SW_COMBO_BUFF_PARTY = 9;
int SW_COMBO_BUFF_DEBILITATE = 10;
int SW_COMBO_BUFF_DAMAGE = 11;
int SW_COMBO_BUFF_DEBILITATE_DESTROY = 12;
int SW_COMBO_SUPRESS_DEBILITATE_DESTROY = 13;
int SW_COMBO_SITH_ATTACK = 14;
int SW_COMBO_BUFF_ATTACK = 15;
int SW_COMBO_SITH_CONFOUND = 16;
int SW_COMBO_JEDI_SMITE = 17;
int SW_COMBO_SITH_TAUNT = 18;
int SW_COMBO_SITH_BLADE = 19;
int SW_COMBO_SITH_CRUSH = 20;
int SW_COMBO_JEDI_CRUSH = 21;
int SW_COMBO_SITH_BRUTALIZE = 22;
int SW_COMBO_SITH_DRAIN = 23;
... (3828 more lines)
```

<a id="k_inc_glob_party"></a>

#### `k_inc_glob_party`

**Description**: Glob Party

**Usage**: `#include "k_inc_glob_party"`

**Source Code**:

```c

//:: k_inc_glob_party
/*
These global scripts are to be used to spawn actual party member objects with thier correct equipment, stats, levels, etc.
Use this to place party members for required scripts and cutscenes.
*/
#include "k_inc_debug"
// FUNCTION DECLARATIONS
string  GetNPCTag( int nNPC );
int     GetNPCConstant( string sTag );
void    ClearPlayerParty();
void    SetPlayerParty(int aNPC_CONSTANT_1, int aNPC_CONSTANT_2);
object  SpawnIndividualPartyMember(int aNPC_CONSTANT, string sWP = "WP_gspawn_");
void    SpawnAllAvailablePartyMembers();
object  SpawnIndividualPuppet(int aNPC_CONSTANT, string sWP = "WP_gspawn_");
string  GetPuppetTag( int nNPC );
int     GetPuppetConstant( string sTag );
// FUNCTION DEFINITIONS:
// Sets the Player created character to be the party leader
// and returns all other party members to the 'party base'.
void ClearPlayerParty()
{
    SetPartyLeader(NPC_PLAYER);
    int i;
    for(i = 0; i < 12; i++)
    {
        if(IsNPCPartyMember( i ))
            RemoveNPCFromPartyToBase( i );
    }
}
// sets the Player created character to be the party leader and then fills the party
// with the passed in constants PROVIDED that they have been previously add to the
// 'party base'
void SetPlayerParty(int aNPC_CONSTANT_1, int aNPC_CONSTANT_2)
{
    ClearPlayerParty();
    object oPartyMember1 = SpawnIndividualPartyMember(aNPC_CONSTANT_1);
    object oPartyMember2 = SpawnIndividualPartyMember(aNPC_CONSTANT_2);
    if(GetIsObjectValid(oPartyMember1) )
    {
        AddPartyMember(aNPC_CONSTANT_1, oPartyMember1);
    }
    if(GetIsObjectValid(oPartyMember2) )
    {
        AddPartyMember(aNPC_CONSTANT_2, oPartyMember2);
    }
}
// Will return the tag of the party member constant passed in.
// Will return 'ERROR' if an invalid constant is passed in.
string GetNPCTag( int nNPC )
... (205 more lines)
```

<a id="k_inc_hawk"></a>

#### `k_inc_hawk`

**Description**: Hawk

**Usage**: `#include "k_inc_hawk"`

**Source Code**:

```c

//:: Script Name
/*
    Desc
*/
//:: Created By:
//:: Copyright (c) 2002 Bioware Corp.
#include "k_inc_glob_party"
#include "k_oei_hench_inc"
void StopCombat()
{
    object oPC = GetFirstPC();
    CancelCombat(oPC);
    int i;
    object oEnemy;
    for(i = 0;i < 20;i++)
    {
        oEnemy = GetObjectByTag("REThug4", i);
        if(GetIsObjectValid(oEnemy))
        {
            ChangeToStandardFaction( oEnemy,STANDARD_FACTION_NEUTRAL );
            CancelCombat(oEnemy);
        }
        oEnemy = GetObjectByTag("REThug5", i);
        if(GetIsObjectValid(oEnemy))
        {
            ChangeToStandardFaction( oEnemy,STANDARD_FACTION_NEUTRAL );
            CancelCombat(oEnemy);
        }
    }
    //take care of the captain
    oEnemy = GetObjectByTag("RECapt");
    if(GetIsObjectValid(oEnemy))
    {
        ChangeToStandardFaction( oEnemy,STANDARD_FACTION_NEUTRAL );
        CancelCombat(oEnemy);
    }
}
void ClearEnemies()
{
    int i;
    object oEnemy;
    for(i = 0;i < 20;i++)
    {
        oEnemy = GetObjectByTag("REThug4", i);
        if(GetIsObjectValid(oEnemy))
            DestroyObject(oEnemy);
        oEnemy = GetObjectByTag("REThug5", i);
        if(GetIsObjectValid(oEnemy))
            DestroyObject(oEnemy);
... (346 more lines)
```

<a id="k_inc_item_gen"></a>

#### `k_inc_item_gen`

**Description**: Item Gen

**Usage**: `#include "k_inc_item_gen"`

**Source Code**:

```c

//:: k_inc_item_gen.nss
/*
    Global script used to generate items on the PC based on the
    NPC being spoken to.
*/
//:: Created By:
//:: Copyright (c) 2002 Bioware Corp.
#include "k_inc_debug"
//Checks the Player's inventory and determines based on OBJECT_SELF
//whether the Player needs equipment.
//Returns TRUE if the Player needs equipment.
//Returns FALSE if the Player does NOT equipment.
int  GetIsEquipmentNeeded();
//Creates equipment on the PC based on the NPC they are talking to.
void CreateEquipmentOnPC();
//Counts and totals up to four different items within the Player's inventory.
int  CheckInventoryNumbers(string sTag1, string sTag2 = "", string sTag3 = "", string sTag4 = "");
//Checks the Player's inventory and determines based on OBJECT_SELF
//whether the Player needs equipment.
//Returns TRUE if the Player needs equipment.
//Returns FALSE if the Player does NOT equipment.
//Global and modified version of EBO_GetIsEquipmentNeeded() from Kotor1
int GetIsEquipmentNeeded()
{
    int nNumber, nGlobal;
    string sTag = GetTag(OBJECT_SELF);
    int nJediFound = (GetGlobalNumber("000_Jedi_Found")*2) + 10;
    if(sTag == "mira")//Mira
    {
        int bMakeLethalGrenades = GetLocalBoolean( OBJECT_SELF, 31 );
        if(bMakeLethalGrenades)
        {//lethals only
            nNumber = CheckInventoryNumbers("g_w_fraggren01","G_W_FIREGREN001");
            nGlobal = GetGlobalNumber("K_MIRA_ITEMS");
            if((nNumber <= 10 && nGlobal < nJediFound) || nGlobal == 0)
            {
                return TRUE;
            }
            return FALSE;
        }
        else
        {//non lethal grenades only, stuns and adhesives
            nNumber = CheckInventoryNumbers("G_w_StunGren01","g_w_adhsvgren001","G_W_CRYOBGREN001","g_w_iongren01");
            nGlobal = GetGlobalNumber("K_MIRA_ITEMS");
            if((nNumber <= 10 && nGlobal < nJediFound) || nGlobal == 0)
            {
                return TRUE;
            }
            return FALSE;
... (222 more lines)
```

<a id="k_inc_npckill"></a>

#### `k_inc_npckill`

**Description**: Richard Taylor

**Usage**: `#include "k_inc_npckill"`

**Source Code**:

```c
//Richard Taylor
//OEI 08/08/04
//Various functions to help with killing creatures in
//violent and damaging explosions.
//When this function is called on something it will
//destroy the oCreature after nDelay seconds and do nDamage to
//everyone within 4 meters radius.
void DamagingExplosion(object oCreature, int nDelay, int nDamage );
//When this function is called on something it will
//destroy the oCreature after nDelay seconds but not
//damage anyone in the explosion
void NonDamagingExplosion(object oCreature, int nDelay);
//When this function is called on something it will do
//an EffectDeath on oCreature after nSeconds
void KillCreature(object oCreature, int nDelay);
int GR_GetGrenadeDC(object oTarget);
void DamagingExplosion( object oCreature, int nDelay, int nDamage )
{
    //IF there is a delay just call ourselves after ndelay seconds and
    //not have a delay next time
    if ( nDelay > 0 )
    {
        //AurPostString( "Delaying Damaging", 10, 25, 5.0f );
        DelayCommand( IntToFloat(nDelay), DamagingExplosion(oCreature, 0, nDamage ));
        return;
    }
    //AurPostString( "Executing Damaging", 10, 26, 5.0f );
    int nDC = 15;
    int nDCCheck = 0;
    location oLoc = GetLocation(oCreature);
    float oOri = GetFacing(oCreature);
    vector vPos = GetPositionFromLocation( oLoc );
    vPos.z = vPos.z + 1.0f ;
    location oExplosionLoc = Location( vPos, oOri );
    object oTarget = GetFirstObjectInShape(SHAPE_SPHERE, 4.0, oLoc, FALSE, 65);
    while (GetIsObjectValid(oTarget) && nDamage > 0 )
    {
        int nFaction = GetStandardFaction( oTarget );
        if ( oTarget != OBJECT_SELF && nFaction != STANDARD_FACTION_NEUTRAL )
        {
            nDCCheck = nDC;
            nDCCheck -= GR_GetGrenadeDC(oTarget);
            if ( !ReflexSave(oTarget, nDCCheck, SAVING_THROW_TYPE_NONE))
            {
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDamage, DAMAGE_TYPE_PIERCING), oTarget);
            }
            else
            {//Do a evasion check
                int nApply = 0;
                if ( GetHasFeat( FEAT_EVASION, oTarget ) )
... (70 more lines)
```

<a id="k_inc_q_crystal"></a>

#### `k_inc_q_crystal`

**Description**: :: a_q_cryst_change

**Usage**: `#include "k_inc_q_crystal"`

**Source Code**:

```c
//:: a_q_cryst_change
/*
Takes the quest crystal the player has, if any.
Gives the player the appropriate quest crystal for their alignment/level
*/
//:: Created By: Kevin Saunders, 06/26/04
//:: Copyright 2004 Obsidian Entertainment
#include "k_inc_utility"
int GetPCLevel()
{
    int n = GetGlobalNumber("G_PC_LEVEL");
    return(n);
}
string GetPCAlignType()
{
    string s;
    if(IsDark()) s = "1";
    if(IsNeutral()) s = "2";
    if(IsLight()) s = "3";
    if(IsDarkComplete()) s = "0";
    if(IsLightComplete()) s = "4";
    return(s);
}
int GetCrystalLevel()
{
    int n = 1 + (GetPCLevel() - 9)/3;
    if(n < 1) n = 1;
    if(n > 9) n = 9;
    return(n);
}

```

<a id="k_inc_quest_hk"></a>

#### `k_inc_quest_hk`

**Description**: Gives the player the next component needed for the HK quest.

**Usage**: `#include "k_inc_quest_hk"`

**Source Code**:

```c
// Gives the player the next component needed for the HK quest.
// kds, 09/06/04
#include "k_inc_treas_k2"
void GiveHKPart(string sString)
{
    int k = 1;
    string sHKpart = "hkpart0";
    string sItem;
    object oItem = OBJECT_SELF;
    object oRecipient;
    if(sString != "") oRecipient = GetObjectByTag(sString);
        else oRecipient = OBJECT_SELF;
if(GetJournalEntry("RebuildHK47") < 80)
{
    for(k; GetIsObjectValid(oItem); k++)
    {
    sItem = sHKpart + IntToString(k);
    oItem = GetItemPossessedBy (GetPartyLeader(),sItem);
    }
    //AddJournalQuestEntry("LightsaberQuest",10*i);
}
CreateItemOnObject( sItem, oRecipient, 1 );
}

```

<a id="k_inc_switch"></a>

#### `k_inc_switch`

**Description**: :: k_inc_switch

**Usage**: `#include "k_inc_switch"`

**Source Code**:

```c
//:: k_inc_switch
/*
     A simple include defining all of the
     events in the game as constants.
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
//DEFAULT AI EVENTS
int KOTOR_DEFAULT_EVENT_ON_HEARTBEAT           = 1001;
int KOTOR_DEFAULT_EVENT_ON_PERCEPTION          = 1002;
int KOTOR_DEFAULT_EVENT_ON_COMBAT_ROUND_END    = 1003;
int KOTOR_DEFAULT_EVENT_ON_DIALOGUE            = 1004;
int KOTOR_DEFAULT_EVENT_ON_ATTACKED            = 1005;
int KOTOR_DEFAULT_EVENT_ON_DAMAGE              = 1006;
int KOTOR_DEFAULT_EVENT_ON_DEATH               = 1007;
int KOTOR_DEFAULT_EVENT_ON_DISTURBED           = 1008;
int KOTOR_DEFAULT_EVENT_ON_BLOCKED             = 1009;
int KOTOR_DEFAULT_EVENT_ON_FORCE_AFFECTED      = 1010;
int KOTOR_DEFAULT_EVENT_ON_GLOBAL_DIALOGUE_END = 1011;
int KOTOR_DEFAULT_EVENT_ON_PATH_BLOCKED        = 1012;
//HENCHMEN AI EVENTS
int KOTOR_HENCH_EVENT_ON_HEARTBEAT           = 2001;
int KOTOR_HENCH_EVENT_ON_PERCEPTION          = 2002;
int KOTOR_HENCH_EVENT_ON_COMBAT_ROUND_END    = 2003;
int KOTOR_HENCH_EVENT_ON_DIALOGUE            = 2004;
int KOTOR_HENCH_EVENT_ON_ATTACKED            = 2005;
int KOTOR_HENCH_EVENT_ON_DAMAGE              = 2006;
int KOTOR_HENCH_EVENT_ON_DEATH               = 2007;
int KOTOR_HENCH_EVENT_ON_DISTURBED           = 2008;
int KOTOR_HENCH_EVENT_ON_BLOCKED             = 2009;
int KOTOR_HENCH_EVENT_ON_FORCE_AFFECTED      = 2010;
int KOTOR_HENCH_EVENT_ON_GLOBAL_DIALOGUE_END = 2011;
int KOTOR_HENCH_EVENT_ON_PATH_BLOCKED        = 2012;
int KOTOR_HENCH_EVENT_ON_ENTER_5m            = 2013;
int KOTOR_HENCH_EVENT_ON_EXIT_5m             = 2014;
//MISC AI EVENTS
int KOTOR_MISC_DETERMINE_COMBAT_ROUND                = 3001;
int KOTOR_MISC_DETERMINE_COMBAT_ROUND_ON_PC          = 3002;
int KOTOR_MISC_DETERMINE_COMBAT_ROUND_ON_INDEX_ZERO  = 3003;
// DJS-OEI 6/12/2004
// Miscellaneous KotOR2 events
// This user-defined event is sent to the Area when the player's
// created character has performed an action that is currently
// considered forbidden for combats in the area.
int KOTOR2_MISC_PC_COMBAT_FORFEIT                    = 4001;

```

<a id="k_inc_treas_k2"></a>

#### `k_inc_treas_k2`

**Description**: Treas K2

**Usage**: `#include "k_inc_treas_k2"`

**Source Code**:

```c
#include "k_inc_q_crystal"
#include "k_inc_treasure"
/*
This include files contains the functions used to randomly generate item treasure
based upon the players' level.
Item classifications
hundreds digit = item class
tens digit = item sub-class
ones digit = specifies specific item resref
(* = these items have been created through at least level 10)
Weapons 100
*  111 - Blaster
*  121 - Blaster Rifle
*  131 - Melee
*  141 - Lightsaber (regular)
*  142 - Lightsaber (short)
*  143 - Lightsaber (Double)
Upgrades 200
Upgrade - Ranged 210
*  211 - Targeting scope
*  212 - Firing Chamber
*  213 - Power Pack
Upgrade - Melee 220
*  221 - Grip
*  222 - Edge
*  223 - Energy Cell
Upgrade - Armor 230
*  231 - Overlay
*  232 - Underlay
Upgrades - Lightsaber 240
  241 - Emitter
*  242 - Lens
  243 - Energy Cell
  244 - Crystals
  245 - Color Crystals
Equipment - 300
*  311 - Belts
*  321 - Gloves
*  331 - Head Gear
   Implants - 340
*   341 - Level 1
*   342 - Level 2
*   343 - Level 3
*   344 - Level 4
Armor - 400
*  411 - Light armor
*  421 - Medium armor
*  431 - Heavy armor
*  441 - Jedi Robes
Droid Items - 500
... (816 more lines)
```

<a id="k_inc_treasure"></a>

#### `k_inc_treasure`

**Description**: :: k_inc_treasure

**Usage**: `#include "k_inc_treasure"`

**Source Code**:

```c
//:: k_inc_treasure
/*
     contains code for filling containers using treasure tables
*/
//:: Created By:  Jason Booth
//:: Copyright (c) 2002 Bioware Corp.
//
//  March 15, 2003  J.B.
//      removed parts and spikes from tables
//
//constants for container types
int SWTR_DEBUG = TRUE;  //set to false to disable console/file logging
int SWTR_TABLE_CIVILIAN_CONTAINER = 1;
int SWTR_TABLE_MILITARY_CONTAINER_LOW = 2;
int SWTR_TABLE_MILITARY_CONTAINER_MID = 3;
int SWTR_TABLE_MILITARY_CONTAINER_HIGH = 4;
int SWTR_TABLE_CORPSE_CONTAINER_LOW = 5;
int SWTR_TABLE_CORPSE_CONTAINER_MID = 6;
int SWTR_TABLE_CORPSE_CONTAINER_HIGH = 7;
int SWTR_TABLE_SHADOWLANDS_CONTAINER_LOW = 8;
int SWTR_TABLE_SHADOWLANDS_CONTAINER_MID = 9;
int SWTR_TABLE_SHADOWLANDS_CONTAINER_HIGH = 10;
int SWTR_TABLE_DROID_CONTAINER_LOW = 11;
int SWTR_TABLE_DROID_CONTAINER_MID = 12;
int SWTR_TABLE_DROID_CONTAINER_HIGH = 13;
int SWTR_TABLE_RAKATAN_CONTAINER = 14;
int SWTR_TABLE_SANDPERSON_CONTAINER = 15;
//Fill an object with treasure from the specified table
//This is the only function that should be used outside this include file
void SWTR_PopulateTreasure(object oContainer,int iTable,int iItems = 1,int bUnique = TRUE);
//for internal debugging use only, output string to the log file and console if desired
void SWTR_Debug_PostString(string sStr,int bConsole = TRUE,int x = 5,int y = 5,float fTime = 5.0)
{
  if(SWTR_DEBUG)
  {
    if(bConsole)
    {
      AurPostString("SWTR_DEBUG - " + sStr,x,y,fTime);
    }
    PrintString("SWTR_DEBUG - " + sStr);
  }
}
//return whether i>=iLow and i<=iHigh
int SWTR_InRange(int i,int iLow,int iHigh)
{
  if(i >= iLow && i <= iHigh)
  {
    return(TRUE);
  }
  else
... (773 more lines)
```

<a id="k_inc_utility"></a>

#### `k_inc_utility`

**Description**: :: k_inc_utility

**Usage**: `#include "k_inc_utility"`

**Source Code**:

```c
//:: k_inc_utility
/*
    common functions used throughout various scripts
    Modified by Peter T. 17/03/03
    - Added UT_MakeNeutral2(), UT_MakeHostile1(), UT_MakeFriendly1() and UT_MakeFriendly2()
*/
//:: Created By: Jason Booth
//:: Copyright (c) 2002 Bioware Corp.
// Plot Flag Constants.
int SW_PLOT_BOOLEAN_01 = 0;
int SW_PLOT_BOOLEAN_02 = 1;
int SW_PLOT_BOOLEAN_03 = 2;
int SW_PLOT_BOOLEAN_04 = 3;
int SW_PLOT_BOOLEAN_05 = 4;
int SW_PLOT_BOOLEAN_06 = 5;
int SW_PLOT_BOOLEAN_07 = 6;
int SW_PLOT_BOOLEAN_08 = 7;
int SW_PLOT_BOOLEAN_09 = 8;
int SW_PLOT_BOOLEAN_10 = 9;
int SW_PLOT_HAS_TALKED_TO = 10;
int SW_PLOT_COMPUTER_OPEN_DOORS = 11;
int SW_PLOT_COMPUTER_USE_GAS = 12;
int SW_PLOT_COMPUTER_DEACTIVATE_TURRETS = 13;
int SW_PLOT_COMPUTER_DEACTIVATE_DROIDS = 14;
int SW_PLOT_COMPUTER_MODIFY_DROID = 15;
int SW_PLOT_REPAIR_WEAPONS = 16;
int SW_PLOT_REPAIR_TARGETING_COMPUTER = 17;
int SW_PLOT_REPAIR_SHIELDS = 18;
int SW_PLOT_REPAIR_ACTIVATE_PATROL_ROUTE = 19;
// UserDefined events
int HOSTILE_RETREAT = 1100;
//Alignment Adjustment Constants
int SW_CONSTANT_DARK_HIT_HIGH = -6;
int SW_CONSTANT_DARK_HIT_MEDIUM = -5;
int SW_CONSTANT_DARK_HIT_LOW = -4;
int SW_CONSTANT_LIGHT_HIT_LOW = -2;
int SW_CONSTANT_LIGHT_HIT_MEDIUM = -1;
int SW_CONSTANT_LIGHT_HIT_HIGH = 0;
// Returns a pass value based on the object's level and DC rating of 0, 1, or 2 (easy, medium, difficult)
// December 20 2001: Changed so that the difficulty is determined by the
// NPC's Hit Dice
int AutoDC(int DC, int nSkill, object oTarget);
//  checks for high charisma
int IsCharismaHigh();
//  checks for low charisma
int IsCharismaLow();
//  checks for normal charisma
int IsCharismaNormal();
//  checks for high intelligence
int IsIntelligenceHigh();
... (2998 more lines)
```

<a id="k_inc_walkways"></a>

#### `k_inc_walkways`

**Description**: :: k_inc_walkways

**Usage**: `#include "k_inc_walkways"`

**Source Code**:

```c
//:: k_inc_walkways
/*
    v1.0
    Walk Way Points Include
    used by k_inc_generic
    NOTE - To get these functions
    use k_inc_generic
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
int WALKWAYS_CURRENT_POSITION = 0;
int WALKWAYS_END_POINT = 1;
int WALKWAYS_SERIES_NUMBER = 2;
int SW_FLAG_AMBIENT_ANIMATIONS  =   29;
// DJS-OEI 3/31/2004
// Modified to make room for designer-reserved values.
/*
int SW_FLAG_AMBIENT_ANIMATIONS_MOBILE = 30;
int SW_FLAG_WAYPOINT_WALK_ONCE  =   34;
int SW_FLAG_WAYPOINT_WALK_CIRCULAR  =   35;
int SW_FLAG_WAYPOINT_WALK_PATH  =   36;
int SW_FLAG_WAYPOINT_WALK_STOP  =   37; //One to three
int SW_FLAG_WAYPOINT_WALK_RANDOM    =   38;
int SW_FLAG_WAYPOINT_WALK_RUN    =   39;
int SW_FLAG_WAYPOINT_DIRECTION = 41;
int SW_FLAG_WAYPOINT_DEACTIVATE = 42;
int SW_FLAG_WAYPOINT_WALK_STOP_LONG = 46;
int SW_FLAG_WAYPOINT_WALK_STOP_RANDOM = 47;
int SW_FLAG_WAYPOINT_START_AT_NEAREST = 73;
*/
int SW_FLAG_AMBIENT_ANIMATIONS_MOBILE = 65;
int SW_FLAG_WAYPOINT_START_AT_NEAREST = 98;
int SW_FLAG_WAYPOINT_WALK_ONCE  =   99;
int SW_FLAG_WAYPOINT_WALK_CIRCULAR  =   100;
int SW_FLAG_WAYPOINT_WALK_PATH  =   101;
int SW_FLAG_WAYPOINT_WALK_RANDOM    =   103;
int SW_FLAG_WAYPOINT_WALK_RUN    =   104;
int SW_FLAG_WAYPOINT_DIRECTION = 105;
int SW_FLAG_WAYPOINT_DEACTIVATE = 106;
//new constants for WAYPOINT PAUSING
int SW_FLAG_WAYPOINT_PAUSE_SHORT  = 102;
int SW_FLAG_WAYPOINT_PAUSE_LONG   = 107;
int SW_FLAG_WAYPOINT_PAUSE_RANDOM = 108;
//old constants for WAYPOINT PAUSING. kept for backwards compatibility
int SW_FLAG_WAYPOINT_WALK_STOP        = 102;// DON'T USE ANYMORE
int SW_FLAG_WAYPOINT_WALK_STOP_LONG   = 107;// DON'T USE ANYMORE
int SW_FLAG_WAYPOINT_WALK_STOP_RANDOM = 108;// DON'T USE ANYMORE
//AWD-OEI 06/23/04 adding a local to store the waypoint animation
int SW_FLAG_USE_WAYPOINT_ANIMATION = 109;
//Makes OBJECT_SELF walk way points based on the spawn in conditions set out.
... (676 more lines)
```

<a id="k_inc_zone"></a>

#### `k_inc_zone`

**Description**: :: k_inc_zones

**Usage**: `#include "k_inc_zone"`

**Source Code**:

```c
//:: k_inc_zones
/*
     Zone including for controlling
     the chaining of creatures
*/
//:: Created By: Preston Watamaniuk
//:: Copyright (c) 2002 Bioware Corp.
#include "k_inc_generic"
//Function run by the trigger to catalog the control nodes followers
void ZN_CatalogFollowers();
//Checks zone conditional on creature to if they belong to the zone
int ZN_CheckIsFollower(object oController, object oTarget);
//Checks the distance and creatures around the PC to see if it should return home.
int ZN_CheckReturnConditions();
//Gets the followers to move back to the controller object
void ZN_MoveToController(object oController, object oFollower);
//Checks to see if a specific individual needs to return to the controller.
int ZN_CheckFollowerReturnConditions(object oTarget);
//::///////////////////////////////////////////////
//:: Catalog Zone Followers
//:: Copyright (c) 2001 Bioware Corp.
//:://////////////////////////////////////////////
/*
     Catalogs all creatures within
     the trigger area and marks
     them with an integer which
     is part of the creature's
     tag.
     Use local number SW_NUMBER_LAST_COMBO
     as a test. A new local number will
     be defined if the system works.
*/
//:://////////////////////////////////////////////
//:: Created By: Preston Watamaniuk
//:: Created On: April 7, 2003
//:://////////////////////////////////////////////
void ZN_CatalogFollowers()
{
    GN_PostString("FIRING", 10,10, 10.0);
    if(GetLocalBoolean(OBJECT_SELF, 10) == FALSE) //Has talked to boolean
    {
        string sZoneTag = GetTag(OBJECT_SELF);
        int nZoneNumber = StringToInt(GetStringRight(sZoneTag, 2));
        //Set up creature followers
        object oZoneFollower = GetFirstInPersistentObject();
        while(GetIsObjectValid(oZoneFollower))
        {
            SetLocalNumber(oZoneFollower, SW_NUMBER_COMBAT_ZONE, nZoneNumber);
            //GN_MyPrintString("ZONING DEBUG ***************** Setup Follower = " + GN_ReturnDebugName(oZoneFollower));
            //GN_MyPrintString("ZONING DEBUG ***************** Setup Follower Zone # = " + GN_ITS(GetLocalNumber(oZoneFollower, SW_NUMBER_COMBAT_ZONE)));
... (110 more lines)
```

<a id="k_oei_hench_inc"></a>

#### `k_oei_hench_inc`

**Description**: K Oei Hench Inc

**Usage**: `#include "k_oei_hench_inc"`

**Source Code**:

```c

//:: Script Name
/*
    Desc
*/
//:: Created By:
//:: Copyright (c) 2002 Bioware Corp.
// Modified by JAB-OEI 7/23/04
// Added special scripts for the 711KOR fight with the entire party
#include "k_inc_generic"
#include "k_inc_utility"
void DoSpecialSpawnIn(object pObject);
void DoSpecialUserDefined(object pObject, int pUserEvent);
//Party Member SpawnIns
void DoAttonSpawnIn(object oPartyMember, string sModuleName);
void DoBaoDurSpawnIn(object oPartyMember, string sModuleName);
void DoMandSpawnIn(object oPartyMember, string sModuleName);
void DoDiscipleSpawnIn(object oPartyMember, string sModuleName);
void DoG0T0SpawnIn(object oPartyMember, string sModuleName);
void DoHandmaidenSpawnIn(object oPartyMember, string sModuleName);
void DoHanharrSpawnIn(object oPartyMember, string sModuleName);
void DoHK47SpawnIn(object oPartyMember, string sModuleName);
void DoKreiaSpawnIn(object oPartyMember, string sModuleName);
void DoMiraSpawnIn(object oPartyMember, string sModuleName);
void DoRemoteSpawnIn(object oPartyMember, string sModuleName);
void DoT3M4SpawnIn(object oPartyMember, string sModuleName);
void DoVisasMarrSpawnIn(object oPartyMember, string sModuleName);
//Party Member UserDefs
void DoAttonUserDef(object oPartyMember, int pUserEvent, string sModuleName);
void DoBaoDurUserDef(object oPartyMember, int pUserEvent, string sModuleName);
void DoMandUserDef(object oPartyMember, int pUserEvent, string sModuleName);
void DoDiscipleUserDef(object oPartyMember, int pUserEvent, string sModuleName);
void DoG0T0UserDef(object oPartyMember,int pUserEvent, string sModuleName);
void DoHandmaidenUserDef(object oPartyMember,int pUserEvent, string sModuleName);
void DoHanharrUserDef(object oPartyMember,int pUserEvent, string sModuleName);
void DoHK47UserDef(object oPartyMember,int pUserEvent, string sModuleName);
void DoKreiaUserDef(object oPartyMember,int pUserEvent, string sModuleName);
void DoMiraUserDef(object oPartyMember,int pUserEvent, string sModuleName);
void DoRemoteUserDef(object oPartyMember,int pUserEvent, string sModuleName);
void DoT3M4UserDef(object oPartyMember,int pUserEvent, string sModuleName);
void DoVisasMarrUserDef(object oPartyMember,int pUserEvent, string sModuleName);
void DoRemoteDefaultUserDef(object oPartyMember, int pUserEvent);
void Do711UserDef(object oPartyMember,int pUserEvent);
void DoSpecialSpawnIn(object pObject)
{
    AurPostString("DoSpecialSpawnIn" + GetTag(pObject), 18, 18, 3.0);
    if(GetIsObjectValid(pObject))
    {
        string tTag = GetTag(pObject);//should be a party member tag
        string sModuleName = GetModuleName();
... (1373 more lines)
```

<!-- TSL_LIBRARY_END -->

## Compilation Process


1. **Parser Creation**: `NssParser` initialized with game-specific functions/constants
2. **Source Parsing**: NSS source code parsed into Abstract Syntax Tree (AST)
3. **Function Resolution**: Function calls resolved to routine numbers via function list lookup
4. **Constant Substitution**: Constants replaced with their literal values
5. **Bytecode Generation**: AST compiled to [NCS](NCS-File-Format) bytecode instructions
6. **Optimization**: Post-compilation optimizers applied (NOP removal, etc.)

**Function Call Resolution:**

```c
// Source code
int result = GetGlobalNumber("K_QUEST_COMPLETED");
```

```c
// Compiler looks up "GetGlobalNumber" in KOTOR_FUNCTIONS
// Finds it at index 159 (routine number)
// Generates: ACTION 159 with 1 argument (string "K_QUEST_COMPLETED")
```

**Constant Resolution:**

```c
// Source code
if (nPlanet == PLANET_TARIS) { ... }
```

```c
// Compiler looks up PLANET_TARIS in KOTOR_CONSTANTS
// Finds value: 1
// Generates: CONSTI 1 (pushes integer 1 onto stack)
```

**Reference:**

- [`Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_auto.py:126-205`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_auto.py)
- [NCS-File-Format#example-5-engine-function-call](NCS-File-Format#example-5-engine-function-call)

---

## Commented-Out Elements in nwscript.nss

The `nwscript.nss` files in **KotOR 1 and 2** contain numerous constants and functions that [ARE](GFF-File-Format) commented out (prefixed with `//`). These represent features from the original **Neverwinter Nights (NWN)** scripting system that were **not implemented or supported in KotOR's Aurora engine variant**. BioWare deliberately disabled these elements to prevent crashes, errors, or undefined behavior if used.

### Reasons for Commented-Out Elements

KOTOR's `nwscript.nss` retains many NWN-era declarations but prefixes unsupported ones with `//` to disable them during compilation. This deliberate choice by BioWare ensures:

- **Engine Compatibility**: KOTOR's Aurora implementation lacks opcodes or assets for certain NWN features (e.g., advanced [animations](MDL-MDX-File-Format), UI behaviors), leading to crashes or no-ops if invoked.

- **Modder Safety**: Prevents accidental use in custom scripts, which would fail at runtime. file-internal comments often explicitly state `// disabled` (e.g., for creature orientation in dialogues).

- **Game-Specific Differences**: K1 and K2/TSL `nwscript.nss` vary slightly; K2 has a notorious syntax error in `SetOrientOnClick` (fixed by modders via override).

No official BioWare documentation explains this (as KOTOR predates widespread modding support), but forum consensus attributes it to engine streamlining for single-player RPG vs. NWN's multiplayer focus.

### Key Examples of Commented Elements

| Category | Examples | Notes from nwscript.nss |
|----------|----------|-------------------------|
| [animations](MDL-MDX-File-Format) | `//int ANIMATION_LOOPING_LOOK_FAR = 5;`<br>`//int ANIMATION_LOOPING_SIT_CHAIR = 6;`<br>`//int ANIMATION_LOOPING_SIT_CROSS = 7;` | Not usable in KOTOR; modders note them when scripting custom behaviors. |
| Effects/Functions | `EffectMovementSpeedIncrease` (with detailed commented description) | Function exists but capped (~200%); higher values ignored, despite "turbo" cheat allowing more. |
| Behaviors | `SetOrientOnClick` | Syntax-broken in early K2; comments note `// disabled` for orient-to-player on click. |

### Common Modder Workarounds

Modders have developed several strategies for working with commented-out elements:

- **Override nwscript.nss**: Extract from `scripts.bif` via Holocron Toolset, fix issues (e.g., K2 syntax error at line ~5710), place in `Override` folder for compilers/DeNCS.

- **Add custom constants**: Modders append new ones (e.g., for feats) rather than uncommenting old.

- **Avoid direct edits**: Messing with core declarations risks compilation failures across all scripts.

**Standard Override Workflow:**

1. Extract via Holocron Toolset (`scripts.bif > Script, Source > nwscript.nss`).
2. Edit (fix/add), save as `.nss` in `Override`.
3. Use with `nwnnsscomp` for compilation.

**K2 Syntax Fix:**

The notorious K2 syntax error in `SetOrientOnClick` can be fixed by changing:

```c
void SetOrientOnClick( object = OBJECT_SELF, ... )
```

to:

```c
void SetOrientOnClick( object oCreature = OBJECT_SELF, ... )
```

### Forum Discussions and Community Knowledge

Modding communities actively reference these commented sections, especially on **Deadly Stream** (primary KOTOR hub), **LucasForums containers**, **Holowan Laboratories** (via MixNMojo/Mixmojo forums), and Reddit.

| Forum | Key threads | Topics covered |
|-------|-------------|----------------|
| Deadly Stream | [Script Shack](https://deadlystream.com/topic/4808-fair-strides-script-shack/page/7/) | [animations](MDL-MDX-File-Format)<br>overrides |
| Deadly Stream | [nwscript.nss Request](https://deadlystream.com/topic/6892-nwscriptnss/) | [animations](MDL-MDX-File-Format)<br>overrides |
| LucasForums Container | [Syntax Error](https://www.lucasforumscontainer.com/thread/142901-syntax-error-in-kotor2-nwscriptnss) | Fixes<br>warnings |
| LucasForums Container | [Don't Mess with It](https://www.lucasforumscontainer.com/thread/168643-im-trying-to-change-classes2da) | Fixes<br>warnings |
| Reddit r/kotor | [Movement Speed](https://www.reddit.com/r/kotor/comments/9dr8iy/modding_question_movement_speed_increase_in_k2/) | Effect caps |
| Czerka R&D Wiki | [nwscript.nss](https://czerka-rd.fandom.com/wiki/Nwscript.nss) | General documentation |

**Notable Discussion Points:**

- **Deadly Stream - Fair Strides' Script Shack** (2016 thread, 100+ pages): Users troubleshooting [animations](MDL-MDX-File-Format) [flag](GFF-File-Format) the exact commented lines (e.g., `ANIMATION_LOOPING_*`), confirming they can't be used natively. No successful uncommenting reported; focus on alternatives like `ActionPlayAnimation` workarounds.

- **Reddit r/kotor** (2018): Thread on speed boosts quotes the commented description for `EffectMovementSpeedIncrease` (line ~165). Users test values >200% (no effect due to cap), note "turbo" cheat bypasses it partially.

- **LucasForums Container** (2004-2007 threads): Multiple posts warn against editing `nwscript.nss` ("very bad idea... loads of trouble"). Syntax fix for K2 widely shared
- `// disabled` snippets appear in context of `SetOrientOnClick`.

### Attempts to Uncomment or Modify

- **Direct Uncommenting**: No documented successes; implied to cause runtime crashes (engine lacks implementation). Forums advise against.

- **Overrides & Additions**: Standard modding workflow (see above). Examples: TSLPatcher/TSL Patcher tools bundle fixed versions; mods like Hardcore/Improved AI reference custom includes (not core uncomments).

- **Advanced Usage**: DeNCS/ncs2nss require game-specific `nwscript.nss` for accurate decompiles; modders parse it for custom tools.

In summary, while no one has publicly shared a "uncomment everything" patch (likely futile), the modding scene thrives on careful overrides, with thousands of posts across these sites confirming the practice since 2003.

### Key Citations

- [Deadly Stream: Fair Strides' Script Shack](https://deadlystream.com/topic/4808-fair-strides-script-shack/page/7/)
- [Czerka Wiki: nwscript.nss](https://czerka-rd.fandom.com/wiki/Nwscript.nss)
- [LucasForums: Syntax Error in K2 nwscript.nss](https://www.lucasforumscontainer.com/thread/142901-syntax-error-in-kotor2-nwscriptnss)
- [Reddit: Movement Speed Modding](https://www.reddit.com/r/kotor/comments/9dr8iy/modding_question_movement_speed_increase_in_k2/)
- [Deadly Stream: nwscript.nss Thread](https://deadlystream.com/topic/6892-nwscriptnss/)
- [LucasForums: Warning on Editing nwscript.nss](https://www.lucasforumscontainer.com/thread/168643-im-trying-to-change-classes2da)

---

## Reference Implementations

**Parsing nwscript.nss:**

- [`reone/src/apps/dataminer/routines.cpp:149-184`](https://github.com/modawan/reone/blob/master/src/apps/dataminer/routines.cpp) - Parses nwscript.nss using regex patterns for constants and functions
- [`reone/src/apps/dataminer/routines.cpp:382-427`](https://github.com/modawan/reone/blob/master/src/apps/dataminer/routines.cpp) - Extracts functions from nwscript.nss in chitin.key for K1 and K2
- [`xoreos-tools/src/nwscript/actions.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/actions.cpp) - Actions data parsing for decompilation
- [`xoreos-tools/src/nwscript/ncsfile.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/ncsfile.cpp) - [NCS file](NCS-File-Format) parsing with actions data integration
- [`NorthernLights/Assets/Scripts/ncs/nwscript_actions.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/nwscript_actions.cs) - Unity C# actions table
- [`NorthernLights/Assets/Scripts/ncs/nwscript.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/nwscript.cs) - Unity C# NWScript class
- **`KotOR-Scripting-Tool/NWN Script/NWScriptParser.cs`** - C# parser for nwscript.nss
  - Upstream (KobaltBlu/KotOR-Scripting-Tool): <https://github.com/KobaltBlu/KotOR-Scripting-Tool/blob/ddd580e1b85e9c25bf5eea77a0b6938e396579c6/NWN%20Script/NWScriptParser.cs>
  - Mirror (th3w1zard1/KotOR-Scripting-Tool): <https://github.com/th3w1zard1/KotOR-Scripting-Tool/blob/ddd580e1b85e9c25bf5eea77a0b6938e396579c6/NWN%20Script/NWScriptParser.cs>

**Function Definitions:**

- [`KotOR.js/src/nwscript/NWScript.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScript.ts) - TypeScript function definitions
- [`KotOR.js/src/nwscript/NWScriptDefK1.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts) - KotOR 1 definitions
- [`KotOR.js/src/nwscript/NWScriptDefK2.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK2.ts) - KotOR 2 definitions
- [`KotOR.js/src/nwscript/compiler/NWScriptParser.ts` L65+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/compiler/NWScriptParser.ts#L65) — Parser for `nwscript.nss` / NSS (engine types, constants, actions)
- [`KotOR.js/src/nwscript/NWScriptInstructionSet.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptInstructionSet.ts) - Instruction set definitions
- [`KotOR.js/src/nwscript/NWScriptConstants.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptConstants.ts) - Constant definitions
- **`HoloLSP/server/src/nwscript-parser.ts` L52+** — `NWScriptParser` (recursive descent)
  - Canonical (th3w1zard1/HoloLSP): <https://github.com/th3w1zard1/HoloLSP/blob/80f2e64bf508a6b487d8f3ecf9ab9cb6812222a2/server/src/nwscript-parser.ts#L52>
- **`HoloLSP/server/src/nwscript-lexer.ts` L9+** — `TokenType` / `NWScriptLexer`
  - Canonical (th3w1zard1/HoloLSP): <https://github.com/th3w1zard1/HoloLSP/blob/80f2e64bf508a6b487d8f3ecf9ab9cb6812222a2/server/src/nwscript-lexer.ts#L9>
- **`HoloLSP/server/src/nwscript-ast.ts` L7+** — AST nodes (`Program`, `FunctionDeclaration`, …)
  - Canonical (th3w1zard1/HoloLSP): <https://github.com/th3w1zard1/HoloLSP/blob/80f2e64bf508a6b487d8f3ecf9ab9cb6812222a2/server/src/nwscript-ast.ts#L7>
- **`HoloLSP/syntaxes/nwscript.tmLanguage.json` L1+** — TextMate grammar
  - Canonical (th3w1zard1/HoloLSP): <https://github.com/th3w1zard1/HoloLSP/blob/80f2e64bf508a6b487d8f3ecf9ab9cb6812222a2/syntaxes/nwscript.tmLanguage.json#L1>
- [`nwscript-mode.el/nwscript-mode.el`](https://github.com/implicit-image/nwscript-mode.el/blob/master/nwscript-mode.el) - Emacs mode for NWScript
- **`nwscript-ts-mode/`** - TypeScript mode for NWScript
  - Upstream (implicit-image/nwscript-ts-mode): <https://github.com/implicit-image/nwscript-ts-mode/tree/8108740ca304d7acbb89ef5a4d9327b430d33fad>
  - Mirror (th3w1zard1/nwscript-ts-mode): <https://github.com/th3w1zard1/nwscript-ts-mode/tree/8108740ca304d7acbb89ef5a4d9327b430d33fad>

**Original Sources:**

- [`Vanilla_KOTOR_Script_Source`](https://github.com/KOTORCommunityPatches/Vanilla_KOTOR_Script_Source) - Original KotOR script sources including nwscript.nss
- [`Vanilla_KOTOR_Script_Source/K1/Data/scripts.bif/`](https://github.com/KOTORCommunityPatches/Vanilla_KOTOR_Script_Source/tree/master/K1/Data/scripts.bif) - KotOR 1 script sources from [BIF](Container-Formats#bif)
- [`Vanilla_KOTOR_Script_Source/TSL/Vanilla/Data/Scripts/`](https://github.com/KOTORCommunityPatches/Vanilla_KOTOR_Script_Source/tree/master/TSL/Vanilla/Data/Scripts) - KotOR 2 script sources
- **`KotOR-Scripting-Tool/NWN Script/k1/nwscript.nss`** - KotOR 1 nwscript.nss
  - Upstream (KobaltBlu/KotOR-Scripting-Tool): <https://github.com/KobaltBlu/KotOR-Scripting-Tool/blob/ddd580e1b85e9c25bf5eea77a0b6938e396579c6/NWN%20Script/k1/nwscript.nss>
  - Mirror (th3w1zard1/KotOR-Scripting-Tool): <https://github.com/th3w1zard1/KotOR-Scripting-Tool/blob/ddd580e1b85e9c25bf5eea77a0b6938e396579c6/NWN%20Script/k1/nwscript.nss>
- **`KotOR-Scripting-Tool/NWN Script/k2/nwscript.nss`** - KotOR 2 nwscript.nss
  - Upstream (KobaltBlu/KotOR-Scripting-Tool): <https://github.com/KobaltBlu/KotOR-Scripting-Tool/blob/ddd580e1b85e9c25bf5eea77a0b6938e396579c6/NWN%20Script/k2/nwscript.nss>
  - Mirror (th3w1zard1/KotOR-Scripting-Tool): <https://github.com/th3w1zard1/KotOR-Scripting-Tool/blob/ddd580e1b85e9c25bf5eea77a0b6938e396579c6/NWN%20Script/k2/nwscript.nss>
- [`NorthernLights/Scripts/k1_nwscript.nss`](https://github.com/lachjames/NorthernLights/blob/master/Scripts/k1_nwscript.nss) - KotOR 1 nwscript.nss (NorthernLights)
- [`NorthernLights/Scripts/k2_nwscript.nss`](https://github.com/lachjames/NorthernLights/blob/master/Scripts/k2_nwscript.nss) - KotOR 2 nwscript.nss (NorthernLights)

**PyKotor Implementation:**

- [`Libraries/PyKotor/src/pykotor/common/script.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/script.py) - data structures (ScriptFunction, ScriptConstant, DataType)
- [`Libraries/PyKotor/src/pykotor/common/scriptdefs.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py) - Function and constant definitions (772 K1 functions, 1489 K1 constants)
- [`Libraries/PyKotor/src/pykotor/common/scriptlib.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptlib.py) - Library file definitions (k_inc_generic, k_inc_utility, etc.)
- [`Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_auto.py:126-205`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_auto.py) - Compilation integration

**Other Implementations:**

- [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9) — C# [NCS](NCS-File-Format) model (`Kotor.NET/Formats/KotorNCS/`)
- **`KotORModSync/KOTORModSync.Core/Data/NWScriptHeader.cs`** - C# NWScript header parser
  - Canonical (th3w1zard1/KotORModSync): <https://github.com/th3w1zard1/KotORModSync/blob/c8b0d10ce3fd7525d593d34a3be8d151da7d3387/KOTORModSync.Core/Data/NWScriptHeader.cs>
- **`KotORModSync/KOTORModSync.Core/Data/NWScriptFileReader.cs`** - C# NWScript file reader
  - Canonical (th3w1zard1/KotORModSync): <https://github.com/th3w1zard1/KotORModSync/blob/c8b0d10ce3fd7525d593d34a3be8d151da7d3387/KOTORModSync.Core/Data/NWScriptFileReader.cs>

**NWScript VM and Execution:**

- [`reone/src/libs/script/format/ncsreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/script/format/ncsreader.cpp) - [NCS](NCS-File-Format) bytecode reader
- [`reone/src/libs/script/format/ncswriter.cpp`](https://github.com/modawan/reone/blob/master/src/libs/script/format/ncswriter.cpp) - [NCS](NCS-File-Format) bytecode writer
- [`xoreos/src/aurora/nwscript/`](https://github.com/xoreos/xoreos/tree/master/src/aurora/nwscript) - NWScript VM implementation
- [`xoreos/src/aurora/nwscript/ncsfile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/nwscript/ncsfile.cpp) - [NCS file](NCS-File-Format) parsing and execution
- [`xoreos/src/aurora/nwscript/object.h`](https://github.com/xoreos/xoreos/blob/master/src/aurora/nwscript/object.h) - NWScript object type definitions
- [`xoreos/src/engines/kotorbase/object.h`](https://github.com/xoreos/xoreos/blob/master/src/engines/kotorbase/object.h) - KotOR object implementation
- [`NorthernLights/Assets/Scripts/ncs/control.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/control.cs) - Unity C# [NCS](NCS-File-Format) VM control
- [`NorthernLights/Assets/Scripts/ncs/NCSReader.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/NCSReader.cs) - Unity C# [NCS](NCS-File-Format) reader
- [`KotOR.js/src/nwscript/NWScript.ts` L39+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScript.ts#L39) — TypeScript NCS container (`NWScript.Load`, instruction map, `newInstance`)
- [`KotOR.js/src/nwscript/NWScriptInstance.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptInstance.ts) - TypeScript NWScript instance
- [`KotOR.js/src/nwscript/NWScriptStack.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptStack.ts) - TypeScript stack implementation
- [`KotOR.js/src/nwscript/NWScriptSubroutine.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptSubroutine.ts) - TypeScript subroutine handling

**Documentation and Specifications:**

- [`xoreos-docs/`](https://github.com/xoreos/xoreos-docs) - xoreos documentation including format specifications
- [`xoreos-docs/specs/torlack/ncs.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/ncs.html) - [NCS](NCS-File-Format) format specification (if available)

**NWScript Language Support:**

- **`HoloLSP/server/src/kotor-definitions.ts` L4+** — KotOR function/constant typings (generated from PyKotor `scriptdefs.py`, per file header)
  - Canonical (th3w1zard1/HoloLSP): <https://github.com/th3w1zard1/HoloLSP/blob/80f2e64bf508a6b487d8f3ecf9ab9cb6812222a2/server/src/kotor-definitions.ts#L4>
- **`HoloLSP/server/src/nwscript-runtime.ts` L6+** — NWScript runtime / interpreter integration
  - Canonical (th3w1zard1/HoloLSP): <https://github.com/th3w1zard1/HoloLSP/blob/80f2e64bf508a6b487d8f3ecf9ab9cb6812222a2/server/src/nwscript-runtime.ts#L6>
- **`HoloLSP/server/src/server.ts` L1+** — Language server entry (completions, diagnostics, NWScript)
  - Canonical (th3w1zard1/HoloLSP): <https://github.com/th3w1zard1/HoloLSP/blob/80f2e64bf508a6b487d8f3ecf9ab9cb6812222a2/server/src/server.ts#L1>

**NWScript Parsing and Compilation:**

- [`xoreos-tools/src/nwscript/decompiler.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/decompiler.cpp) - [NCS](NCS-File-Format) decompiler implementation

**NWScript Execution:**

- [`reone/src/libs/script/virtualmachine.cpp` L36+](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/script/virtualmachine.cpp#L36) — Script VM (`VirtualMachine` implementation)
- [`reone/include/reone/script/virtualmachine.h` L41+](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/include/reone/script/virtualmachine.h#L41) — `VirtualMachine` declaration
- [`reone/src/libs/script/program.cpp` L28+](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/script/program.cpp#L28) — `ScriptProgram` bytecode container (`add`, instruction helpers)
- [`xoreos/src/aurora/nwscript/execution.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/nwscript/execution.cpp) - NWScript execution engine
- [`xoreos/src/aurora/nwscript/variable.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/nwscript/variable.cpp) - Variable handling
- [`xoreos/src/aurora/nwscript/function.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/nwscript/function.cpp) - Function call handling
- [`NorthernLights/Assets/Scripts/ncs/control.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/control.cs) - Unity C# [NCS](NCS-File-Format) VM control and execution
- [`KotOR.js/src/nwscript/NWScriptInstance.ts` L32+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptInstance.ts#L32) — Per-script execution state (`run` / `runScript`, stack, instruction stepping)

**Routine Implementations:**

- [`reone/src/libs/script/routine/main/`](https://github.com/modawan/reone/tree/master/src/libs/script/routine/main) - Main routine implementations
- [`reone/src/libs/script/routine/action/`](https://github.com/modawan/reone/tree/master/src/libs/script/routine/action) - Action routine implementations
- [`reone/src/libs/script/routine/effect/`](https://github.com/modawan/reone/tree/master/src/libs/script/routine/effect) - Effect routine implementations
- [`xoreos/src/engines/kotorbase/script/routines.cpp`](https://github.com/xoreos/xoreos/blob/master/src/engines/kotorbase/script/routines.cpp) - KotOR-specific routine implementations

**NWScript type System:**

- [`xoreos/src/aurora/nwscript/types.h`](https://github.com/xoreos/xoreos/blob/master/src/aurora/nwscript/types.h) - NWScript type definitions
- [`xoreos/src/aurora/nwscript/types.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/nwscript/types.cpp) - type system implementation
- [`KotOR.js/src/enums/nwscript/NWScriptDataType.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/enums/nwscript/NWScriptDataType.ts) - TypeScript data type enumerations
- [`KotOR.js/src/enums/nwscript/NWScriptTypes.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/enums/nwscript/NWScriptTypes.ts) - TypeScript type definitions

**NWScript Events:**

- [`KotOR.js/src/nwscript/events/NWScriptEvent.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/events/NWScriptEvent.ts) - Event handling
- [`KotOR.js/src/nwscript/events/NWScriptEventFactory.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/events/NWScriptEventFactory.ts) - Event factory
- [`KotOR.js/src/enums/nwscript/NWScriptEventType.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/enums/nwscript/NWScriptEventType.ts) - Event type enumerations

**NWScript Bytecode:**

- [`KotOR.js/src/nwscript/NWScriptOPCodes.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptOPCodes.ts) - Opcode definitions
- [`KotOR.js/src/nwscript/NWScriptInstruction.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptInstruction.ts) - Instruction handling
- [`KotOR.js/src/nwscript/NWScriptInstructionInfo.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptInstructionInfo.ts) - Instruction information
- [`KotOR.js/src/enums/nwscript/NWScriptByteCode.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/enums/nwscript/NWScriptByteCode.ts) - Bytecode enumerations

**NWScript Stack:**

- [`KotOR.js/src/nwscript/NWScriptStack.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptStack.ts) - Stack implementation
- [`KotOR.js/src/nwscript/NWScriptStackVariable.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptStackVariable.ts) - Stack variable handling

**NWScript Interface Definitions:**

- [`KotOR.js/src/interface/nwscript/INWScriptStoreState.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/interface/nwscript/INWScriptStoreState.ts) - Store state interface
- [`KotOR.js/src/interface/nwscript/INWScriptDefAction.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/interface/nwscript/INWScriptDefAction.ts) - Action definition interface

**NWScript AST and Parsing:**

- [`KotOR.js/src/nwscript/compiler/NWScriptCompiler.ts` L95+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/compiler/NWScriptCompiler.ts#L95) — NSS → NCS compiler pipeline (`NWScriptCompiler`)
- [`KotOR.js/src/nwscript/compiler/ASTTypes.ts` L4+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/compiler/ASTTypes.ts#L4) — Compiler AST node types (`ProgramNode`, `FunctionNode`, …)
- **`HoloLSP/server/src/nwscript-ast.ts` L7+** — LSP-side AST definitions
  - Canonical (th3w1zard1/HoloLSP): <https://github.com/th3w1zard1/HoloLSP/blob/80f2e64bf508a6b487d8f3ecf9ab9cb6812222a2/server/src/nwscript-ast.ts#L7>

**Game-Specific NWScript Extensions:**

- [`xoreos/src/engines/kotorbase/script/routines.cpp`](https://github.com/xoreos/xoreos/blob/master/src/engines/kotorbase/script/routines.cpp) - KotOR-specific routine implementations
- [`xoreos/src/engines/nwn/script/functions_action.cpp`](https://github.com/xoreos/xoreos/blob/master/src/engines/nwn/script/functions_action.cpp) - NWN action function implementations
- [`NorthernLights/Assets/Scripts/ncs/constants.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/constants.cs) - NWScript constant definitions
- [`reone/src/libs/game/script/routines.cpp`](https://github.com/modawan/reone/blob/master/src/libs/game/script/routines.cpp) - Game-specific routine implementations
- [`reone/include/reone/game/script/routines.h`](https://github.com/modawan/reone/blob/master/include/reone/game/script/routines.h) - Game routine header
- [`xoreos-tools/src/nwscript/subroutine.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/subroutine.cpp) - Subroutine handling
- [`xoreos-tools/src/nwscript/subroutine.h`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/subroutine.h) - Subroutine header
- [`xoreos/src/engines/kotorbase/types.h`](https://github.com/xoreos/xoreos/blob/master/src/engines/kotorbase/types.h) - KotOR type definitions including base item types
- [`KotOR.js/src/module/Module.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/module/Module.ts) - Module loading and management
- [`KotOR.js/src/module/ModuleArea.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/module/ModuleArea.ts) - Area management and transitions
- [`xoreos/src/engines/nwn/module.cpp`](https://github.com/xoreos/xoreos/blob/master/src/engines/nwn/module.cpp) - NWN module implementation
- [`xoreos/src/engines/nwn2/module.cpp`](https://github.com/xoreos/xoreos/blob/master/src/engines/nwn2/module.cpp) - NWN2 module implementation
- [`xoreos/src/engines/nwn2/module.h`](https://github.com/xoreos/xoreos/blob/master/src/engines/nwn2/module.h) - NWN2 module header
- [`xoreos/src/engines/dragonage2/script/functions_module.cpp`](https://github.com/xoreos/xoreos/blob/master/src/engines/dragonage2/script/functions_module.cpp) - Dragon Age 2 module functions
- [`xoreos/src/engines/nwn/script/functions_effect.cpp`](https://github.com/xoreos/xoreos/blob/master/src/engines/nwn/script/functions_effect.cpp) - NWN effect function implementations
- [`xoreos/src/engines/nwn/script/functions_object.cpp`](https://github.com/xoreos/xoreos/blob/master/src/engines/nwn/script/functions_object.cpp) - NWN object function implementations
- [`xoreos/src/engines/nwn2/script/functions.cpp`](https://github.com/xoreos/xoreos/blob/master/src/engines/nwn2/script/functions.cpp) - NWN2 function implementations
- [`reone/src/libs/script/routine/action/`](https://github.com/modawan/reone/tree/master/src/libs/script/routine/action) - Action routine implementations
- [`reone/src/libs/script/routine/effect/`](https://github.com/modawan/reone/tree/master/src/libs/script/routine/effect) - Effect routine implementations
- [`reone/src/libs/script/routine/object/`](https://github.com/modawan/reone/tree/master/src/libs/script/routine/object) - Object routine implementations
- [`reone/src/libs/script/routine/party/`](https://github.com/modawan/reone/tree/master/src/libs/script/routine/party) - Party routine implementations
- [`reone/src/libs/script/routine/combat/`](https://github.com/modawan/reone/tree/master/src/libs/script/routine/combat) - Combat routine implementations
- [`NorthernLights/Assets/Scripts/ncs/nwscript_actions.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/nwscript_actions.cs) - Complete actions table mapping routine numbers to function names
- [`NorthernLights/Assets/Scripts/Systems/AuroraActions/AuroraAction.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/Systems/AuroraActions/AuroraAction.cs) - Action system implementation

---

### Other Constants

See [Other Constants](NSS-File-Format#other-constants) for detailed documentation.

## Related systems

- **[NCS File Format](NCS-File-Format)**: Compiled bytecode format that NSS compiles to
- **[GFF File Format](GFF-File-Format)**: Scripts are stored in [GFF](GFF-File-Format) templates such as:

  - [UTC](GFF-File-Format#utc-creature)
  - [UTD](GFF-File-Format#utd-door)
  - [UTP](GFF-File-Format#utp-placeable)
  - [IFO](GFF-File-Format#ifo-module-info)
  - (see [GFF File Format](GFF-File-Format) for the full type index)
- **[KEY File Format](Container-Formats#key)**: nwscript.nss is stored in [chitin.key](Container-Formats#key)

### See also

- [NCS File Format](NCS-File-Format) -- Compiled NWScript bytecode
- [NSS Shared Functions - Actions](NSS-File-Format#actions) -- Action functions
- [NSS Shared Constants](NSS-File-Format#object-type-constants) -- Object type and script constants
- [GFF-DLG](GFF-Creature-and-Dialogue#dlg) -- Dialogue files that trigger NCS scripts
- [2DA File Format](2DA-File-Format) -- Game data tables referenced by scripts
- [Home](Home#community-sources-and-archives) -- Community sources and archives
