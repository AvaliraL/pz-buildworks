# -*- coding: utf-8 -*-
"""Export our tile-sheet work into the git repo (c:\\Users\\josep\\Kiro\\pz-buildworks).

The repo replaces zipped hand-offs to the World Essentials dev: he gets a GitHub compare link.

  python export_repo.py --baseline   # we/ <- zomboid/WE_submods/upstream (WE's shipped version)
  python export_repo.py              # we/ <- zomboid/WE_submods/work, plus src/ and notes/

History model: commit the baseline whenever WE updates (after _refresh_upstream.py), then commit
our work on top. Each hand-off = compare link between the baseline tag and our commit.
Mirrors trees: files removed on our side are removed from the repo too.
"""
import os, sys, shutil, filecmp

K = r"c:\Users\josep\Kiro"
REPO = os.path.join(K, "pz-buildworks")
P = os.path.join(K, "pz_craft_loops")
SUBMODS = ["World Essentials - Community Buildworks", "World Essentials - TikiTown Buildworks",
           "World Essentials (base, our files only)"]

SRC_SCRIPTS = [
    "build_community_mod.py", "build_tikitown_mod.py", "build_merged_test_mod.py", "kbw_tilepatch.py",
    "we_sync.py", "we_dylan.py", "tooltip_fix.py", "name_tooltip_pass.py", "we_bug_pass.py",
    "_vendor_we_dylan.py", "_refresh_upstream.py", "_run_all.py", "patch_we_tooltips.py",
    "_audit_faces.py", "classify_wall_pieces.py", "gen_wall_full.py", "export_repo.py",
    "align_appliance_costs.py", "counter_variants.py", "container_caps.py", "rotation_fix.py",
    # sheet generators + bench tools (deliverables are built from these)
    "dirkies_couches.py", "dirkies_bedroom.py", "dirkies_stairs.py", "tikitown_tterika_storage.py",
    "bench_tools.py", "we_inventory.py",
]
TIKI_SRC = [  # build_tikitown_mod.SRC_FILES
    "21_tikitown_walls_accurate.json", "22_tikitown_doors.json", "23_tikitown_furniture.json",
    "24_tikitown_bookshelves.json", "25_tikitown_bedroom.json", "26_tikitown_glass_accurate.json",
    "27_tikitown_newburbs_interiors_accurate.json", "28_tikitown_newburbs_walls_accurate.json",
    "29_tikitown_garages.json", "30_tikitown_shelving.json", "31_tikitown_newburbs_roofs_accurate.json",
    "32_tikitown_newburbs_flags.json", "33_tikitown_newburbs_doors_accurate.json",
    "34_tikitown_newburbs_windows_accurate.json",
]


def mirror(src, dst, keep=lambda rel: True):
    """Make dst an exact copy of src (filtered by keep). Returns (added, changed, removed)."""
    a = c = r = 0
    want = {}
    for d, _, fs in os.walk(src):
        for f in fs:
            rel = os.path.relpath(os.path.join(d, f), src)
            if keep(rel):
                want[rel] = os.path.join(d, f)
    have = set()
    if os.path.isdir(dst):
        for d, _, fs in os.walk(dst):
            for f in fs:
                have.add(os.path.relpath(os.path.join(d, f), dst))
    for rel in have - set(want):
        os.remove(os.path.join(dst, rel)); r += 1
    for rel, s in want.items():
        t = os.path.join(dst, rel)
        if os.path.isfile(t) and filecmp.cmp(s, t, shallow=False):
            continue
        c += os.path.isfile(t); a += not os.path.isfile(t)
        os.makedirs(os.path.dirname(t), exist_ok=True)
        shutil.copy2(s, t)
    for d, ds, fs in sorted(os.walk(dst, topdown=False), reverse=False):   # prune empty dirs
        if d != dst and not os.listdir(d):
            os.rmdir(d)
    return a, c, r


def _json_style(raw):
    """Find a json.dumps style that reproduces `raw` (bytes) exactly, or None."""
    import json
    try:
        text = raw.decode("utf-8-sig")
        data = json.loads(text)
    except Exception:
        return None
    bom = raw.startswith(b"\xef\xbb\xbf")
    nl = "\r\n" if "\r\n" in text else "\n"
    for indent in (1, 2, 4, "\t", None):
        for ascii_ in (False, True):
            for seps in (None, (",", ":")):
                body = json.dumps(data, indent=indent, ensure_ascii=ascii_, separators=seps)
                for tail in ("", nl):
                    cand = body.replace("\n", nl) + tail
                    if cand == text:
                        return (indent, ascii_, seps, nl, tail, bom)
    return None


def match_we_format(we_dir, baseline_dir):
    """Rewrite each changed JSON in we_dir in the exact formatting of its baseline file, so a
    compare shows only real changes. Only when the style reproduces the baseline byte for byte."""
    import json
    done, skipped = 0, []
    for d, _, fs in os.walk(we_dir):
        for f in fs:
            if not f.endswith(".json"):
                continue
            p = os.path.join(d, f)
            q = os.path.join(baseline_dir, os.path.relpath(p, we_dir))
            if not os.path.isfile(q):
                continue
            style = _json_style(open(q, "rb").read())
            if style is None:
                skipped.append(os.path.relpath(p, we_dir)); continue
            indent, ascii_, seps, nl, tail, bom = style
            data = json.loads(open(p, "rb").read().decode("utf-8-sig"))
            out = json.dumps(data, indent=indent, ensure_ascii=ascii_, separators=seps).replace("\n", nl) + tail
            raw = (b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8")
            if raw != open(p, "rb").read():
                open(p, "wb").write(raw); done += 1
    return done, skipped


def mirror_files(src_dir, names, dst):
    tmp = {n for n in names if os.path.isfile(os.path.join(src_dir, n))}
    return mirror(src_dir, dst, keep=lambda rel: rel in tmp)


def main():
    baseline = "--baseline" in sys.argv
    root = os.path.join(K, "zomboid", "WE_submods", "upstream" if baseline else "work")
    out = []
    for s in SUBMODS:
        if os.path.isdir(os.path.join(root, s)):
            out.append(("we/" + s, mirror(os.path.join(root, s), os.path.join(REPO, "we", s))))
    if not baseline:
        up = os.path.join(K, "zomboid", "WE_submods", "upstream")
        for s in SUBMODS:
            if os.path.isdir(os.path.join(REPO, "we", s)):
                n, skipped = match_we_format(os.path.join(REPO, "we", s), os.path.join(up, s))
                print("%-40s reformatted %d JSON to WE's style; style unknown for %d: %s"
                      % ("we/" + s, n, len(skipped), skipped[:5]))
        out.append(("src/pz_craft_loops", mirror_files(P, SRC_SCRIPTS, os.path.join(REPO, "src", "pz_craft_loops"))))
        ct = os.path.join(K, "zomboid", "communitytilepack")
        out.append(("src/communitytilepack/deliverables", mirror(os.path.join(ct, "deliverables"), os.path.join(REPO, "src", "communitytilepack", "deliverables"))))
        out.append(("src/communitytilepack/vendor_we", mirror(os.path.join(ct, "vendor_we"), os.path.join(REPO, "src", "communitytilepack", "vendor_we"))))
        ct_docs = [f for f in os.listdir(ct) if f.endswith((".md", ".csv"))]
        out.append(("src/communitytilepack (docs)", mirror_files(ct, ct_docs, os.path.join(REPO, "src", "communitytilepack", "docs"))))
        tk = os.path.join(K, "zomboid", "tikitown")
        tk_files = TIKI_SRC + [f for f in os.listdir(tk) if f.endswith(".md") or f == "WALL_SHEET_INDEX_REFERENCE.txt"]
        out.append(("src/tikitown", mirror_files(tk, tk_files, os.path.join(REPO, "src", "tikitown"))))
        notes = os.path.join(REPO, "notes")
        os.makedirs(notes, exist_ok=True)
        for s in (os.path.join(K, "zomboid", "WE_submods", "BUG_PASS_2026-11-01.md"),
                  os.path.join(K, "zomboid", "WE_submods", "HANDOFF_INVENTORY.md"),
                  os.path.join(K, "zomboid", "WE_submods", "HANDOFF_NOTES.md"),
                  os.path.join(K, "zomboid", "WE_submods", "UPSTREAM_VERSION.txt"),
                  os.path.join(K, ".kiro", "steering", "we-submods-workflow.md"),
                  os.path.join(K, ".kiro", "steering", "pz-kahlua-lua.md")):
            if os.path.isfile(s):
                shutil.copy2(s, os.path.join(notes, os.path.basename(s)))
    for name, (a, c, r) in out:
        print("%-40s added %4d  changed %4d  removed %4d" % (name, a, c, r))


if __name__ == "__main__":
    main()
