/* ============================================================
   PBM Interactive — HTMLならではの「操作できる図解」ウィジェット
   ------------------------------------------------------------
   使い方:
     PBM.renderWidget(el, { type:"interactive", widget:"filter-context",
                            title:"フィルターコンテキストを体験する" })
   - 外部ライブラリ / CDN 不使用（素の JS + CSS + SVG のみ）
   - 配色はすべて既存の CSS 変数を利用（ライト/ダーク両対応）
   ============================================================ */
(function () {
  "use strict";

  const PBM = (window.PBM = window.PBM || {});

  const esc =
    PBM.esc ||
    function (s) {
      return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
      });
    };

  /* ---------- 小さなヘルパー ---------- */

  function reduced() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }
  /** アニメーション用の待ち時間（reduce 指定なら 0 にする） */
  function ms(n) {
    return reduced() ? 0 : n;
  }
  function el(tag, cls, html) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }
  function fmt(n) {
    return Number(n).toLocaleString("ja-JP");
  }
  function yen(n) {
    return "¥" + fmt(n);
  }
  const SVGNS = "http://www.w3.org/2000/svg";
  function sv(tag, attrs, text) {
    const n = document.createElementNS(SVGNS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (text != null) n.textContent = text;
    return n;
  }
  /** ボタン群（トグル）を作る。items: [{v,label,hint}] */
  function segmented(items, current, onPick, label) {
    const box = el("div", "pbmw-seg");
    box.setAttribute("role", "group");
    if (label) box.setAttribute("aria-label", label);
    items.forEach(function (it) {
      const b = el("button", "pbmw-segbtn", esc(it.label));
      b.type = "button";
      b.dataset.v = it.v;
      b.setAttribute("aria-pressed", String(it.v === current));
      if (it.hint) b.title = it.hint;
      b.addEventListener("click", function () {
        Array.prototype.forEach.call(box.children, function (c) {
          c.setAttribute("aria-pressed", String(c === b));
        });
        onPick(it.v, it);
      });
      box.appendChild(b);
    });
    return box;
  }
  function panel(title, cls) {
    const p = el("div", "pbmw-panel" + (cls ? " " + cls : ""));
    if (title) p.appendChild(el("div", "pbmw-panel-h", esc(title)));
    return p;
  }
  function tableWrap(tbl) {
    const w = el("div", "pbmw-scroll");
    w.appendChild(tbl);
    return w;
  }

  /* ============================================================
     1. filter-context — フィルターコンテキストを体で理解する
     ============================================================ */
  const FC_ROWS = [
    { i: 1, d: "2024-03-14", y: 2024, c: "家電", p: "テレビ", a: 120000 },
    { i: 2, d: "2024-06-02", y: 2024, c: "家電", p: "掃除機", a: 45000 },
    { i: 3, d: "2024-08-21", y: 2024, c: "衣料", p: "コート", a: 28000 },
    { i: 4, d: "2024-11-09", y: 2024, c: "食品", p: "コーヒー", a: 3600 },
    { i: 5, d: "2025-01-18", y: 2025, c: "家電", p: "冷蔵庫", a: 180000 },
    { i: 6, d: "2025-04-05", y: 2025, c: "家電", p: "テレビ", a: 132000 },
    { i: 7, d: "2025-05-30", y: 2025, c: "衣料", p: "シャツ", a: 9800 },
    { i: 8, d: "2025-09-12", y: 2025, c: "衣料", p: "コート", a: 31000 },
    { i: 9, d: "2025-12-24", y: 2025, c: "食品", p: "紅茶", a: 4200 }
  ];

  function wFilterContext(body, api) {
    const cats = ["家電", "衣料", "食品"];
    const years = [2024, 2025];
    const sum = function (c, y) {
      return FC_ROWS.filter(function (r) {
        return (!c || r.c === c) && (!y || r.y === y);
      }).reduce(function (t, r) {
        return t + r.a;
      }, 0);
    };

    /* --- マトリックス --- */
    const mp = panel("① レポートのマトリックス表");
    const tbl = el("table", "pbmw-table pbmw-matrix");
    let html = "<thead><tr><th>カテゴリ</th>";
    years.forEach(function (y) {
      html += "<th>" + y + "年</th>";
    });
    html += "<th>合計</th></tr></thead><tbody>";
    cats.concat(["__total"]).forEach(function (c) {
      const isT = c === "__total";
      html += '<tr class="' + (isT ? "pbmw-trtotal" : "") + '"><th>' + (isT ? "合計" : esc(c)) + "</th>";
      years.concat([""]).forEach(function (y) {
        const cc = isT ? "" : c;
        html +=
          '<td><button type="button" class="pbmw-cell" data-c="' +
          esc(cc) +
          '" data-y="' +
          y +
          '" aria-pressed="false">' +
          fmt(sum(cc, y)) +
          "</button></td>";
      });
      html += "</tr>";
    });
    html += "</tbody>";
    tbl.innerHTML = html;
    tbl.setAttribute("aria-label", "カテゴリ×年の売上マトリックス");
    mp.appendChild(tableWrap(tbl));

    /* --- 効いているフィルター --- */
    const fp = panel("② そのセルに効いているフィルター");
    const chips = el("div", "pbmw-chips", '<span class="pbmw-muted">セルをクリックすると表示されます</span>');
    const calc = el(
      "div",
      "pbmw-code",
      '売上合計 = <span class="pbmw-tok-f">SUM</span>( 売上<span class="pbmw-tok-col">[金額]</span> )'
    );
    const res = el("div", "pbmw-bignum", "—");
    fp.appendChild(chips);
    fp.appendChild(calc);
    fp.appendChild(res);

    /* --- 元データ --- */
    const dp = panel("③ 元データ（このうち何行が残るか）");
    const dt = el("table", "pbmw-table pbmw-data");
    let dh = "<thead><tr><th>#</th><th>日付</th><th>年</th><th>カテゴリ</th><th>商品</th><th class=\"num\">金額</th></tr></thead><tbody>";
    FC_ROWS.forEach(function (r) {
      dh +=
        '<tr data-i="' + r.i + '"><td>' + r.i + "</td><td>" + r.d + "</td><td>" + r.y + "</td><td>" + esc(r.c) +
        "</td><td>" + esc(r.p) + '</td><td class="num">' + yen(r.a) + "</td></tr>";
    });
    dt.innerHTML = dh + "</tbody>";
    dp.appendChild(tableWrap(dt));
    const cnt = el("div", "pbmw-sub", "対象行: —");
    dp.appendChild(cnt);

    body.appendChild(mp);
    body.appendChild(fp);
    body.appendChild(dp);

    function pick(c, y, cellBtn) {
      Array.prototype.forEach.call(tbl.querySelectorAll(".pbmw-cell"), function (b) {
        b.setAttribute("aria-pressed", String(b === cellBtn));
      });
      const hit = FC_ROWS.filter(function (r) {
        return (!c || r.c === c) && (!y || r.y === y);
      });
      /* フィルターのチップ */
      const fl = [];
      if (c) fl.push('カテゴリ = "' + c + '"');
      if (y) fl.push("年 = " + y);
      chips.innerHTML = fl.length
        ? fl
            .map(function (f) {
              return '<span class="pbmw-chip on">' + esc(f) + "</span>";
            })
            .join("")
        : '<span class="pbmw-chip none">フィルターなし（全行が対象）</span>';
      /* 元データのハイライト */
      Array.prototype.forEach.call(dt.querySelectorAll("tbody tr"), function (tr) {
        const on = hit.some(function (r) {
          return String(r.i) === tr.dataset.i;
        });
        tr.classList.toggle("hit", on);
        tr.classList.toggle("out", !on);
      });
      const total = hit.reduce(function (t, r) {
        return t + r.a;
      }, 0);
      res.innerHTML = "= " + esc(yen(total));
      cnt.innerHTML =
        "対象行: <b>" + hit.length + "</b> / " + FC_ROWS.length + " 行 &nbsp;→&nbsp; SUM の中身: " +
        hit
          .map(function (r) {
            return fmt(r.a);
          })
          .join(" + ") || "対象行: 0 行";

      /* 一言解説 */
      if (c && y) {
        api.note(
          "<b>" + esc(c) + " × " + y + "</b> のセルでは、<b>カテゴリと年の2つのフィルターが同時に</b>効いています。" +
            "SUM は表全体ではなく、残った " + hit.length + " 行だけを足しています。これがフィルターコンテキストです。",
          "brand"
        );
      } else if (!c && y) {
        api.note(
          "合計行は「上の3セルを足したもの」ではありません。<b>カテゴリのフィルターを外し、年 = " + y +
            " だけの状態で SUM をやり直した</b>結果です（" + hit.length + "行）。値がたまたま一致するだけで、計算のやり直しが起きています。",
          "warn"
        );
      } else if (c && !y) {
        api.note(
          "合計列では<b>年のフィルターが外れ</b>、カテゴリ = \"" + esc(c) + "\" だけで再評価されています（" +
            hit.length + "行）。",
          "warn"
        );
      } else {
        api.note(
          "総計は<b>フィルターが1つも効いていない</b>状態です。全 " + FC_ROWS.length +
            " 行に対してもう一度 SUM が実行されます。<b>セルごとに毎回ゼロから計算し直す</b>——これが Power BI の基本動作です。",
          "ok"
        );
      }
    }

    tbl.addEventListener("click", function (e) {
      const b = e.target.closest(".pbmw-cell");
      if (!b) return;
      pick(b.dataset.c || "", b.dataset.y ? Number(b.dataset.y) : 0, b);
    });
  }

  /* ============================================================
     2. star-explorer — フィルターの伝播
     ============================================================ */
  const STAR_DIMS = [
    { id: "prod", name: "Dim_商品", pick: 'カテゴリ = "家電"', rows: 120, hit: 18, fact: 260, pos: "tl" },
    { id: "date", name: "Dim_日付", pick: "年 = 2025", rows: 730, hit: 365, fact: 520, pos: "tr" },
    { id: "shop", name: "Dim_店舗", pick: 'エリア = "関東"', rows: 40, hit: 12, fact: 410, pos: "bl" },
    { id: "cust", name: "Dim_顧客", pick: "会員区分 = ゴールド", rows: 900, hit: 210, fact: 330, pos: "br" }
  ];
  const STAR_TOTAL = 1000;
  /* 双方向にしたとき、ファクト経由で他ディメンションに残る行数 */
  const STAR_RIPPLE = { prod: { date: 214, shop: 33, cust: 96 }, date: { prod: 88, shop: 38, cust: 380 }, shop: { prod: 104, date: 300, cust: 240 }, cust: { prod: 96, date: 290, shop: 36 } };

  function wStarExplorer(body, api) {
    let bidi = false;
    let timers = [];
    const clearT = function () {
      timers.forEach(clearTimeout);
      timers = [];
    };

    const ctrl = el("div", "pbmw-row");
    ctrl.appendChild(el("span", "pbmw-lbl", "クロスフィルターの方向"));
    ctrl.appendChild(
      segmented(
        [
          { v: "single", label: "単一方向 →" },
          { v: "both", label: "双方向 ⇄" }
        ],
        "single",
        function (v) {
          bidi = v === "both";
          api.note(
            bidi
              ? "<b>双方向</b>にしました。フィルターはディメンション→ファクトだけでなく、<b>ファクトから他のディメンションへも逆流</b>します。便利ですが、循環や意図しない絞り込みの原因になります。もう一度ディメンションを押してみてください。"
              : "<b>単一方向</b>（推奨）。フィルターは「1」側のディメンションから「多」側のファクトへ<b>片道でしか流れません</b>。ディメンションを押してみてください。",
            bidi ? "warn" : "ok"
          );
          if (sel) fire(sel);
        },
        "クロスフィルターの方向"
      )
    );
    body.appendChild(ctrl);

    const stage = el("div", "pbmw-star");
    const svg = sv("svg", { class: "pbmw-star-svg", "aria-hidden": "true" });
    stage.appendChild(svg);

    const nodes = {};
    STAR_DIMS.forEach(function (d) {
      const b = el(
        "button",
        "pbmw-node pbmw-dim pos-" + d.pos,
        '<span class="nm">' + esc(d.name) + '</span><span class="sub">' + esc(d.pick) + '</span><span class="cnt">' + fmt(d.rows) + " 行</span>"
      );
      b.type = "button";
      b.dataset.id = d.id;
      b.setAttribute("aria-pressed", "false");
      b.addEventListener("click", function () {
        fire(d.id);
      });
      nodes[d.id] = b;
      stage.appendChild(b);
    });
    const fact = el(
      "div",
      "pbmw-node pbmw-fact",
      '<span class="nm">Fact_売上</span><span class="cnt">' + fmt(STAR_TOTAL) + " 行</span>"
    );
    fact.id = "pbmw-fact-" + Math.random().toString(36).slice(2, 7);
    nodes.fact = fact;
    stage.appendChild(fact);
    body.appendChild(stage);

    const lines = {};
    const edgeState = { flow: null, back: [] };
    function applyEdgeState() {
      Object.keys(lines).forEach(function (k) {
        lines[k].flow.classList.toggle("on", edgeState.flow === k);
        lines[k].back.classList.toggle("on", edgeState.back.indexOf(k) >= 0);
      });
    }
    function draw() {
      const r0 = stage.getBoundingClientRect();
      if (!r0.width) return;
      svg.setAttribute("width", r0.width);
      svg.setAttribute("height", r0.height);
      svg.setAttribute("viewBox", "0 0 " + r0.width + " " + r0.height);
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      const c = function (n) {
        const r = n.getBoundingClientRect();
        return { x: r.left - r0.left + r.width / 2, y: r.top - r0.top + r.height / 2 };
      };
      const f = c(fact);
      STAR_DIMS.forEach(function (d) {
        const p = c(nodes[d.id]);
        const base = sv("line", { x1: p.x, y1: p.y, x2: f.x, y2: f.y, class: "pbmw-edge" });
        const flow = sv("line", { x1: p.x, y1: p.y, x2: f.x, y2: f.y, class: "pbmw-edge-flow", "data-id": d.id });
        const back = sv("line", { x1: f.x, y1: f.y, x2: p.x, y2: p.y, class: "pbmw-edge-back", "data-id": d.id });
        svg.appendChild(base);
        svg.appendChild(flow);
        svg.appendChild(back);
        lines[d.id] = { flow: flow, back: back };
      });
      applyEdgeState();
    }
    if (window.ResizeObserver) new ResizeObserver(draw).observe(stage);
    window.addEventListener("resize", draw);
    requestAnimationFrame(draw);
    setTimeout(draw, 60);

    const out = panel("伝播の結果");
    const log = el("ol", "pbmw-steps", '<li class="pbmw-muted">ディメンションをクリックすると、フィルターが流れる様子が見えます。</li>');
    out.appendChild(log);
    body.appendChild(out);

    let sel = null;
    function reset() {
      clearT();
      Object.keys(nodes).forEach(function (k) {
        nodes[k].classList.remove("sel", "hit", "ripple");
        if (nodes[k].hasAttribute("aria-pressed")) nodes[k].setAttribute("aria-pressed", "false");
      });
      edgeState.flow = null;
      edgeState.back = [];
      applyEdgeState();
      STAR_DIMS.forEach(function (d) {
        nodes[d.id].querySelector(".cnt").textContent = fmt(d.rows) + " 行";
      });
      fact.querySelector(".cnt").textContent = fmt(STAR_TOTAL) + " 行";
    }

    function fire(id) {
      reset();
      sel = id;
      const d = STAR_DIMS.filter(function (x) {
        return x.id === id;
      })[0];
      nodes[id].classList.add("sel");
      nodes[id].setAttribute("aria-pressed", "true");
      nodes[id].querySelector(".cnt").textContent = fmt(d.hit) + " 行に絞り込み";
      log.innerHTML = '<li><b>' + esc(d.name) + "</b> で <code>" + esc(d.pick) + "</code> を選択 → " + fmt(d.hit) + " 行</li>";

      timers.push(
        setTimeout(function () {
          edgeState.flow = id;
          applyEdgeState();
        }, ms(80))
      );
      timers.push(
        setTimeout(function () {
          fact.classList.add("hit");
          fact.querySelector(".cnt").textContent = fmt(d.fact) + " / " + fmt(STAR_TOTAL) + " 行";
          log.insertAdjacentHTML(
            "beforeend",
            "<li>リレーションシップを伝って <b>Fact_売上</b> が <b>" + fmt(d.fact) + " 行</b>に絞り込まれた</li>"
          );
          if (!bidi) {
            log.insertAdjacentHTML(
              "beforeend",
              '<li class="pbmw-muted">単一方向なので、ここで<b>流れは止まります</b>。他のディメンションの行数は変わりません。</li>'
            );
            api.note(
              "<b>" + esc(d.name) + "</b> の絞り込みが矢印を伝って Fact_売上 に届き、" + fmt(STAR_TOTAL) + " 行 → <b>" +
                fmt(d.fact) + " 行</b>になりました。フィルターは「1」側から「多」側へ<b>片道</b>で流れます。",
              "brand"
            );
          }
        }, ms(950))
      );

      if (bidi) {
        timers.push(
          setTimeout(function () {
            const rip = STAR_RIPPLE[id] || {};
            edgeState.back = STAR_DIMS.filter(function (o) { return o.id !== id; }).map(function (o) { return o.id; });
            applyEdgeState();
            STAR_DIMS.forEach(function (o) {
              if (o.id === id) return;
              nodes[o.id].classList.add("ripple");
              nodes[o.id].querySelector(".cnt").textContent = fmt(rip[o.id] || o.rows) + " 行に波及";
            });
            log.insertAdjacentHTML(
              "beforeend",
              '<li class="warn">双方向なので、ファクトから<b>他のディメンションへ逆流</b>：' +
                STAR_DIMS.filter(function (o) {
                  return o.id !== id;
                })
                  .map(function (o) {
                    return esc(o.name) + " " + fmt(rip[o.id] || o.rows) + "行";
                  })
                  .join(" / ") +
                "</li>"
            );
            api.note(
              "双方向にすると、<b>選んでいないディメンションまで一緒に絞り込まれます</b>。スライサーの選択肢が勝手に減る、循環参照でモデルが作れない、といった事故はここが原因です。既定は単一方向のままにしておくのが安全です。",
              "warn"
            );
          }, ms(1500))
        );
      }
    }
  }

  /* ============================================================
     3. visual-picker — 目的からビジュアルを選ぶ
     ============================================================ */
  const VP_PREVIEW = {
    hbar: "横棒グラフ",
    bar: "縦棒グラフ",
    line: "折れ線グラフ",
    stack: "積み上げ横棒",
    pie: "円グラフ",
    tree: "ツリーマップ",
    hist: "ヒストグラム",
    scatter: "散布図",
    bubble: "バブルチャート",
    card: "カード",
    gauge: "ゲージ",
    matrix: "マトリックス"
  };
  function vpPreview(kind) {
    const s = sv("svg", { viewBox: "0 0 200 120", class: "pbmw-preview", role: "img", "aria-label": (VP_PREVIEW[kind] || "") + "のイメージ" });
    const g = function (n) {
      s.appendChild(n);
    };
    const B = "var(--brand)";
    if (kind === "hbar") {
      [86, 66, 50, 34, 22].forEach(function (w, i) {
        g(sv("rect", { x: 34, y: 12 + i * 21, width: w, height: 13, rx: 3, fill: B, opacity: 1 - i * 0.13 }));
        g(sv("rect", { x: 8, y: 15 + i * 21, width: 20, height: 7, rx: 3, fill: "var(--border-strong)" }));
      });
    } else if (kind === "bar") {
      [40, 62, 30, 78, 55].forEach(function (h, i) {
        g(sv("rect", { x: 20 + i * 34, y: 100 - h, width: 22, height: h, rx: 3, fill: B, opacity: 1 - i * 0.1 }));
      });
      g(sv("line", { x1: 10, y1: 100, x2: 190, y2: 100, stroke: "var(--border-strong)", "stroke-width": 2 }));
    } else if (kind === "line") {
      g(sv("polyline", { points: "14,86 48,62 82,70 116,38 150,44 184,18", fill: "none", stroke: B, "stroke-width": 3, "stroke-linejoin": "round" }));
      "14,86 48,62 82,70 116,38 150,44 184,18".split(" ").forEach(function (p) {
        const a = p.split(",");
        g(sv("circle", { cx: a[0], cy: a[1], r: 3.4, fill: B }));
      });
      g(sv("line", { x1: 10, y1: 100, x2: 190, y2: 100, stroke: "var(--border-strong)", "stroke-width": 2 }));
    } else if (kind === "stack") {
      [[70, 45, 30], [50, 60, 20], [90, 25, 35]].forEach(function (seg, i) {
        let x = 20;
        seg.forEach(function (w, j) {
          g(sv("rect", { x: x, y: 16 + i * 32, width: w, height: 18, rx: 2, fill: j === 0 ? B : j === 1 ? "var(--ok)" : "var(--warn)" }));
          x += w + 1;
        });
      });
    } else if (kind === "pie") {
      g(sv("circle", { cx: 100, cy: 60, r: 44, fill: "var(--brand-soft)" }));
      g(sv("path", { d: "M100 60 L100 16 A44 44 0 0 1 138 82 Z", fill: B }));
      g(sv("path", { d: "M100 60 L138 82 A44 44 0 0 1 62 82 Z", fill: "var(--ok)" }));
    } else if (kind === "tree") {
      [[8, 10, 96, 60], [106, 10, 86, 34], [106, 46, 40, 24], [148, 46, 44, 24], [8, 74, 60, 36], [70, 74, 122, 36]].forEach(function (r, i) {
        g(sv("rect", { x: r[0], y: r[1], width: r[2], height: r[3], rx: 3, fill: B, opacity: 1 - i * 0.12 }));
      });
    } else if (kind === "hist") {
      [12, 30, 58, 84, 66, 38, 16].forEach(function (h, i) {
        g(sv("rect", { x: 14 + i * 25, y: 100 - h, width: 24, height: h, fill: B, opacity: 0.9 }));
      });
      g(sv("line", { x1: 8, y1: 100, x2: 192, y2: 100, stroke: "var(--border-strong)", "stroke-width": 2 }));
    } else if (kind === "scatter" || kind === "bubble") {
      const pts = [[30, 84, 5], [56, 70, 5], [72, 76, 5], [96, 52, 5], [110, 60, 5], [134, 36, 5], [158, 44, 5], [176, 22, 5]];
      pts.forEach(function (p, i) {
        g(sv("circle", { cx: p[0], cy: p[1], r: kind === "bubble" ? 5 + (i % 4) * 4 : 5, fill: B, opacity: 0.75 }));
      });
      g(sv("line", { x1: 14, y1: 100, x2: 192, y2: 100, stroke: "var(--border-strong)", "stroke-width": 2 }));
      g(sv("line", { x1: 14, y1: 8, x2: 14, y2: 100, stroke: "var(--border-strong)", "stroke-width": 2 }));
    } else if (kind === "card") {
      g(sv("rect", { x: 24, y: 20, width: 152, height: 80, rx: 10, fill: "var(--brand-soft)", stroke: B, "stroke-width": 2 }));
      g(sv("text", { x: 100, y: 62, "text-anchor": "middle", "font-size": 28, "font-weight": "800", fill: B }, "¥8.2億"));
      g(sv("text", { x: 100, y: 84, "text-anchor": "middle", "font-size": 13, fill: "var(--fg-muted)" }, "売上合計"));
    } else if (kind === "gauge") {
      g(sv("path", { d: "M26 96 A74 74 0 0 1 174 96", fill: "none", stroke: "var(--border-strong)", "stroke-width": 16, "stroke-linecap": "round" }));
      g(sv("path", { d: "M26 96 A74 74 0 0 1 148 41", fill: "none", stroke: B, "stroke-width": 16, "stroke-linecap": "round" }));
      g(sv("text", { x: 100, y: 92, "text-anchor": "middle", "font-size": 22, "font-weight": "800", fill: "var(--fg)" }, "78%"));
    } else {
      g(sv("rect", { x: 10, y: 10, width: 180, height: 100, rx: 6, fill: "none", stroke: "var(--border-strong)", "stroke-width": 2 }));
    }
    return s;
  }

  const VP_TREE = {
    compare: {
      label: "比較したい",
      icon: "⚖️",
      q: "比べる項目はいくつありますか？",
      opts: [
        {
          v: "few",
          label: "少ない（〜7個）",
          r: {
            k: "hbar",
            why: "項目名が長くても読めて、長さで大小をそのまま比較できます。並べ替えれば順位も一目で分かります。",
            avoid: ["円グラフ（角度の比較は人間には苦手）", "3D グラフ（奥行きで長さが歪む）"]
          }
        },
        {
          v: "many",
          label: "多い（8〜30個）",
          r: {
            k: "hbar",
            why: "横棒グラフを降順に並べ、上位だけを表示（TopN フィルター）します。残りは「その他」にまとめると読みやすくなります。",
            avoid: ["全項目を1画面に詰め込む", "ラベルを45度傾けた縦棒グラフ"]
          }
        },
        {
          v: "huge",
          label: "とても多い（30個以上）",
          r: {
            k: "matrix",
            why: "30個を超えるとグラフは「模様」になって読めません。マトリックス＋条件付き書式（データバー）で表として見せ、上位だけグラフにします。",
            avoid: ["棒が100本並ぶ縦棒グラフ", "ラベルが重なった散布図"]
          }
        }
      ]
    },
    trend: {
      label: "推移を見たい",
      icon: "📈",
      q: "時間の区切りはどれくらいですか？",
      opts: [
        {
          v: "cont",
          label: "連続した時系列（日次・月次など）",
          r: {
            k: "line",
            why: "線がつながることで「連続した変化」を表せます。時間は必ず横軸（左から右）に置きます。",
            avoid: ["時間を縦軸に置く", "0 から始まらない軸で変化を誇張する"]
          }
        },
        {
          v: "few",
          label: "少数の時点（4四半期など）",
          r: {
            k: "bar",
            why: "時点が少ないときは縦棒のほうが各時点の値を読みやすく、比較もしやすくなります。",
            avoid: ["3点しかないのに折れ線でつなぐ（過剰な連続感）"]
          }
        }
      ]
    },
    composition: {
      label: "構成を見たい",
      icon: "🥧",
      q: "内訳はいくつありますか？",
      opts: [
        {
          v: "2-3",
          label: "2〜3個だけ",
          r: {
            k: "pie",
            why: "「半分より多い/少ない」程度の粗い割合なら円グラフでも伝わります。必ずデータラベルに％を出します。",
            avoid: ["ドーナツの中に余計な情報を詰める", "項目が4個以上ある円グラフ"]
          }
        },
        {
          v: "many",
          label: "4個以上",
          r: {
            k: "stack",
            why: "100% 積み上げ横棒なら、項目が多くても構成比を比較できます。カテゴリ間の比較もできます。",
            avoid: ["円グラフ（4個以上は角度が読めない）", "凡例だけで色を判別させる"]
          }
        },
        {
          v: "hier",
          label: "階層がある（分類→商品）",
          r: {
            k: "tree",
            why: "ツリーマップは面積で大小と入れ子構造を同時に表せます。ドリルダウンとも相性が良いです。",
            avoid: ["階層を無視してフラットに並べる"]
          }
        }
      ]
    },
    distribution: {
      label: "分布を見たい",
      icon: "📊",
      q: "何の分布ですか？",
      opts: [
        {
          v: "one",
          label: "1つの数値の散らばり",
          r: {
            k: "hist",
            why: "ヒストグラムなら「平均では見えない偏り」（山が2つある、外れ値がある）が分かります。ビンの幅を変えて確かめます。",
            avoid: ["平均値だけをカードで出す", "棒グラフと混同してビンの間に隙間を空ける"]
          }
        },
        {
          v: "group",
          label: "グループごとの散らばりを比べたい",
          r: {
            k: "scatter",
            why: "カテゴリを横軸にしたドットプロット（散布図）で、グループごとの広がりを比較できます。箱ひげ図のカスタムビジュアルも有効です。",
            avoid: ["平均値の棒グラフだけで判断する"]
          }
        }
      ]
    },
    relation: {
      label: "関係を見たい",
      icon: "🔗",
      q: "見たい数値はいくつですか？",
      opts: [
        {
          v: "2",
          label: "2つ（例：広告費と売上）",
          r: {
            k: "scatter",
            why: "散布図は2つの数値の関係と、外れ値の存在を同時に示せます。傾向線を足すと関係の向きが伝わります。",
            avoid: ["相関を因果だと言い切る", "点が重なりすぎて塊になった図"]
          }
        },
        {
          v: "3",
          label: "3つ（3つ目を大きさで表したい）",
          r: {
            k: "bubble",
            why: "バブルチャートなら X・Y に加えて「規模」を面積で表せます。色でカテゴリを分けると4つ目の情報も乗ります。",
            avoid: ["バブルを直径で比例させる（面積で比例させる）", "情報を詰め込みすぎる"]
          }
        }
      ]
    },
    single: {
      label: "1つの数字を見たい",
      icon: "🔢",
      q: "比べる基準はありますか？",
      opts: [
        {
          v: "no",
          label: "とにかく現在値を大きく",
          r: {
            k: "card",
            why: "カードは1つの数字を最も速く伝えます。単位と期間をタイトルに必ず書きます。",
            avoid: ["桁区切りのない数字", "何の期間か分からないカード"]
          }
        },
        {
          v: "yes",
          label: "目標や前年と比べたい",
          r: {
            k: "gauge",
            why: "ゲージ（またはKPIビジュアル）は現在値・目標・達成率を1つで表せます。目標値はメジャーで持たせます。",
            avoid: ["目標のないゲージ", "最大値を勝手に決めて達成率を演出する"]
          }
        }
      ]
    }
  };

  function wVisualPicker(body, api) {
    const step1 = panel("① 何を知りたいですか？");
    const g1 = el("div", "pbmw-goals");
    Object.keys(VP_TREE).forEach(function (k) {
      const t = VP_TREE[k];
      const b = el("button", "pbmw-goal", '<span class="ic" aria-hidden="true">' + t.icon + "</span>" + esc(t.label));
      b.type = "button";
      b.dataset.k = k;
      b.setAttribute("aria-pressed", "false");
      b.addEventListener("click", function () {
        Array.prototype.forEach.call(g1.children, function (c) {
          c.setAttribute("aria-pressed", String(c === b));
        });
        showStep2(k);
      });
      g1.appendChild(b);
    });
    step1.appendChild(g1);

    const step2 = panel("② もう少し教えてください");
    const q = el("div", "pbmw-q", '<span class="pbmw-muted">まず上の「知りたいこと」を選んでください。</span>');
    const g2 = el("div", "pbmw-opts");
    step2.appendChild(q);
    step2.appendChild(g2);

    const step3 = panel("③ おすすめのビジュアル");
    const out = el("div", "pbmw-rec", '<p class="pbmw-muted">ここに結果が出ます。</p>');
    step3.appendChild(out);

    body.appendChild(step1);
    body.appendChild(step2);
    body.appendChild(step3);

    function showStep2(k) {
      const t = VP_TREE[k];
      q.innerHTML = "<b>" + esc(t.q) + "</b>";
      g2.innerHTML = "";
      out.innerHTML = '<p class="pbmw-muted">選択肢を選ぶと、おすすめと「避けるべき選択」が出ます。</p>';
      t.opts.forEach(function (o) {
        const b = el("button", "pbmw-opt", esc(o.label));
        b.type = "button";
        b.setAttribute("aria-pressed", "false");
        b.addEventListener("click", function () {
          Array.prototype.forEach.call(g2.children, function (c) {
            c.setAttribute("aria-pressed", String(c === b));
          });
          showRec(t, o);
        });
        g2.appendChild(b);
      });
      api.note("<b>" + esc(t.label) + "</b> を選びました。ビジュアル選びは「グラフの種類」から始めず、<b>問いから始める</b>のが鉄則です。", "brand");
    }

    function showRec(t, o) {
      const r = o.r;
      out.innerHTML = "";
      const head = el("div", "pbmw-rec-head");
      head.appendChild(el("div", "pbmw-rec-name", "▶ " + esc(VP_PREVIEW[r.k] || r.k)));
      out.appendChild(head);
      const cols = el("div", "pbmw-rec-cols");
      const left = el("div", "pbmw-rec-prev");
      left.appendChild(vpPreview(r.k));
      const right = el("div", "pbmw-rec-why");
      right.innerHTML =
        '<div class="pbmw-rec-lbl ok">なぜこれか</div><p>' +
        esc(r.why) +
        '</p><div class="pbmw-rec-lbl ng">避けるべき選択</div><ul>' +
        r.avoid
          .map(function (a) {
            return "<li>" + esc(a) + "</li>";
          })
          .join("") +
        "</ul>";
      cols.appendChild(left);
      cols.appendChild(right);
      out.appendChild(cols);
      api.note(
        "<b>" + esc(t.label) + " × " + esc(o.label) + "</b> なら <b>" + esc(VP_PREVIEW[r.k] || r.k) +
          "</b>。ビジュアルは「見た目の好み」ではなく<b>問いの形</b>で決まります。",
        "ok"
      );
    }
  }

  /* ============================================================
     4. dax-anatomy — DAX式の解剖
     ============================================================ */
  const DAX_SAMPLES = {
    CALCULATE: {
      label: "CALCULATE",
      lead: "フィルターコンテキストを書き換えてから計算する、DAX で最も重要な関数。",
      lines: [
        [{ t: "売上（家電）", r: "measure", d: "メジャー名。ここで定義した名前が、ビジュアルの「値」に置けるようになります。" }, { t: " = ", r: "plain" }],
        [{ t: "CALCULATE", r: "func", d: "第1引数の式を、第2引数以降で書き換えたフィルターコンテキストで評価し直します。「計算しなおす」関数です。" }, { t: "(", r: "plain" }],
        [{ t: "    " , r: "plain" }, { t: "SUM", r: "func", d: "1つの列を単純に合計する集計関数。行ごとの掛け算などはできません（その場合は SUMX）。" }, { t: "( ", r: "plain" }, { t: "売上", r: "table", d: "テーブル参照。どのテーブルの列かを明示します。" }, { t: "[金額]", r: "column", d: "列参照。角括弧の前にテーブル名が付くのが「列」の書き方です。" }, { t: " ),", r: "plain" }],
        [{ t: "    ", r: "plain" }, { t: "Dim_商品", r: "table", d: "フィルター対象のテーブル。" }, { t: "[カテゴリ]", r: "column", d: "フィルターに使う列。" }, { t: ' = "家電"', r: "filter", d: 'フィルター引数。内部では FILTER(ALL(Dim_商品[カテゴリ]), … ) に展開され、この列の既存フィルターを置き換えます。' }],
        [{ t: ")", r: "plain" }]
      ]
    },
    SUMX: {
      label: "SUMX",
      lead: "テーブルを1行ずつ回りながら式を評価し、その結果を合計する反復関数。",
      lines: [
        [{ t: "加重売上", r: "measure", d: "メジャー名。" }, { t: " = ", r: "plain" }],
        [{ t: "SUMX", r: "func", d: "第1引数のテーブルを1行ずつ走査し、各行で第2引数を計算して合計します。行ごとの掛け算が必要なときに使います。" }, { t: "(", r: "plain" }],
        [{ t: "    ", r: "plain" }, { t: "売上", r: "table", d: "反復するテーブル。ここで「行コンテキスト」が生まれます。" }, { t: ",", r: "plain" }],
        [{ t: "    ", r: "plain" }, { t: "売上[数量]", r: "column", d: "行コンテキストがあるので、この行の数量が取り出せます。" }, { t: " * ", r: "plain" }, { t: "RELATED", r: "func", d: "リレーションシップの「1」側の列を、今の行に対応づけて取ってくる関数。行コンテキストがないと使えません。" }, { t: "( ", r: "plain" }, { t: "Dim_商品[単価]", r: "column", d: "別テーブルの列。RELATED 経由で参照しています。" }, { t: " )", r: "plain" }],
        [{ t: ")", r: "plain" }]
      ]
    },
    TOTALYTD: {
      label: "TOTALYTD",
      lead: "年初から今日までの累計。タイムインテリジェンス関数の代表格。",
      lines: [
        [{ t: "売上YTD", r: "measure", d: "メジャー名。" }, { t: " = ", r: "plain" }],
        [{ t: "TOTALYTD", r: "func", d: "内部で CALCULATE + DATESYTD に展開されます。年初から現在のフィルター期間末までの累計を返します。" }, { t: "(", r: "plain" }],
        [{ t: "    ", r: "plain" }, { t: "[売上合計]", r: "measure", d: "メジャー参照。テーブル名が付かない角括弧はメジャーです。ここでは暗黙の CALCULATE が働きます。" }, { t: ",", r: "plain" }],
        [{ t: "    ", r: "plain" }, { t: "Dim_日付[日付]", r: "column", d: "日付テーブルの日付列。連続した日付を持ち、日付テーブルとしてマークされている必要があります。" }, { t: ",", r: "plain" }],
        [{ t: "    ", r: "plain" }, { t: '"3/31"', r: "filter", d: "決算期末（省略可）。3月決算ならここを \"3/31\" にすると会計年度の累計になります。" }],
        [{ t: ")", r: "plain" }]
      ]
    },
    RANKX: {
      label: "RANKX",
      lead: "指定したテーブルの中で順位を付ける関数。ALL の使い方が肝。",
      lines: [
        [{ t: "売上順位", r: "measure", d: "メジャー名。" }, { t: " = ", r: "plain" }],
        [{ t: "RANKX", r: "func", d: "第1引数のテーブルを走査して式を評価し、現在の行の値が何位かを返します。" }, { t: "(", r: "plain" }],
        [{ t: "    ", r: "plain" }, { t: "ALL", r: "func", d: "フィルターを取り除く関数。ここで外さないと「自分自身1行だけ」の中での順位になり、全部1位になってしまいます。" }, { t: "( ", r: "plain" }, { t: "Dim_商品[商品名]", r: "column", d: "順位を付ける母集団の列。" }, { t: " ),", r: "plain" }],
        [{ t: "    ", r: "plain" }, { t: "[売上合計]", r: "measure", d: "順位付けの基準となるメジャー。各行でコンテキスト遷移が起きて評価されます。" }, { t: ",,", r: "plain" }],
        [{ t: "    ", r: "plain" }, { t: "DESC", r: "filter", d: "並び順。DESC なら大きいほうが1位です。省略すると昇順（小さいほうが1位）になります。" }, { t: ", ", r: "plain" }, { t: "Dense", r: "filter", d: "同順位のあとの番号の付け方。Dense なら 1,2,2,3 と詰めます。" }],
        [{ t: ")", r: "plain" }]
      ]
    }
  };
  const DAX_ROLE = {
    func: "関数",
    column: "列参照",
    measure: "メジャー参照",
    table: "テーブル参照",
    filter: "フィルター引数 / オプション"
  };

  function wDaxAnatomy(body, api) {
    const keys = Object.keys(DAX_SAMPLES);
    const tabs = el("div", "pbmw-tabs");
    tabs.setAttribute("role", "tablist");
    const codeBox = el("div", "pbmw-code pbmw-daxcode");
    const lead = el("p", "pbmw-sub", "");
    const pop = el("div", "pbmw-pop", '<span class="pbmw-muted">色の付いた部分にマウスを乗せる／タップすると、その役割が出ます。</span>');
    pop.setAttribute("role", "status");
    pop.setAttribute("aria-live", "polite");

    keys.forEach(function (k, i) {
      const b = el("button", "pbmw-tab", esc(DAX_SAMPLES[k].label));
      b.type = "button";
      b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", String(i === 0));
      b.addEventListener("click", function () {
        Array.prototype.forEach.call(tabs.children, function (c) {
          c.setAttribute("aria-selected", String(c === b));
        });
        show(k);
      });
      tabs.appendChild(b);
    });

    body.appendChild(tabs);
    body.appendChild(lead);
    body.appendChild(codeBox);
    body.appendChild(pop);

    function show(k) {
      const s = DAX_SAMPLES[k];
      lead.textContent = s.lead;
      codeBox.innerHTML = "";
      s.lines.forEach(function (ln) {
        const line = el("div", "pbmw-cl");
        ln.forEach(function (tk) {
          if (!tk.d) {
            line.appendChild(document.createTextNode(tk.t));
            return;
          }
          const b = el("button", "pbmw-tok r-" + tk.r, esc(tk.t));
          b.type = "button";
          b.setAttribute("aria-label", tk.t + "：" + DAX_ROLE[tk.r]);
          const showIt = function () {
            Array.prototype.forEach.call(codeBox.querySelectorAll(".pbmw-tok"), function (o) {
              o.classList.toggle("on", o === b);
            });
            pop.innerHTML =
              '<span class="pbmw-rolebadge r-' + tk.r + '">' + esc(DAX_ROLE[tk.r]) + '</span><code>' + esc(tk.t.trim()) + "</code><p>" + esc(tk.d) + "</p>";
          };
          b.addEventListener("mouseenter", showIt);
          b.addEventListener("focus", showIt);
          b.addEventListener("click", function (e) {
            e.preventDefault();
            showIt();
            api.note("<b>" + esc(tk.t.trim()) + "</b> は <b>" + esc(DAX_ROLE[tk.r]) + "</b>。" + esc(tk.d), "brand");
          });
          line.appendChild(b);
        });
        codeBox.appendChild(line);
      });
      pop.innerHTML = '<span class="pbmw-muted">色の付いた部分にマウスを乗せる／タップすると、その役割が出ます。</span>';
      api.note("<b>" + esc(s.label) + "</b> の式に切り替えました。" + esc(s.lead), "");
    }
    show(keys[0]);
  }

  /* ============================================================
     5. calc-vs-measure — 計算列とメジャーの評価タイミング
     ============================================================ */
  function wCalcVsMeasure(body, api) {
    let timers = [];
    const clearT = function () {
      timers.forEach(clearTimeout);
      timers = [];
    };

    const ctrl = el("div", "pbmw-row");
    const bRefresh = el("button", "pbmw-btn primary", "🔄 データ更新（リフレッシュ）");
    const bUse = el("button", "pbmw-btn", "🖱 グラフを操作（スライサーを動かす）");
    bRefresh.type = bUse.type = "button";
    ctrl.appendChild(bRefresh);
    ctrl.appendChild(bUse);
    body.appendChild(ctrl);

    const cols = el("div", "pbmw-2col");
    function side(title, sub) {
      const p = panel(title, "pbmw-side");
      p.appendChild(el("div", "pbmw-sub", esc(sub)));
      const stg = el("div", "pbmw-stagelist");
      p.appendChild(stg);
      const st = el("div", "pbmw-state", "待機中");
      p.appendChild(st);
      return { p: p, stg: stg, st: st };
    }
    const L = side("計算列（Calculated Column）", "売上[粗利] = 売上[金額] - 売上[原価]");
    const R = side("メジャー（Measure）", "粗利合計 = SUM(売上[金額]) - SUM(売上[原価])");
    cols.appendChild(L.p);
    cols.appendChild(R.p);
    body.appendChild(cols);

    const memP = panel("メモリ（モデルサイズ）への影響");
    const bars = el("div", "pbmw-bars");
    bars.innerHTML =
      '<div class="pbmw-barrow"><span class="l">計算列</span><span class="pbmw-bar"><i style="width:0%" data-b="col"></i></span><span class="v" data-v="col">0 MB</span></div>' +
      '<div class="pbmw-barrow"><span class="l">メジャー</span><span class="pbmw-bar"><i style="width:0%;background:var(--ok)" data-b="mea"></i></span><span class="v" data-v="mea">0 MB</span></div>';
    memP.appendChild(bars);
    memP.appendChild(el("div", "pbmw-sub", "前提：売上テーブル 1,000万行。計算列は1行ずつの結果をモデルに保存します。"));
    body.appendChild(memP);

    function setBar(k, pct, txt) {
      bars.querySelector('[data-b="' + k + '"]').style.width = pct + "%";
      bars.querySelector('[data-v="' + k + '"]').textContent = txt;
    }

    function steps(target, list) {
      target.stg.innerHTML = "";
      list.forEach(function (s, i) {
        const n = el("div", "pbmw-stage", esc(s));
        target.stg.appendChild(n);
        timers.push(
          setTimeout(function () {
            n.classList.add("on");
          }, ms(120 + i * 420))
        );
      });
    }

    function refresh() {
      clearT();
      L.st.className = "pbmw-state busy";
      L.st.textContent = "計算中…";
      R.st.className = "pbmw-state idle";
      R.st.textContent = "何もしない";
      steps(L, ["1行目を計算", "2行目を計算", "… 1,000万行ぶん計算", "結果を列としてモデルに保存 💾"]);
      steps(R, ["式が置いてあるだけ", "この瞬間は 1 行も計算しない"]);
      timers.push(
        setTimeout(function () {
          L.st.className = "pbmw-state done";
          L.st.textContent = "完了（値は保存済み）";
          setBar("col", 78, "約 80 MB");
          setBar("mea", 2, "約 0 MB（式だけ）");
          api.note(
            "<b>計算列はデータ更新のときに一度だけ</b>、全行ぶん計算されます。結果はモデルに保存されるので、<b>行数ぶんのメモリを食います</b>。更新時間も伸びます。",
            "warn"
          );
        }, ms(1900))
      );
    }

    function use() {
      clearT();
      L.st.className = "pbmw-state idle";
      L.st.textContent = "保存済みの値を読むだけ";
      R.st.className = "pbmw-state busy";
      R.st.textContent = "いま計算中…";
      steps(L, ["保存された [粗利] 列を読む", "そのまま集計に使う"]);
      steps(R, ["いまのフィルターを確認", "その条件で SUM を実行", "結果を1つ返す（保存しない）"]);
      timers.push(
        setTimeout(function () {
          R.st.className = "pbmw-state done";
          R.st.textContent = "完了（結果は保存されない）";
          api.note(
            "<b>メジャーは画面を操作するたびに、その場で計算</b>されます。結果は保存されないのでメモリはほぼ0。だから「スライサーを変えたら数字が変わる」処理はメジャーの仕事です。",
            "ok"
          );
        }, ms(1500))
      );
    }

    bRefresh.addEventListener("click", refresh);
    bUse.addEventListener("click", use);
  }

  /* ============================================================
     6. join-lab — 結合の種類
     ============================================================ */
  const JL_LEFT = [
    { id: "S1", pid: "P01", qty: 1 },
    { id: "S2", pid: "P02", qty: 2 },
    { id: "S3", pid: "P02", qty: 1 },
    { id: "S4", pid: "P99", qty: 3 },
    { id: "S5", pid: "P01", qty: 5 }
  ];
  const JL_RIGHT = [
    { pid: "P01", nm: "テレビ", cat: "家電" },
    { pid: "P02", nm: "冷蔵庫", cat: "家電" },
    { pid: "P03", nm: "洗濯機", cat: "家電" }
  ];
  const JL_KINDS = [
    { v: "left", label: "左外部", desc: "左（売上）は全部残し、右に一致があれば付ける。Power Query の既定。" },
    { v: "inner", label: "内部", desc: "両方に一致がある行だけ残す。行が黙って消えるので危険。" },
    { v: "full", label: "完全外部", desc: "どちらかにあれば全部残す。両側の欠けを一度に確認できる。" },
    { v: "lanti", label: "左反", desc: "右に一致が「ない」左の行だけ。マスタ未登録の検出に使う。" },
    { v: "ranti", label: "右反", desc: "左に一致が「ない」右の行だけ。売れていない商品の検出に使う。" }
  ];

  function wJoinLab(body, api) {
    const src = el("div", "pbmw-2col");
    function srcTable(title, rows, cols, keyCol) {
      const p = panel(title);
      const t = el("table", "pbmw-table pbmw-data");
      t.innerHTML =
        "<thead><tr>" +
        cols
          .map(function (c) {
            return "<th>" + esc(c[1]) + "</th>";
          })
          .join("") +
        "</tr></thead><tbody>" +
        rows
          .map(function (r) {
            return (
              '<tr data-k="' + esc(r[keyCol]) + '" data-row="' + esc(r.id || r.pid) + '">' +
              cols
                .map(function (c) {
                  return "<td>" + esc(r[c[0]]) + "</td>";
                })
                .join("") +
              "</tr>"
            );
          })
          .join("") +
        "</tbody>";
      p.appendChild(tableWrap(t));
      return { p: p, t: t };
    }
    const LT = srcTable("左：売上", JL_LEFT, [["id", "売上ID"], ["pid", "商品ID"], ["qty", "数量"]], "pid");
    const RT = srcTable("右：商品マスタ", JL_RIGHT, [["pid", "商品ID"], ["nm", "商品名"], ["cat", "カテゴリ"]], "pid");
    src.appendChild(LT.p);
    src.appendChild(RT.p);
    body.appendChild(src);

    const ctrl = el("div", "pbmw-row");
    ctrl.appendChild(el("span", "pbmw-lbl", "結合の種類"));
    ctrl.appendChild(
      segmented(
        JL_KINDS.map(function (k) {
          return { v: k.v, label: k.label, hint: k.desc };
        }),
        "left",
        function (v) {
          run(v);
        },
        "結合の種類"
      )
    );
    body.appendChild(ctrl);

    const outP = panel("結合結果");
    const kindDesc = el("div", "pbmw-sub", "");
    const counter = el("div", "pbmw-counters", "");
    const outT = el("table", "pbmw-table pbmw-data");
    outP.appendChild(kindDesc);
    outP.appendChild(counter);
    outP.appendChild(tableWrap(outT));
    body.appendChild(outP);

    function run(v) {
      const k = JL_KINDS.filter(function (x) {
        return x.v === v;
      })[0];
      kindDesc.textContent = k.desc;
      const rights = {};
      JL_RIGHT.forEach(function (r) {
        rights[r.pid] = r;
      });
      const rows = [];
      const droppedL = [],
        droppedR = [];
      JL_LEFT.forEach(function (l) {
        const m = rights[l.pid];
        if (v === "inner" || v === "left" || v === "full") {
          if (m || v !== "inner") rows.push({ l: l, r: m || null });
          else droppedL.push(l.id);
        } else if (v === "lanti") {
          if (!m) rows.push({ l: l, r: null });
          else droppedL.push(l.id);
        } else if (v === "ranti") {
          droppedL.push(l.id);
        }
      });
      JL_RIGHT.forEach(function (r) {
        const used = JL_LEFT.some(function (l) {
          return l.pid === r.pid;
        });
        if (v === "full" && !used) rows.push({ l: null, r: r });
        else if (v === "ranti" && !used) rows.push({ l: null, r: r });
        else if (!used && (v === "left" || v === "inner" || v === "lanti")) droppedR.push(r.pid);
        else if (v === "ranti" && used) droppedR.push(r.pid);
      });

      outT.innerHTML =
        "<thead><tr><th>売上ID</th><th>商品ID</th><th>数量</th><th>商品名</th><th>カテゴリ</th></tr></thead><tbody>" +
        (rows.length
          ? rows
              .map(function (x) {
                const nul = '<span class="pbmw-null">null</span>';
                const warn = x.l && !x.r ? " warnrow" : "";
                return (
                  '<tr class="newrow' + warn + '">' +
                  "<td>" + (x.l ? esc(x.l.id) : nul) + "</td>" +
                  "<td>" + (x.l ? esc(x.l.pid) : esc(x.r.pid)) + "</td>" +
                  "<td>" + (x.l ? x.l.qty : nul) + "</td>" +
                  "<td>" + (x.r ? esc(x.r.nm) : nul) + "</td>" +
                  "<td>" + (x.r ? esc(x.r.cat) : nul) + "</td></tr>"
                );
              })
              .join("")
          : '<tr><td colspan="5" class="pbmw-muted">該当する行はありません（0行）</td></tr>') +
        "</tbody>";

      /* 消えた行のマーク */
      Array.prototype.forEach.call(LT.t.querySelectorAll("tbody tr"), function (tr) {
        tr.classList.toggle("dropped", droppedL.indexOf(tr.dataset.row) >= 0);
      });
      Array.prototype.forEach.call(RT.t.querySelectorAll("tbody tr"), function (tr) {
        tr.classList.toggle("dropped", droppedR.indexOf(tr.dataset.row) >= 0);
      });

      const diff = rows.length - JL_LEFT.length;
      counter.innerHTML =
        '<span class="pbmw-count">左 ' + JL_LEFT.length + " 行</span>" +
        '<span class="pbmw-count">右 ' + JL_RIGHT.length + " 行</span>" +
        '<span class="pbmw-count strong">結果 ' + rows.length + " 行</span>" +
        '<span class="pbmw-count ' + (diff === 0 ? "" : diff < 0 ? "ng" : "warn") + '">左に対して ' +
        (diff === 0 ? "±0" : (diff > 0 ? "+" : "") + diff) + " 行</span>" +
        (droppedL.length || droppedR.length
          ? '<span class="pbmw-count ng">消えた行: ' +
            (droppedL.length ? "左 " + droppedL.join(",") + " " : "") +
            (droppedR.length ? "右 " + droppedR.join(",") : "") +
            "</span>"
          : "");

      const notes = {
        left: "左外部結合。左（売上）の5行は<b>1行も減りません</b>。マスタにない P99 は右側が null になります。マスタ未登録は「消える」のではなく「空欄になる」——ここが左外部の安全なところです。",
        inner: "内部結合。<b>P99 の売上が黙って消えました</b>（5行→4行）。売上金額の合計が減っているのに誰も気づかない、という事故の典型です。件数は必ず前後で確認しましょう。",
        full: "完全外部結合。売れていない P03（洗濯機）も現れて6行になりました。<b>両側の「相手がいない行」を一度に洗い出せます</b>。",
        lanti: "左反結合。<b>マスタに存在しない商品IDの売上だけ</b>が残りました（P99）。データ品質チェックの定番です。",
        ranti: "右反結合。<b>1件も売れていない商品だけ</b>が残りました（P03）。死に筋商品の抽出に使えます。"
      };
      api.note(notes[v], v === "inner" ? "ng" : v === "left" ? "ok" : "brand");
    }
    run("left");
  }

  /* ============================================================
     7. cardinality-lab — カーディナリティとモデルサイズ
     ============================================================ */
  const CL_ROWS = 10000000; // 1,000万行
  const CL_PRESETS = [
    { label: "真偽値（2種類）", v: 2 },
    { label: "都道府県（47）", v: 47 },
    { label: "商品ID（5,000）", v: 5000 },
    { label: "日付のみ（約3年 = 1,095）", v: 1095 },
    { label: "顧客ID（80万）", v: 800000 },
    { label: "日時・秒まで（3年で約9,500万）", v: 95000000 }
  ];
  function clSize(card) {
    const c = Math.max(2, Math.min(card, CL_ROWS));
    const bits = Math.max(1, Math.ceil(Math.log(c) / Math.LN2));
    const values = (CL_ROWS * bits) / 8 / 1048576; // MB
    const compress = 0.35 + 0.6 * Math.min(1, Math.log(c) / Math.log(CL_ROWS)); // 種類が少ないほど RLE が効く
    const dict = (c * 24) / 1048576;
    return { mb: values * compress + dict, bits: bits, dict: dict, values: values * compress };
  }
  function wCardinalityLab(body, api) {
    const MAXP = 1000;
    const toCard = function (p) {
      return Math.round(Math.pow(10, 0.3 + (p / MAXP) * 7));
    };
    const toPos = function (c) {
      return Math.round(((Math.log(c) / Math.LN10 - 0.3) / 7) * MAXP);
    };

    const pre = el("div", "pbmw-row");
    pre.appendChild(el("span", "pbmw-lbl", "よくある列"));
    CL_PRESETS.forEach(function (p) {
      const b = el("button", "pbmw-chipbtn", esc(p.label));
      b.type = "button";
      b.addEventListener("click", function () {
        slider.value = String(Math.max(0, Math.min(MAXP, toPos(p.v))));
        update(p.v, p.label);
      });
      pre.appendChild(b);
    });
    body.appendChild(pre);

    const sp = panel("列の値の種類数（カーディナリティ）");
    const slider = document.createElement("input");
    slider.type = "range";
    slider.min = "0";
    slider.max = String(MAXP);
    slider.value = String(toPos(5000));
    slider.className = "pbmw-slider";
    slider.setAttribute("aria-label", "カーディナリティ");
    const readout = el("div", "pbmw-bignum", "");
    sp.appendChild(readout);
    sp.appendChild(slider);
    sp.appendChild(el("div", "pbmw-sub", "前提：1,000万行のテーブルにある1つの列。左に行くほど「同じ値の繰り返し」が多い列です。"));
    body.appendChild(sp);

    const gp = panel("圧縮後の推定サイズ");
    const chart = sv("svg", { viewBox: "0 0 640 220", class: "pbmw-curve", role: "img", "aria-label": "カーディナリティとモデルサイズの関係" });
    gp.appendChild(chart);
    const bars = el("div", "pbmw-bars");
    bars.innerHTML =
      '<div class="pbmw-barrow"><span class="l">この列</span><span class="pbmw-bar"><i style="width:0%" data-b="now"></i></span><span class="v" data-v="now">—</span></div>' +
      '<div class="pbmw-barrow"><span class="l">比較：都道府県</span><span class="pbmw-bar"><i style="width:0%;background:var(--ok)" data-b="ref"></i></span><span class="v" data-v="ref">—</span></div>';
    gp.appendChild(bars);
    body.appendChild(gp);

    /* グラフは「1ユーザー単位 = 1px」で描く（文字が縮まないようにするため） */
    const PAD = { l: 76, r: 16, t: 16, b: 40 };
    const H = 220;
    const maxMB = clSize(CL_ROWS).mb;
    let CW = 640;
    const X = function (p) {
      return PAD.l + (p / MAXP) * (CW - PAD.l - PAD.r);
    };
    const Y = function (mb) {
      return H - PAD.b - (mb / maxMB) * (H - PAD.t - PAD.b);
    };
    const marker = sv("circle", { r: 7, class: "pbmw-marker", cx: 0, cy: 0 });
    const vline = sv("line", { class: "pbmw-vline", x1: 0, y1: PAD.t, x2: 0, y2: H - PAD.b });

    function drawChart() {
      const w = Math.max(260, Math.min(760, Math.round(gp.clientWidth - 24)));
      CW = w;
      chart.setAttribute("width", w);
      chart.setAttribute("height", H);
      chart.setAttribute("viewBox", "0 0 " + w + " " + H);
      while (chart.firstChild) chart.removeChild(chart.firstChild);
      chart.appendChild(sv("line", { x1: PAD.l, y1: H - PAD.b, x2: w - PAD.r, y2: H - PAD.b, class: "pbmw-axis" }));
      chart.appendChild(sv("line", { x1: PAD.l, y1: PAD.t, x2: PAD.l, y2: H - PAD.b, class: "pbmw-axis" }));
      let d = "";
      for (let p = 0; p <= MAXP; p += 10) {
        d += (p === 0 ? "M" : "L") + X(p).toFixed(1) + " " + Y(clSize(toCard(p)).mb).toFixed(1) + " ";
      }
      chart.appendChild(sv("path", { d: d, class: "pbmw-curveline" }));
      [
        [0, "2"],
        [500, "6千"],
        [1000, "1千万"]
      ].forEach(function (t) {
        chart.appendChild(
          sv("text", { x: X(t[0]), y: H - 14, "text-anchor": t[0] === 0 ? "start" : t[0] === MAXP ? "end" : "middle", class: "pbmw-axistext" }, t[1])
        );
      });
      chart.appendChild(sv("text", { x: PAD.l - 8, y: PAD.t + 12, "text-anchor": "end", class: "pbmw-axistext" }, Math.round(maxMB) + "MB"));
      chart.appendChild(sv("text", { x: PAD.l - 8, y: H - PAD.b, "text-anchor": "end", class: "pbmw-axistext" }, "0MB"));
      chart.appendChild(sv("text", { x: X(0), y: PAD.t + 12, "text-anchor": "start", class: "pbmw-axistext" }, "種類が少ない ←→ 多い"));
      chart.appendChild(vline);
      chart.appendChild(marker);
      place(lastCard);
    }
    if (window.ResizeObserver) new ResizeObserver(drawChart).observe(gp);

    let lastCard = 5000;
    function place(card) {
      const s2 = clSize(card);
      const p = Math.max(0, Math.min(MAXP, toPos(card)));
      marker.setAttribute("cx", X(p));
      marker.setAttribute("cy", Y(s2.mb));
      vline.setAttribute("x1", X(p));
      vline.setAttribute("x2", X(p));
    }

    const refMB = clSize(47).mb;
    function update(card, label) {
      const s = clSize(card);
      readout.innerHTML =
        fmt(card) + " 種類 <span class=\"pbmw-unit\">→ 圧縮後 約 " + s.mb.toFixed(1) + " MB</span>" + (label ? ' <span class="pbmw-tagline">' + esc(label) + "</span>" : "");
      lastCard = card;
      place(card);
      bars.querySelector('[data-b="now"]').style.width = Math.max(1, (s.mb / maxMB) * 100) + "%";
      bars.querySelector('[data-v="now"]').textContent = s.mb.toFixed(1) + " MB";
      bars.querySelector('[data-b="ref"]').style.width = Math.max(1, (refMB / maxMB) * 100) + "%";
      bars.querySelector('[data-v="ref"]').textContent = refMB.toFixed(1) + " MB";

      let note;
      if (card <= 100) {
        note = "種類が少ない列は<b>同じ値の繰り返し</b>なので、VertiPaq がまとめて圧縮できます（辞書も小さい）。約 " + s.mb.toFixed(1) + " MB。";
      } else if (card <= 100000) {
        note = "中くらいのカーディナリティ。1値あたり約 " + s.bits + " ビットで格納され、約 " + s.mb.toFixed(1) + " MB。実務ではよくある範囲です。";
      } else {
        note =
          "<b>高カーディナリティ列</b>。約 " + s.mb.toFixed(1) + " MB（辞書だけで " + s.dict.toFixed(1) +
          " MB）。日時列は<b>日付と時刻に分割</b>する、使わないIDは削る——これがモデル軽量化の第一手です。";
      }
      api.note(note, card > 100000 ? "ng" : card <= 100 ? "ok" : "brand");
    }
    slider.addEventListener("input", function () {
      update(toCard(Number(slider.value)), "");
    });
    drawChart();
    requestAnimationFrame(drawChart);
    update(5000, "商品ID（5,000）");
  }

  /* ============================================================
     8. context-transition — コンテキスト遷移
     ============================================================ */
  const CT_PRODUCTS = [
    { nm: "テレビ", v: 300 },
    { nm: "冷蔵庫", v: 250 },
    { nm: "掃除機", v: 120 },
    { nm: "洗濯機", v: 180 }
  ];
  const CT_ALL = CT_PRODUCTS.reduce(function (t, p) {
    return t + p.v;
  }, 0);

  function wContextTransition(body, api) {
    let step = -1;

    const code = el(
      "div",
      "pbmw-code",
      '商品数ぶんの売上 = <span class="pbmw-tok-f">SUMX</span>( Dim_商品, <span class="pbmw-tok-m">[売上合計]</span> )<br>' +
        '<span class="pbmw-cmt">-- [売上合計] = SUM( 売上[金額] )　※単位：万円</span>'
    );
    body.appendChild(code);

    const ctrl = el("div", "pbmw-row");
    const bNext = el("button", "pbmw-btn primary", "次の行へ ▶");
    const bPrev = el("button", "pbmw-btn", "◀ 戻る");
    const bReset = el("button", "pbmw-btn", "最初から");
    [bNext, bPrev, bReset].forEach(function (b) {
      b.type = "button";
      ctrl.appendChild(b);
    });
    body.appendChild(ctrl);

    const cols = el("div", "pbmw-2col");
    function makeSide(title, sub, tone) {
      const p = panel(title, "pbmw-side " + tone);
      p.appendChild(el("div", "pbmw-sub", esc(sub)));
      const t = el("table", "pbmw-table pbmw-data");
      t.innerHTML =
        "<thead><tr><th>Dim_商品の行</th><th>効いているフィルター</th><th class=\"num\">[売上合計]</th></tr></thead><tbody>" +
        CT_PRODUCTS.map(function (p2, i) {
          return '<tr data-i="' + i + '"><td>' + esc(p2.nm) + '</td><td class="f">—</td><td class="num v">—</td></tr>';
        }).join("") +
        "</tbody>";
      p.appendChild(tableWrap(t));
      const tot = el("div", "pbmw-bignum", "合計 = —");
      p.appendChild(tot);
      return { p: p, t: t, tot: tot };
    }
    const L = makeSide("A. 行コンテキストだけの世界", "もし [売上合計] がただの SUM だったら（＝コンテキスト遷移が起きなければ）", "bad");
    const R = makeSide("B. コンテキスト遷移が起きた世界", "メジャー参照 = 暗黙の CALCULATE。行コンテキストがフィルターに変換される", "good");
    cols.appendChild(L.p);
    cols.appendChild(R.p);
    body.appendChild(cols);

    function render() {
      [L, R].forEach(function (S) {
        Array.prototype.forEach.call(S.t.querySelectorAll("tbody tr"), function (tr) {
          const i = Number(tr.dataset.i);
          tr.classList.toggle("cur", i === step);
          tr.classList.toggle("done", i < step);
          const f = tr.querySelector(".f"),
            v = tr.querySelector(".v");
          if (i > step) {
            f.textContent = "—";
            v.textContent = "—";
            f.className = "f";
            return;
          }
          if (S === L) {
            f.innerHTML = '<span class="pbmw-chip none">なし（行コンテキストは SUM に効かない）</span>';
            v.textContent = fmt(CT_ALL);
          } else {
            f.innerHTML = '<span class="pbmw-chip on">商品名 = "' + esc(CT_PRODUCTS[i].nm) + '"</span>';
            v.textContent = fmt(CT_PRODUCTS[i].v);
          }
        });
        const n = Math.max(0, Math.min(step + 1, CT_PRODUCTS.length));
        const sub = S === L ? CT_ALL * n : CT_PRODUCTS.slice(0, n).reduce(function (t, p) { return t + p.v; }, 0);
        S.tot.innerHTML =
          n === 0
            ? "まだ1行も評価していません"
            : (n === CT_PRODUCTS.length ? "合計 = " : n + " 行までの途中経過 = ") + "<b>" + fmt(sub) + "</b> 万円";
      });
      bPrev.disabled = step < 0;
      bNext.disabled = step >= CT_PRODUCTS.length - 1;

      if (step < 0) {
        api.note("「次の行へ」を押すと、SUMX が Dim_商品 を1行ずつ回る様子が見えます。左右で何が違うかを見比べてください。", "");
      } else if (step < CT_PRODUCTS.length - 1) {
        const p = CT_PRODUCTS[step];
        api.note(
          "<b>" + esc(p.nm) + "</b> の行を処理中。<b>A</b> では行コンテキストが SUM に伝わらないので、毎回<b>全商品の合計 " + fmt(CT_ALL) +
            "</b> が返ります。<b>B</b> ではメジャー参照が暗黙の CALCULATE を起こし、行コンテキストが<b>フィルター「商品名 = &quot;" +
            esc(p.nm) + "&quot;」に変換</b>されるので " + fmt(p.v) + " が返ります。",
          "brand"
        );
      } else {
        api.note(
          "最終結果：<b>A = " + fmt(CT_ALL * CT_PRODUCTS.length) + " 万円（明らかにおかしい）</b> / <b>B = " + fmt(CT_ALL) +
            " 万円（正しい）</b>。この差を生むのが<b>コンテキスト遷移</b>です。SUMX の中でメジャー名を書いた瞬間に、その行の情報がフィルターに化けます。",
          "ok"
        );
      }
    }
    bNext.addEventListener("click", function () {
      if (step < CT_PRODUCTS.length - 1) step++;
      render();
    });
    bPrev.addEventListener("click", function () {
      if (step >= 0) step--;
      render();
    });
    bReset.addEventListener("click", function () {
      step = -1;
      render();
    });
    render();
  }

  /* ============================================================
     9. rls-simulator — 行レベルセキュリティ
     ============================================================ */
  const RLS_STORES = [
    { nm: "新宿本店", area: "関東", sales: 4200, cust: 31000 },
    { nm: "渋谷店", area: "関東", sales: 3100, cust: 26000 },
    { nm: "横浜店", area: "関東", sales: 2600, cust: 21000 },
    { nm: "大阪本店", area: "関西", sales: 3800, cust: 29000 },
    { nm: "福岡店", area: "九州", sales: 1500, cust: 12000 }
  ];
  const RLS_USERS = [
    {
      v: "shop",
      label: "新宿本店の店長",
      upn: "tencho.shinjuku@example.com",
      role: "店舗ロール",
      dax: '[店舗名] = LOOKUPVALUE( Dim_ユーザー[店舗名], Dim_ユーザー[UPN], USERPRINCIPALNAME() )',
      test: function (s) {
        return s.nm === "新宿本店";
      },
      note: "店長には<b>自分の店舗の行しか届きません</b>。同じレポートファイルなのに、見える数字が変わっているのがポイントです。"
    },
    {
      v: "area",
      label: "関東エリアマネージャ",
      upn: "kanto.mgr@example.com",
      role: "エリアロール",
      dax: '[エリア] = LOOKUPVALUE( Dim_ユーザー[エリア], Dim_ユーザー[UPN], USERPRINCIPALNAME() )',
      test: function (s) {
        return s.area === "関東";
      },
      note: "エリアマネージャは<b>関東3店舗ぶんだけ</b>が見えます。KPIカードの数字も、その3行だけで再計算されています。"
    },
    {
      v: "hq",
      label: "経営企画",
      upn: "hq.planning@example.com",
      role: "ロール未割り当て（全体閲覧）",
      dax: "（フィルターなし）",
      test: function () {
        return true;
      },
      note: "ロールを割り当てないユーザーには<b>全社の行が見えます</b>。「全部見える人」は明示的に管理しないと、意図せず全開になりがちです。"
    },
    {
      v: "none",
      label: "権限なし",
      upn: "guest@example.com",
      role: "空のロール",
      dax: "FALSE()",
      test: function () {
        return false;
      },
      note: "条件が常に偽なので<b>1行も残りません</b>。エラーではなく<b>空白のレポート</b>になります。「数字が出ない」問い合わせの多くはこれです。"
    }
  ];

  function wRlsSimulator(body, api) {
    const ctrl = el("div", "pbmw-row");
    ctrl.appendChild(el("span", "pbmw-lbl", "ログインユーザー"));
    ctrl.appendChild(
      segmented(
        RLS_USERS.map(function (u) {
          return { v: u.v, label: u.label };
        }),
        "shop",
        function (v) {
          run(v);
        },
        "ログインユーザー"
      )
    );
    body.appendChild(ctrl);

    const who = el("div", "pbmw-who", "");
    body.appendChild(who);

    const kpiP = el("div", "pbmw-kpis");
    kpiP.innerHTML =
      '<div class="pbmw-kpi"><div class="v" data-k="sales">—</div><div class="l">売上合計（万円）</div></div>' +
      '<div class="pbmw-kpi"><div class="v" data-k="shops">—</div><div class="l">店舗数</div></div>' +
      '<div class="pbmw-kpi"><div class="v" data-k="cust">—</div><div class="l">客数</div></div>';
    body.appendChild(kpiP);

    const tp = panel("店舗別売上（同じビジュアル・同じレポート）");
    const t = el("table", "pbmw-table pbmw-data");
    t.innerHTML =
      "<thead><tr><th>店舗名</th><th>エリア</th><th class=\"num\">売上</th><th class=\"num\">客数</th></tr></thead><tbody>" +
      RLS_STORES.map(function (s) {
        return (
          '<tr data-nm="' + esc(s.nm) + '"><td>' + esc(s.nm) + "</td><td>" + esc(s.area) + '</td><td class="num">' +
          fmt(s.sales) + '</td><td class="num">' + fmt(s.cust) + "</td></tr>"
        );
      }).join("") +
      "</tbody>";
    tp.appendChild(tableWrap(t));
    const empty = el("div", "pbmw-empty", "表示できるデータがありません");
    empty.hidden = true;
    tp.appendChild(empty);
    body.appendChild(tp);

    const daxP = panel("適用されている RLS のフィルター式");
    const dax = el("div", "pbmw-code", "");
    daxP.appendChild(dax);
    body.appendChild(daxP);

    function run(v) {
      const u = RLS_USERS.filter(function (x) {
        return x.v === v;
      })[0];
      who.innerHTML =
        '<span class="pbmw-avatar" aria-hidden="true">👤</span><div><b>' + esc(u.label) + "</b>" +
        '<div class="pbmw-sub"><code>USERPRINCIPALNAME()</code> = "' + esc(u.upn) + '" ／ ロール: ' + esc(u.role) + "</div></div>";
      const vis = RLS_STORES.filter(u.test);
      Array.prototype.forEach.call(t.querySelectorAll("tbody tr"), function (tr) {
        const on = vis.some(function (s) {
          return s.nm === tr.dataset.nm;
        });
        tr.classList.toggle("hidden-row", !on);
      });
      empty.hidden = vis.length > 0;
      const sales = vis.reduce(function (a, s) {
        return a + s.sales;
      }, 0);
      const cust = vis.reduce(function (a, s) {
        return a + s.cust;
      }, 0);
      kpiP.querySelector('[data-k="sales"]').textContent = vis.length ? fmt(sales) : "（空白）";
      kpiP.querySelector('[data-k="shops"]').textContent = vis.length ? fmt(vis.length) : "0";
      kpiP.querySelector('[data-k="cust"]').textContent = vis.length ? fmt(cust) : "（空白）";
      const dparts = u.dax.split(" = ");
      dax.innerHTML =
        u.dax === "（フィルターなし）"
          ? '<span class="pbmw-muted">ロールが割り当てられていないため、テーブルフィルターは適用されません。</span>'
          : "Dim_店舗 テーブルのフィルター DAX 式：<br>" +
            (dparts.length > 1
              ? '<span class="pbmw-tok-col">' + esc(dparts[0]) + "</span> = " + esc(dparts.slice(1).join(" = "))
              : '<span class="pbmw-tok-f">' + esc(u.dax) + "</span>");
      api.note(u.note, v === "none" ? "ng" : v === "hq" ? "warn" : "ok");
    }
    run("shop");
  }

  /* ============================================================
     10. granularity-lab — 粒度
     ============================================================ */
  const GR_LEVELS = [
    {
      nm: "明細レベル",
      key: "レシート番号 × 明細行",
      rows: 1200000,
      cols: ["レシート番号", "日時（秒）", "店舗", "商品", "数量", "金額"],
      size: 96
    },
    {
      nm: "日次サマリ",
      key: "日付 × 店舗 × 商品",
      rows: 48000,
      cols: ["日付", "店舗", "商品", "数量合計", "金額合計"],
      size: 4.2
    },
    {
      nm: "月次サマリ",
      key: "年月 × 店舗",
      rows: 1200,
      cols: ["年月", "店舗", "金額合計"],
      size: 0.12
    }
  ];
  const GR_Q = [
    { q: "何時に売れたか（ピークの時間帯）", lv: 0 },
    { q: "1回の買い物で何点買ったか（バスケット単価）", lv: 0 },
    { q: "同時に買われた商品の組み合わせ", lv: 0 },
    { q: "1日のレシート枚数（客数）", lv: 0 },
    { q: "どの商品が売れたか（商品別ランキング）", lv: 1 },
    { q: "曜日別の売れ行き", lv: 1 },
    { q: "日別の売上推移", lv: 1 },
    { q: "店舗別の月次売上", lv: 2 },
    { q: "前年同月比", lv: 2 }
  ];

  function wGranularityLab(body, api) {
    let lv = 0;

    const ctrl = el("div", "pbmw-row");
    const bCoarse = el("button", "pbmw-btn primary", "▼ 粒度を粗くする（集計する）");
    const bFine = el("button", "pbmw-btn", "▲ 細かく戻す");
    const bReset = el("button", "pbmw-btn", "元データを取り直す");
    [bCoarse, bFine, bReset].forEach(function (b) {
      b.type = "button";
      ctrl.appendChild(b);
    });
    body.appendChild(ctrl);

    const lvP = panel("いまのテーブル");
    const lvHead = el("div", "pbmw-levels", "");
    const meta = el("div", "pbmw-counters", "");
    const cols = el("div", "pbmw-chips", "");
    lvP.appendChild(lvHead);
    lvP.appendChild(meta);
    lvP.appendChild(cols);
    body.appendChild(lvP);

    const qP = panel("このテーブルで答えられる質問");
    const qList = el("ul", "pbmw-qlist", "");
    qP.appendChild(qList);
    body.appendChild(qP);

    function render(reason) {
      const L = GR_LEVELS[lv];
      lvHead.innerHTML = GR_LEVELS.map(function (x, i) {
        return '<span class="pbmw-level' + (i === lv ? " on" : i < lv ? " past" : "") + '">' + esc(x.nm) + "</span>";
      }).join('<span class="pbmw-arrow" aria-hidden="true">→</span>');
      meta.innerHTML =
        '<span class="pbmw-count strong">' + fmt(L.rows) + " 行</span>" +
        '<span class="pbmw-count">キー: ' + esc(L.key) + "</span>" +
        '<span class="pbmw-count ' + (lv === 0 ? "warn" : "") + '">約 ' + L.size + " MB</span>";
      cols.innerHTML = L.cols
        .map(function (c) {
          return '<span class="pbmw-chip on">' + esc(c) + "</span>";
        })
        .join("");
      const lost = [];
      qList.innerHTML = GR_Q.map(function (x) {
        const ok = lv <= x.lv;
        if (!ok) lost.push(x.q);
        return (
          '<li class="' + (ok ? "ok" : "ng") + '"><span class="ic" aria-hidden="true">' + (ok ? "✔" : "✖") + "</span>" +
          '<span class="tx">' + esc(x.q) + "</span>" +
          (ok ? "" : '<span class="rs">' + esc(GR_LEVELS[x.lv].nm) + "が必要</span>") +
          "</li>"
        );
      }).join("");
      bCoarse.disabled = lv >= GR_LEVELS.length - 1;
      bFine.disabled = true;
      bFine.title = "集計してしまったデータからは、細かい粒度に戻せません";

      if (reason === "coarse") {
        api.note(
          "<b>" + esc(L.nm) + "</b> にしました。行数は " + fmt(GR_LEVELS[lv - 1].rows) + " → <b>" + fmt(L.rows) +
            " 行</b>（" + Math.round((1 - L.rows / GR_LEVELS[lv - 1].rows) * 100) + "% 削減）。速くて軽くなった代わりに、<b>" +
            esc(lost[lost.length - 1] || lost[0]) + "</b> のような質問に<b>もう答えられません</b>。",
          "warn"
        );
      } else if (reason === "fine") {
        api.note(
          "<b>戻せません。</b>集計してしまった行から元の明細は復元できません。粒度は<b>後から細かくできない</b>——だから取り込みの段階で「将来どんな質問をされるか」を決めておく必要があります。（やり直すには「元データを取り直す」＝ソースから再取得しかありません）",
          "ng"
        );
      } else if (reason === "reset") {
        api.note("ソースから明細を取り直しました。重いですが、<b>すべての質問に答えられる状態</b>です。", "ok");
      } else {
        api.note("いまは明細レベル。9つの質問すべてに答えられます。「粒度を粗くする」を押すと、何が失われるか見えます。", "");
      }
    }

    bCoarse.addEventListener("click", function () {
      if (lv < GR_LEVELS.length - 1) {
        lv++;
        render("coarse");
      }
    });
    bFine.addEventListener("click", function () {
      render("fine");
    });
    /* 無効化ボタンでもクリックを拾えるようにラッパーで説明を出す */
    bFine.disabled = true;
    const fineWrap = el("span", "pbmw-disabled-wrap");
    bFine.parentNode.insertBefore(fineWrap, bFine);
    fineWrap.appendChild(bFine);
    fineWrap.addEventListener("click", function () {
      render("fine");
    });
    fineWrap.tabIndex = 0;
    fineWrap.setAttribute("role", "button");
    fineWrap.setAttribute("aria-label", "細かく戻す（できません）");
    fineWrap.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        render("fine");
      }
    });
    bReset.addEventListener("click", function () {
      lv = 0;
      render("reset");
    });
    render("");
  }

  /* ============================================================
     ウィジェット登録 & 共通シェル
     ============================================================ */
  const WIDGETS = {
    "filter-context": {
      title: "フィルターコンテキストを体験する",
      guide: "表の数字（青いセル）をクリックしてみてください。合計行・総計もクリックできます。",
      build: wFilterContext
    },
    "star-explorer": {
      title: "スタースキーマとフィルターの流れ",
      guide: "ディメンション（四隅）をクリックすると、フィルターが矢印を伝ってファクトへ流れます。方向を切り替えて違いを見てください。",
      build: wStarExplorer
    },
    "visual-picker": {
      title: "ビジュアルの選び方",
      guide: "「何を知りたいか」→「もう少し詳しく」の順に選ぶと、おすすめのビジュアルが決まります。",
      build: wVisualPicker
    },
    "dax-anatomy": {
      title: "DAX式の解剖",
      guide: "タブで式を切り替え、色の付いた部分にマウスを乗せる／タップすると役割が出ます。",
      build: wDaxAnatomy
    },
    "calc-vs-measure": {
      title: "計算列とメジャーはいつ計算されるか",
      guide: "「データ更新」と「グラフを操作」を押し比べてください。動くほうが、そのとき計算しているほうです。",
      build: wCalcVsMeasure
    },
    "join-lab": {
      title: "結合の種類で残る行が変わる",
      guide: "結合の種類を切り替えてください。消えた行は左右の表で赤く消し込まれます。",
      build: wJoinLab
    },
    "cardinality-lab": {
      title: "カーディナリティとモデルサイズ",
      guide: "スライダーを動かすか、下のプリセットを押してください。値の種類数でサイズがどう変わるかが見えます。",
      build: wCardinalityLab
    },
    "context-transition": {
      title: "コンテキスト遷移を1行ずつ追う",
      guide: "「次の行へ」を押して、SUMX が1行ずつ回る様子を左右で見比べてください。",
      build: wContextTransition
    },
    "rls-simulator": {
      title: "行レベルセキュリティ（RLS）シミュレーター",
      guide: "ログインユーザーを切り替えてください。同じレポートでも、見える行とKPIが変わります。",
      build: wRlsSimulator
    },
    "granularity-lab": {
      title: "粒度を粗くすると何が失われるか",
      guide: "「粒度を粗くする」を押してください。行数が減る代わりに、答えられない質問が増えていきます。",
      build: wGranularityLab
    }
  };

  PBM.widgets = Object.keys(WIDGETS);

  PBM.renderWidget = function (node, cfg) {
    if (!node) return;
    cfg = cfg || {};
    const name = String(cfg.widget || "");
    const def = WIDGETS[name];

    node.classList.add("pbmw");
    node.setAttribute("data-widget", name);
    node.innerHTML = "";

    if (!def) {
      node.classList.add("pbmw-missing");
      node.innerHTML =
        '<div class="pbmw-head"><h4 class="pbmw-title">' + esc(cfg.title || "操作できる図") + "</h4></div>" +
        '<div class="pbmw-body"><div class="pbmw-unimpl"><b>未実装のウィジェットです</b>' +
        '<div class="pbmw-sub">widget: <code>' + esc(name || "(指定なし)") + "</code></div>" +
        '<div class="pbmw-sub">使えるのは次の10種類です：<br>' +
        PBM.widgets
          .map(function (w) {
            return "<code>" + esc(w) + "</code>";
          })
          .join(" / ") +
        "</div></div></div>";
      return node;
    }

    const head = el("div", "pbmw-head");
    const h = el("h4", "pbmw-title", esc(cfg.title || def.title));
    head.appendChild(h);
    head.appendChild(el("p", "pbmw-guide", '<span class="ic" aria-hidden="true">👆</span>' + esc(cfg.guide || def.guide)));
    node.appendChild(head);

    const bodyEl = el("div", "pbmw-body");
    node.appendChild(bodyEl);

    const note = el("div", "pbmw-note");
    note.setAttribute("role", "status");
    note.setAttribute("aria-live", "polite");
    note.innerHTML = '<span class="pbmw-muted">操作すると、ここに解説が出ます。</span>';
    node.appendChild(note);

    const api = {
      note: function (html, tone) {
        note.className = "pbmw-note" + (tone ? " t-" + tone : "");
        note.innerHTML = html;
      },
      cfg: cfg
    };

    try {
      def.build(bodyEl, api);
    } catch (e) {
      bodyEl.innerHTML = '<div class="pbmw-unimpl">図の描画でエラーが発生しました：<code>' + esc(String((e && e.message) || e)) + "</code></div>";
    }
    return node;
  };

  /** data 属性からの一括マウント（任意） */
  PBM.mountWidgets = function (root) {
    const list = (root || document).querySelectorAll("[data-pbm-widget]:not([data-pbm-mounted])");
    Array.prototype.forEach.call(list, function (n) {
      n.setAttribute("data-pbm-mounted", "1");
      PBM.renderWidget(n, { type: "interactive", widget: n.getAttribute("data-pbm-widget"), title: n.getAttribute("data-pbm-title") || "" });
    });
  };
})();
