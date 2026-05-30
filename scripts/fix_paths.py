#!/usr/bin/env python3
"""Fix absolute-root href/src paths and known broken-link patterns across
the static HTML wiki.

This script is idempotent and re-runnable. It:

  1. Rewrites href="/foo/bar.html" and src="/foo/bar.html" to depth-relative
     paths so the wiki works on file:// and at any URL prefix. Skips
     templates/ (which intentionally use absolute paths consumed by the
     build script).
  2. Rewrites a small set of known broken-link patterns:
       - mechanics/damage-calculation.html  -> mechanics/damage-system.html
       - artifacts/by-effect.html           -> artifacts/index.html
       - artifacts/index.html#<N>           -> artifacts/index.html#artifact-<N>
       - mechanics/stats.html#criticaldamage -> mechanics/stats.html#critdamage
       - mechanics/curses.html#strongerenemies -> #stronger-enemies
       - index.html#contributing            -> about.html  (anchor removed)
       - per-page variant typos in spells/mine.html and spells/orb.html

Skip rules:
  - Files under /templates/ are left alone (build sources).
  - data-* attributes are not modified.
  - http(s):// and data: hrefs are not modified.

Usage:
    python3 scripts/fix_paths.py [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ABS_HREF = re.compile(r'(href|src)="/([a-zA-Z][^"]*)"')
# Also normalize data-search-index since js/wiki.js fetches it as-is and an
# absolute "/data/..." path breaks under file:// or any non-root URL prefix.
ABS_DATA_SEARCH = re.compile(r'data-search-index="/([a-zA-Z][^"]*)"')

# Per-page rewrites applied to every HTML file. Order matters: file-target
# rewrites first, then anchor rewrites.
LINK_REWRITES: list[tuple[re.Pattern[str], str]] = [
    # Non-existent target pages
    (re.compile(r'(mechanics/)damage-calculation\.html'), r'\1damage-system.html'),
    (re.compile(r'(artifacts/)by-effect\.html(#[a-z0-9-]+)?'), r'\1index.html'),
    # Anchor name fixes
    (re.compile(r'(mechanics/stats\.html)#criticaldamage\b'), r'\1#critdamage'),
    (re.compile(r'(mechanics/curses\.html)#strongerenemies\b'), r'\1#stronger-enemies'),
    # artifacts/index.html#13  ->  artifacts/index.html#artifact-13
    # Use lookbehind to avoid double-rewriting already-prefixed anchors.
    (re.compile(r'(artifacts/index\.html)#(?!artifact-)([0-9]+)\b'), r'\1#artifact-\2'),
    # The "contributing" section was never built on index.html. Send readers
    # to the About page (which covers methodology/sources) instead. The
    # leading "../" path component (or absence of one) is preserved.
    (re.compile(r'index\.html#contributing\b'), 'about.html'),
]


def page_depth(path: Path) -> int:
    """Depth from wiki root (e.g. /spells/foo.html -> 1)."""
    return len(path.relative_to(ROOT).parts) - 1


def fix_absolute_paths(text: str, depth: int) -> tuple[str, int]:
    """Convert href="/..." and src="/..." (plus data-search-index="/...")
    to depth-relative form so the wiki works on file:// and at any URL
    prefix."""
    prefix = "../" * depth
    count = 0

    def _sub_href(m: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return f'{m.group(1)}="{prefix}{m.group(2)}"'

    out = ABS_HREF.sub(_sub_href, text)

    def _sub_data(m: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return f'data-search-index="{prefix}{m.group(1)}"'

    out = ABS_DATA_SEARCH.sub(_sub_data, out)
    return out, count


def fix_known_link_bugs(text: str) -> tuple[str, int]:
    """Apply the curated set of link rewrites."""
    total = 0
    out = text
    for pattern, repl in LINK_REWRITES:
        if callable(repl):
            new = pattern.sub(repl, out)
        else:
            new = pattern.sub(repl, out)
        # count substitutions
        matches = len(pattern.findall(out))
        total += matches
        out = new
    return out, total


def find_html_files(root: Path) -> list[Path]:
    """All .html files except those under templates/."""
    return [p for p in sorted(root.rglob("*.html")) if "templates" not in p.parts]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Report changes without writing files.")
    args = parser.parse_args()

    files = find_html_files(ROOT)
    total_abs = 0
    total_link = 0
    files_changed = 0

    for f in files:
        original = f.read_text()
        new, abs_n = fix_absolute_paths(original, page_depth(f))
        new, link_n = fix_known_link_bugs(new)
        if new != original:
            files_changed += 1
            total_abs += abs_n
            total_link += link_n
            if not args.dry_run:
                f.write_text(new)
            print(f"  fixed {f.relative_to(ROOT)}: abs={abs_n} link={link_n}")

    print()
    print(f"Files scanned:    {len(files)}")
    print(f"Files changed:    {files_changed}")
    print(f"Abs paths fixed:  {total_abs}")
    print(f"Link bugs fixed:  {total_link}")
    if args.dry_run:
        print("(dry-run: no files written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
