QUARTO ?= quarto
GECODE_PREFIX ?= ../../../../gecode/build/release-readiness-nompfr-install
BUILD := _build
GECODE_DIR := $(abspath $(GECODE_PREFIX)/lib/cmake/Gecode)

.PHONY: render html pdf extract code-test output-test verify clean

render:
	$(QUARTO) render

html: render

pdf: render

extract:
	python3 scripts/extract_sources.py

code-test: extract
	cmake -S . -B $(BUILD)/cmake -G Ninja -DGecode_DIR=$(GECODE_DIR)
	cmake --build $(BUILD)/cmake
	ctest --test-dir $(BUILD)/cmake --output-on-failure

output-test: render extract
	python3 scripts/check_outputs.py

verify: code-test output-test

clean:
	cmake -E remove_directory $(BUILD)
	cmake -E remove_directory .quarto
	cmake -E remove_directory site_libs
	cmake -E remove_directory tmp
	cmake -E rm -f Modeling-and-Programming-with-Gecode.tex
	cmake -E rm -f figures/propagation.svg figures/propagation.pdf
