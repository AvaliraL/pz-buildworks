# TODO (idea for later): wheelchair as a rideable "bicycle" (user, 2026-08-28)

**Goal:** the server runs a bicycle mod. Try making our wheelchair (Dirkies `location_community_medical_ddd_01` 24-27) work as one of its bikes.

- The rider uses the normal seated chair animation.
- No wheel animation is needed.

**Not started.** First steps:

- Identify the bicycle mod (Workshop id) and read how it defines a bike. Is it a vehicle script, an item with a world sprite, or a custom IsoObject?
- Check whether its "ride" state can take a different sprite or model, and an idle sit animation (vanilla `SitOnFurniture` / chair sit).
- Our built wheelchair is currently a KBW chair copy (`KBWCommunityIceShell_126..129`: bed + chair<dir>, file 65). A rideable version is a separate piece. The map / built chair stays as it is.
