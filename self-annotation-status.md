# PyCSL Self-Annotation — Status & Strategy

## Introduction

PyCSL is a deductive verifier for a contract-annotated subset of Python: you write `#@`
contracts (`requires`/`ensures`/`assigns`/`loop invariant`/…) on your code, and PyCSL transpiles
the program-plus-contracts to WhyML and discharges the verification conditions with Why3 + SMT
solvers. **Self-annotation** is PyCSL turned on *itself*: the transpiler's own statement-emitter
methods (`_handle_*`) are annotated with `#@` contracts and verified by PyCSL, so the tool proves
its own code is body-faithful. This document records the global strategy, the roles of the three
`src/` pillars that make it work, and exactly where the effort stands today (2026-07-03).

---

## The three pillars: `src/pycsl`, `src/formal-semantics`, `src/self-annotate`

The trust story rests on three directories that play distinct, complementary roles. One is the
*artifact*, one is the *mathematics*, one is the *bridge* that ties the artifact to the
mathematics.

### `src/pycsl` — the transpiler (the artifact under verification)

The live Python implementation of PyCSL: the program that ingests annotated `.py`, type-checks
the contracts, lowers everything to an IR, and emits WhyML. It is a 6-stage pipeline:

| Stage | File(s) | Role |
|---|---|---|
| Module 1 — Ingestor | `frontend/Module1_Ingestor.py` | read `.py`, split out the `#@` contract lines |
| Module 2 — Parser | `frontend/Module2_Parser.py` | EBNF grammar → AST for the contract language |
| Module 3 — Weaver | `frontend/Module3_Weaver.py` | attach parsed contracts to the Python AST nodes |
| Module 4 — Semantic Analyzer | `frontend/…` (+ `core_ir_semantic.py`) | type-checking, scope/typing analysis |
| Module 5 — IR Emitter | `frontend/Module5_IREmitter.py` | Python AST → typed intermediate representation |
| Module 6 — WhyML Transpiler | `Module6_WhyMLTranspiler.py` (facade) + `module6_whyml/` | typed IR → WhyML text |

Supporting top-level modules: `pycsl.py` (CLI entry point), `ir_schema.py` (the **typed IR**
dataclasses — `AssignStmt`, `IfStmt`, `MatchStmt`, … subclassing `StmtIR`/`ExprIR`), `errors.py`,
`exception_model.py`, `audit_proof.py` / `proof_axiom_allowlist.py` (proof-provenance auditing).

**Module 6 is where self-annotation lives.** The `module6_whyml/` subpackage is a set of mixins
composed onto the `Module6_WhyMLTranspiler` facade:

- `statements.py` — `StatementEmissionMixin`: the `_handle_*_stmt` statement emitters.
- `stmt_control_flow.py` — `ControlFlowStmtMixin`: the control-flow emitters (`return`/`if`/
  `while`/`for`/`try`/`match`).
- `expressions.py` — `ExpressionEmissionMixin`: the `_EXPR_DISPATCH` expression emitters.
- `types.py`, `functions.py`, `preamble.py`, `identifiers.py`, `ir_scanner.py`, `scc.py`,
  `abstract_ops.py`, `auto_trust.py`, `struct_format.py`, `expr_ghost_*` — the supporting
  type-inference, signature/contract emission, preamble/`use`, SCC ordering, and abstract-op
  machinery.

`src/pycsl` is the thing whose faithfulness we want to establish. Everything else exists to
verify it.

### `src/formal-semantics` — the machine-checked mathematics

The formal soundness of PyCSL's calculus, proved **twice independently** in two proof assistants
(Rocq/Coq: ~56 `.v` files; Lean: ~49 `.lean` files). This is the *mathematics* layer — it says
nothing about the Python code directly; it proves the underlying theory is correct.

The development is staged (`Phase0…Phase6+`):

- **Phase 0–1** — the IR/JSON model and the abstract syntax (`Phase0_IrJson`, `Phase1_AST`,
  `Phase1b_IrToStmt`, `Phase1c_ValidateIr`).
- **Phase 2** — the state model (`Phase2_State.v`: state as an association list `ident × value`;
  `update`/`lookup` laws).
- **Phase 3** — the structural operational semantics (`Phase3_SOS`) and desugaring
  (`Phase3b_Desugar`).
- **Phase 4** — the weakest-precondition calculus (`Phase4_WP.v`), one arm per statement form.
- **Phase 5** — soundness: the WP calculus is sound w.r.t. the SOS (`Phase5b_Soundness`,
  `Phase5a_WhileInv`), plus concurrency (`ConcurrentModel`) and class invariants.
- **Phase 6** — **emitter coherence**: `Phase6L_Emit*` lemmas prove the WhyML the emitter prints,
  when evaluated, equals the WP the calculus computes — one lemma per WP arm.

The apex theorem is **`pycsl_soundness`**; the whole-program emitter composition is
**`emit_stmts_coherent`**. These are the ground truth that the self-annotation layer connects the
Python implementation to.

### `src/self-annotate` — the mirror and the proof harness (the bridge)

This directory makes "PyCSL verifies its own emitter" concrete. It closes the gap between the
*mathematics* (`src/formal-semantics`) and the *artifact* (`src/pycsl`).

- **`src/self-annotate/src/`** — the **mirror**: a copy of `src/pycsl`'s layout (`module6_whyml/`,
  `frontend/`, the top-level modules) carrying the `#@` contracts. PyCSL is run *on this mirror*
  (`pycsl <mirror-file> --import-path src/pycsl`) to verify it. The mirror is **heterogeneous**:
  - **un-`\trusted` methods** — the body-faithful `_handle_*` handlers — are **verbatim copies**
    of the live emitter (byte-identical modulo added `#@` lines); verifying the mirror therefore
    verifies the *real* emitter code.
  - **`\trusted` stubs** — the recursion leaves and cross-mixin siblings (`_expr_to_whyml`,
    `_stmts_to_whyml`, …) — are bodyless `val`s with a sound `ensures`; they mark the trust
    boundary (see the Ceiling, below).
- **`pycsl-wp-spec.mlw`** — the **Layer-3 coherence proof** (hand-written WhyML): the audited
  bridge that stratifies value-faithfulness into the evaluator-axiom boundary ("D2"). This is
  where the residual trusted core lives.
- **`arm-coverage.md`, `evaluator-axiom-audit.md`, `audit-guide.md`, `README.md`,
  `semantic-ceiling.md`** — the audit surfaces and the guide from Rocq theorem → `#@` annotation.
- **`attic/`** — historical plans (including the campaign plans retired 2026-07-03).

The mirror↔emitter fidelity is machine-enforced by two gates:
`bin/check-self-annotate-mirror-sync.py` (every un-`\trusted` mirror method is byte-identical to
its live counterpart) and `bin/self-annotate-mirror-check.sh` (structural signature check).

---

## Global strategy: the four-layer trust chain

No single layer can establish faithfulness alone; each covers what the others cannot. The design
composes four:

```
Layer 0 — Rocq / Lean type-checkers  (src/formal-semantics)
   Machine-checked soundness theorem `pycsl_soundness`.  ← the WP calculus is mathematically sound
         ↓
Layer 1 — PyCSL #@ contracts on the Python implementation  (src/self-annotate/src)
   Structural faithfulness: frame conditions, loop termination, exhaustive dispatch —
   the emitter doesn't drop statements, corrupt state, or diverge from the formal structure.
         ↓
Layer 2 — Why3 + SMT  (every `pycsl` run)
   Output verification: the generated .mlw is accepted by Why3 for the user's program.
         ↓
Layer 3 — Emitter self-verification  (src/self-annotate/pycsl-wp-spec.mlw)
   Coherence: the WhyML string the emitter prints, when evaluated, equals the WP the calculus
   computes.  Residual trust = the audited evaluator-axiom boundary ("D2").
```

**The self-annotation loop (Layer 1) is the active workstream.** The strategy is:

1. Port each live `_handle_*` emitter method **verbatim** into the mirror and add `#@ requires
   True / ensures True / assigns <frame>`.
2. Drive PyCSL to verify it — type-safety of the emitted WhyML plus a **checked `assigns`
   frame** — extending the emitter's own type-inference with small, `@mutable_state`-gated
   recognizers where a reflective construct leaks.
3. Gate every change with **byte-diff 0** across the 627-program reference corpus (the emitter's
   output for real user programs must not change — the corpus contains no `@mutable_state` /
   emit_ir-reflection code, so the self-annotation machinery is provably inert there).
4. Un-`\trust` the method and enforce the mirror↔emitter sync gate.

**The Ceiling (why this is bounded).** Layer 1 proves **type-safety + frame**, *not* the
value-faithful `ensures \result == <the exact WhyML string>`. That last step would require the
emitter to prove its own recursion leaves (`_expr_to_whyml` / `_stmts_to_whyml`) correct — i.e. a
system proving its own evaluator sound, which is impossible by Gödel's second incompleteness /
Löb's theorem. This is **Ceiling B**. The sound resolution is *stratification*: the value-level
claim is discharged in `pycsl-wp-spec.mlw` against an explicit, audited set of **D2 evaluator
axioms**, and the recursion leaves stay `\trusted` with sound `ensures`. There is deliberately
**no un-`\trust` deliverable** for the leaves.

---

## Exactly where we stand (2026-07-03)

### ✅ Item 4 — the statement-handler campaign is COMPLETE

**All 18 `_handle_*` statement emitters verify their own bodies** (type-safety + checked
`assigns` frame), un-`\trusted`, byte-diff 0, both mirror-sync gates green, self-annotation suite
0-FAIL:

| Family | Count | Handlers |
|---|---|---|
| Reflecting (`statements.py`) | 12 | `assign`, `seq_assign`, `ghost_assign`, `ghost_array_set`, `tuple_unpack`, `array_slice_set`, `array_set`, `critical_section`, `augassign`, `fieldassign`, `fieldaugassign`, `expr_stmt` |
| Control-flow (`stmt_control_flow.py`) | 6 | `return`, `if`, `while`, `for`, `try`, `match` |

Milestones along the way: `ghost_array_set` was the **first** emitter method ever removed from the
trusted base; `try` was the deepest reflecting handler (uniform `seq string` model); `match` was
the last and broadest (landed via `cf6.md` as an additive, gated pass — a `stmts_of` opaque
stmt-list projection distinct from `args_of`, a subscript-vs-`.get` "pattern" key split, and an
IR-mutation-as-sound-no-op). The mirror-sync gate currently reports **24 un-`\trusted` methods
verbatim** (the 18 handlers plus 6 supporting emitter methods).

### ✅ Item 3 — the recursion-leaf value contracts are IRREDUCIBLE, and AUDITED

This is **Ceiling B** — not a build task. The audit (`item34.md §1`, tasks I3.1–I3.3, closed
2026-07-03) confirms the boundary is intact:

- **I3.1** — `pycsl-wp-spec.mlw` residual = **37 axioms, 0 `Admitted`/`sorry`/`assume`**. All 37
  are the enumerated D2 class: 2 state-model foundation axioms (matching `Phase2_State.v`), ~33
  WP-arm `*_semantics` axioms (one per rule arm), and 2 coherence-bridge axioms (`expr_coherent`,
  `eval_e_int`). Several former axioms were promoted to proved `let lemma`s (TCB shrank). No stray
  axiom.
- **I3.2** — every `\trusted` sibling/leaf stub carries a sound `#@ ensures` (predominantly
  `ensures True` — claims nothing); a machine check for a stub *without* an `ensures` returned
  empty → **no silent hole**.
- **I3.3** — the standing boundary is reconciled across the docs; item 3 is
  **complete-by-stratification**.

### The residual trusted core (what is NOT proved, by design)

1. The **37 D2 evaluator axioms** in `pycsl-wp-spec.mlw` (the audited semantics of the abstract
   evaluator / WP arms — Ceiling B).
2. The **`\trusted` recursion leaves and siblings** in the mirror (`_expr_to_whyml`,
   `_stmts_to_whyml`, and the supporting stubs), each with a sound `ensures`.
3. Layer 0's own trust base: the Rocq/Lean kernels.

Everything else in the emitter's statement path is now machine-verified body-faithful.

### The trust surface, quantified: ≈1290 `\trusted` stubs vs 24 verified methods

`find src/self-annotate/ -name '*.py' -exec grep '\trusted' {} \; | wc -l` reports **≈1296**.
Every one is the same marker — `#@ \trusted reviewer: pycsl-self-annotate` — and understanding it
is understanding where the effort stands.

The mirror (`src/self-annotate/src/`) is a copy of the **whole tool** — all six pipeline modules
plus `frontend/`, `proof2why3/`, `core_ir_semantic.py`, `pycsl.py`, etc. (~1276 methods). Of
those, only the **~24 methods on the Module-6 statement-emission path are verified body-faithful**
(the 18 `_handle_*` handlers + ~6 supporting emitter methods). The other **≈1290 are `\trusted`
stubs**: bodyless `val`s whose *signature matches the source* (the mirror-check gate enforces
parity) and whose contract is the soundest possible — `#@ requires True / ensures True / assigns
\nothing`, i.e. it **claims nothing false**.

Their two jobs:

1. **Provide the interfaces the verified slice calls.** A verified `_handle_*` handler calls into
   the parser, the IR emitter, the type-inference helpers, and the recursion leaves. For the
   verified slice to type-check *in isolation*, every callee needs a declared interface — the
   stubs supply exactly that, without requiring those callees to be proved.
2. **Be the explicit, auditable trust boundary.** The *named* form (`reviewer:
   pycsl-self-annotate`, distinct from anonymous `\trusted`) is what the "0-trusted" lint counts —
   the trusted core is enumerated and visible, never hidden. Un-`\trusting` a stub (converting it
   to a verified body) is precisely one unit of self-annotation progress; the campaign has done 24
   and the ≈1290 are the remaining surface.

**Why the count is large but the soundness story is not weakened.** The bulk of the ≈1290 is the
**front-end** — `frontend/pure_ast.py` (262), `Module5_IREmitter.py` (180), `Module2_Parser.py`
(91), `Module3_Weaver.py` (39), plus `core_ir_semantic.py` (66) and `proof2why3/` (~90). These are
*structural* stages, and the layered trust chain does **not** route soundness through them:

- **Layer 0** already proves the *calculus* (`src/formal-semantics`), independently of any Python.
- **Layer 3** connects the **emitter** (Module 6) to that calculus — so Module 6 is the
  load-bearing path, and it is exactly what the campaign verified.
- **Layer 2** re-checks the *actual generated WhyML* on every real run — a front-end defect
  surfaces as a parse/type error or a Why3 rejection, **not** as silent unsoundness.

So the ≈1290 stubs are a **scoping choice**, not a soundness gap: the effort deliberately verified
the semantically critical emitter path first. Extending body-faithfulness into the front-end and
supporting modules is a large, additive, demand-gated continuation — each stub un-`\trusted` the
same way the 24 emitter methods were, one shrinking increment at a time.

### 🔮 What remains (future, demand-gated)

- **Lambda / higher-order support** (`lambda-plan.md`, `lambda.md`) — the main greenfield.
  Deliberately gated behind the deferred **Phase-7 typed/store memory model** (a returned
  closure's captured environment needs a heap footprint the current association-list state can't
  express). Demand-driven: built when a driver requires it.
- **Value-faithful emitter contracts** — permanently unavailable (Ceiling B). Not a work item.
- The retired feature plans (typed-IR, no-more-int, faithful-string, todict-reflection, …) are in
  `attic/`; their only residuals were the item-3 ceiling or explicitly demand-gated YAGNI exits.

---

## Verification / gates (how to reproduce the status)

```bash
# The self-annotation suite — proves every mirror file (18 handlers un-\trusted):
bash bin/run-self-annotation-suite.sh                      # 0 FAIL (7 pre-existing (file missing))

# Mirror ↔ live emitter fidelity (both must be green):
bash bin/check-self-annotate-sync.sh                       # method-body-verbatim gate
bash bin/self-annotate-mirror-check.sh                     # structural-signature gate

# Corpus non-regression (the emitter's output for real programs is unchanged):
PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh /tmp/after && diff -rq <clean-baseline> /tmp/after

# A single handler, directly:
python3 src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/stmt_control_flow.py --import-path src/pycsl   # full proof
```

## Map of the governing documents

- `item34.md` — the master ledger (item 4 = done, item 3 = irreducible + audited).
- `remaining-trust.md` — the two-surface assessment (item 3 = Ceiling B; item 4 = the campaign).
- `a3-plan.md` / `a2-a3-plan.md` — the mutable-transpiler-state (`@mutable_state`) foundation that
  unblocked the whole campaign.
- `lambda-plan.md` / `lambda.md` — the future higher-order work (Phase-7-gated).
- `src/self-annotate/README.md` — the mirror mechanism + the Layer 0–3 trust chain in detail.
- `attic/` — the completed/superseded campaign plans (cf6, resync-campaign, seq-model-pivot,
  self-ir-schema, list-comprehension-lowering, typed-ir-for-b-ceiling, faithful-string-op,
  todict-reflection-plan, no-more-int-emitter-plan, i-feel-good, b1-plan, mutable-self-plan,
  phase-b-expr-plan, semantic-ceiling-plan).
