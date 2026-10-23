# tree-walk-wall-impl.md — implementation plan (spike-first, refutation-exit)

Synthesized from `tree-walk-wall.md` + `tree-walk-wall-response.md` (Gate R CONFIRMED with refinements).

## Design (refined per the fable review)
- **Per-discriminant recursive match recognizer**, NOT a string-keyed generic fold (Why3 program-string-eq gap):
  emit `stmt_has_raise : stmt_ir -> bool` (recursive), `match s with SRaise _ -> true | <compound> -> <∨ over
  stmt sub-children> | _ -> false`.
- **Inline constructor recursion**, NOT an `ir_children : node -> list node` (ill-typed for heterogeneous
  children): the recogniser matches each stmt_ir constructor and ∨-recurses into its stmt_list children
  (SWhile/SIf/SFor/STry/SMatch/SCriticalSection bodies) via a sibling `sl_has_raise : stmt_list -> bool`.
- **STRUCTURAL variant `variant { s }` / `variant { l }`** (the emitter's native idiom, preamble.py ~3738 —
  recurses on pattern-bound sub-terms, discharges natively) — NOT the single-component `variant { size s }`
  (Spike A proved it FAILS: certified `size_slist (SLCons h SLNil) = size_stmt h`, non-strict list→head).
- **Param retype**: the walker's untyped `body`/`node` param typed `stmt_ir` (`"StmtIR"` ann, as ce71e3ab
  retyped to pyast_stmt). `_body_has_raise` needs NO expr descent (Raise is a stmt discriminant only) — simplest.
- Lowerings: `node.get("stmt")=="Raise"` → the `SRaise`/`stmt_kind_of` discriminant; `for v in node.values():
  walk(v)` → the recursive `stmt_has_raise`/`sl_has_raise` descent; `found[0]`/`return bool` → the ∨ result.

## Gate S — MAKE-OR-BREAK SPIKE FIRST (emission-level; the modeling is already fable-proven)
The fable proved the MODELING (Spike B/C). The impl make-or-break is whether the TOOL emits a provable
recogniser for the REAL `_body_has_raise` verbatim body:
1. Add the minimal `stmt_has_raise`/`sl_has_raise` recursive recogniser to the emitter (gated on a `_uses_*`
   signal), retype `_body_has_raise`'s `body` param to `"StmtIR"`, port the verbatim body, emit `--keep-mlw`.
2. Inspect: does `for v in node.values()` lower to the recursive descent (NOT opaque `iter_get`/`isinstance_op
   0 0`)? Does the emitted recursive fold carry a STRUCTURAL `variant`?
3. Prove (whole-file or `--fun _body_has_raise`): 
   - PASS (discharges, non-vacuous — an evil-twin body without Raise must not prove `found`) → build the full
     recogniser + convert + R2 follow-ons.
   - REFUTE (the recursion won't lower, or the structural variant won't discharge at full core_ir_semantic
     theory scale, or it forces an axiom) → CERTIFIED-BOUNDARY: record + stop, do NOT grind.
   - REFINE (a different blocker, e.g. the `body` is a stmt_list not a single stmt) → re-plan the residual.

## Build (only if Gate S PASSES) — ONE recogniser, then parameterize
- **T1: `_body_has_raise`** (the make-or-break) — convert end-to-end, all gates.
- **T2 (R2 same-fold cluster): `_body_has_return`** (SReturn discriminant), **`_body_has_diverging_construct`**
  (stmt_kind ∈ {While,For,CriticalSection} OR an expr `Call` — needs a shallow expr-descent too), **`_contains_
  result`** (type=="Result" — an EXPR-tree walk, `emit_ir` structural variant). Each = the SAME recursive
  recogniser parameterized by a different discriminant predicate. The recogniser must accept the discriminant
  GENERICALLY (a per-stub discriminant set), lowered per-discriminant (match recognizers, not a string param).
- **Defer**: `_lemma_returns_value` (depth-2 Return-value arg-read), `_lemma_calls_trusted` (string result +
  first-hit traversal order + trusted-set param — REFUTED as same-fold), `_union_c8_test_references_union_var`.

## Gate battery (per converted stub — driver-verifier FRESH)
Mutation test (change the discriminant tag / a branch → emitted `.mlw` changes) ∧ whole-file Why3 proof (if it
wedges on re-run with all-VCs-Valid, agent's clean SUCCESS is the verdict) ∧ byte-diff-0 (recogniser gated on
`_uses_*`, corpus-inert) ∧ fidelity (mirror==live verbatim) ∧ count strictly down ∧ ledger 3 (the recursive
recogniser is a NEW operation over the EXISTING certified stmt_ir/emit_ir ADT — likely a cert EXTENSION, a
`stmt_has`-terminates lemma; verify axiom-free, `Print Assumptions`/`#print axioms`).

## Honest costed scope
The recogniser (recursive match + structural variant, per-discriminant) is the build; ~4 conversions
(`_body_has_raise` + 3 R2). The `_body_has_diverging_construct`/`_contains_result` expr-descent + the deferred
value-reading walkers are follow-on scope. Yield: ~4 stubs from one recogniser — highest on the frontier.

## GATE-S OUTCOME (2026-07-20, driver run) — REFINE: modeling PROVEN at full scale, emission gated on 3 builds
The make-or-break emission spike REFINED the plan decisively:
- **T1 correction: `_body_has_raise` is DEAD** — the certified stmt_ir ADT has NO `SRaise` ctor (`_py_stmt_raise`
  is the sole unconverted `_py_stmt_*` handler; mirror stub = `pass`). A `stmt_has_raise` recogniser is vacuously
  `false` (facade; fails the mutation test). REQUIRES `_py_stmt_raise`+`SRaise`+Phase2d extension first → deferred.
  **New T1 = `_body_has_return`** (`SReturn` EXISTS → faithful, non-vacuous).
- **VARIANT correction: the mandated STRUCTURAL variant `{s}`/`{l}` FAILS at full scale** — the `handler_list`/
  `match_case` RECORD-FIELD-PROJECTION descents (`sl_has_return h.eh_body`) timed out at 44-55M steps (Why3's
  structural order can't relate a record-field projection to the inductive order; the fable miniature lacked these
  record mutuals). **USE the LEXICOGRAPHIC variant `variant { size_stmt s, 0 }` / `{ size_slist l, 1 }` / `{
  size_hlist l, 1 }` / `{ size_mclist l, 1 }`** (fable Spike B). PROVEN Valid at full M5 scale, both provers,
  axiom-free, non-vacuous. Banked: `scratchpad/standalone.mlw` (`stmt_has_return`+`sl_/hl_/mcl_has_return`).
- **The CONVERSION is gated behind 3 emitter builds (impl under-scoped these):**
  (a) a **read-only gating signal** — `_uses_stmt_ir` requires a `.append({"stmt":K})` shape; the semantic-checker
      walkers only READ `node.get("stmt")` → the stmt_ir theory + recogniser is never emitted into
      `core_ir_semantic.py`. Need a `_uses_*` detector for a `.values()`-tree-walk over stmt_ir.
  (b) a **`"StmtIR"`→stmt_ir param-typing** mechanism — currently `"StmtIR"`/`"ExprIR"`/`"IRNode"` ALL map to
      `emit_ir` (the EXPR ADT, functions.py:153); the walker's `body` param must type as the STATEMENT tree
      (parallel to ce71e3ab's `_current_pyast_classdef_params` for pyast_stmt).
  (c) a **closure-walker recogniser** — the live body is a nested `def walk(node)` + `found=[False]` cell with
      `for v in node.values()`; existing recognizers match FLAT `for x in xs` shapes. Either a new recogniser OR a
      behavior-preserving refactor of live+mirror `_body_has_return` to a flat direct-recursive form.
- **Re-planned build order:** (b) stmt_ir param-typing [foundational] → (a) read-only gating → (c) recogniser/refactor
  → convert `_body_has_return` [proven] → R2 discriminant-exists follow-ons (`_body_has_diverging_construct`
  While/For/CriticalSection, `_contains_result` type=="Result" via emit_ir). Yield ~3-4 (raise-family deferred to SRaise).

## R2 DRAIN OUTCOME (2026-07-20) — both DEFERRED, T2 PROVEN FEASIBLE (not a wall)
The banked `recognize_stmt_has` is a STMT-body catamorphism (sl/hl/mcl descents); every stmt_ir ctor's expr
payload is `_`-ignored. Both R2 targets need EXPR-tree machinery it lacks.
- **`_body_has_diverging_construct` DEFERRED**: stmt multiway (While/For/CriticalSection) is trivial (already in
  `_STMT_COMPOUND`), but the `type=="Call"` test needs a COUPLED stmt↔expr mutual existence fold (a Call sits in
  any stmt's expr payload). Multi-piece; T2's proven `expr_has_call` unblocks the expr half.
- **`_contains_result` DEFERRED but PROVEN FEASIBLE**: make-or-break spike (`scratchpad/spike-t2-min.mlw`) — a
  full ~60-arm `expr_has_result : emit_ir -> bool` fold over the real emit_ir + irlist/iropt_ir mutuals with a
  **STRUCTURAL variant `{ e }`** — is **Valid on Z3** (0.74s, 2.5M steps; Alt-Ergo times out but pycsl proof is
  best-of-N, Z3 wins), non-vacuous, axiom-free. STRUCTURAL works here (unlike stmt_has) because emit_ir's mutuals
  are PLAIN-INDUCTIVE (pattern-bound descent), NO record-field-projection wall. The BUILD is the deferral reason:
  needs a NEW generic-`isinstance(dict)/type-test/.values()` descent recogniser (neither `recognize_stmt_has` nor
  `recognize_bool_existence` matches), the ~60-arm `emit_expr_has_group` (written+proven in the spike), an
  `"ExprIR"→emit_ir` param-typing gate, and a live `_contains_result` explicit-loop refactor.
**NEXT ESCALATION = the T2 emit_ir expr-tree existence fold** (Gate-S already PROVEN): converts `_contains_result`,
then unblocks `_body_has_diverging_construct`'s Call half. Frontier-map "emit_ir existence fold = wall" → FEASIBLE.

## T2 BUILD OUTCOME (2026-07-20) — BUILT + strongly-evidenced, but REVERTED on a whole-file PROOF-ENV WEDGE
`_contains_result` was built end-to-end (emit_expr_has_group ~60-arm expr_has_result fold + recognize_expr_has +
live↔mirror closure→flat refactor; banked patch `scratchpad/contains-result-build.patch` + fixture `0915`). Gates
that PASSED (independently re-verified): L3-tc typecheck SUCCESS; MUTATION TEST body-dependent (IrResult arm 4→3 on
discriminant flip); byte-diff-0 EMPTY; fidelity mirror-check green + live↔mirror byte-identical; consumer mirrors
typecheck; count 1025; allowlist clean; the fold's termination Z3-proven at FULL emit_ir scale (the R2 spike).
**BLOCKER: the whole-file Why3 proof HARD-WEDGES.** `core_ir_semantic.py` now carries BOTH the committed stmt
catamorphism (`_body_has_return`) AND the new ~60-arm expr fold; the combined theory hangs why3 at **0% CPU (idle,
persistent)** — not OOM-killed, not compute-bound — surviving why3server kills + clean solo relaunches. `--fun
_contains_result` launches were disrupted by the pkill exit-144 artifact. Cannot distinguish env-resource/deadlock
from a genuine full-context E-matching wall. Per the driver (whole-file Why3 REQUIRED; no unproven commit; no dirty
tree) → REVERTED. **The expr_has fold is FEASIBLE standalone (spike) but the FULL-CONTEXT proof is the wall** — a
core_ir_semantic proof-SCALING limit (the smaller `_body_has_return` catamorphism proved; adding the expr fold on
top wedges). Retry needs a proof-capable environment OR a lighter fold. `_body_has_diverging_construct` (needs the
same expr fold for its Call test) is likewise blocked. **Tree-walk wall net: +1 (_body_has_return); expr-fold
follow-ons blocked on the proof env.**
