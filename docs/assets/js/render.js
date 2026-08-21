/* ============================================================
   PBM Render — Markdown / Mermaid図解 / コードハイライト の共通処理
   ============================================================ */
(function () {
  "use strict";
  const PBM = (window.PBM = window.PBM || {});

  /* ---------- DAX / M 用の軽量シンタックスハイライト ---------- */
  const DAX_FUNCS = ("CALCULATE|CALCULATETABLE|SUM|SUMX|AVERAGE|AVERAGEX|MIN|MINX|MAX|MAXX|COUNT|COUNTA|COUNTAX|COUNTX|" +
    "COUNTROWS|DISTINCTCOUNT|DIVIDE|IF|IFERROR|SWITCH|AND|OR|NOT|BLANK|ISBLANK|ISFILTERED|ISCROSSFILTERED|ISINSCOPE|" +
    "HASONEVALUE|SELECTEDVALUE|VALUES|DISTINCT|ALL|ALLEXCEPT|ALLSELECTED|ALLNOBLANKROW|REMOVEFILTERS|KEEPFILTERS|" +
    "FILTER|RELATED|RELATEDTABLE|USERELATIONSHIP|CROSSFILTER|EARLIER|RANKX|TOPN|ADDCOLUMNS|SUMMARIZE|SUMMARIZECOLUMNS|" +
    "GENERATE|GENERATEALL|ROW|SELECTCOLUMNS|UNION|INTERSECT|EXCEPT|NATURALINNERJOIN|TREATAS|CONCATENATEX|" +
    "DATESYTD|TOTALYTD|TOTALQTD|TOTALMTD|DATESMTD|DATESQTD|SAMEPERIODLASTYEAR|PARALLELPERIOD|DATEADD|DATESINPERIOD|" +
    "DATESBETWEEN|FIRSTDATE|LASTDATE|ENDOFMONTH|STARTOFMONTH|CALENDAR|CALENDARAUTO|DATE|YEAR|MONTH|DAY|WEEKDAY|" +
    "WEEKNUM|EOMONTH|TODAY|NOW|FORMAT|CONCATENATE|LEFT|RIGHT|MID|LEN|TRIM|UPPER|LOWER|SUBSTITUTE|SEARCH|FIND|" +
    "USERPRINCIPALNAME|USERNAME|LOOKUPVALUE|CONTAINS|CONTAINSSTRING|PATH|PATHCONTAINS|ROUND|ROUNDUP|ROUNDDOWN|" +
    "INT|ABS|SIGN|POWER|SQRT|RANDBETWEEN|VALUE|CURRENCY|CONVERT").split("|");
  const DAX_KEYWORDS = ["VAR", "RETURN", "EVALUATE", "DEFINE", "MEASURE", "ORDER", "BY", "ASC", "DESC", "TRUE", "FALSE", "IN"];
  const M_KEYWORDS = ["let", "in", "each", "if", "then", "else", "type", "meta", "try", "otherwise", "as", "is", "error", "null", "true", "false", "and", "or", "not"];

  const PH = "\u0001"; // 退避用プレースホルダ

  function highlight(code, lang) {
    const esc = PBM.esc(code);
    const l = (lang || "").toLowerCase();
    if (l !== "dax" && l !== "m" && l !== "powerquery") return esc;

    const parts = [];
    // 文字列とコメントを一旦退避（誤ハイライト防止）
    let s = esc.replace(/(&quot;[^\n]*?&quot;|\/\/[^\n]*|\/\*[\s\S]*?\*\/)/g, function (m) {
      const cls = (m.indexOf("//") === 0 || m.indexOf("/*") === 0) ? "tok-c" : "tok-s";
      parts.push('<span class="' + cls + '">' + m + "</span>");
      return PH + (parts.length - 1) + PH;
    });

    if (l === "dax") {
      s = s.replace(new RegExp("\\b(" + DAX_FUNCS.join("|") + ")\\b(?=\\s*\\()", "gi"), '<span class="tok-f">$1</span>');
      s = s.replace(new RegExp("\\b(" + DAX_KEYWORDS.join("|") + ")\\b", "g"), '<span class="tok-k">$1</span>');
      s = s.replace(/(\[[^\]\n]+\])/g, '<span class="tok-col">$1</span>');
      s = s.replace(/('[^'\n]+')/g, '<span class="tok-t">$1</span>');
    } else {
      s = s.replace(new RegExp("\\b(" + M_KEYWORDS.join("|") + ")\\b", "g"), '<span class="tok-k">$1</span>');
      s = s.replace(/\b(Table|List|Text|Number|Date|DateTime|Record|Value|Excel|Csv|Json|Web|Sql|Splitter|Replacer|Duration|Character)\.[A-Za-z]+/g,
        '<span class="tok-f">$&</span>');
    }
    s = s.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="tok-n">$1</span>');
    return s.replace(new RegExp(PH + "(?:<[^>]*>)*?(\\d+)(?:<[^>]*>)*?" + PH, "g"), function (m, i) { return parts[+i]; });
  }
  PBM.highlight = highlight;

  /* ---------- Markdown → HTML ---------- */
  const CALLOUTS = {
    NOTE: { cls: "",     icon: "\u{1F4CC}",     label: "ポイント" },
    TIP:  { cls: "tip",  icon: "\u{1F4A1}",     label: "コツ" },
    WARN: { cls: "warn", icon: "⚠️", label: "注意" },
    TRAP: { cls: "trap", icon: "\u{1F6A7}",     label: "つまずきポイント" },
    EXAM: { cls: "exam", icon: "\u{1F3AF}",     label: "試験に出る" }
  };

  PBM.markdown = function (md) {
    if (!window.marked) return "<pre>" + PBM.esc(md) + "</pre>";
    const renderer = new marked.Renderer();
    let figNo = 0, hNo = 0;

    renderer.code = function (code, info) {
      const lang = (info || "").split(/\s+/)[0];
      if (lang === "mermaid") {
        figNo++;
        const cap = (info || "").slice("mermaid".length).trim();
        return '<figure class="mermaid-wrap"><div class="mermaid">' + PBM.esc(code) + "</div>" +
          '<figcaption class="cap">図' + figNo + (cap ? "：" + PBM.esc(cap) : "") + "</figcaption></figure>";
      }
      return '<pre><code class="language-' + PBM.esc(lang || "text") + '">' + highlight(code, lang) + "</code></pre>";
    };
    renderer.table = function (header, body) {
      return '<div class="table-scroll"><table><thead>' + header + "</thead><tbody>" + body + "</tbody></table></div>";
    };
    renderer.blockquote = function (quote) {
      const m = quote.match(/^\s*<p>\s*\[!(NOTE|TIP|WARN|TRAP|EXAM)\]\s*(?:<br\s*\/?>)?\s*/i);
      if (!m) return "<blockquote>" + quote + "</blockquote>";
      const t = CALLOUTS[m[1].toUpperCase()];
      const rest = quote.replace(m[0], "<p>");
      return '<div class="callout ' + t.cls + '"><div class="callout-title">' + t.icon + " " + t.label + "</div>" + rest + "</div>";
    };
    renderer.heading = function (text, level) {
      const id = "h" + (++hNo);
      return "<h" + level + ' id="' + id + '">' + text + "</h" + level + ">";
    };
    marked.setOptions({ renderer: renderer, breaks: false, gfm: true, headerIds: false, mangle: false });
    return marked.parse(md);
  };

  /* ---------- Mermaid 初期化 ---------- */
  let mermaidReady = null;
  PBM.renderMermaid = async function (root) {
    const nodes = (root || document).querySelectorAll(".mermaid:not([data-processed])");
    if (!nodes.length) return;
    if (!mermaidReady) {
      mermaidReady = import("https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.esm.min.mjs")
        .then(function (m) { window.mermaid = m.default; return m.default; })
        .catch(function () { return null; });
    }
    const mermaid = await mermaidReady;
    if (!mermaid) {
      nodes.forEach(function (n) {
        const w = n.closest(".mermaid-wrap");
        if (w) w.innerHTML = '<p class="small muted">図の描画ライブラリを読み込めませんでした（オフライン環境の可能性があります）。</p>';
      });
      return;
    }
    const dark = PBM.currentTheme() === "dark";
    const css = getComputedStyle(document.documentElement);
    const v = function (n, f) { return (css.getPropertyValue(n) || f).trim(); };
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      theme: "base",
      fontFamily: v("--font", "sans-serif"),
      themeVariables: {
        background: v("--bg-elevated", "#fff"),
        primaryColor: dark ? "#1f2a3d" : "#e7efff",
        primaryTextColor: v("--fg", "#111"),
        primaryBorderColor: v("--brand", "#2f6fed"),
        lineColor: v("--fg-muted", "#666"),
        secondaryColor: dark ? "#2b2416" : "#fdf0dc",
        tertiaryColor: dark ? "#10352a" : "#e0f5ee",
        fontSize: "14px"
      },
      flowchart: { htmlLabels: true, curve: "basis", useMaxWidth: true },
      sequence: { useMaxWidth: true }
    });
    let i = 0;
    for (const node of nodes) {
      const src = node.textContent;
      node.setAttribute("data-processed", "1");
      node.setAttribute("data-src", src);
      try {
        const out = await mermaid.render("mmd-" + Date.now() + "-" + (i++), src);
        node.innerHTML = out.svg;
      } catch (e) {
        node.innerHTML = '<pre class="small">図の記述にエラーがあります\n' + PBM.esc(String((e && e.message) || e)) + "</pre>";
      }
    }
  };

  /* テーマ切替時に図を再描画 */
  document.addEventListener("pbm:themechange", function () {
    document.querySelectorAll(".mermaid[data-processed]").forEach(function (n) {
      n.removeAttribute("data-processed");
      n.textContent = n.getAttribute("data-src") || "";
    });
    PBM.renderMermaid(document);
  });

  /* ---------- 目次生成 ---------- */
  PBM.buildToc = function (proseEl, tocEl) {
    const hs = proseEl.querySelectorAll("h2, h3");
    if (!hs.length) { tocEl.innerHTML = ""; return; }
    tocEl.innerHTML = '<div class="small muted" style="font-weight:700;margin-bottom:8px">目次</div>' +
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
})();
