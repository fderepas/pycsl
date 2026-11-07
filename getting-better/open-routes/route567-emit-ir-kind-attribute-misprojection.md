# OPEN ROUTE #567 — `.kind` (AND THE OTHER _EMIT_IR_STR_ATTRS) READ ON A RECORD-MODELLED NON-IR CLASS VALUE (`isinstance(node, DictView)` under a @mutable_state class, the parameter annotated "ExprIR") IS LOWERED TO `kind_of <node>`, THE emit_ir CONSTRUCTOR TAG, NOT THE RECORD FIELD, SO A FALSE POSTCONDITION BECOMES A THEOREM OF THE MODEL
**Status: REPAIRED (run #5, executor lvG off 0ce6ece57 = run5-int37, branch run5-lvG, the §1 commits). Mechanism (emitter, `expressions.py::_handle_attribute_expr`, mirror twin `\trusted`: the narrowing table is computed there from the IR body of the function being emitted, read-only, no new emitter field; inline, no new def, no axiom, no new ADT arm; annotations §7.566): `PYCSL-R567-EMITIR-ATTR-ON-NONIR` -- an `_EMIT_IR_STR_ATTRS` projector read (`.kind` / `.name` / `.op` / ...) whose receiver access path is, or extends through a field of, a path an `isinstance(path, C)` of the same body tests against a class that is not an IR class (an `ir_schema.IRNode` subclass named bare and not declared by this file, or an `ast.<Node>` / CSL class the isinstance-on-emit_ir recognizers map to a real discriminant), when C may carry the attribute (its record fields, an `ast` class's `_fields` / `_attributes`, every attribute for an unknown class), is REFUSED. Flow-insensitive, closed under plain assignment. Applied EVERYWHERE: the mirror-only relaxation first added here (only record-modelled classes narrowed in the mirror) was REJECTED by the user and REMOVED in run #5 lvG2; five Module5 mirror functions it covered are now `\trusted` (see the lvG2 block below).** EVIDENCE: see the block at the end of this file.

Opened as: **Status: OPEN, Severity 1 (model-level unsoundness; the full proof of the exemplar is solver-bound today).** Found by the independent vm-irnode review (ac1d388bf, hazard H1): expressions.py:185, gated only on @mutable_state.
Exemplar witnesses-r567/w567_kind_misproj.py: `is_keys_view(DictView("d", "keys"))` returns 1 in CPython, `ensures \result == 0`. The review's 3-arm why3 spike proves the misprojected claim Valid with Z3 (the faithful projector's false claim Unknown); on the full 110-arm emission Z3 / Alt-Ergo time out at 120 s, so pycsl reports Verification FAILED today (scratchpad/vmF/toy/f1_kind_misproj.proof.log) — the model is wrong, only the prover's capacity hides it.

## EVIDENCE (run #5, executor lvG, base run5-int37 0ce6ece57)
- Witnesses x default / typed / store, `--no-proof` front end: `w567_kind_misproj` -> 3/3 PYCSL-R567-EMITIR-ATTR-ON-NONIR.
  Full default-model verdicts at base: w567 / corpus 9025 (alias `dv = node`), 9026 (direct `node.kind`), 9027 (`.name` under a
  TUPLE-of-classes isinstance to file records) Verification FAILED -- the 110-arm `kind_of` case split times out, the model
  entails the false claim (the review's 3-arm spike: Valid in 0.00 s). At HEAD all REFUSED in all three models.
- Corpus: 9025 / 9026 / 9027 FAIL (REFUSED at HEAD); advice control 9033 (`dv: DictView` parameter, honest two-sided claim)
  PASS at base and HEAD = `witnesses-r567/advice/a567_record_typed_param.py` (audited FOLLOWABLE); control 9034 (its false
  `\result == 0`) FAIL at base and HEAD (the faithful field read); control 9035 (`node.kind` with no isinstance: the tag
  projector kept) PASS at base and HEAD.
- The first rule (keyed on the ROOT variable, every non-schema class) refused the Module5 mirror (`_callable_type_tag`'s
  `node.id` under `isinstance(node, ast.Name)`, `_classify_literal_value`, `_const_int_value`'s `value.op` under
  `ast.UnaryOp`): measured, then narrowed to access paths, to the attributes the tested class may carry, to the recognizer
  maps' classes as IR classes, and -- in the mirror only -- to record-modelled classes. Module5 mirror emission byte-identical.
- Byte-diff vs 0ce6ece57: root 0 MOVED / 0 GONE / 0 APPEARED (+6), python-reference 2185 0 / 0 / 0. Mirror: 53/53 0 MOVED / 0 GONE / 0 APPEARED (every mirror twin touched is `\trusted`; nothing owed).

## EXEMPTION REMOVED (run #5, executor lvG2, base run5-int45 ad5b44278, branch run5-lvG2)
- USER DECISION: the mirror relaxation is rejected. The `is_self_mirror_r566` clause of the narrowing judge in
  `expressions.py::_handle_attribute_expr` is deleted (with its now-dead `_rec567` flag); `pycsl.py::_run_pipeline` no
  longer computes the path flag. Every `isinstance` against a non-IR class narrows, in every file.
- Mirror functions now refused, all in `frontend/Module5_IREmitter.py`, all RE-TRUSTED (`cost-scale:emit-ir-narrowing-view`,
  getting-better/driver-backlog.md "routes #566 / #567 mirror re-trusts"): `_const_int_value` (`value.op`, `value`
  narrowed to `ast.UnaryOp`), `_collect_final_registry` (`sub.target.value.id`, `sub` narrowed to `ast.AnnAssign`),
  `_collect_typevar_registry` (`call.func`, `call = stmt.value` with `stmt` narrowed to `ast.Assign`),
  `_m5_get_type_name_legacy` and `_union_arm_tag` (`elt.value.id`, `elt` also tested against `ast.Constant`). No
  equivalent rewrite avoids the read (an alias that hides the narrowing would exploit the hole below, not repair the
  function). Live code unchanged (a `\trusted` mirror body is not sync-checked). Every other mirror file emits with the
  strict rule (measured: a per-file `--no-proof` emission of all 53 mirror files, refusals iterated to a fixpoint).
- HOLE (open, reported): the assignment closure runs FORWARD only. `dv = node; if isinstance(dv, DictView): if
  node.kind == "keys": return 1` is NOT refused and lowers `node.kind` to `kind_of node` (measured `--no-proof` at the
  lvG2 tip; the forward form `if isinstance(node, DictView): dv = node; if dv.kind ...` is refused). The same misprojection
  as w567 is reachable through a backward alias.
