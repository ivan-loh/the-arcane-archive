# Data Accuracy Review

Reviewer: data-accuracy spot-check pass
Sample method: 5 spells (Arrow, Beam, Plant, Meteor, Shotgun), 5 artifacts (3, 7, 11, 15, 19), 5 characters (BellMage, Hatty, Ludwig, StarMage, VampireMage). Each spot-checked against the authoritative `.asset` YAML in `/mnt/data/tsb2/ExportedProject/Assets/Resources/` and the IL2CPP enum dump at `/home/ivan/tools/Il2CppDumper/out_tsb/dump.cs`.

## Summary
- Total spot-checks performed: 15 (5 spell pages, 5 artifact pages, 5 character pages)
- Issues found: 4 (critical: 1, minor: 3)
- Confidence overall: **HIGH** for spell and artifact data; **MEDIUM** for character stat-modifier presentation (one math/semantic bug; everything else accurate)

---

## Spell findings

Mapping cross-checked from `dump.cs`:

```
StatType: 0=Damage 1=Range 2=FireRate 3=Speed 4=LifeTime 5=DamageTickRate
          6=Size 7=MovementSpeed 8=MaxHealth ... 20=Projectiles 26=HitboxSizeMultiplier
          27=ElementWeaknessMultiplier 30=ElementStrengthMultiplier
SpellType: 0=Orb 1=Boomerang 2=EnergyZone 3=Laser 4=Proximity 5=Shotgun 6=Rifle
           7=Smg 8=Trail 9=BombLauncher 10=FallingStar 11=Mine 12=Fence
           13=Beam 14=Arrow 15=Plant 16=Summon 17=Slash 18=Meteor 19=Book 20=Bell
```

### Arrow (`spells/arrow.html`)
- SpellType 14 → page eyebrow `SpellType 14` — verified
- Base Stats: Damage 165, FireRate 0.4036364 (displayed 0.403636), Speed 6.2, Range 8 — all verified against `ArrowConfiguration.asset`
- StartingModifiers: FireRate +12% — verified (`StatType: 2, Value: 12`)
- Variant `Arrow_ExplodeAtEnd` (SpellVariant 13 = ExplodeAtEnd) — verified, RepeatAmount 0 → no "stackable" badge (correct)
- Variant `Arrow_HitExtraEnemy` (SpellVariant 22) RepeatAmount 2 → HTML "stackable ×2" — verified
- Infusion `ArrowFire` (Element 1) — verified
- Improvements: Damage common=10 rare=15 epic=25 legendary=35 and FireRate same — verified against `ArrowDamage.asset` / `ArrowFireRate.asset`

### Beam (`spells/beam.html`)
- SpellType 13 — verified
- Base Stats: Damage 104, Range 7.5, FireRate 1.9, Projectiles 1 — verified
- StartingModifiers: Damage +8%, FireRate +4% — verified

### Plant (`spells/plant.html`)
- SpellType 15 — verified
- Base Stats: Damage 118.5, FireRate 0.266667, Size 3, DamageTickRate 1.35, LifeTime 5 — verified
- StartingModifiers: Size +25%, DamageTickRate +12% — verified

### Meteor (`spells/meteor.html`)
- SpellType 18 — verified
- Base Stats: Range 15, Damage 61, FireRate 0.5335, Projectiles 4 — verified
- StartingModifiers: FireRate +12% — verified
- Variant `Meteor_ExtraProjectile` (SpellVariant 4) RepeatAmount 5, StatModifier StatType=20 (Projectiles) Value=1 — synergy callout says "Up to 5 extra meteors per cast" — verified

### Shotgun (`spells/shotgun.html`)
- SpellType 5 — verified
- Base Stats: Damage 300, FireRate 0.485, Speed 11.5, LifeTime 0.67, Projectiles 3, Size 0.95 — verified
- StartingModifiers: Size +25%, FireRate +12% — verified
- ShotgunDamage improvement: 10/15/25/35 — verified

**Spell verdict:** all five sampled spell pages match the source YAML exactly. No critical or minor issues found in spells.

---

## Artifact findings

ArtifactType enum cross-checked from `dump.cs` (id 3=TheLessHPTheMoreXPGain, 7=IncreaseCritDamageWhileStandingStill, 11=IncreaseDamageForEveryRevive, 15=IncreaseElementalDamageForEveryInfusion, 19=HealOnXPPickup).

### Artifact 3 (`artifacts/artifact-3.html`)
- ArtifactType 3 = TheLessHPTheMoreXPGain — verified
- Parameters[0] = 40 — verified
- AddsModifier true, SpawnRate 50, HideForSinglePlayer false — verified
- Confidence label `inferred` for the parameter — honest (no explicit IL2CPP class found; "BonusExpWhenBelowHealthThreshold" is the impl class name, but the exact meaning of `40` is reasonably called inferred)

### Artifact 7 (`artifacts/artifact-7.html`)
- ArtifactType 7 = IncreaseCritDamageWhileStandingStill — verified
- Parameters[0] = 100 — verified
- AddsModifier true, SpawnRate 50 — verified
- Confidence `high` — reasonable given matching class name

### Artifact 11 (`artifacts/artifact-11.html`)
- ArtifactType 11 = IncreaseDamageForEveryRevive — verified
- Parameters[0] = 10 — verified
- AddsModifier true, SpawnRate 100 (decays over time true) — verified, page explicitly notes "(decays over time)"
- HideForSinglePlayer true — page correctly shows "hidden from solo runs" callout

### Artifact 15 (`artifacts/artifact-15.html`)
- ArtifactType 15 = IncreaseElementalDamageForEveryInfusion — verified
- Parameters[0] = 10 — verified
- AddsModifier true, SpawnRate 50 — verified
- Confidence `inferred` for parameter meaning — honest

### Artifact 19 (`artifacts/artifact-19.html`)
- ArtifactType 19 = HealOnXPPickup — verified
- Parameters[0] = 15, Parameters[1] = 1 — verified
- AddsModifier **false** — page correctly says "AddsModifier in the asset YAML is false" (this is the one in the sample where AddsModifier is false; matches YAML)
- SpawnRate 50 — verified
- Two-parameter decoding (chanceToHeal 15%, healAmount 1) marked confidence `high` — reasonable given the class fields cited

**Artifact verdict:** All five sampled artifact pages match source. ID mapping, parameters, SpawnRate, AddsModifier, HideForSinglePlayer all correct. Confidence labels are calibrated honestly (inferred vs. high used appropriately).

---

## Character findings

Shared base from `characterstatsdata/CharacterStatsData.asset`: MovementSpeed 3.6, MaxHealth 600, Luck 0, PickupRadius 4, CritChance 10, CritDamage 150, Armor 0, Dodge 0, HealthRegen 0, Rerolls 0, Bans 0, Pins 0, Revives 2, HealthPctOnRevive 0.5, ReviveZoneSize 6.5. All five sampled character pages render these base values correctly.

UniqueModifier hex bytes decoded as little-endian uint32 array against the `UniqueModifier` enum (0=IgnoresNegativeEffects, 7=LifeStealOnSlashSpell, 8=CanReviveWhenDown, 9=ReturnDamageWhenHit, 10=ExplodeOnDeath, 11=LifeStealOnSignatureSpell).

### BellMage (`characters/bell-mage.html`)
- Id 14, InitialSpell 20 (Bell), InitialPrestige 8 (Trail) — all verified
- Modifiers: [] — page shows no stat changes — verified
- UniqueModifiers `090000000a000000` → [9, 10] → ReturnDamageWhenHit + ExplodeOnDeath — both rendered correctly with explanations
- Skins: 7 in asset, page shows "Skins available: 7" — verified

### Hatty (`characters/hatty.html`)
- Id 6, InitialSpell 7 (Smg), InitialPrestige 19 (Book) — verified
- Modifiers: Damage +6, MaxHealth -300 (→ HP 300), ElementWeaknessMultiplier +15 — verified
- UniqueModifiers empty — page shows none — verified
- Skins: 8 — verified

### Ludwig (`characters/ludwig.html`)
- Id 4, InitialSpell 3 (Laser), InitialPrestige 17 (Slash) — verified
- Modifiers: HitboxSizeMultiplier +25, Armor +12, MovementSpeed -10 — values correct
- UniqueModifiers `00000000` → [0] → IgnoresNegativeEffects — verified
- Skins: 8 — verified
- **CRITICAL — see "Issue C1" below**: MovementSpeed -10 is rendered as a *flat* subtraction (3.6 + (-10) = **-6.4**). Negative movement speed is nonsensical; the StatType=7 modifier value 10 is almost certainly a **percent**, so the after-modifier value should be 3.6 × (1 - 0.10) = **3.24** (or 3.6 × 0.9, depending on the in-game stacking rule).

### StarMage (`characters/star-mage.html`)
- Id 8, InitialSpell 10 (FallingStar), InitialPrestige 7 (Smg) — verified
- Modifiers: ElementStrengthMultiplier +15 (StatType 30) — verified; rendered as 0% → 15%
- UniqueModifiers empty — verified
- Skins: 8 — verified

### VampireMage (`characters/vampire-mage.html`)
- Id 13, InitialSpell 17 (Slash), InitialPrestige 13 (Beam) — verified
- Modifiers: [] — verified
- UniqueModifiers `0b00000008000000` → [11, 8] → LifeStealOnSignatureSpell + CanReviveWhenDown — both rendered with explanations — verified
- Skins: 8 — verified

---

## Issues

### C1 (CRITICAL) — Character stat modifiers are summed as flat values when several stats are clearly percent
File: `characters/ludwig.html` (and the underlying templater for every character page)

Ludwig's `StatType: 7, Value: -10` modifier is rendered as:

```
Movement Speed   3.6   -6.4 (-10)
```

A negative movement speed is impossible in-game. StatType 7 (MovementSpeed) modifier values in this game are percentages. Expected display:

```
Movement Speed   3.6   3.24 (-10%)
```

The same flat-vs-percent ambiguity affects:
- Hatty `Damage +6` rendered "Damage 0 → 6 (+6)" — Damage is a spell stat; +6 is percent and there is no character-level "Damage" base (rendering "0 → 6" is misleading even if the bare number 6 is correct).
- Hatty `ElementWeaknessMultiplier +15` rendered as "0% → 15% (+15)" — this one is fine because the renderer treats StatType 27 as percent.
- Ludwig `HitboxSizeMultiplier +25` rendered "0% → 25% (+25)" — fine for the same reason.
- StarMage `ElementStrengthMultiplier +15` rendered "0% → 15% (+15)" — fine.
- Ludwig `Armor +12` rendered "0 → 12 (+12)" — fine; Armor is a flat int in the source struct.
- Hatty `MaxHealth -300` rendered "600 → 300 (-300)" — likely fine; MaxHealth modifiers in similar games are usually flat, and Hatty being a 300 HP glass cannon is canonical/intended.

The renderer apparently picks flat or percent based on a per-stat policy, but for `StatType=7` (MovementSpeed) it is using flat addition. Recommended fix: classify MovementSpeed and a few other "small float base" stats (PickupRadius, ReviveZoneSize, possibly FireRate-on-character) as percentage modifiers.

### M1 (MINOR) — Hatty "Damage 0 → 6" is semantically misleading
Even if MovementSpeed is the only one with truly wrong math, presenting spell-stat `Damage` as a character row with base 0 is confusing. Consider either (a) hiding spell-only StatTypes from the character stat table and listing them in a separate "Spell-damage bonuses" block, or (b) labeling them as percent (e.g., "+6%").

### M2 (MINOR) — Inconsistent decimal precision
`spells/arrow.html` shows `FireRate 0.403636` (6 sig figs), but the YAML value is `0.4036364` (7 sig figs). The `aria-label` correctly contains `0.4036364`. Display truncation is intentional but worth documenting; not wrong, just inconsistent across spells (Meteor `0.5335` is shown unrounded). Pure cosmetic.

### M3 (MINOR) — `aria-label` for stat-bar uses raw value but visible cell rounds
Same as M2; benign but flags as a minor inconsistency for an a11y reader vs. visual reader.

---

## Recommended fixes (prioritized)

1. **CRITICAL — fix MovementSpeed modifier semantics.** The character-stats renderer should treat `StatType: 7` (MovementSpeed) modifier values as percent. Audit other small-base float stats (PickupRadius=11, ReviveZoneSize=36) for the same bug. Verify by re-rendering Ludwig: post-fix MovementSpeed should read `3.24 (-10%)`, not `-6.4`.
2. **MINOR — disambiguate flat vs. percent labeling** for stats that look like character stats but actually scale spell output (Damage=0, FireRate=2 on characters who get such modifiers). Add `%` suffix and avoid the misleading "0 →" prefix when the base for that StatType doesn't exist on the character.
3. **MINOR — unify decimal precision** across spell stat tables (or document the rounding rule in `mechanics/stats.html`).

---

## Sample commands used

```
# Spell base configurations
cat /mnt/data/tsb2/ExportedProject/Assets/Resources/spellconfigurations/ArrowConfiguration.asset
grep "SpellType\|StartingModifiers\|StatType\|Stat:\|Value:" .../BeamConfiguration.asset

# Variants/improvements
cat .../storeitems/spells/arrow/variants/Arrow_HitExtraEnemy.asset
cat .../storeitems/spells/arrow/improvements/ArrowDamage.asset
cat .../storeitems/spells/meteor/variants/Meteor_ExtraProjectile.asset

# Artifacts
for n in 3 7 11 15 19; do cat .../storeitems/artifacts/Artifact_$n.asset; done

# Characters
cat .../characterstatsdata/CharacterStatsData.asset
for c in BellMage Hatty Ludwig StarMage VampireMage; do cat .../characterresources/$c.asset; done

# Enum cross-checks
grep -A40 '^public enum StatType '   /home/ivan/tools/Il2CppDumper/out_tsb/dump.cs
grep -A40 '^public enum SpellType '  /home/ivan/tools/Il2CppDumper/out_tsb/dump.cs
grep -A40 '^public enum SpellVariant ' /home/ivan/tools/Il2CppDumper/out_tsb/dump.cs
grep -A40 '^public enum ArtifactType ' /home/ivan/tools/Il2CppDumper/out_tsb/dump.cs
grep -A20 '^public enum UniqueModifier ' /home/ivan/tools/Il2CppDumper/out_tsb/dump.cs

# Rendered HTML extraction
grep -E "page-hero__eyebrow|stat-bar|meta-list|ArtifactType|Modifier|Skin" \
     /home/ivan/Project/the-spell-brigade-wiki/{spells,artifacts,characters}/*.html
```
