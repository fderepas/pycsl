# Run #6 capability census (cv11)

Executor cv11, driver run #6, 2026-11-08/09. Tree `pycsl-cv11`, branch `run6-cv11` at 822621340 (= `ghost-assign-bc6` HEAD at
run #6 start). Census only: nothing was built, no `src/pycsl` file was edited, no whole-file proof was run. All emissions
ran `--no-proof --keep-mlw` (the Why3 type-check included, so `L3-TC` = a Why3 type error) on heavy.sh QUICK slot 3, one
probe per heavy.sh call, in scratch trees under `scratchpad/cv11/` (`st` = HEAD copy; `stlvb` = HEAD + the held lvB
lowering from `run5-lvB`; `stR1` = HEAD with lvG2's exemption removal 012547a1e reverse-applied, the stand-in for the
vm-irnode R1 narrowing view; `dr` = HEAD copy for the declaration planes).


Method (cv9's chain method). (1) Depth-0: for every governing `#@ \trusted` marker, the VERBATIM live body is ported into a
scratch copy of its mirror file (`bin/port-one-mirror-body.py --convert [--replace]`), emitted, and the first blocker is
classified with cv8's classifier (`scratchpad/cv11/classify11.py`) and diffed against cv8's row. (2) Chains: every
cv9/cv10 chain whose deepest probe had a patch spec was REPLAYED at HEAD (the same cumulative patch spec applied to the
HEAD port, `r9x*` / `r10x*` probes) to check that its terminal wall still stands; stubs with no prior chain, and rows whose
first blocker changed, were walked here (`specs_data.py`, kinds [R] equivalent rewrite / [T] mirror retype / [S] stand-in).
(3) Honesty read off the emitted `.mlw` at every TC-OK. (4) Set cover over COMPLETE (closed) chains: a stub counts for a
capability only if its whole chain is known and nothing else unbuilt remains. Raw data: `scratchpad/cv11/probe/`
(`results.tsv`, `<tag>.src.py/.log/.mlw/.patchlog`), `merged11.json` (one record per stub), `cover11.json`,
`lever_notes.md`.


## 0. Headline

- **Population.** `grep -rhF '#@ \trusted' src/self-annotate/src --include=*.py | wc -l` = 405 lines; 28 are prose
  (module docstrings / comments quoting the marker), **377 are governing markers**: 370 stubs + 7 nested closures of
  `\trusted` parents (`MERGED`, they convert with their parent). Run #5 start (cv8): 387 governing of 415.
- **Depth-0 at HEAD (all 377, verbatim live body, one QUICK emission each):** REFUSED 294, L3-TC 62, TC-OK 18, PORT-ABORT 3.
  Against cv8: **13 first blockers CHANGED** (`Module6_WhyMLTranspiler._emit_prefunctions_infra`, `Module6_WhyMLTranspiler._shared_use_lines`, `_ContractParser._parse_atom_bs`, `_ContractParser._parse_atom_name`, `_ContractParser._parse_quantifier`, `PyCSLToJSONEmitter.__init__`, `PyCSLToJSONEmitter._csl_list_to_ir`, `check_imports`, `_decode_string`, `ExpressionEmissionMixin._handle_attribute_expr`, `StatementEmissionMixin._seq_init_expr`, `_expand_anon_binders`, `_nat_to_int_with_sidecond`); 14 rows are new since cv8 (the 7 run #5
  re-trusts + the 7 nested closures now marked separately); every other row has cv8's first-blocker class (48 of them at
  a different site/message, same class). **No first blocker simply vanished into an honest TC-OK.** The TC-OK rows at
  depth 0 are the known facades (`_Parser.error/unsupported`, `_err`, `PyCSLError.__init__`, `iter_fields`,
  `_cache_root`, `_stub_set`, `stable_hash`, `_parse_args`, the generator `_sexp_tokens`), 6 of the 7 nested closures
  (vacuous: emitted as an opaque val with the parent), `PyCSLToJSONEmitter.__init__` (TC-OK but not emitted at all: its only allocation site is itself `\trusted`)
  and `_expand_anon_binders` (TC-OK now that lvA's `re` models landed; still needs `#@ \diverges` or a re.sub counting law).
- **Chains.** 192 prior cv9/cv10 chains were replayed at HEAD with their deepest patch spec: 184 reach the
  same terminal class, 6 moved (`PyCSLToJSONEmitter._collect_class_fields` (r9xs080_2: R: in-place receiver mutator -> R: R567-EMITIR-ATTR-ON-NONIR); `PyCSLToJSONEmitter._emit_namedtuple_record` (r9xs078_2: R: in-place receiver mutator -> R: R566-EMITIR-ITEM-STORE); `PyCSLToJSONEmitter._synthesize_namedtuple_functional` (r9xs079_2: R: in-place receiver mutator -> R: R567-EMITIR-ATTR-ON-NONIR); `PyCSLToJSONEmitter._synthesize_typeddict_functional` (r9xs077_2: R: in-place receiver mutator -> R: R567-EMITIR-ATTR-ON-NONIR); `ExpressionEmissionMixin._to_bool` (r10xh059_4: R: and/or used as a VALUE on non-bool operands (new since cv -> R: route #568); `StatementEmissionMixin._seq_init_expr` (r10xh098_4: L3-TC record/ADT vs emit_ir clash (non-int) -> R: route #568)); 2 cv10 chain(s) ran on a scratch emitter (st2) and are not comparable. Chain end states over the 377 rows: DEPTH-STOP 243, HONESTY-WALL 91, TC-OK-FACADE 11, TC-OK-PARTIAL 10, MERGED 7, TC-OK-HONEST 6, CERTIFIED-BOUNDARY 3, REFUSED-termination 3, DECL-FAIL 2, DECL-ONE-CAP 1.
- **Near misses (equivalent rewrites / mirror retypes only): NONE** (§1). The closest are one capability, one emitter
  fix or one user decision away (§1 table).
- **Ranking (§2, greedy over complete chains):** 1. cap-vm-irnode-R1-narrowing-view -> 6 stub(s), 2.5 h new proof; 2. cap-exception-payload-model -> 4 stub(s), 3.8 h new proof; 3. cap-diverges -> 1 stub(s), 0.2 h new proof; 4. decision-widen-15-frames -> 1 stub(s), 9.4 h new proof; 5. cap-none-default-map-param -> 1 stub(s), 0.0 h new proof; 6. cap-dependent-return-type -> 1 stub(s), 0.0 h new proof.
- **Levers (§4):** (i) `src/pycsl_lib` models: NOT usable (route #326 refuses them under `--import-path`; aliased in by a
  mirror import they are closed-world toys: `isfile` always False, `expanduser` identity, `Path.read_text -> int`; the
  os model itself is refused R489 when imported). (ii) R1 narrowing view: **6 conversions** (the #567 re-trusts, TC-OK in a
  stand-in tree); R1+R2+R3 together: 7; mutator lowering (lvB + self-field alias + exact pop + set()): 0 complete
  chains; str seam: 1 (`stable_hash`); genexp-sum: 0 (1 with 3 partners); method recursion / termination: 1, only via the `#@ \diverges`
  decision (`_expand_anon_binders`), +1 with a record-list model. (6) `declared_in`: 0 available as-is; `_expr_to_whyml` after one S emitter fix,
  `_track_collection_metadata` after widening 8 verified + 7 trusted frames.


## 1. Near misses (equivalent rewrites / mirror retypes only)

**None.** No stub reaches an honest TC-OK at HEAD with only [R] equivalent rewrites and [T] mirror retypes: every chain
that reaches TC-OK either leans on a stand-in for an unbuilt capability, is a facade, or needs a user decision. (Run #5's
four rewrite-only candidates, `_e`, `_resolve_dotted_signature`, `_handle_augassign_stmt`, `_emit_bitwise_or_power`, were
taken by lvI; the last one reverted at proof time, row 11 below.) The cheapest conversions, each ONE step away, with the
exact change:

| # | stub (file) | the one step | exact change measured | after it |
|---:|---|---|---|---|
| 1-6 | `PyCSLToJSONEmitter._collect_final_registry`, `_collect_type_params`, `_collect_typevar_registry`, `_const_int_value`, `_m5_get_type_name_legacy`, `_union_arm_tag` (Module5_IREmitter.py) | capability R1: the receiver-typed non-IR narrowing view (§4.2) | verbatim port; in `stR1` (lvG2's 012547a1e reverse-applied as the stand-in) all six are TC-OK (probes `s098_X1`, `s099_X1`, `s100_X1`, `s102_X1`, `s114_X1`, `s124_X1`); two of the mirror bodies were stubbed by lvG2 for the trusted-termination ratchet (`_collect_final_registry`, `_m5_get_type_name_legacy`), so their conversion also moves that ratchet back down | input-reading (`is_var elt` / `name_of elt`), proved whole-file before lvG2; one Module5 proof (~2.5 h) |
| 7 | `StatementEmissionMixin._expr_to_whyml` declaration (statements.py) | EMITTER fix `cap-none-default-map-param` (S) | declaration `subst: Optional[Dict[str, str]] = None` + `#@ declared_in module6_whyml/expressions.py::ExpressionEmissionMixin._expr_to_whyml` (probe `s298_D1`): L3-TC only at the callers that omit `subst` (`int` vs `string -> option string`) | a `declared_in` swap (counts as a conversion); statements.py proof (~9.4 h) |
| 8 | `_expand_anon_binders` (proof2why3/normalize.py) | user decision 3 of run #5 (`#@ \diverges`), or a counting law for `re.sub(count=1)` | verbatim port is TC-OK at HEAD (probe `s337_1`); the `while True` fixed point has no expressible variant | input-reading (`re_sub_callable_op` over `s`); normalize.py proof (~0.2 h) |
| 9 | `StatementEmissionMixin._track_collection_metadata` declaration (statements.py) | widen 15 frames (8 VERIFIED: a contract change the driver must approve) | `#@ assigns` + `self._rebound_collections`, `#@ declared_in module6_whyml/types.py::TypeInferenceMixin._track_collection_metadata`, field `_rebound_collections: Set[str] = None` declared on `StatementEmissionMixin` (probe `s307_D2`): TC-OK, conformance OK, underdeclaration HOLE-V +15 (§4.7) | statements.py proof (~9.4 h) |
| 10 | `_synthesize_legacy_text` (pycsl.py) | `cap-vm-unerase-list` for a `List[Dict[str, Any]]` (list-of-dict elements) | [R] `"\n\n".join(<genexp>)` -> `parts: List[str] = []` / `for r in records: parts.append(_synthesize_block(r))` / `return "\n\n".join(parts)`; [T] `records: List[Dict[str, Any]]` (probes `s375_2`, `s375_3`): the element is still `int` | input-reading as far as the trusted `_synthesize_block` val |
| 11 | `ExpressionEmissionMixin._emit_bitwise_or_power` (expressions.py) | `cap-ir-number-int-view` (proof-level: route #259's `py_pow y >= 0` needs an int view of the IR Number payload; lvI reverted it) | cv10's [R]/[T] links (replay `r10xh062_4` at HEAD: still TC-OK) | partial (child-IR guards havoc); expressions.py proof (~11 h) |
| 12 | `PyCSLToJSONEmitter.__init__` (Module5_IREmitter.py) | an EMITTED allocation site (its only one, `Module5_IREmitter.generate_json`, is itself `\trusted`, DEPTH-STOP name rebinding) | verbatim port TC-OK at depth 0 (`s094_1`) but no `let` is emitted for the constructor: converting it alone is vacuous | n/a until an allocation is verified |


## 2. Capability ranking (set cover over COMPLETE chains)

**How to read.** A capability (or a bundle of 2-3 that only pay off together) is credited with a stub only when the stub's
chain is CLOSED (TC-OK reached with stand-ins, or an identified honesty wall) and everything else the chain needs is either
free (an equivalent rewrite / a mirror retype) or built at an EARLIER step. DEPTH-STOP chains (a further wall that could not
be simulated) are never credited. The ranking is greedy on
`score = stubs x risk factor / (new whole-file proof hours + build hours)`, risk factor low 1 / med 0.7 / high 0.4, build
hours S 4, S-M 8, M 16, M-L 24, L 40, XL 80 (capability sizes and risks: cv9/cv10 `capmeta`, cv11 additions in
`cover11.py::EXTRA`). Proof hours are the last measured whole-file times (run #5 driver proofs, `scratchpad/run5/*-proofs.txt`:
expressions 11.3, statements 9.4, stmt_control_flow 5.0, pure_ast 3.0, Module5 2.5, core_ir_semantic 1.8, functions 1.6,
Transpiler 1.0, pycsl 0.5, Module2 0.5, ir_resolve 0.45, identifiers 0.33, struct_format 0.14, Module3 0.12 h); unmeasured
small files are costed 0.25 h (`est.`). A capability that changes the EMITTER also owes the mirror sweep and the moved
mirror files' proofs; the column counts only the home files of the completed stubs.

### 2a. Greedy ranking (each row assumes the rows above it are built)

| step | capability (bundle) built at this step | stubs it completes (TC-OK + honest, given the earlier steps) | home files to prove + hours (not yet paid by an earlier step) | risk | build estimate | score |
|---:|---|---|---|---|---|---:|
| 1 | `cap-vm-irnode-R1-narrowing-view` | 6: `PyCSLToJSONEmitter._collect_final_registry` (Module5_IREmitter.py; TC-OK-HONEST)<br>`PyCSLToJSONEmitter._collect_type_params` (Module5_IREmitter.py; TC-OK-HONEST)<br>`PyCSLToJSONEmitter._collect_typevar_registry` (Module5_IREmitter.py; TC-OK-HONEST)<br>`PyCSLToJSONEmitter._const_int_value` (Module5_IREmitter.py; TC-OK-HONEST)<br>`PyCSLToJSONEmitter._m5_get_type_name_legacy` (Module5_IREmitter.py; TC-OK-HONEST)<br>`PyCSLToJSONEmitter._union_arm_tag` (Module5_IREmitter.py; TC-OK-HONEST) | frontend/Module5_IREmitter.py 2.5 h (new: 2.50 h) | med (the rejected file-path exemption, re-done per receiver) | M (~16 h) | 0.227 |
| 2 | `cap-exception-payload-model` | 4: `PyCSLError.__init__` (errors.py; TC-OK-FACADE)<br>`_ContractParser._err` (Module2_Parser.py; TC-OK-FACADE)<br>`_Parser.error` (pure_ast.py; TC-OK-FACADE)<br>`_Parser.unsupported` (pure_ast.py; TC-OK-FACADE) | errors.py 0.25 h est., frontend/Module2_Parser.py 0.5 h, frontend/pure_ast.py 3 h (new: 3.75 h) | low | M (~16 h) | 0.203 |
| 3 | `cap-diverges` | 1: `_expand_anon_binders` (normalize.py; REFUSED-termination) | proof2why3/normalize.py 0.19 h (new: 0.19 h) | med (a decision, run #5 item 3) | S (~4 h) | 0.167 |
| 4 | `decision-widen-15-frames` | 1: `StatementEmissionMixin._track_collection_metadata` (statements.py; DECL-FAIL) | module6_whyml/statements.py 9.4 h (new: 9.40 h) | low (a truthful frame; 8 verified contracts change) | S (~4 h) | 0.075 |
| 5 | `cap-none-default-map-param` | 1: `StatementEmissionMixin._expr_to_whyml` (statements.py; DECL-ONE-CAP) | module6_whyml/statements.py 9.4 h (new: 0.00 h) | low | S (~4 h) | 0.250 |
| 6 | `cap-dependent-return-type` | 1: `_decode_fstring_middle` (pure_ast.py; TC-OK-PARTIAL) | frontend/pure_ast.py 3 h (new: 0.00 h) | med | M (~16 h) | 0.044 |
| 7 | `cap-faithful-string-hash` | 1: `stable_hash` (identifiers.py; TC-OK-FACADE) | module6_whyml/identifiers.py 0.33 h (new: 0.33 h) | med | M (~16 h) | 0.043 |
| 8 | `cap-R325-call-complex`<br>`cap-R325-call-str-to-number` | 1: `_parse_number` (pure_ast.py; HONESTY-WALL) | frontend/pure_ast.py 3 h (new: 0.00 h) | med; low | M, S (~20 h) | 0.035 |
| 9 | `cap-re-match-model`<br>`cap-return-exn-nonint` | 1: `_rewrite_annotation_str` (monomorphize.py; HONESTY-WALL) | frontend/monomorphize.py 0.25 h est. (new: 0.25 h) | low-med; med | S, M (~20 h) | 0.035 |
| 10 | `cap-pair-unroll` | 1: `_match_block_hdr` (Module1_Ingestor.py; TC-OK-FACADE) | frontend/Module1_Ingestor.py 0.25 h est. (new: 0.25 h) | low | S (~4 h) | 0.235 |
| 11 | `cap-trusted-val-unit-return`<br>`cap-vm-unerase-tuple` | 3: `_ContractParser._parse_inductive` (Module2_Parser.py; TC-OK-PARTIAL)<br>`_ContractParser._parse_inductive_rules` (Module2_Parser.py; TC-OK-PARTIAL)<br>`parse_format` (struct_format.py; HONESTY-WALL) | frontend/Module2_Parser.py 0.5 h, module6_whyml/struct_format.py 0.14 h (new: 0.14 h) | high; low | L, S (~44 h) | 0.027 |
| 12 | `cap-R325-call-subprocess`<br>`cap-closure-lift`<br>`cap-context-manager-model` | 7: `_coqc_version` (audit_proof_reverify.py; HONESTY-WALL)<br>`_lean_version` (audit_proof_reverify.py; HONESTY-WALL)<br>`extract_lean_statements` (extract.py; HONESTY-WALL)<br>`extract_rocq_statements` (extract.py; HONESTY-WALL)<br>`_dispatch_provers` (pycsl.py; HONESTY-WALL)<br>`_run_vacuity_gate` (pycsl.py; HONESTY-WALL)<br>`_why3_typecheck` (pycsl.py; HONESTY-WALL) | audit_proof_reverify.py 0.25 h est., proof2why3/extract.py 0.25 h est., pycsl.py 0.5 h (new: 1.00 h) | high; med; med | XL, M, M (~112 h) | 0.025 |
| 13 | `cap-R325-call-pathlib` | 1: `SertopSession.type_of_batch` (sertop.py; HONESTY-WALL) | proof2why3/sertop.py 0.25 h est. (new: 0.25 h) | low (law-free val; honesty still needs FS) | S (~4 h) | 0.235 |
| 14 | `cap-argparse-model` | 2: `_parse_args` (pycsl.py; TC-OK-FACADE)<br>`_run_proofs` (pycsl.py; HONESTY-WALL) | pycsl.py 0.5 h (new: 0.00 h) | low | L (~40 h) | 0.050 |

### 2b. Where the capabilities sit (how many chains need each; the closed chains it is the last piece of)

| capability | on chains of | closed chains it is the ONLY missing piece of | DEPTH-STOP chains where it is the only KNOWN remaining wall (next wall unknown) | family / size / risk |
|---|---:|---|---:|---|
| `cap-vm-unerase-irnode` | 56 | 0 | 6 | VMSEAM / XL / high |
| `cap-fs-path-model` | 30 | 1: `_cache_root` | 0 | EXTERNAL / XL / high |
| `cap-method-recursion-cycle` | 28 | 0 | 1 | CONTROL / L / high (termination) |
| `cap-vm-unerase-list` | 26 | 0 | 5 | VMSEAM / XL / high |
| `cap-vm-unerase-dict` | 25 | 0 | 5 | VMSEAM / XL / high |
| `cap-pyast-node-typing` | 21 | 0 | 2 | PYAST / L / med-high |
| `cap-R325-call-subprocess` | 20 | 3: `_coqc_version`, `_lean_version`, `_why3_typecheck` | 0 | EXTERNAL / XL / high |
| `cap-context-manager-model` | 19 | 0 | 1 | CONTROL / M / med |
| `cap-self-field-alias-analysis` | 18 | 0 | 0 | MUTATOR / L / high |
| `cap-vm-unerase-tuple` | 16 | 1: `_ContractParser._parse_inductive_rules` | 0 | VMSEAM / L / high |
| `cap-closure-lift` | 16 | 0 | 0 | CONTROL / M / med |
| `cap-vm-unerase-union` | 14 | 0 | 2 | VMSEAM / L / high |
| `cap-erased-to-builtin-slot-arg` | 13 | 0 | 0 | VMSEAM / M / high (typing the upstream value is the real fix) |
| `cap-inplace-mutator-fresh-local` | 12 | 0 | 0 | MUTATOR / M (built) / med |
| `cap-vm-irnode-R1-narrowing-view` | 11 | 6: `PyCSLToJSONEmitter._collect_final_registry`, `PyCSLToJSONEmitter._collect_type_params`, `PyCSLToJSONEmitter._collect_typevar_registry`, `PyCSLToJSONEmitter._const_int_value`, `PyCSLToJSONEmitter._m5_get_type_name_legacy`, `PyCSLToJSONEmitter._union_arm_tag` | 0 | VMSEAM / M / med (the rejected file-path exemption, re-done per receiver) |
| `cap-effectful-callback` | 11 | 0 | 0 | CONTROL / XL / high |
| `cap-exact-pop-model` | 10 | 0 | 1 | MUTATOR / M / med |
| `cap-re-match-model` | 10 | 0 | 1 | RE / M / med |
| `cap-inplace-mutator-computed-receiver` | 10 | 0 | 2 | MUTATOR / L / high |
| `cap-pyast-node-attr-writeback` | 10 | 0 | 0 | PYAST / L / high (node aliasing) |
| `cap-identity-vs-literal` | 10 | 0 | 2 | CONTROL / M / med |
| `cap-binder-hygiene-R327` | 10 | 0 | 1 | DEFECT / S (live rename) / low |
| `cap-method-arg-frame` | 10 | 0 | 2 | MUTATOR / M / med |
| `cap-field-collection-writeback` | 9 | 0 | 0 | MUTATOR / L / high |
| `cap-R325-call-set-ctor` | 9 | 0 | 0 | VMSEAM / S-M / low |
| `cap-getattr-dynamic` | 9 | 0 | 0 | PYAST / M / high |
| `cap-hash-judge-class-set` | 9 | 0 | 1 | VMSEAM / M / med |
| `cap-dict-alias` | 9 | 0 | 4 | MUTATOR / M / med |
| `cap-R325-call-str-split` | 8 | 0 | 0 | RE / S-M / low |
| `cap-inplace-mutator-pop` | 8 | 0 | 1 | MUTATOR / M / med |


## 3. Per-stub chain table

One row per governing marker (377; the 7 nested closures of `\trusted` parents are `MERGED`: they are emitted as an opaque
`val` with their parent and convert only with it, so their depth-0 TC-OK is vacuous). Columns: **first blocker (HEAD)** =
the depth-0 class and capability id (`remote:<fn>` when the refusal names another function); **changed** = the class
differs from cv8's row (run #5 start; cv9/cv10 re-measured the hot and non-hot rows on int36/int40 with the same
classes); **links** = patched links of the chain used (source in brackets: cv11 = walked here, cv9 / cv10 / lvA-lvH =
reused) plus the replay verdict at HEAD; **terminal** = the end state and every capability still needed (LIVE-REFACTOR /
MIRROR-RETYPE links are free and omitted); **TC-OK?** = the chain reaches a Why3-type-checking emission (with its
stand-ins); **honest?** = the honesty read at that TC-OK.


| stub | file | first blocker (HEAD) | changed since run #5? | links | terminal | TC-OK? | honest? |
|---|---|---|---|---|---|---|---|
| `Module6_WhyMLTranspiler._build_callee_no_exception_summary` | Module6_WhyMLTranspiler.py | R: R325 opaque-int fallback `cap-R325-dict-values` | no | 1 (cv10; replay r10xh122_2: same terminal) | DEPTH-STOP: cap-R325-nonint-dict-value-field, cap-vm-unerase-irnode | no | - |
| `Module6_WhyMLTranspiler._compute_shared_module_maps` | Module6_WhyMLTranspiler.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 1 (cv10; replay r10xh127_2: same terminal) | DEPTH-STOP: cap-vm-unerase-irnode | no | - |
| `Module6_WhyMLTranspiler._emit_prefunctions_infra` | Module6_WhyMLTranspiler.py | R: element store through non-list value `cap-elem-store-nonlist` | **yes** (cv8: R: R325 opaque-int fallback) | 0 (cv11) | DEPTH-STOP: cap-vm-unerase-dict | no | - |
| `Module6_WhyMLTranspiler._maybe_emit_no_exception_assert` | Module6_WhyMLTranspiler.py | R: in-place receiver mutator `cap-inplace-mutator-update` | no | 2 (cv10; replay r10xh125_3: same terminal) | DEPTH-STOP: cap-mirror-field-decl, cap-vm-unerase-set | no | - |
| `Module6_WhyMLTranspiler._render_callee_condition` | Module6_WhyMLTranspiler.py | R: in-place receiver mutator `cap-inplace-mutator-pop` | no | 2 (lvH(reused)) | DEPTH-STOP: cap-exact-pop-model, cap-exception-hierarchy-model, cap-self-field-alias-analysis | no | - |
| `Module6_WhyMLTranspiler._shared_use_lines` | Module6_WhyMLTranspiler.py | R: element store through non-list value `cap-elem-store-nonlist` | **yes** (cv8: L3-TC int-erasure type seam) | 0 (cv11) | DEPTH-STOP: cap-vm-unerase-dict | no | - |
| `Module6_WhyMLTranspiler._sig_val_from_let` | Module6_WhyMLTranspiler.py | R: parameter rebinding in a nested block `cap-param-rebind-nested` | no | 3 (cv10; replay r10xh129_4: same terminal) | DEPTH-STOP: cap-vm-unerase-list | no | - |
| `Module6_WhyMLTranspiler._sig_val_from_let._hdr_name` | Module6_WhyMLTranspiler.py | TC-OK `none-TC-OK` | new stub | 0 (cv11) | MERGED: - | no | (with parent) |
| `Module6_WhyMLTranspiler._transpile_modular` | Module6_WhyMLTranspiler.py | R: function/class name rebound (setattr / namespace dict wri `cap-name-rebinding-model` | no | 0 (cv10) | DEPTH-STOP: cap-import-system-local-module | no | - |
| `Module6_WhyMLTranspiler._transpile_modular._emit_funcs` | Module6_WhyMLTranspiler.py | TC-OK `none-TC-OK` | new stub | 0 (cv11) | MERGED: - | no | (with parent) |
| `Module6_WhyMLTranspiler._wrap_call_with_callee_raises_assert` | Module6_WhyMLTranspiler.py | R: in-place receiver mutator `cap-inplace-mutator-update` | no | 2 (cv10; replay r10xh123_3: same terminal) | DEPTH-STOP: cap-vm-unerase-irnode | no | - |
| `Module6_WhyMLTranspiler.transpile` | Module6_WhyMLTranspiler.py | R: global / module-scope write `cap-global-nonlocal-write` | no | 1 (cv10; replay r10xh126_2: same terminal) | DEPTH-STOP: cap-import-system-local-module | no | - |
| `_audit_one_prover` | audit_proof.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 1 (cv9; replay r9xs003_2: same terminal) | HONESTY-WALL: cap-R325-call-subprocess, cap-erased-to-builtin-slot-arg, cap-field-collection-writeback, cap-fs-path-model | no | no (honesty wall) |
| `_extract_directives` | audit_proof.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 4 (cv9; replay r9xs001_5: same terminal) | DEPTH-STOP: cap-R325-call-pathlib, cap-R325-call-str-split, cap-vm-unerase-list | no | - |
| `_index_proofs_dir` | audit_proof.py | R: exception object read (route #233) `cap-exception-object-read` | no | 2 (cv9; replay r9xs002_3: same terminal) | HONESTY-WALL: cap-exception-object-read, cap-fs-path-model, cap-return-exn-nonint | no | no (honesty wall) |
| `_index_proofs_dir_by_file` | audit_proof.py | R: in-place receiver mutator `cap-inplace-mutator-setdefault` | no | 4 (lvB) | DEPTH-STOP: cap-fs-path-model, cap-inplace-mutator-fresh-local, cap-inplace-mutator-setdefault, cap-set-iteration | no | - |
| `_parse_lean_file` | audit_proof.py | R: in-place receiver mutator `cap-inplace-mutator-extend` | no | 4 (lvB) | DEPTH-STOP: cap-R325-call-str-split, cap-exact-pop-model, cap-fs-path-model, cap-inplace-mutator-extend | no | - |
| `_parse_rocq_file` | audit_proof.py | R: in-place receiver mutator `cap-inplace-mutator-pop` | no | 4 (lvB) | DEPTH-STOP: cap-R325-call-str-split, cap-exact-pop-model, cap-fs-path-model, cap-inplace-mutator-pop | no | - |
| `ReverifyReport.summary` | audit_proof_reverify.py | L3-TC int-erasure type seam `cap-vm-unerase-scalar` | no | 3 (cv9; replay r9xs004_4: same terminal) | TC-OK-PARTIAL: cap-float-str, cap-fstring-float-format, cap-genexp-sum, cap-vm-unerase-list | yes | partial |
| `_cache_key` | audit_proof_reverify.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 2 (cv9; replay r9xs006_3: same terminal) | HONESTY-WALL: cap-R325-str-encoding-op, cap-fs-path-model, cap-hashlib-model, cap-sorted-str-list, cap-str-join-array | no | no (honesty wall) |
| `_cache_load` | audit_proof_reverify.py | L3-TC int-erasure type seam `cap-vm-unerase-union` | no | 0 (cv9) | HONESTY-WALL: cap-fs-path-model, cap-json-model | no | no (honesty wall) |
| `_cache_root` | audit_proof_reverify.py | TC-OK `none-TC-OK` | no | 0 (cv9) | TC-OK-FACADE: cap-fs-path-model | yes | FACADE |
| `_cache_store` | audit_proof_reverify.py | L3-TC int-erasure type seam `cap-vm-unerase-dict` | no | 0 (cv9) | HONESTY-WALL: cap-fs-path-model, cap-json-model | no | no (honesty wall) |
| `_coqc_version` | audit_proof_reverify.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 0 (cv9) | HONESTY-WALL: cap-R325-call-subprocess | no | no (honesty wall) |
| `_lean_version` | audit_proof_reverify.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 0 (cv9) | HONESTY-WALL: cap-R325-call-subprocess | no | no (honesty wall) |
| `_sha256_file` | audit_proof_reverify.py | R: in-place receiver mutator `cap-inplace-mutator-update` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-fresh-local, cap-inplace-mutator-update | no | - |
| `_to_cache_payload` | audit_proof_reverify.py | L3-TC int-erasure type seam `cap-vm-unerase-str` | no | 0 (cv11) | DEPTH-STOP: cap-vm-unerase-dict, cap-vm-unerase-list | no | - |
| `verify_lean_file` | audit_proof_reverify.py | R: definite-assignment (read of a not-definitely-assigned lo `cap-definite-assignment-flow` | no | 2 (cv9; replay r9xs012_3: same terminal) | HONESTY-WALL: cap-R325-call-subprocess, cap-context-manager-model, cap-fs-path-model, cap-sorted-key | no | no (honesty wall) |
| `verify_rocq_file` | audit_proof_reverify.py | R: definite-assignment (read of a not-definitely-assigned lo `cap-definite-assignment-flow` | no | 2 (cv9; replay r9xs011_3: same terminal) | HONESTY-WALL: cap-R325-call-subprocess, cap-context-manager-model, cap-fs-path-model, cap-heterogeneous-list | no | no (honesty wall) |
| `_namedtuple_check_call` | core_ir_semantic.py | L3-TC int-erasure type seam `cap-vm-unerase-dict` | no | 2 (cv9; replay r9xs016_3: same terminal) | DEPTH-STOP: cap-vm-unerase-dict, cap-vm-unerase-irnode | no | - |
| `_returns_literal_none` | core_ir_semantic.py | R: nested closure lift `cap-closure-lift` (remote:walk) | no | 2 (cv9; replay r9xs014_3: same terminal) | DEPTH-STOP: cap-r325-typepos | no | - |
| `_returns_literal_none.walk` | core_ir_semantic.py | TC-OK `none-TC-OK` | new stub | 0 (cv11) | MERGED: - | no | (with parent) |
| `run_ir_semantic_checks` | core_ir_semantic.py | R: R325 opaque-int fallback `cap-R325-call-set-ctor` (remote:_lemma_calls_trusted) | no | 3 (cv9; replay r9xs013_4: same terminal) | DEPTH-STOP: cap-R325-call-set-ctor, cap-vm-unerase-irnode | no | - |
| `PyCSLError.__init__` | errors.py | TC-OK `none-TC-OK` | no | 0 (cv9) | TC-OK-FACADE: cap-exception-payload-model | yes | FACADE |
| `bases_closure` | exception_model.py | R: in-place receiver mutator `cap-inplace-mutator-pop` | no | 3 (lvB) | CERTIFIED-BOUNDARY: cap-diverges, cap-exact-pop-model, cap-inplace-mutator-pop | no | - |
| `ConcurrencyChecker._check_function` | frontend/ConcurrencyChecker.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 3 (cv9; replay r9xs018_4: same terminal) | DEPTH-STOP: cap-R325-call-set-ctor, cap-R325-nonint-field, cap-pyast-node-typing, cap-stdlib-ast-model, cap-vm-unerase-dict | no | - |
| `ConcurrencyChecker._walk_stmt` | frontend/ConcurrencyChecker.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 3 (cv9; replay r9xs019_4: same terminal) | TC-OK-PARTIAL: cap-erased-to-builtin-slot-arg, cap-method-recursion-cycle, cap-pyast-node-typing, cap-stdlib-ast-model | yes | partial |
| `ConcurrencyChecker.check` | frontend/ConcurrencyChecker.py | R: in-place receiver mutator `cap-inplace-mutator-add` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-add, cap-self-field-alias-analysis | no | - |
| `Module1_Ingestor.process` | frontend/Module1_Ingestor.py | R: getattr non-literal default (route #309) `cap-getattr-dynamic` | no | 3 (cv9; replay r9xs021_4: same terminal) | DEPTH-STOP: cap-getattr-dynamic, cap-inplace-mutator-sort, cap-pyast-node-typing, cap-sorted-key | no | - |
| `_Harvester._assign` | frontend/Module1_Ingestor.py | R: hash of unknown/unhashable class `cap-hash-judge-class-set` | no | 3 (cv9; replay r9xs024_4: same terminal) | DEPTH-STOP: cap-R325-nonint-field, cap-field-collection-writeback, cap-hash-judge-class-set | no | - |
| `_Harvester._build` | frontend/Module1_Ingestor.py | R: field-collection append without write-back `cap-field-collection-writeback` | no | 3 (cv9; replay r9xs023_4: same terminal) | DEPTH-STOP: cap-field-collection-writeback, cap-method-recursion-cycle, cap-vm-unerase-tuple | no | - |
| `_Harvester._emit_suite` | frontend/Module1_Ingestor.py | R: recursion cycle through a METHOD/constructor call `cap-method-recursion-cycle` | no | 1 (cv9; replay r9xs027_2: same terminal) | TC-OK-PARTIAL: cap-method-recursion-cycle, cap-vm-unerase-list | yes | partial |
| `_Harvester._fold_blocks` | frontend/Module1_Ingestor.py | R: tuple-unpack alias `cap-tuple-unpack-alias` | no | 4 (cv9; replay r9xs026_5: same terminal) | DEPTH-STOP: cap-R325-str-encoding-op, cap-str-join-array, cap-trusted-val-unit-return, cap-vm-unerase-tuple | no | - |
| `_Harvester._make` | frontend/Module1_Ingestor.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 2 (cv9; replay r9xs022_3: same terminal) | DEPTH-STOP: cap-pyast-node-typing | no | - |
| `_Harvester._normalize_leading` | frontend/Module1_Ingestor.py | L3-TC unbound symbol emitted (emitter defect) `cap-emit-unbound-symbol-defect` | no | 5 (cv9; replay r9xs025_6: same terminal) | DEPTH-STOP: cap-any-genexp-callee-order, cap-trusted-val-unit-return, cap-vm-unerase-union | no | - |
| `_match_block_hdr` | frontend/Module1_Ingestor.py | L3-TC int-erasure type seam `cap-vm-unerase-tuple` | no | 1 (cv9; replay r9xs020_2: same terminal) | TC-OK-FACADE: cap-pair-unroll, cap-re-match-model | yes | FACADE |
| `Module2_Parser.parse_contract` | frontend/Module2_Parser.py | R: in-place receiver mutator `cap-inplace-mutator-computed-receiver` | no | 1 (lvB) | DEPTH-STOP: cap-inplace-mutator-computed-receiver | no | - |
| `_ContractParser.__init__` | frontend/Module2_Parser.py | R: class-invariant ctor obligation (route #226) `cap-ctor-invariant-obligation` | no | 2 (cv9; replay r9xs028_3: same terminal) | DEPTH-STOP: cap-ctor-invariant-obligation, cap-vm-unerase-tuple | no | - |
| `_ContractParser._err` | frontend/Module2_Parser.py | TC-OK `none-TC-OK` | no | 0 (cv9) | TC-OK-FACADE: cap-exception-payload-model | yes | FACADE |
| `_ContractParser._grab_reviewer_id` | frontend/Module2_Parser.py | R: R325 opaque-int fallback `cap-R325-call-re` (remote:_contractparser___parse_trusted) | no | 3 (lvC) | DEPTH-STOP: cap-re-match-model, cap-vm-unerase-str, cap-vm-unerase-union | no | - |
| `_ContractParser._parse_act_block` | frontend/Module2_Parser.py | L3-TC int-erasure type seam `cap-vm-unerase-irnode` | no | 1 (cv9; replay r9xs034_2: same terminal) | DEPTH-STOP: cap-heterogeneous-list, cap-vm-unerase-irnode | no | - |
| `_ContractParser._parse_assigns` | frontend/Module2_Parser.py | R: R551-CONSTRUCTOR-ARGUMENT-KIND `cap-kind-judge-list-arg` | no | 1 (cv9; replay r9xs032_2: same terminal) | DEPTH-STOP: cap-heterogeneous-list, cap-kind-judge-list-arg, cap-vm-unerase-list | no | - |
| `_ContractParser._parse_assigns_target` | frontend/Module2_Parser.py | R: heterogeneous list literal `cap-heterogeneous-list` | no | 1 (cv9; replay r9xs033_2: same terminal) | HONESTY-WALL: cap-heterogeneous-list, cap-trusted-val-unit-return, cap-vm-callable-value | no | no (honesty wall) |
| `_ContractParser._parse_atom_bs` | frontend/Module2_Parser.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | **yes** (cv8: R: R551-CONSTRUCTOR-ARGUMENT-KIND) | 1 (cv9; replay r9xs043_2: same terminal) | DEPTH-STOP: cap-kind-judge-list-arg, cap-vm-unerase-irnode | no | - |
| `_ContractParser._parse_atom_name` | frontend/Module2_Parser.py | R: R325 opaque-int fallback `cap-R325-call-re` | **yes** (cv8: R: R551-CONSTRUCTOR-ARGUMENT-KIND) | 1 (cv9; replay r9xs042_2: same terminal) | DEPTH-STOP: cap-kind-judge-list-arg, cap-vm-callable-value, cap-vm-unerase-irnode | no | - |
| `_ContractParser._parse_atom_primary` | frontend/Module2_Parser.py | R: except reachable by unmodelled exception (route #174, new `cap-exception-hierarchy-model` | no | 1 (cv9; replay r9xs041_2: same terminal) | DEPTH-STOP: cap-exception-hierarchy-model, cap-vm-unerase-irnode | no | - |
| `_ContractParser._parse_contract` | frontend/Module2_Parser.py | R: R325 opaque-int fallback `cap-R325-call-re` | no | 1 (lvC) | DEPTH-STOP: cap-re-match-model | no | - |
| `_ContractParser._parse_datatype` | frontend/Module2_Parser.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv9; replay r9xs037_2: same terminal) | DEPTH-STOP: cap-vm-unerase-list | no | - |
| `_ContractParser._parse_happy` | frontend/Module2_Parser.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv9; replay r9xs035_2: same terminal) | DEPTH-STOP: cap-vm-unerase-union | no | - |
| `_ContractParser._parse_happy_targets` | frontend/Module2_Parser.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 1 (cv9; replay r9xs036_2: same terminal) | DEPTH-STOP: cap-erased-to-builtin-slot-arg, cap-vm-unerase-union | no | - |
| `_ContractParser._parse_inductive` | frontend/Module2_Parser.py | R: R551-CONSTRUCTOR-ARGUMENT-KIND `cap-kind-judge-list-arg` | no | 4 (cv9; replay r9xs039_6: same terminal) | TC-OK-PARTIAL: cap-trusted-val-unit-return, cap-vm-unerase-tuple | yes | partial |
| `_ContractParser._parse_inductive_rules` | frontend/Module2_Parser.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv9; replay r9xs040_2: same terminal) | TC-OK-PARTIAL: cap-vm-unerase-tuple | yes | partial |
| `_ContractParser._parse_quantifier` | frontend/Module2_Parser.py | R: R567-EMITIR-ATTR-ON-NONIR `cap-vm-irnode-R1-narrowing-view` | **yes** (cv8: R: R325 opaque-int fallback) | 0 (cv11) | DEPTH-STOP: cap-vm-irnode-R1-record-arm, cap-vm-callable-value, cap-vm-unerase-union | no | - |
| `_ContractParser._parse_variant_def` | frontend/Module2_Parser.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 2 (cv9; replay r9xs038_4: same terminal) | DEPTH-STOP: cap-vm-unerase-list | no | - |
| `_ContractParser._try` | frontend/Module2_Parser.py | R: hash of unknown/unhashable class `cap-hash-judge-class-set` | no | 1 (cv9; replay r9xs030_2: same terminal) | HONESTY-WALL: cap-hash-judge-class-set, cap-vm-callable-value | no | no (honesty wall) |
| `_lex_contract` | frontend/Module2_Parser.py | L3-TC int-erasure type seam `cap-vm-unerase-str` | no | 0 (cv11) | HONESTY-WALL: cap-re-match-model, cap-vm-unerase-list | no | no (honesty wall) |
| `Module3_Weaver._attach_labels_and_ghost_assigns` | frontend/Module3_Weaver.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv9; replay r9xs056_2: same terminal) | DEPTH-STOP: cap-vm-unerase-dict | no | - |
| `Module3_Weaver._check_protect_aliasing` | frontend/Module3_Weaver.py | R: recursion cycle through a METHOD/constructor call `cap-method-recursion-cycle` | no | 1 (cv9; replay r9xs063_2: same terminal) | DEPTH-STOP: cap-method-recursion-cycle, cap-pyast-node-typing, cap-set-iteration | no | - |
| `Module3_Weaver._collect_field_read_sites` | frontend/Module3_Weaver.py | R: in-place receiver mutator `cap-list-param-byref-append` | no | 1 (cv9; replay r9xs067_2: same terminal) | DEPTH-STOP: cap-list-param-byref-append, cap-method-recursion-cycle, cap-pyast-node-typing | no | - |
| `Module3_Weaver._collect_self_call_sites` | frontend/Module3_Weaver.py | R: in-place receiver mutator `cap-list-param-byref-append` | no | 1 (cv9; replay r9xs065_2: same terminal) | DEPTH-STOP: cap-list-param-byref-append, cap-method-recursion-cycle, cap-pyast-node-typing | no | - |
| `Module3_Weaver._consolidate_module_concurrency` | frontend/Module3_Weaver.py | R: append to untracked list / array-local model `cap-growable-list-local` | no | 2 (cv9; replay r9xs055_3: same terminal) | DEPTH-STOP: cap-field-collection-writeback, cap-inplace-mutator-add, cap-pyast-node-attr-writeback | no | - |
| `Module3_Weaver._expand_happy_properties` | frontend/Module3_Weaver.py | R: identity test vs literal `cap-identity-vs-literal` | no | 1 (cv9; replay r9xs060_2: same terminal) | DEPTH-STOP: cap-identity-vs-literal, cap-object-identity-model | no | - |
| `Module3_Weaver._extract_happy_properties` | frontend/Module3_Weaver.py | R: UB-7.1 loop body mutates iterated collection `cap-iter-mutation` | no | 2 (cv9; replay r9xs057_3: same terminal) | DEPTH-STOP: cap-dict-param-byref-store, cap-inplace-mutator-extend, cap-iter-mutation | no | - |
| `Module3_Weaver._field_write_site` | frontend/Module3_Weaver.py | R: append to untracked list / array-local model `cap-growable-list-local` | no | 1 (cv9; replay r9xs058_2: same terminal) | DEPTH-STOP: cap-growable-list-local, cap-return-exn-nonint | no | - |
| `Module3_Weaver._happy_predicate` | frontend/Module3_Weaver.py | R: nested closure lift `cap-closure-lift` (remote:module3_weaver__to_csl) | no | 1 (cv9; replay r9xs059_2: same terminal) | HONESTY-WALL: cap-R325-call-deepcopy, cap-closure-lift, cap-pyast-unparse | no | no (honesty wall) |
| `Module3_Weaver._parse_extracted_contracts` | frontend/Module3_Weaver.py | R: in-place receiver mutator `cap-inplace-mutator-computed-receiver` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-computed-receiver | no | - |
| `Module3_Weaver._region_bound_str` | frontend/Module3_Weaver.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-return` | no | 0 (cv9) | HONESTY-WALL: cap-float-str, cap-getattr-dynamic, cap-vm-unerase-irnode | no | no (honesty wall) |
| `Module3_Weaver._subscript_read_site` | frontend/Module3_Weaver.py | L3-TC int-erasure type seam `cap-vm-unerase-irnode` | no | 1 (cv9; replay r9xs064_2: same terminal) | DEPTH-STOP: cap-pyast-node-typing, cap-vm-unerase-irnode | no | - |
| `Module3_Weaver._subst_csl_param` | frontend/Module3_Weaver.py | R: recursion cycle through a METHOD/constructor call `cap-method-recursion-cycle` | no | 0 (cv9) | HONESTY-WALL: cap-dataclass-reflection, cap-method-recursion-cycle | no | no (honesty wall) |
| `Module3_Weaver._synthesize_selfcomp` | frontend/Module3_Weaver.py | R: nested closure lift `cap-closure-lift` (remote:module3_weaver___call) | no | 0 (cv9) | HONESTY-WALL: cap-closure-lift, cap-pyast-ctor-model, cap-pyast-node-attr-writeback | no | no (honesty wall) |
| `Module3_Weaver.process` | frontend/Module3_Weaver.py | R: R327 ident collision with an emitter-generated binder nam `cap-binder-hygiene-R327` | no | 2 (lvE) | DEPTH-STOP: cap-binder-hygiene-R327, cap-identity-vs-literal | no | - |
| `PyCSLWeaver._attach_loop_contracts` | frontend/Module3_Weaver.py | R: append to untracked list / array-local model `cap-growable-list-local` | no | 1 (cv9; replay r9xs052_2: same terminal) | DEPTH-STOP: cap-field-collection-writeback, cap-pyast-node-attr-writeback | no | - |
| `PyCSLWeaver._desugar_acts` | frontend/Module3_Weaver.py | L3-TC int-erasure type seam `cap-vm-unerase-irnode` | no | 1 (cv9; replay r9xs045_2: same terminal) | DEPTH-STOP: cap-vm-unerase-irnode | no | - |
| `PyCSLWeaver._dispatch_function_contracts` | frontend/Module3_Weaver.py | R: dropped unpacking / loop target (route #301) `cap-nested-unpack-target` | no | 2 (cv9; replay r9xs047_3: same terminal) | DEPTH-STOP: cap-field-collection-writeback, cap-nested-unpack-target, cap-pyast-node-attr-writeback, cap-trusted-val-unit-return | no | - |
| `PyCSLWeaver._extract_mixin_directives` | frontend/Module3_Weaver.py | R: append to untracked list / array-local model `cap-growable-list-local` | no | 2 (cv9; replay r9xs046_3: same terminal) | DEPTH-STOP: cap-field-collection-writeback, cap-inplace-mutator-computed-receiver, cap-pyast-node-attr-writeback | no | - |
| `PyCSLWeaver._subst_var` | frontend/Module3_Weaver.py | R: R325 opaque-int fallback `cap-R325-module-constant` (remote:pv_size) | no | 3 (lvC) | HONESTY-WALL: cap-dataclass-reflection, cap-r325-typepos, cap-vm-unerase-irnode | no | no (honesty wall) |
| `PyCSLWeaver.visit_ClassDef` | frontend/Module3_Weaver.py | R: append to untracked list / array-local model `cap-growable-list-local` | no | 1 (cv9; replay r9xs051_2: same terminal) | DEPTH-STOP: cap-field-collection-writeback, cap-pyast-node-attr-writeback | no | - |
| `PyCSLWeaver.visit_For` | frontend/Module3_Weaver.py | R: METHOD-ARG-UNFRAMED (writes an argument) `cap-method-arg-frame` (remote:pycslweaver___attach_loop_contracts) | no | 1 (cv9; replay r9xs054_2: same terminal) | DEPTH-STOP: cap-method-arg-frame, cap-pyast-node-attr-writeback | no | - |
| `PyCSLWeaver.visit_FunctionDef` | frontend/Module3_Weaver.py | R: METHOD-ARG-UNFRAMED (writes an argument) `cap-method-arg-frame` (remote:pycslweaver___init_function_csl_fields) | no | 1 (cv9; replay r9xs049_2: same terminal) | DEPTH-STOP: cap-method-arg-frame, cap-pyast-node-attr-writeback | no | - |
| `PyCSLWeaver.visit_Module` | frontend/Module3_Weaver.py | R: in-place receiver mutator `cap-inplace-mutator-add` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-add, cap-inplace-mutator-computed-receiver | no | - |
| `PyCSLWeaver.visit_While` | frontend/Module3_Weaver.py | R: METHOD-ARG-UNFRAMED (writes an argument) `cap-method-arg-frame` (remote:pycslweaver___attach_loop_contracts) | no | 1 (cv9; replay r9xs053_2: same terminal) | DEPTH-STOP: cap-method-arg-frame, cap-pyast-node-attr-writeback | no | - |
| `PyCSLWeaver.visit_With` | frontend/Module3_Weaver.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv9; replay r9xs050_2: same terminal) | DEPTH-STOP: cap-vm-unerase-dict | no | - |
| `Module5_IREmitter.generate_json` | frontend/Module5_IREmitter.py | R: function/class name rebound (setattr / namespace dict wri `cap-name-rebinding-model` | no | 0 (cv9) | DEPTH-STOP: cap-name-rebinding-model | no | - |
| `PyCSLToJSONEmitter.__init__` | frontend/Module5_IREmitter.py | TC-OK `none-TC-OK` | **yes** (cv8: R: and/or used as a VALUE on non-bool operands (new since cv) | 0 (cv11) | DEPTH-STOP: cap-name-rebinding-model | no | - |
| `PyCSLToJSONEmitter._build_function_ir` | frontend/Module5_IREmitter.py | R: R327 ident collision with an emitter-generated binder nam `cap-binder-hygiene-R327` | no | 2 (lvE) | DEPTH-STOP: cap-binder-hygiene-R327, cap-identity-vs-literal | no | - |
| `PyCSLToJSONEmitter._build_function_symbol_table` | frontend/Module5_IREmitter.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 1 (cv9; replay r9xs085_2: same terminal) | DEPTH-STOP: cap-inplace-mutator-setdefault, cap-pyast-node-typing | no | - |
| `PyCSLToJSONEmitter._collect_class_fields` | frontend/Module5_IREmitter.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 0 (cv11; replay r9xs080_2: MOVED R: in-place receiver mutator -> R: R567-EMITIR-ATTR-ON-NONIR) | DEPTH-STOP: cap-vm-irnode-R1-narrowing-view, cap-exact-pop-model, cap-pyast-node-typing | no | - |
| `PyCSLToJSONEmitter._collect_final_registry` | frontend/Module5_IREmitter.py | R: R567-EMITIR-ATTR-ON-NONIR `cap-vm-irnode-R1-narrowing-view` | new stub | 0 (cv11) | TC-OK-HONEST: cap-vm-irnode-R1-narrowing-view | yes | honest (input-reading) |
| `PyCSLToJSONEmitter._collect_type_params` | frontend/Module5_IREmitter.py | R: R567-EMITIR-ATTR-ON-NONIR `cap-vm-irnode-R1-narrowing-view` | new stub | 0 (cv11) | TC-OK-HONEST: cap-vm-irnode-R1-narrowing-view | yes | honest (input-reading) |
| `PyCSLToJSONEmitter._collect_typevar_registry` | frontend/Module5_IREmitter.py | R: R567-EMITIR-ATTR-ON-NONIR `cap-vm-irnode-R1-narrowing-view` | new stub | 0 (cv11) | TC-OK-HONEST: cap-vm-irnode-R1-narrowing-view | yes | honest (input-reading) |
| `PyCSLToJSONEmitter._collect_union_arms` | frontend/Module5_IREmitter.py | R: in-place receiver mutator `cap-inplace-mutator-pop` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-fresh-local, cap-inplace-mutator-pop | no | - |
| `PyCSLToJSONEmitter._const_int_value` | frontend/Module5_IREmitter.py | R: R567-EMITIR-ATTR-ON-NONIR `cap-vm-irnode-R1-narrowing-view` | new stub | 0 (cv11) | TC-OK-HONEST: cap-vm-irnode-R1-narrowing-view | yes | honest (input-reading) |
| `PyCSLToJSONEmitter._csl_in` | frontend/Module5_IREmitter.py | L3-TC int-erasure type seam `cap-vm-unerase-irnode` | no | 0 (cv9) | DEPTH-STOP: cap-vm-unerase-irnode | no | - |
| `PyCSLToJSONEmitter._csl_list_to_ir` | frontend/Module5_IREmitter.py | R: R566-EMITIR-ITEM-STORE `cap-emit-ir-item-store-model` | **yes** (cv8: L3-TC int-erasure type seam) | 0 (cv11) | DEPTH-STOP: cap-emit-ir-item-store-model, cap-vm-irnode-R1-narrowing-view, cap-getattr-dynamic | no | - |
| `PyCSLToJSONEmitter._detect_array_dimensions` | frontend/Module5_IREmitter.py | R: element store through non-list value `cap-elem-store-nonlist` | no | 1 (cv9; replay r9xs086_2: same terminal) | DEPTH-STOP: cap-closure-lift, cap-elem-store-nonlist | no | - |
| `PyCSLToJSONEmitter._detect_seq_promotion` | frontend/Module5_IREmitter.py | R: element store through non-list value `cap-elem-store-nonlist` | no | 1 (cv9; replay r9xs087_2: same terminal) | DEPTH-STOP: cap-closure-lift, cap-elem-store-nonlist, cap-inplace-mutator-discard | no | - |
| `PyCSLToJSONEmitter._emit_namedtuple_record` | frontend/Module5_IREmitter.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 0 (cv11; replay r9xs078_2: MOVED R: in-place receiver mutator -> R: R566-EMITIR-ITEM-STORE) | DEPTH-STOP: cap-vm-irnode-R1-narrowing-view, cap-emit-ir-item-store-model, cap-erased-to-builtin-slot-arg, cap-inplace-mutator-computed-receiver, cap-pyast-node-typing, cap-self-field-alias-analysis | no | - |
| `PyCSLToJSONEmitter._emit_protocol_interface` | frontend/Module5_IREmitter.py | R: in-place receiver mutator `cap-inplace-mutator-computed-receiver` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-computed-receiver, cap-inplace-mutator-fresh-local | no | - |
| `PyCSLToJSONEmitter._emit_typeddict_record` | frontend/Module5_IREmitter.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 1 (cv9; replay r9xs076_2: same terminal) | DEPTH-STOP: cap-erased-to-builtin-slot-arg, cap-inplace-mutator-computed-receiver, cap-pyast-node-typing, cap-self-field-alias-analysis | no | - |
| `PyCSLToJSONEmitter._encode_callable_annotation` | frontend/Module5_IREmitter.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 0 (cv9) | DEPTH-STOP: cap-vm-unerase-irnode, cap-vm-unerase-list | no | - |
| `PyCSLToJSONEmitter._field_type_from_annotation_inst` | frontend/Module5_IREmitter.py | L3-TC int-erasure type seam `cap-vm-unerase-str` | no | 0 (cv11) | DEPTH-STOP: cap-missing-mirror-sibling, cap-pyast-node-typing | no | - |
| `PyCSLToJSONEmitter._get_mutex_invariant_ir` | frontend/Module5_IREmitter.py | L3-TC int-erasure type seam `cap-vm-unerase-irnode` | no | 0 (cv9) | DEPTH-STOP: cap-vm-unerase-union | no | - |
| `PyCSLToJSONEmitter._m5_get_type_name` | frontend/Module5_IREmitter.py | R: except Exception vs user exception (route #175) `cap-exception-hierarchy-model` | no | 1 (cv9; replay r9xs084_2: same terminal) | DEPTH-STOP: cap-exception-hierarchy-model | no | - |
| `PyCSLToJSONEmitter._m5_get_type_name_legacy` | frontend/Module5_IREmitter.py | R: R567-EMITIR-ATTR-ON-NONIR `cap-vm-irnode-R1-narrowing-view` | new stub | 0 (cv11) | TC-OK-HONEST: cap-vm-irnode-R1-narrowing-view | yes | honest (input-reading) |
| `PyCSLToJSONEmitter._match_pattern_to_ir` | frontend/Module5_IREmitter.py | R: identity test vs literal `cap-identity-vs-literal` | no | 1 (cv9; replay r9xs075_2: same terminal) | DEPTH-STOP: cap-identity-vs-literal, cap-method-recursion-cycle | no | - |
| `PyCSLToJSONEmitter._normalize_literal_annotation` | frontend/Module5_IREmitter.py | R: field-collection append without write-back `cap-field-collection-writeback` | no | 2 (cv9; replay r9xs082_3: same terminal) | DEPTH-STOP: cap-field-collection-writeback, cap-vm-unerase-irnode | no | - |
| `PyCSLToJSONEmitter._normalize_union_annotation` | frontend/Module5_IREmitter.py | R: dropped unpacking / loop target (route #301) `cap-nested-unpack-target` | no | 1 (cv9; replay r9xs081_2: same terminal) | DEPTH-STOP: cap-getattr-dynamic, cap-nested-unpack-target | no | - |
| `PyCSLToJSONEmitter._populate_protocol_conformance` | frontend/Module5_IREmitter.py | R: in-place receiver mutator `cap-inplace-mutator-setdefault` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-fresh-local, cap-inplace-mutator-setdefault | no | - |
| `PyCSLToJSONEmitter._py_expr_call` | frontend/Module5_IREmitter.py | R: in-place receiver mutator `cap-inplace-mutator-reverse` | no | 4 (lvB) | DEPTH-STOP: cap-R325-call-set-ctor, cap-inplace-mutator-fresh-local, cap-inplace-mutator-reverse, cap-str-join-read | no | - |
| `PyCSLToJSONEmitter._py_expr_fstring` | frontend/Module5_IREmitter.py | R: recursion cycle through a METHOD/constructor call `cap-method-recursion-cycle` | no | 1 (cv9; replay r9xs073_2: same terminal) | DEPTH-STOP: cap-method-recursion-cycle, cap-pyast-node-typing | no | - |
| `PyCSLToJSONEmitter._py_stmts_to_ir` | frontend/Module5_IREmitter.py | R: R541-ELEMENT-KIND `cap-kind-judge-list-arg` | no | 1 (cv9; replay r9xs074_2: same terminal) | DEPTH-STOP: cap-kind-judge-list-arg, cap-method-recursion-cycle | no | - |
| `PyCSLToJSONEmitter._synthesize_namedtuple_functional` | frontend/Module5_IREmitter.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 0 (cv11; replay r9xs079_2: MOVED R: in-place receiver mutator -> R: R567-EMITIR-ATTR-ON-NONIR) | DEPTH-STOP: cap-vm-irnode-R1-narrowing-view, cap-erased-to-builtin-slot-arg, cap-inplace-mutator-computed-receiver, cap-pyast-node-typing, cap-self-field-alias-analysis | no | - |
| `PyCSLToJSONEmitter._synthesize_typeddict_functional` | frontend/Module5_IREmitter.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 0 (cv11; replay r9xs077_2: MOVED R: in-place receiver mutator -> R: R567-EMITIR-ATTR-ON-NONIR) | DEPTH-STOP: cap-vm-irnode-R1-narrowing-view, cap-erased-to-builtin-slot-arg, cap-inplace-mutator-computed-receiver, cap-pyast-node-typing, cap-self-field-alias-analysis | no | - |
| `PyCSLToJSONEmitter._union_arm_tag` | frontend/Module5_IREmitter.py | R: R567-EMITIR-ATTR-ON-NONIR `cap-vm-irnode-R1-narrowing-view` | new stub | 0 (cv11) | TC-OK-HONEST: cap-vm-irnode-R1-narrowing-view | yes | honest (input-reading) |
| `PyCSLToJSONEmitter.visit_ClassDef` | frontend/Module5_IREmitter.py | R: R327 ident collision with an emitter-generated binder nam `cap-binder-hygiene-R327` | no | 2 (lvE) | DEPTH-STOP: cap-binder-hygiene-R327, cap-tuple-unpack-alias | no | - |
| `PyCSLToJSONEmitter.visit_FunctionDef` | frontend/Module5_IREmitter.py | R: append to untracked list / array-local model `cap-growable-list-local` | no | 1 (cv9; replay r9xs088_2: same terminal) | DEPTH-STOP: cap-growable-list-local, cap-self-field-alias-analysis | no | - |
| `PyCSLToJSONEmitter.visit_Module` | frontend/Module5_IREmitter.py | R: import-system manipulation (route #326) `cap-import-system-local-module` | no | 1 (cv9; replay r9xs069_2: same terminal) | DEPTH-STOP: cap-import-system-local-module | no | - |
| `_ChainDesugarer.visit_Compare` | frontend/desugar.py | R: R325 opaque-int fallback `cap-R325-call-ast-ctor` | no | 2 (lvC) | DEPTH-STOP: cap-R325-call-ast-ctor, cap-pyast-node-attr-writeback | no | - |
| `_try_reaches_assert` | frontend/desugar.py | R: R325 opaque-int fallback `cap-R325-call-ast-walk` | no | 2 (lvC) | REFUSED-termination: cap-R325-call-ast-walk, cap-diverges | no | - |
| `normalize_stores` | frontend/desugar.py | R: function/class name rebound (setattr / namespace dict wri `cap-name-rebinding-model` | no | 0 (cv9) | HONESTY-WALL: cap-getattr-dynamic, cap-pyast-ctor-model | no | no (honesty wall) |
| `_ExecSplicer.visit_Expr` | frontend/exec_splice.py | R: R506-TRIGGER-SITE-UNLOWERED `cap-R506-trigger-site` | no | 1 (cv9; replay r9xs091_2: same terminal) | HONESTY-WALL: cap-R325-call-ast-parse, cap-R506-trigger-site, cap-pyast-ctor-model | no | no (honesty wall) |
| `_stub_set` | frontend/import_classifier.py | TC-OK `none-TC-OK` | no | 0 (cv9) | TC-OK-FACADE: cap-fs-path-model, cap-vm-unerase-str | yes | FACADE |
| `check_imports` | frontend/import_classifier.py | R: R562-COMPREHENSION-ELEMENT-KIND `cap-kind-judge-list-arg` | **yes** (cv8: L3-TC int-erasure type seam) | 2 (cv9; replay r9xs093_3: same terminal) | DEPTH-STOP: cap-pyast-node-typing | no | - |
| `_Inliner._expand` | frontend/ir_inline.py | R: identity test vs literal `cap-identity-vs-literal` | no | 3 (cv9; replay r9xs095_4: same terminal) | DEPTH-STOP: cap-erased-to-builtin-slot-arg, cap-identity-vs-literal, cap-inplace-mutator-update, cap-sorted-str-list | no | - |
| `_Inliner._hoist_calls_in_expr` | frontend/ir_inline.py | R: in-place receiver mutator `cap-inplace-mutator-extend` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-extend, cap-method-arg-frame | no | - |
| `_Inliner.inline_stmts` | frontend/ir_inline.py | R: METHOD-FRAME (body writes a param not in assigns) `cap-method-arg-frame` | no | 3 (cv9; replay r9xs096_4: same terminal) | DEPTH-STOP: cap-R274-writing-call-in-comprehension, cap-method-arg-frame | no | - |
| `_inline_calls` | frontend/ir_inline.py | R: in-place receiver mutator `cap-inplace-mutator-update` | no | 2 (lvB) | CERTIFIED-BOUNDARY: cap-certified-boundary-escape, cap-inplace-mutator-update | no | - |
| `_recursive_methods` | frontend/ir_inline.py | R: nested closure lift `cap-closure-lift` (remote:reaches_self) | no | 4 (cv9; replay r9xs094_5: same terminal) | DEPTH-STOP: cap-R274-writing-call-in-comprehension, cap-vm-unerase-irnode | no | - |
| `apply_inline_globals` | frontend/ir_inline.py | R: in-place receiver mutator `cap-inplace-mutator-pop` | no | 2 (lvB) | CERTIFIED-BOUNDARY: cap-certified-boundary-escape, cap-inplace-mutator-pop | no | - |
| `_find_record_type_from_dep_imports` | frontend/ir_resolve.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 2 (cv9; replay r9xs101_3: same terminal) | DEPTH-STOP: cap-vm-unerase-irnode, cap-vm-unerase-tuple, cap-vm-unerase-union | no | - |
| `_get_module_exports` | frontend/ir_resolve.py | R: `with ... as` binding unmodelled (context-manager model) `cap-context-manager-model` | no | 1 (cv9; replay r9xs098_2: same terminal) | TC-OK-FACADE: cap-R325-call-ast-parse, cap-context-manager-model, cap-fs-path-model, cap-stdlib-ast-model | yes | FACADE |
| `_inject_functions` | frontend/ir_resolve.py | R: in-place receiver mutator `cap-inplace-mutator-computed-receiver` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-computed-receiver, cap-inplace-mutator-fresh-local | no | - |
| `_process_dependency` | frontend/ir_resolve.py | R: element store through non-list value `cap-elem-store-nonlist` | no | 2 (cv9; replay r9xs099_3: same terminal) | DEPTH-STOP: cap-context-manager-model, cap-elem-store-nonlist, cap-fs-read-model, cap-vm-unerase-irnode | no | - |
| `_resolve_direct_imports` | frontend/ir_resolve.py | R: import-system manipulation (route #326) `cap-import-system-local-module` | no | 0 (cv9) | HONESTY-WALL: cap-R325-call-ast-parse, cap-defaultdict-list, cap-fs-path-model, cap-import-system-local-module | no | no (honesty wall) |
| `_resolve_imported_base_classes` | frontend/ir_resolve.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 1 (cv9; replay r9xs106_2: same terminal) | DEPTH-STOP: cap-inplace-mutator-setdefault, cap-vm-unerase-irnode | no | - |
| `_resolve_imported_classes` | frontend/ir_resolve.py | R: dropped unpacking / loop target (route #301) `cap-nested-unpack-target` | no | 2 (cv9; replay r9xs105_3: same terminal) | DEPTH-STOP: cap-defaultdict-list, cap-nested-unpack-target, cap-vm-unerase-irnode | no | - |
| `_resolve_module_imports` | frontend/ir_resolve.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 1 (cv9; replay r9xs104_2: same terminal) | DEPTH-STOP: cap-R542-container-kind, cap-vm-unerase-irnode | no | - |
| `_resolve_module_path` | frontend/ir_resolve.py | R: import-system manipulation (route #326) `cap-import-system-local-module` | no | 0 (cv9) | HONESTY-WALL: cap-fs-path-model, cap-import-system-local-module | no | no (honesty wall) |
| `_resolve_wildcard_imports` | frontend/ir_resolve.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 1 (cv9; replay r9xs103_2: same terminal) | DEPTH-STOP: cap-dict-alias, cap-vm-unerase-irnode | no | - |
| `_strip_dir_scan_proofs` | frontend/ir_resolve.py | R: parameter rebinding in a nested block `cap-param-rebind-nested` | no | 2 (cv9; replay r9xs100_3: same terminal) | HONESTY-WALL: cap-R325-call-dict-copy, cap-R542-container-kind, cap-list-comp-model, cap-param-rebind-nested | no | no (honesty wall) |
| `apply_composition` | frontend/ir_resolve.py | R: R327 ident collision (case fold) `cap-binder-hygiene-R327` | no | 2 (lvE) | DEPTH-STOP: cap-binder-hygiene-R327, cap-closure-lift | no | - |
| `apply_inheritance` | frontend/ir_resolve.py | R: hash of unknown/unhashable class `cap-hash-judge-class-set` | no | 1 (cv9; replay r9xs107_2: same terminal) | DEPTH-STOP: cap-closure-lift, cap-hash-judge-class-set, cap-vm-unerase-irnode | no | - |
| `resolve` | frontend/ir_resolve.py | R: global / module-scope write `cap-global-nonlocal-write` | no | 3 (cv9; replay r9xs109_4: same terminal) | DEPTH-STOP: cap-R489-implicit-dunder, cap-dict-alias, cap-global-nonlocal-write, cap-optional-param-default | no | - |
| `resolve_imports` | frontend/ir_resolve.py | R: tuple-unpack alias `cap-tuple-unpack-alias` | no | 2 (cv9; replay r9xs108_3: same terminal) | DEPTH-STOP: cap-tuple-unpack-alias, cap-vm-unerase-irnode | no | - |
| `collect_module_constants` | frontend/module_collect.py | R: R325 opaque-int fallback `cap-R325-call-getattr-unknown` (remote:_module_const_int) | no | 4 (lvC) | HONESTY-WALL: cap-R325-call-getattr-unknown, cap-dict-comp-model, cap-emit-unbound-symbol-defect, cap-none-fold-unpack | no | no (honesty wall) |
| `collect_module_globals` | frontend/module_collect.py | R: R325 opaque-int fallback `cap-R325-call-getattr-unknown` | no | 4 (lvC) | HONESTY-WALL: cap-R325-call-getattr-unknown, cap-dict-comp-model, cap-emit-unbound-symbol-defect, cap-none-fold-unpack | no | no (honesty wall) |
| `_check_gt4_polymorphic_recursion` | frontend/monomorphize.py | R: R325 opaque-int fallback `cap-R325-call-ast-walk` (remote:_extract_ast_subscript) | no | 3 (lvC) | DEPTH-STOP: cap-R325-call-ast-walk, cap-R325-call-set-ctor, cap-exception-payload-model | no | - |
| `_collect_instantiations` | frontend/monomorphize.py | R: for-loop variant over unconstrained iterable `cap-iterable-termination-variant` | no | 2 (cv9; replay r9xs111_3: same terminal) | DEPTH-STOP: cap-iterable-termination-variant, cap-vm-unerase-irnode | no | - |
| `_emit_specializations` | frontend/monomorphize.py | R: element store through non-list value `cap-elem-store-nonlist` | no | 2 (cv9; replay r9xs112_3: same terminal) | DEPTH-STOP: cap-elem-store-nonlist, cap-erased-to-builtin-slot-arg, cap-vm-unerase-irnode | no | - |
| `_record_classification` | frontend/monomorphize.py | R: in-place receiver mutator `cap-inplace-mutator-setdefault` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-setdefault, cap-method-arg-frame | no | - |
| `_rewrite_annotation_str` | frontend/monomorphize.py | R: R542-NON-CONTAINER-OPERAND `cap-R542-container-kind` | no | 1 (cv9; replay r9xs116_2: same terminal) | HONESTY-WALL: cap-re-match-model, cap-return-exn-nonint | no | no (honesty wall) |
| `_rewrite_annotations` | frontend/monomorphize.py | R: element store through non-list value `cap-elem-store-nonlist` | no | 2 (cv9; replay r9xs115_3: same terminal) | DEPTH-STOP: cap-elem-store-nonlist, cap-vm-unerase-irnode | no | - |
| `_rewrite_call_sites` | frontend/monomorphize.py | R: element store through non-list value `cap-elem-store-nonlist` | no | 2 (cv9; replay r9xs113_3: same terminal) | DEPTH-STOP: cap-elem-store-nonlist, cap-vm-unerase-irnode | no | - |
| `_rewrite_subscript_calls_in_stmt` | frontend/monomorphize.py | R: R325 opaque-int fallback `cap-R325-module-constant` (remote:pv_size) | no | 3 (lvC) | HONESTY-WALL: cap-r325-typepos, cap-vm-unerase-dict, cap-vm-unerase-irnode | no | no (honesty wall) |
| `_rewrite_subscript_to_name` | frontend/monomorphize.py | R: R542-NON-CONTAINER-OPERAND `cap-R542-container-kind` | no | 1 (cv9; replay r9xs114_2: same terminal) | HONESTY-WALL: cap-r325-typepos, cap-vm-unerase-irnode | no | no (honesty wall) |
| `_specialize_decl` | frontend/monomorphize.py | R: in-place receiver mutator `cap-inplace-mutator-pop` | no | 4 (lvB) | DEPTH-STOP: cap-R274-writing-call-in-comprehension, cap-inplace-mutator-fresh-local, cap-inplace-mutator-pop, cap-vm-unerase-irnode | no | - |
| `_specialize_function` | frontend/monomorphize.py | R: in-place receiver mutator `cap-inplace-mutator-pop` | no | 4 (lvB) | DEPTH-STOP: cap-R274-writing-call-in-comprehension, cap-inplace-mutator-fresh-local, cap-inplace-mutator-pop, cap-vm-unerase-irnode | no | - |
| `apply_monomorphization` | frontend/monomorphize.py | R: R542-NON-CONTAINER-OPERAND `cap-R542-container-kind` | no | 2 (cv9; replay r9xs110_3: same terminal) | DEPTH-STOP: cap-R542-container-kind, cap-dict-alias, cap-pyval-tree-writeback | no | - |
| `Ellipsis.__new__` | frontend/pure_ast.py | R: UB-7.6 non-trivial __new__ `none-UB-7.6-new` | no | 0 (cv10) | HONESTY-WALL: cap-ub76-new-singleton | no | no (honesty wall) |
| `NodeTransformer.generic_visit` | frontend/pure_ast.py | R: function/class name rebound (setattr / namespace dict wri `cap-name-rebinding-model` | no | 0 (cv10) | HONESTY-WALL: cap-dynamic-getattr-setattr, cap-generator-yield-model | no | no (honesty wall) |
| `NodeVisitor.generic_visit` | frontend/pure_ast.py | R: R542-NON-CONTAINER-OPERAND `cap-R542-callee-result-kind` | no | 0 (cv10) | HONESTY-WALL: cap-R542-callee-result-kind, cap-dynamic-getattr-method-dispatch, cap-generator-yield-model | no | no (honesty wall) |
| `NodeVisitor.visit` | frontend/pure_ast.py | R: getattr non-literal default (route #309) `cap-getattr-dynamic` | no | 0 (cv10) | HONESTY-WALL: cap-dynamic-getattr-method-dispatch | no | no (honesty wall) |
| `NodeVisitor.visit_Constant` | frontend/pure_ast.py | R: METHOD-ARG-UNFRAMED (writes an argument) `cap-method-arg-frame` (remote:nodevisitor__generic_visit) | no | 0 (cv10) | HONESTY-WALL: cap-dynamic-getattr-method-dispatch, cap-method-arg-frame | no | no (honesty wall) |
| `_Parser.__init__` | frontend/pure_ast.py | R: class-invariant ctor obligation (route #226) `cap-ctor-invariant-obligation` | no | 1 (cv10; replay r10xh007_2: same terminal) | DEPTH-STOP: cap-method-recursion-cycle | no | - |
| `_Parser._fin` | frontend/pure_ast.py | L3-TC int-erasure type seam `cap-vm-unerase-irnode` | no | 3 (cv10; replay r10xh011_4: same terminal) | DEPTH-STOP: cap-emit-ir-inplace-field-write, cap-vm-unerase-union | no | - |
| `_Parser._fin_block` | frontend/pure_ast.py | R: dropped unpacking / loop target (route #301) `cap-nested-unpack-target` | no | 3 (cv10; replay r10xh014_4: same terminal) | HONESTY-WALL: cap-dynamic-getattr-setattr, cap-emit-ir-inplace-field-write, cap-vm-unerase-tuple | no | no (honesty wall) |
| `_Parser._max_end` | frontend/pure_ast.py | R: recursion cycle through a METHOD/constructor call `cap-method-recursion-cycle` | no | 1 (cv10; replay r10xh013_2: same terminal) | TC-OK-PARTIAL: cap-dynamic-getattr-setattr, cap-method-recursion-cycle, cap-pyast-node-typing | yes | partial |
| `_Parser._slice` | frontend/pure_ast.py | R: dropped unpacking / loop target (route #301) `cap-nested-unpack-target` | no | 3 (cv10; replay r10xh008_4: same terminal) | DEPTH-STOP: cap-method-recursion-cycle, cap-self-field-untyped-ctor | no | - |
| `_Parser.error` | frontend/pure_ast.py | TC-OK `none-TC-OK` | no | 0 (cv10) | TC-OK-FACADE: cap-exception-payload-model | yes | FACADE |
| `_Parser.node` | frontend/pure_ast.py | L3-TC int-erasure type seam `cap-vm-unerase-irnode` | no | 1 (cv10; replay r10xh012_2: same terminal) | DEPTH-STOP: cap-pyast-dynamic-ctor | no | - |
| `_Parser.unsupported` | frontend/pure_ast.py | TC-OK `none-TC-OK` | no | 0 (cv10) | TC-OK-FACADE: cap-exception-payload-model | yes | FACADE |
| `_Precedence.next` | frontend/pure_ast.py | R: R337 operator on self `cap-R337-operator-on-self` | no | 2 (cv10; replay r10xh035_3: same terminal) | DEPTH-STOP: cap-enum-value-lookup | no | - |
| `_Unparser.__init__` | frontend/pure_ast.py | R: `with` on an unproven context manager (route #257) `cap-context-manager-model` (remote:visit_NamedExpr) | no | 0 (cv10) | DEPTH-STOP: cap-context-manager-model | no | - |
| `_Unparser._str_literal_helper` | frontend/pure_ast.py | R: in-place receiver mutator `cap-inplace-mutator-sort` | no | 0 (cv10) | DEPTH-STOP: cap-R325-str-encoding-op, cap-closure-lift, cap-inplace-mutator-sort, cap-map-builtin, cap-sorted-key | no | - |
| `_Unparser._write_docstring_and_traverse_body` | frontend/pure_ast.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv10; replay r10xh044_2: same terminal) | TC-OK-PARTIAL: cap-effectful-callback, cap-pyast-node-typing | yes | partial |
| `_Unparser._write_fstring_inner` | frontend/pure_ast.py | L3-TC raises unlisted exception `cap-raises-clause-propagation` | no | 1 (cv10; replay r10xh051_2: same terminal) | DEPTH-STOP: cap-method-recursion-cycle, cap-raises-clause-propagation | no | - |
| `_Unparser.buffered` | frontend/pure_ast.py | R: parameter rebinding in a nested block `cap-param-rebind-nested` | no | 0 (cv10) | HONESTY-WALL: cap-context-manager-model, cap-generator-yield-model | no | no (honesty wall) |
| `_Unparser.delimit_if` | frontend/pure_ast.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-return` | no | 0 (cv11) | HONESTY-WALL: cap-context-manager-model, cap-self-field-alias-analysis, cap-effectful-callback | no | no (honesty wall) |
| `_Unparser.get_type_comment` | frontend/pure_ast.py | R: non-int value returned from an int-annotated function (ne `cap-vm-unerase-return-kind` | no | 1 (cv10; replay r10xh043_2: same terminal) | DEPTH-STOP: cap-getattr-dynamic, cap-optional-str-truthiness, cap-self-field-untyped-ctor | no | - |
| `_Unparser.interleave` | frontend/pure_ast.py | R: R325 opaque-int fallback `cap-R325-call-iter-builtin` | no | 0 (cv10) | HONESTY-WALL: cap-R325-call-iter-builtin, cap-effectful-callback | no | no (honesty wall) |
| `_Unparser.items_view` | frontend/pure_ast.py | L3-TC cannot apply int (callable erased) `cap-vm-callable-value` | no | 0 (cv10) | HONESTY-WALL: cap-effectful-callback, cap-vm-callable-value | no | no (honesty wall) |
| `_Unparser.set_precedence` | frontend/pure_ast.py | R: element store through non-list value `cap-elem-store-nonlist` | no | 0 (cv10) | DEPTH-STOP: cap-self-field-untyped-ctor, cap-vm-unerase-dict | no | - |
| `_Unparser.visit_BoolOp` | frontend/pure_ast.py | R: nonlocal write `cap-global-nonlocal-write` (remote:_unparser__increasing_level_traverse) | no | 0 (cv10) | HONESTY-WALL: cap-context-manager-model, cap-effectful-callback, cap-global-nonlocal-write | no | no (honesty wall) |
| `_Unparser.visit_Dict` | frontend/pure_ast.py | L3-TC int-erasure type seam `cap-vm-unerase-tuple` | no | 0 (cv10) | HONESTY-WALL: cap-context-manager-model, cap-effectful-callback, cap-vm-unerase-tuple | no | no (honesty wall) |
| `_Unparser.visit_JoinedStr` | frontend/pure_ast.py | R: `with ... as` binding unmodelled (context-manager model) `cap-context-manager-model` | no | 0 (cv11) | HONESTY-WALL: cap-context-manager-model, cap-self-field-alias-analysis, cap-effectful-callback | no | no (honesty wall) |
| `_Unparser.visit_Lambda` | frontend/pure_ast.py | R: `with ... as` binding unmodelled (context-manager model) `cap-context-manager-model` | no | 0 (cv11) | HONESTY-WALL: cap-context-manager-model, cap-self-field-alias-analysis, cap-effectful-callback | no | no (honesty wall) |
| `_Unparser.visit_MatchClass` | frontend/pure_ast.py | R: sorted(key=) `cap-sorted-key` | no | 0 (cv10) | HONESTY-WALL: cap-builtin-kwarg-zip-strict, cap-context-manager-model, cap-effectful-callback | no | no (honesty wall) |
| `_Unparser.visit_MatchMapping` | frontend/pure_ast.py | R: sorted(key=) `cap-sorted-key` | no | 0 (cv10) | HONESTY-WALL: cap-builtin-kwarg-zip-strict, cap-context-manager-model, cap-effectful-callback | no | no (honesty wall) |
| `_Unparser.visit_arguments` | frontend/pure_ast.py | L3-TC int-erasure type seam `cap-vm-unerase-tuple` | no | 0 (cv10) | DEPTH-STOP: cap-pyast-node-typing, cap-vm-unerase-tuple | no | - |
| `_Unparser.write` | frontend/pure_ast.py | R: in-place receiver mutator `cap-inplace-mutator-extend` | no | 0 (cv10) | HONESTY-WALL: cap-effectful-callback, cap-self-field-alias-analysis | no | no (honesty wall) |
| `_build_nodes` | frontend/pure_ast.py | R: function/class name rebound (setattr / namespace dict wri `cap-name-rebinding-model` | no | 0 (cv10) | DEPTH-STOP: cap-name-rebinding-model | no | - |
| `_decode_escapes` | frontend/pure_ast.py | R: R325 opaque-int fallback `cap-R325-module-constant` | no | 1 (cv10; replay r10xh020_2: same terminal) | DEPTH-STOP: cap-R325-call-chr-int-base, cap-R325-str-encoding-op | no | - |
| `_decode_fstring_middle` | frontend/pure_ast.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-return` | no | 1 (cv10; replay r10xh015_2: same terminal) | TC-OK-PARTIAL: cap-dependent-return-type | yes | partial |
| `_decode_string` | frontend/pure_ast.py | R: R558-BYTES-VALUE-KIND `cap-bytes-value-model` | **yes** (cv8: R: R325 opaque-int fallback) | 0 (cv11) | DEPTH-STOP: cap-bytes-value-model, cap-dependent-return-type | no | - |
| `_lex` | frontend/pure_ast.py | R: nested closure lift `cap-closure-lift` (remote:to_byte) | no | 1 (cv10; replay r10xh004_2: same terminal) | HONESTY-WALL: cap-tokenize-model | no | no (honesty wall) |
| `_merge_str_constants` | frontend/pure_ast.py | R: function/class name rebound (setattr / namespace dict wri `cap-name-rebinding-model` | no | 1 (cv10; replay r10xh016_2: same terminal) | HONESTY-WALL: cap-augassign-subscript-field, cap-emit-ir-inplace-field-write | no | no (honesty wall) |
| `_parse_number` | frontend/pure_ast.py | R: R325 opaque-int fallback `cap-R325-call-complex-bytes` (remote:_parser___pattern_number) | no | 1 (cv10; replay r10xh018_2: same terminal) | HONESTY-WALL: cap-R325-call-complex, cap-R325-call-str-to-number | no | no (honesty wall) |
| `_self_test` | frontend/pure_ast.py | R: sorted(key=) `cap-sorted-key` | no | 0 (cv10) | HONESTY-WALL: cap-builtin-kwarg-open-encoding, cap-fs-path-model | no | no (honesty wall) |
| `_set_ctx` | frontend/pure_ast.py | L3-TC unbound symbol emitted (emitter defect) `cap-emit-unbound-symbol-defect` | no | 0 (cv10) | HONESTY-WALL: cap-emit-ir-inplace-field-write | no | no (honesty wall) |
| `comments` | frontend/pure_ast.py | R: R325 opaque-int fallback `cap-R325-call-ctor-call` | no | 0 (cv10) | HONESTY-WALL: cap-R325-call-ctor-call, cap-tokenize-model | no | no (honesty wall) |
| `copy_location` | frontend/pure_ast.py | R: function/class name rebound (setattr / namespace dict wri `cap-name-rebinding-model` | no | 0 (cv10) | HONESTY-WALL: cap-dynamic-getattr-setattr | no | no (honesty wall) |
| `dump` | frontend/pure_ast.py | R: nested closure lift `cap-closure-lift` (remote:_format) | no | 1 (cv10; replay r10xh029_2: same terminal) | HONESTY-WALL: cap-dynamic-getattr-setattr, cap-tuple-unpack-alias | no | no (honesty wall) |
| `fix_missing_locations` | frontend/pure_ast.py | L3-TC int-erasure type seam `cap-vm-unerase-tuple` | no | 0 (cv10) | HONESTY-WALL: cap-dynamic-getattr-setattr, cap-generator-yield-model | no | no (honesty wall) |
| `get_source_segment` | frontend/pure_ast.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 2 (cv10; replay r10xh030_3: same terminal) | DEPTH-STOP: cap-R325-str-encoding-op, cap-bytes-value-model | no | - |
| `increment_lineno` | frontend/pure_ast.py | R: R542-NON-CONTAINER-OPERAND `cap-R542-callee-result-kind` | no | 0 (cv10) | HONESTY-WALL: cap-dynamic-getattr-setattr, cap-generator-yield-model | no | no (honesty wall) |
| `iter_child_nodes` | frontend/pure_ast.py | R: R542-NON-CONTAINER-OPERAND `cap-R542-callee-result-kind` | no | 0 (cv10) | HONESTY-WALL: cap-R542-callee-result-kind, cap-generator-yield-model | no | no (honesty wall) |
| `iter_fields` | frontend/pure_ast.py | TC-OK `none-TC-OK` | no | 0 (cv10) | TC-OK-FACADE: cap-generator-yield-model | yes | FACADE |
| `literal_eval` | frontend/pure_ast.py | R: R325 opaque-int fallback `cap-R325-str-encoding-op` (remote:_raise_malformed_node) | no | 1 (cv10; replay r10xh022_2: same terminal) | DEPTH-STOP: cap-R325-call-tuple-ctor, cap-R325-str-encoding-op, cap-closure-lift, cap-map-builtin, cap-method-recursion-cycle, cap-pyast-node-typing | no | - |
| `main` | frontend/pure_ast.py | R: hash of unknown/unhashable class `cap-hash-judge-class-set` | no | 0 (cv10) | HONESTY-WALL: cap-fs-path-model, cap-hash-judge-class-set | no | no (honesty wall) |
| `parse` | frontend/pure_ast.py | R: in-place receiver mutator `cap-inplace-mutator-extend` | no | 1 (cv10; replay r10xh021_2: same terminal) | DEPTH-STOP: cap-emit-unbound-symbol-defect, cap-pyast-dynamic-ctor, cap-tokenize-model | no | - |
| `unparse` | frontend/pure_ast.py | L3-TC effect: depends on _pyobj_state left out of spec `cap-pyobj-state-frame` | no | 0 (cv10) | DEPTH-STOP: cap-fresh-object-frame | no | - |
| `walk` | frontend/pure_ast.py | R: deque(<iterable>) unmodelled `cap-deque-iterable` | no | 1 (cv10; replay r10xh025_2: same terminal) | HONESTY-WALL: cap-generator-yield-model, cap-inplace-mutator-extend | no | no (honesty wall) |
| `validate_ir` | ir_schema.py | R: optional TypedDict key read (NotRequired, new since cv6) `cap-typeddict-optional-key` | no | 2 (cv9; replay r9xs117_3: same terminal) | DEPTH-STOP: cap-typeddict-optional-key | no | - |
| `AbstractOpsMixin._add_abstract_op` | module6_whyml/abstract_ops.py | R: in-place receiver mutator `cap-inplace-mutator-setdefault` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-setdefault, cap-self-field-alias-analysis | no | - |
| `AbstractOpsMixin._advance_past_referenced_axiom_decls` | module6_whyml/abstract_ops.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 3 (cv9; replay r9xs118_4: same terminal) | DEPTH-STOP: cap-R325-call-str-split, cap-getattr-dynamic, cap-set-iteration, cap-vm-unerase-list | no | - |
| `AbstractOpsMixin._insert_abstract_val_block` | module6_whyml/abstract_ops.py | R: R327 ident collision with an emitter-generated binder nam `cap-binder-hygiene-R327` | no | 3 (lvE) | DEPTH-STOP: cap-R314-str-method-kwarg, cap-binder-hygiene-R327, cap-inplace-mutator-insert | no | - |
| `AutoTrustMixin._build_witness_str` | module6_whyml/auto_trust.py | R: param default not of annotation kind (route #350) `cap-optional-param-default` | no | 2 (cv9; replay r9xs119_3: same terminal) | DEPTH-STOP: cap-boolop-value, cap-optional-param-default, cap-vm-unerase-union | no | - |
| `AutoTrustMixin._check_witness_vals` | module6_whyml/auto_trust.py | R: global / module-scope write `cap-global-nonlocal-write` | no | 0 (cv9) | HONESTY-WALL: cap-eval | no | no (honesty wall) |
| `AutoTrustMixin._should_auto_trust_tuple_return` | module6_whyml/auto_trust.py | R: nested closure lift `cap-closure-lift` (remote:autotrustmixin___tuple_return_has_array_slot) | no | 2 (cv9; replay r9xs121_3: same terminal) | DEPTH-STOP: cap-closure-lift, cap-vm-unerase-list | no | - |
| `GhostSpecOpsMixin._handle_ctor_payload_expr` | module6_whyml/expr_ghost_spec_ops.py | R: R563-METHOD-ARGUMENT-KIND `cap-kind-judge-list-arg` | no | 1 (cv9; replay r9xs124_2: same terminal) | DEPTH-STOP: cap-kind-judge-list-arg, cap-vm-unerase-irnode | no | - |
| `GhostSpecOpsMixin._handle_proj_expr` | module6_whyml/expr_ghost_spec_ops.py | R: R563-METHOD-ARGUMENT-KIND `cap-kind-judge-list-arg` | no | 1 (cv9; replay r9xs123_2: same terminal) | DEPTH-STOP: cap-kind-judge-list-arg, cap-vm-unerase-irnode | no | - |
| `ExpressionEmissionMixin._call_bytes_methods` | module6_whyml/expressions.py | L3-TC int-erasure type seam `cap-vm-unerase-str` | no | 3 (cv10; replay r10xh083_4: same terminal) | DEPTH-STOP: cap-R325-call-str-strip-arg, cap-vm-unerase-list | no | - |
| `ExpressionEmissionMixin._call_named_builtins` | module6_whyml/expressions.py | R: parameter rebinding in a nested block `cap-param-rebind-nested` | no | 3 (cv10; replay r10xh080_4: same terminal) | DEPTH-STOP: cap-exact-pop-model | no | - |
| `ExpressionEmissionMixin._call_record_constructor` | module6_whyml/expressions.py | R: nested closure lift `cap-closure-lift` (remote:expressionemissionmixin___field_default) | no | 3 (cv10; replay r10xh082_4: same terminal) | DEPTH-STOP: cap-elem-store-nonlist, cap-vm-unerase-dict | no | - |
| `ExpressionEmissionMixin._coerce_dotted_args` | module6_whyml/expressions.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 4 (cv10; replay r10xh072_5: same terminal) | DEPTH-STOP: cap-dict-ifexp-literal | no | - |
| `ExpressionEmissionMixin._content_string_method` | module6_whyml/expressions.py | R: in-place receiver mutator `cap-inplace-mutator-pop` | no | 4 (lvH(reused)) | DEPTH-STOP: cap-exact-pop-model, cap-inplace-mutator-extend, cap-vm-unerase-irnode | no | - |
| `ExpressionEmissionMixin._dotted_ensures_suffix` | module6_whyml/expressions.py | R: hash of unknown/unhashable class `cap-hash-judge-class-set` | no | 0 (cv10) | DEPTH-STOP: cap-hash-judge-class-set, cap-vm-unerase-tuple | no | - |
| `ExpressionEmissionMixin._emit_bitwise_or_power` | module6_whyml/expressions.py | R: computed callee erased (no effect) `cap-computed-callee` | no | 0 (cv11; replay r10xh062_4: same terminal) | TC-OK-PARTIAL: cap-vm-unerase-irnode, cap-ir-number-int-view | yes | partial |
| `ExpressionEmissionMixin._emit_membership` | module6_whyml/expressions.py | R: sorted(key=) `cap-sorted-key` | no | 2 (cv10; replay r10xh061_3: same terminal) | DEPTH-STOP: cap-sorted-key, cap-vm-unerase-irnode | no | - |
| `ExpressionEmissionMixin._expr_to_whyml` | module6_whyml/expressions.py | R: route #390 `cap-star-kwargs-call` | no | 2 (cv10; replay r10xh090_3: same terminal) | DEPTH-STOP: cap-definite-assignment-flow | no | - |
| `ExpressionEmissionMixin._expr_to_whyml_string_ctx` | module6_whyml/expressions.py | R: recursion cycle through a METHOD/constructor call `cap-method-recursion-cycle` | no | 3 (cv10; replay r10xh091_4: same terminal) | TC-OK-PARTIAL: cap-method-recursion-cycle, cap-missing-mirror-function, cap-vm-unerase-list | yes | partial |
| `ExpressionEmissionMixin._handle_attribute_expr` | module6_whyml/expressions.py | R: other `cap-refused-other` | **yes** (cv8: R: R327 ident collision with an emitter-generated binder nam) | 1 (cv11) | DEPTH-STOP: cap-binder-hygiene-R327, cap-nested-unpack-target | no | - |
| `ExpressionEmissionMixin._handle_binop` | module6_whyml/expressions.py | R: R327 ident collision with an emitter-generated binder nam `cap-binder-hygiene-R327` | no | 1 (lvE(reused)) | DEPTH-STOP: cap-identity-vs-literal | no | - |
| `ExpressionEmissionMixin._handle_call_expr` | module6_whyml/expressions.py | R: R327 ident collision with an emitter-generated binder nam `cap-binder-hygiene-R327` | no | 1 (lvE(reused)) | DEPTH-STOP: cap-tuple-unpack-alias | no | - |
| `ExpressionEmissionMixin._handle_dotted_call` | module6_whyml/expressions.py | R: slice del unmodelled `cap-slice-del` | no | 4 (cv10; replay r10xh071_5: same terminal) | DEPTH-STOP: cap-self-field-alias-analysis, cap-tuple-unpack-alias | no | - |
| `ExpressionEmissionMixin._handle_fstring_expr` | module6_whyml/expressions.py | R: identity test vs literal `cap-identity-vs-literal` | no | 2 (cv10; replay r10xh088_3: same terminal) | DEPTH-STOP: cap-R274-writing-call-in-comprehension, cap-erased-to-builtin-slot-arg, cap-identity-vs-literal | no | - |
| `ExpressionEmissionMixin._handle_ifexpr_expr` | module6_whyml/expressions.py | R: definite-assignment (read of a not-definitely-assigned lo `cap-definite-assignment-flow` | no | 3 (cv10; replay r10xh089_4: not comparable (cv10 ran it on a scratch EMITTER st2)) | DEPTH-STOP: cap-exact-pop-model, cap-inplace-mutator-extend, cap-missing-mirror-sibling, cap-r325-typepos | no | - |
| `ExpressionEmissionMixin._handle_isinstance` | module6_whyml/expressions.py | R: R523-STR-LITERAL-LIST-MUTATED `cap-R523-str-literal-list` | no | 3 (cv10; replay r10xh081_4: same terminal) | DEPTH-STOP: cap-identity-vs-literal, cap-self-field-alias-analysis, cap-vm-unerase-irnode | no | - |
| `ExpressionEmissionMixin._handle_join_call` | module6_whyml/expressions.py | R: param default not of annotation kind (route #350) `cap-optional-param-default` | no | 3 (cv10; replay r10xh068_4: same terminal) | DEPTH-STOP: cap-list-literal-none-elem, cap-vm-unerase-irnode | no | - |
| `ExpressionEmissionMixin._handle_len_call` | module6_whyml/expressions.py | R: and/or used as a VALUE on non-bool operands (new since cv `cap-boolop-value` | no | 4 (cv10; replay r10xh067_5: same terminal) | DEPTH-STOP: cap-vm-unerase-irnode | no | - |
| `ExpressionEmissionMixin._handle_struct_call` | module6_whyml/expressions.py | R: in-place receiver mutator `cap-inplace-mutator-setdefault` | no | 1 (lvH(reused)) | DEPTH-STOP: cap-R325-str-concat-opaque, cap-global-receiver-mutator, cap-inplace-mutator-setdefault | no | - |
| `ExpressionEmissionMixin._handle_subscript` | module6_whyml/expressions.py | R: R327 ident collision with an emitter-generated binder nam `cap-binder-hygiene-R327` | no | 1 (lvE(reused)) | DEPTH-STOP: cap-inplace-mutator-pop | no | - |
| `ExpressionEmissionMixin._handle_sum_call` | module6_whyml/expressions.py | L3-TC int-erasure type seam `cap-vm-unerase-str` | no | 2 (cv10; replay r10xh069_3: same terminal) | DEPTH-STOP: cap-R325-call-str-to-number, cap-vm-unerase-dict | no | - |
| `ExpressionEmissionMixin._is_emit_ir_expr` | module6_whyml/expressions.py | R: recursion cycle through a METHOD/constructor call `cap-method-recursion-cycle` | no | 3 (cv10; replay r10xh057_4: same terminal) | DEPTH-STOP: cap-method-recursion-cycle, cap-missing-mirror-sibling | no | - |
| `ExpressionEmissionMixin._is_string_expr` | module6_whyml/expressions.py | R: R274 writing call inside opaque comprehension `cap-R274-writing-call-in-comprehension` | no | 3 (cv10; replay r10xh063_4: same terminal) | DEPTH-STOP: cap-R274-writing-call-in-comprehension, cap-method-recursion-cycle | no | - |
| `ExpressionEmissionMixin._iter_len_expr` | module6_whyml/expressions.py | R: nested closure lift `cap-closure-lift` (remote:expressionemissionmixin___operand_len) | no | 3 (cv10; replay r10xh066_4: same terminal) | DEPTH-STOP: cap-method-recursion-cycle, cap-vm-unerase-irnode | no | - |
| `ExpressionEmissionMixin._linear_form` | module6_whyml/expressions.py | R: dropped unpacking / loop target (route #301) `cap-nested-unpack-target` | no | 3 (cv10; replay r10xh076_4: same terminal) | DEPTH-STOP: cap-method-recursion-cycle, cap-vm-unerase-tuple, cap-vm-unerase-union | no | - |
| `ExpressionEmissionMixin._match_pattern_cond` | module6_whyml/expressions.py | R: R542-NON-CONTAINER-OPERAND `cap-R542-container-kind` | no | 4 (cv10; replay r10xh060_5: same terminal) | DEPTH-STOP: cap-local-type-from-call, cap-method-recursion-cycle | no | - |
| `ExpressionEmissionMixin._pop_quant_binder` | module6_whyml/expressions.py | R: in-place receiver mutator `cap-inplace-mutator-pop` | no | 1 (cv10; replay r10xh087_2: same terminal) | DEPTH-STOP: cap-heterogeneous-tuple-return, cap-self-field-alias-analysis | no | - |
| `ExpressionEmissionMixin._push_quant_binder` | module6_whyml/expressions.py | R: dict alias (route #59) `cap-dict-alias` | no | 1 (cv10; replay r10xh086_2: same terminal) | DEPTH-STOP: cap-heterogeneous-tuple-return, cap-self-field-alias-analysis | no | - |
| `ExpressionEmissionMixin._resolve_dotted_signature` | module6_whyml/expressions.py | R: append to untracked list / array-local model `cap-growable-list-local` | no | 0 (cv10) | DEPTH-STOP: cap-array-local-rebind | no | - |
| `ExpressionEmissionMixin._static_width` | module6_whyml/expressions.py | R: dropped unpacking / loop target (route #301) `cap-nested-unpack-target` | no | 2 (cv10; replay r10xh077_3: same terminal) | DEPTH-STOP: cap-vm-unerase-tuple, cap-vm-unerase-union | no | - |
| `ExpressionEmissionMixin._to_bool` | module6_whyml/expressions.py | R: sorted(key=) `cap-sorted-key` | no | 0 (cv11; replay r10xh059_4: MOVED R: and/or used as a VALUE on non-bool operands (new since cv -> R: route #568) | DEPTH-STOP: cap-pyobj-state-frame-568, cap-boolop-value, cap-method-recursion-cycle | no | - |
| `ExpressionEmissionMixin._union_local_read_projection` | module6_whyml/expressions.py | L3-TC int-erasure type seam `cap-vm-unerase-union` | no | 2 (cv10; replay r10xh065_3: same terminal) | DEPTH-STOP: cap-missing-mirror-sibling, cap-optional-union-nominal | no | - |
| `FunctionEmissionMixin._emit_contracts` | module6_whyml/functions.py | R: in-place receiver mutator `cap-inplace-mutator-pop` | no | 4 (lvH(reused)) | DEPTH-STOP: cap-R325-str-concat-opaque, cap-cross-mixin-decl-stubs, cap-exact-pop-model, cap-inplace-mutator-fresh-local, cap-r325-typepos | no | - |
| `FunctionEmissionMixin._emit_function` | module6_whyml/functions.py | R: in-place receiver mutator `cap-inplace-mutator-add` | no | 1 (lvH(reused)) | DEPTH-STOP: cap-self-field-alias-analysis, cap-vm-unerase-set | no | - |
| `FunctionEmissionMixin._emit_narrowing_vc` | module6_whyml/functions.py | R: nested closure lift `cap-closure-lift` (remote:functionemissionmixin__conj) | no | 2 (cv10; replay r10xh115_3: same terminal) | DEPTH-STOP: cap-R325-str-concat-opaque, cap-vm-unerase-irnode | no | - |
| `FunctionEmissionMixin._emit_subtyping_goals` | module6_whyml/functions.py | R: METHOD-FRAME (body writes a param not in assigns) `cap-method-arg-frame` | no | 1 (cv10; replay r10xh118_2: same terminal) | DEPTH-STOP: cap-method-arg-frame | no | - |
| `FunctionEmissionMixin._emit_union_arm_vc` | module6_whyml/functions.py | R: R325 opaque-int fallback `cap-R325-str-encoding-op` | no | 1 (cv10; replay r10xh116_2: same terminal) | DEPTH-STOP: cap-vm-unerase-dict, cap-vm-unerase-irnode | no | - |
| `FunctionEmissionMixin._mixin_dep_pseudo_functions` | module6_whyml/functions.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv10; replay r10xh121_2: same terminal) | DEPTH-STOP: cap-vm-unerase-irnode | no | - |
| `FunctionEmissionMixin._param_type_str` | module6_whyml/functions.py | R: in-place receiver mutator `cap-inplace-mutator-add` | no | 2 (cv10; replay r10xh112_3: same terminal) | DEPTH-STOP: cap-self-field-alias-analysis, cap-vm-unerase-irnode | no | - |
| `FunctionEmissionMixin._parse_mixin_sig` | module6_whyml/functions.py | R: and/or used as a VALUE on non-bool operands (new since cv `cap-boolop-value` | no | 3 (cv10; replay r10xh120_4: same terminal) | DEPTH-STOP: cap-R325-call-str-split, cap-list-comp-model, cap-vm-unerase-tuple | no | - |
| `FunctionEmissionMixin._render_refinement_goal` | module6_whyml/functions.py | R: METHOD-ARG-UNFRAMED (writes an argument) `cap-method-arg-frame` (remote:functionemissionmixin___reset_function_state) | no | 0 (cv10) | DEPTH-STOP: cap-method-arg-frame | no | - |
| `FunctionEmissionMixin._reset_function_state` | module6_whyml/functions.py | R: UB-7.1 loop body mutates iterated collection `cap-iter-mutation` | no | 1 (cv10; replay r10xh113_2: same terminal) | DEPTH-STOP: cap-hash-judge-class-set | no | - |
| `stable_hash` | module6_whyml/identifiers.py | TC-OK `none-TC-OK` | no | 0 (cv9) | TC-OK-FACADE: cap-faithful-string-hash | yes | FACADE |
| `PreambleEmissionMixin._emit_class_inv_axioms` | module6_whyml/preamble.py | R: R542-NON-CONTAINER-OPERAND `cap-R542-container-kind` | no | 2 (cv9; replay r9xs128_3: same terminal) | DEPTH-STOP: cap-R325-module-constant, cap-R542-container-kind, cap-set-iteration | no | - |
| `PreambleEmissionMixin._emit_inductive_decls` | module6_whyml/preamble.py | R: nested closure lift `cap-closure-lift` (remote:preambleemissionmixin___emit_member) | no | 1 (cv9; replay r9xs135_3: same terminal) | DEPTH-STOP: cap-closure-lift, cap-vm-unerase-irnode | no | - |
| `PreambleEmissionMixin._emit_module_globals` | module6_whyml/preamble.py | R: in-place receiver mutator `cap-inplace-mutator-pop` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-fresh-local, cap-inplace-mutator-pop | no | - |
| `PreambleEmissionMixin._emit_opaque_class_aliases` | module6_whyml/preamble.py | R: in-place receiver mutator `cap-inplace-mutator-add` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-add, cap-method-arg-frame | no | - |
| `PreambleEmissionMixin._emit_preamble` | module6_whyml/preamble.py | R: append to untracked list / array-local model `cap-growable-list-local` | no | 2 (cv9; replay r9xs130_3: same terminal) | DEPTH-STOP: cap-growable-list-local, cap-kind-judge-list-arg, cap-vm-unerase-dict | no | - |
| `PreambleEmissionMixin._emit_preamble_axioms` | module6_whyml/preamble.py | R: R542-NON-CONTAINER-OPERAND `cap-R542-container-kind` | no | 2 (cv9; replay r9xs129_3: same terminal) | DEPTH-STOP: cap-R325-call-set-ctor, cap-R542-container-kind, cap-inplace-mutator-add | no | - |
| `PreambleEmissionMixin._emit_preamble_exceptions` | module6_whyml/preamble.py | R: R542-NON-CONTAINER-OPERAND `cap-R542-container-kind` | no | 2 (cv9; replay r9xs127_3: same terminal) | DEPTH-STOP: cap-R542-container-kind, cap-erased-to-builtin-slot-arg, cap-vm-unerase-irnode | no | - |
| `PreambleEmissionMixin._emit_preamble_uses` | module6_whyml/preamble.py | R: R327 ident collision with an emitter-generated binder nam `cap-binder-hygiene-R327` | no | 3 (lvE) | DEPTH-STOP: cap-R325-call-other, cap-R542-container-kind, cap-binder-hygiene-R327 | no | - |
| `PreambleEmissionMixin._emit_shared_state` | module6_whyml/preamble.py | R: tuple-unpack alias `cap-tuple-unpack-alias` | no | 1 (cv9; replay r9xs131_2: same terminal) | DEPTH-STOP: cap-R325-call-other, cap-tuple-unpack-alias, cap-vm-unerase-irnode | no | - |
| `PreambleEmissionMixin._emit_type_decls` | module6_whyml/preamble.py | R: hash of unknown/unhashable class `cap-hash-judge-class-set` | no | 2 (cv9; replay r9xs138_3: same terminal) | DEPTH-STOP: cap-binder-hygiene-R327, cap-hash-judge-class-set, cap-nested-unpack-target | no | - |
| `PreambleEmissionMixin._emit_uncited_axiom_func_decls` | module6_whyml/preamble.py | R: R325 opaque-int fallback `cap-R325-call-set-ctor` | no | 2 (cv9; replay r9xs134_3: same terminal) | DEPTH-STOP: cap-R325-call-set-ctor, cap-R325-call-str-split, cap-getattr-dynamic, cap-inplace-mutator-discard | no | - |
| `PreambleEmissionMixin._fresh_globals_facts` | module6_whyml/preamble.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv9; replay r9xs137_2: same terminal) | DEPTH-STOP: cap-iterable-termination-variant, cap-vm-unerase-irnode | no | - |
| `PreambleEmissionMixin._inductive_referenced_axiom_decls` | module6_whyml/preamble.py | R: R325 opaque-int fallback `cap-R325-call-str-split` | no | 1 (cv9; replay r9xs133_2: same terminal) | DEPTH-STOP: cap-R325-call-str-split, cap-getattr-dynamic | no | - |
| `PreambleEmissionMixin._mutex_inv_application` | module6_whyml/preamble.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv9; replay r9xs132_2: same terminal) | DEPTH-STOP: cap-vm-unerase-list | no | - |
| `PreambleEmissionMixin._precompute_axiom_logic_funcs` | module6_whyml/preamble.py | R: in-place receiver mutator `cap-inplace-mutator-add` | no | 2 (lvB) | DEPTH-STOP: cap-inplace-mutator-add, cap-inplace-mutator-fresh-local | no | - |
| `PreambleEmissionMixin._scan_preamble_needs` | module6_whyml/preamble.py | R: function/class name rebound (setattr / namespace dict wri `cap-name-rebinding-model` | no | 0 (cv9) | DEPTH-STOP: cap-name-rebinding-model | no | - |
| `PreambleEmissionMixin._subst_self_in_expr` | module6_whyml/preamble.py | R: nested closure lift `cap-closure-lift` (remote:preambleemissionmixin__rec) | no | 0 (cv9) | HONESTY-WALL: cap-closure-lift, cap-vm-unerase-irnode | no | no (honesty wall) |
| `compute_sccs` | module6_whyml/scc.py | R: nested closure lift `cap-closure-lift` (remote:strongconnect) | no | 0 (cv9) | DEPTH-STOP: cap-closure-lift, cap-global-nonlocal-write, cap-method-recursion-cycle | no | - |
| `sort_functions_by_scc` | module6_whyml/scc.py | R: append to untracked list / array-local model `cap-growable-list-local` | no | 4 (cv9; replay r9xs140_5: same terminal) | DEPTH-STOP: cap-R325-call-set-ctor, cap-vm-unerase-irnode | no | - |
| `StatementEmissionMixin._emit_body_code` | module6_whyml/statements.py | R: R327 ident collision with an emitter-generated binder nam `cap-binder-hygiene-R327` | no | 1 (lvE(reused)) | DEPTH-STOP: cap-dict-alias | no | - |
| `StatementEmissionMixin._emit_first_assign` | module6_whyml/statements.py | R: parameter rebinding in a nested block `cap-param-rebind-nested` | no | 3 (cv10; replay r10xh096_4: same terminal) | DEPTH-STOP: cap-dict-ifexp-literal, cap-vm-unerase-irnode | no | - |
| `StatementEmissionMixin._emit_frame_condition` | module6_whyml/statements.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 3 (cv10; replay r10xh105_4: same terminal) | DEPTH-STOP: cap-vm-unerase-irnode, cap-vm-unerase-list | no | - |
| `StatementEmissionMixin._expr_to_whyml` | module6_whyml/statements.py | PORT-ABORT: no live def (mixin sibling interface stub) `none-mixin-interface-stub` | no | 0 (cv11) | DECL-ONE-CAP: cap-none-default-map-param | no (1 emitter fix) | - |
| `StatementEmissionMixin._handle_array_set_stmt` | module6_whyml/statements.py | R: R327 ident collision with an emitter-generated binder nam `cap-binder-hygiene-R327` | no | 1 (lvE(reused)) | DEPTH-STOP: cap-boolop-value | no | - |
| `StatementEmissionMixin._handle_assign_stmt` | module6_whyml/statements.py | R: definite-assignment (read of a not-definitely-assigned lo `cap-definite-assignment-flow` | no | 2 (cv10; replay r10xh097_3: same terminal) | DEPTH-STOP: cap-dict-alias | no | - |
| `StatementEmissionMixin._handle_expr_stmt` | module6_whyml/statements.py | R: definite-assignment (read of a not-definitely-assigned lo `cap-definite-assignment-flow` | no | 2 (cv10; replay r10xh103_3: same terminal) | DEPTH-STOP: cap-identity-vs-literal | no | - |
| `StatementEmissionMixin._handle_ghost_assign_stmt` | module6_whyml/statements.py | R: dict alias (route #59) `cap-dict-alias` (remote:statementemissionmixin___handle_array_slice_set_stmt) | no | 0 (cv10) | DEPTH-STOP: cap-dict-alias | no | - |
| `StatementEmissionMixin._handle_return_stmt` | module6_whyml/statements.py | PORT-ABORT: no live def (mixin sibling interface stub) `none-mixin-interface-stub` | no | 0 (cv10) | DECL-FAIL: cap-base-override-refines | no | - |
| `StatementEmissionMixin._handle_tuple_unpack_stmt` | module6_whyml/statements.py | R: dict alias (route #59) `cap-dict-alias` (remote:statementemissionmixin___handle_array_slice_set_stmt) | no | 0 (cv10) | DEPTH-STOP: cap-dict-alias | no | - |
| `StatementEmissionMixin._seq_init_expr` | module6_whyml/statements.py | R: route #568 `cap-pyobj-state-frame-568` | **yes** (cv8: R: R274 writing call inside opaque comprehension) | 0 (cv11; replay r10xh098_4: MOVED L3-TC record/ADT vs emit_ir clash (non-int) -> R: route #568) | DEPTH-STOP: cap-pyobj-state-frame-568, cap-missing-mirror-function, cap-optional-union-nominal | no | - |
| `StatementEmissionMixin._stmts_to_whyml` | module6_whyml/statements.py | R: hash of unknown/unhashable class `cap-hash-judge-class-set` | no | 2 (cv10; replay r10xh104_3: same terminal) | DEPTH-STOP: cap-dict-alias, cap-identity-vs-literal | no | - |
| `StatementEmissionMixin._track_collection_metadata` | module6_whyml/statements.py | PORT-ABORT: no live def (mixin sibling interface stub) `none-mixin-interface-stub` | no | 0 (cv11) | DECL-FAIL: decision-widen-15-frames | no | - |
| `StatementEmissionMixin._typed_local_vars` | module6_whyml/statements.py | R: hash of unknown/unhashable class `cap-hash-judge-class-set` | no | 3 (cv10; replay r10xh106_4: same terminal) | DEPTH-STOP: cap-binder-hygiene-R327 | no | - |
| `ControlFlowStmtMixin._callee_raised_in` | module6_whyml/stmt_control_flow.py | R: recursion cycle through a METHOD/constructor call `cap-method-recursion-cycle` | no | 3 (cv10; replay r10xh110_4: not comparable (cv10 ran it on a scratch EMITTER st2)) | DEPTH-STOP: cap-method-recursion-cycle, cap-r325-typepos, cap-vm-unerase-list | no | - |
| `ControlFlowStmtMixin._classify_iterable` | module6_whyml/stmt_control_flow.py | R: identity test vs literal `cap-identity-vs-literal` | no | 2 (cv10; replay r10xh108_3: same terminal) | DEPTH-STOP: cap-R506-trigger-site | no | - |
| `ControlFlowStmtMixin._handle_for_stmt` | module6_whyml/stmt_control_flow.py | R: hash of unknown/unhashable class `cap-hash-judge-class-set` | no | 2 (cv10; replay r10xh109_3: same terminal) | DEPTH-STOP: cap-none-default-map-param, cap-vm-unerase-irnode | no | - |
| `ControlFlowStmtMixin._handle_match_stmt` | module6_whyml/stmt_control_flow.py | R: R566-EMITIR-ITEM-STORE `cap-emit-ir-item-store-model` | new stub | 0 (cv11) | DEPTH-STOP: cap-emit-ir-item-store-model, cap-vm-unerase-str | no | - |
| `ControlFlowStmtMixin._render_match_pattern` | module6_whyml/stmt_control_flow.py | R: global / module-scope write `cap-global-nonlocal-write` | no | 1 (cv10; replay r10xh111_2: same terminal) | DEPTH-STOP: cap-method-recursion-cycle, cap-poison-marker-literal | no | - |
| `calcsize` | module6_whyml/struct_format.py | L3-TC int-erasure type seam `cap-vm-unerase-str` | no | 0 (cv11) | HONESTY-WALL: cap-re-match-model, cap-vm-unerase-dict | no | no (honesty wall) |
| `parse_format` | module6_whyml/struct_format.py | R: ctor unexpected keyword (route #369, new since cv6) `cap-ctor-kwargs` | no | 4 (cv9; replay r9xs141_5: same terminal) | HONESTY-WALL: cap-re-match-model, cap-return-exn-nonint, cap-vm-unerase-tuple | no | no (honesty wall) |
| `TypeInferenceMixin._collect_array_var_assigns` | module6_whyml/types.py | R: dropped unpacking / loop target (route #301) `cap-nested-unpack-target` | no | 1 (cv9; replay r9xs142_2: same terminal) | DEPTH-STOP: cap-R325-call-set-ctor, cap-inplace-mutator-add, cap-nested-unpack-target | no | - |
| `TypeInferenceMixin._track_collection_metadata` | module6_whyml/types.py | R: R327 ident collision with an emitter-generated binder nam `cap-binder-hygiene-R327` | no | 2 (lvE) | DEPTH-STOP: cap-binder-hygiene-R327, cap-dict-alias | no | - |
| `_load_axiom_registry` | proof2why3/crosscheck.py | L3-TC int-erasure type seam `cap-vm-unerase-str` | no | 3 (lvA) | HONESTY-WALL: cap-fs-path-model, cap-stdlib-ast-model, cap-vm-unerase-str | no | no (honesty wall) |
| `crosscheck_file` | proof2why3/crosscheck.py | R: sorted(key=) `cap-sorted-key` | no | 4 (lvA) | HONESTY-WALL: cap-R325-call-subprocess, cap-fs-path-model, cap-sorted-key, cap-vm-unerase-dict | no | no (honesty wall) |
| `main` | proof2why3/crosscheck.py | R: parameter rebinding in a nested block `cap-param-rebind-nested` | no | 0 (cv11) | HONESTY-WALL: cap-param-rebind-nested, cap-argparse-model, cap-fs-path-model, cap-stdout-model | no | no (honesty wall) |
| `IRCrossCheckResult.diagnostic` | proof2why3/crosscheck_ir.py | R: R489 implicit dunder through inferred frame (new since cv `cap-R489-implicit-dunder` | no | 1 (lvA) | DEPTH-STOP: cap-R489-implicit-dunder | no | - |
| `IRCrossCheckResult.pairwise` | proof2why3/crosscheck_ir.py | L3-TC int-erasure type seam `cap-vm-unerase-scalar` | no | 0 (cv11) | DEPTH-STOP: cap-closure-lift, cap-vm-unerase-dict, cap-term-equality-model | no | - |
| `_load_axiom_registry` | proof2why3/crosscheck_ir.py | L3-TC int-erasure type seam `cap-vm-unerase-str` | no | 3 (lvA) | HONESTY-WALL: cap-fs-path-model, cap-stdlib-ast-model, cap-vm-unerase-str | no | no (honesty wall) |
| `crosscheck_file_ir` | proof2why3/crosscheck_ir.py | R: sorted(key=) `cap-sorted-key` | no | 4 (lvA) | HONESTY-WALL: cap-R325-call-subprocess, cap-fs-path-model, cap-sorted-key, cap-vm-unerase-dict | no | no (honesty wall) |
| `main` | proof2why3/crosscheck_ir.py | R: hash of unknown/unhashable class `cap-hash-judge-class-set` | no | 0 (cv11) | HONESTY-WALL: cap-hash-judge-class-set, cap-argparse-model, cap-fs-path-model, cap-stdout-model | no | no (honesty wall) |
| `extract_lean_statements` | proof2why3/extract.py | R: definite-assignment (read of a not-definitely-assigned lo `cap-definite-assignment-flow` | no | 2 (lvA) | HONESTY-WALL: cap-R325-call-subprocess, cap-context-manager-model | no | no (honesty wall) |
| `extract_rocq_statements` | proof2why3/extract.py | R: definite-assignment (read of a not-definitely-assigned lo `cap-definite-assignment-flow` | no | 2 (lvA) | HONESTY-WALL: cap-R325-call-subprocess, cap-context-manager-model | no | no (honesty wall) |
| `extract_lean_statements_meta` | proof2why3/extract_lean_meta.py | R: heterogeneous list literal `cap-heterogeneous-list` | no | 0 (cv11) | HONESTY-WALL: cap-heterogeneous-list, cap-R325-call-subprocess, cap-json-model | no | no (honesty wall) |
| `_is_ofnat_lit` | proof2why3/from_lean_json.py | L3-TC int-erasure type seam `cap-vm-unerase-dict` | no | 0 (cv11) | DEPTH-STOP: cap-vm-unerase-dict, cap-vm-unerase-tuple, cap-int-of-str-model | no | - |
| `_linearize_app` | proof2why3/from_lean_json.py | R: in-place receiver mutator `cap-inplace-mutator-insert` | no | 0 (cv11) | DEPTH-STOP: cap-inplace-mutator-insert, cap-vm-unerase-dict, cap-vm-unerase-tuple | no | - |
| `project_to_ir` | proof2why3/from_lean_json.py | R: parameter rebinding in a nested block `cap-param-rebind-nested` | no | 0 (cv11) | DEPTH-STOP: cap-param-rebind-nested, cap-vm-unerase-dict, cap-method-recursion-cycle | no | - |
| `_construct_indices` | proof2why3/from_sexp.py | R: non-int value returned from an int-annotated function (ne `cap-vm-unerase-return-kind` | no | 0 (cv11) | DEPTH-STOP: cap-vm-unerase-return-kind, cap-sexp-tuple-value-model | no | - |
| `_find_construct_idx` | proof2why3/from_sexp.py | R: non-int value returned from an int-annotated function (ne `cap-vm-unerase-return-kind` | no | 0 (cv11) | DEPTH-STOP: cap-vm-unerase-return-kind, cap-sexp-tuple-value-model, cap-method-recursion-cycle | no | - |
| `_project_app` | proof2why3/from_sexp.py | R: R542-NON-CONTAINER-OPERAND `cap-R542-container-kind` | no | 0 (cv11) | DEPTH-STOP: cap-R542-container-kind, cap-sexp-tuple-value-model | no | - |
| `project_constr` | proof2why3/from_sexp.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 0 (cv11) | DEPTH-STOP: cap-erased-to-builtin-slot-arg, cap-sexp-tuple-value-model, cap-method-recursion-cycle | no | - |
| `_alpha_rename` | proof2why3/normalize.py | R: sorted(key=) `cap-sorted-key` | no | 5 (lvA) | DEPTH-STOP: cap-R325-call-str-split, cap-re-escape, cap-re-match-model, cap-sorted-key, cap-vm-unerase-dict | no | - |
| `_expand_anon_binders` | proof2why3/normalize.py | TC-OK `none-TC-OK` | **yes** (cv8: R: R325 opaque-int fallback) | 0 (cv11) | REFUSED-termination: cap-diverges | no | - |
| `_nat_to_int_with_sidecond` | proof2why3/normalize.py | R: R325 opaque-int fallback `cap-R325-call-re` (remote:_strip_all_parens) | **yes** (cv8: L3-TC int-erasure type seam) | 3 (lvA) | HONESTY-WALL: cap-re-compiled, cap-re-match-model, cap-re-named-def-callable | no | no (honesty wall) |
| `normalize_surface` | proof2why3/parser.py | L3-TC int-erasure type seam `cap-vm-unerase-str` | no | 3 (lvA) | REFUSED-termination: cap-diverges, cap-optstr-sentinel, cap-pair-unroll | no | - |
| `parse_type_expr` | proof2why3/parser.py | R: exception object read (route #233) `cap-exception-object-read` | no | 0 (cv11) | DEPTH-STOP: cap-exception-object-read, cap-exception-payload-model | no | - |
| `SertopSession.type_of_batch` | proof2why3/sertop.py | R: R325 opaque-int fallback `cap-R325-call-pathlib` | no | 0 (cv11) | HONESTY-WALL: cap-R325-call-pathlib, cap-R325-call-subprocess | no | no (honesty wall) |
| `_sexp_parse` | proof2why3/sertop.py | R: in-place receiver mutator `cap-inplace-mutator-pop` | no | 0 (cv11) | DEPTH-STOP: cap-exact-pop-model, cap-vm-unerase-list, cap-sexp-tuple-value-model | no | - |
| `_sexp_tokens` | proof2why3/sertop.py | TC-OK `none-TC-OK` | no | 2 (lvA) | HONESTY-WALL: cap-generator-sequence-model, cap-loop-variants-only | no | no (honesty wall) |
| `extract_via_sertop` | proof2why3/sertop.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 0 (cv11) | HONESTY-WALL: cap-vm-unerase-list, cap-R325-call-subprocess | no | no (honesty wall) |
| `parse_sexp` | proof2why3/sertop.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 0 (cv11) | DEPTH-STOP: cap-vm-unerase-list, cap-sexp-tuple-value-model | no | - |
| `run_sertop_batch` | proof2why3/sertop.py | R: except reachable by unmodelled exception (route #174, new `cap-exception-hierarchy-model` | no | 0 (cv11) | HONESTY-WALL: cap-exception-hierarchy-model, cap-R325-call-subprocess | no | no (honesty wall) |
| `sertop_version` | proof2why3/sertop.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 0 (cv11) | HONESTY-WALL: cap-vm-unerase-list, cap-R325-call-subprocess | no | no (honesty wall) |
| `parse_rocq_assumptions_block` | proof_axiom_allowlist.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv9; replay r9xs143_3: same terminal) | DEPTH-STOP: cap-return-exn-nonint, cap-vm-unerase-str | no | - |
| `_build_soundness_report` | pycsl.py | R: hash of unknown/unhashable class `cap-hash-judge-class-set` | no | 1 (cv9; replay r9xs149_2: same terminal) | DEPTH-STOP: cap-hash-judge-class-set, cap-vm-unerase-irnode | no | - |
| `_check_rocq_proofs` | pycsl.py | R: heterogeneous list literal `cap-heterogeneous-list` | no | 0 (cv9) | HONESTY-WALL: cap-R325-call-subprocess, cap-fs-path-model, cap-heterogeneous-list | no | no (honesty wall) |
| `_dispatch_provers` | pycsl.py | R: nested closure lift `cap-closure-lift` (remote:_finalize) | no | 0 (cv9) | HONESTY-WALL: cap-R325-call-subprocess, cap-closure-lift | no | no (honesty wall) |
| `_dispatch_provers._finalize` | pycsl.py | TC-OK `none-TC-OK` | new stub | 0 (cv11) | MERGED: - | no | (with parent) |
| `_find_coqc` | pycsl.py | L3-TC int-erasure type seam `cap-vm-unerase-union` | no | 0 (cv9) | HONESTY-WALL: cap-fs-path-model, cap-vm-unerase-union | no | no (honesty wall) |
| `_function_body_eqs` | pycsl.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv9; replay r9xs160_2: same terminal) | HONESTY-WALL: cap-re-match-model, cap-vm-unerase-list, cap-vm-unerase-union | no | no (honesty wall) |
| `_generate_rocq_obligations` | pycsl.py | R: `with ... as` binding unmodelled (context-manager model) `cap-context-manager-model` | no | 1 (cv9; replay r9xs144_2: same terminal) | HONESTY-WALL: cap-context-manager-model, cap-fs-path-model | no | no (honesty wall) |
| `_json_goal_records` | pycsl.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv9; replay r9xs155_2: same terminal) | DEPTH-STOP: cap-list-comp-model, cap-vm-unerase-list | no | - |
| `_merge_records_best_of_n` | pycsl.py | L3-TC int-erasure type seam `cap-vm-unerase-dict` | no | 0 (cv9) | DEPTH-STOP: cap-vm-unerase-dict, cap-vm-unerase-list | no | - |
| `_parse_args` | pycsl.py | TC-OK `none-TC-OK` | no | 0 (cv9) | TC-OK-FACADE: cap-argparse-model | yes | FACADE |
| `_parse_goal_blocks` | pycsl.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 1 (cv9; replay r9xs153_2: same terminal) | DEPTH-STOP: cap-str-join-array, cap-vm-unerase-list | no | - |
| `_parse_why3_json` | pycsl.py | R: tuple-unpack alias `cap-tuple-unpack-alias` | no | 1 (cv9; replay r9xs154_2: same terminal) | HONESTY-WALL: cap-inplace-mutator-extend, cap-json-model, cap-tuple-unpack-alias | no | no (honesty wall) |
| `_print_soundness_report` | pycsl.py | R: and/or used as a VALUE on non-bool operands (new since cv `cap-boolop-value` | no | 1 (cv9; replay r9xs150_2: same terminal) | HONESTY-WALL: cap-boolop-value, cap-json-model, cap-stdout-model | no | no (honesty wall) |
| `_record_key` | pycsl.py | L3-TC int-erasure type seam `cap-vm-unerase-list` | no | 0 (cv9) | DEPTH-STOP: cap-vm-unerase-dict | no | - |
| `_residual_selectors_from_records` | pycsl.py | R: R325 opaque-int fallback `cap-R325-str-encoding-op` | no | 0 (cv9) | DEPTH-STOP: cap-R325-call-set-ctor, cap-inplace-mutator-add, cap-vm-unerase-dict, cap-vm-unerase-union | no | - |
| `_resolve_runtime_config` | pycsl.py | R: `with ... as` binding unmodelled (context-manager model) `cap-context-manager-model` | no | 1 (cv9; replay r9xs170_2: same terminal) | HONESTY-WALL: cap-context-manager-model, cap-fs-path-model, cap-json-model | no | no (honesty wall) |
| `_run_audit_mode` | pycsl.py | R: erased value into builtin-typed slot `cap-erased-to-builtin-slot-arg` | no | 0 (cv9) | HONESTY-WALL: cap-argparse-model, cap-erased-to-builtin-slot-arg, cap-fs-path-model | no | no (honesty wall) |
| `_run_pipeline` | pycsl.py | R: function/class name rebound (setattr / namespace dict wri `cap-name-rebinding-model` | no | 0 (cv9) | DEPTH-STOP: cap-name-rebinding-model | no | - |
| `_run_proofs` | pycsl.py | R: nested closure lift `cap-closure-lift` (remote:_gate_vacuity_then_succeed) | no | 0 (cv9) | HONESTY-WALL: cap-R325-call-subprocess, cap-argparse-model, cap-closure-lift | no | no (honesty wall) |
| `_run_proofs._gate_vacuity_then_succeed` | pycsl.py | TC-OK `none-TC-OK` | new stub | 0 (cv11) | MERGED: - | no | (with parent) |
| `_run_vacuity_gate` | pycsl.py | R: `with ... as` binding unmodelled (context-manager model) `cap-context-manager-model` | no | 1 (cv9; replay r9xs161_2: same terminal) | HONESTY-WALL: cap-R325-call-subprocess, cap-closure-lift, cap-context-manager-model | no | no (honesty wall) |
| `_run_vacuity_gate._probe_one` | pycsl.py | R: tuple-unpack alias `cap-tuple-unpack-alias` | new stub | 0 (cv11) | MERGED: - | no | (with parent) |
| `_run_vacuity_gate._probe_one._is_false_goal` | pycsl.py | TC-OK `none-TC-OK` | new stub | 0 (cv11) | MERGED: - | no | (with parent) |
| `_run_why3_prove` | pycsl.py | R: heterogeneous list literal `cap-heterogeneous-list` | no | 0 (cv9) | HONESTY-WALL: cap-R325-call-subprocess, cap-heterogeneous-list | no | no (honesty wall) |
| `_sha256_file` | pycsl.py | R: `with ... as` binding unmodelled (context-manager model) `cap-context-manager-model` | no | 1 (cv9; replay r9xs145_2: same terminal) | HONESTY-WALL: cap-context-manager-model, cap-fs-path-model, cap-hashlib-model, cap-inplace-mutator-update | no | no (honesty wall) |
| `_synthesize_block` | pycsl.py | R: and/or used as a VALUE on non-bool operands (new since cv `cap-boolop-value` | no | 0 (cv9) | DEPTH-STOP: cap-boolop-value, cap-fstring-float-format, cap-vm-unerase-dict | no | - |
| `_synthesize_legacy_text` | pycsl.py | L3-TC int-erasure type seam `cap-vm-unerase-str` | no | 2 (cv11) | DEPTH-STOP: cap-vm-unerase-list | no | - |
| `_why3_typecheck` | pycsl.py | R: R325 opaque-int fallback `cap-R325-call-subprocess` | no | 0 (cv9) | HONESTY-WALL: cap-R325-call-subprocess | no | no (honesty wall) |
| `main` | pycsl.py | R: definite-assignment (read of a not-definitely-assigned lo `cap-definite-assignment-flow` | no | 0 (cv9) | HONESTY-WALL: cap-argparse-model, cap-definite-assignment-flow, cap-fs-path-model | no | no (honesty wall) |


## 4. Lever evaluations (brief point 5) and the `declared_in` swaps (point 6)

Yields below are set-cover yields over the merged chains (§3): "completes alone" = closed chains whose every non-free
need is inside the lever; "+1" = closed chains with exactly one need outside it (the best partners).

| lever | stubs whose chain needs it | completes ALONE (closed chains, nothing else unbuilt) | completes with ONE more capability (best partner) |
|---|---:|---|---|
| (i) stdlib models (fs/subprocess/json/hashlib/argparse/stdout via src/pycsl_lib) | 49 | 8: `_cache_load`, `_cache_root`, `_cache_store`, `_coqc_version`, `_lean_version`, `SertopSession.type_of_batch`, `_parse_args`, `_why3_typecheck` | `cap-context-manager-model` +4 (`extract_lean_statements`, `extract_rocq_statements`, `_generate_rocq_obligations`, `_resolve_runtime_config`); `cap-heterogeneous-list` +3 (`extract_lean_statements_meta`, `_check_rocq_proofs`, `_run_why3_prove`); `cap-hash-judge-class-set` +2 (`main`, `main`) |
| (ii-a) vm-irnode R1 narrowing view only | 11 | 6: `PyCSLToJSONEmitter._collect_final_registry`, `PyCSLToJSONEmitter._collect_type_params`, `PyCSLToJSONEmitter._collect_typevar_registry`, `PyCSLToJSONEmitter._const_int_value`, `PyCSLToJSONEmitter._m5_get_type_name_legacy`, `PyCSLToJSONEmitter._union_arm_tag` | - |
| (ii-a) vm-irnode R1+R2+R3 (narrowing view + record arm + typed IR dict/TypedDict views + List[ExprIR]/IR-list wiring + item store) | 73 | 7: `PyCSLToJSONEmitter._collect_final_registry`, `PyCSLToJSONEmitter._collect_type_params`, `PyCSLToJSONEmitter._collect_typevar_registry`, `PyCSLToJSONEmitter._const_int_value`, `PyCSLToJSONEmitter._m5_get_type_name_legacy`, `PyCSLToJSONEmitter._union_arm_tag`, `ExpressionEmissionMixin._emit_bitwise_or_power` | `cap-r325-typepos` +1 (`_rewrite_subscript_to_name`); `cap-closure-lift` +1 (`PreambleEmissionMixin._subst_self_in_expr`) |
| (ii-b) mutator lowering: lvB fresh-local havoc + whole-module self-field alias analysis + exact pop() + set() model | 82 | 0 | `cap-effectful-callback` +1 (`_Unparser.write`); `cap-generator-yield-model` +1 (`walk`) |
| (ii-c) str seam (str locals/lists, split/join/encode, f-string formats, faithful hash) | 28 | 1: `stable_hash` | `cap-fs-path-model` +1 (`_stub_set`) |
| (ii-d) genexp-sum | 1 | 0 | - |
| (ii-e) method-recursion-cycle / termination (structural measure; \diverges) | 34 | 1: `_expand_anon_binders` | `cap-vm-unerase-list` +1 (`_Harvester._emit_suite`); `cap-dataclass-reflection` +1 (`Module3_Weaver._subst_csl_param`); `cap-R325-call-ast-walk` +1 (`_try_reaches_assert`) |

### 4.1 (i) `src/pycsl_lib` stdlib models for the external-world stubs: NOT reachable soundly, and not input-reading where reached

Measured on HEAD (probes `s353_L1a/L1b/L1b2`, `s022_L1c`, `s132_L1c`, `s373_L1d/L1d2`, `s360_L1e/L1e2/L1e4`,
`s376_L1f`, `s024_L1f`; notes in `scratchpad/cv11/lever_notes.md`):

| probe | stub | how the model was reached | result |
|---|---|---|---|
| s353_L1a | pycsl `_find_coqc` | mirror unchanged, extra `--import-path src/pycsl_lib` | **REFUSED** `PYCSL-SEM-IMPORT-SHADOWS-STDLIB` (route #326) at `import json`: a local `json/` that is not the interpreter's own source may not stand in for the stdlib. By design: under `--import-path`, `import os/json/...` can never resolve to `pycsl_lib`. |
| s353_L1b | `_find_coqc` | mirror import rewritten `import pycsl_lib.os as os` (a mirror-only import change: it names a module CPython does not run) | the model IS reached (`access !opam_coqc (get_X_OK os) ..` calls `pycsl_lib.os.access`); next R325 on the module constant `os.X_OK` through the alias |
| s353_L1b2 | `_find_coqc` | + `os.X_OK` -> `1` | **REFUSED R489 inside the model itself** (`UnixInodeFileSystem.__init__` is a bodyless val with an inferred frame; implicit dunder via `load_host_dir`): the os model does not pass today's front-end when imported |
| s022_L1c | audit_proof_reverify `_cache_root` | `from pycsl_lib.plib import Path` | REFUSED: the dataclass member `ReverifyReport.proof_file: Path` cannot be resolved |
| s132_L1c | import_classifier `_stub_set` | `from pycsl_lib.plib import Path` | TC-OK but **FACADE** (`raise (Return (any int))` / `set_comp 0`: plib has no `iterdir`, the comprehension is erased) |
| s373_L1d, L1d2 | pycsl `_sha256_file` | `import pycsl_lib.hlib as hashlib` | `with open(..) as f` (context manager) -> stand-in -> `h.update(..)` in-place mutator refusal (`Sha256.update` mutates its receiver) |
| s360_L1e..L1e4 | pycsl `_parse_why3_json` | `import pycsl_lib.json as _json` | tuple-unpack alias -> [R] -> `out.extend(<genexp>)` -> [R] loop -> R325 on `list` inside `pv_size` (the decoded-pyval list model): 4 links, still walled |
| s376_L1f, s024_L1f | `_why3_typecheck`, `_coqc_version` | `import pycsl_lib.subproc as subprocess` | REFUSED arity: the model is `run(args, capture_output, check)` (no defaults, no `text=`/`timeout=`/`cwd=`, no `stdout`) |

**Faithfulness of the models (read, not argued):** `pycsl_lib/os/path.py` `expanduser` is the identity, `isfile`
always returns False, `exists`/`isdir` are constants; `pycsl_lib/os/__init__.py` instantiates ONE fresh virtual disk
(`_filesystem = UnixInodeFileSystem()`, 32 inodes, 256 blocks); every `plib.Path` method returns `int`
(`read_text -> int`); `subproc.run` models only `returncode >= 0`; `hlib` digests are `list`. The
`import_classifier.py` docstring already records that nine of these packages "carry the real stdlib module's NAME over
an integer model whose contracts pin constants". **Verdict: NO.** Route #326 (correctly) refuses them under
`--import-path`; aliasing them in by a mirror import rewrite reaches a closed-world simulation whose facts are false of
the real host (a converted `_find_coqc` would "prove" it never returns the opam path), so it would make the
external-world stubs neither honest nor sound. The ~31 external-world stubs stay conversion targets, but their capability
is a NEW faithful, open-world model per effect (filesystem reads as an uninterpreted, havoc'd world state; subprocess
results as fresh unconstrained values with the observable fields typed; json as the pyval model), each XL. Even then
the set cover gives the external family 8 completions alone (the `_cache_*` / `*_version` / `_parse_args` /
`type_of_batch` / `_why3_typecheck` rows of §4 table), most of them input-blind beyond the world value.

### 4.2 (ii-a) vm-irnode reopenings R1 / R2 / R3

- **R1, the non-IR narrowing view: 6 conversions, the best single capability of this census.** The 6 Module5 bodies
  lvG2 re-trusted when the #567 mirror exemption was rejected (`_collect_final_registry`, `_collect_type_params` (#574),
  `_collect_typevar_registry`, `_const_int_value`, `_m5_get_type_name_legacy`, `_union_arm_tag`) are REFUSED R567 at HEAD
  and **TC-OK in `stR1`** (probes `s098_X1` .. `s124_X1`), a scratch tree where lvG2's removal commit 012547a1e is
  reverse-applied, i.e. the old narrowing of `ast.*` reads on an `isinstance`-tested `emit_ir` value. The emission is
  input-reading (`isinstance(elt, ast.Name)` -> `is_var elt`, `elt.id` -> `name_of elt`), and these exact bodies were
  proved whole-file before lvG2. What the capability must be to be acceptable (the user rejected the PATH-keyed
  exemption): the same narrowing decided per RECEIVER (the value's static class is an `ast.*` node class modelled as
  `emit_ir`, never a record-modelled class: `_parse_quantifier`'s `domain.kind` stays refused, probe `s063_X1`), plus
  #574's two-way alias closure for `_collect_type_params`. Cost: Module5 whole-file (~2.5 h) once; build M; risk med (it
  re-opens the #567 misprojection surface, so the per-receiver rule needs its own red-team pass).
- **R1 record arm (DictView-style narrowing for record classes): 0 completions** (`_parse_quantifier`, `_region_bound_str`,
  `_csl_in` all have further walls: callable values, Optional unions, the `act_name` store).
- **R2 typed TypedDict / IR-dict views (FunctionView) and R3 `List[ExprIR]` wiring: 1 completion together**
  (`_emit_bitwise_or_power`, which additionally needs the IR Number int view lvI hit at proof time). `cap-vm-unerase-irnode`
  sits on 56 chains but is the LAST missing piece of only that one; the item-store model (#566) completes 0
  (`_csl_list_to_ir` and `_handle_match_stmt` hit a second value-model wall in `stR1`, probes `s104_X1`, `s312_X1`).
  The whole R1+R2+R3 bundle is on 73 chains and completes 7 (the 6 R1 rows + `_emit_bitwise_or_power`).


### 4.3 (ii-b) The mutator lowering held on `run5-lvB` (+ self-field alias analysis, exact pop(), set() model)

**Measured at HEAD.** `stlvb` = HEAD + lvB's `src/pycsl` diff (`git diff f10176e85 run5-lvB -- src/pycsl`, applies
cleanly, one hunk offset). All 40 stubs whose HEAD first blocker is the in-place mutator refusal were re-emitted there
(probes `<sid>_B1`): **39 are refused at the SAME mutator site**, 1 gets past it (`audit_proof._index_proofs_dir_by_file`,
`out.setdefault(qn, path)` admitted, next wall L3-TC: `for qn in <Set[str]>`, the set-iteration value model, exactly
as lvB recorded). Receiver shapes of the 39: raising `pop()` on a local / parameter 10 (exact-pop with an IndexError VC
needed), `self.<field>` 9 (whole-module self-field alias analysis), computed receiver 4, `update` with a set / mutable
argument 4, `extend` 3, `setdefault` on a parameter / module constant 2, `add` 2, `reverse` / `sort(key=)` / `insert` 1
each, other 3. Set cover: the mutator family is on 82 chains and is the LAST missing piece of **0** closed chains; with
the self-field alias analysis + exact pop + set() model added (the three reopenings run #5 named) it still completes 0
alone; with one more partner, 2 pure_ast honesty walls (`_Unparser.write` + the effectful-callback model, `walk` + the
generator model). **Verdict: worth 0 conversions in run #6**; keep it as a ready link (it is byte-inert on the corpus per
lvB) for a later value-model batch.

### 4.4 (ii-c) The str seam

On 28 chains (str-typed locals and `List[str]` locals built by `.append`, `str.split` / `join` / `encode` /
`strip(chars)`, f-string float formats, the faithful string hash), the last missing piece of ONE closed chain:
`identifiers.py::stable_hash` (needs the faithful string-hash model; today `pycsl_mod (int_2 (any int) 16) ..` is
input-blind). With one partner it adds `_stub_set` (only with the filesystem model). Run #5's lvD measured the same
shape (nine distinct causes, one stub each). The str-list local (`List[str]` built by append = a seq of int hashes, cv9's
s001 wall) is the piece with the widest reach in the hot files, but every chain it sits on has another wall behind it.

### 4.5 (ii-d) genexp-sum

On exactly 1 chain (`ReverifyReport.summary`, TC-OK-PARTIAL via cv9 stand-ins; replay `r9xs004_4` at HEAD: same
TC-OK), which also needs the float-to-str / f-string float format models and a typed list element: completes 0 alone,
1 together with the str-seam float formats + `cap-vm-unerase-list` (3 capabilities for one stub in
audit_proof_reverify.py).

### 4.6 (ii-e) method-recursion-cycle / termination

On 34 chains; completes 1 alone, and only through the `#@ \diverges` decision (`_expand_anon_binders`, §1 row 8); no structural-measure completion. Four chains reach TC-OK with the recursion removed as a stand-in (replays at HEAD
confirm all four: `_Harvester._emit_suite` r9xs027_2, `_Parser._max_end` r10xh013_2, `ConcurrencyChecker._walk_stmt`
r9xs019_4, `_expr_to_whyml_string_ctx` r10xh091_4), each with a further value-model need (`List[_Target]` records, dynamic
getattr / node typing, the stdlib-ast model, a missing mirror sibling + str list). `_emit_suite` is the closest: the
structural measure + `cap-vm-unerase-list` (a record list) = 1 stub. The three `\diverges` refusals of run #5 are
unchanged except `_expand_anon_binders` (now TC-OK at depth 0, §1).

### 4.7 Point 6: `\trusted -> #@ declared_in` swaps

`bin/check-declaration-conformance.py` at HEAD: 28 declarations, 24 conform, 4 FAIL (all ledgered);
"0 `\trusted` declaration stub(s) are CHECKED (conforming)": **no swap is honestly available as-is.** The three
`\trusted` declaration stubs, measured:

| declaration | what blocks the swap | measured |
|---|---|---|
| `StatementEmissionMixin._expr_to_whyml` (statements) | (e) `subst: int` vs the definition's `Optional[Dict[str, str]]` | with the definition's annotation + `declared_in` (probe `s298_D1`): L3-TC `int` vs `string -> option string` at the callers that omit `subst` = the emitter defect `cap-none-default-map-param` (an omitted `None` default of an `Optional[Dict]` parameter lowered as `0`). **One S emitter fix away**; statements.py moves (~9.4 h). |
| `StatementEmissionMixin._track_collection_metadata` (statements) | (a) frame misses `self._rebound_collections` | widened frame + `declared_in` (probe `s307_D1`): TC-OK and conformance OK (25/28 with the ledger row removed), but the field is not in `StatementEmissionMixin`'s record, so it is dropped from the emitted `writes` (the writes-survival TRAP ratchet, which may only shrink). Declaring the field on the class (probe `s307_D2`): TC-OK, but `check-assigns-underdeclaration --transitive` goes RED, **HOLE-V +15**: 8 VERIFIED frames (`_emit_new_ghost_ref`, `_handle_array_slice_set_stmt`, `_handle_augassign_stmt`, `_handle_critical_section_stmt`, `_handle_fieldassign_stmt`, `_handle_fieldaugassign_stmt`, `_handle_ghost_array_set_stmt`, `_handle_seq_assign`) and 7 `\trusted` ones omit the now-mentionable field. Honest swap = widen those 15 frames (a contract change on 8 verified methods: driver decision) + statements.py proof. |
| `StatementEmissionMixin._handle_return_stmt` | base-class override (`stmt: ExprIR` vs `ReturnStmt`) | stays `\trusted` (ledger; no refines goal is emitted for a base imported from the live tree) |

The PORT-ABORT "no live def" rows of the depth-0 pass (3) are exactly these declarations.
