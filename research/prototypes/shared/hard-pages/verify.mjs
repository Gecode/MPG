import { execFileSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const fixture = JSON.parse(await readFile(join(here, 'fixture.json'), 'utf8'));
const binaryDirectory = process.argv[2];
if (!binaryDirectory) throw new Error('usage: node verify.mjs BINARY_DIRECTORY');

const run = (name) => execFileSync(join(binaryDirectory, name), { encoding: 'utf8' }).trim().split('\n');
const nonogram = run('nonogram-heart');
const crossword = run('crossword-grid');
if (JSON.stringify(nonogram) !== JSON.stringify(fixture.nonogram.solution))
  throw new Error(`nonogram output disagrees with fixture: ${JSON.stringify(nonogram)}`);
if (JSON.stringify(crossword) !== JSON.stringify(fixture.crossword.rows))
  throw new Error(`crossword output disagrees with fixture: ${JSON.stringify(crossword)}`);
console.log('PASS executable crossword/nonogram outputs agree with illustration data');
