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

---

# P2 addendum — C2 (structural/relational, generator-emitted)

*Executed 2026-07-10, branch `ghost-assign-bc6`, base HEAD `9565ce0f`. All C2
contracts are produced by `bin/gen-bridge-contracts.py` (REGISTRY-owned,
`--check` idempotent, `--lint` clean), PROVE verbatim (pipeline
Alt-Ergo→Z3, per-goal; a prover, not L3-tc), are non-vacuous (twin fails), and
are corpus byte-diff-0 + ledger-0 (no `src/formal-semantics`/allowlist change,
no `axiom` keyword — the deep/relational/fragment predicates are pure
DEFINITIONS + proved WhyML `lemma`s).*

## Methods lifted to C2

| method | file | family | C2 fact(s) | rung |
|---|---|---|---|---|
| `_subst_type_in_ir` | frontend/monomorphize.py | substmap (T1) | `wf_ir_deep` preservation (P2.1) + `in_emitted_fragment` preservation (P2.3), atop the retained C1 `size(\result)>0` | **C2** |
| `collection_binder_kinds` | module6_whyml/ir_scanner.py | setfold | `setfold_leaf_empty(obj,\result)` — leaf⇒empty relation (P2.2) | **C2** |

## P2.1 — wf-preservation: the honest ceiling + the resolution

- **Ceiling finding (measured):** the CERTIFIED shallow `wf_ir`
  (Phase2c_PyValDict.v line 262-263: top-level dict keys only, no recursion into
  values/lists) is **NOT an inductive invariant** of the recursive substitution.
  Threading it as `#@ requires wf_ir(node) / #@ ensures wf_ir(\result)` proves
  the TOP VC (0.08s) but the helper VCs `_subst_type_in_ir__dict'vc` /
  `__list'vc` **TIME OUT** (Alt-Ergo, 20s, 318k/174k steps) — not because SMT
  cannot redo the induction, but because the recursive-call precondition
  `wf_ir <subvalue>` is GENUINELY UNDISCHARGEABLE (shallow wf_ir constrains
  neither list elements nor non-string-key dict values). This is a real C2
  ceiling for the certified-shallow predicate.
- **Resolution (proved):** the genuinely-preservable invariant is a DEEP
  strengthening `wf_ir_deep` / `wf_dict_deep` / `wf_list_deep` (recurses into
  list elements AND dict values). It is a pure DEFINITION (NO axiom) emitted by
  `emit_substmap_group`, with two proved `let rec lemma`s
  `wf_dict_deep_shallow` / `wf_ir_deep_shallow` establishing
  `wf_ir_deep v -> wf_ir v` (so `ensures wf_ir_deep(\result)` ENTAILS the
  audited shallow `wf_ir`). Requires-threading + per-helper preservation
  ensures (`__dict: wf_dict_deep`, `__list: wf_list_deep`) discharge the
  induction helper-by-helper. The wf_val string-key case needs one lemma-pack
  fact — a CALLED `let lemma wf_val_str_stable` (split-robust exact
  instantiation) + a string-stability ensures on the top. Whole-file proof:
  **SUCCESS! All contracts formally proven**; every subst/lemma goal Valid
  (`__dict'vc` 2.0-3.1s Alt-Ergo). Non-vacuous: an `ensures false` twin times
  out (preconditions consistent).

## P2.2 — one generator-emitted relational ensures (setfold)

- `setfold_leaf_empty(v, r)` = a set fold maps a LEAF (non-dict, non-list) input
  to the EMPTY set (`r = const false`) — the set-fold analog of decoder
  totality / `None ⇒ skipped`. Pure definition, NO axiom; discharges from the
  top fold's `_ -> const false` arm alone (no per-helper threading needed).
- Co-landed: the `top_ensures` thread on `emit_setfold_group` (reverted in P1 as
  an unused facade) is re-landed HERE with its consumer.
- `collection_binder_kinds` postcondition **Valid**; whole `--fun` proof SUCCESS.
  Non-vacuous: a twin with the leaf arm demanding `const true` TIMES OUT under
  BOTH Alt-Ergo and Z3.

## P2.3 — `in_emitted_fragment` (grammar membership)

- `in_emitted_fragment(v)` = grammar-membership scoped to the emitted IR fragment
  the evaluator axioms range over (`src/self-annotate/evaluator-axiom-audit.md`).
  Structural scope: no bare `PNone` sentinel. The string-TAG half (which audited
  `stmt` tags appear) is the `pystr_eq`-opaque boundary the audit leaves to
  prose — so the CONTRACT captures the structural half, the audit prose the tag
  half.
- **Audit classification:** a BRIDGE-AUDIT OBLIGATION (a WhyML re-statement of
  the audited fragment grammar) — NOT a soundness axiom. Pure definition, ledger
  untouched. Its correspondence to `evaluator-axiom-audit.md`'s fragment is
  audited, not proven.
- Landed as a PRESERVATION contract on `_subst_type_in_ir` (the type-substitution
  rewrites annotation strings only, never removes the structural spine, so
  fragment membership is preserved), composed with the P2.1 wf machinery in
  `emit_substmap_group`. Whole-file proof SUCCESS. Non-vacuous: the predicate is
  genuinely non-trivial (`in_emitted_fragment PNone` is UNPROVABLE — it is
  false; the no-precondition identity `ensures in_emitted_fragment(\result)`
  times out), and DROPPING `requires in_emitted_fragment(node)` breaks the
  fragment ensures on the leaf arm under BOTH provers (`wf_ir_deep node ->
  in_emitted_fragment node` is false — PNone witness) — i.e. the requires is
  load-bearing.

## Gates (all green)

- **Every C2 contract PROVES** verbatim (pipeline per-goal Alt-Ergo→Z3): both
  mirror files report `Verification SUCCESS! All contracts formally proven`.
- **Non-vacuous:** twins fail (above).
- **Generated, not hand-written:** `gen-bridge-contracts.py` REGISTRY reproduces
  every clause byte-for-byte; `--check` idempotent; `--lint` clean (now covers
  hand-written bridge `#@ requires` AND `#@ ensures`).
- **Corpus byte-diff 0:** worktree-at-HEAD baseline vs working tree, one
  foreground `bin/byte-diff-sweep.sh` each — **763/763 identical** (the deep /
  relational / fragment predicate blocks + per-helper contracts are gated on the
  C2 contract being present; no reference-corpus program routes them).
- **Ledger == 3:** `git diff HEAD -- src/formal-semantics
  '**/proof_axiom_allowlist.py'` empty; no `axiom` keyword emitted.
- **Fidelity:** `bin/self-annotate-mirror-check.sh` → all 52/52 in sync.

## Files changed by P2

- `src/pycsl/module6_whyml/generic_fold.py` — `_wf_deep_predicate_lines`
  (P2.1 deep wf family + connecting lemmas + `wf_val_str_stable`),
  `_frag_predicate_lines` (P2.3 `in_emitted_fragment`),
  `_setfold_leaf_empty_lines` (P2.2); `emit_substmap_group` gains
  requires-threading + a composable preservation-family loop (wf_ir_deep +
  in_emitted_fragment) with per-helper contracts and body proof-hints;
  `emit_setfold_group` gains the `top_ensures` thread + leaf-empty predicate.
- `src/pycsl/module6_whyml/functions.py` — `_lower_fold_requires` (new);
  `_lower_fold_ensures`/`_lower_fold_requires` seed `_current_params` so
  param-referencing bridge clauses lower bare (not `!`-deref / abstract const);
  setfold dispatch passes `_lower_fold_ensures`; substmap dispatch passes
  requires too.
- `src/pycsl/module6_whyml/expressions.py` — `_CERTIFIED_PYVAL_ARITY` gains
  `wf_ir_deep`/`wf_dict_deep`/`wf_list_deep`/`setfold_leaf_empty`(2)/
  `in_emitted_fragment`/`frag_dict`/`frag_list` (direct application, not the
  opaque numbered fallback).
- `bin/gen-bridge-contracts.py` — FACT_CATALOG gains `wf_ir_deep_preserve`,
  `setfold_leaf_empty_fact`, `in_emitted_fragment_preserve`; multi-fact /
  requires+ensures / `{subject}`-aware clause model; decorator-preserving block
  reconstruction; lint covers requires.
- Mirror `#@` (generator-written): `_subst_type_in_ir` (C2 wf + fragment),
  `collection_binder_kinds` (C2 setfold relation).
- No `src/formal-semantics`, no allowlist, no new axiom.
