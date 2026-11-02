"""Expand a walls deliverable to include EVERY non-damage tile as a buildable (Option B).
- Keeps each sheet's existing plain-wall buildable VERBATIM (id/recipe/cost/name preserved),
  tagging it pieceClass="wall".
- Appends buildables for every additional non-damage piece (windows, door frame, segments),
  cloning that sheet's recipe/cost/object block (deep copy) and changing only:
  id suffix, iconSprite, geometry W/N sprites, displayName, placement flags, pieceClass.
- Window pieces: placement + dontNeedFrame + providesWindowFrame (NO windowGlass callback - solid material).
- Door pieces:   object.isDoorFrame + canPassThrough; door-cut sprites recorded on object.
- SEG pieces:    kind:"wall" like the main wall (half/segment sprites).
- Skips the 2 MANUAL sheets entirely (their existing single buildable is kept as-is).
- Runs per file so recipe/cost profiles stay native to each (cheap vs accurate) and ids match.

Reversible: originals backed up to wall_backups\*.PRE_EXPANSION.json. Every new buildable
carries "pieceClass" so a curated subset = filter, no re-derivation.
"""
import json, copy, re, sys

PIECES = json.load(open(r"c:\Users\josep\Kiro\pz_craft_loops\_wall_pieces.json",encoding="utf8"))
MANUAL = {"tikitown_tents_01","tt_melos_tiles_overgrown_ruins_01"}

def sheet_of(b):
    sp=b["stages"][0]["geometry"]["faces"]["W"]["layers"][0]["rows"][0][0]
    return sp.rsplit("_",1)[0]

def face_sprite(sheet, idx):
    return f"{sheet}_{idx}" if idx is not None else None

def set_faces(stage, sheet, w_idx, n_idx):
    faces=stage["geometry"]["faces"]
    faces["W"]["layers"][0]["rows"][0][0]=face_sprite(sheet,w_idx)
    if n_idx is not None:
        faces["N"]["layers"][0]["rows"][0][0]=face_sprite(sheet,n_idx)
    else:
        # fall back N to W sprite if no N partner (keeps a valid 2-face wall)
        faces["N"]["layers"][0]["rows"][0][0]=face_sprite(sheet,w_idx)

def make_piece(base, sheet, kind, w_idx, n_idx, suffix, name_suffix):
    b=copy.deepcopy(base)
    newid_sprite=f"{sheet}_{suffix}"
    b["id"]=f"worldessentials.tikitown.{newid_sprite}"
    b["translationKey"]=f"IGUI_WETiki_{newid_sprite}"
    b["tooltipKey"]=f"Tooltip_WETiki_{newid_sprite}"
    b["iconSprite"]=face_sprite(sheet,w_idx)
    b["displayName"]=f'{base["displayName"]}{name_suffix}'
    b["pieceClass"]=kind
    stage=b["stages"][0]
    set_faces(stage, sheet, w_idx, n_idx)
    obj=stage.setdefault("object",{})
    pl=b["placement"]
    if kind=="window":
        pl["kind"]="wall"; pl["requiresFloor"]=False
        pl["dontNeedFrame"]=True; pl["providesWindowFrame"]=True
        # windows don't carry the main wall's corner/pillar
        obj.pop("cornerSprite",None); obj.pop("pillarSprite",None)
    elif kind=="door":
        pl["kind"]="wall"; pl["requiresFloor"]=False
        obj["isDoorFrame"]=True; obj["canPassThrough"]=True
        obj.pop("cornerSprite",None); obj.pop("pillarSprite",None)
    else:  # segment
        pl["kind"]="wall"; pl["requiresFloor"]=False
        obj.pop("cornerSprite",None); obj.pop("pillarSprite",None)
    return b

def expand(path):
    doc=json.load(open(path,encoding="utf8"))
    old=doc["buildables"]
    bySheet={}
    for b in old:
        bySheet.setdefault(sheet_of(b),b)
    new=[]
    stats={"wall":0,"window":0,"door":0,"segment":0,"kept_manual":0}
    for b in old:
        sh=sheet_of(b)
        if sh in MANUAL:
            new.append(b); stats["kept_manual"]+=1; continue
        pdata=PIECES.get(sh)
        if not pdata or pdata.get("manual") or pdata.get("error"):
            new.append(b); continue
        # 1) primary wall buildable: keep existing id/recipe/cost/name, but set its sprites
        #    to the classifier's TRUE wall piece (fixes any pre-existing index drift).
        base=copy.deepcopy(b)
        base["pieceClass"]="wall"
        corner=pdata.get("corner"); se=pdata.get("se")
        # choose the true primary wall piece: first WALL, else first SEG, else first piece
        prim=None
        for p in pdata["pieces"]:
            if p["kind"]=="WALL": prim=p; break
        if prim is None:
            for p in pdata["pieces"]:
                if p["kind"]=="SEG": prim=p; break
        if prim is None and pdata["pieces"]:
            prim=pdata["pieces"][0]
        stage=base["stages"][0]; obj=stage.setdefault("object",{})
        if prim is not None:
            set_faces(stage, sh, prim["w"], prim["n"])
            base["iconSprite"]=face_sprite(sh, prim["w"])
        if corner is not None:
            obj["cornerSprite"]=face_sprite(sh,corner)
            obj["pillarSprite"]=face_sprite(sh,corner)
        base_true_w = prim["w"] if prim else None
        new.append(base); stats["wall"]+=1
        # 2) append every other piece
        win_n=0; seg_n=0
        # Skip re-emitting the primary wall piece (now set to its TRUE W index).
        base_w_idx = base_true_w
        for p in pdata["pieces"]:
            kind=p["kind"]; w=p["w"]; n=p["n"]
            if w==base_w_idx:
                # this is the primary wall already represented by `base`; do not duplicate
                continue
            if kind=="WALL":
                # extra full-wall piece beyond the primary -> emit as segment-style wall
                seg_n+=1
                new.append(make_piece(base, sh, "segment", w, n, f"{w}", f" (Segment {seg_n})"))
                stats["segment"]+=1
            elif kind=="WINDOW":
                win_n+=1
                new.append(make_piece(base, sh, "window", w, n, f"{w}", f" (Window {win_n})"))
                stats["window"]+=1
            elif kind=="DOOR":
                db=make_piece(base, sh, "door", w, n, f"{w}", " (Door Frame)")
                # attach door-cut sprites if present
                dc=pdata.get("doorcuts") or {}
                cw=dc.get("W") or []; cn=dc.get("N") or []
                if cw: db["stages"][0]["object"]["cutSpritesW"]=[face_sprite(sh,i) for i in cw]
                if cn: db["stages"][0]["object"]["cutSpritesN"]=[face_sprite(sh,i) for i in cn]
                new.append(db); stats["door"]+=1
            elif kind=="SEG":
                seg_n+=1
                new.append(make_piece(base, sh, "segment", w, n, f"{w}", f" (Segment {seg_n})"))
                stats["segment"]+=1
    doc["buildables"]=new
    return doc, stats, len(old), len(new)

def check(doc):
    ids=[b["id"] for b in doc["buildables"]]
    from collections import Counter
    dup=[i for i,c in Counter(ids).items() if c>1]
    # also check sprite references well-formed
    return dup, len(ids)

def main():
    import io
    dry = "--write" not in sys.argv
    out=io.StringIO()
    pairs=[(r"c:\Users\josep\Kiro\zomboid\tikitown\21_tikitown_walls.json",
            r"c:\Users\josep\Kiro\pz_craft_loops\wall_backups\_DRY_walls.json"),
           (r"c:\Users\josep\Kiro\zomboid\tikitown\21_tikitown_walls_accurate.json",
            r"c:\Users\josep\Kiro\pz_craft_loops\wall_backups\_DRY_walls_accurate.json")]
    results={}
    for path,drypath in pairs:
        doc,stats,n0,n1=expand(path)
        dup,nids=check(doc)
        out.write(f"{path}\n  {n0} -> {n1} buildables  stats={stats}\n  DUP_IDS={dup}\n")
        results[path]=[b["id"] for b in doc["buildables"]]
        target = path if not dry else drypath
        json.dump(doc, open(target,"w",encoding="utf8"), indent=1, ensure_ascii=False)
        out.write(f"  wrote -> {target}\n")
    # id parity between the two files
    keys=list(results.keys())
    if len(keys)==2:
        a=set(results[keys[0]]); b=set(results[keys[1]])
        out.write(f"\nID PARITY: cheap_only={len(a-b)} accurate_only={len(b-a)} common={len(a&b)}\n")
        if a-b: out.write("  cheap_only sample: "+str(list(a-b)[:5])+"\n")
        if b-a: out.write("  accurate_only sample: "+str(list(b-a)[:5])+"\n")
    out.write(f"\nMODE={'DRY (wrote to wall_backups\\_DRY_*)' if dry else 'WRITE (overwrote deliverables)'}\n")
    open(r"c:\Users\josep\Kiro\pz_craft_loops\_gen_wall_result.txt","w",encoding="utf8").write(out.getvalue())

if __name__=="__main__":
    main()
