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

## Order of work (measure-before-build each)
1. ~~CENSUS + PROBE~~ DONE. ~~Increment 1 (string-leaf-attr fix + _callable_type_tag)~~ LANDED.
2. If feasible, build the primitive + convert the cluster incrementally (whole-file-proof-gated, byte-diff
   characterized — the annotation path MAY be corpus-affecting: verify by sweep, re-prove changed files).
3. Then the Module6 emitter reflection (isinstance-on-value/typeof/getattr).
4. Floor-audit the irreducible leaves (whyml_string_literal etc.) → record as F1, do not convert.

## Gate (per conversion, unchanged): FIDELITY (mirror body == live body verbatim — DIFF IT) ∧ whole-file Why3 proof
∧ corpus byte-diff (0 if inert, else every changed file re-proves faithfully + fixtures regenerated) ∧ ledger 3
(no new axiom) ∧ isinstance_op=0. No infrastructure-without-conversion; no simplified-body facade.
