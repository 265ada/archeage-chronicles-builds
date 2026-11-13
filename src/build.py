"""Build the ArcheAge Chronicles class build pages.

Usage: python build.py <out_dir> <mode>
  mode "site"     -> pages link to each other by relative path (GitHub Pages)
  mode "artifact" -> pages link to the published claude.ai artifacts
"""
import json, sys, pathlib
here = pathlib.Path(__file__).parent
out_dir = pathlib.Path(sys.argv[1]); mode = sys.argv[2] if len(sys.argv) > 2 else "site"
tpl = (here / "template.html").read_text(encoding="utf-8")
CLASSES = [
    ("berserker", "Berserker", "Warhammer", "https://claude.ai/artifact/3DXEHfA24ULioZGEFqNhrF"),
    ("ranger", "Ranger", "Storm Hatchets", "https://claude.ai/artifact/3PZzK7ubzSiiaaP4Ko7Ly1"),
    ("mage", "Mage", "Thunderbolt Staff", "https://claude.ai/artifact/MgLdeEHG8UrS2aZR3MH3C6"),
]
datas = {k: json.loads((here / f"{k}.json").read_text(encoding="utf-8")) for k, *_ in CLASSES}
links = [{"id": datas[k]["id"], "cls": c, "build": b, "url": (u if mode == "artifact" else datas[k]["out"])} for k, c, b, u in CLASSES]
ok = True
for k, *_ in CLASSES:
    d = datas[k]; nodes = {n["id"]: n for n in d["tree"]["nodes"]}
    print(f"{k}: {len(nodes)} nodes")
    for n in nodes.values():
        for p in n.get("p", []):
            if p not in nodes: print("  missing parent", n["id"], p); ok = False
    for pr in d["tree"]["presets"]:
        have = set(); total = 0
        for i in pr["order"]:
            n = nodes.get(i)
            if not n: print("  unknown id", i); ok = False; continue
            ps = n.get("p", [])
            if i in have: print("  duplicate", i); ok = False
            if ps and not any(p in have for p in ps): print(f"  order error: {i} before any of {ps}"); ok = False
            have.add(i); total += n["c"]
        print(f"  preset {pr['name']}: {total} pts, {len(pr['order'])} nodes")
    html = (tpl.replace("__TITLE__", d["title"])
            .replace("__LINKS__", json.dumps(links, ensure_ascii=False))
            .replace("__DATA__", json.dumps(d, ensure_ascii=False).replace("</", r"<\/")))
    if mode == "site":
        # Same-site links, and a real document head (the claude.ai host adds one itself).
        html = html.replace('`<a class="cls" href="${c.url}" target="_blank" rel="noopener">', '`<a class="cls" href="${c.url}">').replace(' ↗</small>', '</small>')
        head = ('<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<style>body{margin:0}[hidden]{display:none!important}</style>\n')
        html = head + html + '\n</html>\n'
    (out_dir / d["out"]).write_text(html, encoding="utf-8")
if mode == "site":
    idx = (here / "index.html").read_text(encoding="utf-8")
    (out_dir / "index.html").write_text(idx, encoding="utf-8")
print("OK" if ok else "ERRORS")
sys.exit(0 if ok else 1)
