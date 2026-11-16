require "TimedActions/ISBaseTimedAction"
require "TimedActions/ISTimedActionQueue"
local R=require "KBWCommunity_RampRecovery"
local A=ISBaseTimedAction:derive("KBWCommunityRampRemovalAction")
function A:isValid()
    local md=R.identity(self.target)
    return md and md.groupId==self.group and self.target:getSquare()==self.square and R.tool(self.character)
        and math.floor(self.character:getZ())==self.square:getZ()
        and math.abs(self.character:getX()-self.square:getX())<=2
        and math.abs(self.character:getY()-self.square:getY())<=2
end
function A:perform()
    if self:isValid() then
        if isClient() then
            sendClientCommand(self.character,"KBWCommunityRamp","remove",{x=self.square:getX(),y=self.square:getY(),z=self.square:getZ(),index=self.target:getObjectIndex(),group=self.group})
        else R.remove(self.character,self.target) end
    end
    ISBaseTimedAction.perform(self)
end
local function begin(player,obj)
    local md=R.identity(obj);if not md or not R.check(player,obj) then return end
    local a=ISBaseTimedAction.new(A,player);a.target=obj;a.square=obj:getSquare();a.group=md.groupId
    a.maxTime=300;a.stopOnWalk=true;a.stopOnRun=true;ISTimedActionQueue.add(a)
end
Events.OnFillWorldObjectContextMenu.Add(function(playerNum,context,worldObjects,test)
    if test then return end
    local p=getSpecificPlayer(playerNum);if not p then return end
    local seen={}
    for _,obj in ipairs(worldObjects) do
        local sq=obj:getSquare()
        if sq and not seen[sq] then
            seen[sq]=true
            local objects=sq:getObjects()
            for i=0,objects:size()-1 do
                local target=objects:get(i)
                if R.identity(target) then
                    local option=context:addOption("Remove vehicle ramp (20 tiles; no refund)",p,begin,target)
                    option.notAvailable=not R.check(p,target)
                    return
                end
            end
        end
    end
end)
