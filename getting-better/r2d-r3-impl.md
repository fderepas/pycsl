# r2d-r3-impl.md — R2d (recursive folds) + R3 (hval assoc-list carrier), spike-gated

User-authorized (18h run): build R2d + R3 together to clear the 8 fully-erased IRScanner
predicates. BOTH are required (the recursion is a second blocker independent of the value model).
R3 is certificate-touching; every make-or-break was spiked FIRST, before any emitter/cert edit.

## §GATE-S — all three make-or-break spikes PASS (oracles in scratchpad/r2d, r3cert)

1. **R2d recursive-fold mechanism** (`recfold.mlw`, `recfold2.mlw`). A recursive predicate whose
   `any`-fold is MUTUALLY recursive with it, shared termination variant. Termination VCs
   (`uses_tag'vc`, `any_uses'vc`) **Valid**; concrete positive `pos7` **Valid** (z3 0.01s / AE
   0.04s); evil twin `evil99` **Valid**; wrong-answer `MUSTFAIL` correctly Timeout/Unknown;
   axioms 0. The mutual-recursion fold shape is sound.

2. **R2d+R3 composed** (`hval_composed.mlw`). The assoc-list hval (HMap carrier = `hpairs` assoc
   list, not a Why3 map) + the recursive `uses_str` fold over it. Nested `{"type":"String"}`
   positive **Valid** (0.01s), evil twin (value ≠ "String") **Valid** (0.03s), `MUSTFAIL`
   Timeout; axioms 0. Reproduces the reviewer's `hval_prog` result; the two mechanisms compose.

3. **R3 §6a — the certificate re-cert (the reviewer left this UNRUN; it was R3's whole risk).**
   `r3cert/Phase2f_assoc.v`: the hval soundness CORE (ADT + `size`/`list_size`/`pairs_size`
   measures + mutual induction + `size_pos`/`list_size_nonneg`/`pairs_size_nonneg` +
   the fold-termination witnesses `list_tail_lt`/`pairs_tail_lt` + observability) with the
   assoc-list HMap carrier. `coqc` builds clean; **`Print Assumptions` = "Closed under the global
   context" for all four load-bearing theorems** → the carrier swap re-certifies AXIOM-FREE. The
   key structural change: `size (HMap p) = 1 + pairs_size p` (was `= 1`, flat) — so the measure
   now DESCENDS into the map, which is exactly what makes `.values()` a terminating fold.

**Disposition: BUILD authorized.** R3's scariest gate (§6a) is green.

## Build sequence (each increment its own gate battery; ledger stays 3)
1. R3 certificate: port the assoc-list carrier into the REAL `Phase2f_PyVal.v` + `PyVal.lean`;
   `make` + `Print Assumptions`/`#print axioms` must stay axiom-free (ledger 3).
2. R3 emitter: `preamble.py` hval theory HMap carrier map→assoc-list + builders/projectors;
   re-lower the 3 existing consumers (`_collect_final_registry`, `_collect_type_params`,
   `_collect_typevar_registry`) + the `map string (option (map string (option hval)))` return.
   Mirror-wide L3-tc (all 52) + corpus byte-diff 0 + whole-file proofs of the 5 hval files.
3. R2d emitter: emit the bounded any/all fold INSIDE the recursive `let rec function … with …`
   group with a shared variant, for a recursive predicate.
4. Converge on the IRScanner 8 (`uses_string`/`uses_sum`/`_check`/…): faithful hval `obj` +
   recursive fold → remove each from `KNOWN_ERASURES` as it de-vacuifies.
Refutation exit at any step: record boundary, revert clean, fall back to R2d-as-infra.
