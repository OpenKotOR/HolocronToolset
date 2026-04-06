# Holocron Toolset: New Features Quick Guide

The most impactful recent additions to the Holocron Toolset are listed below. Each feature works out of the box — no configuration required beyond having the latest version installed.

---

## Quick start: what's new?

### 1. Navigate to Favorites instantly

**What it does:** Jump directly to any bookmarked resource with one click.

**How to use:**

1. Bookmark resources (Ctrl+B or right-click → Add to Favorites)
2. Open Favorites (Ctrl+Shift+B)
3. Select a favorite → Click "Go To"
4. Instantly navigates to that resource in the file browser

**Why it's useful:** No more searching through thousands of files to find frequently used resources.

---

### 2. Rename resources safely

**What it does:** Rename resources with automatic validation and safety checks.

**How to use:**

1. Right-click any resource in Override folder
2. Select "Rename..."
3. Enter new name (extension preserved automatically)
4. Confirm if file exists
5. Resource renamed and refreshed in browser

**Safety features:**

- Only works in Override folder (protects core game files)
- Automatically preserves file extensions
- Detects name collisions before renaming
- Shows clear error messages if something goes wrong

**Example:** Rename `my_texture.tpc` → `character_head.tpc` in seconds.

---

### 3. Move resources (Cut/Paste)

**What it does:** Move resources between folders using familiar Cut/Paste.

**How to use:**

1. Select resource(s) in Override
2. Cut (Ctrl+X or right-click → Cut)
3. Navigate to destination folder
4. Paste (Ctrl+V or right-click → Paste)
5. Resources moved, model updated automatically

**Example:** Organize your Override folder by moving all textures into a `textures/` subfolder.

---

### 4. Batch operations

**What it does:** Process dozens or hundreds of files at once with progress tracking.

**How to use:**

1. Select multiple resources (Shift+Click or Ctrl+Click)
2. Right-click → "Batch Operations..." (or Ctrl+Shift+O)
3. Choose operation:
   - **Extract All** -- Save all to a folder
   - **Duplicate All to Override** -- Copy all to Override
   - **Delete All** -- Remove all (with confirmation)
   - **Rename with Pattern** -- Bulk rename with wildcards
4. Watch progress bar
5. Get summary: "Success: 47, Failed: 0, Skipped: 2"

**Example:** Extract 100 texture files to a backup folder in under 10 seconds.

---

### 5. Rename with pattern

**What it does:** Rename multiple files using wildcard patterns.

**How to use:**

1. Select files to rename
2. Batch Operations → "Rename with Pattern"
3. Enter find pattern: `old_*.tpc` (use * for any text)
4. Enter replace pattern: `new_*.tpc`
5. Preview: "15 files will be renamed"
6. Click OK
7. All matching files renamed instantly

**Examples:**

- `texture_*` → `char_*` renames `texture_001.tpc` to `char_001.tpc`
- `temp_*` → `*` removes "temp_" prefix from all files
- `*_old` → `*` removes "_old" suffix

---

### 6. Open With... dialog

**What it does:** Choose which editor to open a resource in.

**How to use:**

1. Right-click any resource
2. Select "Open With..."
3. See list of available editors (Generic GFF Editor, Specialized Editor, Dialog Editor, etc.)
4. Select preferred editor
5. Resource opens in chosen editor

**Example:** Edit a DLG in the generic GFF editor to see raw structure, or use the specialized dialog tree editor.

**Supported editors:** Dialog Editor, Creature Editor, Placeable Editor, Door Editor, Item Editor, Trigger Editor, Sound Editor, Waypoint Editor, 2DA Editor, Script Editor, Texture Editor, Model Editor, and more.

---

### 7. Create new resources

**What it does:** Create new resources from templates with one dialog.

**How to use:**

1. Right-click on any folder OR File → New
2. Select "New Resource..."
3. Choose resource type (2DA Table, Script Source, Creatures, Placeables, Items, Triggers, Dialogs, Journals, etc.)
4. Enter resource name
5. Confirm if file exists
6. Resource created with proper structure
7. Optional: Open immediately in appropriate editor

**What gets created:**

- **2DA files:** Minimal valid 2DA header
- **Script files (NSS):** Empty text file ready for coding
- **GFF files (UTC, DLG, etc.):** Minimal valid GFF structure with TemplateResRef
- **Text files (TXT, TXI):** Empty text file

---

### 8. Save editors (Ctrl+S)

**What it does:** Save editor changes back to your installation.

**How to use:**

- **Single editor open:** Ctrl+S → editor saves immediately
- **Multiple editors open:** Ctrl+S → dialog shows all open editors; choose Save selected, Save All, or Cancel

Saves go to the Override folder (or current location); file browser refreshes; "Saved: filename.ext" message shown.

---

### 9. Favorite star indicator

**What it does:** Shows a star in the status bar when the selected resource is bookmarked.

**How to use:** Select any resource; if it's in your favorites, status bar shows "1 item(s) selected ★".

---

### 10. Command palette enhancements

**What it does:** Quick access to all features via keyboard.

**How to use:**

1. Press Ctrl+Shift+P (Command Palette)
2. Type to filter: "save", "new", "batch", "open", etc.
3. Select command
4. Command executes immediately

**New commands added:** File: Save Editor, File: Open With..., File: New Resource, all batch operations, all navigation commands.

---

## Essential keyboard shortcuts

| Shortcut       | Action            |
|----------------|-------------------|
| **Ctrl+S**     | Save current editor |
| **Ctrl+N**     | New resource (if mapped) |
| **Ctrl+X**     | Cut selected resources |
| **Ctrl+V**     | Paste resources   |
| **Ctrl+B**     | Bookmark resource |
| **Ctrl+Shift+B** | Show favorites  |
| **Ctrl+Shift+O** | Batch operations |
| **Ctrl+Shift+P** | Command palette |
| **F5**         | Refresh browser   |
| **Delete**     | Delete selected   |

---

## Safety features

- **Override-only operations** -- Core game files cannot be modified by rename/move
- **Collision detection** -- Prompted before overwriting files
- **Validation** -- Invalid operations prevented before execution
- **Clear error messages** -- Explains what went wrong
- **Operation summaries** -- See what succeeded/failed after batch operations

---

### See also

- [Holocron Toolset: Getting Started](Holocron-Toolset-Getting-Started)
- [Holocron Toolset: Override resources](Holocron-Toolset-Override-Resources)
- [Mod Creation Best Practices](Mod-Creation-Best-Practices)
