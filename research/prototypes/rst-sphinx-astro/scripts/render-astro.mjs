import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { basename, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import katex from 'katex';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const publication = JSON.parse(await readFile(join(root, 'build/semantic/publication.json'), 'utf8'));
const escape = (v = '') => String(v).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const idAttr = (node) => node.ids?.length ? ` id="${escape(node.ids.at(-1))}"` : '';
const renderChildren = (node, context = {}) => (node.children ?? []).map(child => render(child, context)).join('');

export function render(node, context = {}) {
  switch (node.type) {
    case 'document': case 'section': case 'group': case 'span': return renderChildren(node, context);
    case 'text': return escape(node.value);
    case 'paragraph': return `<p${idAttr(node)}>${renderChildren(node, context)}</p>`;
    case 'title': return `<h${node.level}${idAttr(node)}>${node.number ? `<span class="section-number">${escape(node.number)}</span>` : ''}${renderChildren(node, context)}</h${node.level}>`;
    case 'inlineCode': return `<code>${escape(node.value)}</code>`;
    case 'emphasis': return `<em>${renderChildren(node, context)}</em>`;
    case 'strong': return `<strong>${renderChildren(node, context)}</strong>`;
    case 'reference': return `<a href="${escape(node.uri ?? `#${node.anchor}`)}"${node.api_symbol ? ` data-api-symbol="${escape(node.api_symbol)}"` : ''}>${renderChildren(node, context)}</a>`;
    case 'download': return `<a class="download" href="../downloads/${escape(basename(node.source))}" download>${renderChildren(node, context)}</a>`;
    case 'inlineMath': return katex.renderToString(node.tex, { throwOnError: true, macros: { '\\Gecode': '\\mathsf{Gecode}' } });
    case 'equation': return `<figure class="equation"${idAttr(node)}><div>${katex.renderToString(node.tex, { displayMode: true, throwOnError: true, macros: { '\\Gecode': '\\mathsf{Gecode}' } })}</div>${node.number ? `<figcaption>Equation ${escape(node.number)}</figcaption>` : ''}</figure>`;
    case 'figure': return `<figure${idAttr(node)}>${renderChildren(node, { ...context, kind: 'Figure', number: node.number })}</figure>`;
    case 'image': return `<img src="../${escape(node.uri)}" alt="${escape(node.alt)}"${node.width ? ` style="width:${escape(node.width)}"` : ''}>`;
    case 'container': return `<figure${idAttr(node)}>${renderChildren(node, { ...context, kind: 'Program', number: node.number })}</figure>`;
    case 'caption': return `<figcaption>${context.kind ?? ({figure:'Figure',table:'Table','code-block':'Program'}[node.kind])} ${escape(context.number ?? '')}. ${renderChildren(node, context)}</figcaption>`;
    case 'code': return `<pre><code class="language-${escape(node.language)}">${escape(node.value)}</code></pre>`;
    case 'table': return `<table${idAttr(node)}>${renderChildren(node, { ...context, kind: 'Table', number: node.number })}</table>`;
    case 'tableGroup': return renderChildren(node, context);
    case 'tableHead': return `<thead>${renderChildren(node, { ...context, head: true })}</thead>`;
    case 'tableBody': return `<tbody>${renderChildren(node, { ...context, head: false })}</tbody>`;
    case 'tableRow': return `<tr>${renderChildren(node, context)}</tr>`;
    case 'tableCell': return context.head ? `<th>${renderChildren(node, context)}</th>` : `<td>${renderChildren(node, context)}</td>`;
    case 'admonition': return `<aside class="admonition ${escape(node.kind)}"><strong>${escape(node.kind[0].toUpperCase() + node.kind.slice(1))}</strong>${renderChildren(node, context)}</aside>`;
    case 'citation': return `<div class="citation"${idAttr(node)}>${renderChildren(node, context)}</div>`;
    case 'citationLabel': return `<span class="citation-label">[${renderChildren(node, context)}]</span> `;
    case 'anchor': return node.ids?.length ? `<span${idAttr(node)}></span>` : '';
    case 'list': return node.ordered ? `<ol>${renderChildren(node, context)}</ol>` : `<ul>${renderChildren(node, context)}</ul>`;
    case 'listItem': return `<li>${renderChildren(node, context)}</li>`;
    default: throw new Error(`Unmapped semantic node type: ${node.type}`);
  }
}

await rm(join(root, 'src/pages'), { recursive: true, force: true });
await mkdir(join(root, 'src/pages'), { recursive: true });
for (const [slug, page] of Object.entries(publication.pages)) {
  const html = render(page);
  const title = ({
    'first-page': 'A first model', 'second-page': 'Cross-page semantics',
    overview: 'Architecture overview', crossword: 'Crossword case study',
    nonogram: 'Nonogram case study',
  })[slug] ?? slug;
  const source = `---\nimport Publication from '../layouts/Publication.astro';\nconst html = ${JSON.stringify(html)};\n---\n<Publication title=${JSON.stringify(title)} release=${JSON.stringify(publication.publication.release)}><Fragment set:html={html} /></Publication>\n`;
  await writeFile(join(root, 'src/pages', `${slug}.astro`), source);
}
await mkdir(join(root, 'public/assets'), { recursive: true });
await mkdir(join(root, 'public/downloads'), { recursive: true });
await cp(join(root, 'content/assets/search-tree.svg'), join(root, 'public/assets/search-tree.svg'));
await cp(join(root, 'examples/send-more-money.cpp'), join(root, 'public/downloads/send-more-money.cpp'));
await cp(join(root, 'content/assets/hard'), join(root, 'public/assets/hard'), { recursive: true });
await cp(join(root, '../shared/hard-pages/examples/crossword-grid.cpp'), join(root, 'public/downloads/crossword-grid.cpp'));
await cp(join(root, '../shared/hard-pages/examples/nonogram-heart.cpp'), join(root, 'public/downloads/nonogram-heart.cpp'));
