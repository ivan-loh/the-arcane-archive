# The Arcane Archive — Site Structure (Canonical IA)

This is the **canonical sitemap**. All downstream HTML builders MUST follow the
filenames, paths, anchors, and nav structure defined here. Wiki is **text-only,
static HTML**, no build tooling, no game art. All href values are
**relative**, computed from a page's own directory.

---

## 1. Design principles

- **Gamer-first**: a player alt-tabs in mid-run with a question. Every top-nav
  click reaches the answer in <=2 hops.
- **Stable, predictable URLs**: `/<section>/<slug>.html`. Kebab-case. No
  query strings. No JS routing.
- **Hub-and-spoke**: every section has an `index.html` hub listing all entries
  with filterable facets (client-side JS, progressive enhancement; the page
  must remain usable with JS disabled).
- **Cross-link aggressively**: any noun mentioned (spell, element, artifact,
  hero, enemy) is a link to its canonical page.
- **One concept = one canonical URL**. Aliases redirect via simple
  `<meta http-equiv="refresh">` only if needed.
- **Long pages over many tiny pages**: a spell's base + 5 infusions + 3
  variants + 3 improvements live on one page with anchors.

---

## 2. URL & filename conventions

- All lowercase, kebab-case: `bomb-launcher.html`, `wizard-king.html`.
- Internal source names in PascalCase (`BombLauncher`) are slugified to
  `bomb-launcher`. Maintain a `data/slug-map.json` (downstream concern) so
  builders agree on the transform.
- Section hubs: `<section>/index.html`. Never link to bare directory; always
  the explicit `index.html` for static-host portability (file://, S3, GH Pages).
- Anchors are kebab-case, prefixed by semantic group:
  `#infusion-fire`, `#variant-ricochet`, `#improvement-2`, `#synergy-heroes`.
- Asset folders: `/css/` (shared stylesheets), `/js/` (filter/search scripts),
  `/data/` (JSON dumps consumed by JS facets; never user-visited).
- The repo's `/images/` directory stays empty — kept only so relative paths
  for hypothetical SVG decorations don't break. **Do not put raster art there.**

---

## 3. Top navigation (7 items, fixed order)

Appears as a horizontal nav bar on every page. Order is meaningful — left to
right is roughly "what I cast" -> "who casts it" -> "what I fight" -> "how
it works".

1. **Spells**          -> `/spells/index.html`
2. **Heroes**          -> `/characters/index.html`
3. **Artifacts**       -> `/artifacts/index.html`
4. **Enemies & Bosses**-> `/enemies/index.html`
5. **Worlds & Waves**  -> `/worlds/index.html`
6. **Mechanics**       -> `/mechanics/index.html`
7. **Guides**          -> `/guides/index.html`

Persistent right-side utility links: **Challenges** (`/challenges/index.html`)
and **Search** (`/search.html`). Challenges are large but secondary — they
don't deserve a top slot but must be one click from anywhere.

Home `/index.html` is the wordmark; clicking it returns to the landing page.

---

## 4. Full sitemap tree

Every leaf below is one HTML file. Counts in parentheses confirm
content-extraction coverage.

```
/index.html                              Landing: quick-cards to top hubs, "new player start here", search box
/search.html                             Client-side faceted search over all entities (uses /data/*.json)
/about.html                              Fan wiki disclaimer, data sources, contributors
/changelog.html                          Wiki edit log (game patch notes optional)

/spells/                                 (21 spell types)
  index.html                             Grid of all 21 spells; facets: archetype (projectile/aoe/melee/summon/utility), element-affinity, single/multi-target
  arrow.html
  beam.html
  bell.html
  bomb-launcher.html
  book.html
  boomerang.html
  energy-zone.html
  falling-star.html
  fence.html
  laser.html
  meteor.html
  mine.html
  orb.html
  plant.html
  proximity.html
  rifle.html
  shotgun.html
  slash.html
  smg.html
  summon.html
  trail.html

/characters/                             (~15 heroes)
  index.html                             Roster grid; facets: starter spell, playstyle tag, unlock condition
  bell-mage.html
  moon-mage.html
  wizard-king.html
  hatty.html
  ...one file per hero
  skins.html                             Aggregate page: all skins (4-5 each) grouped by hero, plus halloween/winter/prestige sets

/artifacts/                              (20 passive items)
  index.html                             Grid; facets: trigger (on-hit/on-crit/on-kill/passive/conditional), stat scaled, rarity
  artifact-01-<name>.html                Files numbered AND named for predictable URLs
  ...20 total
  by-effect.html                         Pivot index: groups artifacts by semantic-type tag (IncreaseDamagePerArmor, HealOnCrit, ...)

/enemies/                                (36 enemy types + 4 elites + 3 bosses)
  index.html                             Bestiary hub; facets: world, role (swarm/tank/ranged/elite), element vulnerability
  bosses/
    index.html                           The three boss profiles
    squid.html                           3-phase boss; anchors per phase
    hydra.html
    toad.html
  elites/
    index.html
    elite-<name>.html                    4 files
  regular/
    <enemy-slug>.html                    36 files, one per enemy type
  events.html                            5 enemy events (swarm spawns, etc.)

/worlds/                                 (4 worlds)
  index.html                             World picker with at-a-glance threat profile
  verdant-meadows.html
  pyrestorm-pit.html
  astral-riftlands.html
  frozen-ancients.html

/waves/                                  (32 waves) — sub-section of Worlds in nav, separate folder for cleaner URLs
  index.html                             Wave timeline; jump-links to each wave
  wave-01.html ... wave-32.html          Per-wave: enemy mix, spawn probabilities, recommended counters
  comparison.html                        Sortable table: all 32 waves, density, elite-chance, boss-flag

/challenges/                             (148 across 16 categories)
  index.html                             Categories grid; total counts; completion-tracker note (browser localStorage, optional)
  boss.html
  covenant.html
  curse.html
  element.html
  enchantment.html
  halloween-skin.html
  objective.html
  prestige-skin.html
  realm.html
  relic.html
  relic-drop.html
  skin.html
  spell.html
  threat-level.html
  winter-skin.html
  wizard.html
                                         Each category page lists all challenges in that category
                                         as a long anchor-linked list. With 148 total / 16 cats,
                                         most pages are short enough for one HTML file.

/mechanics/                              (the rules of the game)
  index.html                             Hub: cards for each subsystem
  damage-calculation.html                CENTERPIECE — see section 10
  elements.html                          All 21 ElementTypes; rock-paper-scissors matrix table
  element-matrix.html                    Standalone interactive matrix (same data, lookup-optimized)
  stats.html                             All 40 StatTypes with definitions and stacking rules
  rarities.html                          4 RarityTypes; how rarity influences drops and rolls
  stat-calculation.html                  3 StatCalculationTypes (additive/multiplicative/override) with worked examples
  upgrades.html                          5 upgrade tiers, 120 upgrade levels — cost curve, what unlocks where
  character-improvements.html            13 per-character upgrades; how they layer with global upgrades
  curses.html                            7 curses
  difficulties.html                      3 difficulties; scaling formulas
  modifiers.html                         3 modifiers; how they interact with curses
  objectives.html                        10 objectives (run goals)
  titles.html                            ~250 player titles, grouped by acquisition theme
  team-awards.html                       11 team awards (co-op end-screen)

/guides/                                 (curated articles)
  index.html                             Featured guides + full list
  new-player-primer.html                 "I just downloaded the game"
  coop-roles.html                        Tank / DPS / utility framings for co-op
  build-fire-burst.html                  Element-themed build guides (one per element family that has 2+ supporting spells)
  build-ice-control.html
  build-lightning-chain.html
  build-arcane-summon.html
  build-nature-dot.html
  build-shadow-curse.html
  best-spells-per-hero.html              Cross-cut: each hero's top 3 spell pairings
  artifact-priority.html                 Pickup tier list with rationale
  wave-survival-15-plus.html             Mid-to-late wave tactics
  boss-kill-order.html                   Phase-by-phase tips for each boss
  challenge-completion-route.html        Suggested order to clear all 148 challenges
```

Total HTML files: roughly 250-280, dominated by 36 enemies, 32 waves, 21
spells, 20 artifacts, ~15 heroes, 16 challenge categories, ~15 guides.

---

## 5. Sidebar / sub-nav patterns

Each section has a left sidebar listing siblings, so you can hop between
spells (or artifacts, etc.) without bouncing to the hub.

- **Spells sidebar**: 21 entries grouped by archetype header (Projectile,
  AOE, Melee, Summon, Utility). Current page highlighted.
- **Characters sidebar**: alphabetical roster + "Skins" link at top.
- **Artifacts sidebar**: numerical 01-20 list with effect-tag suffix
  (`07 - HealOnCrit`) so users learn the numbering they see in-game.
- **Enemies sidebar**: collapsible tree -> Bosses / Elites / Regular (by
  world) / Events.
- **Worlds sidebar**: 4 worlds + "All Waves" + "Wave Comparison".
- **Mechanics sidebar**: ordered for learning (Elements -> Stats ->
  Stat Calculation -> Damage Calculation -> Rarities -> Upgrades -> Curses
  -> Difficulties -> Modifiers -> Objectives -> Titles -> Team Awards).
- **Guides sidebar**: grouped by Primer / Build Guides / Hero Guides /
  Encounter Guides / Meta Guides.
- **Challenges sidebar**: 16 categories with count badges.

Sidebar is the same HTML partial conceptually but each section provides its
own list. On narrow viewports it collapses to a `<details>` element above
the main content — pure HTML, no JS required.

---

## 6. Cross-linking strategy

Every entity page carries a **"Related"** section near the bottom plus
inline links in prose. Specific link contracts:

- **Spell page** links to:
  - Each `ElementType` page used in its infusions (`/mechanics/elements.html#fire` etc.)
  - Heroes whose starter spell is this one, and heroes whose
    character-improvements buff this spell type
  - Artifacts that name this spell type or its stat (e.g., projectile-count
    artifacts on projectile spells)
  - Relevant build guides
- **Artifact page** links to:
  - The `StatType` it scales with (`/mechanics/stats.html#armor`)
  - Spells most affected by that stat
  - Heroes whose kit synergizes
- **Hero page** links to:
  - Their starter spell, recommended spells, anti-synergies
  - Their unlock challenge (in `/challenges/...`)
  - Their skins on the skins page (anchor)
- **Enemy / boss page** links to:
  - World(s) and wave(s) they appear in
  - Element vulnerabilities (-> `/mechanics/element-matrix.html`)
  - Counter spells / artifacts
- **Wave page** links to:
  - Each enemy in the spawn table (with spawn probability)
  - The world it's part of, prev/next wave
- **Mechanics pages** link laterally to each other and "see also" guides.
- **Guide articles** are the main outbound linker — every noun is a link.

A **breadcrumb** sits above every non-home page:
`Home / Spells / Bomb Launcher` — purely from the URL.

---

## 7. Landing-page priority (above-the-fold on `/index.html`)

Ordered by likely first-question frequency for a mid-run player:

1. **Search bar** (jumps to `/search.html` with query)
2. **Spells** quick-grid (most common lookup: "what does my next pick do?")
3. **Artifacts** quick-grid (#2 most common, especially "artifact 13")
4. **Damage Calculation** featured card linking to the centerpiece guide
5. **Element Matrix** thumbnail (CSS-grid table preview)
6. **Current run helpers**: "Which wave am I on?" -> waves index;
   "What's this boss?" -> bosses index
7. **New player primer** card (low-traffic for veterans but high-impact for new)
8. **Build guides** carousel

No marketing fluff above these.

---

## 8. Search / filter UX

- **Global search** (`/search.html`): single input, client-side over a
  prebuilt JSON index at `/data/search-index.json`. Results grouped by
  entity type. No server.
- **Per-hub facets** (rendered as checkbox groups; JS filters the DOM grid
  in place, URL hash mirrors state e.g. `#element=fire&rarity=epic` for
  shareable filtered views):

| Hub        | Facets that matter most                                       |
|------------|---------------------------------------------------------------|
| Spells     | archetype, element-affinity, target-shape, hits-multi-target |
| Heroes     | starter spell, role tag, unlock difficulty                   |
| Artifacts  | trigger condition, stat scaled, rarity, effect-tag           |
| Enemies    | world, role, element-weakness, elite?, boss?                 |
| Waves      | world, has-elite, has-boss, density bucket                   |
| Challenges | category, est. difficulty, requires-DLC-skin                 |
| Mechanics  | (no facets; curated nav)                                     |
| Guides     | topic tag, skill level, co-op vs solo                        |

- **Sort options** on tabular pages (waves comparison, artifact list, stat
  list): sortable `<th>` via tiny JS; default sort always defined in HTML.
- **Keyboard**: `/` focuses search input on every page (one shared JS file).

---

## 9. Page templates

Downstream HTML agents should implement exactly these templates. Names are
the contract.

1. **`layout-base`** — shell: header, top nav, breadcrumb, sidebar slot,
   main slot, footer.
2. **`hub-index`** — grid of cards + facet sidebar. Used by every
   `<section>/index.html`.
3. **`spell-page`** — fixed sections (see anchor pattern below).
4. **`artifact-page`** — effect summary, scaling table, synergy list.
5. **`hero-page`** — kit summary, starter spell, improvements table,
   skins list, unlock, synergies.
6. **`enemy-page`** — stat block, behavior, appears-in waves, weaknesses,
   counters.
7. **`boss-page`** — multi-phase variant of enemy-page with per-phase
   anchors.
8. **`wave-page`** — spawn table, timeline strip, recommended counters.
9. **`world-page`** — world overview + wave list + enemy roster.
10. **`mechanics-explainer`** — long-form prose with worked examples and
    formula blocks (use `<pre>` and semantic `<math>` where helpful).
11. **`matrix-table`** — element-matrix and similar 2D lookups (CSS grid).
12. **`comparison-table`** — sortable table template (waves comparison,
    artifact comparison).
13. **`guide-article`** — long-form editorial with TOC, callouts, links.
14. **`challenge-category`** — anchored long-list template.
15. **`search-page`** — input + result groups.

---

## 10. Anchor patterns inside long pages

Strict, identical across every page of the same template — predictable
deep-linkability is the whole point.

**Spell page** (`/spells/<slug>.html`):
```
#overview          Top summary (one paragraph + key stats card)
#base              Base configuration: damage, cooldown, projectiles, scaling
#infusions         Section header
  #infusion-fire   one anchor per element variant present
  #infusion-ice
  #infusion-lightning
  #infusion-arcane
  #infusion-nature
#variants          Section header
  #variant-<slug>  one anchor per variant (~3)
#improvements      Section header
  #improvement-1
  #improvement-2
  #improvement-3
#synergies         Sub-anchors: #synergy-heroes, #synergy-artifacts, #synergy-spells
#counters          What this spell struggles against
#related           Outbound link list
```

**Artifact page**:
`#overview / #effect / #scaling / #triggers / #synergies / #counters / #related`

**Hero page**:
`#overview / #kit / #starter-spell / #improvements / #skins / #unlock / #synergies / #related`

**Enemy / Boss**:
`#overview / #stats / #behavior / #phase-1 / #phase-2 / #phase-3 (boss only) / #weaknesses / #appears-in / #counters / #related`

**Wave page**:
`#overview / #timeline / #spawn-table / #elites / #counters / #related`

**Mechanics explainers** use a TOC of `#section-N` for stability while
content evolves.

---

## 11. The Damage Calculation guide (centerpiece)

**Location**: `/mechanics/damage-calculation.html`. Lives in Mechanics, not
Guides, because it's reference material; Guides reference it heavily.

**Why here**: a player looking up "why did my fireball do 47?" wants
mechanics, not opinion. Putting it in Mechanics also lets every spell,
artifact, and stat page link to its canonical anchor.

**Structure (anchors)**:

```
#overview             One-paragraph TL;DR with the master formula
#formula              The full damage formula in a <pre> block, every term named
#term-glossary        Each variable links out to its source page
  #term-base
  #term-element-mult
  #term-rarity-mult
  #term-stat-mult
  #term-crit
  #term-armor
  #term-resist
#order-of-operations  Step-by-step with a labelled diagram (CSS/SVG only)
#worked-examples      Section header
  #example-basic      A single hit, no crit, no armor
  #example-crit       With crit chance & multiplier
  #example-elemental  Element matchup vs neutral
  #example-artifact   With one artifact modifier (e.g., IncreaseDamagePerArmor)
  #example-coop       Two players stacking
#element-matchups     Embedded element matrix preview + link to full matrix
#stat-stacking        How additive vs multiplicative vs override interact
                      (links to /mechanics/stat-calculation.html for depth)
#armor-resist         Defense math from the receiving side
#edge-cases           Caps, floors, integer truncation, on-hit triggers
#patch-notes          Reserved for tracked changes to formula across versions
#related              Links to: elements, stats, stat-calculation, rarities,
                      every artifact that modifies damage, build guides
```

**Cross-linking IN to this page** (must be enforced by builders):

- Every **spell page** `#base` block links its damage row to
  `damage-calculation.html#formula`.
- Every **artifact page** that touches a damage term links to the
  specific term anchor (e.g., `#term-stat-mult`).
- Every **element page** entry links to `#element-matchups`.
- Every **stat page** entry for a damage-related stat links to
  `#term-stat-mult` and `#stat-stacking`.
- **Build guides** open with a "Math behind this build ->" callout to the
  relevant worked example anchor.

**Cross-linking OUT** is exhaustive: every named term is a hyperlink the
first time it appears in a section, then plain text afterwards (to keep
prose readable).

**Companion page**: `/mechanics/element-matrix.html` is a lookup-optimized
sibling — same data presented as a sortable, filterable matrix for players
who just want the multiplier. Both pages cross-link in their headers.

---

## 12. Footer (every page)

- Left: "Fan wiki, not affiliated with the developers. Data extracted from
  game files for reference."
- Middle: link to `/about.html`, `/changelog.html`.
- Right: "Back to top" anchor.

---

## 13. Out of scope (do not build)

- Account system, comments, edit history UI.
- Any image of the game; any audio.
- Server-side anything.
- A 404 page is optional; static hosts handle it.

---

End of canonical structure. Builders: if a page you need is not listed
here, **stop and update this doc first** before creating the file.
