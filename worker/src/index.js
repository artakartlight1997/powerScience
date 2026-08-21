/**
 * Aki’s Power BI 道場 — アクセス/学習ログ収集 API
 * Cloudflare Workers + D1
 *
 *  POST /collect          … サイトからのイベント受信（認証不要・公開）
 *  POST /admin/login      … パスワード認証 → 期限付きトークン発行
 *  GET  /admin/summary    … 集計データ（要トークン）
 *  GET  /admin/recent     … 直近イベント（要トークン）
 *  GET  /admin/export.csv … CSVエクスポート（要トークン）
 *  GET  /health           … 死活確認
 *
 * 管理画面のパスワードは `wrangler secret put ADMIN_PASSWORD` で設定します。
 * IPアドレスは一切保存しません。国・地域は Cloudflare が付与する
 * リクエストメタデータ(request.cf)から取得しています。
 */

const enc = new TextEncoder();

/* ---------------- CORS ---------------- */
function corsHeaders(request, env) {
  const origin = request.headers.get("Origin") || "";
  const allowed = (env.ALLOWED_ORIGINS || "*").split(",").map((s) => s.trim()).filter(Boolean);
  let allow = "";
  if (allowed.includes("*")) allow = origin || "*";
  else if (allowed.includes(origin)) allow = origin;
  return {
    "Access-Control-Allow-Origin": allow || "null",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin"
  };
}
function json(data, request, env, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...corsHeaders(request, env) }
  });
}

/* ---------------- 認証トークン（HMAC-SHA256） ---------------- */
async function hmac(key, msg) {
  const k = await crypto.subtle.importKey("raw", enc.encode(key), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", k, enc.encode(msg));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
function timingSafeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}
async function issueToken(env) {
  const exp = Date.now() + Number(env.SESSION_HOURS || 12) * 3600 * 1000;
  const sig = await hmac(env.ADMIN_PASSWORD, "pbm-admin:" + exp);
  return exp + "." + sig;
}
async function verifyToken(env, token) {
  if (!token || !env.ADMIN_PASSWORD) return false;
  const [expStr, sig] = String(token).split(".");
  const exp = Number(expStr);
  if (!exp || !sig || Date.now() > exp) return false;
  return timingSafeEqual(sig, await hmac(env.ADMIN_PASSWORD, "pbm-admin:" + exp));
}
async function requireAuth(request, env) {
  const auth = request.headers.get("Authorization") || "";
  const token = auth.replace(/^Bearer\s+/i, "") || new URL(request.url).searchParams.get("t") || "";
  return verifyToken(env, token);
}

/* ---------------- User-Agent の粗い分類 ---------------- */
function parseUA(ua) {
  ua = ua || "";
  let browser = "その他";
  if (/Edg\//.test(ua)) browser = "Edge";
  else if (/OPR\/|Opera/.test(ua)) browser = "Opera";
  else if (/Chrome\//.test(ua) && !/Chromium/.test(ua)) browser = "Chrome";
  else if (/Firefox\//.test(ua)) browser = "Firefox";
  else if (/Safari\//.test(ua) && /Version\//.test(ua)) browser = "Safari";
  let os = "その他";
  if (/Windows NT/.test(ua)) os = "Windows";
  else if (/iPhone|iPad|iPod/.test(ua)) os = "iOS";
  else if (/Android/.test(ua)) os = "Android";
  else if (/Mac OS X/.test(ua)) os = "macOS";
  else if (/Linux/.test(ua)) os = "Linux";
  return { browser, os };
}

const clip = (v, n) => (v == null ? null : String(v).slice(0, n));

/* ---------------- /collect ---------------- */
async function handleCollect(request, env) {
  let b;
  try {
    const raw = await request.text();
    if (raw.length > 8000) return new Response("payload too large", { status: 413, headers: corsHeaders(request, env) });
    b = JSON.parse(raw);
  } catch (e) {
    return new Response("bad request", { status: 400, headers: corsHeaders(request, env) });
  }
  if (!b || typeof b.event !== "string") {
    return new Response("bad request", { status: 400, headers: corsHeaders(request, env) });
  }

  const cf = request.cf || {};
  const now = new Date();
  const ua = parseUA(request.headers.get("User-Agent"));
  const meta = b.meta && typeof b.meta === "object" ? b.meta : {};

  // リファラは「どこ経由で来たか」だけ分かればよいのでオリジンのみ保存
  let ref = null;
  try { ref = b.ref ? new URL(b.ref).origin : null; } catch (e) { ref = null; }

  const seconds = Number.isFinite(meta.sec) ? Math.min(Math.round(meta.sec), 86400)
                : Number.isFinite(meta.total) ? Math.min(Math.round(meta.total), 86400) : null;

  await env.DB.prepare(
    `INSERT INTO events (ts,day,hour,event,vid,sid,page,path,title,ref,
       country,region,city,continent,colo,tz,lang,mobile,screen,browser,os,
       lesson,quiz,score,seconds,meta)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`
  ).bind(
    now.getTime(),
    now.toISOString().slice(0, 10),
    now.getUTCHours(),
    clip(b.event, 40),
    clip(b.vid, 64), clip(b.sid, 64),
    clip(b.page, 80), clip(b.path, 200), clip(b.title, 160), clip(ref, 120),
    clip(cf.country, 8), clip(cf.regionCode || cf.region, 60), clip(cf.city, 80),
    clip(cf.continent, 8), clip(cf.colo, 8),
    clip(b.tz, 60), clip(b.lang, 20),
    b.mobile ? 1 : 0, clip(b.screen, 20),
    ua.browser, ua.os,
    clip(meta.lesson || meta.lab, 20), clip(meta.quiz, 20),
    Number.isFinite(meta.score) ? Math.round(meta.score) : null,
    seconds,
    clip(JSON.stringify(meta), 900)
  ).run();

  return new Response(null, { status: 204, headers: corsHeaders(request, env) });
}

/* ---------------- 集計 ---------------- */
async function handleSummary(request, env) {
  const u = new URL(request.url);
  const days = Math.min(Math.max(parseInt(u.searchParams.get("days") || "30", 10), 1), 400);
  const since = Date.now() - days * 86400000;
  const country = u.searchParams.get("country") || null;

  const where = country ? "ts >= ? AND country = ?" : "ts >= ?";
  const args = country ? [since, country] : [since];
  const q = (sql, extra = []) => env.DB.prepare(sql).bind(...args, ...extra).all();

  const [overview, byDay, byHour, byCountry, byRegion, byCity, byPage, byLesson,
         byDevice, byBrowser, byRef, byTz, quizzes, exams, retention] = await Promise.all([
    q(`SELECT COUNT(*) AS events,
              SUM(CASE WHEN event='pageview' THEN 1 ELSE 0 END) AS pageviews,
              COUNT(DISTINCT vid) AS visitors,
              COUNT(DISTINCT sid) AS sessions,
              COUNT(DISTINCT country) AS countries
       FROM events WHERE ${where}`),
    q(`SELECT day, COUNT(DISTINCT vid) AS visitors,
              SUM(CASE WHEN event='pageview' THEN 1 ELSE 0 END) AS pageviews
       FROM events WHERE ${where} GROUP BY day ORDER BY day`),
    q(`SELECT hour, COUNT(*) AS n FROM events WHERE ${where} AND event='pageview' GROUP BY hour ORDER BY hour`),
    q(`SELECT COALESCE(country,'不明') AS k, COUNT(DISTINCT vid) AS visitors,
              SUM(CASE WHEN event='pageview' THEN 1 ELSE 0 END) AS pageviews
       FROM events WHERE ${where} GROUP BY k ORDER BY pageviews DESC LIMIT 50`),
    q(`SELECT COALESCE(country,'?')||' / '||COALESCE(region,'不明') AS k, COUNT(DISTINCT vid) AS visitors,
              SUM(CASE WHEN event='pageview' THEN 1 ELSE 0 END) AS pageviews
       FROM events WHERE ${where} GROUP BY k ORDER BY pageviews DESC LIMIT 40`),
    q(`SELECT COALESCE(city,'不明') AS k, COUNT(DISTINCT vid) AS visitors,
              SUM(CASE WHEN event='pageview' THEN 1 ELSE 0 END) AS pageviews
       FROM events WHERE ${where} GROUP BY k ORDER BY pageviews DESC LIMIT 40`),
    q(`SELECT COALESCE(page,'不明') AS k, COUNT(*) AS pageviews, COUNT(DISTINCT vid) AS visitors
       FROM events WHERE ${where} AND event='pageview'
       GROUP BY k ORDER BY pageviews DESC LIMIT 40`),
    q(`SELECT lesson AS k, COUNT(*) AS n, COUNT(DISTINCT vid) AS visitors
       FROM events WHERE ${where} AND event='lesson_complete' AND lesson IS NOT NULL
       GROUP BY k ORDER BY n DESC LIMIT 50`),
    q(`SELECT CASE mobile WHEN 1 THEN 'スマホ' ELSE 'PC/タブレット' END AS k,
              COUNT(DISTINCT vid) AS visitors, COUNT(*) AS events
       FROM events WHERE ${where} GROUP BY k`),
    q(`SELECT COALESCE(browser,'?')||' / '||COALESCE(os,'?') AS k, COUNT(DISTINCT vid) AS visitors
       FROM events WHERE ${where} GROUP BY k ORDER BY visitors DESC LIMIT 20`),
    q(`SELECT COALESCE(ref,'直接アクセス') AS k, COUNT(DISTINCT sid) AS sessions
       FROM events WHERE ${where} AND event='pageview' GROUP BY k ORDER BY sessions DESC LIMIT 20`),
    q(`SELECT COALESCE(tz,'不明') AS k, COUNT(DISTINCT vid) AS visitors
       FROM events WHERE ${where} GROUP BY k ORDER BY visitors DESC LIMIT 20`),
    q(`SELECT quiz AS k, COUNT(*) AS attempts, ROUND(AVG(score),1) AS avg_score, MIN(score) AS min_score
       FROM events WHERE ${where} AND event='quiz_result' AND quiz IS NOT NULL
       GROUP BY k ORDER BY avg_score ASC LIMIT 50`),
    q(`SELECT day, COUNT(*) AS attempts, ROUND(AVG(score),1) AS avg_score
       FROM events WHERE ${where} AND event='exam_result' GROUP BY day ORDER BY day`),
    q(`SELECT ROUND(AVG(seconds),0) AS avg_seconds
       FROM events WHERE ${where} AND event='leave' AND seconds IS NOT NULL AND seconds < 7200`)
  ]);

  return json({
    days,
    generatedAt: new Date().toISOString(),
    overview: overview.results[0] || {},
    avgSeconds: (retention.results[0] || {}).avg_seconds || 0,
    byDay: byDay.results, byHour: byHour.results,
    byCountry: byCountry.results, byRegion: byRegion.results, byCity: byCity.results,
    byPage: byPage.results, byLesson: byLesson.results,
    byDevice: byDevice.results, byBrowser: byBrowser.results,
    byRef: byRef.results, byTz: byTz.results,
    quizzes: quizzes.results, exams: exams.results
  }, request, env);
}

async function handleRecent(request, env) {
  const u = new URL(request.url);
  const limit = Math.min(Math.max(parseInt(u.searchParams.get("limit") || "100", 10), 1), 500);
  const r = await env.DB.prepare(
    `SELECT ts, event, page, country, region, city, mobile, browser, os, lesson, quiz, score, seconds
     FROM events ORDER BY ts DESC LIMIT ?`
  ).bind(limit).all();
  return json({ rows: r.results }, request, env);
}

async function handleExport(request, env) {
  const u = new URL(request.url);
  const days = Math.min(Math.max(parseInt(u.searchParams.get("days") || "30", 10), 1), 400);
  const since = Date.now() - days * 86400000;
  const r = await env.DB.prepare(
    `SELECT ts, day, hour, event, vid, sid, page, country, region, city, colo, tz, lang,
            mobile, browser, os, lesson, quiz, score, seconds
     FROM events WHERE ts >= ? ORDER BY ts DESC LIMIT 100000`
  ).bind(since).all();
  const cols = ["ts","day","hour","event","vid","sid","page","country","region","city","colo","tz","lang","mobile","browser","os","lesson","quiz","score","seconds"];
  const esc = (v) => (v == null ? "" : /[",\n]/.test(String(v)) ? '"' + String(v).replace(/"/g, '""') + '"' : String(v));
  const csv = "﻿" + cols.join(",") + "\n" + r.results.map((row) => cols.map((c) => esc(row[c])).join(",")).join("\n");
  return new Response(csv, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": 'attachment; filename="pbm-analytics.csv"',
      ...corsHeaders(request, env)
    }
  });
}

/* ---------------- ルーティング ---------------- */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(request, env) });
    if (path === "/health") return json({ ok: true, hasPassword: !!env.ADMIN_PASSWORD }, request, env);

    if (path === "/collect" && request.method === "POST") return handleCollect(request, env);

    if (path === "/admin/login" && request.method === "POST") {
      if (!env.ADMIN_PASSWORD) return json({ error: "ADMIN_PASSWORD が未設定です。wrangler secret put ADMIN_PASSWORD を実行してください。" }, request, env, 500);
      let body = {};
      try { body = await request.json(); } catch (e) {}
      // 総当たり対策の簡易ディレイ
      await new Promise((r) => setTimeout(r, 400));
      if (!timingSafeEqual(String(body.password || ""), env.ADMIN_PASSWORD)) {
        return json({ error: "パスワードが違います" }, request, env, 401);
      }
      return json({ token: await issueToken(env), expiresIn: Number(env.SESSION_HOURS || 12) * 3600 }, request, env);
    }

    if (path.startsWith("/admin/")) {
      if (!(await requireAuth(request, env))) return json({ error: "認証が必要です" }, request, env, 401);
      if (path === "/admin/summary") return handleSummary(request, env);
      if (path === "/admin/recent") return handleRecent(request, env);
      if (path === "/admin/export.csv") return handleExport(request, env);
    }

    return json({ error: "not found" }, request, env, 404);
  },

  /* 保持期間を過ぎたログを削除 */
  async scheduled(event, env, ctx) {
    const keep = Number(env.RETENTION_DAYS || 400);
    const cutoff = Date.now() - keep * 86400000;
    ctx.waitUntil(env.DB.prepare("DELETE FROM events WHERE ts < ?").bind(cutoff).run());
  }
};
