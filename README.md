# ArcheAge Chronicles Class Builds

Start-to-endgame build guides for ArcheAge Chronicles (Early Access, November 2026). Each page includes:

- A stage-by-stage build (leveling, gearing, endgame) covering weapons, skills, traits, stat priority and gear, with checklists
- An interactive trait tree. Click a node to read it, double-click to unlock it, and use **Fill with my points** to follow the build order
- The endgame rotation
- A weapon point-split planner
- A table of where the guides disagree, plus sources

| Class | Build | Trait trees |
|---|---|---|
| [Warrior](docs/warrior-frostbreaker.html) | Frostbreaker Greatsword with a Longsword healing swap | Greatsword and Longsword (both match the in-game screens) |
| [Berserker](docs/berserker-warhammer.html) | Fire & Thunder Warhammer (RaidDex Thunderclap) | Warhammer (matches the in-game screen) and Axe & Shield |
| [Ranger](docs/ranger-storm-hatchet.html) | Storm Hatchets with a Longbow opener | Hatchets (matches the in-game screen) and Longbow |
| [Mage](docs/mage-thunderbolt.html) | Fire leveling to Thunderbolt Staff | Elemental Staff and Wavesword (approximate layout) |

**Trait rules used** (inferred from in-game Traits screens):
- 47 Raeven's Coilstones × 2 points = **94 trait points** in Early Access, shared by both weapons: 22 in Diamond Shores (Lv ~7–20), 50 by the end of Gylden Ruins (~21–35), and 94 in Astron Plains (~36–40).
- Nodes marked "3" in-game cost 3. Every other node costs 1. Wikily's 2-point costs don't match the in-game screens.
- Where two branches split and rejoin, you take one side, and the other locks (red in-game).
- Stats: 3 points per level, 117 by Lv 40. Endurance (+6.6 SP and +4.2 defense per point, AAC Tools demo values) is weighted second on every class.

**Granted skills:** each weapon's default skills cost no trait points. That's Proficiency plus every skill that doesn't branch from it (the lit cluster on the left of the in-game Traits screen). They're marked ✓ and excluded from point totals.

**These builds have not been verified in-game.** They combine fan guides (RaidDex, ArcheAge Builds, AOEAH, Wikily and others), and every claim on each page is tagged by how many sources back it up. Trait node names, costs and requirements for all 8 weapons come from Wikily. Plain-text tree data lives in `src/trees/`.

## Viewing

Open `docs/index.html` in a browser, or enable GitHub Pages for the `docs/` folder.

## Editing

The build data lives in `src/*.json`, and all four pages share `src/template.html`. To rebuild the site:

```bash
python src/build.py docs site
```

The build checks that every trait path unlocks each node only after something it requires, and prints each path's point total.

Fan-made, not affiliated with XLGAMES or Kakao Games.
