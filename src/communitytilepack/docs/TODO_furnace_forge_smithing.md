# TODO: Dirkies furnaces as Forge / Smithing stations (user, 2026-08-28)

**Sheets** (Community pack, `diederiks_tile_palooza.pack`; each has its own depth map in the pack):

- `edit_ddd_RUS_Production_Furnace`
  - Art: `Resources/Dirkies/edit_ddd_RUS_Production_Furnace.png`
- `edit_ddd_RUS_House_Furnace`
  - Art: `Resources/Dirkies/edit_ddd_RUS_House_Furnace.png`

**Goal:** use sprites from these sheets as custom forge and smithing tiles that work like B42's own metalworking stations.

**Not started.** First steps:

- Read the props of both sheets.
- Find out how vanilla B42 defines its forge and smithing stations: entity scripts, CraftBench and the fuel/heat components.
- Check how KBW's `EntityCompat.attach` instances native entity components on built pieces.
