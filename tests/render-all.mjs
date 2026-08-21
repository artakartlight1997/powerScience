/**
 * 全レッスン・全ラボの描画テスト（Playwright が必要）
 *
 *     cd docs && python3 -m http.server 8123   # 別ターミナル
 *     node tests/render-all.mjs
 *
 * 未閉じの強調記法、Mermaidの構文エラー、本文の欠落を検出します。
 * ネットワーク制限で Mermaid を読み込めない場合はフォールバック表示になりますが、
 * それ自体はテスト失敗とはみなしません。
 */
import { chromium } from 'playwright';
import fs from 'node:fs';
const BASE = 'http://localhost:8123';
const cur = JSON.parse(fs.readFileSync(new URL('../docs/content/curriculum.json', import.meta.url), 'utf8'));
const targets = [
  ...cur.lessons.map(l => ['lesson.html?id=' + l.id, l.id]),
  ...cur.labs.map(l => ['lab.html?id=' + l.id, l.id]),
];
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page = await ctx.newPage();
let bad = 0, diagrams = 0, mermaidErr = 0, unavailable = 0, tables = 0, callouts = 0;
const pageErrs = [];
page.on('pageerror', e => pageErrs.push(e.message));
for (const [url, id] of targets) {
  await page.goto(`${BASE}/${url}`, { waitUntil: 'networkidle' });
  await page.waitForSelector('.prose h2, .prose p', { timeout: 10000 });
  await page.waitForTimeout(900);
  const r = await page.evaluate(() => {
    const prose = document.getElementById('prose');
    const clone = prose.cloneNode(true);
    clone.querySelectorAll('pre, code').forEach(e => e.remove());
    const txt = clone.textContent;
    return {
      stray: (txt.match(/\*\*/g) || []).length,
      strong: prose.querySelectorAll('strong').length,
      svg: prose.querySelectorAll('.mermaid svg').length,
      figs: prose.querySelectorAll('.mermaid-wrap').length,
      syntaxErr: prose.querySelectorAll('.mermaid .mermaid-error, .mermaid > pre.small').length,
      unavailable: prose.querySelectorAll('.mermaid-wrap > .callout.warn').length,
      tbl: prose.querySelectorAll('table').length,
      call: prose.querySelectorAll('.callout').length,
      empty: prose.textContent.trim().length < 300,
    };
  });
  diagrams += r.svg; mermaidErr += r.syntaxErr; unavailable += r.unavailable; tables += r.tbl; callouts += r.call;
  if (r.stray > 0 || r.syntaxErr > 0 || r.empty) {
    bad++;
    console.log(`FAIL ${id}  stray**=${r.stray} diagramSyntaxErr=${r.syntaxErr} empty=${r.empty}`);
  }
}
console.log(`\n${targets.length} pages checked`);
console.log(`diagrams rendered: ${diagrams}, syntax errors: ${mermaidErr}, tables: ${tables}, callouts: ${callouts}`);
if (unavailable) console.log(`note: ${unavailable} figure(s) fell back (mermaid CDN unreachable from this machine)`);
console.log(pageErrs.length ? 'PAGE ERRORS: ' + pageErrs.slice(0,5).join(' | ') : 'no page errors');
console.log(bad ? `${bad} page(s) with issues` : 'All lesson/lab pages render cleanly');
await browser.close();
process.exit(bad ? 1 : 0);
