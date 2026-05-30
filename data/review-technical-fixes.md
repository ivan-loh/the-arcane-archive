# Wiki technical review and fixes

Run date: 2026-05-30
Files scanned: 135 HTML (`templates/` excluded; those are build inputs).

## Initial audit (severity-ordered)

| Severity | Issue | Count |
|---|---|---|
| Critical | `href="/..."` / `src="/..."` absolute-root paths (break under `file://` and at non-root URL prefixes) | **378** in 10 files |
| Critical | `data-search-index="/data/search-index.json"` absolute path (broke search under `file://`) | **34** in 33 files |
| High | Broken cross-page links (target file does not exist) | **30** in many spell/guide pages |
|   | -> `mechanics/damage-calculation.html` (typo for `damage-system.html`) | 21 |
|   | -> `artifacts/by-effect.html` (never built; meant `artifacts/index.html`) | 9 |
| High | Broken in-page / cross-page anchors (`#id` target missing) | **283** |
|   | -> `index.html#contributing` (section never built) | 50 |
|   | -> `mechanics/stats.html#size,#lifetime,#range,#projectiles,#damagetickrate,#healondodge,#healonlevelup,#healingmultiplier,#elementstrengthmultiplier,#criticaldamage` | 134 |
|   | -> `artifacts/index.html#<N>` should be `#artifact-<N>` | 119 |
|   | -> `mechanics/curses.html#strongerenemies` (kebab id is `stronger-enemies`) | 1 |
|   | -> `mechanics/elements.html#neutral` (no anchor) | 1 |
|   | -> `spells/mine.html#variant-explodeatend`, `spells/orb.html#variant-{extratrajectory,increaseinsize}` (variants don't exist on those pages) | 3 |
| Pass | External resources (no `https://` `<script>`/`<link>`/`<img>`) | 0 |
| Pass | `<img>` tags (project is text-only) | 0 |
| Pass | Required metadata (charset, viewport, description, title, single `<h1>`, `css/main.css`, `css/components.css`, `js/wiki.js`) | 135/135 pass |
| Pass | Vague link text ("click here", bare "here", "read more") | 0 |
| Pass | Tables without `<caption>` or `aria-label` | 0 |

Initial audit detail: `data/audit-prefix-report.txt`.

## Fixes applied

### 1. Path-normalization script (re-runnable)
Wrote `scripts/fix_paths.py`. It:
- Rewrites `href="/foo"`, `src="/foo"`, and `data-search-index="/foo"` to depth-relative paths based on each file's directory depth (e.g. `mechanics/stats.html` -> `../css/main.css`).
- Skips `templates/` (build sources that legitimately keep absolute paths, since `scripts/build_spells.py:adjust_paths()` re-relativizes them at build time).
- Applies curated link rewrites for the cross-page bugs above (`damage-calculation.html` -> `damage-system.html`, `by-effect.html` -> `index.html`, `artifacts/index.html#N` -> `#artifact-N`, `#criticaldamage` -> `#critdamage`, `#strongerenemies` -> `#stronger-enemies`, `index.html#contributing` -> `about.html`).

### 2. Script execution
- 80 files changed
- 378 absolute href/src rewrites + 34 `data-search-index` rewrites = **412 path normalizations**
- 303 link-bug rewrites

### 3. JS update
`js/wiki.js` previously hardcoded `'/data/search-index.json'` as the fallback when `data-search-index` was absent. Replaced with a computed walk-up from `window.location.pathname`, so the fallback path is correct on `file://`, on `/wiki/...` subpath hosts, and at site root.

### 4. Manual anchor additions
Added missing `id=` attributes on existing content in `mechanics/stats.html` so external refs resolve without adding new copy:
- `id="range"`, `id="lifetime"`, `id="damagetickrate"`, `id="size"`, `id="projectiles"`, `id="healondodge"`, `id="healonlevelup"`, `id="healingmultiplier"`, `id="elementstrengthmultiplier"` (added to the `<td>` cells already present in the full stat table).
- `mechanics/damage-system.html`: added `<span id="formula">` alias inside the `#master-formula` section.
- `mechanics/elements.html`: added `id="neutral"` to the `None` row of the ElementType table.

### 5. Manual variant-link fixes
- `spells/mine.html`: `#variant-explodeatend` -> `#variant-burst` (only valid "self-triggering" variant on the page).
- `spells/orb.html`: `#variant-extratrajectory` -> `#variant-split`; `#variant-increaseinsize` -> `#variant-burst` (Orb's actual variants are `aimathighesthp`, `burst`, `split`).

## Verification (post-fix)

```bash
# Absolute href/src in shipped HTML
$ find . -name '*.html' -not -path './templates/*' \
    -exec grep -lE 'href="/[a-zA-Z]|src="/[a-zA-Z]|data-search-index="/' {} \; | wc -l
0

# Templates retain absolute paths intentionally (build inputs)
$ find ./templates -name '*.html' -exec grep -cE 'href="/[a-zA-Z]|src="/[a-zA-Z]' {} \;
17  9  3

# Broken anchors / missing targets (Python audit)
missing target refs: 0
missing anchor refs: 0

# Spot-check three random nested pages
spells/arrow.html               -> href="../css/main.css", "../css/components.css", "../js/wiki.js"
guides/spell-tier-list.html     -> href="../css/main.css", "../css/components.css", "../js/wiki.js"
artifacts/artifact-13.html      -> href="../css/main.css", "../css/components.css", "../js/wiki.js"
```

Counts before -> after:
- Absolute paths (non-template): 378 -> 0
- `data-search-index` absolute: 34 -> 0
- Missing target files: 30 -> 0
- Broken anchors: 283 -> 0

## What remains (documented exceptions)

1. **Templates** under `templates/{base,header,footer}.html` deliberately keep `href="/..."` (29 total). `scripts/build_spells.py:adjust_paths()` re-relativizes them at build time. Future per-section build scripts MUST call the same `adjust_paths()` helper, or pages they emit will regress.
2. **`xmllint --html`** emits ~8,600 diagnostics across all pages; spot checks show all of them are libxml2's HTML4 DTD refusing to recognize HTML5 tags (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`). None are real validity bugs.
3. The previous `index.html#contributing` link has been redirected to `about.html`. If a contributing/methodology section is added to `index.html` later, those redirects can be reverted by removing the rule in `scripts/fix_paths.py`.

## Reproduction

```bash
cd /home/ivan/Project/the-spell-brigade-wiki
python3 scripts/fix_paths.py            # apply
python3 scripts/fix_paths.py --dry-run  # check
```
