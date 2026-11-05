# vm-irnode wall — implementation plan (run #5, driver synthesis of vm-irnode-wall.md + vm-irnode-wall-response.md)

Verdict of the independent review (Gate R passed, ac1d388bf): COST/SCALE wall with two live CORRECTNESS defects riding on it; not a certified boundary. Plan = the review's §5, gated.

## 0. Make-or-break spike FIRST (Gate P / S) — QUICK, no emitter commit
S1: in a scratch tree, make functions.py's return-type lowering select `array emit_ir` + `materialize_ir` when the mirror return annotation is `List["ExprIR"|"StmtIR"|...]` (gated on that annotation, int lists untouched); re-run probe p13 (`_csl_list_to_ir` port) to `--type-only` clean AND run the corpus byte-diff root + pyref against the base: must be 0 MOVED.
- REFUTES (p13 not clean for a model reason, or the corpus moves in a way that is not exactly the intended return lowering) -> the list half is a CERTIFIED-BOUNDARY for this run; record why; continue with step 1 only.
- REFINES (a different next wall) -> record it; re-plan steps 2-3 around it.

## 1. Close the two live soundness defects (mandatory, converts 0) — routes #566 / #567
- #566 (H2): statements.py emit_ir ArraySet branch (`<emit_ir>[k] = v` in a @mutable_state class) returns () WITHOUT lowering the rest of the block (statements.py:2694-2706). Fix: refuse the store (named code) when it would be dropped; never drop the continuation. Witness: response toy f2o (Verification SUCCESS today, a violated callee precondition after the store) must be refused / fail; control f2o_control unchanged.
- #567 (H1): expressions.py:185 maps `.kind` (and the other _EMIT_IR_STR_ATTRS) on a value it believes is emit_ir to kind_of even when the value is a record-modelled non-IR class (reachable via @mutable_state + isinstance). Fix: refuse such a read (named code) unless the receiver is provably emit_ir. Witness: toy f1_kind_misproj (a false ensures proves) refused.
- Both in ALL THREE memory models; corpus witnesses + controls; census / advice / annotations §7 / route docs; corpus byte-diff 0 MOVED (expected) and mirror sweep: report movers; owed whole-file proofs (expressions ~6 h, statements ~5.3 h) are DRIVER-batched (never both at once).

## 2. Wire step 0 + R1 step 1 (CSLIn retype, precedent ef94162f) and convert what becomes honest TC-OK
`_csl_list_to_ir` will NOT convert verbatim while its `act_name` store is refused by #566 — record it; take the other stubs the wiring completes (census rows in run5-chain-census.md, vm-irnode-wall.md §routes).

## 3. R3 slice: a FunctionView TypedDict for the function-entry record (optional keys as option), first consumer core_ir_semantic (s013 / s016)
Spike first: port s013 verbatim with the view declared in scratch; if the next wall is the `set()` constructor (R325) build that small ctor model first and re-probe; stop if the chain is not reachable.

## Gate battery (every increment): --fun 0 non-Valid + non-vacuity mutation test per conversion; corpus root + pyref byte-diff (0 MOVED or declared, M1 re-runs); mirror sweep with exact movers; fidelity rc 0; fast planes; ledger 3; no new \trusted, no axiom, no new sum type / cert in this run; driver re-proves every mover whole-file on the integrated tree.

## Refutation exits: S1 REFUTES -> boundary for the list half (step 1 still mandatory); step 3 spike walls -> COST/SCALE recorded with the reopening capability; any need for a new axiom -> CERTIFIED-BOUNDARY.
