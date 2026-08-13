#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

test -x .venv/bin/sphinx-build || { echo "Run: uv venv --python 3.13 .venv && uv pip install --python .venv/bin/python -r requirements.lock"; exit 2; }
test -d node_modules || { echo "Run: npm ci"; exit 2; }

node ../shared/hard-pages/generate-assets.mjs content/assets/hard

# All publication inputs are local and pinned; poisoned proxies make accidental
# HTTP access fail during the clean rebuild.
export http_proxy=http://127.0.0.1:9
export https_proxy=http://127.0.0.1:9
export HTTP_PROXY=$http_proxy
export HTTPS_PROXY=$https_proxy
export NO_PROXY=localhost,127.0.0.1

.venv/bin/sphinx-build -E -W --keep-going -n -b mpg-semantic content build/semantic
npm run build:astro
npx astro check
.venv/bin/python scripts/check-unknown.py

GECODE_SOURCE_DIR=${GECODE_SOURCE_DIR:-/Users/zayenz/gecode/gecode-mpg-6.4.0}
GECODE_BUILD_DIR=${GECODE_BUILD_DIR:-$GECODE_SOURCE_DIR/build}
cmake -S . -B build/cpp -G Ninja -DGECODE_SOURCE_DIR="$GECODE_SOURCE_DIR" -DGECODE_BUILD_DIR="$GECODE_BUILD_DIR"
cmake --build build/cpp
ctest --test-dir build/cpp --output-on-failure
cmp examples/send-more-money.cpp public/downloads/send-more-money.cpp
cmp examples/send-more-money.cpp dist/downloads/send-more-money.cpp
echo "PASS canonical, downloaded, and compiled C++ inputs are byte-identical"

mkdir -p build/hard-examples
for example_source in ../shared/hard-pages/examples/*.cpp; do
  example_name="${example_source##*/}"
  example_name="${example_name%.cpp}"
  c++ -std=c++17 -Wall -Wextra -pedantic -I/opt/homebrew/include \
    "$example_source" -L/opt/homebrew/lib \
    -lgecodesearch -lgecodeminimodel -lgecodeint -lgecodekernel -lgecodesupport \
    -o "build/hard-examples/$example_name"
  cmp "$example_source" "public/downloads/$example_name.cpp"
  cmp "$example_source" "dist/downloads/$example_name.cpp"
done
node ../shared/hard-pages/verify.mjs build/hard-examples

DEPENDENCY_DIR=$(mktemp -d "${TMPDIR:-/tmp}/mpg-rst-dependency.XXXXXX")
trap 'rm -rf "$DEPENDENCY_DIR"' EXIT
.venv/bin/sphinx-build -W -n -b mpg-semantic content "$DEPENDENCY_DIR" >/dev/null
touch examples/send-more-money.cpp
.venv/bin/sphinx-build -W -n -b mpg-semantic content "$DEPENDENCY_DIR" >"$DEPENDENCY_DIR/rebuild.log"
grep -q '1 changed' "$DEPENDENCY_DIR/rebuild.log"
grep -q 'first-page' "$DEPENDENCY_DIR/rebuild.log"
.venv/bin/python scripts/check-dependency.py "$DEPENDENCY_DIR"
touch ../shared/hard-pages/examples/crossword-grid.cpp
.venv/bin/sphinx-build -W -n -b mpg-semantic content "$DEPENDENCY_DIR" >"$DEPENDENCY_DIR/crossword.log"
grep -q '1 changed' "$DEPENDENCY_DIR/crossword.log"
grep -q 'crossword' "$DEPENDENCY_DIR/crossword.log"
touch ../shared/hard-pages/examples/nonogram-heart.cpp
.venv/bin/sphinx-build -W -n -b mpg-semantic content "$DEPENDENCY_DIR" >"$DEPENDENCY_DIR/nonogram.log"
grep -q '1 changed' "$DEPENDENCY_DIR/nonogram.log"
grep -q 'nonogram' "$DEPENDENCY_DIR/nonogram.log"
echo "PASS each canonical C++ change invalidated exactly its owning page"

.venv/bin/sphinx-build -E -W --keep-going -n -b latex content build/latex
(cd build/latex && latexmk -pdfxe -interaction=nonstopmode -halt-on-error mpg-rst-spike.tex >/dev/null)
pdfinfo build/latex/mpg-rst-spike.pdf | grep -q 'Page size:.*A4'
grep -q '\\usepackage{mpg-sphinx}' build/latex/mpg-rst-spike.tex
grep -q '\\MPGPartNumber{13}{Modeling}' build/latex/mpg-rst-spike.tex
test -s build/latex/gecode-logo.pdf
pdffonts build/latex/mpg-rst-spike.pdf | grep -q 'Charter-Roman'
pdffonts build/latex/mpg-rst-spike.pdf | grep -q 'BeraSansMono-Roman'
! pdffonts build/latex/mpg-rst-spike.pdf | grep -q 'FontAwesome'
! grep -Eq 'Overfull|LaTeX Font Warning' build/latex/mpg-rst-spike.log
pdftotext -layout build/latex/mpg-rst-spike.pdf build/pdf.txt
grep -q 'This part demonstrates the classical MPG' build/pdf.txt
grep -Eq '^M +Modeling' build/pdf.txt
grep -q 'Tip 1.1 (Release publication)' build/pdf.txt
node scripts/check-output.mjs

mkdir -p tmp/pdfs
pdftoppm -png -r 110 build/latex/mpg-rst-spike.pdf tmp/pdfs/page >/dev/null 2>&1
echo "PASS rendered PDF pages are in tmp/pdfs for visual inspection"
