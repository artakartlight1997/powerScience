/* ============================================================
   PBM Analytics — 学習ログ / アクセス統計クライアント
   ・IPアドレスは送信しません（国・地域はサーバ側でCloudflareが付与）
   ・PBM_CONFIG.analyticsEndpoint が空なら完全に無効（送信ゼロ）
   ・localStorage に "pbm.optout" = "1" があればユーザー側で無効化
   ============================================================ */
(function () {
  "use strict";
  const CFG = window.PBM_CONFIG || {};
  const PBM = (window.PBM = window.PBM || {});

  const ENDPOINT = (CFG.analyticsEndpoint || "").replace(/\/$/, "");
  const OPTOUT = () => localStorage.getItem("pbm.optout") === "1";
  const ENABLED = () => !!ENDPOINT && CFG.analyticsEnabled !== false && !OPTOUT();

  PBM.optOut = function (yes) {
    if (yes === false) localStorage.removeItem("pbm.optout");
    else localStorage.setItem("pbm.optout", "1");
  };
  PBM.isOptedOut = OPTOUT;

  /* 端末ごとの匿名ID（個人情報を含まないランダム値） */
  function anonId() {
    let v = localStorage.getItem("pbm.vid");
    if (!v) {
      v = (crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2) + Date.now().toString(36));
      localStorage.setItem("pbm.vid", v);
    }
    return v;
  }
  /* セッションID（タブを閉じるまで） */
  function sessionId() {
    let v = sessionStorage.getItem("pbm.sid");
    if (!v) {
      v = (crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2) + Date.now().toString(36));
      sessionStorage.setItem("pbm.sid", v);
    }
    return v;
  }

  const startedAt = Date.now();
  let lastBeat = startedAt;

  function payload(event, meta) {
    return {
      event: event,
      ts: Date.now(),
      vid: anonId(),
      sid: sessionId(),
      path: location.pathname.replace(/^.*\/docs\//, "/"),
      page: (location.pathname.split("/").pop() || "index.html"),
      query: location.search.slice(0, 200),
      title: document.title.slice(0, 160),
      ref: (document.referrer || "").slice(0, 200),
      tz: (Intl.DateTimeFormat().resolvedOptions().timeZone || ""),
      lang: navigator.language || "",
      screen: innerWidth + "x" + innerHeight,
      mobile: matchMedia("(max-width: 859px)").matches ? 1 : 0,
      meta: meta || {}
    };
  }

  function send(event, meta, useBeacon) {
    if (!ENABLED()) return;
    const body = JSON.stringify(payload(event, meta));
    try {
      if (useBeacon && navigator.sendBeacon) {
        navigator.sendBeacon(ENDPOINT + "/collect", new Blob([body], { type: "application/json" }));
      } else {
        fetch(ENDPOINT + "/collect", {
          method: "POST", body: body, keepalive: true,
          headers: { "Content-Type": "application/json" }
        }).catch(() => {});
      }
    } catch (e) { /* 計測失敗は学習体験を止めない */ }
  }

  PBM.track = function (event, meta) { send(event, meta, false); };

  /* ページビュー */
  addEventListener("DOMContentLoaded", function () { send("pageview", {}); });

  /* 滞在時間（heartbeat + 離脱時） */
  const hb = Math.max(10, CFG.heartbeatSeconds || 30) * 1000;
  setInterval(function () {
    if (document.visibilityState !== "visible") return;
    const now = Date.now();
    send("heartbeat", { sec: Math.round((now - lastBeat) / 1000), total: Math.round((now - startedAt) / 1000) });
    lastBeat = now;
  }, hb);

  addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden") {
      send("leave", { sec: Math.round((Date.now() - startedAt) / 1000) }, true);
    }
  });
  addEventListener("pagehide", function () {
    send("leave", { sec: Math.round((Date.now() - startedAt) / 1000) }, true);
  });
})();
