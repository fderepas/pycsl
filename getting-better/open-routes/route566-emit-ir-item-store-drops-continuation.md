# OPEN ROUTE #566 — AN ITEM STORE INTO A VALUE THE EMITTER TYPES AS emit_ir (`d["act_name"] = an`, `d` from a `-> "ExprIR"` method of a @mutable_state class) IS LOWERED TO `()` AND THE REST OF THE BLOCK IS NEVER LOWERED, SO EVERY OBLIGATION AFTER THE STORE (a callee precondition, an assert, the return value) DISAPPEARS
**Status: REPAIRED (run #5, executor lvG off 0ce6ece57 = run5-int37, branch run5-lvG, the §1 commits). Mechanism (emitter, `statements.py::_handle_array_set_stmt`, mirror twin `\trusted`; inline, no new def, no axiom, no new ADT arm; annotations §7.566): `PYCSL-R566-EMITIR-ITEM-STORE` -- an item store whose receiver the emitter types `emit_ir` in a `@mutable_state` class is REFUSED, everywhere: the self-annotation-mirror file-path exemption first added here (the mirror kept the unmodelled no-op) was REJECTED by the user and REMOVED in run #5 lvG2 (no path flag remains in `_run_pipeline`); the mirror's one verified store (`stmt_control_flow.py::_handle_match_stmt`) is now refused and that mirror function is `\trusted` (see the lvG2 block below). Lowering the continuation alone was not enough: a store LAST in its block (nothing dropped) still left the model reading the OLD node after the block -- new witness `witnesses-r566/s566_stale_lit.py` (`d = {"type": "Var", "name": ""}; if an == "x": d["name"] = an` then `self.need_empty(d.name)`).** EVIDENCE: see the block at the end of this file.

Opened as: **Status: OPEN, Severity 1 (fail-OPEN; opened in driver run #5, 2026-11-05).** Found by the independent vm-irnode review (getting-better/vm-irnode-wall-response.md, ac1d388bf, hazard H2): statements.py:2694-2706, the emit_ir ArraySet branch returns without lowering `rest`. Neither check-dropped-mutation.py (Module 5 population) nor check-param-mutator-visibility.py (parameter receivers) sees it.
Exemplar witnesses-r566/w566_dropped_tail_precond.py: `bump` stores into `d = self.mk(an)` then calls `self.need_empty(an)` whose precondition `an == ""` is violated for an = "x". Driver repro on main 80bb03d98 (2026-11-05T14:5xZ, scratchpad/run5/r566/repro.out): Verification SUCCESS; control witnesses-r566/c566_control_no_store.py (the same without the store): Verification FAILED on the R167 precondition sub-goal (correct).

## EVIDENCE (run #5, executor lvG, base run5-int37 0ce6ece57)
- Witnesses x default (hoare) / typed / store, `--no-proof` front end (scratchpad/lvG/w/out-g3): `w566_dropped_tail_precond`,
  `s566_stale_lit`, `s566_stale_attr` -> 9/9 PYCSL-R566-EMITIR-ITEM-STORE. Full default-model verdicts at base 0ce6ece57:
  w566 / corpus 9020 Verification SUCCESS (the dropped callee precondition), 9021 SUCCESS (the dropped `raise` under
  `no_exception \all`), s566_stale_lit / 9022 SUCCESS (the stale read after a store LAST in its block); s566_stale_attr FAILED
  (the opaque `mk` result hides the staleness). At HEAD all REFUSED. The `typed` / `store` emission of these programs fails
  L3 at the base (`unbound type symbol 'array'`), so there the refusal replaces an L3 failure.
- Corpus: 9020 / 9021 / 9022 FAIL (REFUSED R566 at HEAD, PROVED at base); control 9030 (no store) FAIL at base and HEAD on the
  R167 precondition sub-goal; advice controls 9031 (a dict display carrying every key) and 9032 (a separate local
  `Dict[str, str]`, `ensures \result == an`) PASS at base and HEAD = `witnesses-r566/advice/`.
- Byte-diff vs a worktree at 0ce6ece57: root 2932 -> 2938 0 MOVED / 0 GONE / 0 APPEARED (+6 emitted new sources: 9030-9035),
  python-reference 2185 0 / 0 / 0. Mirror: 53/53 0 MOVED / 0 GONE / 0 APPEARED (every mirror twin touched is `\trusted`; nothing owed).
- (SUPERSEDED by the lvG2 block) The one verified mirror store (`stmt_control_flow.py::_handle_match_stmt`,
  `c["pattern"] = new_pat`) was kept by a mirror-only allowance; that allowance is gone.

## EXEMPTION REMOVED (run #5, executor lvG2, base run5-int45 ad5b44278, branch run5-lvG2)
- USER DECISION: the file-path exemption is rejected. `statements.py::_handle_array_set_stmt` raises
  `PYCSL-R566-EMITIR-ITEM-STORE` unconditionally (the no-op + continuation branch is deleted) and the
  `transpiler.is_self_mirror_r566` path flag is removed from `pycsl.py::_run_pipeline` (its only readers were the two
  exemptions). Mirror twins of both live methods are `\trusted`: nothing owed for the live edit.
- The mirror's one verified store is refused: `module6_whyml/stmt_control_flow.py` `ControlFlowStmtMixin._handle_match_stmt`
  RE-TRUSTED (`cost-scale:emit-ir-item-store-model`, getting-better/driver-backlog.md "routes #566 / #567 mirror
  re-trusts"). No equivalent rewrite types in the mirror model: the rebuilt case (`{"pattern": new_pat, "guard": ...,
  "body": ...}`) or a separate pattern list would hold a dict with no `"type"` key, which is not an emit_ir value, while
  `cases` is an `array emit_ir`. The live method is unchanged (a `\trusted` mirror body is not sync-checked).
- Gates: see the lvG2 report (getting-better/driver-run-log.md) -- witnesses, corpus byte-diff, mirror sweep movers.
