/**
 * 全ページのスモークテスト（Playwright が必要）
 *
 *     cd docs && python3 -m http.server 8123   # 別ターミナル
 *     node tests/smoke.mjs
 */
import { chromium } from 'playwright';

const BASE = 'http://localhost:8123';
const PAGES = [
  ['index.html', '#levels a'],
  ['roadmap.html', '.road-node .lesson-row'],
  ['lesson.html?id=L201', '.prose h2'],
  ['lesson.html?id=L303', '.prose pre code.language-dax'],
  ['labs.html', '#labs a'],
  ['lab.html?id=LAB04', '.prose h2'],
  ['quizzes.html', '#list a.lesson-row'],
  ['quiz.html?id=L302', '.choice'],
  ['exam.html', '#start'],
  ['glossary.html', '#list .card'],
  ['progress.html', '#levels .area-row'],
  ['admin.html', '#btn-login'],
  ['404.html', 'h1'],
];

const browser = await chromium.launch();
let fail = 0;
for (const [path, sel] of PAGES) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  const errs = [];
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  page.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
  try {
    await page.goto(`${BASE}/${path}`, { waitUntil: 'networkidle', timeout: 20000 });
    await page.waitForSelector(sel, { timeout: 8000 });
    const title = await page.title();
    const hasHeader = await page.$('.site-header') !== null;
    const n = await page.$$eval(sel, els => els.length);
    // 外部CDNへ到達できない環境でもサイト自体は動作するため、その種のエラーは除外する
    const bad = errs.filter(e => !/favicon/i.test(e) && !/ERR_TUNNEL|ERR_NAME_NOT_RESOLVED|ERR_INTERNET_DISCONNECTED|ERR_CONNECTION|net::ERR_/i.test(e));
    console.log(`${bad.length ? 'FAIL' : ' OK '} ${path.padEnd(26)} sel=${n} header=${hasHeader} title="${title.slice(0,40)}"`);
    if (bad.length) { fail++; bad.slice(0,3).forEach(e => console.log('       ! ' + e.slice(0,180))); }
  } catch (e) {
    fail++;
    console.log(`FAIL ${path.padEnd(26)} ${String(e.message).split('\n')[0].slice(0,140)}`);
    errs.slice(0,3).forEach(x => console.log('       ! ' + x.slice(0,180)));
  }
  await ctx.close();
}
await browser.close();
console.log(fail ? `\n${fail} page(s) failed` : '\nAll pages OK');
process.exit(fail ? 1 : 0);
