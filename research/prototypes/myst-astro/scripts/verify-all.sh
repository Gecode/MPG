#!/usr/bin/env bash
set -euo pipefail

mkdir -p generated exports
node ../shared/hard-pages/generate-assets.mjs content/assets/hard
node scripts/validate-source.mjs
node -e "require('node:fs').rmSync('_build', {recursive: true, force: true})"

# The local metadata-only template means this fails if MyST attempts network I/O.
HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 ALL_PROXY=http://127.0.0.1:9 \
  npm run myst:site -- --strict --ci

cmp -s reference-inventory.json ../shared/reference-inventory.json

c++ -std=c++17 -Wall -Wextra -pedantic -I/opt/homebrew/include \
  examples/send-more-money.cpp -L/opt/homebrew/lib \
  -lgecodedriver -lgecodesearch -lgecodeminimodel -lgecodeint \
  -lgecodekernel -lgecodesupport -o generated/send-more-money
test "$(./generated/send-more-money)" = "9 5 6 7 1 0 8 2"

for example_source in ../shared/hard-pages/examples/*.cpp; do
  example_name="${example_source##*/}"
  example_name="${example_name%.cpp}"
  c++ -std=c++17 -Wall -Wextra -pedantic -I/opt/homebrew/include \
    "$example_source" -L/opt/homebrew/lib \
    -lgecodesearch -lgecodeminimodel -lgecodeint -lgecodekernel -lgecodesupport \
    -o "generated/$example_name"
done
node ../shared/hard-pages/verify.mjs generated

npm run astro:build
npm run astro:check
npm run verify:fragment
if MPG_TEST_UNKNOWN_NODE=1 npm run render:fragment >/dev/null 2>&1; then
  echo "FAIL strict unknown-node rejection"
  exit 1
fi
echo "PASS strict unknown-node rejection"

pdf_log=generated/pdf-build.log
HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 ALL_PROXY=http://127.0.0.1:9 \
  npm run myst:tex -- --strict --ci 2>&1 | tee "$pdf_log"
! grep -q 'Unhandled LaTeX conversion' "$pdf_log"
cp templates/plain-latex-book/mpg-myst.sty generated/mpg-myst.sty
cmp -s templates/plain-latex-book/mpg-myst.sty generated/mpg-myst.sty
node scripts/fix-program-latex.mjs
node scripts/adapt-classical-latex.mjs
(cd generated && TEXINPUTS=../templates/plain-latex-book//:../../shared/classical-pdf//: SOURCE_DATE_EPOCH=1596240000 latexmk -xelatex -interaction=nonstopmode -halt-on-error mpg-myst-astro-spike.tex >/dev/null)
if grep -q 'Overfull \\hbox' generated/mpg-myst-astro-spike.log; then
  echo 'FAIL overfull PDF box'
  exit 1
fi
if grep -q 'LaTeX Font Warning' generated/mpg-myst-astro-spike.log; then
  echo 'FAIL PDF font substitution'
  exit 1
fi
cp generated/mpg-myst-astro-spike.pdf exports/mpg-myst-astro-spike.pdf

pdfinfo exports/mpg-myst-astro-spike.pdf > generated/pdfinfo.txt
pdffonts exports/mpg-myst-astro-spike.pdf > generated/pdffonts.txt
grep -q 'Pages:' generated/pdfinfo.txt
grep -q 'Page size:.*595.*841.*A4' generated/pdfinfo.txt
grep -q 'Charter' generated/pdffonts.txt
grep -Eq 'Bera|fvm' generated/pdffonts.txt
pdftotext -layout exports/mpg-myst-astro-spike.pdf generated/mpg-spike.txt
grep -q 'Program 1.1' generated/mpg-spike.txt
grep -q 'Program 4.1' generated/mpg-spike.txt
grep -q 'Program 5.1' generated/mpg-spike.txt
grep -q 'Program 5.2' generated/mpg-spike.txt
grep -q 'Fidelity sentinels for publication: -- ++ ->' generated/mpg-spike.txt
grep -q 'Table 1.1' generated/mpg-spike.txt
grep -q 'Gecode::Space' generated/mpg-spike.txt
grep -q 'Bibliography' generated/mpg-spike.txt
grep -Eq 'M +Modeling' generated/mpg-spike.txt
grep -q 'A first model' generated/mpg-spike.txt
grep -q 'Release invariant' generated/mpg-spike.txt
grep -q 'Tip 1.1 (Release invariant).' generated/mpg-spike.txt
! grep -q 'Figure 2: The checked search loop excerpt' generated/mpg-spike.txt
! grep -q 'Figure [0-9].*Posting the across and down table constraints' generated/mpg-spike.txt
! grep -q 'Figure [0-9].*Constructing a regular expression from line hints' generated/mpg-spike.txt

test -f dist/doc/6.4.0/modeling/index.html
test -f dist/doc/6.4.0/modeling/cross-page/index.html
test -f dist/doc/6.4.0/modeling/overview/index.html
test -f dist/doc/6.4.0/modeling/crossword/index.html
test -f dist/doc/6.4.0/modeling/nonogram/index.html
echo "PASS real Gecode C++ compile/run and byte-identical download"
echo "PASS offline MyST-to-Astro release build"
echo "PASS A4 PDF with matching chapter-scoped Program/Table semantics"
echo "PASS classical MPG part, chapter, tip, and program adapter"
