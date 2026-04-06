# Ghidra Code Browser: An Authoritative Walkthrough

The Ghidra Code Browser provides a disassembly listing, decompiler, symbol tree, and data type manager — everything needed to reverse-engineer a binary. The sections below cover function signatures, calling conventions (cdecl, fastcall, stdcall, thiscall), structures, vtables, template classes, and common decompile pitfalls, using a Windows KotOR binary as the running example.

---

## Table of contents

1. [Introduction](#1-introduction)
2. [Ghidra Repos and Projects](#2-ghidra-repos-and-projects)
3. [Code Browser Overview](#3-code-browser-overview)
4. [Symbol Tree](#4-symbol-tree)
5. [Data Type Manager](#5-data-type-manager)
6. [The Listing](#6-the-listing)
7. [Decompile View](#7-decompile-view)
8. [Other Code Browser Tools](#8-other-code-browser-tools)
9. [Functions](#9-Functions)
10. [Calling Conventions](#10-Calling-Conventions)
11. [Returns and Custom Storage](#11-Returns-and-Custom-Storage)
12. [Structures](#12-Structures)
13. [Vtables](#13-VTables)
14. [Template Classes](#14-Template-Classes)
15. [Common Decompile Issues](#15-Common-Decompile-Issues)
16. [Closing](#16-Closing)

---

## 1. Introduction

Code Browser Overview
<img width="1920" height="720" alt="frame_00-00-00" src="https://github.com/user-attachments/assets/e800a7a8-a4ac-47f3-a001-51c302d6d0c5" />

This walkthrough introduces basic concepts and ideas in Ghidra so you can get your feet wet and understand what you're working with.

---

## 2. Ghidra Repos and Projects

A Ghidra project is made up of different repos; each repo represents an executable binary. Double-clicking a repo opens the code browser.

Project repos organized by version and platform
<img width="1920" height="720" alt="frame_00-00-35" src="https://github.com/user-attachments/assets/62c20481-baed-45e8-a735-b4fcf6035ba1" />

Repos are often organized by version and platform (e.g. Android, iOS, Mac, Amazon games, GOG, Xbox). The following sections use the Code Browser opened for the Windows GOG version of KOTOR one—a heavily labeled and analyzed binary—as the example.

Code Browser opened for Windows GOG KOTOR one
<img width="1920" height="720" alt="frame_00-00-50" src="https://github.com/user-attachments/assets/42a2c52e-02a7-40a4-a431-5f5a0248a4b6" />

---

## 3. Code Browser Overview

Code browser with symbol tree visible
<img width="1920" height="720" alt="frame_00-01-15" src="https://github.com/user-attachments/assets/ccb6d608-9551-4f1d-9750-82ae72d2fd6e" />


The code browser is the main workspace. The first element to note is the symbol tree (see below).

---

## 4. Symbol Tree

The symbol tree lists all symbols in the binary: classes, namespaces, functions, labels, imports (typically DLLs), and exports—which for a Windows executable is the entry point. Use it as your starting point when searching the .exe; you can search function and class names and browse the hierarchy.

Symbol Tree pane with search
<img width="1920" height="720" alt="frame_00-02-15" src="https://github.com/user-attachments/assets/e8b96acb-7c78-429e-a55e-b7e8039b9d4b" />


For example, to find server-side creature symbols, search for *CSWS creature* to get the function of that name; clearing the search then shows everything under that class.

Symbol tree expanded for a class with many functions
<img width="1920" height="720" alt="frame_00-02-25" src="https://github.com/user-attachments/assets/fe19aa10-7c7a-4b03-a3f0-86ff4f443051" />


The class implements many functions—for server creatures, a large set. More advanced filter settings (e.g. regex) are available; the basic search is often sufficient. You can also search variables (e.g. *enable*); outside the class section you will see symbols such as shadows enabled, enable beams, and similar. In short, the symbol tree is the main entry point for searching the executable.

---

## 5. Data Type Manager

The Data Type Manager shows all types defined in the repo: structures (often associated with classes), unions, enums (e.g. for game effects, gender), and function types (return type, calling convention, parameters). Pointers are part of this but hidden by default since they are usually redundant with the types they point to.

Data Type Manager overview
<img width="1920" height="720" alt="frame_00-03-20" src="https://github.com/user-attachments/assets/cb7d92e0-d043-4009-bb42-a57da2bd0aa3" />


The Data Type Manager contains several archives. The red archive *swkotor.exe* is the main one for the program; *Windows* holds the Windows headers; *Built-in types* is what Ghidra always provides. Types are often grouped (e.g. enums in a dedicated folder). Under Code types you see the structures and enums in use.

Data Type Manager archives: swkotor.exe, Windows, Built-in types
<img width="1920" height="720" alt="frame_00-03-35" src="https://github.com/user-attachments/assets/893bb115-bfb4-4991-9c60-b5ddf3537b92" />

Opening `CSWSObject` (the server object structure) in the structure editor shows name, description, and size. Enums can be grouped in their own directory—for example game effects like entangle, poison, ability increase, used numerically.

Structure editor for `CSWSObject`
<img width="1920" height="720" alt="frame_00-04-10" src="https://github.com/user-attachments/assets/96efea08-adf9-402d-b174-f28360372723" />

Unions are used where the code treats the same memory differently—e.g. *res internal* (Edit Component) can be four integers or 16 characters; the union keeps the decompile clear.

Right-click a type and choose **Find uses of** to search the repository for its usage. Clicking a result jumps to that use—e.g. *get item and slot* passing *main hand*, so the constant 16 is labeled as main hand and you avoid memorizing magic numbers.

Find uses of a type showing references e.g. get item and slot with main hand
<img width="1920" height="720" alt="frame_00-05-25" src="https://github.com/user-attachments/assets/24e15af1-ec52-4b31-9627-b47d4232e94d" />


---

## 6. The Listing

The listing is where the program assembly appears. It should be your primary interface in the code browser. The listing is the ground truth for what the program does; trust it over the decompile view, because the assembly is the actual machine code. The decompile view and data types are inferred from the listing.

Listing as primary view: assembly and addresses
<img width="1920" height="720" alt="frame_00-05-50" src="https://github.com/user-attachments/assets/6207b76d-190b-4f78-80ff-807b784bb3c4" />


Double-clicking a label in the listing jumps to it. Labels are not always associated with a function; sometimes a label is part of the code structure—e.g. a conditional jump to a label can define an if. The listing shows current address, bytes at that address, and the instruction as interpreted.

Listing navigation: label double-click and conditional jump to label
<img width="1920" height="720" alt="frame_00-06-20" src="https://github.com/user-attachments/assets/514727ae-734a-48a6-ad2e-6e5534cf087f" />


Xrefs (cross references) show where a function or symbol is called or referenced. Clicking a reference shows the use in context (e.g. *load module finish*). The same works for data: the app manager global may have dozens of references; jumping to one (e.g. in *pause*) shows where it is used.

Cross references (xrefs) for a symbol
<img width="1920" height="720" alt="frame_00-07-00" src="https://github.com/user-attachments/assets/672bfca6-e42b-4daa-80bd-ed86874fd2ab" />

In the data section, unanalyzed bytes appear as address, byte, and default interpretation. Right-click → **Data** → **String** (or another type) to define data; the string is then marked up where it is used in code.

Data section: defining a string via Right-click Data
<img width="1920" height="720" alt="frame_00-07-50" src="https://github.com/user-attachments/assets/f4fb2678-3b67-4396-853b-547c17fe7e2c" />


The toolbar offers quick navigation: **F** (next function), previous function, next/last label, next undefined (often NOPs), next instruction. Instruction Info (often in a popup or panel) shows the exact operands for the current instruction.

---

## 7. Decompile View

The decompile view is Ghidra's best-effort C-like reconstruction of the current function. It updates only when the cursor is in a function; selecting something in a data section (e.g. *enable render*) does not change the decompile. As soon as you jump to a new function, the decompile updates.

Decompile view showing reconstructed C-like code
<img width="1920" height="720" alt="frame_00-09-25" src="https://github.com/user-attachments/assets/7606468d-db65-4308-8bc1-3c77a0996ae4" />

The decompile is useful for intuition about what the program does, but it is a heuristic, not an algorithm—accuracy can vary. The following example illustrates typical usage.

You can navigate by double-clicking any function or label in the decompile. To rename a variable or function, use the **L** hotkey (by default). **L** on a function also allows changing the namespace. The semicolon control opens the function signature editor for more advanced changes (see the section on functions).

Decompile with function/label navigation and rename (L)
<img width="1920" height="720" alt="frame_00-10-50" src="https://github.com/user-attachments/assets/fc5bf3c9-5080-45e0-9001-403613775365" />

The refresh button has limited effect. An option allows unreachable code to appear; most functions have none, but it is available when needed. Other options are worth exploring in the UI.

---

## 8. Other Code Browser Tools

The function call trees show outgoing and incoming references for the current function (like xrefs) and can jump to those references. The memory map lists the executable's sections: headers and magic numbers at the start, *.text* (bulk of the program), *.rdata* (read-only data), other data with static initializations, unallocated data, and resources.

Function call trees and memory map
<img width="1920" height="720" alt="frame_00-11-45" src="https://github.com/user-attachments/assets/d0c39874-e603-4720-a92c-63ddc25727ad" />

Bookmarks let you save addresses and jump back to them later.

The symbol table lists all symbols. With "all" selected, a heavily labeled project may show on the order of 155,000 items. The table supports more complex and filtered searches than the symbol tree; the tree is better for hierarchy and browsing, the symbol table for narrow, specific lookups. Filters (e.g. undefined parameters) narrow the list to functions that still need typing.

Symbol table with filters
<img width="1920" height="720" alt="frame_00-13-00" src="https://github.com/user-attachments/assets/dc0f6085-7e52-4346-b16e-27d875cf66b8" />

The Functions view is similar to the symbol table but function-specific: filter by calling convention, inlining, function size, location, or full signature.

Functions view with calling convention filter
<img width="1920" height="720" alt="frame_00-14-05" src="https://github.com/user-attachments/assets/497fa7f0-373c-41cb-b1b8-63374b50642a" />

The Jython console is a Python wrapper for Ghidra's Java APIs. It is useful for quick queries—e.g. hex conversion, *current program*, *current address*, *getFunctionAt(currentAddress)*—and scripting. Jython is being superseded by PyGhidra (the Python wrapper for Ghidra v12); see official documentation for migration.

Script output from the script manager appears in the console. Many small features and plugins are available in the code browser and are worth exploring. The next sections cover core concepts: functions, calling conventions, structures, vtables, and common issues.

---

## 9. Functions

A function is defined at an address and has a name, calling convention, return type, and zero or more parameters. It can belong to a class or namespace (visible in the symbol tree); the class/namespace is set only via the rename view (e.g. **L** hotkey). Other properties include varargs (e.g. *printf*'s *...*), inlining (body inserted at call sites—useful for small or unusually called functions), custom storage (see below), call fixups, and thunks (function redirects; a few exist in KOTOR).

Function list and edit context
<img width="1920" height="720" alt="frame_00-16-35" src="https://github.com/user-attachments/assets/0156538d-3c8b-4372-bff1-f576e3139cbe" />


Navigate to a function (e.g. **G** and an address) and open the edit view. The namespace or class (e.g. *CSWMinigame*) appears in the edit function view only after the function has been renamed. To change namespace, set it to global and enter the new name with leading colons.

Edit function view: update function and namespace
<img width="1920" height="720" alt="frame_00-18-15" src="https://github.com/user-attachments/assets/de07eec7-86f4-40a1-b3e8-82735519261f" />


The editor shows name, calling convention (covered below), return type (e.g. *void*), and parameters. A *this* parameter is typically in the ECX register; other parameters appear with their storage—e.g. a float at stack offset 4 from the initial stack pointer.

Function signature: name, calling convention, return type, this in ECX, stack parameter
<img width="1920" height="720" alt="frame_00-18-30" src="https://github.com/user-attachments/assets/187e7504-82bb-41e2-98eb-cbb4dbfa551a" />

---

## 10. Calling Conventions

Four calling conventions matter most on this platform: **cdecl**, **fastcall**, **stdcall**, and **thiscall**. The example function uses thiscall.

Calling convention selector: thiscall
<img width="1920" height="720" alt="frame_00-19-15" src="https://github.com/user-attachments/assets/3944f28e-f4c3-43ee-a1d3-02e4d0d2f1e3" />

**cdecl** is used for C and some C++ functions. The *caller* is responsible for stack cleanup. For example, the library function *positive* (returns whether a double is greater than zero) has one stack parameter—a 32-bit pointer to a double (four bytes on the stack). The callee uses it and does not clean it; the caller adjusts ESP after the call.

**stdcall** is similar but the *callee* cleans the stack. At the return instruction, the function specifies how many bytes to pop (e.g. eight bytes for two 32-bit pointer parameters). It also restores the base pointer and registers such as EDX, EDI, ESI before returning. So: cdecl = caller cleans; stdcall = callee cleans.

stdcall return with stack cleanup
<img width="1920" height="720" alt="frame_00-20-50" src="https://github.com/user-attachments/assets/29d282c8-182b-4369-94ee-e11af624f4d3" />

**fastcall** is rare in KOTOR. Parameters are passed in registers instead of on the stack (e.g. library functions like *write pair* or the sig lookup from Visual Studio 2003). **thiscall** is by far the most common in KOTOR: the *this* pointer is passed in **ECX** (the 32-bit C register). Other parameters are on the stack.

thiscall: this in ECX, e.g. update function and Minigame object call
<img width="1920" height="720" alt="frame_00-22-45" src="https://github.com/user-attachments/assets/7b6b3ce8-0202-4b60-9e09-43382ab91501" />

For thiscall, cleanup depends on parameter count. If there is one or more stack parameter, thiscall behaves like stdcall (callee pops registers and stack). If there are no stack parameters (only *this* in ECX), it behaves like cdecl (caller cleans). Example: *MGO array* is called with no stack args, so no callee cleanup.

**Returns:** Regardless of convention, the return value lives in **EAX** (32 bits). When inspecting returns, look at EAX. Even when the return type is *void*, the function still leaves a value in EAX; that value is simply unused by callers unless you exploit it (e.g. for patching). See the section on custom storage for the exception (e.g. FPU returns).

---

## 11. Returns and Custom Storage

Custom storage overrides how a function's parameters or return values are stored when it violates the normal calling convention—e.g. due to compiler optimization or non-standard patterns. The most common need is for floating-point (FPU) returns and for the float-to-long style library function.

Custom storage and float-to-long in Data Type Manager
<img width="1920" height="720" alt="frame_00-26-35" src="https://github.com/user-attachments/assets/b157fb2b-da24-4ebd-ac02-5da533218992" />

**Float return example:** *read float* returns a *float 10* (10-byte x87 FPU type used for high-precision floating-point). The FPU uses its own stack; results are left in **ST(0)**. Because 10 bytes do not fit in EAX, the calling convention is violated. In the function's custom storage, set the return register to **ST** (FPU stack position zero). The rest can remain thiscall (e.g. *this* in ECX). The decompile then shows the return correctly.

read float with custom return storage ST
<img width="1920" height="720" alt="frame_00-27-15" src="https://github.com/user-attachments/assets/ca7d40c0-0e7d-44d6-880f-bb9cbddc236c" />


**Float-to-long (fol):** The library function *float to long* returns an unsigned long in EAX/EDX as usual, but the compiler often leaves a *float 10* in ST(0) as well, and callers use that value (e.g. *set size browsing rectangle*). To avoid spurious *extra out ST(0)* variables in callers, define a composite return type: the long result plus 10 bytes for the float, and in custom storage place the float part in ST and the long part in EAX/EDX. Then the decompile of callers stays clean.

float-to-long custom return type and usage in caller
<img width="1920" height="720" alt="frame_00-29-35" src="https://github.com/user-attachments/assets/1a0f2fa9-1af2-4943-bee4-dae1011e5dce" />

---

## 12. Structures

Structures describe how data is laid out in memory. Each has name, size, description, and a set of fields; each field has name, type (possibly another structure), length, and offset. Labeled fields appear in the decompile when referenced; unlabeled ones show as *field_N* and offset.

Structure editor: name, size, fields with offsets
<img width="1920" height="720" alt="frame_00-30-30" src="https://github.com/user-attachments/assets/8e5ac970-1f2f-4dc5-a424-30a34a773bc5" />

For example, *app manager* is a type with a *client* field at offset 4. In the decompile, *app manager + 4* or *ex manager + 4* is marked up as *client*. That is how structure fields are reflected in the decompile.

Decompile showing app manager and client at offset 4
<img width="1920" height="720" alt="frame_00-31-20" src="https://github.com/user-attachments/assets/b7a36a68-24c7-4662-9652-59d0e08067d3" />

Unlabeled fields appear by index and offset—e.g. the 11th field at offset 0xC might be used in the code before you have named it. Once you edit the data type and label the field, the decompile will use that name.

---

## 13. VTables

A **vtable** (or vftable) is an array of addresses of non-static member functions for a class—the usual C++ pattern where a pointer leads to a vtable and calls go through it. Ghidra's support for vtable labeling is limited; many entries stay as *field_N* at offsets. Vtables are still central to how logic is organized in the codebase.

Vtable concept and inheritance
<img width="1920" height="720" alt="frame_00-32-10" src="https://github.com/user-attachments/assets/9a1689fc-e413-4c31-b3e8-99f9bd20c754" />

Vtables are shared through inheritance. Some entries are unimplemented (e.g. return zero or void); others delegate to the parent class (e.g. Minigame obstacle using the parent's load script) or are overridden. The first slot is usually the destructor; then come "as" cast functions (as module, as creature, as door, as placeable, as item, etc.).

CSWS creature vtable: destructor and as-functions
<img width="1920" height="720" alt="frame_00-33-50" src="https://github.com/user-attachments/assets/91fd571f-36aa-4ec9-9a92-719618b50aa7" />

The vtable lives at offset 0 of the object; the first field is often the parent type. For *CSWS creature*, Edit Component shows inheritance from *C game object*; opening that reveals the vtable. Child classes can have longer vtables than the parent; Ghidra stores the vtable on the most senior parent, so creature-specific slots may still appear as generic *field_* entries.

Creature data type and vtable at offset 0 via parent C game object
<img width="1920" height="720" alt="frame_00-34-45" src="https://github.com/user-attachments/assets/e8b5dcda-e112-4bdf-ab64-e6ff80f61eda" />

In the listing, vtable calls look like a call through an offset (e.g. "code" and an address at +24). To resolve: take the object's type (e.g. *CSW track follower*), open its vtable, compute base + 0x18 for slot 24, and jump there—e.g. to *update*, which takes a float. Once the vtable function is labeled and given a return type (Edit Component), **Find uses of** will show call sites and the decompile will reflect the return type (e.g. creature pointer for *as creature*).

Vtable call in listing at +24 and resolving to update
<img width="1920" height="720" alt="frame_00-37-20" src="https://github.com/user-attachments/assets/25d047d4-17b9-493c-b7ab-17342511772f" />

When the vtable is owned by a parent (e.g. game object), different derived classes can have different functions at the same offset. Ghidra does not model that per-class, so some vtable slots stay ambiguous and the decompile can show conflicts between classes that share the same parent vtable.

---

## 14. Template Classes

Ghidra represents each template instantiation as a separate structure. Every *CXO array list&lt;T&gt;* variant gets its own entry in the Data Type Manager, which you must fill out. Main templated types to recognize: **array list**, **link list**, **resource helper**, **funk holder**, and **safe pointer** (less critical).

Data Type Manager: multiple template instantiations e.g. CXO array list
<img width="1920" height="720" alt="frame_00-39-30" src="https://github.com/user-attachments/assets/da8301a2-9a50-467f-bef5-9b085b6d0684" />

**Array list:** Fixed layout—12 bytes: *data* (pointer to T), *size*, *capacity*. So pointer elements become double pointers in the type. Simple and consistent.

**Link list:** Always 4 bytes, containing a *link list internal*; the element type is not represented. All link lists look the same in the type system, so the decompile is hard to annotate and tends to look messy.

**Funk holder:** Holds console commands—a vtable plus function slots (e.g. character/integer/void, string params, no-param functions).

**Resource helper:** Double template—first parameter is the resource type (e.g. *C res layout*, res vtable), second is the resource type ID (e.g. layout 3000, ifo 2014). These appear frequently.

**Safe pointer** and stdlib *vector* show up occasionally; *vector* is often messy in the decompile. The types above are the ones to be aware of.

---

## 15. Common Decompile Issues

The decompile view is heuristic; do not trust it over the listing. Common issues:

**Extra out variables:** A local named *extra out ...* means some called function's return (or register state) is wrong or incomplete. Examples: *extra out EAX* (function is void but EAX is used), *extra out ST(0)* (FPU return not modeled), or a wrong return type (byte vs int, bool vs int). Fix by correcting the callee's return type or custom storage. Sometimes the cause is the compiler treating a register as non-volatile and omitting restore; those cases are harder.

Extra out variable e.g. refill word ushort vs integer
<img width="1920" height="720" alt="frame_00-44-10" src="https://github.com/user-attachments/assets/9ea7690b-ed54-4154-b218-3c614e24ba56" />

Example: *refill word* returns a *ushort* (2 bytes), but the following code treats the result as 4 bytes. Ghidra shows *concat2* (pcode): the "extra" part is whatever was in the high bytes of EAX. Retyping *refill word* to a 4-byte return (where correct) can fix it.

A trickier case is **extra out ECX** from a function like the C string helper: the function leaves ECX unchanged (compiler optimized away restore because ECX was not clobbered). Callers then reuse ECX. That violates the normal convention, so Ghidra reports *extra out ECX*. Custom storage (ECX as an output) can clean the decompile but is verbose; often it is left as-is.

**Stack parameter violations:** The compiler may overwrite a stack parameter slot for reuse as a local. In Ghidra, param one might then appear to change type (e.g. from server creature to message data), and you see casts (e.g. to message data) and destructor calls that look wrong. Ghidra has no built-in fix; there is a long-standing GitHub issue. A typical sign is the function storing param one immediately and reusing that slot later.

Stack param violation: param one overwritten with message data
<img width="1920" height="720" alt="frame_00-48-25" src="https://github.com/user-attachments/assets/e3235a19-ffea-471c-9323-f461b9cab48e" />

**Unaffected (unaff) variables:** Variables like *unaff EBX* or *unaff return address* appear when a register or value is used without a clear definition—often due to an untyped vtable call or a wrong/non-standard calling convention. Ghidra does not know whether the callee or caller cleans up, so it shows these placeholder variables. Labeling the vtable function (and setting its convention) can remove them; otherwise they are hard to fix and may remain.

Unaffected EBX and return value from vtable call
<img width="1920" height="720" alt="frame_00-50-40" src="https://github.com/user-attachments/assets/edf8f43c-dbe5-4937-871e-2ec5b7aa0ec0" />

---

## 16. Closing

This concludes the walkthrough. For more detail, consult the official Ghidra documentation and community resources.

### See also

- [Reverse engineering findings](reverse_engineering_findings) — Engine behavior synthesis from K1 and TSL binaries
- [UTC Editor field types (AgentDecompile)](UTC-Editor-Field-Types-AgentDecompile) — RE findings for creature editor fields
- [NCS bytecode format](NCS-File-Format) — Compiled script format encountered during binary analysis
- [MDL/MDX model format](MDL-MDX-File-Format) — 3D model structures visible in decompiled engine code

---

*This guide walks through the Ghidra Code Browser using a Windows binary (Star Wars: Knights of the Old Republic — KOTOR) as the example. Names and terms such as swkotor.exe, NGO array, MGO array, refill word, CSWMinigame, and PyGhidra are used as they appear in the example codebase or in common usage.*
