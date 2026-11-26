"""Mock test (lupa, next removed) for WorldEssentialsTakePinned.lua: WE's upstream copy vs our work/ fix.
Simulates the MP timing: a transfer action leaves the queue first, and the server's container sync
moves the item (as a NEW object in the destination) SYNC_TICKS later. Also SP (immediate) and a
cancelled transfer (item never moves). Not a game test."""
import lupa

UP = r"c:\Users\josep\Kiro\zomboid\WE_submods\upstream\World Essentials (base, our files only)\42\media\lua\client\WorldEssentialsTakePinned.lua"
WK = r"c:\Users\josep\Kiro\zomboid\WE_submods\work\World Essentials (base, our files only)\42\media\lua\client\WorldEssentialsTakePinned.lua"

MOCK = r'''
next = nil
local T = 0
function getTimestampMs() return T end
local ticks = {}
Events = { OnTick = { Add = function(f) ticks[f] = true end, Remove = function(f) ticks[f] = nil end } }
function getActivatedMods() return { contains = function(_, id) return id == "EURY_CONTAINERS" end } end
local PIN = { isFavourite = function(t) return t == "Base.Pinned" end, FavouritedItems = { ["Base.Pinned"] = true } }
function require(name) if name == "BetterContainers/Upgrades/PinnedItems" then return PIN end return true end
function instanceof(o, cls) return type(o) == "table" and o._class == cls end
function isForceDropHeavyItem() return false end
function getCore() return { isTutorial = function() return false end } end
function getTextManager() return { getFontHeight = function() return 10 end } end
UIFont = { Small = 1 }
ISButton = { new = function() return {} end }
local function derive() return { derive = derive } end
ISLootWindowObjectControlHandler = { derive = function() return {} end }
ISLootWindowFloorControlHandler = { derive = function() return {} end }
ISLootWindowContainerControls = { AddHandler = function() end, AddFloorHandler = function() end }

-- containers
local function Container(kind)
    local c = { list = {}, kind = kind }
    function c:getItems() local l = self.list
        return { size = function() return #l end, get = function(_, i) return l[i + 1] end } end
    function c:contains(it) for _, x in ipairs(self.list) do if x == it then return true end end return false end
    function c:remove(it) for i, x in ipairs(self.list) do if x == it then table.remove(self.list, i) return end end end
    function c:add(it) self.list[#self.list + 1] = it; it._c = self end
    function c:isInCharacterInventory() return self.kind == "inv" end
    function c:getType() return self.kind end
    function c:getParent() return nil end
    function c:isInside() return false end
    function c:isItemAllowed() return true end
    function c:hasRoomFor() return true end
    return c
end
local function Item()
    local it = { _class = "InventoryItem" }
    function it:getContainer() return self._c end
    function it:getFullType() return "Base.Pinned" end
    function it:isHumanCorpse() return false end
    function it:isUnwanted() return false end
    function it:getOutermostContainer() return nil end
    function it:getUnequippedWeight() return 0.1 end
    return it
end

local player = { isDead = function() return false end, getCurrentSquare = function() return nil end }
function getSpecificPlayer() return player end
local dest = Container("inv")
local page = { inventoryPane = { inventory = dest } }
function getPlayerInventory() return page end
local queue = { queue = {} }
ISTimedActionQueue = { getTimedActionQueue = function() return queue end,
    add = function(a) queue.queue[#queue.queue + 1] = a end }
ISInventoryTransferUtil = { newInventoryTransferAction = function(_, item, src, dst)
    return { item = item, src = src, dst = dst } end }

MODE = "mp"; SYNC_TICKS = 4
local pendingSync = {}
function runTick()
    T = T + 16
    -- the current action finishes this tick (client side)
    local a = queue.queue[1]
    if a then
        table.remove(queue.queue, 1)
        if MODE == "sp" then a.src:remove(a.item); a.dst:add(a.item)
        elseif MODE == "mp" then pendingSync[#pendingSync + 1] = { a = a, at = T + SYNC_TICKS * 16 } end
        -- MODE == "cancel": nothing moves
    end
    for i = #pendingSync, 1, -1 do
        local p = pendingSync[i]
        if T >= p.at then
            p.a.src:remove(p.a.item)
            local fresh = Item(); p.a.dst:add(fresh)          -- server sync: a new object
            table.remove(pendingSync, i)
        end
    end
    for f in pairs(ticks) do f() end
end
function setup(n)
    local src = Container("floor")
    for _ = 1, n do src:add(Item()) end
    return { backpacks = { { inventory = src } }, getIsVisible = function() return true end }, src
end
function reset() dest.list = {}; queue.queue = {}; pendingSync = {}; for f in pairs(ticks) do ticks[f] = nil end end
function destCount() return #dest.list end
'''

DRIVER = r'''
return function(mode, n)
    reset(); MODE = mode
    local loot, src = setup(n)
    BC_TakePinned.run(0, loot)
    local t0 = getTimestampMs()
    local stoppedAt = nil
    for _ = 1, 2000 do
        runTick()
        if not BC_TakePinned.isRunning(0) and not stoppedAt then stoppedAt = getTimestampMs() - t0 end
    end
    return destCount(), #src.list, stoppedAt or -1
end
'''


def run(path, mode, n=8):
    L = lupa.LuaRuntime(unpack_returned_tuples=True)
    L.execute(MOCK)
    L.execute(open(path, encoding="utf-8").read())
    return L.execute(DRIVER)(mode, n)


for label, path in (("WE upstream", UP), ("work fix   ", WK)):
    for mode in ("sp", "mp", "cancel"):
        moved, left, stop = run(path, mode)
        print("%s  %-6s moved %d of 8, left at source %d, run ended after %d ms" % (label, mode, moved, left, stop))
