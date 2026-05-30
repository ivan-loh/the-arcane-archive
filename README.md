# The Arcane Archive

An unofficial, fan-built, static HTML wiki for the co-op wave-survival
magic-brawler *The Spell Brigade* by BoltBlasterGames.

- **No build tooling**, no server, no JavaScript framework.
- **No game art**, no audio, no logos — text-only by design.
- **No trackers**, no CDN, no external requests.

## Viewing the wiki

```
Open index.html in any modern browser.
```

That's it. There is no dev server, no `npm install`, no compile step. Every
page is a hand-written or generator-written `.html` file that links to two
CSS files and one JS file using **relative paths**, so it works equally well
from `file://`, a static host (GitHub Pages, S3, Netlify), or `python3 -m
http.server`.

If you want absolute paths to resolve (only matters for `404.html` and any
asset link that begins with `/`), serve the root with a tiny local server:

```bash
cd the-spell-brigade-wiki
python3 -m http.server 8000
# then open http://localhost:8000/
```

## Directory structure

```
the-spell-brigade-wiki/
  index.html             Landing page (this is what visitors see first)
  about.html             Wiki provenance, methodology, disclaimers
  styleguide.html        Visual styleguide (component showcase, for builders)
  404.html               Friendly not-found page with search and section links
  README.md              This file

  css/
    main.css             Layout, typography, colour tokens
    components.css       Item cards, badges, stat bars, tier rows, callouts, ...

  js/
    wiki.js              Single vanilla-JS file: search, table sort, mobile nav,
                         filters, stat-bar rendering. Progressive enhancement —
                         every feature degrades gracefully without JS.

  data/
    site-structure.md    Canonical IA contract every page must follow.
    search-index.json    Flat search index consumed by wiki.js search.
    spells.json          21 spells with infusions, variants, improvements.
    artifacts.json       20 artifacts with effect type and stat scaling.
    characters.json      15 heroes (+ 1 test character) with starter spells.
    enemies.json         36 enemies, including elites.
    bosses.json          3 bosses with phase data and bullet-hell patterns.
    waves.json           32 waves with spawn tables and probabilities.
    mechanics.json       36 stats, 21 elements, 4 rarities, 3 stat-calc types.
    meta.json            Worlds, curses, difficulties, modifiers, objectives,
                         upgrades, challenges, titles, team awards.

  templates/
    base.html            Shell with header/footer/sidebar slots.
    header.html          Top nav + search bar.
    footer.html          Site footer with browse and meta links.

  spells/    characters/    artifacts/    enemies/    bosses/
  worlds/    waves/         mechanics/    guides/     challenges/
                         Per-entity page directories — one .html per entry,
                         plus an index.html hub per section.

  images/                Intentionally empty (kept so relative image paths
                         don't 404 if a page ever adds an SVG decoration).
```

## Data source provenance

All wiki content is derived from the shipped game files of *The Spell Brigade*
(Unity compiled build). Two tools do the extraction:

- **the extraction pipeline** — unpacks Unity asset bundles into readable
  `.prefab`, `ScriptableObject`, and metadata files.
- **the extraction pipeline** — reconstructs C# class names, enum maps, and method
  signatures from the compiled `GameAssembly.dll`.

This wiki is a **snapshot of current build** (the
build hash from `boot.config`). When the developer ships a new build, the
extraction pipeline is re-run and affected pages are regenerated.

## How this wiki was generated

The wiki was produced by a parallel-agent pipeline:

1. **8 extractor agents** ran in parallel, each focused on one entity family
   (spells, artifacts, characters, enemies, bosses, waves, mechanics, meta).
   Every extractor verified its output twice against the raw dump before
   writing JSON to `data/`.
2. **8 builder agents** consumed those JSON files in parallel to produce the
   per-family HTML.
3. **5 reviewer agents** spot-checked the rendered HTML for data integrity,
   anchor consistency, cross-link validity, and accessibility.

The canonical site contract (URL conventions, anchor patterns, template
names, cross-linking rules) lives in `data/site-structure.md` and was
treated as a hard contract by every builder.

## The search index

`data/search-index.json` is a flat JSON array consumed by `js/wiki.js`. Each
entry looks like:

```json
{
  "title": "Bomb Launcher",
  "url": "spells/bomb-launcher.html",
  "kind": "spell",
  "tags": ["spell", "aoe", "explosive", "projectile", "fire", "ice"]
}
```

The search bar in the header (and on `404.html`) loads this file on first
keystroke, scores entries by title prefix / substring / tag hit, and renders
the top 10. No backend.

## Disclaimer

This wiki is **not affiliated with, endorsed by, or sponsored by
BoltBlasterGames**, the developer of *The Spell Brigade*. All game names,
trademarks, and assets belong to their respective owners. The wiki is a fan
project, text-only, with no game art or audio used.

Some mechanics are inferred from class names and parameter shapes rather
than confirmed in-game — these are flagged inline on the relevant pages. If
you spot a discrepancy, assume the game is correct.

Localized strings (item names, descriptions) that we could not extract from
the compressed Unity addressable bundles are shown as raw Unity localization
keys (e.g. `SpellName_Arrow`). These will be replaced as the string tables
are unpacked.

See [`about.html`](about.html) for the full provenance and methodology
write-up.

## License

The wiki's **HTML, CSS, and JavaScript source** are released for any use; the
**game data** it references belongs to BoltBlasterGames and is reproduced
here as a fan reference under fair-use principles (factual data, no art,
clearly labelled).


## Takedown / removal requests

If you are with BoltBlasterGames (or otherwise hold rights to any content reproduced here) and would like anything removed or modified, please [open an issue](https://github.com/ivan-loh/the-arcane-archive/issues/new) on this repo. Requests are honoured promptly &mdash; typically within 48 hours.
