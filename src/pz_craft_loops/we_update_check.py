# -*- coding: utf-8 -*-
"""Read-only check after a World Essentials update (2026-11-14). For every file we track
(zomboid/WE_submods/upstream + work, the four submod folders), compare the installed WE copy with
upstream/ (the last baseline) and work/ (ours), and match changed files against our hand-off tags in
the pz-buildworks repo. JSON is compared as data (formatting / order ignored; buildables by id).
Writes _we_update_check.txt. Nothing is modified.

Categories per file:
  unchanged          installed == upstream (WE did not touch it)
  merged             installed == work (WE took exactly our version)
  merged-from-tag    installed equals one of our hand-off tags (which one is listed)
  WE-own-change      installed differs from upstream, work and every tag: needs a look
  new-in-WE / removed-by-WE
"""
import glob, json, os, subprocess, sys
from collections import Counter

WE = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3733324672\mods"
D = r"c:\Users\josep\Kiro\zomboid\WE_submods"
REPO = r"c:\Users\josep\Kiro\pz-buildworks"
GIT = sorted(glob.glob(os.path.join(os.environ["LOCALAPPDATA"], "GitHubDesktop", "app-*")))[-1] + r"\resources\app\git\cmd\git.exe"
PAIRS = [("World Essentials - Community Buildworks", "World Essentials - Community Buildworks", True),
         ("World Essentials - TikiTown Buildworks", "World Essentials - TikiTown Buildworks", True),
         ("World Essentials - Raven Creek Buildworks", "World Essentials - Raven Creek Buildworks", True),
         ("World Essentials", "World Essentials (base, our files only)", False),
         ("World Essentials - Knox Buildworks Expansion", "World Essentials - Knox Buildworks Expansion (our files only)", False)]


def norm(raw, name):
    if raw is None:
        return None
    if name.endswith(".json"):
        try:
            d = json.loads(raw.decode("utf-8-sig"))
            if isinstance(d, dict) and isinstance(d.get("buildables"), list):
                d = dict(d, buildables={b.get("id"): b for b in d["buildables"]})
            return ("json", json.dumps(d, sort_keys=True))
        except Exception:
            pass
    return ("raw", raw.replace(b"\r\n", b"\n"))


def read(p):
    return open(p, "rb").read() if os.path.isfile(p) else None


def files(root):
    s = set()
    if os.path.isdir(root):
        for dp, _dn, fn in os.walk(root):
            for f in fn:
                s.add(os.path.relpath(os.path.join(dp, f), root))
    return s


def tags():
    r = subprocess.run([GIT, "-C", REPO, "tag", "--sort=creatordate"], capture_output=True)
    return [t for t in r.stdout.decode().split() if t.startswith(("handoff-", "we-baseline-"))]


def at_tag(tag, ours, rel):
    r = subprocess.run([GIT, "-C", REPO, "show", "%s:we/%s/%s" % (tag, ours, rel.replace(os.sep, "/"))],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def main():
    acf = open(r"C:\Program Files (x86)\Steam\steamapps\workshop\appworkshop_108600.acf", encoding="utf-8").read()
    i = acf.find('"3733324672"')
    out = ["installed WE entry: " + " ".join(acf[i:i + 200].split())]
    ver = open(os.path.join(D, "UPSTREAM_VERSION.txt"), encoding="utf-8").read().splitlines()[:2]
    out += ["upstream/: " + " ".join(l.strip() for l in ver), ""]
    tag_list = tags()
    tally, lines = Counter(), []
    for inst_name, ours, full in PAIRS:
        inst, up, wk = os.path.join(WE, inst_name), os.path.join(D, "upstream", ours), os.path.join(D, "work", ours)
        rels = files(up) | files(wk)
        if full:
            rels |= files(inst)
        for rel in sorted(rels):
            ni, nu, nw = (norm(read(os.path.join(r, rel)), rel) for r in (inst, up, wk))
            if ni == nu:
                k = "unchanged"
            elif ni is None:
                k = "removed-by-WE"
            elif ni == nw:
                k = "merged"
            else:
                hit = [t for t in tag_list if norm(at_tag(t, ours, rel), rel) == ni]
                if hit:
                    k = "merged-from-tag " + hit[-1]
                elif nu is None and nw is None:
                    k = "new-in-WE"
                else:
                    k = "WE-own-change"
            tally[(ours, k)] += 1
            if k != "unchanged":
                lines.append("%-62s %-48s %s" % (ours[:62], k, rel))
    out += ["%-62s %-48s %d" % (a[:62], b, n) for (a, b), n in sorted(tally.items())]
    out += ["", "---- changed files"] + lines
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_we_update_check.txt")
    open(p, "w", encoding="utf-8").write("\n".join(out))
    print("\n".join(out[:3 + len(tally) + 1]))


if __name__ == "__main__":
    main()
