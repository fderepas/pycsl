# `closer-to-code-execution-status.md` — index

Jump-table for the 64-item execution ledger of the
`closer-to-code.md` multi-quarter program. Items grouped by
program area (Q1/Q2/Q3/Q4/CC/sticky/recent).

To find an item's full entry: `grep -n "^<N>\." closer-to-code-execution-status.md`.

---

## Q2 — Sub-α per-construct emit_stmt (items 1-13, strikethrough)

Originally tracked as the "next actions" sub-list early in the
doc. All 13 items closed 2026-05-28; reduced to one-liners and
referenced from the Q2 close-out paragraph in
`src/formal-semantics/audit-plan.md`.

- Items 1-13 — Sub-α pilot through composition lemma + state-aware printer.

## Q3 — Sub-β Why3 formula semantics

- **14** — Q3 Sub-β setup (Cohen & JF formula_rep import; 2026-05-28).
- **16** — Sub-β Phase 4: port back into main pycsl build (2026-05-28).
- **17** — Sub-β Phase 5: cert-as-witness refactor (2026-05-29).

## Q1 — Lateral + Cleanup

- **18** — L.2 + L.3 actually added (Phase1_AST.v) (2026-05-29).

## Q4 — Upward chain (Module 5 IR ↔ formal stmt)

- **19** — U.1 sketch: `Phase0_IrJson.v` (2026-05-29).
- **23** — Item C: U.2 sketch `ir_to_stmt` simple subset.
- **24** — U.2 expansion: compound statements.
- **26** — U.3 first slice: `validate_ir` + correspondence.
- **27** — U.4 first slice: extraction.
- **28** — U.4 driver + orchestrator.
- **29** — U.2 contract-expr expansion.
- **30** — U.3 second slice: `KeysUnique` + lookup lemmas.
- **31** — Orchestrator improvements.
- **32** — Driver per-construct blocker analysis.
- **33** — `FieldAssign` / `FieldAugAssign` cases in `ir_to_stmt`.
- **34** — `Call(len)` in `ir_to_expr`.
- **35** — Ghost atoms expansion in `ir_to_contract_expr`.
- **36** — U.2 `TupleUnpack` + ghost array atoms (placed
  out-of-sequence in doc at line 1726).
- **37** — `div`/`//` binop aliases + ghost string atoms.
- **38** — `EFieldGet` extension to formal `expr`.
- **39** — v7 corpus run with EFieldGet + UnaryOp fix.
- **40** — `ECall` extension to formal `expr`.
- **41** — More expr extensions (session 5).
- **42** — `OpMod` (modulo) extension.
- **43** — Session 6 cumulative converter tolerance.
- **44** — **U.5**: per-stmt-constructor correspondence (round-trip).
- **45** — **U.6**: chain composition (closes the IR-boundary trust).
- **46** — U.3 third slice: `KeysUniqueRec` + bidirectional.

## Cross-cutting (CC.*)

- **20** — CC.1 + CC.3 housekeeping (2026-05-29).
- **22** — Item B: CC.4 self-annotate citations.
- **25** — CC.4 Module 4: `expr_eq_dec` + citation.
- **49** — CC.4 audit-anchor stubs — `make self-annotate-verify` green.
- **51** — CC.4 Module 4 Lean citation re-added.

## Self-annotation thread (sticky-01.md prep)

- **47** — Layer 2 fully green; self-annot-2.md blocker list stale.
- **48** — Q4 U.5 compound stmt round-trip expansion.
- **50** — Item 1 — contract_expr encoder + SAssert/SGhost*/SFor U.5.
- **52** — Item 2 — Q4 corpus residue scoped (NOT implemented).

## sticky-01.md — Mechanical cross-check (Phase 0 + Phases 1-4)

- **53** — Phase 0: `--reverify-proofs` (coqc + lake + Print Assumptions).
- **54** — Phases 1+2+3 v0 (regex-based mechanical cross-check).
- **55** — Phases 1-4 production v1 (first-order IR cross-check).

## sticky-02.md — Production-grade extraction backends

- **21** — Item A: Lean Why3Trust cert-as-witness port (precursor to sticky-02 Phase B).
- **56** — Phase D: make integration; cross-check on every `make`.
- **57** — Phase A: sertop foundation.
- **58** — Phase B: Lean meta-extractor working.
- **59** — Phase C: IR expansion DEFERRED (no test target then).
- **60** — Phase A v1: full sertop integration end-to-end.
- **61** — Phase C: IR expansion for non-gcd theorems (`wp_gen_correct` validated).

## Recent — Self-annotate + closer-to-code close-out (2026-05-30)

- **62** — Self-annotate mirror body merger (`bin/sync-mirror-bodies.py`; 365 bodies replaced).
- **63** — Module 6 fixes restore 26/26 PROVED (map-typed params, exception-name sanitization).
- **64** — closer-to-code.md close-out (3 glossary entries, audit-plan Q2+Q4 closures, Rocq9 stub → attic).

---

## Reading order for new maintainers

1. **`closer-to-code.md`** — the master plan (~240 lines).
2. **`src/formal-semantics/audit-plan.md`** §2-3 — current trust state.
3. **This index** + item **64** (close-out) — current state of execution.
4. **Items 44-46** — the U.5/U.6 IR-boundary closure (the keystone results).
5. **Items 56-61** — sticky-01/02 cross-check work (the
   mechanical-verification arc).
6. **`0342_explanation.md`** + **`working-with-two-sources-of-truth.md`** — worked example + dual-prover reference.

## End-state metrics (post item 64)

- Rocq: **0 PyCSL-specific axioms** in the live build.
- Lean: 2 visible + 1 hidden PyCSL axioms (all anchored to
  named external trust lines).
- Self-annotation suite: **26/26 PROVED**.
- `make self-annotate-verify`: Layer 1 14/14 + audit 34/34 +
  cross-check 14 PASS / 8 SKIP / 0 FAIL.
- Byte-diff PASS rate on real corpus: 346/386 = **89.6%**.
- Reference 0342 + neighbors (0342-0351): **10/10** under full proof.

## Open work (per `todo-saturday.md`)

- Q4 corpus residue (22 blockers, 8 categories) — multi-week.
- Manual `Expr.decEq` in Lean — ~1 day cosmetic.
- `proof2why3 emit` registry auto-gen — ~2-3 days.
- This index — ✅ done (item 65 to come).
