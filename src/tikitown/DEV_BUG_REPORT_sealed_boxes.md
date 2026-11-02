# TikiTown — Bug Report: Sealed-box loot vanishes on relog (multiplayer)

Mod: TikiTown (workshop 3037854728)
File: `42/media/lua/server/TikitownReturnsandXP.lua`
Recipes: `Open_Large_Box`, `Open_Medium_Box`, `Open_Small_Box`
(`42/media/scripts/Tikitown_Recipes.txt`)

---

## Symptom (confirmed in-game)

On a dedicated multiplayer server, opening a sealed box (Large/Medium/Small Post
Office Box) drops the bonus loot into the player's inventory as expected — but
the items are **not authoritative on the server**. They disappear on
logout/login. The recipe's declared `outputs` (`SheetPaper2`, `Mov_CardboardBox`)
persist correctly; only the randomized bonus loot vanishes.

---

## Root cause

The bonus loot is added imperatively in the recipe's `OnCreate`
(`CraftRecipeCode.GenerateTreasure.GenerateLgBoxLoot` etc.) through this helper:

```lua
local function giveItem(character, itemType)
    if not character or not itemType then return end
    if isServer() and not isClient() then
        sendServerCommand(character, "TikitownLoot", "give", { item = itemType })
    else
        local inv = character:getInventory()
        if inv then inv:AddItem(itemType) end
    end
end
```

and the paired receiver:

```lua
if isClient() then
    local function onServerCommand(module, command, args)
        ...
        player:getInventory():AddItem(args.item)   -- client-side add
    end
    Events.OnServerCommand.Add(onServerCommand)
end
```

Two problems combine:

1. **`OnCreate` runs in the CLIENT VM for a client-initiated craft.** So
   `isServer() and not isClient()` is false on a dedicated server, and `giveItem`
   always falls into the `else` branch: a bare `inv:AddItem(itemType)` on the
   client. That add is never registered on the server, so it is discarded on the
   next full inventory sync (i.e. relog). This is the disappearance.

2. **The direction is inverted.** The intended-authoritative branch uses
   `sendServerCommand` (server → client) and the `OnServerCommand` receiver then
   does the `AddItem` **on the client** — still non-authoritative. Even if that
   branch fired, the item would not be server-persisted. What's needed is the
   opposite: the client asks the server, and the **server** performs the add.

Net: every path ends in a client-side `AddItem` the server never records.

---

## Fix

Route the grant through the server authoritatively: client `OnCreate` sends a
request; a **server-side** handler performs the `AddItem` and lets PZ sync it
back. This is the standard B42 pattern for mod-granted inventory.

**1. Replace `giveItem` (client asks server):**

```lua
local function giveItem(character, itemType)
    if not character or not itemType then return end
    -- Singleplayer / co-op host: this VM is authoritative, add directly.
    if isServer() then
        local inv = character:getInventory()
        if inv then
            inv:AddItem(itemType)
        end
        return
    end
    -- MP client: request the server to grant it authoritatively.
    sendClientCommand(character, "TikitownLoot", "give", { item = tostring(itemType) })
end
```

**2. Replace the receiver with a SERVER-side handler (client -> server):**

```lua
-- Runs on the dedicated server / host. Adds the item to the authoritative
-- inventory; PZ syncs it to the owning client.
if isServer() then
    local function onClientCommand(module, command, player, args)
        if module ~= "TikitownLoot" then return end
        if command ~= "give" then return end
        if not player or not args or not args.item then return end
        local inv = player:getInventory()
        if inv then
            inv:AddItem(args.item)
        end
    end
    Events.OnClientCommand.Add(onClientCommand)
end
```

Key changes vs current code:
- `sendServerCommand` (server->client) → `sendClientCommand` (client->server).
- The `AddItem` moves from an `OnServerCommand` (client) handler to an
  `OnClientCommand` (server) handler.
- The `isServer()` fast path keeps singleplayer/host working with a direct add.

No recipe/script changes are needed; the declared `outputs` already persist.

---

## Notes / to verify

- Confirmed the code path and that the current add is client-side and
  non-authoritative, which fully explains the relog loss. The exact VM in which
  B42 runs `OnCreate` for a client craft is stated from the crafting system's
  architecture; a debug print in `giveItem` (log `isServer()`/`isClient()` at
  call time) will confirm it takes the `else`/client branch on the server.
- The author already scaffolded MP handling (`sendServerCommand` /
  `OnServerCommand`), so this is a direction mistake (client<->server swapped),
  not missing MP support.
- Same helper feeds all three box sizes, so the single `giveItem` fix covers
  Large, Medium, and Small boxes at once.
- Unrelated: `TraceCardsOnBox` spawns a duffel with `Titanium_Baseball_Bat` at
  world (7782, 7399, z0) via `getPlayer()` — also client-side; if that path is
  also used on a dedicated server it may have the same authority issue and is
  worth a second look, though it spawns a world item rather than an inventory
  add.
```
