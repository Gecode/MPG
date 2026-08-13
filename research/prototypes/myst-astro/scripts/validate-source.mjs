import { readFile } from 'node:fs/promises';

export function validate(sources) {
  const definitions = new Map();
  const references = [];
  for (const [file, source] of Object.entries(sources)) {
    const labels = [
      ...source.matchAll(/^\(([-\w.]+)\)=\s*$/gm),
      ...source.matchAll(/^:label:\s*([-\w.]+)\s*$/gm),
    ];
    for (const match of labels) {
      const label = match[1];
      if (definitions.has(label)) throw new Error(`Duplicate label ${label}: ${definitions.get(label)} and ${file}`);
      definitions.set(label, file);
    }
    for (const match of source.matchAll(/@([-\w]+(?:\.[-\w]+)*)/g)) references.push([match[1], file]);
    for (const match of source.matchAll(/\[\]\(#([-\w.]+)\)/g)) references.push([match[1], file]);
  }
  for (const [label, file] of references) {
    if (!definitions.has(label)) throw new Error(`Unresolved reference ${label} in ${file}`);
  }
}

if (process.argv[1] === new URL(import.meta.url).pathname) {
  const files = [
    'content/index.md', 'content/second-page.md', 'content/overview.md',
    'content/crossword.md', 'content/nonogram.md',
  ];
  const sources = Object.fromEntries(await Promise.all(files
    .map(async (file) => [file, await readFile(new URL(`../${file}`, import.meta.url), 'utf8')])));
  validate(sources);
  try { validate({ a: '(same)=\n', b: '(same)=\n' }); throw new Error('duplicate fixture did not fail'); }
  catch (error) { if (!String(error).includes('Duplicate label')) throw error; }
  try { validate({ a: 'See @missing.\n' }); throw new Error('unresolved fixture did not fail'); }
  catch (error) { if (!String(error).includes('Unresolved reference')) throw error; }
  console.log('PASS source labels unique and references resolved');
  console.log('PASS duplicate/unresolved reference rejection fixtures');
}
