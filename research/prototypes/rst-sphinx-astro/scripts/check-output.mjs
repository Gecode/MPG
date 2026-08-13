import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
import { render } from './render-astro.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const first = await readFile(join(root, 'dist/first-page/index.html'), 'utf8');
const second = await readFile(join(root, 'dist/second-page/index.html'), 'utf8');
const overview = await readFile(join(root, 'dist/overview/index.html'), 'utf8');
const crossword = await readFile(join(root, 'dist/crossword/index.html'), 'utf8');
const nonogram = await readFile(join(root, 'dist/nonogram/index.html'), 'utf8');
const pdfText = await readFile(join(root, 'build/pdf.txt'), 'utf8');
const checks = [
  ['section number', first.includes('section-number">1') && second.includes('Section 1')],
  ['equation agreement', first.includes('Equation 1.1') && second.includes('Equation 1.1') && pdfText.includes('Equation 1.1')],
  ['figure agreement', first.includes('Figure 1.1') && second.includes('Figure 1.1') && pdfText.includes('Figure 1.1')],
  ['program agreement', first.includes('Program 1.1') && second.includes('Program 1.1') && pdfText.includes('Program 1.1')],
  ['table agreement', first.includes('Table 1.1') && second.includes('Table 1.1') && pdfText.includes('Table 1.1')],
  ['server-rendered accessible math', first.includes('class="katex-mathml"') && first.includes('Gecode')],
  ['SVG and callout', first.includes('search-tree.svg') && first.includes('class="admonition tip"')],
  ['citation and bibliography', first.includes('Efficient constraint propagation engines') && first.includes('Schulte')],
  ['versioned imported API link', first.includes('/doc/6.4.0/reference/classGecode_1_1Space.html') && second.includes('data-api-symbol="class:Gecode::Space"')],
  ['cross-page route', second.includes('../first-page/#sec-first-model')],
  ['A4 PDF content', pdfText.includes('Publication is a release job') && pdfText.includes('ACM Transactions')],
  ['hard-page routes and accessible SVG', overview.includes('architecture.svg') && overview.includes('alt="Layered Gecode architecture') && crossword.includes('crossword-puzzle.svg') && crossword.includes('crossword-solution.svg') && crossword.includes('crossword-mini-solution.svg') && nonogram.includes('nonogram-heart.svg')],
  ['hard-page semantic listings', crossword.includes('Posting the across and down table constraints') && nonogram.includes('Constructing a regular expression from line hints') && nonogram.includes('Posting row and column constraints')],
  ['hard-page PDF content', pdfText.includes('Architecture overview') && pdfText.includes('Crossword case study') && pdfText.includes('Nonogram case study') && /Constructing a regular expression from\s+line hints/.test(pdfText)],
  ['hard-page equation and programs', nonogram.includes('Equation 5.1') && nonogram.includes('Program 5.1') && nonogram.includes('Program 5.2') && pdfText.includes('Program 5.2')],
  ['hard-page code punctuation fidelity', nonogram.includes('Fidelity sentinels for publication: -- ++ -&gt;') && pdfText.includes('Fidelity sentinels for publication: -- ++ ->')],
];
for (const [label, ok] of checks) {
  if (!ok) throw new Error(`FAIL ${label}`);
  console.log(`PASS ${label}`);
}
try {
  render({ type: 'unsupportedFixture' });
  throw new Error('FAIL Astro adapter accepted an unknown semantic node');
} catch (error) {
  if (!String(error).includes('Unmapped semantic node type')) throw error;
  console.log('PASS Astro adapter rejects unknown semantic nodes');
}
