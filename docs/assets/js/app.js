/* ============================================================
   PBM — 共通ライブラリ（ヘッダー描画 / テーマ / 進捗 / データ取得）
   ============================================================ */
(function () {
  "use strict";

  const CFG = window.PBM_CONFIG || {};
  const PBM = (window.PBM = window.PBM || {});

  /* ---------- パス解決（/docs 直下でもサブパス公開でも動くように） ---------- */
  const BASE = (function () {
    const p = location.pathname;
    const i = p.lastIndexOf("/");
    return p.slice(0, i + 1);
  })();
  PBM.url = (rel) => BASE + rel;

  /* ---------- テーマ ---------- */
  const THEME_KEY = "pbm.theme";
  PBM.applyTheme = function (t) {
    if (t === "light" || t === "dark") {
      document.documentElement.setAttribute("data-theme", t);
      localStorage.setItem(THEME_KEY, t);
    } else {
      document.documentElement.removeAttribute("data-theme");
      localStorage.removeItem(THEME_KEY);
    }
  };
  PBM.currentTheme = function () {
    const stored = localStorage.getItem(THEME_KEY);
    if (stored) return stored;
    return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };
  PBM.toggleTheme = function () {
    PBM.applyTheme(PBM.currentTheme() === "dark" ? "light" : "dark");
    document.dispatchEvent(new CustomEvent("pbm:themechange"));
  };
  (function initTheme() {
    const stored = localStorage.getItem(THEME_KEY);
    if (stored) document.documentElement.setAttribute("data-theme", stored);
  })();

  /* ---------- 進捗ストア（localStorage） ----------
     形: { lessons: {L001:{done:true, at:ts}}, quizzes:{L001:{best:80,at:ts,tries:2}},
           labs:{LAB01:{done:true}}, exams:[{score,at,byArea}] }                       */
  const PKEY = "pbm.progress.v1";
  function loadProgress() {
    try { return JSON.parse(localStorage.getItem(PKEY)) || {}; } catch (e) { return {}; }
  }
  function saveProgress(p) { localStorage.setItem(PKEY, JSON.stringify(p)); }

  PBM.progress = {
    all: loadProgress,
    reset() { localStorage.removeItem(PKEY); },
    isLessonDone(id) { const p = loadProgress(); return !!(p.lessons && p.lessons[id] && p.lessons[id].done); },
    setLessonDone(id, done) {
      const p = loadProgress(); p.lessons = p.lessons || {};
      p.lessons[id] = { done: !!done, at: Date.now() };
      saveProgress(p);
      PBM.track(done ? "lesson_complete" : "lesson_uncomplete", { lesson: id });
      return p;
    },
    isLabDone(id) { const p = loadProgress(); return !!(p.labs && p.labs[id] && p.labs[id].done); },
    setLabDone(id, done) {
      const p = loadProgress(); p.labs = p.labs || {};
      p.labs[id] = { done: !!done, at: Date.now() };
      saveProgress(p);
      if (done) PBM.track("lab_complete", { lab: id });
    },
    quizResult(id) { const p = loadProgress(); return (p.quizzes && p.quizzes[id]) || null; },
    setQuizResult(id, score, total) {
      const p = loadProgress(); p.quizzes = p.quizzes || {};
      const prev = p.quizzes[id] || { best: 0, tries: 0 };
      const pct = Math.round((score / total) * 100);
      p.quizzes[id] = { best: Math.max(prev.best || 0, pct), last: pct, tries: (prev.tries || 0) + 1, at: Date.now() };
      saveProgress(p);
      PBM.track("quiz_result", { quiz: id, score: pct, total: total });
      return p.quizzes[id];
    },
    addExam(rec) {
      const p = loadProgress(); p.exams = p.exams || [];
      p.exams.push(Object.assign({ at: Date.now() }, rec));
      if (p.exams.length > 30) p.exams = p.exams.slice(-30);
      saveProgress(p);
      PBM.track("exam_result", { score: rec.score });
    },
    exams() { return loadProgress().exams || []; },
    export() { return JSON.stringify(loadProgress(), null, 2); },
    import(json) {
      const obj = JSON.parse(json);
      if (typeof obj !== "object" || obj === null) throw new Error("形式が不正です");
      saveProgress(obj);
    }
  };

  /* ---------- カリキュラム取得（キャッシュ付き） ---------- */
  let _curriculum = null;
  PBM.curriculum = async function () {
    if (_curriculum) return _curriculum;
    const res = await fetch(PBM.url("content/curriculum.json"), { cache: "no-cache" });
    if (!res.ok) throw new Error("カリキュラムを読み込めませんでした (" + res.status + ")");
    _curriculum = await res.json();
    _curriculum.lessonById = Object.fromEntries(_curriculum.lessons.map((l) => [l.id, l]));
    _curriculum.levelById = Object.fromEntries(_curriculum.levels.map((l) => [l.id, l]));
    _curriculum.labById = Object.fromEntries(_curriculum.labs.map((l) => [l.id, l]));
    return _curriculum;
  };
  PBM.lessonsOfLevel = (c, levelId) => c.lessons.filter((l) => l.level === levelId);

  /* ---------- 進捗集計 ---------- */
  PBM.stats = function (c) {
    const p = loadProgress();
    const done = c.lessons.filter((l) => p.lessons && p.lessons[l.id] && p.lessons[l.id].done).length;
    const quizzes = Object.values(p.quizzes || {});
    const passed = quizzes.filter((q) => q.best >= (CFG.quizPassLine || 80)).length;
    const labs = c.labs.filter((l) => p.labs && p.labs[l.id] && p.labs[l.id].done).length;
    const minutes = c.lessons.reduce((s, l) => s + (p.lessons && p.lessons[l.id] && p.lessons[l.id].done ? l.minutes : 0), 0);
    return {
      lessonsDone: done, lessonsTotal: c.lessons.length,
      pct: c.lessons.length ? Math.round((done / c.lessons.length) * 100) : 0,
      quizPassed: passed, quizTaken: quizzes.length,
      labsDone: labs, labsTotal: c.labs.length,
      minutes: minutes
    };
  };
  PBM.levelStats = function (c, levelId) {
    const p = loadProgress();
    const ls = PBM.lessonsOfLevel(c, levelId);
    const done = ls.filter((l) => p.lessons && p.lessons[l.id] && p.lessons[l.id].done).length;
    return { done, total: ls.length, pct: ls.length ? Math.round((done / ls.length) * 100) : 0 };
  };

  /* ---------- 次にやるべきレッスン ---------- */
  PBM.nextLesson = function (c) {
    const p = loadProgress();
    return c.lessons.find((l) => !(p.lessons && p.lessons[l.id] && p.lessons[l.id].done)) || null;
  };

  /* ---------- 共通ヘッダー / フッター ---------- */
  const NAV = [
    ["index.html", "ホーム"],
    ["roadmap.html", "ロードマップ"],
    ["labs.html", "ハンズオン"],
    ["quizzes.html", "クイズ"],
    ["exam.html", "模擬試験"],
    ["glossary.html", "用語集"],
    ["progress.html", "学習記録"]
  ];
  PBM.renderChrome = function () {
    const here = location.pathname.split("/").pop() || "index.html";
    const header = document.createElement("header");
    header.className = "site-header";
    header.innerHTML =
      '<div class="wrap">' +
        '<a class="brand" href="' + PBM.url("index.html") + '">' +
          '<span class="brand-mark">P</span><span>' + (CFG.siteName || "Power BI Mastery") + "</span>" +
        "</a>" +
        '<nav class="nav">' +
          NAV.map(([h, t]) => '<a href="' + PBM.url(h) + '"' + (h === here ? ' aria-current="page"' : "") + ">" + t + "</a>").join("") +
        "</nav>" +
        '<span class="spacer"></span>' +
        '<button class="icon-btn" id="pbm-theme" aria-label="配色を切り替え" title="配色を切り替え">◐</button>' +
        '<button class="icon-btn" id="pbm-menu" aria-label="メニュー" aria-expanded="false" style="display:none">☰</button>' +
      "</div>" +
      '<div class="drawer" id="pbm-drawer">' +
        NAV.map(([h, t]) => '<a href="' + PBM.url(h) + '">' + t + "</a>").join("") +
      "</div>";
    document.body.insertBefore(header, document.body.firstChild);

    const mq = matchMedia("(max-width: 859px)");
    const menuBtn = header.querySelector("#pbm-menu");
    const applyMq = () => { menuBtn.style.display = mq.matches ? "grid" : "none"; };
    applyMq(); mq.addEventListener("change", applyMq);

    menuBtn.addEventListener("click", () => {
      const d = header.querySelector("#pbm-drawer");
      const open = d.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", String(open));
    });
    header.querySelector("#pbm-theme").addEventListener("click", PBM.toggleTheme);

    const footer = document.createElement("footer");
    footer.className = "site-footer";
    footer.innerHTML =
      '<div class="wrap">' +
        "<p>" + (CFG.siteName || "Power BI Mastery") +
        " — PL-300 合格までの学習ロードマップ。学習進捗はお使いのブラウザ内(localStorage)に保存されます。</p>" +
        '<p class="small">Power BI は Microsoft Corporation の商標です。本サイトは非公式の学習教材です。' +
        ' 内容は学習用に要約しています。仕様は変わるため、受験前に必ず ' +
        '<a href="https://learn.microsoft.com/ja-jp/credentials/certifications/exams/pl-300/" target="_blank" rel="noopener">Microsoft Learn の公式ページ</a>' +
        "で最新の出題範囲をご確認ください。</p>" +
      "</div>";
    document.body.appendChild(footer);
  };

  /* ---------- 小物 ---------- */
  PBM.esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  PBM.qs = (k, d) => new URLSearchParams(location.search).get(k) || d || null;
  PBM.fmtMin = (m) => (m >= 60 ? Math.floor(m / 60) + "時間" + (m % 60 ? (m % 60) + "分" : "") : m + "分");
  PBM.shuffle = function (arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  };
})();
