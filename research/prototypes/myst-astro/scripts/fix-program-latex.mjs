import { readFile, readdir, writeFile } from 'node:fs/promises';

const directory = new URL('../generated/', import.meta.url);
const files = (await readdir(directory)).filter((name) => /^mpg-myst-astro-spike-(?:index|content\..+)\.tex$/.test(name));
let converted = 0;
for (const name of files) {
  const file = new URL(name, directory);
  const suffix = name.slice('mpg-myst-astro-spike-'.length, -'.tex'.length);
  const document = JSON.parse(await readFile(new URL(`../_build/site/content/${suffix}.json`, import.meta.url), 'utf8'));
  const programs = [];
  const walk = (node) => {
    if (node.type === 'container' && node.kind === 'code') {
      const code = node.children?.find((child) => child.type === 'code');
      if (!code || !node.identifier) throw new Error(`unidentified code container in ${suffix}`);
      if (code.value.includes('\\end{verbatim}')) throw new Error(`unsupported verbatim terminator in ${node.identifier}`);
      programs.push({ label: node.identifier, value: code.value });
    }
    (node.children ?? []).forEach(walk);
  };
  walk(document.mdast);
  let source = await readFile(file, 'utf8');
  for (const program of programs) {
    const escaped = program.label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pattern = new RegExp(`\\\\begin\\{figure\\}\\[h\\]([\\s\\S]*?\\\\label\\{${escaped}\\}[\\s\\S]*?)\\\\end\\{figure\\}`);
    const match = source.match(pattern);
    if (!match) throw new Error(`MyST code-listing LaTeX shape changed for ${program.label}`);
    const exact = match[1].replace(/\\begin\{verbatim\}[\s\S]*?\\end\{verbatim\}/, `\\begin{verbatim}\n${program.value}\n\\end{verbatim}`);
    source = source.replace(pattern, `\\begin{mpgprogram}[H]${exact}\\end{mpgprogram}`);
    converted++;
  }
  await writeFile(file, source);
}
if (converted !== 4)
  throw new Error(`expected four code-listing LaTeX repairs, found ${converted}; refusing an unverified PDF`);
console.log(`PASS restored ${converted} exact AST code blocks and Program kinds for LaTeX`);
