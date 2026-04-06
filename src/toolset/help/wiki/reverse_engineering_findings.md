# Reverse Engineering Findings: swkotor.exe and swkotor2.exe

## Overview

This document summarizes engine-level findings from reverse engineering the KotOR I and II game executables (e.g. with Ghidra). It is meant to inform PyKotor and toolset work at a conceptual level: class names, control flow, and subsystem roles—not step-by-step tool transcripts or raw dumps. For continued analysis, use your usual RE workflow on a loaded game binary and cross-check with vendor and community references; see [Community sources and archives](Home#community-sources-and-archives). Walkmesh / BWM / AABB engine behavior is documented under [BWM / walkmesh / AABB (engine implementation analysis)](reverse_engineering_findings#bwm-walkmesh-aabb-engine-implementation-analysis) below. Repository automation guidance for agents is in [AGENTS.md](https://github.com/OpenKotOR/PyKotor/blob/master/AGENTS.md) (conceptual wiki policy).

## Table of Contents

- [Reverse Engineering Findings: swkotor.exe and swkotor2.exe](#reverse-engineering-findings-swkotorexe-and-swkotor2exe)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Engine Architecture](#engine-architecture)
    - [Scripting Engine (NWScript Virtual Machine)](#scripting-engine-nwscript-virtual-machine)
    - [Resource Management System](#resource-management-system)
      - [CExoResMan (resource manager)](#cexoresman-resource-manager)
    - [Module Archive Loading System](#module-archive-loading-system)
    - [Generic GFF Field Defaults](#generic-gff-field-defaults)
    - [Graphics and Rendering System](#graphics-and-rendering-system)
    - [Model Loading System](#model-loading-system)
      - [MDL/MDX read pipeline](#mdlmdx-read-pipeline)
    - [Save / Load System](#save-load-system)
    - [Executable Startup and Initialization](#executable-startup-and-initialization)
  - [BWM / walkmesh / AABB (engine implementation analysis)](#bwm-walkmesh-aabb-engine-implementation-analysis)
    - [Overview](#overview-1)
    - [Key Data Structures](#key-data-structures)
      - [`CSWWalkMeshHeader`](#cswwalkmeshheader)
      - [`CSWRoomSurfaceMesh`](#cswroomsurfacemesh)
      - [`AABB_t` Node Structure](#aabb_t-node-structure)
    - [Critical Functions](#critical-functions)
      - [`CSWCollisionMesh__LoadMeshBinary`](#cswcollisionmesh__loadmeshbinary)
      - [`CheckAABBNode` / `HitCheckAABBnode`](#checkaabbnode-hitcheckaabbnode)
      - [`CSWCollisionMesh__WorldToLocal`](#cswcollisionmesh__worldtolocal)
      - [Writing BWM Files](#writing-bwm-files)
    - [Coordinate Spaces and Transformations](#coordinate-spaces-and-transformations)
      - [WOK Files (Area Walkmeshes)](#wok-files-area-walkmeshes)
      - [PWK/DWK Files (Placeable/Door Walkmeshes)](#pwkdwk-files-placeabledoor-walkmeshes)
    - [*AABB* Tree Implementation Details](#aabb-tree-implementation-details)
      - [Child Index Encoding](#child-index-encoding)
      - [Most Significant Plane Values](#most-significant-plane-values)
    - [Material Handling](#material-handling)
      - [Material IDs and Masks](#material-ids-and-masks)
      - [Walkable vs. Non-Walkable Materials](#walkable-vs-non-walkable-materials)
    - [*Adjacency* Encoding](#adjacency-encoding)
      - [*Storage* Format](#storage-format)
      - [Decoding Formula](#decoding-formula)
      - [Bidirectional Requirement](#bidirectional-requirement)
    - [Edge and Perimeter Handling](#edge-and-perimeter-handling)
      - [Edge Format](#edge-format)
      - [*Perimeter* Format](#perimeter-format)
    - [Implementation Recommendations](#implementation-recommendations)
    - [References](#references)
  - [Using agdec for further analysis](#using-agdec-for-further-analysis)
  - [Tools Used](#tools-used)
  - [See Also](#see-also)
  - [References](#references-1)

## Engine Architecture

### Scripting Engine (NWScript Virtual Machine)

**Key Components:**

- `CVirtualMachine`: Main virtual machine class that manages script execution
- `CVirtualMachineInternal`: Core VM implementation with stack management
- `CVirtualMachineStack`: Stack-based execution environment
- `CVirtualMachineCmdImplementer`: Command implementation interface

**Execution Flow:**

1. `CVirtualMachine::RunScript()` loads and executes scripts
2. `ReadScriptFile()` parses NCS bytecode from files
3. `ExecuteCode()` interprets bytecode using a large switch-based interpreter (5529 bytes at 0x005d2bd0)
4. Stack operations handle data types: int, float, string, object, vector
5. Call stack tracks function execution depth

**Detailed ExecuteCode Analysis:**
The `ExecuteCode` function is a massive switch statement with the following instruction set:

**Stack Operations:**

- `CPDOWNSP`/`CPDOWNBP`: Copy down stack/base pointer with offset and size parameters
- `CPTOPSP`/`CPTOPBP`: Copy to top of stack/base pointer
- `RSADDx`: Reserve space and add (types: int=3, float=4, string=5, object=6, engine_structs=16-25)

**Constants:**

- `CONSTx`: Push constants (int=3, float=4, string=5, object=6) with embedded values

**Actions:**

- `ACTION`: Execute command with 16-bit command ID parameter

**Logic:**

- `LOGANDII`: Logical AND for integers

**Control Flow:**

- `JMP`, `JZ`, `JNZ`: Jump instructions
- `RETN`: Return from function

**Arithmetic:**

- `ADDII`/`ADDIF`/`ADDFF`: Addition operations
- `SUBII`/`SUBIF`/`SUBFF`: Subtraction operations
- `MULII`/`MULIF`/`MULFF`: Multiplication operations
- `DIVII`/`DIVIF`/`DIVFF`: Division operations

**Safety Features:**

- Instruction count limit (0x1ffff instructions max)
- Stack bounds checking prevents overflows
- Invalid instruction types return `INVALID_INSTRUCTION_TYPE` error
- Stack unwinding on execution failures

**Key Insights:**

- Scripts are loaded synchronously via resource system
- Bytecode execution is stack-based with typed operations
- Error handling includes stack unwinding on failures
- Command callbacks allow engine integration

<a id="resource-management-system"></a>

### Resource Management System

**Core Classes:**

- `CRes`: Base resource class for all file formats
- `CResRef`: 16-byte resource reference (ResRef) with string conversion
- `CResGFF`: GFF file format handler
- `CRes2DA`: 2DA file format handler
- `CResHelper<T>`: Template for type-specific resource handlers

#### CExoResMan (resource manager)

This section documents the core resource manager used by both KotOR I and II (reverse-engineered from the game executables). The `CExoResMan` class provides a unified interface for locating and loading resources (textures, models, scripts, etc.) from several storage shapes. High-level resolution order matches the wiki’s [resource resolution order](Concepts#resource-resolution-order): override directory, then loaded MOD/SAV, then KEY/BIF.

**Container type flags** (how the engine classifies registered sources):

- `FIXED` (0x00000000): KEY/BIF files (chitin.key + data/*.bif)
- `RIM` (0x20000000): Resource-image path in the resource manager (e.g. texture packs; naming per MacOS symbols / `AddResourceImageFile()`, see [PyKotor#47](https://github.com/OpenKotOR/PyKotor/issues/47); compare on-disk [RIM](Container-Formats#rim) capsules)
- `ERF` (0x40000000): Encapsulated archives on disk ([ERF File Format](Container-Formats#erf), [RIM File Format](Container-Formats#rim); often `modules/*.rim`, `modules/*.mod`, `modules/*.erf`)
- `DIRECTORY` (0x80000000): Loose files in directories

**Logical storage categories** (orthogonal to the flags above):

- **Directories** on disk (e.g. override)
- **Encapsulated containers** (BIF/ERF)
- **Image resources** (resource-image / binary blobs registered via the RIM-type path)
- **Resource files** (ERF-backed modules and similar)

**Typical internal lookup sequence** (conceptual; all paths follow the same pattern):

1. Inspect the `CRes` instance for flags or already-cached data.
2. Compute a hash or index key (K1 examples: helpers around `0x005e9b60` / `0x005e9b90`—re-verify offsets for your binary and build).
3. Walk the relevant table until a match is found.
4. Dispatch to the resource-type loader via virtual methods.
5. Update the `CRes` object and optionally invoke callbacks.

**Primary registration and load entry points:**

- `CExoResMan::AddKeyTable()`: Loads container tables with type flags
- `CExoResMan::ReadResource()`: Loads resources from containers
- `AddResourceImageFile()` calls `AddKeyTable(..., RIM, 0)` for texture packs (RIM = Resource Image)

**Other notable `CExoResMan` methods** (names are stable across K1/TSL; confirm in decompilation):

- `GetResOfType` — returns a `CExoStringList` of resource names for a type
- `AddResourceDirectory` / `AddResourceImageFile` — register search paths
- `ServiceFromDirectory` / `ServiceFromEncapsulated` / `ServiceFromImage` / `ServiceFromResFile` — core lookup routines per storage kind
- `CancelRequest` / `Demand` — reference counting and cancellation
- `Exists` — quick existence check (may fill a timestamp pointer)
- `Update` — periodic maintenance; may refresh internal caches
- `ReadRaw` — raw bytes; dispatches to the appropriate service method
- `WipeDirectory` — internal cleanup when a directory is removed

**Notes for contributors:**

- When extending RE notes for new resource types, follow the same hash/lookup pattern described above.
- Cross-check both K1 and TSL; the engines are nearly identical but addresses differ.
- [2DA-File-Format](2DA-File-Format) documents table layout; pair with [Container-Formats#key](Container-Formats#key), [Container-Formats#bif](Container-Formats#bif), and [Container-Formats#erf](Container-Formats#erf) for container-level behaviour.

Open work: map these methods to the exact BIF/ERF/KEY parser routines in a loaded binary and keep this section aligned with those findings.

**GFF Structure (from `CResGFF` analysis):**

```cpp
struct CResGFF {
    CRes resource;                    // Base resource (inherits from CRes)
    GFFHeaderInfo* header;            // File header with type/version
    GFFStructData* structs;           // Struct definitions array
    GFFFieldData* fields;             // Field definitions array
    char (*labels)[16];               // 16-byte null-terminated labels
    void* field_data;                 // Raw field data buffer
    ulong* field_indices_data;        // Field index arrays
    ulong* list_indices_data;         // List index arrays
    // Dynamic capacity tracking for all arrays
};
```

**GFF Creation Process (from `CreateGFFFile` at `0x00411260`):**

1. Takes file type string parameter (param_3)
2. Uses hardcoded global `GFFVersion` variable (`0x0073e2c8`) containing "V3.2" for version
3. Writes 4-byte file type (little-endian) to header using param_3 bytes
4. Writes hardcoded 4-byte version `"V3.2"` (little-endian) to header from global variable
5. Creates root struct with `AddStruct(this, 0xffffffff)`
6. Initializes all data structures for writing

**GFF Version Support:**
The engine's `CreateGFFFile` function is hardcoded to only create V3.2 GFF files. It does not accept version parameters - instead uses a global `GFFVersion` variable containing `"V3.2"`. The xoreos-tools support for V3.3, V4.0, and V4.1 suggests these formats may be supported for reading but not writing by the original engine.

**Key Functions:**

- `CResRef::CopyToString()`: Converts ResRef to string
- `CResGFF::ReadFieldCResRef()`: Reads ResRef fields from [GFF](GFF-File-Format)
- `CResGFF::WriteFieldCResRef()`: Writes ResRef fields to [GFF](GFF-File-Format)
- `CreateGFFFile()`: Creates [GFF](GFF-File-Format) files with specified type/version
- `WriteGFFFile()`: Serializes [GFF](GFF-File-Format) to disk

### Module Archive Loading System

The module loader uses a small set of archive naming rules rather than a single container format. The core behavior recovered from both executables is:

- Simple path: load `<module>.rim` directly.
- Area-split path: prefer `<module>_a.rim`; if absent, try `<module>_adx.rim`; if both are absent, fall back to `<module>.rim`.
- Supplemental data path: load `<module>_s.rim` in addition to the base area archive when it exists.
- TSL-specific dialog split: load `<module>_dlg.erf` for dialog resources instead of storing DLG data in `_s.rim`.
- Override archive path: `<module>.mod` takes precedence over the vanilla multi-file set and suppresses the normal RIM/ERF combination.

The same research also confirms the effective runtime search order used by higher-level resource lookups: loose override content first, then active module resources, then the global KEY/BIF set. The loadscreen path follows the same pattern after resolving the module ARE header and then mapping `LoadScreenID` through `loadscreens.2da` to `bmpresref`.

### Generic GFF Field Defaults

Reverse-engineered GFF generic behavior is still incomplete, but a few points are stable enough to centralize here.

- `CResGFF::CreateGFFFile()` only writes `V3.2` headers in the original engine.
- Encounter (`UTE`) creature-list identity is driven by the creature entry itself rather than list index position.
- Confirmed `UTE` creature-list fields include `ResRef`, `CR`, `SingleSpawn`, and `Appearance`.
- `GuaranteedCount` is TSL-only in the known encounter path and defaults to `0` when absent, so a missing field and an explicit zero should be treated as equivalent for behavioral comparison.

Confirmed encounter reader references from prior research:

- `CSWSEncounter::LoadEncounter` @ (K1: `0x00593830`, TSL: `TODO`)
- `ReadEncounterFromGff` @ (K1: `0x00592430`, TSL: `TODO`)

### Graphics and Rendering System

**OpenGL Setup:**

```cpp
void SetupOpenGL() {
    glClearColor(0, 0, 0, 0);
    glEnable(GL_CULL_FACE);
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_LIGHTING);
    glEnable(GL_TEXTURE_2D);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable(GL_ALPHA_TEST);
}
```

**Features:**

- Standard OpenGL 1.x pipeline
- Depth testing and face culling
- Multi-texturing support
- Alpha blending for transparency
- Lighting system integration

### Model Loading System

**Architecture:**

- `IODispatcher`: Central I/O system for resource loading
- `MaxTree`: Tree-based model representation
- Model caching with `modelsList` global array
- Synchronous loading via `IODispatcher::ReadSync()`

**Key Functions:**

- `LoadModel()`: Main [model](MDL-MDX-File-Format) loading function
- `FindModel()`: [Model](MDL-MDX-File-Format) cache lookup
- `AddModel()`: Cache management
- `MaxTree::AsModel()`: Tree to [model](MDL-MDX-File-Format) conversion

#### MDL/MDX read pipeline

Binary MDL/MDX file I/O operations.

This module handles reading and writing binary MDL/MDX format files used in KotOR. The MDL file contains node hierarchy, animations, and metadata, while the MDX file contains vertex data, faces, and geometry payload.

**Scope:**

- The MDL file stores hierarchy, animation, and metadata.
- The MDX file stores geometry payload such as vertices and faces.
- The engine path below covers the executable-side binary parsing and object construction flow.

**I/O and parsing functions:**

- **LoadModel** @  (/K1/k1_win_gog_swkotor.exe: 0x00464200, TSL: 0x0047a570)
  - Main model loader entry point (172 bytes, 6 callees, 2 callers).
  - Signature: `Model * __cdecl LoadModel(int param_1, undefined4 param_2)`
  - Logic:
    1. Saves `CurrentModel` to the stack.
    2. Returns `NULL` if `param_1` is `0`.
    3. Sets `CurrentModel` to `NULL`.
    4. Gets the `IODispatcher` singleton via `IODispatcher::GetRef()` @  (/K1/k1_win_gog_swkotor.exe: 0x004a0580, TSL: 0x004cda00).
    5. Calls `IODispatcher::ReadSync()` @  (/K1/k1_win_gog_swkotor.exe: 0x004a15d0, TSL: 0x004cead0) with `param_1` and `param_2`.
    6. `ReadSync()` creates an `Input` object and calls `Input::Read()` @  (/K1/k1_win_gog_swkotor.exe: 0x004a1260, TSL: 0x004ce780).
    7. `Input::Read()` calls `InputBinary::Read()`, which parses the binary MDL/MDX format.
    8. The returned `MaxTree*` is converted to `Model*` via `MaxTree::AsModel()` @  (/K1/k1_win_gog_swkotor.exe: 0x0043e1c0, TSL: 0x0044ff90).
    9. `MaxTree::AsModel()` checks for `MODEL_TYPE` and returns the cast pointer or `NULL`.
    10. On success, the loader scans `modelsList.data` for a duplicate by comparing model names with `__stricmp()`.
    11. If a duplicate exists, the new model is destroyed and the cached model is returned.
    12. Otherwise, the newly loaded model is returned.
    13. `CurrentModel` is restored before return.
  - Callees:
    - `~Model()` @  (/K1/k1_win_gog_swkotor.exe: 0x0043f790, TSL: 0x004527d0) for duplicate cleanup.
    - `IODispatcher::GetRef()` @  (/K1/k1_win_gog_swkotor.exe: 0x004a0580, TSL: 0x004cda00) for singleton access.
    - `MaxTree::AsModel()` @  (/K1/k1_win_gog_swkotor.exe: 0x0043e1c0, TSL: 0x0044ff90) for the type check and cast.
    - `__stricmp()` @  (/K1/k1_win_gog_swkotor.exe: 0x0070acaf, TSL: 0x0077e24f) for case-insensitive model-name comparison.
    - `operator.delete()` @  (/K1/k1_win_gog_swkotor.exe: 0x0044aec0, TSL: 0x0045f520) for deallocation.
    - `IODispatcher::ReadSync()` @  (/K1/k1_win_gog_swkotor.exe: 0x004a15d0, TSL: 0x004cead0), which reaches:
      - `Input::Read()` @  (/K1/k1_win_gog_swkotor.exe: 0x004a1260, TSL: 0x004ce780)
      - `InputBinary::Read()`
      - `AurResGetNextLine()` @  (/K1/k1_win_gog_swkotor.exe: 0x0044bfa0, TSL: N/A - ASCII MDL format not supported in TSL)
      - `AurResGet()` @  (/K1/k1_win_gog_swkotor.exe: 0x0044c740, TSL: 0x00460db0)
      - `FuncInterp()` @  (/K1/k1_win_gog_swkotor.exe: 0x0044c1f0, TSL: N/A - ASCII MDL format not supported in TSL)
  - Callers:
    - `NewCAurObject()` @  (/K1/k1_win_gog_swkotor.exe: 0x00449cc0, TSL: 0x0045e2e0) -> `LoadModel()` @  (/K1/k1_win_gog_swkotor.exe: 0x00449d9d, TSL: 0x0047a570)
      - Used by `HideWieldedItems()`, `LoadSpellVisual()`, `LoadConjureVisual()`, `AddObstacle()`, `SetWeather()`, `LoadVisualEffect()`, `SetGunModel()`, `SpawnRooms()`, `CollapsePartTree()`, `FireGunCallback()`, `LoadAnimatedCamera()`, `SetPlayer()`, `LoadModel()`, `LoadModelAttachment()`, `AddEnemy()`, `LoadLight()`, `AddGun()`, `CreateReferenceObjects()`, `ChunkyParticle()`, `CreateMuzzleFlash()`, `SpawnPartsForTile()`, `SetProjectileVelAndAccel()`, `SpawnHitVisuals()`, `LoadArea()`, `SpawnVisualEffect()`, `AddPlaceableObjectLight()`, `LoadBeam()`, `ApplyShadowBlob()`, `AddModel()`, and `SpawnRoom()`.
    - `LoadAddInAnimations()` @  (/K1/k1_win_gog_swkotor.exe: 0x00440890, TSL: 0x004538d0) -> `LoadModel()` @  (/K1/k1_win_gog_swkotor.exe: 0x004408f7, TSL: 0x0047a570)
      - Searches with `FindModel(param_1)`.
      - Appends `.mdl` if no cached model is found.
      - Opens the file and synchronizes animation trees with `MaxTree::SynchronizeTree()`.
  - Notes:
    - Uses the global `CurrentModel` as thread-local-style context.
    - Accesses the global `modelsList` cache.
    - TSL does not expose the same easy-to-match address pattern; the higher-level loaders may have absorbed part of this logic.

- **IODispatcher::ReadSync** @  (/K1/k1_win_gog_swkotor.exe: 0x004a15d0, TSL: 0x004cead0)
  - Synchronous I/O dispatcher for model files (36 bytes).
  - Signature: `void __thiscall IODispatcher::ReadSync(IODispatcher *this, FILE *param_1, FILE *param_2)`
  - Logic:
    1. Creates a 12-byte `Input` object on the stack.
    2. Calls `Input::Read(local_10, param_1, param_2)`.
    3. Defers all actual MDL/MDX parsing to `Input::Read()`.
  - Callees:
    - `Input::Read()` @  (/K1/k1_win_gog_swkotor.exe: 0x004a1260, TSL: 0x004ce780)
    - `InputBinary::Read()`
    - `AurResGetNextLine()` @  (/K1/k1_win_gog_swkotor.exe: 0x0044bfa0, TSL: N/A - ASCII MDL format not supported in TSL)
    - `AurResGet()` @  (/K1/k1_win_gog_swkotor.exe: 0x0044c740, TSL: 0x00460db0)
    - `FuncInterp()` @  (/K1/k1_win_gog_swkotor.exe: 0x0044c1f0, TSL: N/A - ASCII MDL format not supported in TSL)
  - Callers:
    - `LoadModel()` @  (/K1/k1_win_gog_swkotor.exe: 0x00464200, TSL: 0x0047a570)

- **MaxTree::AsModel** @  (/K1/k1_win_gog_swkotor.exe: 0x0043e1c0, TSL: 0x0044ff90)
  - Type-check-and-cast helper (16 bytes, 88 callers).
  - Signature: `Model * __thiscall MaxTree::AsModel(MaxTree *this)`
  - Logic:
    1. Checks whether `(this->type & 0x7f) == 2` (`MODEL_TYPE`).
    2. Uses a bitwise mask to return either `this` cast to `Model*` or `NULL`.
    3. Equivalent high-level form: `return ((this->type & 0x7f) == 2) ? (Model*)this : NULL;`
  - Representative callers:
    - `ProcessSkinSeams()` @  (/K1/k1_win_gog_swkotor.exe: 0x004392b6, TSL: 0x0044a920) and its in-function call sites.
    - `FindModel()` @  (/K1/k1_win_gog_swkotor.exe: 0x00464176, TSL: 0x0047a480).
    - `LoadModel()` @  (/K1/k1_win_gog_swkotor.exe: 0x00464236, TSL: 0x0047a570).
    - `BuildVertexArrays()` @  (/K1/k1_win_gog_swkotor.exe: 0x00478b50, TSL: 0x00495620) and its in-function call sites.
    - `Input::Read()` @  (/K1/k1_win_gog_swkotor.exe: 0x004a1435, TSL: 0x004ce8c0) and related in-function call sites.

**Function discovery methodology:**

Functions are located through:

1. String cross-references, such as `.mdl`, model names, and error strings.
2. Call-chain analysis from known entry points.
3. VTable offsets for virtual methods.
4. Imported-library call sites used by model code.
5. Decompilation-pattern matching across both executables.

**Engine-level model loading functions:**

      These functions are part of the game engine's object system and handle loading models
      into creature, placeable, and other game objects. These are higher-level functions
      that use the binary MDL/MDX I/O functions above.

##### CSWCCreature::LoadModel / LoadModel_Internal

- Address: (K1: 0x0061b380, TSL: 0x00669ea0)
- VTable entry: `CSWCCreature_LoadModel_vtable_entry` @  (/K1/k1_win_gog_swkotor.exe: 0x0074f670, TSL: 0x007c8040)
- Signatures:
  - K1: `undefined4 __thiscall CSWCCreature::LoadModel(CSWCCreature *this, undefined4 *param_1, undefined4 param_2, char param_3)`
  - TSL: `undefined4 __thiscall CSWCCreature::LoadModel_Internal(int param_1, undefined4 *param_2, undefined4 param_3, char param_4)`
- Structure:
  - K1 keeps the logic inline in `CSWCCreature::LoadModel`.
  - TSL splits the logic into a wrapper at `0x0066a0f0` and the main implementation at `0x00669ea0`.
- High-level execution flow:
  1. Set up exception handling and recover any cached `anim_base` state.
  2. Reuse the current `anim_base` when its type already matches the requested loader mode.
  3. Otherwise destroy the current anim base and allocate a replacement based on the requested type.
  4. Initialize animation tuning values through `CSWAnimBase::Set()`.
  5. Invoke the anim-base virtual load method to read the model resource.
  6. On failure, format `"CSWCCreature::LoadModel(): Failed to load creature model '%s'."` and return `0`.
  7. For special attachment values (`-1`, `-2`, `-3`, `-4`), query the attachment object and perform attachment setup.
  8. Register callbacks, enable animation state, and apply size-class-dependent animation settings.
  9. Return `1` on success and `0` on failure.
- Anim-base allocation cases:
  - `0`: standard anim base via `CSWCAnimBase::CSWCAnimBase()` @  (/K1/k1_win_gog_swkotor.exe: 0x0069dfb0, TSL: 0x006f8340)
  - `1`: head anim base via `CSWCAnimBaseHead::CSWCAnimBaseHead()` @  (/K1/k1_win_gog_swkotor.exe: 0x0069bb80, TSL: 0x006f5e60)
  - `2`: wield anim base via `CSWCAnimBaseWield::CSWCAnimBaseWield()` @  (/K1/k1_win_gog_swkotor.exe: 0x00699dd0, TSL: 0x006f41b0)
  - `3`: head+wield anim base via `CSWCAnimBaseHeadWield::CSWCAnimBaseHeadWield()` @  (/K1/k1_win_gog_swkotor.exe: 0x00698ec0, TSL: 0x006f32a0)
  - `0x0b`: TSL-only two-weapon anim base via `CSWCAnimBaseTW::CSWCAnimBaseTW()` @  (/K1/k1_win_gog_swkotor.exe: 0x0069cbd0, TSL: 0x006f6fb0)
- Special-case handling:
  - `param_3 == -1` triggers the `headconjure` path.
  - That path calls `RegisterCallbacks_Headconjure()` @  (/K1/k1_win_gog_swkotor.exe: 0x0061ab40, TSL: 0x00669570), looks up the `headconjure` dummy node, and derives a fallback/default vertical placement value when the dummy is missing.
  - Both games use callback registration, but TSL adds a cached callback path and uses `SetCallbackTarget()` @ (K1: N/A, TSL: 0x005056f0) instead of K1's direct registration flow.
- Size-class interpolation:
  - TSL adds interpolation logic driven by `FloatConstant_0_0125`, `FloatConstant_0_65`, `FloatConstant_0_05`, and `FloatConstant_0_01`.
  - `FloatConstant_1_0` remains part of the same interpolation path.
- Major K1 vs TSL differences:
  - TSL adds the two-weapon case `0x0b`.
  - TSL anim-base allocations are consistently 12 bytes larger for the shared variants.
  - TSL shifts several member offsets, including cached anim-base state and callback cache fields.
  - TSL changes several vtable offsets used later in the load sequence, including dummy lookup, size-setting, and animation-enable methods.
  - TSL introduces callback caching at `param_1 + 0xf8` and cached field state at `param_1 + 0x370` / `param_1 + 0x374`.
  - TSL adds explicit size-class interpolation work not present in K1.
- Notable helper functions and callees:
  - `operator_new()` @  (/K1/k1_win_gog_swkotor.exe: 0x006fa7e6, TSL: 0x0076d9f6)
  - `CSWAnimBase::Set()` @  (/K1/k1_win_gog_swkotor.exe: 0x00698e30, TSL: 0x006f3210)
  - `RegisterCallbacks()` @  (/K1/k1_win_gog_swkotor.exe: 0x0061ab40, TSL: 0x00693fe0)
  - `CResRef::CopyToString()` @  (/K1/k1_win_gog_swkotor.exe: 0x00405f70, TSL: 0x00406050)
  - `CResRef::GetResRefStr()` @  (/K1/k1_win_gog_swkotor.exe: 0x00405fe0, TSL: N/A)
  - `sprintf()` @  (/K1/k1_win_gog_swkotor.exe: 0x006fadb0, TSL: 0x0076dac2)
- Important string and data references:
  - Error string @  (/K1/k1_win_gog_swkotor.exe: 0x0074f85c, TSL: 0x007c82fc): `CSWCCreature::LoadModel(): Failed to load creature model '%s'.`
  - `headconjure` @ (K1: inline at 0x0061b676, TSL: 0x007c82f0)
  - `_head_hit` @  (/K1/k1_win_gog_swkotor.exe: 0x00753918, TSL: 0x007ccaf8)
  - `snd_Footstep` @  (/K1/k1_win_gog_swkotor.exe: 0x0074f838, TSL: 0x007c82d0)
  - `snd_hitground` @  (/K1/k1_win_gog_swkotor.exe: 0x0074f824, TSL: 0x007c82bc)
  - `GameObjectType_Constant_5` @  (/K1/k1_win_gog_swkotor.exe: 0x00746634, TSL: 0x007beaec)
  - `FloatConstant_0_125` @  (/K1/k1_win_gog_swkotor.exe: 0x0073f400, TSL: 0x007b7428)
  - `FloatConstant_0_0125` @ (K1: inline `0x3c888889`, TSL: 0x007c82ec)
  - `FloatConstant_1_0` @ (K1: inline `0x3f800000`, TSL: 0x007b5774)
  - `FloatConstant_0_65` @ (K1: inline `0x3d266666`, TSL: 0x007c82e8)
  - `FloatConstant_0_05` @ (K1: inline `0x3d4ccccd`, TSL: 0x007b9700)
  - `FloatConstant_0_01` @ (K1: inline `0x3c23d70a`, TSL: 0x007b5f88)
  - `SizeClassConstant_5` @ (K1: N/A, TSL: 0x007c514c)

##### CSWCPlaceable::LoadModel

- Address: (K1: 0x006823f0, TSL: 0x006d9721)
- Signature: `undefined4 __thiscall CSWCPlaceable::LoadModel(CSWCPlaceable *this, CResRef *param_1, byte param_2, byte param_3)`
- High-level behavior:
  - Allocates a `CSWCAnimBasePlaceable` if the placeable does not yet have an anim base.
  - Calls the virtual model-load method on the anim base.
  - On success, fetches an attachment, applies attachment and object-type setup, extracts the model name, and constructs a `"_head_hit"` suffix string.
  - Returns `1` on success and `0` on load failure.
- Representative callees:
  - `operator_new()`
  - `CResRef::CopyToString()` @  (/K1/k1_win_gog_swkotor.exe: 0x00405f70, TSL: 0x00406050)
  - `CSWCAnimBasePlaceable::CSWCAnimBasePlaceable()` @  (/K1/k1_win_gog_swkotor.exe: 0x006e4e50, TSL: 0x00755970)
  - `CExoString::SubString()` @  (/K1/k1_win_gog_swkotor.exe: 0x005e6270, TSL: 0x00631330)
  - `CExoString::operator+()` @  (/K1/k1_win_gog_swkotor.exe: 0x005e5d10, TSL: 0x00630dd0)

##### CSWCCreature::UnloadModel

- Address: (K1: 0x0060c8e0, TSL: N/A - likely inlined or reorganized)
- Signature: `void __thiscall CSWCCreature::UnloadModel(CSWCCreature *this)`
- Behavior:
  - Reads the current `anim_base`.
  - If non-null, calls the unload/cleanup virtual method and then the deleting destructor.
  - Clears the stored `anim_base` pointer.

**Resource management functions:**

- `CResMDL::CResMDL` @  (/K1/k1_win_gog_swkotor.exe: 0x005cea50, TSL: N/A)
  - Initializes the `CResMDL` vtable, calls the base `CRes::CRes()` constructor, clears state, and zeros the data pointer/size fields.
- `CResMDL::~CResMDL` @  (/K1/k1_win_gog_swkotor.exe: 0x005cea80, TSL: 0x00435200)
  - Restores the `CResMDL` vtable and then calls `CRes::~CRes()`.
- `CResMDL::~CResMDL` deleting destructor @  (/K1/k1_win_gog_swkotor.exe: 0x005cea90, TSL: 0x00447740)
  - Calls the non-deleting destructor and conditionally frees the object when the delete flag is set.

**Error messages:**

- `CSWCCreature::LoadModel(): Failed to load creature model '%s'.`
  - Address: (K1: 0x0074f85c, TSL: 0x007c82fc)
  - Used by the creature loader failure path and its TSL wrapper/error helper.
- `Model %s nor the default model %s could be loaded.`
  - Address: (K1: 0x00751c70, TSL: 0x007cad14)
  - Generic fallback model-load failure string.

**String references:**

- `.mdl` @  (/K1/k1_win_gog_swkotor.exe: 0x00740ca8, TSL: 0x007b8d28)
  - Referenced by `Input::Read()` and `LoadAddInAnimations()` when constructing/opening model paths.

**References:**

- Based on `/K1/k1_win_gog_swkotor.exe` and `swkotor2.exe` MDL/MDX I/O implementation.
- Addresses were verified through string cross-references, call-chain analysis, and decompilation.

### Save / Load System

The save/load path in both games follows a stable high-level sequence even though offsets and a few file details differ.

K1 save flow:

1. Initialize locals and exception state.
2. Check free disk space using the configured save-root alias.
3. Create the save directory; on failure, clean the directory and retry once.
4. Compare directory size constraints before continuing.
5. Build the final save path and notify the client that save/load is beginning.
6. Start the load-bar stall event.
7. Resolve the save alias path and decide whether the screenshot step should run.
8. Capture the save screenshot.
9. Persist the save-folder resources in fixed order.
10. Clear transient save/load state and return success or failure.

K1 load flow:

1. Set load-bar progress.
2. Apply the fixed sequence of load-bar steps (`10`, `20`, `23`, `23`, `23`).
3. Build the save path and temporarily add it as a resource directory.
4. Load table info, then core save data, then remove the resource directory.
5. Set the post-load flags and call `LoadModule()`.

TSL keeps the same broad structure but uses different internal offsets, stores additional save content such as `PIFO.ifo` and galaxy-map state, and resolves dialogs from the TSL-specific module layout noted above.

Confirmed save/load entry points from prior research:

- `DoSaveGameScreenShot` @ (K1: `0x00401080`, TSL: `0x0040e0f0`)
- `HasEnoughDiskSpaceForSaveGame` @ (K1: `0x004b2520`, TSL: `TODO`)
- `SaveGame` / internal save path @ (K1: `0x004b58a0`, TSL: `0x007b7980`)
- `LoadGame` / internal load path @ (K1: `0x004ba640`, TSL: `0x007b2f00`)
- `LoadModule` @ (K1: `0x004b95b0`, TSL: `0x007b4fd0`)

### Executable Startup and Initialization

The Windows entry point performs standard CRT setup plus a small amount of engine-specific environment preparation before control reaches `WinMain`.

- Entry addresses: K1 `entry(void)` @ `0x006fb38d`; TSL `entry(void)` @ `0x0076e2dd`.
- Structured exception handling is installed immediately.
- `GetVersionExA` fills the OS version structure, and the engine copies platform, major, minor, and build fields into globals.
- The build number keeps a high-bit marker for non-NT platforms after the lower 15 bits are masked.
- Major and minor versions are also packed into a combined value of the form `major * 0x100 + minor`.
- The PE header is inspected to determine whether the image should be treated like a DLL for exit behavior.
- Heap initialization, CRT startup, TLS/static initialization, and other runtime setup happen before the final handoff to the main game entry.

<a id="bwm-walkmesh-aabb-engine-implementation-analysis"></a>

## BWM / walkmesh / AABB (engine implementation analysis)

This document analyzes how the original *KOTOR* game engine (`/K1/k1_win_gog_swkotor.exe` / `/TSL/k2_win_gog_aspyr_swkotor2.exe`) handles *BWM* files, *AABB* trees, and walkmeshes. Those paths refer to **local or decompilation-derived sources** (not GitHub repositories); structure and line references in this doc are to that local/vendor copy.

### Overview

The game engine uses several key data structures and functions to manage walkmeshes for *collision detection*, *pathfinding*, and *spatial queries*.

---

### Key Data Structures

#### `CSWWalkMeshHeader`

The *[BWM](Level-Layout-Formats#bwm)* file header structure that the game reads directly from disk:

```c
struct CSWWalkMeshHeader {
    char magic[4];                  // "BWM "
    char version[4];                // "V1.0"
    int world_coords;               // 0=local, 1=world coordinates
    struct Vector relative_use_positions[2];
    struct Vector absolute_use_positions[2];
    struct Vector position;
    ulong vertex_count;
    ulong vertex_offset;
    ulong face_count;
    ulong face_offset;
    ulong materials_offset;
    ulong normals_offset;
    ulong distances_offset;
    ulong aabb_count;
    ulong aabb_offset;
    ulong aabb_root;               // Root node index for AABB tree
    ulong adjacency_count;
    ulong adjacency_offset;
    ulong edge_count;
    ulong edge_offset;
    ulong perimeter_count;
    ulong perimeter_offset;
};
```

**Key Findings:**

1. **`world_coords` field (Offset 0x08)**: The game explicitly checks this field to determine coordinate space
   - `0` = Local coordinates (*PWK/DWK*) - vertices transformed by object position/rotation at runtime
   - `1` = World coordinates (*WOK*) - vertices already in world space
   - Referenced in: `CSWCollisionMesh__LoadMeshBinary`, `CSWCollisionMesh__WorldToLocal`, `CSWCollisionMesh__LocalToWorld`

2. **`aabb_root` field (Offset 0x6C)**: Stores the root node index for AABB tree traversal
   - Used in: `CheckAABBNode` function calls
   - This confirms ***AABB* trees use 0-based array indexing**

3. **File structure**: Header is *exactly* **136 bytes (0x88)**, followed by data tables at specified offsets

#### `CSWRoomSurfaceMesh`

The runtime *mesh* structure that loads *BWM* data:

```c
struct CSWRoomSurfaceMesh {
    struct CSWCollisionMesh mesh;
    struct SurfaceMeshAdjacency *adjacencies;
    struct CExoArrayList__SurfaceMeshEdge edges;
    int edges_initialized_;
    struct CExoArrayList__uint perimeters;
    int perimeters_initialized_;
    struct CExoArrayList__SurfaceMeshAABB aabbs;
    int aabbs_initialized_;
    undefined4 field8_0xbc;
    undefined4 field9_0xc0;
    undefined4 field10_0xc4;
    undefined4 field11_0xc8;
    undefined4 field12_0xcc;
    undefined4 field13_0xd0;
    int aabb_root;                     // Root node index
    ulong los_material_mask;           // Line-of-sight material filter
    ulong walkable_material_mask;      // Walkability filter
    ulong walk_check_material_mask;    // Walk check filter
    ulong all_material_mask;           // All materials mask
};
```

**Key Findings:**

1. **Material Bitmasks**: The game uses bitmasks to filter faces by material type
   - `walkable_material_mask`: Determines which materials are walkable
   - `los_material_mask`: Determines which materials block line of sight
   - This is why material IDs matter - they're used as bit positions in masks

2. **Adjacency Storage**: *Adjacencies* are stored as a flat array indexed by `face_index * 3 + edge_index`

3. **AABB tree**: Stored as a dynamic array (`CExoArrayList__SurfaceMeshAABB`)
   - Tree is accessed via `aabb_root` index
   - Nodes reference children by *array index (0-based)*

#### `AABB_t` Node Structure

```c
struct AABB {
    Vector min_bounds_0x0;                  // Min bounds
    Vector max_bounds_0xc;                  // Max bounds
    struct AABB_t *right_child;         // Right child pointer
    struct AABB_t *left_child;          // Left child pointer
    undefined4 most_significant_plane_0x24;             // Most significant plane
};
```

**Key Findings:**

1. **Child pointers**: In the *binary* file, these are stored as 32-bit unsigned integers (indices)
2. **Node size**: Each *AABB* node is **44 (0x2C) bytes** on disk
3. **Traversal**: The game uses recursive traversal starting from `aabb_root` (root node index for AABB tree)

---

### Critical Functions

#### `CSWCollisionMesh__LoadMeshBinary`

Loads BWM data from file into runtime structures:

```c
iVar2 = CSWCollisionMesh__LoadMeshBinary(&this_->mesh,param_1);
if (iVar2 != 0) {
    // Load adjacencies
    pSVar3 = (SurfaceMeshAdjacency *)(param_1->data_pointer + *(int *)((int)param_1->data + 0x74));
    this_->adjacencies = pSVar3;
    
    // Load AABB root
    iVar2 = *(int *)((int)param_1->data + 0x6c);
    this_->aabb_root = iVar2;
    
    // Load edges
    iVar2 = *(int *)((int)pvVar1 + 0x78);
    pSVar4 = (SurfaceMeshEdge *)(param_1->data_pointer + *(int *)((int)pvVar1 + 0x7c));
    if ((this_->edges).size == 0) {
        // Initialize edges...
    }
}
```

**Key Findings:**

1. **Offset 108 (0x6C)**: `aabb_root` is read from file header
2. **Offset 116 (0x74)**: Adjacency offset
3. **Offset 120 (0x78)**: Edge count
4. **Offset 124 (0x7C)**: Edge offset

This confirms our [BWM](Level-Layout-Formats#bwm) documentation is correct!

#### `CheckAABBNode` / `HitCheckAABBnode`

Recursive *AABB* tree traversal for raycasting:

```c
ulong __cdecl HitCheckAABBnode(AABB_t *param_1, Vector *param_2, Vector *param_3, float param_4) {
    // ... Bounding box intersection test ...
    
    if ((param_1->field5_0x24 & AABBDirectionHeuristic) == 0) {
        // Traverse left child first
        local_80 = HitCheckAABBnode(pAVar4->left_child, param_2, param_3, param_4);
        pAVar4 = pAVar4->right_child;
    } else {
        // Traverse right child first (direction heuristic)
        local_80 = HitCheckAABBnode(pAVar4->left_child, param_2, param_3, param_4);
        pAVar4 = pAVar4->right_child;
    }
    
    uVar10 = HitCheckAABBnode(pAVar4, param_2, param_3, param_4);
    local_80 = local_80 + uVar10;
}
```

**Key Findings:**

1. **Direction heuristic**: The game uses `AABBDirectionHeuristic` to determine traversal order
   - This optimizes raycasting by testing closer children first
   - The `most_significant_plane_0x24` (most significant plane) stores the split axis

2. **Recursive traversal**: Both children are tested, not early-exit on first hit
   - This is why the function returns a count (`local_80 + uVar10`)
   - Multiple hits are accumulated

3. **Leaf node detection**: When `face_index != -1`, node is a leaf

#### `CSWCollisionMesh__WorldToLocal`

Converts world coordinates to local mesh coordinates:

```c
CSWCollisionMesh__WorldToLocal(&this_->mesh, &local_2c, param_1);
local_44.x = local_2c.x;
local_44.y = local_2c.y;
local_50.x = local_2c.x;
local_50.y = local_2c.y;
local_38.x = 0.0;
local_38.y = 0.0;
local_38.z = 0.0;
local_44.z = m1000_0;
local_50.z = -m1000_0;
```

**Key Findings:**

1. **Coordinate transformation**: The game transforms query points before AABB tree traversal
2. **Z-axis range**: Uses large Z values (±1000.0) for vertical ray casts
3. **Material filtering**: Material masks are applied BEFORE tree traversal (not during)

#### Writing BWM Files

The game writes BWM files in this exact order:

```c
header.aabb_count = (this_->aabbs).size;
header.aabb_offset = _ftell(_File);
header.aabb_root = this_->aabb_root;
_fwrite(this_->aabbs).data, 0x2c, header.aabb_count, _File);

header.adjacency_offset = _ftell(_File);
_fwrite(this_->adjacencies, 4, header.adjacency_count * 3, _File);

header.edge_count = (this_->edges).size;
header.edge_offset = _ftell(_File);
_fwrite(this_->edges).data, 8, header.edge_count, _File);

header.perimeter_count = (this_->perimeters).size;
header.perimeter_offset = _ftell(_File);
_fwrite(this_->perimeters).data, 4, header.perimeter_count, _File);
```

**Key Findings:**

1. **AABB node size**: `0x2c` (44 bytes) per node
2. **Adjacency size**: 4 bytes × (adjacency_count * 3) - confirms `face_count * 3` encoding
3. **Edge size**: 8 bytes per edge (4 bytes edge_index, 4 bytes transition)
4. **Perimeter size**: 4 bytes per perimeter marker (1-based loop end index)
5. **Order matters**: Data is written in the exact order listed above

---

### Coordinate Spaces and Transformations

#### WOK Files (Area Walkmeshes)

**Coordinate mode**: `world_coords = 1`

- Vertices are stored in **world space**
- Room position in LYT file translates the entire room
- BWM vertices are NOT translated - they're already world-positioned
- **Critical**: ModuleKit does NOT apply LYT translation to WOK vertices

**Example from m01aa (Endar Spire):**

```
LYT: m01aa_room0 at (0.0, 0.0, 0.0)
WOK: m01aa_room0.wok vertices already in world coordinates
     Vertex (10.5, 20.3, 0.0) = world position (10.5, 20.3, 0.0)
```

#### PWK/DWK Files (Placeable/Door Walkmeshes)

**Coordinate mode**: `world_coords = 0`

- Vertices are stored in **local/object space**
- Engine applies transformation matrix at runtime:
  - Translation: Object's position in the area
  - Rotation: Object's orientation
  - Scale: Object's scale (usually 1.0)

**Example:**

```
PWK: container001.pwk vertices in local space
     Vertex (0.5, 0.5, 0.0) = local position
     
When placed at (100.0, 200.0, 0.0) with 0° rotation:
     World position = (100.5, 200.5, 0.0)
```

**Game engine transformation sequence:**

1. Read `world_coords` from [BWM](Level-Layout-Formats#bwm) header (offset 0x08)
2. If `world_coords == 0`:
   - Call `CSWCollisionMesh__LocalToWorld` to transform vertices
   - Apply placeable/door transformation matrix
3. If `world_coords == 1`:
   - Use vertices as-is (already world-space)

---

### *AABB* Tree Implementation Details

#### Child Index Encoding

**Format**: 32-bit unsigned integer (`uint32`)

**Encoding**: **0-based array index**

- First node: index 0
- Second node: index 1
- Nth node: index N-1
- No child: `0xFFFFFFFF` (-1 when interpreted as signed)

**Proof from game engine:**

1. **Writing**:

   ```c
   _fwrite(this_->aabbs).data, 0x2c, header.aabb_count, _File);
   ```

   - Writes AABB array sequentially
   - No index transformation applied

2. **Reading**:

   ```c
   iVar2 = *(int *)((int)param_1->data + 0x6c);
   this_->aabb_root = iVar2;
   ```

   - Reads root index directly from file
   - No offset adjustment

3. **Traversal**:

   ```c
   HitCheckAABBnode(pAVar4->left_child, ...);
   HitCheckAABBnode(pAVar4->right_child, ...);
   ```

   - Uses pointers directly (resolved from indices at load time)
   - No arithmetic on indices during traversal

**This definitively confirms**: AABB child indices are **0-based array positions**, not byte offsets or 1-based indices.

#### Most Significant Plane Values

From `CheckAABBNode` / `HitCheckAABBnode` analysis:

- `0x00` (0): No split (leaf node)
- `0x01` (1): Split on positive X axis
- `0x02` (2): Split on positive Y axis
- `0x03` (3): Split on positive Z axis
- `0xFFFFFFFE` (-2): Split on negative X axis
- `0xFFFFFFFD` (-3): Split on negative Y axis
- `0xFFFFFFFC` (-4): Split on negative Z axis

**Usage:**

The `AABBDirectionHeuristic` checks this field to determine traversal order:

```c
if ((param_1->field5_0x24 & AABBDirectionHeuristic) == 0) {
    // Standard traversal order
} else {
    // Reverse traversal (direction heuristic optimization)
}
```

This optimizes raycasting by testing closer children first based on ray direction.

---

### Material Handling

#### Material IDs and Masks

The game uses **bitmask filtering** for materials:

```c
struct CSWRoomSurfaceMesh {
    ...
    ulong walkable_material_mask;      // Bitmask for walkable materials
    ulong los_material_mask;           // Bitmask for LOS-blocking materials
    ulong walk_check_material_mask;    // Bitmask for walk checks
    ulong all_material_mask;           // All materials
};
```

**Encoding**: `mask |= (1 << material_id)`

**Example:**

```
SurfaceMaterial.DIRT = 1
Mask bit = (1 << 1) = 0x00000002

SurfaceMaterial.GRASS = 3
Mask bit = (1 << 3) = 0x00000008

Combined mask for DIRT + GRASS = 0x0000000A
```

**Usage in spatial queries:**

```c
if ((material_mask & (1 << face_material)) != 0) {
    // Face passes material filter
}
```

This is why material IDs must be consistent - they're used as bit positions!

#### Walkable vs. Non-Walkable Materials

From `CSWRoomSurfaceMesh__GetSurfaceMaterialWalkCheckOnly`:

```c
// Get the surface material ID for walk check only, for the mesh at mesh_ptr and vertex vertex_index
int surface_material_id = CSWRoomSurfaceMesh__GetSurfaceMaterialWalkCheckOnly(
    *(CSWRoomSurfaceMesh **)(mesh_ptr + 0x3c), vertex_index
);

// Prepare string to look for "Walk" column in 2DA
CExoString walk_column_name;
CExoString__CExoString(&walk_column_name, "Walk");

// Query the value from the surfacemat 2DA table: 
// Parameters: (2da_table, row_index, column_name_str, output_int_ptr)
int is_walkable = 0;
C2DA__GetINTEntry(Rules->internal->all_2DAs->surfacemat, surface_material_id, &walk_column_name, &is_walkable);
```


The game reads *walkability* from `surfacemat.2da` at runtime!

**Key Insight**: *Material walkability* is **NOT** hardcoded - it's *data-driven* via [2DA files](2DA-File-Format).

---

### *Adjacency* Encoding

#### *Storage* Format

*Adjacencies* are stored as a flat `int32` array:

- **Size**: `walkable_face_count * 3` entries
- **Indexing**: `adjacency[face_idx * 3 + edge_idx]`
- **Encoding**: `adjacent_face_idx * 3 + adjacent_edge_idx`
- **No neighbor**: `-1` (0xFFFFFFFF)

**Proof from game engine:**

```c
_fwrite(this_->adjacencies, 4, header.adjacency_count * 3, _File);
```

- 4 bytes per entry (int32)
- `adjacency_count * 3` Total Entries
- `adjacency_count` = Number of Walkable Faces

#### Decoding Formula

Given *adjacency* value `adj`:

```c
face_index = adj / 3;
edge_index = adj % 3;
```

**Example:**

```
adj = 38
face_index = 38 / 3 = 12
edge_index = 38 % 3 = 2

This means: *edge* connects to *face 12*, *edge 2*
```

#### Bidirectional Requirement

If ***face A*** *edge 0* connects to ***face B*** *edge 2*:

- `adjacencies[A * 3 + 0] = B * 3 + 2`
- `adjacencies[B * 3 + 2] = A * 3 + 0`

The game **requires** bidirectional linking for pathfinding!

---

### Edge and Perimeter Handling

#### Edge Format

Each *edge* is **8 bytes**:

```c
struct SurfaceMeshEdge {
    ulong index;        // Encoded: face_index * 3 + local_edge_index
    int transition;     // Transition ID or -1
};
```

**Proof:**

```c
_fwrite(this_->edges).data, 8, header.edge_count, _File);
```

#### *Perimeter* Format

*Perimeters* are **1-based loop end indices**:

```c
_fwrite(this_->perimeters).data, 4, header.perimeter_count, _File);
```

**Format**: Array of `uint32` values

**Interpretation**:

- `perimeters[0] = N`: *Loop 1* contains *edges 0 to N-1*
- `perimeters[1] = M`: *Loop 2* contains *edges N to M-1*
- etc.

**Example:**

```
perimeters = [59, 66, 73]

*Loop 1*: *edges 0-58*   (59 edges)
*Loop 2*: *edges 59-65*  (7 edges)
*Loop 3*: *edges 66-72*  (7 edges)
```

---

### Implementation Recommendations

Based on this analysis, our *PyKotor/HolocronToolset* implementation **MUST**:

1. **Coordinate spaces**:
   - *WOK* files: Write `world_coords = 1`, store vertices in world space
   - *PWK/DWK* files: Write `world_coords = 0`, store vertices in local space
   - *ModuleKit*: Do ***NOT*** translate *[WOK](Level-Layout-Formats#bwm)* vertices when building composite modules

2. **AABB trees**:
   - Use **0-based array indexing** for child node references
   - Write `aabb_root` as array index (**NOT** byte offset)
   - Ensure tree is balanced for optimal query performance
   - Write 44 bytes per node

3. **Materials**:
   - Preserve material IDs exactly (they're used as bitmask positions)
   - Do ***NOT*** remap materials during transformations
   - Validate materials are in range [0, 22]

4. **Adjacencies**:
   - Encode as `face_index * 3 + edge_index`
   - Ensure bidirectional linking
   - Write 12 (0x0C) bytes per walkable face (3 edges × 4 bytes)

5. **Edges and perimeters**:
   - Write 8 (0x08) bytes per edge (edge_index, transition)
   - Write 1-based perimeter loop end indices
   - Ensure perimeter loops are closed

6. **File structure**:
   - Write header (136 (0x88) bytes)
   - Write data tables in exact order: *vertices*, *faces*, *materials*, *normals*, *distances*, *AABBs*, *adjacencies*, *edges*, *perimeters*
   - Update header offsets **correctly**

---

### References

- *`swkotor.c`* / *`swkotor.h`* — Decompiled engine source/headers used alongside local RE work (not part of the PyKotor distribution)
- [Level-Layout-Formats#bwm](Level-Layout-Formats#bwm) — **Format specification** (binary layout, header, vertices, faces, AABB, adjacency, edges, perimeters). This section covers engine-side behavior only; the BWM wiki is the canonical format reference.

## Using agdec for further analysis

To extend these findings or verify behavior against a specific binary:

1. **Open a game binary in Ghidra:** Load `/K1/k1_win_gog_swkotor.exe`, `/TSL/k2_win_gog_aspyr_swkotor2.exe` into a Ghidra project. Ensure the program is **loaded and analyzed** (e.g. Auto Analysis complete); agdec tools require an open program to query.
2. **Use the agdec MCP server:** With the binary loaded, tools such as `list-functions`, `search-strings`, `list-exports`, and `list-cross-references` can map entry points, locate format-related strings (e.g. "KEY ", "GFF ", "NCS "), and trace call graphs. This is useful for confirming which functions read KEY/BIF, parse GFF or 2DA, or execute NCS.
3. **Match findings to format docs:** Cross-reference addresses and function names with vendor implementations (e.g. reone, xoreos) and with this wiki’s format pages. Document engine-specific quirks (e.g. alignment, field order) in the relevant format page; for geometry/walkmesh, align with [BWM / walkmesh / AABB](reverse_engineering_findings#bwm-walkmesh-aabb-engine-implementation-analysis) and [Level-Layout-Formats#bwm](Level-Layout-Formats#bwm).
4. **Community and archives:** For historical RE notes and tool discussions, see [Community sources and archives](Home#community-sources-and-archives) (DeadlyStream, LucasForums archives). Wiki content stays conceptual; do not paste raw RE dumps or tool names into format pages—link to this document (especially [Resource Management System](reverse_engineering_findings#resource-management-system)) for engine-level detail.

## Tools Used

- **RE / agdec:** Ghidra integration for reverse engineering (list-functions, search-strings, list-exports, list-cross-references)
- **Ghidra:** Binary analysis and decompilation
- **Function Analysis:** Cross-referencing and call graph analysis

## See Also

- [Level-Layout-Formats#bwm](Level-Layout-Formats#bwm) -- BWM binary layout (canonical format); [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide), [Kit-Structure-Documentation](Kit-Structure-Documentation) -- Walkmesh extraction
- [Container-Formats#key](Container-Formats#key), [Container-Formats#bif](Container-Formats#bif), [Container-Formats#erf](Container-Formats#erf) -- Containers and resolution with KEY/BIF
- [NCS-File-Format](NCS-File-Format), [NSS-File-Format](NSS-File-Format) -- Script execution; [MDL-MDX-File-Format](MDL-MDX-File-Format) -- Model loading
- [GFF-File-Format](GFF-File-Format), [2DA-File-Format](2DA-File-Format) -- Engine data formats
- [Concepts](Concepts) -- Resource resolution, ResRef, override folder
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, LucasForums for RE and tool history

## References

- Original game executables: `/K1/k1_win_gog_swkotor.exe`, `/TSL/k2_win_gog_aspyr_swkotor2.exe`
- Analysis conducted using RE tools in Ghidra
- Findings validated against PyKotor library implementation
