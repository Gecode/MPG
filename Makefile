.PHONY: all quick tex gcc gcc-test gcc-notest test docs dist clean realclean veryclean doctor

UV ?= uv
export UV_CACHE_DIR ?= $(CURDIR)/.mpg/uv-cache
export UV_PROJECT_ENVIRONMENT ?= $(CURDIR)/.mpg/.venv
MPG = $(UV) run -- python bin/mpg.py
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

tex:
	$(MPG) extract $(GC_ARGS)

gcc:
	$(MPG) build --kind all $(GC_ARGS)

gcc-test:
	$(MPG) build --kind tests $(GC_ARGS)

gcc-notest:
	$(MPG) build --kind notest $(GC_ARGS)

test:
	$(MPG) test --kind all $(GC_ARGS)

dist:
	$(MPG) dist $(GC_ARGS)

doctor:
	$(MPG) doctor $(GC_ARGS)

clean:
	$(MPG) clean $(GC_ARGS)

realclean: clean
veryclean: clean
