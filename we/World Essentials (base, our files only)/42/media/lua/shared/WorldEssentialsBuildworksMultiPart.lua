-- Event-driven multipart furniture support. No grid callbacks, timers or custom packets.
if not (getActivatedMods():contains("KnoxCommunityTilepack") or getActivatedMods():contains("TikiTownKBW")) then return end
local Policy = require "Patches/WorldEssentialsGuestActions"
require "Patches/WorldEssentialsLocksmithProtection_Shared"
local Resolver = require "KnoxBuildworks/Definitions/Resolver"
local Matrix = require "KnoxBuildworks/Geometry/Matrix"
local M = {}
WorldEssentialsBuildworksMultiPart = M
local function ours(id)
    return type(id) == "string" and (id:find("community.",1,true)==1 or id:find("tikitown.",1,true)==1
        or id:find("worldessentials.tikitown.",1,true)==1 or id:find("kbwcb.",1,true)==1)
end
-- nil: ordinary/native object, false: incomplete group (must not mutate), table: exact group.
function M.members(object)
    if not object or not object:hasModData() then return nil end
    local k = object:getModData().KBW
    if type(k) ~= "table" or not ours(k.buildableId) or not k.groupId or (tonumber(k.partCount) or 1)<2 then return nil end
    local definition, stage = Resolver.resolveStage(k.buildableId,k.variantId,k.materialId,k.stageId)
    if not definition or not stage then return false end
    local placement = stage.placement or definition.placement or {}
    if placement.kind ~= "object" then return nil end -- native gates, walls, stairs and floors retain their dedicated routes
    local cells = Matrix.getFaceCells(stage,k.direction or 1)
    local partIndex = tonumber(k.partIndex)
    if not cells or #cells > 32 or #cells ~= tonumber(k.partCount) or not partIndex or not cells[partIndex] then return false end
    local sq = object:getSquare()
    if not sq or object:getObjectIndex()<0 then return false end
    local anchor = cells[partIndex]
    local x,y,z = sq:getX()-(anchor.dx or 0),sq:getY()-(anchor.dy or 0),sq:getZ()-(anchor.dz or 0)
    local result = {object}
    local count = 0
    for i, cell in ipairs(cells) do
        if cell.sprite then
            local target = getCell():getGridSquare(x+(cell.dx or 0),y+(cell.dy or 0),z+(cell.dz or 0))
            if not target then return false end -- never force a chunk to load
            local found
            local objects=target:getObjects()
            for j=0,objects:size()-1 do
                local other=objects:get(j)
                if other:hasModData() then
                    local o=other:getModData().KBW
                    if type(o)=="table" and o.groupId==k.groupId and o.partIndex==i then
                        local sprite=other:getSprite()
                        if found or not sprite or sprite:getName()~=cell.sprite or o.buildableId~=k.buildableId then return false end
                        found=other
                    end
                end
            end
            if not found then return false end
            count=count+1
            if found~=object then result[#result+1]=found end
        end
    end
    if #result~=count then return false end
    return result
end
function M.allowed(character,object)
    if not character or not object or object:getObjectIndex()<0 then return false end
    local sq=object:getSquare()
    if not sq or not Policy.objectAllowed(object,character) then return false end
    if math.abs(character:getX()-sq:getX())>4 or math.abs(character:getY()-sq:getY())>4 or character:getZ()~=sq:getZ() then return false end
    local locks=WorldEssentialsLocksmithProtection
    if locks and locks.shouldBlockLockedObjectDestruction(character,object) then return false end
    local power=WorldEssentialsTikitownPowerProtection
    if power and power.isProtectedObject(object) then return false end
    return true
end
-- If native work fails after removing a part, keep survivors independently usable.
-- Never reconstruct removed items (which could duplicate successfully created moveables).
function M.releaseSurvivors(members)
    if isClient() then return end
    local partial=false
    for _,member in ipairs(members) do if member:getObjectIndex()<0 then partial=true end end
    if not partial then return end
    for _,member in ipairs(members) do
        if member:getObjectIndex()>=0 then
            local k=member:getModData().KBW
            if type(k)=="table" then k.groupId=nil;k.partCount=1;k.partIndex=1 end
            if isServer() then member:transmitModData() end
        end
    end
end
local function install()
    require "Moveables/ISMoveableSpriteProps"
    require "TimedActions/ISDestroyStuffAction"
    local P,A=ISMoveableSpriteProps,ISDestroyStuffAction
    if P._weKBWMultiPart then return end
    P._weKBWMultiPart=true
    local originalCan,originalPick=P.canPickUpMoveable,P.pickUpMoveable
    P.canPickUpMoveable=function(self,character,square,object)
        local members=M.members(object)
        if members==nil then return originalCan(self,character,square,object) end
        if not members then return false end
        for _,member in ipairs(members) do
            local props=ISMoveableSpriteProps.fromObject(member)
            if not M.allowed(character,member) or not props or not props.isMoveable
                or not props:canPickUpMoveableInternal(character,member:getSquare(),member,true) then return false end
        end
        return true
    end
    P.pickUpMoveable=function(self,character,square,createItem,forceAllow)
        local object,attached=self:findOnSquare(square,self.spriteName)
        if attached then return originalPick(self,character,square,createItem,forceAllow) end
        local members=M.members(object)
        if members==nil then return originalPick(self,character,square,createItem,forceAllow) end
        if not members or not self:canPickUpMoveable(character,square,object) then return false end
        -- Keep native sprite-grid pickup when it already owns the complete group.
        if self.isMultiSprite and self:getSpriteGridInfo(square,true) then
            return originalPick(self,character,square,createItem,forceAllow)
        end
        local items={}
        for _,member in ipairs(members) do
            local props=ISMoveableSpriteProps.fromObject(member)
            if not M.allowed(character,member) then return false end
            local was=props.isMultiSprite
            props.isMultiSprite=true -- vanilla drops part items on their squares
            local ok,item=pcall(props.pickUpMoveableInternal,props,character,member:getSquare(),member,nil,member:getSprite():getName(),createItem,false)
            props.isMultiSprite=was
            if not ok then M.releaseSurvivors(members);error(item) end -- never repeat an already completed part
            if member:getObjectIndex()>=0 then M.releaseSurvivors(members);return false end
            if item then items[#items+1]=item end
        end
        return items
    end
    local originalComplete=A.complete
    A.complete=function(self)
        local members=M.members(self.item)
        if members==nil then return originalComplete(self) end
        if not members then return false end
        local selected=self.item
        -- All permission/tool/state checks run before the first removal.
        for _,member in ipairs(members) do
            self.item=member
            local valid=M.allowed(self.character,member) and self:isValid()
            if valid and getServerOptions():getBoolean("SledgehammerOnlyInSafehouse") then
                local role=self.character:getRole()
                local privileged=role and role:hasCapability(Capability.UseBuildCheat)
                local safe=SafeHouse.isSafeHouse(member:getSquare(),nil,false)
                valid=privileged or (safe and safe:playerAllowed(self.character))
            end
            self.item=selected
            if not valid then return false end
        end
        for _,member in ipairs(members) do
            if member:getObjectIndex()>=0 then
                self.item=member
                local ok,result=pcall(originalComplete,self)
                self.item=selected
                if not ok then M.releaseSurvivors(members);error(result) end
                if not result then M.releaseSurvivors(members);return false end
            end
        end
        return true
    end
end
Events.OnGameStart.Add(install)
if Events.OnServerStarted then Events.OnServerStarted.Add(install) end
return M
