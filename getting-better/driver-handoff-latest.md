# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-26, RELAUNCH #2 worker)

## The L14 debt is SETTLED. Do not re-open it.

The frame-soundness fix is **LANDED at `e95f73de`**; L14-b at `3871b47a`. Verify in two seconds if you
doubt it: `git show HEAD:src/pycsl/module6_whyml/functions.py | grep -n "if (is_method$"` — if that
line has no `and not emit_as_val`, the fix is in.

**Re-proof sweep result: 8 of 8 mirrors SUCCESS, 6146 goals Valid, 0 Unknown, ZERO conversions
reverted.** `\trusted` count UNCHANGED — 668 raw / 631 directives, before and after — which is the
correct outcome for a soundness repair. Full per-file evidence is in `driver-backlog.md` §L14 and in
`driver-progress.log`.

## Three things this window learned that will bite you if you ignore them

1. **A gate result committed without the code it gates is a CLAIM.** Two prior windows reported L14
   done. Only the oracle and a green-gates log entry had been committed; the patch sat in an orphan
   worktree and HEAD still had the bug. Before believing any "landed", read the source at HEAD.
   (Lesson (u).)
2. **The prover pin is stale and it silently halves every gate.** `pycsl.py:1318` names
   `Alt-Ergo,2.6.2,`; the installed one is **2.6.3**, so Why3 rejects it, the second prover contributes
   nothing, and every "dual-prover" run is Z3-only. Fail-closed, so nothing unsound was accepted — but a
   sweep that must decide *revert or keep* will FALSE-REVERT anything only Alt-Ergo can prove.
   **Pass `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` explicitly on every gate you rely on.** Expect ~2x
   the historical per-file time: `_run_vacuity_gate` runs every prover with no early exit, so the
   timings recorded in this backlog were taken with the second prover effectively disabled.
   (Lesson (w). The permanent config repair stays on the flagged-for-USER list — it moves proof
   outcomes corpus-wide and wants a deliberate M1 sweep.)
3. **Two `\trusted` counts are in circulation and both are right.** Raw `grep -cF '\trusted'` = 668;
   `grep -cF '#@ \trusted'` = 631; the 37-line gap is prose that mentions the marker. Commit messages
   track 631, relaunch prompts quote 668. Never compare across the two.

## Useful timings measured this window (correctly-pinned dual-prover, whole-file, vacuity gate on)

`proof2why3/parser` 54s · `pure_ast` 410s · `Module2_Parser` 621s · `statements` ~1400s ·
`Module6_WhyMLTranspiler` ~1050-1550s · `expressions` 1608s · `stmt_control_flow` 3100s ·
`Module5_IREmitter` 3281s. Four in parallel on 12 cores is comfortable. **Emit-and-diff BEFORE you
prove** (lesson (r)) — it cut this sweep from 52 files to 8, and the two slowest mirrors were among
the ones it excluded from earlier sweeps.

## Where the ladder stands — L13 is LANDED

`b6c417f6` opened the certified `term` inductive to the general emission path and **converted 5
`_Parser` stubs** (`parse_expr`, `parse_implication`, `parse_disjunction`, `parse_conjunction`,
`parse_comparison`). **Directives 631 -> 626.** Gates: proof **3071/3071 Valid, 0 Unknown** across the
3 mirrors the emission diff selects; corpus byte-diff **0** (813/813); fidelity at the baseline
2 DIVERGED / 3 drifted; ledger 3, no new axiom.

**Pick up here — three concrete continuations, in demand-first order:**
1. **`parse_arith_add`, `parse_arith_mul`, `expect`** are now the ASSUMED-INTERFACE FRONTIER. Each
   carries `#@ ensures self.pos >= \old(self.pos)` + `self.pos <= \length(self.toks)` as a reviewer
   assertion on a still-`\trusted` stub. **Converting each one RETIRES its assumption** — that is
   count reduction AND TCB reduction in the same move, and the capability they need is already landed.
2. **The `0`-reads-as-`None` faithfulness bug.** `Module5_IREmitter::_collect_class_constants` emits
   `if (!iv <> 0)` as a stand-in for "is not None", so a legitimate constant value of 0 reads as None.
   The union-local typing fixes it, but the concrete-resolution gate (`_record_array_fields`) excludes
   `PyCSLToJSONEmitter`. Widening that gate is the lever, and the corpus byte-diff is the real gate.
3. **`parse_quant` / `parse_atom` / `parse_atom_application`** need the one unbuilt capability:
   seq -> `list term` at an ADT CONSTRUCTOR ARGUMENT (`tuple(binders)`), precedent
   `_bind_listfield_from_seq` (which binds a record FIELD, not a ctor argument), plus `" ".join(...)`.

**Two process facts this window paid for, do not relearn them:**
- **The §10.4 re-port obligation is live.** Editing a LIVE emitter function that has an UN-TRUSTED
  mirror counterpart breaks `check-self-annotate-sync.sh` until you port the change into the mirror.
  It caught exactly that here (`functions::_compute_return_type`, `stmt_control_flow::_handle_return_stmt`),
  and the re-port then GREW the emission diff from 1 mirror to 3. Budget for that.
- **Run the corpus byte-diff BEFORE the mirror proof sweep.** ~7 min/side versus ~50 min, and it
  falsified an intermediate version of this build in one shot.

## The rest of the ladder

Next position: **L13, the `proof2why3` `_Parser` cursor nest** — top lever, spike PASSED (41/41),
closed capability set of FOUR, payoff 11-15 stubs. Read `driver-backlog.md` §L13 and the Gate-R
amendments in `getting-better/cursor-nest/cursor-nest.md`. Two constraints that L14's landing makes
BINDING rather than theoretical:
  - the nest is largely ALL-OR-NOTHING now, because a converted member cannot discharge its
    termination measure while its callee is a `\trusted` val with a declared `writes { self.pos }`,
    unless that stub is given a monotonicity postcondition (= TCB growth);
  - BUT Gate R proved a counter-construction: `parse_expr`, `parse_quant`, `parse_comparison` have no
    self-call and no callee-dependent loop, so **3 of the 11 convert piecewise with ZERO TCB growth**.
    That is the cheap entry point — take it before attempting the whole nest.
Then L10 (`Optional[X]` field value model + string-aware `_field_default`; entry point located verbatim
in the backlog), then L9-drain, L2, L3, L6, L5.

Standing discipline unchanged: demand-first (capability-first is REFUTED, three convergent yield-0
builds); close a blocker set by ITERATED measurement until L3-tc PASSES; spike-first with a refutation
exit; lesson (p) census-first; the three L-planes driver-verified fresh; ledger stays 3.
