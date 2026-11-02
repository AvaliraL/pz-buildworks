"""Classify every sprite of each wall sheet into piece roles, pairing W/N.
Rule B: every non-damage tile becomes a buildable.
Excludes: *Trans damage states, empty cells, prop cells (non-wall flags),
and (reported) siding structural-pillar extra row.
Outputs _wall_pieces.json (machine) + _wall_pieces_report.txt (human)."""
import importlib.util, json, io
spec=importlib.util.spec_from_file_location("tx", r"c:\Users\josep\Kiro\pz_craft_loops\tiles_extract.py")
tx=importlib.util.module_from_spec(spec); spec.loader.exec_module(tx)

MANUAL=["tikitown_tents_01","tt_melos_tiles_overgrown_ruins_01"]

def role_of(fl, wt):
    s=set(fl or [])
    # damage/transition states -> skip
    if any(f.endswith("Trans") for f in s):
        return ("DAMAGE", None)
    if not s:
        return ("EMPTY", None)
    # corners
    if "WallNW" in s: return ("CORNER_NW", None)
    if "WallSE" in s: return ("CORNER_SE", None)
    # doors
    if "DoorWallW" in s:
        if any(c.startswith("cut") for c in s): return ("DOORCUT_W", None)
        return ("DOOR", "W")
    if "DoorWallN" in s:
        if any(c.startswith("cut") for c in s): return ("DOORCUT_N", None)
        return ("DOOR", "N")
    # windows
    if "WindowW" in s: return ("WINDOW", "W")
    if "WindowN" in s: return ("WINDOW", "N")
    # plain walls (wt=wall => the main wall; wt=None => half/segment pieces)
    if "WallW" in s:
        return ("WALL" if wt=="wall" else "SEG", "W")
    if "WallN" in s:
        return ("WALL" if wt=="wall" else "SEG", "N")
    # anything else = prop
    return ("PROP", None)

def classify(sheet):
    ex=tx.extract(sheet)
    sprites=ex.get("sprites",[])
    recs=[]
    for s in sprites:
        role,face=role_of(s.get("flags"), s.get("WallType"))
        recs.append({"idx":s["index"],"role":role,"face":face,
                     "wt":s.get("WallType"),"flags":s.get("flags") or []})
    return ex.get("leading_blanks"), recs

def pair_pieces(recs):
    """Walk the records in index order and pair consecutive W/N of the same role
    into buildables. A piece = {kind, w_idx, n_idx, corner_idx, se_idx, cuts:[...]}.
    Stops before DAMAGE region (first DAMAGE ends the non-damage zone)."""
    pieces=[]
    corner=None; se=None
    # find first damage index -> cut recs there
    dmg_cut=None
    for r in recs:
        if r["role"]=="DAMAGE":
            dmg_cut=r["idx"]; break
    live=[r for r in recs if (dmg_cut is None or r["idx"]<dmg_cut)]
    # capture corner/se (first occurrences, for the main wall object)
    for r in live:
        if r["role"]=="CORNER_NW" and corner is None: corner=r["idx"]
        if r["role"]=="CORNER_SE" and se is None: se=r["idx"]
    # pair WALL/WINDOW/DOOR/SEG by scanning; W then its N partner (next same-role N)
    pend={}  # role-> list of pending W idx
    doorcuts={"W":[], "N":[]}
    i=0
    order=[]  # keep emission order
    byrole_counter={}
    # Build sequential pairs: iterate, when we see a W of role R, look for the NEXT N of role R
    used=set()
    for a_i,r in enumerate(live):
        if r["idx"] in used: continue
        role=r["role"]; face=r["face"]
        if role in ("WALL","WINDOW","DOOR","SEG") and face=="W":
            # find next N of same role not used
            partner=None
            for b in live[a_i+1:]:
                if b["role"]==role and b["face"]=="N" and b["idx"] not in used:
                    partner=b; break
            n_idx=partner["idx"] if partner else None
            if partner: used.add(partner["idx"])
            used.add(r["idx"])
            order.append({"kind":role,"w":r["idx"],"n":n_idx})
        elif role in ("DOORCUT_W","DOORCUT_N"):
            doorcuts["W" if role=="DOORCUT_W" else "N"].append(r["idx"])
            used.add(r["idx"])
    return {"corner":corner,"se":se,"doorcuts":doorcuts,"pieces":order,
            "damage_starts":dmg_cut}

def main():
    import json as J
    rpt=io.StringIO()
    allsheets=J.load(open(r"c:\Users\josep\Kiro\zomboid\tikitown\21_tikitown_walls.json",encoding="utf8"))
    sheets=[]
    for b in allsheets["buildables"]:
        sp=b["stages"][0]["geometry"]["faces"]["W"]["layers"][0]["rows"][0][0]
        sh=sp.rsplit("_",1)[0]
        if sh not in sheets: sheets.append(sh)
    data={}
    for sh in sheets:
        if sh in MANUAL:
            rpt.write(f"\n### {sh}  [MANUAL - skipped]\n"); 
            data[sh]={"manual":True}; continue
        try:
            lead,recs=classify(sh)
        except Exception as e:
            rpt.write(f"\n### {sh}  ERROR {e}\n"); data[sh]={"error":str(e)}; continue
        pp=pair_pieces(recs)
        data[sh]={"lead":lead,**pp}
        walls=[p for p in pp["pieces"] if p["kind"]=="WALL"]
        wins=[p for p in pp["pieces"] if p["kind"]=="WINDOW"]
        doors=[p for p in pp["pieces"] if p["kind"]=="DOOR"]
        segs=[p for p in pp["pieces"] if p["kind"]=="SEG"]
        rpt.write(f"\n### {sh} lead={lead} dmg@{pp['damage_starts']} corner={pp['corner']} se={pp['se']}\n")
        rpt.write(f"    WALL={len(walls)} WINDOW={len(wins)} DOOR={len(doors)} SEG={len(segs)}  total_pieces={len(pp['pieces'])}\n")
        for p in pp["pieces"]:
            rpt.write(f"      {p['kind']:<7} W={p['w']} N={p['n']}\n")
    open(r"c:\Users\josep\Kiro\pz_craft_loops\_wall_pieces.json","w",encoding="utf8").write(J.dumps(data,indent=1))
    # summary totals
    tot=0; 
    summ=io.StringIO()
    for sh,v in data.items():
        if v.get("manual") or v.get("error"): continue
        n=len(v["pieces"]); tot+=n
    summ.write(f"TOTAL non-damage buildable pieces across {len([s for s in data if not data[s].get('manual') and not data[s].get('error')])} auto sheets = {tot}\n")
    open(r"c:\Users\josep\Kiro\pz_craft_loops\_wall_pieces_report.txt","w",encoding="utf8").write(summ.getvalue()+rpt.getvalue())
main()
