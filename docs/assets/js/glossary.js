/* ============================================================
   PBM — 用語集エンジン
   ・docs/content/glossary/*.json を読み込み（存在しないファイルは無視）
   ・本文中の専門用語を自動的に用語集へリンク
   ・リンクにホバー / タップで用語ポップオーバーを表示
   ============================================================ */
(function () {
  "use strict";

  const PBM = (window.PBM = window.PBM || {});
  const url = (rel) => (typeof PBM.url === "function" ? PBM.url(rel) : rel);
  const esc = (s) =>
    typeof PBM.esc === "function"
      ? PBM.esc(s)
      : String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
          ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const DIR = "content/glossary/";
  const MAX_PER_PAGE = 2;      /* 同じ用語は1ページに2回までしかリンクしない */
  const MIN_SURFACE = 2;       /* 1文字の語は自動リンクしない */

  /* 用語ファイルの推測候補（index.json が無いときのフォールバック）。
     存在しないファイルは 404 になるが、すべて握り潰す。 */
  const CANDIDATE_FILES = (function () {
    const a = [];
    for (let i = 0; i <= 24; i++) a.push("M" + String(i).padStart(2, "0"));
    return a;
  })();

  /* 既知モジュールの表示名（curriculum から取れない場合の予備） */
  const MODULE_FALLBACK = { M00: { title: "共通の基礎用語", tier: "T0" } };

  /* ---------------------------------------------------------
     1. データ読み込み（キャッシュ付き・エラーは握り潰す）
     --------------------------------------------------------- */
  async function getJSON(rel) {
    try {
      const res = await fetch(url(rel), { cache: "no-cache" });
      if (!res.ok) return null;
      return await res.json();
    } catch (e) {
      return null;
    }
  }

  function normalize(raw, mid) {
    if (!raw || typeof raw !== "object") return null;
    const term = String(raw.term == null ? "" : raw.term).trim();
    if (!term) return null;
    const tags = Array.isArray(raw.tags) ? raw.tags.filter(Boolean).map(String) : [];
    const aliases = Array.isArray(raw.aliases) ? raw.aliases.filter(Boolean).map(String) : [];
    return {
      term: term,
      en: raw.en ? String(raw.en) : "",
      reading: String(raw.reading || raw.yomi || term).trim(),
      short: raw.short ? String(raw.short) : "",
      desc: raw.desc ? String(raw.desc) : "",
      lesson: raw.lesson || null,
      tags: tags,
      aliases: aliases,
      autolink: raw.autolink !== false,
      module: raw.module || mid || null,
      tier: raw.tier || (MODULE_FALLBACK[raw.module || mid] || {}).tier || null
    };
  }

  function fileList(idx) {
    /* index.json は「ファイル名の配列」でも「用語そのものの配列」でも
       { files: [...] } / { modules: [...] } でも受け付ける */
    if (Array.isArray(idx)) {
      if (idx.length && idx[0] && typeof idx[0] === "object") return { inline: idx };
      return { files: idx.map(String) };
    }
    if (idx && typeof idx === "object") {
      const named = idx.files || idx.sources || idx.modules;
      if (Array.isArray(named) && named.length) {
        const files = named
          .map((m) => (typeof m === "string" ? m : String((m && (m.id || m.file)) || "")))
          .filter(Boolean);
        if (files.length) return { files: files };
      }
      if (Array.isArray(idx.terms)) return { inline: idx.terms };
    }
    return null;
  }

  let _dataPromise = null;

  PBM.glossaryData = function () {
    if (_dataPromise) return _dataPromise;
    _dataPromise = (async function () {
      const out = [];
      const seen = new Map(); /* 用語名(小文字) -> entry。先勝ち */
      const modules = new Map();

      function push(entry) {
        if (!entry) return;
        const key = entry.term.toLowerCase();
        if (seen.has(key)) return;
        seen.set(key, entry);
        out.push(entry);
        if (entry.module && !modules.has(entry.module)) {
          const f = MODULE_FALLBACK[entry.module] || {};
          modules.set(entry.module, { id: entry.module, title: f.title || entry.module, tier: entry.tier || f.tier || null });
        }
      }

      const spec = fileList(await getJSON(DIR + "index.json"));
      if (spec && spec.inline) {
        spec.inline.forEach((t) => push(normalize(t, t && t.module)));
      } else {
        let guess = null;
        if (!spec || !spec.files) {
          try {
            const c = await PBM.curriculum();
            if (c && Array.isArray(c.modules) && c.modules.length)
              guess = c.modules.map(function (m) { return m && m.id; }).filter(Boolean);
          } catch (e) { /* カリキュラムが無ければ総当りに戻る */ }
        }
        const names = ((spec && spec.files) || guess || CANDIDATE_FILES)
          .map((f) => String(f).replace(/^.*\//, "").replace(/\.json$/i, ""))
          .filter(Boolean);
        const uniq = names.filter((n, i) => names.indexOf(n) === i);
        const loaded = await Promise.all(
          uniq.map(async (n) => ({ mid: n, list: await getJSON(DIR + n + ".json") }))
        );
        loaded
          .filter((r) => Array.isArray(r.list))
          .sort((a, b) => (a.mid < b.mid ? -1 : a.mid > b.mid ? 1 : 0))
          .forEach((r) => r.list.forEach((t) => push(normalize(t, r.mid))));
      }

      /* モジュール名をカリキュラムから補完（取れなくても動く） */
      try {
        if (typeof PBM.curriculum === "function" && modules.size) {
          const c = await PBM.curriculum();
          const mods = (c && (c.modules || c.levels)) || [];
          mods.forEach(function (m) {
            if (m && m.id && modules.has(m.id)) {
              const cur = modules.get(m.id);
              cur.title = m.title || cur.title;
              cur.tier = m.tier || cur.tier;
            }
          });
        }
      } catch (e) {
        /* カリキュラムが無くても用語集は動く */
      }

      return { terms: out, byTerm: seen, modules: Array.from(modules.values()) };
    })();
    return _dataPromise;
  };

  /* モジュールの表示名とティア。用語集ページだけが使う（本文ページでは呼ばない） */
  let _modPromise = null;
  PBM.glossaryModules = function () {
    if (_modPromise) return _modPromise;
    _modPromise = (async function () {
      const data = await PBM.glossaryData();
      const mods = (data.modules || []).slice();
      /* カリキュラムにモジュール一覧があればそこから取る。
         無いときだけモジュール定義を直接読む（存在しないファイルは無視される）。 */
      let known = null;
      try {
        const c = await PBM.curriculum();
        if (c && Array.isArray(c.modules) && c.modules.length) known = c.modules;
      } catch (e) { /* カリキュラムが無くても動く */ }
      if (known) {
        const byId = {};
        known.forEach(function (m) { if (m && m.id) byId[m.id] = m; });
        mods.forEach(function (m) {
          const k = byId[m.id];
          if (k) { m.title = k.title || m.title; m.tier = k.tier || m.tier; }
        });
      }
      return mods;
    })();
    return _modPromise;
  };

  /* ---------------------------------------------------------
     2. マッチ用インデックス（正規表現1本に結合）
     --------------------------------------------------------- */
  const RE_ESC = /[.*+?^${}()|[\]\\]/g;
  const ASCII_W = /[0-9A-Za-z_]/;
  const KATAKANA = /[ァ-ヿｦ-ﾟ]/;   /* ー(30FC) を含む */
  const KANJI_ONLY = /^[一-鿿々〆]+$/;
  const KANJI = /[一-鿿々〆]/;

  let _index = null;

  function buildIndex(terms) {
    const map = new Map();      /* 表記(小文字) -> entry */
    const surfaces = [];
    terms.forEach(function (t) {
      if (!t.autolink) return;
      [t.term].concat(t.aliases).forEach(function (s) {
        s = String(s || "").trim();
        if (s.length < MIN_SURFACE) return;
        const k = s.toLowerCase();
        if (map.has(k)) return;
        map.set(k, t);
        surfaces.push(s);
      });
    });
    /* 長い語を優先（スタースキーマ が スキーマ より先にマッチする） */
    surfaces.sort(function (a, b) { return b.length - a.length || (a < b ? -1 : 1); });

    const parts = surfaces.map(function (s) {
      let p = s.replace(RE_ESC, "\\$&");
      /* 英数字で終わる語は後続の英数字を拒否（ALL が ALLSELECTED に当たらない） */
      if (ASCII_W.test(s.charAt(s.length - 1))) p += "(?![0-9A-Za-z_])";
      return p;
    });
    return { map: map, re: parts.length ? new RegExp(parts.join("|"), "gi") : null, count: surfaces.length };
  }

  /* 前後の文字を見て、語の途中で切っていないか判定する。
     日本語には単語境界が無いので、カタカナ列・漢字列の途中は避ける。 */
  function boundaryOk(text, start, end, s) {
    const prev = start > 0 ? text.charAt(start - 1) : "";
    const next = end < text.length ? text.charAt(end) : "";
    const first = s.charAt(0);
    const last = s.charAt(s.length - 1);
    if (ASCII_W.test(first) && prev && ASCII_W.test(prev)) return false;
    if (ASCII_W.test(last) && next && ASCII_W.test(next)) return false;
    if (KATAKANA.test(first) && prev && KATAKANA.test(prev)) return false;
    if (KATAKANA.test(last) && next && KATAKANA.test(next)) return false;
    if (KANJI_ONLY.test(s) && ((prev && KANJI.test(prev)) || (next && KANJI.test(next)))) return false;
    return true;
  }

  /* ---------------------------------------------------------
     3. 自動リンク
     --------------------------------------------------------- */
  const SKIP_SELECTOR =
    "a, code, pre, h1, h2, h3, .gl-term, figure, .pbm-figure, script, style, .callout-title," +
    " textarea, select, option, .mermaid, .mermaid-wrap, [data-no-glossary]";

  const _counts = new Map(); /* 用語 -> このページで張ったリンク数 */
  PBM.resetGlossaryCounts = function () { _counts.clear(); };

  function makeLink(entry, surface) {
    const a = document.createElement("a");
    a.className = "gl-term";
    a.href = url("glossary.html#" + encodeURIComponent(entry.term));
    a.setAttribute("data-gl-term", entry.term);
    a.textContent = surface;
    return a;
  }

  function processTextNode(node, idx) {
    const text = node.nodeValue;
    if (!text || text.length < MIN_SURFACE) return 0;
    const re = idx.re;
    re.lastIndex = 0;
    let m, last = 0, made = 0, frag = null;
    while ((m = re.exec(text)) !== null) {
      const s = m[0];
      const start = m.index;
      const end = start + s.length;
      if (end === start) { re.lastIndex = start + 1; continue; }
      const entry = idx.map.get(s.toLowerCase());
      if (!entry || !boundaryOk(text, start, end, s)) { re.lastIndex = start + 1; continue; }
      const n = _counts.get(entry.term) || 0;
      if (n >= MAX_PER_PAGE) { re.lastIndex = end; continue; }
      _counts.set(entry.term, n + 1);
      if (!frag) frag = document.createDocumentFragment();
      if (start > last) frag.appendChild(document.createTextNode(text.slice(last, start)));
      frag.appendChild(makeLink(entry, s));
      last = end;
      made++;
      re.lastIndex = end;
    }
    if (frag) {
      if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
      node.parentNode.replaceChild(frag, node);
    }
    return made;
  }

  PBM.linkGlossary = async function (rootEl) {
    const root = rootEl || document.querySelector("#prose, .prose") || document.body;
    if (!root || !root.ownerDocument) return 0;
    let data;
    try { data = await PBM.glossaryData(); } catch (e) { return 0; }
    if (!data || !data.terms.length) return 0;
    if (!_index) _index = buildIndex(data.terms);
    if (!_index.re) return 0;

    const nodes = [];
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (!n.nodeValue || n.nodeValue.length < MIN_SURFACE) return NodeFilter.FILTER_REJECT;
        const p = n.parentElement;
        if (!p || p.closest(SKIP_SELECTOR)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    while (walker.nextNode()) nodes.push(walker.currentNode);

    let made = 0;
    for (let i = 0; i < nodes.length; i++) made += processTextNode(nodes[i], _index);

    initPopover();
    root.dispatchEvent(new CustomEvent("pbm:glossarylinked", { bubbles: true, detail: { links: made } }));
    return made;
  };

  /* ---------------------------------------------------------
     4. ポップオーバー
     --------------------------------------------------------- */
  let pop = null, popAnchor = null, hideTimer = null, showTimer = null, inited = false, escAt = 0, escAnchor = null, touchLike = false, openedAt = 0;
  const isCoarse = () => touchLike || matchMedia("(hover: none), (pointer: coarse)").matches;
  const isNarrow = () => matchMedia("(max-width: 640px)").matches;

  function ensurePop() {
    if (pop) return pop;
    pop = document.createElement("div");
    pop.className = "gl-pop";
    pop.id = "gl-pop";
    pop.setAttribute("role", "dialog");
    pop.setAttribute("aria-label", "用語の説明");
    pop.hidden = true;
    pop.addEventListener("mouseenter", function () { clearTimeout(hideTimer); });
    pop.addEventListener("mouseleave", function () { scheduleClose(260); });
    document.body.appendChild(pop);
    return pop;
  }

  function render(entry) {
    const p = ensurePop();
    const lessonLink = entry.lesson
      ? '<a class="gl-pop-link" href="' + url("lesson.html?id=" + encodeURIComponent(entry.lesson)) + '">このレッスンで学ぶ →</a>'
      : "";
    p.innerHTML =
      '<button type="button" class="gl-pop-close" aria-label="閉じる">✕</button>' +
      '<div class="gl-pop-head"><span class="gl-pop-term">' + esc(entry.term) + "</span>" +
      (entry.en ? '<span class="gl-pop-en">' + esc(entry.en) + "</span>" : "") + "</div>" +
      (entry.short ? '<p class="gl-pop-short">' + esc(entry.short) + "</p>" : "") +
      (entry.desc ? '<p class="gl-pop-desc">' + esc(entry.desc) + "</p>" : "") +
      (entry.tags.length
        ? '<div class="gl-pop-tags">' + entry.tags.map((t) => '<span class="gl-tag">' + esc(t) + "</span>").join("") + "</div>"
        : "") +
      '<div class="gl-pop-links">' +
      '<a class="gl-pop-link" href="' + url("glossary.html#" + encodeURIComponent(entry.term)) + '">用語集で詳しく見る →</a>' +
      lessonLink +
      "</div>";
    p.querySelector(".gl-pop-close").addEventListener("click", closePop);
    return p;
  }

  function place(anchor) {
    const p = pop;
    if (isNarrow()) { p.classList.add("gl-pop-sheet"); p.style.left = ""; p.style.top = ""; return; }
    p.classList.remove("gl-pop-sheet");
    p.style.left = "0px";
    p.style.top = "-9999px";
    const r = anchor.getBoundingClientRect();
    const pw = p.offsetWidth, ph = p.offsetHeight;
    const vw = document.documentElement.clientWidth, vh = document.documentElement.clientHeight;
    let left = r.left + r.width / 2 - pw / 2;
    left = Math.max(8, Math.min(left, vw - pw - 8));
    let top = r.bottom + 8;
    if (top + ph > vh - 8) top = Math.max(8, r.top - ph - 8);
    p.style.left = Math.round(left + window.scrollX) + "px";
    p.style.top = Math.round(top + window.scrollY) + "px";
  }

  async function openPop(anchor) {
    const name = anchor.getAttribute("data-gl-term");
    if (!name) return;
    let data;
    try { data = await PBM.glossaryData(); } catch (e) { return; }
    const entry = data.byTerm.get(name.toLowerCase());
    if (!entry) return;
    clearTimeout(hideTimer);
    popAnchor = anchor;
    render(entry);
    pop.hidden = false;
    pop.classList.add("open");
    openedAt = Date.now();
    place(anchor);
    anchor.setAttribute("aria-describedby", "gl-pop");
    if (typeof PBM.track === "function") PBM.track("glossary_hover", { term: entry.term });
  }

  function closePop() {
    clearTimeout(showTimer);
    clearTimeout(hideTimer);
    if (popAnchor) popAnchor.removeAttribute("aria-describedby");
    popAnchor = null;
    if (!pop) return;
    pop.classList.remove("open");
    pop.hidden = true;
  }
  function scheduleClose(ms) { clearTimeout(hideTimer); hideTimer = setTimeout(closePop, ms || 200); }

  function initPopover() {
    if (inited) return;
    inited = true;
    ensurePop();

    document.addEventListener("pointerdown", function (e) {
      touchLike = e.pointerType === "touch" || e.pointerType === "pen";
    }, true);
    document.addEventListener("touchstart", function () { touchLike = true; }, { passive: true, capture: true });

    document.addEventListener("mouseover", function (e) {
      const a = e.target.closest ? e.target.closest("a.gl-term") : null;
      if (!a) return;
      if (isCoarse()) return;
      clearTimeout(showTimer);
      clearTimeout(hideTimer);
      if (popAnchor === a && pop && !pop.hidden) { place(a); return; }
      showTimer = setTimeout(function () { openPop(a); }, 110);
    });
    document.addEventListener("mouseout", function (e) {
      if (isCoarse()) return;   /* タップ端末は互換マウスイベントで閉じない */
      const a = e.target.closest ? e.target.closest("a.gl-term") : null;
      if (!a) return;
      clearTimeout(showTimer);
      const to = e.relatedTarget;
      if (to && pop && (pop === to || pop.contains(to))) return;
      scheduleClose(240);
    });
    document.addEventListener("focusin", function (e) {
      const a = e.target.closest ? e.target.closest("a.gl-term") : null;
      if (a) {
        if (a === escAnchor && Date.now() - escAt < 600) return;  /* Escで閉じた直後は開き直さない */
        clearTimeout(hideTimer);
        openPop(a);
      } else if (pop && !pop.hidden && !pop.contains(e.target)) {
        closePop();
      }
    });
    document.addEventListener("focusout", function (e) {
      const a = e.target.closest ? e.target.closest("a.gl-term") : null;
      if (!a) return;
      const to = e.relatedTarget;
      if (to && pop && pop.contains(to)) return;
      scheduleClose(200);
    });
    document.addEventListener("click", function (e) {
      const a = e.target.closest ? e.target.closest("a.gl-term") : null;
      if (a) {
        /* タップ端末では1回目のタップで説明を出す（誤タップで離脱させない） */
        if (isCoarse() && (popAnchor !== a || Date.now() - openedAt < 500)) {
          e.preventDefault();
          openPop(a);
        }
        return;
      }
      if (pop && !pop.hidden && !pop.contains(e.target)) closePop();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && pop && !pop.hidden) {
        const a = popAnchor;
        escAt = Date.now();
        escAnchor = a;
        closePop();
        if (a && a.focus) a.focus();
      }
    });
    window.addEventListener("scroll", function () { if (popAnchor && !isNarrow()) place(popAnchor); }, { passive: true });
    window.addEventListener("resize", function () { if (popAnchor) place(popAnchor); });
  }

  PBM.glossaryPopover = { open: openPop, close: closePop, init: initPopover };

  /* 本文ページに読み込まれていれば自動でリンクする */
  function auto() {
    const root = document.querySelector("[data-glossary-root], #prose, .prose");
    if (root && !root.hasAttribute("data-no-glossary")) PBM.linkGlossary(root);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", auto);
  else setTimeout(auto, 0);
})();
