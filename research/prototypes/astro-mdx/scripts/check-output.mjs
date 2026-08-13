import { readFile } from 'node:fs/promises';

const html = await readFile(new URL('../dist/chapters/m-started/index.html', import.meta.url), 'utf8');
const checks = [
  ['KaTeX math', 'class="katex"'],
  ['figure anchor', 'id="fig-space"'],
  ['cross-reference', 'href="#fig-space"'],
  ['citation link', 'href="#bib-schultetack2008"'],
  ['bibliography', 'class="csl-entry"'],
  ['canonical C++ listing', 'class="astro-code'],
  ['callout', 'callout--tip'],
];

for (const [name, needle] of checks) {
  if (!html.includes(needle)) throw new Error(`Missing ${name}: ${needle}`);
  console.log(`ok - ${name}`);
}
