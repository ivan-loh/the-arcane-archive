#!/usr/bin/env python3
"""Build the spells/ section of The Spell Brigade wiki.

Generates spells/index.html, spells/element-matrix.html, and one HTML page per
spell. Pure HTML5; CSS lives in css/{main,components}.css; no inline styles.

All href values are relative to the page's directory (so the wiki works on
file:// and any static host).
"""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path("/home/ivan/Project/the-spell-brigade-wiki")
DATA = ROOT / "data" / "spells.json"
OUT_DIR = ROOT / "spells"
TPL_BASE = (ROOT / "templates" / "base.html").read_text()
TPL_HEADER = (ROOT / "templates" / "header.html").read_text()
TPL_FOOTER = (ROOT / "templates" / "footer.html").read_text()

OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Static data: archetype synthesis + element-key normalisation
# ---------------------------------------------------------------------------

# Map a SpellType to one primary archetype tag + a list of secondary tags. The
# game does not expose this; this is a curated synthesis based on name +
# base-stat shape (Range, FireRate, Speed, LifeTime, Size, Projectiles).
ARCHETYPES: dict[str, tuple[str, list[str]]] = {
    "Arrow":        ("projectile",  ["homing", "single-target"]),
    "Beam":         ("projectile",  ["piercing", "channeled"]),
    "Bell":         ("aoe",         ["zone", "summon"]),
    "BombLauncher": ("projectile",  ["aoe", "bouncing"]),
    "Book":         ("orbital",     ["persistent", "melee-range"]),
    "Boomerang":    ("projectile",  ["returning", "multi-hit"]),
    "EnergyZone":   ("aoe",         ["zone", "self-centred"]),
    "FallingStar":  ("aoe",         ["from-above", "burst"]),
    "Fence":        ("utility",     ["placed", "wall"]),
    "Laser":        ("projectile",  ["piercing", "channeled"]),
    "Meteor":       ("aoe",         ["from-above", "burst"]),
    "Mine":         ("utility",     ["placed", "trap"]),
    "Orb":          ("orbital",     ["persistent", "melee-range"]),
    "Plant":        ("summon",      ["placed", "stationary"]),
    "Proximity":    ("aoe",         ["self-centred", "passive"]),
    "Rifle":        ("projectile",  ["single-target", "long-range"]),
    "Shotgun":      ("projectile",  ["spread", "short-range"]),
    "Slash":        ("melee",       ["arc", "burst"]),
    "Smg":          ("projectile",  ["rapid-fire", "spread"]),
    "Summon":       ("summon",      ["minion", "autonomous"]),
    "Trail":        ("utility",     ["dot", "trail"]),
}

# Display labels for the 5 single elements used in infusions.
ELEMENT_DISPLAY = {
    "Fire": "Fire",
    "Lightning": "Lightning",
    "Ice": "Ice",
    "Acid": "Acid",
    "Dark": "Dark",
}

# Single-element infusion key set (ignoring multi/double combos for the
# top-of-page row; the matrix below covers all 21).
INFUSION_ORDER = ["Fire", "Lightning", "Ice", "Acid", "Dark"]

# Friendly description fallback for the few infusion key types we see.
INFUSION_KIND_DESC = {
    "SpellInfusion_Description_First":  "First infusion of this element.",
    "SpellInfusion_Description_Second": "Second infusion (combo).",
    "SpellInfusion_Description_Double": "Double infusion (single-element specialist).",
}

# How to interpret a variant's dynamic_parameters list. Hand-curated where the
# meaning is obvious from the variant name; otherwise rendered as raw floats.
DYNAMIC_PARAM_NOTES: dict[str, list[str]] = {
    "BellZoneGivesArmor":                 ["Armor granted while inside zone"],
    "DealMoreDamageWhenStandingStill":    ["Damage bonus % at full charge"],
    "BiggerOnLowerHealth":                ["Max size bonus % at 0 HP"],
    "ReduceDamageTakenWhenEnemiesInProximity": ["Damage reduction % per enemy"],
    "IncreaseSizeWhenStandingStill":      ["Max size bonus %", "Time to reach max (s)"],
}

# ---------------------------------------------------------------------------
# Spell -> hand-picked synergy notes. 2-4 bullets per spell. Each entry is
# (anchor-text, relative href, short explanation).
# ---------------------------------------------------------------------------

SYNERGIES: dict[str, list[tuple[str, str, str]]] = {
    "Arrow": [
        ("HitExtraEnemy variant", "#variant-hitextraenemy",
         "Stacks repeat hits with high single-target damage."),
        ("Lightning infusion", "../mechanics/elements.html#lightning",
         "Chains across the extra targets the variant exposes."),
        ("Damage-scaling artifacts", "../artifacts/by-effect.html#damage",
         "Arrow's high base damage benefits from flat Damage% rolls."),
    ],
    "Beam": [
        ("ExtraProjectile variant", "#variant-extraprojectile",
         "Up to 5 extra beams fan out — combine with FireRate improvements."),
        ("Acid infusion", "../mechanics/elements.html#acid",
         "DoT keeps ticking even while the beam re-aims."),
        ("Projectile-count artifacts", "../artifacts/by-effect.html#projectiles",
         "Each extra beam multiplies effective DPS."),
    ],
    "Bell": [
        ("BellSpawnsGuaranteedCrits variant", "#variant-bellspawnsguaranteedcrits",
         "Pairs with any CriticalDamage% source."),
        ("BellZoneGivesArmor variant", "#variant-bellzonegivesarmor",
         "Defensive option for tanky co-op builds."),
        ("Size-scaling artifacts", "../artifacts/by-effect.html#size",
         "Bell's zone benefits enormously from Size% rolls."),
    ],
    "BombLauncher": [
        ("BombLauncherExtraBounce variant", "#variant-bomblauncherextrabounce",
         "Each bounce is another full-damage AOE."),
        ("Fire infusion", "../mechanics/elements.html#fire",
         "Burn DoT applies on every bounce."),
        ("Range improvements", "#improvements",
         "Range determines bounce distance and arc."),
    ],
    "Book": [
        ("ExtraProjectile variant", "#variant-extraprojectile",
         "Orbits more pages — pure DPS multiplier."),
        ("ThrowAtEnd variant", "#variant-throwatend",
         "Bigger LifeTime turns into ranged finisher damage."),
        ("Size-scaling artifacts", "../artifacts/by-effect.html#size",
         "Larger pages = wider orbital coverage."),
    ],
    "Boomerang": [
        ("BoomerangCriticalDamageOnApex variant", "#variant-boomerangcriticaldamageonapex",
         "Pairs with CriticalDamage% stacking."),
        ("BoomerangStayOnApex variant", "#variant-boomerangstayonapex",
         "Turns the apex into a stationary multi-hit zone."),
        ("Range improvements", "#improvements",
         "Longer Range = farther apex = more travel-hits."),
    ],
    "EnergyZone": [
        ("ExtraProjectileButSmallerSize variant", "#variant-extraprojectilebutsmallersize",
         "Spawns up to 5 extra zones — area uptime skyrockets."),
        ("Size-scaling artifacts", "../artifacts/by-effect.html#size",
         "Counters the variant's size penalty."),
        ("Acid infusion", "../mechanics/elements.html#acid",
         "Persistent DoT inside long-lasting zones is brutal."),
    ],
    "FallingStar": [
        ("ExtraProjectile variant", "#variant-extraprojectile",
         "Up to 5 extra stars per cast."),
        ("Fire infusion", "../mechanics/elements.html#fire",
         "Impact burn covers the brief downtime between casts."),
        ("Damage improvements", "#improvements",
         "FallingStar lives or dies on raw burst Damage rolls."),
    ],
    "Fence": [
        ("ConnectAllFences variant", "#variant-connectallfences",
         "Turns the fence into a kiting cage."),
        ("ExtraProjectile variant", "#variant-extraprojectile",
         "More fence segments = bigger denied area."),
        ("LifeTime improvements", "#improvements",
         "Long uptime is what makes Fence a control tool."),
    ],
    "Laser": [
        ("HigherSizeLowerSpeed variant", "#variant-highersizelowerspeed",
         "Trade mobility for area coverage."),
        ("DealMoreDamageWhenStandingStill variant", "#variant-dealmoredamagewhenstandingstill",
         "Stack with stationary-bonus artifacts."),
        ("Size improvements", "#improvements",
         "Wider beam = more enemies pierced per tick."),
    ],
    "Meteor": [
        ("ExtraProjectile variant", "#variant-extraprojectile",
         "Up to 5 extra meteors per cast — saturate the field."),
        ("Fire infusion", "../mechanics/elements.html#fire",
         "Impact burn applies to every meteor."),
        ("Damage improvements", "#improvements",
         "Each meteor benefits from flat Damage% — they all crit independently."),
    ],
    "Mine": [
        ("MoveTowardsEnemies variant", "#variant-movetowardsenemies",
         "Turns a passive trap into active AOE."),
        ("ExplodeAtEnd variant", "#variant-explodeatend",
         "Guarantees the mine procs even if untouched."),
        ("Damage-scaling artifacts", "../artifacts/by-effect.html#damage",
         "Mine damage is mostly front-loaded — flat Damage% scales well."),
    ],
    "Orb": [
        ("ExtraTrajectory variant", "#variant-extratrajectory",
         "More orbits = more uptime around the caster."),
        ("IncreaseInSize variant", "#variant-increaseinsize",
         "Each tick grows the orb — late-cast bursts become massive."),
        ("Lightning infusion", "../mechanics/elements.html#lightning",
         "Chain bounces between enemies clustered around you."),
    ],
    "Plant": [
        ("AimAtHighestHP variant (if present)", "#variants",
         "Useful for boss waves where one target dominates."),
        ("LifeTime improvements", "#improvements",
         "Plants stay rooted; LifeTime is effectively uptime."),
        ("Acid infusion", "../mechanics/elements.html#acid",
         "DoT pairs naturally with stationary damage source."),
    ],
    "Proximity": [
        ("ReduceDamageTakenWhenEnemiesInProximity variant", "#variant-reducedamagetakenwhenenemiesinproximity",
         "Turns crowding into a defensive bonus."),
        ("BiggerOnLowerHealth variant", "#variant-biggeronlowerhealth",
         "Risky but enormous size at low HP."),
        ("Size improvements", "#improvements",
         "Bigger zone = more enemies hit per tick."),
    ],
    "Rifle": [
        ("AimAtHighestHP variant", "#variant-aimathighesthp",
         "Always shoots the most valuable target — perfect for elites/bosses."),
        ("Critical-damage artifacts", "../artifacts/by-effect.html#critical",
         "Single high-damage shots benefit most from crit scaling."),
        ("Range improvements", "#improvements",
         "Rifle outranges most enemies; more Range = safer shots."),
    ],
    "Shotgun": [
        ("ExtraProjectile variant", "#variant-extraprojectile",
         "More pellets per blast = much higher close-range DPS."),
        ("Fire infusion", "../mechanics/elements.html#fire",
         "Each pellet applies burn — DoT scales with pellet count."),
        ("Size-scaling artifacts", "../artifacts/by-effect.html#size",
         "Wider spread covers more targets."),
    ],
    "Slash": [
        ("IncreaseSizeWhenStandingStill variant", "#variant-increasesizewhenstandingstill",
         "Reward for holding ground — huge late arcs."),
        ("FireRate improvements", "#improvements",
         "Slash is melee; faster swings are pure DPS gain."),
        ("Dark infusion", "../mechanics/elements.html#dark",
         "Cursed slashes pair well with sustained close combat."),
    ],
    "Smg": [
        ("ExtraProjectile variant", "#variant-extraprojectile",
         "Up to 5 extra bullets per burst."),
        ("SmgRotates variant", "#variant-smgrotates",
         "Sweeps in a circle — covers all angles."),
        ("Critical-damage artifacts", "../artifacts/by-effect.html#critical",
         "High fire-rate means crit procs happen often."),
    ],
    "Summon": [
        ("FirstHitIsCrit variant", "#variant-firsthitiscrit",
         "Stacks with CriticalDamage% sources."),
        ("LifeTime improvements", "#improvements",
         "Longer-lived minions = more uptime."),
        ("Dark infusion", "../mechanics/elements.html#dark",
         "Curse minions to amplify damage on whatever they touch."),
    ],
    "Trail": [
        ("TrailEndExplodes variant", "#variant-trailendexplodes",
         "Adds a burst finisher to the DoT trail."),
        ("TrailSpawnsGuaranteedCrits variant", "#variant-trailspawnsguaranteedcrits",
         "Crits on every tick — multiply with CriticalDamage%."),
        ("DamageTickRate improvements", "#improvements",
         "Faster ticks = more DoT damage in the same uptime."),
    ],
}

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def humanize_camel(s: str) -> str:
    """`FriendlyFireHealsInstead` -> `Friendly Fire Heals Instead`."""
    # Split on case boundaries and digit boundaries.
    out = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)
    out = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", out)
    return out


def slugify(name: str) -> str:
    """`BombLauncher` -> `bomb-launcher`."""
    out = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", name)
    out = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "-", out)
    return out.lower()


def variant_display_name(variant_name: str) -> str:
    return humanize_camel(variant_name)


def variant_anchor(variant_name: str) -> str:
    # Anchor uses the kebab form of the variant_name only (no spell prefix).
    return f"variant-{variant_name.lower()}"


def element_data_attr(element_name: str) -> str:
    """Map game element name to a CSS data-element value.

    Multi-element prefab keys (FireLightning, AcidDouble, ...) collapse to
    their dominant single element for badge tinting purposes.
    """
    n = element_name.lower()
    if n.startswith("none"):
        return "neutral"
    for e in ("fire", "lightning", "ice", "acid", "dark"):
        if e in n:
            return e
    return "neutral"


# Approximate "interesting maximum" per stat, used to scale stat-bar fill so
# that the bars are visually comparable across spells. Picked from a quick
# survey of the data; not load-bearing for correctness.
STAT_MAX = {
    "Damage":        200,
    "Range":         15,
    "FireRate":      8,
    "Speed":         12,
    "LifeTime":      8,
    "DamageTickRate": 2,
    "Size":          6,
    "Projectiles":   6,
}


def stat_bar(stat_name: str, value: float, element_attr: str | None = None) -> str:
    """Render a stat-bar span the same shape the styleguide uses."""
    max_v = STAT_MAX.get(stat_name, max(10.0, value * 2))
    # 0..10 integer fill
    filled = max(0, min(10, round((value / max_v) * 10)))
    el = f' data-element="{element_attr}"' if element_attr else ""
    return (f'<span class="stat-bar"{el} data-value="{filled}" data-max="10" '
            f'aria-label="{escape(stat_name)} {value}"></span>')


# ---------------------------------------------------------------------------
# Template plumbing
# ---------------------------------------------------------------------------

def adjust_paths(html: str, depth: int) -> str:
    """Rewrite absolute hrefs (/foo/bar.html) and srcs to relative.

    Templates use root-absolute paths; the wiki must be portable to file://,
    so we rewrite for the current page's depth (depth=1 for spells/foo.html).
    """
    prefix = "../" * depth
    out = html
    # Rewrite href="/..." and src="/..." to "../..." (preserving the part
    # after the leading slash).
    out = re.sub(r'href="/([^"]*)"', lambda m: f'href="{prefix}{m.group(1)}"', out)
    out = re.sub(r'src="/([^"]*)"',  lambda m: f'src="{prefix}{m.group(1)}"', out)
    return out


def render_page(*,
                title: str,
                description: str,
                breadcrumbs_html: str,
                content_html: str,
                sidebar_html: str = "",
                page_modifiers: str = "has-sidebar",
                depth: int = 1) -> str:
    page = TPL_BASE
    page = page.replace("{{HEADER}}", TPL_HEADER)
    page = page.replace("{{FOOTER}}", TPL_FOOTER)
    page = page.replace("{{TITLE}}", escape(title))
    page = page.replace("{{DESCRIPTION}}", escape(description))
    page = page.replace("{{BREADCRUMBS}}", breadcrumbs_html)
    page = page.replace("{{CONTENT}}", content_html)
    page = page.replace("{{SIDEBAR}}", sidebar_html)
    page = page.replace("{{PAGE_MODIFIERS}}", page_modifiers)
    return adjust_paths(page, depth=depth)


def breadcrumbs(*crumbs: tuple[str, str | None]) -> str:
    """Each crumb is (label, href). href=None marks the current page."""
    parts = []
    for label, href in crumbs:
        if href is None:
            parts.append(
                f'<li aria-current="page">{escape(label)}</li>')
        else:
            parts.append(
                f'<li><a href="{escape(href)}">{escape(label)}</a></li>')
    return "\n            ".join(parts)


# ---------------------------------------------------------------------------
# Sidebar (shared across all spell pages): 21 spells grouped by archetype.
# ---------------------------------------------------------------------------

def build_spell_sidebar(spell_keys: list[str], current_key: str | None) -> str:
    groups: dict[str, list[str]] = {}
    for k in spell_keys:
        arch = ARCHETYPES[k][0].title()
        groups.setdefault(arch, []).append(k)

    GROUP_ORDER = ["Projectile", "Aoe", "Orbital", "Melee", "Summon", "Utility"]
    out = ['<aside class="sidebar" aria-label="Spells">']
    out.append('  <h2 class="sidebar__title">Spells</h2>')
    out.append('  <ul class="sidebar__nav">')
    out.append(f'    <li><a href="index.html">All spells</a></li>')
    out.append(f'    <li><a href="element-matrix.html">Element matrix</a></li>')
    out.append('  </ul>')

    for group in GROUP_ORDER:
        members = sorted(groups.get(group, []))
        if not members:
            continue
        out.append(f'  <h2 class="sidebar__title">{escape(group)}</h2>')
        out.append('  <ul class="sidebar__nav">')
        for k in members:
            slug = slugify(k)
            label = humanize_camel(k)
            current = ' aria-current="page"' if k == current_key else ""
            out.append(f'    <li><a href="{slug}.html"{current}>{escape(label)}</a></li>')
        out.append('  </ul>')
    out.append('</aside>')
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Per-spell page rendering
# ---------------------------------------------------------------------------

def render_base_stats_table(spell: dict) -> str:
    rows = []
    for s in spell["base_stats"]:
        nm = s["stat_name"]
        val = s["value"]
        rows.append(
            "<tr>"
            f"<td><a href=\"../mechanics/stats.html#{nm.lower()}\">{escape(nm)}</a></td>"
            f"<td class=\"num\">{val:g}</td>"
            f"<td>{stat_bar(nm, val)}</td>"
            "</tr>"
        )
    body = "\n          ".join(rows)
    return f"""
      <div class="stat-table-wrap">
        <table class="stat-table sortable">
          <caption>Base stats &mdash; level 1, no infusion, no improvements</caption>
          <thead>
            <tr>
              <th data-sort="string">Stat</th>
              <th data-sort="number" class="num">Value</th>
              <th>Scale</th>
            </tr>
          </thead>
          <tbody>
          {body}
          </tbody>
        </table>
      </div>
""".strip()


def render_starting_modifiers(spell: dict) -> str:
    mods = spell.get("starting_modifiers") or []
    if not mods:
        return ""
    items = []
    for m in mods:
        nm = m["stat_name"]
        val = m["value"]
        items.append(
            f'<li><a href="../mechanics/stats.html#{nm.lower()}">{escape(nm)}</a> '
            f'<strong class="num">+{val:g}%</strong></li>'
        )
    return f"""
    <section id="starting-modifiers">
      <h2>Starting modifiers</h2>
      <p>This spell starts with the following innate stat bonuses on top of
         its base stats.</p>
      <ul class="meta-list">
        {chr(10).join(items)}
      </ul>
    </section>
"""


def render_infusions(spell: dict) -> str:
    by_element = {inf["element_name"]: inf for inf in spell["infusions"]}
    cards = []
    for el in INFUSION_ORDER:
        inf = by_element.get(el)
        anchor = f"infusion-{el.lower()}"
        if not inf:
            cards.append(f"""
            <article class="item-card" data-element="{element_data_attr(el)}" id="{anchor}">
              <header class="item-card__header">
                <div>
                  <h3 class="item-card__title">{escape(el)}</h3>
                  <p class="item-card__subtitle">Not available</p>
                </div>
                <div class="item-card__badges">
                  <span class="el-badge" data-element="{element_data_attr(el)}"><span class="el-badge__glyph" aria-hidden="true"></span><span class="el-badge__label">{escape(el)}</span></span>
                </div>
              </header>
              <p class="item-card__desc">No {escape(el)} infusion is defined for this spell.</p>
            </article>""")
            continue

        kind_desc = INFUSION_KIND_DESC.get(
            inf["description_entry"], "Infusion variant.")
        demo_badge = ""
        if inf.get("is_included_in_demo"):
            demo_badge = '<span class="tag">demo</span>'
        cards.append(f"""
            <article class="item-card" data-element="{element_data_attr(el)}" id="{anchor}">
              <header class="item-card__header">
                <div>
                  <h3 class="item-card__title">{escape(humanize_camel(spell['spell_type']))} &middot; {escape(el)}</h3>
                  <p class="item-card__subtitle"><code>{escape(inf['name'])}</code></p>
                </div>
                <div class="item-card__badges">
                  <span class="el-badge" data-element="{element_data_attr(el)}"><span class="el-badge__glyph" aria-hidden="true"></span><span class="el-badge__label">{escape(el)}</span></span>
                  {demo_badge}
                </div>
              </header>
              <p class="item-card__desc">{escape(kind_desc)} See <a href="../mechanics/elements.html#{el.lower()}">{escape(el)} element</a> for matchup multipliers.</p>
            </article>""")

    return f"""
    <section id="infusions">
      <h2>Infusions</h2>
      <p>Each spell accepts one infusion at a time, drawn from the five
         single elements. Combining two infusions of different elements
         produces a combo prefab (see the <a href="element-matrix.html">element matrix</a> for all 21 combinations).</p>
      <div class="grid grid-cards">
        {''.join(cards)}
      </div>
    </section>
"""


def render_variant_card(spell_key: str, v: dict) -> str:
    vname = v["variant_name"]
    display = variant_display_name(vname)
    anchor = variant_anchor(vname)

    warn = ""
    if v.get("hide_for_single_player"):
        warn = """
              <aside class="callout" data-kind="warn">
                <span class="callout__title">Co-op only</span>
                <p>Hidden in single-player runs (<code>HideForSinglePlayer = true</code>).</p>
              </aside>"""

    # Stat modifier chips
    mod_chips = []
    for m in v.get("stat_modifiers") or []:
        sign = "+" if m["value"] >= 0 else ""
        mod_chips.append(
            f'<span class="tag">{escape(m["stat_name"])} {sign}{m["value"]:g}%</span>'
        )
    repeat = v.get("repeat_amount") or 0
    if repeat:
        mod_chips.append(f'<span class="tag">stackable &times;{repeat}</span>')

    # Dynamic parameters
    dyn = v.get("dynamic_parameters") or []
    dyn_html = ""
    if dyn:
        notes = DYNAMIC_PARAM_NOTES.get(vname)
        items = []
        for i, val in enumerate(dyn):
            label = notes[i] if notes and i < len(notes) else f"param {i+1}"
            items.append(
                f"<li><code>{val:g}</code> &mdash; <span class=\"u-muted\">{escape(label)}</span></li>"
            )
        dyn_html = (
            '<div class="meta-dl"><dt>Dynamic parameters</dt><dd><ul class="meta-list">'
            + "".join(items)
            + "</ul></dd></div>"
        )

    mods_block = ""
    if mod_chips:
        mods_block = f'<div class="item-card__badges">{"".join(mod_chips)}</div>'

    return f"""
        <article class="item-card" data-kind="variant" id="{anchor}">
          <header class="item-card__header">
            <div>
              <h3 class="item-card__title">{escape(display)}</h3>
              <p class="item-card__subtitle"><code>{escape(v['name'])}</code></p>
            </div>
          </header>
          <p class="item-card__desc">{escape(display)} <span class="u-muted">(in-game description not available in this build).</span></p>
          {mods_block}
          {dyn_html}
          {warn}
        </article>"""


def render_variants(spell: dict) -> str:
    variants = spell.get("variants") or []
    if not variants:
        return ""
    cards = "\n".join(render_variant_card(spell["spell_type"], v) for v in variants)
    return f"""
    <section id="variants">
      <h2>Variants</h2>
      <p>Mutually-exclusive on-pickup choices that reshape how the spell
         behaves. <code>repeat_amount</code> indicates how many extra times
         the variant can stack.</p>
      <div class="grid grid-cards">
        {cards}
      </div>
    </section>
"""


def render_improvements(spell: dict) -> str:
    imps = spell.get("improvements") or []
    if not imps:
        return ""
    rows = []
    for i, imp in enumerate(imps, 1):
        stat = imp["stat_name"]
        v = imp["values_by_rarity"]
        rows.append(
            f'<tr id="improvement-{i}">'
            f'<td><a href="../mechanics/stats.html#{stat.lower()}">{escape(stat)}</a></td>'
            f'<td class="num">+{v["common"]:g}%</td>'
            f'<td class="num">+{v["rare"]:g}%</td>'
            f'<td class="num">+{v["epic"]:g}%</td>'
            f'<td class="num">+{v["legendary"]:g}%</td>'
            "</tr>"
        )
    body = "\n          ".join(rows)
    return f"""
    <section id="improvements">
      <h2>Improvements</h2>
      <p>Per-rarity stat upgrades that drop during a run. Values are
         additive percentages applied to the spell's base stat.</p>
      <div class="stat-table-wrap">
        <table class="stat-table sortable">
          <caption>Rarity scaling for each improvement</caption>
          <thead>
            <tr>
              <th data-sort="string">Stat</th>
              <th class="num"><span class="rarity-pill" data-rarity="common">Common</span></th>
              <th class="num"><span class="rarity-pill" data-rarity="rare">Rare</span></th>
              <th class="num"><span class="rarity-pill" data-rarity="epic">Epic</span></th>
              <th class="num"><span class="rarity-pill" data-rarity="legendary">Legendary</span></th>
            </tr>
          </thead>
          <tbody>
          {body}
          </tbody>
        </table>
      </div>
    </section>
"""


def render_synergies(spell_key: str) -> str:
    bullets = SYNERGIES.get(spell_key, [])
    if not bullets:
        return ""
    items = "\n        ".join(
        f'<li><a href="{escape(href)}">{escape(text)}</a> &mdash; {escape(why)}</li>'
        for text, href, why in bullets
    )
    return f"""
    <section id="synergies">
      <h2>Synergies</h2>
      <ul class="meta-list">
        {items}
      </ul>
    </section>
"""


def render_see_also(spell_key: str) -> str:
    arch = ARCHETYPES[spell_key][0]
    # Find a couple of sibling spells in the same archetype
    siblings = [k for k, (a, _) in ARCHETYPES.items()
                if a == arch and k != spell_key][:3]
    sibling_links = "\n        ".join(
        f'<a class="see-also__link" href="{slugify(k)}.html">'
        f'<strong>{escape(humanize_camel(k))}</strong>'
        f'Another {escape(arch)} spell &mdash; compare base stats and variants.'
        f'</a>'
        for k in siblings
    )
    return f"""
    <section id="related">
      <h2>See also</h2>
      <div class="see-also">
        {sibling_links}
        <a class="see-also__link" href="../mechanics/damage-calculation.html">
          <strong>Damage calculation</strong>
          The master formula that turns base damage into a final hit number.
        </a>
        <a class="see-also__link" href="../mechanics/stats.html">
          <strong>Stat reference</strong>
          Every stat the spell touches, with stacking rules.
        </a>
        <a class="see-also__link" href="../mechanics/elements.html">
          <strong>Element matchups</strong>
          Strength/weakness multipliers for each infusion.
        </a>
        <a class="see-also__link" href="index.html">
          <strong>All spells</strong>
          Back to the spell index.
        </a>
      </div>
    </section>
"""


def render_spell_page(spell_key: str, spell: dict, spell_keys: list[str]) -> str:
    name = humanize_camel(spell["spell_type"])
    arch, tags = ARCHETYPES[spell_key]

    # Pick a primary-stat highlight: Damage if present, else first base stat.
    primary = next((s for s in spell["base_stats"] if s["stat_name"] == "Damage"),
                   spell["base_stats"][0])

    tag_html = "".join(f'<span class="tag">{escape(t)}</span>' for t in [arch] + tags)

    hero = f"""
    <header class="page-hero">
      <p class="page-hero__eyebrow">Spell &middot; SpellType <code>{spell['spell_type_id']}</code></p>
      <h1 id="overview">{escape(name)}</h1>
      <p class="page-hero__lede">
        {escape(name)} is a <strong>{escape(arch)}</strong> spell. Its
        baseline <a href="../mechanics/stats.html#{primary['stat_name'].lower()}">{escape(primary['stat_name'])}</a>
        is <strong class="num">{primary['value']:g}</strong>.
        Below: every infusion, variant and improvement currently extracted
        from the game files.
      </p>
      <div class="page-hero__badges">
        {tag_html}
      </div>
    </header>
"""

    content = f"""
    {hero}

    <section id="base">
      <h2>Base configuration</h2>
      {render_base_stats_table(spell)}
      <p>
        <a href="../mechanics/damage-calculation.html#formula">How these
        numbers turn into a damage figure &rarr;</a>
      </p>
    </section>

    {render_starting_modifiers(spell)}

    {render_infusions(spell)}

    {render_variants(spell)}

    {render_improvements(spell)}

    {render_synergies(spell_key)}

    {render_see_also(spell_key)}
"""

    sidebar = build_spell_sidebar(spell_keys, spell_key)
    crumbs = breadcrumbs(
        ("Home", "../index.html"),
        ("Spells", "index.html"),
        (name, None),
    )
    desc = (f"{name}: base stats, all infusions, variants, and improvements "
            f"for The Spell Brigade.")
    return render_page(
        title=name,
        description=desc,
        breadcrumbs_html=crumbs,
        content_html=content,
        sidebar_html=sidebar,
    )


# ---------------------------------------------------------------------------
# Index page
# ---------------------------------------------------------------------------

def render_index_page(spells: dict, spell_keys: list[str]) -> str:
    # Filter-chip rows
    elements_row = "".join(
        f'<button class="tier-chip" type="button" data-facet="element" data-value="{e.lower()}">{escape(e)}</button>'
        for e in INFUSION_ORDER
    )
    archetypes = sorted({ARCHETYPES[k][0] for k in spell_keys})
    archetype_row = "".join(
        f'<button class="tier-chip" type="button" data-facet="archetype" data-value="{a}">{escape(a.title())}</button>'
        for a in archetypes
    )

    # Card grid
    cards = []
    for k in spell_keys:
        s = spells[k]
        arch, tags = ARCHETYPES[k]
        slug = slugify(k)
        dmg = next((b["value"] for b in s["base_stats"] if b["stat_name"] == "Damage"), None)
        dmg_str = f"{dmg:g}" if dmg is not None else "n/a"
        infus = s["counts"]["infusions"]
        vars_ = s["counts"]["variants"]
        imps = s["counts"]["improvements"]
        tag_html = "".join(f'<span class="tag">{escape(t)}</span>' for t in [arch] + tags)
        cards.append(f"""
            <article class="item-card" data-kind="spell"
                     data-archetype="{escape(arch)}"
                     data-spell="{escape(k)}">
              <header class="item-card__header">
                <div>
                  <h3 class="item-card__title"><a href="{slug}.html">{escape(humanize_camel(k))}</a></h3>
                  <p class="item-card__subtitle">SpellType <code>{s['spell_type_id']}</code> &middot; {escape(arch)}</p>
                </div>
              </header>
              <div class="item-card__badges">{tag_html}</div>
              <div class="item-card__stats">
                <div class="item-card__stat"><span class="item-card__stat-label">Damage</span><span class="item-card__stat-value">{dmg_str}</span></div>
                <div class="item-card__stat"><span class="item-card__stat-label">Infusions</span><span class="item-card__stat-value">{infus}</span></div>
                <div class="item-card__stat"><span class="item-card__stat-label">Variants</span><span class="item-card__stat-value">{vars_}</span></div>
                <div class="item-card__stat"><span class="item-card__stat-label">Improvements</span><span class="item-card__stat-value">{imps}</span></div>
              </div>
            </article>""")

    # Comparison table
    table_rows = []
    for k in spell_keys:
        s = spells[k]
        slug = slugify(k)
        by = {b["stat_name"]: b["value"] for b in s["base_stats"]}
        def cell(n):
            v = by.get(n)
            return f'<td class="num">{v:g}</td>' if v is not None else '<td class="num u-muted">&mdash;</td>'
        table_rows.append(
            "<tr>"
            f"<td><a href=\"{slug}.html\">{escape(humanize_camel(k))}</a></td>"
            f"<td>{escape(ARCHETYPES[k][0])}</td>"
            + cell("Damage") + cell("FireRate") + cell("Speed") + cell("Range") +
            "</tr>"
        )
    table_body = "\n          ".join(table_rows)

    content = f"""
    <header class="page-hero">
      <p class="page-hero__eyebrow">Section hub</p>
      <h1>Spells</h1>
      <p class="page-hero__lede">
        All {len(spell_keys)} spell types in The Spell Brigade. Pick a spell
        for its full breakdown &mdash; base stats, every infusion, every
        variant, and per-rarity improvements. The
        <a href="element-matrix.html">element matrix</a> shows which
        prefab exists for each (spell, element) pair.
      </p>
    </header>

    <section id="filters" aria-labelledby="filters-h">
      <h2 id="filters-h">Filters</h2>
      <p>Click a chip to highlight matching cards. Filters are visual aids;
         the page works without JavaScript.</p>
      <div class="meta-dl">
        <dt>By element availability</dt>
        <dd>{elements_row}</dd>
        <dt>By archetype</dt>
        <dd>{archetype_row}</dd>
      </div>
    </section>

    <section id="grid" aria-labelledby="grid-h">
      <h2 id="grid-h">All spells</h2>
      <div class="grid grid-cards" data-spell-grid>
        {''.join(cards)}
      </div>
    </section>

    <section id="comparison" aria-labelledby="cmp-h">
      <h2 id="cmp-h">Comparison table</h2>
      <p>Sortable by any column; default sort is by spell name.</p>
      <div class="stat-table-wrap">
        <table class="stat-table sortable">
          <caption>All 21 spells &mdash; baseline values for the four most-used stats</caption>
          <thead>
            <tr>
              <th data-sort="string">Spell</th>
              <th data-sort="string">Archetype</th>
              <th data-sort="number" class="num">Damage</th>
              <th data-sort="number" class="num">FireRate</th>
              <th data-sort="number" class="num">Speed</th>
              <th data-sort="number" class="num">Range</th>
            </tr>
          </thead>
          <tbody>
          {table_body}
          </tbody>
        </table>
      </div>
    </section>

    <section id="related">
      <h2>See also</h2>
      <div class="see-also">
        <a class="see-also__link" href="element-matrix.html">
          <strong>Spell &times; element matrix</strong>
          All 21 spells across all 21 element combinations &mdash; one chip per prefab.
        </a>
        <a class="see-also__link" href="../mechanics/elements.html">
          <strong>Element reference</strong>
          Damage type matchups, immunities, and combo rules.
        </a>
        <a class="see-also__link" href="../mechanics/damage-calculation.html">
          <strong>Damage calculation</strong>
          How a base-stat number becomes a hit number.
        </a>
        <a class="see-also__link" href="../guides/index.html">
          <strong>Build guides</strong>
          Curated combinations of spells, infusions, and artifacts.
        </a>
      </div>
    </section>
"""

    sidebar = build_spell_sidebar(spell_keys, None)
    crumbs = breadcrumbs(
        ("Home", "../index.html"),
        ("Spells", None),
    )
    return render_page(
        title="Spells",
        description=("Catalogue of all 21 spell types in The Spell Brigade, "
                     "with base stats, infusions, variants and improvements."),
        breadcrumbs_html=crumbs,
        content_html=content,
        sidebar_html=sidebar,
    )


# ---------------------------------------------------------------------------
# Element matrix
# ---------------------------------------------------------------------------

def render_element_matrix(spells: dict, spell_keys: list[str],
                          element_type_map: dict) -> str:
    # Column order: the 21 element keys as listed in the data, in their
    # game-file order (single elements first, then doubles, then combos).
    element_cols = list(element_type_map.values())
    # Build header
    header_cells = "".join(
        f'<th class="matrix__el" scope="col" data-element="{element_data_attr(el)}">'
        f'<span class="el-badge" data-element="{element_data_attr(el)}">'
        f'<span class="el-badge__glyph" aria-hidden="true"></span>'
        f'<span class="el-badge__label">{escape(el)}</span></span></th>'
        for el in element_cols
    )

    rows = []
    for k in spell_keys:
        slug = slugify(k)
        prefabs = spells[k].get("prefab_guids_by_element", {})
        cells = []
        for el in element_cols:
            guid = prefabs.get(el)
            if guid:
                cells.append(
                    f'<td class="matrix__cell" data-element="{element_data_attr(el)}">'
                    f'<span class="tag" title="{escape(guid)}" aria-label="{escape(k)} {escape(el)} prefab present">&#10003;</span>'
                    "</td>"
                )
            else:
                cells.append(
                    '<td class="matrix__cell matrix__cell--empty" aria-label="not present">&middot;</td>'
                )
        rows.append(
            "<tr>"
            f"<th scope=\"row\"><a href=\"{slug}.html\">{escape(humanize_camel(k))}</a></th>"
            + "".join(cells)
            + "</tr>"
        )

    table = f"""
      <div class="stat-table-wrap matrix-wrap">
        <table class="stat-table matrix">
          <caption>Prefab presence for each (spell, element) pair &mdash; check mark = configured prefab exists</caption>
          <thead>
            <tr>
              <th scope="col">Spell</th>
              {header_cells}
            </tr>
          </thead>
          <tbody>
          {chr(10).join(rows)}
          </tbody>
        </table>
      </div>
"""

    content = f"""
    <header class="page-hero">
      <p class="page-hero__eyebrow">Lookup table</p>
      <h1>Spell &times; element matrix</h1>
      <p class="page-hero__lede">
        Every spell can be infused with each of the 5 single elements, the 5
        double-infusions, and the 10 two-element combinations &mdash; for a
        total of 21 element prefabs per spell. The matrix below confirms
        which prefabs are actually present in the extracted game data.
      </p>
    </header>

    <section id="matrix">
      <h2>The matrix</h2>
      <p>Tap a spell name to open its detail page. Hover any check mark to
         see the prefab GUID.</p>
      {table}
    </section>

    <section id="related">
      <h2>See also</h2>
      <div class="see-also">
        <a class="see-also__link" href="index.html">
          <strong>Spell index</strong>
          All 21 spells with filters and a sortable comparison table.
        </a>
        <a class="see-also__link" href="../mechanics/element-matrix.html">
          <strong>Element &times; element matrix</strong>
          Damage multipliers between elements (lookup-optimised).
        </a>
        <a class="see-also__link" href="../mechanics/elements.html">
          <strong>Element reference</strong>
          Names, glyphs, and infusion combo rules.
        </a>
      </div>
    </section>
"""
    sidebar = build_spell_sidebar(spell_keys, None)
    crumbs = breadcrumbs(
        ("Home", "../index.html"),
        ("Spells", "index.html"),
        ("Element matrix", None),
    )
    return render_page(
        title="Spell × element matrix",
        description=("Coverage matrix of all 21 spells against the 21 element "
                     "prefab keys in The Spell Brigade."),
        breadcrumbs_html=crumbs,
        content_html=content,
        sidebar_html=sidebar,
    )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def main() -> None:
    data = json.loads(DATA.read_text())
    spells = data["spells"]
    element_type_map = data["element_type_map"]
    # Canonical alphabetical order for the index + sidebar
    spell_keys = sorted(spells.keys())

    written: list[Path] = []

    # Per-spell pages
    for k in spell_keys:
        html = render_spell_page(k, spells[k], spell_keys)
        path = OUT_DIR / f"{slugify(k)}.html"
        path.write_text(html)
        written.append(path)

    # Index
    idx_path = OUT_DIR / "index.html"
    idx_path.write_text(render_index_page(spells, spell_keys))
    written.append(idx_path)

    # Matrix
    mx_path = OUT_DIR / "element-matrix.html"
    mx_path.write_text(render_element_matrix(spells, spell_keys, element_type_map))
    written.append(mx_path)

    print(f"Wrote {len(written)} files to {OUT_DIR}")
    for p in written:
        print(" -", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
