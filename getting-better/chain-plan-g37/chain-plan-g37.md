# Chain plan g37 (ch32) — FIRST-blocker re-measurement of the `\trusted` population at HEAD

Measured 2026-10-22 at `e1535d21` (worktree `pycsl-g37ch32`, detached at main). Count at HEAD:
`grep -cF '#@ \trusted'` sum = **448** (incl. prose mentions); line-prefix markers =
**420** (`check-trusted-reasons.py`: 420 <-> 420, 53 mirror files). The g36 plan was computed at
430 rows on 2026-10-17; since then ch19-ch31 + r2c landed capabilities and routes #277-#303
landed refusals. **Result: 0 honest TCOK0 markers, 0 conversions (420 -> 420).**

## Method

`census.py` = g36 `chain.py` with `--first`: for every row of `trusted-reasons.tsv`, port the LIVE
body + live signature into the mirror of a SCRATCH copy of `src/` (session scratchpad, never this
tree; file restored after every row, scratch tree verified identical to `src/` at the end), emit
`--no-proof --keep-mlw` through `heavy.sh` (QUICK slot), stop at the FIRST blocker: a front-end
refusal (classified by message) or a Why3 type error (located to a Python statement via the g36
anchored re-emit). Nothing is neutralised, so the g36 PH (placeholder) bucket does not apply.
Same pre-skip classes as g36 (NOLIVE / DNC-EFFECT / NESTED-IN-TRUSTED / CORRECTNESS).
`plan37.py` = g36 `classify.py` rules PREFIXED by the refusal families that did not exist on
2026-10-17 (ERASED route #252, R301, DEFASSIGN, TUPALIAS, MCYCLE, APPENDLEN, COMPRECV, KWARG,
ELEMSTORE, OPAQUEWRITE). Raw rows: `first.jsonl` (one JSON per marker). Reproduce:
`python3 census.py <scratch-tree> first.jsonl --first --budget 480` (resumable, why3 on PATH:
`. scratchpad/g29/env.sh`), then `python3 plan37.py first.jsonl --rows`.

A first blocker is a LOWER bound on the work: the g36 chains show most markers carry several
blockers behind the first, so unlocking a family does not convert its markers by itself.

## Population

```
    359  BLOCKED
     24  SKIP-NOLIVE
     19  SKIP-DNC-EFFECT
     10  TCOK0
      7  SKIP-NESTED-IN-TRUSTED
      1  SKIP-CORRECTNESS
    420  TOTAL rows (trusted-reasons.tsv)
```

## Per-family totals (FIRST blocker)

```
    41  M  MUTRECV in-place mutator (.pop/.add/.extend/.setdefault/.update/... on local/self-field)
    36  M  ERASED erased (Any/object/unannotated) value flows into a builtin-typed parameter slot
    25  L  DICT Dict[str,Any] IR-dict: heterogeneous values typed `string -> option int` (Map.get value read as str/dict/list)
    20  M  NESTED def lift / closure
    19  M  RECORD record/ADT value (emit_ir/term/classdef/stmt) vs erased int local
    18  M  LISTSTR List[str]/List[T] local or field typed array int (element typing)
    14  M  GETATTR AST getattr / hasattr / getter erasure
    12  L  REBIND name rebound / namespace-dict write / global / dynamic eval
    12  S  R301 dropped unpacking / loop target of tuple-with-tuple/attribute shape (route #301)
    11  M  INTSTR int<->string erasure (upstream local/param typed int)
    11  M  TUPALIAS mutating a collection aliased by a tuple-unpacking assignment
    11  M  DEFASSIGN local read that is not definitely assigned on every path
    10  L  MCYCLE recursion through a METHOD/constructor call (bodyless stub would assume termination)
     8  M  EXT stdlib/external call erased to 0-ary input-blind val (pathlib/os/json/hashlib/io)
     8  M  ALIAS dict/set value observed through two names / mutated dict aliased or stored
     7  M  APPENDLEN `.append` to a list whose length the lowering cannot track (non-growable local: field/call-result bound)
     7  M  GENEXP generator / comprehension / any()/all()/sorted() erasure
     6  M  EXC exception object read / except-as / try-else
     6  S  STRM str method erasure (split/strip/startswith/join/...)
     6  M  TUPLE tuple return slot / tuple unpack typing
     6  M  COMPRECV mutator/call on a COMPUTED receiver (subscript / tuple elt / call result / attribute of one)
     6  S  UNBOUND unbound symbol (missing helper/val/field)
     6  L  CALLABLE first-class function value applied
     6  M  WITH-AS context manager
     6  M  KWARG builtin keyword argument discarded by its lowering (sorted key= / open encoding=)
     4  M  SET set()/frozenset value typed (StrSet / Array.make 1024 / membership)
     4  S  UNIT unit-returning call used as a value
     4  S  SYNTAX emitter produced ill-formed WhyML
     4  S  FSTR f-string / str literal hashed into int str_concat
     4  M  PYVAL IR-dict node (pyval) vs erased int local
     3  M  ARRAY-REASSIGN array local from non-literal RHS
     3  L  MUTPARAM in-place mutation of a dict/set/list PARAMETER (caller-visible writes frame)
     3  L  ELEMSTORE element store through a value not modelled as a list (abstract subscript_set)
     2  M  FLOAT real-valued field
     2  M  OPTREC Optional[record] / None where a record (or tuple) is expected
     2  S  ISBOOL `x is True/False` identity
     1  L  HETERO heterogeneous list literal
     1  L  OBJSTATE class instantiation (_pyobj_state)
     1  M  REF ref vs value (mutable-local aliasing)
     1  M  OPAQUEWRITE a WRITING call inside an opaquely-lowered comprehension/generator/lambda
     1  S  BOOL bool vs int
     1  L  OTHER unclassified
```

## Cheaper-first unlock table

Rank = cost class (S=1 emitter arm, M=3 model extension + spike, L=8 new value model / certificate),
then markers whose FIRST blocker is this family (desc). Unlocking the first blocker does NOT make a
marker landable: most g36 chains had further blockers behind the first.

| # | family | cost | markers (first blocker) | example markers |
|---|---|---|---|---|
| 1 | R301 | S | 12 | `_collect_array_var_assigns`, `_dispatch_function_contracts`, `_fin_block`, `_handle_attribute_expr` |
| 2 | STRM | S | 6 | `_cache_key`, `_split_rocq_check_output`, `_synthesize_block`, `_synthesize_legacy_text` |
| 3 | UNBOUND | S | 6 | `_const_value_getter`, `_const_value_setter`, `_lex_contract`, `_normalize_leading` |
| 4 | UNIT | S | 4 | `_decode_fstring_middle`, `_parse_inductive`, `fix_missing_locations`, `parse` |
| 5 | SYNTAX | S | 4 | `_collect_instantiations`, `_parse_atom_name`, `_parse_contract`, `unparse` |
| 6 | FSTR | S | 4 | `_emit_preamble_uses`, `get_type_comment`, `visit_Compare`, `whyml_ident` |
| 7 | ISBOOL | S | 2 | `_classify_iterable`, `_match_pattern_to_ir` |
| 8 | BOOL | S | 1 | `pairwise` |
| 9 | MUTRECV | M | 41 | `_add_abstract_op`, `_build`, `_collect_union_arms`, `_content_string_method` |
| 10 | ERASED | M | 36 | `_build_function_symbol_table`, `_check_function`, `_collect_class_fields`, `_compute_shared_module_maps` |
| 11 | NESTED | M | 20 | `_ac_normalize`, `_call_record_constructor`, `_detect_array_dimensions`, `_dispatch_provers` |
| 12 | RECORD | M | 19 | `__init__`, `_csl_in`, `_csl_list_to_ir`, `_e` |
| 13 | LISTSTR | M | 18 | `_advance_past_referenced_axiom_decls`, `_emit_contract_logic_symbol`, `_emit_uncited_axiom_func_decls`, `_encode_callable_annotation` |
| 14 | GETATTR | M | 14 | `_call_bytes_methods`, `_desugar_acts`, `_expand_nat_to_int`, `_handle_augassign_stmt` |
| 15 | INTSTR | M | 11 | `_emit_class_inv_axioms`, `_emit_first_assign`, `_emit_union_arm_vc`, `_load_axiom_registry` |
| 16 | TUPALIAS | M | 11 | `_build_function_ir`, `_dedup_arrow_chain`, `_emit_shared_state`, `_fold_blocks` |
| 17 | DEFASSIGN | M | 11 | `_build_soundness_report`, `_call_named_builtins`, `_expr_to_whyml`, `_get_module_exports` |
| 18 | EXT | M | 8 | `_cache_load`, `_expand_anon_binders`, `_function_body_eqs`, `_make_temp_mlw_path` |
| 19 | ALIAS | M | 8 | `_dotted_ensures_suffix`, `_emit_bitwise_or_power`, `_emit_body_code`, `_handle_ghost_assign_stmt` |
| 20 | APPENDLEN | M | 7 | `_assign`, `_attach_loop_contracts`, `_audit_one_prover`, `_consolidate_module_concurrency` |
| 21 | GENEXP | M | 7 | `_alpha_rename`, `_attach_labels_and_ghost_assigns`, `_coerce_dotted_args`, `_fin` |
| 22 | EXC | M | 6 | `_index_proofs_dir`, `_m5_get_type_name`, `_write_fstring_inner`, `parse_type_expr` |
| 23 | TUPLE | M | 6 | `__repr__`, `_match_block_hdr`, `_parse_variant_def`, `parse_rocq_assumptions_block` |
| 24 | COMPRECV | M | 6 | `_emit_protocol_interface`, `_inject_functions`, `_parse_extracted_contracts`, `_populate_protocol_conformance` |
| 25 | WITH-AS | M | 6 | `__init__`, `_resolve_runtime_config`, `_sha256_file`, `delimit_if` |
| 26 | KWARG | M | 6 | `_alpha_rename`, `_self_test`, `crosscheck_file_ir`, `crosscheck_file` |
| 27 | SET | M | 4 | `_build_callee_no_exception_summary`, `_fresh_globals_facts`, `_record_key`, `run_ir_semantic_checks` |
| 28 | PYVAL | M | 4 | `_construct_indices`, `_project_app`, `_rewrite_subscript_to_name`, `check_imports` |
| 29 | ARRAY-REASSIGN | M | 3 | `_field_write_site`, `_resolve_dotted_signature`, `visit_FunctionDef` |
| 30 | FLOAT | M | 2 | `_subst_var`, `summary` |
| 31 | OPTREC | M | 2 | `_get_mutex_invariant_ir`, `diagnostic` |
| 32 | REF | M | 1 | `buffered` |
| 33 | OPAQUEWRITE | M | 1 | `_match_pattern_cond` |
| 34 | DICT | L | 25 | `__init__`, `_build_witness_str`, `_check_gt4_polymorphic_recursion`, `_decode_escapes` |
| 35 | REBIND | L | 12 | `_build_nodes`, `_check_witness_vals`, `_merge_str_constants`, `_render_match_pattern` |
| 36 | MCYCLE | L | 10 | `__init__`, `__init__`, `_callee_raised_in`, `_check_protect_aliasing` |
| 37 | CALLABLE | L | 6 | `_parse_quantifier`, `_try`, `interleave`, `items_view` |
| 38 | MUTPARAM | L | 3 | `_collect_field_read_sites`, `_collect_self_call_sites`, `_emit_opaque_class_aliases` |
| 39 | ELEMSTORE | L | 3 | `_rewrite_annotations`, `_rewrite_call_sites`, `set_precedence` |
| 40 | HETERO | L | 1 | `_parse_assigns_target` |
| 41 | OBJSTATE | L | 1 | `__new__` |
| 42 | OTHER | L | 1 | `_run_pipeline` |

Cost classes: S = one emitter arm / fail-closed arm; M = model extension + hand spike; L = new value
model or certificate. ERASED (route #252) is rated M, not S: the refusal is correct (an erased `Any`
reaching a `str`/`int`/`bool` parameter would re-apply builtin laws to a user object); unlocking it
needs the SOURCE typed (hval `HStr` projection with a checked fallback, or typed IR/AST reads). Its
largest sub-clusters: `whyml_ident(name)` 9 markers, Module5 `scope_name` into
`_field_type_from_annotation_inst`/`_typeddict_field_type`/`_m5_get_type_name` 6,
`_resolve_module_path(level, module_dotted)` 3.

**Post-2026-10-17 refusals as first blocker**: ERASED 36 + R301 12 + TUPALIAS 11 + DEFASSIGN 11 +
MCYCLE 10 + APPENDLEN 7 + COMPRECV 6 + KWARG 6 + ELEMSTORE 3 + OPAQUEWRITE 1 = **103 markers**
(25 % of the population) whose first wall is now a fail-closed refusal rather than an L3-tc error.
These refusals do not make the markers harder (the g36 chain ran PAST the same constructs only
because they were silently erased); they make the cost visible.

**SYNTAX (4, completeness bugs, fail-closed by Why3, not soundness)**: the emitter prints an
EMPTY record literal `{  }` for a field-less record type (`_ContractParser._parse_contract`
`raise (Return_emit_ir {  })`, `_parse_atom_name` `raise (Return {  })`, `pure_ast.unparse`
`let unparser = {  } in`), and `(any int)` inside a `variant { .. }` term
(`monomorphize._collect_instantiations`). Cheapest S arms in the table, but each marker has more
blockers behind (not measured).

## TCOK0 (L3-tc clean at HEAD, zero neutralisation) + facade check

```
  frontend/pure_ast.py::_Parser.error  facade=reads-inputs used=[] marks={} reason=cost-scale:exception-payload-model
  frontend/pure_ast.py::_Parser.unsupported  facade=reads-inputs used=[] marks={} reason=cost-scale:exception-payload-model
  frontend/pure_ast.py::_parse_number  facade=reads-inputs used=['s'] marks={'anyval': 3, 'zeroary': 1, 'hash': 4} reason=cost-scale:int-erasure-seam
  frontend/pure_ast.py::iter_fields  facade=reads-inputs used=['node'] marks={'anyval': 1} reason=cost-scale:generator-sequence-model
  frontend/pure_ast.py::iter_child_nodes  facade=reads-inputs used=['node'] marks={'anyval': 4} reason=cost-scale:generator-sequence-model
  frontend/pure_ast.py::NodeVisitor.generic_visit  facade=reads-inputs used=['node'] marks={'anyval': 2} reason=unclassified
  ir_schema.py::validate_ir  facade=reads-inputs used=['ir'] marks={'anyval': 4, 'zeroary': 3, 'hash': 13} reason=unclassified
  module6_whyml/identifiers.py::stable_hash  facade=FACADE used=[] marks={'anyval': 1, 'hash': 1} reason=cost-scale:faithful-string-hash
  proof2why3/sertop.py::_sexp_tokens  facade=reads-inputs used=['s'] marks={'anyval': 4} reason=unclassified
  pycsl.py::_parse_args  facade=n/a-noinputs used=[] marks={'zeroary': 2, 'hash': 40} reason=unclassified
```

Verdict per TCOK0 (facade = what the emitted block really reads; none is honest, none converted):

```
  _Parser.error / _Parser.unsupported  raise-only (DNC, vacuous: converting certifies nothing)       SKIP
  _parse_number        TC-clean ONLY under the live (unannotated) signature. With the mirror's
                       `-> "PyConstVal"` it is L3-tc ✗ (pure_ast.mlw: body `int` vs `pyconst_val`,
                       re-measured this run). Body: `float(..)` = `py_float_1 (str_hash_op s)` (hash
                       erasure), `any(c in low for c in ".e")` = `any_1 (any (array int))` (input-
                       blind branch), `complex(..)` unmodelled. FACADE                             SKIP
  iter_fields / iter_child_nodes / _sexp_tokens
                       generators: every `yield` -> `any int`, return `unit`; the exact shape
                       `bin/check-yield-erasure.py` exists to refuse (wall-lessons: iter_fields was
                       converted once and re-trusted). FACADE                                       SKIP
  NodeVisitor.generic_visit   refused by the gen #31 vacuity screen (g36 step 2); anyval 2.         SKIP
  validate_ir          `ir.keys()` -> 0-ary `ir_keys_0 ()`, `ir.get` receiver-dropped, isinstance
                       `any bool` (g36 step 2). FACADE                                             SKIP
  stable_hash          emitted block reads no input (facade_check FACADE). FACADE                   SKIP
  _parse_args          argparse erased to 0-ary vals (zeroary 2, 40 hashed literals); g36: refused
                       by screen check 1 (new abstract ops). FACADE                                 SKIP
```

**Deltas vs the g36 TCOK0 list (14 -> 10)**: `_Unparser.visit_If` CONVERTED (ae771d38);
`PyCSLWeaver._attach_loop_contracts` now REFUSED (APPENDLEN: `node.csl_invariants.append` on a
non-growable local) — closes the g36 "fresh local array swallows the caller-visible write" facade;
`monomorphize._rewrite_call_sites` now REFUSED (ELEMSTORE) — closes the g36 soundness suspicion:
the g36 repro `alias_elem_store.py` (`for x in d.get("fs", []): x["body"] = []` under
`assigns \nothing`) is REFUSED at HEAD ("an element store through a value the model does not
represent as a list is out of scope"), re-run this session; `_Parser._max_end` now MCYCLE.

## Soundness

No new suspicion found by this census (it is a type-check census; no proof was run). The one open
g36 suspicion (element-alias store into a dict parameter) is CLOSED at HEAD (above). Open items
inherited, not re-checked: r2c's "hval key projection maps a non-string key to `\"\"`".

## Ranked next (cheapest first, by markers unlocked at the FIRST wall)

1. **R301** (S, 12): tuple-with-tuple / tuple-with-attribute unpacking targets
   (`for (a, b), c in ..`, `x.f, y = ..`) — an emitter arm that binds every leaf.
2. **ERASED / whyml_ident cluster** (M, 9 of 36): an `HStr`-checked projection at the call
   boundary (`whyml_ident(<hval>)`), the same lever as ch30/ch31; then Module5 `scope_name` (6).
3. **MUTRECV** (M, 41): still the largest; `.pop`/`.setdefault`/`.extend` on locals dominate (g36
   detail table unchanged in kind).
4. **SYNTAX** (S, 4): empty-record literal and `any` in a variant — emitter bugs worth fixing on
   their own (fail-closed today).
5. **DEFASSIGN** (M, 11) / **TUPALIAS** (M, 11): both are correct refusals; unlocking needs a
   maybe-unbound local model (UnboundLocalError) and tuple-unpack alias tracking respectively.

## Appendix — per-marker first blocker

```
  SET         Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._build_callee_no_exception_summary | self._module_func_no_exception[name] = set(contracts.get('no_exception | This expression has type array.Array.array int @rho, but is expected to have type int /tmp/claude-1000/-home-f
  MUTRECV     Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._wrap_call_with_callee_raises_assert | active.update(all_phase1_exceptions()) | `active.update(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an a
  MUTRECV     Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._render_callee_condition | _n141 = _r141.pop() | `_r141.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstr
  MUTRECV     Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._maybe_emit_no_exception_assert | active.update(all_phase1_exceptions()) | `active.update(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an a
  REBIND      Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler.transpile |  | a function, method or class NAME is rebound after its definition (a write through a namespace dict at line 109
  ERASED      Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._compute_shared_module_maps | _nm = str(func.get('name', '')) | function 'module6_whymltranspiler___compute_shared_module_maps': an erased (`Any`/`object`/unannotated/TypeVar
  DICT        Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._emit_prefunctions_infra | out += self._emit_preamble_axioms(axiom_ir) | This expression has type string -> option.Option.option int, but is expected to have type int /tmp/claude-1000
  LISTSTR     Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._sig_val_from_let | HDR If len(hdr_idxs) > 1 | This expression has type int, but is expected to have type array.Array.array 'mu @rho /tmp/claude-1000/-home-f
  SKIP-NESTED-IN-TRUSTED Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._sig_val_from_let._hdr_name
  REBIND      Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._transpile_modular |  | a function, method or class NAME is rebound after its definition (a write through a namespace dict at line 109
  SKIP-NESTED-IN-TRUSTED Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._transpile_modular._emit_funcs
  LISTSTR     Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._shared_use_lines | lib_uses = self._emit_preamble_uses(needs, module_name='__tmp__')[1:] | This expression has type int, but is expected to have type array.Array.array int @rho /tmp/claude-1000/-home-f
  LISTSTR     audit_proof.py::_extract_directives | HDR If len(parts) < 4 | This expression has type int, but is expected to have type array.Array.array 'mu @rho
  MUTRECV     audit_proof.py::_parse_rocq_file | top = frame_stack.pop() | `frame_stack.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an
  MUTRECV     audit_proof.py::_parse_lean_file | ns_stack.extend(segs) | `ns_stack.extend(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an
  EXC         audit_proof.py::_index_proofs_dir | HDR except (OSError, UnicodeDecodeError) as exc | [whyml-emit]: '_index_proofs_dir' reads the exception object 'exc' bound by `except ... as exc` (ROUTE #233). 
  APPENDLEN   audit_proof.py::_audit_one_prover | _alts.append(_d) | [module6-whyml]: `report.failures.append(...)` appends to a list whose length this lowering cannot track: the 
  MUTRECV     audit_proof.py::_index_proofs_dir_by_file | out.setdefault(qn, path) | `out.setdefault(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an 
  FLOAT       audit_proof_reverify.py::ReverifyReport.summary | return f'{head} reverify {self.prover}: {self.proof_file} compile={sel | This expression has type real, but is expected to have type int
  SKIP-DNC-EFFECT audit_proof_reverify.py::_cache_root
  MUTRECV     audit_proof_reverify.py::_sha256_file | h.update(path.read_bytes()) | `h.update(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstra
  STRM        audit_proof_reverify.py::_cache_key | parts = [_sha256_file(proof_file), ','.join(sorted(qualnames)), prover | This expression has type array.Array.array string @rho, but is expected to have type array.Array.array int @rh
  EXT         audit_proof_reverify.py::_cache_load | return json.loads(f.read_text()) | This expression has type int, but is expected to have type PyCSL_Program. _union__cache_load_0
  SKIP-DNC-EFFECT audit_proof_reverify.py::_cache_store
  SKIP-DNC-EFFECT audit_proof_reverify.py::_coqc_version
  SKIP-DNC-EFFECT audit_proof_reverify.py::_lean_version
  SKIP-DNC-EFFECT audit_proof_reverify.py::verify_rocq_file
  SKIP-DNC-EFFECT audit_proof_reverify.py::verify_lean_file
  INTSTR      audit_proof_reverify.py::_to_cache_payload | return {'compile_ok': report.compile_ok, 'compile_stdout': report.comp | This expression has type string, but is expected to have type int
  SET         core_ir_semantic.py::run_ir_semantic_checks | trusted_funcs = set(ir.get('trusted_funcs') or []) | This expression has type array.Array.array int @rho, but is expected to have type int
  NESTED      core_ir_semantic.py::_returns_literal_none | NESTED def walk | nested function 'walk' is lifted to a sibling of its enclosing function, and the lift is not faithful here: it
  SKIP-NESTED-IN-TRUSTED core_ir_semantic.py::_returns_literal_none.walk
  DICT        core_ir_semantic.py::_typeddict_check_subscript |  | This expression has type int -> option.Option.option int, but is expected to have type string -> option.Option
  DICT        core_ir_semantic.py::_namedtuple_check_call | nfields, field_names, defaulted = nt_arities[callee] | This expression has type int -> option.Option.option int, but is expected to have type int
  DICT        core_ir_semantic.py::_namedtuple_check_subscript |  | This expression has type int -> option.Option.option int, but is expected to have type string -> option.Option
  MUTRECV     exception_model.py::bases_closure | b = frontier.pop() | `frontier.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an ab
  MUTRECV     frontend/ConcurrencyChecker.py::ConcurrencyChecker.check | self._thread_entries.add(node.name) | `self._thread_entries.add(...)` MUTATES its receiver in place, and no certified lowering models it: the call b
  ERASED      frontend/ConcurrencyChecker.py::ConcurrencyChecker._check_function | self._walk_body(func.body, held=set(), func_name=func.name) | function 'concurrencychecker___check_function': an erased (`Any`/`object`/unannotated/TypeVar) value flows int
  ERASED      frontend/ConcurrencyChecker.py::ConcurrencyChecker._walk_stmt | inner_held = held | {mutex} if mutex else held | function 'concurrencychecker___walk_stmt': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a s
  TUPLE       frontend/Module1_Ingestor.py::_match_block_hdr | return None | This expression has type int, but is expected to have type (int, int)
  COMPRECV    frontend/Module1_Ingestor.py::Module1_Ingestor.process |  | [module6-call]: `.run(...)` on a COMPUTED receiver (a subscript, a tuple element, a call result, or an attribu
  ERASED      frontend/Module1_Ingestor.py::_Harvester._make | indent = getattr(node, 'col_offset', 0) | function '_harvester___make': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot declared 
  MUTRECV     frontend/Module1_Ingestor.py::_Harvester._build | self._flat.append(tgt) | `self._flat.append(...)` appends to the collection in the field `_flat`, and no certified lowering models it: 
  APPENDLEN   frontend/Module1_Ingestor.py::_Harvester._assign | _dec_owner.leading.append(c.text[2:].rstrip()) | [module6-whyml]: `_dec_owner.leading.append(...)` appends to a list whose length this lowering cannot track: t
  UNBOUND     frontend/Module1_Ingestor.py::_Harvester._normalize_leading |  | unbound function or predicate symbol '_match_block_hdr'
  TUPALIAS    frontend/Module1_Ingestor.py::_Harvester._fold_blocks | clauses, i = self._fold_clauses(raw_lines, i, n, blk_indent, f'{kw} {n | [module6-assign]: function '_harvester___fold_blocks': mutating a collection that a TUPLE-UNPACKING assignment
  MCYCLE      frontend/Module1_Ingestor.py::_Harvester._emit_suite |  | [ir-semantic] src/self-annotate/src/frontend/Module1_Ingestor.py: the functions ['_harvester___emit_suite'] ca
  UNBOUND     frontend/Module2_Parser.py::_lex_contract |  | unbound function or predicate symbol 'toks'
  MCYCLE      frontend/Module2_Parser.py::_ContractParser.__init__ |  | [ir-semantic] src/self-annotate/src/frontend/Module2_Parser.py: the functions ['_contractparser___parse_atom']
  RECORD      frontend/Module2_Parser.py::_ContractParser._err |  | This expression has type PyCSL_Program.emit_ir, but is expected to have type ()
  CALLABLE    frontend/Module2_Parser.py::_ContractParser._try | return fn() | This expression has type int, it cannot be applied
  UNIT        frontend/Module2_Parser.py::_ContractParser.parse | node = self._parse_contract() | This expression has type (), but is expected to have type int
  SYNTAX      frontend/Module2_Parser.py::_ContractParser._parse_contract | HDR If kw == 'no_inline' | syntax error
  ERASED      frontend/Module2_Parser.py::_ContractParser._grab_reviewer_id | self._err('expected reviewer id') | function '_contractparser___parse_trusted': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a 
  LISTSTR     frontend/Module2_Parser.py::_ContractParser._parse_assigns | return Assigns(self._parse_assigns_target()) | This expression has type PyCSL_Program.assigns <array.Array.array int @rho1> @rho, but is expected to have typ
  HETERO      frontend/Module2_Parser.py::_ContractParser._parse_assigns_target |  | heterogeneous list literal (contains a record (Nothing) element mixed with other element types) has no faithfu
  RECORD      frontend/Module2_Parser.py::_ContractParser._parse_act_block | self.advance() | This expression has type PyCSL_Program.emit_ir, but is expected to have type int
  LISTSTR     frontend/Module2_Parser.py::_ContractParser._parse_happy | return HappyProperty(name, '', lo, hi, except_set, protects=[path], pa | This expression has type array.Array.array string @rho, but is expected to have type int
  ERASED      frontend/Module2_Parser.py::_ContractParser._parse_happy_targets | return HappyProperty(name, '', None, None, [], context='postcond', tar | function '_contractparser___parse_happy_targets': an erased (`Any`/`object`/unannotated/TypeVar) value flows i
  LISTSTR     frontend/Module2_Parser.py::_ContractParser._parse_datatype | self.expect_name('datatype') | This expression has type PyCSL_Program.datatypedecl <array.Array.array int @rho1, array.Array.array int @rho2>
  TUPLE       frontend/Module2_Parser.py::_ContractParser._parse_variant_def | return (ctor, types) | This expression has type (string, seq.Seq.seq string), but is expected to have type (int, int)
  UNIT        frontend/Module2_Parser.py::_ContractParser._parse_inductive | rules = self._parse_inductive_rules() | This expression has type (), but is expected to have type int
  LISTSTR     frontend/Module2_Parser.py::_ContractParser._parse_inductive_rules | rules = [] | This expression has type array.Array.array int @rho, but is expected to have type int
  CALLABLE    frontend/Module2_Parser.py::_ContractParser._parse_quantifier | return cls(var, self._mk_in(var, domain, body, is_exists), binder_type | This expression has type ref int @rho, it cannot be applied
  RECORD      frontend/Module2_Parser.py::_ContractParser._parse_atom_primary | self.advance() | This expression has type PyCSL_Program.stringliteral @rho, but is expected to have type PyCSL_Program.emit_ir
  SYNTAX      frontend/Module2_Parser.py::_ContractParser._parse_atom_name | HDR If name == 'None' | syntax error
  UNBOUND     frontend/Module2_Parser.py::_ContractParser._parse_atom_bs |  | unbound function or predicate symbol 'i'
  LISTSTR     frontend/Module2_Parser.py::_ContractParser._parse_expr_list | return exprs | This expression has type seq.Seq.seq PyCSL_Program.emit_ir, but is expected to have type seq.Seq.seq int
  COMPRECV    frontend/Module2_Parser.py::Module2_Parser.parse_contract |  | [module6-call]: `.parse(...)` on a COMPUTED receiver (a subscript, a tuple element, a call result, or an attri
  FLOAT       frontend/Module3_Weaver.py::PyCSLWeaver._subst_var | return Number(int(m)) | This expression has type int, but is expected to have type real
  GETATTR     frontend/Module3_Weaver.py::PyCSLWeaver._desugar_acts | out.append(Requires(BinOp(A, '==>', cl.expr))) | This expression has type int, but is expected to have type PyCSL_Program. emit_ir
  APPENDLEN   frontend/Module3_Weaver.py::PyCSLWeaver._extract_mixin_directives | node.csl_provides.append(c.method) | [module6-whyml]: `node.csl_provides.append(...)` appends to a list whose length this lowering cannot track: th
  R301        frontend/Module3_Weaver.py::PyCSLWeaver._dispatch_function_contracts |  | dropped unpacking / loop target refused (route #301) -- function '_dispatch_function_contracts': an unpacking 
  GETATTR     frontend/Module3_Weaver.py::PyCSLWeaver._validate_function_contracts | HDR For _cm in getattr(node, 'csl_acts', []) or [] | This expression has type array.Array.array int @rho, but is expected to have type int
  GETATTR     frontend/Module3_Weaver.py::PyCSLWeaver.visit_FunctionDef | self._dispatch_function_contracts(node, self.contracts_map[node.lineno | This expression has type int, but is expected to have type seq.Seq.seq int
  MUTRECV     frontend/Module3_Weaver.py::PyCSLWeaver.visit_Module | self._csl_bound_names.add(_n_bn.id) | `self._csl_bound_names.add(...)` MUTATES its receiver in place, and no certified lowering models it: the call 
  GETATTR     frontend/Module3_Weaver.py::PyCSLWeaver.visit_With | HDR For c in self.contracts_map[node.lineno] | This expression has type int, but is expected to have type seq.Seq.seq int
  APPENDLEN   frontend/Module3_Weaver.py::PyCSLWeaver.visit_ClassDef | node.csl_class_invariants.append(c) | [module6-whyml]: `node.csl_class_invariants.append(...)` appends to a list whose length this lowering cannot t
  APPENDLEN   frontend/Module3_Weaver.py::PyCSLWeaver._attach_loop_contracts | node.csl_invariants.append(c) | [module6-whyml]: `node.csl_invariants.append(...)` appends to a list whose length this lowering cannot track: 
  GENEXP      frontend/Module3_Weaver.py::PyCSLWeaver.visit_While | node.csl_invariants = [] | This expression has type PyCSL_Program.py_while <array.Array.array int @rho1> @rho, but is expected to have ty
  GENEXP      frontend/Module3_Weaver.py::PyCSLWeaver.visit_For | node.csl_invariants = [] | This expression has type PyCSL_Program.py_for <array.Array.array int @rho1> @rho, but is expected to have type
  COMPRECV    frontend/Module3_Weaver.py::Module3_Weaver._parse_extracted_contracts |  | [module6-call]: `.extend(...)` on a COMPUTED receiver (a subscript, a tuple element, a call result, or an attr
  APPENDLEN   frontend/Module3_Weaver.py::Module3_Weaver._consolidate_module_concurrency | python_ast.csl_inductives.append(n) | [module6-whyml]: `python_ast.csl_inductives.append(...)` appends to a list whose length this lowering cannot t
  GENEXP      frontend/Module3_Weaver.py::Module3_Weaver._attach_labels_and_ghost_assigns | names = [n.name for n in nodes if isinstance(n, CSLLabel)] | This expression has type int, but is expected to have type array.Array.array int @rho
  MUTRECV     frontend/Module3_Weaver.py::Module3_Weaver._extract_happy_properties | out.extend((n for n in nodes if isinstance(n, HappyProperty))) | `out.extend(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abst
  ARRAY-REASSIGN frontend/Module3_Weaver.py::Module3_Weaver._field_write_site |  | reassigning an array LOCAL from a non-literal right-hand side is not modelled: the local is represented as a f
  NESTED      frontend/Module3_Weaver.py::Module3_Weaver._happy_predicate | NESTED def to_csl | nested function 'module3_weaver__to_csl' is lifted to a sibling of its enclosing function, and the lift is not
  MUTRECV     frontend/Module3_Weaver.py::Module3_Weaver._expand_happy_properties | _r206_cur = _r206_queue.pop() | `_r206_queue.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an
  GETATTR     frontend/Module3_Weaver.py::Module3_Weaver._region_bound_str | return getattr(node, 'name', '<expr>') | This expression has type int, but is expected to have type string
  MCYCLE      frontend/Module3_Weaver.py::Module3_Weaver._subst_csl_param |  | [ir-semantic] src/self-annotate/src/frontend/Module3_Weaver.py: the functions ['module3_weaver___subst_csl_par
  MCYCLE      frontend/Module3_Weaver.py::Module3_Weaver._check_protect_aliasing |  | [ir-semantic] src/self-annotate/src/frontend/Module3_Weaver.py: the functions ['module3_weaver___check_protect
  RECORD      frontend/Module3_Weaver.py::Module3_Weaver._subscript_read_site | base = sub.value | This expression has type PyCSL_Program.emit_ir, but is expected to have type int
  MUTPARAM    frontend/Module3_Weaver.py::Module3_Weaver._collect_self_call_sites | out.append((cur_stmt, cur_func)) | [module6-whyml]: in-place `append` to list parameter 'out' is out of scope: Python passes a list argument BY R
  NESTED      frontend/Module3_Weaver.py::Module3_Weaver._synthesize_selfcomp | NESTED def _call | nested function 'module3_weaver___call' is lifted to a sibling of its enclosing function, and the lift is not 
  MUTPARAM    frontend/Module3_Weaver.py::Module3_Weaver._collect_field_read_sites | out.append((cur_stmt, site, cur_func)) | [module6-whyml]: in-place `append` to list parameter 'out' is out of scope: Python passes a list argument BY R
  TUPALIAS    frontend/Module3_Weaver.py::Module3_Weaver.process | _dc_dm, _dc_da = _dc_det | [module6-assign]: function 'module3_weaver__process': mutating a collection that a TUPLE-UNPACKING assignment 
  DICT        frontend/Module5_IREmitter.py::PyCSLToJSONEmitter.__init__ |  | This expression has type int, but is expected to have type string /tmp/claude-1000/-home-fabrice-git-pycsl/011
  R301        frontend/Module5_IREmitter.py::PyCSLToJSONEmitter.visit_Module | self._shared_var_names = {d.variable for d in shared_decls} | function 'pycsltojsonemitter__visit_Module': the tuple `for` target component `c` is read outside its loop, bu
  OPTREC      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._get_mutex_invariant_ir | return None | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /tmp/claude-1000/-home-fabri
  RECORD      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._csl_in | elt_ir = self._csl_to_ir(node.element) | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /tmp/claude-1000/-home-fabri
  RECORD      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._csl_list_to_ir | d = self._csl_to_ir(c) | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /tmp/claude-1000/-home-fabri
  MUTRECV     frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._py_expr_call | parts.reverse() | `parts.reverse(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an a
  MCYCLE      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._py_expr_fstring |  | [ir-semantic] src/self-annotate/src/frontend/Module5_IREmitter.py: the functions ['pycsltojsonemitter___py_exp
  MCYCLE      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._py_stmts_to_ir |  | [ir-semantic] src/self-annotate/src/frontend/Module5_IREmitter.py: the functions ['pycsltojsonemitter___py_stm
  ISBOOL      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._match_pattern_to_ir | HDR If pattern.value is True | [whyml-emit]: an IDENTITY test against a `bool` literal (`X is True` / `X is False`) is refused unless the emi
  RECORD      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._field_type_from_annotation_inst | HDR If self._irnode_ann_name(annotation) is not None | This expression has type PyCSL_Program.emit_ir, but is expected to have type int /tmp/claude-1000/-home-fabric
  ERASED      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._emit_typeddict_record | fields: List[Dict[str, Any]] = [] | function 'pycsltojsonemitter___emit_typeddict_record': an erased (`Any`/`object`/unannotated/TypeVar) value fl
  ERASED      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._synthesize_typeddict_functional | fields: List[Dict[str, Any]] = [] | function 'pycsltojsonemitter___synthesize_typeddict_functional': an erased (`Any`/`object`/unannotated/TypeVar
  ERASED      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._emit_namedtuple_record | fields: List[Dict[str, Any]] = [] | function 'pycsltojsonemitter___emit_namedtuple_record': an erased (`Any`/`object`/unannotated/TypeVar) value f
  ERASED      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._synthesize_namedtuple_functional | fields: List[Dict[str, Any]] = [] | function 'pycsltojsonemitter___synthesize_namedtuple_functional': an erased (`Any`/`object`/unannotated/TypeVa
  COMPRECV    frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._emit_protocol_interface |  | [module6-call]: `.append(...)` on a COMPUTED receiver (a subscript, a tuple element, a call result, or an attr
  COMPRECV    frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._populate_protocol_conformance | tail = fname[len(prefix_sub):] | [module6-call]: `.append(...)` on a COMPUTED receiver (a subscript, a tuple element, a call result, or an attr
  ERASED      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._collect_class_fields | fields: List[Dict[str, Any]] = [] | function 'pycsltojsonemitter___collect_class_fields': an erased (`Any`/`object`/unannotated/TypeVar) value flo
  TUPALIAS    frontend/Module5_IREmitter.py::PyCSLToJSONEmitter.visit_ClassDef | _t183 = _r183 = None | [module6-assign]: function 'pycsltojsonemitter__visit_ClassDef': mutating a collection that a TUPLE-UNPACKING 
  MUTRECV     frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._collect_union_arms | node = stack.pop() | `stack.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstr
  R301        frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._normalize_union_annotation | lowered: List[Tuple[str, str]] = [] | dropped unpacking / loop target refused (route #301) -- function '_normalize_union_annotation': an unpacking /
  MUTRECV     frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._normalize_literal_annotation | self._cur_literal_ensures.append(clauses[0]) | `self._cur_literal_ensures.append(...)` appends to the collection in the field `_cur_literal_ensures`, and no 
  LISTSTR     frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._encode_callable_annotation | HDR If not (isinstance(slice_node, ast.Tuple) and len(slice_node.elts) | This expression has type array.Array.array PyCSL_Program.emit_ir @rho, but is expected to have type int /tmp/c
  EXC         frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._m5_get_type_name | HDR except Exception | [whyml-emit]: `except Exception` in '_m5_get_type_name' is meant to catch the raised `PyCSLIRError`, a user su
  ERASED      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._build_function_symbol_table | arg_type = self._m5_get_type_name(_eff_ann, _scope_name, arg.arg, dedu | function 'pycsltojsonemitter___build_function_symbol_table': an erased (`Any`/`object`/unannotated/TypeVar) va
  TUPALIAS    frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._build_function_ir | _sym, _dvt, _dkt, _pann, _plet, _plne, _plfe, _svt = self._build_funct | [module6-assign]: function 'pycsltojsonemitter___build_function_ir': mutating a collection that a TUPLE-UNPACK
  NESTED      frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._detect_array_dimensions | NESTED def _collect_augextend | nested function 'pycsltojsonemitter___collect_augextend' is lifted to a sibling of its enclosing function, and
  MUTRECV     frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._detect_seq_promotion | list_vars.discard(None) | `list_vars.discard(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes 
  ARRAY-REASSIGN frontend/Module5_IREmitter.py::PyCSLToJSONEmitter.visit_FunctionDef |  | reassigning an array LOCAL from a non-literal right-hand side is not modelled: the local is represented as a f
  REBIND      frontend/Module5_IREmitter.py::Module5_IREmitter.generate_json |  | a function, method or class NAME is rebound after its definition (`setattr`/`delattr` of a function name at li
  FSTR        frontend/desugar.py::_ChainDesugarer.visit_Compare | tmp = '_pycsl_cmp_%d' % (self._n,) | This expression has type string, but is expected to have type int
  DICT        frontend/desugar.py::_try_reaches_assert | HDR For _k in _funcs | This expression has type int -> option.Option.option int, but is expected to have type int
  REBIND      frontend/desugar.py::normalize_stores | setattr(_n, _f, _c) | a function, method or class NAME is rebound after its definition (`setattr`/`delattr` of a function name at li
  EXC         frontend/exec_splice.py::_ExecSplicer.visit_Expr | HDR except Exception as exc | [whyml-emit]: 'visit_Expr' reads the exception object 'exc' bound by `except ... as exc` (ROUTE #233). The han
  DICT        frontend/import_classifier.py::_stub_set | HDR If not stub_dir.is_dir() | This expression has type int, but is expected to have type int -> option. Option.option int
  PYVAL       frontend/import_classifier.py::check_imports | imports = collect_imports(tree) | This expression has type int, but is expected to have type PyCSL_Program. pyval
  NESTED      frontend/ir_inline.py::_recursive_methods | NESTED def reaches_self | nested function 'reaches_self' is lifted to a sibling of its enclosing function, and the lift is not faithful 
  ERASED      frontend/ir_inline.py::_Inliner._expand | pre: List[Any] = [] | function '_inliner___expand': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot declared 
  MUTRECV     frontend/ir_inline.py::_Inliner._hoist_calls_in_expr | pre.extend(self._expand(callee, recv, hoisted_args, res)) | `pre.extend(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abst
  MUTRECV     frontend/ir_inline.py::_Inliner.inline_stmts | out.extend(pre) | `out.extend(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abst
  MUTRECV     frontend/ir_inline.py::_inline_calls | _cb.update((t for t in _nd['targets'] if isinstance(t, str))) | `_cb.update(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abst
  SKIP-DNC-EFFECT frontend/ir_inline.py::apply_inline_globals
  EXT         frontend/ir_resolve.py::_resolve_module_path | candidate = os.path.join(base, *parts) + '.py' | This expression has type int, but is expected to have type string
  DEFASSIGN   frontend/ir_resolve.py::_get_module_exports | tree = _ast.parse(f.read()) | [ir-semantic] src/self-annotate/src/frontend/ir_resolve.py line 66: src/self-annotate/src/frontend/ir_resolve.
  DEFASSIGN   frontend/ir_resolve.py::_process_dependency | dep_source = f.read() | [ir-semantic] src/self-annotate/src/frontend/ir_resolve.py line 91: src/self-annotate/src/frontend/ir_resolve.
  DICT        frontend/ir_resolve.py::_strip_dir_scan_proofs | proofs = func.get('proof') | This expression has type string -> option.Option.option int, but is expected to have type ref 'mu @rho
  LISTSTR     frontend/ir_resolve.py::_find_record_type_from_dep_imports | local, original, module, level, _is_mod = entry[:5] | This expression has type int, but is expected to have type array.Array.array int @rho
  COMPRECV    frontend/ir_resolve.py::_inject_functions |  | [module6-call]: `.insert(...)` on a COMPUTED receiver (a subscript, a tuple element, a call result, or an attr
  R301        frontend/ir_resolve.py::_resolve_direct_imports |  | dropped unpacking / loop target refused (route #301) -- function '_resolve_direct_imports': an unpacking / loo
  ERASED      frontend/ir_resolve.py::_resolve_wildcard_imports | resolved = _resolve_module_path(module_path, level, main_file) | function '_resolve_wildcard_imports': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot d
  ERASED      frontend/ir_resolve.py::_resolve_module_imports | resolved = _resolve_module_path(module_path, level, main_file) | function '_resolve_module_imports': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot dec
  R301        frontend/ir_resolve.py::_resolve_imported_classes |  | dropped unpacking / loop target refused (route #301) -- function '_resolve_imported_classes': an unpacking / l
  ERASED      frontend/ir_resolve.py::_resolve_imported_base_classes | resolved = _resolve_module_path(module_path, level, main_file) | function '_resolve_imported_base_classes': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a s
  DEFASSIGN   frontend/ir_resolve.py::apply_inheritance | merge_one(td) | [ir-semantic] src/self-annotate/src/frontend/ir_resolve.py line 475: src/self-annotate/src/frontend/ir_resolve
  NESTED      frontend/ir_resolve.py::apply_composition | NESTED def walk | nested function 'walk' is lifted to a sibling of its enclosing function, and the lift is not faithful here: it
  TUPALIAS    frontend/ir_resolve.py::resolve_imports | _imp_ev, _imp_wild = _bind143['<importer>'] | [module6-assign]: function 'resolve_imports': mutating a collection that a TUPLE-UNPACKING assignment aliases 
  REBIND      frontend/ir_resolve.py::resolve | global _EXTRA_IMPORT_PATHS | function 'resolve' writes _EXTRA_IMPORT_PATHS through a `global` declaration, and no certified lowering models
  GETATTR     frontend/module_collect.py::collect_module_constants | shared = {d.variable for d in getattr(node, 'csl_shared_decls', [])} | This expression has type int, but is expected to have type array.Array.array int @rho
  GETATTR     frontend/module_collect.py::collect_module_globals | shared = {d.variable for d in getattr(node, 'csl_shared_decls', [])} | This expression has type int, but is expected to have type array.Array.array int @rho
  DICT        frontend/monomorphize.py::apply_monomorphization | generics = _collect_generic_decls(ir_data) | This expression has type string -> option.Option.option int, but is expected to have type string -> option.Opt
  SYNTAX      frontend/monomorphize.py::_collect_instantiations | HDR For site in _find_subscript_calls(func.get('body', []), generic_na | syntax error
  DICT        frontend/monomorphize.py::_check_gt4_polymorphic_recursion | gen_tvars[gname] = info['type_params'][0]['name'] | This expression has type int, but is expected to have type string
  ERASED      frontend/monomorphize.py::_emit_specializations | new_type_decls: List[Dict[str, Any]] = [] | function '_emit_specializations': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot decla
  MUTRECV     frontend/monomorphize.py::_specialize_decl | spec.pop('type_params', None) | `spec.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstra
  MUTRECV     frontend/monomorphize.py::_specialize_function | spec.pop('type_params', None) | `spec.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstra
  ELEMSTORE   frontend/monomorphize.py::_rewrite_call_sites |  | [ir-semantic] src/self-annotate/src/frontend/monomorphize.py: an element store through a value the model does 
  DICT        frontend/monomorphize.py::_rewrite_subscript_calls_in_stmt | new[k] = _rewrite_subscript_to_name(v, rename_map) | This expression has type int -> option.Option.option string, but is expected to have type int
  PYVAL       frontend/monomorphize.py::_rewrite_subscript_to_name | ct = _type_str(slice_node) | This expression has type int, but is expected to have type PyCSL_Program. pyval
  ELEMSTORE   frontend/monomorphize.py::_rewrite_annotations |  | [ir-semantic] src/self-annotate/src/frontend/monomorphize.py: an element store through a value the model does 
  DICT        frontend/monomorphize.py::_rewrite_annotation_str | return rename_map[gname, ct] | This expression has type string, but is expected to have type int
  MUTRECV     frontend/monomorphize.py::_record_classification | ir_data.setdefault('monomorphization_report', {})['uninstantiated'] =  | `ir_data.setdefault(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes
  REBIND      frontend/pure_ast.py::_build_nodes |  | a function, method or class NAME is rebound after its definition (a write through a namespace dict at line 63)
  UNBOUND     frontend/pure_ast.py::_const_value_getter | return self.value | unbound function or predicate symbol 'self'
  UNBOUND     frontend/pure_ast.py::_const_value_setter | self.value = value | unbound function or predicate symbol 'self'
  OBJSTATE    frontend/pure_ast.py::Ellipsis.__new__ | return Constant.__new__(cls, *args, **kwargs) | Class 'Ellipsis' (line 113): non-trivial `__new__` is rejected under UB-7.6. Allocation interposition (caching
  TUPLE       frontend/pure_ast.py::_Tok.__repr__ | return f'Tok({_tokenize.tok_name[self.type]}, {self.string!r}, {self.s | This expression has type PyCSL_Program.pytuple_int_int, but is expected to have type int
  NESTED      frontend/pure_ast.py::_lex | NESTED def to_byte | nested function 'to_byte' is lifted to a sibling of its enclosing function, and the lift is not faithful here:
  RECORD      frontend/pure_ast.py::Comment.__init__ |  | This expression has type ref PyCSL_Program.emit_ir @rho, but is expected to have type PyCSL_Program.comment @r
  GETATTR     frontend/pure_ast.py::comments | before = t.line[:t.start[1]] | This expression has type int, but is expected to have type array.Array.array int @rho
  MCYCLE      frontend/pure_ast.py::_Parser.__init__ |  | [ir-semantic] src/self-annotate/src/frontend/pure_ast.py: the functions ['_parser___binop', '_parser___call_ar
  R301        frontend/pure_ast.py::_Parser._slice |  | dropped unpacking / loop target refused (route #301) -- function '_slice': an unpacking / loop target of shape
  TCOK0       frontend/pure_ast.py::_Parser.error
  TCOK0       frontend/pure_ast.py::_Parser.unsupported
  GENEXP      frontend/pure_ast.py::_Parser._fin | et = end_tok if end_tok is not None else self.toks[max(self.i - 1, 0)] | This expression has type PyCSL_Program._tok, but is expected to have type int
  RECORD      frontend/pure_ast.py::_Parser.node |  | This expression has type PyCSL_Program._tok, but is expected to have type int
  MCYCLE      frontend/pure_ast.py::_Parser._max_end |  | [ir-semantic] src/self-annotate/src/frontend/pure_ast.py: the functions ['_parser___max_end'] call one another
  R301        frontend/pure_ast.py::_Parser._fin_block |  | dropped unpacking / loop target refused (route #301) -- function '_fin_block': an unpacking / loop target of s
  UNIT        frontend/pure_ast.py::_decode_fstring_middle | return _decode_escapes(text, False) | This expression has type (), but is expected to have type int
  REBIND      frontend/pure_ast.py::_merge_str_constants | out = [] | a function, method or class NAME is rebound after its definition (attribute `.n` written on `Constant...` at l
  SKIP-CORRECTNESS frontend/pure_ast.py::_set_ctx
  TCOK0       frontend/pure_ast.py::_parse_number
  DICT        frontend/pure_ast.py::_decode_string | prefix += tok[i] | This expression has type string, but is expected to have type int
  DICT        frontend/pure_ast.py::_decode_escapes | digits += body[j] | This expression has type string, but is expected to have type int
  MUTRECV     frontend/pure_ast.py::parse | body.extend(p.statement()) | `body.extend(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abs
  INTSTR      frontend/pure_ast.py::literal_eval |  | This expression has type string, but is expected to have type int
  TCOK0       frontend/pure_ast.py::iter_fields
  TCOK0       frontend/pure_ast.py::iter_child_nodes
  LISTSTR     frontend/pure_ast.py::walk | from collections import deque | [ir-emit]: `deque(<iterable>)` with arguments is not modelled: the lowering reduces a deque to the list/array 
  REBIND      frontend/pure_ast.py::copy_location | setattr(new_node, attr, value) | a function, method or class NAME is rebound after its definition (`setattr`/`delattr` of a function name at li
  UNIT        frontend/pure_ast.py::fix_missing_locations |  | This expression has type (), but is expected to have type int
  GETATTR     frontend/pure_ast.py::increment_lineno | child.lineno = getattr(child, 'lineno', 0) + n | This expression has type ref int @rho, but is expected to have type int
  NESTED      frontend/pure_ast.py::dump | NESTED def _format | nested function '_format' is lifted to a sibling of its enclosing function, and the lift is not faithful here:
  ERASED      frontend/pure_ast.py::get_source_segment | 'Get the source segment of *source* that generated *node*.' | function 'get_source_segment': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot declared
  CALLABLE    frontend/pure_ast.py::NodeVisitor.visit | return visitor(node) | This expression has type ref int @rho, it cannot be applied
  TCOK0       frontend/pure_ast.py::NodeVisitor.generic_visit
  EXC         frontend/pure_ast.py::NodeVisitor.visit_Constant | return visitor(node) | [whyml-emit]: the `else:` block of a `try` in 'nodevisitor__visit_Constant' jumps out (ROUTE #37): Module 6 ap
  REBIND      frontend/pure_ast.py::NodeTransformer.generic_visit | setattr(node, field, new_node) | a function, method or class NAME is rebound after its definition (`setattr`/`delattr` of a function name at li
  RECORD      frontend/pure_ast.py::_Precedence.next | return self.__class__(self + 1) | This expression has type PyCSL_Program._precedence, but is expected to have type int
  WITH-AS     frontend/pure_ast.py::_Unparser.__init__ |  | [whyml-emit]: a `with` item (line 4533, in 'visit_NamedExpr') uses a context expression of kind `Call` that is
  CALLABLE    frontend/pure_ast.py::_Unparser.interleave | f(next(seq)) | This expression has type int, it cannot be applied
  CALLABLE    frontend/pure_ast.py::_Unparser.items_view | traverser(items[0]) | This expression has type int, it cannot be applied
  MUTRECV     frontend/pure_ast.py::_Unparser.write | self._source.extend(text) | `self._source.extend(...)` MUTATES its receiver in place, and no certified lowering models it: the call become
  REF         frontend/pure_ast.py::_Unparser.buffered | HDR If buffer is None | This expression has type int, but is expected to have type ref 'mu @rho
  WITH-AS     frontend/pure_ast.py::_Unparser.delimit_if |  | [whyml-emit]: a `with` item (line 4527, in 'visit_NamedExpr') uses a context expression of kind `Call` that is
  ELEMSTORE   frontend/pure_ast.py::_Unparser.set_precedence |  | [ir-semantic] src/self-annotate/src/frontend/pure_ast.py: an element store through a value the model does not 
  FSTR        frontend/pure_ast.py::_Unparser.get_type_comment | return f' # type: {comment}' | This expression has type string, but is expected to have type int
  GETATTR     frontend/pure_ast.py::_Unparser._write_docstring_and_traverse_body | self.traverse(node.body[1:]) | This expression has type int, but is expected to have type array.Array.array int @rho
  TUPLE       frontend/pure_ast.py::_Unparser.visit_Dict |  | This pattern has type ('mu, 'mu1), but is expected to have type int
  NESTED      frontend/pure_ast.py::_Unparser.visit_BoolOp |  | function '_unparser__increasing_level_traverse' writes operator_precedence through a `nonlocal` declaration, a
  TUPLE       frontend/pure_ast.py::_Unparser.visit_arguments | a, d = elements | This pattern has type ('mu, 'mu1), but is expected to have type int
  WITH-AS     frontend/pure_ast.py::_Unparser.visit_Lambda | HDR With self.buffered() as buffer | function '_unparser__visit_Lambda' binds buffer with a `with ... as` clause, and no certified lowering models 
  MUTRECV     frontend/pure_ast.py::_Unparser._str_literal_helper | possible_quotes.sort(key=lambda q: q[0] == escaped_string[-1]) | `possible_quotes.sort(...)` MUTATES its receiver in place, and no certified lowering models it: the call becom
  WITH-AS     frontend/pure_ast.py::_Unparser.visit_JoinedStr | HDR With self.buffered() as buffer | function '_unparser__visit_JoinedStr' binds buf, buffer with a `with ... as` clause, and no certified lowering
  EXC         frontend/pure_ast.py::_Unparser._write_fstring_inner |  | this expression raises unlisted exception ValueError
  INTSTR      frontend/pure_ast.py::_Unparser.visit_MatchStar | name = '_' | This expression has type string, but is expected to have type int
  KWARG       frontend/pure_ast.py::_Unparser.visit_MatchMapping | self.interleave(lambda: self.write(', '), write_key_pattern_pair, zip( | `zip(..., strict=...)` is not modelled: a builtin's keyword arguments are DISCARDED by its lowering, so the bu
  KWARG       frontend/pure_ast.py::_Unparser.visit_MatchClass | self.interleave(lambda: self.write(', '), write_attr_pattern, zip(attr | `zip(..., strict=...)` is not modelled: a builtin's keyword arguments are DISCARDED by its lowering, so the bu
  SYNTAX      frontend/pure_ast.py::unparse | unparser = _Unparser() | syntax error
  KWARG       frontend/pure_ast.py::_self_test | src = open(path, encoding='utf-8').read() | `open(..., encoding=...)` is not modelled: a builtin's keyword arguments are DISCARDED by its lowering, so the
  DEFASSIGN   frontend/pure_ast.py::main | source = _sys.stdin.buffer.read() | [ir-semantic] src/self-annotate/src/frontend/pure_ast.py line 5596: src/self-annotate/src/frontend/pure_ast.py
  TCOK0       ir_schema.py::validate_ir
  MUTRECV     module6_whyml/abstract_ops.py::AbstractOpsMixin._add_abstract_op | self._abstract_ops.setdefault('_pyobj_state', 'val _pyobj_state : ref  | `self._abstract_ops.setdefault(...)` MUTATES its receiver in place, and no certified lowering models it: the c
  LISTSTR     module6_whyml/abstract_ops.py::AbstractOpsMixin._advance_past_referenced_axiom_decls | HDR If len(p) >= 3 and p[0] == 'val' and (p[1] in ('function', 'consta | This expression has type int, but is expected to have type array.Array.array 'mu @rho
  MUTRECV     module6_whyml/abstract_ops.py::AbstractOpsMixin._insert_abstract_val_block | out.insert(insert_idx, line) | `out.insert(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abst
  DICT        module6_whyml/auto_trust.py::AutoTrustMixin._build_witness_str | field_types = field_types or {} | This expression has type int, but is expected to have type string -> option. Option.option string /tmp/claude-
  REBIND      module6_whyml/auto_trust.py::AutoTrustMixin._check_witness_vals |  | a name's runtime value is not the one the model reads (a dynamic `eval` that can bind into the module namespac
  NESTED      module6_whyml/auto_trust.py::AutoTrustMixin._should_auto_trust_tuple_return | NESTED def _tuple_return_has_array_slot | nested function 'autotrustmixin___tuple_return_has_array_slot' is lifted to a sibling of its enclosing functio
  SKIP-NOLIVE module6_whyml/expr_ghost_collections.py::GhostCollectionOpsMixin._e
  SKIP-NOLIVE module6_whyml/expr_ghost_spec_ops.py::GhostSpecOpsMixin._e
  SKIP-NOLIVE module6_whyml/expr_ghost_spec_ops.py::GhostSpecOpsMixin._expr_to_whyml_string_ctx
  RECORD      module6_whyml/expr_ghost_spec_ops.py::GhostSpecOpsMixin._handle_proj_expr | idx = int(node.index) | This expression has type PyCSL_Program.emit_ir, but is expected to have type int
  RECORD      module6_whyml/expr_ghost_spec_ops.py::GhostSpecOpsMixin._handle_ctor_payload_expr | idx = int(node.index) | This expression has type PyCSL_Program.emit_ir, but is expected to have type int
  SKIP-NOLIVE module6_whyml/expressions.py::ExpressionEmissionMixin._add_abstract_op
  MCYCLE      module6_whyml/expressions.py::ExpressionEmissionMixin._is_emit_ir_expr |  | [ir-semantic] src/self-annotate/src/module6_whyml/expressions.py: the functions ['expressionemissionmixin___is
  RECORD      module6_whyml/expressions.py::ExpressionEmissionMixin._e | return self._expr_to_whyml(ir, lr) | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /tmp/claude-1000/-home-fabri
  ERASED      module6_whyml/expressions.py::ExpressionEmissionMixin._to_bool | raise PyCSLSemanticError(f"the truthiness of `{ir_expr.get('name')}` i | function 'expressionemissionmixin___to_bool': an erased (`Any`/`object`/unannotated/TypeVar) value flows into 
  OPAQUEWRITE module6_whyml/expressions.py::ExpressionEmissionMixin._match_pattern_cond | return self._match_pattern_cond(pat['inner'], subject, local_refs) | [ir-semantic] src/self-annotate/src/module6_whyml/expressions.py: 'expressionemissionmixin___match_pattern_con
  ERASED      module6_whyml/expressions.py::ExpressionEmissionMixin._emit_membership | _mo = rhs.get('object') | function 'expressionemissionmixin___emit_membership': an erased (`Any`/`object`/unannotated/TypeVar) value flo
  ALIAS       module6_whyml/expressions.py::ExpressionEmissionMixin._emit_bitwise_or_power |  | [ir-semantic] src/self-annotate/src/module6_whyml/expressions.py line 497: an in-place mutation reached throug
  DEFASSIGN   module6_whyml/expressions.py::ExpressionEmissionMixin._is_string_expr | return self._is_string_expr(self._todict_routed_ir(_al, _kir.get('valu | [ir-semantic] src/self-annotate/src/module6_whyml/expressions.py line 501: src/self-annotate/src/module6_whyml
  TUPALIAS    module6_whyml/expressions.py::ExpressionEmissionMixin._handle_binop | _optv = _strv = None | [module6-assign]: function 'expressionemissionmixin___handle_binop': mutating a collection that a TUPLE-UNPACK
  GETATTR     module6_whyml/expressions.py::ExpressionEmissionMixin._union_local_read_projection | return self._union_read_projection(getattr(self, '_current_symbol_tabl | This expression has type int, but is expected to have type PyCSL_Program. _union__union_local_read_projection_
  NESTED      module6_whyml/expressions.py::ExpressionEmissionMixin._iter_len_expr | NESTED def _operand_len | nested function 'expressionemissionmixin___operand_len' is lifted to a sibling of its enclosing function, and 
  ERASED      module6_whyml/expressions.py::ExpressionEmissionMixin._handle_len_call | _ob = arg_ir.get('object') | function 'expressionemissionmixin___handle_len_call': an erased (`Any`/`object`/unannotated/TypeVar) value flo
  ERASED      module6_whyml/expressions.py::ExpressionEmissionMixin._handle_join_call | _sepg = self._expr_to_whyml(expr.get('receiver'), local_refs or set(), | function 'expressionemissionmixin___handle_join_call': an erased (`Any`/`object`/unannotated/TypeVar) value fl
  DICT        module6_whyml/expressions.py::ExpressionEmissionMixin._handle_sum_call | arg_ir = expr.get('args', [{}])[0] if expr.get('args') else {} | This expression has type int, but is expected to have type string /tmp/claude-1000/-home-fabrice-git-pycsl/011
  ARRAY-REASSIGN module6_whyml/expressions.py::ExpressionEmissionMixin._resolve_dotted_signature |  | reassigning an array LOCAL from a non-literal right-hand side is not modelled: the local is represented as a f
  MUTRECV     module6_whyml/expressions.py::ExpressionEmissionMixin._handle_dotted_call | del _ops186[:] | [ir-emit]: `del <seq>[i:j]` (a SLICE delete) is not modelled: Python's slice `del` REMOVES a whole range, shif
  GENEXP      module6_whyml/expressions.py::ExpressionEmissionMixin._coerce_dotted_args | HDR For (arg, ptype) in zip(args, param_types) | This expression has type array.Array.array string @rho, but is expected to have type int /tmp/claude-1000/-hom
  ALIAS       module6_whyml/expressions.py::ExpressionEmissionMixin._dotted_ensures_suffix | _prev_params = self._current_params | [module6-whyml]: function 'expressionemissionmixin___dotted_ensures_suffix': a dict/set value reaches the dict
  ERASED      module6_whyml/expressions.py::ExpressionEmissionMixin._handle_struct_call | fmt = fmt_ir.get('value', '') | function 'expressionemissionmixin___handle_struct_call': an erased (`Any`/`object`/unannotated/TypeVar) value 
  LISTSTR     module6_whyml/expressions.py::ExpressionEmissionMixin._emit_contract_logic_symbol | HDR If len(raw_args) != len(args) | This expression has type int, but is expected to have type array.Array.array 'mu @rho /tmp/claude-1000/-home-f
  R301        module6_whyml/expressions.py::ExpressionEmissionMixin._linear_form | lf = self._linear_form(ir.get('left', {})) | dropped unpacking / loop target refused (route #301) -- function '_linear_form': an unpacking / loop target of
  R301        module6_whyml/expressions.py::ExpressionEmissionMixin._static_width |  | dropped unpacking / loop target refused (route #301) -- function '_static_width': an unpacking / loop target o
  TUPALIAS    module6_whyml/expressions.py::ExpressionEmissionMixin._handle_call_expr | _kwo232, _poo232, _hkw232 = _pk232 | [module6-assign]: function 'expressionemissionmixin___handle_call_expr': mutating a collection that a TUPLE-UN
  MUTRECV     module6_whyml/expressions.py::ExpressionEmissionMixin._content_string_method | _s = _fs_work.pop() | `_fs_work.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an ab
  DEFASSIGN   module6_whyml/expressions.py::ExpressionEmissionMixin._call_named_builtins | coerced = [self._coerce_to_int(a) for a in args] | [ir-semantic] src/self-annotate/src/module6_whyml/expressions.py line 968: src/self-annotate/src/module6_whyml
  ERASED      module6_whyml/expressions.py::ExpressionEmissionMixin._handle_isinstance | '`isinstance(x, T)` → `subtag (\\typeof x) T` (decision: \\subtag, not | function 'expressionemissionmixin___handle_isinstance': an erased (`Any`/`object`/unannotated/TypeVar) value f
  NESTED      module6_whyml/expressions.py::ExpressionEmissionMixin._call_record_constructor | NESTED def _field_default | nested function 'expressionemissionmixin___field_default' is lifted to a sibling of its enclosing function, an
  GETATTR     module6_whyml/expressions.py::ExpressionEmissionMixin._call_bytes_methods | is_arr = any((st.startswith(p) for p in _ARR)) or (st.lstrip('!').repl | This expression has type int, but is expected to have type string /tmp/claude-1000/-home-fabrice-git-pycsl/011
  MUTRECV     module6_whyml/expressions.py::ExpressionEmissionMixin._handle_subscript | _x170 = _w170.pop() | `_w170.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstr
  R301        module6_whyml/expressions.py::ExpressionEmissionMixin._handle_attribute_expr | _ecls = next((c for c, v in getattr(self, '_record_types', {}).items() | dropped unpacking / loop target refused (route #301) -- function '_handle_attribute_expr': an unpacking / loop
  ALIAS       module6_whyml/expressions.py::ExpressionEmissionMixin._push_quant_binder | dl = self._dict_locals | aliasing a mutated dict is out of scope: `dl = self._dict_locals` binds a SECOND NAME TO THE SAME dict in Pyth
  MUTRECV     module6_whyml/expressions.py::ExpressionEmissionMixin._pop_quant_binder | self._quant_record_binders.pop(var, None) | `self._quant_record_binders.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the 
  MUTRECV     module6_whyml/expressions.py::ExpressionEmissionMixin._handle_fstring_expr | _n291 = _wk291.pop() | `_wk291.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abst
  RECORD      module6_whyml/expressions.py::ExpressionEmissionMixin._handle_ifexpr_expr | HDR If _ms and _is_arr_var(_bd) and _is_arr_var(_od) | This expression has type PyCSL_Program.emit_ir, but is expected to have type int /tmp/claude-1000/-home-fabric
  DEFASSIGN   module6_whyml/expressions.py::ExpressionEmissionMixin._expr_to_whyml | _r231_w = self._expr_to_whyml(_r231_v, local_refs, invariant_ctx, subs | [ir-semantic] src/self-annotate/src/module6_whyml/expressions.py line 2295: src/self-annotate/src/module6_whym
  ERASED      module6_whyml/expressions.py::ExpressionEmissionMixin._expr_to_whyml_string_ctx | name = ir.get('name', '') | function 'expressionemissionmixin___expr_to_whyml_string_ctx': an erased (`Any`/`object`/unannotated/TypeVar) 
  ERASED      module6_whyml/functions.py::FunctionEmissionMixin._param_type_str | symtype = symbol_table.get(arg) | function 'functionemissionmixin___param_type_str': an erased (`Any`/`object`/unannotated/TypeVar) value flows 
  R301        module6_whyml/functions.py::FunctionEmissionMixin._reset_function_state | _el303 = _v303.get('elts') if _v303.get('type') in ('Tuple', 'List') e | dropped unpacking / loop target refused (route #301) -- function '_reset_function_state': an unpacking / loop 
  ERASED      module6_whyml/functions.py::FunctionEmissionMixin._emit_contracts | lines: List[str] = [] | function 'functionemissionmixin___emit_contracts': an erased (`Any`/`object`/unannotated/TypeVar) value flows 
  NESTED      module6_whyml/functions.py::FunctionEmissionMixin._emit_narrowing_vc | NESTED def conj | nested function 'functionemissionmixin__conj' is lifted to a sibling of its enclosing function, and the lift i
  INTSTR      module6_whyml/functions.py::FunctionEmissionMixin._emit_union_arm_vc | HDR If symtype in seen_variants | This expression has type int, but is expected to have type string
  ERASED      module6_whyml/functions.py::FunctionEmissionMixin._emit_function | _d = str(_d) | function 'functionemissionmixin___emit_function': an erased (`Any`/`object`/unannotated/TypeVar) value flows i
  DICT        module6_whyml/functions.py::FunctionEmissionMixin._emit_subtyping_goals | overrides = [o for o in overrides if o.get('from_conforms_to')] | This expression has type int, but is expected to have type array.Array.array int @rho
  ERASED      module6_whyml/functions.py::FunctionEmissionMixin._render_refinement_goal | _rx278: List[str] = [] | function 'functionemissionmixin___render_refinement_goal': an erased (`Any`/`object`/unannotated/TypeVar) valu
  INTSTR      module6_whyml/functions.py::FunctionEmissionMixin._parse_mixin_sig | ret = 'int' | This expression has type string, but is expected to have type int
  ERASED      module6_whyml/functions.py::FunctionEmissionMixin._mixin_dep_pseudo_functions | pseudo: List[Dict[str, Any]] = [] | function 'functionemissionmixin___mixin_dep_pseudo_functions': an erased (`Any`/`object`/unannotated/TypeVar) 
  TCOK0       module6_whyml/identifiers.py::stable_hash
  FSTR        module6_whyml/identifiers.py::whyml_ident | sanitized.append(ascii_ch if ascii_ch else f'u{ord(ch)}') | This expression has type string, but is expected to have type int
  REBIND      module6_whyml/preamble.py::PreambleEmissionMixin._scan_preamble_needs |  | a function, method or class NAME is rebound after its definition (a write through a namespace dict at line 109
  FSTR        module6_whyml/preamble.py::PreambleEmissionMixin._emit_preamble_uses | out = [f'module {module_name}', '  use int.Int', '  use int.EuclideanD | This expression has type seq.Seq.seq int, but is expected to have type seq. Seq.seq string
  ERASED      module6_whyml/preamble.py::PreambleEmissionMixin._emit_preamble_exceptions | out: List[str] = [] | function 'preambleemissionmixin___emit_preamble_exceptions': an erased (`Any`/`object`/unannotated/TypeVar) va
  MUTRECV     module6_whyml/preamble.py::PreambleEmissionMixin._precompute_axiom_logic_funcs | self._axiom_logic_funcs.add(fn) | `self._axiom_logic_funcs.add(...)` MUTATES its receiver in place, and no certified lowering models it: the cal
  INTSTR      module6_whyml/preamble.py::PreambleEmissionMixin._emit_class_inv_axioms | out.append(f'  (* {qn} — {provenance} *)') | This expression has type int, but is expected to have type string
  DICT        module6_whyml/preamble.py::PreambleEmissionMixin._emit_preamble_axioms | kept_qualnames.add(entry['qualname']) | This expression has type int, but is expected to have type string
  APPENDLEN   module6_whyml/preamble.py::PreambleEmissionMixin._emit_preamble | out.append('') | [module6-whyml]: `out.append(...)` appends to a list whose length this lowering cannot track: the local is not
  TUPALIAS    module6_whyml/preamble.py::PreambleEmissionMixin._emit_shared_state | mutex, inv_ir = sorted_mi[i] | [module6-assign]: function 'preambleemissionmixin___emit_shared_state': mutating a collection that a TUPLE-UNP
  LISTSTR     module6_whyml/preamble.py::PreambleEmissionMixin._mutex_inv_application | params = self._mutex_inv_params(mutex, inv_str) | This expression has type array.Array.array string @rho, but is expected to have type int
  LISTSTR     module6_whyml/preamble.py::PreambleEmissionMixin._inductive_referenced_axiom_decls | HDR If len(parts) >= 3 and parts[0] == 'val' and (parts[1] == 'functio | This expression has type int, but is expected to have type array.Array.array 'mu @rho
  LISTSTR     module6_whyml/preamble.py::PreambleEmissionMixin._emit_uncited_axiom_func_decls | HDR If not wanted | This expression has type int, but is expected to have type array.Array.array 'mu @rho
  NESTED      module6_whyml/preamble.py::PreambleEmissionMixin._emit_inductive_decls | NESTED def _emit_member | nested function 'preambleemissionmixin___emit_member' is lifted to a sibling of its enclosing function, and th
  NESTED      module6_whyml/preamble.py::PreambleEmissionMixin._subst_self_in_expr | NESTED def rec | nested function 'preambleemissionmixin__rec' is lifted to a sibling of its enclosing function, and the lift is
  SET         module6_whyml/preamble.py::PreambleEmissionMixin._fresh_globals_facts | HDR For ens in rec.get('init_ensures', []) or [] | This expression has type array.Array.array int @rho, but is expected to have type int
  MUTRECV     module6_whyml/preamble.py::PreambleEmissionMixin._emit_module_globals | self._module_global_classes.pop('result', None) | `self._module_global_classes.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the
  MUTRECV     module6_whyml/preamble.py::PreambleEmissionMixin._emit_type_decls | _cur = _work.pop() | `_work.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstr
  MUTPARAM    module6_whyml/preamble.py::PreambleEmissionMixin._emit_opaque_class_aliases | declared_types.add(st) | [module6-whyml]: in-place mutation of dict/set parameter 'declared_types' (`declared_types.add(...)`) is out o
  NESTED      module6_whyml/scc.py::compute_sccs | NESTED def strongconnect | nested function 'strongconnect' is lifted to a sibling of its enclosing function, and the lift is not faithful
  ERASED      module6_whyml/scc.py::sort_functions_by_scc | call_graph: Dict[str, Set[str]] = {} | function 'sort_functions_by_scc': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot decla
  SKIP-NOLIVE module6_whyml/statements.py::StatementEmissionMixin._add_abstract_op
  SKIP-NOLIVE module6_whyml/statements.py::StatementEmissionMixin._resolve_dotted_signature
  SKIP-NOLIVE module6_whyml/statements.py::StatementEmissionMixin._is_emit_ir_expr
  SKIP-NOLIVE module6_whyml/statements.py::StatementEmissionMixin._coerce_to_int
  SKIP-NOLIVE module6_whyml/statements.py::StatementEmissionMixin._expr_to_whyml
  SKIP-NOLIVE module6_whyml/statements.py::StatementEmissionMixin._expr_to_whyml_string_ctx
  SKIP-NOLIVE module6_whyml/statements.py::StatementEmissionMixin._is_string_expr
  SKIP-NOLIVE module6_whyml/statements.py::StatementEmissionMixin._track_collection_metadata
  SKIP-NOLIVE module6_whyml/statements.py::StatementEmissionMixin._e
  SKIP-NOLIVE module6_whyml/statements.py::StatementEmissionMixin._maybe_emit_no_exception_assert
  SKIP-NOLIVE module6_whyml/statements.py::StatementEmissionMixin._mutex_inv_application
  SKIP-NOLIVE module6_whyml/statements.py::StatementEmissionMixin._handle_return_stmt
  INTSTR      module6_whyml/statements.py::StatementEmissionMixin._emit_first_assign | _empty = self._dv_empty_default(nu) | This expression has type int, but is expected to have type string /tmp/claude-1000/-home-fabrice-git-pycsl/011
  DEFASSIGN   module6_whyml/statements.py::StatementEmissionMixin._handle_assign_stmt | _cls279 = set(_live279) | [ir-semantic] src/self-annotate/src/module6_whyml/statements.py line 1211: src/self-annotate/src/module6_whyml
  DICT        module6_whyml/statements.py::StatementEmissionMixin._seq_init_expr |  | This expression has type PyCSL_Program.emit_ir, but is expected to have type string -> option.Option.option in
  ALIAS       module6_whyml/statements.py::StatementEmissionMixin._handle_ghost_assign_stmt | code += ';\n' + self._stmts_to_whyml(rest, local_refs, declared_refs,  | [module6-whyml]: function 'statementemissionmixin___handle_array_slice_set_stmt': a dict/set value reaches `se
  ALIAS       module6_whyml/statements.py::StatementEmissionMixin._handle_tuple_unpack_stmt | rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, inde | [module6-whyml]: function 'statementemissionmixin___handle_array_slice_set_stmt': a dict/set value reaches `se
  RECORD      module6_whyml/statements.py::StatementEmissionMixin._handle_array_set_stmt | return self._handle_expr_stmt(stmt_from_dict({'stmt': 'Expr', 'value': | This expression has type PyCSL_Program.emit_ir, but is expected to have type PyCSL_Program.exprstmt @rho /tmp/
  GETATTR     module6_whyml/statements.py::StatementEmissionMixin._handle_augassign_stmt | HDR If target in set(getattr(self, '_formal_params', []) or []) and (t | This expression has type array.Array.array int @rho, but is expected to have type int /tmp/claude-1000/-home-f
  DEFASSIGN   module6_whyml/statements.py::StatementEmissionMixin._handle_expr_stmt | raise PyCSLSemanticError(f'r2c-local: the path mutation of `{_r2c_root | [ir-semantic] src/self-annotate/src/module6_whyml/statements.py line 2549: src/self-annotate/src/module6_whyml
  MUTRECV     module6_whyml/statements.py::StatementEmissionMixin._stmts_to_whyml | _a84_n = _a84_stack.pop() | `_a84_stack.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an 
  ERASED      module6_whyml/statements.py::StatementEmissionMixin._emit_frame_condition | obj = a.get('object') | function 'statementemissionmixin___emit_frame_condition': an erased (`Any`/`object`/unannotated/TypeVar) value
  ALIAS       module6_whyml/statements.py::StatementEmissionMixin._typed_local_vars | self._emit_ir_local_vars = self._collect_emit_ir_result_locals(body_st | [module6-whyml]: function 'statementemissionmixin___typed_local_vars': a dict/set value reaches the dict/set f
  ALIAS       module6_whyml/statements.py::StatementEmissionMixin._emit_body_code | self._current_append_targets = append_targets | [module6-whyml]: function 'statementemissionmixin___emit_body_code': a dict/set value reaches the dict/set fie
  SKIP-NOLIVE module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._is_string_expr
  SKIP-NOLIVE module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._add_abstract_op
  SKIP-NOLIVE module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._seq_init_expr
  SKIP-NOLIVE module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._expr_to_whyml
  SKIP-NOLIVE module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._coerce_to_int
  SKIP-NOLIVE module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._to_bool
  SKIP-NOLIVE module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._stmts_to_whyml
  ISBOOL      module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._classify_iterable | HDR If iter_ir.get('_r2b_hval_seq') is True | [whyml-emit]: an IDENTITY test against a `bool` literal (`X is True` / `X is False`) is refused unless the emi
  NESTED      module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._handle_for_stmt | NESTED def _bind_lines | nested function 'controlflowstmtmixin___bind_lines' is lifted to a sibling of its enclosing function, and the 
  MCYCLE      module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._callee_raised_in |  | [ir-semantic] src/self-annotate/src/module6_whyml/stmt_control_flow.py: the functions ['controlflowstmtmixin__
  SKIP-NOLIVE module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._match_pattern_cond
  REBIND      module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._render_match_pattern | body = _ctor + (''.join((' ' + s for s in sub)) if sub else '') | a name's runtime value is not the one the model reads (an attribute or item written, or a namespace reached, a
  MUTRECV     module6_whyml/struct_format.py::parse_format | slots.extend([slot_type] * count) | `slots.extend(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an ab
  DICT        module6_whyml/struct_format.py::calcsize | HDR If char in sizes | This expression has type int, but is expected to have type string
  ALIAS       module6_whyml/types.py::TypeInferenceMixin._track_collection_metadata | _rb = getattr(self, '_rebound_collections', None) | [module6-whyml]: function 'typeinferencemixin___track_collection_metadata': a dict/set value reaches the dict/
  R301        module6_whyml/types.py::TypeInferenceMixin._collect_array_var_assigns | found |= self._collect_array_var_assigns(s[k]) | dropped unpacking / loop target refused (route #301) -- function '_collect_array_var_assigns': an unpacking / 
  DICT        proof2why3/canonical.py::substitute | return Var(mapping.get(t.name, t.name)) | This expression has type PyCSL_Program.var @rho, but is expected to have type PyCSL_Program.term
  GETATTR     proof2why3/canonical.py::_expand_nat_to_int | new_body = _expand_nat_to_int(t.body) | This expression has type PyCSL_Program.term, but is expected to have type int
  GENEXP      proof2why3/canonical.py::_alpha_rename | return App(head=t.head, args=tuple((_alpha_rename(a, counter) for a in | This expression has type int, but is expected to have type array.Array.array int @rho
  TUPALIAS    proof2why3/canonical.py::_dedup_arrow_chain | recursed = _dedup_arrow_chain(h) | [module6-assign]: function '_dedup_arrow_chain': mutating a collection that a TUPLE-UNPACKING assignment alias
  NESTED      proof2why3/canonical.py::_ac_normalize | NESTED def collect | nested function 'collect' is lifted to a sibling of its enclosing function, and the lift is not faithful here:
  TUPALIAS    proof2why3/canonical.py::_sort_arrow_hypotheses | hyps_normalized = [_sort_arrow_hypotheses(h) for h in hyps] | [module6-assign]: function '_sort_arrow_hypotheses': mutating a collection that a TUPLE-UNPACKING assignment a
  MUTRECV     proof2why3/canonical.py::_flatten_foralls | binders.extend(cur.binders) | `binders.extend(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an 
  RECORD      proof2why3/canonical.py::_normalize_names | return Var(_camel_to_snake(t.name)) | This expression has type PyCSL_Program.var @rho, but is expected to have type PyCSL_Program.term
  INTSTR      proof2why3/canonical.py::_normalize_type_string | out_parts.append(_camel_to_snake(token)) | This expression has type int, but is expected to have type string
  RECORD      proof2why3/canonical.py::_iff_app_to_binop | HDR If isinstance(t, App) and t.head == 'iff' and (len(t.args) == 2) | This expression has type list.List.list PyCSL_Program.term, but is expected to have type int
  INTSTR      proof2why3/crosscheck.py::CrossCheckResult.diagnostic | lines.append(f"  {label}: {('PASS' if ok else 'FAIL')}") | This expression has type string, but is expected to have type int
  INTSTR      proof2why3/crosscheck.py::_load_axiom_registry | src = (_REPO_ROOT / 'src' / 'pycsl' / 'module6_whyml' / 'preamble.py') | This expression has type string, but is expected to have type int
  KWARG       proof2why3/crosscheck.py::crosscheck_file | rocq_qns = sorted({d.qualname for d in directives if d.prover == 'rocq | `sorted(..., key=...)` is not modelled: a builtin's keyword arguments are DISCARDED by its lowering, so the bu
  EXT         proof2why3/crosscheck.py::main | argv = sys.argv[1:] | This expression has type int, but is expected to have type array.Array.array int @rho /tmp/claude-1000/-home-f
  BOOL        proof2why3/crosscheck_ir.py::IRCrossCheckResult.pairwise |  | This expression has type bool, but is expected to have type int /tmp/claude-1000/-home-fabrice-git-pycsl/0119d
  OPTREC      proof2why3/crosscheck_ir.py::IRCrossCheckResult.diagnostic | HDR If self.rocq_canon is not None | This expression has type int, but is expected to have type option.Option. option PyCSL_Program.term
  INTSTR      proof2why3/crosscheck_ir.py::_load_axiom_registry | src = (_REPO_ROOT / 'src' / 'pycsl' / 'module6_whyml' / 'preamble.py') | This expression has type string, but is expected to have type int
  KWARG       proof2why3/crosscheck_ir.py::crosscheck_file_ir | rocq_qns = sorted({d.qualname for d in directives if d.prover == 'rocq | `sorted(..., key=...)` is not modelled: a builtin's keyword arguments are DISCARDED by its lowering, so the bu
  EXT         proof2why3/crosscheck_ir.py::main | argv = sys.argv[1:] | This expression has type int, but is expected to have type array.Array.array int @rho /tmp/claude-1000/-home-f
  SKIP-DNC-EFFECT proof2why3/extract.py::extract_rocq_statements
  STRM        proof2why3/extract.py::_split_rocq_check_output | HDR If lines[i].strip() == qn | This expression has type string, but is expected to have type int
  SKIP-DNC-EFFECT proof2why3/extract.py::extract_lean_statements
  SKIP-DNC-EFFECT proof2why3/extract_lean_meta.py::extract_lean_statements_meta
  MUTRECV     proof2why3/from_lean_json.py::_linearize_app | args.insert(0, cur['arg']) | `args.insert(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abs
  DICT        proof2why3/from_lean_json.py::_is_ofnat_lit | head, args = _linearize_app(ast) | This expression has type string -> option.Option.option int, but is expected to have type int
  ERASED      proof2why3/from_lean_json.py::project_to_ir | ty_term = project_to_ir(ty_ast, ctx) | function 'project_to_ir': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot declared as a
  PYVAL       proof2why3/from_sexp.py::_construct_indices | parts = _find_kername_components(payload) | This expression has type int, but is expected to have type PyCSL_Program. pyval
  RECORD      proof2why3/from_sexp.py::_find_construct_idx | r = _find_construct_idx(elem) | This expression has type PyCSL_Program._union__find_construct_idx_2, but is expected to have type int
  PYVAL       proof2why3/from_sexp.py::_project_app | sname = _const_name(head) | This expression has type int, but is expected to have type PyCSL_Program. pyval
  ERASED      proof2why3/from_sexp.py::project_constr | return project_constr(constr[1], ctx) | function 'project_constr': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot declared as 
  STRM        proof2why3/normalize.py::normalize_prover_output | out = out.replace(u, a) | This expression has type int, but is expected to have type string
  NESTED      proof2why3/normalize.py::_nat_to_int_with_sidecond | NESTED def repl | This expression has type int, but is expected to have type string
  EXT         proof2why3/normalize.py::_expand_anon_binders | new = pattern.sub(lambda m: f'{m.group(1).strip()} -> ', s, count=1) | This expression has type int -> string, but is expected to have type int
  KWARG       proof2why3/normalize.py::_alpha_rename | binders_match = re.match('forall\\s+([a-zA-Z_0-9 ]+?)\\s*:', s) | `sorted(..., key=...)` is not modelled: a builtin's keyword arguments are DISCARDED by its lowering, so the bu
  EXT         proof2why3/normalize.py::normalize_whyml_axiom | out = re.sub('\\b(\\w+(?:\\s+\\w+)*)\\s*<=\\s*(\\w+(?:\\s+\\w+)*)', la | This expression has type int, but is expected to have type string
  STRM        proof2why3/parser.py::normalize_surface | out = out.replace(u, a) | This expression has type int, but is expected to have type string /tmp/claude-1000/-home-fabrice-git-pycsl/011
  UNBOUND     proof2why3/parser.py::lex |  | unbound function or predicate symbol 'toks' /tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-2
  EXC         proof2why3/parser.py::parse_type_expr | HDR except (SyntaxError, IndexError) as exc | [whyml-emit]: 'parse_type_expr' reads the exception object 'exc' bound by `except ... as exc` (ROUTE #233). Th
  SKIP-DNC-EFFECT proof2why3/sertop.py::sertop_version
  TCOK0       proof2why3/sertop.py::_sexp_tokens
  MUTRECV     proof2why3/sertop.py::_sexp_parse | tok = tokens.pop(0) | `tokens.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abst
  LISTSTR     proof2why3/sertop.py::parse_sexp | return _sexp_parse(tokens) | This expression has type int, but is expected to have type array.Array.array string @rho
  SKIP-DNC-EFFECT proof2why3/sertop.py::run_sertop_batch
  CALLABLE    proof2why3/sertop.py::SertopSession.type_of_batch | cwd = self.cwd or Path.cwd() | This expression has type ref int @rho, it cannot be applied
  SKIP-DNC-EFFECT proof2why3/sertop.py::extract_via_sertop
  TUPLE       proof_axiom_allowlist.py::parse_rocq_assumptions_block | return (True, []) | This expression has type (int, array.Array.array int @rho), but is expected to have type (int, int)
  EXT         pycsl.py::_make_temp_mlw_path | fd, path = tempfile.mkstemp(prefix='.pycsl_', suffix='.mlw') | This expression has type int, but is expected to have type string /tmp/claude-1000/-home-fabrice-git-pycsl/011
  SKIP-DNC-EFFECT pycsl.py::_generate_rocq_obligations
  WITH-AS     pycsl.py::_sha256_file | HDR With open(path, 'rb') as f | function '_sha256_file' binds f with a `with ... as` clause, and no certified lowering models it. `_py_stmt_wi
  RECORD      pycsl.py::_find_coqc | return _sh.which('coqc') | This expression has type int, but is expected to have type PyCSL_Program. _union__find_coqc_1 /tmp/claude-1000
  SKIP-DNC-EFFECT pycsl.py::_check_rocq_proofs
  TCOK0       pycsl.py::_parse_args
  DEFASSIGN   pycsl.py::_build_soundness_report | _ma_lbl = str(_ma_x.get('name')) | [ir-semantic] src/self-annotate/src/pycsl.py line 543: src/self-annotate/src/pycsl.py (line 543): function `_b
  DICT        pycsl.py::_print_soundness_report | print(_json.dumps(report, indent=2)) | This expression has type string -> option.Option.option int, but is expected to have type int /tmp/claude-1000
  OTHER       pycsl.py::_run_pipeline | _cls257, _cbases257 = ({}, {}) | Subscript assignment to undefined variable '_cls257' in function '_run_pipeline'.
  SKIP-DNC-EFFECT pycsl.py::_why3_typecheck
  LISTSTR     pycsl.py::_parse_goal_blocks | header = '\n'.join(cur_header) | This expression has type seq.Seq.seq 'mu, but is expected to have type int /tmp/claude-1000/-home-fabrice-git-
  TUPALIAS    pycsl.py::_parse_why3_json | obj, end = dec.raw_decode(s, i) | [module6-assign]: function '_parse_why3_json': mutating a collection that a TUPLE-UNPACKING assignment aliases
  GENEXP      pycsl.py::_json_goal_records | return [r for r in _parse_why3_json(stdout) if 'prover-result' in r] | This expression has type int, but is expected to have type array.Array.array int @rho /tmp/claude-1000/-home-f
  SET         pycsl.py::_record_key | return ((loc.get('file-name'), loc.get('start-line'), loc.get('start-c | This expression has type array.Array.array int @rho, but is expected to have type int /tmp/claude-1000/-home-f
  DICT        pycsl.py::_merge_records_best_of_n | k = _record_key(rec) | This expression has type int, but is expected to have type string -> option. Option.option int /tmp/claude-100
  STRM        pycsl.py::_synthesize_block | expl = ', '.join(term.get('explanations') or []) or 'goal' | This expression has type array.Array.array int @rho, but is expected to have type int /tmp/claude-1000/-home-f
  STRM        pycsl.py::_synthesize_legacy_text | return '\n\n'.join((_synthesize_block(r) for r in records)) | This expression has type int, but is expected to have type string /tmp/claude-1000/-home-fabrice-git-pycsl/011
  DICT        pycsl.py::_residual_selectors_from_records | HDR If _record_is_valid(rec) | This expression has type int, but is expected to have type string -> option. Option.option PyCSL_Program.hval 
  EXT         pycsl.py::_function_body_eqs | cur = m.group(1) | This expression has type int, but is expected to have type string /tmp/claude-1000/-home-fabrice-git-pycsl/011
  SKIP-DNC-EFFECT pycsl.py::_run_vacuity_gate
  SKIP-NESTED-IN-TRUSTED pycsl.py::_run_vacuity_gate._probe_one
  SKIP-NESTED-IN-TRUSTED pycsl.py::_run_vacuity_gate._probe_one._is_false_goal
  SKIP-DNC-EFFECT pycsl.py::_run_why3_prove
  NESTED      pycsl.py::_dispatch_provers | NESTED def _finalize | nested function '_finalize' is lifted to a sibling of its enclosing function, and the lift is not faithful her
  SKIP-NESTED-IN-TRUSTED pycsl.py::_dispatch_provers._finalize
  SKIP-DNC-EFFECT pycsl.py::_run_proofs
  SKIP-NESTED-IN-TRUSTED pycsl.py::_run_proofs._gate_vacuity_then_succeed
  ERASED      pycsl.py::_run_audit_mode | 'Handle --audit-proof / --audit-proof-rocq / --audit-proof-lean.\n\n   | function '_run_audit_mode': an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot declared as
  WITH-AS     pycsl.py::_resolve_runtime_config | HDR With open(config_path) as _cf | function '_resolve_runtime_config' binds _cf with a `with ... as` clause, and no certified lowering models it.
  DEFASSIGN   pycsl.py::main | source_code = f.read() | [ir-semantic] src/self-annotate/src/pycsl.py line 1472: src/self-annotate/src/pycsl.py (line 1472): function `
```
