# Run #6 lvP re-census (Part 1): the five run #6 capabilities against the cv11 chains

Executor lvP, driver run #6 batch E, 2026-11-10. Base `run6-lvP` = `run6-lvO` (ghost-assign-bc6 + u36 + lvM + lvN + lvL + lvO).
Census only (this section); nothing below was built for it. Method = cv9/cv11 chain method: the VERBATIM live body is
ported into a scratch copy of its mirror file (`bin/port-one-mirror-body.py --convert [--replace]`), emitted
`--no-proof --keep-mlw` (Why3 type-check included) on heavy.sh QUICK slot 3, the blocker classified, then the deepest
cv11 chain spec (`scratchpad/cv11/spec/<tag>.json`, cv11's `patch.py`) replayed on the same tree, and where a run #6
capability could have moved the wall, new links walked. Scratch tree `stU` = this base + `run6-u37` (route #583's
unified `avalue_of`, the fifth capability, which is NOT in lvP's base) built with `git merge-tree` (clean merge).
Raw data: `scratchpad/lvP/probe/` in the lvP worktree (`results.tsv`, `<tag>.src.py/.log/.mlw/.patchlog`),
`scratchpad/lvP/spec/` (new link specs), `scratchpad/lvP/sel.json` (selection).

**Selection.** Every `\trusted` stub whose cv11 record (`scratchpad/cv11/merged11.json`: need / links / finals / prior
chains / d0 capability) names one of `cap-vm-irnode-R1-narrowing-view`, `cap-exception-payload-model`,
`cap-exception-object-read`, `cap-re-match-model`, `cap-pair-unroll`, `cap-none-default-map-param`,
`cap-trusted-val-unit-return`, `cap-vm-unerase-tuple`, or an emit_ir `.value` read: 54 records, of which 9 are no longer
governing markers at this base (converted in run #6: `_match_block_hdr` (lvO), `_ContractParser._err`, `_Parser.error`,
`_Parser.unsupported` (lvM), `_collect_type_params`, `_collect_typevar_registry`, `_const_int_value`,
`_m5_get_type_name_legacy` (lvL R1), `StatementEmissionMixin._expr_to_whyml` (lvN declared_in)) and 2 are converted only on
`run6-u37` (`_collect_final_registry`, `_union_arm_tag`: PORT-ABORT "no governing marker" in `stU`). 45 stubs re-walked,
70 probes + 9 new-link probes.

## 0. Headline

- **No first blocker vanished.** At depth 0 every one of the 45 has cv11's first-blocker class (two at a shifted site:
  `_parse_inductive` / `_parse_inductive_rules`, see below). The R1 view, the exception-payload model, the re.Match model,
  the pair unroll and `pycsl_none_map` did not reach any of these walls by themselves: the R1 rows still stop on R567 /
  R566 for RECORD-modelled receivers or item stores (`_collect_class_fields`, `_csl_list_to_ir`,
  `_emit_namedtuple_record`, `_synthesize_*_functional`, `_parse_quantifier`); the exception-payload model does not cover
  a READ of `exc` bound by `except .. as exc` (route #233 still refuses `_index_proofs_dir`, `parse_type_expr`:
  `cap-exception-object-read` is unbuilt); the re.Match model (lvO) is gated on plain `import re`, a `str`-declared
  NAME subject and `if m:` / `if not m:` tests, so the Module2 matches (`import re as _re`, `self.source[pos:]`,
  `m is None`) and the struct_format / normalize matches (`m.lastgroup`, `m.start()`, `m.group()`, `Any` subject) stay
  opaque at depth 0.
- **Near misses (rewrites / retypes only): ONE new.** `_ContractParser._grab_reviewer_id` (Module2_Parser.py) is TC-OK
  and honest after [R] three behaviour-identical rewrites of its LIVE body (`_re.match` -> `re.match` with a plain
  `import re`; the slice subject bound to a `str` local; `m is None` -> `not m`, a `re.Match` is always truthy) and [T]
  two mirror retypes (the `\trusted` `_ContractParser.__init__` stub declares the `source: str` field the live
  constructor sets; `#@ raises ContractSyntaxError when True`, the live body calls the raising `_err`). Probe
  `s050_R3`: input-reading (`str_sub_op self.source pos ..`, `re_match_op "[A-Za-z0-9._@-]+" rest 0`,
  `re_group_op m 0`, the token-skip loop over `self.toks`). Its home is Module2_Parser.py, Part 2's file.
- **One capability away:** `_ContractParser._parse_inductive_rules` (cap-vm-unerase-tuple only; TC-OK at
  `s062_R2` with the [T] return retype `-> List[Tuple[str, Any]]` + the raises clause, every appended `(name, expr)`
  rule still `any int`), `_ContractParser._parse_inductive` (the same + its own retype; TC-OK at `s061_R2`, record list
  fields `any_array ()`; cv11's second capability `cap-trusted-val-unit-return` is NOT needed once
  `_parse_inductive_rules` is converted in the same file: lvF (run #5) already announces a `pass`-body `\trusted`
  `-> List[..]` stub as `array int`; only `Tuple[...]` returns stay `unit`), `_ContractParser._parse_contract` (needs
  the re.Match model on its `declared_in` arm: with [R] `import re`, a `str` subject local and the `or`-test split into
  two `if`s plus [T] the `source` field, `s057_R2` moves to a new wall: `py_label` record vs `emit_ir`, i.e. the
  record-vs-ADT seam of the `label` arm: not one capability), `_ContractParser._parse_variant_def` (its `(str,
  List[str])` tuple return is typed `(int, int)`: cap-vm-unerase-tuple for a list slot), `_lex_contract`
  (needs `m.lastgroup` / `m.start()` / `m.group()` in the re.Match model AND the `(toks, source)` tuple return).
- **A pipeline CRASH introduced in run #6 (fixed in this branch, lvP increment (2)):** the verbatim port of
  `proof2why3/normalize.py::_alpha_rename` died with `UNEXPECTED PIPELINE ERROR: cannot use 'tuple' as a set element
  (unhashable type: 'dict')` in lvO's match-local scan (`functions.py::_reset_function_state`, the
  `_rxm_sigs.discard` of a call whose argument is an f-string node). After the fix (`s336_T1`) the port is back at
  cv11's wall (route #275 `sorted(.., key=..)`).
- `_Harvester._normalize_leading`: depth 0 still `unbound function '_match_block_hdr'` although lvO VERIFIED that
  function: the converted callee is emitted AFTER its caller (`any(<genexp>)` callee ordering, cv11's
  `cap-any-genexp-callee-order`), unchanged.
- `ControlFlowStmtMixin._handle_for_stmt`: cv10's chain now stops one link earlier on the mirror's
  `ControlFlowStmtMixin._expr_to_whyml` declaration (no `subst` parameter, while lvN's statements.py declaration has it);
  with that [T] retype (`s311_R1`) the next wall is R327 (identifier collision, route #327): DEPTH-STOP as before.

## 1. Per-stub table

Verdicts: REFUSED = a PyCSL refusal, L3-TC = Why3 type error, TC-OK = emitted and type-checks, PORT-ABORT = no governing
marker in `stU`. "still missing" subtracts the five run #6 capabilities and the free kinds (mirror retype, live
refactor) from cv11's chain needs; it is cv11's knowledge, refined by the new links in §2.

| sid | stub (file) | cv11 end | depth-0 at HEAD+u37 (verbatim port) | deepest cv11 chain spec replayed at HEAD+u37 | still missing (cv11 chain needs minus run #6 builds) |
|---|---|---|---|---|---|
| s015 | `_index_proofs_dir` (audit_proof.py) | HONESTY-WALL | REFUSED: '_index_proofs_dir' reads the exception object 'exc' bound by `except ... as exc` (ROUTE #233). The handler is modelled | L3-TC: mlw l.202: This expression has type int, but is expected to have type array.Array.array int @rho | `cap-exception-object-read`, `cap-fs-path-model`, `cap-return-exn-nonint` |
| s034 | `PyCSLError.__init__` (errors.py) | TC-OK-FACADE | TC-OK | - | (none) |
| s041 | `_Harvester._build` (frontend/Module1_Ingestor.py) | DEPTH-STOP | REFUSED: `self._flat.append(...)` appends to the collection in the field `_flat`, and no certified lowering models it: the append | L3-TC: mlw l.205: This expression has type ref int @rho, but is expected to have type PyCSL_Program._target <array.Array.array | `cap-field-collection-writeback`, `cap-method-recursion-cycle`, `cap-vm-unerase-tuple` |
| s043 | `_Harvester._fold_blocks` (frontend/Module1_Ingestor.py) | DEPTH-STOP | REFUSED: function '_harvester___fold_blocks': mutating a collection that a TUPLE-UNPACKING assignment aliases is out of scope: `[ | REFUSED: PYCSL-R325-OPAQUE-INT-FALLBACK (route #325) — in '_harvester___fold_blocks', the value 'str_concat' comes from 'str_conc | `cap-R325-str-encoding-op`, `cap-str-join-array`, `cap-trusted-val-unit-return`, `cap-vm-unerase-tuple` |
| s045 | `_Harvester._normalize_leading` (frontend/Module1_Ingestor.py) | DEPTH-STOP | L3-TC: mlw l.122: unbound function or predicate symbol '_match_block_hdr' | L3-TC: mlw l.340: This expression has type option.Option.option (string, string), but is expected to have type int | `cap-any-genexp-callee-order`, `cap-trusted-val-unit-return`, `cap-vm-unerase-union` |
| s046 | `_match_block_hdr` (frontend/Module1_Ingestor.py) | TC-OK-FACADE | not a governing marker at base (converted in run #6) | - | - |
| s048 | `_ContractParser.__init__` (frontend/Module2_Parser.py) | DEPTH-STOP | REFUSED: class '_ContractParser' carries a `#@ class invariant`, but its constructor obligation (route #226: the invariant must h | REFUSED: the functions ['_contractparser___parse_atom'] call one another in a cycle that passes through a METHOD or CONSTRUCTOR c | `cap-ctor-invariant-obligation`, `cap-vm-unerase-tuple` |
| s049 | `_ContractParser._err` (frontend/Module2_Parser.py) | TC-OK-FACADE | not a governing marker at base (converted in run #6) | - | - |
| s050 | `_ContractParser._grab_reviewer_id` (frontend/Module2_Parser.py) | DEPTH-STOP | REFUSED: PYCSL-R325-OPAQUE-INT-FALLBACK (route #325) — in '_contractparser___parse_trusted', the value 'reviewer' comes from 'm_g | - | `cap-vm-unerase-str`, `cap-vm-unerase-union` |
| s053 | `_ContractParser._parse_assigns_target` (frontend/Module2_Parser.py) | HONESTY-WALL | REFUSED: heterogeneous list literal (contains a record (Nothing) element mixed with other element types) has no faithful WhyML `a | L3-TC: mlw l.1195: This expression has type (), but is expected to have type int | `cap-heterogeneous-list`, `cap-trusted-val-unit-return`, `cap-vm-callable-value` |
| s057 | `_ContractParser._parse_contract` (frontend/Module2_Parser.py) | DEPTH-STOP | REFUSED: PYCSL-R325-OPAQUE-INT-FALLBACK (route #325) — in '_contractparser___parse_contract', the value '_m_di_group_1' comes fro | - | (none) |
| s061 | `_ContractParser._parse_inductive` (frontend/Module2_Parser.py) | TC-OK-PARTIAL | REFUSED: line 1416: PYCSL-R551-CONSTRUCTOR-ARGUMENT-KIND: `rules` is passed to the parameter `rules` of `InductiveDecl`, declared | L3-TC: mlw l.1642: this expression raises unlisted exception ContractSyntaxError | `cap-trusted-val-unit-return`, `cap-vm-unerase-tuple` |
| s062 | `_ContractParser._parse_inductive_rules` (frontend/Module2_Parser.py) | TC-OK-PARTIAL | L3-TC: mlw l.1634: This expression has type array.Array.array int @rho, but is expected to have type int | L3-TC: mlw l.1638: this expression raises unlisted exception ContractSyntaxError | `cap-vm-unerase-tuple` |
| s063 | `_ContractParser._parse_quantifier` (frontend/Module2_Parser.py) | DEPTH-STOP | REFUSED: PYCSL-R567-EMITIR-ATTR-ON-NONIR: `domain.kind` (in `_contractparser___parse_quantifier`) reads a field of a value this f | - | `cap-vm-callable-value`, `cap-vm-irnode-R1-record-arm`, `cap-vm-unerase-union` |
| s064 | `_ContractParser._parse_variant_def` (frontend/Module2_Parser.py) | DEPTH-STOP | L3-TC: mlw l.1902: This expression has type (string, seq.Seq.seq string), but is expected to have type (int, int) | L3-TC: mlw l.1901: This expression has type seq.Seq.seq string, but is expected to have type seq.Seq.seq int | `cap-vm-unerase-list` |
| s066 | `_lex_contract` (frontend/Module2_Parser.py) | HONESTY-WALL | L3-TC: mlw l.1960: This expression has type int, but is expected to have type string | - | `cap-vm-unerase-list` |
| s072 | `Module3_Weaver._expand_happy_properties` (frontend/Module3_Weaver.py) | DEPTH-STOP | REFUSED: src/self-annotate/src/frontend/Module3_Weaver.py line 413: src/self-annotate/src/frontend/Module3_Weaver.py (function 'm | REFUSED: src/self-annotate/src/frontend/Module3_Weaver.py line 413: src/self-annotate/src/frontend/Module3_Weaver.py (function 'm | `cap-identity-vs-literal`, `cap-object-identity-model` |
| s084 | `PyCSLWeaver._dispatch_function_contracts` (frontend/Module3_Weaver.py) | DEPTH-STOP | REFUSED: dropped unpacking / loop target refused (route #301) -- function '_dispatch_function_contracts': an unpacking / loop tar | L3-TC: mlw l.1521: This expression has type int, but is expected to have type array.Array.array int @rho | `cap-field-collection-writeback`, `cap-nested-unpack-target`, `cap-pyast-node-attr-writeback`, `cap-trusted-val-unit-return` |
| s097 | `PyCSLToJSONEmitter._collect_class_fields` (frontend/Module5_IREmitter.py) | DEPTH-STOP | REFUSED: function 'pycsltojsonemitter___collect_class_fields': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a | REFUSED: PYCSL-R567-EMITIR-ATTR-ON-NONIR: `rhs.func` (in `pycsltojsonemitter___collect_class_fields`) reads a field of a value th | `cap-exact-pop-model`, `cap-pyast-node-typing` |
| s098 | `PyCSLToJSONEmitter._collect_final_registry` (frontend/Module5_IREmitter.py) | TC-OK-HONEST | PORT-ABORT | - | (none) |
| s099 | `PyCSLToJSONEmitter._collect_type_params` (frontend/Module5_IREmitter.py) | TC-OK-HONEST | not a governing marker at base (converted in run #6) | - | - |
| s100 | `PyCSLToJSONEmitter._collect_typevar_registry` (frontend/Module5_IREmitter.py) | TC-OK-HONEST | not a governing marker at base (converted in run #6) | - | - |
| s102 | `PyCSLToJSONEmitter._const_int_value` (frontend/Module5_IREmitter.py) | TC-OK-HONEST | not a governing marker at base (converted in run #6) | - | - |
| s104 | `PyCSLToJSONEmitter._csl_list_to_ir` (frontend/Module5_IREmitter.py) | DEPTH-STOP | REFUSED: PYCSL-R566-EMITIR-ITEM-STORE: an item store `d[...] = ...` into a value the model types as an IR node (`emit_ir`: a `-> | - | `cap-emit-ir-item-store-model`, `cap-getattr-dynamic` |
| s107 | `PyCSLToJSONEmitter._emit_namedtuple_record` (frontend/Module5_IREmitter.py) | DEPTH-STOP | REFUSED: function 'pycsltojsonemitter___emit_namedtuple_record': an erased (`Any`/`object`/unannotated/TypeVar) value flows into | REFUSED: PYCSL-R566-EMITIR-ITEM-STORE: an item store `_fld[...] = ...` into a value the model types as an IR node (`emit_ir`: a ` | `cap-emit-ir-item-store-model`, `cap-erased-to-builtin-slot-arg`, `cap-inplace-mutator-computed-receiver`, `cap-pyast-node-typing`, `cap-self-field-alias-analysis` |
| s114 | `PyCSLToJSONEmitter._m5_get_type_name_legacy` (frontend/Module5_IREmitter.py) | TC-OK-HONEST | not a governing marker at base (converted in run #6) | - | - |
| s122 | `PyCSLToJSONEmitter._synthesize_namedtuple_functional` (frontend/Module5_IREmitter.py) | DEPTH-STOP | REFUSED: function 'pycsltojsonemitter___synthesize_namedtuple_functional': an erased (`Any`/`object`/unannotated/TypeVar) value f | REFUSED: PYCSL-R567-EMITIR-ATTR-ON-NONIR: `call.func` (in `pycsltojsonemitter___synthesize_namedtuple_functional`) reads a field | `cap-erased-to-builtin-slot-arg`, `cap-inplace-mutator-computed-receiver`, `cap-pyast-node-typing`, `cap-self-field-alias-analysis` |
| s123 | `PyCSLToJSONEmitter._synthesize_typeddict_functional` (frontend/Module5_IREmitter.py) | DEPTH-STOP | REFUSED: function 'pycsltojsonemitter___synthesize_typeddict_functional': an erased (`Any`/`object`/unannotated/TypeVar) value fl | REFUSED: PYCSL-R567-EMITIR-ATTR-ON-NONIR: `call.func` (in `pycsltojsonemitter___synthesize_typeddict_functional`) reads a field o | `cap-erased-to-builtin-slot-arg`, `cap-inplace-mutator-computed-receiver`, `cap-pyast-node-typing`, `cap-self-field-alias-analysis` |
| s124 | `PyCSLToJSONEmitter._union_arm_tag` (frontend/Module5_IREmitter.py) | TC-OK-HONEST | PORT-ABORT | - | (none) |
| s140 | `_find_record_type_from_dep_imports` (frontend/ir_resolve.py) | DEPTH-STOP | L3-TC: mlw l.1511: This expression has type int, but is expected to have type array.Array.array int @rho | L3-TC: mlw l.1533: This expression has type PyCSL_Program._union__resolve_module_path_0, but is expected to have type int | `cap-vm-unerase-irnode`, `cap-vm-unerase-tuple`, `cap-vm-unerase-union` |
| s157 | `_check_gt4_polymorphic_recursion` (frontend/monomorphize.py) | DEPTH-STOP | REFUSED: PYCSL-R325-OPAQUE-INT-FALLBACK (route #325) — in '_extract_ast_subscript', the value 'node' comes from '_ast_walk_1', a | - | `cap-R325-call-ast-walk`, `cap-R325-call-set-ctor` |
| s161 | `_rewrite_annotation_str` (frontend/monomorphize.py) | HONESTY-WALL | REFUSED: line 388: PYCSL-R542-NON-CONTAINER-OPERAND: `rename_map` is the container of `in` / `not in` and may be a number. CPytho | L3-TC: mlw l.821: This expression has type string, but is expected to have type int | `cap-return-exn-nonint` |
| s176 | `_Parser._fin_block` (frontend/pure_ast.py) | HONESTY-WALL | REFUSED: dropped unpacking / loop target refused (route #301) -- function '_fin_block': an unpacking / loop target of shape `Tupl | L3-TC: mlw l.4344: This expression has type int, but is expected to have type PyCSL_Program. pytuple_int_int | `cap-dynamic-getattr-setattr`, `cap-emit-ir-inplace-field-write`, `cap-vm-unerase-tuple` |
| s179 | `_Parser.error` (frontend/pure_ast.py) | TC-OK-FACADE | not a governing marker at base (converted in run #6) | - | - |
| s181 | `_Parser.unsupported` (frontend/pure_ast.py) | TC-OK-FACADE | not a governing marker at base (converted in run #6) | - | - |
| s194 | `_Unparser.visit_Dict` (frontend/pure_ast.py) | HONESTY-WALL | L3-TC: mlw l.5741: This pattern has type ('mu, 'mu1), but is expected to have type int | - | `cap-context-manager-model`, `cap-effectful-callback`, `cap-vm-unerase-tuple` |
| s199 | `_Unparser.visit_arguments` (frontend/pure_ast.py) | DEPTH-STOP | L3-TC: mlw l.5682: This pattern has type ('mu, 'mu1), but is expected to have type int | - | `cap-pyast-node-typing`, `cap-vm-unerase-tuple` |
| s213 | `fix_missing_locations` (frontend/pure_ast.py) | HONESTY-WALL | L3-TC: mlw l.890: This expression has type (), but is expected to have type int | - | `cap-dynamic-getattr-setattr`, `cap-generator-yield-model` |
| s237 | `ExpressionEmissionMixin._dotted_ensures_suffix` (module6_whyml/expressions.py) | DEPTH-STOP | REFUSED: '_handle_field_get_expr' line 1488: `self_type` (an instance of ['ExpressionEmissionMixin', 'a list / dict / set']) is H | - | `cap-hash-judge-class-set`, `cap-vm-unerase-tuple` |
| s241 | `ExpressionEmissionMixin._expr_to_whyml_string_ctx` (module6_whyml/expressions.py) | TC-OK-PARTIAL | REFUSED: the functions ['expressionemissionmixin___expr_to_whyml_string_ctx'] call one another in a cycle that passes through a M | TC-OK | `cap-method-recursion-cycle`, `cap-missing-mirror-function`, `cap-vm-unerase-list` |
| s257 | `ExpressionEmissionMixin._linear_form` (module6_whyml/expressions.py) | DEPTH-STOP | REFUSED: dropped unpacking / loop target refused (route #301) -- function '_linear_form': an unpacking / loop target of shape `Tu | REFUSED: line 783: PYCSL-R542-NON-CONTAINER-OPERAND: `lv` is the argument of `dict` and may be a dict, a number. CPython cannot i | `cap-method-recursion-cycle`, `cap-vm-unerase-tuple`, `cap-vm-unerase-union` |
| s262 | `ExpressionEmissionMixin._static_width` (module6_whyml/expressions.py) | DEPTH-STOP | REFUSED: dropped unpacking / loop target refused (route #301) -- function '_static_width': an unpacking / loop target of shape `T | REFUSED: line 776: PYCSL-R542-NON-CONTAINER-OPERAND: `uv` is the argument of `dict` and may be a dict, a number. CPython cannot i | `cap-vm-unerase-tuple`, `cap-vm-unerase-union` |
| s272 | `FunctionEmissionMixin._parse_mixin_sig` (module6_whyml/functions.py) | DEPTH-STOP | REFUSED: an `and` / `or` expression whose operand is not a bool or an int (a list, str, dict, set, float, Optional or object) is | L3-TC: mlw l.2540: This expression has type string, but is expected to have type int | `cap-R325-call-str-split`, `cap-list-comp-model`, `cap-vm-unerase-tuple` |
| s298 | `StatementEmissionMixin._expr_to_whyml` (module6_whyml/statements.py) | DECL-ONE-CAP | not a governing marker at base (converted in run #6) | - | - |
| s311 | `ControlFlowStmtMixin._handle_for_stmt` (module6_whyml/stmt_control_flow.py) | DEPTH-STOP | REFUSED: '_handle_for_stmt' line 785: `_r2b_root` (an instance of ['BoolWrapIRView', 'ControlFlowStmtMixin', 'a list / dict / set | REFUSED: '_handle_for_stmt' line 1326: the call `self._expr_to_whyml(var_ir, inv_refs, subst=inv_subst)` got an unexpected keywor | `cap-vm-unerase-irnode` |
| s314 | `calcsize` (module6_whyml/struct_format.py) | HONESTY-WALL | L3-TC: mlw l.113: This expression has type string, but is expected to have type int | - | `cap-vm-unerase-dict` |
| s315 | `parse_format` (module6_whyml/struct_format.py) | HONESTY-WALL | REFUSED: 'parse_format' line 98: the construction `StructFormat(raw=fmt, prefix=prefix, slots=tuple(slots), chars=tuple(chars))` | L3-TC: mlw l.68: The type of top-level exception Return__union_parse_format_0 has mutable components | `cap-return-exn-nonint`, `cap-vm-unerase-tuple` |
| s329 | `_is_ofnat_lit` (proof2why3/from_lean_json.py) | DEPTH-STOP | L3-TC: mlw l.256: This expression has type int -> option.Option.option int, but is expected to have type int | - | `cap-int-of-str-model`, `cap-vm-unerase-dict`, `cap-vm-unerase-tuple` |
| s330 | `_linearize_app` (proof2why3/from_lean_json.py) | DEPTH-STOP | REFUSED: `args.insert(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstract oper | - | `cap-inplace-mutator-insert`, `cap-vm-unerase-dict`, `cap-vm-unerase-tuple` |
| s336 | `_alpha_rename` (proof2why3/normalize.py) | DEPTH-STOP | REFUSED: cannot use 'tuple' as a set element (unhashable type: 'dict') | - | `cap-R325-call-str-split`, `cap-re-escape`, `cap-sorted-key`, `cap-vm-unerase-dict` |
| s338 | `_nat_to_int_with_sidecond` (proof2why3/normalize.py) | HONESTY-WALL | REFUSED: PYCSL-R325-OPAQUE-INT-FALLBACK (route #325) — in '_strip_all_parens', the value 's' comes from 'pattern_sub_2', a call P | - | `cap-re-compiled`, `cap-re-named-def-callable` |
| s339 | `normalize_surface` (proof2why3/parser.py) | REFUSED-termination | L3-TC: mlw l.851: This expression has type string, but is expected to have type int | - | `cap-diverges`, `cap-optstr-sentinel` |
| s340 | `parse_type_expr` (proof2why3/parser.py) | DEPTH-STOP | REFUSED: 'parse_type_expr' reads the exception object 'exc' bound by `except ... as exc` (ROUTE #233). The handler is modelled wi | - | `cap-exception-object-read` |
| s354 | `_function_body_eqs` (pycsl.py) | HONESTY-WALL | L3-TC: mlw l.1427: This expression has type array.Array.array string @rho, but is expected to have type int | L3-TC: mlw l.1432: This expression has type int, but is expected to have type string | `cap-vm-unerase-list`, `cap-vm-unerase-union` |

## 2. New links walked (lvP specs under `scratchpad/lvP/spec/`, extra edits under `scratchpad/lvP/probe/<tag>.extra.sh`)

| tag | stub | links (R = behaviour-identical live rewrite, T = mirror retype) | verdict | next |
|---|---|---|---|---|
| s050_R1 | `_ContractParser._grab_reviewer_id` | R `re.match` (plain `import re`), R `rest: str = self.source[pos:]`, R `if not m:` | L3-TC (`self.source` is a dynamic getattr: no such field in the mirror record) | T |
| s050_R2 | same | + T `self.source: str = raw` in the `\trusted` `__init__` stub (live sets it) | L3-TC unlisted `ContractSyntaxError` | T |
| s050_R3 | same | + T `#@ raises ContractSyntaxError when True` | **TC-OK, honest** | convert (Part 2) |
| s057_R1 | `_ContractParser._parse_contract` | R `re.match`, R str subject local, R `not _m_di` inside the `or` | REFUSED R325 `_m_di_group_1` (lvO's model needs a bare `if not m:` test) | R |
| s057_R2 | same | + R `or` split into two `if`s (same message, same order) + T `source` field | L3-TC `py_label` record vs `emit_ir` (the `label` arm builds a record where the method returns the ADT) | DEPTH-STOP (record/ADT seam) |
| s061_R2 | `_ContractParser._parse_inductive` | cv11 r9xs039_6 + T raises clause on both | TC-OK, PARTIAL (list fields `any_array ()`, member triples `any int`) | cap-vm-unerase-tuple |
| s062_R2 | `_ContractParser._parse_inductive_rules` | cv11 r9xs040_2 + T raises clause | TC-OK, PARTIAL (each `(name, expr)` rule `any int`) | cap-vm-unerase-tuple |
| s311_R1 | `ControlFlowStmtMixin._handle_for_stmt` | cv10 r10xh109_3 + T `subst` / `invariant_ctx` on the mirror `_expr_to_whyml` declaration | REFUSED R327 identifier collision | DEPTH-STOP |
| s336_T1 | `_alpha_rename` | none (after the lvP crash fix) | REFUSED route #275 `sorted(.., key=..)` | as cv11 |

## 3. Summary for the driver

- Near misses (rewrites / retypes only): `_ContractParser._grab_reviewer_id` (Module2_Parser.py, Part 2 converts it).
- One capability: `_parse_inductive_rules` (cap-vm-unerase-tuple), `_parse_inductive` (cap-vm-unerase-tuple; the
  trusted-val unit return is already handled for `List[..]` by lvF), both Part 2. `_parse_variant_def`: the same
  capability for a `(str, List[str])` slot plus its caller `_parse_datatype` (cv11 `cap-vm-unerase-list`).
- Unbuilt and still blocking: `cap-exception-object-read` (s015, s340), the re.Match surface beyond lvO (lastgroup /
  start / group() / `Any` subject / an `_re` alias: s066, s314, s161, s338), R567/R566 for record-modelled receivers
  (the R1 DEPTH-STOP rows), route #301 nested unpack targets (s084, s176, s257, s262).

## 4. Outcome (Part 2, same branch)

Converted in lvP increment (3): `_ContractParser._grab_reviewer_id` (the near miss), `_ContractParser._parse_inductive_rules`,
`_ContractParser._parse_inductive` (cap-vm-unerase-tuple, lvP increment (2)), and `_ContractParser._parse_variant_def`
(its `(str, List[str])` return through the declared-tuple return of increment (2), after a behaviour-identical single-`return`
respelling of the live body). The `_alpha_rename` crash is fixed in increment (2) (witness 9510).
