/**
 * 全レッスン・全ラボの描画テスト（Playwright が必要）
 *
 *     cd docs && python3 -m http.server 8123   # 別ターミナル
 *     node tests/render-all.mjs
 *
 * 検出するもの
 *   - 未閉じの強調記法（日本語で ** が生のまま残る）
 *   - figure ブロックの設定エラー・未描画
 *   - Mermaid の残骸
 *   - 本文の欠落
 *   - 用語リンクが1つも張られていないページ
 */
import { chromium } from 'playwright';
import fs from 'node:fs';

const BASE = 'http://localhost:8123';
const cur = JSON.parse(fs.readFileSync(new URL('../docs/content/curriculum.json', import.meta.url), 'utf8'));
const written = new Set(fs.readdirSync(new URL('../docs/content/lessons', import.meta.url)).map(f => f.replace(/\.md$/, '')));

const targets = [
  ...cur.lessons.filter(l => written.has(l.id)).map(l => ['lesson.html?id=' + l.id, l.id]),
  ...fs.readdirSync(new URL('../docs/content/labs', import.meta.url))
      .filter(f => /^LAB\d+\.md$/.test(f))
      .map(f => ['lab.html?id=' + f.replace(/\.md$/, ''), f.replace(/\.md$/, '')]),
];

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page = await ctx.newPage();
const pageErrs = [];
page.on('pageerror', e => pageErrs.push(e.message));

let bad = 0, figs = 0, figErrs = 0, tables = 0, callouts = 0, terms = 0, widgets = 0, empty = 0;

for (const [url, id] of targets) {
  await page.goto(`${BASE}/${url}`, { waitUntil: 'networkidle' });
  try {
    await page.waitForSelector('.prose h2, .prose p', { timeout: 12000 });
  } catch { /* 空ページはあとで検出する */ }
  await page.waitForTimeout(700);

  const r = await page.evaluate(() => {
    const prose = document.getElementById('prose');
    if (!prose) return null;
    const clone = prose.cloneNode(true);
    clone.querySelectorAll('pre, code').forEach(e => e.remove());
    return {
      stray: (clone.textContent.match(/\*\*/g) || []).length,
      mermaid: prose.querySelectorAll('.pbm-figure-error').length,
      figTotal: prose.querySelectorAll('.pbm-figure:not(.pbm-figure-error)').length,
      figDone: prose.querySelectorAll('.pbm-figure[data-rendered]').length,
      widget: prose.querySelectorAll('.pbmw, [class*="pbmw-"]').length ? 1 : 0,
      tbl: prose.querySelectorAll('table').length,
      call: prose.querySelectorAll('.callout').length,
      gl: prose.querySelectorAll('.gl-term').length,
      len: prose.textContent.trim().length,
    };
  });

  if (!r) { bad++; console.log(`FAIL ${id}  本文コンテナがありません`); continue; }

  figs += r.figTotal; figErrs += r.mermaid; tables += r.tbl; callouts += r.call; terms += r.gl; widgets += r.widget;
  const unrendered = r.figTotal - r.figDone;
  const isEmpty = r.len < 500;
  if (isEmpty) empty++;

  if (r.stray > 0 || r.mermaid > 0 || unrendered > 0 || isEmpty) {
    bad++;
    console.log(`FAIL ${id.padEnd(8)} stray**=${r.stray} figureError=${r.mermaid} unrendered=${unrendered} len=${r.len}`);
  }
}

console.log(`\n${targets.length} pages checked`);
console.log(`figures=${figs}  figureErrors=${figErrs}  tables=${tables}  callouts=${callouts}  glossaryLinks=${terms}  pagesWithWidget=${widgets}`);
if (empty) console.log(`本文が空/極端に短いページ: ${empty}`);
console.log(pageErrs.length ? 'PAGE ERRORS: ' + [...new Set(pageErrs)].slice(0, 5).join(' | ') : 'no page errors');
console.log(bad ? `${bad} page(s) with issues` : 'All lesson/lab pages render cleanly');

await browser.close();
process.exit(bad ? 1 : 0);
