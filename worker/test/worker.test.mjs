/**
 * Worker の単体テスト（依存パッケージなし）
 *
 *     node worker/test/worker.test.mjs
 *
 * D1 をモックしているため、Cloudflare へのデプロイなしで
 * ルーティング・認証・CORS・SQLのバインド数を検証できます。
 */
import worker from '../src/index.js';

// ---- D1 のモック ----
const store = [];
let lastSQL = null, lastBind = null;
const DB = {
  prepare(sql) {
    lastSQL = sql;
    const stmt = {
      _args: [],
      bind(...a) { this._args = a; lastBind = a; return this; },
      async run() {
        if (/^INSERT/i.test(sql)) {
          const cols = sql.match(/INSERT INTO events \(([\s\S]*?)\)\s*VALUES/i)[1]
                          .split(',').map(s => s.trim()).filter(Boolean);
          const ph = (sql.match(/VALUES\s*\(([^)]*)\)/i)[1].match(/\?/g) || []).length;
          if (cols.length !== ph) throw new Error(`column/placeholder mismatch: ${cols.length} cols vs ${ph} placeholders`);
          if (this._args.length !== ph) throw new Error(`bind arity mismatch: ${this._args.length} args vs ${ph} placeholders`);
          store.push(Object.fromEntries(cols.map((c, i) => [c, this._args[i]])));
        }
        return { success: true };
      },
      async all() { return { results: [{ k: 'x', pageviews: 1, visitors: 1, events: 1, sessions: 1, countries: 1, avg_seconds: 42 }] }; }
    };
    return stmt;
  }
};
const env = { DB, ADMIN_PASSWORD: 'sup3r-secret', ALLOWED_ORIGINS: 'https://example.github.io', SESSION_HOURS: '12', RETENTION_DAYS: '400' };

let failures = 0;
const ok = (l, c, x = '') => { if (!c) failures++; console.log(`${c ? ' OK ' : 'FAIL'} ${l} ${x}`); };
const req = (path, init = {}, cf = {}) => {
  const r = new Request('https://api.example.com' + path, init);
  Object.defineProperty(r, 'cf', { value: cf, configurable: true });
  return r;
};
const ORIGIN = { Origin: 'https://example.github.io' };

// 1. health
let res = await worker.fetch(req('/health'), env);
let body = await res.json();
ok('GET /health', res.status === 200 && body.ok === true && body.hasPassword === true);

// 2. CORS: 許可オリジン
res = await worker.fetch(req('/health', { headers: ORIGIN }), env);
ok('CORS allows configured origin', res.headers.get('Access-Control-Allow-Origin') === 'https://example.github.io');

// 3. CORS: 未許可オリジン
res = await worker.fetch(req('/health', { headers: { Origin: 'https://evil.example' } }), env);
ok('CORS rejects unknown origin', res.headers.get('Access-Control-Allow-Origin') === 'null',
   res.headers.get('Access-Control-Allow-Origin'));

// 4. preflight
res = await worker.fetch(req('/collect', { method: 'OPTIONS', headers: ORIGIN }), env);
ok('OPTIONS preflight', res.status === 204);

// 5. /collect 正常系（cf の位置情報が保存されるか / IPは保存しないか）
res = await worker.fetch(req('/collect', {
  method: 'POST', headers: { ...ORIGIN, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1', 'CF-Connecting-IP': '203.0.113.9' },
  body: JSON.stringify({ event: 'pageview', vid: 'v1', sid: 's1', page: 'lesson.html', path: '/lesson.html',
    title: 'L201', ref: 'https://www.google.com/search?q=powerbi', tz: 'Asia/Tokyo', lang: 'ja', mobile: 1,
    screen: '390x844', meta: { lesson: 'L201' } })
}, { country: 'JP', regionCode: '13', city: 'Shinjuku', continent: 'AS', colo: 'NRT' }), env);
const row = store[store.length - 1];
ok('POST /collect stores event', res.status === 204 && row && row.event === 'pageview');
ok('geo from request.cf', row.country === 'JP' && row.region === '13' && row.city === 'Shinjuku' && row.colo === 'NRT');
ok('UA parsed', row.browser === 'Safari' && row.os === 'iOS', `${row.browser}/${row.os}`);
ok('referrer reduced to origin', row.ref === 'https://www.google.com', row.ref);
ok('no IP column stored', !Object.keys(row).some(k => /ip/i.test(k)), Object.keys(row).filter(k=>/ip/i.test(k)).join());
ok('day/hour derived', /^\d{4}-\d{2}-\d{2}$/.test(row.day) && Number.isInteger(row.hour));

// 6. /collect 学習イベント
await worker.fetch(req('/collect', { method: 'POST', headers: { ...ORIGIN, 'Content-Type': 'application/json' },
  body: JSON.stringify({ event: 'quiz_result', vid: 'v1', sid: 's1', meta: { quiz: 'L302', score: 75 } }) }, { country: 'US' }), env);
const r2 = store[store.length - 1];
ok('quiz_result captures score', r2.quiz === 'L302' && r2.score === 75);

// 7. 不正な body
res = await worker.fetch(req('/collect', { method: 'POST', headers: ORIGIN, body: 'not json' }), env);
ok('rejects malformed body', res.status === 400, String(res.status));
res = await worker.fetch(req('/collect', { method: 'POST', headers: ORIGIN, body: JSON.stringify({ nope: 1 }) }), env);
ok('rejects missing event', res.status === 400, String(res.status));
res = await worker.fetch(req('/collect', { method: 'POST', headers: ORIGIN, body: 'x'.repeat(9000) }), env);
ok('rejects oversized payload', res.status === 413, String(res.status));

// 8. 認証なしで管理APIを叩く
res = await worker.fetch(req('/admin/summary', { headers: ORIGIN }), env);
ok('admin requires auth', res.status === 401);

// 9. 誤ったパスワード
res = await worker.fetch(req('/admin/login', { method: 'POST', headers: { ...ORIGIN, 'Content-Type': 'application/json' },
  body: JSON.stringify({ password: 'wrong' }) }), env);
ok('login rejects wrong password', res.status === 401);

// 10. 正しいパスワード → トークン
res = await worker.fetch(req('/admin/login', { method: 'POST', headers: { ...ORIGIN, 'Content-Type': 'application/json' },
  body: JSON.stringify({ password: 'sup3r-secret' }) }), env);
const login = await res.json();
ok('login issues token', res.status === 200 && typeof login.token === 'string' && login.token.includes('.'));

// 11. トークンで管理API
res = await worker.fetch(req('/admin/summary?days=30', { headers: { ...ORIGIN, Authorization: 'Bearer ' + login.token } }), env);
const sum = await res.json();
ok('summary with token', res.status === 200 && sum.days === 30 && !!sum.overview && Array.isArray(sum.byCountry));

// 12. 改ざんトークン
const tampered = login.token.split('.')[0] + '.' + 'f'.repeat(64);
res = await worker.fetch(req('/admin/summary', { headers: { ...ORIGIN, Authorization: 'Bearer ' + tampered } }), env);
ok('tampered token rejected', res.status === 401);

// 13. 期限切れトークン
res = await worker.fetch(req('/admin/summary', { headers: { ...ORIGIN, Authorization: 'Bearer ' + (Date.now() - 1000) + '.' + 'a'.repeat(64) } }), env);
ok('expired token rejected', res.status === 401);

// 14. クエリ文字列のトークン（CSVダウンロード用）
res = await worker.fetch(req('/admin/export.csv?days=7&t=' + encodeURIComponent(login.token), { headers: ORIGIN }), env);
const csv = await res.text();
ok('csv export via query token', res.status === 200 && res.headers.get('Content-Type').includes('text/csv') && csv.includes('event'),
   res.headers.get('Content-Disposition'));

// 15. recent
res = await worker.fetch(req('/admin/recent?limit=5', { headers: { ...ORIGIN, Authorization: 'Bearer ' + login.token } }), env);
ok('recent with token', res.status === 200);

// 16. days のクランプ
res = await worker.fetch(req('/admin/summary?days=99999', { headers: { ...ORIGIN, Authorization: 'Bearer ' + login.token } }), env);
ok('days clamped', (await res.json()).days === 400);

// 17. 未知のパス
res = await worker.fetch(req('/nope', { headers: ORIGIN }), env);
ok('404 for unknown path', res.status === 404);

// 18. ADMIN_PASSWORD 未設定
res = await worker.fetch(req('/admin/login', { method: 'POST', headers: { ...ORIGIN, 'Content-Type': 'application/json' },
  body: JSON.stringify({ password: 'x' }) }), { ...env, ADMIN_PASSWORD: undefined });
const nop = await res.json();
ok('clear error when password unset', res.status === 500 && nop.error.includes('ADMIN_PASSWORD'));

// 19. scheduled（保持期間の削除）
let deleted = null;
const env2 = { ...env, DB: { prepare(sql) { deleted = sql; return { bind: () => ({ run: async () => ({}) }) }; } } };
await worker.scheduled({}, env2, { waitUntil: p => p });
ok('scheduled purges old rows', /DELETE FROM events WHERE ts </.test(deleted || ''), deleted);

// 20. ワイルドカードオリジン
res = await worker.fetch(req('/health', { headers: { Origin: 'https://anything.test' } }), { ...env, ALLOWED_ORIGINS: '*' });
ok('wildcard origin allowed', res.headers.get('Access-Control-Allow-Origin') === 'https://anything.test');

console.log(failures ? `\n${failures} 件失敗` : '\nすべて成功');
process.exit(failures ? 1 : 0);
