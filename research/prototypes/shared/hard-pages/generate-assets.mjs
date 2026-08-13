import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const destination = process.argv[2];
if (!destination) throw new Error('usage: node generate-assets.mjs OUTPUT_DIRECTORY');
const fixture = JSON.parse(await readFile(join(here, 'fixture.json'), 'utf8'));

const esc = (value) => String(value)
  .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;');

function svg(title, description, width, height, body) {
  const id = title.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  return `<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="${id}-title ${id}-desc" viewBox="0 0 ${width} ${height}">
  <title id="${id}-title">${esc(title)}</title>
  <desc id="${id}-desc">${esc(description)}</desc>
  <style>
    .display { font: 600 24px Raleway, Verdana, sans-serif; fill: #14221c; }
    .label { font: 650 15px "Open Sans", Arial, sans-serif; fill: #14221c; }
    .small { font: 600 12px "Open Sans", Arial, sans-serif; fill: #64716b; }
    .cell { font: 600 13px "Roboto Mono", ui-monospace, monospace; text-anchor: middle; dominant-baseline: central; }
  </style>
${body}
</svg>
`;
}

function architecture() {
  const modules = fixture.architecture.modules.map((name, index) => {
    const x = 210 + index * 96;
    const accents = ['#8bc5b2', '#acd5c8', '#d8c690', '#a9bdd8'];
    return `<g><rect x="${x}" y="188" width="82" height="116" rx="15" fill="#fff" stroke="${accents[index]}" stroke-width="3"/><text class="label" x="${x + 41}" y="242" text-anchor="middle">${name}</text><text class="small" x="${x + 41}" y="264" text-anchor="middle">module</text></g>`;
  }).join('\n');
  return svg('Gecode architecture', 'Modeling spans the integer, set, float, and search modules. All modules rest on the kernel. Extension points surround the modules for propagators, branchers, variables, and search engines.', 760, 420, `
  <rect width="760" height="420" rx="24" fill="#f4f1e8"/>
  <path d="M72 108H688" stroke="#d7d0bd" stroke-width="1"/>
  <text class="display" x="72" y="66">From model to search</text>
  <rect x="184" y="90" width="540" height="70" rx="18" fill="#dcebdc" stroke="#3e8668" stroke-width="3"/>
  <text class="label" x="454" y="132" text-anchor="middle">Modeling layer</text>
  <rect x="36" y="188" width="142" height="116" rx="18" fill="#dce8f3" stroke="#4d7399" stroke-width="3"/>
  <text class="label" x="107" y="232" text-anchor="middle">Propagators</text><text class="label" x="107" y="254" text-anchor="middle">and branchers</text><text class="small" x="107" y="280" text-anchor="middle">extension point</text>
  ${modules}
  <rect x="604" y="188" width="120" height="54" rx="15" fill="#f4dfc9" stroke="#c87436" stroke-width="3"/><text class="label" x="664" y="220" text-anchor="middle">Variables</text>
  <rect x="604" y="250" width="120" height="54" rx="15" fill="#f2d8d8" stroke="#b85656" stroke-width="3"/><text class="label" x="664" y="282" text-anchor="middle">Engines</text>
  <rect x="184" y="336" width="540" height="52" rx="16" fill="#183d33"/>
  <text x="454" y="367" text-anchor="middle" style="font:650 16px 'Open Sans', sans-serif;fill:#fff">Gecode kernel · spaces · actors · memory</text>
  <path d="M454 160V178M454 304V326" stroke="#647d74" stroke-width="3" stroke-linecap="round"/>
  <path d="M446 175L454 183L462 175M446 323L454 331L462 323" fill="none" stroke="#647d74" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  `);
}

function crossword(rows, solved, title) {
  const size = rows.length;
  const cell = size > 5 ? 25 : 48;
  const pad = 32;
  const board = size * cell;
  let cells = '';
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const value = rows[y][x];
      const blocked = value === '*';
      cells += `<rect x="${pad + x * cell}" y="${pad + y * cell}" width="${cell}" height="${cell}" fill="${blocked ? '#183d33' : '#fffdf7'}" stroke="#789086" stroke-width="${size > 5 ? .65 : 1}"/>`;
      if (solved && !blocked) cells += `<text class="cell" x="${pad + (x + .5) * cell}" y="${pad + (y + .5) * cell}" fill="#183d33" style="font-size:${size > 5 ? 12 : 21}px">${esc(value.toUpperCase())}</text>`;
    }
  }
  return svg(title, `${size} by ${size} crossword ${solved ? 'solution with letters' : 'grid with blocked and open cells'}.`, board + pad * 2, board + pad * 2, `
  <rect width="100%" height="100%" rx="22" fill="#f4f1e8"/>
  <rect x="${pad - 8}" y="${pad - 8}" width="${board + 16}" height="${board + 16}" rx="9" fill="#d8d0ba"/>
  ${cells}
  `);
}

function hints(line) {
  const values = [];
  let run = 0;
  for (const value of `${line}.`) {
    if (value === '#') run++;
    else if (run) { values.push(run); run = 0; }
  }
  return values;
}

function nonogram() {
  const rows = fixture.nonogram.solution;
  const columns = rows[0].split('').map((_, x) => rows.map((row) => row[x]).join(''));
  const rowHints = rows.map(hints);
  const colHints = columns.map(hints);
  const cell = 31, left = 92, top = 82, board = 9 * cell, gap = 74;
  const panelWidth = left + board + 34;
  const renderPanel = (offset, solved, label) => {
    let result = `<text class="display" x="${offset + 20}" y="36">${label}</text>`;
    for (let i = 0; i < 9; i++) {
      result += `<text class="small" x="${offset + left - 12}" y="${top + (i + .5) * cell}" text-anchor="end" dominant-baseline="central">${rowHints[i].join(' ')}</text>`;
      const column = colHints[i];
      column.forEach((hint, j) => {
        result += `<text class="small" x="${offset + left + (i + .5) * cell}" y="${top - 12 - (column.length - 1 - j) * 17}" text-anchor="middle">${hint}</text>`;
      });
      for (let x = 0; x < 9; x++) {
        const filled = solved && rows[i][x] === '#';
        result += `<rect x="${offset + left + x * cell}" y="${top + i * cell}" width="${cell}" height="${cell}" rx="2" fill="${filled ? '#d65b4a' : '#fffdf7'}" stroke="#789086"/>`;
      }
    }
    return result;
  };
  return svg('Heart nonogram puzzle and solution', 'A modern rendering of the nine by nine heart nonogram. Row and column hints surround an empty puzzle grid; the solved grid uses coral squares to form a heart.', panelWidth * 2 + gap, 410, `
  <rect width="100%" height="100%" rx="24" fill="#f4f1e8"/>
  ${renderPanel(0, false, 'Puzzle')}
  <path d="M${panelWidth + gap / 2} 36V374" stroke="#d7d0bd" stroke-width="2" stroke-dasharray="5 8"/>
  ${renderPanel(panelWidth + gap, true, 'Solved')}
  `);
}

await mkdir(destination, { recursive: true });
const outputs = {
  'architecture.svg': architecture(),
  'crossword-puzzle.svg': crossword(fixture.crossword.blocked_rows, false, 'Crossword puzzle'),
  'crossword-solution.svg': crossword(fixture.crossword.blocked_rows, true, 'Crossword solution'),
  'crossword-mini-solution.svg': crossword(fixture.crossword.rows, true, 'Executable miniature crossword solution'),
  'nonogram-heart.svg': nonogram(),
};
for (const [name, contents] of Object.entries(outputs))
  await writeFile(join(destination, name), contents);
console.log(`generated ${Object.keys(outputs).length} accessible SVG assets in ${destination}`);
