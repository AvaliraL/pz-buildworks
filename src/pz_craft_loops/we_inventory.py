# -*- coding: utf-8 -*-
"""Inventory of what our WORK copy adds / changes versus the LIVE (Steam) World Essentials submods.

  python we_inventory.py   -> zomboid/WE_submods/HANDOFF_INVENTORY.md

Also checks LIVE against our upstream/ snapshot: any difference means WE updated since our baseline
and work/ must be reconciled before the hand-off.
"""
import os, json, hashlib, collections, datetime

K = r"c:\Users\josep\Kiro"
LIVE = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3733324672\mods"
WE = os.path.join(K, "zomboid", "WE_submods")
OUT = os.path.join(WE, "HANDOFF_INVENTORY.md")
SUBS = [("World Essentials - Community Buildworks", "World Essentials - Community Buildworks"),
        ("World Essentials - TikiTown Buildworks", "World Essentials - TikiTown Buildworks"),
        ("World Essentials (base, our files only)", "World Essentials")]
SKIP = {"mod.info", "bundled_source.txt", "workshop.txt", "preview.png", "poster.png"}


def files(root):
    out = {}
    if not os.path.isdir(root):
        return out
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root).replace("\\", "/")] = p
    return out


def sha(p):
    return hashlib.sha1(open(p, "rb").read()).hexdigest()


def jload(p):
    try:
        return json.load(open(p, encoding="utf-8-sig"))
    except Exception:
        return None


def buildables(doc):
    """{id: buildable} for a definitions document."""
    out = {}
    if isinstance(doc, dict):
        for b in doc.get("buildables") or []:
            if isinstance(b, dict) and b.get("id"):
                out[b["id"]] = b
    return out


def same_json(a, b):
    return jload(a) == jload(b) and jload(a) is not None


def group_of(bid):
    parts = bid.split(".")
    return ".".join(parts[:3]) if len(parts) >= 3 else bid


def grouped(ids):
    """Counter of ids by group; collapses to 2 segments when there are too many groups."""
    c = collections.Counter(group_of(i) for i in ids)
    if len(c) > 12:
        c = collections.Counter(".".join(i.split(".")[:2]) for i in ids)
    return c


def diff_keys(old, new):
    """Which parts of a buildable changed: top-level keys and, for stages, the stage keys."""
    out = set()
    for k in set(old) | set(new):
        if k == "stages":
            os_, ns = old.get("stages") or [], new.get("stages") or []
            if len(os_) != len(ns):
                out.add("stages(count)")
                continue
            for a, b in zip(os_, ns):
                for sk in set(a) | set(b):
                    if a.get(sk) != b.get(sk):
                        out.add("stage." + sk)
        elif old.get(k) != new.get(k):
            out.add(k)
    return out


def main():
    L = []
    w = L.append
    w("# World Essentials hand-off inventory")
    w("")
    w("Generated %s by `pz_craft_loops/we_inventory.py`." % datetime.date.today().isoformat())
    w("Compares our `work/` copy against the LIVE Steam World Essentials (Workshop 3733324672).")
    w("")
    # ---- 1. has WE changed since our baseline? -------------------------------------------
    w("## 1. Has live WE changed since our baseline (`upstream/`)?")
    w("")
    drift_total = 0
    for work_name, live_name in SUBS:
        up = files(os.path.join(WE, "upstream", work_name))
        lv = files(os.path.join(LIVE, live_name))
        drift = []
        for rel, p in up.items():
            if os.path.basename(rel) in SKIP:
                continue
            if rel not in lv:
                drift.append(("removed in live", rel))
            elif sha(p) != sha(lv[rel]):
                drift.append(("changed in live", rel))
        drift_total += len(drift)
        w("- **%s**: %d of %d baseline files differ in live%s" % (
            work_name, len(drift), len(up), "" if drift else " (baseline is current)"))
        for kind, rel in drift[:40]:
            w("    - %s: `%s`" % (kind, rel))
        if len(drift) > 40:
            w("    - ... %d more" % (len(drift) - 40))
    w("")
    if drift_total:
        w("> **Live WE differs from our baseline.** Refresh `upstream/` (`_refresh_upstream.py`) and "
          "reconcile `work/` before handing off; the sections below compare against LIVE regardless.")
        w("")
    # ---- 2. work vs live ----------------------------------------------------------------
    w("## 2. Our work vs LIVE")
    w("")
    summary = []
    detail = []
    for work_name, live_name in SUBS:
        wk = files(os.path.join(WE, "work", work_name))
        lv = files(os.path.join(LIVE, live_name))
        added, changed, same = [], [], 0
        for rel, p in wk.items():
            if os.path.basename(rel) in SKIP:
                continue
            if rel not in lv:
                added.append(rel)
            elif sha(p) == sha(lv[rel]) or (rel.endswith(".json") and same_json(p, lv[rel])):
                same += 1
            else:
                changed.append(rel)
        summary.append((work_name, len(added), len(changed), same))
        detail.append((work_name, wk, lv, sorted(added), sorted(changed)))
    w("| Submod | New files | Changed files | Identical |")
    w("|---|---:|---:|---:|")
    for n, a, c, s in summary:
        w("| %s | %d | %d | %d |" % (n, a, c, s))
    w("")

    for work_name, wk, lv, added, changed in detail:
        w("### %s" % work_name)
        w("")
        # buildable-level inventory for definitions
        new_b = collections.OrderedDict()
        chg_b = collections.OrderedDict()
        chg_kinds = collections.OrderedDict()
        for rel in added + changed:
            if "/KnoxBuildworks/definitions/" not in rel or not rel.endswith(".json"):
                continue
            nd = buildables(jload(wk[rel]))
            od = buildables(jload(lv[rel])) if rel in lv else {}
            for bid, b in nd.items():
                if bid not in od:
                    new_b.setdefault(rel, []).append(bid)
                elif od[bid] != b:
                    chg_b.setdefault(rel, []).append(bid)
                    kc = chg_kinds.setdefault(rel, collections.Counter())
                    for kk in diff_keys(od[bid], b):
                        kc[kk] += 1
        gone = collections.OrderedDict()
        for rel in changed:
            if "/KnoxBuildworks/definitions/" in rel and rel.endswith(".json"):
                nd = buildables(jload(wk[rel]))
                od = buildables(jload(lv[rel]))
                miss = [b for b in od if b not in nd]
                if miss:
                    gone[rel] = miss
        tot_new = sum(len(v) for v in new_b.values())
        tot_chg = sum(len(v) for v in chg_b.values())
        tot_gone = sum(len(v) for v in gone.values())
        w("**Buildables: %d new, %d changed, %d removed.**" % (tot_new, tot_chg, tot_gone))
        w("")
        if new_b:
            w("New buildables, by definitions file:")
            w("")
            for rel, ids in new_b.items():
                grp = grouped(ids)
                w("- `%s` (%s): **%d**" % (os.path.basename(rel), "new file" if rel in added else "existing file", len(ids)))
                for g, n in sorted(grp.items()):
                    w("    - `%s`: %d" % (g, n))
            w("")
        if chg_b:
            w("Changed buildables (same id, different definition):")
            w("")
            for rel, ids in chg_b.items():
                w("- `%s`: **%d** changed; what differs: %s" % (
                    os.path.basename(rel), len(ids),
                    ", ".join("%s x%d" % (k, n) for k, n in sorted(chg_kinds[rel].items(), key=lambda t: -t[1]))))
                for i in ids[:3]:
                    w("    - e.g. `%s`" % i)
            w("")
        if gone:
            w("Buildables present in live but REMOVED in ours:")
            w("")
            for rel, ids in gone.items():
                w("- `%s`: %s" % (os.path.basename(rel), ", ".join("`%s`" % i for i in ids[:20])))
            w("")
        # non-definition files
        other_new = [r for r in added if "/KnoxBuildworks/definitions/" not in r]
        other_chg = [r for r in changed if "/KnoxBuildworks/definitions/" not in r]
        if other_new:
            w("New non-definition files:")
            w("")
            for r in other_new:
                w("- `%s` (%d bytes)" % (r, os.path.getsize(wk[r])))
            w("")
        if other_chg:
            w("Changed non-definition files:")
            w("")
            for r in other_chg:
                extra = ""
                if r.endswith("IG_UI.json") or r.endswith("Tooltip.json"):
                    nd, od = jload(wk[r]) or {}, jload(lv[r]) or {}
                    if isinstance(nd, dict) and isinstance(od, dict):
                        ak = [k for k in nd if k not in od]
                        ck = [k for k in nd if k in od and nd[k] != od[k]]
                        extra = " - %d keys added, %d changed" % (len(ak), len(ck))
                elif r.endswith("manifest.json"):
                    nd, od = jload(wk[r]) or {}, jload(lv[r]) or {}
                    na = {d if isinstance(d, str) else json.dumps(d, sort_keys=True) for d in nd.get("definitions", [])}
                    oa = {d if isinstance(d, str) else json.dumps(d, sort_keys=True) for d in od.get("definitions", [])}
                    extra = " - %d definition files added, %d removed" % (len(na - oa), len(oa - na))
                w("- `%s`%s" % (r, extra))
            w("")
        # live-only files (informational)
        gone_files = [r for r in lv if r not in wk and os.path.basename(r) not in SKIP
                      and work_name != "World Essentials (base, our files only)"]
        if gone_files:
            w("Files in LIVE that our work copy does not have (%d):" % len(gone_files))
            w("")
            for r in sorted(gone_files)[:40]:
                w("- `%s`" % r)
            w("")
    notes = os.path.join(WE, "HANDOFF_NOTES.md")
    if os.path.isfile(notes):
        w("## 3. Notes for the WE dev")
        w("")
        w(open(notes, encoding="utf-8").read().rstrip())
        w("")
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("wrote", OUT, len(L), "lines")


if __name__ == "__main__":
    main()
