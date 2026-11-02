# TikiTown — Bug: ImmunoStasis-3E (ImmunoCure) does not actually cure infection

Mod: TikiTown (Workshop 3037854728)
Item: `Tikitown.ImmunoCure` (in-game "ImmunoStasis-3E"), the crafted end product of
the Proxima cure chain.
File: `42/media/lua/shared/ProximaActions.lua`

## Symptom (player report)

After injecting the finished cure, the "Sick" moodle drops to 0 and the player
looks cured, but the **zombie infection keeps rising** and the player still turns.

## Root cause

The cure only clears the top-level infection **flags/timers** on `BodyDamage`; it
never clears the **infected wound** that actually drives infection. The effect
code (`applyEffect`, key `Tikitown:ImmunoCure`):

```lua
elseif key == "Tikitown:ImmunoCure" then
    bd:setInfected(false)
    bd:setInfectionMortalityDuration(-1)
    bd:setInfectionTime(-1)
    bd:setInfectionGrowthRate(0)
    bd:AddGeneralHealth(50)
end
```

In Build 42, zombie infection is derived from an **infected wound on a BodyPart**
(a bitten/infected scratch/laceration). `BodyDamage:Update()` re-reads those
wounds every health tick and re-raises `infected`, the infection level, and the
growth rate from them. So:

- The cure sets `infected=false` and zeroes the timers for a single frame.
- The infected wound is left in place.
- On the next tick, the engine re-derives infection from that wound and infection
  climbs again — undoing the cure instantly.

Net: the item appears to work (it heals 50 HP, which clears the generic "Sick"
illness moodle, so **sickness reads 0**) but **does not remove the infection**,
because it doesn't touch the wound. This is why sickness goes to 0 while
infection rises. It fails identically in single-player and MP (the server
re-applies the same flawed clear via the OnClientCommand handler).

### Why "sickness → 0" but "infection rising"
Two separate systems:
- **Illness / "Sick" moodle** = food-sickness / generic illness. The
  `AddGeneralHealth(50)` improves condition and clears this — cosmetic success.
- **Zombie infection** = the wound-driven Knox virus track. Untouched by the
  cure — keeps rising.

## Potential fix (using the base game's own verified API)

Clear the infection **at the wound level** across all body parts, then zero the
summary state. The exact calls below are taken from vanilla PZ's own
infection-clear code — see "API validation" at the bottom.

```lua
elseif key == "Tikitown:ImmunoCure" then
    local parts = bd:getBodyParts()
    for i = 0, parts:size() - 1 do
        local bp = parts:get(i)
        if bp:isInfectedWound() then
            bp:setWoundInfectionLevel(-1)   -- clears the infected wound (vanilla uses -1)
        end
    end
    -- now the summary state will not be re-raised from a wound next tick
    bd:setInfected(false)
    bd:setInfectionMortalityDuration(-1)
    bd:setInfectionTime(-1)
    bd:setInfectionGrowthRate(0)
    bd:AddGeneralHealth(50)
end
```

Key point: the load-bearing addition is
**`bp:setWoundInfectionLevel(-1)` on each infected body part**. Without it, no
amount of setting `BodyDamage` flags will stick, because `BodyDamage:Update()`
recomputes infection from the wound each tick.

If you also want to fully heal (like NeuroCline does), you can additionally call
`bp:RestoreToFullHealth()` per part — that's what vanilla's "heal full body"
cheat does. Leave it out if the cure should only stop the infection, not mend
wounds.

### API validation (verified against base-game Lua, not guessed)
These method names are confirmed from Project Zomboid's own scripts in this
install:
- `bodyPart:isInfectedWound()` and `bodyPart:setWoundInfectionLevel(-1)` —
  `media/lua/server/ClientCommands.lua` (the "infected" debug toggle) and
  `media/lua/client/XpSystem/ISUI/ISHealthPanel.lua`.
- `bodyPart:RestoreToFullHealth()` — same ClientCommands.lua ("healthFullBody").
- `getBodyDamage():getBodyParts()` / `:get(i)` iteration — used throughout the
  above files.

(An earlier draft of this report guessed `setInfectedWound(false)`; the correct
vanilla call is `setWoundInfectionLevel(-1)`. Corrected here.)

### MP
No MP change needed — the existing client→server `sendClientCommand` /
`OnClientCommand` routing is correct and applies `applyEffect` authoritatively on
the server. The fix goes inside `applyEffect`, so both the client-side prediction
and the server-authoritative application get the wound clear.

## Confidence / caveats
- Confirmed from source: the cure code touches only `BodyDamage` summary
  flags/timers and never the body-part wounds. That is certain and is the cause.
- The fix's API (`isInfectedWound`, `setWoundInfectionLevel(-1)`,
  `RestoreToFullHealth`, `getBodyParts`) is **verified against the base game's own
  Lua** in this install (ClientCommands.lua / ISHealthPanel.lua) — not guessed.
- The "Sick moodle → 0" explanation is inferred from `AddGeneralHealth(50)` plus
  the player's report; the infection-rising behavior is the direct consequence of
  the missing wound clear.
