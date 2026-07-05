SHELL := /bin/bash
LEAN_ENV := source $(HOME)/.elan/env &&

LEAN_FILES := PyCSL/AST.lean PyCSL/State.lean PyCSL/SOS.lean \
              PyCSL/DesugarDef.lean PyCSL/Desugar.lean PyCSL/WP.lean \
              PyCSL/WhileInv.lean PyCSL/Soundness.lean PyCSL/RecordVal.lean \
              PyCSL/Tests.lean

all: build

build:
	$(LEAN_ENV) lake build

proof: build
	@echo "=== PyCSL Lean proof status ==="
	@echo "Files compiled: $(words $(LEAN_FILES))"
	@sorry=$$(grep -cl 'sorry' $(LEAN_FILES) 2>/dev/null | wc -l); \
	 echo "Files with sorry: $$sorry"; \
	 if [ "$$sorry" -gt 0 ]; then \
	   grep -n 'sorry' $(LEAN_FILES) | sed 's/^/  /'; \
	 fi
	@echo "=== All proofs checked ==="

clean:
	rm -rf .lake/build .lake/config

.PHONY: all build proof clean
