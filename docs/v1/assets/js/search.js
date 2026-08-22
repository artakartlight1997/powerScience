/* ============================================================
   PBM Search — サイト内検索（レッスン・見出し・ハンズオン・用語）
   ・インデックスは開いたときに1回だけ読み込む（初期表示を遅くしない）
   ・Ctrl/Cmd + K または「/」で開く
   ============================================================ */
(function () {
  "use strict";
  const PBM = (window.PBM = window.PBM || {});

  let index = null, loading = null, overlay = null, inputEl = null, listEl = null, metaEl = null;
  let items = [], cursor = -1, lastQuery = "";

  const TYPE_LABEL = { lesson: "レッスン", section: "セクション", lab: "ハンズオン", term: "用語" };
  const TYPE_WEIGHT = { term: 3.0, lesson: 2.6, lab: 2.2, section: 1.0 };

  /* ---------- インデックスの読み込み ---------- */
  function load() {
    if (index) return Promise.resolve(index);
    if (loading) return loading;
    loading = fetch(PBM.url("content/search.json"), { cache: "force-cache" })
      .then(function (r) { if (!r.ok) throw new Error("index " + r.status); return r.json(); })
      .then(function (j) { index = j; return j; })
      .catch(function (e) { console.error("search:", e); index = { entries: [], parents: {} }; return index; });
    return loading;
  }

  /* ---------- 検索 ---------- */
  function tokenize(q) {
    return q.trim().toLowerCase().split(/[\s　]+/).filter(Boolean).slice(0, 6);
  }

  function score(entry, parents, tokens) {
    const parent = entry.t === "section" ? (parents[entry.id] || {}) : null;
    const title = (entry.title || (parent && parent.title) || "").toLowerCase();
    const head = (entry.h || "").toLowerCase();
    const text = (entry.x || "").toLowerCase();
    const keys = (entry.k || []).join(" ").toLowerCase();
    const code = (entry.c || []).join(" ").toLowerCase();

    let total = 0;
    for (let i = 0; i < tokens.length; i++) {
      const t = tokens[i];
      let s = 0;
      if (title === t) s += 60;
      else if (title.indexOf(t) === 0) s += 34;
      else if (title.indexOf(t) >= 0) s += 20;
      if (head.indexOf(t) >= 0) s += 16;
      if (keys.indexOf(t) >= 0) s += 14;
      if (text.indexOf(t) >= 0) s += 7;
      if (code.indexOf(t) >= 0) s += 5;
      if (s === 0) return 0;                 // すべての語を含むものだけを出す
      total += s;
    }
    return total * (TYPE_WEIGHT[entry.t] || 1);
  }

  PBM.search = function (q, limit) {
    if (!index) return [];
    const tokens = tokenize(q);
    if (!tokens.length) return [];
    const parents = index.parents || {};
    const out = [];
    const entries = index.entries || [];
    for (let i = 0; i < entries.length; i++) {
      const sc = score(entries[i], parents, tokens);
      if (sc > 0) out.push({ e: entries[i], s: sc });
    }
    out.sort(function (a, b) { return b.s - a.s; });
    return out.slice(0, limit || 40);
  };

  /* ---------- 表示 ---------- */
  function highlight(text, tokens) {
    let out = PBM.esc(text || "");
    tokens.forEach(function (t) {
      if (!t) return;
      const re = new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
      out = out.replace(re, "<mark>$1</mark>");
    });
    return out;
  }

  function render(q) {
    const tokens = tokenize(q);
    if (!tokens.length) {
      listEl.innerHTML =
        '<div class="sr-empty">' +
        "<p>レッスン・見出し・ハンズオン・用語をまとめて検索します。</p>" +
        '<p class="small">例：<button class="sr-chip" data-q="CALCULATE">CALCULATE</button>' +
        '<button class="sr-chip" data-q="スタースキーマ">スタースキーマ</button>' +
        '<button class="sr-chip" data-q="ピボット解除">ピボット解除</button>' +
        '<button class="sr-chip" data-q="RLS">RLS</button>' +
        '<button class="sr-chip" data-q="増分更新">増分更新</button></p></div>';
      listEl.querySelectorAll(".sr-chip").forEach(function (b) {
        b.addEventListener("click", function () { inputEl.value = b.dataset.q; run(); });
      });
      metaEl.textContent = index ? (index.count || 0) + " 件を索引済み" : "";
      items = []; cursor = -1;
      return;
    }
    const res = PBM.search(q, 40);
    items = res;
    cursor = res.length ? 0 : -1;
    metaEl.textContent = res.length ? res.length + " 件" + (res.length === 40 ? "以上" : "") : "";
    if (!res.length) {
      listEl.innerHTML = '<div class="sr-empty"><p>「' + PBM.esc(q) + "」に一致するものが見つかりませんでした。</p>" +
        '<p class="small">別の言い方や、英語名でも試してみてください。</p></div>';
      return;
    }
    const parents = index.parents || {};
    listEl.innerHTML = res.map(function (r, i) {
      const e = r.e;
      const p = e.t === "section" ? (parents[e.id] || {}) : null;
      const title = e.title || (p && p.title) || e.id;
      const where = e.t === "section" ? (p && p.mod ? p.mod + " ／ " + title : title) : (e.mod || "");
      const head = e.h ? highlight(e.h, tokens) : "";
      return '<a class="sr-item' + (i === cursor ? " on" : "") + '" href="' + PBM.url(e.url) + '" data-i="' + i + '">' +
        '<span class="sr-kind sr-' + e.t + '">' + (TYPE_LABEL[e.t] || e.t) + "</span>" +
        '<span class="sr-body">' +
          '<span class="sr-title">' + (e.t === "section" ? head : highlight(title, tokens)) + "</span>" +
          (where ? '<span class="sr-where">' + PBM.esc(where) + "</span>" : "") +
          (e.x ? '<span class="sr-text">' + highlight(e.x, tokens) + "</span>" : "") +
        "</span></a>";
    }).join("");
    listEl.querySelectorAll(".sr-item").forEach(function (a) {
      a.addEventListener("mousemove", function () { setCursor(+a.dataset.i); });
    });
  }

  function setCursor(i) {
    if (!items.length) return;
    cursor = Math.max(0, Math.min(items.length - 1, i));
    listEl.querySelectorAll(".sr-item").forEach(function (a, n) { a.classList.toggle("on", n === cursor); });
    const el = listEl.querySelector(".sr-item.on");
    if (el) el.scrollIntoView({ block: "nearest" });
  }

  let timer = null;
  function run() {
    clearTimeout(timer);
    timer = setTimeout(function () {
      const q = inputEl.value;
      if (q === lastQuery) return;
      lastQuery = q;
      render(q);
    }, 90);
  }

  /* ---------- 開閉 ---------- */
  function build() {
    if (overlay) return;
    overlay = document.createElement("div");
    overlay.className = "sr-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "サイト内検索");
    overlay.innerHTML =
      '<div class="sr-panel">' +
        '<div class="sr-head">' +
          '<span class="sr-icon" aria-hidden="true">🔍</span>' +
          '<input type="search" id="sr-input" placeholder="レッスン・用語・DAX関数を検索" ' +
                 'autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="検索語">' +
          '<button class="sr-close" aria-label="閉じる">Esc</button>' +
        "</div>" +
        '<div class="sr-meta" id="sr-meta"></div>' +
        '<div class="sr-list" id="sr-list"></div>' +
        '<div class="sr-foot"><span>↑↓ 移動</span><span>Enter 開く</span><span>Esc 閉じる</span></div>' +
      "</div>";
    document.body.appendChild(overlay);
    inputEl = overlay.querySelector("#sr-input");
    listEl = overlay.querySelector("#sr-list");
    metaEl = overlay.querySelector("#sr-meta");

    overlay.addEventListener("click", function (e) { if (e.target === overlay) close(); });
    overlay.querySelector(".sr-close").addEventListener("click", close);
    inputEl.addEventListener("input", run);
    inputEl.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { setCursor(cursor + 1); e.preventDefault(); }
      else if (e.key === "ArrowUp") { setCursor(cursor - 1); e.preventDefault(); }
      else if (e.key === "Enter" && items[cursor]) { location.href = PBM.url(items[cursor].e.url); e.preventDefault(); }
      else if (e.key === "Escape") { close(); }
    });
  }

  function open(initial) {
    build();
    overlay.classList.add("on");
    document.body.style.overflow = "hidden";
    inputEl.value = initial || "";
    lastQuery = " ";
    metaEl.textContent = "読み込み中…";
    listEl.innerHTML = '<div class="spinner"></div>';
    load().then(function () { render(inputEl.value); });
    setTimeout(function () { inputEl.focus(); }, 30);
    PBM.track("search_open", {});
  }
  function close() {
    if (!overlay) return;
    overlay.classList.remove("on");
    document.body.style.overflow = "";
  }
  PBM.openSearch = open;
  PBM.closeSearch = close;

  /* ---------- ショートカット ---------- */
  addEventListener("keydown", function (e) {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test((e.target.tagName || "")) || e.target.isContentEditable;
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { open(); e.preventDefault(); return; }
    if (e.key === "/" && !typing) { open(); e.preventDefault(); }
  });

  /* ---------- ヘッダーにボタンを追加 ---------- */
  addEventListener("DOMContentLoaded", function () {
    const header = document.querySelector(".site-header .wrap");
    if (!header || header.querySelector("#pbm-search")) return;
    const btn = document.createElement("button");
    btn.id = "pbm-search";
    btn.className = "icon-btn sr-trigger";
    btn.type = "button";
    btn.setAttribute("aria-label", "サイト内を検索");
    btn.innerHTML = '<span aria-hidden="true">🔍</span><span class="sr-kbd">Ctrl K</span>';
    btn.addEventListener("click", function () { open(); });
    const theme = header.querySelector("#pbm-theme");
    if (theme) header.insertBefore(btn, theme); else header.appendChild(btn);
  });
})();
