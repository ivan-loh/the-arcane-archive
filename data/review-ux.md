# UX Review — Gamer Perspective

## Overall verdict: 3 / 5 stars

The wiki is content-rich, opinionated, fast (text-only, no CDN), and visually pleasant — a strong skeleton for a "very good fan wiki". But it has a critical findability problem that bites the most important persona (mid-run lookup): **the search index URLs do not match the actual filenames, and the home page advertises 7 guides that don't exist**. Once you know how to click your way past those traps, the actual content (boss strategy, artifact priorities, damage guide, tier list) is genuinely useful. Fix the broken links and this becomes a 4.5 / 5.

---

## Persona 1 — Mid-run lookup ("Increase Damage Per Armor")

- **Time to answer (happy path):** 3 clicks (home → Artifacts → sidebar "13 — Increase Damage Per Armor"). Acceptable.
- **Time to answer if I use the search bar:** infinite. I typed "armor" or "damage per armor" and the index returns `artifacts/artifact-13-increase-damage-per-armor.html`, which 404s. Real file is `artifact-13.html`. **This is the #1 critical bug** — every artifact result in the search box is a dead link (`/home/ivan/Project/the-spell-brigade-wiki/data/search-index.json`).
- **Clarity score:** 5 / 10. Once on `artifacts/artifact-13.html`:
  - The overview literally says "ArtifactType enum: `IncreaseDamagePerArmor` (id 13). Affects Damage. Spawn rate 50." — jargon-first, no plain-English summary up top.
  - The Parameters table is honest but unhelpful mid-run: parameter `[0] = 1` confidence "guess", `[1] = 0.25` confidence "inferred — likely 0.25% per armor… or 0.25 multiplier per Parameters[0] armor". A paused player cannot use that to decide buy/skip.
  - "When to pick" gives 3 short bullets — these are the only useful sentences and they should be at the top, not 2/3 down the page.
- **Friction points:**
  - The hero paragraph on the page leaks `DynamicStatModifier`, `IL2CPP`, `ArtifactStatModifier_IncreaseDamagePerArmor`, `RVA 0x24FA380`, `Dump line 262186`. None of this matters to a gamer mid-run.
  - "Source & references" dl is the longest block on the page. It should be collapsed behind a `<details>` summary like "Reverse-engineering notes".
  - Sidebar "Related" links `../guides/artifact-priority.html` (singular) — file is `artifact-priorities.html` (plural). Another broken link.
- **Recommended improvements:**
  - Above the fold: a 1-sentence plain-English effect (e.g. "+25% damage at 100 Armor; scales linearly") and a verdict line ("SSS tier — see Artifact Priorities").
  - Confidence pills already exist — promote them next to the headline number so I see at a glance the value is a guess.
  - Hide the RVA/dump-line block by default.
  - Fix the search-index slug mismatch (highest priority).

---

## Persona 2 — Build planner (crit-stacking Wizard King)

- **Expected click trail:** home → Damage Guide → Tier List → Artifact Priorities → Wizard King.
- **What actually happens:**
  1. Home "Read the Damage Guide" button → `mechanics/damage-calculation.html` → **404**. The file is `mechanics/damage-system.html`. The "Most useful pages" card and the "Browse" tile both link to the wrong path. 63 pages across the wiki link to the missing `damage-calculation.html`.
  2. If I land on the Guides hub instead, the suggested reading order works (`damage-optimization.html`, `element-pairing.html`, `spell-tier-list.html`, `artifact-priorities.html`). These four guides are good — the tier list has a real ranked grid, the priorities page has a global tier list **and** per-archetype pick orders. Solid content.
  3. The Artifact Priorities tier chips link `../artifacts/index.html#13` — but the actual anchor on the index is `id="artifact-13"`. So clicking "#13 Damage / Armor" scrolls to the top, not the card. Same for every other tier chip.
  4. Wizard King page: clean stat block, the "+10 CritChance" delta is highlighted nicely (`is-modified` row). Synergy section is one paragraph — adequate but light. The "Related" tile to `guides/best-spells-per-hero.html` is **another broken link** (file doesn't exist).
- **Findability:** 6 / 10 once you avoid the home-page traps and use the global top nav (Heroes / Spells / Artifacts / Guides).
- **Clarity score:** 7 / 10 for the actual guide content; the Damage Optimization + Artifact Priorities pair is the best content on the wiki and clearly the authorial centerpiece.
- **Friction points:**
  - No "Wizard King build" page exists. The persona wants "crit-stacking Wizard King" but has to assemble it themselves from Wizard King + tier list + priorities. A per-hero build page is what `best-spells-per-hero.html` was supposed to be.
  - Cross-links from Wizard King → specific artifacts (HealOnCrit, CritDamage While Standing Still) are missing. The synergy paragraph mentions "crit-damage upgrades" but doesn't link to the relevant artifact pages.
- **Recommended improvements:**
  - Fix the artifact anchor IDs (or change the priority page links) so the tier chips actually jump to the artifact card.
  - On every hero page, add a small "Recommended artifacts" panel that lists 3–5 specific artifacts as links (driven by the existing archetype tag).
  - Build the missing `best-spells-per-hero.html` — even a stub table of hero → top 3 spells from the tier list would close the persona's loop.

---

## Persona 3 — Boss prep (Toad in World 1)

- **Click trail:** home → mobile-nav "Bosses" (note: bosses is **not** in the desktop top nav — `/home/ivan/Project/the-spell-brigade-wiki/index.html` line 30-37 only lists 7 sections and Bosses isn't one of them — you reach it via the "Bosses · 3" tile or the footer or the mobile nav). Two clicks to Toad. Acceptable.
- **Toad page quality:** This is the best page on the wiki for the gamer persona. The stat block uses `<dl>` for fast scanning, the strategy guide has 5 numbered subsections, callouts for Pro tip / Do not, an explicit "Pre-bait the kill toward an arena edge" actionable tip, phase transition tells with the 50% HP marker. Recommended spells are linked (Venom Mist, Glacial Shard).
- **Clarity score:** 8.5 / 10. Genuinely useful even for a player paused mid-run.
- **Friction points:**
  - "See also" links `../guides/beginners-primer.html` — **broken** (no such file; guides hub has no beginner primer).
  - "Recommended spells & artifacts" mentions `HealOnCrit` and `Grim Pact` as italics, **not links**. I have to go hunt them.
  - Header says "Slowest of the three bosses by a wide margin (2.25 m/s)" — great context. But there's no link from this page to a per-spell "kiteable" tag/filter; the player has to know which spells qualify.
  - Persona asked about "Squid in World 1" — Squid is actually the **Scorched Abyss** boss, Toad is Verdant Meadows. The bosses hub page makes this clear ("Squid · Scorched Abyss / Pyrestorm Pit") but the worlds index isn't directly cross-linked from each boss card — `../worlds/index.html` (no anchor) just dumps you on a generic page.
- **Recommended improvements:**
  - On every boss page, link every italicized spell/artifact name (HealOnCrit, Grim Pact, Venom Mist already linked).
  - Add a "World" field to each boss header that links to the specific world subpage (`worlds/verdant-meadows.html` etc), so the journey "I am in World N → which boss?" works in reverse too.
  - Add Bosses to the desktop top nav. There is no reason it's omitted while Worlds / Mechanics / Guides are present.

---

## Cross-cutting findings

### Navigation consistency
- **Desktop top nav and mobile nav diverge.** Desktop has 7 links (no Bosses, no Waves, no Challenges, no About). Mobile has 11. Pick one and apply uniformly, or at minimum add Bosses to desktop — they're a core gameplay concern.
- One page says "Heroes", another says "Characters" for the same section. The home page top-nav says "Heroes" (line 31) but the artifacts page top-nav says "Characters" (line 25). Inconsistent label.
- Breadcrumbs are present on every page checked — good.

### Search coverage and correctness
- 196 entries indexed. Coverage of titles (artifacts, spells, bosses, heroes, mechanics) is broad.
- **All 20 artifact result URLs are broken** (slug format vs. numeric format). This silently destroys the primary entry point for the mid-run-lookup persona.
- Wizard King result URL is correct (`characters/wizard-king.html`). Boss/spell URLs are correct. Only the artifact slugs are wrong.

### Mobile concerns
- Stat tables wrap in `<div class="stat-table-wrap">` — good, they should scroll horizontally on 360px.
- The artifacts comparison table has 5 columns and will be cramped on mobile; the wrapper makes it survivable but a "card view" toggle would help.
- The site uses `clamp()` for hero font size — responsive.
- Sidebar on `.page.has-sidebar` should be verified to collapse/hide below ~720px. (Cannot test from HTML alone; recommend a manual check.)

### Jargon issues (specific instances)
- `artifacts/artifact-13.html` line 105: "ArtifactType enum: `IncreaseDamagePerArmor` (id 13)" — leading with internal enum names.
- `artifacts/index.html` line 106-115: overview paragraph drops `DynamicStatModifier`, `event-driven`, "PlayerMotor" without inline explanation.
- Every artifact page: "Source & references" dl exposes RVA addresses, dump line numbers, asset filenames. Belongs in a collapsed `<details>`.
- `mechanics/damage-calculation.html` (when fixed) and `stats.html` are referenced as "the place where jargon is explained" — a real glossary page (or inline `<abbr title="…">` on first use) would help.
- Spell tier list uses `ExtraProjectile`, `IncreaseSizeAndDamageWithEveryAttack`, `BellZoneGivesArmor` as bare `<code>` strings — at minimum, link them to the upgrades page or define them.

### Missing cross-links / broken links (specific)
- `/home/ivan/Project/the-spell-brigade-wiki/index.html` line 93, 144 → `mechanics/damage-calculation.html` (file is `damage-system.html`). **63 files reference this missing path.**
- `/home/ivan/Project/the-spell-brigade-wiki/index.html` line 269 → `mechanics/rarities.html` (file is `rarity.html`).
- `/home/ivan/Project/the-spell-brigade-wiki/index.html` lines 277-284 → 7 guide files that don't exist: `new-player-primer.html`, `coop-roles.html`, `build-fire-burst.html`, `build-ice-control.html`, `build-lightning-chain.html`, `best-spells-per-hero.html`, `boss-kill-order.html`. The home page is selling content the wiki doesn't have.
- `/home/ivan/Project/the-spell-brigade-wiki/artifacts/index.html` line 90 → `guides/artifact-priority.html` (file is `artifact-priorities.html`, plural). Same wrong path in all 20 artifact subpages' sidebars.
- `/home/ivan/Project/the-spell-brigade-wiki/artifacts/artifact-13.html` line 172 → `mechanics/stat-calculation.html` (doesn't exist).
- `/home/ivan/Project/the-spell-brigade-wiki/bosses/toad.html` line 258 → `guides/beginners-primer.html` (doesn't exist).
- `/home/ivan/Project/the-spell-brigade-wiki/characters/wizard-king.html` line 66 → `mechanics/character-improvements.html` (doesn't exist; **17 character pages reference it**).
- `/home/ivan/Project/the-spell-brigade-wiki/characters/wizard-king.html` line 212 → `guides/best-spells-per-hero.html` (doesn't exist).
- `/home/ivan/Project/the-spell-brigade-wiki/spells/index.html` lines 117, 141, last "see-also" → `element-matrix.html` resolved relative to `/spells/` (file lives in `/mechanics/`). Should be `../mechanics/element-matrix.html`.
- `/home/ivan/Project/the-spell-brigade-wiki/spells/rifle.html` → `../artifacts/by-effect.html#critical` (file `artifacts/by-effect.html` doesn't exist).
- `/home/ivan/Project/the-spell-brigade-wiki/guides/artifact-priorities.html` tier chips → `../artifacts/index.html#13` (anchor is `#artifact-13`). All 20 tier chips and all per-archetype pick-order links land at the page top instead of the right card.
- `/home/ivan/Project/the-spell-brigade-wiki/data/search-index.json` lines for all 20 artifacts → slug URLs that do not match the numeric `artifact-N.html` filenames.

### Visual hierarchy
- Tier rows are nicely colored and immediately scannable.
- Stat-block `<dl class="meta-dl">` with bold values reads well.
- But the boss strategy page mixes prose and callouts in a way where the most actionable item ("pre-bait the kill") is buried in paragraph #2. Consider a "TL;DR" callout at the top of every strategy section.

---

## Prioritized improvements

### CRITICAL (would block a user)
1. **Fix the search-index artifact URLs.** Rewrite `data/search-index.json` so artifact URLs match the on-disk filenames (`artifact-13.html`), or rename the artifact files to the slug format. Right now the search bar — the obvious mid-run tool — never lands on an artifact page.
2. **Fix the home-page Damage Guide button.** It links to `mechanics/damage-calculation.html` which is a 404. Rename the file or fix the link in all 63 places. This is the wiki's self-declared "centerpiece reference" and the home page can't reach it.
3. **Remove or build the 7 phantom guides** advertised in `index.html` table-of-contents. Currently the home page promises a beginner primer, three build guides, a co-op guide, a per-hero spell guide, and a boss kill order — none exist. Either build stubs or delete the links.

### HIGH (friction)
4. Fix the artifact anchor mismatch (`#artifact-13` vs `#13`) so the Artifact Priorities tier chips actually scroll to cards.
5. Add Bosses (and Waves, Challenges) to the desktop top nav.
6. Pick "Heroes" or "Characters" and use it consistently everywhere.
7. On every artifact page, move the "When to pick" bullets above the Parameters table, and collapse the RVA/dump-line metadata behind `<details>`.
8. On every boss page, link every italicized spell/artifact name.
9. Repair the sidebar "Artifact priority guide" link in all 20 artifact pages (`artifact-priority.html` → `artifact-priorities.html`).
10. Build (or stub) `mechanics/character-improvements.html` referenced by all 15 character pages.

### NICE (polish)
11. Add a per-hero "Recommended artifacts" panel cross-linking to the priorities page archetype.
12. Add a TL;DR callout to each boss page's strategy section (3 bullets: kite/burst/avoid).
13. Add a Glossary page (or `<abbr>` first-use) for terms like DynamicStatModifier, ElementStrengthMultiplier, BellZoneGivesArmor.
14. Add a "card view" / collapsing toggle for the 5-column artifact comparison table on mobile.
15. Link boss pages directly to their specific world subpage rather than the generic worlds hub.
16. Surface confidence pills (guess / inferred / canon) earlier in artifact effect descriptions, not only inside parameter tables.

---

## What works well

- **Damage Optimization + Artifact Priorities + Spell Tier List + Element Pairing** is a genuinely strong opinionated guide quartet. Authorial voice is confident and uses real numbers.
- Toad's strategy page is what every boss page should aspire to — phases, tells, do/don't callouts, pro tips.
- Stat tables use semantic `<dl>` / `<table>` markup with `is-modified` highlighting (Wizard King's +10 CritChance pops correctly).
- Methodology callout on the home page is admirably honest about IL2CPP extraction and the unofficial status — sets correct expectations.
- Breadcrumbs everywhere, skip-link, ARIA labels — accessibility baseline is solid.
- Text-only, no CDN, no images, no trackers — fast load, friendly for the "paused mid-run on Steam Deck" use case.
- Confidence pills on inferred parameter values are an honest touch that data-extraction wikis often skip.
- Sidebar navigation within sections (artifacts, characters, bosses) gives one-click traversal between siblings — well-suited to "browse the list, find the one I saw in-game" flow.
