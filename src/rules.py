"""Trait tree rules inferred from in-game Traits screens.

- Cost: nodes marked "3" in-game cost 3; every other node costs 1.
  (Wikily lists some nodes at 2, but the Berserker screen had 4 points
  pending on Meteor Hammer, Meteor Hammer II, Evasive Assault and Fire ATK.)
  Stat-cluster nodes (the "Damage up" group) keep Wikily's listed cost.
- Choices: where two branches split and rejoin, you take one branch; the
  other locks (shown red in-game on the Hatchet screen).
"""
from itertools import combinations


def apply_costs(nodes):
    for n in nodes.values():
        n.setdefault("wc", n["c"])  # Wikily's listed cost, kept for reference
        if not n.get("sc"):
            n["c"] = 3 if n["wc"] == 3 else 1


def exclusive_pairs(nodes):
    par = {i: n.get("p", []) for i, n in nodes.items()}
    anc = {}
    def A(i):
        if i not in anc:
            s = set()
            for p in par[i]:
                s.add(p); s |= A(p)
            anc[i] = s
        return anc[i]
    depth = {}
    def D(i):
        if i not in depth:
            depth[i] = 1 + max((D(p) for p in par[i]), default=0)
        return depth[i]
    out = {}
    for m, n in nodes.items():
        ps = [p for p in par[m] if not nodes[p].get("f")]
        if len(ps) < 2:
            continue
        for a, b in combinations(ps, 2):
            ca = (A(a) | {a}) & (A(b) | {b})
            if not ca or a in ca or b in ca:
                continue
            s = max(ca, key=D)
            br = lambda x: frozenset(y for y in (A(x) | {x}) if s in A(y))
            ba, bb = br(a), br(b)
            if ba & bb:
                continue
            key = frozenset([ba, bb])
            out[key] = (s, m, sorted(ba), sorted(bb))
    return list(out.values())
