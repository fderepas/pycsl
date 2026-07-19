# Value-model campaign (multi-session, user-authorized 2026-07-19)

**Goal:** convert the value-model / reflection trusted stubs that remain after the reachable-cheap frontier was
exhausted at 1041 (entire AST-lowering surface + str_of_int done). These need faithful Python-VALUE modeling
(the "no-more-int" doctrine) rather than int-erasure. START = measure-before-build; keep delegated builds on a
TIGHT leash (a facade slipped through proof+byte-diff+mirror-check last round — FIDELITY is a separate oracle,
see `config/skills/self-tcb-reduction/emit-ir-conversion-lessons.md` §9-§10).

## Frontier (from probes + peer triage; to be refined by the census)
- **Module5 annotation-walkers (~22)** — recursive isinstance-dispatch on `ast.Subscript`/`Name`/`Attribute`
  type-annotation nodes → type-tag STRINGS (`_field_type_from_annotation(_inst)`, `_normalize_union/final/literal_
  annotation`, `_m5_get_type_name(_legacy)`, `_m5_get_dict_key/value_type`, `_typeddict_field_type`, `_wrap_optional`,
  `_union_arm_tag`, `_collect_union_arms`, `_encode_callable_annotation`, `_callable_type_tag`,
  `_extract_generic_arg_names`, `_classify_literal_value`, `_collect_type_params/typevar/final_registry`,
  `_mixin_field_type`, `_array_init_size`). Hypothesis: reachable via the annotation-node → emit_ir retype +
  isinstance-on-emit_ir discriminants + type-tag string construction (str concat + str_of_int). THE FIRST PROBE TARGET.
- **Module6 emitter reflection** — `isinstance(x, str)`→`typeof_op`, `getattr(self, hashed)`, `x in self._dict`
  membership. Value/instance-state reflection.
- **Irreducible leaves** — `whyml_string_literal` (per-char UTF-8 encoding loop), `stable_hash`, `_fresh_var`
  (counter+format). These are likely F1-FLOOR (legitimately trusted primitives — a faithful port = a trusted stub =
  net-zero; do NOT facade them with a simplified body).

## Progress log
- **CENSUS + PROBE done** (2026-07-19): VERDICT PARTIAL — ~8 walkers (→~11 with `str_lower`) behind the P1/P2/P3
  mechanical primitives; ~7 are genuine value-model walls (`.lower`/`.strip`/`.join`, stateful `program_ir`/`self._cur_*`
  mutation, AST-node construction giants).
- **INCREMENT 1 LANDED** (commit `16fffed7`, 1041→1040): a foundational TOOL fix + `_callable_type_tag`. The fix:
  `_is_emit_ir_expr` (module6_whyml/expressions.py Attribute/FieldGet branch) misclassified STRING-LEAF attrs
  (`_EMIT_IR_STR_ATTRS`: id/attr/name/op/…, which route to `name_of`/`kind_of` string projectors) as emit_ir
  sub-nodes → a str-returning walker binding `x = node.id` got `_returns_emit_ir` + a `Return_emit_ir` wrapper on a
  string (typecheck fail). Fix = exclude `_EMIT_IR_STR_ATTRS` from that branch (symmetric with `_is_string_expr`).
  CORPUS-INERT (byte-diff 0). CONSUMER-SAFE: statements.py + module6/expressions.py + Module5 all re-prove SUCCESS
  (the mandatory cross-file re-prove for a shared-tool change). Fidelity VERBATIM. This unblocks the whole class of
  string-returning `.id`/`.attr`-readers. P3 (sub-dispatcher retype) not needed for this walker.

## ANNOTATION-WALKER SUB-CAMPAIGN COMPLETE (increments 1-9, 1041→1035, −6 walkers)
Converted: `_callable_type_tag`, `_typeddict_field_type`, `_m5_get_dict_key_type`, `_normalize_final_annotation`,
`_m5_get_dict_value_type`, `_union_arm_tag`. 9 BANKED REUSABLE PRIMITIVES: `_is_emit_ir_expr` string-leaf fix;
scoped `.slice`→sindex_of; P3 sub-dispatcher ExprIR-retype; IrMkTupleN element access (is_mktuple/irlen/irnth/
elts_of); isinstance-on-emit_ir-ref-local deref; synthesized-variant early-return exception (`Return_<variant>`);
generalized string-return wrapping; tuple-unpack-from-IrMkTupleN; `is_none`-conjunction recognizer. All: fidelity
verbatim, corpus byte-diff 0 (or gated-inert), consumers re-prove, ledger 3, no facade. PROVEN BOUNDARIES (not
assumed): pyconst_val per-kind value discrimination (`_classify_literal_value` — emit_ir arm carries no pyconst_val,
`is_none` covers only None); `.lower()`/`.strip()` string-method leaves; stateful `program_ir`-mutating giants
(`_normalize_union/literal_annotation`, `_collect_*`); variant-to-variant delegation (`_m5_get_field_key_type`).
NEXT candidate: `str_lower` (abstract val, str_of_int-analog) for the `.lower()`-walled leaves — measure-before-build.

## GIANTS FRONT MEASURED (increment 10 loop-over-irlist LANDED 496c27e9 1032→1031; increment 11 BOUNDARY)
The annotation-walker frontier is EXHAUSTED. Turned to the 24 "stateful giants." A read-only census claimed
~11 are PURE-NOW (return-a-collection, blocked only by a collection-accumulator loop). **An emission probe REFUTED
that** (`getting-better`/`targeted-refactor.md` §2c): the accumulator (`map_update_some`/`Seq.snoc`) already exists;
the real blocker is that the ITERABLE (`node.body` ClassDef, `node.args.args` FunctionDef, `node.type_params`) and its
ELEMENTS (statements/args) are **un-modeled opaque AST nodes** — `isinstance(child, ast.Assign)`→`isinstance_op`,
`child.targets[0].id`→opaque `get_id/subscript_get`. **0 of 7 targets convert with a collection primitive.**
**Gating prerequisite for the WHOLE giants front (collectors PURE-NOW *and* the MUTATES refactor set):**
statement/definition-node AST modeling — `class_body_ast`/`func_args_ast`/`type_params_ast` child-list readers +
typed statement/arg element-field readers (`.targets`/`.value`/`.annotation`) + a `type(x).__name__` reflection
decision. A substantial multi-reader build (authorize-first), NOT a lowering primitive. The refactor (return-the-value)
is necessary-but-not-sufficient: a mutating method made pure still can't verify until this AST modeling lands.
**Reachable autonomous transcription frontier is EXHAUSTED at 1031.**

## Order of work (measure-before-build each)
1. ~~CENSUS + PROBE~~ DONE. ~~Increments 1-9 (annotation-walker sub-campaign)~~ COMPLETE (1041→1035).
2. If feasible, build the primitive + convert the cluster incrementally (whole-file-proof-gated, byte-diff
   characterized — the annotation path MAY be corpus-affecting: verify by sweep, re-prove changed files).
3. Then the Module6 emitter reflection (isinstance-on-value/typeof/getattr).
4. Floor-audit the irreducible leaves (whyml_string_literal etc.) → record as F1, do not convert.

## Gate (per conversion, unchanged): FIDELITY (mirror body == live body verbatim — DIFF IT) ∧ whole-file Why3 proof
∧ corpus byte-diff (0 if inert, else every changed file re-proves faithfully + fixtures regenerated) ∧ ledger 3
(no new axiom) ∧ isinstance_op=0. No infrastructure-without-conversion; no simplified-body facade.
