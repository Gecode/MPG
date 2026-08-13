import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  base: '/doc/6.4.0/mpg/',
  build: { format: 'directory' }
});
