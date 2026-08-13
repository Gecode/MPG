import { access, mkdir } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { chromium } from 'playwright-core';

const candidates = [
  process.env.CHROME_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
].filter(Boolean);

let executablePath;
for (const candidate of candidates) {
  try { await access(candidate); executablePath = candidate; break; } catch {}
}
if (!executablePath) throw new Error('Chrome not found; set CHROME_PATH to a Chromium-family executable.');

const host = '127.0.0.1';
const port = 4329;
const preview = spawn(process.execPath, ['./node_modules/astro/bin/astro.mjs', 'preview', '--host', host, '--port', String(port)], {
  stdio: ['ignore', 'pipe', 'inherit'],
});

try {
  const url = `http://${host}:${port}/doc/current/mpg/chapters/m-started/`;
  for (let attempt = 0; attempt < 50; attempt++) {
    try { if ((await fetch(url)).ok) break; } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100));
    if (attempt === 49) throw new Error('Astro preview did not become ready.');
  }

  const browser = await chromium.launch({ executablePath, headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.emulateMedia({ media: 'print' });
  await mkdir(new URL('../dist/', import.meta.url), { recursive: true });
  await page.pdf({
    path: new URL('../dist/mpg-prototype.pdf', import.meta.url).pathname,
    format: 'A4',
    printBackground: true,
    margin: { top: '15mm', right: '16mm', bottom: '17mm', left: '16mm' },
  });
  await browser.close();
  console.log('wrote dist/mpg-prototype.pdf');
} finally {
  preview.kill('SIGTERM');
}
