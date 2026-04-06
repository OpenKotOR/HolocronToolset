# NSS — NWScript Source

NSS files contain human-readable NWScript source code — the scripting language that controls game logic in Knights of the Old Republic and The Sith Lords ([`NssParser` L80](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compiler/parser.py#L80), [xoreos-tools `src/nwscript/`](https://github.com/xoreos/xoreos-tools/tree/master/src/nwscript)). The engine does not execute NSS directly; source files are compiled to [NCS bytecode](NCS-File-Format) before they can run ([`InbuiltNCSCompiler.compile_script` L51](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compilers.py#L51), [KotOR-Scripting-Tool](https://github.com/KobaltBlu/KotOR-Scripting-Tool)). The master include file `nwscript.nss` defines all engine-exposed functions and constants available to scripts; KotOR and TSL each ship their own version with game-specific additions ([`KOTOR_FUNCTIONS` L3268](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L3268), [`KOTOR_CONSTANTS` L12](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L12), [Vanilla_KOTOR_Script_Source](https://github.com/KOTORCommunityPatches/Vanilla_KOTOR_Script_Source)).

NWScript is a C-like language with strong typing, automatic garbage collection for strings, and a fixed set of engine action routines ([reone `VirtualMachine` L41](https://github.com/seedhartha/reone/blob/master/include/reone/script/virtualmachine.h#L41), [xoreos `src/aurora/nwscript/`](https://github.com/xoreos/xoreos/tree/master/src/aurora/nwscript), [KotOR.js `NWScript` L39](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScript.ts#L39)). Scripts interact with the game world through these action routines — spawning creatures, modifying objects, running dialogue branches, applying effects — and are triggered from [GFF](GFF-File-Format) resources: [DLG](GFF-Creature-and-Dialogue#dlg) dialogue files, [UTC](GFF-File-Format#utc-creature) creatures, [UTD](GFF-Spatial-Objects#utd) doors, [UTP](GFF-Spatial-Objects#utp) placeables, and [IFO](GFF-Module-and-Area#ifo) module definitions. Scripts also commonly read [2DA](2DA-File-Format) configuration data at runtime. Like all resources, NSS files are resolved through the standard [resource resolution order](Concepts#resource-resolution-order) (override → MOD/SAV → KEY/BIF).

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

- [`script.py` L21+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/script.py#L21) (data structures)
- [`KOTOR_CONSTANTS` L12+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L12) (constants)
- [`KOTOR_FUNCTIONS` L3268+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L3268) (function signatures)
- [`scriptlib.py` L5+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptlib.py#L5) (`#include` library text)
- [`compilers.py` `InbuiltNCSCompiler` L28+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compilers.py#L28)
- [`parser.py` `NssParser` L80+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compiler/parser.py#L80)

---

## Shared Functions (K1 & TSL)

<!-- SHARED_FUNCTIONS_START -->

### Abilities and Stats

<a id="getcurrenthitpoints"></a>

#### `GetCurrentHitPoints(oObject=0)` - Routine 49

Get the current hitpoints of oObject
* Return value on error: 0

**Parameters:**

- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getmaxhitpoints"></a>

#### `GetMaxHitPoints(oObject=0)` - Routine 50

Get the maximum hitpoints of oObject
* Return value on error: 0

**Parameters:**

- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getcurrentforcepoints"></a>

#### `GetCurrentForcePoints(oObject=0)` - Routine 55

returns the current force points for the creature

**Parameters:**

- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getmaxforcepoints"></a>

#### `GetMaxForcePoints(oObject=0)` - Routine 56

returns the Max force points for the creature

**Parameters:**

- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getabilityscore"></a>

#### `GetAbilityScore(oCreature, nAbilityType)` - Routine 139

Get the ability score of type nAbility for a creature (otherwise 0)
- oCreature: the creature whose ability score we wish to find out
- nAbilityType: ABILITY_*
Return value on error: 0

**Parameters:**

- `oCreature`: `object`
- `nAbilityType`: `int`

**Returns:** `int`

<a id="getreflexadjusteddamage"></a>

#### `GetReflexAdjustedDamage(nDamage, oTarget, nDC, nSaveType=0, oSaveVersus=0)` - Routine 299

Use this in spell scripts to get nDamage adjusted by oTarget's reflex and
evasion saves.
- nDamage
- oTarget
- nDC: Difficulty check
- nSaveType: SAVING_THROW_TYPE_*
- oSaveVersus

**Parameters:**

- `nDamage`: `int`
- `oTarget`: `object`
- `nDC`: `int`
- `nSaveType`: `int` (default: `0`)
- `oSaveVersus`: `object` (default: `0`)

**Returns:** `int`

<a id="getabilitymodifier"></a>

#### `GetAbilityModifier(nAbility, oCreature=0)` - Routine 331

Returns the ability modifier for the specified ability
Get oCreature's ability modifier for nAbility.
- nAbility: ABILITY_*
- oCreature

**Parameters:**

- `nAbility`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getfortitudesavingthrow"></a>

#### `GetFortitudeSavingThrow(oTarget)` - Routine 491

Get oTarget's base fortitude saving throw value (this will only work for
creatures, doors, and placeables).
* Returns 0 if oTarget is invalid.

**Parameters:**

- `oTarget`: `object`

**Returns:** `int`

<a id="getwillsavingthrow"></a>

#### `GetWillSavingThrow(oTarget)` - Routine 492

Get oTarget's base will saving throw value (this will only work for creatures,
doors, and placeables).
* Returns 0 if oTarget is invalid.

**Parameters:**

- `oTarget`: `object`

**Returns:** `int`

<a id="getreflexsavingthrow"></a>

#### `GetReflexSavingThrow(oTarget)` - Routine 493

Get oTarget's base reflex saving throw value (this will only work for
creatures, doors, and placeables).
* Returns 0 if oTarget is invalid.

**Parameters:**

- `oTarget`: `object`

**Returns:** `int`

<a id="swmg_adjustfollowerhitpoints"></a>

#### `SWMG_AdjustFollowerHitPoints(oFollower, nHP, nAbsolute=0)` - Routine 590

adjusts a followers hit points, can specify the absolute value to set to
SWMG_AdjustFollowerHitPoints

**Parameters:**

- `oFollower`: `object`
- `nHP`: `int`
- `nAbsolute`: `int` (default: `0`)

**Returns:** `int`

<a id="swmg_setfollowerhitpoints"></a>

#### `SWMG_SetFollowerHitPoints(oFollower, nHP)` - Routine 604

SWMG_SetFollowerHitPoints

**Parameters:**

- `oFollower`: `object`
- `nHP`: `int`

<a id="swmg_gethitpoints"></a>

#### `SWMG_GetHitPoints(oFollower)` - Routine 616

SWMG_GetHitPoints

**Parameters:**

- `oFollower`: `object`

**Returns:** `int`

<a id="swmg_getmaxhitpoints"></a>

#### `SWMG_GetMaxHitPoints(oFollower)` - Routine 617

SWMG_GetMaxHitPoints

**Parameters:**

- `oFollower`: `object`

**Returns:** `int`

<a id="swmg_setmaxhitpoints"></a>

#### `SWMG_SetMaxHitPoints(oFollower, nMaxHP)` - Routine 618

SWMG_SetMaxHitPoints

**Parameters:**

- `oFollower`: `object`
- `nMaxHP`: `int`

<a id="setmaxhitpoints"></a>

#### `SetMaxHitPoints(oObject, nMaxHP)` - Routine 758

SetMaxHitPoints
Set the maximum hitpoints of oObject
The objects maximum AND current hitpoints will be nMaxHP after the function is called

**Parameters:**

- `oObject`: `object`
- `nMaxHP`: `int`
### Actions

<a id="assigncommand"></a>

#### `AssignCommand(oActionSubject, aActionToAssign)` - Routine 6

Assign aActionToAssign to oActionSubject.
* No return value, but if an error occurs, the log file will contain
"AssignCommand failed."
(If the object doesn't exist, nothing happens.)

**Parameters:**

- `oActionSubject`: `object`
- `aActionToAssign`: `action`

<a id="delaycommand"></a>

#### `DelayCommand(fSeconds, aActionToDelay)` - Routine 7

Delay aActionToDelay by fSeconds.
* No return value, but if an error occurs, the log file will contain
"DelayCommand failed.".

**Parameters:**

- `fSeconds`: `float`
- `aActionToDelay`: `action`

<a id="clearallactions"></a>

#### `ClearAllActions()` - Routine 9

Clear all the actions of the caller. (This will only work on Creatures)
* No return value, but if an error occurs, the log file will contain
"ClearAllActions failed.".

<a id="actionrandomwalk"></a>

#### `ActionRandomWalk()` - Routine 20

The action subject will generate a random location near its current location
and pathfind to it.  All commands will remove a RandomWalk() from the action
queue if there is one in place.
* No return value, but if an error occurs the log file will contain
"ActionRandomWalk failed."

<a id="actionmovetolocation"></a>

#### `ActionMoveToLocation(lDestination, bRun=0)` - Routine 21

The action subject will move to lDestination.
- lDestination: The object will move to this location.  If the location is
invalid or a path cannot be found to it, the command does nothing.
- bRun: If this is TRUE, the action subject will run rather than walk
* No return value, but if an error occurs the log file will contain
"MoveToPoint failed."

**Parameters:**

- `lDestination`: `location`
- `bRun`: `int` (default: `0`)

<a id="actionmovetoobject"></a>

#### `ActionMoveToObject(oMoveTo, bRun=0, fRange=1.0)` - Routine 22

Cause the action subject to move to a certain distance from oMoveTo.
If there is no path to oMoveTo, this command will do nothing.
- oMoveTo: This is the object we wish the action subject to move to
- bRun: If this is TRUE, the action subject will run rather than walk
- fRange: This is the desired distance between the action subject and oMoveTo
* No return value, but if an error occurs the log file will contain
"ActionMoveToObject failed."

**Parameters:**

- `oMoveTo`: `object`
- `bRun`: `int` (default: `0`)
- `fRange`: `float` (default: `1.0`)

<a id="actionmoveawayfromobject"></a>

#### `ActionMoveAwayFromObject(oFleeFrom, bRun=0, fMoveAwayRange=40.0)` - Routine 23

Cause the action subject to move to a certain distance away from oFleeFrom.
- oFleeFrom: This is the object we wish the action subject to move away from.
If oFleeFrom is not in the same area as the action subject, nothing will
happen.
- bRun: If this is TRUE, the action subject will run rather than walk
- fMoveAwayRange: This is the distance we wish the action subject to put
between themselves and oFleeFrom
* No return value, but if an error occurs the log file will contain
"ActionMoveAwayFromObject failed."

**Parameters:**

- `oFleeFrom`: `object`
- `bRun`: `int` (default: `0`)
- `fMoveAwayRange`: `float` (default: `40.0`)

<a id="actionspeakstring"></a>

#### `ActionSpeakString(sStringToSpeak, nTalkVolume=0)` - Routine 39

Add a speak action to the action subject.
- sStringToSpeak: String to be spoken
- nTalkVolume: TALKVOLUME_*

**Parameters:**

- `sStringToSpeak`: `string`
- `nTalkVolume`: `int` (default: `0`)

<a id="actionplayanimation"></a>

#### `ActionPlayAnimation(nAnimation, fSpeed=1.0, fDurationSeconds=0.0)` - Routine 40

Cause the action subject to play an animation
- nAnimation: ANIMATION_*
- fSpeed: Speed of the animation
- fDurationSeconds: Duration of the animation (this is not used for Fire and
Forget animations) If a time of -1.0f is specified for a looping animation
it will loop until the next animation is applied.

**Parameters:**

- `nAnimation`: `int`
- `fSpeed`: `float` (default: `1.0`)
- `fDurationSeconds`: `float` (default: `0.0`)

<a id="actionopendoor"></a>

#### `ActionOpenDoor(oDoor)` - Routine 43

Cause the action subject to open oDoor

**Parameters:**

- `oDoor`: `object`

<a id="actionclosedoor"></a>

#### `ActionCloseDoor(oDoor)` - Routine 44

Cause the action subject to close oDoor

**Parameters:**

- `oDoor`: `object`

<a id="actionforcefollowobject"></a>

#### `ActionForceFollowObject(oFollow, fFollowDistance=0.0)` - Routine 167

The action subject will follow oFollow until a ClearAllActions() is called.
- oFollow: this is the object to be followed
- fFollowDistance: follow distance in metres
* No return value

**Parameters:**

- `oFollow`: `object`
- `fFollowDistance`: `float` (default: `0.0`)

<a id="actionjumptoobject"></a>

#### `ActionJumpToObject(oToJumpTo, bWalkStraightLineToPoint=1)` - Routine 196

Jump to an object ID, or as near to it as possible.

**Parameters:**

- `oToJumpTo`: `object`
- `bWalkStraightLineToPoint`: `int` (default: `1`)

<a id="actionwait"></a>

#### `ActionWait(fSeconds)` - Routine 202

Do nothing for fSeconds seconds.

**Parameters:**

- `fSeconds`: `float`

<a id="actionjumptolocation"></a>

#### `ActionJumpToLocation(lLocation)` - Routine 214

The subject will jump to lLocation instantly (even between areas).
If lLocation is invalid, nothing will happen.

**Parameters:**

- `lLocation`: `location`

<a id="actionspeakstringbystrref"></a>

#### `ActionSpeakStringByStrRef(nStrRef, nTalkVolume=0)` - Routine 240

Causes the creature to speak a translated string.
- nStrRef: Reference of the string in the talk table
- nTalkVolume: TALKVOLUME_*

**Parameters:**

- `nStrRef`: `int`
- `nTalkVolume`: `int` (default: `0`)

<a id="actionusefeat"></a>

#### `ActionUseFeat(nFeat, oTarget)` - Routine 287

Use nFeat on oTarget.
- nFeat: FEAT_*
- oTarget

**Parameters:**

- `nFeat`: `int`
- `oTarget`: `object`

<a id="actionuseskill"></a>

#### `ActionUseSkill(nSkill, oTarget, nSubSkill=0, oItemUsed=1)` - Routine 288

Runs the action "UseSkill" on the current creature
Use nSkill on oTarget.
- nSkill: SKILL_*
- oTarget
- nSubSkill: SUBSKILL_*
- oItemUsed: Item to use in conjunction with the skill

**Parameters:**

- `nSkill`: `int`
- `oTarget`: `object`
- `nSubSkill`: `int` (default: `0`)
- `oItemUsed`: `object` (default: `1`)

<a id="actiondocommand"></a>

#### `ActionDoCommand(aActionToDo)` - Routine 294

Do aActionToDo.

**Parameters:**

- `aActionToDo`: `action`

<a id="actionusetalentonobject"></a>

#### `ActionUseTalentOnObject(tChosenTalent, oTarget)` - Routine 309

Use tChosenTalent on oTarget.

**Parameters:**

- `tChosenTalent`: `talent`
- `oTarget`: `object`

<a id="actionusetalentatlocation"></a>

#### `ActionUseTalentAtLocation(tChosenTalent, lTargetLocation)` - Routine 310

Use tChosenTalent at lTargetLocation.

**Parameters:**

- `tChosenTalent`: `talent`
- `lTargetLocation`: `location`

<a id="actioninteractobject"></a>

#### `ActionInteractObject(oPlaceable)` - Routine 329

Use oPlaceable.

**Parameters:**

- `oPlaceable`: `object`

<a id="actionmoveawayfromlocation"></a>

#### `ActionMoveAwayFromLocation(lMoveAwayFrom, bRun=0, fMoveAwayRange=40.0)` - Routine 360

Causes the action subject to move away from lMoveAwayFrom.

**Parameters:**

- `lMoveAwayFrom`: `location`
- `bRun`: `int` (default: `0`)
- `fMoveAwayRange`: `float` (default: `40.0`)

<a id="actionsurrendertoenemies"></a>

#### `ActionSurrenderToEnemies()` - Routine 379

<a id="actionequipmostdamagingmelee"></a>

#### `ActionEquipMostDamagingMelee(oVersus=1, bOffHand=0)` - Routine 399

The creature will equip the melee weapon in its possession that can do the
most damage. If no valid melee weapon is found, it will equip the most
damaging range weapon. This function should only ever be called in the
EndOfCombatRound scripts, because otherwise it would have to stop the combat
round to run simulation.
- oVersus: You can try to get the most damaging weapon against oVersus
- bOffHand

**Parameters:**

- `oVersus`: `object` (default: `1`)
- `bOffHand`: `int` (default: `0`)

<a id="actionequipmostdamagingranged"></a>

#### `ActionEquipMostDamagingRanged(oVersus=1)` - Routine 400

The creature will equip the range weapon in its possession that can do the
most damage.
If no valid range weapon can be found, it will equip the most damaging melee
weapon.
- oVersus: You can try to get the most damaging weapon against oVersus

**Parameters:**

- `oVersus`: `object` (default: `1`)

<a id="actionequipmosteffectivearmor"></a>

#### `ActionEquipMostEffectiveArmor()` - Routine 404

The creature will equip the armour in its possession that has the highest
armour class.

<a id="actionunlockobject"></a>

#### `ActionUnlockObject(oTarget)` - Routine 483

The action subject will unlock oTarget, which can be a door or a placeable
object.

**Parameters:**

- `oTarget`: `object`

<a id="actionlockobject"></a>

#### `ActionLockObject(oTarget)` - Routine 484

The action subject will lock oTarget, which can be a door or a placeable
object.

**Parameters:**

- `oTarget`: `object`

<a id="actioncastfakespellatobject"></a>

#### `ActionCastFakeSpellAtObject(nSpell, oTarget, nProjectilePathType=0)` - Routine 501

The action subject will fake casting a spell at oTarget; the conjure and cast
animations and visuals will occur, nothing else.
- nSpell
- oTarget
- nProjectilePathType: PROJECTILE_PATH_TYPE_*

**Parameters:**

- `nSpell`: `int`
- `oTarget`: `object`
- `nProjectilePathType`: `int` (default: `0`)

<a id="actioncastfakespellatlocation"></a>

#### `ActionCastFakeSpellAtLocation(nSpell, lTarget, nProjectilePathType=0)` - Routine 502

The action subject will fake casting a spell at lLocation; the conjure and
cast animations and visuals will occur, nothing else.
- nSpell
- lTarget
- nProjectilePathType: PROJECTILE_PATH_TYPE_*

**Parameters:**

- `nSpell`: `int`
- `lTarget`: `location`
- `nProjectilePathType`: `int` (default: `0`)

<a id="getcurrentaction"></a>

#### `GetCurrentAction(oObject=0)` - Routine 522

Get the current action (ACTION_*) that oObject is executing.

**Parameters:**

- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="actionbarkstring"></a>

#### `ActionBarkString(strRef)`

700. ActionBarkString
this will cause a creature to bark the strRef from the talk table.

**Parameters:**

- `strRef`: `int`

<a id="actionfollowleader"></a>

#### `ActionFollowLeader()`

730. ActionFollowLeader
this action has a party member follow the leader.
DO NOT USE ON A CREATURE THAT IS NOT IN THE PARTY!!
### Alignment System

<a id="getgoodevilvalue"></a>

#### `GetGoodEvilValue(oCreature)` - Routine 125

Get an integer between 0 and 100 (inclusive) to represent oCreature's
Good/Evil alignment
(100=good, 0=evil)
* Return value if oCreature is not a valid creature: -1

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="getalignmentgoodevil"></a>

#### `GetAlignmentGoodEvil(oCreature)` - Routine 127

Return an ALIGNMENT_* constant to represent oCreature's good/evil alignment
* Return value if oCreature is not a valid creature: -1

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="getfactionequal"></a>

#### `GetFactionEqual(oFirstObject, oSecondObject=0)` - Routine 172

* Returns TRUE if the Faction Ids of the two objects are the same

**Parameters:**

- `oFirstObject`: `object`
- `oSecondObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getfactionaveragegoodevilalignment"></a>

#### `GetFactionAverageGoodEvilAlignment(oFactionMember)` - Routine 187

Get an integer between 0 and 100 (inclusive) that represents the average
good/evil alignment of oFactionMember's faction.
* Return value on error: -1

**Parameters:**

- `oFactionMember`: `object`

**Returns:** `int`

<a id="adjustalignment"></a>

#### `AdjustAlignment(oSubject, nAlignment, nShift)` - Routine 201

Adjust the alignment of oSubject.
- oSubject
- nAlignment:
-> ALIGNMENT_LIGHT_SIDE/ALIGNMENT_DARK_SIDE: oSubject's
alignment will be shifted in the direction specified
-> ALIGNMENT_NEUTRAL: nShift is applied to oSubject's dark side/light side
alignment value in the direction which is towards neutrality.
e.g. If oSubject has an alignment value of 80 (i.e. light side)
then if nShift is 15, the alignment value will become (80-15)=65
Furthermore, the shift will at most take the alignment value to 50 and
not beyond.
e.g. If oSubject has an alignment value of 40 then if nShift is 15,
the aligment value will become 50
- nShift: this is the desired shift in alignment
* No return value

**Parameters:**

- `oSubject`: `object`
- `nAlignment`: `int`
- `nShift`: `int`

<a id="getreputation"></a>

#### `GetReputation(oSource, oTarget)` - Routine 208

Get an integer between 0 and 100 (inclusive) that represents how oSource
feels about oTarget.
-> 0-10 means oSource is hostile to oTarget
-> 11-89 means oSource is neutral to oTarget
-> 90-100 means oSource is friendly to oTarget
* Returns -1 if oSource or oTarget does not identify a valid object

**Parameters:**

- `oSource`: `object`
- `oTarget`: `object`

**Returns:** `int`

<a id="getisenemy"></a>

#### `GetIsEnemy(oTarget, oSource=0)` - Routine 235

* Returns TRUE if oSource considers oTarget as an enemy.

**Parameters:**

- `oTarget`: `object`
- `oSource`: `object` (default: `0`)

**Returns:** `int`

<a id="getisfriend"></a>

#### `GetIsFriend(oTarget, oSource=0)` - Routine 236

* Returns TRUE if oSource considers oTarget as a friend.

**Parameters:**

- `oTarget`: `object`
- `oSource`: `object` (default: `0`)

**Returns:** `int`

<a id="getisneutral"></a>

#### `GetIsNeutral(oTarget, oSource=0)` - Routine 237

* Returns TRUE if oSource considers oTarget as neutral.

**Parameters:**

- `oTarget`: `object`
- `oSource`: `object` (default: `0`)

**Returns:** `int`

<a id="versusalignmenteffect"></a>

#### `VersusAlignmentEffect(eEffect, nLawChaos=0, nGoodEvil=0)` - Routine 355

Set eEffect to be versus a specific alignment.
- eEffect
- nLawChaos: ALIGNMENT_LAWFUL/ALIGNMENT_CHAOTIC/ALIGNMENT_ALL
- nGoodEvil: ALIGNMENT_GOOD/ALIGNMENT_EVIL/ALIGNMENT_ALL

**Parameters:**

- `eEffect`: `effect`
- `nLawChaos`: `int` (default: `0`)
- `nGoodEvil`: `int` (default: `0`)

**Returns:** `effect`

<a id="setgoodevilvalue"></a>

#### `SetGoodEvilValue(oCreature, nAlignment)` - Routine 750

SetAlignmentGoodEvil
Set oCreature's alignment value

**Parameters:**

- `oCreature`: `object`
- `nAlignment`: `int`
### Class System

<a id="gethasspelleffect"></a>

#### `GetHasSpellEffect(nSpell, oObject=0)` - Routine 304

Determine if oObject has effects originating from nSpell.
- nSpell: SPELL_*
- oObject

**Parameters:**

- `nSpell`: `int`
- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getclassbyposition"></a>

#### `GetClassByPosition(nClassPosition, oCreature=0)` - Routine 341

A creature can have up to three classes.  This function determines the
creature's class (CLASS_TYPE_*) based on nClassPosition.
- nClassPosition: 1, 2 or 3
- oCreature
* Returns CLASS_TYPE_INVALID if the oCreature does not have a class in
nClassPosition (i.e. a single-class creature will only have a value in
nClassLocation=1) or if oCreature is not a valid creature.

**Parameters:**

- `nClassPosition`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getlevelbyposition"></a>

#### `GetLevelByPosition(nClassPosition, oCreature=0)` - Routine 342

A creature can have up to three classes.  This function determines the
creature's class level based on nClass Position.
- nClassPosition: 1, 2 or 3
- oCreature
* Returns 0 if oCreature does not have a class in nClassPosition
(i.e. a single-class creature will only have a value in nClassLocation=1)
or if oCreature is not a valid creature.

**Parameters:**

- `nClassPosition`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getlevelbyclass"></a>

#### `GetLevelByClass(nClassType, oCreature=0)` - Routine 343

Determine the levels that oCreature holds in nClassType.
- nClassType: CLASS_TYPE_*
- oCreature

**Parameters:**

- `nClassType`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="gethasspell"></a>

#### `GetHasSpell(nSpell, oCreature=0)` - Routine 377

Determine whether oCreature has nSpell memorised.
- nSpell: SPELL_*
- oCreature

**Parameters:**

- `nSpell`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getspellcastitem"></a>

#### `GetSpellCastItem()` - Routine 438

Use this in a spell script to get the item used to cast the spell.

**Returns:** `object`
### Combat Functions

<a id="getlastattacker"></a>

#### `GetLastAttacker(oAttackee=0)` - Routine 36

Get the last attacker of oAttackee.  This should only be used ONLY in the
OnAttacked events for creatures, placeables and doors.
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oAttackee`: `object` (default: `0`)

**Returns:** `object`

<a id="actionattack"></a>

#### `ActionAttack(oAttackee, bPassive=0)` - Routine 37

Attack oAttackee.
- bPassive: If this is TRUE, attack is in passive mode.

**Parameters:**

- `oAttackee`: `object`
- `bPassive`: `int` (default: `0`)

<a id="getspelltargetobject"></a>

#### `GetSpellTargetObject()` - Routine 47

Get the object at which the caller last cast a spell
* Return value on error: OBJECT_INVALID

**Returns:** `object`

<a id="actioncastspellatobject"></a>

#### `ActionCastSpellAtObject(nSpell, oTarget, nMetaMagic=0, bCheat=0, nDomainLevel=0, nProjectilePathType=0, bInstantSpell=0)` - Routine 48

This action casts a spell at oTarget.
- nSpell: SPELL_*
- oTarget: Target for the spell
- nMetamagic: METAMAGIC_*
- bCheat: If this is TRUE, then the executor of the action doesn't have to be
able to cast the spell.
- nDomainLevel: TBD - SS
- nProjectilePathType: PROJECTILE_PATH_TYPE_*
- bInstantSpell: If this is TRUE, the spell is cast immediately. This allows
the end-user to simulate a high-level magic-user having lots of advance
warning of impending trouble

**Parameters:**

- `nSpell`: `int`
- `oTarget`: `object`
- `nMetaMagic`: `int` (default: `0`)
- `bCheat`: `int` (default: `0`)
- `nDomainLevel`: `int` (default: `0`)
- `nProjectilePathType`: `int` (default: `0`)
- `bInstantSpell`: `int` (default: `0`)

<a id="getspelltargetlocation"></a>

#### `GetSpellTargetLocation()` - Routine 222

Get the location of the caller's last spell target.

**Returns:** `location`

<a id="actioncastspellatlocation"></a>

#### `ActionCastSpellAtLocation(nSpell, lTargetLocation, nMetaMagic=0, bCheat=0, nProjectilePathType=0, bInstantSpell=0)` - Routine 234

Cast spell nSpell at lTargetLocation.
- nSpell: SPELL_*
- lTargetLocation
- nMetaMagic: METAMAGIC_*
- bCheat: If this is TRUE, then the executor of the action doesn't have to be
able to cast the spell.
- nProjectilePathType: PROJECTILE_PATH_TYPE_*
- bInstantSpell: If this is TRUE, the spell is cast immediately; this allows
the end-user to simulate
a high-level magic user having lots of advance warning of impending trouble.

**Parameters:**

- `nSpell`: `int`
- `lTargetLocation`: `location`
- `nMetaMagic`: `int` (default: `0`)
- `bCheat`: `int` (default: `0`)
- `nProjectilePathType`: `int` (default: `0`)
- `bInstantSpell`: `int` (default: `0`)

<a id="getspellid"></a>

#### `GetSpellId()` - Routine 248

This is for use in a Spell script, it gets the ID of the spell that is being
cast (SPELL_*).

**Returns:** `int`

<a id="getattacktarget"></a>

#### `GetAttackTarget(oCreature=0)` - Routine 316

Get the attack target of oCreature.
This only works when oCreature is in combat.

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `object`

<a id="getisincombat"></a>

#### `GetIsInCombat(oCreature=0)` - Routine 320

* Returns TRUE if oCreature is in combat.

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="setisdestroyable"></a>

#### `SetIsDestroyable(bDestroyable, bRaiseable=1, bSelectableWhenDead=0)` - Routine 323

Set the destroyable status of the caller.
- bDestroyable: If this is FALSE, the caller does not fade out on death, but
sticks around as a corpse.
- bRaiseable: If this is TRUE, the caller can be raised via resurrection.
- bSelectableWhenDead: If this is TRUE, the caller is selectable after death.

**Parameters:**

- `bDestroyable`: `int`
- `bRaiseable`: `int` (default: `1`)
- `bSelectableWhenDead`: `int` (default: `0`)

<a id="getdamagedealtbytype"></a>

#### `GetDamageDealtByType(nDamageType)` - Routine 344

Get the amount of damage of type nDamageType that has been dealt to the caller.
- nDamageType: DAMAGE_TYPE_*

**Parameters:**

- `nDamageType`: `int`

**Returns:** `int`

<a id="gettotaldamagedealt"></a>

#### `GetTotalDamageDealt()` - Routine 345

Get the total amount of damage that has been dealt to the caller.

**Returns:** `int`

<a id="getlastdamager"></a>

#### `GetLastDamager()` - Routine 346

Get the last object that damaged the caller.
* Returns OBJECT_INVALID if the caller is not a valid object.

**Returns:** `object`

<a id="actionforcemovetolocation"></a>

#### `ActionForceMoveToLocation(lDestination, bRun=0, fTimeout=30.0)` - Routine 382

Force the action subject to move to lDestination.

**Parameters:**

- `lDestination`: `location`
- `bRun`: `int` (default: `0`)
- `fTimeout`: `float` (default: `30.0`)

<a id="actionforcemovetoobject"></a>

#### `ActionForceMoveToObject(oMoveTo, bRun=0, fRange=1.0, fTimeout=30.0)` - Routine 383

Force the action subject to move to oMoveTo.

**Parameters:**

- `oMoveTo`: `object`
- `bRun`: `int` (default: `0`)
- `fRange`: `float` (default: `1.0`)
- `fTimeout`: `float` (default: `30.0`)

<a id="getisweaponeffective"></a>

#### `GetIsWeaponEffective(oVersus=1, bOffHand=0)` - Routine 422

* Returns TRUE if the weapon equipped is capable of damaging oVersus.

**Parameters:**

- `oVersus`: `object` (default: `1`)
- `bOffHand`: `int` (default: `0`)

**Returns:** `int`

<a id="getlastkiller"></a>

#### `GetLastKiller()` - Routine 437

Get the object that killed the caller.

**Returns:** `object`

<a id="getweaponranged"></a>

#### `GetWeaponRanged(oItem)` - Routine 511

* Returns TRUE if oItem is a ranged weapon.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="getlasthostileactor"></a>

#### `GetLastHostileActor(oVictim=0)` - Routine 556

Get the last object that was sent as a GetLastAttacker(), GetLastDamager(),
GetLastSpellCaster() (for a hostile spell), or GetLastDisturbed() (when a
creature is pickpocketed).
Note: Return values may only ever be:
1) A Creature
2) Plot Characters will never have this value set
3) Area of Effect Objects will return the AOE creator if they are registered
as this value, otherwise they will return INVALID_OBJECT_ID
4) Traps will not return the creature that set the trap.
5) This value will never be overwritten by another non-creature object.
6) This value will never be a dead/destroyed creature

**Parameters:**

- `oVictim`: `object` (default: `0`)

**Returns:** `object`
### Dialog and Conversation Functions

<a id="actionpauseconversation"></a>

#### `ActionPauseConversation()` - Routine 205

Pause the current conversation.

<a id="actionresumeconversation"></a>

#### `ActionResumeConversation()` - Routine 206

Resume a conversation after it has been paused.

<a id="speakstring"></a>

#### `SpeakString(sStringToSpeak, nTalkVolume=0)` - Routine 221

The caller will immediately speak sStringToSpeak (this is different from
ActionSpeakString)
- sStringToSpeak
- nTalkVolume: TALKVOLUME_*

**Parameters:**

- `sStringToSpeak`: `string`
- `nTalkVolume`: `int` (default: `0`)

<a id="beginconversation"></a>

#### `BeginConversation(sResRef=, oObjectToDialog=1)` - Routine 255

Use this in an OnDialog script to start up the dialog tree.
- sResRef: if this is not specified, the default dialog file will be used
- oObjectToDialog: if this is not specified the person that triggered the
event will be used

**Parameters:**

- `sResRef`: `string` (default: ``)
- `oObjectToDialog`: `object` (default: `1`)

**Returns:** `int`

<a id="setcustomtoken"></a>

#### `SetCustomToken(nCustomTokenNumber, sTokenValue)` - Routine 284

Set the value for a custom token.

**Parameters:**

- `nCustomTokenNumber`: `int`
- `sTokenValue`: `string`

<a id="eventconversation"></a>

#### `EventConversation()` - Routine 295

Conversation event.

**Returns:** `event`

<a id="speakonelinerconversation"></a>

#### `SpeakOneLinerConversation(sDialogResRef=, oTokenTarget=32767)` - Routine 417

Immediately speak a conversation one-liner.
- sDialogResRef
- oTokenTarget: This must be specified if there are creature-specific tokens
in the string.

**Parameters:**

- `sDialogResRef`: `string` (default: ``)
- `oTokenTarget`: `object` (default: `32767`)

<a id="getisinconversation"></a>

#### `GetIsInConversation(oObject)` - Routine 445

Determine whether oObject is in conversation.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getlastconversation"></a>

#### `GetLastConversation()` - Routine 711

GetLastConversation
Gets the last conversation string.

**Returns:** `string`

<a id="actionstartconversation"></a>

#### `ActionStartConversation(oObjectToConverse, sDialogResRef=, bPrivateConversation=0, nConversationType=0, bIgnoreStartRange=0, sNameObjectToIgnore1=, sNameObjectToIgnore2=, sNameObjectToIgnore3=, sNameObjectToIgnore4=, sNameObjectToIgnore5=, sNameObjectToIgnore6=, bUseLeader=0)`

AMF: APRIL 28, 2003 - I HAVE CHANGED THIS FUNCTION AS PER DAN'S REQUEST
Starts a conversation with oObjectToConverseWith - this will cause their
OnDialog event to fire.
- oObjectToConverseWith
- sDialogResRef: If this is blank, the creature's own dialogue file will be used
- bPrivateConversation: If this is blank, the default is FALSE.
- nConversationType - If this is blank the default will be Cinematic, ie. a normal conversation type
other choices inclue: CONVERSATION_TYPE_COMPUTER
UPDATE:  nConversationType actually has no meaning anymore.  This has been replaced by a flag in the dialog editor.  However
for backwards compatability it has been left here.  So when using this command place CONVERSATION_TYPE_CINEMATIC in here. - DJF
- bIgnoreStartRange - If this is blank the default will be FALSE, ie. Start conversation ranges are in effect
Setting this to TRUE will cause creatures to start a conversation without requiring to close
the distance between the two object in dialog.
- sNameObjectToIgnore1-6 - Normally objects in the animation list of the dialog editor have to be available for animations on that node to work
these 6 strings are to indicate 6 objects that dont need to be available for things to proceed.  The string should be EXACTLY
the same as the string that it represents in the dialog editor.

**Parameters:**

- `oObjectToConverse`: `object`
- `sDialogResRef`: `string` (default: ``)
- `bPrivateConversation`: `int` (default: `0`)
- `nConversationType`: `int` (default: `0`)
- `bIgnoreStartRange`: `int` (default: `0`)
- `sNameObjectToIgnore1`: `string` (default: ``)
- `sNameObjectToIgnore2`: `string` (default: ``)
- `sNameObjectToIgnore3`: `string` (default: ``)
- `sNameObjectToIgnore4`: `string` (default: ``)
- `sNameObjectToIgnore5`: `string` (default: ``)
- `sNameObjectToIgnore6`: `string` (default: ``)
- `bUseLeader`: `int` (default: `0`)

<a id="getisconversationactive"></a>

#### `GetIsConversationActive()`

701. GetIsConversationActive
Checks to see if any conversations are currently taking place

**Returns:** `int`
### Effects System

<a id="effectassuredhit"></a>

#### `EffectAssuredHit()` - Routine 51

EffectAssuredHit
Create an Assured Hit effect, which guarantees that all attacks are successful

**Returns:** `effect`

<a id="effectheal"></a>

#### `EffectHeal(nDamageToHeal)` - Routine 78

Create a Heal effect. This should be applied as an instantaneous effect.
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nDamageToHeal < 0.

**Parameters:**

- `nDamageToHeal`: `int`

**Returns:** `effect`

<a id="effectdamage"></a>

#### `EffectDamage(nDamageAmount, nDamageType=8, nDamagePower=0)` - Routine 79

Create a Damage effect
- nDamageAmount: amount of damage to be dealt. This should be applied as an
instantaneous effect.
- nDamageType: DAMAGE_TYPE_*
- nDamagePower: DAMAGE_POWER_*

**Parameters:**

- `nDamageAmount`: `int`
- `nDamageType`: `int` (default: `8`)
- `nDamagePower`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectabilityincrease"></a>

#### `EffectAbilityIncrease(nAbilityToIncrease, nModifyBy)` - Routine 80

Create an Ability Increase effect
- bAbilityToIncrease: ABILITY_*

**Parameters:**

- `nAbilityToIncrease`: `int`
- `nModifyBy`: `int`

**Returns:** `effect`

<a id="effectdamageresistance"></a>

#### `EffectDamageResistance(nDamageType, nAmount, nLimit=0)` - Routine 81

Create a Damage Resistance effect that removes the first nAmount points of
damage of type nDamageType, up to nLimit (or infinite if nLimit is 0)
- nDamageType: DAMAGE_TYPE_*
- nAmount
- nLimit

**Parameters:**

- `nDamageType`: `int`
- `nAmount`: `int`
- `nLimit`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectresurrection"></a>

#### `EffectResurrection()` - Routine 82

Create a Resurrection effect. This should be applied as an instantaneous effect.

**Returns:** `effect`

<a id="effectacincrease"></a>

#### `EffectACIncrease(nValue, nModifyType=0, nDamageType=8199)` - Routine 115

Create an AC Increase effect
- nValue: size of AC increase
- nModifyType: AC_*_BONUS
- nDamageType: DAMAGE_TYPE_*
* Default value for nDamageType should only ever be used in this function prototype.

**Parameters:**

- `nValue`: `int`
- `nModifyType`: `int` (default: `0`)
- `nDamageType`: `int` (default: `8199`)

**Returns:** `effect`

<a id="effectsavingthrowincrease"></a>

#### `EffectSavingThrowIncrease(nSave, nValue, nSaveType=0)` - Routine 117

Create an AC Decrease effect
- nSave: SAVING_THROW_* (not SAVING_THROW_TYPE_*)
- nValue: size of AC decrease
- nSaveType: SAVING_THROW_TYPE_*

**Parameters:**

- `nSave`: `int`
- `nValue`: `int`
- `nSaveType`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectattackincrease"></a>

#### `EffectAttackIncrease(nBonus, nModifierType=0)` - Routine 118

Create an Attack Increase effect
- nBonus: size of attack bonus
- nModifierType: ATTACK_BONUS_*

**Parameters:**

- `nBonus`: `int`
- `nModifierType`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectdamagereduction"></a>

#### `EffectDamageReduction(nAmount, nDamagePower, nLimit=0)` - Routine 119

Create a Damage Reduction effect
- nAmount: amount of damage reduction
- nDamagePower: DAMAGE_POWER_*
- nLimit: How much damage the effect can absorb before disappearing.
Set to zero for infinite

**Parameters:**

- `nAmount`: `int`
- `nDamagePower`: `int`
- `nLimit`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectdamageincrease"></a>

#### `EffectDamageIncrease(nBonus, nDamageType=8)` - Routine 120

Create a Damage Increase effect
- nBonus: DAMAGE_BONUS_*
- nDamageType: DAMAGE_TYPE_*

**Parameters:**

- `nBonus`: `int`
- `nDamageType`: `int` (default: `8`)

**Returns:** `effect`

<a id="effectentangle"></a>

#### `EffectEntangle()` - Routine 130

Create an Entangle effect
When applied, this effect will restrict the creature's movement and apply a
(-2) to all attacks and a -4 to AC.

**Returns:** `effect`

<a id="effectdeath"></a>

#### `EffectDeath(nSpectacularDeath=0, nDisplayFeedback=1)` - Routine 133

Create a Death effect
- nSpectacularDeath: if this is TRUE, the creature to which this effect is
applied will die in an extraordinary fashion
- nDisplayFeedback

**Parameters:**

- `nSpectacularDeath`: `int` (default: `0`)
- `nDisplayFeedback`: `int` (default: `1`)

**Returns:** `effect`

<a id="effectknockdown"></a>

#### `EffectKnockdown()` - Routine 134

Create a Knockdown effect
This effect knocks creatures off their feet, they will sit until the effect
is removed. This should be applied as a temporary effect with a 3 second
duration minimum (1 second to fall, 1 second sitting, 1 second to get up).

**Returns:** `effect`

<a id="effectparalyze"></a>

#### `EffectParalyze()` - Routine 148

Create a Paralyze effect

**Returns:** `effect`

<a id="effectspellimmunity"></a>

#### `EffectSpellImmunity(nImmunityToSpell=-1)` - Routine 149

Create a Spell Immunity effect.
There is a known bug with this function. There *must* be a parameter specified
when this is called (even if the desired parameter is SPELL_ALL_SPELLS),
otherwise an effect of type EFFECT_TYPE_INVALIDEFFECT will be returned.
- nImmunityToSpell: SPELL_*
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nImmunityToSpell is
invalid.

**Parameters:**

- `nImmunityToSpell`: `int` (default: `-1`)

**Returns:** `effect`

<a id="effectforcejump"></a>

#### `EffectForceJump(oTarget, nAdvanced=0)` - Routine 153

EffectForceJump
The effect required for force jumping

**Parameters:**

- `oTarget`: `object`
- `nAdvanced`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectsleep"></a>

#### `EffectSleep()` - Routine 154

Create a Sleep effect

**Returns:** `effect`

<a id="effecttemporaryforcepoints"></a>

#### `EffectTemporaryForcePoints(nTempForce)` - Routine 156

This was previously EffectCharmed();

**Parameters:**

- `nTempForce`: `int`

**Returns:** `effect`

<a id="effectconfused"></a>

#### `EffectConfused()` - Routine 157

Create a Confuse effect

**Returns:** `effect`

<a id="effectfrightened"></a>

#### `EffectFrightened()` - Routine 158

Create a Frighten effect

**Returns:** `effect`

<a id="effectchoke"></a>

#### `EffectChoke()` - Routine 159

Choke the bugger...

**Returns:** `effect`

<a id="effectstunned"></a>

#### `EffectStunned()` - Routine 161

Create a Stun effect

**Returns:** `effect`

<a id="effectregenerate"></a>

#### `EffectRegenerate(nAmount, fIntervalSeconds)` - Routine 164

Create a Regenerate effect.
- nAmount: amount of damage to be regenerated per time interval
- fIntervalSeconds: length of interval in seconds

**Parameters:**

- `nAmount`: `int`
- `fIntervalSeconds`: `float`

**Returns:** `effect`

<a id="effectmovementspeedincrease"></a>

#### `EffectMovementSpeedIncrease(nNewSpeedPercent)` - Routine 165

Create a Movement Speed Increase effect.
- nNewSpeedPercent: This works in a dodgy way so please read this notes carefully.
If you supply an integer under 100, 100 gets added to it to produce the final speed.
e.g. if you supply 50, then the resulting speed is 150% of the original speed.
If you supply 100 or above, then this is used directly as the resulting speed.
e.g. if you specify 100, then the resulting speed is 100% of the original speed that is,
it is unchanged.
However if you specify 200, then the resulting speed is double the original speed.

**Parameters:**

- `nNewSpeedPercent`: `int`

**Returns:** `effect`

<a id="effectareaofeffect"></a>

#### `EffectAreaOfEffect(nAreaEffectId, sOnEnterScript=, sHeartbeatScript=, sOnExitScript=)` - Routine 171

Create an Area Of Effect effect in the area of the creature it is applied to.
If the scripts are not specified, default ones will be used.

**Parameters:**

- `nAreaEffectId`: `int`
- `sOnEnterScript`: `string` (default: ``)
- `sHeartbeatScript`: `string` (default: ``)
- `sOnExitScript`: `string` (default: ``)

**Returns:** `effect`

<a id="effectvisualeffect"></a>

#### `EffectVisualEffect(nVisualEffectId, nMissEffect=0)` - Routine 180

* Create a Visual Effect that can be applied to an object.
- nVisualEffectId
- nMissEffect: if this is TRUE, a random vector near or past the target will
be generated, on which to play the effect

**Parameters:**

- `nVisualEffectId`: `int`
- `nMissEffect`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectlinkeffects"></a>

#### `EffectLinkEffects(eChildEffect, eParentEffect)` - Routine 199

Link the two supplied effects, returning eChildEffect as a child of
eParentEffect.
Note: When applying linked effects if the target is immune to all valid
effects all other effects will be removed as well. This means that if you
apply a visual effect and a silence effect (in a link) and the target is
immune to the silence effect that the visual effect will get removed as well.
Visual Effects are not considered "valid" effects for the purposes of
determining if an effect will be removed or not and as such should never be
packaged *only* with other visual effects in a link.

**Parameters:**

- `eChildEffect`: `effect`
- `eParentEffect`: `effect`

**Returns:** `effect`

<a id="effectbeam"></a>

#### `EffectBeam(nBeamVisualEffect, oEffector, nBodyPart, bMissEffect=0)` - Routine 207

Create a Beam effect.
- nBeamVisualEffect: VFX_BEAM_*
- oEffector: the beam is emitted from this creature
- nBodyPart: BODY_NODE_*
- bMissEffect: If this is TRUE, the beam will fire to a random vector near or
past the target
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nBeamVisualEffect is
not valid.

**Parameters:**

- `nBeamVisualEffect`: `int`
- `oEffector`: `object`
- `nBodyPart`: `int`
- `bMissEffect`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectforceresistanceincrease"></a>

#### `EffectForceResistanceIncrease(nValue)` - Routine 212

Create a Force Resistance Increase effect.
- nValue: size of Force Resistance increase

**Parameters:**

- `nValue`: `int`

**Returns:** `effect`

<a id="effectbodyfuel"></a>

#### `EffectBodyFuel()` - Routine 224

the effect of body fule.. convers HP -> FP i think

**Returns:** `effect`

<a id="effectpoison"></a>

#### `EffectPoison(nPoisonType)` - Routine 250

Create a Poison effect.
- nPoisonType: POISON_*

**Parameters:**

- `nPoisonType`: `int`

**Returns:** `effect`

<a id="effectassureddeflection"></a>

#### `EffectAssuredDeflection(nReturn=0)` - Routine 252

Assured Deflection
This effect ensures that all projectiles shot at a jedi will be deflected
without doing an opposed roll.  It takes an optional parameter to say whether
the deflected projectile will return to the attacker and cause damage

**Parameters:**

- `nReturn`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectforcepushtargeted"></a>

#### `EffectForcePushTargeted(lCentre, nIgnoreTestDirectLine=0)` - Routine 269

EffectForcePushTargeted
This effect is exactly the same as force push, except it takes a location parameter that specifies
where the location of the force push is to be done from.  All orientations are also based on this location.
AMF:  The new ignore test direct line variable should be used with extreme caution
It overrides geometry checks for force pushes, so that the object that the effect is applied to
is guaranteed to move that far, ignoring collisions.  It is best used for cutscenes.

**Parameters:**

- `lCentre`: `location`
- `nIgnoreTestDirectLine`: `int` (default: `0`)

**Returns:** `effect`

<a id="effecthaste"></a>

#### `EffectHaste()` - Routine 270

Create a Haste effect.

**Returns:** `effect`

<a id="effectimmunity"></a>

#### `EffectImmunity(nImmunityType)` - Routine 273

Create an Immunity effect.
- nImmunityType: IMMUNITY_TYPE_*

**Parameters:**

- `nImmunityType`: `int`

**Returns:** `effect`

<a id="effectdamageimmunityincrease"></a>

#### `EffectDamageImmunityIncrease(nDamageType, nPercentImmunity)` - Routine 275

Creates a Damage Immunity Increase effect.
- nDamageType: DAMAGE_TYPE_*
- nPercentImmunity

**Parameters:**

- `nDamageType`: `int`
- `nPercentImmunity`: `int`

**Returns:** `effect`

<a id="effecttemporaryhitpoints"></a>

#### `EffectTemporaryHitpoints(nHitPoints)` - Routine 314

Create a Temporary Hitpoints effect.
- nHitPoints: a positive integer
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nHitPoints < 0.

**Parameters:**

- `nHitPoints`: `int`

**Returns:** `effect`

<a id="effectskillincrease"></a>

#### `EffectSkillIncrease(nSkill, nValue)` - Routine 351

Create a Skill Increase effect.
- nSkill: SKILL_*
- nValue
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nSkill is invalid.

**Parameters:**

- `nSkill`: `int`
- `nValue`: `int`

**Returns:** `effect`

<a id="effectdamageforcepoints"></a>

#### `EffectDamageForcePoints(nDamage)` - Routine 372

Damages the creatures force points

**Parameters:**

- `nDamage`: `int`

**Returns:** `effect`

<a id="effecthealforcepoints"></a>

#### `EffectHealForcePoints(nHeal)` - Routine 373

Heals the creatures force points

**Parameters:**

- `nHeal`: `int`

**Returns:** `effect`

<a id="effecthitpointchangewhendying"></a>

#### `EffectHitPointChangeWhenDying(fHitPointChangePerRound)` - Routine 387

Create a Hit Point Change When Dying effect.
- fHitPointChangePerRound: this can be positive or negative, but not zero.
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if fHitPointChangePerRound is 0.

**Parameters:**

- `fHitPointChangePerRound`: `float`

**Returns:** `effect`

<a id="effectdroidstun"></a>

#### `EffectDroidStun()` - Routine 391

Stunn the droid

**Returns:** `effect`

<a id="effectforcepushed"></a>

#### `EffectForcePushed()` - Routine 392

Force push the creature...

**Returns:** `effect`

<a id="effectforceresisted"></a>

#### `EffectForceResisted(oSource)` - Routine 402

Effect that will play an animation and display a visual effect to indicate the
target has resisted a force power.

**Parameters:**

- `oSource`: `object`

**Returns:** `effect`

<a id="effectforcefizzle"></a>

#### `EffectForceFizzle()` - Routine 420

Effect that will display a visual effect on the specified object's hand to
indicate a force power has fizzled out.

**Returns:** `effect`

<a id="effectabilitydecrease"></a>

#### `EffectAbilityDecrease(nAbility, nModifyBy)` - Routine 446

Create an Ability Decrease effect.
- nAbility: ABILITY_*
- nModifyBy: This is the amount by which to decrement the ability

**Parameters:**

- `nAbility`: `int`
- `nModifyBy`: `int`

**Returns:** `effect`

<a id="effectattackdecrease"></a>

#### `EffectAttackDecrease(nPenalty, nModifierType=0)` - Routine 447

Create an Attack Decrease effect.
- nPenalty
- nModifierType: ATTACK_BONUS_*

**Parameters:**

- `nPenalty`: `int`
- `nModifierType`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectdamagedecrease"></a>

#### `EffectDamageDecrease(nPenalty, nDamageType=8)` - Routine 448

Create a Damage Decrease effect.
- nPenalty
- nDamageType: DAMAGE_TYPE_*

**Parameters:**

- `nPenalty`: `int`
- `nDamageType`: `int` (default: `8`)

**Returns:** `effect`

<a id="effectdamageimmunitydecrease"></a>

#### `EffectDamageImmunityDecrease(nDamageType, nPercentImmunity)` - Routine 449

Create a Damage Immunity Decrease effect.
- nDamageType: DAMAGE_TYPE_*
- nPercentImmunity

**Parameters:**

- `nDamageType`: `int`
- `nPercentImmunity`: `int`

**Returns:** `effect`

<a id="effectacdecrease"></a>

#### `EffectACDecrease(nValue, nModifyType=0, nDamageType=8199)` - Routine 450

Create an AC Decrease effect.
- nValue
- nModifyType: AC_*
- nDamageType: DAMAGE_TYPE_*
* Default value for nDamageType should only ever be used in this function prototype.

**Parameters:**

- `nValue`: `int`
- `nModifyType`: `int` (default: `0`)
- `nDamageType`: `int` (default: `8199`)

**Returns:** `effect`

<a id="effectmovementspeeddecrease"></a>

#### `EffectMovementSpeedDecrease(nPercentChange)` - Routine 451

Create a Movement Speed Decrease effect.
- nPercentChange: This is expected to be a positive integer between 1 and 99 inclusive.
If a negative integer is supplied then a movement speed increase will result,
and if a number >= 100 is supplied then the effect is deleted.

**Parameters:**

- `nPercentChange`: `int`

**Returns:** `effect`

<a id="effectsavingthrowdecrease"></a>

#### `EffectSavingThrowDecrease(nSave, nValue, nSaveType=0)` - Routine 452

Create a Saving Throw Decrease effect.
- nSave
- nValue
- nSaveType: SAVING_THROW_TYPE_*

**Parameters:**

- `nSave`: `int`
- `nValue`: `int`
- `nSaveType`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectskilldecrease"></a>

#### `EffectSkillDecrease(nSkill, nValue)` - Routine 453

Create a Skill Decrease effect.
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nSkill is invalid.

**Parameters:**

- `nSkill`: `int`
- `nValue`: `int`

**Returns:** `effect`

<a id="effectforceresistancedecrease"></a>

#### `EffectForceResistanceDecrease(nValue)` - Routine 454

Create a Force Resistance Decrease effect.

**Parameters:**

- `nValue`: `int`

**Returns:** `effect`

<a id="effectinvisibility"></a>

#### `EffectInvisibility(nInvisibilityType)` - Routine 457

Create an Invisibility effect.
- nInvisibilityType: INVISIBILITY_TYPE_*
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nInvisibilityType
is invalid.

**Parameters:**

- `nInvisibilityType`: `int`

**Returns:** `effect`

<a id="effectconcealment"></a>

#### `EffectConcealment(nPercentage)` - Routine 458

Create a Concealment effect.
- nPercentage: 1-100 inclusive
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nPercentage < 1 or
nPercentage > 100.

**Parameters:**

- `nPercentage`: `int`

**Returns:** `effect`

<a id="effectforceshield"></a>

#### `EffectForceShield(nShield)` - Routine 459

Create a Force Shield that has parameters from the guven index into the forceshields.2da

**Parameters:**

- `nShield`: `int`

**Returns:** `effect`

<a id="effectdispelmagicall"></a>

#### `EffectDispelMagicAll(nCasterLevel)` - Routine 460

Create a Dispel Magic All effect.

**Parameters:**

- `nCasterLevel`: `int`

**Returns:** `effect`

<a id="effectdisguise"></a>

#### `EffectDisguise(nDisguiseAppearance)` - Routine 463

Create a Disguise effect.
- * nDisguiseAppearance: DISGUISE_TYPE_*s

**Parameters:**

- `nDisguiseAppearance`: `int`

**Returns:** `effect`

<a id="effecttrueseeing"></a>

#### `EffectTrueSeeing()` - Routine 465

Create a True Seeing effect.

**Returns:** `effect`

<a id="effectseeinvisible"></a>

#### `EffectSeeInvisible()` - Routine 466

Create a See Invisible effect.

**Returns:** `effect`

<a id="effecttimestop"></a>

#### `EffectTimeStop()` - Routine 467

Create a Time Stop effect.

**Returns:** `effect`

<a id="effectblasterdeflectionincrease"></a>

#### `EffectBlasterDeflectionIncrease(nChange)` - Routine 469

Increase the blaster deflection rate, i think...

**Parameters:**

- `nChange`: `int`

**Returns:** `effect`

<a id="effectblasterdeflectiondecrease"></a>

#### `EffectBlasterDeflectionDecrease(nChange)` - Routine 470

decrease the blaster deflection rate

**Parameters:**

- `nChange`: `int`

**Returns:** `effect`

<a id="effecthorrified"></a>

#### `EffectHorrified()` - Routine 471

Make the creature horified. BOO!

**Returns:** `effect`

<a id="effectspelllevelabsorption"></a>

#### `EffectSpellLevelAbsorption(nMaxSpellLevelAbsorbed, nTotalSpellLevelsAbsorbed=0, nSpellSchool=0)` - Routine 472

Create a Spell Level Absorption effect.
- nMaxSpellLevelAbsorbed: maximum spell level that will be absorbed by the
effect
- nTotalSpellLevelsAbsorbed: maximum number of spell levels that will be
absorbed by the effect
- nSpellSchool: SPELL_SCHOOL_*
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if:
nMaxSpellLevelAbsorbed is not between -1 and 9 inclusive, or nSpellSchool
is invalid.

**Parameters:**

- `nMaxSpellLevelAbsorbed`: `int`
- `nTotalSpellLevelsAbsorbed`: `int` (default: `0`)
- `nSpellSchool`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectdispelmagicbest"></a>

#### `EffectDispelMagicBest(nCasterLevel)` - Routine 473

Create a Dispel Magic Best effect.

**Parameters:**

- `nCasterLevel`: `int`

**Returns:** `effect`

<a id="effectmisschance"></a>

#### `EffectMissChance(nPercentage)` - Routine 477

Create a Miss Chance effect.
- nPercentage: 1-100 inclusive
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nPercentage < 1 or
nPercentage > 100.

**Parameters:**

- `nPercentage`: `int`

**Returns:** `effect`

<a id="effectmodifyattacks"></a>

#### `EffectModifyAttacks(nAttacks)` - Routine 485

Create a Modify Attacks effect to add attacks.
- nAttacks: maximum is 5, even with the effect stacked
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nAttacks > 5.

**Parameters:**

- `nAttacks`: `int`

**Returns:** `effect`

<a id="effectdamageshield"></a>

#### `EffectDamageShield(nDamageAmount, nRandomAmount, nDamageType)` - Routine 487

Create a Damage Shield effect which does (nDamageAmount + nRandomAmount)
damage to any melee attacker on a successful attack of damage type nDamageType.
- nDamageAmount: an integer value
- nRandomAmount: DAMAGE_BONUS_*
- nDamageType: DAMAGE_TYPE_*

**Parameters:**

- `nDamageAmount`: `int`
- `nRandomAmount`: `int`
- `nDamageType`: `int`

**Returns:** `effect`

<a id="effectforcedrain"></a>

#### `EffectForceDrain(nDamage)` - Routine 675

EffectForceDrain
This command will reduce the force points of a creature.

**Parameters:**

- `nDamage`: `int`

**Returns:** `effect`

<a id="effectpsychicstatic"></a>

#### `EffectPsychicStatic()` - Routine 676

EffectTemporaryForcePoints

**Returns:** `effect`

<a id="effectcutscenehorrified"></a>

#### `EffectCutSceneHorrified()` - Routine 754

EffectCutSceneHorrified
Get a horrified effect for cutscene purposes (ie. this effect will ignore immunities).

**Returns:** `effect`

<a id="effectcutsceneparalyze"></a>

#### `EffectCutSceneParalyze()` - Routine 755

EffectCutSceneParalyze
Get a paralyze effect for cutscene purposes (ie. this effect will ignore immunities).

**Returns:** `effect`

<a id="effectcutscenestunned"></a>

#### `EffectCutSceneStunned()` - Routine 756

EffectCutSceneStunned
Get a stun effect for cutscene purposes (ie. this effect will ignore immunities).

**Returns:** `effect`

<a id="effectlightsaberthrow"></a>

#### `EffectLightsaberThrow(oTarget1, oTarget2=1, oTarget3=1, nAdvancedDamage=0)`

702. EffectLightsaberThrow
This function throws a lightsaber at a target
If multiple targets are specified, then the lightsaber travels to them
sequentially, returning to the first object specified
This effect is applied to an object, so an effector is not needed

**Parameters:**

- `oTarget1`: `object`
- `oTarget2`: `object` (default: `1`)
- `oTarget3`: `object` (default: `1`)
- `nAdvancedDamage`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectwhirlwind"></a>

#### `EffectWhirlWind()`

703.
creates the effect of a whirl wind.

**Returns:** `effect`
### Global Variables

<a id="setglobalstring"></a>

#### `SetGlobalString(sIdentifier, sValue)` - Routine 160

Sets a global string with the specified identifier.  This is an EXTREMELY
restricted function - do not use without expilicit permission.
This means if you are not Preston.  Then go see him if you're even thinking
about using this.

**Parameters:**

- `sIdentifier`: `string`
- `sValue`: `string`

<a id="getglobalstring"></a>

#### `GetGlobalString(sIdentifier)` - Routine 194

Get a global string with the specified identifier
This is an EXTREMELY restricted function.  Use only with explicit permission.
This means if you are not Preston.  Then go see him if you're even thinking
about using this.

**Parameters:**

- `sIdentifier`: `string`

**Returns:** `string`

<a id="getglobalboolean"></a>

#### `GetGlobalBoolean(sIdentifier)` - Routine 578

GetGlobalBoolean
This function returns the value of a global boolean (TRUE or FALSE) scripting variable.

**Parameters:**

- `sIdentifier`: `string`

**Returns:** `int`

<a id="setglobalboolean"></a>

#### `SetGlobalBoolean(sIdentifier, nValue)` - Routine 579

SetGlobalBoolean
This function sets the value of a global boolean (TRUE or FALSE) scripting variable.

**Parameters:**

- `sIdentifier`: `string`
- `nValue`: `int`

<a id="getglobalnumber"></a>

#### `GetGlobalNumber(sIdentifier)` - Routine 580

GetGlobalNumber
This function returns the value of a global number (-128 to +127) scripting variable.

**Parameters:**

- `sIdentifier`: `string`

**Returns:** `int`

<a id="setglobalnumber"></a>

#### `SetGlobalNumber(sIdentifier, nValue)` - Routine 581

SetGlobalNumber
This function sets the value of a global number (-128 to +127) scripting variable.

**Parameters:**

- `sIdentifier`: `string`
- `nValue`: `int`

<a id="getgloballocation"></a>

#### `GetGlobalLocation(sIdentifier)` - Routine 692

GetGlobalLocation
This function returns the a global location scripting variable.

**Parameters:**

- `sIdentifier`: `string`

**Returns:** `location`

<a id="setgloballocation"></a>

#### `SetGlobalLocation(sIdentifier, lValue)` - Routine 693

SetGlobalLocation
This function sets the a global location scripting variable.

**Parameters:**

- `sIdentifier`: `string`
- `lValue`: `location`

<a id="setglobalfadein"></a>

#### `SetGlobalFadeIn(fWait=0.0, fLength=0.0, fR=0.0, fG=0.0, fB=0.0)`

719. SetGlobalFadeIn
Sets a Fade In that starts after fWait seconds and fades for fLength Seconds.
The Fade will be from a color specified by the RGB values fR, fG, and fB.
Note that fR, fG, and fB are normalized values.
The default values are an immediate cut in from black.

**Parameters:**

- `fWait`: `float` (default: `0.0`)
- `fLength`: `float` (default: `0.0`)
- `fR`: `float` (default: `0.0`)
- `fG`: `float` (default: `0.0`)
- `fB`: `float` (default: `0.0`)

<a id="setglobalfadeout"></a>

#### `SetGlobalFadeOut(fWait=0.0, fLength=0.0, fR=0.0, fG=0.0, fB=0.0)`

720. SetGlobalFadeOut
Sets a Fade Out that starts after fWait seconds and fades for fLength Seconds.
The Fade will be to a color specified by the RGB values fR, fG, and fB.
Note that fR, fG, and fB are normalized values.
The default values are an immediate cut to from black.

**Parameters:**

- `fWait`: `float` (default: `0.0`)
- `fLength`: `float` (default: `0.0`)
- `fR`: `float` (default: `0.0`)
- `fG`: `float` (default: `0.0`)
- `fB`: `float` (default: `0.0`)
### Item Management

<a id="getitempossessor"></a>

#### `GetItemPossessor(oItem)` - Routine 29

Get the possessor of oItem
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oItem`: `object`

**Returns:** `object`

<a id="getitempossessedby"></a>

#### `GetItemPossessedBy(oCreature, sItemTag)` - Routine 30

Get the object possessed by oCreature with the tag sItemTag
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oCreature`: `object`
- `sItemTag`: `string`

**Returns:** `object`

<a id="createitemonobject"></a>

#### `CreateItemOnObject(sItemTemplate, oTarget=0, nStackSize=1)` - Routine 31

Create an item with the template sItemTemplate in oTarget's inventory.
- nStackSize: This is the stack size of the item to be created
* Return value: The object that has been created.  On error, this returns
OBJECT_INVALID.

**Parameters:**

- `sItemTemplate`: `string`
- `oTarget`: `object` (default: `0`)
- `nStackSize`: `int` (default: `1`)

**Returns:** `object`

<a id="actionequipitem"></a>

#### `ActionEquipItem(oItem, nInventorySlot, bInstant=0)` - Routine 32

Equip oItem into nInventorySlot.
- nInventorySlot: INVENTORY_SLOT_*
* No return value, but if an error occurs the log file will contain
"ActionEquipItem failed."

**Parameters:**

- `oItem`: `object`
- `nInventorySlot`: `int`
- `bInstant`: `int` (default: `0`)

<a id="actionunequipitem"></a>

#### `ActionUnequipItem(oItem, bInstant=0)` - Routine 33

Unequip oItem from whatever slot it is currently in.

**Parameters:**

- `oItem`: `object`
- `bInstant`: `int` (default: `0`)

<a id="actionpickupitem"></a>

#### `ActionPickUpItem(oItem)` - Routine 34

Pick up oItem from the ground.
* No return value, but if an error occurs the log file will contain
"ActionPickUpItem failed."

**Parameters:**

- `oItem`: `object`

<a id="actionputdownitem"></a>

#### `ActionPutDownItem(oItem)` - Routine 35

Put down oItem on the ground.
* No return value, but if an error occurs the log file will contain
"ActionPutDownItem failed."

**Parameters:**

- `oItem`: `object`

<a id="getlastitemequipped"></a>

#### `GetLastItemEquipped()` - Routine 52

Returns the last item that was equipped by a creature.

**Returns:** `object`

<a id="actiongiveitem"></a>

#### `ActionGiveItem(oItem, oGiveTo)` - Routine 135

Give oItem to oGiveTo
If oItem is not a valid item, or oGiveTo is not a valid object, nothing will
happen.

**Parameters:**

- `oItem`: `object`
- `oGiveTo`: `object`

<a id="actiontakeitem"></a>

#### `ActionTakeItem(oItem, oTakeFrom)` - Routine 136

Take oItem from oTakeFrom
If oItem is not a valid item, or oTakeFrom is not a valid object, nothing
will happen.

**Parameters:**

- `oItem`: `object`
- `oTakeFrom`: `object`

<a id="getitemstacksize"></a>

#### `GetItemStackSize(oItem)` - Routine 138

Gets the stack size of an item.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="setitemstacksize"></a>

#### `SetItemStackSize(oItem, nStackSize)` - Routine 150

Set the stack size of an item.
NOTE: The stack size will be clamped to between 1 and the max stack size (as
specified in the base item).

**Parameters:**

- `oItem`: `object`
- `nStackSize`: `int`

<a id="getiteminslot"></a>

#### `GetItemInSlot(nInventorySlot, oCreature=0)` - Routine 155

Get the object which is in oCreature's specified inventory slot
- nInventorySlot: INVENTORY_SLOT_*
- oCreature
* Returns OBJECT_INVALID if oCreature is not a valid creature or there is no
item in nInventorySlot.

**Parameters:**

- `nInventorySlot`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `object`

<a id="createobject"></a>

#### `CreateObject(nObjectType, sTemplate, lLocation, bUseAppearAnimation=0)` - Routine 243

Create an object of the specified type at lLocation.
- nObjectType: OBJECT_TYPE_ITEM, OBJECT_TYPE_CREATURE, OBJECT_TYPE_PLACEABLE,
OBJECT_TYPE_STORE
- sTemplate
- lLocation
- bUseAppearAnimation
Waypoints can now also be created using the CreateObject function.
nObjectType is: OBJECT_TYPE_WAYPOINT
sTemplate will be the tag of the waypoint
lLocation is where the waypoint will be placed
bUseAppearAnimation is ignored

**Parameters:**

- `nObjectType`: `int`
- `sTemplate`: `string`
- `lLocation`: `location`
- `bUseAppearAnimation`: `int` (default: `0`)

**Returns:** `object`

<a id="setitemnonequippable"></a>

#### `SetItemNonEquippable(oItem, bNonEquippable)` - Routine 266

Flag the specified item as being non-equippable or not.  Set bNonEquippable
to TRUE to prevent this item from being equipped, and FALSE to allow
the normal equipping checks to determine if the item can be equipped.
NOTE: This will do nothing if the object passed in is not an item.  Items that
are already equipped when this is called will not automatically be
unequipped.  These items will just be prevented from being re-equipped
should they be unequipped.

**Parameters:**

- `oItem`: `object`
- `bNonEquippable`: `int`

<a id="giveitem"></a>

#### `GiveItem(oItem, oGiveTo)` - Routine 271

Give oItem to oGiveTo (instant; for similar Action use ActionGiveItem)
If oItem is not a valid item, or oGiveTo is not a valid object, nothing will
happen.

**Parameters:**

- `oItem`: `object`
- `oGiveTo`: `object`

<a id="getmoduleitemacquired"></a>

#### `GetModuleItemAcquired()` - Routine 282

Use this in an OnItemAcquired script to get the item that was acquired.
* Returns OBJECT_INVALID if the module is not valid.

**Returns:** `object`

<a id="getmoduleitemacquiredfrom"></a>

#### `GetModuleItemAcquiredFrom()` - Routine 283

Use this in an OnItemAcquired script to get the creatre that previously
possessed the item.
* Returns OBJECT_INVALID if the item was picked up from the ground.

**Returns:** `object`

<a id="getmoduleitemlost"></a>

#### `GetModuleItemLost()` - Routine 292

Use this in an OnItemLost script to get the item that was lost/dropped.
* Returns OBJECT_INVALID if the module is not valid.

**Returns:** `object`

<a id="getmoduleitemlostby"></a>

#### `GetModuleItemLostBy()` - Routine 293

Use this in an OnItemLost script to get the creature that lost the item.
* Returns OBJECT_INVALID if the module is not valid.

**Returns:** `object`

<a id="getidentified"></a>

#### `GetIdentified(oItem)` - Routine 332

Determined whether oItem has been identified.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="setidentified"></a>

#### `SetIdentified(oItem, bIdentified)` - Routine 333

Set whether oItem has been identified.

**Parameters:**

- `oItem`: `object`
- `bIdentified`: `int`

<a id="getfirstitemininventory"></a>

#### `GetFirstItemInInventory(oTarget=0)` - Routine 339

Get the first item in oTarget's inventory (start to cycle through oTarget's
inventory).
* Returns OBJECT_INVALID if the caller is not a creature, item, placeable or store,
or if no item is found.

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `object`

<a id="getnextitemininventory"></a>

#### `GetNextItemInInventory(oTarget=0)` - Routine 340

Get the next item in oTarget's inventory (continue to cycle through oTarget's
inventory).
* Returns OBJECT_INVALID if the caller is not a creature, item, placeable or store,
or if no item is found.

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `object`

<a id="getinventorydisturbitem"></a>

#### `GetInventoryDisturbItem()` - Routine 353

get the item that caused the caller's OnInventoryDisturbed script to fire.
* Returns OBJECT_INVALID if the caller is not a valid object.

**Returns:** `object`

<a id="getbaseitemtype"></a>

#### `GetBaseItemType(oItem)` - Routine 397

Get the base item type (BASE_ITEM_*) of oItem.
* Returns BASE_ITEM_INVALID if oItem is an invalid item.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="getitemacvalue"></a>

#### `GetItemACValue(oItem)` - Routine 401

Get the Armour Class of oItem.
* Return 0 if the oItem is not a valid item, or if oItem has no armour value.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="eventactivateitem"></a>

#### `EventActivateItem(oItem, lTarget, oTarget=1)` - Routine 424

Activate oItem.

**Parameters:**

- `oItem`: `object`
- `lTarget`: `location`
- `oTarget`: `object` (default: `1`)

**Returns:** `event`

<a id="getitemactivated"></a>

#### `GetItemActivated()` - Routine 439

Use this in an OnItemActivated module script to get the item that was activated.

**Returns:** `object`

<a id="getitemactivator"></a>

#### `GetItemActivator()` - Routine 440

Use this in an OnItemActivated module script to get the creature that
activated the item.

**Returns:** `object`

<a id="getitemactivatedtargetlocation"></a>

#### `GetItemActivatedTargetLocation()` - Routine 441

Use this in an OnItemActivated module script to get the location of the item's
target.

**Returns:** `location`

<a id="getitemactivatedtarget"></a>

#### `GetItemActivatedTarget()` - Routine 442

Use this in an OnItemActivated module script to get the item's target.

**Returns:** `object`

<a id="getnumstackeditems"></a>

#### `GetNumStackedItems(oItem)` - Routine 475

Get the number of stacked items that oItem comprises.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="changeitemcost"></a>

#### `ChangeItemCost(sItem, fCostMultiplier)` - Routine 747

ChangeItemCost
Change the cost of an item

**Parameters:**

- `sItem`: `string`
- `fCostMultiplier`: `float`

<a id="createitemonfloor"></a>

#### `CreateItemOnFloor(sTemplate, lLocation, bUseAppearAnimation=0)`

766. CreateItemOnFloor
Should only be used for items that have been created on the ground, and will
be destroyed without ever being picked up or equipped.  Returns true if successful

**Parameters:**

- `sTemplate`: `string`
- `lLocation`: `location`
- `bUseAppearAnimation`: `int` (default: `0`)

**Returns:** `object`
### Item Properties

<a id="getitemhasitemproperty"></a>

#### `GetItemHasItemProperty(oItem, nProperty)` - Routine 398

Determines whether oItem has nProperty.
- oItem
- nProperty: ITEM_PROPERTY_*
* Returns FALSE if oItem is not a valid item, or if oItem does not have
nProperty.

**Parameters:**

- `oItem`: `object`
- `nProperty`: `int`

**Returns:** `int`
### Local Variables

<a id="getlocalboolean"></a>

#### `GetLocalBoolean(oObject, nIndex)`

679. GetLocalBoolean
This gets a boolean flag on an object
currently the index is a range between 0 and 63

**Parameters:**

- `oObject`: `object`
- `nIndex`: `int`

**Returns:** `int`

<a id="setlocalboolean"></a>

#### `SetLocalBoolean(oObject, nIndex, nValue)`

680. SetLocalBoolean
This sets a boolean flag on an object
currently the index is a range between 0 and 63

**Parameters:**

- `oObject`: `object`
- `nIndex`: `int`
- `nValue`: `int`

<a id="getlocalnumber"></a>

#### `GetLocalNumber(oObject, nIndex)`

681. GetLocalNumber
This gets a number on an object
currently the index is a range between 0 and 0

**Parameters:**

- `oObject`: `object`
- `nIndex`: `int`

**Returns:** `int`

<a id="setlocalnumber"></a>

#### `SetLocalNumber(oObject, nIndex, nValue)`

682. SetLocalNumber
This sets a number on an object
currently the index is a range between 0 and 0

**Parameters:**

- `oObject`: `object`
- `nIndex`: `int`
- `nValue`: `int`
### Module and Area Functions

<a id="settime"></a>

#### `SetTime(nHour, nMinute, nSecond, nMillisecond)` - Routine 12

Set the time to the time specified.
- nHour should be from 0 to 23 inclusive
- nMinute should be from 0 to 59 inclusive
- nSecond should be from 0 to 59 inclusive
- nMillisecond should be from 0 to 999 inclusive
1) Time can only be advanced forwards; attempting to set the time backwards
will result in the day advancing and then the time being set to that
specified, e.g. if the current hour is 15 and then the hour is set to 3,
the day will be advanced by 1 and the hour will be set to 3.
2) If values larger than the max hour, minute, second or millisecond are
specified, they will be wrapped around and the overflow will be used to
advance the next field, e.g. specifying 62 hours, 250 minutes, 10 seconds
and 10 milliseconds will result in the calendar day being advanced by 2
and the time being set to 18 hours, 10 minutes, 10 milliseconds.

**Parameters:**

- `nHour`: `int`
- `nMinute`: `int`
- `nSecond`: `int`
- `nMillisecond`: `int`

<a id="setareaunescapable"></a>

#### `SetAreaUnescapable(bUnescapable)` - Routine 14

Sets whether the current area is escapable or not
TRUE means you can not escape the area
FALSE means you can escape the area

**Parameters:**

- `bUnescapable`: `int`

<a id="getareaunescapable"></a>

#### `GetAreaUnescapable()` - Routine 15

Returns whether the current area is escapable or not
TRUE means you can not escape the area
FALSE means you can escape the area

**Returns:** `int`

<a id="gettimehour"></a>

#### `GetTimeHour()` - Routine 16

Get the current hour.

**Returns:** `int`

<a id="gettimeminute"></a>

#### `GetTimeMinute()` - Routine 17

Get the current minute

**Returns:** `int`

<a id="gettimesecond"></a>

#### `GetTimeSecond()` - Routine 18

Get the current second

**Returns:** `int`

<a id="gettimemillisecond"></a>

#### `GetTimeMillisecond()` - Routine 19

Get the current millisecond

**Returns:** `int`

<a id="getarea"></a>

#### `GetArea(oTarget)` - Routine 24

Get the area that oTarget is currently in
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oTarget`: `object`

**Returns:** `object`

<a id="getenteringobject"></a>

#### `GetEnteringObject()` - Routine 25

The value returned by this function depends on the object type of the caller:
1) If the caller is a door or placeable it returns the object that last
triggered it.
2) If the caller is a trigger, area of effect, module, area or encounter it
returns the object that last entered it.
* Return value on error: OBJECT_INVALID

**Returns:** `object`

<a id="getexitingobject"></a>

#### `GetExitingObject()` - Routine 26

Get the object that last left the caller.  This function works on triggers,
areas of effect, modules, areas and encounters.
* Return value on error: OBJECT_INVALID

**Returns:** `object`

<a id="gettransitiontarget"></a>

#### `GetTransitionTarget(oTransition)` - Routine 198

Get the destination (a waypoint or a door) for a trigger or a door.
* Returns OBJECT_INVALID if oTransition is not a valid trigger or door.

**Parameters:**

- `oTransition`: `object`

**Returns:** `object`

<a id="setareatransitionbmp"></a>

#### `SetAreaTransitionBMP(nPredefinedAreaTransition, sCustomAreaTransitionBMP=)` - Routine 203

Set the transition bitmap of a player; this should only be called in area
transition scripts. This action should be run by the person "clicking" the
area transition via AssignCommand.
- nPredefinedAreaTransition:
-> To use a predefined area transition bitmap, use one of AREA_TRANSITION_*
-> To use a custom, user-defined area transition bitmap, use
AREA_TRANSITION_USER_DEFINED and specify the filename in the second
parameter
- sCustomAreaTransitionBMP: this is the filename of a custom, user-defined
area transition bitmap

**Parameters:**

- `nPredefinedAreaTransition`: `int`
- `sCustomAreaTransitionBMP`: `string` (default: ``)

<a id="getmodulefilename"></a>

#### `GetModuleFileName()` - Routine 210

Gets the actual file name of the current module

**Returns:** `string`

<a id="getmodule"></a>

#### `GetModule()` - Routine 242

Get the module.
* Return value on error: OBJECT_INVALID

**Returns:** `object`

<a id="exploreareaforplayer"></a>

#### `ExploreAreaForPlayer(oArea, oPlayer)` - Routine 403

Expose the entire map of oArea to oPlayer.

**Parameters:**

- `oArea`: `object`
- `oPlayer`: `object`

<a id="getmodulename"></a>

#### `GetModuleName()` - Routine 561

Get the module's name in the language of the server that's running it.
* If there is no entry for the language of the server, it will return an
empty string

**Returns:** `string`
### Object Query and Manipulation

<a id="setfacing"></a>

#### `SetFacing(fDirection)` - Routine 10

Cause the caller to face fDirection.
- fDirection is expressed as anticlockwise degrees from Due East.
DIRECTION_EAST, DIRECTION_NORTH, DIRECTION_WEST and DIRECTION_SOUTH are
predefined. (0.0f=East, 90.0f=North, 180.0f=West, 270.0f=South)

**Parameters:**

- `fDirection`: `float`

<a id="getposition"></a>

#### `GetPosition(oTarget)` - Routine 27

Get the position of oTarget
* Return value on error: vector (0.0f, 0.0f, 0.0f)

**Parameters:**

- `oTarget`: `object`

**Returns:** `vector`

<a id="getfacing"></a>

#### `GetFacing(oTarget)` - Routine 28

Get the direction in which oTarget is facing, expressed as a float between
0.0f and 360.0f
* Return value on error: -1.0f

**Parameters:**

- `oTarget`: `object`

**Returns:** `float`

<a id="getnearestcreature"></a>

#### `GetNearestCreature(nFirstCriteriaType, nFirstCriteriaValue, oTarget=0, nNth=1, nSecondCriteriaType=-1, nSecondCriteriaValue=-1, nThirdCriteriaType=-1, nThirdCriteriaValue=-1)` - Routine 38

Get the creature nearest to oTarget, subject to all the criteria specified.
- nFirstCriteriaType: CREATURE_TYPE_*
- nFirstCriteriaValue:
-> CLASS_TYPE_* if nFirstCriteriaType was CREATURE_TYPE_CLASS
-> SPELL_* if nFirstCriteriaType was CREATURE_TYPE_DOES_NOT_HAVE_SPELL_EFFECT
or CREATURE_TYPE_HAS_SPELL_EFFECT
-> TRUE or FALSE if nFirstCriteriaType was CREATURE_TYPE_IS_ALIVE
-> PERCEPTION_* if nFirstCriteriaType was CREATURE_TYPE_PERCEPTION
-> PLAYER_CHAR_IS_PC or PLAYER_CHAR_NOT_PC if nFirstCriteriaType was
CREATURE_TYPE_PLAYER_CHAR
-> RACIAL_TYPE_* if nFirstCriteriaType was CREATURE_TYPE_RACIAL_TYPE
-> REPUTATION_TYPE_* if nFirstCriteriaType was CREATURE_TYPE_REPUTATION
For example, to get the nearest PC, use:
(CREATURE_TYPE_PLAYER_CHAR, PLAYER_CHAR_IS_PC)
- oTarget: We're trying to find the creature of the specified type that is
nearest to oTarget
- nNth: We don't have to find the first nearest: we can find the Nth nearest...
- nSecondCriteriaType: This is used in the same way as nFirstCriteriaType to
further specify the type of creature that we are looking for.
- nSecondCriteriaValue: This is used in the same way as nFirstCriteriaValue
to further specify the type of creature that we are looking for.
- nThirdCriteriaType: This is used in the same way as nFirstCriteriaType to
further specify the type of creature that we are looking for.
- nThirdCriteriaValue: This is used in the same way as nFirstCriteriaValue to
further specify the type of creature that we are looking for.
* Return value on error: OBJECT_INVALID

**Parameters:**

- `nFirstCriteriaType`: `int`
- `nFirstCriteriaValue`: `int`
- `oTarget`: `object` (default: `0`)
- `nNth`: `int` (default: `1`)
- `nSecondCriteriaType`: `int` (default: `-1`)
- `nSecondCriteriaValue`: `int` (default: `-1`)
- `nThirdCriteriaType`: `int` (default: `-1`)
- `nThirdCriteriaValue`: `int` (default: `-1`)

**Returns:** `object`

<a id="getdistancetoobject"></a>

#### `GetDistanceToObject(oObject)` - Routine 41

Get the distance from the caller to oObject in metres.
* Return value on error: -1.0f

**Parameters:**

- `oObject`: `object`

**Returns:** `float`

<a id="getisobjectvalid"></a>

#### `GetIsObjectValid(oObject)` - Routine 42

* Returns TRUE if oObject is a valid object.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getfirsteffect"></a>

#### `GetFirstEffect(oCreature)` - Routine 85

Get the first in-game effect on oCreature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `effect`

<a id="getnexteffect"></a>

#### `GetNextEffect(oCreature)` - Routine 86

Get the next in-game effect on oCreature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `effect`

<a id="removeeffect"></a>

#### `RemoveEffect(oCreature, eEffect)` - Routine 87

Remove eEffect from oCreature.
* No return value

**Parameters:**

- `oCreature`: `object`
- `eEffect`: `effect`

<a id="geteffectcreator"></a>

#### `GetEffectCreator(eEffect)` - Routine 91

Get the object that created eEffect.
* Returns OBJECT_INVALID if eEffect is not a valid effect.

**Parameters:**

- `eEffect`: `effect`

**Returns:** `object`

<a id="getobjecttype"></a>

#### `GetObjectType(oTarget)` - Routine 106

Get the object type (OBJECT_TYPE_*) of oTarget
* Return value if oTarget is not a valid object: -1

**Parameters:**

- `oTarget`: `object`

**Returns:** `int`

<a id="setfacingpoint"></a>

#### `SetFacingPoint(vTarget)` - Routine 143

Cause the caller to face vTarget

**Parameters:**

- `vTarget`: `vector`

<a id="getdistancebetween"></a>

#### `GetDistanceBetween(oObjectA, oObjectB)` - Routine 151

Get the distance in metres between oObjectA and oObjectB.
* Return value if either object is invalid: 0.0f

**Parameters:**

- `oObjectA`: `object`
- `oObjectB`: `object`

**Returns:** `float`

<a id="gettag"></a>

#### `GetTag(oObject)` - Routine 168

Get the Tag of oObject
* Return value if oObject is not a valid object: ""

**Parameters:**

- `oObject`: `object`

**Returns:** `string`

<a id="geteffecttype"></a>

#### `GetEffectType(eEffect)` - Routine 170

Get the effect type (EFFECT_TYPE_*) of eEffect.
* Return value if eEffect is invalid: EFFECT_INVALIDEFFECT

**Parameters:**

- `eEffect`: `effect`

**Returns:** `int`

<a id="getobjectbytag"></a>

#### `GetObjectByTag(sTag, nNth=0)` - Routine 200

Get the nNth object with the specified tag.
- sTag
- nNth: the nth object with this tag may be requested
* Returns OBJECT_INVALID if the object cannot be found.

**Parameters:**

- `sTag`: `string`
- `nNth`: `int` (default: `0`)

**Returns:** `object`

<a id="getlocation"></a>

#### `GetLocation(oObject)` - Routine 213

Get the location of oObject.

**Parameters:**

- `oObject`: `object`

**Returns:** `location`

<a id="location"></a>

#### `Location(vPosition, fOrientation)` - Routine 215

Create a location.

**Parameters:**

- `vPosition`: `vector`
- `fOrientation`: `float`

**Returns:** `location`

<a id="applyeffectatlocation"></a>

#### `ApplyEffectAtLocation(nDurationType, eEffect, lLocation, fDuration=0.0)` - Routine 216

Apply eEffect at lLocation.

**Parameters:**

- `nDurationType`: `int`
- `eEffect`: `effect`
- `lLocation`: `location`
- `fDuration`: `float` (default: `0.0`)

<a id="applyeffecttoobject"></a>

#### `ApplyEffectToObject(nDurationType, eEffect, oTarget, fDuration=0.0)` - Routine 220

Apply eEffect to oTarget.

**Parameters:**

- `nDurationType`: `int`
- `eEffect`: `effect`
- `oTarget`: `object`
- `fDuration`: `float` (default: `0.0`)

<a id="getpositionfromlocation"></a>

#### `GetPositionFromLocation(lLocation)` - Routine 223

Get the position vector from lLocation.

**Parameters:**

- `lLocation`: `location`

**Returns:** `vector`

<a id="getfacingfromlocation"></a>

#### `GetFacingFromLocation(lLocation)` - Routine 225

Get the orientation value from lLocation.

**Parameters:**

- `lLocation`: `location`

**Returns:** `float`

<a id="getnearestcreaturetolocation"></a>

#### `GetNearestCreatureToLocation(nFirstCriteriaType, nFirstCriteriaValue, lLocation, nNth=1, nSecondCriteriaType=-1, nSecondCriteriaValue=-1, nThirdCriteriaType=-1, nThirdCriteriaValue=-1)` - Routine 226

Get the creature nearest to lLocation, subject to all the criteria specified.
- nFirstCriteriaType: CREATURE_TYPE_*
- nFirstCriteriaValue:
-> CLASS_TYPE_* if nFirstCriteriaType was CREATURE_TYPE_CLASS
-> SPELL_* if nFirstCriteriaType was CREATURE_TYPE_DOES_NOT_HAVE_SPELL_EFFECT
or CREATURE_TYPE_HAS_SPELL_EFFECT
-> TRUE or FALSE if nFirstCriteriaType was CREATURE_TYPE_IS_ALIVE
-> PERCEPTION_* if nFirstCriteriaType was CREATURE_TYPE_PERCEPTION
-> PLAYER_CHAR_IS_PC or PLAYER_CHAR_NOT_PC if nFirstCriteriaType was
CREATURE_TYPE_PLAYER_CHAR
-> RACIAL_TYPE_* if nFirstCriteriaType was CREATURE_TYPE_RACIAL_TYPE
-> REPUTATION_TYPE_* if nFirstCriteriaType was CREATURE_TYPE_REPUTATION
For example, to get the nearest PC, use
(CREATURE_TYPE_PLAYER_CHAR, PLAYER_CHAR_IS_PC)
- lLocation: We're trying to find the creature of the specified type that is
nearest to lLocation
- nNth: We don't have to find the first nearest: we can find the Nth nearest....
- nSecondCriteriaType: This is used in the same way as nFirstCriteriaType to
further specify the type of creature that we are looking for.
- nSecondCriteriaValue: This is used in the same way as nFirstCriteriaValue
to further specify the type of creature that we are looking for.
- nThirdCriteriaType: This is used in the same way as nFirstCriteriaType to
further specify the type of creature that we are looking for.
- nThirdCriteriaValue: This is used in the same way as nFirstCriteriaValue to
further specify the type of creature that we are looking for.
* Return value on error: OBJECT_INVALID

**Parameters:**

- `nFirstCriteriaType`: `int`
- `nFirstCriteriaValue`: `int`
- `lLocation`: `location`
- `nNth`: `int` (default: `1`)
- `nSecondCriteriaType`: `int` (default: `-1`)
- `nSecondCriteriaValue`: `int` (default: `-1`)
- `nThirdCriteriaType`: `int` (default: `-1`)
- `nThirdCriteriaValue`: `int` (default: `-1`)

**Returns:** `object`

<a id="getnearestobject"></a>

#### `GetNearestObject(nObjectType=32767, oTarget=0, nNth=1)` - Routine 227

Get the Nth object nearest to oTarget that is of the specified type.
- nObjectType: OBJECT_TYPE_*
- oTarget
- nNth
* Return value on error: OBJECT_INVALID

**Parameters:**

- `nObjectType`: `int` (default: `32767`)
- `oTarget`: `object` (default: `0`)
- `nNth`: `int` (default: `1`)

**Returns:** `object`

<a id="getnearestobjecttolocation"></a>

#### `GetNearestObjectToLocation(nObjectType, lLocation, nNth=1)` - Routine 228

Get the nNth object nearest to lLocation that is of the specified type.
- nObjectType: OBJECT_TYPE_*
- lLocation
- nNth
* Return value on error: OBJECT_INVALID

**Parameters:**

- `nObjectType`: `int`
- `lLocation`: `location`
- `nNth`: `int` (default: `1`)

**Returns:** `object`

<a id="getnearestobjectbytag"></a>

#### `GetNearestObjectByTag(sTag, oTarget=0, nNth=1)` - Routine 229

Get the nth Object nearest to oTarget that has sTag as its tag.
* Return value on error: OBJECT_INVALID

**Parameters:**

- `sTag`: `string`
- `oTarget`: `object` (default: `0`)
- `nNth`: `int` (default: `1`)

**Returns:** `object`

<a id="destroyobject"></a>

#### `DestroyObject(oDestroy, fDelay=0.0, bNoFade=0, fDelayUntilFade=0.0)` - Routine 241

Destroy oObject (irrevocably).
This will not work on modules and areas.
The bNoFade and fDelayUntilFade are for creatures and placeables only

**Parameters:**

- `oDestroy`: `object`
- `fDelay`: `float` (default: `0.0`)
- `bNoFade`: `int` (default: `0`)
- `fDelayUntilFade`: `float` (default: `0.0`)

<a id="getname"></a>

#### `GetName(oObject)` - Routine 253

Get the name of oObject.

**Parameters:**

- `oObject`: `object`

**Returns:** `string`

<a id="getdistancebetweenlocations"></a>

#### `GetDistanceBetweenLocations(lLocationA, lLocationB)` - Routine 298

Get the distance between lLocationA and lLocationB.

**Parameters:**

- `lLocationA`: `location`
- `lLocationB`: `location`

**Returns:** `float`

<a id="playanimation"></a>

#### `PlayAnimation(nAnimation, fSpeed=1.0, fSeconds=0.0)` - Routine 300

Play nAnimation immediately.
- nAnimation: ANIMATION_*
- fSpeed
- fSeconds: Duration of the animation (this is not used for Fire and
Forget animations) If a time of -1.0f is specified for a looping animation
it will loop until the next animation is applied.

**Parameters:**

- `nAnimation`: `int`
- `fSpeed`: `float` (default: `1.0`)
- `fSeconds`: `float` (default: `0.0`)

<a id="getdistancebetween2d"></a>

#### `GetDistanceBetween2D(oObjectA, oObjectB)` - Routine 319

Get the distance in metres between oObjectA and oObjectB in 2D.
* Return value if either object is invalid: 0.0f

**Parameters:**

- `oObjectA`: `object`
- `oObjectB`: `object`

**Returns:** `float`

<a id="getdistancebetweenlocations2d"></a>

#### `GetDistanceBetweenLocations2D(lLocationA, lLocationB)` - Routine 334

Get the distance between lLocationA and lLocationB. in 2D

**Parameters:**

- `lLocationA`: `location`
- `lLocationB`: `location`

**Returns:** `float`

<a id="getdistancetoobject2d"></a>

#### `GetDistanceToObject2D(oObject)` - Routine 335

Get the distance from the caller to oObject in metres.
* Return value on error: -1.0f

**Parameters:**

- `oObject`: `object`

**Returns:** `float`
### Other Functions

<a id="random"></a>

#### `Random(nMaxInteger)` - Routine 0

Get an integer between 0 and nMaxInteger-1.
Return value on error: 0

**Parameters:**

- `nMaxInteger`: `int`

**Returns:** `int`

<a id="printstring"></a>

#### `PrintString(sString)` - Routine 1

Output sString to the log file.

**Parameters:**

- `sString`: `string`

<a id="printfloat"></a>

#### `PrintFloat(fFloat, nWidth=18, nDecimals=9)` - Routine 2

Output a formatted float to the log file.
- nWidth should be a value from 0 to 18 inclusive.
- nDecimals should be a value from 0 to 9 inclusive.

**Parameters:**

- `fFloat`: `float`
- `nWidth`: `int` (default: `18`)
- `nDecimals`: `int` (default: `9`)

<a id="floattostring"></a>

#### `FloatToString(fFloat, nWidth=18, nDecimals=9)` - Routine 3

Convert fFloat into a string.
- nWidth should be a value from 0 to 18 inclusive.
- nDecimals should be a value from 0 to 9 inclusive.

**Parameters:**

- `fFloat`: `float`
- `nWidth`: `int` (default: `18`)
- `nDecimals`: `int` (default: `9`)

**Returns:** `string`

<a id="printinteger"></a>

#### `PrintInteger(nInteger)` - Routine 4

Output nInteger to the log file.

**Parameters:**

- `nInteger`: `int`

<a id="printobject"></a>

#### `PrintObject(oObject)` - Routine 5

Output oObject's ID to the log file.

**Parameters:**

- `oObject`: `object`

<a id="executescript"></a>

#### `ExecuteScript(sScript, oTarget, nScriptVar=-1)` - Routine 8

Make oTarget run sScript and then return execution to the calling script.
If sScript does not specify a compiled script, nothing happens.
- nScriptVar: This value will be returned by calls to GetRunScriptVar.

**Parameters:**

- `sScript`: `string`
- `oTarget`: `object`
- `nScriptVar`: `int` (default: `-1`)

<a id="setcamerafacing"></a>

#### `SetCameraFacing(fDirection)` - Routine 45

Change the direction in which the camera is facing
- fDirection is expressed as anticlockwise degrees from Due East.
(0.0f=East, 90.0f=North, 180.0f=West, 270.0f=South)
This can be used to change the way the camera is facing after the player
emerges from an area transition.

**Parameters:**

- `fDirection`: `float`

<a id="getsubscreenid"></a>

#### `GetSubScreenID()` - Routine 53

Returns the ID of the subscreen that is currently onscreen.  This will be one of the
SUBSCREEN_ID_* constant values.

**Returns:** `int`

<a id="cancelcombat"></a>

#### `CancelCombat(oidCreature)` - Routine 54

Cancels combat for the specified creature.

**Parameters:**

- `oidCreature`: `object`

<a id="pausegame"></a>

#### `PauseGame(bPause)` - Routine 57

Pauses the game if bPause is TRUE.  Unpauses if bPause is FALSE.

**Parameters:**

- `bPause`: `int`

<a id="getstringlength"></a>

#### `GetStringLength(sString)` - Routine 59

Get the length of sString
* Return value on error: -1

**Parameters:**

- `sString`: `string`

**Returns:** `int`

<a id="getstringuppercase"></a>

#### `GetStringUpperCase(sString)` - Routine 60

Convert sString into upper case
* Return value on error: ""

**Parameters:**

- `sString`: `string`

**Returns:** `string`

<a id="getstringlowercase"></a>

#### `GetStringLowerCase(sString)` - Routine 61

Convert sString into lower case
* Return value on error: ""

**Parameters:**

- `sString`: `string`

**Returns:** `string`

<a id="getstringright"></a>

#### `GetStringRight(sString, nCount)` - Routine 62

Get nCount characters from the right end of sString
* Return value on error: ""

**Parameters:**

- `sString`: `string`
- `nCount`: `int`

**Returns:** `string`

<a id="getstringleft"></a>

#### `GetStringLeft(sString, nCount)` - Routine 63

Get nCounter characters from the left end of sString
* Return value on error: ""

**Parameters:**

- `sString`: `string`
- `nCount`: `int`

**Returns:** `string`

<a id="insertstring"></a>

#### `InsertString(sDestination, sString, nPosition)` - Routine 64

Insert sString into sDestination at nPosition
* Return value on error: ""

**Parameters:**

- `sDestination`: `string`
- `sString`: `string`
- `nPosition`: `int`

**Returns:** `string`

<a id="getsubstring"></a>

#### `GetSubString(sString, nStart, nCount)` - Routine 65

Get nCount characters from sString, starting at nStart
* Return value on error: ""

**Parameters:**

- `sString`: `string`
- `nStart`: `int`
- `nCount`: `int`

**Returns:** `string`

<a id="findsubstring"></a>

#### `FindSubString(sString, sSubString)` - Routine 66

Find the position of sSubstring inside sString
* Return value on error: -1

**Parameters:**

- `sString`: `string`
- `sSubString`: `string`

**Returns:** `int`

<a id="fabs"></a>

#### `fabs(fValue)` - Routine 67

Maths operation: absolute value of fValue

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="cos"></a>

#### `cos(fValue)` - Routine 68

Maths operation: cosine of fValue

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="sin"></a>

#### `sin(fValue)` - Routine 69

Maths operation: sine of fValue

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="tan"></a>

#### `tan(fValue)` - Routine 70

Maths operation: tan of fValue

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="acos"></a>

#### `acos(fValue)` - Routine 71

Maths operation: arccosine of fValue
* Returns zero if fValue > 1 or fValue < -1

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="asin"></a>

#### `asin(fValue)` - Routine 72

Maths operation: arcsine of fValue
* Returns zero if fValue >1 or fValue < -1

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="atan"></a>

#### `atan(fValue)` - Routine 73

Maths operation: arctan of fValue

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="log"></a>

#### `log(fValue)` - Routine 74

Maths operation: log of fValue
* Returns zero if fValue <= zero

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="pow"></a>

#### `pow(fValue, fExponent)` - Routine 75

Maths operation: fValue is raised to the power of fExponent
* Returns zero if fValue ==0 and fExponent <0

**Parameters:**

- `fValue`: `float`
- `fExponent`: `float`

**Returns:** `float`

<a id="sqrt"></a>

#### `sqrt(fValue)` - Routine 76

Maths operation: square root of fValue
* Returns zero if fValue <0

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="abs"></a>

#### `abs(nValue)` - Routine 77

Maths operation: integer absolute value of nValue
* Return value on error: 0

**Parameters:**

- `nValue`: `int`

**Returns:** `int`

<a id="getcasterlevel"></a>

#### `GetCasterLevel(oCreature)` - Routine 84

Get the Caster Level of oCreature.
* Return value on error: 0;

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="getiseffectvalid"></a>

#### `GetIsEffectValid(eEffect)` - Routine 88

* Returns TRUE if eEffect is a valid effect.

**Parameters:**

- `eEffect`: `effect`

**Returns:** `int`

<a id="geteffectdurationtype"></a>

#### `GetEffectDurationType(eEffect)` - Routine 89

Get the duration type (DURATION_TYPE_*) of eEffect.
* Return value if eEffect is not valid: -1

**Parameters:**

- `eEffect`: `effect`

**Returns:** `int`

<a id="geteffectsubtype"></a>

#### `GetEffectSubType(eEffect)` - Routine 90

Get the subtype (SUBTYPE_*) of eEffect.
* Return value on error: 0

**Parameters:**

- `eEffect`: `effect`

**Returns:** `int`

<a id="inttostring"></a>

#### `IntToString(nInteger)` - Routine 92

Convert nInteger into a string.
* Return value on error: ""

**Parameters:**

- `nInteger`: `int`

**Returns:** `string`

<a id="getfirstobjectinarea"></a>

#### `GetFirstObjectInArea(oArea=1, nObjectFilter=1)` - Routine 93

Get the first object in oArea.
If no valid area is specified, it will use the caller's area.
- oArea
- nObjectFilter: OBJECT_TYPE_*
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oArea`: `object` (default: `1`)
- `nObjectFilter`: `int` (default: `1`)

**Returns:** `object`

<a id="getnextobjectinarea"></a>

#### `GetNextObjectInArea(oArea=1, nObjectFilter=1)` - Routine 94

Get the next object in oArea.
If no valid area is specified, it will use the caller's area.
- oArea
- nObjectFilter: OBJECT_TYPE_*
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oArea`: `object` (default: `1`)
- `nObjectFilter`: `int` (default: `1`)

**Returns:** `object`

<a id="d2"></a>

#### `d2(nNumDice=1)` - Routine 95

Get the total from rolling (nNumDice x d2 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d3"></a>

#### `d3(nNumDice=1)` - Routine 96

Get the total from rolling (nNumDice x d3 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d4"></a>

#### `d4(nNumDice=1)` - Routine 97

Get the total from rolling (nNumDice x d4 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d6"></a>

#### `d6(nNumDice=1)` - Routine 98

Get the total from rolling (nNumDice x d6 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d8"></a>

#### `d8(nNumDice=1)` - Routine 99

Get the total from rolling (nNumDice x d8 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d10"></a>

#### `d10(nNumDice=1)` - Routine 100

Get the total from rolling (nNumDice x d10 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d12"></a>

#### `d12(nNumDice=1)` - Routine 101

Get the total from rolling (nNumDice x d12 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d20"></a>

#### `d20(nNumDice=1)` - Routine 102

Get the total from rolling (nNumDice x d20 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d100"></a>

#### `d100(nNumDice=1)` - Routine 103

Get the total from rolling (nNumDice x d100 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="vectormagnitude"></a>

#### `VectorMagnitude(vVector)` - Routine 104

Get the magnitude of vVector; this can be used to determine the
distance between two points.
* Return value on error: 0.0f

**Parameters:**

- `vVector`: `vector`

**Returns:** `float`

<a id="getmetamagicfeat"></a>

#### `GetMetaMagicFeat()` - Routine 105

Get the metamagic type (METAMAGIC_*) of the last spell cast by the caller
* Return value if the caster is not a valid object: -1

**Returns:** `int`

<a id="getracialtype"></a>

#### `GetRacialType(oCreature)` - Routine 107

Get the racial type (RACIAL_TYPE_*) of oCreature
* Return value if oCreature is not a valid creature: RACIAL_TYPE_INVALID

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="fortitudesave"></a>

#### `FortitudeSave(oCreature, nDC, nSaveType=0, oSaveVersus=0)` - Routine 108

Do a Fortitude Save check for the given DC
- oCreature
- nDC: Difficulty check
- nSaveType: SAVING_THROW_TYPE_*
- oSaveVersus
Returns: 0 if the saving throw roll failed
Returns: 1 if the saving throw roll succeeded
Returns: 2 if the target was immune to the save type specified

**Parameters:**

- `oCreature`: `object`
- `nDC`: `int`
- `nSaveType`: `int` (default: `0`)
- `oSaveVersus`: `object` (default: `0`)

**Returns:** `int`

<a id="reflexsave"></a>

#### `ReflexSave(oCreature, nDC, nSaveType=0, oSaveVersus=0)` - Routine 109

Does a Reflex Save check for the given DC
- oCreature
- nDC: Difficulty check
- nSaveType: SAVING_THROW_TYPE_*
- oSaveVersus
Returns: 0 if the saving throw roll failed
Returns: 1 if the saving throw roll succeeded
Returns: 2 if the target was immune to the save type specified

**Parameters:**

- `oCreature`: `object`
- `nDC`: `int`
- `nSaveType`: `int` (default: `0`)
- `oSaveVersus`: `object` (default: `0`)

**Returns:** `int`

<a id="willsave"></a>

#### `WillSave(oCreature, nDC, nSaveType=0, oSaveVersus=0)` - Routine 110

Does a Will Save check for the given DC
- oCreature
- nDC: Difficulty check
- nSaveType: SAVING_THROW_TYPE_*
- oSaveVersus
Returns: 0 if the saving throw roll failed
Returns: 1 if the saving throw roll succeeded
Returns: 2 if the target was immune to the save type specified

**Parameters:**

- `oCreature`: `object`
- `nDC`: `int`
- `nSaveType`: `int` (default: `0`)
- `oSaveVersus`: `object` (default: `0`)

**Returns:** `int`

<a id="getspellsavedc"></a>

#### `GetSpellSaveDC()` - Routine 111

Get the DC to save against for a spell (10 + spell level + relevant ability
bonus).  This can be called by a creature or by an Area of Effect object.

**Returns:** `int`

<a id="magicaleffect"></a>

#### `MagicalEffect(eEffect)` - Routine 112

Set the subtype of eEffect to Magical and return eEffect.
(Effects default to magical if the subtype is not set)

**Parameters:**

- `eEffect`: `effect`

**Returns:** `effect`

<a id="supernaturaleffect"></a>

#### `SupernaturalEffect(eEffect)` - Routine 113

Set the subtype of eEffect to Supernatural and return eEffect.
(Effects default to magical if the subtype is not set)

**Parameters:**

- `eEffect`: `effect`

**Returns:** `effect`

<a id="extraordinaryeffect"></a>

#### `ExtraordinaryEffect(eEffect)` - Routine 114

Set the subtype of eEffect to Extraordinary and return eEffect.
(Effects default to magical if the subtype is not set)

**Parameters:**

- `eEffect`: `effect`

**Returns:** `effect`

<a id="getac"></a>

#### `GetAC(oObject, nForFutureUse=0)` - Routine 116

If oObject is a creature, this will return that creature's armour class
If oObject is an item, door or placeable, this will return zero.
- nForFutureUse: this parameter is not currently used
* Return value if oObject is not a creature, item, door or placeable: -1

**Parameters:**

- `oObject`: `object`
- `nForFutureUse`: `int` (default: `0`)

**Returns:** `int`

<a id="roundstoseconds"></a>

#### `RoundsToSeconds(nRounds)` - Routine 121

Convert nRounds into a number of seconds
A round is always 6.0 seconds

**Parameters:**

- `nRounds`: `int`

**Returns:** `float`

<a id="hourstoseconds"></a>

#### `HoursToSeconds(nHours)` - Routine 122

Convert nHours into a number of seconds
The result will depend on how many minutes there are per hour (game-time)

**Parameters:**

- `nHours`: `int`

**Returns:** `float`

<a id="turnstoseconds"></a>

#### `TurnsToSeconds(nTurns)` - Routine 123

Convert nTurns into a number of seconds
A turn is always 60.0 seconds

**Parameters:**

- `nTurns`: `int`

**Returns:** `float`

<a id="getfirstobjectinshape"></a>

#### `GetFirstObjectInShape(nShape, fSize, lTarget, bLineOfSight=0, nObjectFilter=1, vOrigin=0.0 0.0 0.0)` - Routine 128

Get the first object in nShape
- nShape: SHAPE_*
- fSize:
-> If nShape == SHAPE_SPHERE, this is the radius of the sphere
-> If nShape == SHAPE_SPELLCYLINDER, this is the radius of the cylinder
-> If nShape == SHAPE_CONE, this is the widest radius of the cone
-> If nShape == SHAPE_CUBE, this is half the length of one of the sides of
the cube
- lTarget: This is the centre of the effect, usually GetSpellTargetPosition(),
or the end of a cylinder or cone.
- bLineOfSight: This controls whether to do a line-of-sight check on the
object returned.
(This can be used to ensure that spell effects do not go through walls.)
- nObjectFilter: This allows you to filter out undesired object types, using
bitwise "or".
For example, to return only creatures and doors, the value for this
parameter would be OBJECT_TYPE_CREATURE | OBJECT_TYPE_DOOR
- vOrigin: This is only used for cylinders and cones, and specifies the
origin of the effect(normally the spell-caster's position).
Return value on error: OBJECT_INVALID

**Parameters:**

- `nShape`: `int`
- `fSize`: `float`
- `lTarget`: `location`
- `bLineOfSight`: `int` (default: `0`)
- `nObjectFilter`: `int` (default: `1`)
- `vOrigin`: `vector` (default: `0.0 0.0 0.0`)

**Returns:** `object`

<a id="getnextobjectinshape"></a>

#### `GetNextObjectInShape(nShape, fSize, lTarget, bLineOfSight=0, nObjectFilter=1, vOrigin=0.0 0.0 0.0)` - Routine 129

Get the next object in nShape
- nShape: SHAPE_*
- fSize:
-> If nShape == SHAPE_SPHERE, this is the radius of the sphere
-> If nShape == SHAPE_SPELLCYLINDER, this is the radius of the cylinder
-> If nShape == SHAPE_CONE, this is the widest radius of the cone
-> If nShape == SHAPE_CUBE, this is half the length of one of the sides of
the cube
- lTarget: This is the centre of the effect, usually GetSpellTargetPosition(),
or the end of a cylinder or cone.
- bLineOfSight: This controls whether to do a line-of-sight check on the
object returned. (This can be used to ensure that spell effects do not go
through walls.)
- nObjectFilter: This allows you to filter out undesired object types, using
bitwise "or". For example, to return only creatures and doors, the value for
this parameter would be OBJECT_TYPE_CREATURE | OBJECT_TYPE_DOOR
- vOrigin: This is only used for cylinders and cones, and specifies the origin
of the effect (normally the spell-caster's position).
Return value on error: OBJECT_INVALID

**Parameters:**

- `nShape`: `int`
- `fSize`: `float`
- `lTarget`: `location`
- `bLineOfSight`: `int` (default: `0`)
- `nObjectFilter`: `int` (default: `1`)
- `vOrigin`: `vector` (default: `0.0 0.0 0.0`)

**Returns:** `object`

<a id="signalevent"></a>

#### `SignalEvent(oObject, evToRun)` - Routine 131

Cause oObject to run evToRun

**Parameters:**

- `oObject`: `object`
- `evToRun`: `event`

<a id="eventuserdefined"></a>

#### `EventUserDefined(nUserDefinedEventNumber)` - Routine 132

Create an event of the type nUserDefinedEventNumber

**Parameters:**

- `nUserDefinedEventNumber`: `int`

**Returns:** `event`

<a id="vectornormalize"></a>

#### `VectorNormalize(vVector)` - Routine 137

Normalize vVector

**Parameters:**

- `vVector`: `vector`

**Returns:** `vector`

<a id="getisdead"></a>

#### `GetIsDead(oCreature)` - Routine 140

* Returns TRUE if oCreature is a dead NPC, dead PC or a dying PC.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="printvector"></a>

#### `PrintVector(vVector, bPrepend)` - Routine 141

Output vVector to the logfile.
- vVector
- bPrepend: if this is TRUE, the message will be prefixed with "PRINTVECTOR:"

**Parameters:**

- `vVector`: `vector`
- `bPrepend`: `int`

<a id="vector"></a>

#### `Vector(x=0.0, y=0.0, z=0.0)` - Routine 142

Create a vector with the specified values for x, y and z

**Parameters:**

- `x`: `float` (default: `0.0`)
- `y`: `float` (default: `0.0`)
- `z`: `float` (default: `0.0`)

**Returns:** `vector`

<a id="angletovector"></a>

#### `AngleToVector(fAngle)` - Routine 144

Convert fAngle to a vector

**Parameters:**

- `fAngle`: `float`

**Returns:** `vector`

<a id="vectortoangle"></a>

#### `VectorToAngle(vVector)` - Routine 145

Convert vVector to an angle

**Parameters:**

- `vVector`: `vector`

**Returns:** `float`

<a id="touchattackmelee"></a>

#### `TouchAttackMelee(oTarget, bDisplayFeedback=1)` - Routine 146

The caller will perform a Melee Touch Attack on oTarget
This is not an action, and it assumes the caller is already within range of
oTarget
* Returns 0 on a miss, 1 on a hit and 2 on a critical hit

**Parameters:**

- `oTarget`: `object`
- `bDisplayFeedback`: `int` (default: `1`)

**Returns:** `int`

<a id="touchattackranged"></a>

#### `TouchAttackRanged(oTarget, bDisplayFeedback=1)` - Routine 147

The caller will perform a Ranged Touch Attack on oTarget
* Returns 0 on a miss, 1 on a hit and 2 on a critical hit

**Parameters:**

- `oTarget`: `object`
- `bDisplayFeedback`: `int` (default: `1`)

**Returns:** `int`

<a id="setreturnstrref"></a>

#### `SetReturnStrref(bShow, srStringRef=0, srReturnQueryStrRef=0)` - Routine 152

SetReturnStrref
This function will turn on/off the display of the 'return to ebon hawk' option
on the map screen and allow the string to be changed to an arbitrary string ref
srReturnQueryStrRef is the string ref that will be displayed in the query pop
up confirming that you wish to return to the specified location.

**Parameters:**

- `bShow`: `int`
- `srStringRef`: `int` (default: `0`)
- `srReturnQueryStrRef`: `int` (default: `0`)

<a id="setcommandable"></a>

#### `SetCommandable(bCommandable, oTarget=0)` - Routine 162

Set whether oTarget's action stack can be modified

**Parameters:**

- `bCommandable`: `int`
- `oTarget`: `object` (default: `0`)

<a id="getcommandable"></a>

#### `GetCommandable(oTarget=0)` - Routine 163

Determine whether oTarget's action stack can be modified.

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `int`

<a id="gethitdice"></a>

#### `GetHitDice(oCreature)` - Routine 166

Get the number of hitdice for oCreature.
* Return value if oCreature is not a valid creature: 0

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="resistforce"></a>

#### `ResistForce(oSource, oTarget)` - Routine 169

Do a Force Resistance check between oSource and oTarget, returning TRUE if
the force was resisted.
* Return value if oSource or oTarget is an invalid object: FALSE

**Parameters:**

- `oSource`: `object`
- `oTarget`: `object`

**Returns:** `int`

<a id="changefaction"></a>

#### `ChangeFaction(oObjectToChangeFaction, oMemberOfFactionToJoin)` - Routine 173

Make oObjectToChangeFaction join the faction of oMemberOfFactionToJoin.
NB. ** This will only work for two NPCs **

**Parameters:**

- `oObjectToChangeFaction`: `object`
- `oMemberOfFactionToJoin`: `object`

<a id="getislistening"></a>

#### `GetIsListening(oObject)` - Routine 174

* Returns TRUE if oObject is listening for something

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="setlistening"></a>

#### `SetListening(oObject, bValue)` - Routine 175

Set whether oObject is listening.

**Parameters:**

- `oObject`: `object`
- `bValue`: `int`

<a id="setlistenpattern"></a>

#### `SetListenPattern(oObject, sPattern, nNumber=0)` - Routine 176

Set the string for oObject to listen for.
Note: this does not set oObject to be listening.

**Parameters:**

- `oObject`: `object`
- `sPattern`: `string`
- `nNumber`: `int` (default: `0`)

<a id="teststringagainstpattern"></a>

#### `TestStringAgainstPattern(sPattern, sStringToTest)` - Routine 177

* Returns TRUE if sStringToTest matches sPattern.

**Parameters:**

- `sPattern`: `string`
- `sStringToTest`: `string`

**Returns:** `int`

<a id="getmatchedsubstring"></a>

#### `GetMatchedSubstring(nString)` - Routine 178

Get the appropriate matched string (this should only be used in
OnConversation scripts).
* Returns the appropriate matched string, otherwise returns ""

**Parameters:**

- `nString`: `int`

**Returns:** `string`

<a id="getmatchedsubstringscount"></a>

#### `GetMatchedSubstringsCount()` - Routine 179

Get the number of string parameters available.
* Returns -1 if no string matched (this could be because of a dialogue event)

**Returns:** `int`

<a id="getfactionweakestmember"></a>

#### `GetFactionWeakestMember(oFactionMember=0, bMustBeVisible=1)` - Routine 181

Get the weakest member of oFactionMember's faction.
* Returns OBJECT_INVALID if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object` (default: `0`)
- `bMustBeVisible`: `int` (default: `1`)

**Returns:** `object`

<a id="getfactionstrongestmember"></a>

#### `GetFactionStrongestMember(oFactionMember=0, bMustBeVisible=1)` - Routine 182

Get the strongest member of oFactionMember's faction.
* Returns OBJECT_INVALID if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object` (default: `0`)
- `bMustBeVisible`: `int` (default: `1`)

**Returns:** `object`

<a id="getfactionmostdamagedmember"></a>

#### `GetFactionMostDamagedMember(oFactionMember=0, bMustBeVisible=1)` - Routine 183

Get the member of oFactionMember's faction that has taken the most hit points
of damage.
* Returns OBJECT_INVALID if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object` (default: `0`)
- `bMustBeVisible`: `int` (default: `1`)

**Returns:** `object`

<a id="getfactionleastdamagedmember"></a>

#### `GetFactionLeastDamagedMember(oFactionMember=0, bMustBeVisible=1)` - Routine 184

Get the member of oFactionMember's faction that has taken the fewest hit
points of damage.
* Returns OBJECT_INVALID if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object` (default: `0`)
- `bMustBeVisible`: `int` (default: `1`)

**Returns:** `object`

<a id="getfactiongold"></a>

#### `GetFactionGold(oFactionMember)` - Routine 185

Get the amount of gold held by oFactionMember's faction.
* Returns -1 if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object`

**Returns:** `int`

<a id="getfactionaveragereputation"></a>

#### `GetFactionAverageReputation(oSourceFactionMember, oTarget)` - Routine 186

Get an integer between 0 and 100 (inclusive) that represents how
oSourceFactionMember's faction feels about oTarget.
* Return value on error: -1

**Parameters:**

- `oSourceFactionMember`: `object`
- `oTarget`: `object`

**Returns:** `int`

<a id="getfactionaveragelevel"></a>

#### `GetFactionAverageLevel(oFactionMember)` - Routine 189

Get the average level of the members of the faction.
* Return value on error: -1

**Parameters:**

- `oFactionMember`: `object`

**Returns:** `int`

<a id="getfactionaveragexp"></a>

#### `GetFactionAverageXP(oFactionMember)` - Routine 190

Get the average XP of the members of the faction.
* Return value on error: -1

**Parameters:**

- `oFactionMember`: `object`

**Returns:** `int`

<a id="getfactionmostfrequentclass"></a>

#### `GetFactionMostFrequentClass(oFactionMember)` - Routine 191

Get the most frequent class in the faction - this can be compared with the
constants CLASS_TYPE_*.
* Return value on error: -1

**Parameters:**

- `oFactionMember`: `object`

**Returns:** `int`

<a id="getfactionworstac"></a>

#### `GetFactionWorstAC(oFactionMember=0, bMustBeVisible=1)` - Routine 192

Get the object faction member with the lowest armour class.
* Returns OBJECT_INVALID if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object` (default: `0`)
- `bMustBeVisible`: `int` (default: `1`)

**Returns:** `object`

<a id="getfactionbestac"></a>

#### `GetFactionBestAC(oFactionMember=0, bMustBeVisible=1)` - Routine 193

Get the object faction member with the highest armour class.
* Returns OBJECT_INVALID if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object` (default: `0`)
- `bMustBeVisible`: `int` (default: `1`)

**Returns:** `object`

<a id="getlistenpatternnumber"></a>

#### `GetListenPatternNumber()` - Routine 195

In an onConversation script this gets the number of the string pattern
matched (the one that triggered the script).
* Returns -1 if no string matched

**Returns:** `int`

<a id="getwaypointbytag"></a>

#### `GetWaypointByTag(sWaypointTag)` - Routine 197

Get the first waypoint with the specified tag.
* Returns OBJECT_INVALID if the waypoint cannot be found.

**Parameters:**

- `sWaypointTag`: `string`

**Returns:** `object`

<a id="adjustreputation"></a>

#### `AdjustReputation(oTarget, oSourceFactionMember, nAdjustment)` - Routine 209

Adjust how oSourceFactionMember's faction feels about oTarget by the
specified amount.
Note: This adjusts Faction Reputation, how the entire faction that
oSourceFactionMember is in, feels about oTarget.
* No return value

**Parameters:**

- `oTarget`: `object`
- `oSourceFactionMember`: `object`
- `nAdjustment`: `int`

<a id="getgoingtobeattackedby"></a>

#### `GetGoingToBeAttackedBy(oTarget)` - Routine 211

Get the creature that is going to attack oTarget.
Note: This value is cleared out at the end of every combat round and should
not be used in any case except when getting a "going to be attacked" shout
from the master creature (and this creature is a henchman)
* Returns OBJECT_INVALID if oTarget is not a valid creature.

**Parameters:**

- `oTarget`: `object`

**Returns:** `object`

<a id="feettometers"></a>

#### `FeetToMeters(fFeet)` - Routine 218

Convert fFeet into a number of meters.

**Parameters:**

- `fFeet`: `float`

**Returns:** `float`

<a id="yardstometers"></a>

#### `YardsToMeters(fYards)` - Routine 219

Convert fYards into a number of meters.

**Parameters:**

- `fYards`: `float`

**Returns:** `float`

<a id="inttofloat"></a>

#### `IntToFloat(nInteger)` - Routine 230

Convert nInteger into a floating point number.

**Parameters:**

- `nInteger`: `int`

**Returns:** `float`

<a id="floattoint"></a>

#### `FloatToInt(fFloat)` - Routine 231

Convert fFloat into the nearest integer.

**Parameters:**

- `fFloat`: `float`

**Returns:** `int`

<a id="stringtoint"></a>

#### `StringToInt(sNumber)` - Routine 232

Convert sNumber into an integer.

**Parameters:**

- `sNumber`: `string`

**Returns:** `int`

<a id="stringtofloat"></a>

#### `StringToFloat(sNumber)` - Routine 233

Convert sNumber into a floating point number.

**Parameters:**

- `sNumber`: `string`

**Returns:** `float`

<a id="getstringbystrref"></a>

#### `GetStringByStrRef(nStrRef)` - Routine 239

Get a string from the talk table using nStrRef.

**Parameters:**

- `nStrRef`: `int`

**Returns:** `string`

<a id="eventspellcastat"></a>

#### `EventSpellCastAt(oCaster, nSpell, bHarmful=1)` - Routine 244

Create an event which triggers the "SpellCastAt" script

**Parameters:**

- `oCaster`: `object`
- `nSpell`: `int`
- `bHarmful`: `int` (default: `1`)

**Returns:** `event`

<a id="getuserdefinedeventnumber"></a>

#### `GetUserDefinedEventNumber()` - Routine 247

This is for use in a user-defined script, it gets the event number.

**Returns:** `int`

<a id="randomname"></a>

#### `RandomName()` - Routine 249

Generate a random name.

**Returns:** `string`

<a id="getloadfromsavegame"></a>

#### `GetLoadFromSaveGame()` - Routine 251

Returns whether this script is being run
while a load game is in progress

**Returns:** `int`

<a id="getlastspeaker"></a>

#### `GetLastSpeaker()` - Routine 254

Use this in a conversation script to get the person with whom you are conversing.
* Returns OBJECT_INVALID if the caller is not a valid creature.

**Returns:** `object`

<a id="getlastperceived"></a>

#### `GetLastPerceived()` - Routine 256

Use this in an OnPerception script to get the object that was perceived.
* Returns OBJECT_INVALID if the caller is not a valid creature.

**Returns:** `object`

<a id="getlastperceptionheard"></a>

#### `GetLastPerceptionHeard()` - Routine 257

Use this in an OnPerception script to determine whether the object that was
perceived was heard.

**Returns:** `int`

<a id="getlastperceptioninaudible"></a>

#### `GetLastPerceptionInaudible()` - Routine 258

Use this in an OnPerception script to determine whether the object that was
perceived has become inaudible.

**Returns:** `int`

<a id="getlastperceptionseen"></a>

#### `GetLastPerceptionSeen()` - Routine 259

Use this in an OnPerception script to determine whether the object that was
perceived was seen.

**Returns:** `int`

<a id="getlastclosedby"></a>

#### `GetLastClosedBy()` - Routine 260

Use this in an OnClosed script to get the object that closed the door or placeable.
* Returns OBJECT_INVALID if the caller is not a valid door or placeable.

**Returns:** `object`

<a id="getlastperceptionvanished"></a>

#### `GetLastPerceptionVanished()` - Routine 261

Use this in an OnPerception script to determine whether the object that was
perceived has vanished.

**Returns:** `int`

<a id="getareaofeffectcreator"></a>

#### `GetAreaOfEffectCreator(oAreaOfEffectObject=0)` - Routine 264

This returns the creator of oAreaOfEffectObject.
* Returns OBJECT_INVALID if oAreaOfEffectObject is not a valid Area of Effect object.

**Parameters:**

- `oAreaOfEffectObject`: `object` (default: `0`)

**Returns:** `object`

<a id="showlevelupgui"></a>

#### `ShowLevelUpGUI()` - Routine 265

Brings up the level up GUI for the player.  The GUI will only show up
if the player has gained enough experience points to level up.
* Returns TRUE if the GUI was successfully brought up; FALSE if not.

**Returns:** `int`

<a id="getbuttonmashcheck"></a>

#### `GetButtonMashCheck()` - Routine 267

GetButtonMashCheck
This function returns whether the button mash check, used for the combat tutorial, is on

**Returns:** `int`

<a id="setbuttonmashcheck"></a>

#### `SetButtonMashCheck(nCheck)` - Routine 268

SetButtonMashCheck
This function sets the button mash check variable, and is used for turning the check on and off

**Parameters:**

- `nCheck`: `int`

<a id="objecttostring"></a>

#### `ObjectToString(oObject)` - Routine 272

Convert oObject into a hexadecimal string.

**Parameters:**

- `oObject`: `object`

**Returns:** `string`

<a id="getisimmune"></a>

#### `GetIsImmune(oCreature, nImmunityType, oVersus=1)` - Routine 274

- oCreature
- nImmunityType: IMMUNITY_TYPE_*
- oVersus: if this is specified, then we also check for the race and
alignment of oVersus
* Returns TRUE if oCreature has immunity of type nImmunity versus oVersus.

**Parameters:**

- `oCreature`: `object`
- `nImmunityType`: `int`
- `oVersus`: `object` (default: `1`)

**Returns:** `int`

<a id="getencounteractive"></a>

#### `GetEncounterActive(oEncounter=0)` - Routine 276

Determine whether oEncounter is active.

**Parameters:**

- `oEncounter`: `object` (default: `0`)

**Returns:** `int`

<a id="setencounteractive"></a>

#### `SetEncounterActive(nNewValue, oEncounter=0)` - Routine 277

Set oEncounter's active state to nNewValue.
- nNewValue: TRUE/FALSE
- oEncounter

**Parameters:**

- `nNewValue`: `int`
- `oEncounter`: `object` (default: `0`)

<a id="getencounterspawnsmax"></a>

#### `GetEncounterSpawnsMax(oEncounter=0)` - Routine 278

Get the maximum number of times that oEncounter will spawn.

**Parameters:**

- `oEncounter`: `object` (default: `0`)

**Returns:** `int`

<a id="setencounterspawnsmax"></a>

#### `SetEncounterSpawnsMax(nNewValue, oEncounter=0)` - Routine 279

Set the maximum number of times that oEncounter can spawn

**Parameters:**

- `nNewValue`: `int`
- `oEncounter`: `object` (default: `0`)

<a id="getencounterspawnscurrent"></a>

#### `GetEncounterSpawnsCurrent(oEncounter=0)` - Routine 280

Get the number of times that oEncounter has spawned so far

**Parameters:**

- `oEncounter`: `object` (default: `0`)

**Returns:** `int`

<a id="setencounterspawnscurrent"></a>

#### `SetEncounterSpawnsCurrent(nNewValue, oEncounter=0)` - Routine 281

Set the number of times that oEncounter has spawned so far

**Parameters:**

- `nNewValue`: `int`
- `oEncounter`: `object` (default: `0`)

<a id="getobjectseen"></a>

#### `GetObjectSeen(oTarget, oSource=0)` - Routine 289

Determine whether oSource sees oTarget.

**Parameters:**

- `oTarget`: `object`
- `oSource`: `object` (default: `0`)

**Returns:** `int`

<a id="getobjectheard"></a>

#### `GetObjectHeard(oTarget, oSource=0)` - Routine 290

Determine whether oSource hears oTarget.

**Parameters:**

- `oTarget`: `object`
- `oSource`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastplayerdied"></a>

#### `GetLastPlayerDied()` - Routine 291

Use this in an OnPlayerDeath module script to get the last player that died.

**Returns:** `object`

<a id="setencounterdifficulty"></a>

#### `SetEncounterDifficulty(nEncounterDifficulty, oEncounter=0)` - Routine 296

Set the difficulty level of oEncounter.
- nEncounterDifficulty: ENCOUNTER_DIFFICULTY_*
- oEncounter

**Parameters:**

- `nEncounterDifficulty`: `int`
- `oEncounter`: `object` (default: `0`)

<a id="getencounterdifficulty"></a>

#### `GetEncounterDifficulty(oEncounter=0)` - Routine 297

Get the difficulty level of oEncounter.

**Parameters:**

- `oEncounter`: `object` (default: `0`)

**Returns:** `int`

<a id="talentspell"></a>

#### `TalentSpell(nSpell)` - Routine 301

Create a Spell Talent.
- nSpell: SPELL_*

**Parameters:**

- `nSpell`: `int`

**Returns:** `talent`

<a id="talentfeat"></a>

#### `TalentFeat(nFeat)` - Routine 302

Create a Feat Talent.
- nFeat: FEAT_*

**Parameters:**

- `nFeat`: `int`

**Returns:** `talent`

<a id="talentskill"></a>

#### `TalentSkill(nSkill)` - Routine 303

Create a Skill Talent.
- nSkill: SKILL_*

**Parameters:**

- `nSkill`: `int`

**Returns:** `talent`

<a id="geteffectspellid"></a>

#### `GetEffectSpellId(eSpellEffect)` - Routine 305

Get the spell (SPELL_*) that applied eSpellEffect.
* Returns -1 if eSpellEffect was applied outside a spell script.

**Parameters:**

- `eSpellEffect`: `effect`

**Returns:** `int`

<a id="getcreaturehastalent"></a>

#### `GetCreatureHasTalent(tTalent, oCreature=0)` - Routine 306

Determine whether oCreature has tTalent.

**Parameters:**

- `tTalent`: `talent`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getcreaturetalentrandom"></a>

#### `GetCreatureTalentRandom(nCategory, oCreature=0, nInclusion=0)` - Routine 307

Get a random talent of oCreature, within nCategory.
- nCategory: TALENT_CATEGORY_*
- oCreature
- nInclusion: types of talent to include

**Parameters:**

- `nCategory`: `int`
- `oCreature`: `object` (default: `0`)
- `nInclusion`: `int` (default: `0`)

**Returns:** `talent`

<a id="getcreaturetalentbest"></a>

#### `GetCreatureTalentBest(nCategory, nCRMax, oCreature=0, nInclusion=0, nExcludeType=-1, nExcludeId=-1)` - Routine 308

Get the best talent (i.e. closest to nCRMax without going over) of oCreature,
within nCategory.
- nCategory: TALENT_CATEGORY_*
- nCRMax: Challenge Rating of the talent
- oCreature
- nInclusion: types of talent to include
- nExcludeType: TALENT_TYPE_FEAT or TALENT_TYPE_FORCE, type of talent that we wish to ignore
- nExcludeId: Talent ID of the talent we wish to ignore.
A value of TALENT_EXCLUDE_ALL_OF_TYPE for this parameter will mean that all talents of
type nExcludeType are ignored.

**Parameters:**

- `nCategory`: `int`
- `nCRMax`: `int`
- `oCreature`: `object` (default: `0`)
- `nInclusion`: `int` (default: `0`)
- `nExcludeType`: `int` (default: `-1`)
- `nExcludeId`: `int` (default: `-1`)

**Returns:** `talent`

<a id="getgoldpiecevalue"></a>

#### `GetGoldPieceValue(oItem)` - Routine 311

Get the gold piece value of oItem.
* Returns 0 if oItem is not a valid item.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="getisplayableracialtype"></a>

#### `GetIsPlayableRacialType(oCreature)` - Routine 312

* Returns TRUE if oCreature is of a playable racial type.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="jumptolocation"></a>

#### `JumpToLocation(lDestination)` - Routine 313

Jump to lDestination.  The action is added to the TOP of the action queue.

**Parameters:**

- `lDestination`: `location`

<a id="getlastattacktype"></a>

#### `GetLastAttackType(oCreature=0)` - Routine 317

Get the attack type (SPECIAL_ATTACK_*) of oCreature's last attack.
This only works when oCreature is in combat.

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastattackmode"></a>

#### `GetLastAttackMode(oCreature=0)` - Routine 318

Get the attack mode (COMBAT_MODE_*) of oCreature's last attack.
This only works when oCreature is in combat.

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastassociatecommand"></a>

#### `GetLastAssociateCommand(oAssociate=0)` - Routine 321

Get the last command (ASSOCIATE_COMMAND_*) issued to oAssociate.

**Parameters:**

- `oAssociate`: `object` (default: `0`)

**Returns:** `int`

<a id="givegoldtocreature"></a>

#### `GiveGoldToCreature(oCreature, nGP)` - Routine 322

Give nGP gold to oCreature.

**Parameters:**

- `oCreature`: `object`
- `nGP`: `int`

<a id="setlocked"></a>

#### `SetLocked(oTarget, bLocked)` - Routine 324

Set the locked state of oTarget, which can be a door or a placeable object.

**Parameters:**

- `oTarget`: `object`
- `bLocked`: `int`

<a id="getlocked"></a>

#### `GetLocked(oTarget)` - Routine 325

Get the locked state of oTarget, which can be a door or a placeable object.

**Parameters:**

- `oTarget`: `object`

**Returns:** `int`

<a id="getclickingobject"></a>

#### `GetClickingObject()` - Routine 326

Use this in a trigger's OnClick event script to get the object that last
clicked on it.
This is identical to GetEnteringObject.

**Returns:** `object`

<a id="setassociatelistenpatterns"></a>

#### `SetAssociateListenPatterns(oTarget=0)` - Routine 327

Initialise oTarget to listen for the standard Associates commands.

**Parameters:**

- `oTarget`: `object` (default: `0`)

<a id="getlastweaponused"></a>

#### `GetLastWeaponUsed(oCreature)` - Routine 328

Get the last weapon that oCreature used in an attack.
* Returns OBJECT_INVALID if oCreature did not attack, or has no weapon equipped.

**Parameters:**

- `oCreature`: `object`

**Returns:** `object`

<a id="getlastusedby"></a>

#### `GetLastUsedBy()` - Routine 330

Get the last object that used the placeable object that is calling this function.
* Returns OBJECT_INVALID if it is called by something other than a placeable or
a door.

**Returns:** `object`

<a id="getblockingdoor"></a>

#### `GetBlockingDoor()` - Routine 336

Get the last blocking door encountered by the caller of this function.
* Returns OBJECT_INVALID if the caller is not a valid creature.

**Returns:** `object`

<a id="getisdooractionpossible"></a>

#### `GetIsDoorActionPossible(oTargetDoor, nDoorAction)` - Routine 337

- oTargetDoor
- nDoorAction: DOOR_ACTION_*
* Returns TRUE if nDoorAction can be performed on oTargetDoor.

**Parameters:**

- `oTargetDoor`: `object`
- `nDoorAction`: `int`

**Returns:** `int`

<a id="dodooraction"></a>

#### `DoDoorAction(oTargetDoor, nDoorAction)` - Routine 338

Perform nDoorAction on oTargetDoor.

**Parameters:**

- `oTargetDoor`: `object`
- `nDoorAction`: `int`

<a id="getlastdisarmed"></a>

#### `GetLastDisarmed()` - Routine 347

Get the last object that disarmed the trap on the caller.
* Returns OBJECT_INVALID if the caller is not a valid placeable, trigger or
door.

**Returns:** `object`

<a id="getlastdisturbed"></a>

#### `GetLastDisturbed()` - Routine 348

Get the last object that disturbed the inventory of the caller.
* Returns OBJECT_INVALID if the caller is not a valid creature or placeable.

**Returns:** `object`

<a id="getlastlocked"></a>

#### `GetLastLocked()` - Routine 349

Get the last object that locked the caller.
* Returns OBJECT_INVALID if the caller is not a valid door or placeable.

**Returns:** `object`

<a id="getlastunlocked"></a>

#### `GetLastUnlocked()` - Routine 350

Get the last object that unlocked the caller.
* Returns OBJECT_INVALID if the caller is not a valid door or placeable.

**Returns:** `object`

<a id="getinventorydisturbtype"></a>

#### `GetInventoryDisturbType()` - Routine 352

Get the type of disturbance (INVENTORY_DISTURB_*) that caused the caller's
OnInventoryDisturbed script to fire.  This will only work for creatures and
placeables.

**Returns:** `int`

<a id="showupgradescreen"></a>

#### `ShowUpgradeScreen(oItem=1)` - Routine 354

Displays the upgrade screen where the player can modify weapons and armor

**Parameters:**

- `oItem`: `object` (default: `1`)

<a id="versusracialtypeeffect"></a>

#### `VersusRacialTypeEffect(eEffect, nRacialType)` - Routine 356

Set eEffect to be versus nRacialType.
- eEffect
- nRacialType: RACIAL_TYPE_*

**Parameters:**

- `eEffect`: `effect`
- `nRacialType`: `int`

**Returns:** `effect`

<a id="versustrapeffect"></a>

#### `VersusTrapEffect(eEffect)` - Routine 357

Set eEffect to be versus traps.

**Parameters:**

- `eEffect`: `effect`

**Returns:** `effect`

<a id="getistalentvalid"></a>

#### `GetIsTalentValid(tTalent)` - Routine 359

* Returns TRUE if tTalent is valid.

**Parameters:**

- `tTalent`: `talent`

**Returns:** `int`

<a id="getattemptedattacktarget"></a>

#### `GetAttemptedAttackTarget()` - Routine 361

Get the target that the caller attempted to attack - this should be used in
conjunction with GetAttackTarget(). This value is set every time an attack is
made, and is reset at the end of combat.
* Returns OBJECT_INVALID if the caller is not a valid creature.

**Returns:** `object`

<a id="gettypefromtalent"></a>

#### `GetTypeFromTalent(tTalent)` - Routine 362

Get the type (TALENT_TYPE_*) of tTalent.

**Parameters:**

- `tTalent`: `talent`

**Returns:** `int`

<a id="getidfromtalent"></a>

#### `GetIdFromTalent(tTalent)` - Routine 363

Get the ID of tTalent.  This could be a SPELL_*, FEAT_* or SKILL_*.

**Parameters:**

- `tTalent`: `talent`

**Returns:** `int`

<a id="playpazaak"></a>

#### `PlayPazaak(sEndScript, nMaxWager, bShowTutorial=0, oOpponent=1)` - Routine 364

Starts a game of pazaak.
- nOpponentPazaakDeck: Index into PazaakDecks.2da; specifies which deck the opponent will use.
- sEndScript: Script to be run when game finishes.
- nMaxWager: Max player wager.  If <= 0, the player's credits won't be modified by the result of the game and the wager screen will not show up.
- bShowTutorial: Plays in tutorial mode (nMaxWager should be 0).

**Parameters:**

- `sEndScript`: `string`
- `nMaxWager`: `int`
- `bShowTutorial`: `int` (default: `0`)
- `oOpponent`: `object` (default: `1`)

<a id="getlastpazaakresult"></a>

#### `GetLastPazaakResult()` - Routine 365

Returns result of last Pazaak game.  Should be used only in an EndScript sent to PlayPazaak.
* Returns 0 if player loses, 1 if player wins.

**Returns:** `int`

<a id="displayfeedbacktext"></a>

#### `DisplayFeedBackText(oCreature, nTextConstant)` - Routine 366

displays a feed back string for the object spicified and the constant
repersents the string to be displayed see:FeedBackText.2da

**Parameters:**

- `oCreature`: `object`
- `nTextConstant`: `int`

<a id="addjournalquestentry"></a>

#### `AddJournalQuestEntry(szPlotID, nState, bAllowOverrideHigher=0)` - Routine 367

Add a journal quest entry to the player.
- szPlotID: the plot identifier used in the toolset's Journal Editor
- nState: the state of the plot as seen in the toolset's Journal Editor
- bAllowOverrideHigher: If this is TRUE, you can set the state to a lower
number than the one it is currently on

**Parameters:**

- `szPlotID`: `string`
- `nState`: `int`
- `bAllowOverrideHigher`: `int` (default: `0`)

<a id="removejournalquestentry"></a>

#### `RemoveJournalQuestEntry(szPlotID)` - Routine 368

Remove a journal quest entry from the player.
- szPlotID: the plot identifier used in the toolset's Journal Editor

**Parameters:**

- `szPlotID`: `string`

<a id="getjournalentry"></a>

#### `GetJournalEntry(szPlotID)` - Routine 369

Gets the State value of a journal quest.  Returns 0 if no quest entry has been added for this szPlotID.
- szPlotID: the plot identifier used in the toolset's Journal Editor

**Parameters:**

- `szPlotID`: `string`

**Returns:** `int`

<a id="playrumblepattern"></a>

#### `PlayRumblePattern(nPattern)` - Routine 370

PlayRumblePattern
Starts a defined rumble pattern playing

**Parameters:**

- `nPattern`: `int`

**Returns:** `int`

<a id="stoprumblepattern"></a>

#### `StopRumblePattern(nPattern)` - Routine 371

StopRumblePattern
Stops a defined rumble pattern

**Parameters:**

- `nPattern`: `int`

**Returns:** `int`

<a id="sendmessagetopc"></a>

#### `SendMessageToPC(oPlayer, szMessage)` - Routine 374

Send a server message (szMessage) to the oPlayer.

**Parameters:**

- `oPlayer`: `object`
- `szMessage`: `string`

<a id="getattemptedspelltarget"></a>

#### `GetAttemptedSpellTarget()` - Routine 375

Get the target at which the caller attempted to cast a spell.
This value is set every time a spell is cast and is reset at the end of
combat.
* Returns OBJECT_INVALID if the caller is not a valid creature.

**Returns:** `object`

<a id="getlastopenedby"></a>

#### `GetLastOpenedBy()` - Routine 376

Get the last creature that opened the caller.
* Returns OBJECT_INVALID if the caller is not a valid door or placeable.

**Returns:** `object`

<a id="openstore"></a>

#### `OpenStore(oStore, oPC, nBonusMarkUp=0, nBonusMarkDown=0)` - Routine 378

Open oStore for oPC.

**Parameters:**

- `oStore`: `object`
- `oPC`: `object`
- `nBonusMarkUp`: `int` (default: `0`)
- `nBonusMarkDown`: `int` (default: `0`)

<a id="getfirstfactionmember"></a>

#### `GetFirstFactionMember(oMemberOfFaction, bPCOnly=1)` - Routine 380

Get the first member of oMemberOfFaction's faction (start to cycle through
oMemberOfFaction's faction).
* Returns OBJECT_INVALID if oMemberOfFaction's faction is invalid.

**Parameters:**

- `oMemberOfFaction`: `object`
- `bPCOnly`: `int` (default: `1`)

**Returns:** `object`

<a id="getnextfactionmember"></a>

#### `GetNextFactionMember(oMemberOfFaction, bPCOnly=1)` - Routine 381

Get the next member of oMemberOfFaction's faction (continue to cycle through
oMemberOfFaction's faction).
* Returns OBJECT_INVALID if oMemberOfFaction's faction is invalid.

**Parameters:**

- `oMemberOfFaction`: `object`
- `bPCOnly`: `int` (default: `1`)

**Returns:** `object`

<a id="getjournalquestexperience"></a>

#### `GetJournalQuestExperience(szPlotID)` - Routine 384

Get the experience assigned in the journal editor for szPlotID.

**Parameters:**

- `szPlotID`: `string`

**Returns:** `int`

<a id="jumptoobject"></a>

#### `JumpToObject(oToJumpTo, nWalkStraightLineToPoint=1)` - Routine 385

Jump to oToJumpTo (the action is added to the top of the action queue).

**Parameters:**

- `oToJumpTo`: `object`
- `nWalkStraightLineToPoint`: `int` (default: `1`)

<a id="setmappinenabled"></a>

#### `SetMapPinEnabled(oMapPin, nEnabled)` - Routine 386

Set whether oMapPin is enabled.
- oMapPin
- nEnabled: 0=Off, 1=On

**Parameters:**

- `oMapPin`: `object`
- `nEnabled`: `int`

<a id="popupguipanel"></a>

#### `PopUpGUIPanel(oPC, nGUIPanel)` - Routine 388

Spawn a GUI panel for the client that controls oPC.
- oPC
- nGUIPanel: GUI_PANEL_*
* Nothing happens if oPC is not a player character or if an invalid value is
used for nGUIPanel.

**Parameters:**

- `oPC`: `object`
- `nGUIPanel`: `int`

<a id="addmulticlass"></a>

#### `AddMultiClass(nClassType, oSource)` - Routine 389

This allows you to add a new class to any creature object

**Parameters:**

- `nClassType`: `int`
- `oSource`: `object`

<a id="getislinkimmune"></a>

#### `GetIsLinkImmune(oTarget, eEffect)` - Routine 390

Tests a linked effect to see if the target is immune to it.
If the target is imune to any of the linked effect then he is immune to all of it

**Parameters:**

- `oTarget`: `object`
- `eEffect`: `effect`

**Returns:** `int`

<a id="setxp"></a>

#### `SetXP(oCreature, nXpAmount)` - Routine 394

Sets oCreature's experience to nXpAmount.

**Parameters:**

- `oCreature`: `object`
- `nXpAmount`: `int`

<a id="getxp"></a>

#### `GetXP(oCreature)` - Routine 395

Get oCreature's experience.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="inttohexstring"></a>

#### `IntToHexString(nInteger)` - Routine 396

Convert nInteger to hex, returning the hex value as a string.
* Return value has the format "0x????????" where each ? will be a hex digit
(8 digits in total).

**Parameters:**

- `nInteger`: `int`

**Returns:** `string`

<a id="getisday"></a>

#### `GetIsDay()` - Routine 405

* Returns TRUE if it is currently day.

**Returns:** `int`

<a id="getisnight"></a>

#### `GetIsNight()` - Routine 406

* Returns TRUE if it is currently night.

**Returns:** `int`

<a id="getisdawn"></a>

#### `GetIsDawn()` - Routine 407

* Returns TRUE if it is currently dawn.

**Returns:** `int`

<a id="getisdusk"></a>

#### `GetIsDusk()` - Routine 408

* Returns TRUE if it is currently dusk.

**Returns:** `int`

<a id="getisencountercreature"></a>

#### `GetIsEncounterCreature(oCreature=0)` - Routine 409

* Returns TRUE if oCreature was spawned from an encounter.

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastplayerdying"></a>

#### `GetLastPlayerDying()` - Routine 410

Use this in an OnPlayerDying module script to get the last player who is dying.

**Returns:** `object`

<a id="getstartinglocation"></a>

#### `GetStartingLocation()` - Routine 411

Get the starting location of the module.

**Returns:** `location`

<a id="changetostandardfaction"></a>

#### `ChangeToStandardFaction(oCreatureToChange, nStandardFaction)` - Routine 412

Make oCreatureToChange join one of the standard factions.
** This will only work on an NPC **
- nStandardFaction: STANDARD_FACTION_*

**Parameters:**

- `oCreatureToChange`: `object`
- `nStandardFaction`: `int`

<a id="getgold"></a>

#### `GetGold(oTarget=0)` - Routine 418

Get the amount of gold possessed by oTarget.

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastrespawnbuttonpresser"></a>

#### `GetLastRespawnButtonPresser()` - Routine 419

Use this in an OnRespawnButtonPressed module script to get the object id of
the player who last pressed the respawn button.

**Returns:** `object`

<a id="setlightsaberpowered"></a>

#### `SetLightsaberPowered(oCreature, bOverride, bPowered=1, bShowTransition=0)` - Routine 421

SetLightsaberPowered
Allows a script to set the state of the lightsaber.  This will override any
game determined lightsaber powerstates.

**Parameters:**

- `oCreature`: `object`
- `bOverride`: `int`
- `bPowered`: `int` (default: `1`)
- `bShowTransition`: `int` (default: `0`)

<a id="getisopen"></a>

#### `GetIsOpen(oObject)` - Routine 443

* Returns TRUE if oObject (which is a placeable or a door) is currently open.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="takegoldfromcreature"></a>

#### `TakeGoldFromCreature(nAmount, oCreatureToTakeFrom, bDestroy=0)` - Routine 444

Take nAmount of gold from oCreatureToTakeFrom.
- nAmount
- oCreatureToTakeFrom: If this is not a valid creature, nothing will happen.
- bDestroy: If this is TRUE, the caller will not get the gold.  Instead, the
gold will be destroyed and will vanish from the game.

**Parameters:**

- `nAmount`: `int`
- `oCreatureToTakeFrom`: `object`
- `bDestroy`: `int` (default: `0`)

<a id="setdialogplaceablecamera"></a>

#### `SetDialogPlaceableCamera(nCameraId)` - Routine 461

Cut immediately to placeable camera 'nCameraId' during dialog.  nCameraId must be
an existing Placeable Camera ID.  Function only works during Dialog.

**Parameters:**

- `nCameraId`: `int`

<a id="getsolomode"></a>

#### `GetSoloMode()` - Routine 462

Returns: TRUE if the player is in 'solo mode' (ie. the party is not supposed to follow the player).
FALSE otherwise.

**Returns:** `int`

<a id="getmaxstealthxp"></a>

#### `GetMaxStealthXP()` - Routine 464

Returns the maximum amount of stealth xp available in the area.

**Returns:** `int`

<a id="setmaxstealthxp"></a>

#### `SetMaxStealthXP(nMax)` - Routine 468

Set the maximum amount of stealth xp available in the area.

**Parameters:**

- `nMax`: `int`

<a id="getcurrentstealthxp"></a>

#### `GetCurrentStealthXP()` - Routine 474

Returns the current amount of stealth xp available in the area.

**Returns:** `int`

<a id="surrendertoenemies"></a>

#### `SurrenderToEnemies()` - Routine 476

Use this on an NPC to cause all creatures within a 10-metre radius to stop
what they are doing and sets the NPC's enemies within this range to be
neutral towards the NPC. If this command is run on a PC or an object that is
not a creature, nothing will happen.

<a id="setcurrentstealthxp"></a>

#### `SetCurrentStealthXP(nCurrent)` - Routine 478

Set the current amount of stealth xp available in the area.

**Parameters:**

- `nCurrent`: `int`

<a id="getcreaturesize"></a>

#### `GetCreatureSize(oCreature)` - Routine 479

Get the size (CREATURE_SIZE_*) of oCreature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="awardstealthxp"></a>

#### `AwardStealthXP(oTarget)` - Routine 480

Award the stealth xp to the given oTarget.  This will only work on creatures.

**Parameters:**

- `oTarget`: `object`

<a id="getstealthxpenabled"></a>

#### `GetStealthXPEnabled()` - Routine 481

Returns whether or not the stealth xp bonus is enabled (ie. whether or not
AwardStealthXP() will actually award any available stealth xp).

**Returns:** `int`

<a id="setstealthxpenabled"></a>

#### `SetStealthXPEnabled(bEnabled)` - Routine 482

Sets whether or not the stealth xp bonus is enabled (ie. whether or not
AwardStealthXP() will actually award any available stealth xp).

**Parameters:**

- `bEnabled`: `int`

<a id="getlasttrapdetected"></a>

#### `GetLastTrapDetected(oTarget=0)` - Routine 486

Get the last trap detected by oTarget.
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `object`

<a id="getnearesttraptoobject"></a>

#### `GetNearestTrapToObject(oTarget=0, nTrapDetected=1)` - Routine 488

Get the trap nearest to oTarget.
Note : "trap objects" are actually any trigger, placeable or door that is
trapped in oTarget's area.
- oTarget
- nTrapDetected: if this is TRUE, the trap returned has to have been detected
by oTarget.

**Parameters:**

- `oTarget`: `object` (default: `0`)
- `nTrapDetected`: `int` (default: `1`)

**Returns:** `object`

<a id="getattemptedmovementtarget"></a>

#### `GetAttemptedMovementTarget()` - Routine 489

the will get the last attmpted movment target

**Returns:** `object`

<a id="getblockingcreature"></a>

#### `GetBlockingCreature(oTarget=0)` - Routine 490

this function returns the bloking creature for the k_def_CBTBlk01 script

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `object`

<a id="getchallengerating"></a>

#### `GetChallengeRating(oCreature)` - Routine 494

Get oCreature's challenge rating.
* Returns 0.0 if oCreature is invalid.

**Parameters:**

- `oCreature`: `object`

**Returns:** `float`

<a id="getfoundenemycreature"></a>

#### `GetFoundEnemyCreature(oTarget=0)` - Routine 495

Returns the found enemy creature on a pathfind.

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `object`

<a id="getmovementrate"></a>

#### `GetMovementRate(oCreature)` - Routine 496

Get oCreature's movement rate.
* Returns 0 if oCreature is invalid.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="getstealthxpdecrement"></a>

#### `GetStealthXPDecrement()` - Routine 498

Returns the amount the stealth xp bonus gets decreased each time the player is detected.

**Returns:** `int`

<a id="setstealthxpdecrement"></a>

#### `SetStealthXPDecrement(nDecrement)` - Routine 499

Sets the amount the stealth xp bonus gets decreased each time the player is detected.

**Parameters:**

- `nDecrement`: `int`

<a id="duplicateheadappearance"></a>

#### `DuplicateHeadAppearance(oidCreatureToChange, oidCreatureToMatch)` - Routine 500

**Parameters:**

- `oidCreatureToChange`: `object`
- `oidCreatureToMatch`: `object`

<a id="cutsceneattack"></a>

#### `CutsceneAttack(oTarget, nAnimation, nAttackResult, nDamage)` - Routine 503

CutsceneAttack
This function allows the designer to specify exactly what's going to happen in a combat round
There are no guarentees made that the animation specified here will be correct - only that it will be played,
so it is up to the designer to ensure that they have selected the right animation
It relies upon constants specified above for the attack result

**Parameters:**

- `oTarget`: `object`
- `nAnimation`: `int`
- `nAttackResult`: `int`
- `nDamage`: `int`

<a id="setlockorientationindialog"></a>

#### `SetLockOrientationInDialog(oObject, nValue)` - Routine 505

SetLockOrientationInDialog
Allows the locking and unlocking of orientation changes for an object in dialog
- oObject - Object
- nValue - TRUE or FALSE

**Parameters:**

- `oObject`: `object`
- `nValue`: `int`

<a id="setlockheadfollowindialog"></a>

#### `SetLockHeadFollowInDialog(oObject, nValue)` - Routine 506

SetLockHeadFollowInDialog
Allows the locking and undlocking of head following for an object in dialog
- oObject - Object
- nValue - TRUE or FALSE

**Parameters:**

- `oObject`: `object`
- `nValue`: `int`

<a id="cutscenemove"></a>

#### `CutsceneMove(oObject, vPosition, nRun)` - Routine 507

CutsceneMoveToPoint
Used by the cutscene system to allow designers to script combat

**Parameters:**

- `oObject`: `object`
- `vPosition`: `vector`
- `nRun`: `int`

<a id="enablevideoeffect"></a>

#### `EnableVideoEffect(nEffectType)` - Routine 508

EnableVideoEffect
Enables the video frame buffer effect specified by nEffectType, which is
an index into VideoEffects.2da. This video effect will apply indefinitely,
and so it should *always* be cleared by a call to DisableVideoEffect().

**Parameters:**

- `nEffectType`: `int`

<a id="disablevideoeffect"></a>

#### `DisableVideoEffect()` - Routine 508

EnableVideoEffect
Enables the video frame buffer effect specified by nEffectType, which is
an index into VideoEffects.2da. This video effect will apply indefinitely,
and so it should *always* be cleared by a call to DisableVideoEffect().

<a id="startnewmodule"></a>

#### `StartNewModule(sModuleName, sWayPoint=, sMovie1=, sMovie2=, sMovie3=, sMovie4=, sMovie5=, sMovie6=)` - Routine 509

Shut down the currently loaded module and start a new one (moving all
currently-connected players to the starting point.

**Parameters:**

- `sModuleName`: `string`
- `sWayPoint`: `string` (default: ``)
- `sMovie1`: `string` (default: ``)
- `sMovie2`: `string` (default: ``)
- `sMovie3`: `string` (default: ``)
- `sMovie4`: `string` (default: ``)
- `sMovie5`: `string` (default: ``)
- `sMovie6`: `string` (default: ``)

<a id="dosingleplayerautosave"></a>

#### `DoSinglePlayerAutoSave()` - Routine 512

Only if we are in a single player game, AutoSave the game.

<a id="getgamedifficulty"></a>

#### `GetGameDifficulty()` - Routine 513

Get the game difficulty (GAME_DIFFICULTY_*).

**Returns:** `int`

<a id="getuseractionspending"></a>

#### `GetUserActionsPending()` - Routine 514

This will test the combat action queu to see if the user has placed any actions on the queue.
will only work during combat.

**Returns:** `int`

<a id="revealmap"></a>

#### `RevealMap(vPoint=0.0 0.0 0.0, nRadius=-1)` - Routine 515

RevealMap
Reveals the map at the given WORLD point 'vPoint' with a MAP Grid Radius 'nRadius'
If this function is called with no parameters it will reveal the entire map.
(NOTE: if this function is called with a valid point but a default radius, ie. 'nRadius' of -1
then the entire map will be revealed)

**Parameters:**

- `vPoint`: `vector` (default: `0.0 0.0 0.0`)
- `nRadius`: `int` (default: `-1`)

<a id="settutorialwindowsenabled"></a>

#### `SetTutorialWindowsEnabled(bEnabled)` - Routine 516

SetTutorialWindowsEnabled
Sets whether or not the tutorial windows are enabled (ie. whether or not they will
appear when certain things happen for the first time).

**Parameters:**

- `bEnabled`: `int`

<a id="showtutorialwindow"></a>

#### `ShowTutorialWindow(nWindow)` - Routine 517

ShowTutorialWindow
Pops up the specified tutorial window.  If the tutorial window has already popped
up once before, this will do nothing.

**Parameters:**

- `nWindow`: `int`

<a id="startcreditsequence"></a>

#### `StartCreditSequence(bTransparentBackground)` - Routine 518

StartCreditSequence
Starts the credits sequence.  If bTransparentBackground is TRUE, the credits will be displayed
with a transparent background, allowing whatever is currently onscreen to show through.  If it
is set to FALSE, the credits will be displayed on a black background.

**Parameters:**

- `bTransparentBackground`: `int`

<a id="iscreditsequenceinprogress"></a>

#### `IsCreditSequenceInProgress()` - Routine 519

IsCreditSequenceInProgress
Returns TRUE if the credits sequence is currently in progress, FALSE otherwise.

**Returns:** `int`

<a id="swmg_setlateralaccelerationpersecond"></a>

#### `SWMG_SetLateralAccelerationPerSecond(fLAPS)` - Routine 520

Sets the minigame lateral acceleration/sec value

**Parameters:**

- `fLAPS`: `float`

<a id="swmg_getlateralaccelerationpersecond"></a>

#### `SWMG_GetLateralAccelerationPerSecond()` - Routine 521

Returns the minigame lateral acceleration/sec value

**Returns:** `float`

<a id="getdifficultymodifier"></a>

#### `GetDifficultyModifier()` - Routine 523

**Returns:** `float`

<a id="getappearancetype"></a>

#### `GetAppearanceType(oCreature)` - Routine 524

Returns the appearance type of oCreature (0 if creature doesn't exist)
- oCreature

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="floatingtextstrrefoncreature"></a>

#### `FloatingTextStrRefOnCreature(nStrRefToDisplay, oCreatureToFloatAbove, bBroadcastToFaction=1)` - Routine 525

Display floaty text above the specified creature.
The text will also appear in the chat buffer of each player that receives the
floaty text.
- nStrRefToDisplay: String ref (therefore text is translated)
- oCreatureToFloatAbove
- bBroadcastToFaction: If this is TRUE then only creatures in the same faction
as oCreatureToFloatAbove
will see the floaty text, and only if they are within range (30 metres).

**Parameters:**

- `nStrRefToDisplay`: `int`
- `oCreatureToFloatAbove`: `object`
- `bBroadcastToFaction`: `int` (default: `1`)

<a id="floatingtextstringoncreature"></a>

#### `FloatingTextStringOnCreature(sStringToDisplay, oCreatureToFloatAbove, bBroadcastToFaction=1)` - Routine 526

Display floaty text above the specified creature.
The text will also appear in the chat buffer of each player that receives the
floaty text.
- sStringToDisplay: String
- oCreatureToFloatAbove
- bBroadcastToFaction: If this is TRUE then only creatures in the same faction
as oCreatureToFloatAbove
will see the floaty text, and only if they are within range (30 metres).

**Parameters:**

- `sStringToDisplay`: `string`
- `oCreatureToFloatAbove`: `object`
- `bBroadcastToFaction`: `int` (default: `1`)

<a id="gettrapdisarmable"></a>

#### `GetTrapDisarmable(oTrapObject)` - Routine 527

- oTrapObject: a placeable, door or trigger
* Returns TRUE if oTrapObject is disarmable.

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="gettrapdetectable"></a>

#### `GetTrapDetectable(oTrapObject)` - Routine 528

- oTrapObject: a placeable, door or trigger
* Returns TRUE if oTrapObject is detectable.

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="gettrapdetectedby"></a>

#### `GetTrapDetectedBy(oTrapObject, oCreature)` - Routine 529

- oTrapObject: a placeable, door or trigger
- oCreature
* Returns TRUE if oCreature has detected oTrapObject

**Parameters:**

- `oTrapObject`: `object`
- `oCreature`: `object`

**Returns:** `int`

<a id="gettrapflagged"></a>

#### `GetTrapFlagged(oTrapObject)` - Routine 530

- oTrapObject: a placeable, door or trigger
* Returns TRUE if oTrapObject has been flagged as visible to all creatures.

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="gettrapbasetype"></a>

#### `GetTrapBaseType(oTrapObject)` - Routine 531

Get the trap base type (TRAP_BASE_TYPE_*) of oTrapObject.
- oTrapObject: a placeable, door or trigger

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="gettraponeshot"></a>

#### `GetTrapOneShot(oTrapObject)` - Routine 532

- oTrapObject: a placeable, door or trigger
* Returns TRUE if oTrapObject is one-shot (i.e. it does not reset itself
after firing.

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="gettrapcreator"></a>

#### `GetTrapCreator(oTrapObject)` - Routine 533

Get the creator of oTrapObject, the creature that set the trap.
- oTrapObject: a placeable, door or trigger
* Returns OBJECT_INVALID if oTrapObject was created in the toolset.

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `object`

<a id="gettrapkeytag"></a>

#### `GetTrapKeyTag(oTrapObject)` - Routine 534

Get the tag of the key that will disarm oTrapObject.
- oTrapObject: a placeable, door or trigger

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `string`

<a id="gettrapdisarmdc"></a>

#### `GetTrapDisarmDC(oTrapObject)` - Routine 535

Get the DC for disarming oTrapObject.
- oTrapObject: a placeable, door or trigger

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="gettrapdetectdc"></a>

#### `GetTrapDetectDC(oTrapObject)` - Routine 536

Get the DC for detecting oTrapObject.
- oTrapObject: a placeable, door or trigger

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="getlockkeyrequired"></a>

#### `GetLockKeyRequired(oObject)` - Routine 537

* Returns TRUE if a specific key is required to open the lock on oObject.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getlockkeytag"></a>

#### `GetLockKeyTag(oObject)` - Routine 538

Get the tag of the key that will open the lock on oObject.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getlocklockable"></a>

#### `GetLockLockable(oObject)` - Routine 539

* Returns TRUE if the lock on oObject is lockable.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getlockunlockdc"></a>

#### `GetLockUnlockDC(oObject)` - Routine 540

Get the DC for unlocking oObject.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getlocklockdc"></a>

#### `GetLockLockDC(oObject)` - Routine 541

Get the DC for locking oObject.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getpclevellingup"></a>

#### `GetPCLevellingUp()` - Routine 542

Get the last PC that levelled up.

**Returns:** `object`

<a id="setplaceableillumination"></a>

#### `SetPlaceableIllumination(oPlaceable=0, bIlluminate=1)` - Routine 544

Set the status of the illumination for oPlaceable.
- oPlaceable
- bIlluminate: if this is TRUE, oPlaceable's illumination will be turned on.
If this is FALSE, oPlaceable's illumination will be turned off.
Note: You must call RecomputeStaticLighting() after calling this function in
order for the changes to occur visually for the players.
SetPlaceableIllumination() buffers the illumination changes, which are then

**Parameters:**

- `oPlaceable`: `object` (default: `0`)
- `bIlluminate`: `int` (default: `1`)

<a id="getplaceableillumination"></a>

#### `GetPlaceableIllumination(oPlaceable=0)` - Routine 545

* Returns TRUE if the illumination for oPlaceable is on

**Parameters:**

- `oPlaceable`: `object` (default: `0`)

**Returns:** `int`

<a id="getisplaceableobjectactionpossible"></a>

#### `GetIsPlaceableObjectActionPossible(oPlaceable, nPlaceableAction)` - Routine 546

- oPlaceable
- nPlaceableAction: PLACEABLE_ACTION_*
* Returns TRUE if nPlacebleAction is valid for oPlaceable.

**Parameters:**

- `oPlaceable`: `object`
- `nPlaceableAction`: `int`

**Returns:** `int`

<a id="doplaceableobjectaction"></a>

#### `DoPlaceableObjectAction(oPlaceable, nPlaceableAction)` - Routine 547

The caller performs nPlaceableAction on oPlaceable.
- oPlaceable
- nPlaceableAction: PLACEABLE_ACTION_*

**Parameters:**

- `oPlaceable`: `object`
- `nPlaceableAction`: `int`

<a id="getfirstpc"></a>

#### `GetFirstPC()` - Routine 548

Get the first PC in the player list.
This resets the position in the player list for GetNextPC().

**Returns:** `object`

<a id="getnextpc"></a>

#### `GetNextPC()` - Routine 548

Get the first PC in the player list.
This resets the position in the player list for GetNextPC().

**Returns:** `object`

<a id="settrapdetectedby"></a>

#### `SetTrapDetectedBy(oTrap, oDetector)` - Routine 550

Set oDetector to have detected oTrap.

**Parameters:**

- `oTrap`: `object`
- `oDetector`: `object`

**Returns:** `int`

<a id="getistrapped"></a>

#### `GetIsTrapped(oObject)` - Routine 551

Note: Only placeables, doors and triggers can be trapped.
* Returns TRUE if oObject is trapped.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="seteffecticon"></a>

#### `SetEffectIcon(eEffect, nIcon)` - Routine 552

SetEffectIcon
This will link the specified effect icon to the specified effect.  The
effect returned will contain the link to the effect icon and applying this
effect will cause an effect icon to appear on the portrait/charsheet gui.
eEffect: The effect which should cause the effect icon to appear.
nIcon: Index into effecticon.2da of the effect icon to use.

**Parameters:**

- `eEffect`: `effect`
- `nIcon`: `int`

**Returns:** `effect`

<a id="faceobjectawayfromobject"></a>

#### `FaceObjectAwayFromObject(oFacer, oObjectToFaceAwayFrom)` - Routine 553

FaceObjectAwayFromObject
This will cause the object oFacer to face away from oObjectToFaceAwayFrom.
The objects must be in the same area for this to work.

**Parameters:**

- `oFacer`: `object`
- `oObjectToFaceAwayFrom`: `object`

<a id="popupdeathguipanel"></a>

#### `PopUpDeathGUIPanel(oPC, bRespawnButtonEnabled=1, bWaitForHelpButtonEnabled=1, nHelpStringReference=0, sHelpString=)` - Routine 554

Spawn in the Death GUI.
The default (as defined by BioWare) can be spawned in by PopUpGUIPanel, but
if you want to turn off the "Respawn" or "Wait for Help" buttons, this is the
function to use.
- oPC
- bRespawnButtonEnabled: if this is TRUE, the "Respawn" button will be enabled
on the Death GUI.
- bWaitForHelpButtonEnabled: if this is TRUE, the "Wait For Help" button will
be enabled on the Death GUI.
- nHelpStringReference
- sHelpString

**Parameters:**

- `oPC`: `object`
- `bRespawnButtonEnabled`: `int` (default: `1`)
- `bWaitForHelpButtonEnabled`: `int` (default: `1`)
- `nHelpStringReference`: `int` (default: `0`)
- `sHelpString`: `string` (default: ``)

<a id="settrapdisabled"></a>

#### `SetTrapDisabled(oTrap)` - Routine 555

Disable oTrap.
- oTrap: a placeable, door or trigger.

**Parameters:**

- `oTrap`: `object`

<a id="exportallcharacters"></a>

#### `ExportAllCharacters()` - Routine 557

Force all the characters of the players who are currently in the game to
be exported to their respective directories i.e. LocalVault/ServerVault/ etc.

<a id="writetimestampedlogentry"></a>

#### `WriteTimestampedLogEntry(sLogEntry)` - Routine 560

Write sLogEntry as a timestamped entry into the log file

**Parameters:**

- `sLogEntry`: `string`

<a id="getfactionleader"></a>

#### `GetFactionLeader(oMemberOfFaction)` - Routine 562

Get the leader of the faction of which oMemberOfFaction is a member.
* Returns OBJECT_INVALID if oMemberOfFaction is not a valid creature.

**Parameters:**

- `oMemberOfFaction`: `object`

**Returns:** `object`

<a id="swmg_setspeedblureffect"></a>

#### `SWMG_SetSpeedBlurEffect(bEnabled, fRatio=0.75)` - Routine 563

Turns on or off the speed blur effect in rendered scenes.
bEnabled: Set TRUE to turn it on, FALSE to turn it off.
fRatio: Sets the frame accumulation ratio.

**Parameters:**

- `bEnabled`: `int`
- `fRatio`: `float` (default: `0.75`)

<a id="endgame"></a>

#### `EndGame(nShowEndGameGui=1)` - Routine 564

Immediately ends the currently running game and returns to the start screen.
nShowEndGameGui: Set TRUE to display the death gui.

**Parameters:**

- `nShowEndGameGui`: `int` (default: `1`)

<a id="getrunscriptvar"></a>

#### `GetRunScriptVar()` - Routine 565

Get a variable passed when calling console debug runscript

**Returns:** `int`

<a id="getcreaturemovmenttype"></a>

#### `GetCreatureMovmentType(oidCreature)` - Routine 566

This function returns a value that matches one of the MOVEMENT_SPEED_... constants
if the OID passed in is not found or not a creature then it will return
MOVEMENT_SPEED_IMMOBILE.

**Parameters:**

- `oidCreature`: `object`

**Returns:** `int`

<a id="gethasinventory"></a>

#### `GetHasInventory(oObject)` - Routine 570

Determine whether oObject has an inventory.
* Returns TRUE for creatures and stores, and checks to see if an item or placeable object is a container.
* Returns FALSE for all other object types.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getstrrefsoundduration"></a>

#### `GetStrRefSoundDuration(nStrRef)` - Routine 571

Get the duration (in seconds) of the sound attached to nStrRef
* Returns 0.0f if no duration is stored or if no sound is attached

**Parameters:**

- `nStrRef`: `int`

**Returns:** `float`

<a id="addtoparty"></a>

#### `AddToParty(oPC, oPartyLeader)` - Routine 572

Add oPC to oPartyLeader's party.  This will only work on two PCs.
- oPC: player to add to a party
- oPartyLeader: player already in the party

**Parameters:**

- `oPC`: `object`
- `oPartyLeader`: `object`

<a id="removefromparty"></a>

#### `RemoveFromParty(oPC)` - Routine 573

Remove oPC from their current party. This will only work on a PC.
- oPC: removes this player from whatever party they're currently in.

**Parameters:**

- `oPC`: `object`

<a id="swmg_getlastevent"></a>

#### `SWMG_GetLastEvent()` - Routine 583

OnAnimKey
get the event and the name of the model on which the event happened
SWMG_GetLastEvent

**Returns:** `string`

<a id="swmg_getlasteventmodelname"></a>

#### `SWMG_GetLastEventModelName()` - Routine 584

SWMG_GetLastEventModelName

**Returns:** `string`

<a id="swmg_getobjectbyname"></a>

#### `SWMG_GetObjectByName(sName)` - Routine 585

gets an object by its name (duh!)
SWMG_GetObjectByName

**Parameters:**

- `sName`: `string`

**Returns:** `object`

<a id="swmg_playanimation"></a>

#### `SWMG_PlayAnimation(oObject, sAnimName, bLooping=1, bQueue=0, bOverlay=0)` - Routine 586

plays an animation on an object
SWMG_PlayAnimation

**Parameters:**

- `oObject`: `object`
- `sAnimName`: `string`
- `bLooping`: `int` (default: `1`)
- `bQueue`: `int` (default: `0`)
- `bOverlay`: `int` (default: `0`)

<a id="swmg_getlastbullethitdamage"></a>

#### `SWMG_GetLastBulletHitDamage()` - Routine 587

OnHitBullet
get the damage, the target type (see TARGETflags), and the shooter
SWMG_GetLastBulletHitDamage

**Returns:** `int`

<a id="swmg_getlastbullethittarget"></a>

#### `SWMG_GetLastBulletHitTarget()` - Routine 588

SWMG_GetLastBulletHitTarget

**Returns:** `int`

<a id="swmg_getlastbullethitshooter"></a>

#### `SWMG_GetLastBulletHitShooter()` - Routine 589

SWMG_GetLastBulletHitShooter

**Returns:** `object`

<a id="swmg_onbullethit"></a>

#### `SWMG_OnBulletHit()` - Routine 591

the default implementation of OnBulletHit
SWMG_OnBulletHit

<a id="swmg_onobstaclehit"></a>

#### `SWMG_OnObstacleHit()` - Routine 592

the default implementation of OnObstacleHit
SWMG_OnObstacleHit

<a id="swmg_getlastfollowerhit"></a>

#### `SWMG_GetLastFollowerHit()` - Routine 593

returns the last follower and obstacle hit
SWMG_GetLastFollowerHit

**Returns:** `object`

<a id="swmg_getlastobstaclehit"></a>

#### `SWMG_GetLastObstacleHit()` - Routine 594

SWMG_GetLastObstacleHit

**Returns:** `object`

<a id="swmg_getlastbulletfireddamage"></a>

#### `SWMG_GetLastBulletFiredDamage()` - Routine 595

gets information about the last bullet fired
SWMG_GetLastBulletFiredDamage

**Returns:** `int`

<a id="swmg_getlastbulletfiredtarget"></a>

#### `SWMG_GetLastBulletFiredTarget()` - Routine 596

SWMG_GetLastBulletFiredTarget

**Returns:** `int`

<a id="swmg_getobjectname"></a>

#### `SWMG_GetObjectName(oid=0)` - Routine 597

gets an objects name
SWMG_GetObjectName

**Parameters:**

- `oid`: `object` (default: `0`)

**Returns:** `string`

<a id="swmg_ondeath"></a>

#### `SWMG_OnDeath()` - Routine 598

the default implementation of OnDeath
SWMG_OnDeath

<a id="swmg_isfollower"></a>

#### `SWMG_IsFollower(oid=0)` - Routine 599

a bunch of Is functions for your pleasure
SWMG_IsFollower

**Parameters:**

- `oid`: `object` (default: `0`)

**Returns:** `int`

<a id="swmg_isplayer"></a>

#### `SWMG_IsPlayer(oid=0)` - Routine 600

SWMG_IsPlayer

**Parameters:**

- `oid`: `object` (default: `0`)

**Returns:** `int`

<a id="swmg_isenemy"></a>

#### `SWMG_IsEnemy(oid=0)` - Routine 601

SWMG_IsEnemy

**Parameters:**

- `oid`: `object` (default: `0`)

**Returns:** `int`

<a id="swmg_istrigger"></a>

#### `SWMG_IsTrigger(oid=0)` - Routine 602

SWMG_IsTrigger

**Parameters:**

- `oid`: `object` (default: `0`)

**Returns:** `int`

<a id="swmg_isobstacle"></a>

#### `SWMG_IsObstacle(oid=0)` - Routine 603

SWMG_IsObstacle

**Parameters:**

- `oid`: `object` (default: `0`)

**Returns:** `int`

<a id="swmg_ondamage"></a>

#### `SWMG_OnDamage()` - Routine 605

SWMG_OnDamage

<a id="swmg_getlasthpchange"></a>

#### `SWMG_GetLastHPChange()` - Routine 606

SWMG_GetLastHPChange

**Returns:** `int`

<a id="swmg_removeanimation"></a>

#### `SWMG_RemoveAnimation(oObject, sAnimName)` - Routine 607

SWMG_RemoveAnimation

**Parameters:**

- `oObject`: `object`
- `sAnimName`: `string`

<a id="swmg_getcameranearclip"></a>

#### `SWMG_GetCameraNearClip()` - Routine 608

SWMG_GetCameraNearClip

**Returns:** `float`

<a id="swmg_getcamerafarclip"></a>

#### `SWMG_GetCameraFarClip()` - Routine 609

SWMG_GetCameraFarClip

**Returns:** `float`

<a id="swmg_setcameraclip"></a>

#### `SWMG_SetCameraClip(fNear, fFar)` - Routine 610

SWMG_SetCameraClip

**Parameters:**

- `fNear`: `float`
- `fFar`: `float`

<a id="swmg_getplayer"></a>

#### `SWMG_GetPlayer()` - Routine 611

SWMG_GetPlayer

**Returns:** `object`

<a id="swmg_getenemycount"></a>

#### `SWMG_GetEnemyCount()` - Routine 612

SWMG_GetEnemyCount

**Returns:** `int`

<a id="swmg_getenemy"></a>

#### `SWMG_GetEnemy(nEntry)` - Routine 613

SWMG_GetEnemy

**Parameters:**

- `nEntry`: `int`

**Returns:** `object`

<a id="swmg_getobstaclecount"></a>

#### `SWMG_GetObstacleCount()` - Routine 614

SWMG_GetObstacleCount

**Returns:** `int`

<a id="swmg_getobstacle"></a>

#### `SWMG_GetObstacle(nEntry)` - Routine 615

SWMG_GetObstacle

**Parameters:**

- `nEntry`: `int`

**Returns:** `object`

<a id="swmg_getsphereradius"></a>

#### `SWMG_GetSphereRadius(oFollower)` - Routine 619

SWMG_GetSphereRadius

**Parameters:**

- `oFollower`: `object`

**Returns:** `float`

<a id="swmg_setsphereradius"></a>

#### `SWMG_SetSphereRadius(oFollower, fRadius)` - Routine 620

SWMG_SetSphereRadius

**Parameters:**

- `oFollower`: `object`
- `fRadius`: `float`

<a id="swmg_getnumloops"></a>

#### `SWMG_GetNumLoops(oFollower)` - Routine 621

SWMG_GetNumLoops

**Parameters:**

- `oFollower`: `object`

**Returns:** `int`

<a id="swmg_setnumloops"></a>

#### `SWMG_SetNumLoops(oFollower, nNumLoops)` - Routine 622

SWMG_SetNumLoops

**Parameters:**

- `oFollower`: `object`
- `nNumLoops`: `int`

<a id="swmg_getposition"></a>

#### `SWMG_GetPosition(oFollower)` - Routine 623

SWMG_GetPosition

**Parameters:**

- `oFollower`: `object`

**Returns:** `vector`

<a id="swmg_getgunbankcount"></a>

#### `SWMG_GetGunBankCount(oFollower)` - Routine 624

SWMG_GetGunBankCount

**Parameters:**

- `oFollower`: `object`

**Returns:** `int`

<a id="swmg_getgunbankbulletmodel"></a>

#### `SWMG_GetGunBankBulletModel(oFollower, nGunBank)` - Routine 625

SWMG_GetGunBankBulletModel

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `string`

<a id="swmg_getgunbankgunmodel"></a>

#### `SWMG_GetGunBankGunModel(oFollower, nGunBank)` - Routine 626

SWMG_GetGunBankGunModel

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `string`

<a id="swmg_getgunbankdamage"></a>

#### `SWMG_GetGunBankDamage(oFollower, nGunBank)` - Routine 627

SWMG_GetGunBankDamage

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `int`

<a id="swmg_getgunbanktimebetweenshots"></a>

#### `SWMG_GetGunBankTimeBetweenShots(oFollower, nGunBank)` - Routine 628

SWMG_GetGunBankTimeBetweenShots

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_getgunbanklifespan"></a>

#### `SWMG_GetGunBankLifespan(oFollower, nGunBank)` - Routine 629

SWMG_GetGunBankLifespan

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_getgunbankspeed"></a>

#### `SWMG_GetGunBankSpeed(oFollower, nGunBank)` - Routine 630

SWMG_GetGunBankSpeed

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_getgunbanktarget"></a>

#### `SWMG_GetGunBankTarget(oFollower, nGunBank)` - Routine 631

SWMG_GetGunBankTarget

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `int`

<a id="swmg_setgunbankbulletmodel"></a>

#### `SWMG_SetGunBankBulletModel(oFollower, nGunBank, sBulletModel)` - Routine 632

SWMG_SetGunBankBulletModel

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `sBulletModel`: `string`

<a id="swmg_setgunbankgunmodel"></a>

#### `SWMG_SetGunBankGunModel(oFollower, nGunBank, sGunModel)` - Routine 633

SWMG_SetGunBankGunModel

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `sGunModel`: `string`

<a id="swmg_setgunbankdamage"></a>

#### `SWMG_SetGunBankDamage(oFollower, nGunBank, nDamage)` - Routine 634

SWMG_SetGunBankDamage

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `nDamage`: `int`

<a id="swmg_setgunbanktimebetweenshots"></a>

#### `SWMG_SetGunBankTimeBetweenShots(oFollower, nGunBank, fTBS)` - Routine 635

SWMG_SetGunBankTimeBetweenShots

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `fTBS`: `float`

<a id="swmg_setgunbanklifespan"></a>

#### `SWMG_SetGunBankLifespan(oFollower, nGunBank, fLifespan)` - Routine 636

SWMG_SetGunBankLifespan

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `fLifespan`: `float`

<a id="swmg_setgunbankspeed"></a>

#### `SWMG_SetGunBankSpeed(oFollower, nGunBank, fSpeed)` - Routine 637

SWMG_SetGunBankSpeed

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `fSpeed`: `float`

<a id="swmg_setgunbanktarget"></a>

#### `SWMG_SetGunBankTarget(oFollower, nGunBank, nTarget)` - Routine 638

SWMG_SetGunBankTarget

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `nTarget`: `int`

<a id="swmg_getlastbullethitpart"></a>

#### `SWMG_GetLastBulletHitPart()` - Routine 639

SWMG_GetLastBulletHitPart

**Returns:** `string`

<a id="swmg_isgunbanktargetting"></a>

#### `SWMG_IsGunBankTargetting(oFollower, nGunBank)` - Routine 640

SWMG_IsGunBankTargetting

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `int`

<a id="swmg_getplayeroffset"></a>

#### `SWMG_GetPlayerOffset()` - Routine 641

SWMG_GetPlayerOffset
returns a vector with the player rotation for rotation minigames
returns a vector with the player translation for translation minigames

**Returns:** `vector`

<a id="swmg_getplayerinvincibility"></a>

#### `SWMG_GetPlayerInvincibility()` - Routine 642

SWMG_GetPlayerInvincibility

**Returns:** `float`

<a id="swmg_getplayerspeed"></a>

#### `SWMG_GetPlayerSpeed()` - Routine 643

SWMG_GetPlayerSpeed

**Returns:** `float`

<a id="swmg_getplayerminspeed"></a>

#### `SWMG_GetPlayerMinSpeed()` - Routine 644

SWMG_GetPlayerMinSpeed

**Returns:** `float`

<a id="swmg_getplayeraccelerationpersecond"></a>

#### `SWMG_GetPlayerAccelerationPerSecond()` - Routine 645

SWMG_GetPlayerAccelerationPerSecond

**Returns:** `float`

<a id="swmg_getplayertunnelpos"></a>

#### `SWMG_GetPlayerTunnelPos()` - Routine 646

SWMG_GetPlayerTunnelPos

**Returns:** `vector`

<a id="swmg_setplayeroffset"></a>

#### `SWMG_SetPlayerOffset(vOffset)` - Routine 647

SWMG_SetPlayerOffset

**Parameters:**

- `vOffset`: `vector`

<a id="swmg_setplayerinvincibility"></a>

#### `SWMG_SetPlayerInvincibility(fInvincibility)` - Routine 648

SWMG_SetPlayerInvincibility

**Parameters:**

- `fInvincibility`: `float`

<a id="swmg_setplayerspeed"></a>

#### `SWMG_SetPlayerSpeed(fSpeed)` - Routine 649

SWMG_SetPlayerSpeed

**Parameters:**

- `fSpeed`: `float`

<a id="swmg_setplayerminspeed"></a>

#### `SWMG_SetPlayerMinSpeed(fMinSpeed)` - Routine 650

SWMG_SetPlayerMinSpeed

**Parameters:**

- `fMinSpeed`: `float`

<a id="swmg_setplayeraccelerationpersecond"></a>

#### `SWMG_SetPlayerAccelerationPerSecond(fAPS)` - Routine 651

SWMG_SetPlayerAccelerationPerSecond

**Parameters:**

- `fAPS`: `float`

<a id="swmg_setplayertunnelpos"></a>

#### `SWMG_SetPlayerTunnelPos(vTunnel)` - Routine 652

SWMG_SetPlayerTunnelPos

**Parameters:**

- `vTunnel`: `vector`

<a id="swmg_getplayertunnelneg"></a>

#### `SWMG_GetPlayerTunnelNeg()` - Routine 653

SWMG_GetPlayerTunnelNeg

**Returns:** `vector`

<a id="swmg_setplayertunnelneg"></a>

#### `SWMG_SetPlayerTunnelNeg(vTunnel)` - Routine 654

SWMG_SetPlayerTunnelNeg

**Parameters:**

- `vTunnel`: `vector`

<a id="swmg_getplayerorigin"></a>

#### `SWMG_GetPlayerOrigin()` - Routine 655

SWMG_GetPlayerOrigin

**Returns:** `vector`

<a id="swmg_setplayerorigin"></a>

#### `SWMG_SetPlayerOrigin(vOrigin)` - Routine 656

SWMG_SetPlayerOrigin

**Parameters:**

- `vOrigin`: `vector`

<a id="swmg_getgunbankhorizontalspread"></a>

#### `SWMG_GetGunBankHorizontalSpread(oEnemy, nGunBank)` - Routine 657

SWMG_GetGunBankHorizontalSpread

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_getgunbankverticalspread"></a>

#### `SWMG_GetGunBankVerticalSpread(oEnemy, nGunBank)` - Routine 658

SWMG_GetGunBankVerticalSpread

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_getgunbanksensingradius"></a>

#### `SWMG_GetGunBankSensingRadius(oEnemy, nGunBank)` - Routine 659

SWMG_GetGunBankSensingRadius

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_getgunbankinaccuracy"></a>

#### `SWMG_GetGunBankInaccuracy(oEnemy, nGunBank)` - Routine 660

SWMG_GetGunBankInaccuracy

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_setgunbankhorizontalspread"></a>

#### `SWMG_SetGunBankHorizontalSpread(oEnemy, nGunBank, fHorizontalSpread)` - Routine 661

SWMG_SetGunBankHorizontalSpread

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`
- `fHorizontalSpread`: `float`

<a id="swmg_setgunbankverticalspread"></a>

#### `SWMG_SetGunBankVerticalSpread(oEnemy, nGunBank, fVerticalSpread)` - Routine 662

SWMG_SetGunBankVerticalSpread

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`
- `fVerticalSpread`: `float`

<a id="swmg_setgunbanksensingradius"></a>

#### `SWMG_SetGunBankSensingRadius(oEnemy, nGunBank, fSensingRadius)` - Routine 663

SWMG_SetGunBankSensingRadius

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`
- `fSensingRadius`: `float`

<a id="swmg_setgunbankinaccuracy"></a>

#### `SWMG_SetGunBankInaccuracy(oEnemy, nGunBank, fInaccuracy)` - Routine 664

SWMG_SetGunBankInaccuracy

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`
- `fInaccuracy`: `float`

<a id="swmg_getisinvulnerable"></a>

#### `SWMG_GetIsInvulnerable(oFollower)` - Routine 665

GetIsInvulnerable
This returns whether the follower object is currently invulnerable to damage

**Parameters:**

- `oFollower`: `object`

**Returns:** `int`

<a id="swmg_startinvulnerability"></a>

#### `SWMG_StartInvulnerability(oFollower)` - Routine 666

StartInvulnerability
This will begin a period of invulnerability (as defined by Invincibility)

**Parameters:**

- `oFollower`: `object`

<a id="swmg_getplayermaxspeed"></a>

#### `SWMG_GetPlayerMaxSpeed()` - Routine 667

GetPlayerMaxSpeed
This returns the player character's max speed

**Returns:** `float`

<a id="swmg_setplayermaxspeed"></a>

#### `SWMG_SetPlayerMaxSpeed(fMaxSpeed)` - Routine 668

SetPlayerMaxSpeed
This sets the player character's max speed

**Parameters:**

- `fMaxSpeed`: `float`

<a id="addjournalworldentry"></a>

#### `AddJournalWorldEntry(nIndex, szEntry, szTitle=World Entry)` - Routine 669

AddJournalWorldEntry
Adds a user entered entry to the world notices

**Parameters:**

- `nIndex`: `int`
- `szEntry`: `string`
- `szTitle`: `string` (default: `World Entry`)

<a id="addjournalworldentrystrref"></a>

#### `AddJournalWorldEntryStrref(strref, strrefTitle)` - Routine 670

AddJournalWorldEntryStrref
Adds an entry to the world notices using stringrefs

**Parameters:**

- `strref`: `int`
- `strrefTitle`: `int`

<a id="barkstring"></a>

#### `BarkString(oCreature, strRef)` - Routine 671

BarkString
this will cause a creature to bark the strRef from the talk table
If creature is specefied as OBJECT_INVALID a general bark is made.

**Parameters:**

- `oCreature`: `object`
- `strRef`: `int`

<a id="deletejournalworldallentries"></a>

#### `DeleteJournalWorldAllEntries()` - Routine 672

DeleteJournalWorldAllEntries
Nuke's 'em all, user entered or otherwise.

<a id="deletejournalworldentry"></a>

#### `DeleteJournalWorldEntry(nIndex)` - Routine 673

DeleteJournalWorldEntry
Deletes a user entered world notice

**Parameters:**

- `nIndex`: `int`

<a id="deletejournalworldentrystrref"></a>

#### `DeleteJournalWorldEntryStrref(strref)` - Routine 674

DeleteJournalWorldEntryStrref
Deletes the world notice pertaining to the string ref

**Parameters:**

- `strref`: `int`

<a id="playvisualareaeffect"></a>

#### `PlayVisualAreaEffect(nEffectID, lTarget)` - Routine 677

PlayVisualAreaEffect

**Parameters:**

- `nEffectID`: `int`
- `lTarget`: `location`

<a id="setjournalquestentrypicture"></a>

#### `SetJournalQuestEntryPicture(szPlotID, oObject, nPictureIndex, bAllPartyMemebers=1, bAllPlayers=0)` - Routine 678

SetJournalQuestEntryPicture
Sets the picture for the quest entry on this object (creature)

**Parameters:**

- `szPlotID`: `string`
- `oObject`: `object`
- `nPictureIndex`: `int`
- `bAllPartyMemebers`: `int` (default: `1`)
- `bAllPlayers`: `int` (default: `0`)

<a id="setnpcselectability"></a>

#### `SetNPCSelectability(nNPC, nSelectability)` - Routine 708

SetNPCSelectability

**Parameters:**

- `nNPC`: `int`
- `nSelectability`: `int`

<a id="getnpcselectability"></a>

#### `GetNPCSelectability(nNPC)` - Routine 709

GetNPCSelectability

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="clearalleffects"></a>

#### `ClearAllEffects()` - Routine 710

Clear all the effects of the caller.
* No return value, but if an error occurs, the log file will contain
"ClearAllEffects failed.".

<a id="getstandardfaction"></a>

#### `GetStandardFaction(oObject)` - Routine 713

GetStandardFaction
Find out which standard faction oObject belongs to.
* Returns INVALID_STANDARD_FACTION if oObject does not belong to
a Standard Faction, or an error has occurred.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="giveplotxp"></a>

#### `GivePlotXP(sPlotName, nPercentage)` - Routine 714

GivePlotXP
Give nPercentage% of the experience associated with plot sPlotName
to the party
- sPlotName
- nPercentage

**Parameters:**

- `sPlotName`: `string`
- `nPercentage`: `int`

<a id="getcategoryfromtalent"></a>

#### `GetCategoryFromTalent(tTalent)` - Routine 735

Get the Category of tTalent.

**Parameters:**

- `tTalent`: `talent`

**Returns:** `int`

<a id="surrenderbyfaction"></a>

#### `SurrenderByFaction(nFactionFrom, nFactionTo)` - Routine 736

This affects all creatures in the area that are in faction nFactionFrom...
- Makes them join nFactionTo
- Clears all actions
- Disables combat mode

**Parameters:**

- `nFactionFrom`: `int`
- `nFactionTo`: `int`

<a id="changefactionbyfaction"></a>

#### `ChangeFactionByFaction(nFactionFrom, nFactionTo)` - Routine 737

This affects all creatures in the area that are in faction nFactionFrom.
making them change to nFactionTo

**Parameters:**

- `nFactionFrom`: `int`
- `nFactionTo`: `int`

<a id="playroomanimation"></a>

#### `PlayRoomAnimation(sRoom, nAnimation)` - Routine 738

PlayRoomAnimation
Plays a looping animation on a room

**Parameters:**

- `sRoom`: `string`
- `nAnimation`: `int`

<a id="showgalaxymap"></a>

#### `ShowGalaxyMap(nPlanet)` - Routine 739

ShowGalaxyMap
Brings up the Galaxy Map Gui, with 'nPlanet' selected.  'nPlanet' can only be a planet
that has already been set available and selectable.

**Parameters:**

- `nPlanet`: `int`

<a id="setplanetselectable"></a>

#### `SetPlanetSelectable(nPlanet, bSelectable)` - Routine 740

SetPlanetSelectable
Sets 'nPlanet' selectable on the Galaxy Map Gui.

**Parameters:**

- `nPlanet`: `int`
- `bSelectable`: `int`

<a id="getplanetselectable"></a>

#### `GetPlanetSelectable(nPlanet)` - Routine 741

GetPlanetSelectable
Returns wheter or not 'nPlanet' is selectable.

**Parameters:**

- `nPlanet`: `int`

**Returns:** `int`

<a id="setplanetavailable"></a>

#### `SetPlanetAvailable(nPlanet, bAvailable)` - Routine 742

SetPlanetAvailable
Sets 'nPlanet' available on the Galaxy Map Gui.

**Parameters:**

- `nPlanet`: `int`
- `bAvailable`: `int`

<a id="getplanetavailable"></a>

#### `GetPlanetAvailable(nPlanet)` - Routine 743

GetPlanetAvailable
Returns wheter or not 'nPlanet' is available.

**Parameters:**

- `nPlanet`: `int`

**Returns:** `int`

<a id="getselectedplanet"></a>

#### `GetSelectedPlanet()` - Routine 744

GetSelectedPlanet
Returns the ID of the currently selected planet.  Check Planetary.2da
for which planet the return value corresponds to. If the return is -1
no planet is selected.

**Returns:** `int`

<a id="setareafogcolor"></a>

#### `SetAreaFogColor(oArea, fRed, fGreen, fBlue)` - Routine 746

SetAreaFogColor
Set the fog color for the area oArea.

**Parameters:**

- `oArea`: `object`
- `fRed`: `float`
- `fGreen`: `float`
- `fBlue`: `float`

<a id="getislivecontentavailable"></a>

#### `GetIsLiveContentAvailable(nPkg)` - Routine 748

GetIsLiveContentAvailable
Determines whether a given live content package is available
nPkg = LIVE_CONTENT_PKG1, LIVE_CONTENT_PKG2, ..., LIVE_CONTENT_PKG6

**Parameters:**

- `nPkg`: `int`

**Returns:** `int`

<a id="resetdialogstate"></a>

#### `ResetDialogState()` - Routine 749

ResetDialogState
Resets the GlobalDialogState for the engine.
NOTE: NEVER USE THIS UNLESS YOU KNOW WHAT ITS FOR!
only to be used for a failing OnDialog script

<a id="getispoisoned"></a>

#### `GetIsPoisoned(oObject)` - Routine 751

GetIsPoisoned
Returns TRUE if the object specified is poisoned.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getspelltarget"></a>

#### `GetSpellTarget(oCreature=0)` - Routine 752

GetSpellTarget
Returns the object id of the spell target

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `object`

<a id="setsolomode"></a>

#### `SetSoloMode(bActivate)` - Routine 753

SetSoloMode
Activates/Deactivates solo mode for the player's party.

**Parameters:**

- `bActivate`: `int`

<a id="cancelpostdialogcharacterswitch"></a>

#### `CancelPostDialogCharacterSwitch()` - Routine 757

<a id="noclicksfor"></a>

#### `NoClicksFor(fDuration)` - Routine 759

**Parameters:**

- `fDuration`: `float`

<a id="holdworldfadeinfordialog"></a>

#### `HoldWorldFadeInForDialog()` - Routine 760

<a id="shipbuild"></a>

#### `ShipBuild()` - Routine 761

**Returns:** `int`

<a id="surrenderretainbuffs"></a>

#### `SurrenderRetainBuffs()` - Routine 762

<a id="getfirstinpersistentobject"></a>

#### `GetFirstInPersistentObject(oPersistentObject=0, nResidentObjectType=1, nPersistentZone=0)`

These are for GetFirstInPersistentObject() and GetNextInPersistentObject()

**Parameters:**

- `oPersistentObject`: `object` (default: `0`)
- `nResidentObjectType`: `int` (default: `1`)
- `nPersistentZone`: `int` (default: `0`)

**Returns:** `object`

<a id="getnextinpersistentobject"></a>

#### `GetNextInPersistentObject(oPersistentObject=0, nResidentObjectType=1, nPersistentZone=0)`

These are for GetFirstInPersistentObject() and GetNextInPersistentObject()

**Parameters:**

- `oPersistentObject`: `object` (default: `0`)
- `nResidentObjectType`: `int` (default: `1`)
- `nPersistentZone`: `int` (default: `0`)

**Returns:** `object`

<a id="aurpoststring"></a>

#### `AurPostString(sString, nX, nY, fLife)`

post a string to the screen at column nX and row nY for fLife seconds
582. AurPostString

**Parameters:**

- `sString`: `string`
- `nX`: `int`
- `nY`: `int`
- `fLife`: `float`

<a id="swmg_getsoundfrequency"></a>

#### `SWMG_GetSoundFrequency(oFollower, nSound)`

683. SWMG_GetSoundFrequency
Gets the frequency of a trackfollower sound

**Parameters:**

- `oFollower`: `object`
- `nSound`: `int`

**Returns:** `int`

<a id="swmg_setsoundfrequency"></a>

#### `SWMG_SetSoundFrequency(oFollower, nSound, nFrequency)`

684. SWMG_SetSoundFrequency
Sets the frequency of a trackfollower sound

**Parameters:**

- `oFollower`: `object`
- `nSound`: `int`
- `nFrequency`: `int`

<a id="swmg_getsoundfrequencyisrandom"></a>

#### `SWMG_GetSoundFrequencyIsRandom(oFollower, nSound)`

685. SWMG_GetSoundFrequencyIsRandom
Gets whether the frequency of a trackfollower sound is using the random model

**Parameters:**

- `oFollower`: `object`
- `nSound`: `int`

**Returns:** `int`

<a id="swmg_setsoundfrequencyisrandom"></a>

#### `SWMG_SetSoundFrequencyIsRandom(oFollower, nSound, bIsRandom)`

686. SWMG_SetSoundFrequencyIsRandom
Sets whether the frequency of a trackfollower sound is using the random model

**Parameters:**

- `oFollower`: `object`
- `nSound`: `int`
- `bIsRandom`: `int`

<a id="swmg_getsoundvolume"></a>

#### `SWMG_GetSoundVolume(oFollower, nSound)`

687. SWMG_GetSoundVolume
Gets the volume of a trackfollower sound

**Parameters:**

- `oFollower`: `object`
- `nSound`: `int`

**Returns:** `int`

<a id="swmg_setsoundvolume"></a>

#### `SWMG_SetSoundVolume(oFollower, nSound, nVolume)`

688. SWMG_SetSoundVolume
Sets the volume of a trackfollower sound

**Parameters:**

- `oFollower`: `object`
- `nSound`: `int`
- `nVolume`: `int`

<a id="isavailablecreature"></a>

#### `IsAvailableCreature(nNPC)`

696. IsAvailableNPC
This returns whether a NPC is in the list of available party members

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="getnpcaistyle"></a>

#### `GetNPCAIStyle(oCreature)`

705.
Returns the party members ai style

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="setnpcaistyle"></a>

#### `SetNPCAIStyle(oCreature, nStyle)`

707.
Sets the party members ai style

**Parameters:**

- `oCreature`: `object`
- `nStyle`: `int`

<a id="getminonehp"></a>

#### `GetMinOneHP(oObject)`

715. GetMinOneHP
Checks to see if oObject has the MinOneHP Flag set on them.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="setminonehp"></a>

#### `SetMinOneHP(oObject, nMinOneHP)`

716. SetMinOneHP
Sets/Removes the MinOneHP Flag on oObject.

**Parameters:**

- `oObject`: `object`
- `nMinOneHP`: `int`

<a id="swmg_getplayertunnelinfinite"></a>

#### `SWMG_GetPlayerTunnelInfinite()`

717. SWMG_GetPlayerTunnelInfinite
Gets whether each of the dimensions is infinite

**Returns:** `vector`

<a id="swmg_setplayertunnelinfinite"></a>

#### `SWMG_SetPlayerTunnelInfinite(vInfinite)`

718. SWMG_SetPlayerTunnelInfinite
Sets whether each of the dimensions is infinite

**Parameters:**

- `vInfinite`: `vector`

<a id="getlasthostiletarget"></a>

#### `GetLastHostileTarget(oAttacker=0)`

721. GetLastAttackTarget
Returns the last attack target for a given object

**Parameters:**

- `oAttacker`: `object` (default: `0`)

**Returns:** `object`

<a id="getlastattackaction"></a>

#### `GetLastAttackAction(oAttacker=0)`

722. GetLastAttackAction
Returns the last attack action for a given object

**Parameters:**

- `oAttacker`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastforcepowerused"></a>

#### `GetLastForcePowerUsed(oAttacker=0)`

723. GetLastForcePowerUsed
Returns the last force power used (as a spell number that indexes the Spells.2da) by the given object

**Parameters:**

- `oAttacker`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastcombatfeatused"></a>

#### `GetLastCombatFeatUsed(oAttacker=0)`

724. GetLastCombatFeatUsed
Returns the last feat used (as a feat number that indexes the Feats.2da) by the given object

**Parameters:**

- `oAttacker`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastattackresult"></a>

#### `GetLastAttackResult(oAttacker=0)`

725. GetLastAttackResult
Returns the result of the last attack

**Parameters:**

- `oAttacker`: `object` (default: `0`)

**Returns:** `int`

<a id="getwasforcepowersuccessful"></a>

#### `GetWasForcePowerSuccessful(oAttacker=0)`

726. GetWasForcePowerSuccessful
Returns whether the last force power used was successful or not

**Parameters:**

- `oAttacker`: `object` (default: `0`)

**Returns:** `int`

<a id="getfirstattacker"></a>

#### `GetFirstAttacker(oCreature=0)`

727. GetFirstAttacker
Returns the first object in the area that is attacking oCreature

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `object`

<a id="getnextattacker"></a>

#### `GetNextAttacker(oCreature=0)`

728. GetNextAttacker
Returns the next object in the area that is attacking oCreature

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `object`

<a id="setformation"></a>

#### `SetFormation(oAnchor, oCreature, nFormationPattern, nPosition)`

729. SetFormation
Put oCreature into the nFormationPattern about oAnchor at position nPosition
- oAnchor: The formation is set relative to this object
- oCreature: This is the creature that you wish to join the formation
- nFormationPattern: FORMATION_*
- nPosition: Integer from 1 to 10 to specify which position in the formation
oCreature is supposed to take.

**Parameters:**

- `oAnchor`: `object`
- `oCreature`: `object`
- `nFormationPattern`: `int`
- `nPosition`: `int`

<a id="setforcepowerunsuccessful"></a>

#### `SetForcePowerUnsuccessful(nResult, oCreature=0)`

731. SetForcePowerUnsuccessful
Sets the reason (through a constant) for why a force power failed

**Parameters:**

- `nResult`: `int`
- `oCreature`: `object` (default: `0`)

<a id="getisdebilitated"></a>

#### `GetIsDebilitated(oCreature=0)`

732. GetIsDebilitated
Returns whether the given object is debilitated or not

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="playmovie"></a>

#### `PlayMovie(sMovie)`

733. PlayMovie
Playes a Movie.

**Parameters:**

- `sMovie`: `string`

<a id="savenpcstate"></a>

#### `SaveNPCState(nNPC)`

734. SaveNPCState
Tells the party table to save the state of a party member NPC

**Parameters:**

- `nNPC`: `int`

<a id="suppressstatussummaryentry"></a>

#### `SuppressStatusSummaryEntry(nNumEntries=1)`

763. SuppressStatusSummaryEntry
This will prevent the next n entries that should have shown up in the status summary
from being added
This will not add on to any existing summary suppressions, but rather replace it.  So
to clear the supression system pass 0 as the entry value

**Parameters:**

- `nNumEntries`: `int` (default: `1`)

<a id="getcheatcode"></a>

#### `GetCheatCode(nCode)`

764. GetCheatCode
Returns true if cheat code has been enabled

**Parameters:**

- `nCode`: `int`

**Returns:** `int`

<a id="setmusicvolume"></a>

#### `SetMusicVolume(fVolume=1.0)`

765. SetMusicVolume
NEVER USE THIS!

**Parameters:**

- `fVolume`: `float` (default: `1.0`)

<a id="ismovieplaying"></a>

#### `IsMoviePlaying()`

768. IsMoviePlaying
Checks if a movie is currently playing.

**Returns:** `int`

<a id="queuemovie"></a>

#### `QueueMovie(sMovie, bSkippable)`

769. QueueMovie
Queues up a movie to be played using PlayMovieQueue.
If bSkippable is TRUE, the player can cancel the movie by hitting escape.
If bSkippable is FALSE, the player cannot cancel the movie and must wait
for it to finish playing.

**Parameters:**

- `sMovie`: `string`
- `bSkippable`: `int`

<a id="playmoviequeue"></a>

#### `PlayMovieQueue(bAllowSeparateSkips)`

770. PlayMovieQueue
Plays the movies that have been added to the queue by QueueMovie
If bAllowSeparateSkips is TRUE, hitting escape to cancel a movie only
cancels out of the currently playing movie rather than the entire queue
of movies (assuming the currently playing movie is flagged as skippable).
If bAllowSeparateSkips is FALSE, the entire movie queue will be cancelled
if the player hits escape (assuming the currently playing movie is flagged
as skippable).

**Parameters:**

- `bAllowSeparateSkips`: `int`

<a id="yavinhackclosedoor"></a>

#### `YavinHackCloseDoor(oidDoor)`

771. YavinHackCloseDoor
This is an incredibly hacky function to allow the doors to be properly
closed on Yavin without running into the problems we've had.  It is too
late in development to fix it correctly, so thus we do this.  Life is
hard.  You'll get over it

**Parameters:**

- `oidDoor`: `object`
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

<a id="setplayerrestrictmode"></a>

#### `SetPlayerRestrictMode(bRestrict)` - Routine 58

SetPlayerRestrictMode
Sets whether the player is currently in 'restricted' mode

**Parameters:**

- `bRestrict`: `int`

<a id="getplayerrestrictmode"></a>

#### `GetPlayerRestrictMode(oObject=0)` - Routine 83

GetPlayerRestrictMode
returns the current player 'restricted' mode

**Parameters:**

- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getispc"></a>

#### `GetIsPC(oCreature)` - Routine 217

* Returns TRUE if oCreature is a Player Controlled character.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="getpcspeaker"></a>

#### `GetPCSpeaker()` - Routine 238

Get the PC that is involved in the conversation.
* Returns OBJECT_INVALID on error.

**Returns:** `object`

<a id="getgender"></a>

#### `GetGender(oCreature)` - Routine 358

Get the gender of oCreature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="givexptocreature"></a>

#### `GiveXPToCreature(oCreature, nXpAmount)` - Routine 393

Gives nXpAmount to oCreature.

**Parameters:**

- `oCreature`: `object`
- `nXpAmount`: `int`

<a id="getplotflag"></a>

#### `GetPlotFlag(oTarget=0)` - Routine 455

Determine whether oTarget is a plot object.

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `int`

<a id="setplotflag"></a>

#### `SetPlotFlag(oTarget, nPlotFlag)` - Routine 456

Set oTarget's plot object status.

**Parameters:**

- `oTarget`: `object`
- `nPlotFlag`: `int`

<a id="getsubrace"></a>

#### `GetSubRace(oCreature)` - Routine 497

GetSubRace of oCreature
Returns SUBRACE_*

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="setcameramode"></a>

#### `SetCameraMode(oPlayer, nCameraMode)` - Routine 504

Set the camera mode for oPlayer.
- oPlayer
- nCameraMode: CAMERA_MODE_*
* If oPlayer is not player-controlled or nCameraMode is invalid, nothing
happens.

**Parameters:**

- `oPlayer`: `object`
- `nCameraMode`: `int`
### Skills and Feats

<a id="getlastspellcaster"></a>

#### `GetLastSpellCaster()` - Routine 245

This is for use in a "Spell Cast" script, it gets who cast the spell.
The spell could have been cast by a creature, placeable or door.
* Returns OBJECT_INVALID if the caller is not a creature, placeable or door.

**Returns:** `object`

<a id="getlastspell"></a>

#### `GetLastSpell()` - Routine 246

This is for use in a "Spell Cast" script, it gets the ID of the spell that
was cast.

**Returns:** `int`

<a id="gethasfeat"></a>

#### `GetHasFeat(nFeat, oCreature=0)` - Routine 285

Determine whether oCreature has nFeat, and nFeat is useable.
- nFeat: FEAT_*
- oCreature

**Parameters:**

- `nFeat`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="gethasskill"></a>

#### `GetHasSkill(nSkill, oCreature=0)` - Routine 286

Determine whether oCreature has nSkill, and nSkill is useable.
- nSkill: SKILL_*
- oCreature

**Parameters:**

- `nSkill`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getskillrank"></a>

#### `GetSkillRank(nSkill, oTarget=0)` - Routine 315

Get the number of ranks that oTarget has in nSkill.
- nSkill: SKILL_*
- oTarget
* Returns -1 if oTarget doesn't have nSkill.
* Returns 0 if nSkill is untrained.

**Parameters:**

- `nSkill`: `int`
- `oTarget`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastspellharmful"></a>

#### `GetLastSpellHarmful()` - Routine 423

Use this in a SpellCast script to determine whether the spell was considered
harmful.
* Returns TRUE if the last spell cast was harmful.

**Returns:** `int`

<a id="gethasfeateffect"></a>

#### `GetHasFeatEffect(nFeat, oObject=0)` - Routine 543

- nFeat: FEAT_*
- oObject
* Returns TRUE if oObject has effects on it originating from nFeat.

**Parameters:**

- `nFeat`: `int`
- `oObject`: `object` (default: `0`)

**Returns:** `int`
### Sound and Music Functions

<a id="playsound"></a>

#### `PlaySound(sSoundName)` - Routine 46

Play sSoundName
- sSoundName: TBD - SS

**Parameters:**

- `sSoundName`: `string`

<a id="soundobjectplay"></a>

#### `SoundObjectPlay(oSound)` - Routine 413

Play oSound.

**Parameters:**

- `oSound`: `object`

<a id="soundobjectstop"></a>

#### `SoundObjectStop(oSound)` - Routine 414

Stop playing oSound.

**Parameters:**

- `oSound`: `object`

<a id="soundobjectsetvolume"></a>

#### `SoundObjectSetVolume(oSound, nVolume)` - Routine 415

Set the volume of oSound.
- oSound
- nVolume: 0-127

**Parameters:**

- `oSound`: `object`
- `nVolume`: `int`

<a id="soundobjectsetposition"></a>

#### `SoundObjectSetPosition(oSound, vPosition)` - Routine 416

Set the position of oSound.

**Parameters:**

- `oSound`: `object`
- `vPosition`: `vector`

<a id="musicbackgroundplay"></a>

#### `MusicBackgroundPlay(oArea)` - Routine 425

Play the background music for oArea.

**Parameters:**

- `oArea`: `object`

<a id="musicbackgroundstop"></a>

#### `MusicBackgroundStop(oArea)` - Routine 426

Stop the background music for oArea.

**Parameters:**

- `oArea`: `object`

<a id="musicbackgroundsetdelay"></a>

#### `MusicBackgroundSetDelay(oArea, nDelay)` - Routine 427

Set the delay for the background music for oArea.
- oArea
- nDelay: delay in milliseconds

**Parameters:**

- `oArea`: `object`
- `nDelay`: `int`

<a id="musicbackgroundchangeday"></a>

#### `MusicBackgroundChangeDay(oArea, nTrack)` - Routine 428

Change the background day track for oArea to nTrack.
- oArea
- nTrack

**Parameters:**

- `oArea`: `object`
- `nTrack`: `int`

<a id="musicbackgroundchangenight"></a>

#### `MusicBackgroundChangeNight(oArea, nTrack)` - Routine 429

Change the background night track for oArea to nTrack.
- oArea
- nTrack

**Parameters:**

- `oArea`: `object`
- `nTrack`: `int`

<a id="musicbattleplay"></a>

#### `MusicBattlePlay(oArea)` - Routine 430

Play the battle music for oArea.

**Parameters:**

- `oArea`: `object`

<a id="musicbattlestop"></a>

#### `MusicBattleStop(oArea)` - Routine 431

Stop the battle music for oArea.

**Parameters:**

- `oArea`: `object`

<a id="musicbattlechange"></a>

#### `MusicBattleChange(oArea, nTrack)` - Routine 432

Change the battle track for oArea.
- oArea
- nTrack

**Parameters:**

- `oArea`: `object`
- `nTrack`: `int`

<a id="ambientsoundplay"></a>

#### `AmbientSoundPlay(oArea)` - Routine 433

Play the ambient sound for oArea.

**Parameters:**

- `oArea`: `object`

<a id="ambientsoundstop"></a>

#### `AmbientSoundStop(oArea)` - Routine 434

Stop the ambient sound for oArea.

**Parameters:**

- `oArea`: `object`

<a id="ambientsoundchangeday"></a>

#### `AmbientSoundChangeDay(oArea, nTrack)` - Routine 435

Change the ambient day track for oArea to nTrack.
- oArea
- nTrack

**Parameters:**

- `oArea`: `object`
- `nTrack`: `int`

<a id="ambientsoundchangenight"></a>

#### `AmbientSoundChangeNight(oArea, nTrack)` - Routine 436

Change the ambient night track for oArea to nTrack.
- oArea
- nTrack

**Parameters:**

- `oArea`: `object`
- `nTrack`: `int`

<a id="musicbackgroundgetdaytrack"></a>

#### `MusicBackgroundGetDayTrack(oArea)` - Routine 558

Get the Day Track for oArea.

**Parameters:**

- `oArea`: `object`

**Returns:** `int`

<a id="musicbackgroundgetnighttrack"></a>

#### `MusicBackgroundGetNightTrack(oArea)` - Routine 559

Get the Night Track for oArea.

**Parameters:**

- `oArea`: `object`

**Returns:** `int`

<a id="ambientsoundsetdayvolume"></a>

#### `AmbientSoundSetDayVolume(oArea, nVolume)` - Routine 567

Set the ambient day volume for oArea to nVolume.
- oArea
- nVolume: 0 - 100

**Parameters:**

- `oArea`: `object`
- `nVolume`: `int`

<a id="ambientsoundsetnightvolume"></a>

#### `AmbientSoundSetNightVolume(oArea, nVolume)` - Routine 568

Set the ambient night volume for oArea to nVolume.
- oArea
- nVolume: 0 - 100

**Parameters:**

- `oArea`: `object`
- `nVolume`: `int`

<a id="musicbackgroundgetbattletrack"></a>

#### `MusicBackgroundGetBattleTrack(oArea)` - Routine 569

Get the Battle Track for oArea.

**Parameters:**

- `oArea`: `object`

**Returns:** `int`

<a id="soundobjectfadeandstop"></a>

#### `SoundObjectFadeAndStop(oSound, fSeconds)` - Routine 745

SoundObjectFadeAndStop
Fades a sound object for 'fSeconds' and then stops it.

**Parameters:**

- `oSound`: `object`
- `fSeconds`: `float`

<a id="soundobjectsetfixedvariance"></a>

#### `SoundObjectSetFixedVariance(oSound, fFixedVariance)`

124. SoundObjectSetFixedVariance
Sets the constant variance at which to play the sound object
This variance is a multiplier of the original sound

**Parameters:**

- `oSound`: `object`
- `fFixedVariance`: `float`

<a id="soundobjectgetfixedvariance"></a>

#### `SoundObjectGetFixedVariance(oSound)`

188. SoundObjectGetFixedVariance
Gets the constant variance at which to play the sound object

**Parameters:**

- `oSound`: `object`

**Returns:** `float`

<a id="soundobjectgetpitchvariance"></a>

#### `SoundObjectGetPitchVariance(oSound)`

689. SoundObjectGetPitchVariance
Gets the pitch variance of a placeable sound object

**Parameters:**

- `oSound`: `object`

**Returns:** `float`

<a id="soundobjectsetpitchvariance"></a>

#### `SoundObjectSetPitchVariance(oSound, fVariance)`

690. SoundObjectSetPitchVariance
Sets the pitch variance of a placeable sound object

**Parameters:**

- `oSound`: `object`
- `fVariance`: `float`

<a id="soundobjectgetvolume"></a>

#### `SoundObjectGetVolume(oSound)`

691. SoundObjectGetVolume
Gets the volume of a placeable sound object

**Parameters:**

- `oSound`: `object`

**Returns:** `int`
## K1-Only Functions

<!-- K1_ONLY_FUNCTIONS_START -->

### Other Functions

<a id="yavinhackclosedoor"></a>

#### `YavinHackCloseDoor(oidDoor)`

771. YavinHackCloseDoor
This is an incredibly hacky function to allow the doors to be properly
closed on Yavin without running into the problems we've had.  It is too
late in development to fix it correctly, so thus we do this.  Life is
hard.  You'll get over it

**Parameters:**

- `oidDoor`: `object`
## TSL-Only Functions

<!-- TSL_ONLY_FUNCTIONS_START -->

### Actions

<a id="actionfollowowner"></a>

#### `ActionFollowOwner(fRange=2.5)`

843
RWT-OEI 07/20/04
Similiar to ActionFollowLeader() except the creature
follows its owner
nRange is how close it should follow. Note that once this
action is queued, it will be the only thing this creature
does until a ClearAllActions() is used.

**Parameters:**

- `fRange`: `float` (default: `2.5`)

<a id="actionswitchweapons"></a>

#### `ActionSwitchWeapons()`

853
ActionSwitchWeapons
Forces the creature to switch between Config 1 and Config 2
of their equipment. Does not work in dialogs. Works with
### Class System

*No functions in this category.*
### Combat Functions

*No functions in this category.*
### Dialog and Conversation Functions

*No functions in this category.*
### Effects System

<a id="effectforcebody"></a>

#### `EffectForceBody(nLevel)`

DJS-OEI 12/15/2003
Create a Force Body effect
- nLevel: The level of the Force Body effect.
0 = Force Body
1 = Improved Force Body
2 = Master Force Body

**Parameters:**

- `nLevel`: `int`

**Returns:** `effect`

<a id="effectfury"></a>

#### `EffectFury()`

DJS-OEI 1/2/2004
Create a Fury effect.

**Returns:** `effect`

<a id="effectblind"></a>

#### `EffectBlind()`

DJS-OEI 1/3/2004
Create a Blind effect.

**Returns:** `effect`

<a id="effectfpregenmodifier"></a>

#### `EffectFPRegenModifier(nPercent)`

DJS-OEI 1/4/2004
Create an FP regeneration modifier effect.

**Parameters:**

- `nPercent`: `int`

**Returns:** `effect`

<a id="effectvpregenmodifier"></a>

#### `EffectVPRegenModifier(nPercent)`

DJS-OEI 1/4/2004
Create a VP regeneration modifier effect.

**Parameters:**

- `nPercent`: `int`

**Returns:** `effect`

<a id="effectcrush"></a>

#### `EffectCrush()`

DJS-OEI 1/9/2004
Create a Force Crush effect.

**Returns:** `effect`

<a id="effectdroidconfused"></a>

#### `EffectDroidConfused()`

809
new function for droid confusion so inherint mind immunity can be
avoided.

**Returns:** `effect`

<a id="effectforcesight"></a>

#### `EffectForceSight()`

823
DJS-OEI 5/5/2004
Creates a Force Sight effect.

**Returns:** `effect`

<a id="effectmindtrick"></a>

#### `EffectMindTrick()`

848
Create a Mind Trick effect

**Returns:** `effect`

<a id="effectfactionmodifier"></a>

#### `EffectFactionModifier(nNewFaction)`

849
Create a Faction Modifier effect.

**Parameters:**

- `nNewFaction`: `int`

**Returns:** `effect`

<a id="effectdroidscramble"></a>

#### `EffectDroidScramble()`

852
Create a Droid Scramble effect

**Returns:** `effect`
### Global Variables

*No functions in this category.*
### Item Management

<a id="getitemcomponent"></a>

#### `GetItemComponent()`

FAK-OEI 12/15/2003
Get the number of components for an item

**Returns:** `int`

<a id="getitemcomponentpiecevalue"></a>

#### `GetItemComponentPieceValue()`

FAK-OEI 12/15/2003
Get the number of components for an item in pieces

**Returns:** `int`
### Object Query and Manipulation

<a id="removeeffectbyid"></a>

#### `RemoveEffectByID(oCreature, nEffectID)`

867
JF-OEI 10-07-2004
Remove an effect by ID

**Parameters:**

- `oCreature`: `object`
- `nEffectID`: `int`

<a id="removeeffectbyexactmatch"></a>

#### `RemoveEffectByExactMatch(oCreature, eEffect)`

868
RWT-OEI 10/07/04
This script removes an effect by an identical match
based on:
Must have matching EffectID types.
Must have the same value in Integer(0)
Must have the same value in Integer(1)
I'm specifically using this function for Mandalore's implant swapping
script and it will probably not be useful for anyone else. If you're
not sure what this script function does, see me before using it.

**Parameters:**

- `oCreature`: `object`
- `eEffect`: `effect`
### Other Functions

<a id="getfeatacquired"></a>

#### `GetFeatAcquired(nFeat, oCreature=0)` - Routine 285

Determine whether oCreature has nFeat, and nFeat is useable.
PLEASE NOTE!!! - This function will return FALSE if the target
is not currently able to use the feat due to daily limits or
other restrictions. Use GetFeatAcquired() if you just want to

**Parameters:**

- `nFeat`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getspellacquired"></a>

#### `GetSpellAcquired(nSpell, oCreature=0)` - Routine 377

Determine whether oCreature has nSpell memorised.
PLEASE NOTE!!! - This function will return FALSE if the target
is not currently able to use the spell due to lack of sufficient
Force Points. Use GetSpellAcquired() if you just want to

**Parameters:**

- `nSpell`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getscriptparameter"></a>

#### `GetScriptParameter(nIndex)`

DJS-OEI
768. GetScriptParameter
This function will take the index of a script parameter
and return the value associated with it. The index
of the first parameter is 1.

**Parameters:**

- `nIndex`: `int`

**Returns:** `int`

<a id="setfadeuntilscript"></a>

#### `SetFadeUntilScript()`

RWT-OEI 12/10/03
769. SetFadeUntilScript
This script function will make it so that the fade cannot be lifted under any circumstances
other than a call to the SetGlobalFadeIn() script.
This function should be called AFTER the fade has already been called. For example, you would
do a SetGlobalFadeOut() first, THEN do SetFadeUntilScript()

<a id="showchemicalupgradescreen"></a>

#### `ShowChemicalUpgradeScreen(oCharacter)`

FAK-OEI 12/15/2003
Start the GUI for Chemical Workshop

**Parameters:**

- `oCharacter`: `object`

<a id="getchemicals"></a>

#### `GetChemicals()`

FAK-OEI 12/15/2003
Get the number of chemicals for an item

**Returns:** `int`

<a id="getchemicalpiecevalue"></a>

#### `GetChemicalPieceValue()`

FAK-OEI 12/15/2003
Get the number of chemicals for an item in pieces

**Returns:** `int`

<a id="getspellforcepointcost"></a>

#### `GetSpellForcePointCost()`

DJS-OEI 12/30/2003
Get the number of Force Points that were required to
cast this spell. This includes modifiers such as Room Force
Ratings and the Force Body power.
* Return value on error: 0

**Returns:** `int`

<a id="swmg_getswoopupgrade"></a>

#### `SWMG_GetSwoopUpgrade(nSlot)`

FAK - OEI 1/12/04
Minigame grabs a swoop bike upgrade

**Parameters:**

- `nSlot`: `int`

**Returns:** `int`

<a id="showswoopupgradescreen"></a>

#### `ShowSwoopUpgradeScreen()`

FAK-OEI 1/12/2004
Displays the Swoop Bike upgrade screen.

<a id="grantfeat"></a>

#### `GrantFeat(nFeat, oCreature)`

DJS-OEI 1/13/2004
Grants the target a feat without regard for prerequisites.

**Parameters:**

- `nFeat`: `int`
- `oCreature`: `object`

<a id="grantspell"></a>

#### `GrantSpell(nSpell, oCreature)`

DJS-OEI 1/13/2004
Grants the target a spell without regard for prerequisites.

**Parameters:**

- `nSpell`: `int`
- `oCreature`: `object`

<a id="spawnmine"></a>

#### `SpawnMine(nMineType, lPoint, nDetectDCBase, nDisarmDCBase, oCreator)`

DJS-OEI 1/13/2004
Places an active mine on the map.
nMineType - Mine Type from Traps.2DA
lPoint - The location in the world to place the mine.
nDetectDCBase - This value, plus the "DetectDCMod" column in Traps.2DA
results in the final DC for creatures to detect this mine.
nDisarmDCBase - This value, plus the "DisarmDCMod" column in Traps.2DA
results in the final DC for creatures to disarm this mine.
oCreator - The object that should be considered the owner of the mine.
If oCreator is set to OBJECT_INVALID, the faction of the mine will be
considered Hostile1, meaning the party will be vulnerable to it.

**Parameters:**

- `nMineType`: `int`
- `lPoint`: `location`
- `nDetectDCBase`: `int`
- `nDisarmDCBase`: `int`
- `oCreator`: `object`

<a id="swmg_gettrackposition"></a>

#### `SWMG_GetTrackPosition(oFollower)`

FAK - OEI 1/15/04
Yet another minigame function. Returns the object's track's position.

**Parameters:**

- `oFollower`: `object`

**Returns:** `vector`

<a id="swmg_setfollowerposition"></a>

#### `SWMG_SetFollowerPosition(vPos)`

FAK - OEI 1/15/04
minigame function that lets you psuedo-set the position of a follower object

**Parameters:**

- `vPos`: `vector`

**Returns:** `vector`

<a id="setfakecombatstate"></a>

#### `SetFakeCombatState(oObject, nEnable)`

RWT-OEI 01/16/04
A function to put the character into a true combat state but the reason set to
not real combat. This should help us control animations in cutscenes with a bit
more precision. -- Not totally sure this is doing anything just yet. Seems
the combat condition gets cleared shortly after anyway.
If nEnable is 1, it enables fake combat mode. If 0, it disables it.
WARNING: Whenever using this function to enable fake combat mode, you should
have a matching call to it to disable it. (pass 0 for nEnable).

**Parameters:**

- `oObject`: `object`
- `nEnable`: `int`

<a id="swmg_destroyminigameobject"></a>

#### `SWMG_DestroyMiniGameObject(oObject)`

FAK - OEI 1/23/04
minigame function that deletes a minigame object

**Parameters:**

- `oObject`: `object`

<a id="getownerdemolitionsskill"></a>

#### `GetOwnerDemolitionsSkill(oObject)`

DJS-OEI 1/26/2004
Returns the Demolitions skill of the creature that
placed this mine. This will often be 0. This function accepts
the object that the mine is attached to (Door, Placeable, or Trigger)
and will determine which one it actually is at runtime.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="setorientonclick"></a>

#### `SetOrientOnClick(oCreature=0, nState=1)`

RWT-OEI 01/29/04
Disables or Enables the Orient On Click behavior in creatures. If
disabled, they will not orient to face the player when clicked on
for dialogue. The default behavior is TRUE.

**Parameters:**

- `oCreature`: `object` (default: `0`)
- `nState`: `int` (default: `1`)

<a id="getinfluence"></a>

#### `GetInfluence(nNPC)`

DJS-OEI 1/29/2004
Gets the PC's influence on the alignment of a CNPC.
Parameters:
nNPC - NPC_* constant identifying the CNPC we're interested in.
If this character is not an available party member, the return
value with be 0. If the character is in the party, but has an
attitude of Ambivalent, this will be -1.

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="setinfluence"></a>

#### `SetInfluence(nNPC, nInfluence)`

DJS-OEI 1/29/2004
Sets the PC's influence on the alignment of a CNPC.
Parameters:
nNPC - NPC_* constant identifying the CNPC we're interested in.
If this character is not an available party member, nothing
will happen.
nInfluence - The new value for the influence on this CNPC.

**Parameters:**

- `nNPC`: `int`
- `nInfluence`: `int`

<a id="modifyinfluence"></a>

#### `ModifyInfluence(nNPC, nModifier)`

DJS-OEI 1/29/2004
Modifies the PC's influence on the alignment of a CNPC.
Parameters:
nNPC - NPC_* constant identifying the CNPC we're interested in.
If this character is not an available party member, nothing
will happen.
nModifier - The modifier to the current influence on this CNPC.
This may be a negative value to reduce the influence.

**Parameters:**

- `nNPC`: `int`
- `nModifier`: `int`

<a id="getracialsubtype"></a>

#### `GetRacialSubType(oTarget)`

FAK - OEI 2/3/04
returns the racial sub-type of the oTarget object

**Parameters:**

- `oTarget`: `object`

**Returns:** `int`

<a id="incrementglobalnumber"></a>

#### `IncrementGlobalNumber(sIdentifier, nAmount)`

DJS-OEI 2/3/2004
Increases the value of the given global number by the given amount.
This function only works with Number type globals, not booleans. It
will fail with a warning if the final amount is greater than the max
of 127.

**Parameters:**

- `sIdentifier`: `string`
- `nAmount`: `int`

<a id="decrementglobalnumber"></a>

#### `DecrementGlobalNumber(sIdentifier, nAmount)`

DJS-OEI 2/3/2004
Decreases the value of the given global number by the given amount.
This function only works with Number type globals, not booleans. It
will fail with a warning if the final amount is less than the minimum
of -128.

**Parameters:**

- `sIdentifier`: `string`
- `nAmount`: `int`

<a id="swmg_setjumpspeed"></a>

#### `SWMG_SetJumpSpeed(fSpeed)`

FAK - OEI 2/11/04
SWMG_SetJumpSpeed -- the sets the 'jump speed' for the swoop
bike races. Gravity will act upon this velocity.

**Parameters:**

- `fSpeed`: `float`

<a id="yavinhackdoorclose"></a>

#### `YavinHackDoorClose(oCreature)`

808

**Parameters:**

- `oCreature`: `object`

<a id="isstealthed"></a>

#### `IsStealthed(oCreature)`

END PC CODE MERGER
810
DJS-OEI 3/8/2004
Determines if the given creature is in Stealth mode or not.
0 = Creature is not stealthed.
1 = Creature is stealthed.
This function will return 0 for any non-creature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="ismeditating"></a>

#### `IsMeditating(oCreature)`

811
DJS-OEI 3/12/2004
Determines if the given creature is using any Meditation Tree
Force Power.
0 = Creature is not meditating.
1 = Creature is meditating.
This function will return 0 for any non-creature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="isintotaldefense"></a>

#### `IsInTotalDefense(oCreature)`

812
DJS-OEI 3/16/2004
Determines if the given creature is using the Total Defense
Stance.
0 = Creature is not in Total Defense.
1 = Creature is in Total Defense.
This function will return 0 for any non-creature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="sethealtarget"></a>

#### `SetHealTarget(oidHealer, oidTarget)`

813
RWT-OEI 03/19/04
Stores a Heal Target for the Healer AI script. Should probably
not be used outside of the Healer AI script.

**Parameters:**

- `oidHealer`: `object`
- `oidTarget`: `object`

<a id="gethealtarget"></a>

#### `GetHealTarget(oidHealer)`

814
RWT-OEI 03/19/04
Retrieves the Heal Target for the Healer AI script. Should probably
not be used outside of the Healer AI script.

**Parameters:**

- `oidHealer`: `object`

**Returns:** `object`

<a id="getrandomdestination"></a>

#### `GetRandomDestination(oCreature, rangeLimit)`

815
RWT-OEI 03/23/04
Returns a vector containing a random destination that the
given creature can walk to that's within the range of the
passed parameter.

**Parameters:**

- `oCreature`: `object`
- `rangeLimit`: `int`

**Returns:** `vector`

<a id="isformactive"></a>

#### `IsFormActive(oCreature, nFormID)`

816
DJS-OEI 3/25/2004
Returns whether the given creature is currently in the
requested Lightsaber/Consular Form and can make use of
its benefits. This function will perform trumping checks
and lightsaber-wielding checks for those Forms that require
them.

**Parameters:**

- `oCreature`: `object`
- `nFormID`: `int`

**Returns:** `int`

<a id="getspellformmask"></a>

#### `GetSpellFormMask(nSpellID)`

817
DJS-OEI 3/28/2004
Returns the Form Mask of the requested spell. This is used
to determine if a spell is affected by various Forms, usually
Consular forms that modify duration/range.

**Parameters:**

- `nSpellID`: `int`

**Returns:** `int`

<a id="getspellbaseforcepointcost"></a>

#### `GetSpellBaseForcePointCost(nSpellID)`

818
DJS-OEI 3/29/2004
Return the base number of Force Points required to cast
the given spell. This does not take into account modifiers
of any kind.

**Parameters:**

- `nSpellID`: `int`

**Returns:** `int`

<a id="setkeepstealthindialog"></a>

#### `SetKeepStealthInDialog(nStealthState)`

819
RWT-OEI 04/05/04
Setting this to TRUE makes it so that the Stealth status is
left on characters even when entering cutscenes. By default,
stealth is removed from anyone taking part in a cutscene.
ALWAYS set this back to FALSE on every End Dialog node in
the cutscene you wanted to stay stealthed in. This isn't a
flag that should be left on indefinitely. In fact, it isn't
saved, so needs to be set/unset on a case by case basis.

**Parameters:**

- `nStealthState`: `int`

<a id="haslineofsight"></a>

#### `HasLineOfSight(vSource, vTarget, oSource=1, oTarget=1)`

820
RWT-OEI 04/06/04
This returns TRUE or FALSE if there is a clear line of sight from
the source vector to the target vector. This is used in the AI to
help the creatures using ranged weapons find better places to shoot
when the player moves out of sight.

**Parameters:**

- `vSource`: `vector`
- `vTarget`: `vector`
- `oSource`: `object` (default: `1`)
- `oTarget`: `object` (default: `1`)

**Returns:** `int`

<a id="showdemoscreen"></a>

#### `ShowDemoScreen(sTexture, nTimeout, nDisplayString, nDisplayX, nDisplayY)`

821
FAK - OEI 5/3/04
ShowDemoScreen, displays a texture, timeout, string and xy for string

**Parameters:**

- `sTexture`: `string`
- `nTimeout`: `int`
- `nDisplayString`: `int`
- `nDisplayX`: `int`
- `nDisplayY`: `int`

**Returns:** `int`

<a id="forceheartbeat"></a>

#### `ForceHeartbeat(oCreature)`

822
DJS-OEI 5/4/2004
Forces a Heartbeat on the given creature. THIS ONLY WORKS FOR CREATURES
AT THE MOMENT. This heartbeat should force perception updates to occur.

**Parameters:**

- `oCreature`: `object`

<a id="isrunning"></a>

#### `IsRunning(oCreature)`

824
FAK - OEI 5/7/04
gets the walk state of the creature: 0 walk or standing, 1 is running

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="swmg_playerapplyforce"></a>

#### `SWMG_PlayerApplyForce(vForce)`

825
FAK - OEI 5/24/04
applies a velocity to the player object

**Parameters:**

- `vForce`: `vector`

<a id="setforfeitconditions"></a>

#### `SetForfeitConditions(nForfeitFlags)`

DJS-OEI 6/12/2004
These constants can be OR'ed together and sent to SetForfeitConditions()

**Parameters:**

- `nForfeitFlags`: `int`

<a id="getlastforfeitviolation"></a>

#### `GetLastForfeitViolation()`

827
DJS-OEI 6/12/2004
This function returns the last FORFEIT_* condition that the player
has violated.

**Returns:** `int`

<a id="modifyreflexsavingthrowbase"></a>

#### `ModifyReflexSavingThrowBase(aObject, aModValue)`

828
AWD-OEI 6/21/2004
This function does not return a value.
This function modifies the BASE value of the REFLEX saving throw for aObject

**Parameters:**

- `aObject`: `object`
- `aModValue`: `int`

<a id="modifyfortitudesavingthrowbase"></a>

#### `ModifyFortitudeSavingThrowBase(aObject, aModValue)`

829
AWD-OEI 6/21/2004
This function does not return a value.
This function modifies the BASE value of the FORTITUDE saving throw for aObject

**Parameters:**

- `aObject`: `object`
- `aModValue`: `int`

<a id="modifywillsavingthrowbase"></a>

#### `ModifyWillSavingThrowBase(aObject, aModValue)`

830
AWD-OEI 6/21/2004
This function does not return a value.
This function modifies the BASE value of the WILL saving throw for aObject

**Parameters:**

- `aObject`: `object`
- `aModValue`: `int`

<a id="getscriptstringparameter"></a>

#### `GetScriptStringParameter()`

DJS-OEI 6/21/2004
831
This function will return the one CExoString parameter
allowed for the currently running script.

**Returns:** `string`

<a id="getobjectpersonalspace"></a>

#### `GetObjectPersonalSpace(aObject)`

832
AWD-OEI 6/29/2004
This function returns the personal space value of an object

**Parameters:**

- `aObject`: `object`

**Returns:** `float`

<a id="adjustcreatureattributes"></a>

#### `AdjustCreatureAttributes(oObject, nAttribute, nAmount)`

833
AWD-OEI 7/06/2004
This function adjusts a creatures stats.
oObject is the creature that will have it's attribute adjusted
The following constants are acceptable for the nAttribute parameter:
ABILITY_STRENGTH
ABILITY_DEXTERITY
ABILITY_CONSTITUTION
ABILITY_INTELLIGENCE
ABILITY_WISDOM
ABILITY_CHARISMA
nAmount is the integer vlaue to adjust the stat by (negative values will work).

**Parameters:**

- `oObject`: `object`
- `nAttribute`: `int`
- `nAmount`: `int`

<a id="setcreatureailevel"></a>

#### `SetCreatureAILevel(oObject, nPriority)`

834
AWD-OEI 7/08/2004
This function raises a creature's priority level.

**Parameters:**

- `oObject`: `object`
- `nPriority`: `int`

<a id="resetcreatureailevel"></a>

#### `ResetCreatureAILevel(oObject)`

835
AWD-OEI 7/08/2004
This function raises a creature's priority level.

**Parameters:**

- `oObject`: `object`

<a id="addavailablepupbytemplate"></a>

#### `AddAvailablePUPByTemplate(nPUP, sTemplate)`

836
RWT-OEI 07/17/04
This function adds a Puppet to the Puppet Table by
template.
Returns 1 if successful, 0 if there was an error
This does not spawn the puppet or anything. It just
adds it to the party table and makes it available for
use down the line. Exactly like AddAvailableNPCByTemplate

**Parameters:**

- `nPUP`: `int`
- `sTemplate`: `string`

**Returns:** `int`

<a id="addavailablepupbyobject"></a>

#### `AddAvailablePUPByObject(nPUP, oPuppet)`

837
RWT-OEI 07/17/04
This function adds a Puppet to the Puppet Table by
creature ID
Returns 1 if successful, 0 if there was an error
This does not spawn the puppet or anything. It just
adds it to the party table and makes it available for
use down the line. Exactly like AddAvailableNPCByTemplate

**Parameters:**

- `nPUP`: `int`
- `oPuppet`: `object`

**Returns:** `int`

<a id="assignpup"></a>

#### `AssignPUP(nPUP, nNPC)`

838
RWT-OEI 07/17/04
This function assigns a PUPPET constant to a
Party NPC.  The party NPC -MUST- be in the game
before calling this.
Both the PUP and the NPC have
to be available in their respective tables
Returns 1 if successful, 0 if there was an error

**Parameters:**

- `nPUP`: `int`
- `nNPC`: `int`

**Returns:** `int`

<a id="spawnavailablepup"></a>

#### `SpawnAvailablePUP(nPUP, lLocation)`

839
RWT-OEI 07/17/04
This function spawns a Party PUPPET.
This must be used whenever you want a copy
of the puppet around to manipulate in the game
since the puppet is stored in the party table
just like NPCs are.  Once a puppet is assigned
to a party NPC (see AssignPUP), it will spawn
or disappear whenever its owner joins or leaves
the party.
This does not add it to the party automatically,
just like SpawnNPC doesn't. You must call AddPuppet()
to actually add it to the party

**Parameters:**

- `nPUP`: `int`
- `lLocation`: `location`

**Returns:** `object`

<a id="getpupowner"></a>

#### `GetPUPOwner(oPUP=0)`

841
RWT-OEI 07/19/04
This returns the object ID of the puppet's owner.
The Puppet's owner must exist and must be in the party
in order to be found.
Returns invalid object Id if the owner cannot be found.

**Parameters:**

- `oPUP`: `object` (default: `0`)

**Returns:** `object`

<a id="getispuppet"></a>

#### `GetIsPuppet(oPUP=0)`

842
RWT-OEI 07/19/04
Returns 1 if the creature is a Puppet in the party.
Otherwise returns 0. It is possible for a 'party puppet'
to exist without actually being in the party table.
such as when SpawnAvailablePUP is used without subsequently
using AddPartyPuppet to add the newly spawned puppet to
the party table. A puppet in that in-between state would
return 0 from this function

**Parameters:**

- `oPUP`: `object` (default: `0`)

**Returns:** `int`

<a id="getispartyleader"></a>

#### `GetIsPartyLeader(oCharacter=0)`

844
RWT-OEI 07/21/04
Returns TRUE if the object ID passed is the character
that the player is actively controlling at that point.
Note that this function is *NOT* able to return correct
information during Area Loading since the player is not
actively controlling anyone at that point.

**Parameters:**

- `oCharacter`: `object` (default: `0`)

**Returns:** `int`

<a id="removenpcfrompartytobase"></a>

#### `RemoveNPCFromPartyToBase(nNPC)`

846
JAB-OEI 07/22/04
Will remove the CNPC from the 3 person party, and remove
him/her from the area, effectively sending the CNPC back
to the base. The CNPC data is still stored in the
party table, and calling this function will not destroy
the CNPC in any way.
Returns TRUE for success.

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="creatureflourishweapon"></a>

#### `CreatureFlourishWeapon(oObject)`

847
AWD-OEI 7/22/2004
This causes a creature to flourish with it's currently equipped weapon.

**Parameters:**

- `oObject`: `object`

<a id="changeobjectappearance"></a>

#### `ChangeObjectAppearance(oObjectToChange, nAppearance)`

850
ChangeObjectAppearance
oObjectToChange = Object to change appearance of
nAppearance = appearance to change to (from appearance.2da)

**Parameters:**

- `oObjectToChange`: `object`
- `nAppearance`: `int`

<a id="getisxbox"></a>

#### `GetIsXBox()`

851
GetIsXBox
Returns TRUE if this script is being executed on the X-Box. Returns FALSE
if this is the PC build.

**Returns:** `int`

<a id="playoverlayanimation"></a>

#### `PlayOverlayAnimation(oTarget, nAnimation)`

854
DJS-OEI 8/29/2004
PlayOverlayAnimation
This function will play an overlay animation on a character
even if the character is moving. This does not cause an action
to be placed on the queue. The animation passed in must be
designated as an overlay in Animations.2DA.

**Parameters:**

- `oTarget`: `object`
- `nAnimation`: `int`

<a id="unlockallsongs"></a>

#### `UnlockAllSongs()`

855
RWT-OEI 08/30/04
UnlockAllSongs
Calling this will set all songs as having been unlocked.
It is INTENDED to be used in the end-game scripts to unlock
any end-game songs as well as the KotOR1 sound track.

<a id="disablemap"></a>

#### `DisableMap(nFlag=0)`

856
RWT-OEI 08/31/04
Passing TRUE into this function turns off the player's maps.
Passing FALSE into this function re-enables them. This change
is permanent once called, so it is important that there *is*
a matching call to DisableMap(FALSE) somewhere or else the

**Parameters:**

- `nFlag`: `int` (default: `0`)

<a id="detonatemine"></a>

#### `DetonateMine(oMine)`

857
RWT-OEI 08/31/04
This function schedules a mine to play its DETONATION
animation once it is destroyed. Note that this detonates
the mine immediately but has nothing to do with causing
the mine to do any damage to anything around it. To
get the mine to damage things around it when it detonates
do:
AssignCommand(<mine>,ExecuteScript( "k_trp_generic",<mine>));
right before you call DetonateMine(). By my experience so far

**Parameters:**

- `oMine`: `object`

<a id="disablehealthregen"></a>

#### `DisableHealthRegen(nFlag=0)`

858
RWT-OEI 09/06/04
This function turns off the innate health regeneration that all party
members have. The health regen will *stay* off until it is turned back
on by passing FALSE to this function.

**Parameters:**

- `nFlag`: `int` (default: `0`)

<a id="setcurrentform"></a>

#### `SetCurrentForm(oCreature, nFormID)`

859
DJS-OEI 9/7/2004
This function sets the current Jedi Form on the given creature. This
call will do nothing if the target does not know the Form itself.

**Parameters:**

- `oCreature`: `object`
- `nFormID`: `int`

<a id="setdisabletransit"></a>

#### `SetDisableTransit(nFlag=0)`

860
RWT-OEI 09/09/04
This will disable or enable area transit

**Parameters:**

- `nFlag`: `int` (default: `0`)

<a id="setinputclass"></a>

#### `SetInputClass(nClass)`

861
RWT-OEI 09/09/04
This will set the specific input class.
The valid options are:
0 - Normal PC control
1 - Mini game control
2 - GUI control
3 - Dialog Control
4 - Freelook control

**Parameters:**

- `nClass`: `int`

<a id="setforcealwaysupdate"></a>

#### `SetForceAlwaysUpdate(oObject, nFlag)`

862
RWT-OEI 09/15/04
This script allows an object to recieve updates even if it is outside
the normal range limit of 250.0f meters away from the player. This should
ONLY be used for cutscenes that involve objects that are more than 250
meters away from the player. It needs to be used on a object by object
basis.
This flag should *always* be set to false once the cutscene it is needed
for is over, or else the game will spend CPU time updating the object
when it doesn't need to.
For questions on use of this function, or what its purpose is, check
with me.

**Parameters:**

- `oObject`: `object`
- `nFlag`: `int`

<a id="enablerain"></a>

#### `EnableRain(nFlag)`

863
RWT-OEI 09/15/04
This function enables or disables rain

**Parameters:**

- `nFlag`: `int`

<a id="displaymessagebox"></a>

#### `DisplayMessageBox(nStrRef, sIcon=)`

864
RWT-OEI 09/27/04
This function displays the generic Message Box with the strref
message in it
sIcon is the resref for an icon you would like to display.

**Parameters:**

- `nStrRef`: `int`
- `sIcon`: `string` (default: ``)

<a id="displaydatapad"></a>

#### `DisplayDatapad(oDatapad)`

865
RWT-OEI 09/28/04
This function displays a datapad popup. Just pass it the
object ID of a datapad.

**Parameters:**

- `oDatapad`: `object`

<a id="removeheartbeat"></a>

#### `RemoveHeartbeat(oPlaceable)`

866
CTJ-OEI 09-29-04
Removes the heartbeat script on the placeable.  Useful for
placeables whose contents get populated in the heartbeat
script and then the heartbeat no longer needs to be called.

**Parameters:**

- `oPlaceable`: `object`

<a id="adjustcreatureskills"></a>

#### `AdjustCreatureSkills(oObject, nSkill, nAmount)`

869
DJS-OEI 10/9/2004
This function adjusts a creature's skills.
oObject is the creature that will have its skill adjusted
The following constants are acceptable for the nSkill parameter:
SKILL_COMPUTER_USE
SKILL_DEMOLITIONS
SKILL_STEALTH
SKILL_AWARENESS
SKILL_PERSUADE
SKILL_REPAIR
SKILL_SECURITY
SKILL_TREAT_INJURY
nAmount is the integer value to adjust the stat by (negative values will work).

**Parameters:**

- `oObject`: `object`
- `nSkill`: `int`
- `nAmount`: `int`

<a id="enablerendering"></a>

#### `EnableRendering(oObject, bEnable)`

871
DJS-OEI 10/15/2004
This function will allow the caller to modify the rendering behavior
of the target object.
oObject - The object to change rendering state on.
bEnable - If 0, the object will stop rendering. Else, the object will render.

**Parameters:**

- `oObject`: `object`
- `bEnable`: `int`

<a id="getcombatactionspending"></a>

#### `GetCombatActionsPending(oCreature)`

872
RWT-OEI 10/19/04
This function returns TRUE if the creature has actions in its
Combat Action queue.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="savenpcbyobject"></a>

#### `SaveNPCByObject(nNPC, oidCharacter)`

873
RWT-OEI 10/26/04
This function saves the party member at that index with the object
that is passed in.

**Parameters:**

- `nNPC`: `int`
- `oidCharacter`: `object`

<a id="savepupbyobject"></a>

#### `SavePUPByObject(nPUP, oidPuppet)`

874
RWT-OEI 10/26/04
This function saves the party puppet at that index with the object
that is passed in. For the Remote, just use '0' for nPUP

**Parameters:**

- `nPUP`: `int`
- `oidPuppet`: `object`

<a id="getisplayermadecharacter"></a>

#### `GetIsPlayerMadeCharacter(oidCharacter)`

875
RWT-OEI 10/29/04
Returns TRUE if the object passed in is the character that the player
made at the start of the game

**Parameters:**

- `oidCharacter`: `object`

**Returns:** `int`
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

*No functions in this category.*
### Skills and Feats

<a id="getskillrankbase"></a>

#### `GetSkillRankBase(nSkill, oObject=0)`

870
DJS-OEI 10/10/2004
This function returns the base Skill Rank for the requested
skill. It does not include modifiers from effects/items.
The following constants are acceptable for the nSkill parameter:
SKILL_COMPUTER_USE
SKILL_DEMOLITIONS
SKILL_STEALTH
SKILL_AWARENESS
SKILL_PERSUADE
SKILL_REPAIR
SKILL_SECURITY
SKILL_TREAT_INJURY
oObject is the creature that will have its skill base returned.

**Parameters:**

- `nSkill`: `int`
- `oObject`: `object` (default: `0`)

**Returns:** `int`
### Sound and Music Functions

*No functions in this category.*
## Shared Constants (K1 & TSL)

<!-- SHARED_CONSTANTS_START -->

### Ability Constants

| Constant | Type | Value |
|----------|------|-------|
| `ABILITY_STRENGTH` | `int` | `0` |
| `ABILITY_DEXTERITY` | `int` | `1` |
| `ABILITY_CONSTITUTION` | `int` | `2` |
| `ABILITY_INTELLIGENCE` | `int` | `3` |
| `ABILITY_WISDOM` | `int` | `4` |
| `ABILITY_CHARISMA` | `int` | `5` |
### Alignment Constants

| Constant | Type | Value |
|----------|------|-------|
| `ALIGNMENT_ALL` | `int` | `0` |
| `ALIGNMENT_NEUTRAL` | `int` | `1` |
| `ALIGNMENT_LIGHT_SIDE` | `int` | `2` |
| `ALIGNMENT_DARK_SIDE` | `int` | `3` |
### Class type Constants

| Constant | Type | Value |
|----------|------|-------|
| `CLASS_TYPE_SOLDIER` | `int` | `0` |
| `CLASS_TYPE_SCOUT` | `int` | `1` |
| `CLASS_TYPE_SCOUNDREL` | `int` | `2` |
| `CLASS_TYPE_JEDIGUARDIAN` | `int` | `3` |
| `CLASS_TYPE_JEDICONSULAR` | `int` | `4` |
| `CLASS_TYPE_JEDISENTINEL` | `int` | `5` |
| `CLASS_TYPE_COMBATDROID` | `int` | `6` |
| `CLASS_TYPE_EXPERTDROID` | `int` | `7` |
| `CLASS_TYPE_MINION` | `int` | `8` |
| `CLASS_TYPE_INVALID` | `int` | `255` |
### Inventory Constants

| Constant | Type | Value |
|----------|------|-------|
| `INVENTORY_SLOT_HEAD` | `int` | `0` |
| `INVENTORY_SLOT_BODY` | `int` | `1` |
| `INVENTORY_SLOT_HANDS` | `int` | `3` |
| `INVENTORY_SLOT_RIGHTWEAPON` | `int` | `4` |
| `INVENTORY_SLOT_LEFTWEAPON` | `int` | `5` |
| `INVENTORY_SLOT_LEFTARM` | `int` | `7` |
| `INVENTORY_SLOT_RIGHTARM` | `int` | `8` |
| `INVENTORY_SLOT_IMPLANT` | `int` | `9` |
| `INVENTORY_SLOT_BELT` | `int` | `10` |
| `INVENTORY_SLOT_CWEAPON_L` | `int` | `14` |
| `INVENTORY_SLOT_CWEAPON_R` | `int` | `15` |
| `INVENTORY_SLOT_CWEAPON_B` | `int` | `16` |
| `INVENTORY_SLOT_CARMOUR` | `int` | `17` |
### NPC Constants

| Constant | Type | Value |
|----------|------|-------|
| `NPC_PLAYER` | `int` | `-1` |
| `NPC_BASTILA` | `int` | `0` |
| `NPC_CANDEROUS` | `int` | `1` |
| `NPC_CARTH` | `int` | `2` |
| `NPC_HK_47` | `int` | `3` |
| `NPC_JOLEE` | `int` | `4` |
| `NPC_JUHANI` | `int` | `5` |
| `NPC_MISSION` | `int` | `6` |
| `NPC_T3_M4` | `int` | `7` |
| `NPC_ZAALBAR` | `int` | `8` |
| `NPC_AISTYLE_DEFAULT_ATTACK` | `int` | `0` |
| `NPC_AISTYLE_RANGED_ATTACK` | `int` | `1` |
| `NPC_AISTYLE_MELEE_ATTACK` | `int` | `2` |
| `NPC_AISTYLE_AID` | `int` | `3` |
| `NPC_AISTYLE_GRENADE_THROWER` | `int` | `4` |
| `NPC_AISTYLE_JEDI_SUPPORT` | `int` | `5` |
### Object type Constants

| Constant | Type | Value |
|----------|------|-------|
| `OBJECT_TYPE_CREATURE` | `int` | `1` |
| `OBJECT_TYPE_ITEM` | `int` | `2` |
| `OBJECT_TYPE_TRIGGER` | `int` | `4` |
| `OBJECT_TYPE_DOOR` | `int` | `8` |
| `OBJECT_TYPE_AREA_OF_EFFECT` | `int` | `16` |
| `OBJECT_TYPE_WAYPOINT` | `int` | `32` |
| `OBJECT_TYPE_PLACEABLE` | `int` | `64` |
| `OBJECT_TYPE_STORE` | `int` | `128` |
| `OBJECT_TYPE_ENCOUNTER` | `int` | `256` |
| `OBJECT_TYPE_SOUND` | `int` | `512` |
| `OBJECT_TYPE_ALL` | `int` | `32767` |
| `OBJECT_TYPE_INVALID` | `int` | `32767` |
### Other Constants

| Constant | Type | Value |
|----------|------|-------|
| `NUM_INVENTORY_SLOTS` | `int` | `18` |
| `TRUE` | `int` | `1` |
| `FALSE` | `int` | `0` |
| `DIRECTION_EAST` | `float` | `0.0` |
| `DIRECTION_NORTH` | `float` | `90.0` |
| `DIRECTION_WEST` | `float` | `180.0` |
| `DIRECTION_SOUTH` | `float` | `270.0` |
| `PI` | `float` | `3.141592` |
| `ATTITUDE_NEUTRAL` | `int` | `0` |
| `ATTITUDE_AGGRESSIVE` | `int` | `1` |
| `ATTITUDE_DEFENSIVE` | `int` | `2` |
| `ATTITUDE_SPECIAL` | `int` | `3` |
| `TALKVOLUME_TALK` | `int` | `0` |
| `TALKVOLUME_WHISPER` | `int` | `1` |
| `TALKVOLUME_SHOUT` | `int` | `2` |
| `TALKVOLUME_SILENT_TALK` | `int` | `3` |
| `TALKVOLUME_SILENT_SHOUT` | `int` | `4` |
| `DURATION_TYPE_INSTANT` | `int` | `0` |
| `DURATION_TYPE_TEMPORARY` | `int` | `1` |
| `DURATION_TYPE_PERMANENT` | `int` | `2` |
| `SUBTYPE_MAGICAL` | `int` | `8` |
| `SUBTYPE_SUPERNATURAL` | `int` | `16` |
| `SUBTYPE_EXTRAORDINARY` | `int` | `24` |
| `SHAPE_SPELLCYLINDER` | `int` | `0` |
| `SHAPE_CONE` | `int` | `1` |
| `SHAPE_CUBE` | `int` | `2` |
| `SHAPE_SPELLCONE` | `int` | `3` |
| `SHAPE_SPHERE` | `int` | `4` |
| `GENDER_MALE` | `int` | `0` |
| `GENDER_FEMALE` | `int` | `1` |
| `GENDER_BOTH` | `int` | `2` |
| `GENDER_OTHER` | `int` | `3` |
| `GENDER_NONE` | `int` | `4` |
| `DAMAGE_TYPE_BLUDGEONING` | `int` | `1` |
| `DAMAGE_TYPE_PIERCING` | `int` | `2` |
| `DAMAGE_TYPE_SLASHING` | `int` | `4` |
| `DAMAGE_TYPE_UNIVERSAL` | `int` | `8` |
| `DAMAGE_TYPE_ACID` | `int` | `16` |
| `DAMAGE_TYPE_COLD` | `int` | `32` |
| `DAMAGE_TYPE_LIGHT_SIDE` | `int` | `64` |
| `DAMAGE_TYPE_ELECTRICAL` | `int` | `128` |
| `DAMAGE_TYPE_FIRE` | `int` | `256` |
| `DAMAGE_TYPE_DARK_SIDE` | `int` | `512` |
| `DAMAGE_TYPE_SONIC` | `int` | `1024` |
| `DAMAGE_TYPE_ION` | `int` | `2048` |
| `DAMAGE_TYPE_BLASTER` | `int` | `4096` |
| `AC_VS_DAMAGE_TYPE_ALL` | `int` | `8199` |
| `DAMAGE_BONUS_1` | `int` | `1` |
| `DAMAGE_BONUS_2` | `int` | `2` |
| `DAMAGE_BONUS_3` | `int` | `3` |
| `DAMAGE_BONUS_4` | `int` | `4` |
| `DAMAGE_BONUS_5` | `int` | `5` |
| `DAMAGE_BONUS_1d4` | `int` | `6` |
| `DAMAGE_BONUS_1d6` | `int` | `7` |
| `DAMAGE_BONUS_1d8` | `int` | `8` |
| `DAMAGE_BONUS_1d10` | `int` | `9` |
| `DAMAGE_BONUS_2d6` | `int` | `10` |
| `DAMAGE_POWER_NORMAL` | `int` | `0` |
| `DAMAGE_POWER_PLUS_ONE` | `int` | `1` |
| `DAMAGE_POWER_PLUS_TWO` | `int` | `2` |
| `DAMAGE_POWER_PLUS_THREE` | `int` | `3` |
| `DAMAGE_POWER_PLUS_FOUR` | `int` | `4` |
| `DAMAGE_POWER_PLUS_FIVE` | `int` | `5` |
| `DAMAGE_POWER_ENERGY` | `int` | `6` |
| `ATTACK_BONUS_MISC` | `int` | `0` |
| `ATTACK_BONUS_ONHAND` | `int` | `1` |
| `ATTACK_BONUS_OFFHAND` | `int` | `2` |
| `AC_DODGE_BONUS` | `int` | `0` |
| `AC_NATURAL_BONUS` | `int` | `1` |
| `AC_ARMOUR_ENCHANTMENT_BONUS` | `int` | `2` |
| `AC_SHIELD_ENCHANTMENT_BONUS` | `int` | `3` |
| `AC_DEFLECTION_BONUS` | `int` | `4` |
| `DOOR_ACTION_OPEN` | `int` | `0` |
| `DOOR_ACTION_UNLOCK` | `int` | `1` |
| `DOOR_ACTION_BASH` | `int` | `2` |
| `DOOR_ACTION_IGNORE` | `int` | `3` |
| `DOOR_ACTION_KNOCK` | `int` | `4` |
| `PLACEABLE_ACTION_USE` | `int` | `0` |
| `PLACEABLE_ACTION_UNLOCK` | `int` | `1` |
| `PLACEABLE_ACTION_BASH` | `int` | `2` |
| `PLACEABLE_ACTION_KNOCK` | `int` | `4` |
| `RACIAL_TYPE_UNKNOWN` | `int` | `0` |
| `RACIAL_TYPE_ELF` | `int` | `1` |
| `RACIAL_TYPE_GNOME` | `int` | `2` |
| `RACIAL_TYPE_HALFLING` | `int` | `3` |
| `RACIAL_TYPE_HALFELF` | `int` | `4` |
| `RACIAL_TYPE_DROID` | `int` | `5` |
| `RACIAL_TYPE_HUMAN` | `int` | `6` |
| `RACIAL_TYPE_ALL` | `int` | `7` |
| `RACIAL_TYPE_INVALID` | `int` | `8` |
| `SAVING_THROW_ALL` | `int` | `0` |
| `SAVING_THROW_FORT` | `int` | `1` |
| `SAVING_THROW_REFLEX` | `int` | `2` |
| `SAVING_THROW_WILL` | `int` | `3` |
| `SAVING_THROW_TYPE_ALL` | `int` | `0` |
| `SAVING_THROW_TYPE_NONE` | `int` | `0` |
| `SAVING_THROW_TYPE_ACID` | `int` | `1` |
| `SAVING_THROW_TYPE_SNEAK_ATTACK` | `int` | `2` |
| `SAVING_THROW_TYPE_COLD` | `int` | `3` |
| `SAVING_THROW_TYPE_DEATH` | `int` | `4` |
| `SAVING_THROW_TYPE_DISEASE` | `int` | `5` |
| `SAVING_THROW_TYPE_LIGHT_SIDE` | `int` | `6` |
| `SAVING_THROW_TYPE_ELECTRICAL` | `int` | `7` |
| `SAVING_THROW_TYPE_FEAR` | `int` | `8` |
| `SAVING_THROW_TYPE_FIRE` | `int` | `9` |
| `SAVING_THROW_TYPE_MIND_AFFECTING` | `int` | `10` |
| `SAVING_THROW_TYPE_DARK_SIDE` | `int` | `11` |
| `SAVING_THROW_TYPE_POISON` | `int` | `12` |
| `SAVING_THROW_TYPE_SONIC` | `int` | `13` |
| `SAVING_THROW_TYPE_TRAP` | `int` | `14` |
| `SAVING_THROW_TYPE_FORCE_POWER` | `int` | `15` |
| `SAVING_THROW_TYPE_ION` | `int` | `16` |
| `SAVING_THROW_TYPE_BLASTER` | `int` | `17` |
| `SAVING_THROW_TYPE_PARALYSIS` | `int` | `18` |
| `IMMUNITY_TYPE_NONE` | `int` | `0` |
| `IMMUNITY_TYPE_MIND_SPELLS` | `int` | `1` |
| `IMMUNITY_TYPE_POISON` | `int` | `2` |
| `IMMUNITY_TYPE_DISEASE` | `int` | `3` |
| `IMMUNITY_TYPE_FEAR` | `int` | `4` |
| `IMMUNITY_TYPE_TRAP` | `int` | `5` |
| `IMMUNITY_TYPE_PARALYSIS` | `int` | `6` |
| `IMMUNITY_TYPE_BLINDNESS` | `int` | `7` |
| `IMMUNITY_TYPE_DEAFNESS` | `int` | `8` |
| `IMMUNITY_TYPE_SLOW` | `int` | `9` |
| `IMMUNITY_TYPE_ENTANGLE` | `int` | `10` |
| `IMMUNITY_TYPE_SILENCE` | `int` | `11` |
| `IMMUNITY_TYPE_STUN` | `int` | `12` |
| `IMMUNITY_TYPE_SLEEP` | `int` | `13` |
| `IMMUNITY_TYPE_CHARM` | `int` | `14` |
| `IMMUNITY_TYPE_DOMINATE` | `int` | `15` |
| `IMMUNITY_TYPE_CONFUSED` | `int` | `16` |
| `IMMUNITY_TYPE_CURSED` | `int` | `17` |
| `IMMUNITY_TYPE_DAZED` | `int` | `18` |
| `IMMUNITY_TYPE_ABILITY_DECREASE` | `int` | `19` |
| `IMMUNITY_TYPE_ATTACK_DECREASE` | `int` | `20` |
| `IMMUNITY_TYPE_DAMAGE_DECREASE` | `int` | `21` |
| `IMMUNITY_TYPE_DAMAGE_IMMUNITY_DECREASE` | `int` | `22` |
| `IMMUNITY_TYPE_AC_DECREASE` | `int` | `23` |
| `IMMUNITY_TYPE_MOVEMENT_SPEED_DECREASE` | `int` | `24` |
| `IMMUNITY_TYPE_SAVING_THROW_DECREASE` | `int` | `25` |
| `IMMUNITY_TYPE_FORCE_RESISTANCE_DECREASE` | `int` | `26` |
| `IMMUNITY_TYPE_SKILL_DECREASE` | `int` | `27` |
| `IMMUNITY_TYPE_KNOCKDOWN` | `int` | `28` |
| `IMMUNITY_TYPE_NEGATIVE_LEVEL` | `int` | `29` |
| `IMMUNITY_TYPE_SNEAK_ATTACK` | `int` | `30` |
| `IMMUNITY_TYPE_CRITICAL_HIT` | `int` | `31` |
| `IMMUNITY_TYPE_DEATH` | `int` | `32` |
| `AREA_TRANSITION_RANDOM` | `int` | `0` |
| `AREA_TRANSITION_USER_DEFINED` | `int` | `1` |
| `AREA_TRANSITION_CITY_01` | `int` | `2` |
| `AREA_TRANSITION_CITY_02` | `int` | `3` |
| `AREA_TRANSITION_CITY_03` | `int` | `4` |
| `AREA_TRANSITION_CITY_04` | `int` | `5` |
| `AREA_TRANSITION_CITY_05` | `int` | `6` |
| `AREA_TRANSITION_CRYPT_01` | `int` | `7` |
| `AREA_TRANSITION_CRYPT_02` | `int` | `8` |
| `AREA_TRANSITION_CRYPT_03` | `int` | `9` |
| `AREA_TRANSITION_CRYPT_04` | `int` | `10` |
| `AREA_TRANSITION_CRYPT_05` | `int` | `11` |
| `AREA_TRANSITION_DUNGEON_01` | `int` | `12` |
| `AREA_TRANSITION_DUNGEON_02` | `int` | `13` |
| `AREA_TRANSITION_DUNGEON_03` | `int` | `14` |
| `AREA_TRANSITION_DUNGEON_04` | `int` | `15` |
| `AREA_TRANSITION_DUNGEON_05` | `int` | `16` |
| `AREA_TRANSITION_DUNGEON_06` | `int` | `17` |
| `AREA_TRANSITION_DUNGEON_07` | `int` | `18` |
| `AREA_TRANSITION_DUNGEON_08` | `int` | `19` |
| `AREA_TRANSITION_MINES_01` | `int` | `20` |
| `AREA_TRANSITION_MINES_02` | `int` | `21` |
| `AREA_TRANSITION_MINES_03` | `int` | `22` |
| `AREA_TRANSITION_MINES_04` | `int` | `23` |
| `AREA_TRANSITION_MINES_05` | `int` | `24` |
| `AREA_TRANSITION_MINES_06` | `int` | `25` |
| `AREA_TRANSITION_MINES_07` | `int` | `26` |
| `AREA_TRANSITION_MINES_08` | `int` | `27` |
| `AREA_TRANSITION_MINES_09` | `int` | `28` |
| `AREA_TRANSITION_SEWER_01` | `int` | `29` |
| `AREA_TRANSITION_SEWER_02` | `int` | `30` |
| `AREA_TRANSITION_SEWER_03` | `int` | `31` |
| `AREA_TRANSITION_SEWER_04` | `int` | `32` |
| `AREA_TRANSITION_SEWER_05` | `int` | `33` |
| `AREA_TRANSITION_CASTLE_01` | `int` | `34` |
| `AREA_TRANSITION_CASTLE_02` | `int` | `35` |
| `AREA_TRANSITION_CASTLE_03` | `int` | `36` |
| `AREA_TRANSITION_CASTLE_04` | `int` | `37` |
| `AREA_TRANSITION_CASTLE_05` | `int` | `38` |
| `AREA_TRANSITION_CASTLE_06` | `int` | `39` |
| `AREA_TRANSITION_CASTLE_07` | `int` | `40` |
| `AREA_TRANSITION_CASTLE_08` | `int` | `41` |
| `AREA_TRANSITION_INTERIOR_01` | `int` | `42` |
| `AREA_TRANSITION_INTERIOR_02` | `int` | `43` |
| `AREA_TRANSITION_INTERIOR_03` | `int` | `44` |
| `AREA_TRANSITION_INTERIOR_04` | `int` | `45` |
| `AREA_TRANSITION_INTERIOR_05` | `int` | `46` |
| `AREA_TRANSITION_INTERIOR_06` | `int` | `47` |
| `AREA_TRANSITION_INTERIOR_07` | `int` | `48` |
| `AREA_TRANSITION_INTERIOR_08` | `int` | `49` |
| `AREA_TRANSITION_INTERIOR_09` | `int` | `50` |
| `AREA_TRANSITION_INTERIOR_10` | `int` | `51` |
| `AREA_TRANSITION_INTERIOR_11` | `int` | `52` |
| `AREA_TRANSITION_INTERIOR_12` | `int` | `53` |
| `AREA_TRANSITION_INTERIOR_13` | `int` | `54` |
| `AREA_TRANSITION_INTERIOR_14` | `int` | `55` |
| `AREA_TRANSITION_INTERIOR_15` | `int` | `56` |
| `AREA_TRANSITION_INTERIOR_16` | `int` | `57` |
| `AREA_TRANSITION_FOREST_01` | `int` | `58` |
| `AREA_TRANSITION_FOREST_02` | `int` | `59` |
| `AREA_TRANSITION_FOREST_03` | `int` | `60` |
| `AREA_TRANSITION_FOREST_04` | `int` | `61` |
| `AREA_TRANSITION_FOREST_05` | `int` | `62` |
| `AREA_TRANSITION_RURAL_01` | `int` | `63` |
| `AREA_TRANSITION_RURAL_02` | `int` | `64` |
| `AREA_TRANSITION_RURAL_03` | `int` | `65` |
| `AREA_TRANSITION_RURAL_04` | `int` | `66` |
| `AREA_TRANSITION_RURAL_05` | `int` | `67` |
| `AREA_TRANSITION_CITY` | `int` | `2` |
| `AREA_TRANSITION_CRYPT` | `int` | `7` |
| `AREA_TRANSITION_FOREST` | `int` | `58` |
| `AREA_TRANSITION_RURAL` | `int` | `63` |
| `BODY_NODE_HAND` | `int` | `0` |
| `BODY_NODE_CHEST` | `int` | `1` |
| `BODY_NODE_HEAD` | `int` | `2` |
| `BODY_NODE_HAND_LEFT` | `int` | `3` |
| `BODY_NODE_HAND_RIGHT` | `int` | `4` |
| `RADIUS_SIZE_SMALL` | `float` | `1.67` |
| `RADIUS_SIZE_MEDIUM` | `float` | `3.33` |
| `RADIUS_SIZE_LARGE` | `float` | `5.0` |
| `RADIUS_SIZE_HUGE` | `float` | `6.67` |
| `RADIUS_SIZE_GARGANTUAN` | `float` | `8.33` |
| `RADIUS_SIZE_COLOSSAL` | `float` | `10.0` |
| `EFFECT_TYPE_INVALIDEFFECT` | `int` | `0` |
| `EFFECT_TYPE_DAMAGE_RESISTANCE` | `int` | `1` |
| `EFFECT_TYPE_REGENERATE` | `int` | `3` |
| `EFFECT_TYPE_DAMAGE_REDUCTION` | `int` | `7` |
| `EFFECT_TYPE_TEMPORARY_HITPOINTS` | `int` | `9` |
| `EFFECT_TYPE_ENTANGLE` | `int` | `11` |
| `EFFECT_TYPE_INVULNERABLE` | `int` | `12` |
| `EFFECT_TYPE_DEAF` | `int` | `13` |
| `EFFECT_TYPE_RESURRECTION` | `int` | `14` |
| `EFFECT_TYPE_IMMUNITY` | `int` | `15` |
| `EFFECT_TYPE_ENEMY_ATTACK_BONUS` | `int` | `17` |
| `EFFECT_TYPE_ARCANE_SPELL_FAILURE` | `int` | `18` |
| `EFFECT_TYPE_AREA_OF_EFFECT` | `int` | `20` |
| `EFFECT_TYPE_BEAM` | `int` | `21` |
| `EFFECT_TYPE_CHARMED` | `int` | `23` |
| `EFFECT_TYPE_CONFUSED` | `int` | `24` |
| `EFFECT_TYPE_FRIGHTENED` | `int` | `25` |
| `EFFECT_TYPE_DOMINATED` | `int` | `26` |
| `EFFECT_TYPE_PARALYZE` | `int` | `27` |
| `EFFECT_TYPE_DAZED` | `int` | `28` |
| `EFFECT_TYPE_STUNNED` | `int` | `29` |
| `EFFECT_TYPE_SLEEP` | `int` | `30` |
| `EFFECT_TYPE_POISON` | `int` | `31` |
| `EFFECT_TYPE_DISEASE` | `int` | `32` |
| `EFFECT_TYPE_CURSE` | `int` | `33` |
| `EFFECT_TYPE_SILENCE` | `int` | `34` |
| `EFFECT_TYPE_TURNED` | `int` | `35` |
| `EFFECT_TYPE_HASTE` | `int` | `36` |
| `EFFECT_TYPE_SLOW` | `int` | `37` |
| `EFFECT_TYPE_ABILITY_INCREASE` | `int` | `38` |
| `EFFECT_TYPE_ABILITY_DECREASE` | `int` | `39` |
| `EFFECT_TYPE_ATTACK_INCREASE` | `int` | `40` |
| `EFFECT_TYPE_ATTACK_DECREASE` | `int` | `41` |
| `EFFECT_TYPE_DAMAGE_INCREASE` | `int` | `42` |
| `EFFECT_TYPE_DAMAGE_DECREASE` | `int` | `43` |
| `EFFECT_TYPE_DAMAGE_IMMUNITY_INCREASE` | `int` | `44` |
| `EFFECT_TYPE_DAMAGE_IMMUNITY_DECREASE` | `int` | `45` |
| `EFFECT_TYPE_AC_INCREASE` | `int` | `46` |
| `EFFECT_TYPE_AC_DECREASE` | `int` | `47` |
| `EFFECT_TYPE_MOVEMENT_SPEED_INCREASE` | `int` | `48` |
| `EFFECT_TYPE_MOVEMENT_SPEED_DECREASE` | `int` | `49` |
| `EFFECT_TYPE_SAVING_THROW_INCREASE` | `int` | `50` |
| `EFFECT_TYPE_SAVING_THROW_DECREASE` | `int` | `51` |
| `EFFECT_TYPE_FORCE_RESISTANCE_INCREASE` | `int` | `52` |
| `EFFECT_TYPE_FORCE_RESISTANCE_DECREASE` | `int` | `53` |
| `EFFECT_TYPE_SKILL_INCREASE` | `int` | `54` |
| `EFFECT_TYPE_SKILL_DECREASE` | `int` | `55` |
| `EFFECT_TYPE_INVISIBILITY` | `int` | `56` |
| `EFFECT_TYPE_IMPROVEDINVISIBILITY` | `int` | `57` |
| `EFFECT_TYPE_DARKNESS` | `int` | `58` |
| `EFFECT_TYPE_DISPELMAGICALL` | `int` | `59` |
| `EFFECT_TYPE_ELEMENTALSHIELD` | `int` | `60` |
| `EFFECT_TYPE_NEGATIVELEVEL` | `int` | `61` |
| `EFFECT_TYPE_DISGUISE` | `int` | `62` |
| `EFFECT_TYPE_SANCTUARY` | `int` | `63` |
| `EFFECT_TYPE_TRUESEEING` | `int` | `64` |
| `EFFECT_TYPE_SEEINVISIBLE` | `int` | `65` |
| `EFFECT_TYPE_TIMESTOP` | `int` | `66` |
| `EFFECT_TYPE_BLINDNESS` | `int` | `67` |
| `EFFECT_TYPE_SPELLLEVELABSORPTION` | `int` | `68` |
| `EFFECT_TYPE_DISPELMAGICBEST` | `int` | `69` |
| `EFFECT_TYPE_ULTRAVISION` | `int` | `70` |
| `EFFECT_TYPE_MISS_CHANCE` | `int` | `71` |
| `EFFECT_TYPE_CONCEALMENT` | `int` | `72` |
| `EFFECT_TYPE_SPELL_IMMUNITY` | `int` | `73` |
| `EFFECT_TYPE_ASSUREDHIT` | `int` | `74` |
| `EFFECT_TYPE_VISUAL` | `int` | `75` |
| `EFFECT_TYPE_LIGHTSABERTHROW` | `int` | `76` |
| `EFFECT_TYPE_FORCEJUMP` | `int` | `77` |
| `EFFECT_TYPE_ASSUREDDEFLECTION` | `int` | `78` |
| `ITEM_PROPERTY_ABILITY_BONUS` | `int` | `0` |
| `ITEM_PROPERTY_AC_BONUS` | `int` | `1` |
| `ITEM_PROPERTY_AC_BONUS_VS_ALIGNMENT_GROUP` | `int` | `2` |
| `ITEM_PROPERTY_AC_BONUS_VS_DAMAGE_TYPE` | `int` | `3` |
| `ITEM_PROPERTY_AC_BONUS_VS_RACIAL_GROUP` | `int` | `4` |
| `ITEM_PROPERTY_ENHANCEMENT_BONUS` | `int` | `5` |
| `ITEM_PROPERTY_ENHANCEMENT_BONUS_VS_ALIGNMENT_GROUP` | `int` | `6` |
| `ITEM_PROPERTY_ENHANCEMENT_BONUS_VS_RACIAL_GROUP` | `int` | `7` |
| `ITEM_PROPERTY_ATTACK_PENALTY` | `int` | `8` |
| `ITEM_PROPERTY_BONUS_FEAT` | `int` | `9` |
| `ITEM_PROPERTY_ACTIVATE_ITEM` | `int` | `10` |
| `ITEM_PROPERTY_DAMAGE_BONUS` | `int` | `11` |
| `ITEM_PROPERTY_DAMAGE_BONUS_VS_ALIGNMENT_GROUP` | `int` | `12` |
| `ITEM_PROPERTY_DAMAGE_BONUS_VS_RACIAL_GROUP` | `int` | `13` |
| `ITEM_PROPERTY_IMMUNITY_DAMAGE_TYPE` | `int` | `14` |
| `ITEM_PROPERTY_DECREASED_DAMAGE` | `int` | `15` |
| `ITEM_PROPERTY_DAMAGE_REDUCTION` | `int` | `16` |
| `ITEM_PROPERTY_DAMAGE_RESISTANCE` | `int` | `17` |
| `ITEM_PROPERTY_DAMAGE_VULNERABILITY` | `int` | `18` |
| `ITEM_PROPERTY_DECREASED_ABILITY_SCORE` | `int` | `19` |
| `ITEM_PROPERTY_DECREASED_AC` | `int` | `20` |
| `ITEM_PROPERTY_DECREASED_SKILL_MODIFIER` | `int` | `21` |
| `ITEM_PROPERTY_EXTRA_MELEE_DAMAGE_TYPE` | `int` | `22` |
| `ITEM_PROPERTY_EXTRA_RANGED_DAMAGE_TYPE` | `int` | `23` |
| `ITEM_PROPERTY_IMMUNITY` | `int` | `24` |
| `ITEM_PROPERTY_IMPROVED_FORCE_RESISTANCE` | `int` | `25` |
| `ITEM_PROPERTY_IMPROVED_SAVING_THROW` | `int` | `26` |
| `ITEM_PROPERTY_IMPROVED_SAVING_THROW_SPECIFIC` | `int` | `27` |
| `ITEM_PROPERTY_KEEN` | `int` | `28` |
| `ITEM_PROPERTY_LIGHT` | `int` | `29` |
| `ITEM_PROPERTY_MIGHTY` | `int` | `30` |
| `ITEM_PROPERTY_NO_DAMAGE` | `int` | `31` |
| `ITEM_PROPERTY_ON_HIT_PROPERTIES` | `int` | `32` |
| `ITEM_PROPERTY_DECREASED_SAVING_THROWS` | `int` | `33` |
| `ITEM_PROPERTY_DECREASED_SAVING_THROWS_SPECIFIC` | `int` | `34` |
| `ITEM_PROPERTY_REGENERATION` | `int` | `35` |
| `ITEM_PROPERTY_SKILL_BONUS` | `int` | `36` |
| `ITEM_PROPERTY_SECURITY_SPIKE` | `int` | `37` |
| `ITEM_PROPERTY_ATTACK_BONUS` | `int` | `38` |
| `ITEM_PROPERTY_ATTACK_BONUS_VS_ALIGNMENT_GROUP` | `int` | `39` |
| `ITEM_PROPERTY_ATTACK_BONUS_VS_RACIAL_GROUP` | `int` | `40` |
| `ITEM_PROPERTY_DECREASED_ATTACK_MODIFIER` | `int` | `41` |
| `ITEM_PROPERTY_UNLIMITED_AMMUNITION` | `int` | `42` |
| `ITEM_PROPERTY_USE_LIMITATION_ALIGNMENT_GROUP` | `int` | `43` |
| `ITEM_PROPERTY_USE_LIMITATION_CLASS` | `int` | `44` |
| `ITEM_PROPERTY_USE_LIMITATION_RACIAL_TYPE` | `int` | `45` |
| `ITEM_PROPERTY_TRAP` | `int` | `46` |
| `ITEM_PROPERTY_TRUE_SEEING` | `int` | `47` |
| `ITEM_PROPERTY_ON_MONSTER_HIT` | `int` | `48` |
| `ITEM_PROPERTY_MASSIVE_CRITICALS` | `int` | `49` |
| `ITEM_PROPERTY_FREEDOM_OF_MOVEMENT` | `int` | `50` |
| `ITEM_PROPERTY_MONSTER_DAMAGE` | `int` | `51` |
| `ITEM_PROPERTY_SPECIAL_WALK` | `int` | `52` |
| `ITEM_PROPERTY_COMPUTER_SPIKE` | `int` | `53` |
| `ITEM_PROPERTY_REGENERATION_FORCE_POINTS` | `int` | `54` |
| `ITEM_PROPERTY_BLASTER_BOLT_DEFLECT_INCREASE` | `int` | `55` |
| `ITEM_PROPERTY_BLASTER_BOLT_DEFLECT_DECREASE` | `int` | `56` |
| `ITEM_PROPERTY_USE_LIMITATION_FEAT` | `int` | `57` |
| `ITEM_PROPERTY_DROID_REPAIR_KIT` | `int` | `58` |
| `BASE_ITEM_QUARTER_STAFF` | `int` | `0` |
| `BASE_ITEM_STUN_BATON` | `int` | `1` |
| `BASE_ITEM_LONG_SWORD` | `int` | `2` |
| `BASE_ITEM_VIBRO_SWORD` | `int` | `3` |
| `BASE_ITEM_SHORT_SWORD` | `int` | `4` |
| `BASE_ITEM_VIBRO_BLADE` | `int` | `5` |
| `BASE_ITEM_DOUBLE_BLADED_SWORD` | `int` | `6` |
| `BASE_ITEM_VIBRO_DOUBLE_BLADE` | `int` | `7` |
| `BASE_ITEM_LIGHTSABER` | `int` | `8` |
| `BASE_ITEM_DOUBLE_BLADED_LIGHTSABER` | `int` | `9` |
| `BASE_ITEM_SHORT_LIGHTSABER` | `int` | `10` |
| `BASE_ITEM_LIGHTSABER_CRYSTALS` | `int` | `11` |
| `BASE_ITEM_BLASTER_PISTOL` | `int` | `12` |
| `BASE_ITEM_HEAVY_BLASTER` | `int` | `13` |
| `BASE_ITEM_HOLD_OUT_BLASTER` | `int` | `14` |
| `BASE_ITEM_ION_BLASTER` | `int` | `15` |
| `BASE_ITEM_DISRUPTER_PISTOL` | `int` | `16` |
| `BASE_ITEM_SONIC_PISTOL` | `int` | `17` |
| `BASE_ITEM_ION_RIFLE` | `int` | `18` |
| `BASE_ITEM_BOWCASTER` | `int` | `19` |
| `BASE_ITEM_BLASTER_CARBINE` | `int` | `20` |
| `BASE_ITEM_DISRUPTER_RIFLE` | `int` | `21` |
| `BASE_ITEM_SONIC_RIFLE` | `int` | `22` |
| `BASE_ITEM_REPEATING_BLASTER` | `int` | `23` |
| `BASE_ITEM_HEAVY_REPEATING_BLASTER` | `int` | `24` |
| `BASE_ITEM_FRAGMENTATION_GRENADES` | `int` | `25` |
| `BASE_ITEM_STUN_GRENADES` | `int` | `26` |
| `BASE_ITEM_THERMAL_DETONATOR` | `int` | `27` |
| `BASE_ITEM_POISON_GRENADE` | `int` | `28` |
| `BASE_ITEM_FLASH_GRENADE` | `int` | `29` |
| `BASE_ITEM_SONIC_GRENADE` | `int` | `30` |
| `BASE_ITEM_ADHESIVE_GRENADE` | `int` | `31` |
| `BASE_ITEM_CRYOBAN_GRENADE` | `int` | `32` |
| `BASE_ITEM_FIRE_GRENADE` | `int` | `33` |
| `BASE_ITEM_ION_GRENADE` | `int` | `34` |
| `BASE_ITEM_JEDI_ROBE` | `int` | `35` |
| `BASE_ITEM_JEDI_KNIGHT_ROBE` | `int` | `36` |
| `BASE_ITEM_JEDI_MASTER_ROBE` | `int` | `37` |
| `BASE_ITEM_ARMOR_CLASS_4` | `int` | `38` |
| `BASE_ITEM_ARMOR_CLASS_5` | `int` | `39` |
| `BASE_ITEM_ARMOR_CLASS_6` | `int` | `40` |
| `BASE_ITEM_ARMOR_CLASS_7` | `int` | `41` |
| `BASE_ITEM_ARMOR_CLASS_8` | `int` | `42` |
| `BASE_ITEM_ARMOR_CLASS_9` | `int` | `43` |
| `BASE_ITEM_MASK` | `int` | `44` |
| `BASE_ITEM_GAUNTLETS` | `int` | `45` |
| `BASE_ITEM_FOREARM_BANDS` | `int` | `46` |
| `BASE_ITEM_BELT` | `int` | `47` |
| `BASE_ITEM_IMPLANT_1` | `int` | `48` |
| `BASE_ITEM_IMPLANT_2` | `int` | `49` |
| `BASE_ITEM_IMPLANT_3` | `int` | `50` |
| `BASE_ITEM_DATA_PAD` | `int` | `52` |
| `BASE_ITEM_ADRENALINE` | `int` | `53` |
| `BASE_ITEM_COMBAT_SHOTS` | `int` | `54` |
| `BASE_ITEM_MEDICAL_EQUIPMENT` | `int` | `55` |
| `BASE_ITEM_DROID_REPAIR_EQUIPMENT` | `int` | `56` |
| `BASE_ITEM_CREDITS` | `int` | `57` |
| `BASE_ITEM_TRAP_KIT` | `int` | `58` |
| `BASE_ITEM_SECURITY_SPIKES` | `int` | `59` |
| `BASE_ITEM_PROGRAMMING_SPIKES` | `int` | `60` |
| `BASE_ITEM_GLOW_ROD` | `int` | `61` |
| `BASE_ITEM_COLLAR_LIGHT` | `int` | `62` |
| `BASE_ITEM_TORCH` | `int` | `63` |
| `BASE_ITEM_PLOT_USEABLE_ITEMS` | `int` | `64` |
| `BASE_ITEM_AESTHETIC_ITEM` | `int` | `65` |
| `BASE_ITEM_DROID_LIGHT_PLATING` | `int` | `66` |
| `BASE_ITEM_DROID_MEDIUM_PLATING` | `int` | `67` |
| `BASE_ITEM_DROID_HEAVY_PLATING` | `int` | `68` |
| `BASE_ITEM_DROID_SEARCH_SCOPE` | `int` | `69` |
| `BASE_ITEM_DROID_MOTION_SENSORS` | `int` | `70` |
| `BASE_ITEM_DROID_SONIC_SENSORS` | `int` | `71` |
| `BASE_ITEM_DROID_TARGETING_COMPUTERS` | `int` | `72` |
| `BASE_ITEM_DROID_COMPUTER_SPIKE_MOUNT` | `int` | `73` |
| `BASE_ITEM_DROID_SECURITY_SPIKE_MOUNT` | `int` | `74` |
| `BASE_ITEM_DROID_SHIELD` | `int` | `75` |
| `BASE_ITEM_DROID_UTILITY_DEVICE` | `int` | `76` |
| `BASE_ITEM_BLASTER_RIFLE` | `int` | `77` |
| `BASE_ITEM_GHAFFI_STICK` | `int` | `78` |
| `BASE_ITEM_WOOKIE_WARBLADE` | `int` | `79` |
| `BASE_ITEM_GAMMOREAN_BATTLEAXE` | `int` | `80` |
| `BASE_ITEM_CREATURE_ITEM_SLASH` | `int` | `81` |
| `BASE_ITEM_CREATURE_ITEM_PIERCE` | `int` | `82` |
| `BASE_ITEM_CREATURE_WEAPON_SL_PRC` | `int` | `83` |
| `BASE_ITEM_CREATURE_HIDE_ITEM` | `int` | `84` |
| `BASE_ITEM_BASIC_CLOTHING` | `int` | `85` |
| `BASE_ITEM_INVALID` | `int` | `256` |
| `ATTACK_RESULT_INVALID` | `int` | `0` |
| `ATTACK_RESULT_HIT_SUCCESSFUL` | `int` | `1` |
| `ATTACK_RESULT_CRITICAL_HIT` | `int` | `2` |
| `ATTACK_RESULT_AUTOMATIC_HIT` | `int` | `3` |
| `ATTACK_RESULT_MISS` | `int` | `4` |
| `ATTACK_RESULT_ATTACK_RESISTED` | `int` | `5` |
| `ATTACK_RESULT_ATTACK_FAILED` | `int` | `6` |
| `ATTACK_RESULT_PARRIED` | `int` | `8` |
| `ATTACK_RESULT_DEFLECTED` | `int` | `9` |
| `AOE_PER_FOGACID` | `int` | `0` |
| `AOE_PER_FOGFIRE` | `int` | `1` |
| `AOE_PER_FOGSTINK` | `int` | `2` |
| `AOE_PER_FOGKILL` | `int` | `3` |
| `AOE_PER_FOGMIND` | `int` | `4` |
| `AOE_PER_WALLFIRE` | `int` | `5` |
| `AOE_PER_WALLWIND` | `int` | `6` |
| `AOE_PER_WALLBLADE` | `int` | `7` |
| `AOE_PER_WEB` | `int` | `8` |
| `AOE_PER_ENTANGLE` | `int` | `9` |
| `AOE_PER_DARKNESS` | `int` | `11` |
| `AOE_MOB_CIRCEVIL` | `int` | `12` |
| `AOE_MOB_CIRCGOOD` | `int` | `13` |
| `AOE_MOB_CIRCLAW` | `int` | `14` |
| `AOE_MOB_CIRCCHAOS` | `int` | `15` |
| `AOE_MOB_FEAR` | `int` | `16` |
| `AOE_MOB_BLINDING` | `int` | `17` |
| `AOE_MOB_UNEARTHLY` | `int` | `18` |
| `AOE_MOB_MENACE` | `int` | `19` |
| `AOE_MOB_UNNATURAL` | `int` | `20` |
| `AOE_MOB_STUN` | `int` | `21` |
| `AOE_MOB_PROTECTION` | `int` | `22` |
| `AOE_MOB_FIRE` | `int` | `23` |
| `AOE_MOB_FROST` | `int` | `24` |
| `AOE_MOB_ELECTRICAL` | `int` | `25` |
| `AOE_PER_FOGGHOUL` | `int` | `26` |
| `AOE_MOB_TYRANT_FOG` | `int` | `27` |
| `AOE_PER_STORM` | `int` | `28` |
| `AOE_PER_INVIS_SPHERE` | `int` | `29` |
| `AOE_MOB_SILENCE` | `int` | `30` |
| `AOE_PER_DELAY_BLAST_FIREBALL` | `int` | `31` |
| `AOE_PER_GREASE` | `int` | `32` |
| `AOE_PER_CREEPING_DOOM` | `int` | `33` |
| `AOE_PER_EVARDS_BLACK_TENTACLES` | `int` | `34` |
| `AOE_MOB_INVISIBILITY_PURGE` | `int` | `35` |
| `AOE_MOB_DRAGON_FEAR` | `int` | `36` |
| `FORCE_POWER_ALL_FORCE_POWERS` | `int` | `-1` |
| `FORCE_POWER_MASTER_ALTER` | `int` | `0` |
| `FORCE_POWER_MASTER_CONTROL` | `int` | `1` |
| `FORCE_POWER_MASTER_SENSE` | `int` | `2` |
| `FORCE_POWER_FORCE_JUMP_ADVANCED` | `int` | `3` |
| `FORCE_POWER_LIGHT_SABER_THROW_ADVANCED` | `int` | `4` |
| `FORCE_POWER_REGNERATION_ADVANCED` | `int` | `5` |
| `FORCE_POWER_AFFECT_MIND` | `int` | `6` |
| `FORCE_POWER_AFFLICTION` | `int` | `7` |
| `FORCE_POWER_SPEED_BURST` | `int` | `8` |
| `FORCE_POWER_CHOKE` | `int` | `9` |
| `FORCE_POWER_CURE` | `int` | `10` |
| `FORCE_POWER_DEATH_FIELD` | `int` | `11` |
| `FORCE_POWER_DROID_DISABLE` | `int` | `12` |
| `FORCE_POWER_DROID_DESTROY` | `int` | `13` |
| `FORCE_POWER_DOMINATE` | `int` | `14` |
| `FORCE_POWER_DRAIN_LIFE` | `int` | `15` |
| `FORCE_POWER_FEAR` | `int` | `16` |
| `FORCE_POWER_FORCE_ARMOR` | `int` | `17` |
| `FORCE_POWER_FORCE_AURA` | `int` | `18` |
| `FORCE_POWER_FORCE_BREACH` | `int` | `19` |
| `FORCE_POWER_FORCE_IMMUNITY` | `int` | `20` |
| `FORCE_POWER_FORCE_JUMP` | `int` | `21` |
| `FORCE_POWER_FORCE_MIND` | `int` | `22` |
| `FORCE_POWER_FORCE_PUSH` | `int` | `23` |
| `FORCE_POWER_FORCE_SHIELD` | `int` | `24` |
| `FORCE_POWER_FORCE_STORM` | `int` | `25` |
| `FORCE_POWER_FORCE_WAVE` | `int` | `26` |
| `FORCE_POWER_FORCE_WHIRLWIND` | `int` | `27` |
| `FORCE_POWER_HEAL` | `int` | `28` |
| `FORCE_POWER_HOLD` | `int` | `29` |
| `FORCE_POWER_HORROR` | `int` | `30` |
| `FORCE_POWER_INSANITY` | `int` | `31` |
| `FORCE_POWER_KILL` | `int` | `32` |
| `FORCE_POWER_KNIGHT_MIND` | `int` | `33` |
| `FORCE_POWER_KNIGHT_SPEED` | `int` | `34` |
| `FORCE_POWER_LIGHTNING` | `int` | `35` |
| `FORCE_POWER_MIND_MASTERY` | `int` | `36` |
| `FORCE_POWER_SPEED_MASTERY` | `int` | `37` |
| `FORCE_POWER_PLAGUE` | `int` | `38` |
| `FORCE_POWER_REGENERATION` | `int` | `39` |
| `FORCE_POWER_RESIST_COLD_HEAT_ENERGY` | `int` | `40` |
| `FORCE_POWER_RESIST_FORCE` | `int` | `41` |
| `FORCE_POWER_RESIST_POISON_DISEASE_SONIC` | `int` | `42` |
| `FORCE_POWER_SHOCK` | `int` | `43` |
| `FORCE_POWER_SLEEP` | `int` | `44` |
| `FORCE_POWER_SLOW` | `int` | `45` |
| `FORCE_POWER_STUN` | `int` | `46` |
| `FORCE_POWER_DROID_STUN` | `int` | `47` |
| `FORCE_POWER_SUPRESS_FORCE` | `int` | `48` |
| `FORCE_POWER_LIGHT_SABER_THROW` | `int` | `49` |
| `FORCE_POWER_WOUND` | `int` | `50` |
| `SPECIAL_ABILITY_BATTLE_MEDITATION` | `int` | `51` |
| `SPECIAL_ABILITY_BODY_FUEL` | `int` | `52` |
| `SPECIAL_ABILITY_COMBAT_REGENERATION` | `int` | `53` |
| `SPECIAL_ABILITY_WARRIOR_STANCE` | `int` | `54` |
| `SPECIAL_ABILITY_SENTINEL_STANCE` | `int` | `55` |
| `SPECIAL_ABILITY_DOMINATE_MIND` | `int` | `56` |
| `SPECIAL_ABILITY_PSYCHIC_STANCE` | `int` | `57` |
| `SPECIAL_ABILITY_CATHAR_REFLEXES` | `int` | `58` |
| `SPECIAL_ABILITY_ENHANCED_SENSES` | `int` | `59` |
| `SPECIAL_ABILITY_CAMOFLAGE` | `int` | `60` |
| `SPECIAL_ABILITY_TAUNT` | `int` | `61` |
| `SPECIAL_ABILITY_WHIRLING_DERVISH` | `int` | `62` |
| `SPECIAL_ABILITY_RAGE` | `int` | `63` |
| `POISON_ABILITY_SCORE_MILD` | `int` | `0` |
| `POISON_ABILITY_SCORE_AVERAGE` | `int` | `1` |
| `POISON_ABILITY_SCORE_VIRULENT` | `int` | `2` |
| `POISON_DAMAGE_MILD` | `int` | `3` |
| `POISON_DAMAGE_AVERAGE` | `int` | `4` |
| `POISON_DAMAGE_VIRULENT` | `int` | `5` |
| `CREATURE_TYPE_RACIAL_TYPE` | `int` | `0` |
| `CREATURE_TYPE_PLAYER_CHAR` | `int` | `1` |
| `CREATURE_TYPE_CLASS` | `int` | `2` |
| `CREATURE_TYPE_REPUTATION` | `int` | `3` |
| `CREATURE_TYPE_IS_ALIVE` | `int` | `4` |
| `CREATURE_TYPE_HAS_SPELL_EFFECT` | `int` | `5` |
| `CREATURE_TYPE_DOES_NOT_HAVE_SPELL_EFFECT` | `int` | `6` |
| `CREATURE_TYPE_PERCEPTION` | `int` | `7` |
| `REPUTATION_TYPE_FRIEND` | `int` | `0` |
| `REPUTATION_TYPE_ENEMY` | `int` | `1` |
| `REPUTATION_TYPE_NEUTRAL` | `int` | `2` |
| `PERCEPTION_SEEN_AND_HEARD` | `int` | `0` |
| `PERCEPTION_NOT_SEEN_AND_NOT_HEARD` | `int` | `1` |
| `PERCEPTION_HEARD_AND_NOT_SEEN` | `int` | `2` |
| `PERCEPTION_SEEN_AND_NOT_HEARD` | `int` | `3` |
| `PERCEPTION_NOT_HEARD` | `int` | `4` |
| `PERCEPTION_HEARD` | `int` | `5` |
| `PERCEPTION_NOT_SEEN` | `int` | `6` |
| `PERCEPTION_SEEN` | `int` | `7` |
| `PLAYER_CHAR_NOT_PC` | `int` | `0` |
| `PLAYER_CHAR_IS_PC` | `int` | `1` |
| `PERSISTENT_ZONE_ACTIVE` | `int` | `0` |
| `PERSISTENT_ZONE_FOLLOW` | `int` | `1` |
| `INVALID_STANDARD_FACTION` | `int` | `-1` |
| `STANDARD_FACTION_HOSTILE_1` | `int` | `1` |
| `STANDARD_FACTION_FRIENDLY_1` | `int` | `2` |
| `STANDARD_FACTION_HOSTILE_2` | `int` | `3` |
| `STANDARD_FACTION_FRIENDLY_2` | `int` | `4` |
| `STANDARD_FACTION_NEUTRAL` | `int` | `5` |
| `STANDARD_FACTION_INSANE` | `int` | `6` |
| `STANDARD_FACTION_PTAT_TUSKAN` | `int` | `7` |
| `STANDARD_FACTION_GLB_XOR` | `int` | `8` |
| `STANDARD_FACTION_SURRENDER_1` | `int` | `9` |
| `STANDARD_FACTION_SURRENDER_2` | `int` | `10` |
| `STANDARD_FACTION_PREDATOR` | `int` | `11` |
| `STANDARD_FACTION_PREY` | `int` | `12` |
| `STANDARD_FACTION_TRAP` | `int` | `13` |
| `STANDARD_FACTION_ENDAR_SPIRE` | `int` | `14` |
| `STANDARD_FACTION_RANCOR` | `int` | `15` |
| `STANDARD_FACTION_GIZKA_1` | `int` | `16` |
| `STANDARD_FACTION_GIZKA_2` | `int` | `17` |
| `SKILL_COMPUTER_USE` | `int` | `0` |
| `SKILL_DEMOLITIONS` | `int` | `1` |
| `SKILL_STEALTH` | `int` | `2` |
| `SKILL_AWARENESS` | `int` | `3` |
| `SKILL_PERSUADE` | `int` | `4` |
| `SKILL_REPAIR` | `int` | `5` |
| `SKILL_SECURITY` | `int` | `6` |
| `SKILL_TREAT_INJURY` | `int` | `7` |
| `SKILL_MAX_SKILLS` | `int` | `8` |
| `SUBSKILL_FLAGTRAP` | `int` | `100` |
| `SUBSKILL_RECOVERTRAP` | `int` | `101` |
| `SUBSKILL_EXAMINETRAP` | `int` | `102` |
| `FEAT_ADVANCED_JEDI_DEFENSE` | `int` | `1` |
| `FEAT_ADVANCED_GUARD_STANCE` | `int` | `2` |
| `FEAT_AMBIDEXTERITY` | `int` | `3` |
| `FEAT_ARMOUR_PROF_HEAVY` | `int` | `4` |
| `FEAT_ARMOUR_PROF_LIGHT` | `int` | `5` |
| `FEAT_ARMOUR_PROF_MEDIUM` | `int` | `6` |
| `FEAT_CAUTIOUS` | `int` | `7` |
| `FEAT_CRITICAL_STRIKE` | `int` | `8` |
| `FEAT_DOUBLE_WEAPON_FIGHTING` | `int` | `9` |
| `FEAT_EMPATHY` | `int` | `10` |
| `FEAT_FLURRY` | `int` | `11` |
| `FEAT_GEAR_HEAD` | `int` | `12` |
| `FEAT_GREAT_FORTITUDE` | `int` | `13` |
| `FEAT_IMPLANT_LEVEL_1` | `int` | `14` |
| `FEAT_IMPLANT_LEVEL_2` | `int` | `15` |
| `FEAT_IMPLANT_LEVEL_3` | `int` | `16` |
| `FEAT_IMPROVED_POWER_ATTACK` | `int` | `17` |
| `FEAT_IMPROVED_POWER_BLAST` | `int` | `18` |
| `FEAT_IMPROVED_CRITICAL_STRIKE` | `int` | `19` |
| `FEAT_IMPROVED_SNIPER_SHOT` | `int` | `20` |
| `FEAT_IRON_WILL` | `int` | `21` |
| `FEAT_LIGHTNING_REFLEXES` | `int` | `22` |
| `FEAT_MASTER_JEDI_DEFENSE` | `int` | `24` |
| `FEAT_MASTER_GUARD_STANCE` | `int` | `25` |
| `FEAT_MULTI_SHOT` | `int` | `26` |
| `FEAT_PERCEPTIVE` | `int` | `27` |
| `FEAT_POWER_ATTACK` | `int` | `28` |
| `FEAT_POWER_BLAST` | `int` | `29` |
| `FEAT_RAPID_SHOT` | `int` | `30` |
| `FEAT_SNIPER_SHOT` | `int` | `31` |
| `FEAT_WEAPON_FOCUS_BLASTER` | `int` | `32` |
| `FEAT_WEAPON_FOCUS_BLASTER_RIFLE` | `int` | `33` |
| `FEAT_WEAPON_FOCUS_GRENADE` | `int` | `34` |
| `FEAT_WEAPON_FOCUS_HEAVY_WEAPONS` | `int` | `35` |
| `FEAT_WEAPON_FOCUS_LIGHTSABER` | `int` | `36` |
| `FEAT_WEAPON_FOCUS_MELEE_WEAPONS` | `int` | `37` |
| `FEAT_WEAPON_FOCUS_SIMPLE_WEAPONS` | `int` | `38` |
| `FEAT_WEAPON_PROFICIENCY_BLASTER` | `int` | `39` |
| `FEAT_WEAPON_PROFICIENCY_BLASTER_RIFLE` | `int` | `40` |
| `FEAT_WEAPON_PROFICIENCY_GRENADE` | `int` | `41` |
| `FEAT_WEAPON_PROFICIENCY_HEAVY_WEAPONS` | `int` | `42` |
| `FEAT_WEAPON_PROFICIENCY_LIGHTSABER` | `int` | `43` |
| `FEAT_WEAPON_PROFICIENCY_MELEE_WEAPONS` | `int` | `44` |
| `FEAT_WEAPON_PROFICIENCY_SIMPLE_WEAPONS` | `int` | `45` |
| `FEAT_WEAPON_SPECIALIZATION_BLASTER` | `int` | `46` |
| `FEAT_WEAPON_SPECIALIZATION_BLASTER_RIFLE` | `int` | `47` |
| `FEAT_WEAPON_SPECIALIZATION_GRENADE` | `int` | `48` |
| `FEAT_WEAPON_SPECIALIZATION_HEAVY_WEAPONS` | `int` | `49` |
| `FEAT_WEAPON_SPECIALIZATION_LIGHTSABER` | `int` | `50` |
| `FEAT_WEAPON_SPECIALIZATION_MELEE_WEAPONS` | `int` | `51` |
| `FEAT_WEAPON_SPECIALIZATION_SIMPLE_WEAPONS` | `int` | `52` |
| `FEAT_WHIRLWIND_ATTACK` | `int` | `53` |
| `FEAT_GUARD_STANCE` | `int` | `54` |
| `FEAT_JEDI_DEFENSE` | `int` | `55` |
| `FEAT_UNCANNY_DODGE_1` | `int` | `56` |
| `FEAT_UNCANNY_DODGE_2` | `int` | `57` |
| `FEAT_SKILL_FOCUS_COMPUTER_USE` | `int` | `58` |
| `FEAT_SNEAK_ATTACK_1D6` | `int` | `60` |
| `FEAT_SNEAK_ATTACK_2D6` | `int` | `61` |
| `FEAT_SNEAK_ATTACK_3D6` | `int` | `62` |
| `FEAT_SNEAK_ATTACK_4D6` | `int` | `63` |
| `FEAT_SNEAK_ATTACK_5D6` | `int` | `64` |
| `FEAT_SNEAK_ATTACK_6D6` | `int` | `65` |
| `FEAT_SNEAK_ATTACK_7D6` | `int` | `66` |
| `FEAT_SNEAK_ATTACK_8D6` | `int` | `67` |
| `FEAT_SNEAK_ATTACK_9D6` | `int` | `68` |
| `FEAT_SNEAK_ATTACK_10D6` | `int` | `69` |
| `FEAT_SKILL_FOCUS_DEMOLITIONS` | `int` | `70` |
| `FEAT_SKILL_FOCUS_STEALTH` | `int` | `71` |
| `FEAT_SKILL_FOCUS_AWARENESS` | `int` | `72` |
| `FEAT_SKILL_FOCUS_PERSUADE` | `int` | `73` |
| `FEAT_SKILL_FOCUS_REPAIR` | `int` | `74` |
| `FEAT_SKILL_FOCUS_SECURITY` | `int` | `75` |
| `FEAT_SKILL_FOCUS_TREAT_INJUURY` | `int` | `76` |
| `FEAT_MASTER_SNIPER_SHOT` | `int` | `77` |
| `FEAT_DROID_UPGRADE_1` | `int` | `78` |
| `FEAT_DROID_UPGRADE_2` | `int` | `79` |
| `FEAT_DROID_UPGRADE_3` | `int` | `80` |
| `FEAT_MASTER_CRITICAL_STRIKE` | `int` | `81` |
| `FEAT_MASTER_POWER_BLAST` | `int` | `82` |
| `FEAT_MASTER_POWER_ATTACK` | `int` | `83` |
| `FEAT_TOUGHNESS` | `int` | `84` |
| `FEAT_ADVANCED_DOUBLE_WEAPON_FIGHTING` | `int` | `85` |
| `FEAT_FORCE_FOCUS_ALTER` | `int` | `86` |
| `FEAT_FORCE_FOCUS_CONTROL` | `int` | `87` |
| `FEAT_FORCE_FOCUS_SENSE` | `int` | `88` |
| `FEAT_FORCE_FOCUS_ADVANCED` | `int` | `89` |
| `FEAT_FORCE_FOCUS_MASTERY` | `int` | `90` |
| `FEAT_IMPROVED_FLURRY` | `int` | `91` |
| `FEAT_IMPROVED_RAPID_SHOT` | `int` | `92` |
| `FEAT_PROFICIENCY_ALL` | `int` | `93` |
| `FEAT_BATTLE_MEDITATION` | `int` | `94` |
| `SPECIAL_ATTACK_INVALID` | `int` | `0` |
| `SPECIAL_ATTACK_CALLED_SHOT_LEG` | `int` | `1` |
| `SPECIAL_ATTACK_CALLED_SHOT_ARM` | `int` | `2` |
| `SPECIAL_ATTACK_SAP` | `int` | `3` |
| `SPECIAL_ATTACK_DISARM` | `int` | `4` |
| `SPECIAL_ATTACK_IMPROVED_DISARM` | `int` | `5` |
| `SPECIAL_ATTACK_KNOCKDOWN` | `int` | `6` |
| `SPECIAL_ATTACK_IMPROVED_KNOCKDOWN` | `int` | `7` |
| `SPECIAL_ATTACK_STUNNING_FIST` | `int` | `8` |
| `SPECIAL_ATTACK_FLURRY_OF_BLOWS` | `int` | `9` |
| `SPECIAL_ATTACK_RAPID_SHOT` | `int` | `10` |
| `COMBAT_MODE_INVALID` | `int` | `0` |
| `COMBAT_MODE_PARRY` | `int` | `1` |
| `COMBAT_MODE_POWER_ATTACK` | `int` | `2` |
| `COMBAT_MODE_IMPROVED_POWER_ATTACK` | `int` | `3` |
| `COMBAT_MODE_FLURRY_OF_BLOWS` | `int` | `4` |
| `COMBAT_MODE_RAPID_SHOT` | `int` | `5` |
| `ENCOUNTER_DIFFICULTY_VERY_EASY` | `int` | `0` |
| `ENCOUNTER_DIFFICULTY_EASY` | `int` | `1` |
| `ENCOUNTER_DIFFICULTY_NORMAL` | `int` | `2` |
| `ENCOUNTER_DIFFICULTY_HARD` | `int` | `3` |
| `ENCOUNTER_DIFFICULTY_IMPOSSIBLE` | `int` | `4` |
| `ANIMATION_LOOPING_PAUSE` | `int` | `0` |
| `ANIMATION_LOOPING_PAUSE2` | `int` | `1` |
| `ANIMATION_LOOPING_LISTEN` | `int` | `2` |
| `ANIMATION_LOOPING_MEDITATE` | `int` | `3` |
| `ANIMATION_LOOPING_WORSHIP` | `int` | `4` |
| `ANIMATION_LOOPING_TALK_NORMAL` | `int` | `5` |
| `ANIMATION_LOOPING_TALK_PLEADING` | `int` | `6` |
| `ANIMATION_LOOPING_TALK_FORCEFUL` | `int` | `7` |
| `ANIMATION_LOOPING_TALK_LAUGHING` | `int` | `8` |
| `ANIMATION_LOOPING_TALK_SAD` | `int` | `9` |
| `ANIMATION_LOOPING_GET_LOW` | `int` | `10` |
| `ANIMATION_LOOPING_GET_MID` | `int` | `11` |
| `ANIMATION_LOOPING_PAUSE_TIRED` | `int` | `12` |
| `ANIMATION_LOOPING_PAUSE_DRUNK` | `int` | `13` |
| `ANIMATION_LOOPING_FLIRT` | `int` | `14` |
| `ANIMATION_LOOPING_USE_COMPUTER` | `int` | `15` |
| `ANIMATION_LOOPING_DANCE` | `int` | `16` |
| `ANIMATION_LOOPING_DANCE1` | `int` | `17` |
| `ANIMATION_LOOPING_HORROR` | `int` | `18` |
| `ANIMATION_LOOPING_READY` | `int` | `19` |
| `ANIMATION_LOOPING_DEACTIVATE` | `int` | `20` |
| `ANIMATION_LOOPING_SPASM` | `int` | `21` |
| `ANIMATION_LOOPING_SLEEP` | `int` | `22` |
| `ANIMATION_LOOPING_PRONE` | `int` | `23` |
| `ANIMATION_LOOPING_PAUSE3` | `int` | `24` |
| `ANIMATION_LOOPING_WELD` | `int` | `25` |
| `ANIMATION_LOOPING_DEAD` | `int` | `26` |
| `ANIMATION_LOOPING_TALK_INJURED` | `int` | `27` |
| `ANIMATION_LOOPING_LISTEN_INJURED` | `int` | `28` |
| `ANIMATION_LOOPING_TREAT_INJURED` | `int` | `29` |
| `ANIMATION_LOOPING_DEAD_PRONE` | `int` | `30` |
| `ANIMATION_LOOPING_KNEEL_TALK_ANGRY` | `int` | `31` |
| `ANIMATION_LOOPING_KNEEL_TALK_SAD` | `int` | `32` |
| `ANIMATION_LOOPING_CHOKE` | `int` | `116` |
| `ANIMATION_FIREFORGET_HEAD_TURN_LEFT` | `int` | `100` |
| `ANIMATION_FIREFORGET_HEAD_TURN_RIGHT` | `int` | `101` |
| `ANIMATION_FIREFORGET_PAUSE_SCRATCH_HEAD` | `int` | `102` |
| `ANIMATION_FIREFORGET_PAUSE_BORED` | `int` | `103` |
| `ANIMATION_FIREFORGET_SALUTE` | `int` | `104` |
| `ANIMATION_FIREFORGET_BOW` | `int` | `105` |
| `ANIMATION_FIREFORGET_GREETING` | `int` | `106` |
| `ANIMATION_FIREFORGET_TAUNT` | `int` | `107` |
| `ANIMATION_FIREFORGET_VICTORY1` | `int` | `108` |
| `ANIMATION_FIREFORGET_VICTORY2` | `int` | `109` |
| `ANIMATION_FIREFORGET_VICTORY3` | `int` | `110` |
| `ANIMATION_FIREFORGET_INJECT` | `int` | `112` |
| `ANIMATION_FIREFORGET_USE_COMPUTER` | `int` | `113` |
| `ANIMATION_FIREFORGET_PERSUADE` | `int` | `114` |
| `ANIMATION_FIREFORGET_ACTIVATE` | `int` | `115` |
| `ANIMATION_FIREFORGET_CHOKE` | `int` | `116` |
| `ANIMATION_FIREFORGET_THROW_HIGH` | `int` | `117` |
| `ANIMATION_FIREFORGET_THROW_LOW` | `int` | `118` |
| `ANIMATION_FIREFORGET_CUSTOM01` | `int` | `119` |
| `ANIMATION_FIREFORGET_TREAT_INJURED` | `int` | `120` |
| `ANIMATION_PLACEABLE_ACTIVATE` | `int` | `200` |
| `ANIMATION_PLACEABLE_DEACTIVATE` | `int` | `201` |
| `ANIMATION_PLACEABLE_OPEN` | `int` | `202` |
| `ANIMATION_PLACEABLE_CLOSE` | `int` | `203` |
| `ANIMATION_PLACEABLE_ANIMLOOP01` | `int` | `204` |
| `ANIMATION_PLACEABLE_ANIMLOOP02` | `int` | `205` |
| `ANIMATION_PLACEABLE_ANIMLOOP03` | `int` | `206` |
| `ANIMATION_PLACEABLE_ANIMLOOP04` | `int` | `207` |
| `ANIMATION_PLACEABLE_ANIMLOOP05` | `int` | `208` |
| `ANIMATION_PLACEABLE_ANIMLOOP06` | `int` | `209` |
| `ANIMATION_PLACEABLE_ANIMLOOP07` | `int` | `210` |
| `ANIMATION_PLACEABLE_ANIMLOOP08` | `int` | `211` |
| `ANIMATION_PLACEABLE_ANIMLOOP09` | `int` | `212` |
| `ANIMATION_PLACEABLE_ANIMLOOP10` | `int` | `213` |
| `ANIMATION_ROOM_SCRIPTLOOP01` | `int` | `1` |
| `ANIMATION_ROOM_SCRIPTLOOP02` | `int` | `2` |
| `ANIMATION_ROOM_SCRIPTLOOP03` | `int` | `3` |
| `ANIMATION_ROOM_SCRIPTLOOP04` | `int` | `4` |
| `ANIMATION_ROOM_SCRIPTLOOP05` | `int` | `5` |
| `ANIMATION_ROOM_SCRIPTLOOP06` | `int` | `6` |
| `ANIMATION_ROOM_SCRIPTLOOP07` | `int` | `7` |
| `ANIMATION_ROOM_SCRIPTLOOP08` | `int` | `8` |
| `ANIMATION_ROOM_SCRIPTLOOP09` | `int` | `9` |
| `ANIMATION_ROOM_SCRIPTLOOP10` | `int` | `10` |
| `ANIMATION_ROOM_SCRIPTLOOP11` | `int` | `11` |
| `ANIMATION_ROOM_SCRIPTLOOP12` | `int` | `12` |
| `ANIMATION_ROOM_SCRIPTLOOP13` | `int` | `13` |
| `ANIMATION_ROOM_SCRIPTLOOP14` | `int` | `14` |
| `ANIMATION_ROOM_SCRIPTLOOP15` | `int` | `15` |
| `ANIMATION_ROOM_SCRIPTLOOP16` | `int` | `16` |
| `ANIMATION_ROOM_SCRIPTLOOP17` | `int` | `17` |
| `ANIMATION_ROOM_SCRIPTLOOP18` | `int` | `18` |
| `ANIMATION_ROOM_SCRIPTLOOP19` | `int` | `19` |
| `ANIMATION_ROOM_SCRIPTLOOP20` | `int` | `20` |
| `TALENT_TYPE_FORCE` | `int` | `0` |
| `TALENT_TYPE_SPELL` | `int` | `0` |
| `TALENT_TYPE_FEAT` | `int` | `1` |
| `TALENT_TYPE_SKILL` | `int` | `2` |
| `TALENT_EXCLUDE_ALL_OF_TYPE` | `int` | `-1` |
| `INVENTORY_DISTURB_TYPE_ADDED` | `int` | `0` |
| `INVENTORY_DISTURB_TYPE_REMOVED` | `int` | `1` |
| `INVENTORY_DISTURB_TYPE_STOLEN` | `int` | `2` |
| `GUI_PANEL_PLAYER_DEATH` | `int` | `0` |
| `POLYMORPH_TYPE_WEREWOLF` | `int` | `0` |
| `POLYMORPH_TYPE_WERERAT` | `int` | `1` |
| `POLYMORPH_TYPE_WERECAT` | `int` | `2` |
| `POLYMORPH_TYPE_GIANT_SPIDER` | `int` | `3` |
| `POLYMORPH_TYPE_TROLL` | `int` | `4` |
| `POLYMORPH_TYPE_UMBER_HULK` | `int` | `5` |
| `POLYMORPH_TYPE_PIXIE` | `int` | `6` |
| `POLYMORPH_TYPE_ZOMBIE` | `int` | `7` |
| `POLYMORPH_TYPE_RED_DRAGON` | `int` | `8` |
| `POLYMORPH_TYPE_FIRE_GIANT` | `int` | `9` |
| `POLYMORPH_TYPE_BALOR` | `int` | `10` |
| `POLYMORPH_TYPE_DEATH_SLAAD` | `int` | `11` |
| `POLYMORPH_TYPE_IRON_GOLEM` | `int` | `12` |
| `POLYMORPH_TYPE_HUGE_FIRE_ELEMENTAL` | `int` | `13` |
| `POLYMORPH_TYPE_HUGE_WATER_ELEMENTAL` | `int` | `14` |
| `POLYMORPH_TYPE_HUGE_EARTH_ELEMENTAL` | `int` | `15` |
| `POLYMORPH_TYPE_HUGE_AIR_ELEMENTAL` | `int` | `16` |
| `POLYMORPH_TYPE_ELDER_FIRE_ELEMENTAL` | `int` | `17` |
| `POLYMORPH_TYPE_ELDER_WATER_ELEMENTAL` | `int` | `18` |
| `POLYMORPH_TYPE_ELDER_EARTH_ELEMENTAL` | `int` | `19` |
| `POLYMORPH_TYPE_ELDER_AIR_ELEMENTAL` | `int` | `20` |
| `POLYMORPH_TYPE_BROWN_BEAR` | `int` | `21` |
| `POLYMORPH_TYPE_PANTHER` | `int` | `22` |
| `POLYMORPH_TYPE_WOLF` | `int` | `23` |
| `POLYMORPH_TYPE_BOAR` | `int` | `24` |
| `POLYMORPH_TYPE_BADGER` | `int` | `25` |
| `POLYMORPH_TYPE_PENGUIN` | `int` | `26` |
| `POLYMORPH_TYPE_COW` | `int` | `27` |
| `POLYMORPH_TYPE_DOOM_KNIGHT` | `int` | `28` |
| `POLYMORPH_TYPE_YUANTI` | `int` | `29` |
| `POLYMORPH_TYPE_IMP` | `int` | `30` |
| `POLYMORPH_TYPE_QUASIT` | `int` | `31` |
| `POLYMORPH_TYPE_SUCCUBUS` | `int` | `32` |
| `POLYMORPH_TYPE_DIRE_BROWN_BEAR` | `int` | `33` |
| `POLYMORPH_TYPE_DIRE_PANTHER` | `int` | `34` |
| `POLYMORPH_TYPE_DIRE_WOLF` | `int` | `35` |
| `POLYMORPH_TYPE_DIRE_BOAR` | `int` | `36` |
| `POLYMORPH_TYPE_DIRE_BADGER` | `int` | `37` |
| `INVISIBILITY_TYPE_NORMAL` | `int` | `1` |
| `INVISIBILITY_TYPE_DARKNESS` | `int` | `2` |
| `INVISIBILITY_TYPE_IMPROVED` | `int` | `4` |
| `CREATURE_SIZE_INVALID` | `int` | `0` |
| `CREATURE_SIZE_TINY` | `int` | `1` |
| `CREATURE_SIZE_SMALL` | `int` | `2` |
| `CREATURE_SIZE_MEDIUM` | `int` | `3` |
| `CREATURE_SIZE_LARGE` | `int` | `4` |
| `CREATURE_SIZE_HUGE` | `int` | `5` |
| `CAMERA_MODE_CHASE_CAMERA` | `int` | `0` |
| `CAMERA_MODE_TOP_DOWN` | `int` | `1` |
| `CAMERA_MODE_STIFF_CHASE_CAMERA` | `int` | `2` |
| `PROJECTILE_PATH_TYPE_DEFAULT` | `int` | `0` |
| `PROJECTILE_PATH_TYPE_HOMING` | `int` | `1` |
| `PROJECTILE_PATH_TYPE_BALLISTIC` | `int` | `2` |
| `PROJECTILE_PATH_TYPE_HIGH_BALLISTIC` | `int` | `3` |
| `PROJECTILE_PATH_TYPE_ACCELERATING` | `int` | `4` |
| `GAME_DIFFICULTY_VERY_EASY` | `int` | `0` |
| `GAME_DIFFICULTY_EASY` | `int` | `1` |
| `GAME_DIFFICULTY_NORMAL` | `int` | `2` |
| `GAME_DIFFICULTY_CORE_RULES` | `int` | `3` |
| `GAME_DIFFICULTY_DIFFICULT` | `int` | `4` |
| `ACTION_MOVETOPOINT` | `int` | `0` |
| `ACTION_PICKUPITEM` | `int` | `1` |
| `ACTION_DROPITEM` | `int` | `2` |
| `ACTION_ATTACKOBJECT` | `int` | `3` |
| `ACTION_CASTSPELL` | `int` | `4` |
| `ACTION_OPENDOOR` | `int` | `5` |
| `ACTION_CLOSEDOOR` | `int` | `6` |
| `ACTION_DIALOGOBJECT` | `int` | `7` |
| `ACTION_DISABLETRAP` | `int` | `8` |
| `ACTION_RECOVERTRAP` | `int` | `9` |
| `ACTION_FLAGTRAP` | `int` | `10` |
| `ACTION_EXAMINETRAP` | `int` | `11` |
| `ACTION_SETTRAP` | `int` | `12` |
| `ACTION_OPENLOCK` | `int` | `13` |
| `ACTION_LOCK` | `int` | `14` |
| `ACTION_USEOBJECT` | `int` | `15` |
| `ACTION_ANIMALEMPATHY` | `int` | `16` |
| `ACTION_REST` | `int` | `17` |
| `ACTION_TAUNT` | `int` | `18` |
| `ACTION_ITEMCASTSPELL` | `int` | `19` |
| `ACTION_COUNTERSPELL` | `int` | `31` |
| `ACTION_HEAL` | `int` | `33` |
| `ACTION_PICKPOCKET` | `int` | `34` |
| `ACTION_FOLLOW` | `int` | `35` |
| `ACTION_WAIT` | `int` | `36` |
| `ACTION_SIT` | `int` | `37` |
| `ACTION_FOLLOWLEADER` | `int` | `38` |
| `ACTION_INVALID` | `int` | `65535` |
| `ACTION_QUEUEEMPTY` | `int` | `65534` |
| `TRAP_BASE_TYPE_FLASH_STUN_MINOR` | `int` | `0` |
| `TRAP_BASE_TYPE_FLASH_STUN_AVERAGE` | `int` | `1` |
| `TRAP_BASE_TYPE_FLASH_STUN_DEADLY` | `int` | `2` |
| `TRAP_BASE_TYPE_FRAGMENTATION_MINE_MINOR` | `int` | `3` |
| `TRAP_BASE_TYPE_FRAGMENTATION_MINE_AVERAGE` | `int` | `4` |
| `TRAP_BASE_TYPE_FRAGMENTATION_MINE_DEADLY` | `int` | `5` |
| `TRAP_BASE_TYPE_LASER_SLICING_MINOR` | `int` | `6` |
| `TRAP_BASE_TYPE_LASER_SLICING_AVERAGE` | `int` | `7` |
| `TRAP_BASE_TYPE_LASER_SLICING_DEADLY` | `int` | `8` |
| `TRAP_BASE_TYPE_POISON_GAS_MINOR` | `int` | `9` |
| `TRAP_BASE_TYPE_POISON_GAS_AVERAGE` | `int` | `10` |
| `TRAP_BASE_TYPE_POISON_GAS_DEADLY` | `int` | `11` |
| `SWMINIGAME_TRACKFOLLOWER_SOUND_ENGINE` | `int` | `0` |
| `SWMINIGAME_TRACKFOLLOWER_SOUND_DEATH` | `int` | `1` |
| `CONVERSATION_TYPE_CINEMATIC` | `int` | `0` |
| `CONVERSATION_TYPE_COMPUTER` | `int` | `1` |
| `PARTY_AISTYLE_AGGRESSIVE` | `int` | `0` |
| `PARTY_AISTYLE_DEFENSIVE` | `int` | `1` |
| `PARTY_AISTYLE_PASSIVE` | `int` | `2` |
| `DISGUISE_TYPE_TEST` | `int` | `1` |
| `DISGUISE_TYPE_P_T3M3` | `int` | `2` |
| `DISGUISE_TYPE_P_HK47` | `int` | `3` |
| `DISGUISE_TYPE_P_BASTILLA` | `int` | `4` |
| `DISGUISE_TYPE_P_CAND` | `int` | `5` |
| `DISGUISE_TYPE_P_CARTH` | `int` | `6` |
| `DISGUISE_TYPE_P_JOLEE` | `int` | `7` |
| `DISGUISE_TYPE_P_JUHANI` | `int` | `8` |
| `DISGUISE_TYPE_P_ZAALBAR` | `int` | `9` |
| `DISGUISE_TYPE_P_MISSION` | `int` | `10` |
| `DISGUISE_TYPE_N_ADMRLSAULKAR` | `int` | `11` |
| `DISGUISE_TYPE_N_BITH` | `int` | `12` |
| `DISGUISE_TYPE_N_CALONORD` | `int` | `13` |
| `DISGUISE_TYPE_N_COMMF` | `int` | `14` |
| `DISGUISE_TYPE_N_COMMKIDF` | `int` | `15` |
| `DISGUISE_TYPE_N_COMMKIDM` | `int` | `16` |
| `DISGUISE_TYPE_N_COMMM` | `int` | `17` |
| `DISGUISE_TYPE_N_CZERLAOFF` | `int` | `18` |
| `DISGUISE_TYPE_N_DARKJEDIF` | `int` | `19` |
| `DISGUISE_TYPE_N_DARKJEDIM` | `int` | `20` |
| `DISGUISE_TYPE_N_DARTHMALAK` | `int` | `21` |
| `DISGUISE_TYPE_N_DARTHREVAN` | `int` | `22` |
| `DISGUISE_TYPE_N_DODONNA` | `int` | `23` |
| `DISGUISE_TYPE_N_DUROS` | `int` | `24` |
| `DISGUISE_TYPE_N_FATCOMF` | `int` | `25` |
| `DISGUISE_TYPE_N_FATCOMM` | `int` | `26` |
| `DISGUISE_TYPE_N_SMUGGLER` | `int` | `27` |
| `DISGUISE_TYPE_N_SITHSOLDIER` | `int` | `28` |
| `DISGUISE_TYPE_N_JEDICOUNTF` | `int` | `30` |
| `DISGUISE_TYPE_N_JEDICOUNTM` | `int` | `31` |
| `DISGUISE_TYPE_N_JEDIMALEK` | `int` | `32` |
| `DISGUISE_TYPE_N_JEDIMEMF` | `int` | `33` |
| `DISGUISE_TYPE_N_JEDIMEMM` | `int` | `34` |
| `DISGUISE_TYPE_N_MANDALORIAN` | `int` | `35` |
| `DISGUISE_TYPE_N_RAKATA` | `int` | `36` |
| `DISGUISE_TYPE_N_REPOFF` | `int` | `37` |
| `DISGUISE_TYPE_N_REPSOLD` | `int` | `38` |
| `DISGUISE_TYPE_N_RODIAN` | `int` | `39` |
| `DISGUISE_TYPE_C_SELKATH` | `int` | `40` |
| `DISGUISE_TYPE_N_SITHAPPREN` | `int` | `41` |
| `DISGUISE_TYPE_N_SITHCOMF` | `int` | `42` |
| `DISGUISE_TYPE_N_SITHCOMM` | `int` | `43` |
| `DISGUISE_TYPE_N_SWOOPGANG` | `int` | `45` |
| `DISGUISE_TYPE_N_TUSKEN` | `int` | `46` |
| `DISGUISE_TYPE_N_TWILEKF` | `int` | `47` |
| `DISGUISE_TYPE_N_TWILEKM` | `int` | `48` |
| `DISGUISE_TYPE_N_WALRUSMAN` | `int` | `49` |
| `DISGUISE_TYPE_N_WOOKIEF` | `int` | `50` |
| `DISGUISE_TYPE_N_WOOKIEM` | `int` | `51` |
| `DISGUISE_TYPE_N_YODA` | `int` | `52` |
| `DISGUISE_TYPE_C_BANTHA` | `int` | `53` |
| `DISGUISE_TYPE_C_BRITH` | `int` | `54` |
| `DISGUISE_TYPE_C_DEWBACK` | `int` | `55` |
| `DISGUISE_TYPE_C_DRDASSASSIN` | `int` | `56` |
| `DISGUISE_TYPE_C_DRDASTRO` | `int` | `57` |
| `DISGUISE_TYPE_C_DRDG` | `int` | `58` |
| `DISGUISE_TYPE_C_DRDMKFOUR` | `int` | `59` |
| `DISGUISE_TYPE_C_DRDMKONE` | `int` | `60` |
| `DISGUISE_TYPE_C_DRDMKTWO` | `int` | `61` |
| `DISGUISE_TYPE_C_DRDPROBE` | `int` | `62` |
| `DISGUISE_TYPE_C_DRDPROT` | `int` | `63` |
| `DISGUISE_TYPE_C_DRDSENTRY` | `int` | `64` |
| `DISGUISE_TYPE_C_DRDSPYDER` | `int` | `65` |
| `DISGUISE_TYPE_C_DRDWAR` | `int` | `66` |
| `DISGUISE_TYPE_C_FIRIXA` | `int` | `67` |
| `DISGUISE_TYPE_C_GAMMOREAN` | `int` | `68` |
| `DISGUISE_TYPE_C_GIZKA` | `int` | `69` |
| `DISGUISE_TYPE_C_HUTT` | `int` | `70` |
| `DISGUISE_TYPE_C_IRIAZ` | `int` | `71` |
| `DISGUISE_TYPE_C_ITHORIAN` | `int` | `72` |
| `DISGUISE_TYPE_C_JAWA` | `int` | `73` |
| `DISGUISE_TYPE_C_KATAARN` | `int` | `74` |
| `DISGUISE_TYPE_C_KHOUNDA` | `int` | `75` |
| `DISGUISE_TYPE_C_KHOUNDB` | `int` | `76` |
| `DISGUISE_TYPE_C_KRAYTDRAGON` | `int` | `77` |
| `DISGUISE_TYPE_C_MYKAL` | `int` | `78` |
| `DISGUISE_TYPE_C_RAKGHOUL` | `int` | `79` |
| `DISGUISE_TYPE_C_RANCOR` | `int` | `80` |
| `DISGUISE_TYPE_C_SEABEAST` | `int` | `81` |
| `DISGUISE_TYPE_C_TACH` | `int` | `83` |
| `DISGUISE_TYPE_C_TWOHEAD` | `int` | `84` |
| `DISGUISE_TYPE_C_VERKAAL` | `int` | `85` |
| `DISGUISE_TYPE_C_WRAID` | `int` | `86` |
| `DISGUISE_TYPE_C_RONTO` | `int` | `87` |
| `DISGUISE_TYPE_C_KINRATH` | `int` | `88` |
| `DISGUISE_TYPE_C_TUKATA` | `int` | `89` |
| `DISGUISE_TYPE_N_TUSKENF` | `int` | `90` |
| `DISGUISE_TYPE_P_FEM_A_SML_01` | `int` | `91` |
| `DISGUISE_TYPE_P_FEM_A_MED_01` | `int` | `92` |
| `DISGUISE_TYPE_P_FEM_A_LRG_01` | `int` | `93` |
| `DISGUISE_TYPE_P_FEM_A_SML_02` | `int` | `94` |
| `DISGUISE_TYPE_P_FEM_A_MED_02` | `int` | `95` |
| `DISGUISE_TYPE_P_FEM_A_LRG_02` | `int` | `96` |
| `DISGUISE_TYPE_P_FEM_A_SML_03` | `int` | `97` |
| `DISGUISE_TYPE_P_FEM_A_MED_03` | `int` | `98` |
| `DISGUISE_TYPE_P_FEM_A_LRG_03` | `int` | `99` |
| `DISGUISE_TYPE_P_FEM_A_SML_04` | `int` | `100` |
| `DISGUISE_TYPE_P_FEM_A_MED_04` | `int` | `101` |
| `DISGUISE_TYPE_P_FEM_A_LRG_04` | `int` | `102` |
| `DISGUISE_TYPE_P_FEM_A_SML_05` | `int` | `103` |
| `DISGUISE_TYPE_P_FEM_A_MED_05` | `int` | `104` |
| `DISGUISE_TYPE_P_FEM_A_LRG_05` | `int` | `105` |
| `DISGUISE_TYPE_P_FEM_B_SML_01` | `int` | `106` |
| `DISGUISE_TYPE_P_FEM_B_MED_01` | `int` | `107` |
| `DISGUISE_TYPE_P_FEM_B_LRG_01` | `int` | `108` |
| `DISGUISE_TYPE_P_FEM_B_SML_02` | `int` | `109` |
| `DISGUISE_TYPE_P_FEM_B_MED_02` | `int` | `110` |
| `DISGUISE_TYPE_P_FEM_B_LRG_02` | `int` | `111` |
| `DISGUISE_TYPE_P_FEM_B_SML_03` | `int` | `112` |
| `DISGUISE_TYPE_P_FEM_B_MED_03` | `int` | `113` |
| `DISGUISE_TYPE_P_FEM_B_LRG_03` | `int` | `114` |
| `DISGUISE_TYPE_P_FEM_B_SML_04` | `int` | `115` |
| `DISGUISE_TYPE_P_FEM_B_MED_04` | `int` | `116` |
| `DISGUISE_TYPE_P_FEM_B_LRG_04` | `int` | `117` |
| `DISGUISE_TYPE_P_FEM_B_SML_05` | `int` | `118` |
| `DISGUISE_TYPE_P_FEM_B_MED_05` | `int` | `119` |
| `DISGUISE_TYPE_P_FEM_B_LRG_05` | `int` | `120` |
| `DISGUISE_TYPE_P_FEM_C_SML_01` | `int` | `121` |
| `DISGUISE_TYPE_P_FEM_C_MED_01` | `int` | `122` |
| `DISGUISE_TYPE_P_FEM_C_LRG_01` | `int` | `123` |
| `DISGUISE_TYPE_P_FEM_C_SML_02` | `int` | `124` |
| `DISGUISE_TYPE_P_FEM_C_MED_02` | `int` | `125` |
| `DISGUISE_TYPE_P_FEM_C_LRG_02` | `int` | `126` |
| `DISGUISE_TYPE_P_FEM_C_SML_03` | `int` | `127` |
| `DISGUISE_TYPE_P_FEM_C_MED_03` | `int` | `128` |
| `DISGUISE_TYPE_P_FEM_C_LRG_03` | `int` | `129` |
| `DISGUISE_TYPE_P_FEM_C_SML_04` | `int` | `130` |
| `DISGUISE_TYPE_P_FEM_C_MED_04` | `int` | `131` |
| `DISGUISE_TYPE_P_FEM_C_LRG_04` | `int` | `132` |
| `DISGUISE_TYPE_P_FEM_C_SML_05` | `int` | `133` |
| `DISGUISE_TYPE_P_FEM_C_MED_05` | `int` | `134` |
| `DISGUISE_TYPE_P_FEM_C_LRG_05` | `int` | `135` |
| `DISGUISE_TYPE_P_MAL_A_SML_01` | `int` | `136` |
| `DISGUISE_TYPE_P_MAL_A_MED_01` | `int` | `137` |
| `DISGUISE_TYPE_P_MAL_A_LRG_01` | `int` | `138` |
| `DISGUISE_TYPE_P_MAL_A_SML_02` | `int` | `139` |
| `DISGUISE_TYPE_P_MAL_A_MED_02` | `int` | `140` |
| `DISGUISE_TYPE_P_MAL_A_LRG_02` | `int` | `141` |
| `DISGUISE_TYPE_P_MAL_A_SML_03` | `int` | `142` |
| `DISGUISE_TYPE_P_MAL_A_MED_03` | `int` | `143` |
| `DISGUISE_TYPE_P_MAL_A_LRG_03` | `int` | `144` |
| `DISGUISE_TYPE_P_MAL_A_SML_04` | `int` | `145` |
| `DISGUISE_TYPE_P_MAL_A_MED_04` | `int` | `146` |
| `DISGUISE_TYPE_P_MAL_A_LRG_04` | `int` | `147` |
| `DISGUISE_TYPE_P_MAL_A_SML_05` | `int` | `148` |
| `DISGUISE_TYPE_P_MAL_A_MED_05` | `int` | `149` |
| `DISGUISE_TYPE_P_MAL_A_LRG_05` | `int` | `150` |
| `DISGUISE_TYPE_P_MAL_B_SML_01` | `int` | `151` |
| `DISGUISE_TYPE_P_MAL_B_MED_01` | `int` | `152` |
| `DISGUISE_TYPE_P_MAL_B_LRG_01` | `int` | `153` |
| `DISGUISE_TYPE_P_MAL_B_SML_02` | `int` | `154` |
| `DISGUISE_TYPE_P_MAL_B_MED_02` | `int` | `155` |
| `DISGUISE_TYPE_P_MAL_B_LRG_02` | `int` | `156` |
| `DISGUISE_TYPE_P_MAL_B_SML_03` | `int` | `157` |
| `DISGUISE_TYPE_P_MAL_B_MED_03` | `int` | `158` |
| `DISGUISE_TYPE_P_MAL_B_LRG_03` | `int` | `159` |
| `DISGUISE_TYPE_P_MAL_B_SML_04` | `int` | `160` |
| `DISGUISE_TYPE_P_MAL_B_MED_04` | `int` | `161` |
| `DISGUISE_TYPE_P_MAL_B_LRG_04` | `int` | `162` |
| `DISGUISE_TYPE_P_MAL_B_SML_05` | `int` | `163` |
| `DISGUISE_TYPE_P_MAL_B_MED_05` | `int` | `164` |
| `DISGUISE_TYPE_P_MAL_B_LRG_05` | `int` | `165` |
| `DISGUISE_TYPE_P_MAL_C_SML_01` | `int` | `166` |
| `DISGUISE_TYPE_P_MAL_C_MED_01` | `int` | `167` |
| `DISGUISE_TYPE_P_MAL_C_LRG_01` | `int` | `168` |
| `DISGUISE_TYPE_P_MAL_C_SML_02` | `int` | `169` |
| `DISGUISE_TYPE_P_MAL_C_MED_02` | `int` | `170` |
| `DISGUISE_TYPE_P_MAL_C_LRG_02` | `int` | `171` |
| `DISGUISE_TYPE_P_MAL_C_SML_03` | `int` | `172` |
| `DISGUISE_TYPE_P_MAL_C_MED_03` | `int` | `173` |
| `DISGUISE_TYPE_P_MAL_C_LRG_03` | `int` | `174` |
| `DISGUISE_TYPE_P_MAL_C_SML_04` | `int` | `175` |
| `DISGUISE_TYPE_P_MAL_C_MED_04` | `int` | `176` |
| `DISGUISE_TYPE_P_MAL_C_LRG_04` | `int` | `177` |
| `DISGUISE_TYPE_P_MAL_C_SML_05` | `int` | `178` |
| `DISGUISE_TYPE_P_MAL_C_MED_05` | `int` | `179` |
| `DISGUISE_TYPE_P_MAL_C_LRG_05` | `int` | `180` |
| `DISGUISE_TYPE_ENVIRONMENTSUIT` | `int` | `181` |
| `DISGUISE_TYPE_TURRET` | `int` | `182` |
| `DISGUISE_TYPE_TURRET2` | `int` | `183` |
| `DISGUISE_TYPE_N_DARTHBAND` | `int` | `184` |
| `DISGUISE_TYPE_COMMONER_FEM_WHITE` | `int` | `185` |
| `DISGUISE_TYPE_COMMONER_FEM_BLACK` | `int` | `186` |
| `DISGUISE_TYPE_COMMONER_FEM_OLD_ASIAN` | `int` | `187` |
| `DISGUISE_TYPE_COMMONER_FEM_OLD_WHITE` | `int` | `188` |
| `DISGUISE_TYPE_COMMONER_FEM_OLD_BLACK` | `int` | `189` |
| `DISGUISE_TYPE_COMMONER_MAL_WHITE` | `int` | `190` |
| `DISGUISE_TYPE_COMMONER_MAL_BLACK` | `int` | `191` |
| `DISGUISE_TYPE_COMMONER_MAL_OLD_ASIAN` | `int` | `192` |
| `DISGUISE_TYPE_COMMONER_MAL_OLD_WHITE` | `int` | `193` |
| `DISGUISE_TYPE_COMMONER_MAL_OLD_BLACK` | `int` | `194` |
| `DISGUISE_TYPE_CZERKA_OFFICER_WHITE` | `int` | `195` |
| `DISGUISE_TYPE_CZERKA_OFFICER_BLACK` | `int` | `196` |
| `DISGUISE_TYPE_CZERKA_OFFICER_OLD_ASIAN` | `int` | `197` |
| `DISGUISE_TYPE_CZERKA_OFFICER_OLD_WHITE` | `int` | `198` |
| `DISGUISE_TYPE_CZERKA_OFFICER_OLD_BLACK` | `int` | `199` |
| `DISGUISE_TYPE_JEDI_WHITE_FEMALE_02` | `int` | `200` |
| `DISGUISE_TYPE_JEDI_WHITE_FEMALE_03` | `int` | `201` |
| `DISGUISE_TYPE_JEDI_WHITE_FEMALE_04` | `int` | `202` |
| `DISGUISE_TYPE_JEDI_WHITE_FEMALE_05` | `int` | `203` |
| `DISGUISE_TYPE_JEDI_ASIAN_FEMALE_01` | `int` | `204` |
| `DISGUISE_TYPE_JEDI_ASIAN_FEMALE_02` | `int` | `205` |
| `DISGUISE_TYPE_JEDI_ASIAN_FEMALE_03` | `int` | `206` |
| `DISGUISE_TYPE_JEDI_ASIAN_FEMALE_04` | `int` | `207` |
| `DISGUISE_TYPE_JEDI_ASIAN_FEMALE_05` | `int` | `208` |
| `DISGUISE_TYPE_JEDI_BLACK_FEMALE_01` | `int` | `209` |
| `DISGUISE_TYPE_JEDI_BLACK_FEMALE_02` | `int` | `210` |
| `DISGUISE_TYPE_JEDI_BLACK_FEMALE_03` | `int` | `211` |
| `DISGUISE_TYPE_JEDI_BLACK_FEMALE_04` | `int` | `212` |
| `DISGUISE_TYPE_JEDI_BLACK_FEMALE_05` | `int` | `213` |
| `DISGUISE_TYPE_JEDI_WHITE_MALE_02` | `int` | `214` |
| `DISGUISE_TYPE_JEDI_WHITE_MALE_03` | `int` | `215` |
| `DISGUISE_TYPE_JEDI_WHITE_MALE_04` | `int` | `216` |
| `DISGUISE_TYPE_JEDI_WHITE_MALE_05` | `int` | `217` |
| `DISGUISE_TYPE_JEDI_ASIAN_MALE_01` | `int` | `218` |
| `DISGUISE_TYPE_JEDI_ASIAN_MALE_02` | `int` | `219` |
| `DISGUISE_TYPE_JEDI_ASIAN_MALE_03` | `int` | `220` |
| `DISGUISE_TYPE_JEDI_ASIAN_MALE_04` | `int` | `221` |
| `DISGUISE_TYPE_JEDI_ASIAN_MALE_05` | `int` | `222` |
| `DISGUISE_TYPE_JEDI_BLACK_MALE_01` | `int` | `223` |
| `DISGUISE_TYPE_JEDI_BLACK_MALE_02` | `int` | `224` |
| `DISGUISE_TYPE_JEDI_BLACK_MALE_03` | `int` | `225` |
| `DISGUISE_TYPE_JEDI_BLACK_MALE_04` | `int` | `226` |
| `DISGUISE_TYPE_JEDI_BLACK_MALE_05` | `int` | `227` |
| `DISGUISE_TYPE_HUTT_02` | `int` | `228` |
| `DISGUISE_TYPE_HUTT_03` | `int` | `229` |
| `DISGUISE_TYPE_HUTT_04` | `int` | `230` |
| `DISGUISE_TYPE_DROID_ASTRO_02` | `int` | `231` |
| `DISGUISE_TYPE_DROID_ASTRO_03` | `int` | `232` |
| `DISGUISE_TYPE_DROID_PROTOCOL_02` | `int` | `233` |
| `DISGUISE_TYPE_DROID_PROTOCOL_03` | `int` | `234` |
| `DISGUISE_TYPE_DROID_PROTOCOL_04` | `int` | `235` |
| `DISGUISE_TYPE_DROID_WAR_02` | `int` | `236` |
| `DISGUISE_TYPE_DROID_WAR_03` | `int` | `237` |
| `DISGUISE_TYPE_DROID_WAR_04` | `int` | `238` |
| `DISGUISE_TYPE_DROID_WAR_05` | `int` | `239` |
| `DISGUISE_TYPE_GAMMOREAN_02` | `int` | `240` |
| `DISGUISE_TYPE_GAMMOREAN_03` | `int` | `241` |
| `DISGUISE_TYPE_GAMMOREAN_04` | `int` | `242` |
| `DISGUISE_TYPE_ITHORIAN_02` | `int` | `243` |
| `DISGUISE_TYPE_ITHORIAN_03` | `int` | `244` |
| `DISGUISE_TYPE_KATH_HOUND_A02` | `int` | `245` |
| `DISGUISE_TYPE_KATH_HOUND_A03` | `int` | `246` |
| `DISGUISE_TYPE_KATH_HOUND_A04` | `int` | `247` |
| `DISGUISE_TYPE_KATH_HOUND_B02` | `int` | `248` |
| `DISGUISE_TYPE_KATH_HOUND_B03` | `int` | `249` |
| `DISGUISE_TYPE_KATH_HOUND_B04` | `int` | `250` |
| `DISGUISE_TYPE_WRAID_02` | `int` | `251` |
| `DISGUISE_TYPE_WRAID_03` | `int` | `252` |
| `DISGUISE_TYPE_WRAID_04` | `int` | `253` |
| `DISGUISE_TYPE_RAKATA_02` | `int` | `254` |
| `DISGUISE_TYPE_RAKATA_03` | `int` | `255` |
| `DISGUISE_TYPE_RODIAN_02` | `int` | `256` |
| `DISGUISE_TYPE_RODIAN_03` | `int` | `257` |
| `DISGUISE_TYPE_RODIAN_04` | `int` | `258` |
| `DISGUISE_TYPE_SELKATH_02` | `int` | `259` |
| `DISGUISE_TYPE_SELKATH_03` | `int` | `260` |
| `DISGUISE_TYPE_SITH_SOLDIER_03` | `int` | `261` |
| `DISGUISE_TYPE_SWOOP_GANG_02` | `int` | `262` |
| `DISGUISE_TYPE_SWOOP_GANG_03` | `int` | `263` |
| `DISGUISE_TYPE_SWOOP_GANG_04` | `int` | `264` |
| `DISGUISE_TYPE_SWOOP_GANG_05` | `int` | `265` |
| `DISGUISE_TYPE_TUSKAN_RAIDER_02` | `int` | `266` |
| `DISGUISE_TYPE_TUSKAN_RAIDER_03` | `int` | `267` |
| `DISGUISE_TYPE_TUSKAN_RAIDER_04` | `int` | `268` |
| `DISGUISE_TYPE_TWILEK_MALE_02` | `int` | `269` |
| `DISGUISE_TYPE_TWILEK_FEMALE_02` | `int` | `270` |
| `DISGUISE_TYPE_WOOKIE_MALE_02` | `int` | `271` |
| `DISGUISE_TYPE_WOOKIE_MALE_03` | `int` | `272` |
| `DISGUISE_TYPE_WOOKIE_MALE_04` | `int` | `273` |
| `DISGUISE_TYPE_WOOKIE_MALE_05` | `int` | `274` |
| `DISGUISE_TYPE_WOOKIE_FEMALE_02` | `int` | `275` |
| `DISGUISE_TYPE_WOOKIE_FEMALE_03` | `int` | `276` |
| `DISGUISE_TYPE_WOOKIE_FEMALE_04` | `int` | `277` |
| `DISGUISE_TYPE_WOOKIE_FEMALE_05` | `int` | `278` |
| `DISGUISE_TYPE_ENVIRONMENTSUIT_02` | `int` | `279` |
| `DISGUISE_TYPE_YUTHURA_BAN` | `int` | `280` |
| `DISGUISE_TYPE_SHYRACK_01` | `int` | `281` |
| `DISGUISE_TYPE_SHYRACK_02` | `int` | `282` |
| `DISGUISE_TYPE_REPUBLIC_SOLDIER_MAL_BLACK` | `int` | `283` |
| `DISGUISE_TYPE_REPUBLIC_SOLDIER_MAL_OLD_ASIAN` | `int` | `284` |
| `DISGUISE_TYPE_REPUBLIC_SOLDIER_MAL_OLD_WHITE` | `int` | `285` |
| `DISGUISE_TYPE_REPUBLIC_SOLDIER_MAL_OLD_BLACK` | `int` | `286` |
| `DISGUISE_TYPE_REPUBLIC_OFFICER_MAL_BLACK` | `int` | `287` |
| `DISGUISE_TYPE_REPUBLIC_OFFICER_MAL_OLD_ASIAN` | `int` | `288` |
| `DISGUISE_TYPE_REPUBLIC_OFFICER_MAL_OLD_WHITE` | `int` | `289` |
| `DISGUISE_TYPE_REPUBLIC_OFFICER_MAL_OLD_BLACK` | `int` | `290` |
| `DISGUISE_TYPE_SITH_FEM_WHITE` | `int` | `291` |
| `DISGUISE_TYPE_SITH_FEM_BLACK` | `int` | `292` |
| `DISGUISE_TYPE_SITH_FEM_OLD_ASIAN` | `int` | `293` |
| `DISGUISE_TYPE_SITH_FEM_OLD_WHITE` | `int` | `294` |
| `DISGUISE_TYPE_SITH_FEM_OLD_BLACK` | `int` | `295` |
| `DISGUISE_TYPE_SITH_MAL_WHITE` | `int` | `296` |
| `DISGUISE_TYPE_SITH_MAL_BLACK` | `int` | `297` |
| `DISGUISE_TYPE_SITH_MAL_OLD_ASIAN` | `int` | `298` |
| `DISGUISE_TYPE_SITH_MAL_OLD_WHITE` | `int` | `299` |
| `DISGUISE_TYPE_SITH_MAL_OLD_BLACK` | `int` | `300` |
| `DISGUISE_TYPE_SITH_FEM_ASIAN` | `int` | `301` |
| `DISGUISE_TYPE_SITH_MAL_ASIAN` | `int` | `302` |
| `DISGUISE_TYPE_JEDI_WHITE_OLD_MALE` | `int` | `303` |
| `DISGUISE_TYPE_JEDI_ASIAN_OLD_MALE` | `int` | `304` |
| `DISGUISE_TYPE_JEDI_BLACK_OLD_MALE` | `int` | `305` |
| `DISGUISE_TYPE_JEDI_WHITE_OLD_FEM` | `int` | `306` |
| `DISGUISE_TYPE_JEDI_ASIAN_OLD_FEM` | `int` | `307` |
| `DISGUISE_TYPE_JEDI_BLACK_OLD_FEM` | `int` | `308` |
| `PLOT_O_DOOM` | `int` | `0` |
| `PLOT_O_SCARY_STUFF` | `int` | `1` |
| `PLOT_O_BIG_MONSTERS` | `int` | `2` |
| `FORMATION_WEDGE` | `int` | `0` |
| `FORMATION_LINE` | `int` | `1` |
| `SUBSCREEN_ID_NONE` | `int` | `0` |
| `SUBSCREEN_ID_EQUIP` | `int` | `1` |
| `SUBSCREEN_ID_ITEM` | `int` | `2` |
| `SUBSCREEN_ID_CHARACTER_RECORD` | `int` | `3` |
| `SUBSCREEN_ID_ABILITY` | `int` | `4` |
| `SUBSCREEN_ID_MAP` | `int` | `5` |
| `SUBSCREEN_ID_QUEST` | `int` | `6` |
| `SUBSCREEN_ID_OPTIONS` | `int` | `7` |
| `SUBSCREEN_ID_MESSAGES` | `int` | `8` |
| `SHIELD_DROID_ENERGY_1` | `int` | `0` |
| `SHIELD_DROID_ENERGY_2` | `int` | `1` |
| `SHIELD_DROID_ENERGY_3` | `int` | `2` |
| `SHIELD_DROID_ENVIRO_1` | `int` | `3` |
| `SHIELD_DROID_ENVIRO_2` | `int` | `4` |
| `SHIELD_DROID_ENVIRO_3` | `int` | `5` |
| `SHIELD_ENERGY` | `int` | `6` |
| `SHIELD_ENERGY_SITH` | `int` | `7` |
| `SHIELD_ENERGY_ARKANIAN` | `int` | `8` |
| `SHIELD_ECHANI` | `int` | `9` |
| `SHIELD_MANDALORIAN_MELEE` | `int` | `10` |
| `SHIELD_MANDALORIAN_POWER` | `int` | `11` |
| `SHIELD_DUELING_ECHANI` | `int` | `12` |
| `SHIELD_DUELING_YUSANIS` | `int` | `13` |
| `SHIELD_VERPINE_PROTOTYPE` | `int` | `14` |
| `SHIELD_ANTIQUE_DROID` | `int` | `15` |
| `SHIELD_PLOT_TAR_M09AA` | `int` | `16` |
| `SHIELD_PLOT_UNK_M44AA` | `int` | `17` |
| `SUBRACE_NONE` | `int` | `0` |
| `SUBRACE_WOOKIE` | `int` | `1` |
| `VIDEO_EFFECT_NONE` | `int` | `-1` |
| `VIDEO_EFFECT_SECURITY_CAMERA` | `int` | `0` |
| `VIDEO_EFFECT_FREELOOK_T3M4` | `int` | `1` |
| `VIDEO_EFFECT_FREELOOK_HK47` | `int` | `2` |
| `TUTORIAL_WINDOW_START_SWOOP_RACE` | `int` | `0` |
| `TUTORIAL_WINDOW_RETURN_TO_BASE` | `int` | `1` |
| `TUTORIAL_WINDOW_MOVEMENT_KEYS` | `int` | `2` |
| `MOVEMENT_SPEED_PC` | `int` | `0` |
| `MOVEMENT_SPEED_IMMOBILE` | `int` | `1` |
| `MOVEMENT_SPEED_VERYSLOW` | `int` | `2` |
| `MOVEMENT_SPEED_SLOW` | `int` | `3` |
| `MOVEMENT_SPEED_NORMAL` | `int` | `4` |
| `MOVEMENT_SPEED_FAST` | `int` | `5` |
| `MOVEMENT_SPEED_VERYFAST` | `int` | `6` |
| `MOVEMENT_SPEED_DEFAULT` | `int` | `7` |
| `MOVEMENT_SPEED_DMFAST` | `int` | `8` |
| `LIVE_CONTENT_PKG1` | `int` | `1` |
| `LIVE_CONTENT_PKG2` | `int` | `2` |
| `LIVE_CONTENT_PKG3` | `int` | `3` |
| `LIVE_CONTENT_PKG4` | `int` | `4` |
| `LIVE_CONTENT_PKG5` | `int` | `5` |
| `LIVE_CONTENT_PKG6` | `int` | `6` |
| `sLanguage` | `string` | `"nwscript"` |
### Planet Constants

| Constant | Type | Value |
|----------|------|-------|
| `PLANET_ENDAR_SPIRE` | `int` | `0` |
| `PLANET_TARIS` | `int` | `1` |
| `PLANET_EBON_HAWK` | `int` | `2` |
| `PLANET_DANTOOINE` | `int` | `3` |
| `PLANET_TATOOINE` | `int` | `4` |
| `PLANET_KASHYYYK` | `int` | `5` |
| `PLANET_MANAAN` | `int` | `6` |
| `PLANET_KORRIBAN` | `int` | `7` |
| `PLANET_LEVIATHAN` | `int` | `8` |
| `PLANET_UNKNOWN_WORLD` | `int` | `9` |
| `PLANET_STAR_FORGE` | `int` | `10` |
| `PLANET_LIVE_01` | `int` | `11` |
| `PLANET_LIVE_02` | `int` | `12` |
| `PLANET_LIVE_03` | `int` | `13` |
| `PLANET_LIVE_04` | `int` | `14` |
| `PLANET_LIVE_05` | `int` | `15` |
### Visual Effects (VFX)

| Constant | Type | Value |
|----------|------|-------|
| `VFX_NONE` | `int` | `-1` |
| `VFX_IMP_HEALING_SMALL` | `int` | `1001` |
| `VFX_IMP_FORCE_JUMP_ADVANCED` | `int` | `1002` |
| `VFX_PRO_AFFLICT` | `int` | `1003` |
| `VFX_IMP_CHOKE` | `int` | `1004` |
| `VFX_IMP_CURE` | `int` | `1005` |
| `VFX_PRO_DEATH_FIELD` | `int` | `1006` |
| `VFX_PRO_DROID_DISABLE` | `int` | `1007` |
| `VFX_PRO_DROID_KILL` | `int` | `1008` |
| `VFX_PRO_DRAIN` | `int` | `1009` |
| `VFX_PRO_FORCE_ARMOR` | `int` | `1010` |
| `VFX_PRO_FORCE_AURA` | `int` | `1011` |
| `VFX_IMP_FORCE_BREACH` | `int` | `1012` |
| `VFX_IMP_FORCE_PUSH` | `int` | `1014` |
| `VFX_PRO_FORCE_SHIELD` | `int` | `1015` |
| `VFX_IMP_FORCE_WAVE` | `int` | `1017` |
| `VFX_IMP_FORCE_WHIRLWIND` | `int` | `1018` |
| `VFX_IMP_HEAL` | `int` | `1019` |
| `VFX_IMP_SPEED_KNIGHT` | `int` | `1020` |
| `VFX_PRO_LIGHTNING_L` | `int` | `1021` |
| `VFX_IMP_SPEED_MASTERY` | `int` | `1022` |
| `VFX_PRO_RESIST_ELEMENTS` | `int` | `1025` |
| `VFX_PRO_RESIST_FORCE` | `int` | `1026` |
| `VFX_PRO_RESIST_POISON` | `int` | `1027` |
| `VFX_PRO_LIGHTNING_S` | `int` | `1028` |
| `VFX_IMP_MIND_FORCE` | `int` | `1031` |
| `VFX_IMP_SUPPRESS_FORCE` | `int` | `1032` |
| `VFX_IMP_MIND_KINIGHT` | `int` | `1033` |
| `VFX_IMP_MIND_MASTERY` | `int` | `1034` |
| `VFX_PRO_LIGHTNING_JEDI` | `int` | `1035` |
| `VFX_PRO_LIGHTNING_L_SOUND` | `int` | `1036` |
| `VFX_IMP_GRENADE_ADHESIVE_PERSONAL` | `int` | `1038` |
| `VFX_IMP_FLAME` | `int` | `1039` |
| `VFX_IMP_STUN` | `int` | `1040` |
| `VFX_DUR_STEALTH_PULSE` | `int` | `2000` |
| `VFX_DUR_INVISIBILITY` | `int` | `2001` |
| `VFX_DUR_SPEED` | `int` | `2004` |
| `VFX_DUR_FORCE_WHIRLWIND` | `int` | `2007` |
| `VFX_DUR_HOLD` | `int` | `2008` |
| `VFX_DUR_BODY_FUAL` | `int` | `2024` |
| `VFX_DUR_PSYCHIC_STATIC` | `int` | `2025` |
| `VFX_BEAM_DEATH_FIELD_TENTACLE` | `int` | `2026` |
| `VFX_BEAM_DROID_DISABLE` | `int` | `2027` |
| `VFX_BEAM_DROID_DESTROY` | `int` | `2028` |
| `VFX_BEAM_DRAIN_LIFE` | `int` | `2029` |
| `VFX_DUR_KNIGHTS_SPEED` | `int` | `2031` |
| `VFX_DUR_SHIELD_RED_MARK_I` | `int` | `2032` |
| `VFX_DUR_SHIELD_RED_MARK_II` | `int` | `2034` |
| `VFX_DUR_SHIELD_RED_MARK_IV` | `int` | `2035` |
| `VFX_BEAM_LIGHTNING_DARK_S` | `int` | `2037` |
| `VFX_BEAM_LIGHTNING_DARK_L` | `int` | `2038` |
| `VFX_DUR_SHIELD_BLUE_01` | `int` | `2040` |
| `VFX_DUR_SHIELD_BLUE_02` | `int` | `2041` |
| `VFX_DUR_SHIELD_BLUE_03` | `int` | `2042` |
| `VFX_DUR_SHIELD_BLUE_04` | `int` | `2043` |
| `VFX_DUR_SHIELD_GREEN_01` | `int` | `2044` |
| `VFX_DUR_SHIELD_RED_01` | `int` | `2045` |
| `VFX_DUR_SHIELD_RED_02` | `int` | `2046` |
| `VFX_DUR_SHIELD_CHROME_01` | `int` | `2047` |
| `VFX_DUR_SHIELD_CHROME_02` | `int` | `2048` |
| `VFX_BEAM_ION_RAY_01` | `int` | `2049` |
| `VFX_BEAM_ION_RAY_02` | `int` | `2050` |
| `VFX_BEAM_COLD_RAY` | `int` | `2051` |
| `VFX_BEAM_STUN_RAY` | `int` | `2052` |
| `VFX_BEAM_FLAME_SPRAY` | `int` | `2053` |
| `VFX_DUR_CARBONITE_ENCASING` | `int` | `2054` |
| `VFX_DUR_CARBONITE_CHUNKS` | `int` | `2055` |
| `VFX_DUR_SHIELD_BLUE_MARK_I` | `int` | `2056` |
| `VFX_DUR_SHIELD_BLUE_MARK_II` | `int` | `2058` |
| `VFX_DUR_SHIELD_BLUE_MARK_IV` | `int` | `2059` |
| `VFX_FNF_FORCE_WAVE` | `int` | `3001` |
| `VFX_FNF_PLOT_MAN_SONIC_WAVE` | `int` | `3002` |
| `VFX_FNF_GRENADE_FRAGMENTATION` | `int` | `3003` |
| `VFX_FNF_GRENADE_STUN` | `int` | `3004` |
| `VFX_FNF_GRENADE_THERMAL_DETONATOR` | `int` | `3005` |
| `VFX_FNF_GRENADE_POISON` | `int` | `3006` |
| `VFX_FNF_GRENADE_SONIC` | `int` | `3007` |
| `VFX_FNF_GRENADE_ADHESIVE` | `int` | `3008` |
| `VFX_FNF_GRENADE_CRYOBAN` | `int` | `3009` |
| `VFX_FNF_GRENADE_PLASMA` | `int` | `3010` |
| `VFX_FNF_GRENADE_ION` | `int` | `3011` |
| `VFX_FNF_GRAVITY_GENERATOR` | `int` | `3013` |
| `VFX_COM_SPARKS_LARGE` | `int` | `4003` |
| `VFX_COM_SPARKS_LIGHTSABER` | `int` | `4004` |
| `VFX_COM_SPARKS_PARRY_METAL` | `int` | `4011` |
| `VFX_COM_POWER_ATTACK_IMPROVED_STAFF` | `int` | `4012` |
| `VFX_COM_POWER_BLAST_IMPROVED` | `int` | `4013` |
| `VFX_COM_CRITICAL_STRIKE_IMPROVED_STAFF` | `int` | `4014` |
| `VFX_COM_SNIPER_SHOT_IMPROVED` | `int` | `4015` |
| `VFX_COM_MULTI_SHOT` | `int` | `4016` |
| `VFX_COM_WHIRLWIND_STRIKE_STAFF` | `int` | `4017` |
| `VFX_COM_CRITICAL_STRIKE_MASTERY_STAFF` | `int` | `4018` |
| `VFX_COM_POWER_ATTACK_MASTERY_STAFF` | `int` | `4019` |
| `VFX_COM_SNIPER_SHOT_MASTERY` | `int` | `4020` |
| `VFX_COM_FLURRY_IMPROVED_STAFF` | `int` | `4021` |
| `VFX_COM_RAPID_SHOT_IMPROVED` | `int` | `4022` |
| `VFX_COM_BLASTER_DEFLECTION` | `int` | `4023` |
| `VFX_COM_BLASTER_IMPACT` | `int` | `4024` |
| `VFX_COM_CRITICAL_STRIKE_IMPROVED_SABER` | `int` | `4025` |
| `VFX_COM_CRITICAL_STRIKE_MASTERY_SABER` | `int` | `4026` |
| `VFX_COM_POWER_ATTACK_IMPROVED_SABER` | `int` | `4027` |
| `VFX_COM_POWER_ATTACK_MASTERY_SABER` | `int` | `4028` |
| `VFX_COM_POWER_BLAST_MASTERY` | `int` | `4029` |
| `VFX_COM_FLURRY_IMPROVED_SABER` | `int` | `4030` |
| `VFX_COM_WHIRLWIND_STRIKE_SABER` | `int` | `4031` |
| `VFX_COM_BLASTER_IMPACT_GROUND` | `int` | `4032` |
| `VFX_COM_SPARKS_BLASTER` | `int` | `4033` |
| `VFX_COM_DROID_EXPLOSION_1` | `int` | `4034` |
| `VFX_COM_DROID_EXPLOSION_2` | `int` | `4035` |
| `VFX_COM_JEDI_FORCE_FIZZLE` | `int` | `4036` |
| `VFX_COM_FORCE_RESISTED` | `int` | `4037` |
| `VFX_ARD_LIGHT_YELLOW_10` | `int` | `5000` |
| `VFX_ARD_LIGHT_YELLOW_20` | `int` | `5001` |
| `VFX_ARD_LIGHT_BLIND` | `int` | `5002` |
| `VFX_ARD_HEAT_SHIMMER` | `int` | `5003` |
| `VFX_IMP_MIRV` | `int` | `6000` |
| `VFX_IMP_MIRV_IMPACT` | `int` | `6001` |
| `VFX_IMP_SCREEN_SHAKE` | `int` | `6002` |
## K1-Only Constants

<!-- K1_ONLY_CONSTANTS_START -->

### NPC Constants

| Constant | Type | Value |
|----------|------|-------|
| `NPC_BASTILA` | `int` | `0` |
| `NPC_CARTH` | `int` | `2` |
| `NPC_JOLEE` | `int` | `4` |
| `NPC_JUHANI` | `int` | `5` |
| `NPC_MISSION` | `int` | `6` |
| `NPC_ZAALBAR` | `int` | `8` |
### Other Constants

| Constant | Type | Value |
|----------|------|-------|
| `TUTORIAL_WINDOW_MOVEMENT_KEYS` | `int` | `2` |
### Planet Constants

| Constant | Type | Value |
|----------|------|-------|
| `PLANET_ENDAR_SPIRE` | `int` | `0` |
| `PLANET_TARIS` | `int` | `1` |
| `PLANET_TATOOINE` | `int` | `4` |
| `PLANET_KASHYYYK` | `int` | `5` |
| `PLANET_MANAAN` | `int` | `6` |
| `PLANET_LEVIATHAN` | `int` | `8` |
| `PLANET_UNKNOWN_WORLD` | `int` | `9` |
| `PLANET_STAR_FORGE` | `int` | `10` |
## TSL-Only Constants

<!-- TSL_ONLY_CONSTANTS_START -->

### Class type Constants

| Constant | Type | Value |
|----------|------|-------|
| `CLASS_TYPE_TECHSPECIALIST` | `int` | `9` |
| `CLASS_TYPE_BOUNTYHUNTER` | `int` | `10` |
| `CLASS_TYPE_JEDIWEAPONMASTER` | `int` | `11` |
| `CLASS_TYPE_JEDIMASTER` | `int` | `12` |
| `CLASS_TYPE_JEDIWATCHMAN` | `int` | `13` |
| `CLASS_TYPE_SITHMARAUDER` | `int` | `14` |
| `CLASS_TYPE_SITHLORD` | `int` | `15` |
| `CLASS_TYPE_SITHASSASSIN` | `int` | `16` |
### Inventory Constants

| Constant | Type | Value |
|----------|------|-------|
| `INVENTORY_SLOT_RIGHTWEAPON2` | `int` | `18` |
| `INVENTORY_SLOT_LEFTWEAPON2` | `int` | `19` |
### NPC Constants

| Constant | Type | Value |
|----------|------|-------|
| `NPC_ATTON` | `int` | `0` |
| `NPC_BAO_DUR` | `int` | `1` |
| `NPC_G0T0` | `int` | `3` |
| `NPC_HANDMAIDEN` | `int` | `4` |
| `NPC_KREIA` | `int` | `6` |
| `NPC_MIRA` | `int` | `7` |
| `NPC_VISAS` | `int` | `9` |
| `NPC_HANHARR` | `int` | `10` |
| `NPC_DISCIPLE` | `int` | `11` |
| `NPC_AISTYLE_HEALER` | `int` | `6` |
| `NPC_AISTYLE_SKIRMISH` | `int` | `7` |
| `NPC_AISTYLE_TURTLE` | `int` | `8` |
| `NPC_AISTYLE_PARTY_AGGRO` | `int` | `9` |
| `NPC_AISTYLE_PARTY_DEFENSE` | `int` | `10` |
| `NPC_AISTYLE_PARTY_RANGED` | `int` | `11` |
| `NPC_AISTYLE_PARTY_STATIONARY` | `int` | `12` |
| `NPC_AISTYLE_PARTY_SUPPORT` | `int` | `13` |
| `NPC_AISTYLE_PARTY_REMOTE` | `int` | `14` |
| `NPC_AISTYLE_MONSTER_POWERS` | `int` | `15` |
### Other Constants

| Constant | Type | Value |
|----------|------|-------|
| `IMMUNITY_TYPE_DROID_CONFUSED` | `int` | `33` |
| `EFFECT_TYPE_DROID_CONFUSED` | `int` | `79` |
| `EFFECT_TYPE_MINDTRICK` | `int` | `80` |
| `EFFECT_TYPE_DROIDSCRAMBLE` | `int` | `81` |
| `ITEM_PROPERTY_DISGUISE` | `int` | `59` |
| `ITEM_PROPERTY_LIMIT_USE_BY_GENDER` | `int` | `60` |
| `ITEM_PROPERTY_LIMIT_USE_BY_SUBRACE` | `int` | `61` |
| `ITEM_PROPERTY_LIMIT_USE_BY_PC` | `int` | `62` |
| `ITEM_PROPERTY_DAMPEN_SOUND` | `int` | `63` |
| `ITEM_PROPERTY_DOORCUTTING` | `int` | `64` |
| `ITEM_PROPERTY_DOORSABERING` | `int` | `65` |
| `BASE_ITEM_WRIST_LAUNCHER` | `int` | `91` |
| `BASE_ITEM_FORCE_PIKE` | `int` | `93` |
| `FORCE_POWER_MASTER_ENERGY_RESISTANCE` | `int` | `133` |
| `FORCE_POWER_MASTER_HEAL` | `int` | `134` |
| `FORCE_POWER_FORCE_BARRIER` | `int` | `135` |
| `FORCE_POWER_IMPROVED_FORCE_BARRIER` | `int` | `136` |
| `FORCE_POWER_MASTER_FORCE_BARRIER` | `int` | `137` |
| `FORCE_POWER_BATTLE_MEDITATION_PC` | `int` | `138` |
| `FORCE_POWER_IMPROVED_BATTLE_MEDITATION_PC` | `int` | `139` |
| `FORCE_POWER_MASTER_BATTLE_MEDITATION_PC` | `int` | `140` |
| `FORCE_POWER_BAT_MED_ENEMY` | `int` | `141` |
| `FORCE_POWER_IMP_BAT_MED_ENEMY` | `int` | `142` |
| `FORCE_POWER_MAS_BAT_MED_ENEMY` | `int` | `143` |
| `FORCE_POWER_CRUSH_OPPOSITION_I` | `int` | `144` |
| `FORCE_POWER_CRUSH_OPPOSITION_II` | `int` | `145` |
| `FORCE_POWER_CRUSH_OPPOSITION_III` | `int` | `146` |
| `FORCE_POWER_CRUSH_OPPOSITION_IV` | `int` | `147` |
| `FORCE_POWER_CRUSH_OPPOSITION_V` | `int` | `148` |
| `FORCE_POWER_CRUSH_OPPOSITION_VI` | `int` | `149` |
| `FORCE_POWER_FORCE_BODY` | `int` | `150` |
| `FORCE_POWER_IMPROVED_FORCE_BODY` | `int` | `151` |
| `FORCE_POWER_MASTER_FORCE_BODY` | `int` | `152` |
| `FORCE_POWER_DRAIN_FORCE` | `int` | `153` |
| `FORCE_POWER_IMPROVED_DRAIN_FORCE` | `int` | `154` |
| `FORCE_POWER_MASTER_DRAIN_FORCE` | `int` | `155` |
| `FORCE_POWER_FORCE_CAMOUFLAGE` | `int` | `156` |
| `FORCE_POWER_IMPROVED_FORCE_CAMOUFLAGE` | `int` | `157` |
| `FORCE_POWER_MASTER_FORCE_CAMOUFLAGE` | `int` | `158` |
| `FORCE_POWER_FORCE_SCREAM` | `int` | `159` |
| `FORCE_POWER_IMPROVED_FORCE_SCREAM` | `int` | `160` |
| `FORCE_POWER_MASTER_FORCE_SCREAM` | `int` | `161` |
| `FORCE_POWER_FORCE_REPULSION` | `int` | `162` |
| `FORCE_POWER_FORCE_REDIRECTION` | `int` | `163` |
| `FORCE_POWER_FURY` | `int` | `164` |
| `FORCE_POWER_IMPROVED_FURY` | `int` | `165` |
| `FORCE_POWER_MASTER_FURY` | `int` | `166` |
| `FORCE_POWER_INSPIRE_FOLLOWERS_I` | `int` | `167` |
| `FORCE_POWER_INSPIRE_FOLLOWERS_II` | `int` | `168` |
| `FORCE_POWER_INSPIRE_FOLLOWERS_III` | `int` | `169` |
| `FORCE_POWER_INSPIRE_FOLLOWERS_IV` | `int` | `170` |
| `FORCE_POWER_INSPIRE_FOLLOWERS_V` | `int` | `171` |
| `FORCE_POWER_INSPIRE_FOLLOWERS_VI` | `int` | `172` |
| `FORCE_POWER_REVITALIZE` | `int` | `173` |
| `FORCE_POWER_IMPROVED_REVITALIZE` | `int` | `174` |
| `FORCE_POWER_MASTER_REVITALIZE` | `int` | `175` |
| `FORCE_POWER_FORCE_SIGHT` | `int` | `176` |
| `FORCE_POWER_FORCE_CRUSH` | `int` | `177` |
| `FORCE_POWER_PRECOGNITION` | `int` | `178` |
| `FORCE_POWER_BATTLE_PRECOGNITION` | `int` | `179` |
| `FORCE_POWER_FORCE_ENLIGHTENMENT` | `int` | `180` |
| `FORCE_POWER_MIND_TRICK` | `int` | `181` |
| `FORCE_POWER_CONFUSION` | `int` | `200` |
| `FORCE_POWER_BEAST_TRICK` | `int` | `182` |
| `FORCE_POWER_BEAST_CONFUSION` | `int` | `184` |
| `FORCE_POWER_DROID_TRICK` | `int` | `201` |
| `FORCE_POWER_DROID_CONFUSION` | `int` | `269` |
| `FORCE_POWER_BREATH_CONTROL` | `int` | `270` |
| `FORCE_POWER_WOOKIEE_RAGE_I` | `int` | `271` |
| `FORCE_POWER_WOOKIEE_RAGE_II` | `int` | `272` |
| `FORCE_POWER_WOOKIEE_RAGE_III` | `int` | `273` |
| `FORM_SABER_I_SHII_CHO` | `int` | `258` |
| `FORM_SABER_II_MAKASHI` | `int` | `259` |
| `FORM_SABER_III_SORESU` | `int` | `260` |
| `FORM_SABER_IV_ATARU` | `int` | `261` |
| `FORM_SABER_V_SHIEN` | `int` | `262` |
| `FORM_SABER_VI_NIMAN` | `int` | `263` |
| `FORM_SABER_VII_JUYO` | `int` | `264` |
| `FORM_FORCE_I_FOCUS` | `int` | `265` |
| `FORM_FORCE_II_POTENCY` | `int` | `266` |
| `FORM_FORCE_III_AFFINITY` | `int` | `267` |
| `FORM_FORCE_IV_MASTERY` | `int` | `268` |
| `POISON_ABILITY_AND_DAMAGE_AVERAGE` | `int` | `6` |
| `POISON_ABILITY_AND_DAMAGE_VIRULENT` | `int` | `7` |
| `POISON_DAMAGE_ROCKET` | `int` | `8` |
| `POISON_DAMAGE_NORMAL_DART` | `int` | `9` |
| `POISON_DAMAGE_KYBER_DART` | `int` | `10` |
| `POISON_DAMAGE_KYBER_DART_HALF` | `int` | `11` |
| `STANDARD_FACTION_SELF_LOATHING` | `int` | `21` |
| `STANDARD_FACTION_ONE_ON_ONE` | `int` | `22` |
| `STANDARD_FACTION_PARTYPUPPET` | `int` | `23` |
| `FEAT_EVASION` | `int` | `125` |
| `FEAT_TARGETING_1` | `int` | `126` |
| `FEAT_TARGETING_2` | `int` | `127` |
| `FEAT_TARGETING_3` | `int` | `128` |
| `FEAT_TARGETING_4` | `int` | `129` |
| `FEAT_TARGETING_5` | `int` | `130` |
| `FEAT_TARGETING_6` | `int` | `131` |
| `FEAT_TARGETING_7` | `int` | `132` |
| `FEAT_TARGETING_8` | `int` | `133` |
| `FEAT_TARGETING_9` | `int` | `134` |
| `FEAT_TARGETING_10` | `int` | `135` |
| `FEAT_CLOSE_COMBAT` | `int` | `139` |
| `FEAT_IMPROVED_CLOSE_COMBAT` | `int` | `140` |
| `FEAT_IMPROVED_FORCE_CAMOUFLAGE` | `int` | `141` |
| `FEAT_MASTER_FORCE_CAMOUFLAGE` | `int` | `142` |
| `FEAT_REGENERATE_FORCE_POINTS` | `int` | `143` |
| `FEAT_DARK_SIDE_CORRUPTION` | `int` | `149` |
| `FEAT_IGNORE_PAIN_1` | `int` | `150` |
| `FEAT_IGNORE_PAIN_2` | `int` | `151` |
| `FEAT_IGNORE_PAIN_3` | `int` | `152` |
| `FEAT_INCREASE_COMBAT_DAMAGE_1` | `int` | `153` |
| `FEAT_INCREASE_COMBAT_DAMAGE_2` | `int` | `154` |
| `FEAT_INCREASE_COMBAT_DAMAGE_3` | `int` | `155` |
| `FEAT_SUPERIOR_WEAPON_FOCUS_LIGHTSABER_1` | `int` | `156` |
| `FEAT_SUPERIOR_WEAPON_FOCUS_LIGHTSABER_2` | `int` | `157` |
| `FEAT_SUPERIOR_WEAPON_FOCUS_LIGHTSABER_3` | `int` | `158` |
| `FEAT_SUPERIOR_WEAPON_FOCUS_TWO_WEAPON_1` | `int` | `159` |
| `FEAT_SUPERIOR_WEAPON_FOCUS_TWO_WEAPON_2` | `int` | `160` |
| `FEAT_SUPERIOR_WEAPON_FOCUS_TWO_WEAPON_3` | `int` | `161` |
| `FEAT_LIGHT_SIDE_ENLIGHTENMENT` | `int` | `167` |
| `FEAT_DEFLECT` | `int` | `168` |
| `FEAT_INNER_STRENGTH_1` | `int` | `169` |
| `FEAT_INNER_STRENGTH_2` | `int` | `170` |
| `FEAT_INNER_STRENGTH_3` | `int` | `171` |
| `FEAT_INCREASE_MELEE_DAMAGE_1` | `int` | `172` |
| `FEAT_INCREASE_MELEE_DAMAGE_2` | `int` | `173` |
| `FEAT_INCREASE_MELEE_DAMAGE_3` | `int` | `174` |
| `FEAT_CRAFT` | `int` | `175` |
| `FEAT_MASTERCRAFT_WEAPONS_1` | `int` | `176` |
| `FEAT_MASTERCRAFT_WEAPONS_2` | `int` | `177` |
| `FEAT_MASTERCRAFT_WEAPONS_3` | `int` | `178` |
| `FEAT_MASTERCRAFT_ARMOR_1` | `int` | `179` |
| `FEAT_MASTERCRAFT_ARMOR_2` | `int` | `180` |
| `FEAT_MASTERCRAFT_ARMOR_3` | `int` | `181` |
| `FEAT_DROID_INTERFACE` | `int` | `182` |
| `FEAT_CLASS_SKILL_AWARENESS` | `int` | `183` |
| `FEAT_CLASS_SKILL_COMPUTER_USE` | `int` | `184` |
| `FEAT_CLASS_SKILL_DEMOLITIONS` | `int` | `185` |
| `FEAT_CLASS_SKILL_REPAIR` | `int` | `186` |
| `FEAT_CLASS_SKILL_SECURITY` | `int` | `187` |
| `FEAT_CLASS_SKILL_STEALTH` | `int` | `188` |
| `FEAT_CLASS_SKILL_TREAT_INJURY` | `int` | `189` |
| `FEAT_DUAL_STRIKE` | `int` | `190` |
| `FEAT_IMPROVED_DUAL_STRIKE` | `int` | `191` |
| `FEAT_MASTER_DUAL_STRIKE` | `int` | `192` |
| `FEAT_FINESSE_LIGHTSABERS` | `int` | `193` |
| `FEAT_FINESSE_MELEE_WEAPONS` | `int` | `194` |
| `FEAT_MOBILITY` | `int` | `195` |
| `FEAT_REGENERATE_VITALITY_POINTS` | `int` | `196` |
| `FEAT_STEALTH_RUN` | `int` | `197` |
| `FEAT_KINETIC_COMBAT` | `int` | `198` |
| `FEAT_SURVIVAL` | `int` | `199` |
| `FEAT_MANDALORIAN_COURAGE` | `int` | `200` |
| `FEAT_PERSONAL_CLOAKING_SHIELD` | `int` | `201` |
| `FEAT_MENTOR` | `int` | `202` |
| `FEAT_IMPLANT_SWITCHING` | `int` | `203` |
| `FEAT_SPIRIT` | `int` | `204` |
| `FEAT_FORCE_CHAIN` | `int` | `205` |
| `FEAT_WAR_VETERAN` | `int` | `206` |
| `FEAT_FIGHTING_SPIRIT` | `int` | `236` |
| `FEAT_HEROIC_RESOLVE` | `int` | `237` |
| `FEAT_PRECISE_SHOT` | `int` | `240` |
| `FEAT_IMPROVED_PRECISE_SHOT` | `int` | `241` |
| `FEAT_MASTER_PRECISE_SHOT` | `int` | `242` |
| `FEAT_PRECISE_SHOT_IV` | `int` | `243` |
| `FEAT_PRECISE_SHOT_V` | `int` | `244` |
| `ANIMATION_LOOPING_CHECK_BODY` | `int` | `33` |
| `ANIMATION_LOOPING_UNLOCK_DOOR` | `int` | `34` |
| `ANIMATION_LOOPING_SIT_AND_MEDITATE` | `int` | `35` |
| `ANIMATION_LOOPING_SIT_CHAIR` | `int` | `36` |
| `ANIMATION_LOOPING_SIT_CHAIR_DRINK` | `int` | `37` |
| `ANIMATION_LOOPING_SIT_CHAIR_PAZAK` | `int` | `38` |
| `ANIMATION_LOOPING_SIT_CHAIR_COMP1` | `int` | `39` |
| `ANIMATION_LOOPING_SIT_CHAIR_COMP2` | `int` | `40` |
| `ANIMATION_LOOPING_RAGE` | `int` | `41` |
| `ANIMATION_LOOPING_CLOSED` | `int` | `43` |
| `ANIMATION_LOOPING_STEALTH` | `int` | `44` |
| `ANIMATION_LOOPING_CHOKE_WORKING` | `int` | `45` |
| `ANIMATION_LOOPING_MEDITATE_STAND` | `int` | `46` |
| `ANIMATION_FIREFORGET_FORCE_CAST` | `int` | `121` |
| `ANIMATION_FIREFORGET_OPEN` | `int` | `122` |
| `ANIMATION_FIREFORGET_DIVE_ROLL` | `int` | `123` |
| `ANIMATION_FIREFORGET_SCREAM` | `int` | `124` |
| `ACTION_FOLLOWOWNER` | `int` | `43` |
| `TRAP_BASE_TYPE_SONIC_CHARGE_MINOR` | `int` | `14` |
| `TRAP_BASE_TYPE_SONIC_CHARGE_AVERAGE` | `int` | `15` |
| `TRAP_BASE_TYPE_SONIC_CHARGE_DEADLY` | `int` | `16` |
| `TRAP_BASE_TYPE_FLASH_STUN_STRONG` | `int` | `17` |
| `TRAP_BASE_TYPE_FLASH_STUN_DEVASTATING` | `int` | `18` |
| `TRAP_BASE_TYPE_FRAGMENTATION_MINE_STRONG` | `int` | `19` |
| `TRAP_BASE_TYPE_FRAGMENTATION_MINE_DEVASTATING` | `int` | `20` |
| `TRAP_BASE_TYPE_LASER_SLICING_STRONG` | `int` | `21` |
| `TRAP_BASE_TYPE_LASER_SLICING_DEVASTATING` | `int` | `22` |
| `TRAP_BASE_TYPE_POISON_GAS_STRONG` | `int` | `23` |
| `TRAP_BASE_TYPE_POISON_GAS_DEVASTATING` | `int` | `24` |
| `TRAP_BASE_TYPE_SONIC_CHARGE_STRONG` | `int` | `25` |
| `TRAP_BASE_TYPE_SONIC_CHARGE_DEVASTATING` | `int` | `26` |
| `PUP_SENSORBALL` | `int` | `0` |
| `PUP_OTHER1` | `int` | `1` |
| `PUP_OTHER2` | `int` | `2` |
| `SHIELD_PLOT_MAN_M28AA` | `int` | `18` |
| `SHIELD_HEAT` | `int` | `19` |
| `SHIELD_DREXL` | `int` | `20` |
| `VIDEO_EFFECT_CLAIRVOYANCE` | `int` | `3` |
| `VIDEO_EFFECT_FORCESIGHT` | `int` | `4` |
| `VIDEO_EFFECT_VISAS_FREELOOK` | `int` | `5` |
| `VIDEO_EFFECT_CLAIRVOYANCEFULL` | `int` | `6` |
| `VIDEO_EFFECT_FURY_1` | `int` | `7` |
| `VIDEO_EFFECT_FURY_2` | `int` | `8` |
| `VIDEO_EFFECT_FURY_3` | `int` | `9` |
| `VIDEO_FFECT_SECURITY_NO_LABEL` | `int` | `10` |
| `TUTORIAL_WINDOW_TEMP1` | `int` | `42` |
| `TUTORIAL_WINDOW_TEMP2` | `int` | `43` |
| `TUTORIAL_WINDOW_TEMP3` | `int` | `44` |
| `TUTORIAL_WINDOW_TEMP4` | `int` | `45` |
| `TUTORIAL_WINDOW_TEMP5` | `int` | `46` |
| `TUTORIAL_WINDOW_TEMP6` | `int` | `47` |
| `TUTORIAL_WINDOW_TEMP7` | `int` | `48` |
| `TUTORIAL_WINDOW_TEMP8` | `int` | `49` |
| `TUTORIAL_WINDOW_TEMP9` | `int` | `50` |
| `TUTORIAL_WINDOW_TEMP10` | `int` | `51` |
| `TUTORIAL_WINDOW_TEMP11` | `int` | `52` |
| `TUTORIAL_WINDOW_TEMP12` | `int` | `53` |
| `TUTORIAL_WINDOW_TEMP13` | `int` | `54` |
| `TUTORIAL_WINDOW_TEMP14` | `int` | `55` |
| `TUTORIAL_WINDOW_TEMP15` | `int` | `56` |
| `AI_LEVEL_VERY_HIGH` | `int` | `4` |
| `AI_LEVEL_HIGH` | `int` | `3` |
| `AI_LEVEL_NORMAL` | `int` | `2` |
| `AI_LEVEL_LOW` | `int` | `1` |
| `AI_LEVEL_VERY_LOW` | `int` | `0` |
| `IMPLANT_NONE` | `int` | `0` |
| `IMPLANT_REGEN` | `int` | `1` |
| `IMPLANT_STR` | `int` | `2` |
| `IMPLANT_END` | `int` | `3` |
| `IMPLANT_AGI` | `int` | `4` |
| `FORFEIT_NO_FORCE_POWERS` | `int` | `1` |
| `FORFEIT_NO_ITEMS` | `int` | `2` |
| `FORFEIT_NO_WEAPONS` | `int` | `4` |
| `FORFEIT_DXUN_SWORD_ONLY` | `int` | `8` |
| `FORFEIT_NO_ARMOR` | `int` | `16` |
| `FORFEIT_NO_RANGED` | `int` | `32` |
| `FORFEIT_NO_LIGHTSABER` | `int` | `64` |
| `FORFEIT_NO_ITEM_BUT_SHIELD` | `int` | `128` |
### Planet Constants

| Constant | Type | Value |
|----------|------|-------|
| `PLANET_DXUN` | `int` | `1` |
| `PLANET_M4_78` | `int` | `4` |
| `PLANET_MALACHOR_V` | `int` | `5` |
| `PLANET_NAR_SHADDAA` | `int` | `6` |
| `PLANET_ONDERON` | `int` | `7` |
| `PLANET_PERAGUS` | `int` | `8` |
| `PLANET_TELOS` | `int` | `9` |
| `PLANET_HARBINGER` | `int` | `10` |
| `PLANET_LIVE_06` | `int` | `16` |
### Visual Effects (VFX)

| Constant | Type | Value |
|----------|------|-------|
| `VFX_DUR_ELECTRICAL_SPARK` | `int` | `2067` |
| `VFX_DUR_HOLO_PROJECT` | `int` | `9010` |
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

- [`Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_auto.py:126-205`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_auto.py)
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

- [`reone/src/apps/dataminer/routines.cpp:149-184`](https://github.com/seedhartha/reone/blob/master/src/apps/dataminer/routines.cpp) - Parses nwscript.nss using regex patterns for constants and functions
- [`reone/src/apps/dataminer/routines.cpp:382-427`](https://github.com/seedhartha/reone/blob/master/src/apps/dataminer/routines.cpp) - Extracts functions from nwscript.nss in chitin.key for K1 and K2
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

- [`Libraries/PyKotor/src/pykotor/common/script.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/script.py) - data structures (ScriptFunction, ScriptConstant, DataType)
- [`Libraries/PyKotor/src/pykotor/common/scriptdefs.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py) - Function and constant definitions (772 K1 functions, 1489 K1 constants)
- [`Libraries/PyKotor/src/pykotor/common/scriptlib.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptlib.py) - Library file definitions (k_inc_generic, k_inc_utility, etc.)
- [`Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_auto.py:126-205`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_auto.py) - Compilation integration

**Other Implementations:**

- [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9) — C# [NCS](NCS-File-Format) model (`Kotor.NET/Formats/KotorNCS/`)
- **`KotORModSync/KOTORModSync.Core/Data/NWScriptHeader.cs`** - C# NWScript header parser
  - Canonical (th3w1zard1/KotORModSync): <https://github.com/th3w1zard1/KotORModSync/blob/c8b0d10ce3fd7525d593d34a3be8d151da7d3387/KOTORModSync.Core/Data/NWScriptHeader.cs>
- **`KotORModSync/KOTORModSync.Core/Data/NWScriptFileReader.cs`** - C# NWScript file reader
  - Canonical (th3w1zard1/KotORModSync): <https://github.com/th3w1zard1/KotORModSync/blob/c8b0d10ce3fd7525d593d34a3be8d151da7d3387/KOTORModSync.Core/Data/NWScriptFileReader.cs>

**NWScript VM and Execution:**

- [`reone/src/libs/script/format/ncsreader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp) - [NCS](NCS-File-Format) bytecode reader
- [`reone/src/libs/script/format/ncswriter.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncswriter.cpp) - [NCS](NCS-File-Format) bytecode writer
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

- [`reone/src/libs/script/virtualmachine.cpp` L36+](https://github.com/seedhartha/reone/blob/master/src/libs/script/virtualmachine.cpp#L36) — Script VM (`VirtualMachine` implementation)
- [`reone/include/reone/script/virtualmachine.h` L41+](https://github.com/seedhartha/reone/blob/master/include/reone/script/virtualmachine.h#L41) — `VirtualMachine` declaration
- [`reone/src/libs/script/program.cpp` L28+](https://github.com/seedhartha/reone/blob/master/src/libs/script/program.cpp#L28) — `ScriptProgram` bytecode container (`add`, instruction helpers)
- [`xoreos/src/aurora/nwscript/execution.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/nwscript/execution.cpp) - NWScript execution engine
- [`xoreos/src/aurora/nwscript/variable.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/nwscript/variable.cpp) - Variable handling
- [`xoreos/src/aurora/nwscript/function.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/nwscript/function.cpp) - Function call handling
- [`NorthernLights/Assets/Scripts/ncs/control.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/control.cs) - Unity C# [NCS](NCS-File-Format) VM control and execution
- [`KotOR.js/src/nwscript/NWScriptInstance.ts` L32+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptInstance.ts#L32) — Per-script execution state (`run` / `runScript`, stack, instruction stepping)

**Routine Implementations:**

- [`reone/src/libs/script/routine/main/`](https://github.com/seedhartha/reone/tree/master/src/libs/script/routine/main) - Main routine implementations
- [`reone/src/libs/script/routine/action/`](https://github.com/seedhartha/reone/tree/master/src/libs/script/routine/action) - Action routine implementations
- [`reone/src/libs/script/routine/effect/`](https://github.com/seedhartha/reone/tree/master/src/libs/script/routine/effect) - Effect routine implementations
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
- [`reone/src/libs/game/script/routines.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/game/script/routines.cpp) - Game-specific routine implementations
- [`reone/include/reone/game/script/routines.h`](https://github.com/seedhartha/reone/blob/master/include/reone/game/script/routines.h) - Game routine header
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
- [`reone/src/libs/script/routine/action/`](https://github.com/seedhartha/reone/tree/master/src/libs/script/routine/action) - Action routine implementations
- [`reone/src/libs/script/routine/effect/`](https://github.com/seedhartha/reone/tree/master/src/libs/script/routine/effect) - Effect routine implementations
- [`reone/src/libs/script/routine/object/`](https://github.com/seedhartha/reone/tree/master/src/libs/script/routine/object) - Object routine implementations
- [`reone/src/libs/script/routine/party/`](https://github.com/seedhartha/reone/tree/master/src/libs/script/routine/party) - Party routine implementations
- [`reone/src/libs/script/routine/combat/`](https://github.com/seedhartha/reone/tree/master/src/libs/script/routine/combat) - Combat routine implementations
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

