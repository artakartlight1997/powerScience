/* ============================================================
   PBM Figure — 図解エンジン（Mermaid の完全な代替）

   使い方:
     <div class="pbm-figure" data-figure='{"type":"flow", ...}'></div>
     PBM.renderFigures(document);

   契約:
     - window.PBM.renderFigures(rootEl) を定義する
     - rootEl 内の div.pbm-figure[data-figure] をすべて処理する
     - 処理済みには data-rendered="1" を付け、二度描画しない
     - type:"interactive" は PBM.renderWidget があれば委譲する
     - JSON破損 / 未知typeは赤枠でエラーを出し、本文は壊さない
     - pbm:themechange で再描画できるよう元JSONを保持する
   ============================================================ */
(function () {
  "use strict";

  var PBM = (window.PBM = window.PBM || {});

  /* =========================================================
     0. 小物
     ========================================================= */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  var uidSeq = 0;
  function uid() { return "pbmf" + (++uidSeq); }
  function n(v) { v = Math.round(Number(v) * 10) / 10; return isFinite(v) ? String(v) : "0"; }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function arr(v) { return Array.isArray(v) ? v : (v == null ? [] : [v]); }
  function str(v) { return v == null ? "" : String(v); }
  function reduceMotion() {
    try { return window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) { return false; }
  }

  /* ---------- トーン ---------- */
  var TONES = ["blue", "green", "amber", "pink", "violet", "cyan", "gray", "red"];
  var ALIAS = {
    good: "green", ok: "green", success: "green", yes: "green",
    bad: "red", ng: "red", error: "red", danger: "red", no: "red",
    neutral: "gray", grey: "gray", none: "gray", muted: "gray",
    warn: "amber", warning: "amber", orange: "amber", yellow: "amber",
    info: "blue", primary: "blue", brand: "blue",
    purple: "violet", teal: "cyan", magenta: "pink"
  };
  var CYCLE = ["blue", "green", "amber", "violet", "cyan", "pink"];

  function tone(t, fallback) {
    if (t == null || t === "") return fallback || "gray";
    var s = String(t).toLowerCase().trim();
    if (ALIAS[s]) s = ALIAS[s];
    return TONES.indexOf(s) >= 0 ? s : (fallback || "gray");
  }
  /* 指定がなければ色を巡回させる（図が単調にならないように） */
  function cyc(t, i) {
    if (t == null || t === "") return CYCLE[(i || 0) % CYCLE.length];
    return tone(t, CYCLE[(i || 0) % CYCLE.length]);
  }

  /* ---------- テキスト幅の見積り（日本語=全角前提） ---------- */
  function charWidth(ch, size) {
    var c = ch.codePointAt(0);
    if (c === 0x20) return size * 0.30;
    if (c < 0x2e80) {
      if ("iIl|.,:;'`!()[]{}jtrf".indexOf(ch) >= 0) return size * 0.34;
      if ("mwMW@%".indexOf(ch) >= 0) return size * 0.88;
      if (ch >= "A" && ch <= "Z") return size * 0.68;
      if (ch >= "0" && ch <= "9") return size * 0.57;
      return size * 0.55;
    }
    if (c >= 0xff61 && c <= 0xff9f) return size * 0.52; /* 半角カナ */
    if (c >= 0x1f000) return size * 1.15;               /* 絵文字 */
    return size * 1.0;                                   /* 全角 */
  }
  function textW(s, size) {
    var w = 0, a = Array.from(str(s));
    for (var i = 0; i < a.length; i++) w += charWidth(a[i], size);
    return w;
  }
  function wrapText(s, size, maxW, maxLines) {
    s = str(s);
    if (!s) return [];
    var out = [], line = "", w = 0;
    var chars = Array.from(s);
    for (var i = 0; i < chars.length; i++) {
      var ch = chars[i];
      if (ch === "\n") { out.push(line); line = ""; w = 0; continue; }
      var cw = charWidth(ch, size);
      if (line !== "" && w + cw > maxW) {
        /* 英単語の途中で切らない */
        var brk = -1;
        if (/[A-Za-z0-9_.]/.test(ch)) {
          for (var k = line.length - 1; k >= 0 && line.length - k < 16; k--) {
            if (!/[A-Za-z0-9_.]/.test(line.charAt(k))) { brk = k + 1; break; }
          }
        }
        if (brk > 0 && brk < line.length) {
          var tail = line.slice(brk);
          out.push(line.slice(0, brk).replace(/\s+$/, ""));
          line = tail + ch; w = textW(line, size);
        } else {
          out.push(line); line = ch; w = cw;
        }
      } else { line += ch; w += cw; }
    }
    if (line !== "") out.push(line);
    if (maxLines && out.length > maxLines) {
      out = out.slice(0, maxLines);
      out[maxLines - 1] = out[maxLines - 1].slice(0, Math.max(1, out[maxLines - 1].length - 1)) + "…";
    }
    return out.length ? out : [""];
  }

  /* ---------- 数値の整形 ---------- */
  function fmtNum(v) {
    var x = Number(v);
    if (!isFinite(x)) return str(v);
    if (Math.abs(x) >= 1000) return x.toLocaleString("ja-JP", { maximumFractionDigits: 2 });
    if (Math.abs(x % 1) < 1e-9) return String(Math.round(x));
    return String(Math.round(x * 100) / 100);
  }
  /* 目盛りが半端な小数にならないように、目盛り数と刻み幅を一緒に決める */
  function niceAxis(maxVal) {
    maxVal = Math.abs(Number(maxVal)) || 1;
    var cands = [];
    [4, 5].forEach(function (tc) {
      var raw = maxVal / tc;
      var e = Math.pow(10, Math.floor(Math.log10(raw)));
      [1, 2, 2.5, 3, 5, 10].forEach(function (m) {
        var step = m * e;
        if (step * tc >= maxVal - 1e-9) cands.push({ max: step * tc, step: step, ticks: tc });
      });
    });
    cands.sort(function (a, b) { return (a.max - b.max) || (a.ticks - b.ticks); });
    return cands[0] || { max: niceMax(maxVal), step: niceMax(maxVal) / 4, ticks: 4 };
  }
  function niceMax(v) {
    if (!(v > 0)) return 1;
    var e = Math.pow(10, Math.floor(Math.log10(v)));
    var f = v / e;
    var ladder = [1, 1.2, 2, 3, 4, 5, 6, 8, 10];
    for (var i = 0; i < ladder.length; i++) { if (f <= ladder[i] + 1e-9) return ladder[i] * e; }
    return 10 * e;
  }

  /* =========================================================
     1. SVG ヘルパ
     ========================================================= */
  function svgOpen(w, h, label, cls) {
    return '<svg class="fig-svg' + (cls ? " " + cls : "") + '" viewBox="0 0 ' + n(w) + " " + n(h) +
      '" width="100%" preserveAspectRatio="xMidYMid meet" role="img" aria-label="' + esc(label || "図") + '">';
  }
  function markerDefs(id, tones) {
    var seen = {}, out = "";
    tones.forEach(function (t) {
      if (seen[t]) return; seen[t] = 1;
      out += '<marker id="' + id + "-ar-" + t + '" viewBox="0 0 10 10" refX="9.2" refY="5" ' +
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">' +
        '<path class="mk" data-tone="' + t + '" d="M0.5,0.7 L9.5,5 L0.5,9.3 L2.6,5 Z"/></marker>';
    });
    return "<defs>" + out + "</defs>";
  }
  function svgText(x, y, lines, o) {
    o = o || {};
    var size = o.size || 16, lh = o.lh || size * 1.35;
    var out = '<text x="' + n(x) + '" y="' + n(y) + '" font-size="' + n(size) + '"' +
      ' text-anchor="' + (o.anchor || "middle") + '"' +
      (o.cls ? ' class="' + o.cls + '"' : "") +
      (o.weight ? ' font-weight="' + o.weight + '"' : "") +
      (o.fill ? ' style="fill:' + o.fill + '"' : "") + ">";
    for (var i = 0; i < lines.length; i++) {
      out += '<tspan x="' + n(x) + '"' + (i ? ' dy="' + n(lh) + '"' : "") + ">" + esc(lines[i]) + "</tspan>";
    }
    return out + "</text>";
  }
  /* ノード寸法の計算 */
  function nodeBox(label, subs, maxW, o) {
    o = o || {};
    var ls = o.labelSize || 18, ss = o.subSize || 16;
    var padX = o.padX == null ? 14 : o.padX, padY = o.padY == null ? 12 : o.padY;
    var inner = Math.max(40, maxW - padX * 2);
    var lLines = wrapText(label, ls, inner, o.maxLabelLines || 3);
    var sLines = [];
    arr(subs).forEach(function (s) { sLines = sLines.concat(wrapText(s, ss, inner, 3)); });
    var w = 0;
    lLines.forEach(function (l) { w = Math.max(w, textW(l, ls)); });
    sLines.forEach(function (l) { w = Math.max(w, textW(l, ss)); });
    var llh = ls * 1.35, slh = ss * 1.4;
    var h = padY * 2 + lLines.length * llh + (sLines.length ? 7 + sLines.length * slh : 0);
    return {
      w: Math.min(maxW, Math.ceil(w + padX * 2 + 2)), h: Math.ceil(h),
      lLines: lLines, sLines: sLines, ls: ls, ss: ss, llh: llh, slh: slh, padY: padY
    };
  }
  function drawNode(b, x, y, w, t, cls) {
    var out = '<g data-tone="' + t + '">';
    out += '<rect class="n-rect' + (cls ? " " + cls : "") + '" x="' + n(x) + '" y="' + n(y) +
      '" width="' + n(w) + '" height="' + n(b.h) + '" rx="' + n(Math.min(14, b.h / 3)) + '"/>';
    var cy = y + b.padY + b.llh / 2;
    out += svgText(x + w / 2, cy, b.lLines, { size: b.ls, cls: "n-label", weight: 800, lh: b.llh });
    if (b.sLines.length) {
      var sy = y + b.padY + b.lLines.length * b.llh + 7 + b.slh / 2;
      out += svgText(x + w / 2, sy, b.sLines, { size: b.ss, cls: "n-sub", lh: b.slh });
    }
    return out + "</g>";
  }
  function drawEdge(d, t, markerId) {
    return '<g data-tone="' + t + '"><path class="edge" d="' + d + '" marker-end="url(#' + markerId + ')"/>' +
      '<path class="edge-flow" d="' + d + '"/></g>';
  }
  function drawEdgeLabel(x, y, text, size) {
    size = size || 16;
    var w = textW(text, size) + 16, h = size + 12;
    return "<g>" +
      '<rect class="edge-label-bg" x="' + n(x - w / 2) + '" y="' + n(y - h / 2) + '" width="' + n(w) +
      '" height="' + n(h) + '" rx="' + n(h / 2) + '"/>' +
      svgText(x, y, [text], { size: size, cls: "edge-label", weight: 700 }) + "</g>";
  }
  function svgWrap(inner) { return '<div class="fig-svgwrap">' + inner + "</svg></div>"; }

  /* =========================================================
     2. 各図のレンダラ（HTML文字列を返す）
     ========================================================= */
  var R = {};
  var VAL = 16;  /* 値ラベルの標準サイズ */

  /* ---------- 5.1 flow ---------- */
  R.flow = function (cfg) {
    var items = arr(cfg.items).slice(0, 8);
    if (!items.length) throw new Error("flow には items が必要です");
    var dir = cfg.dir === "col" || cfg.dir === "column" ? "col" : "row";
    var out = '<div class="fl" data-dir="' + dir + '">';
    items.forEach(function (it, i) {
      if (i) out += '<div class="fl-arrow" aria-hidden="true"><i>&#8594;</i></div>';
      out += '<div class="fl-item" data-tone="' + cyc(it.tone, i) + '">' +
        (it.icon ? '<div class="fl-icon">' + esc(it.icon) + "</div>" : "") +
        '<div class="fl-label">' + esc(it.label != null ? it.label : it.title) + "</div>" +
        (it.sub ? '<div class="fl-sub">' + esc(it.sub) + "</div>" : "") +
        "</div>";
    });
    return out + "</div>";
  };

  /* ---------- 5.2 steps ---------- */
  R.steps = function (cfg) {
    var items = arr(cfg.items);
    if (!items.length) throw new Error("steps には items が必要です");
    var out = '<ol class="st">';
    items.forEach(function (it, i) {
      out += '<li class="st-item" data-tone="' + cyc(it.tone, i) + '">' +
        '<div class="st-num" aria-hidden="true">' + (i + 1) + "</div>" +
        '<div class="st-body">' +
        '<div class="st-title">' + esc(it.title != null ? it.title : it.label) + "</div>" +
        (it.text ? '<div class="st-text">' + esc(it.text) + "</div>" : "") +
        "</div></li>";
    });
    return out + "</ol>";
  };

  /* ---------- 5.3 compare ---------- */
  R.compare = function (cfg) {
    var panels = arr(cfg.panels).length ? arr(cfg.panels) : arr(cfg.items);
    if (!panels.length) throw new Error("compare には panels が必要です");
    var out = '<div class="cmp" data-n="' + Math.min(3, panels.length) + '">';
    panels.forEach(function (p, i) {
      var raw = String(p.tone == null ? "" : p.tone).toLowerCase();
      var t = tone(p.tone, CYCLE[i % CYCLE.length]);
      var mark = raw === "good" || raw === "ok" || t === "green" ? "&#10003;"
        : (raw === "bad" || raw === "ng" || t === "red" ? "&#10007;" : String(i + 1));
      out += '<div class="cmp-panel" data-tone="' + t + '">' +
        '<div class="cmp-head"><span class="cmp-mark" aria-hidden="true">' + mark + "</span>" +
        '<span class="cmp-title">' + esc(p.title) + "</span></div>";
      var items = arr(p.items);
      if (items.length) {
        out += '<ul class="cmp-list">';
        items.forEach(function (x) { out += "<li>" + esc(x) + "</li>"; });
        out += "</ul>";
      }
      if (p.note) out += '<div class="cmp-note">' + esc(p.note) + "</div>";
      out += "</div>";
    });
    return out + "</div>";
  };

  /* ---------- 5.4 cards ---------- */
  R.cards = function (cfg) {
    var items = arr(cfg.items);
    if (!items.length) throw new Error("cards には items が必要です");
    var cols = clamp(parseInt(cfg.cols, 10) || Math.min(3, items.length), 1, 6);
    var out = '<div class="cds" data-cols="' + cols + '">';
    items.forEach(function (it, i) {
      out += '<div class="cd" data-tone="' + cyc(it.tone, i) + '">' +
        (it.icon ? '<div class="cd-icon">' + esc(it.icon) + "</div>" : "") +
        '<div class="cd-title">' + esc(it.title != null ? it.title : it.label) + "</div>" +
        (it.text ? '<div class="cd-text">' + esc(it.text) + "</div>" : "") +
        "</div>";
    });
    return out + "</div>";
  };

  /* ---------- 5.5 stack ---------- */
  R.stack = function (cfg) {
    var layers = arr(cfg.layers).length ? arr(cfg.layers) : arr(cfg.items);
    if (!layers.length) throw new Error("stack には layers が必要です");
    var out = '<div class="stk">';
    layers.forEach(function (l, i) {
      if (i) out += '<div class="stk-sep" aria-hidden="true">&#9660;</div>';
      out += '<div class="stk-layer" data-tone="' + cyc(l.tone, i) + '">' +
        '<div class="stk-label">' + esc(l.label != null ? l.label : l.title) + "</div>" +
        (l.sub ? '<div class="stk-sub">' + esc(l.sub) + "</div>" : "") +
        "</div>";
    });
    return out + "</div>";
  };

  /* ---------- 5.6 matrix ---------- */
  R.matrix = function (cfg) {
    var q = arr(cfg.quadrants);
    if (q.length < 4) throw new Error("matrix には quadrants が4つ必要です（左上→右上→左下→右下）");
    var out = '<div class="mx">';
    if (cfg.yLabel) out += '<div class="mx-ylab"><span>&#8593; ' + esc(cfg.yLabel) + "</span></div>";
    out += '<div class="mx-ytick is-high">' + esc(cfg.yHigh || "高") + "</div>";
    out += '<div class="mx-ytick is-low">' + esc(cfg.yLow || "低") + "</div>";
    var pos = [
      { c: 2, r: 2 }, { c: 3, r: 2 }, { c: 2, r: 3 }, { c: 3, r: 3 }
    ];
    q.slice(0, 4).forEach(function (cell, i) {
      out += '<div class="mx-cell" data-tone="' + cyc(cell.tone, i) + '" style="grid-column:' + pos[i].c +
        ";grid-row:" + pos[i].r + '">' +
        '<div class="mx-title">' + esc(cell.title) + "</div>" +
        (cell.text ? '<div class="mx-text">' + esc(cell.text) + "</div>" : "") +
        "</div>";
    });
    out += '<div class="mx-xtick" style="grid-column:2">' + esc(cfg.xLow || "小") + "</div>";
    out += '<div class="mx-xtick" style="grid-column:3">' + esc(cfg.xHigh || "大") + "</div>";
    if (cfg.xLabel) out += '<div class="mx-xlab"><span>' + esc(cfg.xLabel) + " &#8594;</span></div>";
    return out + "</div>";
  };

  /* ---------- 5.7 tablediff ---------- */
  function diffTable(side, fallbackTone) {
    if (!side) return "";
    var t = tone(side.tone, fallbackTone);
    var out = '<div class="td-side" data-tone="' + t + '">' +
      '<div class="td-title">' + esc(side.title || "") + "</div>" +
      '<div class="td-scroll"><table class="td-table">';
    var head = arr(side.head);
    if (head.length) {
      out += "<thead><tr>";
      head.forEach(function (h) { out += "<th>" + esc(str(h).replace(/^!/, "")) + "</th>"; });
      out += "</tr></thead>";
    }
    out += "<tbody>";
    arr(side.rows).forEach(function (row) {
      out += "<tr>";
      arr(row).forEach(function (cell) {
        var v = str(cell), hl = v.charAt(0) === "!";
        out += "<td" + (hl ? ' class="hl"' : "") + ">" + esc(hl ? v.slice(1) : v) + "</td>";
      });
      out += "</tr>";
    });
    return out + "</tbody></table></div></div>";
  }
  R.tablediff = function (cfg) {
    if (!cfg.before || !cfg.after) throw new Error("tablediff には before と after が必要です");
    return '<div class="td">' +
      diffTable(cfg.before, "gray") +
      '<div class="td-arrow"><span class="td-arrow-glyph" aria-hidden="true">&#10142;</span>' +
      (cfg.arrowLabel ? '<span class="td-arrow-label">' + esc(cfg.arrowLabel) + "</span>" : "") +
      "</div>" +
      diffTable(cfg.after, "blue") +
      "</div>";
  };

  /* ---------- 5.10 timeline ---------- */
  R.timeline = function (cfg) {
    var items = arr(cfg.items);
    if (!items.length) throw new Error("timeline には items が必要です");
    var out = '<ol class="tl">';
    items.forEach(function (it, i) {
      out += '<li class="tl-item" data-tone="' + cyc(it.tone, i) + '">' +
        '<div class="tl-dot" aria-hidden="true"></div>' +
        (it.label ? '<div class="tl-label">' + esc(it.label) + "</div>" : "") +
        '<div class="tl-title">' + esc(it.title != null ? it.title : it.label) + "</div>" +
        (it.text ? '<div class="tl-text">' + esc(it.text) + "</div>" : "") +
        "</li>";
    });
    return out + "</ol>";
  };

  /* ---------- 5.11 formula ---------- */
  function splitFormula(code, parts) {
    var segs = [{ text: code, part: -1 }];
    var found = [];
    parts.forEach(function (p, i) {
      var m = str(p.match);
      found[i] = false;
      if (!m) return;
      for (var s = 0; s < segs.length; s++) {
        if (segs[s].part !== -1) continue;
        var idx = segs[s].text.indexOf(m);
        if (idx < 0) continue;
        var before = segs[s].text.slice(0, idx), after = segs[s].text.slice(idx + m.length);
        var repl = [];
        if (before) repl.push({ text: before, part: -1 });
        repl.push({ text: m, part: i });
        if (after) repl.push({ text: after, part: -1 });
        segs.splice.apply(segs, [s, 1].concat(repl));
        found[i] = true;
        break;
      }
    });
    return { segs: segs, found: found };
  }
  R.formula = function (cfg) {
    var code = str(cfg.code);
    if (!code) throw new Error("formula には code が必要です");
    var parts = arr(cfg.parts);
    var sp = splitFormula(code, parts);
    var out = '<div class="fm">';
    if (cfg.lang) out += '<div class="fm-lang">' + esc(cfg.lang) + "</div>";
    out += '<div class="fm-code"><code>';
    sp.segs.forEach(function (s) {
      if (s.part < 0) { out += esc(s.text); return; }
      var p = parts[s.part];
      out += '<span class="fm-part" data-i="' + s.part + '" data-tone="' + cyc(p.tone, s.part) + '">' +
        esc(s.text) + '<sup class="fm-idx">' + (s.part + 1) + "</sup></span>";
    });
    out += "</code></div>";
    if (parts.length) {
      out += '<div class="fm-notes" data-n="' + Math.min(4, parts.length) + '">';
      parts.forEach(function (p, i) {
        out += '<div class="fm-note" data-i="' + i + '" data-tone="' + cyc(p.tone, i) + '">' +
          '<span class="fm-badge" aria-hidden="true">' + (i + 1) + "</span>" +
          '<span class="fm-note-b">' +
          (sp.found[i] ? "" : '<span class="fm-note-c">' + esc(p.match) + "</span>") +
          '<span class="fm-note-t">' + esc(p.label) + "</span></span></div>";
      });
      out += "</div>";
      out += '<svg class="fm-links" aria-hidden="true" focusable="false"></svg>';
    }
    return out + "</div>";
  };

  /* ---------- 5.8 star（SVG） ---------- */
  R.star = function (cfg, W) {
    var fact = cfg.fact || {};
    var dims = arr(cfg.dims).slice(0, 6);
    if (!fact.label || !dims.length) throw new Error("star には fact と dims が必要です");
    var id = uid();
    var eTone = "gray";
    var tones = ["gray"];
    dims.forEach(function (d, i) { tones.push(cyc(d.tone, i)); });
    var body = "", H, needLegend = false;
    var factTone = tone(fact.tone, "amber");
    var edgeLabel = str(cfg.edgeLabel);
    var wide = W >= 700;

    if (wide) {
      var gap = 40;
      var colW = clamp(Math.round((W - gap * 2) * 0.30), 150, 250);
      var centerW = W - colW * 2 - gap * 2;
      var fb = nodeBox(fact.label, fact.lines, centerW, { labelSize: 19, subSize: 16, padY: 14 });
      var boxes = dims.map(function (d) { return nodeBox(d.label, d.lines, colW, { labelSize: 18, subSize: 16 }); });
      var nL = Math.ceil(dims.length / 2);
      var L = boxes.slice(0, nL), Rt = boxes.slice(nL);
      var vg = 22;
      var colH = function (a) { return a.reduce(function (s, b) { return s + b.h; }, 0) + Math.max(0, a.length - 1) * vg; };
      H = Math.max(colH(L), colH(Rt), fb.h) + 16;
      var fx = colW + gap + (centerW - fb.w) / 2, fy = (H - fb.h) / 2;
      var fcy = fy + fb.h / 2;
      var edges = "", labels = "";
      var place = function (list, side, offset) {
        var y = (H - colH(list)) / 2;
        list.forEach(function (b, i) {
          var gi = offset + i;
          var t = cyc(dims[gi].tone, gi);
          var x = side === "L" ? 0 : W - colW;
          body += drawNode(b, x, y, colW, t);
          var sx = side === "L" ? colW : W - colW;
          var sy = y + b.h / 2;
          var spread = Math.min(20, fb.h / (list.length + 1));
          var ty = fcy + (i - (list.length - 1) / 2) * spread;
          var tx = side === "L" ? fx : fx + fb.w;
          var c1 = side === "L" ? sx + gap * 0.6 : sx - gap * 0.6;
          var c2 = side === "L" ? tx - gap * 0.6 : tx + gap * 0.6;
          var d = "M" + n(sx) + "," + n(sy) + " C" + n(c1) + "," + n(sy) + " " + n(c2) + "," + n(ty) + " " + n(tx) + "," + n(ty);
          edges += drawEdge(d, t, id + "-ar-" + t);
          tones.push(t);
          if (edgeLabel) {
            var pw = textW(edgeLabel, 15) + 16;
            if (Math.abs(tx - sx) >= pw + 6) {
              labels += drawEdgeLabel(sx + (tx - sx) * 0.55, sy + (ty - sy) * 0.55, edgeLabel, 15);
            } else { needLegend = true; }
          }
          y += b.h + vg;
        });
      };
      place(L, "L", 0);
      place(Rt, "R", nL);
      body = edges + body + drawNode(fb, fx, fy, fb.w, factTone, "is-strong") + labels;
    } else {
      /* 狭い画面：ディメンションを2列のグリッドにして、ファクトを真ん中に置く */
      var hg = 12;
      var cw = dims.length > 1 ? Math.floor((W - hg) / 2) : W;
      var rows = [];
      for (var i = 0; i < dims.length; i += 2) rows.push(dims.slice(i, i + 2));
      var rowBoxes = rows.map(function (row) {
        return row.map(function (d) { return nodeBox(d.label, d.lines, cw, { labelSize: 17.5, subSize: 16 }); });
      });
      var rowH = rowBoxes.map(function (row) { return Math.max.apply(null, row.map(function (b) { return b.h; })); });
      var topRows = Math.ceil(rows.length / 2);
      var fbN = nodeBox(fact.label, fact.lines, W, { labelSize: 19, subSize: 16, padY: 14 });
      var fw = Math.round(Math.max(fbN.w, Math.min(W, W * 0.66)));
      var fx2 = Math.round((W - fw) / 2);
      var VG = 36, RG = 14;
      var rowY = [], yy = 2, ri;
      for (ri = 0; ri < topRows; ri++) { rowY[ri] = yy; yy += rowH[ri] + RG; }
      var factY = topRows > 0 ? yy - RG + VG : 2;
      yy = factY + fbN.h + VG;
      for (ri = topRows; ri < rows.length; ri++) { rowY[ri] = yy; yy += rowH[ri] + RG; }
      H = (rows.length > topRows ? yy - RG : factY + fbN.h) + 4;

      var edges2 = "", idx = 0;
      rowBoxes.forEach(function (row, ri2) {
        row.forEach(function (b, ci) {
          var gi = idx++;
          var t = cyc(dims[gi].tone, gi);
          var single = row.length === 1;
          var w = single ? Math.min(W, Math.max(b.w, W * 0.6)) : cw;
          var x = single ? (W - w) / 2 : (ci === 0 ? 0 : W - cw);
          body += drawNode(b, x, rowY[ri2], w, t);
          tones.push(t);
          var above = ri2 < topRows;
          var sx = x + w / 2;
          var sy = above ? rowY[ri2] + b.h : rowY[ri2];
          var tx = fx2 + fw * (single ? 0.5 : (ci === 0 ? 0.28 : 0.72));
          var ty = above ? factY : factY + fbN.h;
          var d = "M" + n(sx) + "," + n(sy) + " C" + n(sx) + "," + n(sy + (above ? 18 : -18)) +
            " " + n(tx) + "," + n(ty + (above ? -18 : 18)) + " " + n(tx) + "," + n(ty);
          edges2 += drawEdge(d, t, id + "-ar-" + t);
        });
      });
      body = edges2 + body + drawNode(fbN, fx2, factY, fw, factTone, "is-strong");
    }
    var svg = svgOpen(W, H, "スタースキーマの図") + markerDefs(id, tones) + body;
    var legend = ((!wide || needLegend) && edgeLabel)
      ? '<div class="fig-legend"><span>&#8594; リレーションシップ：' + esc(edgeLabel) + "</span></div>" : "";
    return svgWrap(svg) + legend;
  };

  /* ---------- 5.9 tree（SVG） ---------- */
  R.tree = function (cfg, W) {
    var rootDef = cfg.root || {};
    if (!rootDef.label) throw new Error("tree には root が必要です");
    var kids = arr(cfg.children).length ? arr(cfg.children) : arr(rootDef.children);
    var nodes = [];
    (function walk(list, depth, parent) {
      list.forEach(function (nd, i) {
        var me = nodes.length;
        nodes.push({ label: nd.label, sub: nd.sub, tone: cyc(nd.tone, nodes.length - 1), depth: depth, parent: parent });
        walk(arr(nd.children), depth + 1, me);
      });
    })(kids, 1, 0);
    nodes.unshift({ label: rootDef.label, sub: rootDef.sub, tone: tone(rootDef.tone, "blue"), depth: 0, parent: -1 });
    /* 先頭に root を差し込んだので、親は depth から引き直す（行きがけ順なので直近の上位が親） */
    for (var j = 1; j < nodes.length; j++) {
      for (var k = j - 1; k >= 0; k--) {
        if (nodes[k].depth === nodes[j].depth - 1) { nodes[j].parent = k; break; }
      }
    }
    var id = uid();
    var IND = W < 520 ? 26 : 36;
    var gapY = 14, y = 2, tones = [];
    var placed = nodes.map(function (nd) {
      var x = nd.depth * IND;
      var maxW = Math.max(120, W - x);
      var b = nodeBox(nd.label, nd.sub ? [nd.sub] : [], maxW, { labelSize: nd.depth === 0 ? 19 : 17.5, subSize: 16 });
      var w = maxW;
      var p = { b: b, x: x, y: y, w: w, tone: nd.tone, depth: nd.depth, parent: nd.parent };
      tones.push(nd.tone);
      y += b.h + gapY;
      return p;
    });
    var H = y - gapY + 4;
    var body = "";
    placed.forEach(function (p) {
      if (p.parent >= 0) {
        var par = placed[p.parent];
        var lx = par.x + IND * 0.5;
        var cy = p.y + p.b.h / 2;
        var r = 10;
        var top = par.y + par.b.h;
        var d = "M" + n(lx) + "," + n(top) + " L" + n(lx) + "," + n(cy - r) +
          " Q" + n(lx) + "," + n(cy) + " " + n(lx + r) + "," + n(cy) + " L" + n(p.x - 2) + "," + n(cy);
        body += drawEdge(d, p.tone, id + "-ar-" + p.tone);
      }
      body += drawNode(p.b, p.x, p.y, p.w, p.tone, p.depth === 0 ? "is-strong" : "");
    });
    return svgWrap(svgOpen(W, H, "階層の図") + markerDefs(id, tones) + body);
  };

  /* ---------- 5.13 pipeline（SVG） ---------- */
  R.pipeline = function (cfg, W) {
    var nodesIn = arr(cfg.nodes);
    if (!nodesIn.length) throw new Error("pipeline には nodes が必要です");
    var edgesIn = arr(cfg.edges);
    var index = {};
    nodesIn.forEach(function (nd, i) { index[str(nd.id) || String(i)] = i; });

    /* ランク付け。フィードバックループ（循環）があっても発散しないよう、
       幅優先で1回だけ到達順にランクを与え、戻り矢印は無視する。          */
    var N = nodesIn.length;
    var rank = [], seen = [], indeg = [];
    for (var z = 0; z < N; z++) { rank[z] = 0; seen[z] = false; indeg[z] = 0; }
    var links = [];
    edgesIn.forEach(function (e) {
      var a = index[str(e.from)], b = index[str(e.to)];
      if (a == null || b == null || a === b) return;
      links.push([a, b]);
      indeg[b]++;
    });
    var queue = [];
    for (var z2 = 0; z2 < N; z2++) if (indeg[z2] === 0) { queue.push(z2); seen[z2] = true; }
    if (!queue.length) { queue.push(0); seen[0] = true; }   // 全体が循環している場合
    while (queue.length) {
      var cur = queue.shift();
      for (var li = 0; li < links.length; li++) {
        if (links[li][0] !== cur) continue;
        var nx = links[li][1];
        if (seen[nx]) continue;                              // 戻り矢印は無視する
        seen[nx] = true;
        rank[nx] = Math.min(rank[cur] + 1, N - 1);
        queue.push(nx);
      }
    }
    for (var z3 = 0; z3 < N; z3++) if (!seen[z3]) { rank[z3] = 0; seen[z3] = true; }

    /* 空のランクを詰めて、列が痩せないようにする */
    var used = [];
    rank.forEach(function (rk) { if (used.indexOf(rk) < 0) used.push(rk); });
    used.sort(function (a, b) { return a - b; });
    var remap = {};
    used.forEach(function (rk, i) { remap[rk] = i; });
    rank = rank.map(function (rk) { return remap[rk]; });

    var maxRank = used.length - 1;
    var groups = [];
    for (var r0 = 0; r0 <= maxRank; r0++) groups.push([]);
    rank.forEach(function (rk, i) { groups[rk].push(i); });

    var id = uid();
    var tones = nodesIn.map(function (nd, i) { return cyc(nd.tone, i); });

    /* 矢印ラベルが入るだけの間隔を空ける。列が痩せすぎるなら縦積みに切り替える */
    var labW = 0;
    edgesIn.forEach(function (e) { if (e.label) labW = Math.max(labW, textW(str(e.label), 16) + 22); });
    var gapX = clamp(Math.max(56, labW + 10), 56, 190);
    var colW = Math.floor((W - gapX * maxRank) / (maxRank + 1));
    var wide = W >= 640 && maxRank > 0 && colW >= 132;
    var pos = [], H;

    if (wide) {
      var boxes = nodesIn.map(function (nd, i) {
        return nodeBox(nd.label, nd.sub ? [nd.sub] : [], colW, { labelSize: 17.5, subSize: 16 });
      });
      var gapY = 20;
      var colHs = groups.map(function (g) {
        return g.reduce(function (s, i) { return s + boxes[i].h; }, 0) + Math.max(0, g.length - 1) * gapY;
      });
      H = Math.max.apply(null, colHs) + 8;
      groups.forEach(function (g, ri) {
        var y = (H - colHs[ri]) / 2;
        g.forEach(function (i) {
          pos[i] = { x: ri * (colW + gapX), y: y, w: colW, h: boxes[i].h, b: boxes[i] };
          y += boxes[i].h + gapY;
        });
      });
    } else {
      var gapYn = 54, rowGapX = 12;
      /* 戻り矢印（下位ランク→上位ランク）があるときは、
         本文を横切らないよう右側に折り返し用のレーンを空ける */
      var hasBack = edgesIn.some(function (e) {
        var a = index[str(e.from)], b = index[str(e.to)];
        return a != null && b != null && a !== b && rank[b] < rank[a];
      });
      var lane = hasBack ? 46 : 0;
      var Wn = W - lane;
      /* 戻り矢印のラベルを最上段のノードの上に置くための余白 */
      var y2 = hasBack ? 34 : 4;
      H = 0;
      groups.forEach(function (g) {
        var cw = g.length > 1 ? Math.floor((Wn - rowGapX * (g.length - 1)) / g.length) : Wn;
        var bs = g.map(function (i) { return nodeBox(nodesIn[i].label, nodesIn[i].sub ? [nodesIn[i].sub] : [], cw, { labelSize: 17.5, subSize: 16 }); });
        var rh = Math.max.apply(null, bs.map(function (b) { return b.h; }));
        g.forEach(function (i, ci) {
          pos[i] = { x: ci * (cw + rowGapX), y: y2, w: cw, h: rh, b: bs[ci] };
        });
        y2 += rh + gapYn;
      });
      H = y2 - gapYn + 4;
    }

    var edges = "", labels = "";
    edgesIn.forEach(function (e) {
      var a = index[str(e.from)], b = index[str(e.to)];
      if (a == null || b == null || !pos[a] || !pos[b]) return;
      var t = tone(e.tone, tones[a]);
      var pa = pos[a], pb = pos[b], d, mx, my;
      if (wide) {
        var x1 = pa.x + pa.w, y1 = pa.y + pa.h / 2, x2 = pb.x, y2b = pb.y + pb.h / 2;
        if (x2 < x1) { x1 = pa.x + pa.w / 2; y1 = pa.y + pa.h; x2 = pb.x + pb.w / 2; y2b = pb.y + pb.h; }
        var cx = Math.max(28, Math.abs(x2 - x1) * 0.45);
        d = "M" + n(x1) + "," + n(y1) + " C" + n(x1 + cx) + "," + n(y1) + " " + n(x2 - cx) + "," + n(y2b) + " " + n(x2) + "," + n(y2b);
        mx = (x1 + x2) / 2; my = (y1 + y2b) / 2 - 2;
      } else if (pb.y < pa.y) {
        /* 戻り矢印：右のレーンを縦に回して対象ノードの右辺に入る */
        var lx = pa.x + pa.w + 26;
        var ry1 = pa.y + pa.h / 2, ry2 = pb.y + pb.h / 2;
        d = "M" + n(pa.x + pa.w) + "," + n(ry1) +
            " C" + n(lx) + "," + n(ry1) + " " + n(lx) + "," + n(ry1) + " " + n(lx) + "," + n(ry1 - 14) +
            " L" + n(lx) + "," + n(ry2 + 14) +
            " C" + n(lx) + "," + n(ry2) + " " + n(lx) + "," + n(ry2) + " " + n(pb.x + pb.w) + "," + n(ry2);
        mx = pb.x + pb.w / 2; my = Math.max(13, pb.y - 15);
      } else {
        var sx = pa.x + pa.w / 2, sy = pa.y + pa.h, tx = pb.x + pb.w / 2, ty = pb.y;
        var cy = Math.max(16, Math.abs(ty - sy) * 0.4);
        d = "M" + n(sx) + "," + n(sy) + " C" + n(sx) + "," + n(sy + cy) + " " + n(tx) + "," + n(ty - cy) + " " + n(tx) + "," + n(ty);
        mx = (sx + tx) / 2; my = (sy + ty) / 2;
      }
      edges += drawEdge(d, t, id + "-ar-" + t);
      tones.push(t);
      if (e.label) labels += drawEdgeLabel(mx, my, str(e.label), 16);
    });

    var body = edges;
    nodesIn.forEach(function (nd, i) {
      if (!pos[i]) return;
      body += drawNode(pos[i].b, pos[i].x, pos[i].y, pos[i].w, tones[i], nd.strong ? "is-strong" : "");
    });
    body += labels;
    return svgWrap(svgOpen(W, H, "処理の流れの図") + markerDefs(id, tones) + body);
  };

  /* ---------- 5.12 chart（SVG） ---------- */
  function chartSeries(cfg) {
    var s = arr(cfg.series);
    if (!s.length && arr(cfg.values).length) s = [{ name: cfg.name || "", values: cfg.values, tone: cfg.tone }];
    return s.map(function (x, i) {
      return {
        name: str(x.name),
        values: arr(x.values).map(function (v) { return Array.isArray(v) ? v : Number(v); }),
        points: arr(x.points),
        tone: cyc(x.tone, i)
      };
    });
  }
  function legendChips(series, x, y, size) {
    var out = "", cx = x;
    series.forEach(function (s) {
      out += '<g data-tone="' + s.tone + '"><rect x="' + n(cx) + '" y="' + n(y - size / 2) + '" width="' + n(size) +
        '" height="' + n(size) + '" rx="3" fill="var(--tone)"/>' +
        svgText(cx + size + 6, y, [s.name], { size: 15, anchor: "start", cls: "n-sub" }) + "</g>";
      cx += size + 10 + textW(s.name, 15) + 18;
    });
    return out;
  }

  R.chart = function (cfg, W) {
    var kind = String(cfg.kind || "bar").toLowerCase();
    var series = chartSeries(cfg);
    if (!series.length) throw new Error("chart には series（または values）が必要です");
    var cats = arr(cfg.categories).length ? arr(cfg.categories).map(str) : arr(cfg.labels).map(str);
    var unit = str(cfg.unit);
    var hi = (cfg.highlight == null || cfg.highlight === false) ? -1 : Number(cfg.highlight);
    var id = uid();

    if (kind === "pie" || kind === "donut") return pieChart(cfg, W, series, cats, unit, hi, id);
    if (kind === "scatter") return scatterChart(cfg, W, series, cats, unit, hi, id);
    if (kind === "hbar" || kind === "barh") return hbarChart(cfg, W, series, cats, unit, hi, id);
    return xyChart(kind, cfg, W, series, cats, unit, hi, id);
  };

  function axisMax(series) {
    var mx = 0;
    series.forEach(function (s) { s.values.forEach(function (v) { if (isFinite(v)) mx = Math.max(mx, v); }); });
    return niceAxis(mx || 1);
  }

  /* bar / line / area 共通（縦軸=値） */
  function xyChart(kind, cfg, W, series, cats, unit, hi, id) {
    var nCat = Math.max.apply(null, series.map(function (s) { return s.values.length; }).concat(cats.length));
    var ax = axisMax(series), max = ax.max, ticks = ax.ticks;
    var tickTexts = [];
    for (var t = 0; t <= ticks; t++) tickTexts.push(fmtNum(max * t / ticks));
    var tickW = Math.max.apply(null, tickTexts.map(function (x) { return textW(x, 16); }));
    var padL = Math.ceil(tickW) + 14;
    var padR = 14;
    var multi = series.length > 1;
    var padT = 34 + (unit ? 22 : 0) + (multi ? 26 : 0);
    var plotW = W - padL - padR;
    var band = plotW / Math.max(1, nCat);
    var catLines = cats.map(function (c) { return wrapText(c, AXIS_SIZE(band), band - 6, 2); });
    var catH = Math.max.apply(null, catLines.map(function (l) { return l.length; })) * 21 + 12;
    var padB = catH + (cfg.xLabel ? 24 : 6);
    var plotH = clamp(Math.round(W * 0.46), 190, 300);
    var H = plotH + padT + padB;
    var y0 = padT + plotH;

    var out = "";
    /* 目盛りとグリッド */
    for (var i = 0; i <= ticks; i++) {
      var gy = y0 - plotH * i / ticks;
      out += '<line x1="' + n(padL) + '" y1="' + n(gy) + '" x2="' + n(W - padR) + '" y2="' + n(gy) +
        '" stroke="' + (i === 0 ? "var(--border-strong)" : "var(--border)") + '" stroke-width="' + (i === 0 ? "1.6" : "1") + '"/>';
      out += svgText(padL - 8, gy, [tickTexts[i]], { size: 16, anchor: "end", cls: "n-sub" });
    }
    if (unit) out += svgText(padL - 8, padT - 14, ["（" + unit + "）"], { size: 15, anchor: "start", cls: "n-sub" });
    if (cfg.yLabel) out += svgText(padL - 8, padT - 14, [str(cfg.yLabel)], { size: 15, anchor: "start", cls: "n-sub" });
    if (multi) out += legendChips(series, padL, padT - (unit || cfg.yLabel ? 38 : 16), 14);

    /* カテゴリ名 */
    for (var c = 0; c < nCat; c++) {
      var cx = padL + band * (c + 0.5);
      if (cats[c]) out += svgText(cx, y0 + 18, catLines[c], { size: AXIS_SIZE(band), cls: "n-sub", weight: hi === c ? 800 : 400, lh: 21 });
    }
    if (cfg.xLabel) out += svgText(padL + plotW / 2, H - 10, [str(cfg.xLabel)], { size: 15, cls: "n-sub", weight: 700 });

    var yOf = function (v) { return y0 - plotH * clamp(v / max, 0, 1); };

    if (kind === "line" || kind === "area") {
      series.forEach(function (s, si) {
        var pts = [];
        for (var i2 = 0; i2 < nCat; i2++) {
          var v = Number(s.values[i2]);
          if (!isFinite(v)) continue;
          pts.push([padL + band * (i2 + 0.5), yOf(v), v, i2]);
        }
        if (!pts.length) return;
        var d = pts.map(function (p, k) { return (k ? "L" : "M") + n(p[0]) + "," + n(p[1]); }).join(" ");
        if (kind === "area") {
          out += '<g data-tone="' + s.tone + '"><path d="' + d + " L" + n(pts[pts.length - 1][0]) + "," + n(y0) +
            " L" + n(pts[0][0]) + "," + n(y0) + ' Z" fill="var(--tone-soft)" opacity=".85"/></g>';
        }
        out += '<g data-tone="' + s.tone + '"><path d="' + d + '" fill="none" stroke="var(--tone)" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"/></g>';
        pts.forEach(function (p) {
          var on = hi < 0 || hi === p[3];
          out += '<g data-tone="' + (on ? s.tone : "gray") + '"><circle cx="' + n(p[0]) + '" cy="' + n(p[1]) +
            '" r="' + (hi === p[3] ? 7.5 : 5.5) + '" fill="var(--tone)" stroke="var(--bg)" stroke-width="2"/></g>';
          if (nCat <= 12) {
            out += svgText(p[0], p[1] - 17, [fmtNum(p[2])], { size: VAL, weight: 800, cls: on ? "" : "n-sub" });
          }
        });
      });
    } else {
      /* bar */
      var groupPad = band * 0.16;
      var bw = (band - groupPad * 2) / series.length;
      for (var ci = 0; ci < nCat; ci++) {
        series.forEach(function (s, si) {
          var v = Number(s.values[ci]);
          if (!isFinite(v)) return;
          var x = padL + band * ci + groupPad + bw * si;
          var yv = yOf(v), h = Math.max(1.5, y0 - yv);
          var on = hi < 0 || hi === ci;
          out += '<g data-tone="' + (on ? s.tone : "gray") + '">' +
            '<rect class="fig-bar" x="' + n(x + bw * 0.08) + '" y="' + n(yv) + '" width="' + n(bw * 0.84) +
            '" height="' + n(h) + '" rx="5" fill="var(--tone)"' + (on ? "" : ' opacity=".55"') + "/></g>";
          out += svgText(x + bw / 2, yv - 14, [fmtNum(v)], { size: VAL, weight: 800, cls: on ? "" : "n-sub" });
        });
      }
    }
    return svgWrap(svgOpen(W, H, "グラフ") + out);
  }
  function AXIS_SIZE(band) { return band < 54 ? 15 : 16; }

  function hbarChart(cfg, W, series, cats, unit, hi, id) {
    var s = series[0];
    var nRow = Math.max(s.values.length, cats.length);
    var axh = axisMax(series), max = axh.max, hticks = axh.ticks;
    var labW = 0;
    cats.forEach(function (c) { labW = Math.max(labW, textW(c, 16)); });
    labW = Math.min(labW + 12, Math.floor(W * 0.42));
    var padR = 14, padT = (unit ? 26 : 8), padB = 30;
    var rowH = 44, gap = 12;
    var plotW = W - labW - padR - 8;
    var H = padT + nRow * (rowH + gap) - gap + padB;
    var out = "";
    if (unit) out += svgText(labW + 8, 12, ["（" + unit + "）"], { size: 15, anchor: "start", cls: "n-sub" });
    for (var t = 0; t <= hticks; t++) {
      var gx = labW + 8 + plotW * t / hticks;
      out += '<line x1="' + n(gx) + '" y1="' + n(padT) + '" x2="' + n(gx) + '" y2="' + n(H - padB + 4) +
        '" stroke="var(--border)" stroke-width="1"/>';
      out += svgText(gx, H - padB + 18, [fmtNum(max * t / hticks)], { size: 15, cls: "n-sub" });
    }
    for (var i = 0; i < nRow; i++) {
      var v = Number(s.values[i]);
      var y = padT + i * (rowH + gap);
      var on = hi < 0 || hi === i;
      out += svgText(labW, y + rowH / 2, wrapText(cats[i] || "", 16, labW, 2), { size: 16, anchor: "end", weight: on ? 800 : 600, lh: 20 });
      if (!isFinite(v)) continue;
      var bw2 = Math.max(2, plotW * clamp(v / max, 0, 1));
      out += '<g data-tone="' + (on ? s.tone : "gray") + '"><rect x="' + n(labW + 8) + '" y="' + n(y + 6) +
        '" width="' + n(bw2) + '" height="' + n(rowH - 12) + '" rx="6" fill="var(--tone)"' + (on ? "" : ' opacity=".55"') + "/></g>";
      var tx = labW + 8 + bw2 + 8, anchor = "start";
      if (tx + textW(fmtNum(v), 16) > W) { tx = labW + 8 + bw2 - 8; anchor = "end"; }
      out += svgText(tx, y + rowH / 2, [fmtNum(v)], { size: 16, weight: 800, anchor: anchor, cls: on ? "" : "n-sub" });
    }
    return svgWrap(svgOpen(W, H, "横棒グラフ") + out);
  }

  function pieChart(cfg, W, series, cats, unit, hi, id) {
    var s = series[0];
    var vals = s.values.map(function (v) { return Math.max(0, Number(v) || 0); });
    var total = vals.reduce(function (a, b) { return a + b; }, 0) || 1;
    var wide = W >= 620;
    var Rr = clamp(wide ? W * 0.20 : W * 0.30, 76, 130);
    var cx = wide ? Rr + 56 : W / 2;
    var cy = Rr + 34;
    var legendX = wide ? cx + Rr + 56 : 8;
    var legendY = wide ? 22 : cy + Rr + 34;
    var lineH = 30;
    var H = wide ? Math.max(cy + Rr + 30, legendY + vals.length * lineH + 10)
      : legendY + vals.length * lineH + 6;
    var out = "", a0 = -Math.PI / 2;
    vals.forEach(function (v, i) {
      var a1 = a0 + (v / total) * Math.PI * 2;
      var t = hi < 0 ? CYCLE[i % CYCLE.length] : (hi === i ? s.tone : "gray");
      var large = (a1 - a0) > Math.PI ? 1 : 0;
      var push = hi === i ? 8 : 0;
      var mid = (a0 + a1) / 2;
      var ox = Math.cos(mid) * push, oy = Math.sin(mid) * push;
      var x1 = cx + ox + Rr * Math.cos(a0), y1 = cy + oy + Rr * Math.sin(a0);
      var x2 = cx + ox + Rr * Math.cos(a1), y2 = cy + oy + Rr * Math.sin(a1);
      out += '<g data-tone="' + t + '"><path d="M' + n(cx + ox) + "," + n(cy + oy) + " L" + n(x1) + "," + n(y1) +
        " A" + n(Rr) + "," + n(Rr) + " 0 " + large + ",1 " + n(x2) + "," + n(y2) + ' Z" fill="var(--tone)" ' +
        'stroke="var(--bg)" stroke-width="2"' + (hi >= 0 && hi !== i ? ' opacity=".5"' : "") + "/></g>";
      var pct = Math.round((v / total) * 100);
      if ((a1 - a0) > 0.42) {
        out += svgText(cx + Math.cos(mid) * (Rr * 0.66), cy + Math.sin(mid) * (Rr * 0.66), [pct + "%"],
          { size: 16, weight: 800, fill: "var(--bg-elevated)" });
      }
      a0 = a1;
    });
    vals.forEach(function (v, i) {
      var t = hi < 0 ? CYCLE[i % CYCLE.length] : (hi === i ? s.tone : "gray");
      var y = legendY + i * lineH;
      var pct = Math.round((v / total) * 100);
      out += '<g data-tone="' + t + '"><rect x="' + n(legendX) + '" y="' + n(y - 8) + '" width="16" height="16" rx="4" fill="var(--tone)"/></g>';
      out += svgText(legendX + 24, y, [str(cats[i] || s.name || "項目" + (i + 1)) + "　" + fmtNum(v) + (unit ? unit : "") + "（" + pct + "%）"],
        { size: 16, anchor: "start", weight: hi === i ? 800 : 400 });
    });
    return svgWrap(svgOpen(W, H, "円グラフ") + out);
  }

  function scatterChart(cfg, W, series, cats, unit, hi, id) {
    var pts = [];
    series.forEach(function (s, si) {
      var src = s.points.length ? s.points : s.values;
      src.forEach(function (p, i) {
        var x, y, label;
        if (Array.isArray(p)) { x = Number(p[0]); y = Number(p[1]); label = p[2]; }
        else if (p && typeof p === "object") { x = Number(p.x); y = Number(p.y); label = p.label; }
        else { x = i; y = Number(p); }
        if (!isFinite(x) || !isFinite(y)) return;
        pts.push({ x: x, y: y, label: str(label || cats[i] || ""), tone: s.tone, si: si, i: i });
      });
    });
    if (!pts.length) throw new Error("scatter には数値の座標が必要です");
    var axx = niceAxis(Math.max.apply(null, pts.map(function (p) { return p.x; })));
    var axy = niceAxis(Math.max.apply(null, pts.map(function (p) { return p.y; })));
    var xmax = axx.max, ymax = axy.max, sticks = Math.max(axx.ticks, axy.ticks);
    var tickTexts = [];
    for (var t = 0; t <= sticks; t++) tickTexts.push(fmtNum(ymax * t / sticks));
    var padL = Math.ceil(Math.max.apply(null, tickTexts.map(function (x) { return textW(x, 16); }))) + 14;
    var padR = 20, padT = 26, padB = 48;
    var plotW = W - padL - padR, plotH = clamp(Math.round(W * 0.5), 200, 300);
    var H = padT + plotH + padB, y0 = padT + plotH;
    var out = "";
    for (var i2 = 0; i2 <= sticks; i2++) {
      var gy = y0 - plotH * i2 / sticks;
      out += '<line x1="' + n(padL) + '" y1="' + n(gy) + '" x2="' + n(W - padR) + '" y2="' + n(gy) + '" stroke="var(--border)" stroke-width="1"/>';
      out += svgText(padL - 8, gy, [tickTexts[i2]], { size: 16, anchor: "end", cls: "n-sub" });
      var gx = padL + plotW * i2 / sticks;
      out += '<line x1="' + n(gx) + '" y1="' + n(padT) + '" x2="' + n(gx) + '" y2="' + n(y0) + '" stroke="var(--border)" stroke-width="1"/>';
      out += svgText(gx, y0 + 18, [fmtNum(xmax * i2 / sticks)], { size: 15, cls: "n-sub" });
    }
    if (cfg.xLabel) out += svgText(padL + plotW / 2, H - 12, [str(cfg.xLabel)], { size: 15, cls: "n-sub", weight: 700 });
    if (cfg.yLabel || unit) out += svgText(padL - 8, padT - 12, [str(cfg.yLabel || "（" + unit + "）")], { size: 15, anchor: "start", cls: "n-sub" });
    pts.forEach(function (p, k) {
      var on = hi < 0 || hi === k;
      var px = padL + plotW * clamp(p.x / xmax, 0, 1), py = y0 - plotH * clamp(p.y / ymax, 0, 1);
      out += '<g data-tone="' + (on ? p.tone : "gray") + '"><circle cx="' + n(px) + '" cy="' + n(py) +
        '" r="' + (hi === k ? 10 : 7) + '" fill="var(--tone)" stroke="var(--bg)" stroke-width="2"' + (on ? "" : ' opacity=".6"') + "/></g>";
      if (p.label) {
        var lw = textW(p.label, 16), lx = px, anc = "middle";
        if (px + lw / 2 > W - 2) { lx = W - 2; anc = "end"; }
        else if (px - lw / 2 < 2) { lx = 2; anc = "start"; }
        out += svgText(lx, py - 18, [p.label], { size: 16, weight: on ? 800 : 400, anchor: anc, cls: on ? "" : "n-sub" });
      }
    });
    return svgWrap(svgOpen(W, H, "散布図") + out);
  }

  /* =========================================================
     3. 図の組み立て
     ========================================================= */
  var SVG_TYPES = { star: 1, tree: 1, pipeline: 1, chart: 1 };

  function figureShell(cfg, inner, type) {
    var no = cfg && cfg.__n ? '<span class="fig-no">図' + esc(cfg.__n) + "</span>" : "";
    var out = '<figure class="fig fig--' + esc(type) + '">';
    if (cfg && cfg.title) out += '<figcaption class="fig-head">' + no + esc(cfg.title) + "</figcaption>";
    else if (no) out += '<figcaption class="fig-head fig-head--bare">' + no + "</figcaption>";
    out += '<div class="fig-body">' + inner + "</div>";
    if (cfg && cfg.caption) out += '<p class="fig-cap">' + esc(cfg.caption) + "</p>";
    return out + "</figure>";
  }

  function errorBox(msg, raw) {
    return '<div class="fig-error" role="alert">' +
      '<div class="fig-error-t">図を表示できませんでした</div>' +
      "<p>" + esc(msg) + "</p>" +
      (raw ? "<pre>" + esc(raw) + "</pre>" : "") + "</div>";
  }

  function widthOf(el) {
    var w = el.clientWidth;
    var p = el.parentElement;
    while ((!w || w < 40) && p) { w = p.clientWidth; p = p.parentElement; }
    if (!w || w < 40) w = 640;
    return Math.round(clamp(w, 280, 1100));
  }

  function buildBody(cfg, el) {
    var type = String(cfg && cfg.type || "").toLowerCase();
    var fn = R[type];
    if (!fn) throw new Error('未知の図の種類です: "' + (cfg && cfg.type) + '"（使えるのは ' + Object.keys(R).join(" / ") + " / interactive）");
    return fn(cfg, widthOf(el));
  }

  function renderOne(el) {
    if (el.getAttribute("data-rendered") === "1") return;
    el.setAttribute("data-rendered", "1");
    var raw = el.dataset ? el.dataset.figure : el.getAttribute("data-figure");
    raw = str(raw);
    el.__pbmFigRaw = raw;

    var cfg;
    try {
      cfg = JSON.parse(raw);
    } catch (e) {
      el.innerHTML = figureShell(null, errorBox("図の設定JSONを読み取れません: " + (e && e.message ? e.message : e), raw), "error");
      return;
    }
    if (!cfg || typeof cfg !== "object") {
      el.innerHTML = figureShell(null, errorBox("図の設定はオブジェクトである必要があります", raw), "error");
      return;
    }
    el.__pbmFigCfg = cfg;
    el.__pbmFigW = widthOf(el);

    var type = String(cfg.type || "").toLowerCase();

    /* interactive → ウィジェットへ委譲 */
    if (type === "interactive") {
      el.innerHTML = "";
      if (typeof PBM.renderWidget === "function") {
        try {
          PBM.renderWidget(el, cfg);
          if (!el.firstChild) el.innerHTML = figureShell(cfg, todoBox(cfg), "interactive");
        } catch (e2) {
          el.innerHTML = figureShell(cfg, errorBox("操作できる図の描画に失敗しました: " + (e2 && e2.message ? e2.message : e2), raw), "interactive");
        }
      } else {
        el.innerHTML = figureShell(cfg, todoBox(cfg), "interactive");
      }
      afterRender(el);
      return;
    }

    try {
      el.innerHTML = figureShell(cfg, buildBody(cfg, el), type || "unknown");
    } catch (e3) {
      el.innerHTML = figureShell(cfg, errorBox((e3 && e3.message ? e3.message : String(e3)), raw), "error");
    }
    el.__pbmFigAt = Date.now();
    afterRender(el);
  }

  function todoBox(cfg) {
    return '<div class="fig-todo">' +
      "<b>この図は準備中です</b>" +
      "操作できる図（インタラクティブ）はまだ読み込まれていません。" +
      (cfg && cfg.widget ? '<span class="fig-todo-tag">' + esc(cfg.widget) + "</span>" : "") +
      "</div>";
  }

  /* ---------- 描画後の処理（アニメーション / formula の連結線 / hover） ---------- */
  var io = null;
  function ensureObserver() {
    if (io || typeof IntersectionObserver === "undefined") return io;
    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add("is-in");
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.04 });
    return io;
  }

  function afterRender(el) {
    var fig = el.querySelector(".fig");
    if (!fig) return;
    if (!reduceMotion()) {
      fig.classList.add("fig-anim");
      var obs = ensureObserver();
      if (obs) {
        obs.observe(fig);
        /* 保険：何らかの理由で観測が働かない場合も必ず表示する */
        setTimeout(function () { fig.classList.add("is-in"); }, 1600);
      } else {
        fig.classList.add("is-in");
      }
    } else {
      fig.classList.add("is-in");
    }
    bindFormula(el);
  }

  /* ---------- formula：ホバー連動 + 連結線 ---------- */
  function bindFormula(el) {
    var fm = el.querySelector(".fm");
    if (!fm) return;
    var parts = fm.querySelectorAll(".fm-part");
    var notes = fm.querySelectorAll(".fm-note");
    function setOn(i, on) {
      var p = fm.querySelector('.fm-part[data-i="' + i + '"]');
      var nt = fm.querySelector('.fm-note[data-i="' + i + '"]');
      if (p) p.classList.toggle("is-on", on);
      if (nt) nt.classList.toggle("is-on", on);
      var pa = fm.querySelector('.fm-links path[data-i="' + i + '"]');
      if (pa) pa.classList.toggle("is-on", on);
    }
    function wire(node) {
      var i = node.getAttribute("data-i");
      node.addEventListener("mouseenter", function () { setOn(i, true); });
      node.addEventListener("mouseleave", function () { setOn(i, false); });
      node.addEventListener("focus", function () { setOn(i, true); });
      node.addEventListener("blur", function () { setOn(i, false); });
      node.setAttribute("tabindex", "0");
    }
    Array.prototype.forEach.call(parts, wire);
    Array.prototype.forEach.call(notes, wire);
    drawFormulaLinks(fm);
    if (typeof ResizeObserver !== "undefined" && !fm.__pbmRO) {
      fm.__pbmRO = new ResizeObserver(function () { drawFormulaLinks(fm); });
      fm.__pbmRO.observe(fm);
    }
  }

  function drawFormulaLinks(fm) {
    var svg = fm.querySelector(".fm-links");
    if (!svg) return;
    var notes = fm.querySelectorAll(".fm-note");
    var wrapRect = fm.getBoundingClientRect();
    svg.setAttribute("width", String(Math.round(wrapRect.width)));
    svg.setAttribute("height", String(Math.round(wrapRect.height)));
    svg.setAttribute("viewBox", "0 0 " + Math.round(wrapRect.width) + " " + Math.round(wrapRect.height));
    /* 注釈が1行に並んでいるときだけ線を引く（縦積みでは線が交差して読みにくい） */
    var top = null, sameRow = notes.length > 0 && notes.length <= 4;
    Array.prototype.forEach.call(notes, function (nt) {
      if (top === null) top = nt.offsetTop;
      else if (Math.abs(nt.offsetTop - top) > 2) sameRow = false;
    });
    if (!sameRow || wrapRect.width < 640) { svg.innerHTML = ""; return; }
    var paths = "";
    Array.prototype.forEach.call(notes, function (nt) {
      var i = nt.getAttribute("data-i");
      var part = fm.querySelector('.fm-part[data-i="' + i + '"]');
      if (!part) return;
      var pr = part.getClientRects()[0];
      if (!pr) return;
      var nr = nt.getBoundingClientRect();
      var x1 = pr.left + pr.width / 2 - wrapRect.left;
      var y1 = pr.bottom - wrapRect.top + 2;
      var x2 = nr.left + Math.min(30, nr.width / 2) - wrapRect.left;
      var y2 = nr.top - wrapRect.top - 1;
      if (y2 - y1 < 8) return;
      var my = (y1 + y2) / 2;
      paths += '<path data-i="' + i + '" data-tone="' + (nt.getAttribute("data-tone") || "gray") + '" d="M' +
        n(x1) + "," + n(y1) + " C" + n(x1) + "," + n(my) + " " + n(x2) + "," + n(my) + " " + n(x2) + "," + n(y2) + '"/>';
    });
    svg.innerHTML = paths;
  }

  /* =========================================================
     4. 公開API
     ========================================================= */
  PBM.renderFigures = function (rootEl) {
    var root = rootEl || document;
    if (!root.querySelectorAll) return;
    var nodes = root.querySelectorAll("div.pbm-figure[data-figure]");
    Array.prototype.forEach.call(nodes, function (el) {
      try { renderOne(el); }
      catch (e) {
        el.setAttribute("data-rendered", "1");
        el.innerHTML = figureShell(null, errorBox("図の描画に失敗しました: " + (e && e.message ? e.message : e), el.__pbmFigRaw || ""), "error");
      }
    });
  };

  /* 図の一覧（デバッグ用） */
  PBM.figureTypes = Object.keys(R).concat(["interactive"]);

  /* ---------- テーマ変更で再描画（元JSONは data-figure / __pbmFigRaw に保持） ---------- */
  document.addEventListener("pbm:themechange", function () {
    var nodes = document.querySelectorAll('div.pbm-figure[data-rendered="1"]');
    Array.prototype.forEach.call(nodes, function (el) {
      var cfg = el.__pbmFigCfg;
      /* interactive はウィジェット側が状態を持つので触らない */
      if (cfg && String(cfg.type).toLowerCase() === "interactive") return;
      /* 直前に描き直したばかりなら二度手間を避ける */
      if (el.__pbmFigAt && Date.now() - el.__pbmFigAt < 400) return;
      var raw = el.__pbmFigRaw || (el.dataset ? el.dataset.figure : "");
      if (!raw) return;
      if (el.dataset && !el.dataset.figure) el.dataset.figure = raw;
      el.removeAttribute("data-rendered");
      el.innerHTML = "";
      renderOne(el);
      var fig = el.querySelector(".fig");
      if (fig) fig.classList.add("is-in");
    });
  });

  /* ---------- 幅が変わったらSVGの図だけ組み直す ---------- */
  var rzTimer = null;
  window.addEventListener("resize", function () {
    if (rzTimer) clearTimeout(rzTimer);
    rzTimer = setTimeout(function () {
      var nodes = document.querySelectorAll('div.pbm-figure[data-rendered="1"]');
      Array.prototype.forEach.call(nodes, function (el) {
        var cfg = el.__pbmFigCfg;
        if (!cfg) return;
        var t = String(cfg.type || "").toLowerCase();
        var fm = el.querySelector(".fm");
        if (fm) drawFormulaLinks(fm);
        if (!SVG_TYPES[t]) return;
        var w = widthOf(el);
        if (Math.abs(w - (el.__pbmFigW || 0)) < 28) return;
        el.__pbmFigW = w;
        var host = el.querySelector(".fig-body");
        if (!host) return;
        try { host.innerHTML = buildBody(cfg, el); } catch (e) { /* 失敗時は既存表示のまま */ }
      });
    }, 180);
  }, { passive: true });
})();
