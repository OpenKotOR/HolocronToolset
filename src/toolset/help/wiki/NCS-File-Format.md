# NCS — Compiled Script Bytecode

NCS files contain compiled NWScript bytecode — the executable form of the scripting language that drives game logic in Knights of the Old Republic and The Sith Lords ([`NCS` L254](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_data.py#L254), [xoreos `ncsfile.cpp`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp)). Scripts control dialogue branching, trigger responses, combat behavior, cutscene sequencing, and virtually every dynamic system in the game. The bytecode runs inside a stack-based virtual machine inherited from the Aurora engine ([`NCSInstruction` L637](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_data.py#L637), [reone `ncsreader.cpp` L28](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp#L28), [KotOR.js `NWScriptInstance.ts` L32](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptInstance.ts#L32)), where the "server" context (game world simulation) executes scripts and the client handles display and input.

The format is shared across Aurora engine games (Neverwinter Nights, Jade Empire, etc.), though KotOR adds game-specific action routines ([`NCSBinaryReader.load` L56](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/io_ncs.py#L56), [xoreos-tools `ncsfile.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/ncsfile.cpp), [NorthernLights `NCSReader.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/NCSReader.cs), [Kotor.NET `NCS.cs` L9](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9)). The sections below focus on KotOR-specific behavior. Scripts are compiled from [NSS](NSS-File-Format) source code and triggered by script hooks on [GFF](GFF-File-Format) resources — [DLG](GFF-Creature-and-Dialogue#dlg) dialogue files, [GIT](GFF-File-Format#git-game-instance-template) area instances, [UTC](GFF-File-Format#utc-creature) creatures, [UTD](GFF-Spatial-Objects#utd) doors, [UTP](GFF-Spatial-Objects#utp) placeables, and [IFO](GFF-Module-and-Area#ifo) module definitions. Like all resources, NCS files are resolved through the standard [resource resolution order](Concepts#resource-resolution-order) (override → MOD/SAV → KEY/BIF).

## File Structure Overview

| Offset | Size | Description |
| ------ | ---- | ----------- |
| 0 (0x00)   | 4    | Signature `"NCS "` |
| 4 (0x04)   | 4    | Version `"V1.0"` |
| 8 (0x08)   | 1    | Program size marker opcode (`0x42`) |
| 9 (0x09)   | 4    | Total file size ([big-endian](https://en.wikipedia.org/wiki/Endianness) UInt32) |
| 13 (0x0D)+  | --    | Stream of bytecode instructions |

- The *VM* executes sequential instructions; control-flow opcodes (`JMP`, `JZ`, `JSR`) adjust the instruction pointer.  
- *KotOR* introduces no custom container sections--scripts are a flat stream.  
All major reverse-engineered engines decode the same structure: [reone](https://github.com/seedhartha/reone), [xoreos](https://github.com/xoreos/xoreos), and [NorthernLights](https://github.com/lachjames/NorthernLights), among others catalogued on [Home](Home#cross-reference-other-tools-and-engines). KotOR.js runs bytecode through its own NWScript stack machine via [`NWScriptInstance.ts` L32+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptInstance.ts#L32) and [`NWScriptStack.ts` L31+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptStack.ts#L31), with per-opcode byte layout matching native VMs.
- The program size marker at offset 8 (`0x42`) is not a real instruction but a metadata field containing the total file size. Execution begins at offset 13 (*0x0D*) after the header; the complete instruction set is specified in the Torlack NWScript spec ([xoreos-docs `specs/torlack/ncs.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/ncs.html)) and is independently verified by PyKotor ([`NCSBinaryReader.load` L56+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/io_ncs.py#L56)), [xoreos `ncsfile.cpp` L342–L350](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L342-L350), [xoreos-tools `ncsfile.cpp` L116–L125](https://github.com/xoreos/xoreos-tools/blob/9ecd99facb6f3f9a1d4d96c5584add96a5f61800/src/nwscript/ncsfile.cpp#L116-L125), [reone `ncsreader.cpp` L28–L40](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp#L28-L40), and [Kotor.NET `NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9).

### Stack-Based Virtual Machine

NWScript uses a [stack-based VM](https://en.wikipedia.org/wiki/Stack_machine) where all operations work on a *stack* rather than CPU registers. Stack grows downward with negative offsets, 4-[byte](https://en.wikipedia.org/wiki/Byte) aligned elements.

**Stack Pointer (SP):** `SP = (stackPtr + 1) * -4`. Stack positions are negative multiples of 4 (e.g., *-4*, *-8*, *-12*).

**Stack Layout Example:**

```mermaid
graph TD
    SP[SP (top)] --> S1["-4: j: 1"]
    S1 --> S2["-8: i: 12"]
    S2 --> S3["-12: (previous frame)"]
```

/*

- `SP` points to the topmost value on the stack.
- Stack grows downward (from higher to lower negatives).
- Each node shows the stack offset, variable name, and value.
*/

**Stack Position Calculations:**

- [Byte](https://en.wikipedia.org/wiki/Byte) offset to position: `-offset / 4` (e.g., *-12* --> position 3)
- [Byte](https://en.wikipedia.org/wiki/Byte) size to elements: `size / 4` (e.g., *12 bytes* --> 3 elements)

**Global Variables:** Accessed via base pointer (*BP*). The `#globals` routine initializes globals before `main()`, then `SAVEBP` saves current SP as BP. Functions access globals via `CPTOPBP`/`CPDOWNBP`. `RESTOREBP` restores previous BP.

**Stack Entry Types:**

- **Constants**: Immutable values (`CONSTx`) read from instructions -- *int*, [*float*](GFF-File-Format#gff-data-types), *string*, *object*
- **Variables**: Assignable stack slots created via `RSADDx`, modified via `CPDOWNSP`/`CPDOWNBP`
- **structures**: Composite types spanning multiple positions (vectors = 3 positions/12 bytes, custom = 4-[*Byte*](https://en.wikipedia.org/wiki/Byte) multiples)

**Lifecycle:** Create (`CONSTx`, `RSADDx`, `CPTOPSP`) --> Modify (`CPDOWNSP`, `INCxSP`) --> Consume (operations, *MOVSP*) --> Destroy (`DESTRUCT`)

**Decompilation Tracking:**

- **Reference Counting**: Track variable usage per stack instance
- **Assignment Status**: Distinguish initialized vs uninitialized variables
- **type Inference**: Infer types through operation chains
- **structure Recognition**: 12-[*Byte*](https://en.wikipedia.org/wiki/Byte) copies --> vectors (z, y, x order), other multiples of 4 --> custom structures
- **Variable Naming**: Generate names from type + position or infer from usage patterns

- [xoreos](https://github.com/xoreos/xoreos) [`ncsfile.cpp` L105–L172](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L105-L172) (SP/BP)
- [xoreos](https://github.com/xoreos/xoreos) [L389–L394](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L389-L394) (globals)
- [xoreos](https://github.com/xoreos/xoreos) [L1039–L1060](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L1039-L1060) (SAVEBP/RESTOREBP)
- [reone](https://github.com/seedhartha/reone) [`ncsreader.cpp` L52–L97](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp#L52-L97)
- [xoreos-tools](https://github.com/xoreos/xoreos-tools) [`ncsfile.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/ncsfile.cpp)
- [KotOR.js](https://github.com/KobaltBlu/KotOR.js) [`NWScriptInstance.ts` L32+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptInstance.ts#L32)
- [NorthernLights](https://github.com/lachjames/NorthernLights) [`NCSReader.cs` (`NCSFile`) L8+](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/Assets/Scripts/ncs/NCSReader.cs#L8)

---

## Header

| Name              | type    | offset | size | Description |
| ----------------- | ------- | ------ | ---- | ----------- |
| file type         | [*char*](GFF-File-Format#gff-data-types) | 0 (0x00)   | 4    | `"NCS "` (must match exactly, ASCII bytes: `0x4E 0x43 0x53 0x20`) |
| file Version      | [*char*](GFF-File-Format#gff-data-types) | 4 (0x04)   | 4    | `"V1.0"` (must match exactly, ASCII bytes: `0x56 0x31 0x2E 0x30`) |
| size Marker       | [*uint8*](GFF-File-Format#gff-data-types)   | 8 (0x08)   | 1    | Program size marker opcode (`0x42`) |
| Total file size   | *UInt32*  | 9 (0x09)   | 4    | Total file size in bytes ([big-endian](https://en.wikipedia.org/wiki/Endianness)) |

The header is 13 bytes total. The size marker (`0x42`) is not a real instruction but a metadata field. All implementations validate that this byte equals `0x42` before reading the size field. The actual instruction stream begins at offset 13 (0x0D).

**Header Validation:**

All implementations validate:

1. File Signature: `"NCS V1.0"` (bytes `[0x4E, 0x43, 0x53, 0x20, 0x56, 0x31, 0x2E, 0x30]`)
2. Size Marker at Offset 8: 66 (`0x42`) (*metadata*, not an instruction)
3. File Size ([big-endian](https://en.wikipedia.org/wiki/Endianness) *UInt32* at offset 9) ≤ actual file size
4. Seek on Offset 13 (0x0D) to begin parsing

**Reject file if any validation fails.**

- [`reone/src/libs/script/format/ncsreader.cpp:28-40`](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp#L28-L40) (header reading and validation)
- [`xoreos/src/aurora/nwscript/ncsfile.cpp:333-350`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L333-L350) (includes validation of 66 (`0x42`) marker)
- [`xoreos-tools/src/nwscript/ncsfile.cpp:106-125`](https://github.com/xoreos/xoreos-tools/blob/9ecd99facb6f3f9a1d4d96c5584add96a5f61800/src/nwscript/ncsfile.cpp#L106-L125) (header parsing utilities)
- [`NorthernLights/Assets/Scripts/ncs/NCSReader.cs:876-886`](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/Assets/Scripts/ncs/NCSReader.cs#L876-L886) (66 (`0x42`) marker handling)
- [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9) (header reading)
- [`Libraries/PyKotor/src/pykotor/resource/formats/ncs/io_ncs.py:62-93`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/io_ncs.py#L62-L93) (NCS instruction definitions)

---

## Instruction Encoding

Every *Instruction* is stored as:

```plaintext
<Bytecode: *uint8*> <Qualifier: *uint8*> <Arguments: *variable*>
```

PyKotor reuses the NWScript *Opcode* table; each *Opcode* accepts a specific *Qualifier*/*Argument* layout described below.

### Bytecode

*Bytecode* selects the fundamental *Instruction* (stack manipulation, arithmetic, logic, control flow, etc.). KotOR supports the standard NWN *Opcodes* plus Bioware extensions such as `STORE_STATE`. See [`Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_data.py:70-142`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_data.py#L70-L142).

### Qualifier

`Qualifier` refines the *Instruction* to specific `Operand` types (e.g., `IntInt`, `FloatFloat`, `VectorVector`).  
Example: `ADDxx` with `Qualifier` `IntInt` performs integer addition, while the same `Opcode` with `Qualifier` `FloatFloat` adds floats.

**Qualifier Type values:**

**Unary Types (Single Operand):**

- `0x03` - *Integer* (*I*) - 4 bytes
- `0x04` - *Float* (*F*) - 4 bytes
- `0x05` - *String* (*S*) - 4 bytes (pointer to string data)
- `0x06` - *Object* (*O*) - 4 bytes (object ID)
- `0x10` - *Effect* (*E*) - 4 bytes
- `0x11` - *Event* (*V*) - 4 bytes
- `0x12` - *Location* (*L*) - 4 bytes
- `0x13` - *Talent* (*T*) - 4 bytes
- `0x10-0x1F` - *Engine Types* (*ET*s) (Reserved range for game-specific types)

**Binary Types (Two Operands):**

- `0x20` - *Integer*, *Integer* (*II*) - 4 bytes each
- `0x21` - *Float*, *Float* (*FF*) - 4 bytes each
- `0x22` - *Object*, *Object* (*OO*) - 4 bytes each
- `0x23` - *String*, *String* (*SS*) - 4 bytes each (pointers)
- `0x24` - *Structure*, *Structure* (*TT*) - variable size (must be multiple of 4)
- `0x25` - *Integer*, *Float* (*IF*) - 4 bytes each
- `0x26` - *Float*, *Integer* (*FI*) - 4 bytes each
- `0x30` - *Effect*, *Effect* (*EE*) - 4 bytes each
- `0x31` - *Event*, *Event* (*VE*) - 4 bytes each
- `0x32` - *Location*, *Location* (*LE*) - 4 bytes each
- `0x33` - *Talent*, *Talent* (*TE*) - 4 bytes each
- `0x30-0x39` - *Engine type pairs* (*ET* pairs) (reserved range)
- `0x3A` - *Vector*, *Vector* (*VV*) - 12 bytes each (3 floats: x, y, z)
- `0x3B` - *Vector*, *Float* (*VF*) - 12 bytes + 4 bytes
- `0x3C` - *Float*, *Vector* (*FV*) - 4 bytes + 12 bytes

**Special type values:**

- `0x00` - *Void* (*V*) (no type, used for return types)
- `0x01` - *Stack* (*S*) (internal type marker)

**type size Information:**

- All primitive types (int, float, string pointer, object ID, engine types) are 4 bytes
- *Vectors* are 12 bytes (3 consecutive floats)
- *Structures* have variable size but must be 4-[*byte*](https://en.wikipedia.org/wiki/Byte) aligned
- The *TT* (structure) qualifier type is used for comparing ranges of elements on the stack, specifically for structures and vectors. When used with `EQUALTT` or `NEQUALTT`, it requires a 2-[*byte*](https://en.wikipedia.org/wiki/Byte) size field indicating how many bytes to compare (must be a multiple of 4).

**type System Details:**

The qualifier [*byte*](https://en.wikipedia.org/wiki/Byte) system allows the same *opcode* to operate on different data types. *Type* qualifiers are organized into ranges:

- *Unary* Types (`0x03-0x1F`): Single operand types
- *Binary* Types (`0x20-0x3C`): Two operand type combinations
- *Special* Types (`0x00`, `0x01`): Void and internal stack marker

*Vectors* types are special: they occupy 3 stack positions (12 bytes) but are treated as a single composite type. When operations involve *vectors*, all three [*float*](GFF-File-Format#gff-data-types) components are processed together.

**Reference:**

- [`reone/src/libs/script/format/ncsreader.cpp:42-190`](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp#L42-L190)
- [`xoreos/src/aurora/nwscript/ncsfile.h:131-177`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.h#L131-L177)
- [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9)
- [`NorthernLights/Assets/Scripts/ncs/NCSReader.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/NCSReader.cs)
- [`NWScriptInstruction.ts` L79+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptInstruction.ts#L79)

### Arguments

Instruction arguments follow the qualifier [*byte*](https://en.wikipedia.org/wiki/Byte) and vary by *instruction* type. All multi-[*byte*](https://en.wikipedia.org/wiki/Byte) values are stored in [**big-endian**](https://en.wikipedia.org/wiki/Endianness) [*byte*](https://en.wikipedia.org/wiki/Byte) order.

**Argument format Patterns:**

1. **No Arguments** (2 bytes total: opcode + qualifier):
   - `RSADDx`, `LOGANDII`, `LOGORII`, `INCORII`, `EXCORII`, `BOOLANDII`, `EQUALxx` (non-*structure*), `NEQUALxx` (non-*structure*), `GEQxx`, `GTxx`, `LTxx`, `LEQxx`, `SHLEFTII`, `SHRIGHTII`, `USHRIGHTII`, `ADDxx`, `SUBxx`, `MULxx`, `DIVxx`, `MODII`, `NEGx`, `COMPI`, `RETN`, `NOTI`, `SAVEBP`, `RESTOREBP`, `NOP`

2. **Signed 32-bit Integer** (6 bytes total: opcode + qualifier + 4 bytes):
   - `MOVSP`: *Stack pointer* adjustment offset (signed, allows positive and negative adjustments)
   - `JMP`, `JSR`, `JZ`, `JNZ`: Relative jump offset (signed, from start of *instruction*, allows forward and backward jumps)
   - `INCxSP`, `DECxSP`, `INCxBP`, `DECxBP`: *Stack*/base pointer offset (signed, negative offsets access stack elements)
   - `CONSTO`: *Object ID* constant (signed 32-bit: `0x00000000` = OBJECT_SELF, `0x00000001` or `0xFFFFFFFF` = OBJECT_INVALID)

3. **Unsigned 32-bit Integer** (6 bytes total: opcode + qualifier + 4 bytes):
   - `CONSTI`: *Integer* constant (stored as unsigned 32-bit [big-endian](https://en.wikipedia.org/wiki/Endianness), but may represent signed integer values in the range -2³¹ to 2³¹-1)

4. **Signed 32-bit Integer Pair** (10 bytes total: opcode + qualifier + 4 bytes + 4 bytes):
   - `STORE_STATE`: Two signed 32-bit size fields (total 10 bytes: opcode + qualifier + [*int32*](GFF-File-Format#gff-data-types) size + [*int32*](GFF-File-Format#gff-data-types) sizeLocals). The first field (`size`) indicates the total number of bytes of stack state to store, and the second field (`sizeLocals`) indicates the number of bytes of local variables to preserve.

5. **32-bit float** (6 bytes total):
   - `CONSTF`: *Float* constant ([IEEE 754](https://en.wikipedia.org/wiki/IEEE_754) [big-endian](https://en.wikipedia.org/wiki/Endianness))

6. **string** (variable length: 2 bytes length + string data):
   - `CONSTS`: 2-byte length prefix ([big-endian](https://en.wikipedia.org/wiki/Endianness) [*uint16*](GFF-File-Format#gff-data-types)) followed by string bytes (ASCII)

7. **Stack Copy Operations** (8 bytes total: opcode + qualifier + 4 bytes offset + 2 bytes size):
   - `CPDOWNSP`, `CPTOPSP`, `CPDOWNBP`, `CPTOPBP`: Signed 32-bit *stack offset* + unsigned 16-bit size
   - Stack offset conversion: Negative [*byte*](https://en.wikipedia.org/wiki/Byte) offsets are converted to stack positions by dividing by 4 (e.g., offset -4 becomes position 1, offset -8 becomes position 2)
   - size field indicates number of bytes to copy (must be multiple of 4 for alignment)

8. **Engine Function Call** (5 bytes total: opcode + qualifier + 2 bytes routine + 1 [*byte*](https://en.wikipedia.org/wiki/Byte) arg count):
   - `ACTION`: Unsigned 16-bit routine number + unsigned 8-bit argument count
   - Routine number indexes into the engine's function table (actions data)
   - Argument count specifies how many stack elements (not bytes) to pass to the function

9. **Destruct Operation** (8 bytes total: opcode + qualifier + 2 bytes + 2 bytes + 2 bytes):
   - `DESTRUCT`: format: `[0x21][qualifier][uint16 size][signed16 stackOffset][uint16 sizeNoDestroy]`
     - `size`: Total number of bytes to destroy from *stack*
     - `stackOffset`: Signed 16-bit offset from *stack pointer* indicating where destruction begins (converted to position by dividing by 4)
     - `sizeNoDestroy`: Number of bytes to preserve (not destroyed) within the destruction range
     - Used for complex stack cleanup when removing multiple elements while preserving specific values (e.g., when unpacking structures or vectors)

10. **Struct Comparison** (4 bytes total: opcode + qualifier + 2 bytes):

- `EQUALTT`, `NEQUALTT`: format: `[0x0B/0x0C][0x24][uint16 size]`
  - `size`: Number of bytes to compare (must be multiple of 4, as structures are 4-[*byte*](https://en.wikipedia.org/wiki/Byte) aligned)
  - Compares two structures on the stack [*byte*](https://en.wikipedia.org/wiki/Byte)-by-[*byte*](https://en.wikipedia.org/wiki/Byte) for equality/inequality
  - Both structures must be the same size
  - Only used when qualifier is `0x24` (structure, structure)

**Jump offset Calculation:**
Jump offsets are **relative to the start of the jump instruction itself**, not the next instruction. The offset is a signed 32-bit *integer* allowing both forward and backward jumps.

**Byte Order:**

All multi-[*byte*](https://en.wikipedia.org/wiki/Byte) values in NCS files are stored in **[big-endian](https://en.wikipedia.org/wiki/Endianness)** ([network byte order](https://en.wikipedia.org/wiki/Endianness#Networking)):

- 16-bit values — most significant [*byte*](https://en.wikipedia.org/wiki/Byte) first:

  - [*uint16*](GFF-File-Format#gff-data-types)
  - [*int16*](GFF-File-Format#gff-data-types)

- 32-bit values — most significant [*byte*](https://en.wikipedia.org/wiki/Byte) first:

  - [*uint32*](GFF-File-Format#gff-data-types)
  - [*int32*](GFF-File-Format#gff-data-types)
  - [*float32*](GFF-File-Format#gff-data-types)
- This applies to: offsets, sizes, constants, jump targets, and all numeric arguments

**Instruction Parsing:**

Standard process: Read opcode + qualifier --> Determine argument format via lookup --> Read arguments (0 to variable bytes) --> Advance IP by total instruction size --> Repeat until EOF

**Variable-Length Instructions:**

- `CONSTx` (0x04): Qualifier determines type: Int (4B), Float (4B [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754)), String (2B length + data), Object (4B)
- `CPDOWNSP`/`CPTOPSP`/`CPDOWNBP`/`CPTOPBP` (0x01/0x03/0x26/0x27): 4B offset + 2B size
- `JMP`/`JSR`/`JZ`/`JNZ` (0x1D/0x1E/0x1F/0x25): 4B signed offset (relative to instruction start)
- `DESTRUCT` (0x21): 2B size + 2B stackOffset + 2B sizeNoDestroy
- `STORE_STATE` (0x2C): 4B size + 4B sizeLocals
- `ACTION` (0x05): 2B routine + 1B argCount
- `EQUALTT`/`NEQUALTT` with qualifier 0x24: 2B size (multiple of 4)

All multi-[*byte*](https://en.wikipedia.org/wiki/Byte) values: [big-endian](https://en.wikipedia.org/wiki/Endianness)

**Execution State:**

- **IP**: *Instruction pointer* (starts at 0x0D)
- **SP**: *Stack pointer* (top of data stack)
- **BP**: *Base pointer* (globals area, set by `SAVEBP`/`RESTOREBP`)
- **Return Stack**: *Separate stack* for `JSR`/`RETN` addresses

**Execution Loop:** Parse *instruction* --> Execute (manipulate stack/IP/BP, call functions) --> Advance IP --> Repeat until termination

**Instruction Sizes:** 2B base + arguments: None (2B), Int/float/Object (6B), String (2+N B), Jump (6B), *Stack copy* (8B), ACTION (5B), DESTRUCT (8B), STORE_STATE (10B), Struct compare (4B)

Static sizing enables: *instruction* list building, jump target resolution, code coverage, static analysis

**Reference:**

- [`xoreos/src/aurora/nwscript/ncsfile.cpp:194-1649`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L194-L1649)
- [`reone/src/libs/script/format/ncsreader.cpp:42-190`](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp#L42-L190)
- [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9)
- [`NorthernLights/Assets/Scripts/ncs/NCSReader.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/NCSReader.cs)
- [`xoreos-tools/src/nwscript/ncsfile.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/ncsfile.cpp)
- [`NWScriptInstance.ts` L32+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptInstance.ts#L32)
- [`xoreos/src/aurora/nwscript/ncsfile.h:86-280`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.h#L86-L280)

### Instruction Encoding Examples

#### Example 1: *Integer* Constant

```text
Bytes: [0x04][0x03][0x00][0x00][0x00][0x2A]
       └─┬─┘ └─┬─┘ └──────────┬──────────┘
      CONST  Int         42 ([big-endian](https://en.wikipedia.org/wiki/Endianness))
```

Pushes *integer* value 42 onto the stack.

#### Example 2: *String* Constant

```text
Bytes: [0x04][0x05][0x00][0x05][0x48][0x65][0x6C][0x6C][0x6F]
       └─┬─┘ └─┬─┘ └─┬─┘ └──────────────────────────┬──────────────────┘
      CONST  Str  length=5                    "Hello"
```

Pushes *string* "Hello" onto the stack.

#### Example 3: *Jump* Instruction

```text
Bytes: [0x1D][0x00][0x00][0x00][0x00][0x10]
       └─┬─┘ └─┬─┘ └──────────┬──────────┘
        JMP  qualifier    offset=16 bytes forward
```

*Jumps* **16 bytes** forward from the start of this instruction.

#### Example 4: *Stack Copy* Operation

```text
Bytes: [0x01][0x00][0xFF][0xFF][0xFF][0xFC][0x00][0x04]
       └─┬─┘ └─┬─┘ └──────────┬──────────┘ └─┬─┘
    CPDOWNSP qualifier   offset=-4 bytes    size=4
```

*Copies* **4 bytes** from ***top*** of *stack* to **offset -4** (one element down).

#### Example 5: Engine Function Call

```text
Bytes: [0x05][0x00][0x00][0x01][0x02]
       └─┬─┘ └─┬─┘ └─┬─┘ └─┬─┘
      ACTION qualifier routine=1  argCount=2
```

*Calls* engine routine #1 with 2 arguments (which must be on *stack* in reverse order).

#### Example 6: float Constant

```text
Bytes: [0x04][0x04][0x40][0x49][0x0F][0xDB]
       └─┬─┘ └─┬─┘ └──────────┬──────────┘
      CONST Float        3.14159... ([big-endian](https://en.wikipedia.org/wiki/Endianness) [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754))
```

Pushes *float* value approximately 3.14159 (π) onto the stack.

#### Example 7: *Object* Constant (`OBJECT_SELF`)

```text
Bytes: [0x04][0x06][0x00][0x00][0x00][0x00]
       └─┬─┘ └─┬─┘ └──────────┬──────────┘
      CONST Object      OBJECT_SELF (0x00000000)
```

Pushes `OBJECT_SELF` constant onto the stack.

#### Example 8: Conditional *Jump* (`JZ`)

```text
Bytes: [0x1F][0x00][0xFF][0xFF][0xFF][0xF0]
       └─┬─┘ └─┬─┘ └──────────┬──────────┘
        JZ  qualifier    offset=-16 bytes backward
```

*Jumps* **16 bytes** backward if ***top*** of *stack* is zero (consumes the *integer* from *stack*).

---

## Instruction Categories

| Category | Opcodes |
| -------- | ------- |
| *Stack* | `CPDOWNSP`, `CPTOPSP`, `MOVSP`, `CPDOWNBP`, `CPTOPBP`, `SAVEBP`, `RESTOREBP`, `INCxSP`, `DECxSP`, `INCxBP`, `DECxBP` |
| *Constants* | `CONSTI`, `CONSTF`, `CONSTS`, `CONSTO`, and typed variants |
| *Arithmetic* | `ADDxx`, `SUBxx`, `MULxx`, `DIVxx`, `MODxx`, `NEGx` |
| *Bitwise/Logic* | `LOGANDxx`, `LOGORxx`, `INCORxx`, `EXCORxx`, `BOOLANDxx`, `NOTx`, `COMPx`, `SHLEFTxx`, `SHRIGHTxx`, `USHRIGHTxx` |
| *Comparison* | `EQUALxx`, `NEQUALxx`, `GTxx`, `GEQxx`, `LTxx`, `LEQxx` |
| *Control Flow* | `JMP`, `JSR`, `JZ`, `JNZ`, `RETN`, `STORE_STATE`, `DESTRUCT` |
| *Function Calls* | `ACTION` (invokes engine-exposed script functions) |

### Detailed Instruction Descriptions

**Stack Manipulation:**

- `CPDOWNSP` (0x01): Copy bytes from top of stack down to specified offset. format: `[0x01][qualifier][signed32 offset][uint16 size]`. *SP* remains unchanged. Used to write local variables.
- `CPTOPSP` (0x03): Copy bytes from specified offset to top of stack. format: `[0x03][qualifier][signed32 offset][uint16 size]`. *SP* increases by `size` bytes. Used to read local variables.
- `MOVSP` (0x1B): Adjust stack pointer by specified value. format: `[0x1B][qualifier][signed32 offset]`. Used to allocate/deallocate stack space for local variables.
- `CPDOWNBP` (0x26): Copy bytes from base pointer down to specified offset (for global variables). format: `[0x26][qualifier][signed32 offset][uint16 size]`. *SP* remains unchanged. Used to write global variables.
- `CPTOPBP` (0x27): Copy bytes from specified offset relative to base pointer to top of stack (for global variables). format: `[0x27][qualifier][signed32 offset][uint16 size]`. *SP* increases by `size` bytes. Used to read global variables.
- `SAVEBP` (0x2A): Save current *BP* and set *BP* to current stack position. format: `[0x2A][qualifier]`. Used when entering a new function scope.
- `RESTOREBP` (0x2B): Restore *BP* from previous `SAVEBP`. format: `[0x2B][qualifier]`. Used when exiting a function scope.
- `RSADDx` (0x02): Reserve space on *stack* for a variable of specified type. format: `[0x02][qualifier]`. *SP* increases by 4 bytes (or 12 for vectors). Qualifier determines type: `0x03`=int, `0x04`=float, `0x05`=string, `0x06`=object, `0x10-0x1F`=engine types.
- `INCxSP` (0x24): Increment variable on *stack* at specified offset. format: `[0x24][qualifier][signed32 offset]`. Qualifier `0x03`=int, `0x04`=float.
- `DECxSP` (0x23): Decrement variable on *stack* at specified offset. format: `[0x23][qualifier][signed32 offset]`. Qualifier `0x03`=int, `0x04`=float.
- `INCxBP` (0x29): Increment global variable at specified *base pointer* offset. format: `[0x29][qualifier][signed32 offset]`.
- `DECxBP` (0x28): Decrement global variable at specified *base pointer* offset. format: `[0x28][qualifier][signed32 offset]`.

**Stack Operation Details:**

- *offsets*: Always negative (e.g., -4, -8), positive = invalid
- Copy ops: Signed 32-bit *offset* + unsigned 16-bit *size* (must be 4-[*byte*](https://en.wikipedia.org/wiki/Byte) multiple)
- `MOVSP`: Adjust *SP* (positive = deallocate, negative = allocate)
- BP ops: Identical to *SP* ops but use *base pointer* (set by `SAVEBP`, points to globals)
- Multi-element copies (*size* > 4): May indicate composite types (vectors, structs)
- `CPDOWNSP`/`CPDOWNBP`: Store to *stack* (*SP* unchanged, source = *top* of *stack*)
- `CPTOPSP`/`CPTOPBP`: Load from *stack* (*SP* increases by copied size)

**Position Conversion:**

- [*byte*](https://en.wikipedia.org/wiki/Byte) *offset* --> position: `-offset / 4` (e.g., -8 --> 2, -12 --> 3)
- *size* --> elements: `size / 4` (e.g., 12B --> 3 elements)
- *position* --> *offset*: `-position * 4`

**Examples:** *offset* -4 = *position* 1 (top), -8 = *position* 2, vector (12B) at -12 = *positions* 1-3

**Reference:**

- [`xoreos/src/aurora/nwscript/ncsfile.cpp:458-545`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L458-L545)
- [`reone/src/libs/script/format/ncsreader.cpp:52-97`](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp#L52-L97)
- [`xoreos/src/aurora/nwscript/ncsfile.cpp:105-172`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L105-L172)
- [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9)
- [`NorthernLights/Assets/Scripts/ncs/NCSReader.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/NCSReader.cs)
- [`NWScriptInstance.ts` L32+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptInstance.ts#L32)

**Constants:**

All use opcode `0x04`, *qualifier* determines type:

- `CONSTI` (0x03): `[0x04][0x03][uint32]` (6B), *SP*+4, unsigned but can represent signed (-2³¹ to 2³¹-1)
- `CONSTF` (0x04): `[0x04][0x04][float32]` (6B), *SP*+4, [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754) [big-endian](https://en.wikipedia.org/wiki/Endianness)
- `CONSTS` (0x05): `[0x04][0x05][uint16 len][ASCII]` (2+N B), *SP*+4 (pointer only, content stored separately), no [null terminator](https://en.cppreference.com/w/c/string/byte)
- `CONSTO` (0x06): `[0x04][0x06][signed32]` (6B), *SP*+4, special: `0x00000000` = `OBJECT_SELF`, `0x00000001`/`0xFFFFFFFF` = `OBJECT_INVALID`

**Parsing:** Read opcode (0x04) --> *qualifier* --> type-specific args (UInt32/[float32](GFF-File-Format#gff-data-types)/string length+data/signed32)

**Behavior:** Read value --> Create immutable constant entry --> Push onto stack (*SP*+4) --> Remains until consumed/removed

**Reference:**

- [`xoreos/src/aurora/nwscript/ncsfile.cpp:500-545`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L500-L545)
- [`reone/src/libs/script/format/ncsreader.cpp:60-73`](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp#L60-L73)
- [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9)
- [`NorthernLights/Assets/Scripts/ncs/NCSReader.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/NCSReader.cs)
- [`xoreos-tools/src/nwscript/ncsfile.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/ncsfile.cpp)
- [`NWScriptDef.ts` L12+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDef.ts#L12)

**Arithmetic Operations:**

All arithmetic operations consume operands from the top of the stack and place the result back on the stack. *SP* increases by result size and decreases by total operand sizes.

- `ADDxx`: Addition (supports *II*, *IF*, *FI*, *FF*, *SS*, *VV*)
- `SUBxx`: Subtraction (supports *II*, *IF*, *FI*, *FF*, *VV*)
- `MULxx`: Multiplication (supports *II*, *IF*, *FI*, *FF*, *VF*, *FV*)
- `DIVxx`: Division (supports *II*, *IF*, *FI*, *FF*, *VF*)
- `MODII`: Modulus (integer only)
- `NEGx`: Negation (supports *I*, *F*)

**Bitwise and Logical Operations:**

- `LOGANDII` (0x06): **Logical AND** of two integers
- `LOGORII` (0x07): **Logical OR** of two integers
- `INCORII` (0x08): **Bitwise Inclusive OR** of two integers
- `EXCORII` (0x09): **Bitwise Exclusive OR** of two integers
- `BOOLANDII` (0x0A): **Boolean/Bitwise AND** of two integers
- `NOTI` (0x22): **Logical NOT** of an integer
- `COMPI` (0x1A): **One's Complement** of an integer
- `SHLEFTII` (0x11): **Shift Integer Left** by specified number of bits
- `SHRIGHTII` (0x12): **Shift Integer Right** by specified number of bits (signed)
- `USHRIGHTII` (0x13): **Unsigned Shift Integer Right** by specified number of bits

**Comparison Operations:**

- `EQUALxx` (0x0B): Test for **EQUAL**ity. format: `[0x0B][qualifier][optional: uint16 size for TT]`. Supports *II*, *FF*, *SS*, *OO*, *TT*, and engine types. For *TT* (struct) qualifier, includes 2-[*byte*](https://en.wikipedia.org/wiki/Byte) size field (must be multiple of 4). Pops two operands from stack, compares them, pushes 1 if equal else 0.
- `NEQUALxx` (0x0C): Test for i**NEQUAL**ity. Format: `[0x0C][qualifier][optional: uint16 size for TT]`. Same as `EQUALxx` but pushes 1 if not equal else 0.
- `GTxx` (0x0E): **Greater Than**. format: `[0x0E][qualifier]`. Supports *II*, *FF*. Pops two operands (top is right operand), pushes 1 if left > right else 0.
- `GEQxx` (0x0D): **Greater Than or Equal**. format: `[0x0D][qualifier]`. Supports *II*, *FF*. Pops two operands, pushes 1 if left >= right else 0.
- `LTxx` (0x0F): **Less Than**. format: `[0x0F][qualifier]`. Supports *II*, *FF*. Pops two operands, pushes 1 if left < right else 0.
- `LEQxx` (0x10): **Less Than or Equal**. format: `[0x10][qualifier]`. Supports *II*, *FF*. Pops two operands, pushes 1 if left <= right else 0.

**Comparison Operation Details:**

- Comparison operations pop two operands from the stack and push a single integer result (1 for true, 0 for false)
- For binary comparisons (`GT`, `GEQ`, `LT`, `LEQ`), the top of stack is the right operand, and the value below it is the left operand
- structure comparisons (`EQUALTT`, `NEQUALTT`) perform [*byte*](https://en.wikipedia.org/wiki/Byte)-by-[*byte*](https://en.wikipedia.org/wiki/Byte) comparison of the specified number of bytes
- The size field for structure comparisons must be a multiple of 4 to maintain alignment
- string comparisons compare string pointers (4-[*byte*](https://en.wikipedia.org/wiki/Byte) values), not string contents directly

**Reference:**

- [`xoreos/src/aurora/nwscript/ncsfile.cpp:712-768`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L712-L768) (Comparison OPCode Implementation)
- [`reone/src/libs/script/format/ncsreader.cpp:102-105`](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp#L102-L105) (Comparison Instruction Parsing)
- [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9) (Comparison Operation Handling)

**Control Flow:**

- `JMP` (0x1D): Unconditional jump to relative offset. format: `[0x1D][qualifier][signed32 offset]`. *offset* is relative to the start of the *JMP* instruction. Used for loops and unconditional branches.
- `JSR` (0x1E): Jump to subroutine at relative offset. format: `[0x1E][qualifier][signed32 offset]`. Pushes return address onto *return stack*, then jumps. Used for function calls within the script.
- `JZ` (0x1F): Jump if top of stack is zero. format: `[0x1F][qualifier][signed32 offset]`. Consumes integer from top of stack (*SP* decreases by 4). If value is zero, jumps to *offset*; otherwise continues to next instruction.
- `JNZ` (0x25): Jump if top of stack is non-zero. format: `[0x25][qualifier][signed32 offset]`. Consumes integer from top of stack (*SP* decreases by 4). If value is non-zero, jumps to *offset*; otherwise continues to next instruction.
- `RETN` (0x20): Return from subroutine. format: `[0x20][qualifier]`. Pops return address from *return stack* and jumps to it. Used to exit script subroutines.
- `DESTRUCT` (0x21): Destroy elements on stack, preserving specified element. format: `[0x21][qualifier][uint16 size][signed16 stackOffset][uint16 sizeNoDestroy]` (8 bytes total). This instruction performs complex stack cleanup by removing `size` bytes from the stack starting at `stackOffset`, but preserves `sizeNoDestroy` bytes within that range. The `stackOffset` is a signed 16-bit value converted to a stack position by dividing by 4. Used for complex stack cleanup operations, particularly when unpacking structures or vectors where only specific elements need to be preserved. The preserved element is moved to the top of the stack after destruction.

**DESTRUCT Operation Details:**

The *DESTRUCT* instruction is used in scenarios where multiple stack elements need to be removed, but a specific element within that range must be preserved:

1. The instruction identifies a range of stack elements starting at `stackOffset` and extending for `size` bytes
2. Within that range, `sizeNoDestroy` bytes starting at a calculated position are preserved
3. All other bytes in the range are removed from the stack
4. The preserved element is moved to the top of the stack (*SP* position 1)
5. This is commonly used when unpacking structures: the structure occupies multiple stack positions, but only one field needs to be extracted

The `stackOffset` parameter is a signed 16-bit value that is converted to a stack position by dividing by 4. The *offset* is relative to the current stack pointer, with negative values indicating positions deeper on the stack. The `size` parameter indicates the total number of bytes to destroy, and `sizeNoDestroy` indicates how many bytes within that range should be preserved.

Example: If a structure occupies positions 3-5 (12 bytes) and only the middle element (position 4) needs to be preserved, *DESTRUCT* would remove positions 3 and 5 while keeping position 4, then move it to the top.

***DESTRUCT* format:**

- *Opcode*: `0x21`
- *Qualifier*: Typically `0x00` (not used for type determination)
- *Arguments*: `[uint16 size][int16 stackOffset][uint16 sizeNoDestroy]` (6 bytes total, 8 bytes including *opcode* and *qualifier*)
- The preserved element is extracted from the destruction range and placed at the top of the stack, effectively replacing the destroyed elements with just the preserved value.

During decompilation, *DESTRUCT* identifies structure field accesses (preserved element position --> field).

- `STORE_STATE` (0x2C): Save stack state for delayed execution. format: `[0x2C][qualifier][int32 size][int32 sizeLocals]` (10B). Used with `DelayCommand`. *size* = total stack bytes, *sizeLocals* = local variable bytes. Separates temp values from persistent locals. Decompilers typically emit as-is with comments.

**Control Flow Details:**

- Jump offsets: Relative to instruction start (not end), signed 32-bit (±2GB range)
- `JSR`: Separate return stack (not data stack), *return addr* = after *JSR*
- `RETN`: Pop *return addr* from return stack, empty stack = main/error
- `JZ`/`JNZ`: Consume top *int* (removed regardless of jump)
- `DESTRUCT`: Atomic multi-element removal with preservation (structure unpacking)

**Examples:** *JMP* @100 +20 --> 120, *JZ* @200 -16 --> 184, *JSR* @300 +50 --> 350 (*return addr* 306)

**Reference:**

- [`xoreos/src/aurora/nwscript/ncsfile.cpp:712-768`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L712-L768)
- [`reone/src/libs/script/format/ncsreader.cpp:81-91`](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp#L81-L91)
- [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9)
- [`NorthernLights/Assets/Scripts/ncs/NCSReader.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/NCSReader.cs)
- [`xoreos-tools/src/nwscript/ncsfile.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/ncsfile.cpp)
- [`KotOR.js/src/nwscript/NWScript.ts` L39+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScript.ts#L39)

**Engine Function Calls:**

- `ACTION` (0x05): format: `[0x05][0x00][uint16 routine][uint8 argCount]` (5B). *Routine* = index into engine function table (K1/K2 differ). *Args* in reverse order (last on top). Engine removes args, pushes return value. vectors = 3 floats (x, y, z). Synchronous execution.

**Function Table:**

Engine-specific mapping: *routine number* --> function (name, params, return type). Used for decompilation (routine 1 --> `GetFirstObject`). Invalid *routine* = error.

**Actions data file:** Lists engine functions, format: `return_type function_name(param_type param, ...)`. Example: `int GetFirstObject(int nObjectFilter, object oArea);`

The decompiler parses this file to build a lookup table mapping *routine numbers* (indices in the file) to function signatures. This allows the decompiler to generate readable function calls instead of raw `ACTION` instructions with numeric *routine* IDs.

**See [NSS File Format](NSS-File-Format) for complete documentation of nwscript.nss, function definitions, and KotOR-specific functions/constants.**

**Reference:**

- [`xoreos/src/aurora/nwscript/ncsfile.cpp:643-660`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L643-L660) (ACTION opcode implementation)
- [`reone/src/libs/script/format/ncsreader.cpp:74-77`](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp#L74-L77) (ACTION instruction parsing)
- [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9) (ACTION instruction handling)
- [`NorthernLights/Assets/Scripts/ncs/NCSReader.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/NCSReader.cs) (engine function call processing)
- [`xoreos-tools/src/nwscript/ncsfile.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/ncsfile.cpp) (actions data parsing for decompilation)

**Special Instructions:**

- `NOP` (0x2D): No-operation, used as placeholder for debugger. format: `[0x2D][qualifier]`. Does nothing, SP remains unchanged.
- Program size marker (0x42): Always found at offset 8 in NCS file header. format: `[0x42][uint32 fileSize]`. This is not a real instruction and is never executed. It contains the total file size in bytes ([*big-endian*](https://en.wikipedia.org/wiki/Endianness)). All implementations validate this marker before parsing instructions.

**Note:** All multi-[*byte*](https://en.wikipedia.org/wiki/Byte) values in NCS files are stored in **[*big-endian*](https://en.wikipedia.org/wiki/Endianness)** [*byte*](https://en.wikipedia.org/wiki/Byte) order. This includes all integers, floats, offsets, and size fields.

**Special Instruction Details:**

- `NOP` (0x2D) is a no-operation instruction that does nothing. It is typically used as a placeholder by debuggers or during script compilation. The *qualifier* is typically `0x00`.
- The program size marker (0x42) at offset 8 is never executed as an instruction. It is a metadata field that all implementations check before parsing the instruction stream. If this byte is not `0x42`, implementations should reject the file as invalid.

**Reference:**

- [`xoreos/src/aurora/nwscript/ncsfile.cpp:342-350`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L342-L350) (header validation including 0x42 check)
- [`xoreos-docs/specs/torlack/ncs.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/ncs.html) (Torlack's original NCS specification)
- [`NorthernLights/Assets/Scripts/ncs/NCSReader.cs:876-886`](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/Assets/Scripts/ncs/NCSReader.cs#L876-L886) (0x42 marker handling)
- [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9) (NOP instruction handling)
- [`Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_data.py:144-242`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_data.py#L144-L242) (instruction definitions)

---

## Control Flow and Jumps

- Jump instructions store relative offsets; readers resolve them to absolute positions.  
- PyKotor's *NCS* class tracks instruction objects and rewires the `jump` attribute so tooling can walk the control-flow graph without recomputing offsets.  
- Subroutines use `JSR` (push return address) and `RETN` (pop address and jump back).  
- `STORE_STATE`/`DESTRUCT` manage VM save/restore for suspended scripts (cutscenes, dialogs); the semantics are identical in Reone and [***Kotor.NET***](https://github.com/NickHugi/Kotor.NET), while [***KotOR.js***](https://github.com/KobaltBlu/KotOR.js) mirrors them for deterministic playback.

### Subroutine Calls

**Calling Conventions:**

**Script Subroutines:** Reserve Return Space --> Push args (reverse) --> `JSR` --> Subroutine removes args --> Return value at reserved location

**Engine Routines:** Push args (reverse) --> `ACTION` (routine #, *arg count*) --> Engine removes args --> Engine pushes return

**Example:** `int j = DoSomeScriptSubroutine(12, 14);`

Before: `SP --> -4: Arg1(12), -8: Arg2(14), -12: Return(??), -16: j(??)`  
After: `SP --> -4: Return(??), -8: j(??)`

**Example Stack Layout for Engine Routine Call:**

Before call to `int j = DoSomeEngineRoutine(12, 14);`:

```plaintext
*SP* --> -4:  *Arg1*: 12
     -8:  *Arg2*: 14
     -12: j: ??
```

After call:

```plaintext
*SP* --> -4:  *Return*: ??
     -8:  j: ??
```

### Jump Instructions

All jump instructions use ***relative offsets*** from the start of the jump instruction itself:

- `JMP`: Unconditional jump to offset
- `JZ`: Jump if top of stack is zero (consumes the integer from stack)
- `JNZ`: Jump if top of stack is non-zero (consumes the integer from stack)
- `JSR`: Jump to subroutine (pushes return address, then jumps)

The *offset* is a signed 32-bit integer stored in [*big-endian*](https://en.wikipedia.org/wiki/Endianness) format, allowing forward and backward jumps within the script. The *offset* is calculated as: `target_address - instruction_address`.

**Jump Resolution:** offsets resolved to absolute instruction pointers during parsing. PyKotor's `NCS` class stores direct instruction references in `jump` attribute for control-flow graph traversal. format: Signed 32-bit [big-endian](https://en.wikipedia.org/wiki/Endianness), `target = instruction_addr + offset`, forward (+) or backward (-).
Jump offsets and resolution behavior are implemented in PyKotor's instruction model ([`ncs_data.py` L244-L421](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/ncs_data.py#L244-L421)) and reader ([`io_ncs.py` L262-L269](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/ncs/io_ncs.py#L262-L269)), with matching parser/execution behavior visible in [reone `ncsreader.cpp` L81-L85](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp#L81-L85), [xoreos `ncsfile.cpp` L712-L768](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/nwscript/ncsfile.cpp#L712-L768), and [Kotor.NET `NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9).

---

## Cross-reference: implementations

Reference implementations include [reone `ncsreader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp), [xoreos `ncsfile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/nwscript/ncsfile.cpp), [xoreos-tools `ncsfile.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/ncsfile.cpp), [Kotor.NET `NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9), [NorthernLights `NCSReader.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/NCSReader.cs), [KotOR.js `NCSResource.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/NCSResource.ts), [kotor-savegame-editor `ncs.ts`](https://github.com/nadrino/kotor-savegame-editor/blob/master/src/formats/ncs.ts), and [xoreos-docs `ncs.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/ncs.html). These implementations use the same opcode space (`0x01-0x2D`, marker `0x42`), qualifier range (`0x03-0x3C`), and [big-endian](https://en.wikipedia.org/wiki/Endianness) encoding.

**Instruction Sizes:** Base *2B* + args: None (*0B*), Int/Float (*4B*), String (2+N B), *Stack copy* (6B), *ACTION* (3B), *DESTRUCT* (6B), `STORE_STATE` (8B), Struct compare (2B)

**Compatibility:** All implementations use identical opcodes (0x01-0x2D, 0x42), qualifiers (0x03-0x3C), and [*big-endian*](https://en.wikipedia.org/wiki/Endianness) encoding, ensuring cross-engine compatibility (same *ACTION* routine table required).

**Decompilation Overview:**

Core analyses: Stack tracking (variable assignments/reads via copy ops), Control flow (jumps --> if/loops/switches), Subroutine analysis (*JSR* --> function calls, infer params/returns), Variable naming (type + position or usage patterns), Dead code elimination

**Analysis Passes:**

1. **Parse**: Bytecode --> instructions + control flow graph (jumps as [edges](Level-Layout-Formats#edges-wok-only))
2. **Subroutines**: Identify boundaries via `JSR`/`RETN`, analyze separately
3. **type Inference**: Operations reveal types (`ADDII` --> ints, calls --> engine function table)
4. **Prototyping**: Infer subroutine signatures from usage (may need multiple passes for recursion)
5. **Stack Tracking**: Track state per instruction (variables, types, assignment), clone/merge at control flow joins
6. **structure Recognition**: 12-[*byte*](https://en.wikipedia.org/wiki/Byte) copies --> vectors, other multiples of 4 --> custom structs
7. **Control Flow**: Jumps --> `if`/loops (forward jumps = conditionals, backward = loops), multi-target = switch
8. **Code Gen**: Emit source with named variables, typed declarations, high-level constructs
9. **Cleanup**: Remove dead code, optimize names, format

**Stack Analysis Details:**

- **Variables**: `CPDOWNSP`/`CPDOWNBP` = writes, `CPTOPSP`/`CPTOPBP` = reads, *offset* identifies variable, size determines primitive vs composite
- **Scope**: `MOVSP` = function entry/exit (negative = allocate, positive = deallocate)
- **structures**: Vectors (*12B*) = z/y/x order, nested structures require hierarchy tracking
- **Globals**: BP operations, separate from locals (*SP* operations)
- **State Merging**: Converging paths require merging stack states (variables on all paths preserved)
- **Reference Counting**: Track usage per stack instance, zero refs + unassigned = placeholder
- **Return values**: Track separately, identified from stack state before *RETN*/**JSR*

Decompiler behavior described above is visible in [xoreos-tools `ncsfile.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/ncsfile.cpp), [xoreos-tools `decompiler.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/nwscript/decompiler.cpp), [reone `ncsreader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/script/format/ncsreader.cpp), [Kotor.NET `NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorNCS/NCS.cs#L9), [xoreos `ncsfile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/nwscript/ncsfile.cpp), [kotor-savegame-editor `ncs.ts`](https://github.com/nadrino/kotor-savegame-editor/blob/master/src/formats/ncs.ts), and [NorthernLights `NCSDecompiler.cs`](https://github.com/lachjames/NorthernLights/blob/master/Assets/Scripts/ncs/NCSDecompiler.cs).

### See also

- [NSS File Format](NSS-File-Format) - NWScript source that compiles to *NCS*
- [GFF-DLG](GFF-Creature-and-Dialogue#dlg) - Dialogue files that trigger *NCS* scripts
- [GFF-UTC](GFF-Creature-and-Dialogue#utc) - Creature Templates with Script Hooks
- [GFF-UTD](GFF-Spatial-Objects#utd) - Door Templates with Script Hooks
- [GFF-UTP](GFF-Spatial-Objects#utp) - Placeable Templates with Script Hooks
- [GFF-IFO](GFF-Module-and-Area#ifo) - Module Information Resource

