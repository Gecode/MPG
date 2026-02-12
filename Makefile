.PHONY: all quick docs extract build build-test build-notest test dist doctor clean tex gcc gcc-test gcc-notest

UV ?= uv
MPG = $(UV) run -- python -m tools.mpg
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

docs:
	$(MPG) docs $(GC_ARGS)

extract:
	$(MPG) extract $(GC_ARGS)

build:
	$(MPG) build --kind all $(GC_ARGS)

build-test:
	$(MPG) build --kind tests $(GC_ARGS)

build-notest:
	$(MPG) build --kind notest $(GC_ARGS)

test:
	$(MPG) test --kind all $(GC_ARGS)

dist:
	$(MPG) dist $(GC_ARGS)

doctor:
	$(MPG) doctor $(GC_ARGS)

clean:
	$(MPG) clean $(GC_ARGS)

tex: extract
gcc: build
gcc-test: build-test
gcc-notest: build-notest
