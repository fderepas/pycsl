# tier3-v2 Step-A — whole-body feasibility CENSUS (measured, not projected)

Executes **Step A** of `triage-ranked-tcb-tier3-phase3-v2.md`. This is a MEASUREMENT
deliverable: no ADT was built, no `src/` file was permanently edited. Every number below
is a **whole-body verbatim port + full Why3 proof** verdict (§2 inviolable rule), reverted
after each probe. It replaces every v1 projection with measured data.

Branch `ghost-assign-bc6`, `\trusted` count 1249. Date 2026-07-06.

---

## 0. Method (exactly as §2/§4 require)

For every IR-reading Module-6-core `\trusted` stub that has a **live same-file counterpart**:

1. `git checkout` the clean stub mirror file; blank the ONE `\trusted` line of the target
   method (line-count preserved).
2. `bin/sync-mirror-bodies.py` ports the **live body + real signature + real return type**
   verbatim into the mirror (all *other* methods stay `\trusted` stubs, so their contracts —
   `ensures True` — are used at call sites; the target is now VERIFIED, not trusted).
3. `PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <mirror> --import-path src/pycsl --fun <name>`
   (per-function, transitive deps). The default non-vacuity gate is ON.
4. Record the verdict; `git checkout` to revert.

**convertible-NOW** = the whole ported body reaches `Verification SUCCESS! All contracts
formally proven.` (safety + termination + non-vacuity all discharged). Confirmed
**non-vacuous** by a positive control: injecting `ensures False` into a SUCCESS method
(`uses_subscript`) makes the proof correctly FAIL.

**Scope reconciliation.** 195 `\trusted` stubs live across the six files; **164 have a live
same-file body** and are the census population. The 31 excluded stubs
(`statements.py`: 21, `stmt_control_flow.py`: 9, `expressions.py`: 1) are *cross-file sibling
type-declarations* — their real body lives in a different module6 file (e.g. `_expr_to_whyml`
is declared in `statements.py` for typing but defined in `expressions.py`). They are
**censused under their home file**, not lost. A verbatim sync leaves such a stub trivial, so it
falsely "proves" `ensures True`; excluding them removes that false-positive (they inflated a
naive first pass to 17 "SUCCESS" in `statements.py` — all spurious).

> **Caveat on "convertible-NOW".** The mirror stubs carry the trivial functional contract
> `ensures True`. A SUCCESS therefore certifies that the whole body **lowers, is type-safe,
> is exception-safe, terminates, and is non-vacuous** — a genuine de-trust (pycsl now verifies
> the body instead of assuming it) that drops the count by 1 each. It does NOT yet pin a rich
> functional post-condition; that is a further (usually much harder) step. This is the honest
> meaning of the 11 below.

---

## 1. PER-BUCKET COUNTS (the numbers that replace all v1 projections)

| bucket | count | ADT extension frees it? |
|---|---:|---|
| **convertible-NOW** | **11** | no extension needed — converts against the LANDED state today |
| **needs-list-kinds / stmt-node size-measure** | **10** | *design projection* (see §3) — a structural `size_list` variant; **not** whole-body-verified, and additionally needs param-retyping |
| **needs-contract-node ADT** | **0** | — (no stub is blocked *first* on a contract-node kind; contract readers hit B1 first) |
| **generic-Any / by-ref-param UNMODELLABLE** | **2** | no — PyCSL rejects by-reference dict/set param mutation |
| **other-blocker: `Dict[str,Any]` value-typing (B1)** | **85** | **no** — the live emitter reads raw heterogeneous dicts; `.get("type")` lowers to `int`, breaking the string dispatch. Unreachable without **retyping live source** to the ADT. |
| **other-blocker: collection-result modeling (set/dict/seq + `.add`/`.update`)** | **43** | no — the *result* collection type, orthogonal to the IR-node ADT |
| **other-blocker: front-end parse (B2 f-string / heterogeneous-list body)** | **3** | no |
| **other-blocker: WhyML-emission bug / unclassified** | **9** | no |
| **other-blocker: negative-index bounds VC (`stmts[-1]`) unprovable** | **1** | no |
| **TOTAL (genuine, same-file body)** | **164** | |

**other-blocker subtotal = 141 / 164 (86%).**

### Headline
- **Really convertible NOW: 11** (9 substantive `ir_scanner` IR-tree walkers + 2 trivial
  string helpers). Zero of these need any ADT extension.
- **Freed by a cheap extension (the size-measure): at most 10, and that is a PROJECTION**, not a
  measured conversion — see §3 for why the honest figure is ≤ 8 and why even those need a
  live-source retype.
- **Generic-Any-UNMODELLABLE (leave-trusted): 2.**
- **Everything else (141) is blocked upstream of the IR-node ADT** on raw-`Dict[str,Any]`
  value-typing (85), result-collection modeling (43), string emission / self-state (12+1). The
  IR-node ADT campaign does nothing for these without rewriting the live emitter.

---

## 2. The corrected diagnosis vs v2 §1

v2 §1 predicted a binary axis (typed-node reader = addressable; generic-Any walker =
unmodellable). **The data refutes the binary.** The real discriminators are:

1. **Pure predicate walkers that reflect with `.values()`/`any(...)` and return `bool`
   PROVE** — `uses_subscript`, `uses_string`, `uses_sum`, … are *generic-Any* walkers, yet all
   9 are convertible-NOW. So "generic-Any" is **not** inherently unmodellable; PyCSL models the
   reflective recursion and discharges its termination.
2. **Walkers that iterate `for s in stmts: … s["body"]` (explicit sub-list indexing) FAIL on
   termination** — no structural measure relates `s["body"]` to `stmts`. This is the only
   cohort a size-measure ADT could help (§3).
3. **The `_handle_*` emitter family is blocked BEFORE any IR-node kind matters** — on
   `Dict[str,Any]` value-typing (B1), string emission (B2), trusted-sibling composition (B3),
   and self-state mutation (B4), all documented in `statements.py`'s own header. The IR-node ADT
   only models the *dispatch*; it does nothing for B1–B4.
4. **The genuine unmodellable class is narrower than v1's "~10 generic-Any walkers": it is the 2
   functions that mutate a dict/set PARAMETER by reference** (`find_named_expr_targets`,
   `functions._collect_assign_targets`) — PyCSL rejects the by-value-map-param write outright.

---

## 3. Honest read of the "needs-size-measure" cohort (the one place a cheap ADT could pay)

10 stubs reach the proof stage with **termination** as an unproven VC (recursion into a nested
`stmt["body"]`/`["orelse"]` list with no structural variant). Confirmed at a 30 s timelimit for
`uses_arrayset`: the **postconditions are Valid**, only the termination VCs (and one slow
index-bounds) remain. A `size_list` structural measure — the deferred list-kinds increment of
`ir-node-adt-signature.md §9a` — is *designed* to discharge exactly this.

But three honesty caveats keep this a **projection, not a measured conversion** (v2 forbids
building on a projection):

1. **Not whole-body-verified.** Per §2's own rule, none of these has been shown to FULLY prove;
   proving them requires *building* the extension (Step B) and re-running. The census only
   establishes that termination is the sole *structural* blocker.
2. **Also needs a live-source retype.** The bodies are verbatim `List[Dict[str,Any]]`. A
   `size_list` measure lives on the ADT type, so it only engages once the param is retyped
   `List[StmtIR]` — a change to **live** `src/pycsl` source (out of Step-A scope, and exactly the
   "rewrite live source" that §1 flags as the boundary).
3. **≥ 2 of the 10 also return collections** (`find_ghost_vars` → `Set[str]`,
   `_collect_record_fields`) and would then hit the §1 collection-result blocker anyway. So the
   size-measure would free **at most ~8** (the pure-`bool` walkers: `uses_arrayset`,
   `uses_break`, `uses_continue`, `uses_for`, `has_continue`, `has_direct_return`,
   `has_in_loop_return`, `uses_inline_set_or_dict_ops`), and even those only after the retype.

---

## 4. FULL per-stub table (all 164 genuine targets)

Recursion (`recurses = yes`) flags a stub that needs a `variant`. Blocker snippet is the
verbatim Why3 / pipeline error.

### convertible-NOW  (n=11)

| file | stub | rec | blocker (verbatim) |
|---|---|:--:|---|
| expressions.py | `_e` | Y |  |
| ir_scanner.py | `is_recursive` | Y |  |
| ir_scanner.py | `uses_array_lit` | Y |  |
| ir_scanner.py | `uses_divmod` |  |  |
| ir_scanner.py | `uses_minmax` | Y |  |
| ir_scanner.py | `uses_ord_chr` | Y |  |
| ir_scanner.py | `uses_set_card` | Y |  |
| ir_scanner.py | `uses_string` | Y |  |
| ir_scanner.py | `uses_subscript` | Y |  |
| ir_scanner.py | `uses_sum` | Y |  |
| statements.py | `_wrap_body_with_return_catch` |  |  |

### needs-list-kinds / stmt-node size-measure (PROJECTION — see §3)  (n=10)

| file | stub | rec | blocker (verbatim) |
|---|---|:--:|---|
| functions.py | `_collect_record_fields` |  | recursion over List[Dict] has no structural variant; termination VC unproven |
| ir_scanner.py | `find_ghost_vars` | Y | recursion over List[Dict] has no structural variant; termination VC unproven |
| ir_scanner.py | `has_continue` | Y | recursion over List[Dict] has no structural variant; termination VC unproven |
| ir_scanner.py | `has_direct_return` | Y | recursion over List[Dict] has no structural variant; termination VC unproven |
| ir_scanner.py | `has_in_loop_return` | Y | recursion over List[Dict] has no structural variant; termination VC unproven |
| ir_scanner.py | `uses_arrayset` | Y | recursion over List[Dict] has no structural variant; termination VC unproven |
| ir_scanner.py | `uses_break` | Y | recursion over List[Dict] has no structural variant; termination VC unproven |
| ir_scanner.py | `uses_continue` | Y | recursion over List[Dict] has no structural variant; termination VC unproven |
| ir_scanner.py | `uses_for` | Y | recursion over List[Dict] has no structural variant; termination VC unproven |
| ir_scanner.py | `uses_inline_set_or_dict_ops` | Y | recursion over List[Dict] has no structural variant; termination VC unproven |

### generic-Any / by-ref-param mutation UNMODELLABLE (leave-trusted)  (n=2)

| file | stub | rec | blocker (verbatim) |
|---|---|:--:|---|
| functions.py | `_collect_assign_targets` | Y | by-ref dict/set param mutation rejected |
| ir_scanner.py | `find_named_expr_targets` | Y | by-ref dict/set param mutation rejected |

### other-blocker: Dict[str,Any] value-typing (B1)  (n=85)

| file | stub | rec | blocker (verbatim) |
|---|---|:--:|---|
| expressions.py | `_call_bytes_methods` |  | This expression has type PyCSL_Program._union__call_bytes_methods_16 |
| expressions.py | `_coerce_str_arg` |  | This expression has type int |
| expressions.py | `_coerce_to_int` |  | This expression has type int |
| expressions.py | `_content_string_method` |  | This expression has type string -> option.Option.option int |
| expressions.py | `_dotted_ensures_suffix` |  | This expression has type PyCSL_Program._union__dotted_ensures_suffix_4 |
| expressions.py | `_dv_store_value` |  | This expression has type PyCSL_Program._union__dv_store_value_0 |
| expressions.py | `_emit_bitwise_or_power` |  | This expression has type 'mu -> option.Option.option int |
| expressions.py | `_emit_membership` |  | This expression has type 'mu -> option.Option.option int |
| expressions.py | `_expr_to_whyml` | Y | This expression has type int |
| expressions.py | `_expr_to_whyml_string_ctx` | Y | This expression has type int |
| expressions.py | `_frame_trigger_term` | Y | This expression has type PyCSL_Program._union__frame_trigger_term_3 |
| expressions.py | `_handle_attribute_expr` |  | This expression has type int |
| expressions.py | `_handle_binop` |  | This expression has type PyCSL_Program.emit_ir |
| expressions.py | `_handle_call_expr` |  | This expression has type int |
| expressions.py | `_handle_dotted_call` |  | This expression has type string |
| expressions.py | `_handle_join_call` |  | This expression has type int |
| expressions.py | `_handle_len_call` |  | This expression has type int |
| expressions.py | `_handle_sum_call` |  | This expression has type int |
| expressions.py | `_is_float_expr` | Y | This expression has type int |
| expressions.py | `_is_null_byte_lit` |  | This expression has type int |
| expressions.py | `_is_string_expr` | Y | This expression has type int |
| expressions.py | `_iter_len_expr` | Y | This expression has type int |
| expressions.py | `_linear_form` | Y | This expression has type int |
| expressions.py | `_match_field_decode_idiom` |  | This expression has type int |
| expressions.py | `_match_pattern_cond` | Y | This expression has type string |
| expressions.py | `_module_binding_names` |  | This expression has type int |
| expressions.py | `_namedtuple_positional_access` |  | This expression has type int |
| expressions.py | `_pop_quant_binder` |  | but is expected to have type int |
| expressions.py | `_push_quant_binder` |  | This expression has type PyCSL_Program._union__push_quant_binder_21 |
| expressions.py | `_recognize_field_decode_idiom` |  | This expression has type PyCSL_Program. |
| expressions.py | `_resolve_dotted_signature` |  | This expression has type string |
| expressions.py | `_static_width` |  | This expression has type PyCSL_Program._union__static_width_8 |
| expressions.py | `_str_operand_to_int` |  | This expression has type int |
| expressions.py | `_subst_params` | Y | This expression has type int |
| expressions.py | `_tag_of_value` |  | This expression has type int |
| expressions.py | `_to_bool` | Y | This expression has type string |
| expressions.py | `_typeddict_field_access` |  | This expression has type int |
| expressions.py | `_typeddict_record_literal` |  | This expression has type string |
| expressions.py | `_union_none_ctor_for` |  | This expression has type int |
| functions.py | `_build_method_return_annotation_map` |  | This expression has type int |
| functions.py | `_build_method_return_type_map` |  | This expression has type int |
| functions.py | `_build_param_list` |  | This expression has type int |
| functions.py | `_callable_tag_to_whyml` |  | This expression has type string |
| functions.py | `_compute_return_type` |  | This expression has type int |
| functions.py | `_emit_function` |  | This expression has type int |
| functions.py | `_emit_union_arm_vc` |  | This expression has type int |
| functions.py | `_infer_tuple_slot_type` |  | This expression has type string -> option.Option.option int |
| functions.py | `_param_type_str` |  | This expression has type string |
| functions.py | `_parse_mixin_sig` |  | This expression has type string |
| functions.py | `_refine_tuple_return_type` |  | This expression has type 'mu -> option.Option.option int |
| functions.py | `_symtype_to_whyml` |  | This expression has type PyCSL_Program._union__symtype_to_whyml_9 |
| ir_scanner.py | `collect_escaping_exceptions` | Y | This expression has type int -> option.Option.option int |
| ir_scanner.py | `collect_user_exceptions` | Y | This expression has type int -> option.Option.option int |
| ir_scanner.py | `collection_binder_kinds` | Y | This expression has type int -> option.Option.option int |
| ir_scanner.py | `find_append_targets` | Y | This expression has type int -> option.Option.option int |
| ir_scanner.py | `uses_ghost_type` | Y | This expression has type int -> option.Option.option int |
| statements.py | `_emit_array_local_reassign` |  | This expression has type int |
| statements.py | `_emit_body_code` |  | This expression has type int |
| statements.py | `_emit_frame_condition` |  | This expression has type string |
| statements.py | `_seq_init_expr` |  | This expression has type int |
| statements.py | `_seq_operand` |  | This expression has type int |
| statements.py | `_stmts_to_whyml` | Y | This expression has type int |
| stmt_control_flow.py | `_callee_raised_direct` |  | This expression has type 'mu -> option.Option.option int |
| stmt_control_flow.py | `_callee_raised_in` | Y | This expression has type 'mu -> option.Option.option int |
| stmt_control_flow.py | `_classify_iterable` |  | This expression has type int |
| stmt_control_flow.py | `_first_assign_value_ir` | Y | This expression has type 'mu -> option.Option.option int |
| stmt_control_flow.py | `_infer_return_value_type` |  | This expression has type PyCSL_Program._union__infer_return_value_type_2 |
| stmt_control_flow.py | `_match_subject_union_info` |  | This expression has type 'mu -> option.Option.option int |
| stmt_control_flow.py | `_maybe_inject_union_return` |  | This expression has type string |
| stmt_control_flow.py | `_pattern_has_constructor` | Y | This expression has type int |
| stmt_control_flow.py | `_render_match_pattern` | Y | This expression has type int |
| stmt_control_flow.py | `_try_local_decl_kind` |  | This expression has type string |
| stmt_control_flow.py | `_try_union_is_none_match` |  | This expression has type 'mu -> option.Option.option int |
| types.py | `_bool_ir_to_int_wrap` |  | This expression has type string -> option.Option.option int |
| types.py | `_call_return_whyml_type` |  | This expression has type string |
| types.py | `_collect_array_var_assigns` | Y | This expression has type PyCSL_Program._union__collect_array_var_assigns_3 |
| types.py | `_collect_variant_var_assigns` | Y | This expression has type 'mu -> option.Option.option int |
| types.py | `_field_type_for` |  | This expression has type PyCSL_Program._union__field_type_for_0 |
| types.py | `_field_type_of` |  | This expression has type 'mu -> option.Option.option int |
| types.py | `_first_assign_kind` |  | This expression has type string |
| types.py | `_resolve_effective_ghost_type` |  | This expression has type string |
| types.py | `_rhs_yields_array` |  | This expression has type string |
| types.py | `_rhs_yields_map` | Y | This expression has type string |
| types.py | `_track_collection_metadata` |  | This expression has type string |
| types.py | `_val_is_bool` |  | This expression has type string |

### other-blocker: collection-result modeling  (n=43)

| file | stub | rec | blocker (verbatim) |
|---|---|:--:|---|
| expressions.py | `_coerce_dotted_args` |  | This expression has type array.Array.array string @rho |
| expressions.py | `_emit_contract_logic_symbol` |  | This expression has type array.Array.array int @rho |
| expressions.py | `_handle_isinstance` |  | This expression has type array.Array.array int @rho |
| expressions.py | `_handle_struct_call` |  | This expression has type array.Array.array int @rho |
| expressions.py | `_is_emit_ir_expr` | Y | This expression has type array.Array.array int @rho |
| functions.py | `_build_method_field_old_ensures_map` |  | This expression has type array.Array.array int @rho |
| functions.py | `_build_method_field_param_frame_ensures_map` |  | This expression has type array.Array.array int @rho |
| functions.py | `_build_method_field_param_post_ensures_map` |  | This expression has type array.Array.array int @rho |
| functions.py | `_build_method_field_param_result_ensures_map` |  | This expression has type array.Array.array int @rho |
| functions.py | `_build_method_field_result_ensures_map` |  | This expression has type array.Array.array int @rho |
| functions.py | `_build_method_param_result_ensures_map` |  | This expression has type array.Array.array int @rho |
| functions.py | `_build_method_param_types_map` |  | This expression has type int |
| functions.py | `_build_method_param_whyml_types_by_name` |  | This expression has type int |
| functions.py | `_build_method_result_ensures_map` |  | This expression has type array.Array.array int @rho |
| functions.py | `_build_method_result_frame_ensures_map` |  | This expression has type array.Array.array int @rho |
| functions.py | `_build_method_writes_map` |  | This expression has type array.Array.array int @rho |
| functions.py | `_callable_whyml_arrow` |  | This expression has type int |
| functions.py | `_compute_scope_sets` |  | This expression has type array.Array.array int @rho |
| functions.py | `_emit_contracts` |  | This expression has type array.Array.array int @rho |
| functions.py | `_emit_narrowing_vc` |  | This expression has type array.Array.array string @rho |
| functions.py | `_first_tuple_return_elts` | Y | This expression has type int |
| functions.py | `_has_dynamic_exec` |  | This expression has type array.Array.array int @rho |
| functions.py | `_mixin_dep_pseudo_functions` |  | This expression has type array.Array.array int @rho |
| functions.py | `_returns_string_seq` |  | This expression has type array.Array.array int @rho |
| ir_scanner.py | `_collect_mutations` | Y | This expression has type int |
| ir_scanner.py | `find_array_and_dict_vars` | Y | This expression has type int |
| ir_scanner.py | `find_assigned_vars` | Y | This expression has type int |
| ir_scanner.py | `find_iteration_mutations` | Y | This expression has type int |
| ir_scanner.py | `find_lambda_vars` | Y | This expression has type int |
| ir_scanner.py | `find_record_var_classes` | Y | This expression has type int |
| ir_scanner.py | `find_record_vars` | Y | This expression has type int |
| ir_scanner.py | `find_return_type` | Y | This expression has type array.Array.array int @rho |
| ir_scanner.py | `has_early_return` | Y | This expression has type array.Array.array int @rho |
| statements.py | `_collect_field_decode_str_locals` |  | This expression has type array.Array.array int @rho |
| statements.py | `_collect_string_elem_read_locals` |  | This expression has type array.Array.array int @rho |
| statements.py | `_typed_local_vars` |  | but is expected to have type seq.Seq.seq |
| stmt_control_flow.py | `_union_ctor_for_arm_tag` |  | This expression has type array.Array.array int @rho |
| types.py | `_collect_dict_var_assigns` | Y | This expression has type int |
| types.py | `_collect_struct_pack_assign_targets` |  | This expression has type array.Array.array int @rho |
| types.py | `_collect_struct_unpack_array_targets` |  | This expression has type array.Array.array int @rho |
| types.py | `_collect_tuple_array_locals` | Y | This expression has type int |
| types.py | `_collect_tuple_var_assigns` | Y | This expression has type int |
| types.py | `_split_tuple_type` |  | This expression has type int |

### other-blocker: front-end parse (B2 / heterogeneous list)  (n=3)

| file | stub | rec | blocker (verbatim) |
|---|---|:--:|---|
| expressions.py | `_handle_subscript` |  | heterogeneous list literal (contains a str element mixed with other element types) has n |
| functions.py | `_render_refinement_goal` |  | heterogeneous list literal (contains a str element mixed with other element types) has n |
| statements.py | `_handle_assign_stmt` |  | ('unterminated string literal (detected at line 416)', (416, 46)) |

### other-blocker: negative-index bounds VC  (n=1)

| file | stub | rec | blocker (verbatim) |
|---|---|:--:|---|
| ir_scanner.py | `ends_with_return` | Y | stmts[-1] bounds VC unproven even at 30s (termination proves) |

### other-blocker: WhyML-emission bug / unclassified  (n=9)

| file | stub | rec | blocker (verbatim) |
|---|---|:--:|---|
| expressions.py | `_call_named_builtins` |  | ? |
| expressions.py | `_call_record_constructor` |  | ? |
| expressions.py | `_emit_metatype_tags` |  | ? |
| expressions.py | `_strip_outer_parens` |  | ? |
| functions.py | `_emit_subtyping_goals` |  | ? |
| functions.py | `_reset_function_state` |  | ? |
| statements.py | `_call_returns_string_collection` |  | ? |
| statements.py | `_emit_first_assign` |  | ? |
| statements.py | `rec` | Y | ? |

---

## 5. Assessment (brutally honest)

- **The marker payoff available today is 11 de-trusts** — and 9 of the 11 sit in one file
  (`ir_scanner.py`, the only self-contained cluster). Converting all 11 moves the count
  1249 → 1238. That is the *entire* measured convertible-NOW yield of the ADT-relevant frontier.
- **No ADT extension the census can justify frees a large set.** The single candidate (the
  `size_list` measure) is a ≤ 8-stub projection that *also* requires editing live `src/pycsl`
  signatures — i.e. it is neither cheap-in-isolation nor coupling-free (it still needs its
  co-landing Phase-3 list-read certificate per v2 §3), for a yield under ten.
- **86% of the frontier (141/164) is blocked upstream of the IR-node ADT** on things the ADT
  categorically cannot touch: raw heterogeneous-dict value-typing (85), result-collection
  modeling (43), emitter string-building / self-state / WhyML-gen (13). These are the semantic
  ceiling, not an ADT-kind gap. The `d989985f`/`8993a5b9` expr ADT is real and sound, but the
  live emitter never *uses* it (it reads `Dict[str,Any]`), so the recognizer cannot engage on a
  verbatim body.
- **The generic-Any "volume" v1 feared is 2 stubs, and it is a by-ref-param-mutation boundary,
  not a reflection-style one** (Step-D leave-trusted, fail-stop — PyCSL rejects at the pipeline,
  it does not false-verify).

### Which PATH the data supports

**PATH 1 — bank the certified foundation and STOP marker conversions — with one cheap
exception.** The census confirms the v2 §5 fear: the convertible-typed-reader set is small (11
now; ≤ 8 more behind a live-source-editing, certificate-requiring extension), and the frontier
is 86% unmodellable-by-the-ADT. That does **not** justify a multi-session Step-B ADT build with
a co-landing lemma. The one action with a positive, measured, zero-build return is to **harvest
the 11 convertible-NOW de-trusts** (a Step-C-style sweep needing no new ADT, no new axiom), then
declare the marker campaign closed at the honest floor.

PATH 2 (proceed to build the size-measure ADT) is **not** supported: its measured upper-bound
yield is ≤ 8, it needs a live-source retype AND its co-landing list-read certificate, and it
leaves the 141-stub semantic ceiling untouched.

---

## WHAT REMAINS TO BE DONE

1. **Measured convertible-NOW count: 11 stubs**, converting against the landed state with **no**
   ADT extension, no new axiom:
   - `ir_scanner.py`: `uses_subscript`, `uses_array_lit`, `uses_minmax`, `is_recursive`,
     `uses_string`, `uses_sum`, `uses_set_card`, `uses_ord_chr`, `uses_divmod` (9 substantive
     IR-tree predicate walkers).
   - `statements.py`: `_wrap_body_with_return_catch` (self-field f-string wrapper).
   - `expressions.py`: `_e` (pass-through delegate).
   Harvesting all 11 (drop `\trusted`, keep the real body, keep `ensures True`) moves the count
   **1249 → 1238**. Each is a real de-trust (pycsl verifies the body's safety + termination +
   non-vacuity), verified whole-body. This is the only zero-cost payoff and it is available now.

2. **Per ADT extension, the ACTUALLY-freed (measured) count:**
   - **list-kinds / stmt-node `size_list` measure:** **≤ 8**, and only as a *projection* — the
     census shows termination is the sole structural blocker for ~8 pure-`bool` walkers, but (a)
     it is not whole-body-verified (needs the build), (b) it needs a live-`src/pycsl` param
     retype from `List[Dict[str,Any]]` to the ADT type, and (c) it still needs its co-landing
     Phase-3 list-read certificate (v2 §3). Do **not** count it as banked.
   - **stmt-node ADT (kinds only, no size):** **0** additional — the stmt-walkers fail on
     termination, not on an unrecognized stmt kind; kinds alone free nothing.
   - **contract-node ADT:** **0** — no stub is blocked first on a contract-node kind.

3. **Generic-Any-UNMODELLABLE (leave-trusted): 2 stubs** — `ir_scanner.find_named_expr_targets`,
   `functions._collect_assign_targets`. Both mutate a dict/set PARAMETER by reference; PyCSL
   rejects this at the pipeline (fail-stop, *not* false-verifying). Step-D disposition:
   leave-trusted with the residual-gap statement "caller-visible by-ref collection mutation is
   outside the by-value-map model."

4. **Other-blocker classes and sizes (141 total, all outside the ADT's reach):**
   - **85 — `Dict[str,Any]` value-typing (B1):** verbatim `.get("type")` on a raw heterogeneous
     dict lowers the value to `int`, breaking every string/kind dispatch. This is the whole
     `_handle_*` emitter family + the typed `types.py`/`stmt_control_flow.py` classifiers.
     Un-blockable without retyping the live emitter to the ADT (a live-source rewrite).
   - **43 — collection-result modeling:** returns/builds `Set`/`Dict`/`seq` and mutates it
     (`.add`/`.update`); lowers to a type mismatch (`array.Array.array …`). Orthogonal to the
     IR-node ADT.
   - **3 — front-end parse (B2):** the real body's f-string / heterogeneous-list literal is
     rejected by pycsl's front end before proof (`_handle_assign_stmt`, `_handle_subscript`,
     `functions._render_refinement_goal`).
   - **9 — WhyML-emission bug / unclassified:** the ported body emits malformed WhyML
     (duplicate variable, syntax error) or trips a union-narrowing warning path.
   - **1 — negative-index bounds:** `ends_with_return`'s `stmts[-1]` bounds VC does not discharge
     even at 30 s (8 M+ steps, non-converging); termination *does* prove, but the `[-1]` access
     over the `List[Dict]` array model is beyond the solver here.

5. **Data-driven PATH recommendation: PATH 1 (bank + stop), plus the single cheap harvest.**
   The numbers: convertible-NOW = 11 (zero build); cheapest extension yield ≤ 8 (projection,
   needs live-source edit + a certificate); unmodellable = 2; semantic-ceiling other-blockers =
   141 (86%). A multi-session, co-landing-lemma ADT build for a sub-ten projected yield fails the
   v2 §5 calculus. **Recommend: harvest the 11, close the marker campaign at the honest floor,
   record the 141-stub semantic ceiling + the 2 leave-trusted as the residual.**

6. **If PATH 2 were nonetheless taken** (not recommended), the ordered remaining steps and a
   realistic total-yield estimate:
   1. Retype the ~8 target `ir_scanner` walkers' `stmts` param from `List[Dict[str,Any]]` to the
      stmt-node ADT in **live** `src/pycsl` (a real emitter edit, gated by byte-diff 0).
   2. Build the `size_list` structural measure + its guarded decrease lemmas in the emitter ADT
      (`preamble.py`), and its **co-landing Phase-3 list-read certificate** in
      `src/formal-semantics/` (v2 §3 obligation 1) + the `variant` (obligation 2), gated on both
      provers / no-axiom / reference locks / byte-diff 0 / conformance 38/38.
   3. Re-run the whole-body census on the ~8; convert those that now FULLY prove.
   - **Realistic total-yield estimate: 11 (now) + ≤ 8 (extension) = ≤ 19 de-trusts**, i.e. the
     count floor is ~1230, against a multi-session build cost with a new certificate. The
     remaining ~140 stubs stay trusted regardless (semantic ceiling + the 2 unmodellable).
