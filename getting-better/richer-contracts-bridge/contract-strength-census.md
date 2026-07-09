# Contract-strength census — richer-contracts-bridge P1 (C1 measure/shape)

*Deliverable of P1 (`richer-contracts-bridge-plan.md` §3). Generated 2026-07-10,
branch `ghost-assign-bc6`, base HEAD `06a0560c`, canonical `\trusted` count **1234**.*

## Headline

- **Methods lifted C0 → C1 in P1: 0 NEW.** The one non-vacuously-eligible method
  (`_subst_type_in_ir`) was already lifted by the S-c1 spike (commit `9677fb3d`)
  and is live at HEAD. P1's honest census shows the eligible fold-walk population,
  under the *non-vacuous certified measure* filter, is a **singleton — already at C1**.
- **Total mirror methods at C1: 1** (`_subst_type_in_ir`, `ensures size(\result) > 0`).
- **Trusted-stub count: 1234** (unchanged; C1 shrinks the *footprint* of what
  `trusted_contracts_axiom` assumes for the C1 method, not the marker count — the
  honest metric per plan §35).
- **P1 mechanism delivered:** the emitter ensures-thread — previously wired only into
  the substmap/T1 family (`emit_substmap_group`) — is now extended to the **setfold,
  dictfold, and sawalk** families (one thread each), defaulting to `["true"]`
  (byte-diff 0). This is the load-bearing infrastructure: it lets the generator's
  REGISTRY target *any* fold family the moment a certified non-vacuous measure lands
  for its result type. Without it, a future REGISTRY entry for a dict/set/walk fold
  would write the `#@ ensures` into the mirror `.py` but the emitter would silently
  drop it (hardcoded `ensures { true }`).

## The eligible denominator — every GenericFold/T1–T3-recognized mirror method

Enumerated by running all 52 mirror files through the emitter recognizers
(`recognize_{generic_fold,bool_existence,frt,setfold,substmap,sawalk,dictfold}`).
14 recognized fold methods total. Eligibility = a **certified measure/top-shape fact
that is a NON-VACUOUS postcondition on `\result`**.

| # | method | file | family | `\result` type | rung | eligible? |
|---|--------|------|--------|----------------|------|-----------|
| 1 | `_subst_type_in_ir` | frontend/monomorphize.py | substmap (T1) | `pyval` | **C1** | **YES** — `size_pos` (`size(\result) > 0`) |
| 2 | `_hp_collect_written` | core_ir_semantic.py | generic_fold (T2) | `unit` | C0 | no — void (by-ref `assigns written`) |
| 3 | `_collect_assign_targets` | module6_whyml/functions.py | generic_fold (T2) | `unit` | C0 | no — void |
| 4 | `find_named_expr_targets` | module6_whyml/ir_scanner.py | generic_fold (T2) | `unit` | C0 | no — void |
| 5 | `_sa_walk` | core_ir_semantic.py | sawalk (T3) | `unit` | C0 | no — void |
| 6 | `_has_return` | module6_whyml/ir_scanner.py | bool_existence | `bool` | C0 | no — bool has no measure |
| 7 | `_has_return_with_value` | module6_whyml/ir_scanner.py | bool_existence | `bool` | C0 | no — bool has no measure |
| 8 | `find_return_type` | module6_whyml/ir_scanner.py | frt (D+T2) | `string` | C0 | no — `String.length \result >= 0` is vacuous |
| 9 | `_collect_calls` | frontend/ir_resolve.py | setfold | `map string bool` | C0 | no — total map, no certified measure |
| 10 | `collection_binder_kinds` | module6_whyml/ir_scanner.py | setfold | `map string bool` | C0 | no — total map |
| 11 | `find_calls_in_ir` | module6_whyml/scc.py | setfold | `map string bool` | C0 | no — total map |
| 12 | `_collect_calls` | pycsl.py | setfold | `map string bool` | C0 | no — total map |
| 13 | `find_record_var_classes` | module6_whyml/ir_scanner.py | dictfold | `sdict` | C0 | no — no non-vacuous sdict measure (see below) |
| 14 | `_collect_tuple_array_locals` | module6_whyml/types.py | dictfold | `sdict` | C0 | no — no non-vacuous sdict measure |

## Eligible-but-excluded classes (the honest exclusions, with reasons)

1. **Void folds** (generic_fold T2 + sawalk T3) — methods 2–5. These fold by
   mutating a by-ref accumulator (`assigns written`) or walking for effect; the
   emitted top-level function returns `unit`. No `\result` ⇒ no value postcondition.
   *Out of scope by the plan (void/by-ref folds have no `\result`).*
2. **Bool-existence folds** — methods 6–7 (`_has_*`). Result type `bool`; a boolean
   carries no measure/shape fact, and no certified predicate applies. Not C1-eligible.
3. **String-returning fold** (frt) — method 8 (`find_return_type`). Result type
   `string`; the only candidate certified fact is `String.length \result >= 0`,
   which is **vacuous** (always true), failing the non-vacuity gate. Not C1-eligible.
4. **Set folds** (`map string bool`) — methods 9–12. A **total map** (`map string bool`)
   has no natural C1 shape and no certified measure fact — confirmed and excluded
   exactly as the plan/task scope stated. Not C1-eligible.
5. **`sdict` dict-folds** (dictfold) — methods 13–14. **A certified sdict measure
   EXISTS in Rocq** (`Phase2c_PyValDict.v`: `Fixpoint sdict_size`, `Theorem
   size_slookup_mem`) — but it does NOT yield a C1 postcondition:
   - **No positivity.** `sdict_size SNil = 0`; a dict-fold can legitimately return an
     empty `sdict` (no matching records), so `sdict_size(\result) > 0` is **FALSE**,
     and `sdict_size(\result) >= 0` is **vacuous** (a `nat`/`int` node-count). Neither
     passes the non-vacuity gate. (Contrast pyval: every constructor has `size >= 1`,
     so `size_pos` gives the strict `size v > 0`.)
   - **Not exported.** `sdict_size` is not in the WhyML preamble `_sdict_theory_lines`
     (only `slookup` + `sappend` are), so it is not even in scope for the mirror.
   Per the task's explicit instruction ("… IF one exists in the certified theory …
   if none, say so — that sub-class is then NOT C1-eligible"), the sdict fold sub-class
   is **NOT C1-eligible**. Adding a wf-predicate/exported measure is deferred (P2/C2).

## The one C1 method — proof evidence (measured/verbatim)

`_subst_type_in_ir` (`frontend/monomorphize.py`), substmap/T1 fold returning `pyval`:

```
#@ requires True
#@ ensures size(\result) > 0        <- generated (registry: fact size_pos), never hand-written
#@ assigns \nothing
```

Emitted WhyML top-level function contract:
`requires { true } ensures { ((size result) > 0) }  variant { size node }`.

- Whole-file proof: **Verification SUCCESS! All contracts formally proven**
  (`pycsl.py monomorphize.py --import-path src/pycsl`).
- Isolated goal, split VC under a prover:
  `Sub-goal Postcondition of goal _subst_type_in_ir'vc` → **Valid (alt-ergo, 0.05s,
  55 steps)** — NOT a typecheck; the `size(\result) > 0` goal is discharged by a prover.
- Non-vacuity: `size_pos` is a **strict** bound (`> 0`) from a certified lemma; the
  S-c1 twin `size(\result) < 1` FAILS (30s timeout) — the postcondition is real, not
  a vacuous-`True` restatement.

## Gates (all green)

- **Corpus byte-diff 0:** worktree-at-HEAD baseline vs working tree, one foreground
  `bin/byte-diff-sweep.sh` each — `diff -rq` clean, **763/763 identical**.
- **Ledger == 3:** `git diff HEAD -- src/formal-semantics '**/proof_axiom_allowlist.py'`
  is **empty** — no new axiom.
- **Fidelity:** `bin/self-annotate-mirror-check.sh` → all **52/52** mirrors in sync
  (the C1 change is `#@`-only on the mirror side).
- **Generator idempotency + lint:** `gen-bridge-contracts.py --check` idempotent;
  `--lint` clean (no hand-written enriched bridge ensures).
- **Round-trip components:** restatement cross-check PASS (`pin_fail=0, goal_fail=0`);
  generator idempotent; lint clean; mirror re-proves; fidelity green; ledger 0. NOTE:
  `bin/bridge-roundtrip.sh` step 7 uses `git status src/pycsl` as a byte-diff proxy —
  that proxy now (correctly) reports the emitter dirty, because P1 legitimately extends
  the emitter (the threading); the real invariant (corpus emission byte-identical) is
  verified directly by the sweep above, which is strictly stronger than the proxy.

## Files changed by P1

- `src/pycsl/module6_whyml/generic_fold.py` — `emit_setfold_group`, `emit_sawalk_group`,
  `emit_dictfold_group` gain the optional `top_ensures` thread (default `["true"]`).
- `src/pycsl/module6_whyml/functions.py` — the setfold/sawalk/dictfold dispatch sites
  pass `self._lower_fold_ensures(func)` (already wired for substmap by S-c1).
- No mirror `.py` change (the sole C1 contract on `_subst_type_in_ir` was already
  written by S-c1 and the generator reproduced it idempotently).
- No `src/formal-semantics`, no allowlist, no new axiom.
