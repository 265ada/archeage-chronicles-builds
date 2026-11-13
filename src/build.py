"""Build the ArcheAge Chronicles class build pages.

Usage: python build.py <out_dir> <mode>
  mode "site"     -> pages link to each other by relative path (GitHub Pages)
  mode "artifact" -> pages link to the published claude.ai artifacts

Granted (free) skills: every non-stat node that does not descend from the
weapon's Proficiency node or from a stat node, plus Proficiency itself. These
are the "default (white) skills" shown lit in the in-game Traits screen.
"""
import json, re, sys, pathlib

here = pathlib.Path(__file__).parent
out_dir = pathlib.Path(sys.argv[1]); mode = sys.argv[2] if len(sys.argv) > 2 else "site"
tpl = (here / "template.html").read_text(encoding="utf-8")
CLASSES = [
    ("warrior", "Warrior", "Frostbreaker Greatsword", "https://claude.ai/artifact/TmKPL4wci49SP6QTKfAZbY"),
    ("berserker", "Berserker", "Warhammer", "https://claude.ai/artifact/3DXEHfA24ULioZGEFqNhrF"),
    ("ranger", "Ranger", "Storm Hatchets", "https://claude.ai/artifact/3PZzK7ubzSiiaaP4Ko7Ly1"),
    ("mage", "Mage", "Thunderbolt Staff", "https://claude.ai/artifact/MgLdeEHG8UrS2aZR3MH3C6"),
]
urls = json.loads((here / "urls.json").read_text()) if (here / "urls.json").exists() else {}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load_txt(name):
    nodes, by_name = [], {}
    for line in (here / "trees" / f"{name}.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        r, n, t, c, ps, e = line.split("|", 5)
        node = {"id": slug(n), "r": int(r), "n": n, "t": t, "c": int(c), "e": e, "_pn": [p for p in ps.split(";") if p]}
        assert node["id"] not in by_name.values(), node["id"]
        by_name[n] = node["id"]; nodes.append(node)
    for node in nodes:
        node["p"] = [by_name[p] for p in node.pop("_pn")]
    return nodes, by_name


def flag(tree):
    nodes = {n["id"]: n for n in tree["nodes"]}
    kids = {i: [] for i in nodes}
    for n in nodes.values():
        for p in n.get("p", []):
            kids[p].append(n["id"])
    def reach(starts):
        seen, st = set(), list(starts)
        while st:
            x = st.pop()
            if x in seen: continue
            seen.add(x); st.extend(kids[x])
        return seen
    prof = [i for i, n in nodes.items() if n["n"].endswith("Proficiency")]
    from_prof = reach(prof)
    stat_roots = [i for i, n in nodes.items() if n["t"] == "T" and not n.get("p")]
    from_stat = reach(stat_roots)
    for i, n in nodes.items():
        n.pop("f", None); n.pop("sc", None)
        if i in prof or (n["t"] != "T" and i not in from_prof and i not in from_stat):
            n["f"] = 1
        if i in from_stat:
            n["sc"] = 1
    return nodes


ok = True
datas = {k: json.loads((here / f"{k}.json").read_text(encoding="utf-8")) for k, *_ in CLASSES}
links = [{"id": datas[k]["id"], "cls": c, "build": b, "url": (urls.get(k, u) if mode == "artifact" else datas[k]["out"])} for k, c, b, u in CLASSES]
for k, *_ in CLASSES:
    d = datas[k]
    trees = []
    for spec in d["trees"]:
        tree = dict(spec)
        if "file" in spec:
            tree["nodes"], by_name = load_txt(spec["file"])
            for pr in tree["presets"]:
                pr["order"] = [by_name[x] for x in pr["order"]]
        trees.append(tree)
    d["trees"] = trees
    for ti, tree in enumerate(trees):
        nodes = flag(tree)
        for n in nodes.values():
            for p in n.get("p", []):
                if p not in nodes: print("  missing parent", n["id"], p); ok = False
        free = [n["n"] for n in nodes.values() if n.get("f")]
        print(f"{k}/{tree['weapon']}: {len(nodes)} nodes, {len(free)} free")
        for pr in tree["presets"]:
            have = {i for i, n in nodes.items() if n.get("f")}; total = 0; order = []
            for i in pr["order"]:
                n = nodes.get(i)
                if not n: print("  unknown id", i); ok = False; continue
                if n.get("f"): continue
                ps = n.get("p", [])
                if i in have: print("  duplicate", i); ok = False
                if ps and not any(p in have for p in ps): print(f"  order error: {i} before any of {ps}"); ok = False
                have.add(i); total += n["c"]; order.append(i)
            pr["order"] = order
            print(f"  path {pr['name']}: {total} pts, {len(order)} nodes")
            if ti == 0 and pr is tree["presets"][0]:
                d["split"]["mainMin"] = total
    html = (tpl.replace("__TITLE__", d["title"])
            .replace("__LINKS__", json.dumps(links, ensure_ascii=False))
            .replace("__DATA__", json.dumps(d, ensure_ascii=False).replace("</", r"<\/")))
    if mode == "site":
        html = html.replace('`<a class="cls" href="${c.url}" target="_blank" rel="noopener">', '`<a class="cls" href="${c.url}">').replace(' ↗</small>', '</small>')
        head = ('<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<style>body{margin:0}[hidden]{display:none!important}</style>\n')
        html = head + html + '\n</html>\n'
    (out_dir / d["out"]).write_text(html, encoding="utf-8")
if mode == "site":
    (out_dir / "index.html").write_text((here / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
print("OK" if ok else "ERRORS")
sys.exit(0 if ok else 1)
