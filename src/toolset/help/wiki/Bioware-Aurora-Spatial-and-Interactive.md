# BioWare Aurora Engine: Spatial and Interactive

*Official Bioware Aurora Documentation — Grouped Reference*

> This page groups related official BioWare Aurora Engine specifications for convenient reference. Each section below was originally a separate BioWare PDF, archived in [xoreos-docs](https://github.com/xoreos/xoreos-docs). The content is mirrored verbatim from the original documentation.

## Contents

- [Door / Placeable (UTD/UTP)](#doorplaceablegff)
- [Trigger (UTT)](#trigger)
- [Waypoint (UTW)](#waypoint)
- [Sound Object (UTS)](#soundobject)
- [Encounter (UTE)](#encounter)

---

<a id="doorplaceablegff"></a>

# DoorPlaceableGFF

*Official Bioware Aurora Documentation*

> **Note**: This official BioWare documentation was originally written for **Neverwinter Nights**, but the Door (UTD) and Placeable (UTP) formats are **identical in KotOR**. All structures, fields, and behaviors described here apply to KotOR as well. The examples may reference NWN-specific features, but the core format is the same.

**Source:** This documentation is extracted from the official BioWare Aurora Engine DoorPlaceableGFF PDF, archived in [`xoreos-docs/specs/bioware/DoorPlaceableGFF.pdf`](https://github.com/xoreos/xoreos-docs/blob/master/specs/bioware/DoorPlaceableGFF.pdf). The original documentation was published on the now-defunct nwn.bioware.com developer site.

---

## Page 1

BioWare Corp.
<http://www.bioware.com>
BioWare Aurora Engine
Situated Object (Door and Placeable Object) Format

1. Introduction
A Situated Object is a base object type from which the Door and Placeable Object types are derived.
Situated objects contain all the shared properties of Doors and Placeable objects. This document will
first discuss these shared properties, then discuss the properties that are specific to doors and placeable
objects themselves.
A Door is an object type that serves several functions. When closed, it blocks movement of creatures,
and may block line of sight. Additionally, doors may serve as an area transition targets and trap
locations.
A Placeable Object is an object type that adds to the ambience of an area, beyond the level provided by
the tiles in the area's tileset. They may be purely decorational and inactive, or they may be set to be
useable by players, whether as operable switches, as containers, or as traps.
Doors and Placeable objects are stored in the game and toolset using BioWare's Generic File Format
(GFF), and it is assumed that the reader of this document is familiar with GFF.
Doors and Placeable objects can be blueprints or instances. Door blueprints are saved as GFF files
having a UTD extension and "UTD " as the FileType string in their header. Door instances are stored as
Door Structs within a module's GIT files. Similarly, Placeable object blueprints are UTP files with
"UTP " as their FileType string, and Placeable instances are Placeable Structs within a module's GIT
files.
2. Base Situated Object Struct
The tables in this section describe the GFF Struct for a basic Situated object. All Doors and Placeables
share the properties of a Situated object.
2.1 Common Situated Fields
The Table below lists the Fields that are present in all Situated Structs, regardless of where they are
found.
Table 2.1: Fields in all Door/Placeable Structs
Label
Type
Description
AnimationState

### BYTE

Specifies animation state of the object. Open, closed,
destroyed, activated, etc.
Appearance

### DWORD

Appearance ID. Index into an appearance-related 2da.
Either doortypes.2da or placeables.2da.
AutoRemoveKey

### BYTE

1 if the key should be destroyed from the inventory of
the creature that opens this object.
0 if the key should remain in the inventory of the
creature that opens this object.
This property applies only if a key item is required to
open this object. (ie., KeyRequired is 1)

## Page 2

BioWare Corp.
<http://www.bioware.com>
CloseLockDC

### BYTE

DC to lock the object. If 0, anyone can lock it.
Conversation
CResRef
ResRef of DLG file to use if a player converses with
this object via ActionStartConversation().
CurrentHP

### SHORT

Current HP of the object. For instances and blueprints
in the toolset, this is always the same as HP. In a game,
it may be different.
Description
CExoLocString
Description of this object. Unlike most object types, the
game does not show the description for a Door when a
player examines it. It does show the description for a
Placeable, however.
DisarmDC

### BYTE

DC to disarm the trap, if any, attached to this object.
Faction

### DWORD

Faction ID of this object. Index into the list of faction
IDs in the module's repute.fac.
Fort

### BYTE

Fortitude save
Hardness

### BYTE

Hardness of this object. Damage reduction against
physical attacks. All slashing, piercing, and
bludgeoning damage is reduced by this amount to a
minimum of 0.
HP

### SHORT

Max Hit Points of this object.
Interruptable

### BYTE

Conversation can be interrupted.
Lockable

### BYTE

1 if this object can be locked after it has been unlocked.
0 if this object cannot be locked again by a Creature or
player after it has been unlocked.
Locked

### BYTE

1 if this object is locked.
0 if this object is not locked.
LocName
CExoLocString
Localized name of this object. Appears in the toolset's
blueprint palette and as the name of this object in the
game.
OnClosed
CResRef
OnClosed event
OnDamaged
CResRef
OnDamaged event
OnDeath
CResRef
OnDeath event
OnDisarm
CResRef
OnDisarm event
OnHeartbeat
CResRef
OnHeartbeat event
OnLock
CResRef
OnLock event
OnMeleeAttacked
CResRef
OnPhysicalAttacked event. Fires when object is
attacked via melee or ranged non-magical attack.
OnOpen
CResRef
OnOpen event
OnSpellCastAt
CResRef
OnSpellCastAt event
OnTrapTriggered
CResRef
OnTrapTriggered event. If blank, then use the trap
script specified by the TrapType.
OnUnlock
CResRef
OnUnlock event
OnUserDefined
CResRef
OnUserDefined event
OpenLockDC

### BYTE

DC to unlock this object, if this object has been locked
by setting Locked to 1.
Plot

### BYTE

Plot flag. Plot objects cannot be damaged or destroyed
by Creatures or players.
PortraitId

### WORD

Index into portraits.2da. See Trigger format document,
Section 3.2 Portraits.
Ref

### BYTE

Reflex save
Tag
CExoString
Tag of the object. Up to 32 characters.
TemplateResRef
CResRef
For blueprints (UTD files), this should be the same as
the filename.
For instances, this is the ResRef of the blueprint that
the instance was created from.

## Page 3

BioWare Corp.
<http://www.bioware.com>
TrapDetectable

### BYTE

1 if Trap can be detected
0 if Trap cannot be detected
TrapDetectDC

### BYTE

DC to detect the Trap. Toolset enforces 1-250 range.
TrapDisarmable

### BYTE

1 if Trap can be disarmed.
0 if Trap cannot be disarmed.
TrapFlag

### BYTE

1 if the object Trapped.
0 if the object is not Trapped.
TrapOneShot

### BYTE

1 if the Trap disappears after firing.
0 if the Trap never disappears.
TrapType

### BYTE

Index into traps.2da.
Specifies the trap type, if the object has a Trap.
See Section 3.3 Traps, in the Trigger format
document.
Will

### BYTE

Will save
2.2. Situated Blueprint Fields
The Top-Level Struct in a UTD or UTP file contains all the Fields in Table 2.1 above, plus those in
Table 2.2 below.
Table 2.2: Fields in Door/Placeable Blueprint Structs
Label
Type
Description
Comment
CExoString
Module designer comment.
PaletteID

### BYTE

ID of the node that the object Blueprint appears under
in the object's blueprint palette.
TemplateResRef
CResRef
The filename of the UTD/UTP file itself. It is an error
if this is different. Certain applications check the value
of this Field instead of the ResRef of the actual file.
If you manually rename a UTD/UTP file outside of the
toolset, then you must also update the TemplateResRef
Field inside it.
2.3. Situated Instance Fields
A Door Instance Struct in a GIT file contains all the Fields in Table 2.1, plus those in Table 2.3 below.
Table 2.3: Fields in Door/Placeable Instance Structs
Label
Type
Description
Bearing

### FLOAT

Orientation of the object, expressed as a bearing in
radians measured counterclockwise from north. This is
the opposite of the direction of the wireframe arrow
attached to the object in the toolset's area viewer.
TemplateResRef
CResRef
For instances, this is the ResRef of the blueprint that
the instance was created from.
X
Y
Z

### FLOAT

(x,y,z) coordinates of the object within the Area that it
is located in.
2.4. Situated Game Instance Fields
After a GIT file has been saved by the game, the Door Instance Struct not only contains the Fields in
Table 2.1 and Table 2.3, it also contains the Fields in Table 2.4.

## Page 4

BioWare Corp.
<http://www.bioware.com>
Table 2.4: Fields in Door/Placeable Instance Structs in SaveGames
Label
Type
Description
ActionList
List
List of Actions stored on this object
StructID 0. See Section 6 of the Common GFF
Structs document.
AnimationDay

### DWORD

AnimationTime

### DWORD

EffectList
List
List of Effects stored on this object
StructID 2. See Section 4 of the Common GFF
Structs document.
ObjectId

### DWORD

Object ID used by game for this object.
VarTable
List
List of scripting variables stored on this object.
StructID 0. See Section 3 of the Common GFF
Structs document.
3. Doors
3.1. Door Struct
Door Structs contain all the Fields in Table 2.1, plus those in Table 3.1 below.
Table 3.1: Fields Unique to Door Structs
Label
Type
Description
AnimationState

### BYTE

Specifies animation state of the object.
0 = closed
1 = opened1 (opened in same direction as wireframe
orientation arrow in toolset area viewer)
2 = opened2 (opened in opposite direction to wireframe
orientation arrow in toolset area viewer)
Appearance

### DWORD

Appearance ID. Index into doortypes.2da.
If greater than 0, use this to determine how the door
looks.
If 0, use GenericType instead to determine how the
door looks.
GenericType

### BYTE

If Appearance is 0, then GenericType determines the
Door appearance by lookup in genericdoors.2da.
LinkedTo
CExoString
Tag of the Waypoint or Door that this Door links to in
an area transition.
LinkedToFlags

### BYTE

0 if this Door does not link to anything
1 if this Door is an Area Transition and links to another
Door.
2 if this Door is an Area Transition and links to a
Waypoint.
LoadScreenID

### WORD

Index into loadscreens.2da.
Specifies a loading screen to use when following this
Area Transition, if the transition causes the player to go
to a different area.
If LoadScreenID == 0, then use the default loading
screen as specified by the destination area.
See Section 2.3 in the Area GFF doc.
OnClick
CResRef
OnAreaTransitionClick event. Fires when a player
clicks on this door while it is opened in order to follow
its area transition.
OnFailToOpen
CResRef
OnFailToOpen event

## Page 5

BioWare Corp.
<http://www.bioware.com>
3.2. Door Blueprint Struct
Door Blueprints contain the Fields listed in Tables 2.1, 2.2, and 3.1.
3.3. Door Instance Struct
3.3.1. Door Instance Fields
Door Instances placed in the toolset contain the Fields listed in Tables 2.1, 2.3, and 3.1.
3.3.2. Relation of Door Instance Models to Appearance and GenericType
The appearance of a door instance is determined by where the door is located on a tile. Doors instances
can only be painted at a location that corresponds to a door hook point on a tile. The hook point
specifies the location and orientation at which a door can be placed, and it also places restrictions on
what model the door can have when placed there.
Hook points on a tile are determined by both the tileset .SET file and the actual model .MDL file for the
tile. It is an error if the SET file and MDL files do not agree, although the toolset itself does not check
for consistency. It only looks at the SET file information. BioWare's BuildTil utility however, enforces
consistency between the SET file and the MDL file, modifying the SET file if necessary to make it
consistent with the MDL file.
There are two types of hook point: Unique (aka. Tileset-specific) and Generic.
Unique door hookpoints are attached to tiles that contain doorway geometry that demands a door of a
specific appearance. The SET file entry for a Unique door hookpoint contains an index into
doortypes.2da. Any door instance painted or moved onto a Unique hookpoint will be modified to have
its Appearance match the one implied by the hookpoint.
Generic door hookpoints are attached to tiles that contain a generic doorway that can fit a variety of
door appearances. The SET file entry for a Generic door hookpoint contains an index into
genericdoors.2da. Any door instance painted or moved onto a Generic hookpoint will be modified to
have Appearance 0, and its model will then be determined by its GenericType.
If a door is moved from a Generic hookpoint to a Unique hookpoint, its Appearance changes, but its
GenericType remains the same, so that when moved back to a Generic hookpoint, it will once again
have the model that it had before.
3.4. Door Game Instance Fields
After a GIT file has been saved by the game, the Door Instance Struct contains the Fields in Tables 2.1,
2.3, 2.4, 3.1, and 4.4.
Table 3.4: Fields in Door Instance Structs in SaveGames
Label
Type
Description
SecretDoorDC

### BYTE

Obsolete. Always 0.

## Page 6

BioWare Corp.
<http://www.bioware.com>
3.5. The 2DA Files Referenced by Door Fields
3.5.1. Door Tileset-Specific Appearances
If a door has an Appearance Field value greater than 0, then its model is determined by using its
Appearance as an index into doortypes.2da.
Table 3.5.1: doortypes.2da columns
Column
Type
Description
Label
String
Programmer label
Model
String
ResRef of MDL model file to display for the door
TileSet
String
ResRef of tileset SET file
TemplateResRef
String
ResRef of UTD file
StringRefGame
Integer
StringRef of text to display as the name of the door
appearance in the toolset
BlockSight
Integer
0 if  the door does not block sight in-game
1 if the door blocks sight in-game
VisibleModel
Integer
0 if the door model is not visible. Invisible-model doors
are always open.
1 if the door model is visible. Visible doors can be opened
and closed.
SoundAppType
Integer
Index into placeableobjsnds.2da.
3.5.2. Door Generic Appearances
If a door has a value of 0 for its Appearance Field, then its model is determined by using its
GenericType as an index into genericdoors.2da.
Table 3.5.2: genericdoors.2da columns
Column
Type
Description
Label
String
Programmer label
StrRef
String
StringRef of text to display as the name of the door in the
game.
ModelName
String
ResRef of MDL model file to use for the door.
BlockSight
Integer
0 if  the door does not block sight in-game
1 if the door blocks sight in-game
TemplateResRef
String
ResRef of UTD file
VisibleModel
Integer
0 if the door model is not visible. Invisible-model doors
are always open.
1 if the door model is visible. Visible doors can be opened
and closed.
SoundAppType
Integer
Index into placeableobjsnds.2da.
Name
StrRef
StringRef of text to display as the name of the generic door
appearance in the toolset
4. Placeable Objects
4.1. Placeable Struct
Placeable Structs contain all the Fields in Table 2.1, plus those in Table 4.1 below.

## Page 7

BioWare Corp.
<http://www.bioware.com>
Table 4.1.1: Fields Unique to Placeable Structs
Label
Type
Description
AnimationState

### BYTE

Specifies animation state of the object. See Table 4.1.2
BodyBag

### BYTE

Index into bodybag.2da.
Specifies the body bag left behind when this object is
destroyed while it still contains inventory.
HasInventory

### BYTE

1 if the Placeable has inventory
0 if the Placeable has no inventory
ItemList
List
List of InventoryObject Structs.
StructID = index of Struct in list.
This list is saved only if the Placeable contains at least
1 item in its inventory.
OnInvDisturbed
CResRef
OnInventoryDisturbed event
OnUsed
CResRef
OnUsed event
Static

### BYTE

1 if the Placeable is static.
0 if the Placeable is nonstatic.

Static objects are loaded client-side and are
inaccessible through scripting because the server
forgets about them after telling the client where they
are located and what they look like. They cannot be
interacted with in any way by the players or creatures
in a game, and they cannot have any animation state
other than the default.

Make objects Static to improve client and server
performance, and if they are present only for
decoration.
Type

### BYTE

Obsolete. Not used. Always 0.
Useable

### BYTE

1 if the Placeable can be used by a player.
The AnimationState of a placeable object specifies what animations it should play. Table 4.1.2 lists the
possible animation states. Not all animation states are available for all Placeable objects. A particular
animation state is only available if the model (MDL) file for its appearance actually contains an
animation of the name specified in Table 4.1.2.
Table 4.1.2: Placeable Object Animation States
Name
Animation State
Required animation on model
default
0
default
open
1
open
closed
2
close
destroyed
3
dead
activated
4
on
deactivated
5
off
The ItemList of a Placeable Object contains InventoryObject Structs. The Fields in an InventoryObject
Struct vary depending on whether the inventory belongs to a Placeable Object Blueprint or Instance. In
both cases, however, InventoryObjects contain at least the Fields in Table 4.1.3.
Table 4.1.3: Fields in all InventoryObject Structs
Label
Type
Description
Repos_PosX

### WORD

x-position of item in inventory grid
Repos_PosY

### WORD

y-position of item in inventory grid

## Page 8

BioWare Corp.
<http://www.bioware.com>
4.2. Placeable Blueprint Struct
Placeable Object Blueprints contain the Fields listed in Tables 2.1.1, 2.2, and 4.1.
Table 4.2.1: Fields Unique to Placeable Structs
Label
Type
Description
ItemList
List
List of InventoryObject blueprint Structs.
StructID = index of Struct in list.
This list is saved only if the Placeable contains at least
1 item in its inventory.
The Fields in an InventoryObject Struct vary depending on whether the inventory belongs to a
Placeable Object Blueprint or Instance. For blueprints, an InventoryObject contains the Fields in Table
4.1.3 plus those in Table 4.2.2.
Table 4.2.2: Fields in InventoryObject Blueprint Structs
Label
Type
Description
InventoryRes
CResRef
ResRef of UTI Item Blueprint file
4.3. Placeable Instance Struct
Placeable Object Instances placed in the toolset contain the Fields listed in Tables 2.1.1, 2.3, and 4.1.1.
Table 4.3.1: Fields Unique to Placeable Structs
Label
Type
Description
ItemList
List
List of InventoryObject instance Structs.
StructID = index of Struct in list.
This list is saved only if the Placeable contains at least
1 item in its inventory.
The Fields in an InventoryObject Struct vary depending on whether the inventory belongs to a
Placeable Object Blueprint or Instance. For instances, an InventoryObject contains the Fields in Table
4.1.3 plus all the Fields normally contained in an Item Instance. See the Item Format document for
details.
4.4. Placeable Game Instance Fields
After a GIT file has been saved by the game, the Placeable Instance Struct contains the Fields in
Tables 2.1.1, 2.3, 2.4, 4.1.1, and 4.4.
Table 4.4: Fields in Placeable Instance Structs in SaveGames
Label
Type
Description
Animation
INT
Game animation state.
0 = default
72 = destroyed
73 = activated
74 = deactivated
75 = opened
76 = closed
AnimationState

### BYTE

This Field is removed by a savegame and replaced by
the Animation Field given above.
DieWhenEmpty

### BYTE

1 for body bag placeables that fade away after they
have been fully looted.
0 for all normal placeable objects and non-fading body

## Page 9

BioWare Corp.
<http://www.bioware.com>
bags.
GroundPile

### BYTE

Obsolete Field. Always 0.
LightState

### BYTE

1 if the light attached to this object is on
0 if the light attached to this object is off, or there is no
light.
Portal
CExoString
Portal Info. Used by the DM droppable portals.
TrapCreator

### DWORD

Object ID of player who placed trap on this object
TrapFaction

### DWORD

Faction ID of the trap placed on this object.
4.5. Placeable 2DA files
4.5.1. Placeables
Table 4.5.1: placeables.2da columns
Column
Type
Description
Label
String
Programmer label
StrRef
Integer
StrRef of the name to show in the toolset
ModelName
String
ResRef of MDL file to use as the model of the Placeable.
LightColor
Integer
Index into lightcolor.2da, specifying the color to use for a
Light object to spawn in with the placeable object's model.

If ****, then do not spawn in a light.
Otherwise, spawn in "fx_placeable01.mdl" as a light
source, and set its colors as specified in lightcolor.2da.

See Table 2.5b in the Area File Format document for a
description of lightcolor.2da.
LightOffsetX
LightOffsetY
LightOffsetZ
Float
Offset in meters by which the light model's "root" node
should be moved after it has been spawned. Spawn in the
light at the same location as the placeable.
SoundAppType
Integer
Index into placeableobjsnds.2da
ShadowSize
Integer
always 1
BodyBag
Integer
Index into bodybag.2da.
LowGore
String
ResRef of alternate MDL to use if the one listed under
ModelName is too violent for the current violence settings
in the game.
4.5.2. Placeable Object Sounds
Table 4.5.2: placeableobjsnds.2da columns
Column
Type
Description
Label
String
Programmer label
ArmorType
String
Determines sound to make when hit in combat. Possible
values are:
wood
stone
plate
leather
Value is used to randomly select a similarly named column
in weaponsounds.2da, and the actual sound depends on
which row of weaponsounds.2da is used by the weapon
that is hitting the object.
Opened
String
ResRef of WAV file to play
Closed
String
ResRef of WAV file to play

## Page 10

BioWare Corp.
<http://www.bioware.com>
Destroyed
String
ResRef of WAV file to play
Used
String
ResRef of WAV file to play
Locked
String
ResRef of WAV file to play
4.5.3. Bodybags
Table 4.5.3: bodybag.2da columns
Column
Type
Description

### LABEL

String
Programmer label
Name
Integer
StrRef of the name to show in the toolset
Appearance
Integer
Index into placeables.2da

### See also

- [GFF-UTD](GFF-Spatial-Objects#utd)
- [GFF-UTP](GFF-Spatial-Objects#utp) -- KotOR door and placeable implementation
- [GFF-File-Format](GFF-File-Format) -- GFF structure
- [GFF-GIT](GFF-Module-and-Area#git) -- Door and placeable instances
- [2DA-placeables](2DA-File-Format#placeables2da)
- [2DA-doortypes](2DA-File-Format#doortypes2da) -- Appearance tables
- [Container-Formats#key](Container-Formats#key) -- Resource resolution


---

<a id="trigger"></a>

# Trigger

*Official Bioware Aurora Documentation*

> **Note**: This official BioWare documentation was originally written for **Neverwinter Nights**, but the Trigger (UTT) format is **identical in KotOR**. All structures, fields, and behaviors described here apply to KotOR as well. The examples may reference NWN-specific features, but the core format is the same.

---

## Page 1

BioWare Corp.
<http://www.bioware.com>
BioWare Aurora Engine
Trigger Format

1. Introduction
A Trigger is a set of vertices defining a region that players and creatures can interact with. Two
common types of Trigger are Area Transitions and Traps.
Triggers are stored in the game and toolset using BioWare's Generic File Format (GFF), and it is
assumed that the reader of this document is familiar with GFF.
Trigger objects can be blueprints or instances. Trigger blueprints are saved as GFF files having a UTT
extension and "UTT " as the FileType string in their header. Trigger instances are stored as Trigger
Structs within a module's GIT files.
2.Trigger Struct
The tables in this section describe the GFF Struct for a Trigger object. Some Fields are only present on
Instances and others only on Blueprints.
For List Fields, the tables indicate the StructID used by the List elements.
2.1 Common Trigger Fields
The Table below lists the Fields that are present in all Trigger Structs, regardless of where they are
found.
Some Fields only make sense if the Trigger is an Area Transition, while other Fields make sense only if
the Trigger is a Trap. See the Field desription for details.
Table 2.1: Fields in all Trigger Structs
Label
Type
Description
AutoRemoveKey

### BYTE

Not used.
Originally intended use: Property for Area Transition
Triggers.
1 = remove the key object from the player that uses this
Area Transition
0 = leave key on player after passing through the Area
Transition
Cursor

### BYTE

Index into cursors.2da.
Specifies a special mouse cursor icon to use when the
player mouses over the Trigger.
0 means there is no mouseover cursor feedback.

Game should use the specified cursor only if the
OnClick event is non-empty.

Area Transition triggers should always have the cursor
set to 1 by the toolset. For Area Transitions, the game
ignores the Cursor value anyway and always uses
Cursor 1.

## Page 2

BioWare Corp.
<http://www.bioware.com>
See section below on cursors.2da.
DisarmDC

### BYTE

If the Trigger is a Trap (Type == 2), then this is the DC
to disarm the trap. Toolset enforces 1-250 range.
Faction

### DWORD

ID of the Faction that the Trigger belongs to. A Trap
Trigger will only go off for creatures that are hostile to
its Faction.
The Faction ID is the index of the Faction in the
module's Faction.fac file.
HighlightHeight

### FLOAT

Some Triggers have a highlight color ingame (Area
Transitions are blue, Traps are red, and clickable
generic triggers are green).
If the trigger highlights, this is the height in metres
above the ground that the highlight extends. Anything
within the Trigger boundaries will be lit by the trigger
highlight color up to this height.
KeyName
CExoString
Not used.
Originally intended use: If the Trigger is an Area
Transition, this is the Tag of an item that the
transitioning creature must be carrying in order to use
the Area Transition.
LinkedTo
CExoString
Tag of the object that this Area Transition links to.
LinkedToFlags

### BYTE

0 if the Trigger does not link to anything
1 if the Trigger is an Area Transition and links to a
Door.
2 if the Trigger is an Area Transition and links to a
Waypoint.
LoadScreenID

### WORD

Index into loadscreens.2da.
Specifies a loading screen to use when following this
Area Transition, if the transition causes the player to go
to a different area.
If LoadScreenID == 0, then use the default loading
screen as specified by the destination area.
See Section 2.3 in the Area GFF doc.
LocalizedName
CExoLocString
Name of the trigger as it appears on the toolset's
Trigger palette and in the Name field of the toolset's
Trigger Properties dialog.
Does not appear in game.
OnClick
CResRef
ResRef of OnClick event. If this is not blank, then the
Toolset will allow the Cursor Field to be set.
OnDisarm
CResRef
OnDisarm event. Applies to Trap Triggers.
OnTrapTriggered
CResRef
OnTrapTriggered event
PortraitId

### WORD

Index into portraits.2da.
See section below on portraits.2da.
ScriptHeartbeat
CResRef
OnHeartbeat event
ScriptOnEnter
CResRef
OnEnter event
ScriptOnExit
CResRef
OnExit event
ScriptUserDefine CResRef
OnUserDefined event
Tag
CExoString
Tag of the Trigger. Up to 32 characters
TemplateResRef
CResRef
For blueprints (UTT files), this should be the same as
the filename.
For instances, this is the ResRef of the blueprint that
the instance was created from.
TrapDetectable

### BYTE

1 if Trap can be detected, 0 if not
TrapDetectDC

### BYTE

DC to detect the Trap. Toolset enforces 1-250 range.
TrapDisarmable

### BYTE

1 if Trap can be disarmed, 0 if not

## Page 3

BioWare Corp.
<http://www.bioware.com>
TrapFlag

### BYTE

1 if the Trigger is a Trap, 0 if not
TrapOneShot

### BYTE

1 if the Trap disappears after firing, 0 otherwise
TrapType

### BYTE

Index into traps.2da.
Specifies the trap type, if the Trigger is a Trap.
See section below on traps.2da.
Type
INT
Trigger Type
0 = Generic
1 = Area Transition
2 = Trap
If the Type is 1 (Area Transition) then LinkedToFlags
must be greater than 0.
If the Type is 2 (Trap) then TrapFlag must also be 1.
2.2. Trigger Blueprint Fields
The Top-Level Struct in a UTW file contains all the Fields in Table 2.1 above, plus those in Table 2.2
below.
Table 2.2: Fields in Trigger Blueprint Structs
Label
Type
Description
Comment
CExoString
Module designer comment.
PaletteID

### BYTE

ID of the node that the Trigger Blueprint appears under
in the Trigger palette.
TemplateResRef
CResRef
The filename of the UTT file itself. It is an error if this
is different. Certain applications check the value of this
Field instead of the ResRef of the actual file.
If you manually rename a UTT file outside of the
toolset, then you must also update the TemplateResRef
Field inside it.
2.3. Trigger Instance Fields
A Trigger Instance Struct in a GIT file contains all the Fields in Table 2.1, plus those in Table 2.3.1
below.
Table 2.3.1: Fields in Trigger Instance Structs (Struct ID 1)
Label
Type
Description
Geometry
List
List of Point Structs (StructID 3) defining the vertices
of the Trigger polygon. See Table 2.3.2.
The polygon is drawn by starting at the first Point
element and drawing a line to each subsequent Point,
then connecting the last one back to the first.
See section 4 for additional rules governing the
Geometry of a Trigger.
TemplateResRef
CResRef
For instances, this is the ResRef of the blueprint that
the instance was created from.
XOrientation
YOrientation

### FLOAT

Orientation of the Trigger. The X and Y components
should both always be zero. If not, the Trigger may
render strangely and incorrectly in the toolset. The
game ignores the orientation.
XPosition
YPosition
ZPosition

### FLOAT

(x,y,z) coordinates of the Trigger within the Area that it
is located in.
The Points in the Trigger Geometry have their
coordinates specified relative to the Trigger's own

## Page 4

BioWare Corp.
<http://www.bioware.com>
location.
Table 2.3.2: Fields in Point Struct (Struct ID 3)
Label
Type
Description
PointX
PointY
PointZ

### FLOAT

(x,y,z) coordinates of the Point, assuming that the
origin is at the owner Trigger's position.
The points in the Trigger's Geometry List use a coordinate system where the origin is the Trigger's own
position. For example, suppose that a Trigger has (XPosition, YPosition, ZPosition) = (10, 20, 30). If
the Geometry contains a Point at (PointX, PointY, PointZ) = (0, 0, 0), then the actual coordinates of
that Point are (10, 20, 30). Similarly, if there is another Point belonging to the same Trigger has
coordinates (PointX, PointY, PointZ) = (1, 2, -10), then the actual coordinates of that Point are (11, 22,
20).
There is no requirement that any Point in the List be at (0,0,0), nor is there any requirement against it.
2.4 Trigger Game Instance Fields
After a GIT file has been saved by the game, the Trigger Instance Struct not only contains the Fields in
Table 2.1 and Table 2.3.1, it also contains the Fields in Table 2.4.
INVALID_OBJECT_ID is a special constant equal to 0x7f000000 in hex.
Table 2.4: Fields in Trigger Instance Structs in SaveGames
Label
Type
Description
ActionList
List
List of Actions stored on this object
StructID 0. See Section 6 of the Common GFF
Structs document.
CreatorId

### DWORD

Object ID of the Trigger's creator.
For Traps set by a player, this is the player's Object ID.
For Triggers painted in the toolset and loaded by the
game, this is equal to the INVALID_OBJECT_ID
constant.
ObjectId

### DWORD

Object ID used by game for this object.
VarTable
List
List of scripting variables stored on this object.
StructID 0. See Section 3 of the Common GFF
Structs document.
3. The 2DA Files Referenced by Trigger Fields
3.1. Cursor
In a Trigger Struct, the Cursor Field is an index into cursors.2da.
Cursors.2da is used mainly by the toolset in order to obtain a list of cursors that can be assigned to
Triggers. The game maintains its own,much larger, internal list of cursors.
Table 3.1: cursors.2da columns
Column
Type
Description
Label
String
Programmer label
ResRef
String
ResRef of TGA texture to use as the icon for the mouse
cursor when the user mouses over the Trigger. Used by
toolset to show the selected icon, but not by game.

## Page 5

BioWare Corp.
<http://www.bioware.com>
CursorID
Integer
Index to game's internal cursor list
Below is a list of the cursor types defined by the game, and referenced by the CursorID column of
cursors.2da.

### MOUSECURSOR_DEFAULT          1

### MOUSECURSOR_DEFAULT_DOWN     2

### MOUSECURSOR_WALK             3

### MOUSECURSOR_WALK_DOWN        4

### MOUSECURSOR_NOWALK           5

### MOUSECURSOR_NOWALK_DOWN      6

### MOUSECURSOR_ATTACK           7

### MOUSECURSOR_ATTACK_DOWN      8

### MOUSECURSOR_NOATTACK         9

### MOUSECURSOR_NOATTACK_DOWN    10

### MOUSECURSOR_TALK             11

### MOUSECURSOR_TALK_DOWN        12

### MOUSECURSOR_NOTALK           13

### MOUSECURSOR_NOTALK_DOWN      14

### MOUSECURSOR_FOLLOW           15

### MOUSECURSOR_FOLLOW_DOWN      16

### MOUSECURSOR_EXAMINE          17

### MOUSECURSOR_EXAMINE_DOWN     18

### MOUSECURSOR_NOEXAMINE        19

### MOUSECURSOR_NOEXAMINE_DOWN   20

### MOUSECURSOR_TRANSITION       21

### MOUSECURSOR_TRANSITION_DOWN  22

### MOUSECURSOR_DOOR             23

### MOUSECURSOR_DOOR_DOWN        24

### MOUSECURSOR_USE              25

### MOUSECURSOR_USE_DOWN         26

### MOUSECURSOR_NOUSE            27

### MOUSECURSOR_NOUSE_DOWN       28

### MOUSECURSOR_MAGIC            29

### MOUSECURSOR_MAGIC_DOWN       30

### MOUSECURSOR_NOMAGIC          31

### MOUSECURSOR_NOMAGIC_DOWN     32

### MOUSECURSOR_DISARM           33

### MOUSECURSOR_DISARM_DOWN      34

### MOUSECURSOR_NODISARM         35

### MOUSECURSOR_NODISARM_DOWN    36

### MOUSECURSOR_ACTION           37

### MOUSECURSOR_ACTION_DOWN      38

### MOUSECURSOR_NOACTION         39

### MOUSECURSOR_NOACTION_DOWN    40

### MOUSECURSOR_LOCK             41

### MOUSECURSOR_LOCK_DOWN        42

### MOUSECURSOR_NOLOCK           43

### MOUSECURSOR_NOLOCK_DOWN      44

### MOUSECURSOR_PUSHPIN          45

### MOUSECURSOR_PUSHPIN_DOWN     46

### MOUSECURSOR_CREATE           47

### MOUSECURSOR_CREATE_DOWN      48

### MOUSECURSOR_NOCREATE         49

### MOUSECURSOR_NOCREATE_DOWN    50

### MOUSECURSOR_KILL             51

### MOUSECURSOR_KILL_DOWN        52

### MOUSECURSOR_NOKILL           53

## Page 6

BioWare Corp.
<http://www.bioware.com>

### MOUSECURSOR_NOKILL_DOWN      54

### MOUSECURSOR_HEAL             55

### MOUSECURSOR_HEAL_DOWN        56

### MOUSECURSOR_NOHEAL           57

### MOUSECURSOR_NOHEAL_DOWN      58

### MOUSECURSOR_ARRUN00          59

### MOUSECURSOR_ARRUN01          60

### MOUSECURSOR_ARRUN02          61

### MOUSECURSOR_ARRUN03          62

### MOUSECURSOR_ARRUN04          63

### MOUSECURSOR_ARRUN05          64

### MOUSECURSOR_ARRUN06          65

### MOUSECURSOR_ARRUN07          66

### MOUSECURSOR_ARRUN08          67

### MOUSECURSOR_ARRUN09          68

### MOUSECURSOR_ARRUN10          69

### MOUSECURSOR_ARRUN11          70

### MOUSECURSOR_ARRUN12          71

### MOUSECURSOR_ARRUN13          72

### MOUSECURSOR_ARRUN14          73

### MOUSECURSOR_ARRUN15          74

### MOUSECURSOR_ARWALK00         75

### MOUSECURSOR_ARWALK01         76

### MOUSECURSOR_ARWALK02         77

### MOUSECURSOR_ARWALK03         78

### MOUSECURSOR_ARWALK04         79

### MOUSECURSOR_ARWALK05         80

### MOUSECURSOR_ARWALK06         81

### MOUSECURSOR_ARWALK07         82

### MOUSECURSOR_ARWALK08         83

### MOUSECURSOR_ARWALK09         84

### MOUSECURSOR_ARWALK10         85

### MOUSECURSOR_ARWALK11         86

### MOUSECURSOR_ARWALK12         87

### MOUSECURSOR_ARWALK13         88

### MOUSECURSOR_ARWALK14         89

### MOUSECURSOR_ARWALK15         90

### MOUSECURSOR_PICKUP           91

### MOUSECURSOR_PICKUP_DOWN      92

3.2. Portrait
In a Trigger Struct, the PortraitId Field is an index into portraits.2da.
Table 3.2.1: portraits.2da columns
Column
Type
Description
BaseResRef
String
"Base" ResRef of TGA texture file to use as the portrait.
The actual ResRef used depends on the portrait size to
display.

To get the actual ResRef, prepend "po_" to the
BaseResRef, and append one of the following letters:

h = huge (256x512 pixels), size used in character creation
portrait selection

## Page 7

BioWare Corp.
<http://www.bioware.com>
l = large (128x256), appears in Character Record sheet in
game.

m = medium (64x128), appears in centre of radial menu, in
conversation window, examine window, and as player
portrait in upper right corner.

s = small (32x64), appears as party member portraits along
right-hand side of game GUI.

t = tiny (16x32) appears in chat window, and in text
bubbles if text bubble mode is set to "Full" in Game
Options|FeedBack Options.
Sex
Integer
Index into gender.2da
Race
Integer
Index into racialtypes.2da, or **** for door and plaeable
object portraits.
InanimateType
Integer
Index into placeabletypes.2da, or **** for creature
portraits
Plot
Integer
0 for normal portraits.
1 if portrait is for a plot character. Shows up when the
"Plot Characters" radio button is selected in the toolset's
Select Portrait dialog. Plot portraits do not show up for
selection in the game during character creation.
LowGore
String
Alternate version of BaseResRef to use if the game
violence settings are low.
The various columns in portraits.2da allow the game and toolset to filter which portraits appear for
selection by the user.
The Sex column in Portraits.2da references gender.2da. For a portrait to show up in the game during
character creation, it should have a Sex of 0 or 1
The Portrait Selection dialog in the toolset allows filtering by Gender, using a dropdown list that gets
its entries from the NAME StrRef in gender.2da.
Table 3.2.2: gender.2da columns
Column
Type
Description

### NAME

Integer
StrRef of the gender.

### GENDER

String
single capital letter abbreviation

### GRAPHIC

String
Not used

### CONSTANT

String
Identifier to use in scripting to refer to the gender. Used in
toolset Script Wizard to autogenerate source code for a
script.
The Race column in Portraits.2da references racialtypes.2da.
For a portrait to show up in the game during character creation, it should belong to a player race. To
determine if the race is player-selectable, check the Race column in portraits.2da, look it up on
racialtypes.2da, and check the corresponding PlayerRace column.
The Portrait Selection dialog in the toolset allows filtering by Race, using a dropdown list that gets its
entries from the Name StrRef in racialtypes.2da.

## Page 8

BioWare Corp.
<http://www.bioware.com>
Table 3.2.3: racialtypes.2da columns
Column
Type
Description
Label
String
Programmer label
Abrev
String
Two-letter abbreviation of the race name.
Formerly used by toolset but not anymore.
Name
Integer
StrRef of the race name as a capitalized singular noun.
Example of text that it points to: "Dwarf", "Elf"
ConverName
Integer
StrRef of the race name as used by the conversation token
<Race>. eg., "Dwarven", "Elven"
ConverNameLower
Integer
StrRef of race name as used by the <race> token.
eg., "dwarven", "elven"
NamePlural
Integer
StrRef of the race name as a capitalized plural noun.
eg., "Dwarves", "Elves"
Description
Integer
StrRef of a description of the race. Seen in character
creation.
Appearance
Integer
Index into appearance.2da.
Default appearance to use for creatures of this race.
StrAdjust
DexAdjust
IntAdjust
ChaAdjust
WisAdjust
ConAdjust
Integer
Adjustments to the creature's ability scores. Dynamically
applied ingame. In general, when saving a creature's ability
scores, the saved score is before the racial adjustment.
Endurance
Integer
not used
Favored
Integer
Index into classes.2da.
Specifies race's favored class.
FeatsTable
String
ResRef of a 2da listing the feats that this race
automatically gets.
Biography
Integer
StrRef of default text to use as a player character's
biography.
PlayerRace
Integer
1 if player-selectable race, 0 if not.
Constant
String
Identifier to use in scripting to refer this race. Used by
toolset's Script Wizard to autogenerate script source code.
Age
Integer
Default age to provide during character creation.
ToolsetDefaultClass
Integer
Index into classes.2da.
Default class to pick when creating a creature of this race
in the toolset Creature Wizard.
CRModifier
Float
Value by which to multiply the final CR calculated for a
creature in the toolset.
The InanimateType column in Portraits.2da references placeabletypes.2da.
The Portrait Selection dialog in the toolset allows filtering by InanimateType, using a dropdown list
that gets its entries from the StrRef column in placeabletypes.2da.
Table 3.2.4: placeabletypes.2da columns
Column
Type
Description
Label
String
Programmer label
StrRef
Integer
StrRef of text to display to user
3.3. TrapType
In a Trigger Struct, the TrapType Field is an index into traps.2da.

## Page 9

BioWare Corp.
<http://www.bioware.com>
Table 3.3: traps.2da columns
Column
Type
Description
Label
String
Programmer label
TrapScript
String
ResRef of script to run when the Trap is triggered
SetDC
Integer
DC for a player with the Set Traps skill to set a Trap of
this type.
DetectDCMod
Integer
Modifier added to the DC to detect a trap of this type when
it is set by a player.
The total detect DC is the player's Set Trap skill check plus
this modifier.
DisarmDCMod
Integer
Modifier to added to the DC to disarm a trap of this type
when it is set by a player.
The total disarm DC is the player's Set Trap skill check
plus this modifier.
TrapName
Integer
StrRef of the name of the trap. This appears when a player
successfully examines the trap ingame. It is also the text
that appears in the toolset when selecting the TrapType for
a Trap.
ResRef
String
ResRef of the corresponding trap kit Item blueprint (UTT
file).
If a player successfully recovers a trap of this type, then an
instance of the specified item is added to the player's
inventory.
IconResRef
String
ResRef of a TGA icon to display as the portrait for the trap
when it is successfully examined ingame.
4. Geometry Rules for the Point List
In a Trigger instance, the Geometry List contains the points that define the outline of the Trigger.
The toolset must enforce several rules for polygon geometry, as given below. Note that the "Single
Inner Surface" and "No Crossing Lines" rules below apply to just the x and y coordinates of the points
in the Geometry List, with the z coordinates ignored.
4.1. Minimum number of Points
There must be a minimum of three Points in the Geometry List to ensure that the polygon actually has
a visible area.
4.2. Single Inner Surface
There must be only one "inside" surface.
For example, a figure-8 as shown in Figure 4.2a is illegal, and will be reduced to being just the upper
portion or the lower portion, as shown in Figure 4.2b. The numbers in Figure 4.2a indicate the order in
which the user painted the vertices, while the numbers in Figure 4.2b indicate the order of the vertices
after the toolset's geometry conversion.

## Page 10

BioWare Corp.
<http://www.bioware.com>
Figure 4.2a: user-drawn polygon with multiple inner surfaces
0
1
2
3
Figure 4.2b: final resolved polygon with extra surfaces removed
0
1
2

4.3. No Crossing Lines
None of the lines connecting the Points should cross.
For example, suppose the user draws a 5-vertex pentragram as shown in Figure 4.3a. The numbers in
the figure indicate the order in which the user painted the vertices.
Figure 4.3a: user-drawn pentagram with crossing lines
0
1
3
4
2

The toolset would convert the geometry so that it becomes a 5-pointed star consisting of 10 vertices
and one contiguous inside area uncrossed by any lines, as shown in Figure 4.3b. The numbers in the
figure indicate the order of the vertices after the toolset's geometry conversion.
Figure 4.3b: final resolved pentagram with no crossing lines
2
2
3
4
6
7
8
9
0
1
5

Although lines may not cross, it is permissible for two points to share the exact same location, such as
points 0 and 3 in Figure 4.3c. None of the lines in Figure 4.3c are considered to cross, even though the

## Page 11

BioWare Corp.
<http://www.bioware.com>
endpoints of four lines do touch. It is, however, next to impossible in the toolset for a user to actually
paint a figure where two points are exactly coincident as in 4.3c, so this special case is more of a
curiosity than anything else.
Figure 4.3c: user-drawn polygon with touching points but no crossing lines
0
1
2
3
4
5

4.4. Leftmost Point First
As a matter of convention, the Point having the smallest x-coordinate is used as the first point in the
Point List. If more than one Point is tied for having the smallest x-coordinate, then the first such point
that was drawn by the user is the one that is used. Figure 4.3b shows the application of this rule to the
figure show in Figure 4.3a.
This rule is not required, in that if the points were in a different order, the toolset and game would still
load the polygon correctly and without errors.

### See also

- [GFF-UTT](GFF-Spatial-Objects#utt) -- KotOR trigger implementation
- [GFF-File-Format](GFF-File-Format) -- GFF structure
- [GFF-GIT](GFF-Module-and-Area#git) -- Trigger instances
- [NSS-File-Format](NSS-File-Format) -- Trigger scripts
- [Container-Formats#key](Container-Formats#key) -- Resource resolution


---

<a id="waypoint"></a>

# Waypoint

*Official Bioware Aurora Documentation*

> **Note**: This official BioWare documentation was originally written for **Neverwinter Nights**, but the Waypoint (UTW) format is **identical in KotOR**. All structures, fields, and behaviors described here apply to KotOR as well. The examples may reference NWN-specific features, but the core format is the same.

---

## Page 1

BioWare Corp.
<http://www.bioware.com>
BioWare Aurora Engine
Waypoint Format

1. Introduction
A Waypoint is a simple object type used for scripting and showing map notes to the player.
Waypoints are stored in the game and toolset using BioWare's Generic File Format (GFF), and it is
assumed that the reader of this document is familiar with GFF.
Waypoint objects can be blueprints or instances. Waypoint blueprints are saved as GFF files having a
UTW extension and "UTW " as the FileType string in their GFF header. Waypoint instances are stored
as Waypoint Structs within the a module's GIT files.
2. Waypoint Struct
The tables in this section describe the GFF Struct for a Waypoint object. Some Fields are only present
on Instances and others only on Blueprints.
For List Fields, the tables indicate the StructID used by the List elements.
2.1 Toolset Waypoint Fields
2.1.1 Common Waypoint Fields
The Table below lists the Fields that are present in all Waypoint Structs, regardless of where they are
found.
Table 2.1.1.1: Fields in all Waypoint Structs
Label
Type
Description
Appearance

### BYTE

Index into waypoint.2da.
Determines only what the waypoint model looks like in
the toolset. Has no effect on game.
Description
CExoLocString
Localized description of waypoint. Only visible in
toolset.
HasMapNote

### BYTE

1 if Waypoint has a map note, 0 otherwise.

If HasMapNote == 0, then in the toolset, the "Map
Note Text" and "Map Note Enabled" controls will still
have their proper values as stored in the MapNote and
MapNoteEnabled Fields, but they will be greyed out.
LinkedTo
CExoString
Tag of object that waypoint is linked to. Unused and
always blank.
LocalizedName
CExoLocString
Localized name of waypoint.
This name appears in the Waypoint palette.
MapNote
CExoLocString
Text that appears ingame when user mouses over the
Waypoint in the Minimap.
MapNoteEnabled

### BYTE

1 if the Waypoint's Map Note is visible in the Minimap
in the game, 0 otherwise.
Tag
CExoString
Tag of the waypoint. Can be up to 32 characters long.
The Appearance Field is an index into waypoint.2da, which is described by the table below:

## Page 2

BioWare Corp.
<http://www.bioware.com>
Table 2.1.1.2: waypoint.2da columns
Column
Type
Description

### LABEL

String
Programmer label

### RESREF

String
ResRef of MDL file to use as the model for the waypoint
in the toolset's area viewer.

### STRREF

Integer
StrRef of localized text description to show to user in the
Appearance dropdown in the toolset's Waypoint Properties
dialog.
2.1.2. Waypoint Blueprint Fields
The Top-Level Struct in a UTW file contains all the Fields in Table 2.1.1.1 above, plus those in Table
2.1.2 below.
Table 2.1.2: Fields in Waypoint Blueprint Structs
Label
Type
Description
Comment
CExoString
Module designer comment.
PaletteID

### BYTE

ID of the node that the Waypoint Blueprint appears
under in the Waypoint palette.
TemplateResRef
CResRef
The filename of the UTW file itself. It is an error if this
is different. Certain applications check the value of this
Field instead of the ResRef of the actual file.
If you manually rename a UTW file outside of the
toolset, then you must also update the TemplateResRef
Field inside it.
2.1.3. Waypoint Instance Fields
A Waypoint Instance Struct in a GIT file contains all the Fields in Table 2.1.1.1, plus those in Table
2.1.3 below.
Table 2.1.3: Fields in Waypoint Instance Structs (StructID 5)
Label
Type
Description
TemplateResRef
CResRef
The ResRef of the blueprint that the instance was
created from.
XOrientation
YOrientation

### FLOAT

x and y components of a unit vector that points in the
direction that the waypoint faces.
Or in other words, the cosine and sine, respectively, of
the waypoint's bearing in the xy plane, measured as an
angle counterclockwise from the positive x-axis.
XPosition
YPosition
ZPosition

### FLOAT

(x,y,z) coordinates of the Waypoint within the Area
that it is located in.
2.2 Game Waypoint Fields
The information discussed in this section is used only by saved games, and is not required by the
toolset. Editing the fields listed in this section can readily lead to corrupted save games.
After a GIT file has been saved by the game, the Waypoint Instance Struct contains not only the Fields
in Table 2.1.1.1 and Table 2.1.3, it also contains the Fields in Table 2.2.

## Page 3

BioWare Corp.
<http://www.bioware.com>
Table 2.2: Fields in Waypoint Instance Structs in SaveGames
Label
Type
Description
ActionList
List
List of Actions stored on this object
StructID 0. See See Section 6 of the Common GFF
Structs document.
ObjectId

### DWORD

Object ID used by game for this object.
VarTable
List
List of scripting variables stored on this object.
StructID 0. See Section 3 of the Common GFF
Structs document.

### See also

- [GFF-UTW](GFF-Spatial-Objects#utw) -- KotOR waypoint implementation
- [GFF-File-Format](GFF-File-Format) -- GFF structure
- [GFF-GIT](GFF-Module-and-Area#git) -- Waypoint instances
- [GFF-PTH](GFF-Spatial-Objects#pth) -- Path data
- [Container-Formats#key](Container-Formats#key) -- Resource resolution


---

<a id="soundobject"></a>

# SoundObject

*Official Bioware Aurora Documentation*

> **Note**: This official BioWare documentation was originally written for **Neverwinter Nights**, but the Sound Object (UTS) format is **identical in KotOR**. All structures, fields, and behaviors described here apply to KotOR as well. The examples may reference NWN-specific features, but the core format is the same.

**Source:** This documentation is extracted from the official BioWare Aurora Engine SoundObject Format PDF, archived in **[xoreos-docs](https://github.com/xoreos/xoreos-docs)**: [`specs/bioware/SoundObject_Format.pdf`](https://github.com/xoreos/xoreos-docs/blob/master/specs/bioware/SoundObject_Format.pdf). The original documentation was published on the now-defunct nwn.bioware.com developer site.

---

## Page 1

BioWare Corp.
<http://www.bioware.com>
BioWare Aurora Engine
Sound Object Format

1. Introduction
A Sound object is a source of sounds that play in an Area. They may be positional, playing from a
specific location, or they may be area-wide, sounding the same regardless of where in the area the
listener is.
Sounds are stored in the game and toolset using BioWare's Generic File Format (GFF), and it is
assumed that the reader of this document is familiar with GFF.
Sound objects can be blueprints or instances. Sound blueprints are saved as GFF files having a UTS
extension and "UTS " as the FileType string in their header. Sound instances are stored as Sound
Structs within a module's GIT files.
2. Sound Struct
The tables in this section describe the GFF Struct for a Sound object. Some Fields are only present on
Instances and others only on Blueprints.
For List Fields, the tables indicate the StructID used by the List elements.
2.1 Common Sound Fields
The Table below lists the Fields that are present in all Sound Structs, regardless of where they are
found.
Table 2.1: Fields in all Sound Structs
Label
Type
Description
Active

### BYTE

1 if the Sound is active and plays.
0 if the Sound is inactive and is not currently playing
any wave files. Inactive Sounds can be manually
activated via scripting.
Continuous

### BYTE

1 if the Sound is continuous, or seamlessly looping. A
continuous sound must have exactly one wave file to
play, and it loops that wave continuously, over and
over with no pauses.
0 if the sound is not continuous. That is, it consists of
one or more wave files played individually. These
waves may play in sequence, in random order, or with
random or non-random pauses inbetween them.

If a Sound is Continuous, then the values of the
following Fields are ignored and always treated as 0:
Interval, IntervalVrtn, PitchVariation, Random,
RandomPositional, RandomRangeX, RandomRangeY,
VolumeVrtn.
Elevation

### FLOAT

Elevation of the Sound above or below the XYZ

## Page 2

BioWare Corp.
<http://www.bioware.com>
position at which it is placed in the toolset. When it
plays, the audio emanates from the elevated position.
Elevation can be negative.
Hours

### DWORD

Set of bit flags specifying which hours of the day the
sound will play in. Bit 0 is hour 00h00, bit 6 is 06h00,
bit 14 is 14h00, etc.
Interval

### DWORD

Interval in milliseconds between playing sounds in the
Sound's list of waves.
IntervalVrtn

### DWORD

Interval Variation measured in milliseconds.
Each time a wave file finishes playing, determine how
long to wait before playing the next one.Ggenerate a
random number ranging from (-InternalVrtn) to
(+IntervalVrtn), and add that to the Interval. If the
resulting value is negative, treat it as 0 and play the
next wave immediately.
LocName
CExoLocString
Name of the Sound as it appears on the toolset's Sound
palette and in the Name field of the toolset's Sound
Properties dialog.
Does not appear in game.
Looping

### BYTE

1 if the Sound repeatedly plays its waves.
0 if the Sound plays its waves at most once then
becomes inactive.
MaxDistance

### FLOAT

Radius in meters outside which a listener cannot hear
the Sound at all.
Must be greater than or equal to the MinDistance.
MinDistance

### FLOAT

Radius in meters inside which a listener hears the
Sound at maximum volume.
Must be less than or equal to the MaxDistance.
PitchVariation

### FLOAT

Pitch variation when playing waves in the Sound's lis t
of waves, measured in octaves. Values from 0 to 1.0.
A 0 pitch variation means the Sound always plays at
normal pitch. A variation of 1 means that each time the
a wave plays, its pitch is randomly anywhere from 0 to
1 octave higher or lower than normal.
Positional

### BYTE

1 if the Sound plays from a specific position. The
volume changes depending on the distance of the
listener, and the relative volume from each
speaker/headphone changes depending on the direction
of the listener from the Sound.
0 if the Sound is area-wide, and has the same volume
regardless of where the listener is in relation to the
Sound. An area-wide Sound has no directional
variation by speaker.
Priority

### BYTE

Index into prioritygroups.2da.
Random

### BYTE

1 if the waves in the Sound's wave list are chosen
randomly each time one finishes playing.
0 if the waves are played in sequential order.
RandomPosition

### BYTE

1 if the XYZ position of the Sound source varies
randomly between the RandomRangeX and
RandomRangeY.
0 if the position of the sound does not vary.
This Field is ignored for area-wide (Positional=0)
sounds.
RandomRangeX
RandomRangeY

### FLOAT

Random distance in meters from the Sound's XYZ
position from which the Sound plays each time it plays

## Page 3

BioWare Corp.
<http://www.bioware.com>
a wave.
These Fields are ignored if Positional=0 or
RandomPosition=0.
Sounds
List
The Sound's wave list. A list of wave files to play.
Each Struct in the List has Struct ID 0, and contains a
single CResRef Field called Sound, which is the
ResRef of a WAV file.
Tag
CExoString
Tag of the Sound. Up to 32 characters.
TemplateResRef
CResRef
For blueprints (UTS files), this should be the same as
the filename.
For instances, this is the ResRef of the blueprint that
the instance was created from.
Times

### BYTE

Times of day in which to play the Sound.
0 = time-specific. Use the Hours Field to determine
when to play.
1 = Day
2 = Night
3 = Always
If the Sound plays during the Day or Night, then day
and night are as defined by the Mod_DawnHour and
Mod_DuskHour Fields in the module's module.ifo file.
See Table 2.1 of the IFO document.
Volume

### BYTE

Volume to play each wave file at. Ranges from 0 (min)
to 127 (full)
VolumeVrtn

### BYTE

Volume Variation from 0 to 127.
Each time a wave is to be played, randomly select a
number from (-VolumeVrtn) to (+VolumVrtn) and add
it to the Volume, then clamp the result to the range of 0
to 127 and use that as the actual volume.
The various combinations of the Looping and Random properties merit additional explanation as to
how they interact with each other. There are four options for playing multiple sounds.
Continuously choose a new random sound to play (Random 1, Looping 1) - A sound is randomly
chosen from the sound list and played. Once it has played and the Interval period has passed, another
sound is randomly picked from the list and played. The process repeats forever or until the
SoundObjectStop() scripting function is called.
Play a randomly selected sound once (Random 1, Looping 0) - One sound is randomly chosen from the
list and played. After that, this sound object becomes inactive and no more sounds are played. The
sound object can be reactivated via the SoundObjectPlay() scripting function. This option is most
useful if Active is initially false, and the sound object is manually triggered during the game by using a
script.
Continuously play sounds in order (Random 0, Looping 1) - The first sound in the sound list is played,
then there is a pause corresponding to the Interval, then the next sound is played, then there is a pause
corresponding to the interval, and so on until all the sounds have played. This process repeats forever
or until scripted to stop.
Play list in order once (Random 0, Looping 0) - The sounds are played in order with an Interval delay
between them, and once all the sounds have played, the current sound object deactivates and does not
play again. This option is most useful if Active is false, and the Sound is manually triggered during the
game by using a script.

## Page 4

BioWare Corp.
<http://www.bioware.com>
2.2. Sound Blueprint Fields
The Top-Level Struct in a UTS file contains all the Fields in Table 2.1 above, plus those in Table 2.2
below.
Table 2.2: Fields in Sound Blueprint Structs
Label
Type
Description
Comment
CExoString
Module designer comment.
PaletteID

### BYTE

ID of the node that the Sound Blueprint appears under
in the Sound palette.
TemplateResRef
CResRef
The filename of the UTS file itself. It is an error if this
is different. Certain applications check the value of this
Field instead of the ResRef of the actual file.
If you manually rename a UTS file outside of the
toolset, then you must also update the TemplateResRef
Field inside it.
2.3. Sound Instance Fields
A Sound Instance Struct in a GIT file contains all the Fields in Table 2.1, plus those in Table 2.3
below.
Table 2.3: Fields in Sound Instance Structs
Label
Type
Description
GeneratedType

### BYTE

0 if manually placed by the module builder in the
toolset.
1 if autogenerated by the Area Properties dialog as part
of the current Area's Ambient Day or Ambient Night
Sound. See the AmbientSndDay and AmbientSndNight
properties in Table 3.2 and 3.3 of the Area format
document.
If GeneratedType is 1, then the Sound instance is
subject to automatic deletion when the user picks a
different ambient sound for the area.
TemplateResRef
CResRef
For instances, this is the ResRef of the blueprint that
the instance was created from.
XPosition
YPosition
ZPosition

### FLOAT

(x,y,z) coordinates of the Sound within the Area that it
is located in.
2.4. Sound Game Instance Fields
After a GIT file has been saved by the game, the Sound Instance Struct not only contains the Fields in
Table 2.1 and Table 2.3, it also contains the Fields in Table 2.4.
INVALID_OBJECT_ID is a special constant equal to 0x7f000000 in hex.
Table 2.4: Fields in Sound Instance Structs in SaveGames
Label
Type
Description
ActionList
List
List of Actions stored on this object
StructID 0. See Section 6 of the Common GFF
Structs document.
ObjectId

### DWORD

Object ID used by game for this object.
VarTable
List
List of scripting variables stored on this object.

## Page 5

BioWare Corp.
<http://www.bioware.com>
StructID 0. See Section 3 of the Common GFF
Structs document.
3. The 2DA Files Referenced by Sound Fields
3.1. Priority Groups
In a Sound Struct, the Priority Field is an index into prioritygroups.2da. Table 3.1.1 describes the
columns in the 2da.
The game and toolset are hardcoded to reference particular rows in prioritygroups, so only the
programmers may change the order of rows, or add or remove rows.
Table 3.1.1: prioritygroups.2da columns
Column
Type
Description
Label
String
Programmer label
Priority
Integer
Matches up to hardcoded integer constants in sound engine
source code. This means that you may not add, remove,
or modify the order of rows in prioritygroups.2da.
Volume
Integer
Volume from 0 to 127
MaxPlaying
Integer
Maximum number of sounds of this priority that may play
simultaneously.
Interrupt
Integer
0 if sound may be interrupted
1 if sound may not be interrupted
FadeTime
Integer
When stopping the sound, number of milliseconds of
fadeout.
MaxVolumeDist
Integer
For placed Sound objects instances, the MaxDistance
overrides this 2da value.
MinVolumeDist
Integer
For placed Sound objects instances, the MinDistance
overrides this 2da value.
PlaybackVariance
Float
Pitch variance in octaves when playing sounds of this
priority. Range is 0 to 1.0.
For placed Sound objects instances, the PitchVariance
overrides this 2da value.
Sound objects edited in the toolset always have the priority groups listed in Table 3.1.2, in accordance
with the values of their Looping and Positional Fields. The other rows in prioritygroups.2da are used
for sounds generated by the game.
Table 3.1.2: Toolset Sound Priorities
Row
Description
Looping
Positional
2
Looping area-wide ambients
1
0
3
looping positional ambients
1
1
19
single-shot global
0
0
20
single-shot positional
0
1
3.2. Default Values
There are two 2da files that determine the default values of various Sound object Fields when the user
creates a new sound using the Sound Wizard in the toolset. The Sound Wizard is hardcoded to look up
certain rows in the sounddefaults 2da files depending on the options that the user selected within the
Wizard's GUI.

## Page 6

BioWare Corp.
<http://www.bioware.com>
Table 3.2.1: sounddefaultspos.2da columns
Column
Type
Description
Label
String
Programmer label
RadiusInner
Float
default MinDistance
RadiusOuter
Float
default MaxDistance
RandomRngX
Float
default RandomRangeX
RandomRngY
Float
default RandomRangeY
Height
Float
default Elevation
Table 3.2.2: sounddefaultstim.2da columns
Column
Type
Description
Label
String
Programmer label
Looping
Integer
default Looping
Continuous
Integer
default Continuous
Random
Integer
default Random
Interval
Integer
default Interval
IntervalVar
Integer
default IntervalVrtn
PitchVar
Float
default PitchVrtn
VolumeVar
Float
default VolumeVrtn

### See also

- [GFF-UTS](GFF-Spatial-Objects#uts) -- KotOR sound object implementation
- [GFF-File-Format](GFF-File-Format) -- GFF structure
- [WAV-File-Format](Audio-and-Localization-Formats#wav) -- Audio resources
- [GFF-GIT](GFF-Module-and-Area#git) -- Sound instances
- [Container-Formats#key](Container-Formats#key) -- Resource resolution


---

<a id="encounter"></a>

# Encounter

*Official Bioware Aurora Documentation*

> **Note**: This official BioWare documentation was originally written for **Neverwinter Nights**, but the Encounter (UTE) format is **identical in KotOR**. All structures, fields, and behaviors described here apply to KotOR as well. The examples may reference NWN-specific features, but the core format is the same.

**Source:** This documentation is extracted from the official BioWare Aurora Engine Encounter Format PDF, archived in [`xoreos-docs/specs/bioware/Encounter_Format.pdf`](https://github.com/xoreos/xoreos-docs/blob/master/specs/bioware/Encounter_Format.pdf). The original documentation was published on the now-defunct nwn.bioware.com developer site.

---

## Page 1

BioWare Corp.
<http://www.bioware.com>
BioWare Aurora Engine
Encounter Format

1. Introduction
An Encounter is a set of vertices defining a region that can spawn in a set of creatures when creatures of
certain factions enter it.
Encounters are stored in the game and toolset using BioWare's Generic File Format (GFF), and it is
assumed that the reader of this document is familiar with GFF.
Encounter objects can be blueprints or instances. Encounter blueprints are saved as GFF files having a
UTE extension and "UTE " as the FileType string in their header. Encounter instances are stored as
Encounter Structs within a module's GIT files.
2. Encounter Struct
The tables in this section describe the GFF Struct for an Encounter object. Some Fields are only present
on Instances and others only on Blueprints.
For List Fields, the tables indicate the StructID used by the List elements.
2.1 Common Encounter Fields
The Table below lists the Fields that are present in all Encounter Structs, regardless of where they are
found.
Table 2.1.1: Fields in all Encounter Structs
Label
Type
Description
Active

### BYTE

1 if the Encounter is active and can spawn creatures,
0 if inactive. To be able to spawn, an inactive encounter
must be activated via scripting.
CreatureList
List
List of EncounterCreature Structs. StructID 0.
This is a list of the creatures that the Encounter can
spawn.
Difficulty
INT
Obsolete Field. Should always be identical to the
VALUE in encdifficulty.2da pointed to by the
DifficultyIndex Field.
DifficultyIndex
INT
Index into encdifficulty.2da.
Faction

### DWORD

ID of the Faction that the Encounter belongs to. An
Encounter will only spawn creatures if it is entered by
creatures that are hostile to its Faction.
The Faction ID is the index of the Faction in the
module's Faction.fac file.
LocalizedName
CExoLocString
Name of the Encounter as it appears on the toolset's
Encounter palette and in the Name field of the toolset's
Encounter Properties dialog.
Does not appear in game.
MaxCreatures
INT
Maximum number of creatures that this encounter can
spawn at a time. Toolset limits this to 1 to 8.
Must be greater than or equal to MinCreatures.
OnEntered
CResRef
OnEnter event

## Page 2

BioWare Corp.
<http://www.bioware.com>
OnExhausted
CResRef
OnExhausted event
OnExit
CResRef
OnExit event
OnHeartbeat
CResRef
OnHeartbeat event
OnUserDefined
CResRef
OnUserDefined event
PlayerOnly

### BYTE

0 if any creature can fire this Encounter so long as it is
of a hostile faction.
1 if only player characters can fire the encounter. The
player must still be hostile to the Encounter's faction
for the Encounter to fire.
RecCreatures
INT
Recommended number of creatures. Maps to "Min
Creatures" field in toolset, but is not a true minimum,
because it is actually possible for the encounter system
to spawn fewer than this number of creatures if it
cannot find enough creatures to fit the level of the
encounter.
Must be less than or equal to MaxCreatures.
Toolset restricts this Field to the range 1 to 8.
Reset

### BYTE

0 if the Encounter does not respawn.
1 if the Encounter does respawn.
ResetTime
INT
Number of seconds before Encounter respawns.
Maximum in toolset is 32000 seconds.
Respawns
INT
Number of times to respawn. Maximum in toolset is
32000.
-1 if the Encounter can respawn an infinite number of
times.
SpawnOption
INT
0 = continuous spawn. The encounter continuously
evaluates the hostile creatures inside it and spawns new
creatures as the existing creatures die.
1 = single-shot spawn. The encounter fires once when a
hostile creature enters it.
Tag
CExoString
Tag of the Encounter. Up to 32 characters
TemplateResRef
CResRef
For blueprints (UTE files), this should be the same as
the filename.
For instances, this is the ResRef of the blueprint that
the instance was created from.
Table 2.1.2: Fields in EncounterCreature Struct (Struct ID 0)
Label
Type
Description
Appearance
INT
Appearance of the creature.
Should be identical to the Appearance stored in the
creature blueprint.
CR

### FLOAT

Challenge Rating of the creature.
Should be identical to the CR stored in the creature
blueprint.
ResRef
CResRef
ResRef of the creature blueprint (utc file) to spawn an
instance of.
SingleSpawn

### BYTE

0 if there are no restrictions on how many copies of this
creature can spawn.
1 if only one of this creature can spawn at a time in an
encounter.
The Appearance and CR Fields are stored on the EncounterCreature for performance, so that the game
does not have to access the disk to load the blueprint just to get the CR.

## Page 3

BioWare Corp.
<http://www.bioware.com>
2.2. Encounter Blueprint Fields
The Top-Level Struct in a UTE file contains all the Fields in Table 2.1 above, plus those in Table 2.2
below.
Table 2.2: Fields in Encounter Blueprint Structs
Label
Type
Description
Comment
CExoString
Module designer comment.
PaletteID

### BYTE

ID of the node that the Encounter Blueprint appears
under in the Encounter palette.
TemplateResRef
CResRef
The filename of the UTE file itself. It is an error if this
is different. Certain applications check the value of this
Field instead of the ResRef of the actual file.
If you manually rename a UTE file outside of the
toolset, then you must also update the TemplateResRef
Field inside it.
2.3. Encounter Instance Fields
An Encounter Instance Struct in a GIT file contains all the Fields in Table 2.1.1 and 2.1.2, plus those in
Table 2.3.1 of the Trigger Format document, plus those in Table 2.3.1 below.
Table 2.3.1: Fields in Encounter Instance Structs
Label
Type
Description
Geometry
List
List of Point Structs (StructID 1) defining the vertices
of the Encounter polygon. See Table 2.3.2.
The polygon is drawn by starting at the first Point
element and drawing a line to each subsequent Point,
then connecting the last one back to the first.
See section 4 of the Trigger Format document for
additional rules governing the Geometry of an
Encounter polygon.
SpawnPointList
List
List of EncounterSpawnPoint Structs. Struct ID 0.
See Table 2.3.3.
The SpawnPointList is only saved out if the encounter
has spawnpoints defined for it in the toolset.
Spawn points define a set of locations at which the
game may spawn in creatures belonging to the
Encounter. If an Encounter has no defined
spawnpoints, then the game will try to spawn creatures
out of visible range of the creatures that fired the
Encounter.
TemplateResRef
CResRef
For instances, this is the ResRef of the blueprint that
the instance was created from.
XPosition
YPosition
ZPosition

### FLOAT

(x,y,z) coordinates of the Encounter within the Area
that it is located in.
The Points in the Encounter Geometry have their
coordinates specified relative to the Encounter's own
location.
Table 2.3.2: Fields in Point Struct (Struct ID 1)
Label
Type
Description
X
Y
Z

### FLOAT

(x,y,z) coordinates of the Point, assuming that the
origin is at the owner Encounter's position.

## Page 4

BioWare Corp.
<http://www.bioware.com>
The points in the Encounter's Geometry List use a coordinate system where the origin is the
Encounter's own position. For example, suppose that an Encounter has (XPosition, YPosition,
ZPosition) = (10, 20, 30). If the Geometry contains a Point at (PointX, PointY, PointZ) = (0, 0, 0), then
the actual coordinates of that Point are (10, 20, 30). Similarly, if there is another Point belonging to the
same Encounter has coordinates (PointX, PointY, PointZ) = (1, 2, -10), then the actual coordinates of
that Point are (11, 22, 20).
There is no requirement that any Point in the List be at (0,0,0), nor is there any requirement against it.
Table 2.3.3: Fields in EncounterSpawnPoint Structs (Struct ID 0)
Label
Type
Description
Orientation

### FLOAT

Orientation of the SpawnPoint, expressed as a bearing
in radians measured counterclockwise from north.
X
Y
Z

### FLOAT

(x,y,z) coordinates of the SpawnPoint within the Area
that it is located in.
2.4. Encounter Game Instance Fields
After a GIT file has been saved by the game, the Encounter Instance Struct contains not only the Fields
in Table 2.1 and Table 2.3.1, but also those in Table 2.4.
Table 2.4: Fields in Encounter Instance Structs in SaveGames
Label
Type
Description
ActionList
List
List of Actions stored on this object
StructID 0. See Section 6 of the Common GFF
Structs document.
AreaListMaxSize
INT

AreaPoints

### FLOAT

CurrentSpawns
INT

CustomScriptId
INT

Exhausted

### BYTE

HeartbeatDay

### DWORD

HeartbeatTime

### DWORD

LastEntered

### DWORD

LastLeft

### DWORD

LastSpawnDay

### DWORD

LastSpawnTime

### DWORD

NumberSpawned
INT

ObjectId

### DWORD

Object ID used by game for this object.
SpawnPoolActive

### FLOAT

Started

### BYTE

1 if any creatures currently exist that belong to the
encounter.
0 if there are no creatures currently belonging to the
encounter.
VarTable
List
List of scripting variables stored on this object.
StructID 0. See Section 3 of the Common GFF
Structs document.
3. The 2DA Files Referenced by Encounter Fields
3.1. EncDifficulty
In an Encounter Struct, the DifficultyIndex Field is an index into encdifficulty.2da.

## Page 5

BioWare Corp.
<http://www.bioware.com>
Table 3.3.1: encdifficulty.2da columns
Column
Type
Description

### LABEL

String
Programmer label

### STRREF

Integer
StrRef of text to display for this difficulty level in the
toolset's Encounter Properties dialog.

### VALUE

Integer
Value to add to the game's calculated encounter level.
4. Geometry Rules for the Point List
In an Encounter instance, the Geometry List contains the points that define the outline of the
Encounter.
The toolset must enforce several rules for polygon geometry, as given in Section 4 of the Trigger
Format document.

### See also

- [GFF-UTE](GFF-Spatial-Objects#ute) -- KotOR encounter implementation
- [GFF-File-Format](GFF-File-Format) -- GFF structure
- [2DA-encdifficulty](2DA-File-Format#encdifficulty2da) -- Difficulty table
- [GFF-GIT](GFF-Module-and-Area#git) -- Encounter instances
- [Bioware-Aurora-Trigger](Bioware-Aurora-Spatial-and-Interactive#trigger) -- Geometry rules
- [Container-Formats#key](Container-Formats#key) -- Resource resolution


---
