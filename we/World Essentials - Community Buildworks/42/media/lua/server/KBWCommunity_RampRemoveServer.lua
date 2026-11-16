if isClient() then return end
local R=require "KBWCommunity_RampRecovery"
-- Weak player keys avoid retaining disconnected players. One attempt per two seconds.
local last=setmetatable({}, {__mode="k"})
local function integer(v) return type(v)=="number" and v==math.floor(v) and math.abs(v)<1000000 end
Events.OnClientCommand.Add(function(module,command,p,args)
    if module~="KBWCommunityRamp" or command~="remove" or not p or type(args)~="table" then return end
    local now=getTimestampMs();if last[p] and now-last[p]<2000 then return end;last[p]=now
    if not integer(args.x) or not integer(args.y) or not integer(args.z) or not integer(args.index)
        or args.index<0 or type(args.group)~="string" or #args.group>200 then return end
    if math.abs(p:getX()-args.x)>2 or math.abs(p:getY()-args.y)>2 or math.floor(p:getZ())~=args.z then return end
    local sq=getCell():getGridSquare(args.x,args.y,args.z)
    if not sq or args.index>=sq:getObjects():size() then return end
    local obj=sq:getObjects():get(args.index);local md=R.identity(obj)
    if not md or md.groupId~=args.group then return end
    R.remove(p,obj)
end)
