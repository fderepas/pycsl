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

## §OUTCOME — 18h run, R2d+R3: authorized goal ACHIEVED (8/8 IRScanner), with honest caveats

**All 8 IRScanner predicates de-vacuified**, driver-verified independently (ir_scanner whole-file
proof SUCCESS 0-unproven re-run by the driver 3×; each emitted body hand-inspected = a real
pyval/pydict fold, `pystr_eq`/`DCons _ v rest`/certified variant, never `any_1`/int-hash; both
`uses_array_lit` arms modelled incl. the nested `obj[left]` projection — NOT under-approximated).
`KNOWN_ERASURES` 12 → 3. Gates all green: byte-diff 0 @ 784==784, L3-tc 52/52, mirror-check 52/52,
drift 5, ledger 3.

### Caveat 1 — the count did NOT move (943 throughout). These are INTEGRITY gains, not count.
The 8 predicates were already-booked (un-trusted) VACUOUS conversions; de-vacuifying makes 8 fake
conversions HONEST. Real value (the mirror proof now says something about what they compute), but
NOT a `\trusted` reduction. Earlier run-prose that framed this as "count moves" was wrong.

### Caveat 2 — R3 (the certificate-touching build) was UNNECESSARY for this goal.
R3 swapped the hval HMap carrier map→assoc-list (verified axiom-free). But R2d de-vacuified all 8
via the PRE-EXISTING Phase2c `pydict` catamorphism, whose `pydict = DNil | DCons key val rest` is
ALREADY the iterable assoc-list R3 rebuilt for hval. The reviewer and driver both missed that the
older certified theory already had the value model. R3 is banked (verified, axiom-free, byte-inert,
a legitimate capability for hval-typed `.values()` walkers) but was avoidable — the driver should
have checked the existing value models before scoping R3. Lesson to bank.

### The 3 remaining erasures are SESSION-SCALE (measured, authorize-first)
All three erase a param that flows ONLY into a `\trusted` sibling stub, so de-vacuifying needs the
sibling converted AND a value-model feature:
- `_emit_new_ghost_ref` — `target` only via `declared_refs.add`/`local_refs.add` (Set[str] params)
  → needs set-param-by-reference + `_stmts_to_whyml` (trusted) converted.
- `_handle_mktuple_expr` — `lr` flows only into `self._e` (trusted).
- `_collect_class_constants` — `field_names` similar.
Bounded frontier EXHAUSTED; run stops early per driver §A.3.

## §REDRAIN — 12h run: recognizer's Phase-1 reach measured & exhausted (1 conversion)
After R2d landed `recognize_type_existence`, a re-drain censused the whole mirror for `\trusted`
recursive-`Any` existence-walker stubs the recognizer could now convert (§10.3's "leave-trusted"
generic-Any class). Strict AST census (exact `if isinstance(_,dict)…/if isinstance(_,list)…/return
False` shape) found only **2** trusted matches, both in `core_ir_semantic.py`:
- **`_contains_result` CONVERTED (943→942, `f9d21fa7`, pushed)** — verbatim port, byte-identical to
  live, emitted as a real pyval/pydict catamorphism (`type_is obj "Result"` + `.values()` fold,
  certified variants), whole-file proof SUCCESS 0-unproven (driver-independent re-run), vacuity
  exit 0, ledger 3.
- **`_union_c8_test_references_union_var` NOT convertible** — needs TWO recognizer features
  (subject-FIRST param ordering + a set-membership discriminant `test.get("name") in union_vars`
  over a threaded SET param). A refined census (bool-returning + set-membership) found only ~1-2
  beneficiaries, so this extension is 2 features for ≈1 stub — over-engineering, NOT built.

**The recognizer's bounded reach is EXHAUSTED at 9 total (8 IRScanner + `_contains_result`).** The
mirror's remaining `Any`-walkers are STRUCTURE-returning (str/dict tree transforms:
`_expr_to_whyml`, `_to_bool`, the `_build_method_*_ensures_map` family) — a fundamentally different
class the bool-existence recognizer does not model (session-scale). Run stopped early per §A.3.
