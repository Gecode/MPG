import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const generated = join(root, 'generated');
const site = join(root, '_build', 'site');
const releaseBase = '/doc/6.4.0/modeling';

function releaseHref(url = '') {
  if (url === '/') return `${releaseBase}/`;
  if (url === '/content/second-page') return `${releaseBase}/cross-page/`;
  if (url === '/content/overview') return `${releaseBase}/overview/`;
  if (url === '/content/crossword') return `${releaseBase}/crossword/`;
  if (url === '/content/nonogram') return `${releaseBase}/nonogram/`;
  return url;
}

const escapeHtml = (value = '') => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;');

const attrs = (values) => Object.entries(values)
  .filter(([, value]) => value !== undefined && value !== null && value !== false && value !== '')
  .map(([key, value]) => ` ${key}="${escapeHtml(value)}"`)
  .join('');

function children(node, context) {
  return (node.children ?? []).map((child) => render(child, context)).join('');
}

function render(node, context) {
  switch (node.type) {
    case 'root':
    case 'block':
    case 'include':
      return children(node, context);
    case 'text':
      return escapeHtml(node.value);
    case 'inlineCode':
      return `<code>${escapeHtml(node.value)}</code>`;
    case 'inlineMath':
      return node.html;
    case 'paragraph':
      return `<p>${children(node, context)}</p>`;
    case 'emphasis':
      return `<em>${children(node, context)}</em>`;
    case 'strong':
      return `<strong>${children(node, context)}</strong>`;
    case 'list':
      return `<${node.ordered ? 'ol' : 'ul'}>${children(node, context)}</${node.ordered ? 'ol' : 'ul'}>`;
    case 'listItem':
      return `<li>${children(node, context)}</li>`;
    case 'heading': {
      const number = node.enumerator
        ? `<span class="section-number">${escapeHtml(node.enumerator)}</span>`
        : '';
      return `<h${node.depth}${attrs({ id: node.html_id ?? node.identifier })}>${number}${children(node, context)}</h${node.depth}>`;
    }
    case 'crossReference': {
      const base = releaseHref(node.url ?? '');
      const href = `${base}${node.html_id ? `#${node.html_id}` : ''}`;
      return `<a class="cross-reference"${attrs({ href, 'data-kind': node.kind, 'data-resolved': node.resolved })}>${children(node, context)}</a>`;
    }
    case 'link':
      return `<a${attrs({ href: releaseHref(node.url), title: node.title, class: node.class })}>${children(node, context)}</a>`;
    case 'citeGroup': {
      const body = children(node, context);
      return `<span class="citation">${node.kind === 'parenthetical' ? `(${body})` : body}</span>`;
    }
    case 'cite':
      return `<a${attrs({ href: `#cite-${node.identifier}`, 'data-cite': node.identifier })}>${children(node, context)}</a>`;
    case 'math':
      return `<figure class="equation"${attrs({ id: node.html_id ?? node.identifier, 'data-tex': node.value })}><div>${node.html}</div><figcaption>(${escapeHtml(node.enumerator)})</figcaption></figure>`;
    case 'container':
      return `<figure${attrs({ id: node.html_id ?? node.identifier, class: `${node.kind ?? ''}-container`.trim() })}>${children(node, context)}</figure>`;
    case 'image':
      return `<img${attrs({ src: node.url, alt: node.alt ?? '', width: node.width })} />`;
    case 'caption':
      return `<figcaption>${children(node, context)}</figcaption>`;
    case 'captionNumber':
      return `<span class="caption-number">${children(node, context)}</span>`;
    case 'code':
      return `${node.filename ? `<div class="code-filename">${escapeHtml(node.filename)}</div>` : ''}<pre><code${attrs({ class: node.lang ? `language-${node.lang}` : undefined })}>${escapeHtml(node.value)}</code></pre>`;
    case 'admonition':
      return `<aside${attrs({ class: `admonition ${node.class ?? ''}`.trim() })}>${children(node, context)}</aside>`;
    case 'admonitionTitle':
      return `<p class="admonition-title">${children(node, context)}</p>`;
    case 'table':
      return `<table><tbody>${children(node, context)}</tbody></table>`;
    case 'tableRow':
      return `<tr>${children(node, context)}</tr>`;
    case 'tableCell': {
      const tag = node.header ? 'th' : 'td';
      return `<${tag}${attrs({ style: node.align ? `text-align:${node.align}` : undefined })}>${children(node, context)}</${tag}>`;
    }
    case 'bibliography': {
      const refs = context.references?.cite;
      if (!refs?.order?.length) return '';
      const items = refs.order.map((id) => {
        const ref = refs.data[id];
        return `<li id="cite-${escapeHtml(id)}">${ref.html}</li>`;
      }).join('');
      return `<section class="bibliography" aria-labelledby="references-heading"><h2 id="references-heading">References</h2><ol>${items}</ol></section>`;
    }
    default:
      throw new Error(`Unmapped MyST node type: ${node.type}`);
  }
}

async function renderPage(input, output) {
  const document = JSON.parse(await readFile(join(site, 'content', input), 'utf8'));
  const bibliography = input === 'index.json'
    ? render({ type: 'bibliography' }, document)
    : '';
  const fragment = `${render(document.mdast, document)}${bibliography}`;
  await writeFile(join(generated, output), `${fragment}\n`);
}

const pages = [
  ['index.json', 'index.fragment.html'],
  ['content.second-page.json', 'second-page.fragment.html'],
  ['content.overview.json', 'overview.fragment.html'],
  ['content.crossword.json', 'crossword.fragment.html'],
  ['content.nonogram.json', 'nonogram.fragment.html'],
];

async function writeDependencies() {
  const dependencyMap = {};
  for (const [input] of pages) {
    const document = JSON.parse(await readFile(join(site, 'content', input), 'utf8'));
    const found = new Set();
    const walk = (node) => {
      if (node.type === 'include' && node.file) found.add(node.file);
      if (node.type === 'link' && node.static && node.urlSource) found.add(node.urlSource);
      (node.children ?? []).forEach(walk);
    };
    walk(document.mdast);
    dependencyMap[document.location] = [...found].sort();
  }
  await writeFile(join(generated, 'dependencies.json'), `${JSON.stringify(dependencyMap, null, 2)}\n`);
}

await mkdir(generated, { recursive: true });
if (process.env.MPG_TEST_UNKNOWN_NODE === '1') {
  render({ type: 'unsupported-contract-fixture' }, {});
}
for (const [input, output] of pages) await renderPage(input, output);
await writeDependencies();
await rm(join(root, 'public'), { recursive: true, force: true });
await cp(join(site, 'public'), join(root, 'public'), { recursive: true, force: true });
