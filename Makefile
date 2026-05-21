
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
	@for f in src/self-annotate/rocq/*.py; do \
	    result=$$($(PYTHON) src/pycsl/pycsl.py --no-proof $$f 2>&1 | tail -1); \
	    if echo "$$result" | grep -q 'SUCCESS'; then \
	        echo "  ✓ $$f"; \
	    else \
	        echo "  ✗ $$f: $$result"; exit 1; \
	    fi; \
	done
	@echo "=== Self-annotation verification (lean path) ==="
	@for f in src/self-annotate/lean/*.py; do \
	    result=$$($(PYTHON) src/pycsl/pycsl.py --no-proof $$f 2>&1 | tail -1); \
	    if echo "$$result" | grep -q 'SUCCESS'; then \
	        echo "  ✓ $$f"; \
	    else \
	        echo "  ✗ $$f: $$result"; exit 1; \
	    fi; \
	done
	@echo "=== All self-annotation files pass pycsl --no-proof ==="

self-annotate: self-annotate-verify

clean:
	rm -rf *~ .venv __pycache__ pycsl_ir.json pycsl_out.mlw
	rm -rf `find . -name __pycache__`
	rm -f data/embeddings/skills_index.json
