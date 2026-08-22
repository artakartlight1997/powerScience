/**
 * v2（初級コース）の表示テスト
 *   cd docs && python3 -m http.server 8124
 *   node tests/v2-smoke.mjs
 */
import { chromium } from 'playwright';
const BASE = 'http://localhost:8124';
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
const page = await ctx.newPage();
const errs = [];
page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
page.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE ' + m.text()); });
const ok = (label, cond, extra = '') => console.log(`${cond ? ' OK ' : 'FAIL'} ${label} ${extra}`);
let bad = 0;
const chk = (label, cond, extra) => { ok(label, cond, extra); if (!cond) bad++; };

// 目次
await page.goto(`${BASE}/index.html`, { waitUntil: 'networkidle' });
const chapters = await page.$$eval('.chapter', e => e.length);
const lessons  = await page.$$eval('.lesson-list a', e => e.length);
chk('目次が出る', chapters >= 5 && lessons >= 20, `章=${chapters} レッスン=${lessons}`);

// 各レッスン
const ids = await page.$$eval('.lesson-list a', as => as.map(a => new URL(a.href).searchParams.get('id')));
let missing = [], figTotal = 0, figErr = 0, overflow = 0;
for (const id of ids) {
  await page.goto(`${BASE}/lesson.html?id=${id}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(350);
  const txt = await page.$eval('#body', e => e.textContent.trim());
  if (/本文がまだありません/.test(txt) || txt.length < 200) { missing.push(id); continue; }
  figTotal += await page.$$eval('.pbm-figure[data-rendered]', e => e.length);
  figErr   += await page.$$eval('.pbm-figure-error, .fig-error', e => e.length);
  const w = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  if (w > 0) { overflow++; console.log(`     はみ出し ${id}: ${w}px`); }
}
chk('全レッスンに本文がある', missing.length === 0, missing.length ? '未作成: ' + missing.join(' ') : `${ids.length}本`);
chk('図が壊れていない', figErr === 0, `図=${figTotal} エラー=${figErr}`);
chk('スマホ幅で横にはみ出さない', overflow === 0, `はみ出し=${overflow}ページ`);

// 読み終わりの記録
await page.goto(`${BASE}/lesson.html?id=L101`, { waitUntil: 'networkidle' });
await page.click('#done');
const saved = await page.evaluate(() => localStorage.getItem('td.done'));
chk('読み終わりが記録される', !!saved && saved.includes('L101'), saved || '');

chk('ページの実行時エラーがない', errs.length === 0, errs.slice(0, 3).join(' | '));
await browser.close();
console.log(bad ? `\n${bad} 件の失敗` : '\nすべて成功');
process.exit(bad ? 1 : 0);
