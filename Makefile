
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
	@echo "=== Self-annotation verification (canonical src/) ==="
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
	@echo ""
	@$(MAKE) check-proof-crosscheck
	@echo ""
	@$(MAKE) check-axiom-registry-emittable
	@echo ""
	@$(MAKE) check-axiom-registry-drift
	@echo ""
	@$(MAKE) stdlib-coverage

# Phase 0 of the fully-annotated-stdlib strategy: classify every
# stub function in `src/pycsl_lib/` by annotation depth (L1
# typed → L5 tested) and regenerate `docs/stdlib-coverage.md`.
# Pure reporting — does not modify any stub. The squeeze is the
# monotonic ratchet enforced by reviewer attention on every PR:
# coverage percentages should never drop. See
# `.claude/plans/parsed-booping-ember.md` for the strategy.
.PHONY: stdlib-coverage
stdlib-coverage: .venv
	@echo "=== Stdlib stub annotation coverage ==="
	@$(PYTHON) bin/stdlib-coverage-report.py --gen-doc
	@$(PYTHON) bin/stdlib-coverage-report.py | tail -30

# `proof2why3 emit` round-trip: every `_AXIOM_REGISTRY` body parses,
# canonicalizes, emits, re-parses, and canonicalizes to the same IR.
# Closes the loop on the registry-as-cache pattern (todo-saturday.md
# Item 3). Pure verification — does not modify `preamble.py`.
.PHONY: check-axiom-registry-emittable
check-axiom-registry-emittable: .venv
	@echo "=== proof2why3 emit round-trip ==="
	@$(PYTHON) bin/proof2why3-emit.py --check

# Drift detection between hand-curated `_AXIOM_REGISTRY` bodies and
# the auto-generated form from cross-checked Rocq + Lean proofs.
# Dry-run: non-zero exit when any added/replaced entry is detected.
# To apply the changes, run `make sync-axiom-registry`.
.PHONY: check-axiom-registry-drift
check-axiom-registry-drift: .venv
	@echo "=== proof2why3 registry drift check ==="
	@$(PYTHON) bin/proof2why3-merge-registry.py

# Regenerate `_AXIOM_REGISTRY` from cross-checked IR — drift-aware:
# entries that already match the canonical form retain their
# hand-curated variable names; only added/replaced entries get the
# auto-generated v0/v1/… form. Always re-run `make
# self-annotate-verify` after a sync to confirm the cross-check
# still passes.
.PHONY: sync-axiom-registry
sync-axiom-registry: .venv
	@echo "=== proof2why3 sync-axiom-registry ==="
	@$(PYTHON) bin/proof2why3-merge-registry.py --write

# Mechanical 3-way cross-check: for every cited `#@ proof rocq/lean`
# qualname, extract the theorem statement from both prover proof
# files (via coqc Check / lake env lean #check), parse to a shared
# first-order IR, canonicalize, and verify it structurally equals the
# Module 6 `_AXIOM_REGISTRY` body. Closes Goal A of sticky-01.md /
# sticky-02.md — the three manual trust assumptions in
# 0342_explanation.md §4.3 collapse to one mechanical predicate.
.PHONY: check-proof-crosscheck
check-proof-crosscheck: .venv
	@bash bin/check-proof-crosscheck.sh

# Audit every `#@ proof rocq` / `#@ proof lean` directive in the
# annotated corpus. The audit invokes `pycsl --audit-proof <file>` per file
# and parses Rocq / Lean proof files namespace-aware (see
# src/pycsl/audit_proof.py). Each file's default proof dir is
# `<file>.proofs/{rocq,lean}/` next to it.
.PHONY: check-proof-attributions
check-proof-attributions:
	@total_pass=0; total_skip=0; total_fail=0; \
	for f in src/self-annotate/src/*.py test-suite/corpus/pycsl-reference/*.py; do \
	    [ -f "$$f" ] || continue; \
	    output=$$($(PYTHON) src/pycsl/pycsl.py --audit-proof "$$f" 2>&1); \
	    p=$$(echo "$$output" | sed -n 's/.*Passed:  *\([0-9][0-9]*\).*/\1/p'); \
	    s=$$(echo "$$output" | sed -n 's/.*Skipped: *\([0-9][0-9]*\).*/\1/p'); \
	    fl=$$(echo "$$output" | sed -n 's/.*Failed:  *\([0-9][0-9]*\).*/\1/p'); \
	    if [ -z "$$p" ]; then p=0; fi; if [ -z "$$s" ]; then s=0; fi; if [ -z "$$fl" ]; then fl=0; fi; \
	    total_pass=$$((total_pass + p)); \
	    total_skip=$$((total_skip + s)); \
	    total_fail=$$((total_fail + fl)); \
	    if [ "$$fl" != "0" ]; then \
	        echo "$$output"; \
	    fi; \
	done; \
	echo "=== Proof-attribution audit summary ==="; \
	echo "  Passed:  $$total_pass"; \
	echo "  Skipped: $$total_skip"; \
	echo "  Failed:  $$total_fail"; \
	test "$$total_fail" = "0"

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
	@echo "Done."

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

# Extreme Rigor gate. Runs the feature-supervisor over the ER-managed
# plans and the load-bearing retrospective check. This is the CI / local
# entry point for ER (gap 8 of the post-implementation retrospective).
#
# CMMI_AUDIT_NESTED=1 is exported for the whole target: the plans'
# acceptance claims shell out to `cmmi-audit.sh --quick`, whose `[ER]`
# step would otherwise re-enter this retrospective and recurse. The guard
# makes every nested cmmi-audit skip the `[ER]` step. See infinite-rec.md.
#
# `timeout` bounds each supervisor run so a regression spikes one run, not
# an unbounded process tree.
.PHONY: er-check
er-check: .venv
	@echo "=== Extreme Rigor gate (er-check) ==="
	@export CMMI_AUDIT_NESTED=1; \
	fail=0; \
	echo "--- required: ER plan must verify (exit 0) ---"; \
	timeout 600 bin/agent-feature-supervisor --feature-file feature-supervisor-extreme-rigor.md --skip-gate || { echo "  ✗ ER plan did not verify"; fail=1; }; \
	echo "--- required: ER fixture tests ---"; \
	$(PYTHON) -m pytest test-suite/agent-tests/test_supervisor_er.py -q || { echo "  ✗ ER fixture tests failed"; fail=1; }; \
	echo "--- required: parent plan must verify (exit 0) ---"; \
	timeout 600 bin/agent-feature-supervisor --feature-file missing-bytes-struct-feature.md --skip-gate || { echo "  ✗ missing-bytes-struct plan did not verify"; fail=1; }; \
	echo "--- required: retrospective mechanism is load-bearing ---"; \
	timeout 600 bin/er-retrospective-check.sh || { echo "  ✗ retrospective check failed"; fail=1; }; \
	echo "--- informational: all other missing-*.md plans ---"; \
	for plan in missing-*.md proposed-features/missing-*.md; do \
	    [ -f "$$plan" ] || continue; \
	    case "$$plan" in missing-bytes-struct-feature.md) continue;; esac; \
	    timeout 600 bin/agent-feature-supervisor --feature-file "$$plan" --skip-gate >/dev/null 2>&1; \
	    rc=$$?; \
	    if [ "$$rc" = "0" ]; then echo "  ✓ $$plan (exit 0)"; \
	    elif [ "$$rc" = "75" ]; then echo "  • $$plan (exit 75 — open phases with unmet acceptance; expected for in-progress plans)"; \
	    else echo "  ? $$plan (exit $$rc)"; fi; \
	done; \
	test "$$fail" = "0"

clean:
	rm -rf *~ .venv __pycache__ pycsl_ir.json pycsl_out.mlw
	rm -rf `find . -name __pycache__`
	rm -f data/embeddings/skills_index.json
