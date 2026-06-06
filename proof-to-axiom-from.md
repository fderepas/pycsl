# Triage `#@ proof rocq:` / `#@ proof lean:` directives — keep only load-bearing

**Status:** ⚠️ **Historical document.** This triage shipped 2026-05-27.
The colon-separated provenance `proof` directive was removed from the
language; the remaining load-bearing `axiom_from` was then renamed
back to `proof` (space-separated). The current syntax is
`#@ proof <prover> <qualname>`. The text below is preserved as
historical context; do not re-execute its steps.

**Original date:** 2026-05-27
**Scope:** Triage all 156 `proof` (provenance-only) directives in `src/self-annotate/src/` and decide per-directive: **delete** (default), **convert to `axiom_from`**, or **keep** (with strong justification). After triage, every remaining `proof` or `axiom_from` directive must be load-bearing or explicitly justified.
**Mode:** Delete-heavy.

## Context

The user wants only load-bearing annotations on PyCSL functions. Today's audit count is 162 PASS / 5 SKIP / 0 FAIL across 172 directives:

| Form | Count | Where | Load-bearing? |
|---|---|---|---|
| `#@ proof rocq:` | 79 | Module2-6 | No — provenance-only |
| `#@ proof lean:` | 77 | Module2-6 | No — provenance-only |
| `#@ axiom_from rocq` | 8 | 0342.py (Gcd) | Yes — emits Why3 axioms |
| `#@ axiom_from lean` | 8 | 0342.py (Gcd) | Yes — emits Why3 axioms |

The 156 `proof` directives cite Pycsl.Reference.Module<N>.* theorems in `src/formal-semantics/rocq/` + `src/formal-semantics/lean/PyCSL/`. Sampling reveals most cite **meta-theorems** about PyCSL semantics (`Module6.wp`, `Module6.handle_assign_branches_correct`, `Module6.while_inv_preserved`) rather than facts about individual function contracts. Meta-theorems aren't convertible to load-bearing `axiom_from` without re-stating them at the function-contract level.

The `_AXIOM_REGISTRY` in `Module6_WhyMLTranspiler.py:3603` is hand-curated (7 entries today, all Gcd). Growing it by 78 entries would require careful theorem-to-axiom translation for each, with a real soundness risk if the translation is incorrect.

**Decision:** Delete-heavy triage. Convert only where the cited theorem demonstrably encodes a function-contract fact AND the Rocq + Lean source is fully proved.

## Recommended approach

### Triage tree (apply per directive)

```
For each cited qualname Q citing function F:
  1. Find Q in src/formal-semantics/{rocq,lean}/ or test-suite/.../*.proofs/.
     ├── Not found → AUDIT BUG, fix audit registry or delete cite.
     └── Found:
  2. Is the file containing Q fully proved? (no Admitted, no Axiom, no sorry,
     no recursive dependency on a partially-proved theorem)
     ├── No → DELETE Q's cite from F. The provenance points at incomplete work.
     └── Yes:
  3. Read Q's statement. Does it encode a fact about F's input/output
     contract (`requires`/`ensures`/`assigns`)?
     ├── No (meta-theorem about PyCSL semantics) → DELETE. The cite is
     │   structural documentation that belongs in a code comment or in
     │   `docs/`, not in a load-bearing position.
     ├── Yes, but Q's statement uses a vocabulary alien to F's contract
     │   (talks about IR nodes, AST shapes, abstract states) → DELETE
     │   unless a useful WhyML axiom can be derived (rare).
     └── Yes, statement maps cleanly to a Why3-expressible fact about F:
  4. Write the WhyML axiom body for Q. Cross-check against the Rocq
     statement line-by-line. Add to `_AXIOM_REGISTRY` and (if needed)
     `_AXIOM_FUNCTIONS`.
  5. Replace `#@ proof rocq: Q` + `#@ proof lean: Q` with
     `#@ axiom_from rocq Q` + `#@ axiom_from lean Q`.
  6. Verify F's module under full proof. The audit must still pass.
     The full-proof status of unrelated functions in the same module
     should not regress (i.e., no new VC failures elsewhere).
```

### Expected outcomes for the 156 Module2-6 `proof` directives

Based on the sampling (`Module6.wp`, `Module6.handle_assign_branches_correct`, `Module2.contract_expr`, etc.) and the proof-file inventory:

| Outcome | Estimated count | Reasoning |
|---|---|---|
| **DELETE** (file has Admitted/Axiom/sorry) | ~40 | Cites into `Phase5b_Soundness`, `Phase6i`, `Phase6k`, `Phase6m`, `SoundnessVerified.lean`, `Tests.lean`, `VcgEmission`, `Why3Vcg`, `Why3Trust` — see Step 1 of triage tree. |
| **DELETE** (meta-theorem, not contract-level) | ~110 | Cites into proved meta-theorems (`Module6.wp`, `Module2.contract_expr`, etc.) that describe the calculus, not F's local contract. |
| **CONVERT** to `axiom_from` | ~5 (maybe 0) | Only if a fully-proved Rocq + Lean theorem encodes a Why3-expressible fact about F's contract. Likely rare for Module2-6 since the proof files are about semantics, not implementation. |
| **KEEP** as `proof` | 0 | The user's stated goal: no provenance-only directives. If a directive can't become load-bearing, delete it (or move provenance to a comment / docstring outside the `#@` lines). |

The 16 `axiom_from` directives in `0342.py` remain unchanged — they're the model for this triage.

## Critical files

- **Inventory + decisions**: New file `proof-triage-inventory.tsv` (intermediate artifact, can be deleted at end). Columns: `qualname`, `file`, `lineno`, `function`, `directive_type`, `decision (DELETE/CONVERT/KEEP)`, `rationale`.
- **Edited**: All 11 self-annotated files in `src/self-annotate/src/*.py` (and the matching attic mirrors if sync is desired):
  - `Module1_Ingestor.py`
  - `Module2_Parser.py`
  - `Module3_Weaver.py`
  - `Module4_SemanticAnalyzer.py`
  - `Module5_IREmitter.py`
  - `Module6_WhyMLTranspiler.py`
  - `ConcurrencyChecker.py`
- **Edited** (only if CONVERT cases land): `src/pycsl/Module6_WhyMLTranspiler.py:3603` — `_AXIOM_REGISTRY` dict, plus `_AXIOM_FUNCTIONS` at line 3625 if new backing functions are needed.
- **Unchanged**: `bin/check-proof-attributions.sh` — the audit treats both directives identically and doesn't need a code change. Its PASS count will drop from 162 toward ~16 (the Gcd directives + any CONVERT survivors).
- **Updated docstrings/comments only** (not load-bearing): for any deleted directive whose provenance link is still useful, move the citation into a code comment ABOVE the `def`, like:
  ```python
  # Implements the WP calculus from Phase4_WP.v (Pycsl.Reference.Module6.wp).
  # See docs/cross-validated-spec-sources.md for the cross-prover audit.
  def some_function(...) -> ...:
  ```

## Phased execution (per module)

Smallest modules first to build confidence:

### Phase 1 — `__init__.py` + `errors.py` + `ir_schema.py`
These have no directives today (per audit). Skip.

### Phase 2 — `ConcurrencyChecker.py` (estimated 7 directives)
Walk through each, apply triage tree. Most likely all delete (the file's responsibility is concurrency analysis, not WP-calculus implementation).

### Phase 3 — `Module1_Ingestor.py` (estimated 6 directives)
Same pattern. Likely all delete.

### Phase 4 — `Module3_Weaver.py` (estimated 8 directives)

### Phase 5 — `Module2_Parser.py` (estimated 8 directives)

### Phase 6 — `Module4_SemanticAnalyzer.py` (estimated 16 directives)

### Phase 7 — `Module5_IREmitter.py` (estimated 50 directives)

### Phase 8 — `Module6_WhyMLTranspiler.py` (estimated 44 directives)

### Phase 9 — Final audit
- Run `make self-annotate-verify`. Audit count should drop from 162 → ~16 (or wherever CONVERT survivors land). FAILED count must remain 0.
- Run full-proof on each module and on all reference tests (0331, 0341–0351). No new VC failures.
- Spot-check pytest: 25 pass, 3 skip.

After each phase, commit so changes are bisectable.

## Per-phase recipe

For each phase:

```bash
# 1. Extract that module's directives.
grep -nE "^\s*#@ (proof|axiom_from) (rocq|lean)" src/self-annotate/src/<MODULE>.py

# 2. For each directive, look up the cited theorem.
# Use Rocq:
grep -rn "Theorem <name>\b\|Lemma <name>\b\|Definition <name>\b" src/formal-semantics/rocq/
# Use Lean:
grep -rn "theorem <name>\b\|lemma <name>\b\|def <name>\b" src/formal-semantics/lean/PyCSL/

# 3. Inspect the file for Admitted/sorry/Axiom around it.
# (If the file has any, scrutinize whether the cited theorem TRANSITIVELY
#  depends on an incomplete one. If yes, decision = DELETE.)

# 4. Apply the triage tree. Record decision + rationale in the
# inventory TSV.

# 5. Edit the .py file: either delete the two-line citation block,
#    or rewrite as axiom_from. If CONVERT, also extend _AXIOM_REGISTRY
#    in src/pycsl/Module6_WhyMLTranspiler.py.

# 6. Verify the module:
PYTHONPATH=src .venv/bin/python -c "from pycsl.pycsl import main; import sys; sys.argv=['pycsl', 'src/pycsl/<MODULE>.py']; main()" 2>&1 | tail -5

# 7. Verify Layer 1 + a sample of reference tests:
make self-annotate-verify 2>&1 | tail -5
for t in 0342 0345 0348; do
  PYTHONPATH=src .venv/bin/python -c "from pycsl.pycsl import main; import sys; sys.argv=['pycsl', 'test-suite/corpus/pycsl-reference/${t}.py']; main()" 2>&1 | tail -1
done
```

## Verification

### Per-phase gate
- `make self-annotate-verify`: must pass (audit FAILED == 0; PASS count drops monotonically as expected).
- Sample full-proof tests stay green (0342 + 0345 + 0348 minimum).
- No new Why3 errors on the module that was just edited.

### Final gate (after all phases)
- `make self-annotate-verify`: green, audit FAILED == 0.
- All 12 reference tests verify under full proof (0331, 0341-0351).
- Full-proof on all 7 modules: each module shows the SAME blocker line as before this work started (drift in line numbers is expected; semantic regression is not). Cross-check against `self-annot.md`'s post-Module5-type-inference snapshot.
- pytest: 25 pass, 3 skip (no regression).
- Any added `_AXIOM_REGISTRY` entry has a comment citing its Rocq + Lean theorem source and a one-line statement of what it asserts.

## Risks

- **Silent soundness regression from an incorrect `_AXIOM_REGISTRY` entry.** If a converted directive's WhyML axiom body doesn't faithfully encode the cited theorem, Why3 may suddenly prove things it shouldn't. The audit DOES NOT catch statement mismatches — only qualname misses. Mitigation: every CONVERT case requires manual cross-check (Rocq statement ↔ Lean statement ↔ WhyML axiom body), recorded in the inventory TSV's "rationale" column. Run full proof on the module to catch indirect signals (Why3 newly closing a proof that was previously timing out is suspicious).

- **Deleting a useful provenance pointer.** When DELETE is the right call but the citation was the only pointer to the Rocq/Lean justification, move the pointer to a code comment so a future reader can find it.

- **Phase-by-phase audit-count drift confusing reviewers.** Document expected count after each phase (162 → ~155 after Phase 2 → ~149 after Phase 3 → ... → ~16 after Phase 8).

- **Attic mirrors (`src/self-annotate/attic/{rocq,lean}/*.py`) diverging further.** The mirrors are independent snapshots; this triage targets `src/self-annotate/src/*.py`. If a future session wants the mirrors synced, that's a separate task.

## Effort estimate

| Step | Effort |
|---|---|
| Phase 2-3 (small modules, ConcurrencyChecker + Module1) | ~30 min each |
| Phase 4-5 (Module3, Module2) | ~45 min each |
| Phase 6 (Module4, 16 directives) | ~90 min |
| Phase 7 (Module5, 50 directives) | ~3 hours |
| Phase 8 (Module6, 44 directives) | ~3 hours |
| Per-phase verification | included above |
| Inventory TSV maintenance | ~30 min total |
| Final regression sweep | ~30 min |
| **Total (delete-heavy, ~0–5 CONVERT cases)** | **~10–12 hours** |

If CONVERT count grows (e.g., 10+), add ~30 min per case for theorem→axiom translation and cross-checking.

## What we are NOT doing

- **NOT modifying `0342.py`'s 16 `axiom_from` directives.** They're already load-bearing and have matching registry entries.
- **NOT removing the audit's `proof` directive recognition.** `bin/check-proof-attributions.sh` keeps handling both forms; any future contributor who re-introduces a `proof` directive will still be audited.
- **NOT writing a `proof2why3` extractor.** The TODO at `Module6:3664` references this future tool; building it is out of scope. CONVERT cases this phase use hand-curated registry entries.
- **NOT touching the attic mirrors.** They live independently. If they end up with stale provenance, that's a separate sync task.
- **NOT changing the semantic analyzer or type checker.** The triage is documentation-level; the only code change is `_AXIOM_REGISTRY` growth for CONVERT cases.
