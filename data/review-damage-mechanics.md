# Damage Guide & Mechanics Accuracy Review

## Verdict: PASS-WITH-MINOR-FIXES

Two factual errors in the log-curve table on the damage-optimization guide and one
master-formula discrepancy (extra term not present in damage-system.html) need
fixing. Everything else — constants, base damages, worked-example arithmetic,
crit / weakspot / armor / friendly-fire semantics, stat IDs, element list, and
tier-list raw DPS — is consistent with both `mechanics.json` and the IL2CPP
dump. Confidence labels and "inferred" callouts are used appropriately
throughout.

---

## Master formula

- **Rendered formula correctness:** The 11-line pipeline in
  `damage-optimization.html#formula` matches `mechanics.json
  > damage_formula_end_to_end` step-for-step.
- **Term order:** Consistent with `damage-system.html` and `critical-hits.html`
  (base × Σ%Damage → spell-specific → weakspot × 1.5 → crit → element
  strength → element weakness → debuff product → flat armor → friendly-fire).
- **Confidence acknowledgments:** "Empirical caveat" callout at the top
  flags the IL2CPP limitation and "treat as 95% correct." Per-term `dl`
  flags `spell_specific_mult`, `damage_multiplier_providers`, and
  `target.Armor` as `inferred`. Good.
- **Inconsistency with damage-system.html (MINOR):** the
  damage-optimization master formula adds a `× (1 + Σ PercentAddLog_damage%)^0.5714`
  line that does not appear in the canonical damage-system master formula.
  The body text immediately below admits "the Damage stat itself is not
  logarithmic" — so this line is at best a label for Range/Size indirectly
  helping damage, and at worst misleading. The damage-system.html formula
  (which omits the line) is the canonical one. Recommend either removing
  the line from the damage-optimization formula or renaming the variable
  to `PercentAddLog_size_range%` and re-labelling its comment.

---

## Worked example arithmetic

All four worked examples re-compute exactly as stated:

### Example A — Arrow + Fire + Damage-per-Armor
- Σ Damage = 87 + (80 × 0.25 = 20) = 107%; 165 × 2.07 = **341.55 ≈ 341.6** ✓
- × 1.15 element = **392.78 ≈ 393** ✓
- Cadence 0.404 × 1.12 = **0.452** ✓; raw DPS 393 × 0.452 = **177.6 ≈ 178** ✓
- New cadence 0.404 × 1.27 = **0.513** ✓; new DPS 393 × 0.513 = **201.6 ≈ 202** ✓
- Reported "+13.5%" pickup → actually (202−178)/178 = **13.48%** ✓

### Example B — Slash crit build
- 296 × 1.60 = **473.6** ✓
- E[hit] = 473.6 × (0.70 + 0.30 × 3.50) = 473.6 × 1.75 = **828.8** ✓
- DPS = 828.8 × 0.75 = **621.6** ✓
- Sensitivity table all consistent: each +10% CritChance at CD=250 adds
  exactly +0.25 to E[mult] = +25% expected damage. ✓

### Example C — Beam vs Squid TTK
- 104 × 1.80 = **187.2** ✓
- E[tick] = 187.2 × (0.60 + 0.40 × 3.0) = 187.2 × 1.80 = **336.96 ≈ 337.0** ✓
- single_DPS = 337.0 × 1.9 = **640.3** ✓; dual_DPS = **1280.6** ✓
- TTK = 185000 / 1280.6 = **144.46 ≈ 144.5 s** ✓
- (Note: 185 k HP for Squid is not in any reviewed data file, so this is
  the only number I could not double-check against source.)

### Example D — Shotgun ExtraProjectile vs +15% Damage
- A: 4 × 300 = 1200 (+33.3%) ✓
- B: 3 × 300 × 1.15 = 1035 (+15%) ✓
- B′: 3 × 300 × 1.75 = 1575; B″: 3 × 300 × 1.60 = 1440; Δ = 135 = +9.375%
  ≈ "+9.4%" ✓

### Late-game scaling (mini example)
- 200 × 1.5 = 300; 200 × 1.5 × 1.2 = 360 (+60, +20%) ✓
- 200 × 3.5 = 700; 200 × 3.5 × 1.2 = 840 (+140, +20%) ✓

---

## Logarithmic curve table — TWO ERRORS

`damage-optimization.html#log-curve` table claims the following but the
actual `(1+Σ)^0.5714286` evaluations differ on three rows:

| Σ% | (1+Σ) | Guide says | Correct | Δ |
|---|---|---|---|---|
| +25% | 1.25 | 1.135× | 1.1360× | OK |
| +50% | 1.50 | 1.262× | 1.2607× | OK |
| +100% | 2.00 | 1.487× | 1.4860× | OK |
| **+200%** | **3.00** | **1.937×** | **1.8734×** | **WRONG** (felt% 121 → should be 87) |
| +300% | 4.00 | 2.213× | 2.2082× | OK (rounding) |
| **+500%** | **6.00** | **2.916×** | **2.7839×** | **WRONG** (felt% 192 → should be 178) |
| **+1000%** | **11.00** | **4.341×** | **3.9362×** | **WRONG** (felt% 334 → should be 294) |

Three rows (200, 500, 1000) appear to have been computed with an exponent
closer to 0.60 instead of 0.5714. The "felt bonus" column is also wrong on
those rows. The "Practical reading" callout's "never out-grow your starting
Size by more than about 4–5×" claim still holds with corrected numbers
(at +1000% you actually get ≈3.94×, so the qualitative point is fine), but
the table itself misleads any reader doing math from it.

---

## Stat hierarchy claims — verified

- "Damage is the #1 priority" — defensible. Damage is the only term scaling
  base spell damage as a `1 + Σ%`. Caveats about diminishing returns
  (greedy-stacking trap) are correctly stated.
- "FireRate is a true second multiplier" — correct; FireRate is its own
  separate PercentAdd bracket, so D×FR multiplies. ✓
- "Crit pair multiplicative; pick CritChance when D/C > 1.75" — partial
  derivative algebra reproduces exactly: d(1+CC×CD/10000) = D/10000 and
  C/10000, so 4D > 7C ⇔ D/C > 1.75. ✓
- "ElementStrengthMultiplier is one of two terms that bypass the additive
  bracket" — matches `ElementEffectivenessCalculator` semantics
  (mechanics.json `element_effectiveness`). ✓
- "Armor is flat-subtracted" — matches mechanics.json `armor_system`
  (inferred but properly labelled). ✓

---

## Build archetype synergies — verified against artifacts.json

| Archetype | Cited artifact | Check |
|---|---|---|
| Crit Stacker | #17 HealOnCrit (0.3 HP) | ✓ params [0.3] |
| Crit Stacker | #14 CritDmg/Revive +35 | ✓ params [35] |
| Crit Stacker | #7 CritDmg StandingStill +100 | ✓ params [100] |
| Crit Stacker | #20 CritDmg/Common +1 | ✓ params [1] |
| Element Specialist | #15 ElemDmg/Infusion +10 | ✓ params [10] |
| Glass Cannon | #3 LessHP→XP up to +40 | ✓ params [40] |
| Glass Cannon | #1 LessHP→MS up to +21 | ✓ params [21] |
| Tank-DPS | #13 +0.25 Dmg/Armor (param[1]=0.25) | ✓ params [1, 0.25] |
| Tank-DPS | #2 AddArmorEqualToPartyLevel | ✓ class confirmed |
| Tank-DPS | #12 Armor/Objective +10 | ✓ params [10] |
| Swarm Clearer | #5 Dmg/NearbyTeammate +20 | ✓ params [20] |

Tank-DPS arithmetic ("4 players × level 30 = 120 Armor → +30% Damage") relies
on the inference that AddArmorEqualToPartyLevel uses `Parameters[0] = 1` per
party-member level. The class trigger (`returns current sum of party member
levels × Parameters[0]`) in mechanics.json supports this, but the JSON shows
`parameters_raw: []` for artifact #2, so the explicit "1" coefficient is not
recoverable from the asset file. **MINOR**: add an "inferred" tag near that
calculation.

---

## Spell-tier raw DPS table — verified

All 21 Damage × FireRate × Projectiles products are correct to one decimal
place. Spot checks: Smg 686.76 ≈ 686.8; Shotgun 436.5; Slash 222.0; Beam
197.6; Orb 195.55 ≈ 195.6; Bell 35.5; Fence 3.76. The "Smg = 0.95m
projectiles / 0.92s lifetime" caveat matches spells.json (Size 0.95,
LifeTime 0.9215).

The methodology disclaimer ("table is misleading on purpose") is appropriate;
the qualitative tier placements (Bell S despite low raw DPS, Smg A despite
high raw DPS, EnergyZone C as a low-base damage zone) all line up with the
formula reasoning. No contradictions found.

---

## Mechanics pages issues

- **stats.html** — all 36 StatType entries present with correct IDs, calc types,
  and display types per dump line 314327–314367. Gaps (21, 28, 29, 31, 32)
  documented. ✓
- **damage-system.html** — pipeline matches mechanics.json verbatim;
  confidence tags ("high", "inferred") present per step. Master formula
  omits the suspect PercentAddLog_damage line, so it is the canonical one. ✓
- **elements.html** — 21 ElementType values, IceEffect chill clamped
  `MinChillFactor = 0.2`, `MaxChillFactor = 0.72` correctly stated. ✓
- **critical-hits.html** — snapshot semantics (cast-time), GetRandomFloat(0,100),
  `× (1 + CriticalDamage/100)`, weakspot × 1.5, OneShotDamage 999999 all
  present and match dump constants at lines 274232, 274233, 293506,
  294027, 310960, 314230. ✓
- **armor-dodge.html** — flat-subtract armor model with `max(0, raw − Armor)`,
  `HasDodged() = GetRandomFloat(0,100) < Dodge`, FriendlyFireMultiplier 0.25.
  All explicitly labelled `inferred` where appropriate. ✓
- **stat-modifiers.html** — caption says "16 ArtifactStatModifier_* and 6
  SpellVariantStatModifier_*", matching `grep -oE` on dump (16 and 6 distinct
  class names). Note the task brief mentions "14 ArtifactStatModifier_*" but
  the page correctly says 16. ✓
- **rarity.html** — 4 tiers (Common 0, Rare 1, Epic 2, Legendary 3),
  ImprovementValueContainer documented. ✓

---

## Cross-page consistency

- Master formula on `damage-system.html` ≠ master formula on
  `damage-optimization.html` (the latter has an extra PercentAddLog_damage
  line). Stats.html doesn't render a master formula itself, only individual
  stat entries — those entries are consistent with both. **MINOR**.
- Crit mechanics (snapshot at cast, GetRandomFloat(0,100), multiplier
  `1 + CriticalDamage/100`, weakspot × 1.5 stacking multiplicatively with
  crit, default 10/150 → 2.5× multiplier) are stated identically across
  damage-system.html, critical-hits.html, stats.html, and
  damage-optimization.html. ✓
- Friendly-fire 0.25× appears identically in damage-system.html,
  armor-dodge.html, and damage-optimization.html. ✓

---

## Recommended changes

1. **MINOR (data error):** `guides/damage-optimization.html#log-curve` — fix
   the three wrong rows in the "Nominal Σ vs. actual scalar" table:
   - 200% (1.50) → row should be **1.873×** / **+87.3%** (not 1.937× / +121%)
   - 500% (6.00) → row should be **2.784×** / **+178%** (not 2.916× / +192%)
   - 1000% (11.00) → row should be **3.936×** / **+294%** (not 4.341× / +334%)
2. **MINOR (consistency):** the master formula in
   `damage-optimization.html#formula` contains an extra line for
   `(1 + Σ PercentAddLog_damage%)^0.5714` that does not appear in the
   canonical `damage-system.html` master formula and is contradicted by the
   guide's own term-by-term commentary ("the Damage stat itself is not
   logarithmic"). Remove the line, or rename the variable to
   `PercentAddLog_size_range%` and re-comment.
3. **MINOR (citation):** in the Tank-DPS archetype, the calculation "4 players
   × level 30 = 120 Armor → +30% Damage" depends on `AddArmorEqualToPartyLevel`'s
   implicit `Parameters[0] = 1`. The artifacts.json entry for #2 has
   `parameters_raw: []`, so add a parenthetical "(inferred coefficient)" or
   move the calculation behind a `callout` note.
4. **NICE-TO-HAVE:** the Example C Squid HP figure (185 000) is not in any
   reviewed JSON; consider citing the source (bosses.json or enemies.json)
   or labelling it "approximate per current testing".
