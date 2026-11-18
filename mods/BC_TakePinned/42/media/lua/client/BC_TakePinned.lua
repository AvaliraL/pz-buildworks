-- BC_TakePinned
-- Adds a "Take Pinned" button to the loot window controls. It moves every item whose type is
-- pinned in Better Containers (EURY_CONTAINERS, "Pin Item Type") out of the nearby containers,
-- the floor, the BC Proximity / corpse views and bags inside them, into the container that is
-- currently open in the player's own inventory window.
--
-- Client-side only. Every move is a normal ISInventoryTransferAction, so the server validates
-- it exactly like a manual transfer. Nothing here edits Better Containers files.

require "ISUI/ISButton"
require "ISUI/LootWindow/ISLootWindowContainerControls"
require "ISUI/LootWindow/ISLootWindowObjectControlHandler"
require "ISUI/LootWindow/ISLootWindowFloorControlHandler"
require "TimedActions/ISInventoryTransferUtil"
require "TimedActions/WalkToTimedAction"

BC_TakePinned = BC_TakePinned or {}
local M = BC_TakePinned

-- ---------------------------------------------------------------------------------------------
-- Better Containers pin lookup
-- ---------------------------------------------------------------------------------------------

local pinnedMod, pinnedChecked = nil, false

-- Resolved once. Better Containers before 42.19 has no PinnedItems module; then the button never shows.
function M.getPinnedMod()
    if pinnedChecked then return pinnedMod end
    pinnedChecked = true
    local ok, mod = pcall(require, "BetterContainers/Upgrades/PinnedItems")
    if ok and type(mod) == "table" and type(mod.isFavourite) == "function" then
        pinnedMod = mod
        if type(mod.load) == "function" and not (mod.isLoaded and mod.isLoaded()) then
            pcall(mod.load)
        end
    end
    return pinnedMod
end

function M.hasAnyPin()
    local mod = M.getPinnedMod()
    if not mod or type(mod.FavouritedItems) ~= "table" then return false end
    for _, v in pairs(mod.FavouritedItems) do
        if v then return true end
    end
    return false
end

-- ---------------------------------------------------------------------------------------------
-- Text
-- ---------------------------------------------------------------------------------------------

-- getTextOrNull is only ever called with the key alone in vanilla (no format-argument overload is
-- known), so the %1 placeholders are filled here, for the translation and the fallback alike.
local function text(key, fallback, ...)
    local t = getTextOrNull and getTextOrNull(key) or nil
    -- (in game 2026-11-17: filling %1 here left "1$s": the Translator stores %1 as a Java format
    -- placeholder.) A translated text is formatted by getText, the way vanilla fills its counts.
    if t and t ~= key then
        local args = { ... }
        if #args == 0 then return t end
        if getText then
            local ok, s = pcall(getText, key, ...)
            if ok and type(s) == "string" then return s end
        end
    end
    local out = fallback
    local args = { ... }
    for i = 1, #args do
        out = string.gsub(out, "%%" .. i, tostring(args[i]))
    end
    return out
end

local function halo(playerObj, good, msg)
    if not (HaloTextHelper and playerObj) then return end
    if good and HaloTextHelper.addGoodText then
        HaloTextHelper.addGoodText(playerObj, msg)
    elseif (not good) and HaloTextHelper.addBadText then
        HaloTextHelper.addBadText(playerObj, msg)
    end
end

-- ---------------------------------------------------------------------------------------------
-- Collecting pinned items
-- ---------------------------------------------------------------------------------------------

local function isLockedForPlayer(container, playerObj)
    local parent = container and container.getParent and container:getParent() or nil
    if not (parent and playerObj) then return false end
    if instanceof(parent, "IsoThumpable") and parent.isLockedToCharacter then
        return parent:isLockedToCharacter(playerObj) == true
    end
    return false
end

local function itemWeight(item)
    if item.getUnequippedWeight then
        local w = item:getUnequippedWeight()
        if type(w) == "number" then return w end
    end
    return 0
end

local function isHeavyForceDrop(item)
    if type(isForceDropHeavyItem) == "function" then
        return isForceDropHeavyItem(item) == true
    end
    return false
end

-- Items that the button must leave alone. Returns true, or false + the reason (counted for the log).
local function canTake(item, ctx)
    local source = item:getContainer()
    if not source then return false, "no container" end
    if source == ctx.dest then return false, "already in destination" end
    if source:isInCharacterInventory(ctx.playerObj) then return false, "carried" end
    -- (in game 2026-11-17: 32 of 34 pinned items in a corpse pile were skipped as "equipped": what a
    -- zombie corpse wears reports isEquipped. Vanilla lets you take those, so only the player's own
    -- equipped items, already excluded above as carried, stay put.)
    if item:isHumanCorpse() then return false, "corpse" end
    if item:isUnwanted(ctx.playerObj) then return false, "unwanted" end
    if isHeavyForceDrop(item) then return false, "heavy" end
    if ctx.dest:isInside(item) then return false, "destination is inside it" end
    return true
end

local function count(ctx, key)
    ctx.skips[key] = (ctx.skips[key] or 0) + 1
end

local function scanContainer(container, ctx)
    local items = container:getItems()
    if not items then return end
    for i = 0, items:size() - 1 do
        local item = items:get(i)
        if item and ctx.seen[item] then
            count(ctx, "seen twice")
        elseif item then
            ctx.seen[item] = true
            ctx.scanned = ctx.scanned + 1
            local took = false
            if ctx.pinned.isFavourite(item:getFullType()) then
                local ok, why = canTake(item, ctx)
                if ok then
                    ctx.found[#ctx.found + 1] = item
                    took = true
                else
                    count(ctx, why)
                end
            end
            -- A pinned bag travels with its contents, so only look inside bags we are not taking.
            if not took and instanceof(item, "InventoryContainer") then
                local inner = item:getInventory()
                if inner and not ctx.visited[inner] then
                    ctx.visited[inner] = true
                    scanContainer(inner, ctx)
                end
            end
        end
    end
end

-- Returns a list of pinned items found in every container listed in the loot window,
-- including the BC proximity / corpse views (their item lists hold the real items), the floor,
-- and bags nested inside any of them. Each item appears once.
function M.collect(playerObj, lootPage, dest)
    local pinned = M.getPinnedMod()
    local ctx = {
        pinned = pinned, playerObj = playerObj, dest = dest,
        seen = {}, visited = {}, found = {}, skips = {}, scanned = 0, log = {},
    }
    if not pinned or not lootPage then return ctx.found, ctx end

    local function visit(container)
        if not container then return end
        if ctx.visited[container] then count(ctx, "container listed twice"); return end
        ctx.visited[container] = true
        local n = container.getItems and container:getItems() and container:getItems():size() or -1
        ctx.log[#ctx.log + 1] = tostring(container:getType()) .. "(" .. tostring(n) .. ")"
        if container:isInCharacterInventory(playerObj) then count(ctx, "container carried"); return end
        if isLockedForPlayer(container, playerObj) then count(ctx, "container locked"); return end
        scanContainer(container, ctx)
    end

    local buttons = lootPage.backpacks or {}
    ctx.buttons = #buttons
    for i = 1, #buttons do
        local b = buttons[i]
        if b and b.inventory then visit(b.inventory) end
    end
    if lootPage.inventoryPane and lootPage.inventoryPane.inventory then
        visit(lootPage.inventoryPane.inventory)
    end
    return ctx.found, ctx
end

-- ---------------------------------------------------------------------------------------------
-- Walking (same idea as BC smart deposit: queue a walk without clearing the action queue)
-- ---------------------------------------------------------------------------------------------

local function rootContainerOf(item)
    local root = item.getOutermostContainer and item:getOutermostContainer() or nil
    return root or item:getContainer()
end

-- Returns true when the player is, or will be, within reach of the container.
local function queueWalkNear(container, playerObj)
    if not (container and playerObj) then return false end
    if container:getType() == "floor" then return true end
    if container:isInCharacterInventory(playerObj) then return true end

    local parent = container:getParent()
    if not (parent and parent.getSquare and parent:getSquare()) then return true end

    local playerSquare = playerObj:getCurrentSquare()
    if not playerSquare then return false end

    if instanceof(parent, "IsoDeadBody") then return true end

    if instanceof(parent, "BaseVehicle") then
        if playerObj:getVehicle() == parent then return true end
        if playerObj:getVehicle() then return false end
        local part = container.getVehiclePart and container:getVehiclePart() or nil
        if part and part.getArea and part:getArea() then
            if part:getVehicle():canAccessContainer(part:getIndex(), playerObj) then return true end
            if ISPathFindAction and ISPathFindAction.pathToVehicleArea then
                local path = ISPathFindAction:pathToVehicleArea(playerObj, parent, part:getArea())
                path.allowedWhileDraggingCorpses = true
                ISTimedActionQueue.add(path)
                return true
            end
        end
        return false
    end

    if parent:getSquare():DistToProper(playerSquare) < 2 then return true end

    local adjacent = AdjacentFreeTileFinder and AdjacentFreeTileFinder.Find(parent:getSquare(), playerObj) or nil
    if not adjacent then return false end
    if adjacent ~= playerSquare then
        local walk = ISWalkToTimedAction:new(playerObj, adjacent)
        walk.allowedWhileDraggingCorpses = true
        ISTimedActionQueue.add(walk)
    end
    return true
end

local function distanceTo(container, playerObj)
    local parent = container and container.getParent and container:getParent() or nil
    local square = parent and parent.getSquare and parent:getSquare() or nil
    local mine = playerObj:getCurrentSquare()
    if not (square and mine) then return 0 end
    return square:DistToProper(mine)
end

-- ---------------------------------------------------------------------------------------------
-- Planning and queueing
-- ---------------------------------------------------------------------------------------------

local function hasRoom(dest, playerObj, item, reserved)
    if not dest:isItemAllowed(item) then return false end
    if reserved <= 0 then
        return dest:hasRoomFor(playerObj, item) == true
    end
    local planned = reserved + itemWeight(item)
    return dest:hasRoomFor(playerObj, planned, planned) == true
end

-- Splits found items into per-source-container groups (nearest first) and applies a weight budget
-- for the destination. Returns plan = { groups = { {root=, items={}} ... }, taken = n, noRoom = n }.
function M.plan(playerObj, dest, found)
    local groups, byRoot = {}, {}
    for _, item in ipairs(found) do
        local root = rootContainerOf(item)
        local group = byRoot[root]
        if not group then
            group = { root = root, items = {} }
            byRoot[root] = group
            groups[#groups + 1] = group
        end
        group.items[#group.items + 1] = item
    end

    for _, g in ipairs(groups) do g.dist = distanceTo(g.root, playerObj) end
    table.sort(groups, function(a, b) return a.dist < b.dist end)

    local plan = { groups = groups, taken = 0, noRoom = 0 }
    local reserved = 0
    for _, g in ipairs(groups) do
        local keep = {}
        for _, item in ipairs(g.items) do
            if hasRoom(dest, playerObj, item, reserved) then
                keep[#keep + 1] = item
                reserved = reserved + itemWeight(item)
                plan.taken = plan.taken + 1
            else
                plan.noRoom = plan.noRoom + 1
            end
        end
        g.items = keep
    end
    return plan
end

function M.run(playerNum, lootPage)
    local playerObj = getSpecificPlayer(playerNum)
    local invPage = getPlayerInventory(playerNum)
    local dest = invPage and invPage.inventoryPane and invPage.inventoryPane.inventory or nil
    if not (playerObj and dest) then return end

    local found = M.collect(playerObj, lootPage, dest)
    if #found == 0 then
        halo(playerObj, false, text("IGUI_BCTakePinned_NoneFound", "No pinned items nearby"))
        return
    end

    local plan = M.plan(playerObj, dest, found)
    local queued, unreachable = 0, 0
    for _, g in ipairs(plan.groups) do
        if #g.items > 0 then
            if queueWalkNear(g.root, playerObj) then
                for _, item in ipairs(g.items) do
                    local source = item:getContainer()
                    if source and source ~= dest then
                        ISTimedActionQueue.add(
                            ISInventoryTransferUtil.newInventoryTransferAction(playerObj, item, source, dest))
                        queued = queued + 1
                    end
                end
            else
                unreachable = unreachable + #g.items
            end
        end
    end

    if queued > 0 then
        halo(playerObj, true, text("IGUI_BCTakePinned_Moved", "Taking pinned items: %1", queued))
    end
    if plan.noRoom > 0 then
        halo(playerObj, false, text("IGUI_BCTakePinned_NoRoom", "No room for %1 pinned item(s)", plan.noRoom))
    end
    if unreachable > 0 then
        halo(playerObj, false, text("IGUI_BCTakePinned_Unreachable", "Can't reach %1 pinned item(s)", unreachable))
    end
end

-- ---------------------------------------------------------------------------------------------
-- Loot window handlers (container controls row, same as Take All / Take Same Type)
-- ---------------------------------------------------------------------------------------------

local function shouldBeVisible(self)
    if getCore():isTutorial() then return false end
    return M.hasAnyPin()
end

local FONT_HGT_SMALL = getTextManager():getFontHeight(UIFont.Small)

-- Our own button (same look as the vanilla handler's), so nothing but our click callback is wired to
-- it. In game (2026-11-17) a click raised "Object 1.0 did not have __call metatable" in
-- ISButton:onMouseDown, i.e. the button's onmousedown slot held a number; it is cleared here every
-- time the row is laid out.
local function buildControl(self)
    if not self.control then
        self.control = ISButton:new(0, 0, 200, 2 + FONT_HGT_SMALL + 2, "", self,
            function(_self, _button) _self:perform() end, nil, nil)
        self.control.borderColor = { r = 0.4, g = 0.4, b = 0.4, a = 1 }
    end
    self.control.onmousedown = nil
    self.control:setTitle(text("IGUI_BCTakePinned_Button", "Take Pinned"))
    self.control:setWidthToTitle()
    self.control:setTooltip(text("IGUI_BCTakePinned_Tooltip",
        "Move every pinned item type from all nearby containers, the floor, and bags inside them into the container open in your inventory window."))
    return self.control
end

local function perform(self)
    if isGamePaused() then return end
    local ok, err = pcall(M.run, self.playerNum, self.lootWindow)
    if not ok then print("[BC_TakePinned] error: " .. tostring(err)) end
end

-- Real containers (objects: crates, shelves, vehicles, ...)
ISLootWindowObjectControlHandler_TakePinned = ISLootWindowObjectControlHandler:derive("ISLootWindowObjectControlHandler_TakePinned")
local ObjectHandler = ISLootWindowObjectControlHandler_TakePinned
ObjectHandler.shouldBeVisible = shouldBeVisible
ObjectHandler.getControl = buildControl
ObjectHandler.perform = perform
function ObjectHandler:handleJoypadContextMenu(context)
    self:addJoypadContextMenuOption(context, text("IGUI_BCTakePinned_Button", "Take Pinned"))
end
function ObjectHandler:new()
    return ISLootWindowObjectControlHandler.new(self)
end

-- Floor, BC Proximity and BC zombie corpse views (no IsoObject parent)
ISLootWindowFloorControlHandler_TakePinned = ISLootWindowFloorControlHandler:derive("ISLootWindowFloorControlHandler_TakePinned")
local FloorHandler = ISLootWindowFloorControlHandler_TakePinned
FloorHandler.shouldBeVisible = shouldBeVisible
FloorHandler.getControl = buildControl
FloorHandler.perform = perform
function FloorHandler:handleJoypadContextMenu(context)
    self:addJoypadContextMenuOption(context, text("IGUI_BCTakePinned_Button", "Take Pinned"))
end
function FloorHandler:new()
    return ISLootWindowFloorControlHandler.new(self)
end

ISLootWindowContainerControls.AddHandler(ObjectHandler)
ISLootWindowContainerControls.AddFloorHandler(FloorHandler)

return M
