-- On-demand only: at most 20 squares, no timers or load events.
local M={}
local ID="kbwcb.stairs.vehicle_ramp"
function M.identity(o)
    if not o or not o:hasModData() then return end
    local md=o:getModData().KBW
    local s=o:getSprite();local name=s and s:getName()
    local i=name and tonumber(string.match(name,"^ramps_01_(%d+)$"))
    if type(md)~="table" or md.buildableId~=ID or md.stageId~="built"
        or type(md.groupId)~="string" or md.groupId=="" or not i then return end
    if i<=19 or i>=24 and i<=43 or i>=48 and i<=67 or i>=72 and i<=91 then return md,i end
end
function M.tool(p)
    local item=p:getPrimaryHandItem()
    return item and instanceof(item,"HandWeapon") and not item:isBroken()
        and (item:hasTag(ItemTag.SLEDGEHAMMER) or item:hasTag(ItemTag.STONE_MAUL)
        or item:hasTag(ItemTag.CLUB_HAMMER) or item:hasTag(ItemTag.PICK_AXE))
end
function M.check(p,o)
    local md,index=M.identity(o);local sq=o and o:getSquare()
    if not md or not sq or not p or p:isDead() or p:getVehicle() or not M.tool(p) then return end
    local x,y,z=sq:getX(),sq:getY(),sq:getZ()
    if math.floor(p:getZ())~=z or math.abs(p:getX()-x)>2 or math.abs(p:getY()-y)>2 then return end
    local opts=getServerOptions()
    if not opts:getBoolean("AllowDestructionBySledgehammer") then return end
    local base=index<=19 and 0 or index<=43 and 24 or index<=67 and 48 or 72
    local offset=index-base;local parts={}
    for i=0,19 do
        local xx,yy=x,y
        if base==0 then yy=y+offset-i elseif base==24 then yy=y-offset+i
        elseif base==48 then xx=x+offset-i else xx=x-offset+i end
        local s=getCell():getGridSquare(xx,yy,z)
        if not s then return end
        local guests=WorldEssentialsSafehouseGuests
        if not SafeHouse.isSafehouseAllowInteract(s,p) and not (guests and guests.canInteract(s,p)) then return end
        if opts:getBoolean("SledgehammerOnlyInSafehouse") and not SafeHouse.isSafeHouse(s,nil,false) then return end
        -- Do not remove support underneath characters, corpses or parked vehicles.
        if s:getMovingObjects():size()>0 or s:getStaticMovingObjects():size()>0 or s:getVehicleContainer() then return end
        local objects=s:getObjects();local found
        for j=0,objects:size()-1 do
            local part=objects:get(j);local other,idx=M.identity(part)
            if other and other.groupId==md.groupId and idx==base+i then
                if found then return end
                found=part
            end
        end
        if not found then return end
        parts[#parts+1]=found
    end
    return parts
end
function M.remove(p,o)
    if isClient() then return false end
    local parts=M.check(p,o);if not parts then return false end
    local dirt=getSprite("blends_natural_01_64")
    if not dirt or not dirt:getProperties():has(IsoFlagType.solidfloor) then return false end
    for i=1,#parts do
        local part=parts[i];local s=part:getSquare()
        s:transmitRemoveItemFromSquare(part,false)
        if s:getObjects():contains(part) then return false end
        if s:getZ()==0 and not s:getFloor() then
            local floor=IsoObject.new(getCell(),s,"blends_natural_01_64")
            s:AddTileObject(floor);floor:transmitCompleteItemToClients()
        end
        s:RecalcAllWithNeighbours(true)
        local chunk=s:getChunk();if chunk then chunk:flagForHotSave() end
    end
    return true
end
return M
