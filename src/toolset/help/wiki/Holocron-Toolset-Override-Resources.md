# Holocron Toolset: Override Resources

## Override Resources

The override folder is the highest-priority resource location in the game. These can be found in the `/override/` folder of your game directory. Override files can be accessed by any module in the game and take priority over core and module resources.

**Warning:** Because override resources take the highest priority and are accessible by any module, conflicts are likely. For example, if a creature file named `n_rodian01` exists in both the *Citadel Station Cantina* and *Nar Shaddaa Loading Docks* and you place a file of the same name in override, both modules will now use the override file, even if the creatures were originally different. If you are adding new files or editing existing ones, be cautious. TSL developers often reused the same filename across multiple modules.

## Override Tab

The "Override" tab allows you to navigate through the override files. In TSL you can store files in nested folders and navigate through existing folders using the dropdown menu. This functionality is not present for KotOR 1.

- **Refresh** -- Refreshes the list of nested folders in the override directory.
- **Reload** -- Reloads the list of resources in the selected folder. If a resource is changed outside of the toolset, press this or an error may occur.

![Override Tab](https://raw.githubusercontent.com/OldRepublicDevs/PyKotor/master/Tools/HolocronToolset/src/toolset/help/images/introduction_1-overrideResources=1.png)

### See also

- [Holocron Toolset: Core resources](Holocron-Toolset-Core-Resources) -- Core resource tab
- [Holocron Toolset: Module resources](Holocron-Toolset-Module-Resources) -- Module resource tab
- [Concepts](Concepts#override-folder) -- Override folder and resource resolution
- [Mod Creation Best Practices](Mod-Creation-Best-Practices#file-priority-and-where-to-put-your-files) -- When to use override vs MOD
- [Concepts](Concepts#resource-resolution-order) -- Resolution order
