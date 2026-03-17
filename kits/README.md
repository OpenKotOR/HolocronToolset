# Indoor Builder Kits

This folder holds **indoor kits** used by the Holocron Toolset’s Indoor Builder (and the Module Designer’s Layout tab). Room pieces and components are loaded from here so you can place them in indoor maps.

- **To add kits:** Put kit directories or archives in this folder. The toolset loads them via `indoorkit_tools.load_kits()` and lists them in the Layout tab’s **Kits** combobox.
- **To get official kits:** Use the kit downloader from the Indoor Builder (or Layout tab) to download and install kits into this location.
- If this folder is empty, the Kits combobox will be empty until you add or download kits.
