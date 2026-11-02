-- Adapted from Workshop 3827764431 (BC_HasBeenRead_Compat), with permission.
-- Restores Has Been Read's inventory icons when Better Containers replaces
-- ISInventoryPane:renderdetails. No inventory traversal, polling or network traffic.
--
-- Has Been Read keeps its module table LOCAL (`local P4HasBeenRead = {}`) and never exports it,
-- so nothing here touches it. Icons are resolved from public inputs only, mirroring Has Been
-- Read 42.15's setTextures():
--   * player ModData `P4HasBeenRead.markedMap` (same keys as P4HasBeenRead.getFullType)
--   * vanilla read state (getAlreadyReadPages, getKnownRecipes, getReadLiterature,
--     isPrintMediaRead, hasReadMap, RecordedMedia:hasListenedToAll, SkillBook)
--   * Has Been Read's own player options, read through PZAPI.ModOptions (public)
--   * Has Been Read's texture files
-- Media target classification is built from public RecMedia at initialization, never per frame.
require 'Patches/WorldEssentialsReading'
local existing = WorldEssentialsReadIcons
if existing then return end
local State = { status = 'pending', limit = 512 }
WorldEssentialsReadIcons = State
local active

local function report(status, reason)
    if State.status == status and State.reason == reason then return end
    State.status, State.reason = status, reason
    print('[WorldEssentials][ReadIcons] '..status..': '..reason)
end

-- ---------------------------------------------------------------------------------------------
-- Textures + options
-- ---------------------------------------------------------------------------------------------
local TEX = {}
local HBR_TEX = {}   -- identity set, used to detect a surviving native Has Been Read overlay

local function loadTextures()
    TEX.NR = getTexture('media/ui/P4HasBeenRead_Book_NR.png')
    TEX.NC = getTexture('media/ui/P4HasBeenRead_Book_NC.png')
    TEX.AR = getTexture('media/ui/P4HasBeenRead_Book_AR.png')
    TEX.CT = getTexture('media/ui/P4HasBeenRead_Book_CT.png')
    TEX.SMM = getTexture('media/ui/P4HasBeenRead_Book_SM_Marked.png')
        or getTexture('media/ui/P4HasBeenRead_Book_SM.png')
    TEX.SMU = getTexture('media/ui/P4HasBeenRead_Book_SM_Unmarked.png')
    local count = 0
    for _, t in pairs(TEX) do HBR_TEX[t] = true; count = count + 1 end
    State.missingTextures = 6 - count
    for _ in pairs(TEX) do return true end
    return false
end

-- Finite warning keys, never an unbounded collection of error strings.
local warnings = {}
local function warnOnce(key)
    if warnings[key] then return end
    warnings[key] = true
    State.warningCount = (State.warningCount or 0) + 1
    print('[WorldEssentials][ReadIcons] fallback: '..key)
end

-- Same benefit codes as the installed Has Been Read module; independent of player read state.
local effectiveMedias = {}
local effectiveCodes = {"CRP","COO","FRM","DOC","ELC","MTL","MEC","TAI","FIS","TRA","FOR","HUS","FKN","BLA","POT","RCP","BAA","BUA","SBU","LBA","SBA","SPE","AIM","REL","SPR","LFT","NIM","SNE"}
local function initMedia()
    effectiveMedias = {}
    if type(RecMedia) ~= 'table' then
        if RecMedia ~= nil then warnOnce('invalid media catalogue') end
        return
    end
    for id, media in pairs(RecMedia) do
        if type(media) == 'table' and type(media.lines) == 'table' then
            for _, line in ipairs(media.lines) do
                if type(line) == 'table' and type(line.codes) == 'string' then
                    if line.codes ~= 'BOR-1' then
                        for _, code in ipairs(effectiveCodes) do
                            if string.find(line.codes, code, 1, true) then effectiveMedias[id] = true; break end
                        end
                    end
                elseif type(line) ~= 'table' or line.codes ~= nil then
                    warnOnce('invalid media line')
                end
                if effectiveMedias[id] then break end
            end
        elseif type(media) ~= 'table' or media.lines ~= nil then
            warnOnce('invalid media entry')
        end
    end
end

-- Reuse small option snapshots by nested render depth; never cache mutable player read state.
local optionSnapshots = {}
local function optionValue(option, index, default, key)
    if not option or not option.getValue then return default end
    local ok, value = pcall(option.getValue, option, index)
    if not ok then warnOnce(key); return default end
    if value == nil then return default end
    return value == true
end
local function readOptions(depth)
    local t = optionSnapshots[depth]
    if not t then
        t = {targets={}}
        if depth <= 4 then optionSnapshots[depth] = t end
    end
    local api = PZAPI and PZAPI.ModOptions
    local opts
    if api and api.getOptions then
        local ok, result = pcall(api.getOptions, api, 'P4HasBeenRead')
        if ok then opts = result else warnOnce('option registry unavailable') end
    end
    local function getOption(key)
        if not opts or not opts.getOption then return nil end
        local ok, result = pcall(opts.getOption, opts, key)
        if ok then return result end
        warnOnce(key)
    end
    local marks, selfMarks = getOption('ShowMarks'), getOption('ShowSM')
    local current, targets = getOption('ShowCT'), getOption('EnableTargets')
    t.NR = optionValue(marks, 1, true, "ShowMarks1") and TEX.NR or nil
    t.NC = optionValue(marks, 2, true, "ShowMarks2") and TEX.NC or nil
    t.AR = optionValue(marks, 3, false, "ShowMarks3") and TEX.AR or nil
    t.CT = optionValue(current, nil, true, "ShowCT") and TEX.CT or nil
    t.SMM = optionValue(selfMarks, 1, true, "ShowSM1") and TEX.SMM or nil
    t.SMU = optionValue(selfMarks, 2, false, "ShowSM2") and TEX.SMU or nil
    for i = 1, 9 do t.targets[i] = optionValue(targets, i, true, "EnableTargets") end
    t.hasStatus = t.NR ~= nil or t.NC ~= nil or t.AR ~= nil
    t.visible = t.hasStatus or t.CT ~= nil or t.SMM ~= nil or t.SMU ~= nil
    return t
end

-- ---------------------------------------------------------------------------------------------
-- Resolver: mirrors Has Been Read 42.15 setTextures / isTargetLiterature / isLiteratureRead /
-- getFullType / getRecipeResourceFullType
-- ---------------------------------------------------------------------------------------------
local function recipeResourceKey(item, fullType)
    local recipes = item:getLearnedRecipes()
    if not recipes or recipes:isEmpty() then return fullType end
    if recipes:size() == 1 then return fullType..'|'..recipes:get(0) end
    local temp, seen = {}, {}
    for i = 0, recipes:size() - 1 do
        local r = recipes:get(i)
        if not seen[r] then seen[r] = true; temp[#temp+1] = r end
    end
    -- Small recipe lists: insertion sort avoids relying on a host-provided table.sort.
    for i = 2, #temp do
        local value, j = temp[i], i - 1
        while j >= 1 and temp[j] > value do temp[j+1] = temp[j]; j = j - 1 end
        temp[j+1] = value
    end
    return fullType..'|'..table.concat(temp, '|')
end

local function markKey(item)
    local key = item:getFullType()
    if key == 'Base.RecipeClipping' or key == 'Base.SewingPattern'
        or (string.find(key, 'Schematic', 1, true) and item:getDisplayCategory() == 'RecipeResource') then
        key = recipeResourceKey(item, key)
    end
    local md = item:getModData()
    if md then
        if md.literatureTitle then key = md.literatureTitle
        elseif md.printMedia and md.printMedia.id then key = md.printMedia.id end
    end
    return key
end

local function isTargetLiterature(item)
    if SkillBook[item:getSkillTrained()] then return true end
    local lr = item:getLearnedRecipes()
    if lr and not lr:isEmpty() then return true end
    local ft = item:getFullType()
    if ft == 'Base.Flier' or ft == 'Base.Brochure' then return true end
    if item:getNumberOfPages() > 0 then return true end
    local md = item:getModData()
    return md ~= nil and (md.literatureTitle ~= nil or md.printMedia ~= nil)
end

local function isLiteratureRead(player, item)
    local md = item:getModData()
    if md.literatureTitle then return player:getReadLiterature():containsKey(md.literatureTitle)
    elseif md.printMedia and md.printMedia.id then return player:isPrintMediaRead(md.printMedia.id)
    elseif item:getNumberOfPages() > 0 then
        return player:getAlreadyReadPages(item:getFullType()) >= item:getNumberOfPages()
    end
    return false
end

local function pick(read, t) if read then return t.AR else return t.NR end end

local function resolve(player, item, markedMap, media, mediaCache, t)
    local status, marking, current
    if item:getCategory() == 'Literature' then
        if not isTargetLiterature(item) then return end
        local fullType = item:getFullType()
        local skillBook = SkillBook[item:getSkillTrained()]
        if skillBook then
            if t.targets[1] and (t.hasStatus or t.CT) then
                local reading,_,useful=WorldEssentialsReading.classify(player,{type=fullType,skill=item:getSkillTrained(),
                    level=item:getLvlSkillTrained(),maxLevel=item:getMaxLevelTrained(),pages=item:getNumberOfPages()})
                if useful then current = t.CT end
                if t.hasStatus then
                    if reading=='complete' then status = t.AR
                    elseif reading=='partial' then status = t.NC
                    else status = t.NR end
                end
            end
        else
            local lr = item:getLearnedRecipes()
            if lr and not lr:isEmpty() then
                if t.targets[2] and t.hasStatus then status = pick(player:getKnownRecipes():containsAll(lr), t) end
            elseif fullType == 'Base.Flier' then
                if t.targets[4] and t.hasStatus then status = pick(isLiteratureRead(player, item), t) end
            elseif fullType == 'Base.Brochure' then
                if t.targets[5] and t.hasStatus then status = pick(isLiteratureRead(player, item), t) end
            elseif t.targets[6] and t.hasStatus then
                local md = item:getModData()
                local n = item:getNumberOfPages()
                if not md.literatureTitle and not md.printMedia and n > 0 then
                    local pages = player:getAlreadyReadPages(fullType)
                    if pages >= n then status = t.AR elseif pages > 0 then status = t.NC else status = t.NR end
                else
                    status = pick(isLiteratureRead(player, item), t)
                end
            end
        end
        if markedMap[markKey(item)] then marking = t.SMM else marking = t.SMU end
    elseif instanceof(item, 'MapItem') then
        local mapId = item:getMapID()
        if mapId then
            if t.targets[3] and t.hasStatus then status = pick(player:hasReadMap(item), t) end
            if markedMap[mapId] then marking = t.SMM else marking = t.SMU end
        end
    elseif media then
        local md = item:getMediaData()
        if md then
            local index, cat = md:getIndex(), md:getCategory()
            local target = (t.targets[7] and cat == 'CDs') or (t.targets[8] and cat == 'Retail-VHS')
                or (t.targets[9] and cat == 'Home-VHS')
            if target and effectiveMedias[md:getId()] then current = t.CT end
            if target and t.hasStatus then
                local cached = mediaCache[index]
                if cached ~= nil then status = cached or nil
                else
                    status = pick(media:hasListenedToAll(player, md), t)
                    mediaCache[index] = status or false
                end
            end
            if markedMap['Base.RM-'..index] then marking = t.SMM else marking = t.SMU end
        end
    end
    return status, marking, current
end

-- ---------------------------------------------------------------------------------------------
-- Overlay pass over the rows captured from renderItemIcon during the inner render
-- ---------------------------------------------------------------------------------------------
local function drawOverlay(frame, texture, x, y, alpha)
    local positions = frame.native[texture]
    if positions and positions[x] and positions[x][y] then return end
    frame.pane:drawTexture(texture, x, y, alpha, 1, 1, 1)
end
local function draw(frame, t)
    local pane = frame.pane
    local player = getSpecificPlayer(pane.player)
    if not player then return end
    local root = player:getModData().P4HasBeenRead
    local markedMap = (root and root.markedMap) or {}
    local radio = getZomboidRadio and getZomboidRadio()
    local media = radio and radio:getRecordedMedia()
    local mediaCache = {}
    -- primary rows draw their icon at column2-texWH-texInset; expanded stack rows at 10+16
    local texWH = math.min((pane.itemHgt or 34) - 2, 32)
    local primaryX = (pane.column2 or 0) - texWH - ((pane.itemHgt or 34) - texWH) / 2
    if frame.dragged and pane.dragging and pane.dragStarted then
        primaryX = primaryX + pane:getMouseX() - pane.draggingX
    end
    for _, row in ipairs(frame.rows) do
        local status, marking, current = resolve(player, row.item, markedMap, media, mediaCache, t)
        if status or marking or current then
            local alpha = row.alpha
            if row.x < primaryX - 4 then alpha = alpha * 0.3 end   -- stack sub-row, like Has Been Read
            local x = row.x - 5
            if not frame.dragged and x < 1 then x = 1 end
            local y = row.y
            if status then drawOverlay(frame, status, x, y + row.h - 16, alpha) end
            if marking then drawOverlay(frame, marking, x + 10, y + row.h - 10, alpha) end
            if current then drawOverlay(frame, current, x - 1, y - 4, alpha) end
        end
    end
end

-- ---------------------------------------------------------------------------------------------
-- Install
-- ---------------------------------------------------------------------------------------------
local function install()
    if State.installed then return end
    local mods = getActivatedMods and getActivatedMods()
    if not mods or not mods:contains('EURY_CONTAINERS') or not mods:contains('P4HasBeenRead') then
        report('inactive', 'requires Better Containers and Has Been Read'); return
    end
    if mods:contains('BC_HasBeenRead_Compat') then
        report('inactive', 'standalone BC_HasBeenRead_Compat is active; integrated adapter stands aside'); return
    end
    if not ISInventoryPane or type(ISInventoryPane.renderdetails) ~= 'function' then
        report('unsupported', 'ISInventoryPane.renderdetails missing'); return
    end
    if not ISInventoryItem or type(ISInventoryItem.renderItemIcon) ~= 'function' then
        report('unsupported', 'ISInventoryItem.renderItemIcon missing'); return
    end
    if not SkillBook then
        report('unsupported', 'vanilla SkillBook table missing'); return
    end
    if not loadTextures() then
        report('unsupported', 'Has Been Read textures not found'); return
    end

    local render, icon = ISInventoryPane.renderdetails, ISInventoryItem.renderItemIcon
    initMedia() -- handles late loading after OnInitRecordedMedia
    Events.OnInitRecordedMedia.Add(initMedia)

    ISInventoryItem.renderItemIcon = function(pane, item, x, y, alpha, w, h, ...)
        local result = icon(pane, item, x, y, alpha, w, h, ...)
        local frame = active
        if frame and frame.pane == pane and item and type(x) == 'number'
            and type(y) == 'number' and type(h) == 'number' and #frame.rows < State.limit then
            frame.rows[#frame.rows + 1] = { item = item, x = x, y = y, h = h, alpha = alpha or 1 }
        end
        return result
    end

    ISInventoryPane.renderdetails = function(self, doDragged, ...)
        if State.failed then return render(self, doDragged, ...) end
        local depth = active and active.depth + 1 or 1
        local optionsOK, options = pcall(readOptions, depth)
        if not optionsOK then
            State.failed = true
            report('degraded', 'options unavailable: '..tostring(options))
            return render(self, doDragged, ...)
        end
        local t = options
        if not t.visible then return render(self, doDragged, ...) end
        local parent = active
        local frame = { depth = depth, pane = self, dragged = doDragged == true, rows = {}, native = {}, nativeCount = 0 }
        local ownDraw, effectiveDraw = rawget(self, 'drawTexture'), self.drawTexture
        active = frame
        -- Preserve instance/class overrides, including nested renders on this same pane.
        self.drawTexture = function(pane, tex, x, y, ...)
            if active == frame and tex and HBR_TEX[tex] and type(x) == 'number' and type(y) == 'number'
                and frame.nativeCount < State.limit * 3 then
                local positions = frame.native[tex]
                if not positions then positions = {}; frame.native[tex] = positions end
                if not positions[x] then positions[x] = {} end
                if not positions[x][y] then
                    positions[x][y] = true
                    frame.nativeCount = frame.nativeCount + 1
                end
            end
            return effectiveDraw(pane, tex, x, y, ...)
        end
        local ok, result = pcall(render, self, doDragged, ...)
        self.drawTexture = ownDraw
        active = nil -- do not capture child overlays as parent native icons
        if not ok then active = parent; error(result) end
        if #frame.rows > 0 then
            if frame.dragged then self:suspendStencil() end
            local overlayOK, reason = pcall(draw, frame, t)
            if frame.dragged then self:resumeStencil() end
            if not overlayOK then
                State.failed = true
                report('degraded', 'overlay disabled after error: '..tostring(reason))
            end
        end
        active = parent
        return result
    end
    State.installed = true
    report(State.missingTextures > 0 and 'partial' or 'installed',
        'public-input resolver; live player options; media targets; bounded visible rows; no polling/network; missingTextures='..State.missingTextures)
end
State.install = install
Events.OnGameStart.Add(install)
