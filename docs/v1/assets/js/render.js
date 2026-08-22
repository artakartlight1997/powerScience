/* ============================================================
   PBM Render v2 — Markdown / 図解ブロック / コードハイライト
   Mermaid は使用しません。図は figure.js が描画します。
   ============================================================ */
(function () {
  "use strict";
  const PBM = (window.PBM = window.PBM || {});

  /* ---------- DAX / M / SQL / Python 用の軽量シンタックスハイライト ---------- */
  const DAX_FUNCS = ("CALCULATE|CALCULATETABLE|SUM|SUMX|AVERAGE|AVERAGEX|MIN|MINX|MAX|MAXX|COUNT|COUNTA|COUNTAX|COUNTX|" +
    "COUNTROWS|COUNTBLANK|DISTINCTCOUNT|DIVIDE|IF|IFERROR|SWITCH|AND|OR|NOT|BLANK|ISBLANK|ISERROR|ISFILTERED|ISCROSSFILTERED|ISINSCOPE|" +
    "HASONEVALUE|HASONEFILTER|SELECTEDVALUE|VALUES|DISTINCT|ALL|ALLEXCEPT|ALLSELECTED|ALLNOBLANKROW|REMOVEFILTERS|KEEPFILTERS|" +
    "FILTER|RELATED|RELATEDTABLE|USERELATIONSHIP|CROSSFILTER|EARLIER|EARLIEST|RANKX|TOPN|ADDCOLUMNS|SUMMARIZE|SUMMARIZECOLUMNS|" +
    "GROUPBY|CURRENTGROUP|GENERATE|GENERATEALL|ROW|SELECTCOLUMNS|UNION|INTERSECT|EXCEPT|NATURALINNERJOIN|NATURALLEFTOUTERJOIN|" +
    "TREATAS|CONCATENATEX|PRODUCTX|DATATABLE|" +
    "DATESYTD|TOTALYTD|TOTALQTD|TOTALMTD|DATESMTD|DATESQTD|SAMEPERIODLASTYEAR|PARALLELPERIOD|DATEADD|DATESINPERIOD|" +
    "DATESBETWEEN|FIRSTDATE|LASTDATE|FIRSTNONBLANK|LASTNONBLANK|ENDOFMONTH|STARTOFMONTH|ENDOFYEAR|STARTOFYEAR|" +
    "CALENDAR|CALENDARAUTO|DATE|DATEDIFF|DATEVALUE|YEAR|MONTH|DAY|HOUR|MINUTE|SECOND|WEEKDAY|" +
    "WEEKNUM|EOMONTH|EDATE|TODAY|NOW|UTCNOW|FORMAT|CONCATENATE|LEFT|RIGHT|MID|LEN|TRIM|UPPER|LOWER|SUBSTITUTE|REPLACE|SEARCH|FIND|" +
    "USERPRINCIPALNAME|USERNAME|CUSTOMDATA|LOOKUPVALUE|CONTAINS|CONTAINSSTRING|CONTAINSROW|PATH|PATHCONTAINS|PATHITEM|PATHLENGTH|" +
    "ROUND|ROUNDUP|ROUNDDOWN|MROUND|CEILING|FLOOR|TRUNC|INT|ABS|SIGN|POWER|SQRT|EXP|LN|LOG|RAND|RANDBETWEEN|" +
    "VALUE|CURRENCY|CONVERT|MEDIAN|MEDIANX|PERCENTILEX|STDEV|GEOMEAN|GEOMEANX|SAMPLE|WINDOW|OFFSET|INDEX|ORDERBY|PARTITIONBY|MATCHBY").split("|");
  const DAX_KEYWORDS = ["VAR", "RETURN", "EVALUATE", "DEFINE", "MEASURE", "COLUMN", "TABLE", "ORDER", "BY", "START", "AT", "ASC", "DESC", "TRUE", "FALSE", "IN", "NOT"];
  const M_KEYWORDS = ["let", "in", "each", "if", "then", "else", "type", "meta", "try", "otherwise", "as", "is", "error", "null", "true", "false", "and", "or", "not", "section", "shared"];
  const SQL_KEYWORDS = ["SELECT", "FROM", "WHERE", "GROUP", "BY", "ORDER", "HAVING", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "FULL", "ON", "AS", "AND", "OR", "NOT", "IN", "EXISTS", "CASE", "WHEN", "THEN", "ELSE", "END", "WITH", "UNION", "ALL", "DISTINCT", "INSERT", "UPDATE", "DELETE", "CREATE", "TABLE", "VIEW", "INDEX", "NULL", "IS", "BETWEEN", "LIKE", "LIMIT", "TOP", "OVER", "PARTITION"];
  const PY_KEYWORDS = ["import", "from", "as", "def", "class", "return", "if", "elif", "else", "for", "while", "in", "not", "and", "or", "is", "None", "True", "False", "try", "except", "finally", "with", "lambda", "yield", "pass", "break", "continue", "print"];

  const PH = "\u0001"; // 退避用プレースホルダ（本文には現れない制御文字）

  function highlight(code, lang) {
    const esc = PBM.esc(code);
    const l = (lang || "").toLowerCase();
    const known = { dax: 1, m: 1, powerquery: 1, sql: 1, python: 1, py: 1 };
    if (!known[l]) return esc;

    const parts = [];
    // 文字列とコメントを一旦退避（誤ハイライト防止）
    let s = esc.replace(/(&quot;[^\n]*?&quot;|\/\/[^\n]*|--[^\n]*|\/\*[\s\S]*?\*\/)/g, function (m) {
      const isComment = /^(\/\/|\/\*|--)/.test(m);
      parts.push('<span class="' + (isComment ? "tok-c" : "tok-s") + '">' + m + "</span>");
      return PH + (parts.length - 1) + PH;
    });

    if (l === "dax") {
      s = s.replace(new RegExp("\\b(" + DAX_FUNCS.join("|") + ")\\b(?=\\s*\\()", "gi"), '<span class="tok-f">$1</span>');
      s = s.replace(new RegExp("\\b(" + DAX_KEYWORDS.join("|") + ")\\b", "g"), '<span class="tok-k">$1</span>');
      s = s.replace(/(\[[^\]\n]+\])/g, '<span class="tok-col">$1</span>');
      s = s.replace(/('[^'\n]+')/g, '<span class="tok-t">$1</span>');
    } else if (l === "sql") {
      s = s.replace(new RegExp("\\b(" + SQL_KEYWORDS.join("|") + ")\\b", "gi"), '<span class="tok-k">$1</span>');
    } else if (l === "python" || l === "py") {
      s = s.replace(new RegExp("\\b(" + PY_KEYWORDS.join("|") + ")\\b", "g"), '<span class="tok-k">$1</span>');
    } else {
      s = s.replace(new RegExp("\\b(" + M_KEYWORDS.join("|") + ")\\b", "g"), '<span class="tok-k">$1</span>');
      s = s.replace(/\b(Table|List|Text|Number|Date|DateTime|DateTimeZone|Time|Record|Value|Excel|Csv|Json|Web|Sql|Odbc|Folder|SharePoint|Splitter|Replacer|Combiner|Comparer|Duration|Character|Binary|Lines|Function|Type|Uri|Expression)\.[A-Za-z]+/g,
        '<span class="tok-f">$&</span>');
    }
    s = s.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="tok-n">$1</span>');
    return s.replace(new RegExp(PH + "(?:<[^>]*>)*?(\\d+)(?:<[^>]*>)*?" + PH, "g"), function (m, i) { return parts[+i]; });
  }
  PBM.highlight = highlight;

  /* ---------- コールアウト ---------- */
  const CALLOUTS = {
    NOTE: { cls: "",     icon: "\u{1F4CC}", label: "ポイント" },
    TIP:  { cls: "tip",  icon: "\u{1F4A1}", label: "実務のコツ" },
    WARN: { cls: "warn", icon: "\u{26A0}",  label: "注意" },
    TRAP: { cls: "trap", icon: "\u{1F6A7}", label: "つまずきポイント" },
    EXAM: { cls: "exam", icon: "\u{1F3AF}", label: "PL-300で問われる" },
    DS:   { cls: "ds",   icon: "\u{1F9EA}", label: "データサイエンス視点" }
  };

  /* 本文の前処理。
     1) CommonMark の強調は、閉じ「**」の直前が句読点だと成立しない。
        日本語では 「**〜する」**です。 が普通なので自前で <strong> に変換する。
     2) [[用語]] を用語集へのリンクにする。
     どちらも **コードブロックと図(figure)の中身には絶対に適用しない**。
     図のJSONには "rows":[[...]] のような [[ ]] が現れるため、
     保護せずに置換するとJSONが壊れる。                                   */
  function preprocess(md) {
    const blocks = [], inlines = [];
    let s = md.replace(/```[\s\S]*?```/g, function (m) { blocks.push(m); return PH + "B" + (blocks.length - 1) + PH; });
    s = s.replace(/`[^`\n]*`/g, function (m) { inlines.push(m); return PH + "I" + (inlines.length - 1) + PH; });

    s = s.replace(/\*\*(?!\s)((?:[^*\n]|\*(?!\*))+?)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/\[\[([^\]\n|]{1,40})\]\]/g, function (m, term) {
      return '<a class="gl-term gl-explicit" href="' + PBM.url("glossary.html#" + encodeURIComponent(term)) +
             '" data-term="' + PBM.esc(term) + '">' + PBM.esc(term) + "</a>";
    });

    s = s.replace(new RegExp(PH + "I(\\d+)" + PH, "g"), function (m, i) { return inlines[+i]; });
    return s.replace(new RegExp(PH + "B(\\d+)" + PH, "g"), function (m, i) { return blocks[+i]; });
  }

  /* ---------- Markdown → HTML ---------- */
  PBM.markdown = function (md) {
    if (!window.marked) return "<pre>" + PBM.esc(md) + "</pre>";
    md = preprocess(md);
    const renderer = new marked.Renderer();
    let figNo = 0, hNo = 0;

    renderer.code = function (code, info) {
      const lang = (info || "").split(/\s+/)[0];

      // 図解ブロック：figure.js が描画する
      if (lang === "figure") {
        figNo++;
        let cfg = null, err = null;
        try { cfg = JSON.parse(code); } catch (e) { err = String(e.message || e); }
        if (err) {
          return '<div class="pbm-figure pbm-figure-error"><strong>図の設定に誤りがあります</strong>' +
                 "<p>" + PBM.esc(err) + '</p><pre>' + PBM.esc(code) + "</pre></div>";
        }
        cfg.__n = figNo;
        return '<div class="pbm-figure" data-figure="' + PBM.esc(JSON.stringify(cfg)) + '"></div>';
      }

      // 万一 mermaid が残っていたら、静かに落とさず明示的に知らせる
      if (lang === "mermaid") {
        return '<div class="pbm-figure pbm-figure-error"><strong>Mermaid は廃止されました</strong>' +
               '<p>この図は figure ブロックに書き換えてください（AUTHORING_SPEC.md 5章）。</p>' +
               "<pre>" + PBM.esc(code) + "</pre></div>";
      }

      return '<pre><code class="language-' + PBM.esc(lang || "text") + '">' + highlight(code, lang) + "</code></pre>";
    };

    renderer.table = function (header, body) {
      return '<div class="table-scroll"><table><thead>' + header + "</thead><tbody>" + body + "</tbody></table></div>";
    };

    renderer.blockquote = function (quote) {
      const m = quote.match(/^\s*<p>\s*\[!(NOTE|TIP|WARN|TRAP|EXAM|DS)\]\s*(?:<br\s*\/?>)?\s*/i);
      if (!m) return "<blockquote>" + quote + "</blockquote>";
      const t = CALLOUTS[m[1].toUpperCase()];
      const rest = quote.replace(m[0], "<p>");
      return '<div class="callout ' + t.cls + '"><div class="callout-title">' +
             '<span class="callout-icon">' + t.icon + "</span>" + t.label + "</div>" + rest + "</div>";
    };

    renderer.heading = function (text, level) {
      const id = "h" + (++hNo);
      return "<h" + level + ' id="' + id + '">' + text + "</h" + level + ">";
    };

    marked.setOptions({ renderer: renderer, breaks: false, gfm: true, headerIds: false, mangle: false });
    return marked.parse(md);
  };

  /* ---------- 描画後の共通処理 ----------
     順序が重要：
       1) 用語の自動リンク … このとき図はまだ空の <div data-figure> なので、
          図やウィジェットの内部テキスト（DAXコードなど）にリンクが入らない
       2) 図とウィジェットの描画
       3) コードのコピーボタン
     いずれも未読み込みなら黙ってスキップする（本文は必ず表示される）。 */
  PBM.enhance = async function (root) {
    if (!root) return;
    try { if (PBM.linkGlossary) await PBM.linkGlossary(root); } catch (e) { console.error("glossary:", e); }
    try { if (PBM.renderFigures) PBM.renderFigures(root); } catch (e) { console.error("figure:", e); }
    try { addCodeCopyButtons(root); } catch (e) { /* noop */ }
  };

  /* コードブロックにコピーボタンを付ける */
  function addCodeCopyButtons(root) {
    root.querySelectorAll("pre > code").forEach(function (code) {
      const pre = code.parentElement;
      if (pre.querySelector(".code-copy")) return;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "code-copy";
      btn.textContent = "コピー";
      btn.setAttribute("aria-label", "コードをコピー");
      btn.addEventListener("click", function () {
        navigator.clipboard.writeText(code.textContent).then(function () {
          btn.textContent = "コピーしました";
          setTimeout(function () { btn.textContent = "コピー"; }, 1600);
        }).catch(function () { btn.textContent = "コピーできません"; });
      });
      pre.appendChild(btn);
      pre.classList.add("has-copy");
    });
  }

  /* テーマ切替時に図を描き直す */
  document.addEventListener("pbm:themechange", function () {
    document.querySelectorAll(".pbm-figure[data-rendered]").forEach(function (el) {
      el.removeAttribute("data-rendered");
    });
    if (PBM.renderFigures) PBM.renderFigures(document);
  });

  /* ---------- 目次生成 ---------- */
  PBM.buildToc = function (proseEl, tocEl) {
    const hs = proseEl.querySelectorAll("h2, h3");
    if (!hs.length) { tocEl.innerHTML = ""; return; }
    tocEl.innerHTML = '<div class="toc-head">目次</div>' +
      Array.prototype.map.call(hs, function (h) {
        return '<a href="#' + h.id + '" class="' + h.tagName.toLowerCase() + '">' + PBM.esc(h.textContent) + "</a>";
      }).join("");
    const links = Array.prototype.slice.call(tocEl.querySelectorAll("a"));
    const obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.classList.toggle("active", a.getAttribute("href") === "#" + e.target.id); });
      });
    }, { rootMargin: "-70px 0px -75% 0px" });
    Array.prototype.forEach.call(hs, function (h) { obs.observe(h); });
  };

  /* ---------- 読了時間の推定 ---------- */
  PBM.readingTime = function (md) {
    const chars = md.replace(/```[\s\S]*?```/g, "").length;
    return Math.max(1, Math.round(chars / 600)); // 日本語は毎分600字程度
  };
})();
