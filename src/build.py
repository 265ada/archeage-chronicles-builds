"""Build the ArcheAge Chronicles class build pages.

Usage: python build.py <out_dir> <mode>
  mode "site"     -> pages link to each other by relative path (GitHub Pages)
  mode "artifact" -> pages link to the published claude.ai artifacts

Rules (see rules.py): granted skills are free, unmarked nodes cost 1 and
"3"-marked nodes cost 3, and each fork that rejoins is a one-side choice.
Each class's plans are checked step by step against those rules and the
94-point Early Access cap.
"""
import json, re, sys, pathlib

here = pathlib.Path(__file__).parent
sys.path.insert(0, str(here))
from rules import apply_costs, exclusive_pairs

out_dir = pathlib.Path(sys.argv[1]); mode = sys.argv[2] if len(sys.argv) > 2 else "site"
tpl = (here / "template.html").read_text(encoding="utf-8")
POS = json.loads((here / "positions.json").read_text(encoding="utf-8"))
CLASSES = [
    ("warrior", "Warrior", "Frostbreaker Greatsword", "https://claude.ai/artifact/TmKPL4wci49SP6QTKfAZbY"),
    ("berserker", "Berserker", "Warhammer", "https://claude.ai/artifact/3DXEHfA24ULioZGEFqNhrF"),
    ("ranger", "Ranger", "Storm Hatchets", "https://claude.ai/artifact/3PZzK7ubzSiiaaP4Ko7Ly1"),
    ("mage", "Mage", "Thunderbolt Staff", "https://claude.ai/artifact/MgLdeEHG8UrS2aZR3MH3C6"),
]
MILESTONES = [
    {"region": "Diamond Shores", "levels": "Lv ~7–20", "stones": 11, "pts": 22},
    {"region": "Gylden Ruins", "levels": "Lv ~21–35", "stones": 14, "pts": 50},
    {"region": "Astron Plains", "levels": "Lv ~36–40", "stones": 22, "pts": 94},
]
CAP = MILESTONES[-1]["pts"]


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
    return nodes


def flag(nodes):
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
    from_stat = reach([i for i, n in nodes.items() if n["t"] == "T" and not n.get("p")])
    for i, n in nodes.items():
        n.pop("f", None); n.pop("sc", None)
        if i in prof or (n["t"] != "T" and i not in from_prof and i not in from_stat):
            n["f"] = 1
        if i in from_stat:
            n["sc"] = 1


ok = True
def err(msg):
    global ok
    ok = False; print("  ERROR:", msg)

datas = {k: json.loads((here / f"{k}.json").read_text(encoding="utf-8")) for k, *_ in CLASSES}
links = [{"id": datas[k]["id"], "cls": c, "build": b, "url": (u if mode == "artifact" else datas[k]["out"])} for k, c, b, u in CLASSES]
for k, *_ in CLASSES:
    d = datas[k]
    trees = []
    for spec in d["trees"]:
        tree = {kk: v for kk, v in spec.items() if kk not in ("presets",)}
        nodes = load_txt(spec["file"]) if "file" in spec else spec["nodes"]
        tree["nodes"] = nodes
        N = {n["id"]: n for n in nodes}
        flag(N); apply_costs(N)
        p = POS.get(spec.get("file", ""))
        if p:
            byn = {n["n"]: n for n in nodes}
            assert set(p["pos"]) == set(byn), set(p["pos"]) ^ set(byn)
            for name, (x, y) in p["pos"].items():
                byn[name]["x"] = round(x * p["fx"]); byn[name]["y"] = round(y * p["fy"])
            tree["groups"] = [{"x": round(g["x"] * p["fx"]), "y": round(g["y"] * p["fy"]), "text": g["text"]} for g in p["groups"]]
            tree["wrap"] = 14
        tree["ex"] = [[a, b] for s, m, a, b in exclusive_pairs(N)]
        trees.append(tree)
        free = sum(1 for n in nodes if n.get("f"))
        print(f"{k}/{tree['weapon']}: {len(nodes)} nodes, {free} free, {len(tree['ex'])} fork pairs{' (screen layout)' if p else ''}")
    d["trees"] = trees
    d["milestones"] = MILESTONES
    for plan in d["plans"]:
        have = [{n["id"] for n in t["nodes"] if n.get("f")} for t in trees]
        steps, run, marks = [], 0, []
        per = [0] * len(trees)
        for st in plan["steps"]:
            ti, name = st[0], st[1]; why = st[2] if len(st) > 2 else ""
            t = trees[ti]; byn = {n["n"]: n for n in t["nodes"]}
            n = byn.get(name)
            if not n: err(f"{plan['name']}: unknown node {name!r} in {t['weapon']}"); continue
            i = n["id"]
            if n.get("f"): err(f"{plan['name']}: {name} is granted free"); continue
            if i in have[ti]: err(f"{plan['name']}: duplicate {name}")
            if n.get("p") and not any(q in have[ti] for q in n["p"]): err(f"{plan['name']}: {name} before its prerequisite")
            for A, B in t["ex"]:
                if (i in A and have[ti] & set(B)) or (i in B and have[ti] & set(A)):
                    err(f"{plan['name']}: {name} breaks a fork choice in {t['weapon']}")
            have[ti].add(i); run += n["c"]; per[ti] += n["c"]; steps.append([ti, i, why] if why else [ti, i])
            for m in MILESTONES:
                if run - n["c"] < m["pts"] and run > m["pts"]: err(f"{plan['name']}: {name} straddles the {m['pts']}-point checkpoint")
            if run in (22, 50): print(f"    at {run}: " + " / ".join(f"{t['weapon']} {v}" for t, v in zip(trees, per)))
            for m in MILESTONES:
                if run - n["c"] < m["pts"] <= run - 0 and run > m["pts"]:
                    marks.append(f"crosses {m['pts']} at {name}")
        plan["steps"] = steps
        if run > CAP: err(f"{plan['name']}: {run} points is over the {CAP} cap")
        print(f"  plan {plan['name']}: {run} pts ({' / '.join(f'{t['weapon']} {v}' for t, v in zip(trees, per))}), {CAP - run} left")
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
