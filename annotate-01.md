# annotate-01.md — Self-Annotation Refresh Plan

**Status:** ⚠️ **Historical document.** This plan proposed moving the
`lean/` and `rocq/` mirrors into `src/self-annotate/attic/`. That move
was carried out, then the `attic/` directory itself was removed on
2026-05-27 (see `proof-to-axiom-from.md`). The text below is preserved
as historical context; do not re-execute its steps.

## Context

PyCSL's self-annotation effort annotates its own Python implementation with `#@`
contracts derived from the machine-checked formal proofs in `src/formal-semantics/`.
The goal is to close the trust gap between the Lean/Rocq soundness theorem and the
Python code that actually runs.

The current directory layout is:

```
src/self-annotate/
  lean/      ← 355 #@ annotations, derived from Lean proofs;  all pass pycsl --no-proof  ✓
  rocq/      ← 355 #@ annotations, derived from Rocq proofs;  all pass pycsl --no-proof  ✓
  src/       ← STALE — pre-refactoring snapshot of src/pycsl/; barely annotated
```

`src/self-annotate/src/` predates the master refactoring that moved `_MODULE_PREFIXES`
to module scope and added `from __future__ import annotations`. Its annotations (well
below 100 total) are a subset of what `lean/` and `rocq/` already carry. The real
annotation work product is in `lean/` and `rocq/`.

**Scope:** only the 11 flat `.py` files directly under `src/pycsl/` — the six pipeline
modules, support files, and the CLI. The `agents/` subdirectory is **excluded** from
annotation (meta-tooling, outside the formal model per §7 of README).

`src/pycsl/` has also been modified since the `lean/` and `rocq/` copies were made
(git status shows `M` on all Module files and ConcurrencyChecker).

---

## Should the existing `src/self-annotate/src/` annotations be kept?

**No — trash them.** They are:
- Pre-refactoring (structural inconsistencies vs current master: wrong placement of
  `_MODULE_PREFIXES`, missing `from __future__ import annotations`)
- Far fewer annotations than `lean/` or `rocq/` (same files, strictly worse)
- Not tested or kept in sync

The `lean/` and `rocq/` copies are the authoritative annotation work products and
must be the reference for the refresh.

---

## Design decisions

| Decision | Choice | Rationale |
|---|---|---|
| Role of `src/self-annotate/src/` | **Single annotation target going forward** | Merge lean+rocq into one canonical copy; lean/ and rocq/ served as cross-validation and are now superseded |
| `agents/` subdirectory | **Excluded** | Meta-tooling outside the formal model (§7); not formally verified |
| Formal semantics reference | **Both Lean and Rocq** | Contracts are identical across the two (confirmed by lean/ vs rocq/ parity); read whichever is clearer per file |

---

## Phase 0 — Trash and refresh `src/self-annotate/src/`

Delete the stale `.py` files and replace with current master copies:

```bash
# Remove stale copies
rm src/self-annotate/src/*.py

# Copy current master (flat files only, no agents/)
cp src/pycsl/Module1_Ingestor.py          src/self-annotate/src/
cp src/pycsl/Module2_Parser.py            src/self-annotate/src/
cp src/pycsl/Module3_Weaver.py            src/self-annotate/src/
cp src/pycsl/Module4_SemanticAnalyzer.py  src/self-annotate/src/
cp src/pycsl/Module5_IREmitter.py         src/self-annotate/src/
cp src/pycsl/Module6_WhyMLTranspiler.py   src/self-annotate/src/
cp src/pycsl/ConcurrencyChecker.py        src/self-annotate/src/
cp src/pycsl/ir_schema.py                 src/self-annotate/src/
cp src/pycsl/errors.py                    src/self-annotate/src/
cp src/pycsl/pycsl.py                     src/self-annotate/src/
cp src/pycsl/__init__.py                  src/self-annotate/src/
```

Result: 11 fresh, unannotated files in `src/self-annotate/src/`, structurally
identical to the current master.

---

## Phase 1 — Port existing annotations from `lean/` into `src/`

For each of the 9 files that already have annotations in `lean/`, diff the lean/
copy against the fresh master copy and re-apply annotations, adapting for any
structural drift (new methods, renamed methods, moved code blocks):

| File | Annotations in lean/ | Layer | Notes |
|---|---|---|---|
| `Module6_WhyMLTranspiler.py` | **155** | A + B | Largest; do careful diff; highest priority |
| `Module2_Parser.py` | 72 | A | 53 AST node dataclasses + parser methods |
| `Module3_Weaver.py` | 49 | A | CST transform visitors |
| `Module5_IREmitter.py` | 38 | A | IR emission methods |
| `Module1_Ingestor.py` | 18 | A | CST visitor interface |
| `Module4_SemanticAnalyzer.py` | 8 | C | Validator / well-formedness |
| `ConcurrencyChecker.py` | 8 | A | Infrastructure analysis pass |
| `ir_schema.py` | 5 | A | Dataclass constructors |
| `pycsl.py` | 2 | A | CLI/I/O; minimal by design |

`errors.py` and `__init__.py` have zero annotations (exception classes and empty
module init — outside formal model per §7).

**Porting procedure per file:**

1. Diff: `diff src/self-annotate/lean/<file>.py src/pycsl/<file>.py`
2. For each `#@` block in lean/, locate the corresponding method in the fresh src/ copy.
   - If the method is unchanged → apply the annotation verbatim.
   - If the method was added or renamed in master → write a fresh annotation following
     the same contract pattern (see formal semantics reference below).
   - If the method was deleted in master → skip.
3. Verify: `python3 src/pycsl/pycsl.py --no-proof src/self-annotate/src/<file>.py`

**Formal semantics reference per file:**

| File | Lean proof | Rocq proof | What to extract |
|---|---|---|---|
| `Module6_WhyMLTranspiler.py` | `PyCSL/WP.lean` | `Phase4_WP.v` | Each WP arm → `assigns` clause + `ensures \result != ""` |
| | `PyCSL/WhileInv.lean` | `Phase5a_WhileInv.v` | All `while` loops → `loop invariant 0 <= i and i <= n` + `loop variant n - i` |
| | `PyCSL/Soundness.lean` | `Phase5b_Soundness.v` | `transpile()` full frame condition (15 mutable fields) |
| | `PyCSL/Desugar.lean` | `Phase3b_Desugar.v` | `_handle_for_stmt`: `requires iter_var != "_pycsl_idx"` |
| `Module2_Parser.py` | `PyCSL/AST.lean` | `Phase1_AST.v` | Dataclass class invariants (`self.expr is not None`) |
| `Module5_IREmitter.py` | `PyCSL/SOS.lean` | `Phase3_SOS.v` | `ensures \forall i, 0 <= i and i < \length(\result) ==> \result[i] is not None` |
| Modules 1, 3, 4 | — | — | Layer A structural only; `assigns \nothing` for pure visitors |

---

## Phase 2 — Handle new methods in master not present in lean/

After porting, check for methods in the fresh `src/` copy that have no counterpart
in lean/ (i.e., added after the lean/ snapshot). For each such method:

- **Falls under an existing WP arm** (e.g., a new helper for `_handle_while_stmt`):
  add `assigns` matching the enclosing handler's frame condition.
- **Pure helper** (no mutable state): add `assigns \nothing` + `ensures \result is not None`.
- **I/O, subprocess, or string assembly** outside the formal model (§7): skip.

This applies primarily to `Module6_WhyMLTranspiler.py`, the most actively modified file.

---

## Phase 3 — Deprecate lean/ and rocq/ directories

Once `src/self-annotate/src/` has full parity with lean/ (≥ 355 annotations, all
passing `pycsl --no-proof`):

1. `mv src/self-annotate/lean src/self-annotate/attic/lean`
2. `mv src/self-annotate/rocq src/self-annotate/attic/rocq`
3. Update `src/self-annotate/README.md`: replace the layout section to list `src/`
   as the single canonical annotated directory.
4. Update `src/self-annotate/coverage-report.md`: regenerate annotation counts
   from `src/`.

---

## Phase 4 — Automation: sync target

Add a `Makefile` target so that when `src/pycsl/` gets new methods, `src/` can be
refreshed. Because the target overwrites, it is an intentionally manual step:

```makefile
.PHONY: sync-annotate-src
sync-annotate-src:
	@for f in Module1_Ingestor Module2_Parser Module3_Weaver \
	           Module4_SemanticAnalyzer Module5_IREmitter Module6_WhyMLTranspiler \
	           ConcurrencyChecker ir_schema errors pycsl __init__; do \
	    cp src/pycsl/$$f.py src/self-annotate/src/$$f.py; \
	done
	@echo "WARNING: annotations overwritten — diff and re-apply from lean/ reference"

.PHONY: verify-annotated
verify-annotated:
	@for f in src/self-annotate/src/*.py; do \
	    python3 src/pycsl/pycsl.py --no-proof $$f || exit 1; \
	done
	@echo "All annotated files pass pycsl --no-proof"
```

---

## Verification checklist

1. `ls src/self-annotate/src/*.py | wc -l` → 11
2. No `agents/` directory under `src/self-annotate/src/`
3. `grep "_MODULE_PREFIXES" src/self-annotate/src/Module1_Ingestor.py` → at module scope (line < 20)
4. `python3 src/pycsl/pycsl.py --no-proof src/self-annotate/src/Module6_WhyMLTranspiler.py` → passes
5. `for f in src/self-annotate/src/*.py; do python3 src/pycsl/pycsl.py --no-proof $f; done` → all 11 pass
6. `grep -c "#@" src/self-annotate/src/Module6_WhyMLTranspiler.py` → ≥ 155
7. Total `#@` count across `src/` → ≥ 355
8. `ls src/self-annotate/attic/lean/ src/self-annotate/attic/rocq/` → both present (moved, not deleted)

---

## Open risks

| Risk | Mitigation |
|---|---|
| Module6 structural drift — new methods added since lean/ snapshot | Port existing 155 first; handle new methods per Phase 2 rule |
| `wp_for_desugar` coherence still sorry/admit — `_handle_for_stmt` Layer B is weakest link | Carry forward from lean/; no new sorry introduced |
| `skip_code_state_coherent`, `array_set_code_state_coherent`, `seq_code_state_coherent` — human-audited axioms | Carry forward from lean/; no new axioms introduced |

---

## Summary

| Phase | What | Files | Priority |
|---|---|---|---|
| 0 | Trash stale `src/`, copy 11 fresh files from master | 11 files | **Immediate** |
| 1 | Port 355 annotations from `lean/` → `src/` | 9 annotated files | **Immediate** |
| 2 | Handle new methods in master not yet in `lean/` | `Module6` primarily | **During Phase 1** |
| 3 | Deprecate `lean/` and `rocq/` → `attic/` | Directory moves only | **After Phase 1+2 verified** |
| 4 | Makefile `sync-annotate-src` + `verify-annotated` targets | `Makefile` | **After Phase 3** |
