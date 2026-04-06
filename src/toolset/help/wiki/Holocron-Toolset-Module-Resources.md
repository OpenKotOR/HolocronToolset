# Holocron Toolset: Module Resources

## Module resources

Module resources are the files stored inside the game's module archives. These can be found in the `/modules/` directory of your game directory and behave like zip files (in the sense of storing multiple files into a single file), carrying the extensions ERF, MOD, or [RIM](Container-Formats#rim). Module resources can only be accessed by the specific module they are stored in.

Resources contained in the module files can be directly edited and saved through the toolset without having to extract them. However, this is an irreversible operation so if you are editing files shipped directly with the game be sure to make backups otherwise you will need to reinstall the whole game.

A single module can have its resources stored across multiple module files and you can see this in the vanilla game (e.g. `danm14aa.rim` and `danm14aa_s.rim` both contain resources for "Dantooine – Courtyard"). In the second game, the `_dlg.erf` would also be part of the module.

## Module tab

The "Module" tab allows you to navigate through the various module files through a dropdown menu and view the resources stored inside them. Like the Core tab you can search for resources using the textbox.

- **Refresh** -- Refreshes the list of module files stored in the game's folder.
- **Reload** -- Reloads the list of resources stored in the module file selected in the dropdown menu. If a resource is changed outside of the toolset, you will need to press this button or an error may occur.

![Module tab](https://raw.githubusercontent.com/OpenKotOR/PyKotor/master/Tools/HolocronToolset/src/toolset/help/images/introduction_3-moduleResources=1.png)

### See also

- [Holocron Toolset: Core Resources](Holocron-Toolset-Core-Resources) -- Core resource tab
- [Holocron Toolset: Override Resources](Holocron-Toolset-Override-Resources) -- Override resource tab
- [Container-Formats#erf](Container-Formats#erf) -- MOD / generic ERF container format
- [Container-Formats#rim](Container-Formats#rim) -- Stock `.rim` / `_s.rim` module archives ([vs. ERF](Container-Formats#rim-versus-erf))
- [Concepts](Concepts#mod-erf-rim) -- MOD, ERF, RIM, and resource resolution
