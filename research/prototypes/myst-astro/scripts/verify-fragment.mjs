import { readFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(fileURLToPath(new URL('..', import.meta.url)));
const index = await readFile(join(root, 'generated/index.fragment.html'), 'utf8');
const second = await readFile(join(root, 'generated/second-page.fragment.html'), 'utf8');
const overview = await readFile(join(root, 'generated/overview.fragment.html'), 'utf8');
const crossword = await readFile(join(root, 'generated/crossword.fragment.html'), 'utf8');
const nonogram = await readFile(join(root, 'generated/nonogram.fragment.html'), 'utf8');
const dependencies = JSON.parse(await readFile(join(root, 'generated/dependencies.json'), 'utf8'));
const inventory = JSON.parse(await readFile(join(root, 'reference-inventory.json'), 'utf8'));
const publicFiles = await readdir(join(root, 'public'));
const canonical = await readFile(join(root, 'examples/send-more-money.cpp'));
const canonicalCrossword = await readFile(join(root, '../shared/hard-pages/examples/crossword-grid.cpp'));
const canonicalNonogram = await readFile(join(root, '../shared/hard-pages/examples/nonogram-heart.cpp'));
const downloads = publicFiles.filter((name) => /^send-more-money-[a-f0-9]+\.cpp$/.test(name));
const downloaded = await Promise.all(downloads.map(async (name) => ({ name, bytes: await readFile(join(root, 'public', name)) })));
const exactDownload = downloaded.find(({ bytes }) => canonical.equals(bytes));
const crosswordDownloads = publicFiles.filter((name) => /^crossword-grid-[a-f0-9]+\.cpp$/.test(name));
const nonogramDownloads = publicFiles.filter((name) => /^nonogram-heart-[a-f0-9]+\.cpp$/.test(name));
const exactCrossword = crosswordDownloads.length === 1 && canonicalCrossword.equals(await readFile(join(root, 'public', crosswordDownloads[0])));
const exactNonogram = nonogramDownloads.length === 1 && canonicalNonogram.equals(await readFile(join(root, 'public', nonogramDownloads[0])));
const apiUrl = `${inventory.base_url}${inventory.objects['class:Gecode::Space'].url}`;

const checks = [
  ['numbered equation and accessible math', index.includes('id="eq-send-more-money"') && index.includes('<figcaption>(1)</figcaption>') && index.includes('<math xmlns="http://www.w3.org/1998/Math/MathML"')],
  ['numbered SVG figure', index.includes('id="fig-search-tree"') && index.includes('Figure 1:') && index.includes('.svg')],
  ['numbered Program 1', index.includes('id="code-search-loop"') && index.includes('Program 1:')],
  ['numbered Table 1', index.includes('id="table-results"') && index.includes('Table 1:')],
  ['callout', index.includes('class="admonition note"') && index.includes('Release invariant')],
  ['shared math macro on both pages', index.includes('mathvariant="script"') && second.includes('mathvariant="script"')],
  ['inventory API resolution', index.includes(`href="${apiUrl}"`) && second.includes(`href="${apiUrl}"`)],
  ['citation and bibliography', index.includes('Schulte, 1999') && index.includes('id="cite-schulte1999"')],
  ['canonical excerpt', index.includes('Gecode::DFS&lt;SendMoreMoney&gt;') && !index.includes('// region search-loop')],
  ['byte-identical download', Boolean(exactDownload)],
  ['explicit C++ dependency', dependencies['/content/index.md']?.includes('../examples/send-more-money.cpp')],
  ['release-shaped cross-page links', second.includes('href="/doc/6.4.0/modeling/#eq-send-more-money"') && second.includes('href="/doc/6.4.0/modeling/#sec-first-model"')],
  ['hard-page accessible SVG figures', overview.includes('architecture-') && overview.includes('alt="Layered Gecode architecture') && crossword.includes('crossword-puzzle-') && crossword.includes('crossword-solution-') && crossword.includes('crossword-mini-solut-') && nonogram.includes('nonogram-heart-')],
  ['hard-page semantic listings', crossword.includes('id="code-crossword-posting"') && nonogram.includes('id="code-nonogram-regex"') && nonogram.includes('id="code-nonogram-posting"')],
  ['hard-page numbered equation', nonogram.includes('id="eq-nonogram-line"') && nonogram.includes('<math xmlns="http://www.w3.org/1998/Math/MathML"')],
  ['hard-page external dependencies', dependencies['/content/crossword.md']?.includes('../../shared/hard-pages/examples/crossword-grid.cpp') && dependencies['/content/nonogram.md']?.includes('../../shared/hard-pages/examples/nonogram-heart.cpp')],
  ['hard-page byte-identical downloads without stale copies', exactCrossword && exactNonogram],
];

const failures = checks.filter(([, passed]) => !passed);
for (const [name, passed] of checks) console.log(`${passed ? 'PASS' : 'FAIL'} ${name}`);
if (failures.length) process.exit(1);
