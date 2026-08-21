/* ============================================================
   PBM Quiz — クイズ / 模擬試験エンジン
   スマホでの片手操作を想定（大きめタップターゲット・1問1画面）
   ============================================================ */
(function () {
  "use strict";
  const PBM = (window.PBM = window.PBM || {});
  const KEYS = "ABCDEFGH";

  PBM.loadQuiz = async function (id) {
    const res = await fetch(PBM.url("content/quizzes/" + id + ".json"), { cache: "no-cache" });
    if (!res.ok) return null;
    return res.json();
  };

  /* options: { mode: "practice"|"exam", limit, minutes, shuffle, onFinish } */
  PBM.mountQuiz = function (root, quiz, options) {
    const opt = Object.assign({ mode: "practice", shuffle: true, limit: 0, minutes: 0 }, options || {});
    let qs = quiz.questions.slice();
    if (typeof opt.filter === "function") qs = qs.filter(opt.filter);
    if (opt.areas && opt.areas.length) qs = qs.filter(function (q) { return opt.areas.indexOf(q.area) >= 0; });
    if (opt.skills && opt.skills.length) qs = qs.filter(function (q) { return opt.skills.indexOf(q.skill) >= 0; });
    if (!qs.length) {
      root.innerHTML = '<div class="card"><h3>該当する設問がありません</h3>' +
        '<p class="muted">条件を緩めてもう一度お試しください。</p></div>';
      return;
    }
    if (opt.shuffle) qs = PBM.shuffle(qs);
    if (opt.limit > 0) qs = qs.slice(0, opt.limit);

    const state = { i: 0, answers: new Array(qs.length).fill(null), locked: new Array(qs.length).fill(false), startedAt: Date.now() };
    let timerId = null;

    root.innerHTML =
      '<div class="row" style="justify-content:space-between">' +
        '<div class="badge" id="q-count"></div>' +
        '<div class="timer hidden" id="q-timer"></div>' +
      "</div>" +
      '<div class="qbar" id="q-bar"></div>' +
      '<div class="q-card" style="margin-top:12px"><div id="q-body"></div></div>' +
      '<div class="actionbar">' +
        '<button class="btn btn-sm btn-ghost" id="q-prev">← 前へ</button>' +
        '<span class="spacer"></span>' +
        '<button class="btn btn-brand" id="q-next">次へ →</button>' +
      "</div>" +
      '<div id="q-result" class="hidden"></div>';

    const $ = (s) => root.querySelector(s);
    const body = $("#q-body"), bar = $("#q-bar"), countEl = $("#q-count");
    const prevBtn = $("#q-prev"), nextBtn = $("#q-next");

    /* ----- タイマー ----- */
    if (opt.minutes > 0) {
      const timerEl = $("#q-timer");
      timerEl.classList.remove("hidden");
      const endAt = Date.now() + opt.minutes * 60000;
      const tick = function () {
        const left = Math.max(0, endAt - Date.now());
        const m = Math.floor(left / 60000), s = Math.floor((left % 60000) / 1000);
        timerEl.textContent = m + ":" + String(s).padStart(2, "0");
        timerEl.classList.toggle("low", left < 300000);
        if (left <= 0) { clearInterval(timerId); finish(true); }
      };
      tick(); timerId = setInterval(tick, 1000);
    }

    function isCorrect(q, ans) {
      if (ans == null) return false;
      if (q.type === "multi") {
        const a = (q.answer || []).slice().sort().join(",");
        return Array.isArray(ans) && ans.slice().sort().join(",") === a;
      }
      return ans === q.answer;
    }

    function drawBar() {
      bar.innerHTML = qs.map(function (q, idx) {
        let cls = "";
        if (idx === state.i) cls = "now";
        else if (opt.mode === "practice" && state.locked[idx]) cls = isCorrect(q, state.answers[idx]) ? "ok" : "ng";
        else if (state.answers[idx] != null) cls = "ok";
        return '<i class="' + cls + '"></i>';
      }).join("");
      countEl.textContent = "第 " + (state.i + 1) + " 問 / 全 " + qs.length + " 問";
    }

    function draw() {
      const q = qs[state.i];
      const multi = q.type === "multi";
      const locked = state.locked[state.i];
      const ans = state.answers[state.i];

      body.innerHTML =
        (q.area ? '<span class="badge">' + PBM.esc(q.area) + "</span> " : "") +
        (q.difficulty ? '<span class="badge">難易度 ' + "★".repeat(q.difficulty) + "</span>" : "") +
        '<div class="q-stem">' + (window.marked ? marked.parseInline(PBM.esc(q.stem)) : PBM.esc(q.stem)) + "</div>" +
        (q.code ? '<pre><code>' + PBM.highlight(q.code, q.codeLang || "dax") + "</code></pre>" : "") +
        (multi ? '<p class="small muted">該当するものを<strong>すべて</strong>選んでください。</p>' : "") +
        '<div id="q-choices"></div>' +
        '<div id="q-explain"></div>';

      const ch = body.querySelector("#q-choices");
      q.choices.forEach(function (c, ci) {
        const b = document.createElement("button");
        b.className = "choice";
        b.type = "button";
        const selected = multi ? (Array.isArray(ans) && ans.indexOf(ci) >= 0) : ans === ci;
        if (selected) b.classList.add("sel");
        if (locked && opt.mode === "practice") {
          const correctIdx = multi ? (q.answer || []) : [q.answer];
          if (correctIdx.indexOf(ci) >= 0) b.classList.add("correct");
          else if (selected) b.classList.add("wrong");
          b.disabled = true;
        }
        b.innerHTML = '<span class="key">' + KEYS[ci] + "</span><span>" + PBM.esc(c) + "</span>";
        b.addEventListener("click", function () { pick(ci); });
        ch.appendChild(b);
      });

      if (locked && opt.mode === "practice" && q.explain) {
        body.querySelector("#q-explain").innerHTML =
          '<div class="explain"><h4>' + (isCorrect(q, ans) ? "✅ 正解" : "❌ 不正解") + " — 解説</h4>" +
          (window.marked ? PBM.markdown(q.explain) : "<p>" + PBM.esc(q.explain) + "</p>") +
          (q.ref ? '<p class="small"><a href="' + PBM.url("lesson.html?id=" + encodeURIComponent(q.ref)) + '">→ 関連レッスンを読む</a></p>' : "") +
          "</div>";
      }

      prevBtn.disabled = state.i === 0;
      const last = state.i === qs.length - 1;
      if (opt.mode === "practice" && !locked) {
        nextBtn.textContent = multi ? "解答する" : "答え合わせ";
        nextBtn.disabled = ans == null || (multi && ans.length === 0);
      } else {
        nextBtn.textContent = last ? "結果を見る" : "次へ →";
        nextBtn.disabled = false;
      }
      drawBar();
      root.scrollIntoView({ block: "start", behavior: "smooth" });
    }

    function pick(ci) {
      const q = qs[state.i];
      if (state.locked[state.i] && opt.mode === "practice") return;
      if (q.type === "multi") {
        const cur = Array.isArray(state.answers[state.i]) ? state.answers[state.i].slice() : [];
        const at = cur.indexOf(ci);
        if (at >= 0) cur.splice(at, 1); else cur.push(ci);
        state.answers[state.i] = cur;
      } else {
        state.answers[state.i] = ci;
      }
      draw();
    }

    nextBtn.addEventListener("click", function () {
      const q = qs[state.i];
      if (opt.mode === "practice" && !state.locked[state.i]) {
        state.locked[state.i] = true;
        PBM.track("quiz_answer", { quiz: quiz.id, q: q.id, correct: isCorrect(q, state.answers[state.i]) ? 1 : 0 });
        draw();
        return;
      }
      if (state.i === qs.length - 1) finish(false);
      else { state.i++; draw(); }
    });
    prevBtn.addEventListener("click", function () { if (state.i > 0) { state.i--; draw(); } });

    /* キーボード操作（PC） */
    document.addEventListener("keydown", function (e) {
      if (root.querySelector("#q-result").classList.contains("hidden") === false) return;
      const idx = KEYS.indexOf(e.key.toUpperCase());
      if (idx >= 0 && idx < qs[state.i].choices.length) { pick(idx); e.preventDefault(); }
      else if (e.key === "Enter" && !nextBtn.disabled) { nextBtn.click(); e.preventDefault(); }
      else if (e.key === "ArrowLeft" && !prevBtn.disabled) prevBtn.click();
    });

    function finish(timeUp) {
      if (timerId) clearInterval(timerId);
      const correct = qs.filter(function (q, i) { return isCorrect(q, state.answers[i]); }).length;
      const pct = Math.round((correct / qs.length) * 100);
      const minutes = Math.round((Date.now() - state.startedAt) / 60000);

      /* 領域別・スキル項目別スコア */
      const byArea = {}, bySkill = {};
      qs.forEach(function (q, i) {
        const ok = isCorrect(q, state.answers[i]);
        const a = q.area || "その他";
        byArea[a] = byArea[a] || { c: 0, t: 0 };
        byArea[a].t++; if (ok) byArea[a].c++;
        if (q.skill) {
          bySkill[q.skill] = bySkill[q.skill] || { c: 0, t: 0 };
          bySkill[q.skill].t++; if (ok) bySkill[q.skill].c++;
        }
      });

      const pass = pct >= ((window.PBM_CONFIG && window.PBM_CONFIG.quizPassLine) || 80);
      const el = root.querySelector("#q-result");
      el.classList.remove("hidden");
      root.querySelector(".q-card").classList.add("hidden");
      root.querySelector(".actionbar").classList.add("hidden");
      bar.classList.add("hidden");
      countEl.classList.add("hidden");

      el.innerHTML =
        '<div class="card result-hero">' +
          (timeUp ? '<p class="badge badge-warn">制限時間終了</p>' : "") +
          '<div class="score" style="color:var(--' + (pass ? "ok" : "ng") + ')">' + pct + "%</div>" +
          "<p>" + qs.length + " 問中 <strong>" + correct + "</strong> 問正解 ・ 所要 " + minutes + " 分</p>" +
          '<p class="badge ' + (pass ? "badge-ok" : "badge-ng") + '">' + (pass ? "合格ライン到達" : "もう一歩") + "</p>" +
        "</div>" +
        '<div class="card" style="margin-top:14px"><h3>領域別の正答率</h3>' +
          Object.keys(byArea).map(function (a) {
            const r = byArea[a], p = Math.round((r.c / r.t) * 100);
            return '<div class="area-row"><div><div class="nm">' + PBM.esc(a) + "</div>" +
              '<div class="bar"><span style="width:' + p + "%;background:var(--" + (p >= 80 ? "ok" : p >= 60 ? "warn" : "ng") + ')"></span></div></div>' +
              '<div class="small" style="text-align:right">' + r.c + "/" + r.t + "</div></div>";
          }).join("") +
        "</div>" +
        (Object.keys(bySkill).length
          ? '<div class="card" style="margin-top:14px"><h3>PL-300 スキル項目別（弱い順）</h3>' +
            Object.keys(bySkill).map(function (k) {
              const r = bySkill[k], pp = Math.round((r.c / r.t) * 100);
              return { k: k, r: r, p: pp };
            }).sort(function (a, b) { return a.p - b.p; }).map(function (x) {
              return '<div class="area-row"><div><div class="nm">' + PBM.esc(x.k) + "</div>" +
                '<div class="bar"><span style="width:' + x.p + "%;background:var(--" +
                (x.p >= 80 ? "ok" : x.p >= 60 ? "warn" : "ng") + ')"></span></div></div>' +
                '<div class="small" style="text-align:right">' + x.r.c + "/" + x.r.t + "</div></div>";
            }).join("") +
            '<p class="small muted" style="margin-top:10px">正答率の低い項目から復習すると、もっとも効率よく点が伸びます。</p>' +
            "</div>"
          : "") +
        '<div class="card" style="margin-top:14px"><h3>復習リスト（間違えた問題）</h3><div id="q-review"></div></div>' +
        '<div class="row" style="margin-top:16px">' +
          '<button class="btn btn-brand" id="q-retry">もう一度挑戦</button>' +
          '<a class="btn btn-ghost" href="' + PBM.url("roadmap.html") + '">ロードマップへ戻る</a>' +
        "</div>";

      const rv = el.querySelector("#q-review");
      const wrong = qs.map(function (q, i) { return { q: q, i: i }; }).filter(function (x) { return !isCorrect(x.q, state.answers[x.i]); });
      if (!wrong.length) rv.innerHTML = '<p class="muted">全問正解です。おみごと。</p>';
      else rv.innerHTML = wrong.map(function (x) {
        const q = x.q;
        const correctTxt = (q.type === "multi" ? (q.answer || []) : [q.answer]).map(function (ci) { return KEYS[ci] + ". " + q.choices[ci]; }).join(" / ");
        return '<details style="margin:10px 0"><summary style="cursor:pointer;font-weight:650">' + PBM.esc(q.stem) + "</summary>" +
          '<div class="explain"><p><strong>正解：</strong>' + PBM.esc(correctTxt) + "</p>" +
          (q.explain ? PBM.markdown(q.explain) : "") +
          (q.ref ? '<p class="small"><a href="' + PBM.url("lesson.html?id=" + encodeURIComponent(q.ref)) + '">→ 関連レッスンで復習</a></p>' : "") +
          "</div></details>";
      }).join("");

      el.querySelector("#q-retry").addEventListener("click", function () { location.reload(); });

      if (opt.onFinish) opt.onFinish({ correct: correct, total: qs.length, pct: pct, byArea: byArea, bySkill: bySkill, minutes: minutes });
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    draw();
  };
})();
