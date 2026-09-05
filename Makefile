.PHONY: all quick docs release web check check-sources build build-test build-notest test dist doctor clean

MPG_VERSION ?= 6.4.0
RST_BUILD ?= rst/_build
MPG_OUTPUT ?= output
PYTHON_VERSION ?=
UV ?= uv
UV_RUN = $(UV) run --locked $(if $(PYTHON_VERSION),--python $(PYTHON_VERSION),) -- python
MPG = $(UV_RUN) -m tools.mpg
AUTO_GECODE_ROOT := $(abspath ../gecode)
ifeq ($(strip $(GECODE_ROOT)$(GECODE_PREFIX)),)
ifneq ($(wildcard $(AUTO_GECODE_ROOT)/test/test.cpp),)
GC_ARGS = --gecode-root $(AUTO_GECODE_ROOT)
else
GC_ARGS =
endif
else
GC_ARGS = $(if $(GECODE_ROOT),--gecode-root $(GECODE_ROOT),) $(if $(GECODE_PREFIX),--gecode-prefix $(GECODE_PREFIX),)
endif

all: quick

quick: docs

docs: check-sources
	GECODE_VERSION=$(MPG_VERSION) $(UV_RUN) rst/scripts/build.py all --build $(RST_BUILD)

release: check docs
	$(UV_RUN) rst/scripts/package_release.py --build $(RST_BUILD) --output $(MPG_OUTPUT) --version $(MPG_VERSION)

web:
	npm run dev

check-sources:
	$(UV_RUN) rst/scripts/check_sources.py

check: check-sources
	$(UV_RUN) -m unittest discover -s tests -p 'test_*.py'
	$(UV_RUN) rst/scripts/verify_platform.py
	$(UV_RUN) rst/scripts/verify_examples.py $(GC_ARGS)

build:
	$(MPG) build --kind all $(GC_ARGS)

build-test:
	$(MPG) build --kind tests $(GC_ARGS)

build-notest:
	$(MPG) build --kind notest $(GC_ARGS)

test:
	$(MPG) test --kind all $(GC_ARGS)

dist: release

doctor:
	$(MPG) doctor $(GC_ARGS)

clean:
	$(MPG) clean $(GC_ARGS)
	$(UV_RUN) rst/scripts/build.py clean --build $(RST_BUILD)
