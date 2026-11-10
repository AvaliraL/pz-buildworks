-- Optional definitions use the normal Knox loader, validation and build path.
-- No world scans, per-frame handlers, extra packets or client-only hiding.
local Registry = require("KnoxBuildworks/Definitions/Registry")
local Hash = require("KnoxBuildworks/Util/Hash")
if Registry._worldEssentialsTikitown then return end
Registry._worldEssentialsTikitown = true
local prefix = "worldessentials.tikitown."
local enabled = false
local function refreshDependencies()
    local map, tiles = false, false
    local mods = getActivatedMods and getActivatedMods()
    if mods then
        for i = 0, mods:size()-1 do
            local id = tostring(mods:get(i))
            if id == "tikitown" then map = true end
            if id == "tikitown_tiles" then tiles = true end
        end
    end
    enabled = map and tiles
end
refreshDependencies()
local reset = Registry.reset
function Registry:reset()
    reset(self)
    refreshDependencies()
end
local register = Registry.register
function Registry:register(definition, source)
    if type(source) == "string" and string.sub(source,1,#"WorldEssentialsKnoxBuildworksExpansion:") == "WorldEssentialsKnoxBuildworksExpansion:"
        and type(definition.id) == "string" and string.sub(definition.id,1,#prefix) == prefix
        and not enabled then return false end
    return register(self,definition,source)
end
local finalize = Registry.finalize
function Registry:finalize()
    -- Knox hashes source files rather than entries. Include the dependency gate
    -- so a mismatched client cannot share a hash with a different recipe set.
    self.files["WorldEssentialsKnoxBuildworksExpansion:tikitown-dependencies"] =
        Hash.string(enabled and "tikitown+tiles:enabled:v1" or "tikitown+tiles:disabled:v1")
    return finalize(self)
end
