/**
 * 機能テスト（Playwright が必要・モバイル幅で実行）
 *
 *     cd docs && python3 -m http.server 8123   # 別ターミナル
 *     node tests/functional.mjs
 */
import { chromium } from 'playwright';
const BASE = 'http://localhost:8123';
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
const page = await ctx.newPage();
const errs = [];
page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
const ok = (label, cond, extra='') => console.log(`${cond ? ' OK ' : 'FAIL'} ${label} ${extra}`);

// --- 1. 図解の描画（Mermaidは廃止済み） ---
await page.goto(`${BASE}/lesson.html?id=L0601`, { waitUntil: 'networkidle' });
await page.waitForTimeout(1500);
const figs = await page.$$eval('.pbm-figure[data-rendered]', e => e.length);
const figErr = await page.$$eval('.pbm-figure-error', e => e.length);
ok('figures rendered (no mermaid)', figs > 0 && figErr === 0, `figures=${figs} errors=${figErr}`);
const codeTok = await page.$$eval('.prose .tok-f', e => e.length);
ok('markdown + callouts render', (await page.$$eval('.prose .callout', e=>e.length)) > 0,
   `callouts=${await page.$$eval('.prose .callout', e=>e.length)} tables=${await page.$$eval('.prose table', e=>e.length)}`);

// --- 2. モバイルでのハンバーガーメニュー ---
const menuVisible = await page.isVisible('#pbm-menu');
await page.click('#pbm-menu');
const drawerOpen = await page.isVisible('#pbm-drawer a');
ok('mobile menu works', menuVisible && drawerOpen);
await page.click('#pbm-menu');

// --- 3. 横スクロールが出ていないか（モバイル） ---
const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
ok('no horizontal overflow (390px)', overflow <= 1, `overflow=${overflow}px`);

// --- 4. レッスン完了 → 進捗保存 ---
await page.click('#btn-done');
await page.waitForTimeout(700);
const stored = await page.evaluate(() => JSON.parse(localStorage.getItem('pbm.progress.v1') || '{}'));
ok('lesson completion persisted', !!(stored.lessons && stored.lessons.L0601 && stored.lessons.L0601.done));

// --- 5. ロードマップに反映 ---
await page.goto(`${BASE}/roadmap.html`, { waitUntil: 'networkidle' });
const checked = await page.$$eval('.check.on', e => e.length);
const pct = await page.textContent('#ring-pct');
ok('roadmap reflects progress', checked === 1, `checked=${checked} ring=${pct}`);

// --- 6. クイズを1問解く ---
await page.goto(`${BASE}/quiz.html?id=L0801`, { waitUntil: 'networkidle' });
await page.waitForSelector('.choice');
const stem = (await page.textContent('.q-stem')).slice(0, 30);
await page.click('.choice >> nth=0');
const nextTxt = await page.textContent('#q-next');
await page.click('#q-next');
await page.waitForTimeout(300);
const graded = await page.$$eval('.choice.correct', e => e.length); // multi設問では複数が正解
const explained = await page.$$eval('.explain', e => e.length);
ok('quiz grading + explanation', graded >= 1 && explained === 1, `btn="${nextTxt}" stem="${stem}…"`);

// --- 7. クイズを最後まで解く → 結果画面 ---
for (let i = 0; i < 20; i++) {
  const hidden = await page.$eval('#q-result', el => el.classList.contains('hidden'));
  if (!hidden) break;
  const disabled = await page.$eval('#q-next', el => el.disabled);
  if (disabled) await page.click('.choice:not([disabled]) >> nth=0');
  await page.click('#q-next');
  await page.waitForTimeout(120);
}
const scoreTxt = await page.textContent('.result-hero .score').catch(() => null);
const areas = await page.$$eval('#q-result .area-row', e => e.length).catch(() => 0);
ok('quiz result screen', !!scoreTxt && areas > 0, `score=${scoreTxt} areaRows=${areas}`);
const qres = await page.evaluate(() => JSON.parse(localStorage.getItem('pbm.progress.v1')||'{}').quizzes);
ok('quiz result persisted', !!(qres && qres.L0801), JSON.stringify(qres || {}));

// --- 8. 模擬試験（タイマー動作） ---
await page.goto(`${BASE}/exam.html`, { waitUntil: 'networkidle' });
await page.selectOption('#sel-count', '10');
await page.click('#start');
await page.waitForSelector('.choice');
const timer1 = await page.textContent('#q-timer');
await page.waitForTimeout(2200);
const timer2 = await page.textContent('#q-timer');
const noExplainInExam = (await page.$$eval('.explain', e => e.length)) === 0;
await page.click('.choice >> nth=0');
await page.click('#q-next');
await page.waitForTimeout(200);
const stillNoExplain = (await page.$$eval('.explain', e => e.length)) === 0;
ok('exam timer counts down', timer1 !== timer2, `${timer1} -> ${timer2}`);
ok('exam hides explanations', noExplainInExam && stillNoExplain);

// --- 9. ダークモード ---
await page.goto(`${BASE}/index.html`, { waitUntil: 'networkidle' });
await page.click('#pbm-theme');
const theme = await page.getAttribute('html', 'data-theme');
const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
ok('dark mode toggle', theme === 'dark' && bg !== 'rgb(246, 248, 252)', `theme=${theme} bg=${bg}`);

// --- 10. 用語集の検索 ---
await page.goto(`${BASE}/glossary.html`, { waitUntil: 'networkidle' });
const before = await page.$$eval('#list .card', e => e.length);
await page.fill('#q', 'CALCULATE');
await page.waitForTimeout(250);
const after = await page.$$eval('#list .card', e => e.length);
ok('glossary search filters', after > 0 && after < before, `${before} -> ${after}`);

// --- 11. 進捗のエクスポート/リセット ---
await page.goto(`${BASE}/progress.html`, { waitUntil: 'networkidle' });
await page.click('#btn-export');
const exported = await page.inputValue('#io');
ok('progress export', exported.includes('L201'), `${exported.length} chars`);

// --- 12. 計測は endpoint 未設定なら送信しない ---
let requests = 0;
page.on('request', r => { if (!r.url().startsWith(BASE)) requests++; });
await page.goto(`${BASE}/index.html`, { waitUntil: 'networkidle' });
await page.waitForTimeout(500);
ok('no analytics traffic when unconfigured', requests === 0, `external requests=${requests}`);

console.log(errs.length ? '\nPAGE ERRORS:\n' + errs.join('\n') : '\nno page errors');
await browser.close();
