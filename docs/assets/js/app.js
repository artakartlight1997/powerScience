/* ============================================================
   たい焼き屋のデータ入門 — 共通の処理
   （ヘッダー / 配色の切り替え / 進み具合の記録 / データ取得）
   ============================================================ */
(function () {
  "use strict";
  var TD = (window.TD = window.TD || {});

  /* 図とMarkdownの描画エンジンは前のバージョンから引き継いだもので、
     PBM という名前で共通の道具を探す。必要なぶんだけ用意しておく。 */
  var PBM = (window.PBM = window.PBM || {});
  PBM.esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  TD.esc = PBM.esc;

  /* 置き場所がどこでも動くように、今いる階層からの相対で組み立てる */
  var BASE = (function () {
    var p = location.pathname;
    return p.slice(0, p.lastIndexOf("/") + 1);
  })();
  TD.url = function (rel) { return BASE + rel; };
  PBM.url = TD.url;

  /* ---------- 配色 ---------- */
  var THEME = "td.theme";
  TD.applyTheme = function (t) {
    if (t === "light" || t === "dark") {
      document.documentElement.setAttribute("data-theme", t);
      try { localStorage.setItem(THEME, t); } catch (e) {}
    } else {
      document.documentElement.removeAttribute("data-theme");
      try { localStorage.removeItem(THEME); } catch (e) {}
    }
  };
  try { TD.applyTheme(localStorage.getItem(THEME)); } catch (e) {}

  /* ---------- 読み終わったレッスンの記録 ---------- */
  var DONE = "td.done";
  function read() {
    try { return JSON.parse(localStorage.getItem(DONE) || "{}") || {}; }
    catch (e) { return {}; }
  }
  TD.doneMap = read;
  TD.isDone = function (id) { return !!read()[id]; };
  TD.setDone = function (id, on) {
    var d = read();
    if (on) d[id] = Date.now(); else delete d[id];
    try { localStorage.setItem(DONE, JSON.stringify(d)); } catch (e) {}
    return on;
  };

  /* ---------- コース定義 ---------- */
  var _course = null;
  TD.course = function () {
    if (_course) return _course;
    _course = fetch(TD.url("content/course.json"), { cache: "no-cache" })
      .then(function (r) {
        if (!r.ok) throw new Error("course.json が読めません (" + r.status + ")");
        return r.json();
      })
      .then(function (c) {
        /* レッスンを1列に並べ、前後をたどれるようにしておく */
        c.flat = [];
        (c.chapters || []).forEach(function (ch, ci) {
          (ch.lessons || []).forEach(function (l, li) {
            c.flat.push({
              id: l.id, title: l.title, q: l.q, gain: l.gain,
              chapter: ch.title, chapterId: ch.id, chapterNo: ci + 1, no: li + 1
            });
          });
        });
        c.byId = {};
        c.flat.forEach(function (l, i) { l.index = i; c.byId[l.id] = l; });
        return c;
      });
    return _course;
  };

  /* ---------- ヘッダー ---------- */
  TD.header = function (title) {
    var h = document.createElement("header");
    h.className = "site-header";
    h.innerHTML =
      '<div class="wrap">' +
        '<a class="brand" href="' + TD.url("index.html") + '">' +
          '<span class="brand-mark">🐟</span><span>' + (title || "たい焼き屋のデータ入門") + "</span>" +
        "</a>" +
        '<span class="spacer"></span>' +
        '<button class="icon-btn" id="td-theme" aria-label="明るさを切り替える" title="明るさを切り替える">◐</button>' +
      "</div>";
    document.body.prepend(h);
    h.querySelector("#td-theme").addEventListener("click", function () {
      var now = document.documentElement.getAttribute("data-theme");
      TD.applyTheme(now === "dark" ? "light" : "dark");
    });
  };

  TD.footer = function () {
    var f = document.createElement("footer");
    f.className = "site-footer";
    f.innerHTML = '<div class="wrap">' +
      "<p>この教材は Microsoft 非公式です。Power BI は Microsoft Corporation の商標です。</p>" +
      '<p><a href="' + TD.url("v1/index.html") + '">前のバージョン（上級者向け・専門用語あり）はこちら</a></p>' +
      "</div>";
    document.body.appendChild(f);
  };
})();
