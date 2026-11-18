"""Mock test for BC_TakePinned (tested against mocks, NOT in game).
Runs the real client Lua under lupa with PZ APIs faked. `next` is deleted first because Kahlua has none.
Run: python tests/test_take_pinned.py
"""
import os
import sys
from lupa import LuaRuntime

HERE = os.path.dirname(os.path.abspath(__file__))
LUA_FILE = os.path.join(HERE, "..", "42", "media", "lua", "client", "BC_TakePinned.lua")

MOCKS = r"""
next = nil          -- Kahlua has no next()
goto_removed = true

QUEUE = {}
HALO = {}

-- ---- class helper -------------------------------------------------------------------------
local function derive(base, name)
    local c = {}
    for k, v in pairs(base) do c[k] = v end
    c.Type = name
    c.__index = c
    c.derive = base.derive
    return c
end

ISLootWindowObjectControlHandler = { Type = "ISLootWindowObjectControlHandler" }
ISLootWindowObjectControlHandler.derive = derive
function ISLootWindowObjectControlHandler:new()
    local o = setmetatable({}, self); self.__index = self; return o
end
function ISLootWindowObjectControlHandler:getButtonControl(title)
    self.control = self.control or { setTooltip = function(s, t) s.tip = t end }
    self.control.title = title
    return self.control
end
function ISLootWindowObjectControlHandler:addJoypadContextMenuOption(ctx, t) end

ISLootWindowFloorControlHandler = { Type = "ISLootWindowFloorControlHandler" }
ISLootWindowFloorControlHandler.derive = derive
function ISLootWindowFloorControlHandler:new()
    local o = setmetatable({}, self); self.__index = self; return o
end
ISLootWindowFloorControlHandler.getButtonControl = ISLootWindowObjectControlHandler.getButtonControl
ISLootWindowFloorControlHandler.addJoypadContextMenuOption = ISLootWindowObjectControlHandler.addJoypadContextMenuOption

REG_OBJ, REG_FLOOR = {}, {}
ISLootWindowContainerControls = {
    AddHandler = function(c) REG_OBJ[#REG_OBJ + 1] = c end,
    AddFloorHandler = function(c) REG_FLOOR[#REG_FLOOR + 1] = c end,
}

-- ---- PZ globals -----------------------------------------------------------------------------
function getCore() return { isTutorial = function() return false end } end
function isGamePaused() return false end
function getTextOrNull(key) return nil end
UIFont = { Small = 1 }
function getTextManager() return { getFontHeight = function() return 14 end } end
ISButton = {}
function ISButton:new(x, y, w, h, title, target, onclick, onmousedown, allowUp)
    local o = { target = target, onclick = onclick, onmousedown = onmousedown, title = title }
    function o:setTitle(t) self.title = t end
    function o:setWidthToTitle() end
    function o:setTooltip(t) self.tip = t end
    return o
end
HaloTextHelper = {
    addGoodText = function(p, t) HALO[#HALO + 1] = "good:" .. t end,
    addBadText = function(p, t) HALO[#HALO + 1] = "bad:" .. t end,
}
function instanceof(o, cls) return o ~= nil and type(o) == "table" and o.__is and o.__is[cls] == true end

ISTimedActionQueue = { add = function(a) QUEUE[#QUEUE + 1] = a end }
ISInventoryTransferUtil = {
    newInventoryTransferAction = function(p, item, src, dest)
        return { kind = "transfer", item = item, src = src, dest = dest }
    end,
}
ISWalkToTimedAction = {}
function ISWalkToTimedAction:new(p, sq) return { kind = "walk", sq = sq } end
AdjacentFreeTileFinder = { Find = function(sq, p) return { name = "adj" } end }

-- ---- model ----------------------------------------------------------------------------------
local function list(t)
    return { size = function(self) return #t end, get = function(self, i) return t[i + 1] end }
end

function newContainer(spec)
    local c = { type = spec.type or "crate", items = {}, cap = spec.cap or 100, inChar = spec.inChar or false }
    c.getItems = function(self) return list(self.items) end
    c.getType = function(self) return self.type end
    c.getParent = function(self) return self.parentObj end
    c.isInCharacterInventory = function(self, p) return self.inChar end
    c.isItemAllowed = function(self, it) return true end
    c.isInside = function(self, it) return false end
    c.used = function(self)
        local w = 0
        for _, it in ipairs(self.items) do w = w + it.weight end
        return w
    end
    c.hasRoomFor = function(self, p, a, b)
        local add = type(a) == "number" and a or a.weight
        return self:used() + add <= self.cap
    end
    c.getVehiclePart = function() return nil end
    c.getContainingItem = function(self) return self.containingItem end
    if spec.far then
        c.parentObj = { getSquare = function() return { DistToProper = function() return spec.far end } end }
    elseif spec.near then
        c.parentObj = { getSquare = function() return { DistToProper = function() return 0.5 end } end }
    end
    return c
end

function newItem(spec)
    local it = {
        full = spec.full, weight = spec.weight or 1, equipped = spec.equipped or false,
        __is = { InventoryContainer = spec.bag and true or false },
    }
    it.getFullType = function(self) return self.full end
    it.getContainer = function(self) return self.container end
    it.isEquipped = function(self) return self.equipped end
    it.isHumanCorpse = function(self) return false end
    it.isUnwanted = function(self, p) return false end
    it.getUnequippedWeight = function(self) return self.weight end
    it.getOutermostContainer = function(self)
        local c = self.container
        while c and c.containingItem do c = c.containingItem.container end
        return c
    end
    if spec.bag then
        it.getInventory = function(self) return self.inner end
        it.inner = newContainer({ type = "bag", cap = spec.bagCap or 50 })
        it.inner.containingItem = it
    end
    return it
end

function put(container, item)
    container.items[#container.items + 1] = item
    item.container = container
    return item
end

PLAYER = {
    getCurrentSquare = function() return { name = "me" } end,
    getVehicle = function() return nil end,
}
function getSpecificPlayer(n) return PLAYER end

function setup(opts)
    QUEUE, HALO = {}, {}
    PINNED = opts.pinned
    package.loaded["BetterContainers/Upgrades/PinnedItems"] = {
        FavouritedItems = PINNED,
        isFavourite = function(ft) return PINNED[ft] == true end,
        isLoaded = function() return true end,
        load = function() end,
    }
end
"""

RUNNER = r"""
-- fake require: PZ modules are no-ops, BC module comes from package.loaded
local realRequire = require
function require(name)
    if package.loaded[name] then return package.loaded[name] end
    if string.find(name, "BetterContainers/", 1, true) then error("module not found: " .. name) end
    return true
end
"""


def lua():
    L = LuaRuntime(unpack_returned_tuples=True)
    L.execute(MOCKS)
    L.execute(RUNNER)
    with open(LUA_FILE, "r", encoding="utf-8") as f:
        L.execute(f.read())
    return L


failures = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (("  " + str(detail)) if (detail and not cond) else ""))
    if not cond:
        failures.append(name)


def scenario_basic():
    L = lua()
    L.execute(r"""
    setup({ pinned = { ["Base.Hammer"] = true, ["Base.Nails"] = true, ["Base.Duffel"] = true } })

    -- destination: the bag the player has open
    DEST = newContainer({ type = "bag", cap = 100, inChar = true })

    CRATE  = newContainer({ type = "crate", near = true })
    FLOOR  = newContainer({ type = "floor" })
    PROX   = newContainer({ type = "proximityInv" })     -- BC virtual view
    OWN    = newContainer({ type = "bag", inChar = true })

    h1 = put(CRATE, newItem({ full = "Base.Hammer" }))
    put(CRATE, newItem({ full = "Base.Saw" }))              -- not pinned
    bag = put(CRATE, newItem({ full = "Base.Sack", bag = true }))
    n1 = put(bag.inner, newItem({ full = "Base.Nails" }))    -- nested pinned
    put(bag.inner, newItem({ full = "Base.Rope" }))
    f1 = put(FLOOR, newItem({ full = "Base.Hammer" }))       -- floor pinned
    fbag = put(FLOOR, newItem({ full = "Base.Sack", bag = true }))
    fn = put(fbag.inner, newItem({ full = "Base.Nails" }))   -- nested on floor
    ownH = put(OWN, newItem({ full = "Base.Hammer" }))       -- already carried
    -- worn by a zombie corpse: isEquipped is true there too, and it is taken (in game 2026-11-17)
    CORPSE = newContainer({ type = "inventorymale", near = true })
    eq = put(CORPSE, newItem({ full = "Base.Hammer", equipped = true }))
    ownEq = put(OWN, newItem({ full = "Base.Hammer", equipped = true }))   -- the player's own: skipped

    -- BC proximity view repeats the real items of the crate and floor (same refs)
    for _, it in ipairs(CRATE.items) do PROX.items[#PROX.items + 1] = it end
    for _, it in ipairs(FLOOR.items) do PROX.items[#PROX.items + 1] = it end

    LOOT = { backpacks = { { inventory = PROX }, { inventory = CRATE }, { inventory = FLOOR }, { inventory = CORPSE } },
             inventoryPane = { inventory = PROX } }
    INV = { inventoryPane = { inventory = DEST } }
    function getPlayerInventory(n) return INV end

    FOUND = BC_TakePinned.collect(PLAYER, LOOT, DEST)
    """)
    found = L.eval("FOUND")
    names = sorted(("%s" % found[i + 1].full) for i in range(len(found)))
    check("collect finds crate hammer, nested nails, floor hammer, floor-nested nails, corpse-worn hammer (5)",
          len(found) == 5, names)
    check("no duplicates from proximity view", L.eval("(function() local s,c={},0 for _,i in ipairs(FOUND) do if s[i] then return false end s[i]=true end return true end)()"))
    check("skips item already in player inventory", not L.eval("(function() for _,i in ipairs(FOUND) do if i==ownH then return true end end return false end)()"))
    check("takes an item worn by a corpse", L.eval("(function() for _,i in ipairs(FOUND) do if i==eq then return true end end return false end)()"))
    check("skips the player's own equipped item", not L.eval("(function() for _,i in ipairs(FOUND) do if i==ownEq then return true end end return false end)()"))

    L.execute("BC_TakePinned.run(0, LOOT)")
    kinds = [L.eval("QUEUE[%d].kind" % (i + 1)) for i in range(L.eval("#QUEUE"))]
    check("5 transfers queued", kinds.count("transfer") == 5, kinds)
    check("all transfers target the active bag", L.eval("(function() for _,a in ipairs(QUEUE) do if a.kind=='transfer' and a.dest~=DEST then return false end end return true end)()"))
    check("nested item is transferred from its bag", L.eval("(function() for _,a in ipairs(QUEUE) do if a.item==n1 and a.src==bag.inner then return true end end return false end)()"))
    check("halo reports success", L.eval("HALO[1]") and str(L.eval("HALO[1]")).startswith("good:"), L.eval("HALO[1]"))


def scenario_capacity():
    L = lua()
    L.execute(r"""
    setup({ pinned = { ["Base.Anvil"] = true } })
    DEST = newContainer({ type = "bag", cap = 25, inChar = true })
    CRATE = newContainer({ type = "crate", near = true })
    for i = 1, 4 do put(CRATE, newItem({ full = "Base.Anvil", weight = 10 })) end
    LOOT = { backpacks = { { inventory = CRATE } }, inventoryPane = { inventory = CRATE } }
    INV = { inventoryPane = { inventory = DEST } }
    function getPlayerInventory(n) return INV end
    BC_TakePinned.run(0, LOOT)
    """)
    n = L.eval("(function() local c=0 for _,a in ipairs(QUEUE) do if a.kind=='transfer' then c=c+1 end end return c end)()")
    check("only items that fit are queued (2 of 4 at 10 each into cap 25)", n == 2, n)
    halos = [str(L.eval("HALO[%d]" % (i + 1))) for i in range(L.eval("#HALO"))]
    check("no-room warning shown", any(h.startswith("bad:No room for 2") for h in halos), halos)


def scenario_walk_order():
    L = lua()
    L.execute(r"""
    setup({ pinned = { ["Base.Hammer"] = true } })
    DEST = newContainer({ type = "bag", cap = 100, inChar = true })
    FARCRATE = newContainer({ type = "crate", far = 6 })
    NEARCRATE = newContainer({ type = "crate", near = true })
    fa = put(FARCRATE, newItem({ full = "Base.Hammer" }))
    ne = put(NEARCRATE, newItem({ full = "Base.Hammer" }))
    LOOT = { backpacks = { { inventory = FARCRATE }, { inventory = NEARCRATE } },
             inventoryPane = { inventory = FARCRATE } }
    INV = { inventoryPane = { inventory = DEST } }
    function getPlayerInventory(n) return INV end
    BC_TakePinned.run(0, LOOT)
    """)
    order = [str(L.eval("QUEUE[%d].kind" % (i + 1))) + ":" + ("near" if L.eval("QUEUE[%d].item == ne" % (i + 1)) else ("far" if L.eval("QUEUE[%d].item == fa" % (i + 1)) else "")) for i in range(L.eval("#QUEUE"))]
    check("nearest container first, walk queued before the far container's transfer",
          order == ["transfer:near", "walk:", "transfer:far"], order)


def scenario_pinned_bag_not_recursed():
    L = lua()
    L.execute(r"""
    setup({ pinned = { ["Base.Duffel"] = true, ["Base.Nails"] = true } })
    DEST = newContainer({ type = "bag", cap = 100, inChar = true })
    CRATE = newContainer({ type = "crate", near = true })
    duf = put(CRATE, newItem({ full = "Base.Duffel", bag = true }))
    put(duf.inner, newItem({ full = "Base.Nails" }))
    LOOT = { backpacks = { { inventory = CRATE } }, inventoryPane = { inventory = CRATE } }
    INV = { inventoryPane = { inventory = DEST } }
    function getPlayerInventory(n) return INV end
    FOUND = BC_TakePinned.collect(PLAYER, LOOT, DEST)
    """)
    check("pinned bag is taken, its contents are not listed separately", L.eval("#FOUND") == 1, L.eval("#FOUND"))


def scenario_no_bc():
    L = LuaRuntime(unpack_returned_tuples=True)
    L.execute(MOCKS)
    L.execute(RUNNER)
    L.execute('package.loaded["BetterContainers/Upgrades/PinnedItems"] = nil')
    with open(LUA_FILE, "r", encoding="utf-8") as f:
        L.execute(f.read())
    check("without BC pins module, hasAnyPin is false and nothing crashes", L.eval("BC_TakePinned.hasAnyPin()") is False)


def scenario_handlers():
    L = lua()
    L.execute('setup({ pinned = {} })')
    check("handlers registered (object + floor)", L.eval("#REG_OBJ") == 1 and L.eval("#REG_FLOOR") == 1)
    check("button hidden when nothing is pinned", L.eval("REG_FLOOR[1].shouldBeVisible({}) == false"))
    L.execute('PINNED["Base.Hammer"] = true')
    check("button visible when something is pinned", L.eval("REG_FLOOR[1].shouldBeVisible({}) == true"))


def scenario_button():
    # 2026-11-17: our own ISButton; its mouse-down slot is cleared on each layout and a click reaches perform
    L = lua()
    L.execute('setup({ pinned = { ["Base.Hammer"] = true } })')
    r = L.execute(r'''
    local h = REG_OBJ[1]:new()
    h.playerNum = 0
    local b = h:getControl()
    b.onmousedown = 1.0                 -- what the in-game error showed
    b = h:getControl()                  -- the next layout clears it
    local performed = false
    local orig = BC_TakePinned.run
    BC_TakePinned.run = function() performed = true end
    b.onclick(b.target, b)
    BC_TakePinned.run = orig
    return tostring(b.onmousedown == nil) .. " " .. tostring(performed) .. " " .. tostring(b.title)
    ''')
    check("button: onmousedown cleared, click reaches perform", r == "true true Take Pinned", r)


for fn in (scenario_basic, scenario_capacity, scenario_walk_order,
           scenario_pinned_bag_not_recursed, scenario_no_bc, scenario_handlers, scenario_button):
    fn()

print()
print("RESULT:", "ALL PASS" if not failures else "FAILURES: %s" % failures)
sys.exit(1 if failures else 0)
