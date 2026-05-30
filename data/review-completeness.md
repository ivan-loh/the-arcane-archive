# Content Completeness Review

Auditor: content-completeness reviewer.
Scope: `/home/ivan/Project/the-spell-brigade-wiki/` (138 HTML files).
Date: 2026-05-30.

## Coverage tally

| Section | Expected (data) | Built | Status | Notes |
|---|---:|---:|---|---|
| Spells | 21 | 21 + `index.html` + `element-matrix.html` (23) | OK | All `spells/*.html` match `spells.json` keys. |
| Artifacts | 20 | 20 + `index.html` (21) | OK | Numeric scheme `artifact-1.html` ... `artifact-20.html`. |
| Characters | 16 | 16 + `index.html` (17) | WARN | `characters/test-character.html` is a real page for an internal `TestCharacter` entry; search index correctly lists only 15 production heroes. |
| Enemies (regular) | 29 | aggregated on `enemies/regular.html` (sortable table) | OK content / BROKEN links | All 29 regulars mentioned, but ~200 wave/world links target non-existent `enemies/regular/<slug>.html`. |
| Elites | 3 (+ events) | `enemies/elites.html`, `enemies/events.html` | OK | All 3 elites + 4 events present. |
| Bosses | 3 | 3 (`squid`, `hydra`, `toad`) + `index.html` | OK | |
| Worlds | 4 | 4 + `index.html` | OK | |
| Waves | 32 raw IDs (20 slots + 12 world overrides) | 20 slot pages + `index.html` | OK | Overrides referenced inside their slot page (e.g., `wave_4_pyrestorm_pit` shows up 5x in `waves/wave-04.html`). All 32 IDs findable. |
| Challenges | 147 across 16 cats | 16 category pages + `index.html` | OK | Counted `<tr id>` rows: 3+3+16+7+6+4+5+15+4+15+3+31+14+3+4+14 = **147**. Matches spec (147; site-structure.md mentions "148" loosely). |
| Stat types | 36 | all 36 named in `mechanics/stats.html` | OK | |
| Element types | 21 | all 21 named in `mechanics/elements.html` | OK | |
| Search index entries | 196 | 196 entries | OK | Breakdown: spell 21, artifact 20, hero 15 (test omitted, good), boss 3, elite 3, enemy 29, event 4, guide 16, hub 10, mechanic 17, page 6, wave 32, world 4, challenge-category 16. |

## Orphan pages

- `404.html` - linked from: only `styleguide.html`. Expected (static-host fallback).
- No other orphans (when absolute paths `/section/...` are honored).
- `mechanics/damage-system.html`, `mechanics/critical-hits.html`, `mechanics/armor-dodge.html`, `mechanics/rarity.html`, `mechanics/stat-modifiers.html` are **only reachable via absolute `/mechanics/...` hrefs** from `mechanics/index.html`. When served from a non-root location (file://, sub-path), they become de-facto orphans. (Path-correctness is the technical reviewer's call; flagged here because the centerpiece "damage system" page is the one most affected.)

## Dead-end pages

- `about.html` - no internal links in `<main>` (header/footer nav only). Acceptable for an about page but a "Back to Home" CTA would improve UX.
- No other dead-ends.

## Cross-link sample (20 spot-checks)

1. `spells/arrow.html` -> `characters/index.html` (3x) - EXISTS - but does NOT link to specific characters that have Arrow as starter spell. WEAK.
2. `spells/arrow.html` -> `artifacts/index.html` (4x) - EXISTS, no per-artifact anchors. WEAK.
3. `artifacts/artifact-13.html` -> 5 spell pages - EXISTS.
4. `artifacts/artifact-13.html` -> `mechanics/*` (9 refs) - EXISTS.
5. `characters/bell-mage.html` -> `spells/bell.html` (3 refs) - EXISTS.
6. `characters/moon-mage.html` -> 11 spell links - EXISTS.
7. `characters/wizard-king.html` -> 11 spell links - EXISTS.
8. `spells/bell.html` -> `characters/bell-mage.html` - **MISSING** (only links to `characters/index.html`). Reciprocal link broken on every spell page (none link to specific starter heroes).
9. `worlds/verdant-meadows.html` -> 29 wave refs - EXISTS.
10. `worlds/pyrestorm-pit.html` -> 10 enemy refs - EXISTS in prose but **12 link to non-existent `enemies/regular/<slug>.html`**.
11. `bosses/hydra.html` -> waves - 1 ref only. WEAK; bosses should reference all wave slots they appear in.
12. `bosses/squid.html` -> `spells/void-lance.html` - **BROKEN** (invented spell name from spec example, not a real game spell).
13. `bosses/squid.html` -> `spells/glacial-shard.html` - **BROKEN** (same issue).
14. `bosses/toad.html` -> `spells/venom-mist.html` - **BROKEN** (invented).
15. `bosses/toad.html` -> `guides/beginners-primer.html` - **BROKEN** (file is `guides/index.html`; no primer exists).
16. `enemies/elites.html` -> `spells/glacial-shard.html` - **BROKEN**.
17. `challenges/spell.html` -> 18 spell-related links - EXISTS.
18. `characters/index.html` -> `guides/coop-roles.html` - **BROKEN**.
19. `characters/<all>` -> `mechanics/character-improvements.html` - **BROKEN on all 16 character pages** (file not built).
20. `artifacts/<all>` -> `guides/artifact-priority.html` - **BROKEN on all 20 artifact pages** (correct name is `artifact-priorities.html`, plural).

## Tier-list completeness

- `guides/spell-tier-list.html` links to all **21/21** spell pages. None missed.

## Site-structure deviations

**Missing pages defined in `data/site-structure.md`:**

- `/search.html` - missing entirely (no global search page).
- `/changelog.html` - missing.
- `/characters/skins.html` - missing (no skins aggregate).
- `/artifacts/by-effect.html` - missing (pivot index).
- `/waves/comparison.html` - missing (sortable wave comparison).
- `/enemies/bosses/index.html` and per-enemy `regular/` folder - missing; replaced by flat `enemies/regular.html`, `enemies/elites.html`. Bosses live at top-level `/bosses/` instead of `/enemies/bosses/`.
- `/mechanics/damage-calculation.html` - renamed to `damage-system.html` (functional equivalent, but broken inbound links exist).
- `/mechanics/stat-calculation.html` - missing (only `stat-modifiers.html` exists).
- `/mechanics/rarities.html` - renamed to `rarity.html` (singular).
- `/mechanics/character-improvements.html` - missing; referenced from every character page.
- `/mechanics/titles.html` - missing.
- `/mechanics/team-awards.html` - missing.
- `/guides/new-player-primer.html` - missing.
- `/guides/coop-roles.html` - missing.
- `/guides/build-fire-burst.html`, `build-ice-control.html`, `build-lightning-chain.html`, `build-arcane-summon.html`, `build-nature-dot.html`, `build-shadow-curse.html` - all 6 build guides missing.
- `/guides/best-spells-per-hero.html` - missing (referenced by every hero page).
- `/guides/artifact-priority.html` - missing; built as `artifact-priorities.html` (plural).
- `/guides/wave-survival-15-plus.html` - missing.
- `/guides/boss-kill-order.html` - missing.
- `/guides/challenge-completion-route.html` - missing.

**Pages built that are not in spec (acceptable / improvements):**

- `styleguide.html` (dev aid; OK to keep).
- `mechanics/element-matrix.html` (spec'd) and `spells/element-matrix.html` (duplicate? second copy in spells/).
- `guides/element-pairing.html`, `guides/damage-optimization.html`, `guides/spell-tier-list.html`, `guides/artifact-priorities.html` - reasonable substitutes for the build-guide series.
- `mechanics/objectives.html`, `mechanics/modifiers.html` - in spec, present.

**URL pattern deviations:**

- Artifacts: spec said `artifact-01-<name>.html`; built `artifact-1.html`...`artifact-20.html` (no zero-pad, no name). Loses the in-game "artifact 13" -> readable name aid but URLs still work.
- Enemy bosses live at `/bosses/<name>.html` (top-level section) rather than spec'd `/enemies/bosses/<name>.html`. Boss section is also missing from top nav (the spec made it part of "Enemies & Bosses").

## Damage guide reference audit

Sampled 10 cross-references emitted by `mechanics/damage-system.html`:

- `../guides/damage-calculation.html` - **BROKEN** (no such guide; self-link mistake).
- `../artifacts/increase-damage-per-armor.html` (3 refs) - **BROKEN** (artifact files are numbered, not slugified by effect).
- `../artifacts/increase-damage-per-nearby-party-member.html` - **BROKEN**.
- `../artifacts/increase-damage-per-revive-performed.html` - **BROKEN**.
- `../artifacts/deal-more-damage-when-standing-still.html` - **BROKEN**.
- `../artifacts/increase-critical-damage-per-revive-performed.html` - **BROKEN**.
- `../artifacts/bell-zone-gives-armor.html` - **BROKEN**.
- `../artifacts/add-armor-equal-to-party-level.html` - **BROKEN**.
- `../artifacts/reduce-damage-taken-when-enemies-in-proximity.html` - **BROKEN**.

Sampled 10 cross-references emitted by `guides/damage-optimization.html` (136 total internal hrefs):

- 135/136 file targets resolve.
- `../enemies/bosses/squid.html` - **BROKEN** (correct path is `../bosses/squid.html`).
- All anchors within in-scope targets resolve.

Anchors in `mechanics/damage-system.html` referenced from elsewhere (`#element-effectiveness`, `#worked-examples`) both exist - OK.

## Issues by severity

### CRITICAL

1. **Damage centerpiece is functionally orphaned in content.** `mechanics/damage-system.html` is referenced only from `mechanics/index.html`. The spec required every spell, artifact, element and stat page to link inward to the damage page. None do.
2. **Every character page links to a non-existent `mechanics/character-improvements.html`** and `guides/best-spells-per-hero.html`. 16 pages x 3 links = 48 dead links in the character section.
3. **Every artifact page links to non-existent `guides/artifact-priority.html`** (correct name is `artifact-priorities.html`) and `mechanics/stat-calculation.html`. 20 pages x 2 = 40 dead links.
4. **All 20 wave pages link to non-existent per-enemy files `enemies/regular/<slug>.html`** (~200 broken hrefs). The aggregate `enemies/regular.html` was built instead; deep-links must point to anchors like `enemies/regular.html#crabling`.
5. **All 4 world pages have the same broken `enemies/regular/<slug>.html` pattern** (~50 broken).
6. **Boss pages reference made-up spell/artifact names** copied from the spec's hypothetical examples: `void-lance`, `glacial-shard`, `venom-mist`, `grim-pact`, `beginners-primer`. These are not in the game and not in this wiki. Same on `enemies/elites.html`.
7. **`mechanics/damage-system.html` references 11 artifact files by descriptive slug** (`increase-damage-per-armor.html`, etc.) that don't exist - the wiki uses numeric artifact files.

### MEDIUM

8. **`spells/<slug>.html` never deep-link to characters or artifacts.** Every spell's "Heroes that start with this spell" / "Artifacts that buff this spell" goes to the section index instead of the specific entries. Reciprocal of the strong character->spell linking.
9. **`bosses/hydra.html`** mentions waves only once. Bosses appear in specific waves and worlds; links should be explicit.
10. **`characters/test-character.html` is publicly browsable** (linked 3x from `characters/index.html`) but excluded from search index and from `characters.json`'s production roster. Either hide the page or document it as a debug entry.
11. **`worlds/index.html` -> `bosses/astral-riftlands.html`** - that file doesn't exist (likely should be `bosses/squid.html` or world page anchor).
12. **`mechanics/index.html` links to `/guides/damage-calculation.html`** (wrong section + wrong filename; should be `../mechanics/damage-system.html`).
13. **Missing global search page** (`/search.html`). The header has no search affordance even though `data/search-index.json` is built and ready (196 entries).
14. **Naming inconsistency in top nav:** spec says "Worlds & Waves" and "Enemies & Bosses". Built nav uses "Worlds", "Enemies" (Waves and Bosses are not in top nav). `Waves` is only in the mobile nav; `Bosses` is reachable only via Enemies hub. Disco-verability hit.

### LOW

15. `about.html` has no in-content links (dead-end).
16. `spells/element-matrix.html` duplicates `mechanics/element-matrix.html` - not in spec; OK if intentional, but should cross-link clearly.
17. Spec mentions "148 challenges across 16 categories"; actual is 147. Probably a spec typo. Reconcile.
18. `mechanics/rarities.html` -> built as `rarity.html` (singular). Update spec or rename file for consistency.
19. `worlds/frozen-ancients.html` calls itself "Crystal Frostlands" in the sidebar but file is `frozen-ancients.html` and `astral-riftlands.html` is labelled "Astral Planes" -- naming drift between display and slug. Pick one and document.
20. Several mechanics pages (`damage-system`, `stat-modifiers`, `rarity`, `armor-dodge`, `critical-hits`) are linked from `mechanics/index.html` only via **absolute paths** (`/mechanics/...`). These work from the doc root but break under any subdir-served deployment; orphaned in practice. Falls partly into technical-reviewer scope but matters here because the centerpiece content is what's affected.

## Recommended fixes (prioritized)

1. **Repair the centerpiece**: from every spell page's `#base`/damage row, every damage-related artifact, every element page entry, and every damage-related stat row in `mechanics/stats.html`, add an outbound link to `mechanics/damage-system.html` (with specific anchors `#master-formula`, `#element-effectiveness`, `#worked-examples`). Then add the inverse - the damage-system page should link out to numeric artifact files, not slugified ones.
2. **Replace `enemies/regular/<slug>.html` patterns** in all wave and world pages with `enemies/regular.html#<slug>` anchors (anchors already exist in that page's table). Mass find/replace.
3. **Create missing referenced pages** OR rewrite the links to existing equivalents:
   - `guides/artifact-priority.html` -> change links to `artifact-priorities.html` (plural).
   - `mechanics/character-improvements.html` -> create stub or link to `mechanics/upgrades.html`.
   - `guides/best-spells-per-hero.html` -> create or remove links.
   - `mechanics/stat-calculation.html` -> link to `mechanics/stat-modifiers.html`.
4. **Purge invented names from boss/elite pages**: `void-lance`, `glacial-shard`, `venom-mist`, `grim-pact`, `beginners-primer`. Replace with real spells/artifacts from `data/spells.json` / `data/artifacts.json`.
5. **Add specific character backlinks on each spell page** (e.g., `spells/bell.html` -> `characters/bell-mage.html`); same for artifact->spell synergy.
6. **Decide whether to keep `characters/test-character.html`.** If keeping, label "Debug only". If not, remove from sitemap and index.
7. **Build `/search.html`** to consume `data/search-index.json`; add a header search input. Otherwise the index is unused.
8. **Add "Bosses" and "Waves" to top nav** (or rename the existing items per spec: "Enemies & Bosses", "Worlds & Waves").
9. **Reconcile site-structure.md with reality**: either build the 12+ missing pages or amend the spec to reflect the current scope (and re-target broken inbound links).
10. **Fix `mechanics/index.html` self-link** to `damage-calculation.html` -> point to the actual `damage-system.html`.
