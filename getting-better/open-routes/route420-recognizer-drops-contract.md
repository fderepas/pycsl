# OPEN ROUTE #420 — THE BESPOKE LOWERINGS DROP THE DECLARED CONTRACT (`ensures False` PROVES)
**Status: REPAIRED, candidate (run #3, 2026-10-26; rc1 executor off `42bc9c879` = main + lv1's L-T1 term gate; see REPAIR). Was OPEN, Severity 1.**
Generalises lv1's finding (run #3, `42bc9c879`: the 7 term-ADT recognizers emitted `ensures { true }` and a transform
annotated `#@ ensures False` printed `Verification SUCCESS`) and driver-backlog item #74 ("THE BESPOKE LOWERINGS DISCARD
THE DECLARED CONTRACT", which `run-soundness-planes.sh` still files as "fail-closed ... a CLAIM-REALITY ratchet, not a
soundness one" — it is a soundness defect: the run reports every contract proven while the declared one never reached
Why3).

```
#420 A RECOGNIZED SHAPE IS REPLACED BY A HAND-BUILT GROUP WITH `requires { true }` / `ensures { true }`  [Module 6]
  generic_fold.py: 147 public recognize_* (+ private walk/outer helpers, 28 multi-function cluster/pair/family
  recognizers); functions.py `_emit_function_block`: 24 FunctionEmissionMixin-local `_is_*` / `_recognize_*` branches.
  Each replaces the function's body; ~397 emission sites write a FIXED `ensures { true }`. Only 7 generic_fold
  families thread the declared ensures (`_lower_fold_ensures`; `_substitute`-style maps also `requires`) and 6 local
  handlers emit requires+ensures (`_expr_bespoke_body`, `_emit_py_expr_compare_bespoke`, gen #34).
  base b8bd00a9d, `#@ ensures False` on a recognized function            -> Verification SUCCESS (CPython: no value satisfies False)
  base, `#@ no_exception IndexError` over `iid[0]` with `iid == ()`        -> Verification SUCCESS (CPython IndexError)
```

## CENSUS (rc1, mechanical; scratchpad `census.py`)
Method: at the Module 6 boundary inject a UNIQUE marker clause into EVERY function's contract (`ensures 910000xx >= 0`,
`requires 920000xx >= 0`), emit, and record which markers are ABSENT from the WhyML (= the lowering dropped the declared
contract), with the recognizers that fired. A per-function refusal is caught and recorded, not counted. Base `b8bd00a9d`:

| population | files | functions (untrusted, emitted) | contract DROPPED |
|---|---|---|---|
| mirror `src/self-annotate/src` | 53 | 2892 | 278 (ensures 264, requires 272) |
| corpus `pycsl-reference` | 3915 | 5026 | 52 (all over `ensures True` fixtures) |
| corpus `python-reference` | 2217 | 2239 | 0 |

Families that fire on a USER program (corpus hits; every one confirmed by an executed probe below): `recognize_generic_fold`,
`pyval_string_walker`, `pyval_list_walker`, `pyval_list_search`, `pyval_flatten`, the 7 term-ADT families
(`term_isinstance_fold` / `_transform` / `term_list_build` / `term_flatten_arrow` / `term_free_vars` / `term_string_pp`, and
the multi-function `term_pp_methods` that lv1's gate did not cover), `crosscheck_selfstate_bool`, `crosscheck_term_method`.
The other 155 families fired only on mirror files (207 functions; most are keyed on the mirror's method NAME and shape,
which a user program can still spell: no name is reserved). Honoured clauses (E = ensures marker kept, R = requires kept):
only `setfold`, `stmt_setfold`, `self_method_calls`, `collect_escaping_exceptions`, `callee_implicit_exceptions`,
`find_array_and_dict_vars` keep ensures (requires dropped); `substmap` keeps both; a few `*_outer` / `first_*` keep requires
only. Every other family drops both. Only 3 mirror functions with a NON-trivial contract are claimed:
`ir_scanner.collection_binder_kinds` (`ensures setfold_leaf_empty(..)`, honoured), `Module5._csl_to_ir` and
`._py_stmt_delete` (unconditioned `raises`, emitted as `raises { E -> true }`).

Full table (family = recognizers that fired; mirror fns; corpus fns; honoured):
```
recognize_crosscheck_term_method                                                                       4   8  --
recognize_term_isinstance_fold                                                                         1   7  --
<cluster/pair member or lifted def>                                                                   48   6  --
recognize_pyval_list_walker                                                                            3   6  --
recognize_term_isinstance_transform                                                                    1   5  --
recognize_pyval_string_walker                                                                          3   3  --
recognize_pyval_list_search                                                                            1   3  --
recognize_generic_fold                                                                                 4   2  --
recognize_crosscheck_selfstate_bool                                                                    1   2  --
recognize_pyval_flatten,recognize_pyval_list_walker                                                    1   2  --
recognize_term_flatten_arrow                                                                           1   2  --
recognize_term_free_vars                                                                               1   2  --
recognize_term_list_build                                                                              1   2  --
recognize_term_string_pp                                                                               1   2  --
recognize_type_existence                                                                              10   0  --
recognize_bool_existence                                                                               8   0  --
recognize_stmt_setfold                                                                                 7   0  E-
_recognize_closure_walk,_recognize_lss_walk                                                            4   0  --
recognize_dictfold                                                                                     4   0  --
_recognize_closure_outer                                                                               3   0  --
_recognize_crn_walk,_recognize_crvn_walk                                                               3   0  --
recognize_sawalk                                                                                       3   0  --
recognize_setfold                                                                                      3   0  E-
recognize_symtab_set_dispatch                                                                          3   0  --
recognize_void_dispatch                                                                                3   0  --
recognize_wall2_items_walk                                                                             3   0  --
FunctionEmissionMixin._recognize_pyx_dispatcher                                                        2   0  --
_recognize_cira_walk,_recognize_iroaf_walk                                                             2   0  --
_recognize_crvn_outer                                                                                  2   0  --
_recognize_fdsl_walk,_recognize_serl_walk                                                              2   0  --
_recognize_frss_walk                                                                                   2   0  --
_recognize_spat_scan,_recognize_suat_scan                                                              2   0  --
recognize_bool_multiway                                                                                2   0  --
recognize_check_body_walk                                                                              2   0  --
recognize_check_field_guard_raise                                                                      2   0  --
recognize_void_generic_descend                                                                         2   0  --
FunctionEmissionMixin._is_act_guard                                                                    1   0  --
FunctionEmissionMixin._is_build_overload_param_guard                                                   1   0  --
FunctionEmissionMixin._is_emit_ghost_assign                                                            1   0  --
FunctionEmissionMixin._is_final_annotation                                                             1   0  -R
FunctionEmissionMixin._is_is_overload_stub                                                             1   0  --
FunctionEmissionMixin._is_py_expr_boolop                                                               1   0  --
FunctionEmissionMixin._is_py_expr_lambda                                                               1   0  --
FunctionEmissionMixin._is_py_stmt_assign                                                               1   0  --
FunctionEmissionMixin._is_py_stmt_delete                                                               1   0  --
FunctionEmissionMixin._is_py_stmt_match                                                                1   0  --
FunctionEmissionMixin._is_py_stmt_try                                                                  1   0  --
FunctionEmissionMixin._is_py_stmt_with                                                                 1   0  --
FunctionEmissionMixin._is_should_skip_method                                                           1   0  --
FunctionEmissionMixin._is_synthesize_overload_guard                                                    1   0  --
FunctionEmissionMixin._recognize_sorted_const_set                                                      1   0  --
FunctionEmissionMixin._recognize_str_pair_lookup                                                       1   0  --
_recognize_build_method_field_old_ensures_map                                                          1   0  --
_recognize_build_method_field_param_frame_ensures_map                                                  1   0  --
_recognize_build_method_field_param_post_ensures_map                                                   1   0  --
_recognize_build_method_field_param_result_ensures_map                                                 1   0  --
_recognize_build_method_field_result_ensures_map                                                       1   0  --
_recognize_build_method_param_result_ensures_map                                                       1   0  --
_recognize_build_method_result_ensures_map                                                             1   0  --
_recognize_build_method_result_frame_ensures_map                                                       1   0  --
_recognize_ccm_outer                                                                                   1   0  --
_recognize_ccm_walk                                                                                    1   0  --
_recognize_cira_outer                                                                                  1   0  --
_recognize_cmtl_outer                                                                                  1   0  -R
_recognize_cmtl_walk                                                                                   1   0  --
_recognize_crd_outer                                                                                   1   0  --
_recognize_crd_walk                                                                                    1   0  --
_recognize_crn_outer                                                                                   1   0  --
_recognize_cssd_outer                                                                                  1   0  --
_recognize_cssd_symbol                                                                                 1   0  --
_recognize_eal_outer                                                                                   1   0  --
_recognize_fdsl_outer                                                                                  1   0  --
_recognize_frss_outer                                                                                  1   0  --
_recognize_hsom_outer                                                                                  1   0  -R
_recognize_hsom_ym                                                                                     1   0  --
_recognize_ile_check                                                                                   1   0  --
_recognize_ile_outer                                                                                   1   0  --
_recognize_iroaf_outer                                                                                 1   0  --
_recognize_lss_outer                                                                                   1   0  --
_recognize_rss_outer                                                                                   1   0  -R
_recognize_sdl_outer                                                                                   1   0  --
_recognize_sdl_walk                                                                                    1   0  --
_recognize_serl_outer                                                                                  1   0  --
_recognize_spat_outer                                                                                  1   0  --
_recognize_suat_outer                                                                                  1   0  --
recognize_any_function_trusted                                                                         1   0  --
recognize_bool_earlyreturn                                                                             1   0  --
recognize_bool_lastelem                                                                                1   0  --
recognize_boolfold_isinstance                                                                          1   0  --
recognize_build_method_param_types_map                                                                 1   0  --
recognize_build_method_param_whyml_by_name                                                             1   0  --
recognize_build_method_return_type_map                                                                 1   0  --
recognize_build_method_writes_map                                                                      1   0  --
recognize_callable_whyml_arrow                                                                         1   0  --
recognize_callee_implicit_exceptions                                                                   1   0  E-
recognize_check_acts                                                                                   1   0  --
recognize_check_bounds                                                                                 1   0  --
recognize_check_callable_params                                                                        1   0  --
recognize_check_class_invariants                                                                       1   0  --
recognize_check_clause_fold                                                                            1   0  --
recognize_check_contract_exprs                                                                         1   0  --
recognize_check_contract_scope                                                                         1   0  --
recognize_check_final                                                                                  1   0  --
recognize_check_fresh_globals                                                                          1   0  --
recognize_check_gt3_schema_only                                                                        1   0  --
recognize_check_guard_cascade                                                                          1   0  --
recognize_check_happy                                                                                  1   0  --
recognize_check_lemma                                                                                  1   0  --
recognize_check_mutex_invariants                                                                       1   0  --
recognize_check_no_exception                                                                           1   0  --
recognize_check_noreturn                                                                               1   0  --
recognize_check_noreturn_successors                                                                    1   0  --
recognize_check_subscript_assignments                                                                  1   0  --
recognize_check_warn_fold                                                                              1   0  --
recognize_classify                                                                                     1   0  --
recognize_collect_escaping_exceptions                                                                  1   0  E-
recognize_collect_field_sites                                                                          1   0  --
recognize_collect_imports                                                                              1   0  --
recognize_collect_instantiations_ast                                                                   1   0  --
recognize_collect_mutations                                                                            1   0  --
recognize_collect_noreturn_names                                                                       1   0  --
recognize_collect_protect_index_sites                                                                  1   0  --
recognize_collect_protect_sites                                                                        1   0  --
recognize_collect_record_fields                                                                        1   0  --
recognize_compute_scope_sets                                                                           1   0  --
recognize_contains_exec                                                                                1   0  --
recognize_cpwalk                                                                                       1   0  --
recognize_crosscheck_str_agree                                                                         1   0  --
recognize_cs_clause                                                                                    1   0  --
recognize_csl_str_cata                                                                                 1   0  --
recognize_extract_ast_subscript                                                                        1   0  --
recognize_find_array_and_dict_vars                                                                     1   0  E-
recognize_find_assigned_vars                                                                           1   0  --
recognize_find_iteration_mutations                                                                     1   0  --
recognize_find_subscript_calls                                                                         1   0  --
recognize_first_assign_value_ir                                                                        1   0  -R
recognize_first_tuple_return                                                                           1   0  -R
recognize_flat_tag_func_pred                                                                           1   0  --
recognize_frame_trigger_term                                                                           1   0  --
recognize_frt                                                                                          1   0  --
recognize_global_call_target                                                                           1   0  --
recognize_handler_catches                                                                              1   0  --
recognize_has_dynamic_exec                                                                             1   0  --
recognize_ir_free_vars                                                                                 1   0  --
recognize_is_linear_vc                                                                                 1   0  --
recognize_is_trivial_new                                                                               1   0  --
recognize_method_edges                                                                                 1   0  --
recognize_module_binding_names                                                                         1   0  --
recognize_mutex_inv_params                                                                             1   0  --
recognize_named_field_existence                                                                        1   0  --
recognize_noreturn_walk_stmts                                                                          1   0  --
recognize_pbexpr                                                                                       1   0  --
recognize_refs_bvar                                                                                    1   0  --
recognize_rewrite_ir_calls                                                                             1   0  --
recognize_scan_node_for_subscript_calls                                                                1   0  --
recognize_self_method_calls                                                                            1   0  E-
recognize_stmt_has                                                                                     1   0  --
recognize_stmt_noreturn_call                                                                           1   0  --
recognize_subclasses_of                                                                                1   0  --
recognize_subst_params                                                                                 1   0  --
recognize_substitute                                                                                   1   0  --
recognize_term_pp_wrapper                                                                              1   0  --
recognize_test_contains_map                                                                            1   0  --
recognize_type_str_reader                                                                              1   0  --
recognize_verify_module_groups                                                                         1   0  --
recognize_walk_dicts_bool_consumer                                                                     1   0  --
recognize_walk_dicts_generator                                                                         1   0  --
recognize_walk_dicts_set_consumer                                                                      1   0  --
recognize_walk_dicts_void_consumer                                                                     1   0  --
```

## CONFIRMED FALSE PROOFS (executed at base `b8bd00a9d`, full proof, rc=0 "Verification SUCCESS! All contracts formally proven.")
Each probe is a corpus control with its contract changed (`#@ ensures True` -> `#@ ensures False` unless noted):
0883 generic_fold `collect_written`; 0942 pyval_string_walker; 0943 pyval_list_walker; 0945 pyval_list_search `find`;
0948 pyval_flatten; 0945 `collect_leaf` + `#@ no_exception IndexError` (CPython raises); 0950 term fold; 0951 term transform;
0952 term_list_build; 0954 term_flatten_arrow; 0956 term_free_vars; 0958 term_string_pp; 0960 term_pp_methods (`App.pp`);
0962 crosscheck_selfstate_bool; 0964 crosscheck_term_method — 15 of 15 PROVED. Mirror-only families: the mirror
`ir_scanner.py` with `#@ ensures False` on six recognized methods (bool_existence, bool_lastelem, generic_fold, dictfold,
boolfold_isinstance, bool_multiway) emits a WhyML byte-identical to the unmodified file (the six claims vanish), and
`pycsl.py --fun irscanner__uses_arrayset --fun irscanner__ends_with_return --fun irscanner__has_direct_return` on it
prints `Verification SUCCESS` (rc=0, 1318 Valid, 0 other).
Call-site `requires`: 0945 with `#@ requires False` on the recognized callee `collect_leaf`, called by the recognized
`find` on a `("Leaf", ...)` tuple — PROVED at base (both groups emit `requires { true }`, so the call carries no
obligation). (A first variant, a GENERIC caller of the 0942 walker, is not constructible: the generic caller passes an
int-erased value to the pyval walker and Why3 rejects the file at base already.)
**16 confirmed false proofs + the mirror `--fun` one.**

## REPAIR (2026-10-26, rc1 executor off `42bc9c879`; code + witnesses + annotations §7.59 / translational §T.6.70 in commit `6b78012f9`)
**Design: ONE predicate, `generic_fold.bespoke_contract_ok(func, honours)`, enforced at the two places a bespoke lowering
can claim a function.** A recognizer may replace `func` only when the declared contract is what its emission establishes:
every `requires` / `ensures` clause the literal `True` unless the family is listed in `_RC420_HONOURS` as threading that
kind onto its top-level `let` as a checked obligation (`setfold`, `self_method_calls`, `stmt_setfold`,
`collect_escaping_exceptions`, `callee_implicit_exceptions`, `find_array_and_dict_vars`: ensures; `substmap`: ensures +
requires); every `raises` entry unconditioned (a pure permission); no `no_exception` / `no_exception \all`.
`\trusted` / `\abstract` functions are exempt (their contract is an assumption; dropping it only weakens callers).
  * `generic_fold.py` (not mirrored): a decorator is applied at module end to all 147 public `recognize_*`, so the
    preamble's needs / cluster / pair scans and the `_emit_function_block` dispatch see the SAME verdict. A single-function
    recognizer returns `None` for a non-conforming function. A multi-function recognizer (clusters, `*_pairs`,
    `term_pp_methods`) keeps its full-list result unless the result references (object, `id`, or name) a non-conforming
    function; then it is re-run on the conforming functions only. lv1's stricter `_term_contract_trivial` stays.
  * `functions.py::_emit_function_block` (not a mirrored method): the 24 `FunctionEmissionMixin`-local `_is_*` /
    `_recognize_*` branches are guarded inline by the same predicate (`_rc420_bare`), the six `_expr_bespoke_body` /
    `_emit_py_expr_compare_bespoke` scaffolds (gen #34 emits their requires + ensures) with both kinds honoured
    (`_rc420_spec`). No new `def` in a mirrored file.
A declined function goes to the generic lowering, which carries the contract or refuses / fails to type-check (for the
pyval / term shapes the generic lowering cannot model these values: an erased-value refusal or a Why3 type error). No
new refusal message, so no census message rows changed; the new witnesses' rows were appended with the tool.

Witnesses (expected FAIL; each PROVED at base `b8bd00a9d` as its probe, FAIL / REFUSED on the candidate): 5920 generic_fold,
5921 pyval_string_walker, 5922 pyval_list_walker, 5923 pyval_list_search, 5924 pyval_flatten, 5925 no_exception over a
raising `collect_leaf`, 5927 term fold, 5928 term_list_build, 5929 term_flatten_arrow, 5930 term_free_vars, 5931
term_string_pp, 5932 term_pp_methods (uncovered by lv1's gate), 5933 crosscheck_selfstate_bool, 5934
crosscheck_term_method (term transform: lv1's 5822); 5926 dropped callee `requires` (candidate: FAIL — a Why3 type
error in the generic lowering of the declined pair, not the precondition goal itself; fail-closed). Controls: the shape files they derive from (0883, 0942, 0943, 0945,
0948, 0950, 0951, 0952, 0954, 0956, 0958, 0960, 0962, 0964), byte-identical and still PROVED on the candidate.

Gates (candidate vs base worktree at `b8bd00a9d`; the candidate also carries lv1's `42bc9c879`):
  * fidelity: `check-self-annotate-sync.sh` rc=0 (929 verbatim, 0 drift), `self-annotate-mirror-check.sh` rc=0 (53 in sync).
  * corpus inertness (`byte-diff-sweep.sh` + `byte-diff-compare.py`, once per tree): root 2439 -> 2450 .mlw, 0 MOVED / 0 GONE /
    0 APPEARED (11 new sources: lv1's 5820/5821 + the witnesses that still emit); pyref 2186 -> 2186, 0/0/0. (5926 and the
    witness clause-strip below landed after the sweep: new files only, they cannot move another file's emission.)
  * mirror (`mirror-emit-sweep.sh`): 53/53, 0 MOVED / 0 GONE / 0 APPEARED -> no mirror moved, no OWED proof, no regression.
  * `pycsl_lib` --no-proof screen: 104 files identical to base (87 rc=0 / 17 rc=1; the 4 textual differences are the
    worktree path inside a refusal message).
  * witnesses: 15/15 PROVED at base (rc=0), FAIL / REFUSED on the candidate (rc=1); controls 14/14 PROVED on the candidate.
  * `run-soundness-planes.sh` (fast 61): 60 ok + `check-claim-vacuity` RED on the first run (the witnesses inherited the
    controls' helper `#@ requires True` / `#@ ensures True` lines: 1791 -> 1799 files). The ratchet is right (a `True`
    clause is a claim that cannot fail); the lines were deleted from the witnesses (default contract, semantics unchanged:
    emission identical at base for 14/15, the 15th re-proved) and the plane is OK (1791/6217). No axiom, ledger unchanged.
  * `\trusted` count unchanged (no stub touched).

Residuals (honest):
  * The predicate ignores `assigns`: a recognized emission is functional, so a declared frame is not checked against it and
    a body that MUTATES a parameter (0883's `collect_written` writes `written`) is modelled as pure. That is a fidelity
    question of the recognizer itself (route-#401 family), not of the dropped contract, and is not repaired here.
  * Class invariants: a recognized METHOD is not checked to preserve its class invariant (the recognized method shapes are
    pure readers today; not enforced by the predicate).
  * The honoured families lower the user's ensures through `_expr_to_whyml` against the BESPOKE representation (pyval,
    `map string bool`); a clause that means something different there is a translation-fidelity question (it fails closed
    when ill-typed), inherited from richer-contracts-bridge, not re-audited here.
  * Declining is fail-closed but not always useful: for most pyval / term shapes the generic lowering refuses (erased value)
    or Why3 rejects the file, so a user who writes a real contract on such a shape gets a refusal, not a proof.
  * `run-soundness-planes.sh` still files backlog #74 as "a CLAIM-REALITY ratchet, not a soundness one"; that comment is
    wrong (this route) but was left untouched (the plane's ratchets are unchanged by this repair).
