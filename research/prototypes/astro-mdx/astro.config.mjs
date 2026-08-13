import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import { unified } from '@astrojs/markdown-remark';
import tailwindcss from '@tailwindcss/vite';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeCitation from 'rehype-citation';

export default defineConfig({
  output: 'static',
  site: 'https://www.gecode.dev',
  base: '/doc/current/mpg/',
  integrations: [mdx()],
  markdown: {
    processor: unified({
      remarkPlugins: [remarkMath],
      rehypePlugins: [
        rehypeKatex,
        [rehypeCitation, {
          bibliography: 'src/content/references.bib',
          csl: 'chicago',
          linkCitations: true,
          path: process.cwd(),
        }],
      ],
    }),
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
