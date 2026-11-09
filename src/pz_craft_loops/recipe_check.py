"""Validate B42 craftRecipe script files against the installed game + mods.

Checks every item / tag / timedAction / recipe Tag / category / skill a recipe uses, the
'-fluid' rule (the line above must be an amount-1 item), drainable amounts vs uses, and that
outputs exist. Prints one line per finding. Usage: python recipe_check.py <recipe.txt> [...]
"""
import os, re, sys, glob
from collections import defaultdict

GAME = r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media\scripts"
KBW = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\108600\3772269882\mods\KnoxBuildworks\42\media\scripts"


def strip_comments(t):
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)


def blocks(text, kind):
    """yield (module, name, body) for 'kind name { ... }' blocks (brace matched)."""
    text = strip_comments(text)
    for mm in re.finditer(r"\bmodule\s+(\w+)\s*\{", text):
        mod = mm.group(1)
        for m in re.finditer(r"\b%s\s+([^\s{]+(?:[ \t]+[^\s{]+)*)\s*\{" % kind, text[mm.end():]):
            start = mm.end() + m.end()
            depth, i = 1, start
            while depth and i < len(text):
                depth += {"{": 1, "}": -1}.get(text[i], 0)
                i += 1
            yield mod, m.group(1).strip(), text[start:i - 1]
        break


def load_items(roots):
    items, tags = {}, defaultdict(set)
    for root in roots:
        for p in glob.glob(os.path.join(root, "**", "*.txt"), recursive=True):
            t = open(p, encoding="utf-8", errors="replace").read()
            if "item " not in t:
                continue
            for mod, name, body in blocks(t, "item"):
                props = {}
                for line in body.split(","):
                    if "=" in line:
                        k, v = line.split("=", 1)
                        props[k.strip().lower()] = v.strip()
                full = "%s.%s" % (mod, name)
                items[full] = props
                for tg in re.split(r"[;\s]+", props.get("tags", "")):
                    if tg:
                        tags[tg.lower()].add(full)
    return items, tags


def load_words(roots, kind):
    s = set()
    for root in roots:
        for p in glob.glob(os.path.join(root, "**", "*.txt"), recursive=True):
            t = open(p, encoding="utf-8", errors="replace").read()
            s |= set(re.findall(r"\b%s\s+(\w+)\s*\{" % kind, strip_comments(t)))
    return s


def vanilla_recipe_fields(roots):
    """Values actually used in vanilla craftRecipes: Tags, category, timedAction, skills."""
    out = defaultdict(set)
    for root in roots:
        for p in glob.glob(os.path.join(root, "**", "*.txt"), recursive=True):
            t = open(p, encoding="utf-8", errors="replace").read()
            if "craftRecipe" not in t:
                continue
            for _m, _n, body in blocks(t, "craftRecipe"):
                for key in ("Tags", "category", "timedAction", "SkillRequired"):
                    for v in re.findall(r"\b%s\s*=\s*([^,\n]+)" % key, body):
                        for part in re.split(r";", v):
                            out[key].add(part.split(":")[0].strip().lower())
    return out


def check(path, items, tags, actions, vfields):
    res = []
    text = open(path, encoding="utf-8").read()
    for mod, name, body in blocks(text, "craftRecipe"):
        say = lambda lvl, msg: res.append("%-5s %s: %s" % (lvl, name, msg))
        for key in ("timedAction",):
            for v in re.findall(r"\btimedAction\s*=\s*(\w+)", body):
                if v not in actions:
                    say("ERROR", "timedAction %s is not defined in the game or KBW" % v)
        for v in re.findall(r"\bTags\s*=\s*([^,\n]+)", body):
            for tg in v.split(";"):
                if tg.strip().lower() not in vfields["Tags"]:
                    say("WARN", "recipe Tag %s is not used by any vanilla recipe" % tg.strip())
        for v in re.findall(r"\bcategory\s*=\s*(\w+)", body):
            if v.lower() not in vfields["category"]:
                say("WARN", "category %s is not used by any vanilla recipe" % v)
        for key in ("SkillRequired", "xpAward"):
            for v in re.findall(r"\b%s\s*=\s*([^,\n]+)" % key, body):
                for part in v.split(";"):
                    sk = part.split(":")[0].strip()
                    if sk.lower() not in vfields["SkillRequired"]:
                        say("ERROR", "%s skill %s not used by vanilla recipes (typo?)" % (key, sk))
        m_in = re.search(r"\binputs\s*\{(.*?)\}", body, re.S)
        m_out = re.search(r"\boutputs\s*\{(.*?)\}", body, re.S)
        lines = [l.strip().rstrip(",") for l in (m_in.group(1) if m_in else "").splitlines() if l.strip()]
        prev = None
        for l in lines:
            if l.startswith("-fluid"):
                if not prev or not re.match(r"item\s+1\s", prev):
                    say("ERROR", "'%s' must follow an amount-1 item line (got: %s)" % (l, prev))
                prev = l
                continue
            mi = re.match(r"item\s+(\d+)\s+(.*)$", l)
            if not mi:
                say("WARN", "unparsed input line: %s" % l)
                prev = l
                continue
            amt, rest = int(mi.group(1)), mi.group(2)
            ml = re.match(r"\[([^\]]*)\]", rest)
            mt = re.match(r"tags\[([^\]]*)\]", rest)
            if ml and ml.group(1).strip() == "*":
                pass
            elif ml:
                for it in ml.group(1).split(";"):
                    it = it.strip()
                    full = it if "." in it else "Base." + it
                    if full not in items:
                        say("ERROR", "input item %s does not exist" % full)
                        continue
                    p = items[full]
                    drain = "drainable" in p.get("itemtype", "").lower() or "usedelta" in p
                    if drain and "usedelta" in p:
                        try:
                            uses = int(round(1.0 / float(p["usedelta"])))
                        except ValueError:
                            uses = None
                        if uses and amt > uses:
                            say("ERROR", "item %d [%s]: %s has only %d uses" % (amt, it, full, uses))
                        else:
                            say("INFO", "item %d [%s]: drainable, %s uses of %s" % (amt, it, amt, uses))
                    elif amt > 1 and "mode:keep" not in rest:
                        say("INFO", "item %d [%s]: consumes %d whole items" % (amt, it, amt))
            elif mt:
                for tg in mt.group(1).split(";"):
                    n = len(tags.get(tg.strip().lower(), ()))
                    if not n:
                        say("ERROR", "tag %s matches no item" % tg.strip())
                    else:
                        say("INFO", "tag %s matches %d items" % (tg.strip(), n))
            else:
                say("WARN", "unparsed item list: %s" % l)
            prev = l
        for l in (m_out.group(1) if m_out else "").splitlines():
            mo = re.match(r"\s*item\s+(\d+)\s+([\w.]+)", l)
            if mo:
                full = mo.group(2) if "." in mo.group(2) else "Base." + mo.group(2)
                if full not in items:
                    say("ERROR", "output item %s does not exist" % full)
                else:
                    say("INFO", "output %s x%s ok" % (full, mo.group(1)))
    return res


if __name__ == "__main__":
    roots = [GAME, KBW]
    items, tags = load_items(roots)
    actions = load_words(roots, "timedAction")
    vf = vanilla_recipe_fields([GAME])
    print("loaded %d items, %d tags, %d timed actions" % (len(items), len(tags), len(actions)))
    for p in sys.argv[1:]:
        print("==", p)
        for r in check(p, items, tags, actions, vf):
            print("  " + r)
