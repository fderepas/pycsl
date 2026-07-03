# self-tcb-reduction.md — shrink the self-annotation trusted core toward its irreducible floor

**Purpose.** The self-annotation mirror (`src/self-annotate/src/`) carries **≈1290 `\trusted`
stubs** (one `#@ \trusted reviewer: pycsl-self-annotate` marker each) against only **24 verified
body-faithful methods** (the completed 18-handler statement-emitter campaign + ~6 supporting
methods). This plan is the long-horizon campaign to convert those stubs — tier by tier, highest
soundness-value first — into verified bodies, driving the trusted core down to its **irreducible
floor**.

**Honest target (read this first).** "Remove all 1296" is **not achievable and not the goal.** A
hard floor is irreducible by design (Ceiling B, Gödel-2/Löb — see `remaining-trust.md`,
`item34.md §1`): the recursion leaves `_expr_to_whyml` / `_stmts_to_whyml` and the 37 D2 evaluator
axioms in `pycsl-wp-spec.mlw` **must stay trusted** — a system cannot prove its own evaluator
sound. The target is therefore **"reduce ≈1290 → the floor"**, where the floor is a *small,
enumerated, audited* set (the leaves + the genuinely-opaque boundaries), NOT zero. Every stub this
plan cannot convert must be *reclassified* into that audited floor with a reason, not left as
undifferentiated trust.

**Doctrine.** Same as the 18-handler campaign: each conversion is **port-verbatim → verify
(type-safety + `assigns` frame) → byte-diff 0 across the 627-corpus → un-`\trust` → both
mirror-sync gates green**. `@mutable_state`/emit_ir-gated recognizers only; the corpus never
changes. **Demand-gated** (`pycsl-how-to-develop §8.2`): convert stubs that carry soundness weight
or that a verified caller needs — do not gold-plate the low-value tail.

---

## 0. Where we start — the ≈1290 stubs by tier (measured 2026-07-03)

| Tier | Scope | ≈ stubs | Soundness weight | Tractability |
|---|---|---:|---|---|
| **T1** | **Module 6 emitter** (`module6_whyml/` + `Module6_WhyMLTranspiler.py`) | **~326** | **HIGH** — the Layer-3 (coherence) load-bearing path | **PROVEN** (18 handlers already done) |
| **T2** | **Semantic analyzer** (`core_ir_semantic.py`) | ~66 | HIGH — Layer-1 structural faithfulness | new contract class (analyzer invariants) |
| **T3** | **Front-end pipeline** (`frontend/`: pure_ast 262, Module5 180, Module2 91, Module3 39, monomorphize 25, ir_resolve 21, Module1 18, ir_inline 17, …) | ~671 | MEDIUM — structural; Layer-2 re-checks output anyway | harder (preservation contracts, not WhyML type-safety) |
| **T4** | **Tooling / orchestration** (`proof2why3/` 118, `pycsl.py` 39, `audit_proof*` 29, `exception_model` 6) | ~192 | LOW — provenance tooling + CLI glue | mixed; mostly YAGNI |

T1 sub-breakdown (the immediate work): `expressions.py` 79 (incl. **24 `_handle_*_expr`
expression handlers** — the direct analog of the done statement handlers), `statements.py` 43
(remaining helpers), `functions.py` 37, `ir_scanner.py` 34, `preamble.py` 25,
`expr_ghost_collections.py` 24, `types.py` 18, `expr_ghost_spec_ops.py` 12, `auto_trust.py` 12,
`struct_format.py` 6, `identifiers.py`/`scc.py` 5, `abstract_ops.py` 4, `Module6_WhyMLTranspiler.py`
22.

---

## 1. The irreducible floor (what STAYS trusted — enumerate, don't shrink)

Before converting anything, fix the floor so "done" is well-defined:

- **F1 — the recursion leaves.** `_expr_to_whyml`, `_stmts_to_whyml` (and any mutually-recursive
  emitter sibling that bottoms out in them). Ceiling B. Stay `\trusted / ensures True`.
- **F2 — the D2 evaluator axioms.** The 37 axioms in `pycsl-wp-spec.mlw` (audited by I3.1). Not
  `.py` stubs, but part of the floor.
- **F3 — genuinely-opaque boundaries.** Any method whose faithful contract would require modelling
  an external/undecidable surface (SMT solver invocation, file I/O in the CLI, subprocess to
  `why3`, the `agents/` LLM calls). These are `\abstract`/`\trusted` with a *documented* boundary
  (`pycsl-how-to-develop §8.4` — sound under-approximation, never a fake axiom).

**Deliverable of every tier:** each stub is either (a) converted to a verified body, or (b)
*re-sited* into F1/F2/F3 with a one-line reason in `arm-coverage.md`. No stub may remain
un-classified.

---

## 2. Stages (each stage = a batch of stubs; the per-stub loop is fixed)

### T1 — Module 6 emitter (do first: highest value × proven tractability)

- **T1.a — the 24 expression handlers** (`_handle_*_expr` in `expressions.py`). The exact analog
  of the 18 statement handlers: port verbatim, `#@ requires True / ensures True / assigns
  <frame>`, extend the recognizers where a reflective construct leaks, byte-diff 0, un-`\trust`.
  Start with the read-only ones (`_handle_var_expr`, `_handle_attribute_expr`,
  `_handle_field_get_expr`) — cheapest end-to-end; end with the broadest (`_handle_call_expr`,
  `_handle_fstring_expr`).
- **T1.b — the emitter helpers** (`types.py`, `functions.py`, `preamble.py`, `ir_scanner.py`,
  `abstract_ops.py`, `auto_trust.py`, `identifiers.py`, `scc.py`, `struct_format.py`,
  `expr_ghost_*`). Mostly pure/structural — many are `assigns \nothing` leaves that verify
  quickly. Convert in dependency order (a verified handler's callees first).
- **Gate (T1):** every `module6_whyml` method is verified OR in F1/F3; `check-self-annotate-sync.sh`
  green; byte-diff 0; the whole coherence path (Layer 3) now rests only on F1+F2.

### T2 — the semantic analyzer (`core_ir_semantic.py`, ~66)

Layer-1 structural faithfulness: contracts here are **analyzer invariants** (type-environment
well-formedness, scope preservation, exhaustive case handling), NOT WhyML type-safety. New
contract class — spike one method first to fix the pattern, then batch.

### T3 — the front-end pipeline (`frontend/`, ~671)

The bulk of the count, the least soundness weight (Layer 2 re-checks the emitted WhyML on every
run, so a front-end defect cannot pass silently). Verify **structural-preservation** contracts
(Layer-A style: `#@ ensures \forall i … \result[i] is not None`, `assigns \nothing`, no dropped
nodes). Order by leaf-first: `Module1_Ingestor` (small), then `ir_resolve`/`ir_inline`/
`monomorphize`, then the big three (`pure_ast`, `Module5_IREmitter`, `Module2_Parser`) as their own
sub-campaigns. **Explicitly demand-gated** — this tier only earns its cost if a driver (or an
external audit requirement) demands front-end faithfulness; otherwise it stays a documented,
lower-priority surface.

### T4 — tooling / orchestration (`proof2why3/`, `pycsl.py`, `audit_proof*`, ~192)

**Lowest value; default to F3 (documented boundary), not conversion.** `pycsl.py` is CLI glue over
`why3`/file-I/O (F3). `proof2why3/` is proof-provenance tooling, off the soundness path. Convert
only the handful with real logic if a demand appears; otherwise re-site into F3 with a reason.
**This tier is expected to end mostly re-classified, not verified.**

---

## 3. Ordering rationale & realistic scope

- **Value gradient:** T1 (emitter) directly reduces what Layer 3 trusts → do first. T2 (analyzer)
  strengthens Layer 1. T3/T4 add structural coverage but Layer 2 already backstops them → later /
  demand-gated.
- **This is a multi-month campaign, not a sprint.** The 18-handler statement campaign — one tier's
  worth — spanned many sessions. Budget T1 as *the* next arc (≈326 stubs, but many are trivial
  `assigns \nothing` leaves), T2 as a focused follow-on, T3 as a standing background reduction, T4
  as reclassification.
- **The honest end state** is NOT 0 trusted. A realistic floor is **F1 (≈2–10 leaf methods) + F2
  (37 axioms) + F3 (the documented opaque boundaries)** — plausibly reducing the ≈1290 `.py` stubs
  to a low-tens *audited* core, with T4 re-sited rather than removed.

---

## 4. Critical files

- `src/self-annotate/src/module6_whyml/*.py` — the T1 mirror (port + un-`\trust`).
- `src/pycsl/module6_whyml/*.py` — incremental `@mutable_state`-gated recognizer additions (a stub
  may surface a new leak the way the statement handlers did).
- `src/self-annotate/src/core_ir_semantic.py`, `frontend/*.py` — T2/T3 mirrors.
- `src/self-annotate/arm-coverage.md` — the floor register (F1/F3 re-siting reasons).
- `bin/check-self-annotate-mirror-sync.py` / `bin/self-annotate-mirror-check.sh` — the gates;
  extend the 0-trusted lint to *report the shrinking count* per tier.

---

## 5. Out-of-scope / soundness boundary

- **The floor (F1/F2/F3) stays trusted** — no attempt to un-`\trust` the recursion leaves
  (Gödel/Löb); no fake axiom.
- **Corpus untouched** — every recognizer `@mutable_state`/reflection-gated; byte-diff 0 is the
  gate on every stub.
- **Type-safety + frame** (and, for T2/T3, structural-preservation) — NOT value-faithful
  `ensures \result == <string>` (that bottoms out at F1/Ceiling B).
- **Demand-gating is a real off-ramp** — T3/T4 stubs with no soundness weight and no verified
  caller may be *documented-and-deferred* indefinitely; that is a legitimate closed state.

---

## 6. Verification (per stub + per tier)

```bash
# per stub: type-check + byte-diff 0
python3 src/pycsl/pycsl.py <mirror-file> --import-path src/pycsl --no-proof
PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh /tmp/after && diff -rq <clean-baseline> /tmp/after
# per tier: full proof + gates + shrinking trusted count
python3 src/pycsl/pycsl.py <mirror-file> --import-path src/pycsl          # full proof
bash bin/check-self-annotate-sync.sh && bash bin/self-annotate-mirror-check.sh
find src/self-annotate/src -name '*.py' -exec grep -h '\trusted' {} \; | wc -l   # must shrink
bash bin/run-self-annotation-suite.sh                                     # no new failures
```

## 7. Reference corpus

Like the emitter campaign, the surface is **self-annotation-internal** (reflection over the tool's
own IR requires `--import-path`), so a standalone corpus witness is not viable (see `cf6.md §3`) —
**the mirror is the driver**, exercised by `bin/run-self-annotation-suite.sh`; the 627-corpus
byte-diff-0 gate proves additivity. Where a T1 conversion adds a genuinely new emit_ir projection,
add a `@mutable_state` witness per `pycsl-how-to-develop §8.2` if it can verify standalone.

---

## 8. Progress ledger (live)

| Tier | Scope | Start | Verified | `\trusted` remaining | Status |
|---|---|---:|---:|---:|---|
| (done) | Module 6 statement handlers | — | 18 + 6 | — | ✅ COMPLETE |
| F1/F2/F3 | irreducible floor (enumerate) | — | — | — | ◻ TODO (fix the floor first) |
| T1.a | expression handlers (`_handle_*_expr`) | 24 | 0 | 24 | ◻ TODO |
| T1.b | Module 6 emitter helpers | ~302 | 0 | ~302 | ◻ TODO |
| T2 | semantic analyzer | ~66 | 0 | ~66 | ◻ TODO |
| T3 | front-end pipeline | ~671 | 0 | ~671 | ◻ demand-gated |
| T4 | tooling / orchestration | ~192 | 0 | ~192 | ◻ re-site to F3 (mostly) |

**Definition of done.** Every `.py` stub in the mirror is either (a) a verified body or (b)
enumerated in the F1/F3 audited floor with a reason; the `wc -l` trusted count is reduced to that
floor; `check-self-annotate-sync.sh`, `self-annotate-mirror-check.sh`, and
`run-self-annotation-suite.sh` all green; byte-diff 0 throughout.
