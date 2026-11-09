# -*- coding: utf-8 -*-
"""Generate 38_tikitown_props14.json: the rest of Drazion's tikitown-props-14 (8 cols; art only in
tikitown_tiles.pack). Soundproofing (8-11, 17-19) is 37_tikitown_soundproof.json; the multi-part
statue (24-26, 32-34 and below) is skipped (user, 2026-08-28).

Pieces (user's sheet map, checked against the tile data and the extracted art):
  1  desk microphone      0-3   1 tile, 4 facings   (pack Facing E,S,W,N; GroupName "Professional Microphone")
  2  small mixer board    4-7   1 tile, 4 facings   (pack Facing N,E,S,W; "Blue Mixer Board")
  3  large mixer board    12-15 2 tiles, 2 facings  ("Teal Mixer Board"). Both pairs join only along
                                Y (art composited both ways): 13 at y0 + 12 at y1, 15 at y0 + 14 at y1,
                                so it runs N-S and faces E / W. The pack's Facing (N,N,S,S) is wrong.
                                E = 13/12 (low front lip toward the camera), W = 15/14 (tall back
                                toward the camera) -- read from the art, VERIFY IN GAME.
  4  electrical cabinet   16    1 tile, 1 facing. The tile carries only `solid`: no CustomName,
                                GroupName or Facing, so the name is ours. Warning labels on the
                                south (left) face, vent on the east face -> face S.
                                Since 2026-11-08 a WORKING GENERATOR ("Electrical Cabinet
                                Generator", see generator_cabinet): face S = 16, face E = our
                                mirrored copy (KBWTikiTownProps_0), one item script per facing.
  5  ATM                  20-22 1 tile, 3 facings. No Facing in the tile data (BlocksPlacement,
                                CanScrap, solidtrans). From the art: 21 screen on the south face,
                                22 screen on the east face, 20 back only -> north.
  6  coffee dispenser     27-30 1 tile, 4 facings   (pack Facing N,W,S,E; "Dispenser - Thermos")
  7  styrofoam cups       23 (single cup), 31 (cup stack): two buildables in one KBW group
                                (arrows in the build menu), not facings.

Single-tile 4-facing pieces: KBW face = the tile's Facing (same rule as the wardrobes/lockers).
Table-top pieces (mic, mixers, dispenser, cups) keep the pack's IsTableTop / IsSurfaceOffset, so they
sit on a counter or table like the TK coffee makers. Costs are first-pass (tunable).
"""
import json
import os

SHEET = "tikitown-props-14"
OUT = r"c:\Users\josep\Kiro\zomboid\tikitown\38_tikitown_props14.json"


def _spr(i):
    return "%s_%d" % (SHEET, i)


def _one(i):
    return {"layers": [{"rows": [[_spr(i)]]}]}


def _col2(a, b):
    # two tiles along Y (N-S run): a at y0, b at y1
    return {"layers": [{"rows": [[_spr(a)], [_spr(b)]]}]}


def _tool(tag, ident):
    return {"id": ident, "role": "tool", "mode": "keep", "resourceType": "Item", "tags": [tag], "amount": 1}


def _mat(n, item, amount):
    return {"id": "source_material_%d" % n, "role": "material", "mode": "consume",
            "resourceType": "Item", "items": [item], "amount": amount}


def _electronics(scrap, wire, small_sheet=0, sheet=0, screws=0):
    inputs = [_tool("base:screwdriver", "tool_screwdriver")]
    for item, amount in (("Base.SmallSheetMetal", small_sheet), ("Base.SheetMetal", sheet),
                         ("Base.Screws", screws), ("Base.ElectronicsScrap", scrap),
                         ("Base.ElectricWire", wire)):
        if amount:
            inputs.append(_mat(len(inputs), item, amount))
    return inputs


ELEC_BUILD = {"timedAction": "BuildWallNoTool", "completionSound": "BuildMetalStructureMedium",
              "category": "Electrical"}
TABLETOP = {"kind": "object", "requiresFloor": True}
FLOOR = {"kind": "object", "requiresFloor": True}

# (slug, name, category, subcategory, material, faces, placement, inputs, skills, time, xp,
#  object, group or None)
PIECES = [
    ("microphone", "Broadcast Desk Microphone", "Appliances", "Audio Equipment", "Metal",
     {"E": _one(0), "S": _one(1), "W": _one(2), "N": _one(3)}, TABLETOP,
     _electronics(scrap=3, wire=1, small_sheet=1), {"Electricity": 2}, 80, {"Electricity": 15},
     {"isThumpable": False, "canPassThrough": True, "dismantable": True}, None),
    ("mixer_small", "Small Mixer Board", "Appliances", "Audio Equipment", "Metal",
     {"N": _one(4), "E": _one(5), "S": _one(6), "W": _one(7)}, TABLETOP,
     _electronics(scrap=6, wire=2, small_sheet=1), {"Electricity": 3}, 120, {"Electricity": 20},
     {"isThumpable": False, "canPassThrough": True, "dismantable": True}, None),
    ("mixer_large", "Large Mixer Board", "Appliances", "Audio Equipment", "Metal",
     {"E": _col2(13, 12), "W": _col2(15, 14)}, TABLETOP,
     _electronics(scrap=12, wire=3, small_sheet=2), {"Electricity": 4}, 180, {"Electricity": 30},
     {"isThumpable": False, "canPassThrough": True, "dismantable": True}, None),
    ("electrical_cabinet", "Electrical Cabinet", "Appliances", "Electrical", "Metal",
     {"S": _one(16)}, FLOOR,
     _electronics(scrap=10, wire=4, sheet=2, screws=8), {"Electricity": 4}, 200, {"Electricity": 35},
     {"isThumpable": True, "dismantable": True}, None),
    ("atm", "ATM", "Appliances", "Electrical", "Metal",
     {"S": _one(21), "E": _one(22), "N": _one(20)}, FLOOR,
     _electronics(scrap=15, wire=4, sheet=4, screws=12), {"Electricity": 5}, 240, {"Electricity": 40},
     {"isThumpable": True, "dismantable": True}, None),
    ("coffee_dispenser", "Thermos Coffee Dispenser", "Furniture and Appliances", "Kitchen Appliances",
     "Metal", {"N": _one(27), "W": _one(28), "S": _one(29), "E": _one(30)}, TABLETOP,
     [_tool("base:screwdriver", "tool_screwdriver"), _mat(1, "Base.SmallSheetMetal", 1),
      _mat(2, "Base.Screws", 2)], {}, 60, {"MetalWelding": 5},
     {"isThumpable": False, "canPassThrough": True, "dismantable": True}, None),
    ("cup", "Styrofoam Cup", "Decorations and Landscaping", "Kitchen Clutter", "Fabric",
     {"S": _one(23)}, TABLETOP, [_mat(1, "Base.Plank", 1)], {}, 20, {},   # 1 wood (user)
     {"isThumpable": False, "canPassThrough": True, "dismantable": True}, "cups"),
    ("cup_stack", "Styrofoam Cup Stack", "Decorations and Landscaping", "Kitchen Clutter", "Fabric",
     {"S": _one(31)}, TABLETOP, [_mat(1, "Base.Plank", 1)], {}, 20, {},   # 1 wood (user)
     {"isThumpable": False, "canPassThrough": True, "dismantable": True}, "cups"),
]

GROUPS = {"cups": ("worldessentials.tikitown.props14_cups", "Styrofoam Cups")}

# ---- Electrical Cabinet -> working generator (user, 2026-11-08) --------------------------------
# KBW builds a real IsoGenerator from stage.nativeObject {type generator, item}; vanilla then handles
# fuel / plug / on-off / repair / pickup. The game identifies a placed generator by its SPRITE:
# IsoGenerator.getGeneratorItemType() looks the sprite name up in a map built from every item
# tagged base:generator (key = the item's WorldObjectSprite). So each facing gets its own item:
# picking up the mirrored cabinet returns the mirrored item, and placing it brings back that facing.
# Item stats (user): wear 1 in 40 (ConditionLowerChanceOneIn; yellow, the best vanilla one, is 36),
# SoundRadius 15 (vanilla 20-25), Weight 40 (vanilla 30-40). Fuel use / tank / range are sandbox-wide
# in IsoGenerator and can't be set per item.
GEN_MODULE = "TikiTownKBW"
GEN_ITEM = GEN_MODULE + ".ElectricalCabinetGenerator"
GEN_ITEM_MIRRORED = GEN_MODULE + ".ElectricalCabinetGeneratorMirrored"
GEN_NAME = "Electrical Cabinet Generator"
CABINET_TILE = 16
# generated mirrored copies of props-14 tiles (written by tikitown_wall_overlays.write_overlay_assets
# into the same pack + tiledef as the wall overlay copies; own tileset)
MIRROR_TILESET = "KBWTikiTownProps"
MIRRORS = [CABINET_TILE]          # index in this list = index in MIRROR_TILESET


def mirror_sprite(tile):
    return "%s_%d" % (MIRROR_TILESET, MIRRORS.index(tile))


_GEN_ITEM_BLOCK = """    item %(name)s
    {
        DisplayCategory = Electronics,
        ItemType = base:normal,
        Weight = 40.0,
        Icon = %(icon)s,
        ConditionMax = 100,
        MetalValue = 500.0,
        RequiresEquippedBothHands = true,
        Tooltip = Tooltip_Generator,
        Tags = base:heavyitem;base:generator;base:hasmetal;base:ignorezombiedensity;base:showcondition,
        WorldObjectSprite = %(sprite)s,
        ConditionLowerChanceOneIn = 40,
        SoundRadius = 15,
        SoundVolume = 1,
    }
"""


# "Rotate" world option (user, 2026-11-08): vanilla can only DROP a generator, so the facing it was
# built in could never change. Swapping the placed IsoGenerator's sprite between the two facings keeps
# fuel / condition / connected / activated (same object). The game types a generator by its sprite,
# so a rotated cabinet picks up as the matching item. MP: the client asks, the server swaps and
# syncs (transmitUpdatedSpriteToClients, the pattern vanilla's rain barrels / campfires use).
ROTATE_LUA_NAME = "KBWTikiTown_GeneratorRotate.lua"
ROTATE_LABEL_KEY = "IGUI_KBWTikiTown_RotateGenerator"
_ROTATE_LUA = r'''-- AUTO-GENERATED by pz_craft_loops/tikitown_props14.py -- edit the generator, not this file.
-- "Rotate" for the Electrical Cabinet Generator: swaps the placed generator between its two
-- facings. Same IsoGenerator object, so fuel, condition, connected and on/off state are kept.
-- Kahlua-safe: avoids the next function, goto, integer division and bitwise operators.
KBWTikiTownGenRotate = KBWTikiTownGenRotate or {}
local R = KBWTikiTownGenRotate
local MODULE, COMMAND = "KBWTikiTown", "rotateGenerator"

R.SWAP = {
    ["%(a)s"] = "%(b)s",
    ["%(b)s"] = "%(a)s",
}

-- our generator on this square, or nil
function R.findOn(square)
    if not square then return nil end
    local objects = square:getObjects()
    for i = 0, objects:size() - 1 do
        local obj = objects:get(i)
        local sprite = obj and obj:getSprite()
        if obj and instanceof(obj, "IsoGenerator") and sprite and R.SWAP[sprite:getName()] then
            return obj
        end
    end
    return nil
end

-- authoritative swap (server, or the game itself in single player)
function R.apply(square)
    local gen = R.findOn(square)
    if not gen then return false end
    local target = R.SWAP[gen:getSprite():getName()]
    local sprite = getSprite(target)
    if not sprite then return false end
    gen:setSprite(sprite)
    if isServer() and gen.transmitUpdatedSpriteToClients then gen:transmitUpdatedSpriteToClients() end
    square:RecalcAllWithNeighbours(true)
    return true
end

if isServer() then
    Events.OnClientCommand.Add(function(module, command, player, args)
        if module ~= MODULE or command ~= COMMAND or type(args) ~= "table" then return end
        local square = getCell():getGridSquare(tonumber(args.x), tonumber(args.y), tonumber(args.z))
        -- only for someone standing next to it (same rule as the vanilla generator actions)
        if square and player and player:getSquare()
            and math.abs(player:getX() - square:getX()) <= 2 and math.abs(player:getY() - square:getY()) <= 2
            and math.floor(player:getZ()) == square:getZ() then
            R.apply(square)
        end
    end)
end

if isServer() then return end   -- the rest is client UI

require "TimedActions/ISBaseTimedAction"
KBWTikiTownRotateGeneratorAction = ISBaseTimedAction:derive("KBWTikiTownRotateGeneratorAction")
local A = KBWTikiTownRotateGeneratorAction

function A:isValid()
    return self.generator and self.generator:getObjectIndex() ~= -1 and R.findOn(self.square) ~= nil
end
function A:waitToStart()
    self.character:faceThisObject(self.generator)
    return self.character:shouldBeTurning()
end
function A:update() self.character:faceThisObject(self.generator) end
function A:start() self:setActionAnim("Loot"); self.character:SetVariable("LootPosition", "Low") end
function A:stop() ISBaseTimedAction.stop(self) end
function A:perform()
    local sq = self.square
    if isClient() then
        sendClientCommand(self.character, MODULE, COMMAND, { x = sq:getX(), y = sq:getY(), z = sq:getZ() })
    else
        R.apply(sq)
    end
    ISBaseTimedAction.perform(self)
end
function A:new(character, generator)
    local o = ISBaseTimedAction.new(self, character)
    o.generator = generator
    o.square = generator:getSquare()
    o.maxTime = character:isTimedActionInstant() and 1 or 60
    return o
end

local function label()
    local t = getText("%(key)s")
    if t == "%(key)s" then t = "Rotate" end
    return t
end

local function onRotate(worldobjects, generator, playerNum)
    local playerObj = getSpecificPlayer(playerNum)
    if not playerObj or playerObj:getVehicle() then return end
    if luautils.walkAdj(playerObj, generator:getSquare()) then
        ISTimedActionQueue.add(KBWTikiTownRotateGeneratorAction:new(playerObj, generator))
    end
end

Events.OnFillWorldObjectContextMenu.Add(function(playerNum, context, worldobjects, test)
    if test then return end
    local seen = {}
    for i = 1, #worldobjects do
        local square = worldobjects[i] and worldobjects[i].getSquare and worldobjects[i]:getSquare()
        if square and not seen[square] then
            seen[square] = true
            local gen = R.findOn(square)
            if gen then
                context:addOption(label(), worldobjects, onRotate, gen, playerNum)
                return
            end
        end
    end
end)
'''


def write_generator_rotate_lua(dest_path):
    lua = _ROTATE_LUA % {"a": _spr(CABINET_TILE), "b": mirror_sprite(CABINET_TILE), "key": ROTATE_LABEL_KEY}
    for bad in ("next(", "goto ", "//", "debug."):
        if bad in lua:
            raise RuntimeError("Kahlua-unsafe construct in rotate Lua: %s" % bad)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    open(dest_path, "w", encoding="utf-8", newline="\n").write(lua)
    return dest_path


# Inventory icons (user: no icon = dealbreaker): generated from the tile art, 32x32 like every icon
# KBW / WE ship, as media/textures/Item_<Icon>.png ("Icon = X" loads texture Item_X).
GEN_ICONS = {GEN_ITEM: "KBWTikiTown_ElectricalCabinetGenerator",
             GEN_ITEM_MIRRORED: "KBWTikiTown_ElectricalCabinetGeneratorMirrored"}
ICON_SIZE = 32


def _gen_items():
    return ((GEN_ITEM, _spr(CABINET_TILE), False), (GEN_ITEM_MIRRORED, mirror_sprite(CABINET_TILE), True))


def write_generator_icons(media_dir):
    """Render each facing's world tile into a 32x32 icon (aspect kept, centred, 1 px margin)."""
    from PIL import Image, ImageOps
    import kbw_tilepatch as k
    import tikitown_wall_overlays as two
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_names")
    k._extract_from_pack(two._TIKITOWN_PACK, {_spr(CABINET_TILE)}, cache)
    src = Image.open(os.path.join(cache, "%s.png" % _spr(CABINET_TILE))).convert("RGBA")
    out = []
    for item, _sprite, mirrored in _gen_items():
        im = ImageOps.mirror(src) if mirrored else src
        im = im.crop(im.getbbox())
        inner = ICON_SIZE - 2
        scale = min(inner / float(im.width), inner / float(im.height))
        im = im.resize((max(1, int(round(im.width * scale))), max(1, int(round(im.height * scale)))),
                       Image.LANCZOS)
        # The cabinet is near-black; at 32 px it vanished on the dark inventory background.
        # Lift the shadows, stretch contrast, and draw a 1 px light outline around the shape.
        from PIL import ImageEnhance, ImageFilter
        alpha = im.getchannel("A")
        rgb = ImageOps.autocontrast(im.convert("RGB"), cutoff=1)
        rgb = rgb.point(lambda v: int(255 * ((v / 255.0) ** 0.6)))       # gamma lift
        rgb = ImageEnhance.Contrast(rgb).enhance(1.15)
        im = Image.merge("RGBA", rgb.split() + (alpha,))
        icon = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
        pos = ((ICON_SIZE - im.width) // 2, (ICON_SIZE - im.height) // 2)
        mask = Image.new("L", (ICON_SIZE, ICON_SIZE), 0)
        mask.paste(alpha.point(lambda a: 255 if a > 60 else 0), pos)
        ring = mask.filter(ImageFilter.MaxFilter(3))
        outline = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (170, 170, 165, 255))
        icon.paste(outline, (0, 0), ring)
        icon.paste(im, pos, im)
        p = os.path.join(media_dir, "textures", "Item_%s.png" % GEN_ICONS[item])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        icon.save(p)
        out.append(p)
    return out


def generator_item_script():
    """Item script text for both facings (module TikiTownKBW)."""
    body = "".join(_GEN_ITEM_BLOCK % {"name": n.split(".", 1)[1], "sprite": s, "icon": GEN_ICONS[n]}
                   for n, s, _m in _gen_items())
    return ("/* TikiTown Buildworks: the Electrical Cabinet as a working generator (tikitown_props14.py).\n"
            " * One item per facing: the game maps a placed generator's sprite to its item. */\n"
            "module %s\n{\n    imports\n    {\n        Base\n    }\n\n%s}\n" % (GEN_MODULE, body))


# ItemName.json keys are the bare full type, like vanilla ("Base.Generator": "Generator - Lectromax")
GEN_ITEM_NAMES = {GEN_ITEM: GEN_NAME, GEN_ITEM_MIRRORED: GEN_NAME + " (Mirrored)"}


def write_generator_items(media_dir):
    p = os.path.join(media_dir, "scripts", "TikiTownKBW_Generators.txt")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8", newline="\n").write(generator_item_script())
    return p


# Build cost = the yellow generator as World Essentials ships it (WE Knox Buildworks Expansion
# 14_material_balance.json, patch of kbw.vanillaexpanded.survival.generator.generator_yellow,
# read 2026-11-08), with every skill requirement +1 (user).
_YELLOW_INPUTS = [
    {"id": "tool_screwdriver", "role": "tool", "mode": "keep", "resourceType": "Item",
     "tags": ["base:screwdriver"], "amount": 1, "flags": ["Prop1", "MayDegradeVeryLight"]},
    {"id": "tool_welding_mask", "role": "tool", "mode": "keep", "resourceType": "Item",
     "tags": ["base:weldingmask"], "amount": 1},
    {"id": "torch_fuel", "role": "consumable", "mode": "drain", "resourceType": "Item",
     "items": ["Base.BlowTorch"], "uses": 6},
    {"id": "welding_rods", "role": "consumable", "mode": "drain", "resourceType": "Item",
     "items": ["Base.WeldingRods"], "uses": 4},
    {"id": "electrical_wire", "role": "material", "mode": "consume", "resourceType": "Item",
     "items": ["Base.ElectricWire"], "amount": 8},
    {"id": "electronic_parts", "role": "material", "mode": "consume", "resourceType": "Item",
     "items": ["Base.ElectronicsScrap"], "amount": 16},
    {"id": "sheet_metal", "role": "material", "mode": "consume", "resourceType": "Item",
     "items": ["Base.SheetMetal"], "amount": 5},
    {"id": "metal_stock", "role": "material", "mode": "consume", "resourceType": "Item",
     "items": ["Base.MetalPipe", "Base.MetalBar"], "amount": 3},
    {"id": "fasteners_screws", "role": "material", "mode": "consume", "resourceType": "Item",
     "items": ["Base.Screws"], "amount": 8},
    {"id": "engine_parts", "role": "material", "mode": "consume", "resourceType": "Item",
     "items": ["Base.EngineParts"], "amount": 15},
]
_YELLOW_SKILLS = {"Electricity": 8, "MetalWelding": 5}
_YELLOW_ALT = {"Electricity": 8, "MetalWelding": 6}
_YELLOW_KNOWLEDGE_SOURCE = {"type": "magazine", "item": "KnoxBuildworks.ProjectsInMetal_Diverse"}


def _plus1(skills):
    return {k: v + 1 for k, v in skills.items()}


def generator_cabinet(b):
    """Turn the built Electrical Cabinet buildable into the generator (in place)."""
    b["displayName"] = GEN_NAME
    b["subcategory"] = "Generators"
    b["materialTags"] = ["Metal", "Electronics"]
    b["tags"] = b["tags"] + ["generator", "electrical"]
    st = b["stages"][0]
    st["geometry"] = {"faces": {"S": _one(CABINET_TILE),
                                "E": {"layers": [{"rows": [[mirror_sprite(CABINET_TILE)]]}]}}}
    st["requirements"] = {
        "inputs": json.loads(json.dumps(_YELLOW_INPUTS)),
        "skills": _plus1(_YELLOW_SKILLS),
        "knowledge": {"recipes": ["KBWKnowledge_ProjectsInMetal_Diverse"], "hideUntilLearned": True,
                      "needToBeLearned": True, "sources": [dict(_YELLOW_KNOWLEDGE_SOURCE)],
                      "skillAlternatives": [{"mode": "all", "skills": _plus1(_YELLOW_ALT)}]},
    }
    st["construction"] = {"time": 600, "timedAction": "BuildMetalStructureMedium",
                          "completionSound": "BuildMetalStructureMedium", "xp": {"Electricity": 140},
                          "category": "Electrical"}
    st.pop("object", None)            # like VE's generators: the IsoGenerator needs no object block
    st["nativeObject"] = {"type": "generator", "item": GEN_ITEM}
    return b


def _buildable(slug, name, cat, sub, material, faces, placement, inputs, skills, time, xp, obj, group):
    first = next(iter(faces.values()))["layers"][0]["rows"][0][0]
    construction = dict(ELEC_BUILD) if "Electricity" in skills else {
        "timedAction": "BuildWallNoTool", "completionSound": "BuildMetalStructureMedium", "category": "Carpentry"}
    construction["time"] = time
    if xp:
        construction["xp"] = xp
    b = {
        "id": "worldessentials.tikitown.props14_%s" % slug,
        "allowSpriteReuse": True,
        "translationKey": "IGUI_WETiki_props14_%s" % slug,
        "displayName": name,
        "category": cat,
        "subcategory": sub,
        "material": material,
        "materialTags": [material],
        "iconSprite": first,
        "placement": dict(placement),
        "tags": ["tikitown", "drazion", "world-essentials", "props14"],
        "stages": [{
            "id": "built",
            "geometry": {"faces": faces},
            "requirements": {"inputs": inputs, "skills": skills} if skills else {"inputs": inputs},
            "construction": construction,
            "object": dict(obj),
        }],
    }
    if group:
        gid, gname = GROUPS[group]
        b["group"] = {"id": gid, "name": gname, "translationKey": "IGUI_WETiki_props14_%s_group" % group,
                      "level": 1}
    return b


def main():
    doc = {
        "schemaVersion": 1,
        "category": "Appliances",
        "source": ("TikiTown tikitown-props-14 (Drazion's Tilepack), everything except the soundproofing "
                   "(37) and the multi-part statue: desk mic, small + large mixer boards, electrical "
                   "cabinet, ATM, thermos coffee dispenser, styrofoam cups. First-pass costs."),
        "buildables": [_buildable(*p) for p in PIECES],
    }
    # the cabinet is a working generator; its mirror face (labels toward the east) is our own copy
    for b in doc["buildables"]:
        if b["id"].endswith("_electrical_cabinet"):
            generator_cabinet(b)
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    ids = [b["id"] for b in doc["buildables"]]
    assert len(ids) == len(set(ids))
    print("wrote %s (%d buildables)" % (OUT, len(ids)))


if __name__ == "__main__":
    main()
