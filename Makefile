
PYTHON:=./.venv/bin/python

.venv:
	python3 -m venv .venv
	./.venv/bin/pip install libcst lark
	./.venv/bin/pip install numpy
	./.venv/bin/pip install -e .

default: .venv
	$(PYTHON) tests/integration/test_123456.py
	why3 prove -P z3 pycsl_out.mlw

# --- skill2rag (RAG indexing for skills) ---

rag-build: .venv
	$(PYTHON) -m skill2rag build

rag-query: .venv
	@test -n "$(Q)" || (echo "Usage: make rag-query Q='your question'" && exit 1)
	$(PYTHON) -m skill2rag query -q "$(Q)"

rag-chunks: .venv
	$(PYTHON) -m skill2rag chunks

self-annotate-generate: .venv
	./bin/self-annotate-generate.sh

self-annotate-verify: .venv
	@echo "=== Self-annotation verification (rocq path) ==="
	@for f in src/self-annotate/attic/rocq/*.py; do \
	    result=$$($(PYTHON) src/pycsl/pycsl.py --no-proof $$f 2>&1 | tail -1); \
	    if echo "$$result" | grep -q 'SUCCESS'; then \
	        echo "  ✓ $$f"; \
	    else \
	        echo "  ✗ $$f: $$result"; exit 1; \
	    fi; \
	done
	@echo "=== Self-annotation verification (lean path) ==="
	@for f in src/self-annotate/attic/lean/*.py; do \
	    result=$$($(PYTHON) src/pycsl/pycsl.py --no-proof $$f 2>&1 | tail -1); \
	    if echo "$$result" | grep -q 'SUCCESS'; then \
	        echo "  ✓ $$f"; \
	    else \
	        echo "  ✗ $$f: $$result"; exit 1; \
	    fi; \
	done
	@echo "=== Self-annotation verification (canonical src/ — Layer 4 attributed) ==="
	@for f in src/self-annotate/src/*.py; do \
	    result=$$($(PYTHON) src/pycsl/pycsl.py --no-proof $$f 2>&1 | tail -1); \
	    if echo "$$result" | grep -q 'SUCCESS'; then \
	        echo "  ✓ $$f"; \
	    else \
	        echo "  ✗ $$f: $$result"; exit 1; \
	    fi; \
	done
	@echo "=== All self-annotation files pass pycsl --no-proof ==="
	@echo ""
	@$(MAKE) check-proof-attributions

# Audit every `#@ proof rocq:` / `#@ proof lean:` directive in the annotated
# corpus resolves to an actual theorem/lemma/inductive/record in the
# corresponding proof file. See bin/check-proof-attributions.sh for the
# namespace registry.
.PHONY: check-proof-attributions
check-proof-attributions:
	@bash bin/check-proof-attributions.sh

# sync-annotate-src: copy fresh master files into src/self-annotate/src/
# WARNING: overwrites unannotated content — diff and re-apply any new-method
# annotations afterward.  Existing #@ lines for unchanged methods survive
# because src/ is rebuilt by port_annotations.py, not by raw cp.
.PHONY: sync-annotate-src
sync-annotate-src: .venv
	@echo "WARNING: refreshing src/self-annotate/src/ from master — re-apply annotations for any new methods"
	@for f in Module1_Ingestor Module2_Parser Module3_Weaver \
	           Module4_SemanticAnalyzer Module5_IREmitter Module6_WhyMLTranspiler \
	           ConcurrencyChecker ir_schema errors pycsl __init__; do \
	    cp src/pycsl/$$f.py src/self-annotate/src/$$f.py; \
	done
	@echo "Done. Run: python3 /tmp/port_annotations.py attic/rocq/<file>.py src/<file>.py  for each changed file"

# verify-annotated: verify all files in the canonical src/ directory
.PHONY: verify-annotated
verify-annotated: .venv
	@echo "=== Canonical self-annotation verification (src/ path) ==="
	@pass=0; fail=0; \
	for f in src/self-annotate/src/*.py; do \
	    result=$$($(PYTHON) src/pycsl/pycsl.py --no-proof $$f 2>&1 | tail -1); \
	    if echo "$$result" | grep -q 'SUCCESS'; then \
	        echo "  ✓ $$f"; pass=$$((pass+1)); \
	    else \
	        echo "  ✗ $$f: $$result"; fail=$$((fail+1)); \
	    fi; \
	done; \
	echo "=== $$pass pass, $$fail fail ==="; \
	test $$fail -eq 0

self-annotate: self-annotate-verify

clean:
	rm -rf *~ .venv __pycache__ pycsl_ir.json pycsl_out.mlw
	rm -rf `find . -name __pycache__`
	rm -f data/embeddings/skills_index.json
