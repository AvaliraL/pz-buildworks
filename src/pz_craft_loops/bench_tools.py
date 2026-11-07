# -*- coding: utf-8 -*-
"""Workbench built-in tools (Direction A). Test bundle until confirmed in game.

Goal (2026-08-28): each workbench provides ALL the core tools for its crafting type while the
player stands next to it, and building the bench COSTS one of each of those tool types (any variant
accepted) on top of its normal materials.

Mechanism (unchanged from the needle proof, which is confirmed working in game):
  * ONE detached virtual ItemContainer per bench config holds one of EVERY member item of every
    core tool tag (e.g. for the scissors tag: Scissors, ScissorsBlunt, ScissorsForged, ...). Being
    detached (ItemContainer.new(), no parent/square) it is never shown in a loot window and never
    saved -- nothing to fill, drop, transfer, or lose.
  * B42 craft panels build their tool pool from ISInventoryPaneContextMenu.getContainers(player) ->
    HandcraftLogic:setContainers. We wrap getContainers to append the bench's virtual container
    ONLY during a craft-panel query AND ONLY when the player is adjacent to a configured bench.
    A module flag gates it, so the loot window and other callers never see the tools.
  * Holding every member item means every recipe variant that asks for the tag resolves, and the
    user's "alternates should all be usable" requirement is satisfied for free.

Build cost: apply_to_buildables() appends one input per core tool tag to the bench recipe, each
input accepting ANY member item of that tag (items[A;B;C], consume, amount 1). So you can pay with
whatever variant you have.

Core tool tags per bench were derived from the B42 craftRecipe scripts (tags used by >=25% of the
category's recipes), with obvious cross-category bleed removed from Metalworking. Tag->member-item
lists come from the B42 item scripts (Tags = base:<tag>). See pz_craft_loops/_tagmembers.txt /
_benchplan.txt for the derivation.
"""
import os

SHARED_LUA = "KBWCommunity_BenchTools.lua"
CLIENT_LUA = "KBWCommunity_BenchMenu.lua"

# --- tag -> member items (from B42 item scripts; items with Tags = base:<tag>) ----------------
# Only the tags used by the configured benches are listed.
TAG_MEMBERS = {
    "scissors":          ["Base.Multitool", "Base.Scissors", "Base.ScissorsBlunt",
                          "Base.ScissorsBluntMedical", "Base.ScissorsForged"],
    "sewingneedle":      ["Base.Needle", "Base.Needle_Bone", "Base.Needle_Brass", "Base.Needle_Forged"],
    "awl":               ["Base.Awl", "Base.Awl_Bone", "Base.Awl_Stone", "Base.Handiknife",
                          "Base.IcePick", "Base.Multitool", "Base.SmallPunchSet"],
    "sharpknife":        ["Base.CrudeKnife", "Base.FightingKnife", "Base.FlintKnife",
                          "Base.HandguardDagger", "Base.Handiknife", "Base.HuntingKnife",
                          "Base.HuntingKnifeForged", "Base.KitchenKnife", "Base.KitchenKnifeForged",
                          "Base.KnifeButterfly", "Base.KnifeFillet", "Base.KnifeParing",
                          "Base.KnifePocket", "Base.KnifeSushi", "Base.LargeKnife",
                          "Base.LargeKnife_Scrap", "Base.LongCrudeKnife", "Base.Machete",
                          "Base.MacheteForged", "Base.MacheteKnife", "Base.Machete_Crude",
                          "Base.Multitool", "Base.RailroadSpikeKnife", "Base.SharpedStone",
                          "Base.SmallKnife", "Base.SteakKnife", "Base.StoneKnifeLong",
                          "Base.StraightRazor", "Base.SwitchKnife"],
    "weldingmask":       ["Base.Glasses_OldWeldingGoggles", "Base.WeldingMask"],
    "metalsaw":          ["Base.Saw"],
    "sheetmetalsnips":   ["Base.SheetMetalSnips"],
    "metalworkingpunch": ["Base.MetalworkingPunch"],
    "drillmetal":        ["Base.HandDrill"],
    "hammer":            ["Base.BallPeenHammer", "Base.BallPeenHammerForged", "Base.Hammer",
                          "Base.HammerForged", "Base.HammerStone", "Base.SmithingHammer"],
    "wrench":            ["Base.Ratchet", "Base.Wrench"],
    "screwdriver":       ["Base.Handiknife", "Base.Multitool", "Base.Screwdriver",
                          "Base.Screwdriver_Improvised", "Base.Screwdriver_Old"],
    "pliers":            ["Base.MetalworkingPliers", "Base.Multitool", "Base.Pliers"],
    "saw":               ["Base.CrudeSaw", "Base.GardenSaw", "Base.Saw"],
    "crudesaw":          ["Base.Saw_Flint"],
    "smallsaw":          ["Base.SmallSaw"],
    "mortarpestle":      ["Base.CeramicMortarandPestle", "Base.MortarPestle"],
}

# --- per bench: craft category + its CORE tool tags -------------------------------------------
# label shown on the right-click menu is IGUI_KBWCB_Bench_<Category>.
_BENCHES = {
    "community.fears.workbench.tailoring": {
        "category": "Tailoring",
        "tags": ["scissors", "sewingneedle", "awl", "sharpknife"],
    },
    "community.fears.workbench.metalworking": {
        "category": "Metalworking",
        # tailoring bleed (scissors/sharpknife/sewingneedle/awl) removed -- not metalworking tools
        "tags": ["weldingmask", "metalsaw", "sheetmetalsnips", "metalworkingpunch",
                 "drillmetal", "hammer", "wrench"],
    },
    "community.fears.workbench.electrical": {
        "category": "Electrical",
        "tags": ["screwdriver", "pliers"],
    },
    "community.fears.workbench.carpentry": {
        "category": "Carpentry",
        "tags": ["saw", "crudesaw", "smallsaw", "hammer"],
    },
    "community.fears.workbench.gunsmithing": {
        "category": "Weaponry",
        "tags": ["drillmetal", "wrench"],
    },
    "community.fears.workbench.chemistry": {
        # no dedicated Chemistry craft category in B42; closest keep-tool category is Medical
        # (mortar & pestle). Give the bench that one tool.
        "category": "Medical",
        "tags": ["mortarpestle"],
    },
}


def _label_key(category):
    return "IGUI_KBWCB_Bench_" + category


def _members(tags):
    """Flattened, de-duped list of every member item across the given tags (stable order)."""
    seen = set()
    out = []
    for t in tags:
        for it in TAG_MEMBERS[t]:
            if it not in seen:
                seen.add(it)
                out.append(it)
    return out


# Build the stage-property config each bench carries (used by the runtime Lua) and the public
# BENCH_TOOLS map used by apply_to_buildables for the build cost.
BENCH_TOOLS = {}
for _bid, _cfg in _BENCHES.items():
    _tags = _cfg["tags"]
    BENCH_TOOLS[_bid] = {
        "category": _cfg["category"],
        "labelKey": _label_key(_cfg["category"]),
        "tags": list(_tags),
        "items": _members(_tags),   # runtime: hold one of each
    }

TRANSLATIONS = {
    "IG_UI": {_label_key(c): c for c in sorted({v["category"] for v in _BENCHES.values()})},
    "ItemName": {},
}

_SHARED = r'''-- AUTO-GENERATED by pz_craft_loops/bench_tools.py -- do not edit by hand.
-- Direction A: a workbench exposes a hidden virtual container holding all its craft-type tools to
-- the craft panel while the player stands next to it. No real item on the bench, no lootable
-- container. Tools are REAL game items (one of every member of each core tool tag), so every
-- recipe variant and every tool alternate resolves.
KBWCommunityBenchTools = KBWCommunityBenchTools or {}
local BT = KBWCommunityBenchTools
local CONFIG_KEY = "kbwcbBenchTools"
local TOOL_MARK = "kbwcbBenchTool"

local function log(text) print("[KBWCommunity] BenchTools: " .. tostring(text)) end

-- hot path (runs for every object on every loaded square): cheapest tests first, no closures
--@BENCH_MAPS@--
function BT.configOf(object)
    if not object or not instanceof(object, "IsoObject") then return nil end
    if object:hasModData() then
        local cfg = object:getModData()[CONFIG_KEY]
        if type(cfg) == "table" and type(cfg.items) == "table" then return cfg end
    end
    -- A bench that was picked up and placed again is a plain moveable object: vanilla does not
    -- carry our modData across, so identify benches by their tile as well.
    local sprite = object:getSprite()
    if sprite then
        local name = sprite:getName()
        local category = name and BT.SPRITE_CATEGORY[name] or nil
        if category then return BT.CATEGORY_CFG[category] end
    end
    return nil
end

-- is there a configured bench on the player's square or an adjacent one? returns the cfg or nil.
-- If wantCategory is given, only a bench whose category matches is returned (for the speed bonus).
function BT.adjacentBenchConfig(player, wantCategory)
    if not player then return nil end
    local sq = player:getSquare()
    if not sq then return nil end
    local cell = getCell()
    local px, py, pz = sq:getX(), sq:getY(), sq:getZ()
    for dx = -1, 1 do
        for dy = -1, 1 do
            local s = cell:getGridSquare(px + dx, py + dy, pz)
            if s then
                local objects = s:getObjects()
                for i = 0, objects:size() - 1 do
                    local cfg = BT.configOf(objects:get(i))
                    if cfg and (not wantCategory or cfg.category == wantCategory) then return cfg end
                end
            end
        end
    end
    return nil
end

-- craft-speed bonus when crafting at a matching workstation (1.0 = none; 0.90 = 10% faster)
BT.SPEED_MULTIPLIER = 0.90

-- One detached virtual container per unique tool-set, built lazily and cached by a signature key.
-- ItemContainer.new() with no parent is never shown in a loot window and is never saved.
BT._virtualContainers = BT._virtualContainers or {}
function BT.virtualContainerFor(cfg)
    local key = cfg.category or "?"
    local container = BT._virtualContainers[key]
    if container then return container end
    local ok, made = pcall(function()
        local c = ItemContainer.new()
        for index = 1, #cfg.items do
            local item = c:AddItem(cfg.items[index])
            -- mark it: a bench tool may be moved into the player's hands for a craft, but must never
            -- stay there (see the sweep below)
            if item then item:getModData()[TOOL_MARK] = true end
        end
        return c
    end)
    if ok and made then
        BT._virtualContainers[key] = made
        log("built virtual tool container for " .. key .. " (" .. tostring(#cfg.items) .. " items)")
        return made
    end
    log("FAILED to build virtual tool container for " .. key)
    return nil
end

-- craft-query flag: only while a craft panel is gathering containers do we inject the tools, so
-- the loot window and other getContainers callers never see them.
BT._inCraftQuery = false

local function wrapGetContainers()
    if not ISInventoryPaneContextMenu or ISInventoryPaneContextMenu._kbwcbBenchTools then return end
    local original = ISInventoryPaneContextMenu.getContainers
    if not original then return end
    ISInventoryPaneContextMenu.getContainers = function(character)
        local list = original(character)
        if BT._inCraftQuery and list and character then
            local cfg = BT.adjacentBenchConfig(character)
            if cfg then
                local container = BT.virtualContainerFor(cfg)
                if container then list:add(container) end
            end
        end
        return list
    end
    ISInventoryPaneContextMenu._kbwcbBenchTools = true
    log("wrapped getContainers")
end

-- Set the craft-query flag around the two craft panels' container refresh (both call
-- getContainers then logic:setContainers), scoping the injection to crafting.
local function wrapCraftPanels()
    if ISHandCraftPanel and ISHandCraftPanel.updateContainers and not ISHandCraftPanel._kbwcbBenchTools then
        local original = ISHandCraftPanel.updateContainers
        ISHandCraftPanel.updateContainers = function(self, ...)
            BT._inCraftQuery = true
            local ok, result = pcall(original, self, ...)
            BT._inCraftQuery = false
            if not ok then error(result) end
            return result
        end
        ISHandCraftPanel._kbwcbBenchTools = true
    end
    if ISCraftLogicPanel and ISCraftLogicPanel.updateContainers and not ISCraftLogicPanel._kbwcbBenchTools then
        local original = ISCraftLogicPanel.updateContainers
        ISCraftLogicPanel.updateContainers = function(self, ...)
            BT._inCraftQuery = true
            local ok, result = pcall(original, self, ...)
            BT._inCraftQuery = false
            if not ok then error(result) end
            return result
        end
        ISCraftLogicPanel._kbwcbBenchTools = true
    end
end

-- stage property: tags the bench object with its config on build / load. No container is seeded.
local okP, Properties = pcall(require, "KnoxBuildworks/Definitions/Properties")
if okP and type(Properties) == "table" and Properties.register then
    Properties.register("kbwcbBenchTools", {
        normalize = function(value, stage, definition, addError)
            if type(value) ~= "table" or type(value.items) ~= "table" then
                addError("must be { items = { \"Module.Item\", ... }, category = \"...\" }")
            end
            return value
        end,
        applyToObject = function(part, buildObj, stage, context)
            if not part then return end
            local cfg = stage.kbwcbBenchTools
            local copy = { items = {}, category = cfg.category, labelKey = cfg.labelKey }
            for index = 1, #cfg.items do copy.items[index] = cfg.items[index] end
            part:getModData()[CONFIG_KEY] = copy
            pcall(function() part:transmitModData() end)
        end,
    })
    log("registered stage property kbwcbBenchTools")
else
    log("Knox Buildworks Properties not found; stage property not registered")
end

-- craft-speed bonus: crafting at a workstation of the recipe's type is SPEED_MULTIPLIER faster.
-- Wrap ISHandcraftAction:getDuration (the single place craft time is decided) and scale the result
-- when the player is adjacent to a configured bench whose category == the recipe's category.
local function wrapCraftSpeed()
    if not ISHandcraftAction or ISHandcraftAction._kbwcbBenchSpeed then return end
    local original = ISHandcraftAction.getDuration
    if not original then return end
    ISHandcraftAction.getDuration = function(self, ...)
        local dur = original(self, ...)
        -- only scale a real, positive duration (instant actions return 1; no recipe returns -1)
        if type(dur) == "number" and dur > 1 and self and self.character and self.craftRecipe then
            local ok, category = pcall(function() return self.craftRecipe:getCategory() end)
            if ok and category then
                local cfg = BT.adjacentBenchConfig(self.character, category)
                if cfg then
                    return dur * BT.SPEED_MULTIPLIER
                end
            end
        end
        return dur
    end
    ISHandcraftAction._kbwcbBenchSpeed = true
    log("wrapped ISHandcraftAction:getDuration (workstation speed bonus)")
end

-- ---- anti-duplication -------------------------------------------------------------------------
-- The B42 craft flow moves tool items from nearby containers into the player's inventory before
-- the craft and back afterwards. If the craft is cancelled (walking away), a bench tool stayed in
-- the inventory: free tools. Bench tools are marked (TOOL_MARK); once the player has no craft or
-- transfer queued, any marked item they hold (bags included) is deleted and the bench's tool set
-- is rebuilt. Marked items may never be transferred anywhere but the player's main inventory.

local function isBenchTool(item)
    if not item or not item.hasModData or not item:hasModData() then return false end
    return item:getModData()[TOOL_MARK] == true
end
BT.isBenchTool = isBenchTool

local function busyCrafting(character)
    local okQ, queue = pcall(function() return ISTimedActionQueue.getTimedActionQueue(character) end)
    if not okQ or type(queue) ~= "table" or type(queue.queue) ~= "table" then return false end
    for index = 1, #queue.queue do
        local action = queue.queue[index]
        local kind = type(action) == "table" and action.Type or nil
        if kind == "ISHandcraftAction" or kind == "ISInventoryTransferAction" then return true end
    end
    return false
end

local function collectMarked(container, out)
    local items = container:getItems()
    for index = 0, items:size() - 1 do
        local item = items:get(index)
        if isBenchTool(item) then
            out[#out + 1] = { item = item, container = container }
        elseif item and item.IsInventoryContainer and item:IsInventoryContainer() then
            collectMarked(item:getInventory(), out)
        end
    end
end

-- remove every bench tool the character holds; returns how many were removed
function BT.sweep(character)
    if not character or busyCrafting(character) then return 0 end
    local found = {}
    local okC = pcall(collectMarked, character:getInventory(), found)
    if not okC then return 0 end
    for index = 1, #found do
        local entry = found[index]
        pcall(function()
            if character:isEquipped(entry.item) then character:removeFromHands(entry.item) end
        end)
        pcall(function() entry.container:DoRemoveItem(entry.item) end)
        pcall(function() sendRemoveItemFromContainer(entry.container, entry.item) end)
    end
    if #found > 0 then
        BT._virtualContainers = {}          -- rebuild the tool sets with fresh items
        pcall(function() ISInventoryPage.dirtyUI() end)
        log("returned " .. tostring(#found) .. " bench tool(s) left in the inventory")
    end
    return #found
end

BT._sweepPending = {}

local function wrapCraftEnd()
    if not ISHandcraftAction or ISHandcraftAction._kbwcbBenchSweep then return end
    local function mark(self)
        if self and self.character then BT._sweepPending[self.character] = true end
    end
    for _, name in ipairs({ "stop", "perform", "forceStop" }) do
        local original = ISHandcraftAction[name]
        if type(original) == "function" then
            ISHandcraftAction[name] = function(self, ...)
                mark(self)
                return original(self, ...)
            end
        end
    end
    ISHandcraftAction._kbwcbBenchSweep = true
end

local function wrapTransfer()
    if not ISInventoryTransferAction or ISInventoryTransferAction._kbwcbBenchTools then return end
    local original = ISInventoryTransferAction.isValid
    if type(original) ~= "function" then return end
    ISInventoryTransferAction.isValid = function(self, ...)
        if self and isBenchTool(self.item) and self.character then
            local dest = self.destContainer
            if dest ~= self.character:getInventory() then return false end
        end
        return original(self, ...)
    end
    ISInventoryTransferAction._kbwcbBenchTools = true
end

-- deferred sweep: once the craft (and its return transfers) are off the queue
local function onPlayerUpdate(character)
    if not BT._sweepPending[character] then return end
    if busyCrafting(character) then return end
    BT._sweepPending[character] = nil
    BT.sweep(character)
end

local function everyMinute()
    for index = 0, getNumActivePlayers() - 1 do
        local player = getSpecificPlayer(index)
        if player then BT.sweep(player) end
    end
end

local function install()
    wrapGetContainers()
    wrapCraftPanels()
    wrapCraftSpeed()
    wrapCraftEnd()
    wrapTransfer()
end

Events.OnPlayerUpdate.Add(onPlayerUpdate)
Events.EveryOneMinute.Add(everyMinute)

Events.OnGameBoot.Add(install)
Events.OnGameStart.Add(install)
if Events.OnServerStarted then Events.OnServerStarted.Add(install) end
'''

_CLIENT = r'''-- AUTO-GENERATED by pz_craft_loops/bench_tools.py -- do not edit by hand.
-- Right-click a workbench with built-in tools -> open the vanilla craft window on its category.
require "TimedActions/ISBaseTimedAction"
local BT = KBWCommunityBenchTools

KBWCBOpenBenchAction = ISBaseTimedAction:derive("KBWCBOpenBenchAction")

function KBWCBOpenBenchAction:isValid() return self.bench ~= nil end
function KBWCBOpenBenchAction:waitToStart()
    self.character:faceThisObject(self.bench)
    return self.character:shouldBeTurning()
end
function KBWCBOpenBenchAction:start() end
function KBWCBOpenBenchAction:update() end
function KBWCBOpenBenchAction:stop() ISBaseTimedAction.stop(self) end
function KBWCBOpenBenchAction:perform()
    local cfg = BT and BT.configOf(self.bench) or nil
    ISEntityUI.OpenHandcraftWindow(self.character, nil)
    local category = cfg and cfg.category or nil
    if category then
        pcall(function()
            local window = ISEntityUI.GetWindowInstance(self.character:getPlayerNum(), "HandcraftWindow")
            local panel = window and window.handCraftPanel or nil
            if panel then
                if panel.recipeCategories then panel.recipeCategories.selectedCategory = category end
                panel:onCategoryChanged(category)
            end
        end)
    end
    ISBaseTimedAction.perform(self)
end
function KBWCBOpenBenchAction:new(character, bench)
    local o = ISBaseTimedAction.new(self, character)
    o.bench = bench
    o.maxTime = 1
    o.stopOnWalk = true
    o.stopOnRun = true
    return o
end

local function findBench(worldobjects)
    for index = 1, #worldobjects do
        local object = worldobjects[index]
        if object and BT.configOf(object) then return object end
        local square = object and object:getSquare() or nil
        if square then
            local objects = square:getObjects()
            for j = 0, objects:size() - 1 do
                local other = objects:get(j)
                if other and BT.configOf(other) then return other end
            end
        end
    end
    return nil
end

local function onOpen(worldobjects, playerNum, bench)
    local playerObj = getSpecificPlayer(playerNum)
    if not playerObj or not bench then return end
    local square = bench:getSquare()
    if square and luautils.walkAdj(playerObj, square, true) then
        ISTimedActionQueue.add(KBWCBOpenBenchAction:new(playerObj, bench))
    end
end

local function onFillMenu(playerNum, context, worldobjects, test)
    if test or not BT then return end
    local bench = findBench(worldobjects)
    if not bench then return end
    local cfg = BT.configOf(bench)
    local label = cfg.labelKey and getText(cfg.labelKey) or tostring(cfg.category)
    context:addOptionOnTop(label, worldobjects, onOpen, playerNum, bench)
end

Events.OnFillWorldObjectContextMenu.Add(onFillMenu)
'''


def _check(lua, name):
    for bad in ("next(", "goto ", "//", "debug."):
        if bad in lua.replace("-- AUTO-GENERATED", ""):
            raise RuntimeError("Kahlua-unsafe construct in %s: %s" % (name, bad))


BENCH_DEFS = r"c:\Users\josep\Kiro\zomboid\communitytilepack\deliverables\56_community_fears_workbenches.json"


def _strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, list):
        for x in o:
            yield from _strings(x)
    elif isinstance(o, dict):
        for x in o.values():
            yield from _strings(x)


def _lua_str(s):
    return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')


def _compose_shared():
    """The shared Lua with the sprite -> category and category -> config tables filled in. Benches
    are recognised by their tile as well as by modData, so a bench that was picked up and placed
    again (a plain moveable object, no modData) still works."""
    import json
    doc = json.load(open(BENCH_DEFS, encoding="utf-8"))
    sprites = {}
    for b in doc.get("buildables", []):
        cfg = BENCH_TOOLS.get(b.get("id"))
        if not cfg:
            continue
        for st in b.get("stages") or []:
            for s in _strings(st.get("geometry")):
                sprites[s] = cfg["category"]
    lines = ["BT.SPRITE_CATEGORY = {"]
    for s in sorted(sprites):
        lines.append("    [%s] = %s," % (_lua_str(s), _lua_str(sprites[s])))
    lines.append("}")
    lines.append("BT.CATEGORY_CFG = {")
    done = set()
    for cfg in BENCH_TOOLS.values():
        if cfg["category"] in done:
            continue
        done.add(cfg["category"])
        items = ", ".join(_lua_str(i) for i in cfg["items"])
        lines.append("    [%s] = { category = %s, labelKey = %s, items = { %s } }," % (
            _lua_str(cfg["category"]), _lua_str(cfg["category"]), _lua_str(cfg["labelKey"]), items))
    lines.append("}")
    if not sprites:
        raise RuntimeError("bench_tools: no bench sprites found in %s" % BENCH_DEFS)
    return _SHARED.replace("--@BENCH_MAPS@--", "\n".join(lines))


def write_assets(media_dir):
    """Write the shared + client Lua into <media_dir>. No item script needed (runtime uses real
    vanilla items), so the old KBWCommunity_BenchTools.txt scripts file is removed if present."""
    for sub, name, text in (("shared", SHARED_LUA, _compose_shared()), ("client", CLIENT_LUA, _CLIENT)):
        _check(text, name)
        p = os.path.join(media_dir, "lua", sub, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8", newline="\n").write(text)
    stale = os.path.join(media_dir, "scripts", "KBWCommunity_BenchTools.txt")
    if os.path.isfile(stale):
        os.remove(stale)


def apply_to_buildables(buildables):
    """For each configured bench: (1) write the kbwcbBenchTools stage property (runtime tool set),
    and (2) add the build cost -- one consumed input per core tool tag, accepting any member item.
    Returns the list of bench ids changed."""
    changed = []
    for b in buildables:
        cfg = BENCH_TOOLS.get(b.get("id"))
        if not cfg:
            continue
        tags = cfg["tags"]
        for st in b.get("stages") or []:
            st["kbwcbBenchTools"] = {"items": list(cfg["items"]), "category": cfg["category"],
                                     "labelKey": cfg["labelKey"]}
            req = st.get("requirements")
            if not isinstance(req, dict):
                continue
            inputs = req.get("inputs")
            if not isinstance(inputs, list):
                # recipe uses a materialGroup ref; materialize an inputs list we can extend so the
                # tool cost is added without disturbing the referenced materials.
                inputs = []
                req["inputs"] = inputs
            existing = {inp.get("id") for inp in inputs if isinstance(inp, dict)}
            for t in tags:
                iid = "benchtool_" + t
                if iid in existing:
                    continue
                # matches KBW VE's proven pattern of inline extra inputs alongside a materialGroup
                # (see appliances/bathroom.json): role "component", mode consume, items[...] alts.
                inputs.append({
                    "id": iid,
                    "role": "component",
                    "mode": "consume",
                    "items": list(TAG_MEMBERS[t]),
                    "amount": 1,
                })
        changed.append(b["id"])
    return changed
