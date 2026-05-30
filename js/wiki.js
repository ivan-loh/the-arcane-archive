/* ============================================================================
 * The Spell Brigade Wiki — wiki.js
 * ----------------------------------------------------------------------------
 * Vanilla JS, no dependencies. Progressive enhancement — every feature
 * degrades gracefully if JS is disabled.
 *
 *   1. initStatBars()      Fill .stat-bar elements with glyph runs.
 *   2. initTableSort()     Click-to-sort .stat-table th[data-sort] columns.
 *   3. initMobileNav()     Toggle .mobile-nav panel.
 *   4. initSearch()        Live search against /data/search-index.json.
 *   5. initFilters()       Generic data-filter button groups.
 *
 * Search index format (data/search-index.json):
 *   [
 *     { "title": "Fireball",
 *       "url": "/spells/fireball.html",
 *       "kind": "spell",
 *       "element": "fire",
 *       "tags": ["aoe","projectile"] },
 *     ...
 *   ]
 * ========================================================================== */
(function () {
  'use strict';

  // ------------------------------------------------------------------ helpers
  const $  = (sel, ctx) => (ctx || document).querySelector(sel);
  const $$ = (sel, ctx) => Array.from((ctx || document).querySelectorAll(sel));

  const debounce = (fn, ms) => {
    let t;
    return function () {
      clearTimeout(t);
      const args = arguments, ctx = this;
      t = setTimeout(() => fn.apply(ctx, args), ms);
    };
  };

  const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));

  // ----------------------------------------------------------- 1. stat bars
  function initStatBars() {
    const FILLED = '▰'; // ▰
    const EMPTY  = '▱'; // ▱

    $$('.stat-bar').forEach((el) => {
      if (el.dataset.rendered === 'true') return;
      const max = Math.max(1, parseInt(el.dataset.max, 10) || 10);
      let val = parseFloat(el.dataset.value);
      if (isNaN(val)) val = 0;
      val = Math.max(0, Math.min(max, val));
      const filled = Math.round(val);
      const empty  = max - filled;

      const showNum = el.dataset.showNumber !== 'false';
      const glyphs = document.createElement('span');
      glyphs.className = 'stat-bar__glyphs';
      glyphs.setAttribute('aria-hidden', 'true');
      glyphs.innerHTML =
        '<span class="on">' + FILLED.repeat(filled) + '</span>' +
        '<span class="off">' + EMPTY.repeat(empty) + '</span>';
      el.appendChild(glyphs);

      if (showNum) {
        const num = document.createElement('span');
        num.className = 'stat-bar__num';
        const suffix = el.dataset.suffix || ('/' + max);
        num.textContent = val + suffix;
        el.appendChild(num);
      }

      // a11y meter role if author didn't already set one
      if (!el.hasAttribute('role')) el.setAttribute('role', 'meter');
      if (!el.hasAttribute('aria-valuenow')) el.setAttribute('aria-valuenow', val);
      if (!el.hasAttribute('aria-valuemin')) el.setAttribute('aria-valuemin', 0);
      if (!el.hasAttribute('aria-valuemax')) el.setAttribute('aria-valuemax', max);

      el.dataset.rendered = 'true';
    });
  }

  // ----------------------------------------------------------- 2. table sort
  function initTableSort() {
    $$('.stat-table').forEach((table) => {
      const headers = $$('th[data-sort]', table);
      headers.forEach((th, colIndex) => {
        th.setAttribute('tabindex', '0');
        th.setAttribute('role', 'button');
        if (!th.hasAttribute('aria-sort')) th.setAttribute('aria-sort', 'none');

        const handler = () => sortTable(table, th, colIndex);
        th.addEventListener('click', handler);
        th.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handler();
          }
        });
      });
    });
  }

  function sortTable(table, th, colIndex) {
    const tbody = table.tBodies[0];
    if (!tbody) return;
    const rows = Array.from(tbody.rows);
    const type = th.dataset.sort || 'string';
    const current = th.getAttribute('aria-sort');
    const dir = current === 'ascending' ? 'descending' : 'ascending';

    // reset other headers
    $$('th[aria-sort]', table).forEach((other) => {
      if (other !== th) other.setAttribute('aria-sort', 'none');
    });
    th.setAttribute('aria-sort', dir);

    const cellVal = (row) => {
      const cell = row.cells[colIndex];
      if (!cell) return '';
      const raw = cell.dataset.sortValue != null
        ? cell.dataset.sortValue
        : cell.textContent.trim();
      if (type === 'number') {
        const n = parseFloat(String(raw).replace(/[^0-9.\-]/g, ''));
        return isNaN(n) ? -Infinity : n;
      }
      return String(raw).toLowerCase();
    };

    rows.sort((a, b) => {
      const va = cellVal(a), vb = cellVal(b);
      if (va < vb) return dir === 'ascending' ? -1 : 1;
      if (va > vb) return dir === 'ascending' ? 1 : -1;
      return 0;
    });

    const frag = document.createDocumentFragment();
    rows.forEach((r) => frag.appendChild(r));
    tbody.appendChild(frag);
  }

  // ----------------------------------------------------------- 3. mobile nav
  function initMobileNav() {
    const toggle = $('[data-nav-toggle]');
    const panel  = $('[data-mobile-nav]');
    if (!toggle || !panel) return;

    const setOpen = (open) => {
      panel.dataset.open = open ? 'true' : 'false';
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    };

    toggle.addEventListener('click', () => {
      const isOpen = panel.dataset.open === 'true';
      setOpen(!isOpen);
    });

    // close on link click + escape
    panel.addEventListener('click', (e) => {
      if (e.target.tagName === 'A') setOpen(false);
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && panel.dataset.open === 'true') setOpen(false);
    });
  }

  // ----------------------------------------------------------- 4. search
  function initSearch() {
    const root = $('[data-search]');
    if (!root) return;
    const input   = $('.search__input', root);
    const results = $('.search__results', root);
    if (!input || !results) return;

    let index = null;
    let loading = false;
    let selectedIdx = -1;

    // Default fallback: walk up from the current page to the wiki root.
    // `pathname` ends in /foo/bar.html, so the number of "../" hops equals
    // (segments - 1). This makes the wiki usable on file:// without any
    // hard-coded site root.
    const computeFallback = () => {
      const segs = window.location.pathname.split('/').filter(Boolean);
      const upCount = Math.max(0, segs.length - 1);
      return '../'.repeat(upCount) + 'data/search-index.json';
    };
    const indexUrl = root.dataset.searchIndex || computeFallback();

    const ensureIndex = async () => {
      if (index || loading) return;
      loading = true;
      try {
        const resp = await fetch(indexUrl, { cache: 'force-cache' });
        if (resp.ok) index = await resp.json();
        else index = [];
      } catch (_e) {
        index = [];
      } finally {
        loading = false;
      }
    };

    const score = (item, q) => {
      const t = item.title.toLowerCase();
      if (t === q) return 100;
      if (t.startsWith(q)) return 80;
      if (t.includes(q)) return 60;
      const tagHit = (item.tags || []).some((x) => x.toLowerCase().includes(q));
      if (tagHit) return 40;
      if ((item.kind || '').toLowerCase().includes(q)) return 20;
      return 0;
    };

    const render = (items, q) => {
      if (!items.length) {
        results.innerHTML = '<div class="search__empty">No entries match &ldquo;'
          + escapeHtml(q) + '&rdquo;.</div>';
        results.hidden = false;
        return;
      }
      results.innerHTML = items.map((it, i) => {
        const meta = [it.kind, it.element].filter(Boolean).join(' · ');
        return '<a class="search__result" role="option"'
          + ' id="search-opt-' + i + '"'
          + ' aria-selected="' + (i === selectedIdx ? 'true' : 'false') + '"'
          + ' href="' + escapeHtml(it.url) + '">'
          + '<span class="search__result-title">' + escapeHtml(it.title) + '</span>'
          + (meta ? '<span class="search__result-meta">' + escapeHtml(meta) + '</span>' : '')
          + '</a>';
      }).join('');
      results.hidden = false;
    };

    const search = debounce(async () => {
      const q = input.value.trim().toLowerCase();
      if (!q) { results.hidden = true; results.innerHTML = ''; selectedIdx = -1; return; }
      await ensureIndex();
      if (!index) return;
      const scored = index
        .map((it) => ({ it, s: score(it, q) }))
        .filter((r) => r.s > 0)
        .sort((a, b) => b.s - a.s)
        .slice(0, 10)
        .map((r) => r.it);
      selectedIdx = -1;
      render(scored, q);
    }, 120);

    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-expanded', 'false');
    input.setAttribute('aria-controls', results.id || 'search-results');
    results.id = results.id || 'search-results';
    results.setAttribute('role', 'listbox');

    input.addEventListener('input', search);
    input.addEventListener('focus', () => { if (input.value.trim()) search(); });

    input.addEventListener('keydown', (e) => {
      const items = $$('.search__result', results);
      if (!items.length) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedIdx = (selectedIdx + 1) % items.length;
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedIdx = (selectedIdx - 1 + items.length) % items.length;
      } else if (e.key === 'Enter' && selectedIdx >= 0) {
        e.preventDefault();
        items[selectedIdx].click();
        return;
      } else if (e.key === 'Escape') {
        results.hidden = true;
        input.blur();
        return;
      } else { return; }
      items.forEach((el, i) => el.setAttribute('aria-selected', i === selectedIdx ? 'true' : 'false'));
      if (items[selectedIdx]) items[selectedIdx].scrollIntoView({ block: 'nearest' });
    });

    document.addEventListener('click', (e) => {
      if (!root.contains(e.target)) results.hidden = true;
    });
  }

  // ----------------------------------------------------------- 5. filters
  function initFilters() {
    $$('[data-filter-group]').forEach((group) => {
      const targetSel = group.dataset.filterTarget;
      if (!targetSel) return;
      const targets = $$(targetSel);

      group.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-filter]');
        if (!btn) return;
        const value = btn.dataset.filter;
        $$('[data-filter]', group).forEach((b) => b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'));
        targets.forEach((t) => {
          const match = value === 'all'
            || (t.dataset.filterTags || '').split(/\s+/).includes(value)
            || t.dataset.element === value
            || t.dataset.rarity === value
            || t.dataset.kind === value;
          t.hidden = !match;
        });
      });
    });
  }

  // ---------------------------------------------------------------- boot
  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else { fn(); }
  }

  ready(() => {
    initStatBars();
    initTableSort();
    initMobileNav();
    initSearch();
    initFilters();
  });
})();
