# BioWare Aurora Engine: Module and Area

*Official Bioware Aurora Documentation — Grouped Reference*

> This page groups related official BioWare Aurora Engine specifications for convenient reference. Each section below was originally a separate BioWare PDF, archived in [xoreos-docs](https://github.com/xoreos/xoreos-docs). The content is mirrored verbatim from the original documentation.

## Contents

- [Area File (ARE)](#areafile)
- [Module Info (IFO)](#ifo)
- [Common GFF Structs](#commongffstructs)
- [Palette / Item Template (ITP)](#paletteitp)

---

<a id="areafile"></a>

# AreaFile

*Official Bioware Aurora Documentation*

> **Note**: This official BioWare documentation was originally written for **Neverwinter Nights**, but the Area (ARE) format is **identical in KotOR**. All structures, fields, and behaviors described here apply to KotOR as well. The examples may reference NWN-specific features, but the core format is the same.

**Source:** This documentation is extracted from the official BioWare Aurora Engine AreaFile Format PDF, archived in [`xoreos-docs/specs/bioware/AreaFile_Format.pdf`](https://github.com/xoreos/xoreos-docs/blob/master/specs/bioware/AreaFile_Format.pdf). The original documentation was published on the now-defunct nwn.bioware.com developer site.

---

## Page 1

BioWare Corp.
<http://www.bioware.com>
BioWare Aurora Engine
Area File (ARE, GIT, GIC) Formats

1. Introduction
In the BioWare Aurora engine, each Area in a module is described by three files. Each file has the same
filename, but a different extension. The following are brief summaries of the area file types.
ARE - static area information: area properties and tile layout.
GIT - dynamic area information - game object instances and sound properties.
GIC - area comments - contains toolset-only comments on game object instances.
The file type are in BioWare's Generic File Format (GFF) and it is assumed that the reader has some
familiarity with GFF.
Conventions
This document describes the GFF structures used by the various area files, as well as any 2DA files that
are referenced by Fields in those GFF files.
For GFF List Fields, the tables indicate the StructID used by the List elements.
Certain numerical GFF Fields have a range of allowable values, and any application that sets these
values should respect the range limitations because there are no guarantees regarding how the game or
toolset treats invalid values.
2. ARE Format
An ARE file contains static information about an Area. The Area properties that are stored in an ARE
file cannot be modified via scripting.
Savegame (.SAV) files are ERFs that contain all the contents of the module, but with modifications and
additions to the some of the original GFF files in the module. The ARE files are not one of the modified
files, though. If the savegame file is for a module having the .nwm extension (from the nwm folder),
then the ARE files are not even included in the savegame. When a nwm-saved game is reloaded, the
game reads the ARE files from the original NWM. For all other saved games, it reads the ARE files
from the SAV file.
2.1. ARE Top Level Struct
In the GFF header of an ARE file, the FileType value is "ARE ".
Table 2.1: Fields in ARE Top Level Struct
Label
Type
Description
ChanceLightning
INT
Percent chance of lightning (0-100)
ChangeRain
INT
Percent chance of rain (0-100)
ChanceSnow
INT
Percent chance of snow (0-100)
Comments
CExoString
Module designer comments
Creator_ID
INT
Deprecated; unused. Always -1.
DayNightCycle

### BYTE

1 if day/night transitions occur, 0 otherwise

## Page 2

BioWare Corp.
<http://www.bioware.com>
Expansion_List
List
Deprecated; unused
Flags

### DWORD

Set of bit flags specifying area terrain type:
0x0001 = interior (exterior if unset)
0x0002 = underground (aboveground if unset)
0x0004 = natural (urban if unset)
These flags affect game behaviour with respect to
ability to hear things behind walls, map exploration
visibility, and whether certain feats are active, though
not necessarily in that order. They do not affect how the
toolset presents the area to the user.
Height
INT
Area size in the y-direction (north-south direction)
measured in number of tiles
ID
INT
Deprecated; unused. Always -1.
IsNight

### BYTE

1 if the area is always night, 0 if area is always day.
Meaningful only if DayNightCycle is 0.
LightingScheme

### BYTE

Index into environment.2da
LoadScreenID

### WORD

Index into loadscreens.2da. Default loading screen to
use when loading this area.
Note that a Door or Trigger that has an area transition
can override the loading screen of the destination area.
ModListenCheck
INT
Modifier to Listen akill checks made in area
ModSpotCheck
INT
Modifier to Spot skill checks made in area
MoonAmbientColor DWORD
Nighttime ambient light color (BGR format)
MoodDiffuseColor DWORD
Nighttime diffuse light color (BGR format)
MoonFogAmount

### BYTE

Nighttime fog amount (0-15)
MoonFogColor

### DWORD

Nighttime fog color (BGR format)
MoonShadows

### BYTE

1 if shadows appear at night, 0 otherwise
Name
CExoLocString
Name of area as seen in game and in left-hand module
contents treeview in toolset. If there is a colon (:) in the
name, then the game does not show any of the text up
to and including the first colon.
NoRest

### BYTE

1 if resting is not allowed, 0 otherwise
OnEnter
CResRef
OnEnter event
OnExit
CResRef
OnExit event
OnHeartbeat
CResRef
OnHeartbeat event
OnUserDefined
CResRef
OnUserDefined event
PlayerVsPlayer

### BYTE

Index into pvpsettings.2da. Note that the settings are
actually hard-coded into the game, and pvpsettings.2da
serves only to provide text descriptions of the settings
(ie., do not edit pvpsettings.2da).
ResRef
CResRef
Should be identical to the filename of the area
SkyBox

### BYTE

Index into skyboxes.2da (0-255). 0 means no skybox.
ShadowOpacity

### BYTE

Opacity of shadows (0-100)
SunAmbientColor

### DWORD

Daytime ambient light color (BGR format)
SunDiffuseColor

### DWORD

Daytime diffuse light color (BGR format)
SunFogAmount

### BYTE

Daytime fog amount (0-15)
SunFogColor

### DWORD

Daytime fog color (BGR format)
SunShadows

### BYTE

1 if shadows appear during the day, 0 otherwise
Tag
CExoString
Tag of the area, used for scripting
Tile_List
List
List of AreaTiles used in the area. StructID 1.
TileSet
CResRef
ResRef of the tileset (.SET) file used by the area
Version

### DWORD

Revision number of the area. Initially 1 when area is
first saved to disk, and increments every time the ARE
file is saved. Equals 2 on second save, and so on.

## Page 3

BioWare Corp.
<http://www.bioware.com>
Width
INT
Area size in the x-direction (west-east direction)
measured in number of tiles
WindPower
INT
Strength of the wind in the area. None, weak, or strong
(0-2).
Some of the color values in the above table are in BGR format. The bytes within a BGR DWORD
value are arranged as 0BGR, where the 0 indicates that the first byte is 0x00. Since GFF integer data is
stored on disk in little-endian/Intel byte ordering, with the least significant byte first, the bytes on disk
will actually appear in the order R G B 0.
2.2. Environment and LightingScheme
The LightingScheme Field is an index into Environment.2da, which contains a list of preset visual area
properties. When a user initially selects one of the lighting schemes in the toolset, it automatically sets
default values for all the area properties that correspond to columns in environment.2da.
The user's choice of environment scheme is stored with the LightingScheme ARE Field, but has no
further effect on any other area property beyond what they were initially set to on first choosing the
lighting scheme. At any time, the user can manually edit the visual area properties and the edited
values will be the ones that are saved.
Table 2.2a: environment.2da columns
Column
Type
Description

### LABEL

String
Programmer label

### STRREF

Integer
StrRef of localized text description to show to user in the
listview on the Visual page of the Area Properties dialog.

### DAYNIGHT

String
"cycle", "light", or "night". Assume night if none of the
above.

### LIGHT_AMB_RED

### LIGHT_AMB_GREEN

### LIGHT_AMB_BLUE

Integer
ambient day color (0-255)

### LIGHT_DIFF_RED

### LIGHT_DIFF_GREEN

### LIGHT_DIFF_BLUE

Integer
diffuse day color (0-255)

### LIGHT_SHADOWS

Integer
flag for shadows on/off during the day (1 or 0)

### DARK_AMB_RED

### DARK_AMB_GREEN

### DARK_AMB_BLUE

Integer
ambient night color (0-255)

### DARK_DIFF_RED

### DARK_DIFF_GREEN

### DARK_DIFF_BLUE

Integer
diffuse night color (0-255)

### DARK_SHADOWS

Integer
setting for shadows on/off during the day (1 or 0)

### LIGHT_FOG_RED

### LIGHT_FOG_GREEN

### LIGHT_FOG_BLUE

Integer
day fog color (0-255)

### DARK_FOG_RED

### DARK_FOG_GREEN

### DARK_FOG_BLUE

Integer
night fog color (0-255)

### LIGHT_FOG

Integer
day fog amount (0-15)

### DARK_FOG

Integer
night fog amount (0-15)
MAIN1_COLOR1 to

### MAIN1_COLOR4

Integer
List of colors to use for MainLight1 property of tiles in the
area (see description of the AreaTile struct). MainLight
colors are chosen randomly when painting a tile or
randomly generating the initial tiles for an area.
Values are indices into lightcolor.2da.

## Page 4

BioWare Corp.
<http://www.bioware.com>
MAIN2_COLOR1 to

### MAIN2_COLOR4

Integer
same as above, but for MainLight2
SECONDARY_COLOR1 to

### SECONDARY_COLOR4

Integer
same as above, but for SourceLight1 and SourceLight2

### WIND

Integer
wind strength (0-2)

### SNOW

Integer
chance of snow (0-100)

### RAIN

Integer
chance of rain (0-100)

### LIGHTNING

Integer
chance of lightning (0-100)

### SHADOW_ALPHA

Integer
shadow opacity (0.0 to 1.0)

### SKYBOX

Integer
Index into skyboxes.2da (0 to 255)

The SkyBox Field is an index into skyboxes.2da, which describes the day/night appearance and
behaviour of each skybox.
Table 2.2b: skyboxes.2da columns
Column
Type
Description

### LABEL

String
Programmer label

### STRING_REF

Integer
StrRef of localized text description to show for the skybox
when selecting it in the toolset's Visual Area Properties
dialog. If the StrRef is ****, then use the LABEL instead.

### CYCLICAL

Integer
1 if the sky changes during transitions from day to night or
vice versa.
0 if the sky never changes. If 0, then the DAWN, DAY,
DUSK, and NIGHT columns should all have the same
value.

### DAWN

DAY

### DUSK

### NIGHT

String
ResRef of the TGA texture to apply to the skybox at the
specified time of day.
Dawn and Dusk each last for one game hour. The duration
of a game hour and the start times for dawn and dusk are
specified in the module properties in module.ifo.
2.3. Loading Screens
The LoadScreenID Field is an index into loadscreens.2da.
The first row in loadscreens.2da is special, and specifies that the loading screen to use is random.
Table 2.3: loadscreens.2da columns
Column
Type
Description
Label
String
Programmer label, also used for display to user if the StrRef is
****
ScriptingName
String
Identifier for the integer constant to use as the first argument to
the NWScript function
void SetAreaTransitionBMP(int nPredefinedAreaTransition,
string sCustomAreaTransitionBMP="").
BMPResRef
String
ResRef of the TGA file to display for this loading screen
TileSet
String
ResRef of tileset that this loading screen represents.
If the loading screen for an area is Random (index 0), then the
game will randomly pick a loading screen whose TileSet Field
matches the ResRef of the area being transitioned to.
If there are no loading screens that match the destination area's
tileset, then the game will pick any loading screen at random.
StrRef
Integer
StrRef of text to display in toolset to describe the loading screen.

## Page 5

BioWare Corp.
<http://www.bioware.com>
2.4. PvP Settings
The PlayerVsPlayer Field is an index into pvpsettings.2da.
Table 2.4: pvpsettings.2da columns
Column
Type
Description
label
String
programmer label
value
Integer
matches up to hardcoded pvp settings in the game
strref
Integer
StrRef of text to display to describe the setting to the user
2.5. Area Tile List
The Tile_List Field is a list of the AreaTiles in the area. An AreaTile describes what tile is located at a
given position in the area, how it is oriented, and what graphical effects exist on it.
To determine the x-y grid coordinates of a tile, use the following formulae:
x = i % w
y = i / w
where:
i = index of the AreaTile Struct in Tile_List
w = the value stored in the area's Width Field
% = modulus operator, ie., the remainder after the left-hand side by the right-hand side
/ = integer division, with result round down to nearest integer
The Fields in an AreaTile are given in the table below:
Table 2.5a: Fields in AreaTile Struct (StructID 1)
Label
Type
Description
Tile_AnimLoop1
Tile_AnimLoop2
Tile_AnimLoop3
INT
Boolean values to indicate if the "AnimLoop01",
"AnimLoop02", or "AnimLoop03" animations on the
tile model should play (1) or not (0).
An AnimLoop can only be set if the correspondingly
named animation actually exists on the tile model.
Otherwise, the Field value is 0.
Tile_Height
INT
Number of height transitions that this tile is located at.
Should never be negative.
Tile_ID
INT
Index into the tileset file's list of tiles, to specify what
tile to use
Tile_MainLight1
Tile_MainLight2

### BYTE

Index into lightcolor.2da to specify mainlight color on
the tile. A tile can have up to 2 mainlights. If a
mainlight does not exist on a tile or is off, the Field
value is 0.
Tile_Orientation INT
Orientation of tile model.
0 = normal orientation
1 = 90 degrees counterclockwise
2 = 180 degrees counterclockwise
3 = 270 degrees counterclockwise
Tile_SrcLight1
Tile_SrcLight2

### BYTE

0 if SourceLight is off or does not exist.
1-15 to specify color and animation of sourcelight.
See "Source Lights" section below for more details.

## Page 6

BioWare Corp.
<http://www.bioware.com>
Some of the Fields in the AreaTile Struct are indices into lightcolor.2da, which is given below.
Table 2.5b: lightcolor.2da columns
Column
Type
Description
RED

### GREEN

### BLUE

Float
RGB colors (0.00 to 2.00).

### LABEL

String
Programmer label

### TOOLSETRED

### TOOLSETBLUE

### TOOLSETGREEN

Float
RGB colors (0.00 to 1.00).
Used by toolset to display a color in the Color Selection dialog
that appears when clicking a color square in the Tile Properties
dialog.
Main Lights
A mainlight is an overall colored lighting effect that can be applied to a tile.
To determine if a tile has a mainlight, the application must inspect its model file. There should be a
light node whose name is the tile model's ResRef in all-caps with "ml1" or "ml2" appended to the end.
For example, if the tile model is tts_a01_01.mdl, then mainlight 1 on that tile would be a light
node called "TTZ_A01_01ml1".
If a light node does not exist, then the toolset does disables the controls to set the light's value.
Source Lights
A sourcelight is a point on a tile where the graphics engine can attach the model of a flaming light
source.
Not all tiles have sourcelights. To determine if a sourcelight is present, the application must inspect the
tile's model file. There should be a dummy node whose name is the tile model's ResRef in all-caps with
"sl1" or "sl2" appended to the end.
To create a sourcelight in the graphics engine, spawn "fx_flame01.mdl" at the position of the tile's
"sl1" or "sl2" dummy node and play the animation whose name matches the value of the appropriate
Tile_SrcLight Field.
Example: if the tile model as specified by the TileSet and Tile_ID is ttz_a01_01.mdl, and
Tile_SrcLight2 is 14, then spawn fx_flame01.mdl at the "TTZ_A01_01sl2" dummy node
in the tile and set it to play the animation named "14".
To get a rough visual representation of the source light color associated with a given number, take the
Tile_SrcLight value, multiply it by 2, and use it as an index into lightcolor.2da, which contains the
RGB values. Note however, that editing lightcolor.2da will have no effect on the colors shown in the
graphics engine; the colors are entirely determined by the animations embedded in fx_flame01.mdl. In
other words, lightcolor.2da should match up with the model, not the other way around.
3. GIT Format
A GIT file contains dynamic information about an area. The main purpose of a GIT is to store lists of
all the object instances in the area, but it is also used to store a few area properties that can be changed
via scripting. When a game is saved, the game includes an updated version of the GIT file for each area
in the .SAV file.
In the GFF header of a GIT file, the FileType value is "GIT ".

## Page 7

BioWare Corp.
<http://www.bioware.com>
Table 3.1: Fields in GIT Top Level Struct
Label
Type
Description
AreaProperties
Struct
StructID 100. See table below.
Creature List
List
List of Creature instances. StructID 4
Door List
List
List of Door instances. StructID 8
Encounter List
List
List of Encounter instances. StructID 7
List
List
List of Item instances. StructID 0
Placeable List
List
List of Placeable instances. StructID 9
SoundList
List
List of Sound instances. StructID 6
StoreList
List
List of Store instances. StructID 11
TriggerList
List
List of Trigger instances. StructID 1
WaypointList
List
List of Waypoint instances. StructID 5
The Lists in a GIT are lists of all the game object instances in the area. The actual format of each of
those Structs is specified in the respective file format documents for each game object type.
The AreaProperties Field is a Struct containing dynamic area properties, and contains the Fields given
in the table below.
Table 3.2: Fields in GIT AreaProperties Struct (StructID 100)
Label
Type
Description
AmbientSndDay
INT
Ambient sound to play during daytime. Index into
ambientsound.2da.
AmbientSndDayVol INT
Volumne of ambient sound during the day (0-127)
AmbientSndNight
INT
Ambient sound to play at night. Index into
ambientsound.2da.
AmbientSndNitVol INT
Volume of ambient sound at night (0-127)
EnvAudio
INT
Environmental audio effects to use for positional
sounds instances in the area. Index into soundeax.2da.
MusicBattle
INT
Index into ambientmusic.2da. Should only point to
indices where the "Resource" 2da value starts with
"mus_bat_"
MusicDay
INT
Index into ambientmusic.2da.
MusicDelay
INT
Index into ambientmusic.2da.
MusicNight
INT
Index into ambientmusic.2da.
The 2da files referenced by the the Fields in the AreaProperties Struct are described below:
Table 3.3: ambientsound.2da columns
Column
Type
Description
Description
Integer
StrRef of localized text description to show to user
Resource
String
Looping sound to play. ResRef of wav file in ambient folder.
PresetInstance0 to
PresetInstance7
String
ResRef of sound blueprints (UTS file) to automatically spawn
into area when this 2da row is selected as the ambient sound for
the area.
DisplayName
String
Alternative to Description, if Description is ****.
Table 3.4: ambientmusic.2da columns
Column
Type
Description
Description
Integer
StrRef of localized text description
Resource
String
Music to play. ResRef of bmu file in music folder.
Stinger1
Stinger2
Stinger3
String
Music to play when combat ends, if this entry is being played as
combat music. Can have up to 3 different stinger variants that
the game chooses randomly.
DisplayName
String
Alternative to Description, if Description is ****.

## Page 8

BioWare Corp.
<http://www.bioware.com>
Table 3.5: soundeax.2da columns
Column
Type
Description
Label
String
Programmer label. Displayed to user if Description is ****.
Description
Integer
StrRef of string to display to user.
SaveGame GIT properties
When a game is saved, a GIT file for every area in the module is saved into the .SAV file. The
savegame GIT serves the same purpose as the GIT created by the toolset, although of course, the
contents of its object lists may differ significantly, and the AreaProperties Struct may have different
Field values.
The game also saves some additional fields to the Toplevel GIT Struct, as given below:
Table 3.6: Fields in GIT Top Level Struct, added by SaveGame
Label
Type
Description
AreaEffectList
List
List of AreaEffects.
StructID 13.
CurrentWeather

### BYTE

Weather conditions currently in area.
0 = Clear
1 = Rain
2 = Snow
VarTable
List
List of variables stored on area.
StructID 0. See Section 3 of the Common GFF
Structs document.
WeatherStarted

### BYTE

1 if weather specified by CurrentWeather is starting, 0
otherwise.
4. GIC Format
The GIC file is used purely to store the Comment properties of all the object instances in the area.
The game does not read or use the toolset-saved Comments in any fashion, so including them in the
GIT file with the rest of the object instance information would unnecessarily increase the size of
SaveGame files (recall that SaveGame ERFs contain GIT files for each area).
There is a one-to-one correspondence between list elements in the GIC file and those in the GIT file for
the same area. Note that Table 4.1 below and Table 3.1 above contain identically named lists.
In the GFF header of a GIC file, the FileType value is "GIC ".
Table 4.1: Fields in GIC Top Level Struct
Label
Type
Description
Creature List
List
List of Creature instances. StructID 4
Door List
List
List of Door instances. StructID 8
Encounter List
List
List of Encounter instances. StructID 7
List
List
List of Item instances. StructID 0
Placeable List
List
List of Placeable instances. StructID 9
SoundList
List
List of Sound instances. StructID 6
StoreList
List
List of Store instances. StructID 11
TriggerList
List
List of Trigger instances. StructID 1
WaypointList
List
List of Waypoint instances. StructID 5
The GIC Lists all contain the same type of Struct. The format of that Struct is given in the table below.

## Page 9

BioWare Corp.
<http://www.bioware.com>
Table 4.2: Fields in Comment Struct
Label
Type
Description
Comment
CExoString
Module designer's comment

### See also

- [GFF-ARE](GFF-Module-and-Area#are) -- KotOR area implementation
- [GFF-GIT](GFF-Module-and-Area#git) -- Instance data
- [GFF-File-Format](GFF-File-Format) -- GFF structure
- [Bioware-Aurora-GFF](Bioware-Aurora-Core-Formats#gff) -- Aurora GFF spec
- [Container-Formats#key](Container-Formats#key) -- Resource resolution


---

<a id="ifo"></a>

# IFO

*Official Bioware Aurora Documentation*

> **Note**: This official BioWare documentation was originally written for **Neverwinter Nights**, but the IFO format is **identical in KotOR**. All structures, fields, and behaviors described here apply to KotOR as well. The examples may reference NWN-specific features, but the core format is the same.

**Source:** This documentation is extracted from the official BioWare Aurora Engine IFO Format PDF, archived in [`xoreos-docs/specs/bioware/IFO_Format.pdf`](https://github.com/xoreos/xoreos-docs/blob/master/specs/bioware/IFO_Format.pdf). The original documentation was published on the now-defunct nwn.bioware.com developer site.

---

## Page 1

BioWare Corp.
<http://www.bioware.com>
BioWare Aurora Engine
IFO File Format

1. Introduction
An IFO file is a module InFOrmation file. Every NWN module (.MOD or .NWM) or savegame (.SAV)
is an Encapsulated Resource File (ERF) that contains an IFO file called "module.ifo".
The IFO file type is in BioWare's Generic File Format (GFF) and it is assumed that the reader has some
familiarity with GFF. Many of the GFF Fields in an IFO file make references to 2-Dimensional Array
(2DA) files, so it is also assumed that the reader is familiar with the 2DA format.
In the GFF header of an IFO file, the FileType value is "IFO ".
2. Top-Level Struct
2.1 Fields created by Toolset
When a module is saved by the toolset, the Top-Level GFF Struct of the module.ifo file has the Fields
given in the table below.
For List Fields, the table indicates the StructID used by the List elements.
Certain numerical Fields have a range of allowable values, and any application that sets these values
should respect the range limitations because there are no guarantees regarding how the game or toolset
treats invalid values.
Table 2.1: Basic Fields in IFO Top Level Struct
Label
Type
Description
Expansion_Pack

### WORD

Bit flags specifying what expansion packs are required
to run this module. Once a bit is set, it is never unset.
Bit 0 = Expansion 1, Bit 1 = Expansion 2, etc.
Mod_Area_List
List
List of Areas in the module.
StructID 6.
Mod_CacheNSSList List
List of scripts that the game should cache.
StructID 9
Mod_Creator_ID
INT
Deprecated; unused. Is always set to 2.
Mod_CustomTlk
CExoString
Name of a custom TLK file to use with this module.
This name does not include the ".tlk" file extension.

Custom tlk files should be located in the "tlk" folder in
the main game installation directory.

For non-English languages that use dialogF.tlk in
addition to dialog.tlk, the custom tlk file must also have
a "F.tlk" counterpart in the tlk folder.

To refer to a string from the module's custom TLK file,
the StrRef's 0x01000000 bit should be set to 1. The
application will then mask that bit off to 0 and use the
resulting value as the StrRef index into the custom
TLK file instead of the usual dialog.tlk. If the custom

## Page 2

BioWare Corp.
<http://www.bioware.com>
string cannot be found, it will attempt to retrieve the
normal dialog.tlk StrRef.
Mod_CutsceneList List
Deprecated; unused.
Mod_DawnHour

### BYTE

Game hour at which dawn begins (0-23). Area lighting
will begin transitioning from Night to Day colors over
the course of 1 game hour.
Mod_Description
CExoLocString
Description of module
Mod_DuskHour

### BYTE

Game hour at which dusk begins (0-23). Area lighting
will begin transitioning from Day to Night colors over
the course of 1 game hour.
Mod_Entry_Area
CResRef
Module's Starting Area
Mod_Entry_Dir_X
Mod_Entry_Dir_Y

### FLOAT

x and y components of Start Location's direction
vector. This is a unit vector.
Or in other words, the cosine and sine, respectively, of
the waypoint's bearing in the xy plane, measured as an
angle counterclockwise from the positive x-axis.
Mod_Entry_X
Mod_Entry_Y
Mod_Entry_Z

### FLOAT

(x,y,z) coordinates of Module Start Location within the
starting area.
The toolset will refuse to save a module or area until
the start location is located on a walkable portion of a
tileIf the start location ends up on an unwalkable spot
anyway (this may be caused if the tileset tiles or
walkmeshes are in a state of flux) then the game will
spawn players in at the closest walkable point.
Mod_Expan_List
List
Deprecated; unused
Mod_GVar_List
List
Deprecated; unused
Mod_Hak
CExoString
(Obsolete) Hak File used by module, without the ".hak"
extension in its filename. If Mod_HakList exists, this
value is used as the module's Hak Pak. Otherwise, it is
ignored.
Mod_HakList
List
List of Hak Files used by module. Resources from the
first Hak Paks in the list have the highest priority and
override resources in later Hak Paks.
StructID 8.
Mod_ID
Binary
Arbitrarily generated 16-byte number sequence
assigned when toolset creates a new module. It is never
modified afterward by toolset. The game saves out 32
bytes instead of 16. Applications other than the toolset
can set this to all null bytes when creating a new IFO
file.
Mod_IsSaveGame

### BYTE

Boolean indicating if the module is a same game.
0 for modules saved by toolset.
1 for saved games.
Mod_MinGameVer
CExoString
Minimum version of the game and associated game
resources required to run the module. Should be in n.nn
format (eg., "1.26", "1.30"). The game and toolset will
refuse to open a module if the module's minimum
version is greater than the user's current version of the
game. The value of this Field can only increase or stay
the same. If this Field does not exist in the IFO, the
default value is "1.22".
Mod_MinPerHour

### BYTE

Number of real-time minutes per game hour. (1-255)
Mod_Name
CExoLocString
Name of module
Mod_OnAcquirItem CResRef
OnAcquireItem event
Mod_OnActvtItem
CResRef
OnActivateItem event

## Page 3

BioWare Corp.
<http://www.bioware.com>
Mod_OnClientEntr CResRef
OnClientEnter event
Mod_OnClientLeav CResRef
OnClientLeave event
Mod_OnCutsnAbort CResRef
OnCutsceneAbort event
Mod_OnHeartbeat
CResRef
OnHeartbeat event
Mod_OnModLoad
CResRef
OnModuleLoad event
Mod_OnModStart
CResRef
OnModuleStart event; deprecated
Mod_OnPlrDeath
CResRef
OnPlayerDeath event
Mod_OnPlrDying
CResRef
OnPlayerDying event
Mod_OnPlrEqItm
CResRef
OnPlayerEquipItem event
Mod_OnPlrLvlUp
CResRef
OnPlayerLevelUp event
Mod_OnPlrRest
CResRef
OnPlayerRest event
Mod_OnPlrUnEqItm CResRef
OnPlayerUnEquipItem event
Mod_OnSpawnBtnDn CResRef
OnPlayerRespawn event
Mod_OnUnAcreItem CResRef
OnUnAcquireItem event
Mod_OnUsrDefined CResRef
OnUserDefined event
Mod_StartDay

### BYTE

Starting day (1-31)
Mod_StartHour

### BYTE

Starting hour (0-23)
Mod_StartMonth

### BYTE

Starting month (1-24)
Mod_StartMovie
CResRef
ResRef of movie in 'movies' folder to play when
starting module
Mod_StartYear

### DWORD

Starting year
Mod_Tag
CExoString
Module's Tag
Mod_Version

### DWORD

Module version. Is always set to 3.
Mod_XPScale

### BYTE

Percentage by which to multiply all XP gained through
killing creatures.
2.2. Fields created by Game
When a module is saved, the game adds additional fields to the module.ifo file, as listed in the table
below.
Table 2.2: Save-Game Fields in IFO Top Level Struct
Label
Type
Description
Creature List
List
Deprecated; unused
EventQueue
List
Game events that were queued up at the time the
module was saved.
StructID 43981
Mod_Effect_NxtId DWORD64
ID to use for the next Effect
Mod_IsNWMFile

### BYTE

Boolean to indicate if the game was saved from a
NWM file (1) or MOD file (0).
Mod_NextCharId0

### DWORD

Keeps track of which id to give the next character
created
Mod_NextCharId1

### DWORD

-

Mod_NextObjId0

### DWORD

Keeps track of which id to give the next object created
Mod_NextObjId1

### DWORD

-

Mod_NWMResName
CExoString
If this game was saved from a nwm module, then this is
the filename of the nwm.
Mod_PlayerList
List
List of Players in the module.
StructID 48813
Mod_Tokens
List
List of Custom Tokens in the module.
StructID 7
Mod_TURDList
List
List of Temporary User Resource Data objects in the
module.
StructID 13634816

## Page 4

BioWare Corp.
<http://www.bioware.com>
Mod_VarTable
List
List of Variables in the module and their values.
StructID 0
3. Common Lists and Structs
Below are descriptions of each of the Lists present in an IFO file. Each section is titled by the Field's
Label and contains the StructID of the Structs contained in the List
3.1 Mod_Area_List
Module Area List
A list of all the areas present in the module.
Table 3.1: Fields in Area List Struct (StructID 6)
Label
Type
Description
AreaName
CResRef
ResRef of area in module. There must be three files in
the module that have this ResRef, with filetypes ARE,
GIT, and GIC.
ObjectId

### DWORD

ObjectID of the area.
(Savegame only; not saved out by toolset)
3.2 Mod_CacheNSSList
Cached Script List
A list of scripts that should be cached by the NWN server while running the module. Typically, these
are scripts that will be executed very often.
Table 3.2: Fields in Cached Script List Struct (StructID 9)
Label
Type
Description
ResRef
CResRef
ResRef of a script. Each script has an NSS source file
and a corresponding NCS compiled script.
3.3 Mod_HakList
Hak Pak List
List of Hak Paks used by the module. The Hak Paks are listed in descending order of priority. The
contents of the earlier Hak Paks in the list will override the contents of later Hak Paks.
Table 3.3: Fields in Hak Pak List Struct (StructID 8)
Label
Type
Description
Mod_Hak
CExoString
Filename of a Hak Pak used by this module, minus the
.hak extension.
4. Save-Game Lists and Structs
Below are descriptions of each of the Lists present in an IFO file after the module has been saved by the
game. Each section is titled by the Label of the List.
Most things ingame have an ObjectID by which the game references them, so ObjectIDs appear in
many of the Structs in the savegame Lists.

## Page 5

BioWare Corp.
<http://www.bioware.com>
4.1 EventQueue
Event Queue
List of Events in the module. See Section 5 of the Common GFF Structs document.
4.2 Mod_PlayerList
Player List
List of Players in the module. Each Player Struct in the list has a StructID of 48813. The Player Struct
itself is too large and complicated to discuss in this document, and merits an entire format-specification
document of its own.
4.3 Mod_Tokens
Module Custom Tokens
List of custom tokens defined in the module via the NWScript function.
void SetCustomToken(int nCustomTokenNumber, string sTokenValue)
Table 4.3: Fields in a Token Struct (StructID 7)
Label
Type
Description
Mod_TokensNumber

### DWORD

Custom Token number.
nCustomTokenNumber argument from
the SetCustomToken() function.
Mod_TokensValue
CExoString
Custom Token value.
sTokenValue argument from the
SetCustomToken() function.
4.4 Mod_TURDList
Temporary User Resource Data
List of player Temporary User Resource Data objects.
These objects are used to store player information for users who joined the game and then logged out.
When a user joins a game, the user's login name and player character's name are checked against those
in the current TURD List to determine if the user is a new player, or one who is returning to the game.
Returning players have their gamestate information restored according to the information in the

### TURD

Table 4.4a: Fields in a TURD Struct (StructID 13634816)
Label
Type
Description
EffectList
List
List of Effects. StructID 2. See See Section
4 of the Common GFF Structs document.
Mod_MapAreasData
Binary
-

Mod_MapDataList
List
List of MapData. StructID 0, contains the
indented Fields immediately below:
Mod_MapData
Binary
-

ModMapNumAreas
INT
-

TURD_AreaId

### DWORD

ObjectID of area in which player logged
out.
TURD_CalendarDay

### DWORD

Day the TURD was generated
TURD_CommntyName
CExoString
Player Name with which the player logged

## Page 6

BioWare Corp.
<http://www.bioware.com>
into Multiplayer.
TURD_FirstName
CExoLocString
First name of the player character
TURD_LastName
CExoLocString
Last name of the player character
TURD_OrientatX
TURD_OrientatY
TURD_OrientatZ

### FLOAT

Orientation of the player at logout
TURD_PersonalRep
List
List of Personal Reputations that other
creatures hold toward the player.
StructID 47787. See Table 4.4b below.
TURD_PlayerID

### DWORD

ObjectID of the player
TURD_PositionX
TURD_PositionY
TURD_PositionZ

### FLOAT

Position of the player at logout
TURD_RepList
List
List of reputations with each Faction in the
module.
StructID 43962, contains the indented Fields
immediately below:
TURD_RepAmount
INT
Reputation with faction X, where X is the
same as the index of the List element
(allowed values are 0-100)
TURD_TimeOfDay

### DWORD

Time the TURD was generated
VarTable
List
List of Variables stored on the character.
StructID 0. See section 4.5.
Table 4.4b: Fields in a Personal Reputation Struct (StructID 47787)
Label
Type
Description
TURD_PR_Amount
INT
Reputation with the faction
TURD_PR_Day

### DWORD

-

TURD_PR_Decays

### BYTE

boolean
TURD_PR_Duration
INT
Measured in seconds
TURD_PR_ObjId

### DWORD

ObjectID of creature that is considering the
owner of this Personal Reputation element
TURD_PR_Time

### DWORD

-

4.5 VarTable
Variable Table
List of scripting variables and their values. See Section 3 of the Common GFF Structs document.

### See also

- [GFF-IFO](GFF-Module-and-Area#ifo) -- KotOR module info implementation
- [Container-Formats#erf](Container-Formats#erf) -- MOD/SAV containers
- [GFF-File-Format](GFF-File-Format) -- GFF structure
- [Container-Formats#key](Container-Formats#key) -- Resource resolution


---

<a id="commongffstructs"></a>

# CommonGFFStructs

*Official Bioware Aurora Documentation*

> **Note**: This official BioWare documentation was originally written for **Neverwinter Nights**, but the common GFF structures are **identical in KotOR**. All structures, fields, and behaviors described here apply to KotOR as well. The examples may reference NWN-specific features, but the core format is the same.

**Source:** Extracted from the official BioWare Aurora Engine CommonGFFStructs PDF, archived in [xoreos-docs](https://github.com/xoreos/xoreos-docs) [`specs/bioware/CommonGFFStructs.pdf`](https://github.com/xoreos/xoreos-docs/blob/master/specs/bioware/CommonGFFStructs.pdf). Original from the defunct *nwn.bioware.com* developer site.

---

## Page 1

BioWare Corp.
<http://www.bioware.com>
BioWare Aurora Engine
Common Game GFF Structures

1. Introduction
This document describes Structs and Lists that are frequently seen in files saved in the BioWare
Generic File Format. This document assumes that the reader is already familiar with the Generic File
Format document.
When describing a Struct in this document, the StructID is provided for completeness, although in some
cases, the StructID may vary depending on the List or Struct that contains the Struct being described.
Also, in most cases, the game and toolset do not actually check the StructID.
This document is intended to supplement the documentation for various GFF files (eg., IFO, ARE, etc.).
Consequently, it may not fully disclose the details of any given Struct. In those instances where a Struct
is not completely described, it is strongly recommended that an application should write it out to disk
exactly as it was read in originally, with no modifications. Modifying a Struct without a good
understanding of it can lead to corrupted modules and corrupted saved games.
2. Location Struct
A Location is a Struct that describes a location in a module.
Table 2: Fields in a Location Struct (StructID 1)
Label
Type
Description
Area

### DWORD

ObjectId of the area containing the location
OrientationX
OrientationY
OrientationZ

### FLOAT

(x,y,z) components of the direction vector in
which the location faces
PositionX
PositionY
PositionZ

### FLOAT

(x,y,z) coordinates of the location
3. VarTable List, Variable Struct
A VarTable is a GFF List containing Variable GFF Structs. It is a list of scripting variables and their
values.
Table 3.1: Fields in a Variable Struct (StructID 0)
Label
Type
Description
Name
CExoString
The name of the variable as set by the
SetGlobalInt(), SetGlobalString(), etc.
scripting functions, and retrieved by the
corresponding GetGlobal*() functions.
Type

### DWORD

Variable's data type
Value
Depends on Type
The value of the Variable
The actual data type of a Variable's 'Value' Field depends on the value of it's 'Type' Field. The table
below lists the type IDs and their associated data types.

## Page 2

BioWare Corp.
<http://www.bioware.com>
Table 3.2: Variable Types
TypeID
GFF Type
NWScript Type
1
INT
int
2

### FLOAT

float
3
CExoString
string
4

### DWORD

object
5
Location Struct. See Section 2.
location
4. EffectsList List, Effect Struct
An EffectsList is a GFF List containing Effect GFF Structs. It is a list of effects on an object.
Table 4: Fields in an Effect Struct (variable StructID)
Label
Type
Description
CreatorId

### DWORD

ObjectID of effect's creator
Duration

### FLOAT

Duration of the effect
ExpireDay

### DWORD

Day the effect expires
ExpireTime

### DWORD

Time the effect expires
FloatList
List
StructID 4. Struct given on next line:
Value

### FLOAT

List of float parameters for the effect
IntList
List
StructID 3. Struct given on next line:
Value
INT
List of int parameters for the effect
IsExposed
INT
Bool – is the effect exposed to scripting?
IsIconShown
INT
Bool – does it show the icon?
NumIntegers
INT
-

ObjectList
List
StructID 6. Struct given on next line:
Value

### DWORD

List of ObjectID parameters for the effect
SkipOnLoad

### BYTE

Bool – should this effect be added on load?
Or skipped?
SpellId

### DWORD

-

StringList
List
StructID 5. Struct given on next line:
Value
CExoString
String parameters for the effect
SubType

### WORD

The effect sub-type
Type

### WORD

The type of the effect.
5. EventQueue List, Event Struct
An EventQueue is a GFF List containing Event GFF Structs. The Fields in an Event are given in the
table below:
Table 5.1: Fields in an Event Struct (StructID 0xABCD)
Label
Type
Description
CallerId

### DWORD

Object Id of the actor object
Day

### DWORD

Game day the event should fire
EventData
Depends on EventId
Struct that depends on the EventId
EventId

### DWORD

ID of the Event type
ObjectId

### DWORD

Object ID the event is acting on
Time

### DWORD

Game time the event should fire
The EventData Field is a GFF Struct that depends on the value of the EventId Field. The table below
lists some EventId values and what Structs are associated with them. These Structs are saved using the
StructID specified in the table, rather than whatever StructIDs they may normally use. Some EventIds
do not save an EventData Struct at all.

## Page 3

BioWare Corp.
<http://www.bioware.com>
Table 5.2: EventId values
EventId
EventData
StructID
Event Description
Struct
1
0x7777

### TIMED_EVENT

ScriptSituation. See Section 7.
2
-

### ENTERED_TRIGGER

none
3
-

### LEFT_TRIGGER

none
4
0x9999

### REMOVE_FROM_AREA

Struct consists of a single
BYTE Field of Label "Value"
5
0x1111

### APPLY_EFFECT

Effect Struct. See Section 4.
6
-

### CLOSE_OBJECT

none
7
-

### OPEN_OBJECT

none
8
0x6666

### SPELL_IMPACT

SpellScriptData Struct
9
0x3333

### PLAY_ANIMATION

Struct consists of a single INT
Field of Label "Value"
10
0x4444

### SIGNAL_EVENT

ScriptEvent. See Section 7.
11
-

### DESTROY_OBJECT

none
12
-

### UNLOCK_OBJECT

none
13
-

### LOCK_OBJECT

none
14
0x1111

### REMOVE_EFFECT

Effect Struct. See Section 4.
15
0x2222

### ON_MELEE_ATTACKED

CombatAttackData Struct.
16
-

### DECREMENT_STACKSIZE

none
17
0x5555

### SPAWN_BODY_BAG

BodyBagInfo Struct
18
0x8888

### FORCED_ACTION

ForcedAction Struct
19
0x6666

### ITEM_ON_HIT_SPELL_IMPACT

SpellScriptData Struct
20
0xAAAA

### BROADCAST_AOO

Struct consists of a single
DWORD Field of Label
"Value"
21
0x2222

### BROADCAST_SAFE_PROJECTILE

CombatAttackData Struct.
22
0xCCCC

### FEEDBACK_MESSAGE

ClientMessageData Struct
23
-

### ABILITY_EFFECT_APPLIED

none
24
0xDDDD

### SUMMON_CREATURE

ScriptEvent. See Section 7.
25
-

### ACQUIRE_ITEM

none
6. ActionList List, Action Struct
Game object instances may have actions queued up at the time that the game is saved. Any such
instances will contain a number of Action objects in their ActionList Field. The table below describes
an Action Struct.
Table 6.1: Fields in an Action Struct (StructID 0)
Label
Type
Description
ActionId

### DWORD

-

GroupActionId

### WORD

-

NumParams

### WORD

Number of elements in the Parameter List
Paramaters
List
List of Parameter Structs (StructID 1). See Table 6.2
This List is not present if NumParams == 0.
Note that the spelling of the "Paramaters" Field is not a typographical error. It really is spelled that
way. By the time someone noticed that the spelling of "parameters" was incorrect, there was too much
existing data to justify fixing the spelling.
The table below describes a Struct in the Parameter List.

## Page 4

BioWare Corp.
<http://www.bioware.com>
Table 6.2: Fields in a Parameter Struct (StructID 1)
Label
Type
Description
Type

### DWORD

The Parameter Value's data type
Value
Depends on Type
The value of the Parameter
In a Parameter Struct, the actual datatype of the Value Field varies depending on the value of the Type
Field. The table below specifies the Value datatypes associated with each Parameter Type.
Table 6.3: Parameter Types
Parameter Type
GFF Type of the Value Field
Description
1
INT
Integer
2

### FLOAT

Floating point value
3

### DWORD

Object ID
4
CExoString
String
5
Struct
Script Situation. StructID 2.
Corresponds to a ScriptSituation in the
virtual machine. See Section 7.
7. Script Situation Struct and Substructs
A Script Situation is a very complicated structure that is used by the scripting virtual machine. Details
of this structure are provided in here, but it is highly recommended that if an application reads this
structure, then it should write it back out exactly as it was read in originally.
Table 7.1: Fields in a Script Situation Struct (variable StructID)
Label
Type
Description
CodeSize
INT

Code

### VOID

InstructionPtr
INT

SecondaryPtr
INT

Name
String

StackSize
INT

Stack
Struct
Stack Structure. StructID 0. See Table 7.2.
Table 7.2: Fields in a Stack Struct (StructID 0)
Label
Type
Description
BasePointer
INT

StackPointer
INT

TotalSize
INT

Stack
List
Has a number of elements equal to the value of the
StackPointer Field.
StructID of each list element is equal to the index of the
Struct in the List.
See Table 7.3a.
Table 7.3a: Fields in each Struct in the Stack List (variable StructID)
Label
Type
Description
Type

### CHAR

Specifies the Field Type of the Value Field. See Table
7.3b.
Value
Variable
Depends on Type Field. See Table 7.3b.
Table 7.3b: Stack Element Value Types
Stack Element Type
GFF Type of the Value Field
Description
3
INT
Integer

## Page 5

BioWare Corp.
<http://www.bioware.com>
4

### FLOAT

Floating point value
5
CExoString
String
6

### DWORD

Object ID
10 to 19
Struct
Game engine structure. Subtract 10
from the Type to get the StructID and
look up the structure type in Table
7.3c.
Table 7.3c: Game Engine Structure IDs
Struct ID/Stack Element Type
Description
0
Effect. See Section 4.
1
ScriptEvent. See Table 7.3
2
ScriptLocation. See Table 7.5
3
ScriptTalent. See Table 7.6
4
ItemProperty. Same save function as effects. See Section 4.
5 to 8
Unused; Reserved
Table 7.4: ScriptEvent Fields (StructID 1)
Label
Type
Description
EventType

### WORD

IntList
List
List of Structs having StructID 105.
Each Struct contains a single Field having the Label
"Parameter" and the Field is an INT
FloatList
List
List of Structs having StructID 105.
Each Struct contains a single Field having the Label
"Parameter" and the Field is a FLOAT
StringList
List
List of Structs having StructID 105.
Each Struct contains a single Field having the Label
"Parameter" and the Field is a CExoString
ObjectList
List
List of Structs having StructID 105.
Each Struct contains a single Field having the Label
"Parameter" and the Field is a DWORD.
Table 7.5: ScriptLocation Fields (StructID 2)
Label
Type
Description
Area

### DWORD

ObjectID of area
OrientationX,
OrientationY,
OrientationZ

### FLOAT

orientation vector
PositionX,
PositionY,
PositionZ

### FLOAT

position vector
Table 7.6: ScriptTalent Fields (StructID 3)
Label
Type
Description
ID
INT

Type
INT

MultiClass

### BYTE

Item

### DWORD

Object ID
ItemPropertyIndex
INT

CasterLevel

### BYTE

MetaType

### BYTE

### See also

- [Bioware-Aurora-GFF](Bioware-Aurora-Core-Formats#gff) -- Aurora GFF spec
- [GFF-File-Format](GFF-File-Format) -- KotOR GFF implementation
- [GFF-IFO](GFF-Module-and-Area#ifo)
- [GFF-ARE](GFF-Module-and-Area#are)
- [GFF-UTC](GFF-Creature-and-Dialogue#utc) -- GFF files referencing common structs
- [Container-Formats#key](Container-Formats#key) -- Resource resolution


---

<a id="paletteitp"></a>

# PaletteITP

*Official Bioware Aurora Documentation*

> **Note**: This official BioWare documentation was originally written for **Neverwinter Nights**, but the Palette/ITP (GFF) format is **identical in KotOR**. All structures, fields, and behaviors described here apply to KotOR as well. The examples may reference NWN-specific features, but the core format is the same.

**Source:** This documentation is extracted from the official BioWare Aurora Engine PaletteITP Format PDF, archived in **[xoreos-docs](https://github.com/xoreos/xoreos-docs)**: [`specs/bioware/PaletteITP_Format.pdf`](https://github.com/xoreos/xoreos-docs/blob/master/specs/bioware/PaletteITP_Format.pdf). The original documentation was published on the now-defunct nwn.bioware.com developer site.

---

## Page 1

BioWare Corp.
<http://www.bioware.com>
BioWare Aurora Engine
ITP (Palette) File Format

1. Introduction
An ITP file defines a palette used by the toolset or DM Client. A palette describes a tree structure of
tiles or object blueprints that can be painted in the toolset, or object blueprints that can be spawned in
the DM Client.
Palettes are stored in the game and toolset using BioWare's Generic File Format (GFF), and it is
assumed that the reader of this document is familiar with the Generic File Format document.
In the GFF header of an ITP file, the FileType value is "ITP ".
2. Blueprint Palettes
2.1. Overview
Blueprint palettes appear in the many treeviews in the toolset that contain paintable object blueprints.
They also appear in treeviews where the user can pick a palette category for an object, such as in the
"Assign Palette Category" step of the various New Blueprint wizards or in the Select Category dialog.
These palette treeviews contain 3 node types:
Blueprint Nodes:
A Blueprint Node is a node that is directly associated with an object blueprint.
Clicking on a blueprint node in the toolset allows the user to paint instances of the associated
Blueprint. Clicking on a Blueprint node in the DM client allows the user to spawn in instances of the
blueprint.
In the toolset, the user can right-click a Blueprint node to perform various maintenance tasks such as
editing it.
A palette can have zero or more Blueprint nodes. The Standard blueprint palettes generally contain
many Blueprint nodes. The Custom blueprint palettes in a new module contain zero blueprint nodes.
Blueprint nodes never have child nodes.
Non-Blueprint Nodes:
Non-blueprint nodes can have child nodes that may be blueprint nodes, or they may be other non-
blueprint nodes. They are not editable in the toolset and they define the overall structure of a palette.
Category Nodes:
A Category Node serves as a parent node for blueprint nodes and can only have blueprint nodes
as children.

## Page 2

BioWare Corp.
<http://www.bioware.com>
When assigning a palette category to a blueprint in the toolset's Select Category dialog, the user
can only select Category nodes.
Branch Nodes:
A Branch Node serves as a parent node for Category nodes or other Branch nodes, but never
Blueprint nodes.
2.2. Skeleton Blueprint Palettes
A skeleton blueprint palette is a blueprint palette that contains no blueprint nodes, but merely defines
the categories and tree structure of a palette. There is one skeleton palette for each blueprint resource
type. The toolset recognizes the following skeleton blueprint palettes:
creaturepal.itp
doorpal.itp
encounterpal.itp
itempal.itp
placeablepal.itp
soundpal.itp
storepal.itp
triggerpal.itp
waypointpal.itp
The toolset uses skeleton blueprint palettes in the "Assign Palette Category" step of the various New
Blueprint wizards and in the Select Category dialog when choosing the palette category while editing
an object blueprint.
Figure 2.2 shows an example skeleton blueprint palette.
Figure 2.2: Example Skeleton Blueprint Palette

### MAIN

Armor (Branch)
Weapons (Branch)
Bladed (Branch)
Daggers (Category)
Heavy (Category)
Helmets (Category)
Swords (Category)
Miscellaneous (Category)
Bows (Category)

## Page 3

BioWare Corp.
<http://www.bioware.com>
The toolset does not edit skeleton palettes. They are edited by hand using the GFF Editor. Because they
are hand-edited, they contain some GFF Fields that exist primarily to make editing easier, and which
have no actual effect in the toolset.
Table 2.2.1 describes the top-level struct in a skeleton blueprint palette.
Table 2.2.1: Top Level Struct, Skeleton Blueprint Palette
Label
Type
Description

### MAIN

List
List of TreeNode Structs of  Struct ID 1.
The Structs can be Branches or Categories.

### NEXT_USEABLE_ID

### BYTE

This field exists for the convenience of the
person editing the palette.

When creating a new palette category, use
the value of this field as the next ID.

After creating the new palette category,
increment this value.

### RESTYPE

### WORD

ResType of the blueprint files to scan when
generating the standard palette for this
skeleton palette. See Section 2.3.
For a list of ResTypes, See Section 1.3 of
the Key and BIF document
All tree nodes in a skeleton blueprint palette share the Fields given below in Table 2.2.2a. Branch and
Category nodes also include the Fields given in Tables 2.2.2b and 2.2.2c, respectively.
Table 2.2.2a: TreeNode
Label
Type
Description

### DELETE_ME

CExoString
User-readable string for the convenience of
the person editing the palette. Should be
identical to the text of the StrRef.

### STRREF

### DWORD

StrRef indicating the text to display for this
TreeNode.

### TYPE

### BYTE

Extra information about this treenode.

This  Field is usually omitted. If omitted, the
toolset will always display this treenode.
Otherwise, the toolset displays this node
according to the value of the TYPE, as
given in Table 2.2.3.
Table 2.2.2b: TreeNode Branch (derived from TreeNode)
Label
Type
Description

### LIST

List
List of other treenode Structs, all having
StructID 1. Child nodes can be Branches or
Categories.
Table 2.2.2c: TreeNode Palette Category (derived from TreeNode)
Label
Type
Description
ID

### BYTE

Palette Node ID
Table 2.2.3: TreeNode Types
Type
Name
Description
0

### DISPLAY_IF_NOT_EMPTY

The node only appears in the toolset if it has

## Page 4

BioWare Corp.
<http://www.bioware.com>
child nodes.
1

### NWPALETTE_DISPLAY_NEVER

The node never appears in the toolset.
2

### NWPALETTE_DISPLAY_CUSTOM

The node only appears:

1) in a custom blueprint palette,
2) in the skeleton palette that is displayed
when creating a new blueprint or
3) in the skeleton palette when choosing the
palette category for a custom blueprint.
2.3. Standard Blueprint Palettes
A standard blueprint palette is a palette that contains blueprint nodes for all the blueprints that exist
in the global game resources. That is, resources that exist in the BIF files and in Override. There is one
standard blueprint palette for each blueprint resource type. The toolset recognizes the following:
creaturepalstd.itp
doorpalstd.itp
encounterpalstd.itp
itempalstd.itp
placeablepalstd.itp
soundpalstd.itp
storepalstd.itp
triggerpalstd.itp
waypointpalstd.itp
The toolset does not edit the standard blueprint palettes.
Each standard palettes is generated from a skeleton palette by the following procedure:

1. Find all treenodes in the skeleton palette that have a TYPE of 1 or 2 (see Table 2.2.3) and remove
them.
2. Remove all DELETE_ME Fields from all treenodes in the skeleton palette. Exception: if the
STRREF is 0xffff ffff, then rename DELETE_ME to NAME and remove the STRREF Field.
3. Remove the NEXT_USEABLE_ID Field from the skeleton palette's Top Level Struct.
4. Read the RESTYPE from the skeleton palette's Top Level Struct then remove that Field.
5. Find all standard resources (resources in the .BIF files and Override) that have the ResType
specified in the previous step.
6. For each resource found, open it and read the "PaletteID" BYTE Field in its Top Level GFF
Struct.
7. Find the Category node in the palette that has an ID Field matching the PaletteID of the blueprint.
If the Category node does not already have a LIST Field (see Table 2.3.2a), add it. Add a
Blueprint TreeNode (see Table 2.3.3a) to that Category node's LIST.
8. If the blueprint's localized name CExoLocString Field (explained below) contains embedded text,
create a NAME Field in the Blueprint Node, and set it to the embedded text string that matches the
user's own language. Otherwise, create a STRREF Field in the Blueprint Node, and set it to the
StrRef of the localized name field. Different blueprint types use different Fields as their localized
name. Check Table 2.3.4 to determine what GFF Field to use.
9. Set the RESREF Field to the blueprint's ResRef. If the palette is a creature palette, the Blueprint
node should include Challenge Rating and Faction information, as given in Table 2.3.3b.
10. Repeat steps 6 to 9 for all blueprint resources found in step 5.
11. Find all treenodes in the skeleton palette that have a TYPE of 0 (see Table 2.2.3) and remove them
if they have no children. If the node stays, remove its TYPE Field.

## Page 5

BioWare Corp.
<http://www.bioware.com>
Figure 2.3 shows an example of a standard blueprint palette that might be generated from the skeleton
palette in Figure 2.2.
Figure 2.3: Example Standard Blueprint Palette

### MAIN

Armor (Branch)
Weapons (Branch)
Bladed (Branch)
Full Plate +4 (Blueprint)
Daggers (Category)
Heavy (Category)
Helmets (Category)
Swords (Category)
Miscellaneous (Category)
Bows (Category)
Top (Blueprint)
Rags (Blueprint)

The tables below describe the GFF structure of a standard blueprint palette.
Table 2.3.1: Top Level Struct
Label
Type
Description

### MAIN

List
List of TreeNode Structs of  Struct ID 0.
Table 2.3.2a: TreeNode
Label
Type
Description

### NAME

CExoString
Text to display for the treenode.
Only NAME or STRREF are present but not
both. See subsequent tables for further
details.

### STRREF

### DWORD

StringRef of the text to display for this
treenode.
Only NAME or STRREF are present but not
both. See subsequent tables for further
details.

## Page 6

BioWare Corp.
<http://www.bioware.com>
Table 2.3.2b: TreeNode Branch (derived from TreeNode)
Label
Type
Description

### LIST

List
List of TreeNode Branches or Categories
but not both.

Technically, there is no reason why there
cannot be both Branches and Categories, but
in practice and as a matter of convention,
this is never done.

### STRREF

### DWORD

StringRef of the text to display for this
treenode. The NAME Field, if present, is
ignored.
Table 2.3.2c: TreeNode Palette Category (derived from TreeNode)
Label
Type
Description

### LIST

List
list of TreeNode Blueprints
ID

### BYTE

Palette Node ID

### STRREF

### DWORD

StringRef of the text to display for this
treenode. The NAME Field, if present, is
ignored.
Table 2.3.3a: TreeNode Blueprint (derived from TreeNode)
Label
Type
Description

### NAME

CExoString
Text to display for the treenode.
Only NAME or STRREF should be present
but not both. STRREF overrides NAME if
both are present.

### STRREF

### DWORD

StringRef of the text to display for this
treenode.
Only NAME or STRREF should be present
but not both. STRREF overrides NAME if
both are present.

### RESREF

CResRef
ResRef of the blueprint
Table 2.3.3b: TreeNode Creature (derived from Blueprint)
Label
Type
Description
CR

### FLOAT

Challenge Rating

### FACTION

CExoString
Name of the creature's faction.
When generating a Blueprint treenode as per the steps given earlier in this section, the NAME or
STRREF Field of the node's Struct is obtained from the source blueprint's localized name Field as listed
in Table 2.3.4.
Table 2.3.4: LocName Fields by ResType
ResType
File Type
Blueprint Type
LocName Field
2025
UTI
Item
LocalizedName
2027
UTC
Creature
FirstName
2032
UTT
Trigger
LocalizedName
2035
UTS
Sound
LocName
2040
UTE
Encounter
LocalizedName
2042
UTD
Door
LocName
2044
UTP
Placeable
LocName
2051
UTM
Store
LocName
2058
UTW
Waypoint
LocalizedName

## Page 7

BioWare Corp.
<http://www.bioware.com>
2.4. Custom Blueprint Palettes
A custom blueprint palette is a palette that contains blueprint nodes for all the blueprints of a given
resource type within a module.
The toolset recognizes the following custom blueprint palettes:
creaturepalcus.itp
doorpalcus.itp
encounterpalcus.itp
itempalcus.itp
placeablepalcus.itp
soundpalcus.itp
storepalcus.itp
triggerpalcus.itp
waypointpalcus.itp
Custom blueprint palettes have the same GFF structure as standard blueprint palettes.
However, instead of having their blueprint nodes defined by the standard game resources, the blueprint
nodes in a custom blueprint palette are generated by scanning all the resources of the appropriate type
within the custom palette's module.
Also, custom blueprint palettes include Category nodes that were Type 2 in the skeleton palette (see
Table 2.2.3) whereas standard blueprint palettes do not include those Category nodes.
3. Tileset Palettes
3.1. Skeleton Tileset Palettes
A skeleton tileset palette acts as a framework from which a full tileset palette can be generated. They
never appear in the toolset or game.
All skeleton tileset palettes are identical except for their TILESETRESREF Field in the Top Level GFF
Struct. Figure 3.1.1 is a simplified representation of a skeleton tileset palette.
Figure 3.1.1: Skeleton Tileset Palette

### MAIN

Terrain (Category)
Groups (Category)
Features (Category)

Figure 3.1.2 shows what a skeleton tileset palette should look like in the GFF Editor. In the last Field,
the <resref> value is the only variable one.

## Page 8

BioWare Corp.
<http://www.bioware.com>
Figure 3.1.2: Skeleton Tileset Palette in GFF Editor

Some internal BioWare tileset palette generation utilities expect the TILESETRESREF Field to have a
value equal to the ResRef of the .set file that the skeleton tileset palette is to be used with. The
following are the skeleton tileset palettes that are included with the original version of the game, and
which follow this resref rule:
tcn01pal.itp
tdc01pal.itp
tde01pal.itp
tdm01pal.itp
tds01pal.itp
tic01pal.itp
tin01pal.itp
tms01pal.itp
ttf01pal.itp
ttr01pal.itp
tcn01pal.itp, for example, has TILESETRESREF = "tcn01".
BioWare's TilePaletteGen program is a command-line application that takes the file path to a
tileset .set file as its single argument. It does not follow the above rule. Instead, it uses the same
skeleton tileset palette (skeletontilepalette.itp) regardless of set file specified, ignoring the
TILESETRESREF Field and using the resref implied by its command line argument instead.
The following tables describe the GFF structure of a skeleton tileset palette.
Table 3.1.1: Top Level Struct, Skeleton Blueprint Palette
Label
Type
Description

### MAIN

List
List of TreeNode Category Structs of  Struct

### ID 1

### NEXT_USEABLE_ID

### BYTE

Always 3

### RESTYPE

### WORD

Always 2013. Corresponds to .set files.

### TILESETRESREF

CResRef
ResRef of the .set file. This is the only field
that differs between between skeleton tileset
palettes.
Table 3.1.2: TreeNode Category
Label
Type
Description

### DELETE_ME

CExoString
User-readable string for the convenience of

## Page 9

BioWare Corp.
<http://www.bioware.com>
the person editing the palette. Should be
identical to the text of the StrRef.
ID

### BYTE

0 = features
1 = groups
2 = terrain

### STRREF

### DWORD

StrRef indicating the text to display for this
TreeNode.
3.2. Standard Tileset Palettes
A standard tileset palette is a completed tileset palette that contains treenodes for all the tileset groups,
features, terrain types, and crossers that are defined in a corresponding tileset .set file. The naming
convention for a standard tileset palette is <tilesetresref>palstd.itp, where <tilesetresref>
is the ResRef of the tileset's .set file. For example, tcn01.set would have a palette called
tcn01palstd.itp.
Figure 3.2 shows a sample tileset palette tree structure. Note its similarity to Figure 3.1.1.
Figure 3.2: Example Standard Tileset Palette

### MAIN

Terrain (Category)
Groups (Category)
Features (Category)
Ant HIll (Feature)
Cave (Feature)
Barn (Group)
Windmill (Group)
Grass (Terrain)
Road (Terrain)
Stream (Terrain)

The following tables describe the GFF Structure of a standard tileset palette.
Table 3.2.1: Top Level Struct, Skeleton Blueprint Palette
Label
Type
Description

### MAIN

List
List of TreeNode Category Structs of  Struct

### ID 1

## Page 10

BioWare Corp.
<http://www.bioware.com>
Table 3.2.2: TreeNode Category
Label
Type
Description
ID

### BYTE

0 = features
1 = groups
2 = terrain

### LIST

List
List of TreeNode Leaves

### STRREF

### DWORD

StrRef indicating the text to display for this
TreeNode.
Note that the NAME CExoString Field is
ignored for tileset palette categories.
Table 3.2.3: TreeNode Leaf
Label
Type
Description

### NAME

CExoString
Text to display for the treenode.
Only NAME or STRREF should be present
but not both. STRREF overrides NAME if
both are present.

### RESREF

CResRef
If parent TreeNode ID == 0 (features):
this is the ResRef of the MDL file for the
Tile to use for this feature.

If parent TreeNode ID == 1 (groups):
this is the ResRef of the first MDL file in
the TileGroup.

If parent TreeNode's ID == 2 (terrain):
this is the name of the TerrainType (Terrain
or Crosser) to paint. This text is all-lower-
case, and is checked against the Terrain and
Crossers defined in the set file via case-
insensitive comparisons. Also, there are two
special terrain nodes, eraser and raise-lower,
that are not directly tied to terrain or
crossers, but which also appear until the
Terrain category.

### STRREF

### DWORD

StrRef indicating the text to display for this
TreeNode Leaf.
Only NAME or STRREF are present but not
both. STRREF overrides NAME if both are
present.
The Features and Groups categories both contain tilegroups from the tileset .set file. The STRREF
Field value is equal to the StrRef of the tilegroup (The StrRef entry in the corresponding [GROUP*]
section in the tileset .set file). The RESREF Field value is equal to the ResRef of the model file used by
the first tileset tile in the tilegroup (The Tile0 entry in the corresponding [GROUP*] section in the
tileset .set file).
The Features list contains tilegroups that contain a single tileset tile. The Groups list contains
tilegroups that contain more than one tileset tile.
As a result of the RESREF Field referencing the first model in a tilegroup, it follows that every
tilegroup in a tileset should use a different tile as its first tile. If two tilegroups both use the same tile as
tile 0, then the toolset will end up using the first tilegroup even when the user tries to paint the second
tilegroup.

## Page 11

BioWare Corp.
<http://www.bioware.com>
The Terrain category contains both terrain and crossers from the tileset .set file. . The STRREF Field
value is equal to the StrRef of the terrain or crosser (The StrRef entry from the corresponding
[CROSSER*] or [TERRAIN*] section in the tileset .set file).The RESREF Field value is equal to the
Name of the terrain or crosser, converted to all-lower-case (The Name entry from the corresponding
[CROSSER*] or [TERRAIN*] section in the tileset .set file). No two terrains or crossers should have
the same tileset name, or else the toolset will use the first one found and never use the others. The list of
terrain types is checked first, followed by the list of crossers.
There are also two special terrain treenodes that do not directly correspond to any crossers or terrain
types. They are the eraser and raise/lower nodes. Their GFF Field values are summarized in Table
3.2.4. If the toolset encounters their exact RESREF values in a treenode located under the Terrain
category, it automatically goes into its eraser or raise/lower handling system, without checking for a
matching crosser or terrain type. Therefore, no crosser or terrain type should use "eraser" or
"raiselower" as their name.
All tileset palettes include an eraser treenode under the Terrain category. The eraser paints down the
tileset's default terrain type (the Default entry from the [GENERAL] section of the tileset .set file).
If a tileset contains height transitions (as specified by the HasHeightTransition entry in the
[GENERAL] section of the tileset .set file) then the tileset palette should also include a raise/lower
treenode under the Terrain category.
Table 3.2.4: Special Terrain Nodes
Type

### RESREF

### STRREF

Description
Eraser
eraser
63291
Paints the default terrain type.
Raise/Lower
raiselower
63292
Present only if the tileset has height transitions.

### See also

- [GFF-File-Format](GFF-File-Format) -- GFF structure
- [Bioware-Aurora-GFF](Bioware-Aurora-Core-Formats#gff) -- Aurora GFF spec
- [Container-Formats#key](Container-Formats#key) -- Resource resolution
- [TSLPatcher-GFFList-Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax) -- Patching GFF


---
