import { readFile, readdir, writeFile } from 'node:fs/promises';

const directory = new URL('../generated/', import.meta.url);
const files = (await readdir(directory))
  .filter((name) => /^mpg-myst-astro-spike-(?:index|content\..+)\.tex$/.test(name))
  .sort();

let chapters = 0;
let tips = 0;
let duplicateHeadings = 0;
for (const name of files) {
  const file = new URL(name, directory);
  let source = await readFile(file, 'utf8');

  // MyST exports each article title as a section. In the release book, an
  // article is a chapter and its authored headings sit below that chapter.
  const outer = source.match(/^\\section\{([^\n{}]+)\}\n/);
  if (!outer) throw new Error(`missing outer article section in ${name}`);
  source = source.replace(/^\\section\{([^\n{}]+)\}\n/, '\\chapter{$1}\n');
  source = source.replaceAll('\\subsection{', '\\section{');
  source = source.replaceAll('\\subsubsection{', '\\subsection{');
  const escapedTitle = outer[1].replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const duplicate = new RegExp(`\\\\section\\{${escapedTitle}\\}(\\\\label\\{[^{}]+\\})`);
  if (duplicate.test(source)) {
    source = source.replace(duplicate, '$1');
    duplicateHeadings++;
  }
  chapters++;

  // The exporter currently lowers every admonition to an anonymous framed
  // block. Recover the semantic title and route it through the shared MPG API.
  source = source.replace(
    /\\begin\{framed\}\n\\textbf\{([^{}]+)\}\\\\\n([\s\S]*?)\\end\{framed\}/g,
    (_match, title, body) => {
      tips++;
      return `\\begin{mpgtip}{${title}}\n${body}\\end{mpgtip}`;
    },
  );

  await writeFile(file, source);
}

if (chapters !== 5)
  throw new Error(`expected five article-to-chapter repairs, found ${chapters}`);
if (duplicateHeadings !== 3)
  throw new Error(`expected three duplicate title-heading repairs, found ${duplicateHeadings}`);
if (tips !== 2)
  throw new Error(`expected two admonition-to-tip repairs, found ${tips}`);

const main = await readFile(new URL('mpg-myst-astro-spike.tex', directory), 'utf8');
for (const sentinel of [
  '\\usepackage{mpg-myst}',
  '\\MPGSetPartAuthors{MPG prototype team}',
  '\\MPGSetPartBlurb{',
  '\\MPGPartNumber{13}{Modeling}',
]) {
  if (!main.includes(sentinel)) throw new Error(`missing classical template sentinel: ${sentinel}`);
}

const combined = await Promise.all(files.map((name) => readFile(new URL(name, directory), 'utf8')));
const output = combined.join('\n');
if ((output.match(/\\begin\{mpgprogram\}/g) ?? []).length !== 4)
  throw new Error('expected four shared mpgprogram environments');
if (/\\begin\{(?:program|framed)\}/.test(output))
  throw new Error('unadapted program or framed environment remains');

console.log(
  `PASS adapted ${chapters} chapters, removed ${duplicateHeadings} duplicate headings, ` +
  `${tips} tips, and 4 programs to mpg-classic through mpg-myst`,
);
