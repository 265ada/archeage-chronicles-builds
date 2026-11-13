# ArcheAge Chronicles Class Builds

Start-to-endgame build guides for ArcheAge Chronicles (Early Access, November 2026). Each page includes:

- A stage-by-stage build (leveling, gearing, endgame) covering weapons, skills, traits, stat priority and gear, with checklists
- An interactive trait tree. Click a node to read it, double-click to unlock it, and use **Fill with my points** to follow the build order
- The endgame rotation
- A weapon point-split planner
- A table of where the guides disagree, plus sources

| Class | Build | Trait tree |
|---|---|---|
| [Berserker](docs/berserker-warhammer.html) | Fire & Thunder Warhammer (RaidDex Thunderclap) | Matches the in-game screen |
| [Ranger](docs/ranger-storm-hatchet.html) | Storm Hatchets with a Longbow opener | Matches the in-game screen |
| [Mage](docs/mage-thunderbolt.html) | Fire leveling to Thunderbolt Staff | Approximate layout |

**These builds have not been verified in-game.** They combine fan guides (RaidDex, ArcheAge Builds, AOEAH, Wikily and others), and every claim on each page is tagged by how many sources back it up. Trait node names and costs come from Wikily.

## Viewing

Open `docs/index.html` in a browser, or enable GitHub Pages for the `docs/` folder.

## Editing

The build data lives in `src/*.json`, and all three pages share `src/template.html`. To rebuild the site:

```bash
python src/build.py docs site
```

The build checks that every trait path unlocks each node only after something it requires, and prints each path's point total.

Fan-made, not affiliated with XLGAMES or Kakao Games.
