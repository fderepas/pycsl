# Tier-5 value-model-gap CENSUS — ranked feature→stubs map + bug-fix quick-wins

Executes menu option **A (CENSUS)** of the self-tcb-reduction Tier-5 track (SKILL §11). This is a
**measurement** deliverable: no feature was built, no `src/pycsl` or mirror file was permanently
edited (every probe reverted; `git status` clean; count held at **1240**). It goes DEEP on the V2
(collection-result) and V3 (emitter string/self-state/WhyML-gen) clusters and runs a CONFIRMING
sample of V1 (`Dict[str,Any]`), each under a **whole-body verbatim `--fun` proof** (§10.1 inviolable
rule). Branch `ghost-assign-bc6`, HEAD `0666ea6c`, date 2026-07-06.

It **supersedes the sub-classification-projection** in `whole-body-census.md §4` for these three
clusters with per-stub *whole-body* verdicts and a precise blocker for each.

---

## 0. Method — and a harness-integrity correction (read this first)

Per stub: `git checkout` the clean mirror file → blank the ONE `\trusted` line of the target →
`bin/sync-mirror-bodies.py <file>` (ports the **live body + real signature + real return type**
verbatim; siblings stay `\trusted` = `ensures True`) → `PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py
<mirror> --import-path src/pycsl --fun <qualname>` (default non-vacuity gate ON) → record → revert.

> **CRITICAL correction (recorded for honesty and for the next agent).** The first probe pass ran
> under the wrong interpreter (`libcst` absent), so `sync-mirror-bodies.py` **silently failed** and
> the mirror kept its **trivial stub bodies** (`return ""`, `return set()`). Those trivial bodies
> proved `ensures True` (and correctly failed an injected `ensures False`), yielding a *spurious*
> "≈72% convertible-NOW / V1 counterexample" that was **100% artifact**. The lesson: **always run
> the mirror toolchain under the project `.venv` (`source .venv/bin/activate`) and assert
> `sync … replaced N bodies` before trusting a verdict.** Every number below is from the **corrected**
> harness (venv active, real body verified — confirmed by re-inspecting the ported signature is
> `List[Dict[str, Any]]`, not the stub `List[int]`).

**"convertible-NOW"** = the whole ported live body reaches `Verification SUCCESS! All contracts
formally proven`. **Result: 0 of 98 probed stubs (V2 0/43, V3 0/13, V1 0/42) are convertible-NOW.**
The corrected data **matches `whole-body-census.md`** and **vindicates its "141 semantic-ceiling"
conclusion.** No emitter/feature commit landed between that census (`7a750917`, 11:33) and HEAD
(`0666ea6c`, 12:37) — only docs + the 9-stub PATH-1 harvest — so the two agree, as they must.

---

## 1. Headline counts

| bucket | probed | convertible-NOW | all-FAILED — dominant first-blocker |
|---|---:|---:|---|
| **V2 — collection-result** | 43 (full) | **0** | collection-RESULT element typing (`array int`↔`array string`↔scalar; `map`) |
| **V3 — emitter string/self-state/WhyML-gen** | 13 (full) | **0** | **8 WhyML-emission DEFECTS** + 4 string-vs-int + 1 proof-incomplete |
| **V1 — `Dict[str,Any]`** | 42 (sample of 85) | **0** | `int`↔`string` opaque-dict value-typing (B1) — **leave-trusted CONFIRMED** |

Non-vacuity gate was ON for every probe (the SUCCESS bar is real; here nothing cleared it).

---

## 2. The decisive structural finding — collection-result sits IN FRONT OF the B1 ceiling

The census tagged V2 (43) "the most promising cluster … tractable via a faithful-collection
feature." **The deep probe refutes that as a cluster win.** A static scan shows **40 of 43 V2 stubs
read a `Dict[str,Any]` internally** (`stmt.get("stmt")`, `func.get("contracts")`, `val.get("type")`
…). Their `array …`/`map …` type error is only the **first** blocker; behind it lies the **same B1
`Dict[str,Any]`→`int` wall that blocks V1**. So a faithful collection-RESULT feature would
whole-body-free **at most the 3 pure-collection stubs** (no dict read) — not 43. The three:
`_coerce_dotted_args`, `_emit_narrowing_vc`, `_split_tuple_type`-family string-list builders
(operate on `List[str]`, build `List[str]`, no `Dict[str,Any]` read).

This is the single most important measured fact in this census: **V2 is not a separable tractable
cluster; it is B1 with a collection-typed façade.**

---

## 3. Ranked feature F → #stubs it would WHOLE-BODY-FREE (measured, honest)

Because every probe FAILED, "F frees N" is a **first-blocker** classification (§10.1: a projection,
not a proven conversion — the body may hit a second blocker, and for V2 it demonstrably does: B1).
Ranked by honest whole-body yield, **not** by first-blocker headcount:

| feature F | first-blocker headcount | **honest whole-body yield** | bounded & buildable? |
|---|---:|---:|---|
| **F-B1 — faithful `Dict[str,Any]` value-typing** (`.get("k")` keeps the value's real type; string/kind dispatch works instead of collapsing to `int`) | ~119 (85 V1 + 30 sampled + 40 V2-behind + 4 V3) | large, but **unbounded** | **NO** — this is the "no-more-int" doctrine at scale; a research-grade modeling change + a co-landing certificate, **not** a Tier-5 feature |
| **F1 — faithful collection-RESULT element typing** (`list[str]`/`set[str]`/`dict` result: `array int`↔`array string`, scalar↔`array`, `map … option`) | 43 V2 + 7 V1(map-result) = **50** | **≤ 3** (only the pure-string-list builders; the other 47 hit B1 behind) | yes (extends WL-04/05 string/list work) — but yield ≤ 3, **fails the §10.7 value calculus** |
| **F-EMIT — fix the 8 WhyML-emission defects** (§4) | 8 V3 | **0–3** (unknown until fixed; some have B1/other behind, some — e.g. `_strip_outer_parens` — are pure and may prove) | yes, per-defect correctness fixes |
| **F-TUPLE — tuple-pattern bound as `seq`** (`_typed_local_vars`: `for k,v in items`) | 1 V2 | ≤ 1 | narrow |
| **F-ADT — IR-node/union reader** (`emit_ir` / `_union__…`: `_handle_binop`, `_symtype_to_whyml`, `_infer_return_value_type`, `_field_type_for`, `_static_width`) | 5 V1 | tier-3 ADT territory | **defer** — not a Tier-5 value feature |

**Single highest-fan-out BOUNDED buildable feature:** F1 (collection-result) by first-blocker
headcount (50) — **but its measured whole-body yield is ≤ 3**, so it does **not** justify a build.
There is **no** bounded feature with both high fan-out and high yield; the high-fan-out axis (B1) is
not a bounded feature.

---

## 4. Bug-fix quick-wins — the 8 V3 WhyML-emission defects (the ONE novel actionable output)

These stubs fail because the emitter produces **invalid WhyML** (Why3 rejects it) — an emission
**defect**, not a modelling gap. This is the only class where a fix is a *correctness* win rather
than a modelling change. Named precisely (verbatim Why3 error):

| file | stub | emission defect (verbatim) | note |
|---|---|---|---|
| statements.py | `_reset_function_state` | `syntax error` (emitted `.mlw` line 244) | malformed WhyML |
| statements.py | `_emit_first_assign` | `unbound function or predicate symbol 'py_val'` | undeclared symbol referenced |
| statements.py | `rec` (nested helper) | `unbound … 'iter_length'` | shared with `_emit_metatype_tags` |
| expressions.py | `_emit_metatype_tags` | `unbound … 'iter_length'` | **recurs** ⇒ one root cause, two stubs |
| expressions.py | `_call_named_builtins` | `unbound … 'func_name'` | |
| expressions.py | `_call_record_constructor` | `unbound … 'kwargs_map'` | |
| expressions.py | `_strip_outer_parens` | `unbound … 's'` | **pure str fn, NO B1 behind** ⇒ best fix-then-convert candidate |
| functions.py | `_emit_subtyping_goals` | `unbound exception symbol 'Return_seq_str'` | |

**Honest caveat (do NOT count these as guaranteed −1s):** each is an "unbound symbol / syntax" under
`--fun` emission. Two open questions per defect must be answered before claiming a −1: (a) is it a
genuine emitter defect or a `--fun`-isolation artifact (a symbol a trusted sibling would normally
declare)? (b) after the emission is fixed, does the *whole body* prove, or is B1/another blocker
behind it? Only `_strip_outer_parens` is known B1-free (pure string function), making it the single
best **fix-then-convert spike**. The recurring `iter_length` (2 stubs) is the best **root-cause**
lead (one fix, two stubs). Realistic clean-−1 yield from this class: **0–3**, needs a spike to know.

**Also near-convertible:** `_call_returns_string_collection` (V3) is the ONE stub that **typechecks
and emits valid WhyML** but leaves a proof goal unproven (`FAILED/INCOMPLETE`, no type/syntax error)
— the closest stub to convertible in the whole sample; worth a single invariant/timelimit spike.

---

## 5. Per-stub tables

### V2 — collection-result (43/43 FAILED; class = COLL-RESULT(F1) unless noted; †=reads `Dict[str,Any]` ⇒ B1 behind)

`array …` / `int↔array` first-blocker on: `_coerce_dotted_args`, `_emit_contract_logic_symbol†`,
`_handle_isinstance†`, `_handle_struct_call†`, `_is_emit_ir_expr†`, `_build_method_field_old_ensures_map†`,
`_build_method_field_param_frame_ensures_map†`, `_build_method_field_param_post_ensures_map†`,
`_build_method_field_param_result_ensures_map†`, `_build_method_field_result_ensures_map†`,
`_build_method_param_result_ensures_map†`, `_build_method_param_types_map†`,
`_build_method_param_whyml_types_by_name†`, `_build_method_result_ensures_map†`,
`_build_method_result_frame_ensures_map†`, `_build_method_writes_map†`, `_callable_whyml_arrow`,
`_compute_scope_sets†`, `_emit_contracts†`, `_emit_narrowing_vc`, `_first_tuple_return_elts†`,
`_has_dynamic_exec†`, `_mixin_dep_pseudo_functions†`, `_returns_string_seq†`, `_collect_mutations†`,
`find_array_and_dict_vars†`, `find_assigned_vars†`, `find_iteration_mutations†`, `find_lambda_vars†`,
`find_record_var_classes†`, `find_record_vars†`, `find_return_type†`, `has_early_return†`,
`_collect_field_decode_str_locals†`, `_collect_string_elem_read_locals†`, `_union_ctor_for_arm_tag†`,
`_collect_dict_var_assigns†`, `_collect_struct_pack_assign_targets†`, `_collect_struct_unpack_array_targets†`,
`_collect_tuple_array_locals†`, `_collect_tuple_var_assigns†`, `_split_tuple_type`.
**TUPLE-SEQ (n=1):** `_typed_local_vars` — `This pattern has type ('mu,'mu1), expected seq.Seq.seq`.

### V3 — emitter (13/13 FAILED)

EMIT-DEFECT (8): see §4. STRING-vs-INT / B1 (4): `_emit_frame_condition`, `_handle_dotted_call`,
`_resolve_dotted_signature`, `_param_type_str` (`string` where `int` expected — the same opaque-dict
value-typing wall, string side). PROOF-INCOMPLETE (1): `_call_returns_string_collection` (§4).

### V1 — `Dict[str,Any]` sample (42/42 FAILED) — leave-trusted CONFIRMED

- **DICT-B1 (30):** `int`↔`string` on `.get("type")`/`["…"]` string dispatch — the opaque-dict ceiling.
  `_handle_attribute_expr`, `_handle_call_expr`, `_coerce_to_int`, `_tag_of_value`, `_emit_function`,
  `_compute_return_type`, `_classify_iterable`, `_val_is_bool`, `_handle_dotted_call`, `_handle_len_call`,
  `_handle_sum_call`, `_handle_join_call`, `_is_string_expr`, `_is_float_expr`, `_subst_params`,
  `_linear_form`, `_match_pattern_cond`, `_to_bool`, `_typeddict_field_access`,
  `_namedtuple_positional_access`, `_build_param_list`, `_param_type_str`, `_parse_mixin_sig`,
  `_emit_array_local_reassign`, `_pattern_has_constructor`, `_render_match_pattern`, `_first_assign_kind`,
  `_rhs_yields_array`, `_resolve_effective_ghost_type`, (+`_classify_iterable` dup).
- **IRNODE-ADT (5):** `_handle_binop` (`emit_ir`), `_symtype_to_whyml`, `_infer_return_value_type`,
  `_field_type_for`, `_static_width` (`_union__…`) — tier-3 ADT/union readers, defer.
- **COLL-RESULT/map (7):** `_expr_to_whyml`, `_infer_tuple_slot_type`, `_refine_tuple_return_type`,
  `collect_user_exceptions`, `find_append_targets`, `uses_ghost_type`, `_stmts_to_whyml`
  (`… -> option.Option.option int` map-result — dict/set builders that fell in the V1 sample).

**V1 verdict: CONFIRMED leave-trusted.** 42/42 blocked; the dominant wall is the un-bounded B1
opaque-dict value-typing, with 5 IR-node-ADT and 7 map-result readers behind it. No counterexample
found (the apparent one in the first pass was the libcst harness artifact of §0).

---

## 6. Honest assessment & recommended next loop move

- **Convertible-with-a-bounded-feature:** essentially **none with worthwhile fan-out.** The only
  bounded feature with real headcount (F1 collection-result, 50 first-blockers) has a **measured
  whole-body yield of ≤ 3** because 40/43 V2 stubs hit B1 behind the collection façade (§2). F1 fails
  the §10.7 "value not count" calculus. F-TUPLE ≤ 1.
- **Bug-fix-now:** **8 WhyML-emission defects** (§4) are the one genuinely novel finding — real
  invalid-WhyML emission, not modelling. But they are **0–3 clean −1s**, not 8: each needs a spike to
  separate genuine-defect from `--fun`-isolation-artifact and to confirm the body proves after the
  fix. `_strip_outer_parens` (pure string, B1-free) + the recurring `iter_length` root cause (2
  stubs) are the best leads; `_call_returns_string_collection` is the one proof-only near-miss.
- **Leave-trusted (confirmed):** **V1 (~85)** on the un-bounded B1 `Dict[str,Any]` ceiling — the deep
  42-stub sample gives 42/42 blocked and **no counterexample**. Add the **40/43 V2** stubs that read
  `Dict[str,Any]` behind their collection façade → the *effective* leave-trusted set is **~125 of the
  141**, not 85.
- **The highest-fan-out feature to build first:** there isn't a good one. By raw first-blocker count
  it is F1; by honest whole-body yield **nothing bounded pays**. The only high-yield lever is F-B1,
  which is **not** a Tier-5 feature (unbounded modeling change + certificate).

**Recommendation — menu move D (STOP) for V1/V2, with a bounded exception spike, NOT B/C at scale.**
The census is vindicated: the Tier-5 frontier is the `Dict[str,Any]` semantic ceiling (B1),
collection-result sitting in front of that same ceiling, and a thin band of emission defects. **Do
not** open a collection-result feature build (measured yield ≤ 3). **Do** run one narrow, cheap
spike — the **8 V3 emission defects**, starting with `_strip_outer_parens` (B1-free) and the
`iter_length` root cause — because those are *correctness* fixes with a possible −1 tail. If the
spike converts ≥ 1 body it is a genuine (if small) win; if each hides B1, close the campaign at the
honest floor (count 1240) and record the ~125-stub B1 ceiling + the 5 IR-node-ADT readers as the
residual.
