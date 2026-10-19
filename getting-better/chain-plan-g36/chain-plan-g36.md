# Chain plan g36 — full blocker chains for the remaining `\trusted` mirror markers

Measured 2026-10-17 at `d257099c` (worktree `pycsl-plan`, detached, all edits in scratch copies,
every emit `--no-proof --keep-mlw` through `heavy.sh` QUICK). Population = the 430 line-prefix
markers of `getting-better/trusted-reasons.tsv` (`check-trusted-reasons.py`: 430 <-> 430). The
`grep -cF '#@ \trusted'` count of 458 includes 28 prose mentions inside comment blocks.

## Method (and what it can and cannot say)

For every row: port the LIVE body **and live signature** into the mirror (marker deleted), emit,
record the first blocker, LOCATE it, NEUTRALISE it, re-emit — first pass up to 8 blocker events
(a second pass, `--purge`, up to 14), then classify every event into a seam family.

* **Locating a Why3 type error**: each round emits an ANCHORED copy (an int store
  `_pycsl_anc = 73000NN` before every statement, via `ast` rewrite); the `.mlw` error line maps
  to the nearest preceding anchor = the Python statement. The anchored error text matched the
  plain emit in every spot-check; a TCOK under anchors is always re-confirmed by a plain emit.
  Front-end refusals are located by message pattern (receiver/method, nested def, `with`, `except`).
* **Neutralising**: expression stmt -> `pass`; `if/while` test -> `False`; `for` iter -> `[]`;
  `return e` -> placeholder of the live return annotation; `x = e` -> placeholder of x's hoisted
  WhyML type; a READ of a wrongly-typed local is re-targeted to its BINDING (`root-var`, the
  binding's RHS is what gets classified); expression-position `.pop/.setdefault` -> a read.
* **PH = placeholder conflict**: when a placeholder itself collides with another use, the chain
  stops (pass 1) or the variable is purged from the body (pass 2). PH events are census artifacts
  and are NOT counted as a family; the real seam is the event that created the placeholder.
* **RIPPLE**: the error moved OUT of the ported body into a mirror caller / the class type decl,
  i.e. the ported body itself type-checks and the mirror's callers still use the old (mirror)
  signature/field types. Counted as a family of its own (cost S: align mirror signatures or port
  the caller), and the chain counts as COMPLETE. Caveat: assumes callee-before-caller emission
  order (true outside `let rec ... with` groups).
* **COMPLETE** = reached L3-tc ✓ (TCOK) or RIPPLE. **INCOMPLETE** = stopped on PH / cap /
  unlocatable (the tail after the recorded prefix is unmeasured).
* Family assignment is a regex classifier over (diagnostic, located statement, error snippet,
  root RHS) — `classify.py`. INTSTR is partly a symptom bucket (a local typed int upstream).
* **Pass 2 coverage is partial**: the QUICK slot was saturated by another agent's census
  (`r263/mcensus.sh`, `cascade.*`), so pass 2 finished 50 of the 198 incomplete rows (11 more
  became TCOK); the other 148 keep their pass-1 chain.
* **TC-clean is not landable.** Every unlocked marker still has to pass the full conversion gate
  (proof, emit-diff "assumptions only become obligations", 3 planes, count, byte-inert). `*`
  marks bodies whose emitted block still carries any-valued / 0-ary / getattr erasure = FACADE
  RISK.

## Population

```
     218  INCOMPLETE
     135  COMPLETE
      24  SKIP-NOLIVE
      19  SKIP-DNC-EFFECT
      11  FACADE?(return neutralised)
      11  FACADE
       7  SKIP-NESTED-IN-TRUSTED
       2  SKIP-DNC-RAISEONLY(vacuous)
       2  UNMEASURED(port crash)
       1  SKIP-CORRECTNESS
     430  TOTAL rows (trusted-reasons.tsv, line-prefix markers)
```

Skipped as un-portable (no conversion is meaningful): SKIP-NOLIVE (live twin gone / renamed),
SKIP-DNC-EFFECT (live body does subprocess / os.makedirs / remove / mkdir / write — the recorded
DO-NOT-CONVERT list: `assigns \nothing` would become certified over a real effect),
SKIP-NESTED-IN-TRUSTED (nested def inside a still-trusted encloser), SKIP-DNC-RAISEONLY
(`_Parser.error` / `_Parser.unsupported`: raise-only, converting is vacuous), SKIP-CORRECTNESS (the
one `correctness:` row). UNMEASURED: `_decode_escapes`, `ExpressionEmissionMixin._expr_to_whyml`
(the live body re-indents badly — porter IndentationError).

## Per-family totals

`in-chain` = measured markers whose chain contains the family; `first` = first blocker;
`only-blocker` = complete chains where it is the ONLY family; last column = complete chains
containing it. Cost: S = one emitter arm, M = model extension + hand spike, L = new value model /
certificate.

```
    fam            cost  in-chain  first  only-blocker(complete)  complete-chains-containing
    MUTRECV           M        93     77                       2                          25   in-place mutator (.pop/.add/.extend/.setdefault/.update/... on local/self-field)
    DICT              L        92     37                       8                          31   Dict[str,Any] IR-dict: heterogeneous values typed `string -> option int` (Map.get value re
    GETATTR           M        60     24                       7                          22   AST getattr / hasattr / getter erasure
    LISTSTR           M        55     16                       4                          22   List[str]/List[T] local or field typed array int (element typing)
    INTSTR            M        48     14                       3                          13   int<->string erasure (upstream local/param typed int)
    RECORD            M        39     17                       3                           7   record/ADT value (emit_ir/term/classdef/stmt) vs erased int local
    RIPPLE            S        36     24                      20                          31   ported body type-checks; the error moved to a mirror CALLER / class type decl (live signat
    STRM              S        32     13                       0                          11   str method erasure (split/strip/startswith/join/...)
    SET               M        31      5                       0                           7   set()/frozenset value typed (StrSet / Array.make 1024 / membership)
    GENEXP            M        31     14                       1                           7   generator / comprehension / any()/all()/sorted() erasure
    TUPLE             M        31     10                       0                           5   tuple return slot / tuple unpack typing
    NESTED            M        30     24                       0                           3   def lift / closure
    EXT               M        19      6                       0                           4   stdlib/external call erased to 0-ary input-blind val (pathlib/os/json/hashlib/io)
    UNBOUND           S        15      2                       0                           6   unbound symbol (missing helper/val/field)
    OPTREC            M        14      2                       1                           2   Optional[record] / None where a record (or tuple) is expected
    ALIAS             M        12     10                       0                           0   dict/set value observed through two names / mutated dict aliased or stored
    EXC               M        11      7                       0                           2   exception object read / except-as / try-else
    REBIND            L        11     11                       1                           4   name rebound / namespace-dict write / global / dynamic eval
    FSTR              S        11      5                       2                           4   f-string / str literal hashed into int str_concat
    EFFECT            M        10      0                       0                           0   write effect inside a pure expression (call with effects in comprehension/cond/arg)
    PYVAL             M         8      4                       1                           4   IR-dict node (pyval) vs erased int local
    WITH-AS           M         8      8                       1                           2   context manager
    UNIT              S         7      5                       1                           5   unit-returning call used as a value
    CALLABLE          L         7      6                       3                           4   first-class function value applied
    OBJSTATE          L         7      1                       0                           0   class instantiation (_pyobj_state)
    MUTPARAM          L         7      3                       1                           3   in-place mutation of a dict/set/list PARAMETER (caller-visible writes frame)
    ARRAY-REASSIGN    M         7      4                       0                           0   array local from non-literal RHS
    SYNTAX            S         6      4                       1                           2   emitter produced ill-formed WhyML
    MEMB              M         5      0                       0                           3   `in`-membership on a container erased to int ('mu -> 'mu1)
    REF               M         5      1                       1                           3   ref vs value (mutable-local aliasing)
    FLOAT             M         3      2                       1                           1   real-valued field
    HETERO            L         3      2                       0                           0   heterogeneous list literal
    ISBOOL            S         3      1                       0                           0   `x is True/False` identity
    OTHER             L         2      1                       0                           0   unclassified
    SIG               S         2      1                       0                           0   mirror/live signature arity mismatch at a call
    STRPLUS           S         1      0                       0                           0   string `+`/`*`/`%` lowered as int arithmetic
```

## Cheaper-first unlock table

Families sorted by cost class, then by complete-chain demand; each row = markers whose COMPLETE
chain is covered once that family and every row above it are fixed. The right column counts
INCOMPLETE chains whose measured prefix is covered (an UPPER BOUND — their tails are unknown).

```
    (no fix: 12 complete chains already clean = TCOK0)
    +RIPPLE         [S]  complete-unlocked   32 (+20)   incomplete-whose-known-chain-is-covered    5
    +STRM           [S]  complete-unlocked   32 (+0)   incomplete-whose-known-chain-is-covered    7
    +UNBOUND        [S]  complete-unlocked   32 (+0)   incomplete-whose-known-chain-is-covered    7
    +UNIT           [S]  complete-unlocked   34 (+2)   incomplete-whose-known-chain-is-covered    7
    +FSTR           [S]  complete-unlocked   37 (+3)   incomplete-whose-known-chain-is-covered    8
    +SYNTAX         [S]  complete-unlocked   38 (+1)   incomplete-whose-known-chain-is-covered   10
    +ISBOOL         [S]  complete-unlocked   38 (+0)   incomplete-whose-known-chain-is-covered   10
    +SIG            [S]  complete-unlocked   38 (+0)   incomplete-whose-known-chain-is-covered   10
    +STRPLUS        [S]  complete-unlocked   38 (+0)   incomplete-whose-known-chain-is-covered   10
    +MUTRECV        [M]  complete-unlocked   42 (+4)   incomplete-whose-known-chain-is-covered   21
    +GETATTR        [M]  complete-unlocked   49 (+7)   incomplete-whose-known-chain-is-covered   23
    +LISTSTR        [M]  complete-unlocked   57 (+8)   incomplete-whose-known-chain-is-covered   28
    +INTSTR         [M]  complete-unlocked   64 (+7)   incomplete-whose-known-chain-is-covered   40
    +RECORD         [M]  complete-unlocked   68 (+4)   incomplete-whose-known-chain-is-covered   44
    +SET            [M]  complete-unlocked   69 (+1)   incomplete-whose-known-chain-is-covered   50
    +GENEXP         [M]  complete-unlocked   73 (+4)   incomplete-whose-known-chain-is-covered   59
    +TUPLE          [M]  complete-unlocked   76 (+3)   incomplete-whose-known-chain-is-covered   73
    +EXT            [M]  complete-unlocked   80 (+4)   incomplete-whose-known-chain-is-covered   76
    +PYVAL          [M]  complete-unlocked   81 (+1)   incomplete-whose-known-chain-is-covered   80
    +NESTED         [M]  complete-unlocked   83 (+2)   incomplete-whose-known-chain-is-covered   96
    +MEMB           [M]  complete-unlocked   84 (+1)   incomplete-whose-known-chain-is-covered   96
    +REF            [M]  complete-unlocked   86 (+2)   incomplete-whose-known-chain-is-covered   98
    +OPTREC         [M]  complete-unlocked   88 (+2)   incomplete-whose-known-chain-is-covered  105
    +EXC            [M]  complete-unlocked   90 (+2)   incomplete-whose-known-chain-is-covered  111
    +WITH-AS        [M]  complete-unlocked   92 (+2)   incomplete-whose-known-chain-is-covered  115
    +FLOAT          [M]  complete-unlocked   93 (+1)   incomplete-whose-known-chain-is-covered  115
    +ALIAS          [M]  complete-unlocked   93 (+0)   incomplete-whose-known-chain-is-covered  126
    +EFFECT         [M]  complete-unlocked   93 (+0)   incomplete-whose-known-chain-is-covered  131
    +ARRAY-REASSIGN [M]  complete-unlocked   93 (+0)   incomplete-whose-known-chain-is-covered  138
    +DICT           [L]  complete-unlocked  124 (+31)   incomplete-whose-known-chain-is-covered  194
    +REBIND         [L]  complete-unlocked  128 (+4)   incomplete-whose-known-chain-is-covered  201
    +CALLABLE       [L]  complete-unlocked  132 (+4)   incomplete-whose-known-chain-is-covered  203
    +MUTPARAM       [L]  complete-unlocked  135 (+3)   incomplete-whose-known-chain-is-covered  206
    +OBJSTATE       [L]  complete-unlocked  135 (+0)   incomplete-whose-known-chain-is-covered  213
    +HETERO         [L]  complete-unlocked  135 (+0)   incomplete-whose-known-chain-is-covered  216
    +OTHER          [L]  complete-unlocked  135 (+0)   incomplete-whose-known-chain-is-covered  218
```

## Greedy plan (the ordering to build)

Pick, at each step, the family with the best (newly-unlocked complete chains / cost weight
S=1 M=3 L=8), ties by fractional credit (1/#unfixed families per chain). Names are the markers
that become type-check-clean at that step (complete chains only); the `+` line lists incomplete
chains whose known prefix becomes covered (worth re-measuring right after that step lands).

 1. RIPPLE [S] — ported body type-checks; the error moved to a mirror CALLER / class type decl (live signature/field types differ from the mirror's)
    unlocks 20 (cumulative 32 incl. 12 TCOK0)  — ConcurrencyChecker.py::ConcurrencyChecker._walk_stmt, Module2_Parser.py::_ContractParser._err, Module2_Parser.py::_ContractParser._parse_atom_bs, Module5_IREmitter.py::PyCSLToJSONEmitter.__init__, core_ir_semantic.py::_namedtuple_check_subscript, core_ir_semantic.py::_typeddict_check_subscript, crosscheck_ir.py::IRCrossCheckResult.pairwise, expressions.py::ExpressionEmissionMixin._static_width, expressions.py::ExpressionEmissionMixin._to_bool, pure_ast.py::Comment.__init__, pure_ast.py::_Parser.node, pure_ast.py::_Unparser.__init__, pure_ast.py::_Unparser._write_fstring_inner, pure_ast.py::_Unparser.visit_Dict, pure_ast.py::_Unparser.visit_MatchClass, pure_ast.py::_Unparser.visit_MatchMapping, pure_ast.py::fix_missing_locations, pure_ast.py::literal_eval, statements.py::StatementEmissionMixin._collect_string_elem_read_locals.rec, statements.py::StatementEmissionMixin._seq_init_expr
    + 4 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): _ContractParser.__init__, _Parser.__init__, _lex_contract, lex
 2. FSTR [S] — f-string / str literal hashed into int str_concat
    unlocks 3 (cumulative 35 incl. 12 TCOK0)  — Module2_Parser.py::_ContractParser._grab_reviewer_id, desugar.py::_ChainDesugarer.visit_Compare*, pure_ast.py::_Unparser.get_type_comment*
    + 1 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): whyml_ident
 3. GETATTR [M] — AST getattr / hasattr / getter erasure
    unlocks 7 (cumulative 42 incl. 12 TCOK0)  — ConcurrencyChecker.py::ConcurrencyChecker._check_function, Module3_Weaver.py::Module3_Weaver._region_bound_str*, Module3_Weaver.py::Module3_Weaver._subst_csl_param*, Module3_Weaver.py::PyCSLWeaver._validate_function_contracts*, Module3_Weaver.py::PyCSLWeaver.visit_FunctionDef, Module3_Weaver.py::PyCSLWeaver.visit_With*, pure_ast.py::_Unparser._write_docstring_and_traverse_body
    + 1 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): _Parser._fin_block
 4. UNIT [S] — unit-returning call used as a value
    unlocks 2 (cumulative 44 incl. 12 TCOK0)  — pure_ast.py::_Unparser.delimit_if*, pure_ast.py::_decode_fstring_middle
 5. MUTRECV [M] — in-place mutator (.pop/.add/.extend/.setdefault/.update/... on local/self-field)
    unlocks 4 (cumulative 48 incl. 12 TCOK0)  — Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._wrap_call_with_callee_raises_assert, ir_resolve.py::_inject_functions, pure_ast.py::_Unparser.visit_Module, struct_format.py::parse_format
    + 6 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): ExpressionEmissionMixin._handle_binop, PyCSLToJSONEmitter._build_function_ir, PyCSLToJSONEmitter.visit_ClassDef, TypeInferenceMixin._collect_array_var_assigns, _parse_why3_json, _record_classification
 6. LISTSTR [M] — List[str]/List[T] local or field typed array int (element typing)
    unlocks 7 (cumulative 55 incl. 12 TCOK0)  — Module1_Ingestor.py::_Harvester._assign*, Module1_Ingestor.py::_Harvester._emit_suite, Module2_Parser.py::_ContractParser._parse_expr_list, Module5_IREmitter.py::PyCSLToJSONEmitter._collect_union_arms, preamble.py::PreambleEmissionMixin._emit_preamble_no_exception_predicates*, pure_ast.py::_Unparser.set_precedence*, pure_ast.py::walk*
    + 4 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): _ContractParser._parse_datatype, _ContractParser._parse_inductive, _parse_goal_blocks, comments
 7. DICT [L] — Dict[str,Any] IR-dict: heterogeneous values typed `string -> option int` (Map.get value read as str/dict/list)
    unlocks 15 (cumulative 70 incl. 12 TCOK0)  — Module3_Weaver.py::Module3_Weaver._parse_extracted_contracts*, Module3_Weaver.py::PyCSLWeaver.visit_Module*, desugar.py::_try_reaches_assert*, expressions.py::ExpressionEmissionMixin._emit_bitwise_or_power*, expressions.py::ExpressionEmissionMixin._tag_of_value, functions.py::FunctionEmissionMixin._emit_subtyping_goals, ir_inline.py::_Inliner.inline_stmts*, monomorphize.py::_rewrite_annotation_str*, monomorphize.py::_rewrite_annotations*, monomorphize.py::_rewrite_subscript_calls_in_stmt*, pycsl.py::_merge_records_best_of_n*, pycsl.py::_print_soundness_report*, pycsl.py::_record_answer, pycsl.py::_residual_selectors_from_records, statements.py::StatementEmissionMixin._handle_augassign_stmt*
    + 13 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): AutoTrustMixin._build_witness_str, ExpressionEmissionMixin._expr_to_whyml_string_ctx, ExpressionEmissionMixin._handle_subscript, FunctionEmissionMixin._emit_contracts, Module6_WhyMLTranspiler._emit_prefunctions_infra, Module6_WhyMLTranspiler._shared_use_lines, PreambleEmissionMixin._emit_preamble, PreambleEmissionMixin._emit_preamble_uses, _collect_generic_decls, _linearize_app, _strip_dir_scan_proofs, _stub_set, apply_monomorphization
 8. STRM [S] — str method erasure (split/strip/startswith/join/...)
    unlocks 2 (cumulative 72 incl. 12 TCOK0)  — Module3_Weaver.py::Module3_Weaver._check_protect_aliasing*, extract.py::_split_rocq_check_output*
    + 5 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): ExpressionEmissionMixin._handle_attribute_expr, Module1_Ingestor.process, PyCSLToJSONEmitter._populate_protocol_conformance, _resolve_module_path, normalize_surface
 9. INTSTR [M] — int<->string erasure (upstream local/param typed int)
    unlocks 8 (cumulative 80 incl. 12 TCOK0)  — Module2_Parser.py::_ContractParser._parse_happy_targets, abstract_ops.py::AbstractOpsMixin._advance_past_referenced_axiom_decls, crosscheck.py::CrossCheckResult.diagnostic*, expressions.py::ExpressionEmissionMixin._call_bytes_methods*, expressions.py::ExpressionEmissionMixin._emit_contract_logic_symbol, monomorphize.py::_specialize_decl*, pure_ast.py::_Unparser.visit_MatchStar, sertop.py::_sexp_parse
    + 14 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): AbstractOpsMixin._insert_abstract_val_block, ControlFlowStmtMixin._classify_iterable, ExpressionEmissionMixin._match_pattern_cond, FunctionEmissionMixin._emit_union_arm_vc, PreambleEmissionMixin._emit_uncited_axiom_func_decls, PyCSLToJSONEmitter._emit_namedtuple_record, _alpha_rename, _build_soundness_report, _extract_directives, _load_axiom_registry, _load_axiom_registry, _normalize_type_string, _resolve_module_imports, _resolve_wildcard_imports
10. RECORD [M] — record/ADT value (emit_ir/term/classdef/stmt) vs erased int local
    unlocks 5 (cumulative 85 incl. 12 TCOK0)  — Module3_Weaver.py::Module3_Weaver._subscript_read_site, Module5_IREmitter.py::PyCSLToJSONEmitter._py_expr_fstring, expressions.py::ExpressionEmissionMixin._handle_ifexpr_expr*, from_sexp.py::_find_construct_idx*, pycsl.py::_find_coqc
    + 7 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): PyCSLToJSONEmitter._csl_in, PyCSLToJSONEmitter._normalize_union_annotation, StatementEmissionMixin._handle_array_set_stmt, StatementEmissionMixin._stmts_to_whyml, _ContractParser._parse_act_block, _flatten_foralls, project_constr
11. TUPLE [M] — tuple return slot / tuple unpack typing
    unlocks 4 (cumulative 89 incl. 12 TCOK0)  — Module1_Ingestor.py::_Harvester._fold_blocks*, core_ir_semantic.py::_namedtuple_check_call, monomorphize.py::_check_gt4_polymorphic_recursion*, pure_ast.py::_Parser._slice
    + 15 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): ExpressionEmissionMixin._content_string_method, ExpressionEmissionMixin._pop_quant_binder, FunctionEmissionMixin._parse_mixin_sig, PyCSLToJSONEmitter._encode_callable_annotation, PyCSLToJSONEmitter._normalize_literal_annotation, PyCSLToJSONEmitter._synthesize_namedtuple_functional, _ContractParser._parse_variant_def, _Unparser.visit_arguments, _decode_string, _dedup_arrow_chain, _find_record_type_from_dep_imports, _make_temp_mlw_path, _match_block_hdr, _sort_arrow_hypotheses, parse_rocq_assumptions_block
12. UNBOUND [S] — unbound symbol (missing helper/val/field)
    unlocks 1 (cumulative 90 incl. 12 TCOK0)  — pycsl.py::_run_audit_mode*
    + 4 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): FunctionEmissionMixin._emit_function, _resolve_direct_imports, _resolve_imported_classes, calcsize
13. GENEXP [M] — generator / comprehension / any()/all()/sorted() erasure
    unlocks 6 (cumulative 96 incl. 12 TCOK0)  — Module1_Ingestor.py::_Harvester._build, Module3_Weaver.py::PyCSLWeaver.visit_For, Module3_Weaver.py::PyCSLWeaver.visit_While, abstract_ops.py::AbstractOpsMixin._find_abstract_val_insert_idx*, preamble.py::PreambleEmissionMixin._emit_module_globals*, pure_ast.py::get_source_segment*
    + 14 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): ExpressionEmissionMixin._coerce_dotted_args, ExpressionEmissionMixin._handle_struct_call, ExpressionEmissionMixin._is_emit_ir_expr, ExpressionEmissionMixin._is_string_expr, PreambleEmissionMixin._emit_preamble_exceptions, PreambleEmissionMixin._emit_shared_state, PyCSLWeaver.visit_ClassDef, _Harvester._normalize_leading, _Parser._fin, _emit_specializations, _json_goal_records, _specialize_function, _split_rocq_print_assumptions, crosscheck_file
14. SET [M] — set()/frozenset value typed (StrSet / Array.make 1024 / membership)
    unlocks 3 (cumulative 99 incl. 12 TCOK0)  — ConcurrencyChecker.py::ConcurrencyChecker.check*, Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._build_callee_no_exception_summary*, functions.py::FunctionEmissionMixin._mixin_dep_pseudo_functions*
    + 15 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): ControlFlowStmtMixin._callee_raised_in, ExpressionEmissionMixin._emit_membership, ExpressionEmissionMixin._handle_isinstance, ExpressionEmissionMixin._handle_join_call, ExpressionEmissionMixin._handle_len_call, PreambleEmissionMixin._emit_class_inv_axioms, PreambleEmissionMixin._fresh_globals_facts, PreambleEmissionMixin._inductive_referenced_axiom_decls, PyCSLToJSONEmitter._collect_class_fields, PyCSLToJSONEmitter._emit_protocol_interface, PyCSLToJSONEmitter._py_expr_call, StatementEmissionMixin._emit_frame_condition, _inline_calls, _resolve_imported_base_classes, sort_functions_by_scc
15. SYNTAX [S] — emitter produced ill-formed WhyML
    unlocks 2 (cumulative 101 incl. 12 TCOK0)  — monomorphize.py::_collect_instantiations*, pure_ast.py::unparse
    + 2 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): _ContractParser._parse_atom_name, _ContractParser._parse_contract
16. EXT [M] — stdlib/external call erased to 0-ary input-blind val (pathlib/os/json/hashlib/io)
    unlocks 4 (cumulative 105 incl. 12 TCOK0)  — audit_proof.py::_parse_lean_file*, audit_proof.py::_parse_rocq_file*, audit_proof_reverify.py::_sha256_file*, normalize.py::normalize_prover_output*
    + 6 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): _expand_anon_binders, _index_proofs_dir_by_file, collect_module_constants, collect_module_globals, main, main
17. PYVAL [M] — IR-dict node (pyval) vs erased int local
    unlocks 3 (cumulative 108 incl. 12 TCOK0)  — from_sexp.py::_construct_indices, ir_inline.py::_Inliner._hoist_calls_in_expr, monomorphize.py::_rewrite_subscript_to_name*
    + 4 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): _Inliner._expand, _project_app, check_imports, run_ir_semantic_checks
18. NESTED [M] — def lift / closure
    unlocks 3 (cumulative 111 incl. 12 TCOK0)  — Module3_Weaver.py::Module3_Weaver._happy_predicate*, auto_trust.py::AutoTrustMixin._should_auto_trust_tuple_return, preamble.py::PreambleEmissionMixin._emit_inductive_decls*
    + 20 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): ExpressionEmissionMixin._call_record_constructor, ExpressionEmissionMixin._iter_len_expr, FunctionEmissionMixin._emit_narrowing_vc, Module6_WhyMLTranspiler._sig_val_from_let, PreambleEmissionMixin._emit_type_decls, PreambleEmissionMixin._precompute_axiom_logic_funcs, PreambleEmissionMixin._subst_self_in_expr, PyCSLToJSONEmitter._build_function_symbol_table, PyCSLWeaver._extract_mixin_directives, StatementEmissionMixin._collect_field_decode_str_locals.rec, _Unparser._str_literal_helper, _Unparser.visit_BoolOp, _dispatch_provers, _lex, _nat_to_int_with_sidecond, _recursive_methods, _returns_literal_none, apply_composition, apply_inheritance, dump
19. REF [M] — ref vs value (mutable-local aliasing)
    unlocks 3 (cumulative 114 incl. 12 TCOK0)  — Module3_Weaver.py::Module3_Weaver._attach_labels_and_ghost_assigns*, pure_ast.py::_Unparser.buffered*, pure_ast.py::increment_lineno*
    + 2 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): _Harvester._make, _audit_one_prover
20. MEMB [M] — `in`-membership on a container erased to int ('mu -> 'mu1)
    unlocks 3 (cumulative 117 incl. 12 TCOK0)  — Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._maybe_emit_no_exception_assert*, exception_model.py::bases_closure*, functions.py::FunctionEmissionMixin._param_type_str*
    + 2 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): ExpressionEmissionMixin._linear_form, PreambleEmissionMixin._emit_preamble_axioms
21. OPTREC [M] — Optional[record] / None where a record (or tuple) is expected
    unlocks 2 (cumulative 119 incl. 12 TCOK0)  — Module2_Parser.py::_ContractParser._parse_happy, crosscheck_ir.py::IRCrossCheckResult.diagnostic*
    + 10 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): PyCSLToJSONEmitter._get_mutex_invariant_ir, _ContractParser._parse_atom_primary, _Precedence.next, _ac_normalize, _alpha_rename, _expand_nat_to_int, _iff_app_to_binop, _normalize_names, project_to_ir, substitute
22. EXC [M] — exception object read / except-as / try-else
    unlocks 2 (cumulative 121 incl. 12 TCOK0)  — Module2_Parser.py::Module2_Parser.parse_contract, exec_splice.py::_ExecSplicer.visit_Expr*
    + 7 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): Module3_Weaver._expand_happy_properties, Module6_WhyMLTranspiler._render_callee_condition, NodeVisitor.visit_Constant, PyCSLToJSONEmitter._m5_get_type_name, _index_proofs_dir, crosscheck_file_ir, parse_type_expr
23. WITH-AS [M] — context manager
    unlocks 2 (cumulative 123 incl. 12 TCOK0)  — pure_ast.py::_Unparser.visit_Lambda, pure_ast.py::main*
    + 4 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): _process_dependency, _resolve_runtime_config, _sha256_file, main
24. CALLABLE [L] — first-class function value applied
    unlocks 4 (cumulative 127 incl. 12 TCOK0)  — Module2_Parser.py::_ContractParser._try, pure_ast.py::NodeVisitor.visit*, pure_ast.py::_Unparser.interleave*, pure_ast.py::_Unparser.items_view
    + 2 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): _ContractParser._parse_quantifier, _Unparser.visit_JoinedStr
25. REBIND [L] — name rebound / namespace-dict write / global / dynamic eval
    unlocks 4 (cumulative 131 incl. 12 TCOK0)  — desugar.py::normalize_stores*, ir_resolve.py::resolve, pure_ast.py::NodeTransformer.generic_visit*, pure_ast.py::copy_location*
    + 7 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): AutoTrustMixin._check_witness_vals, ControlFlowStmtMixin._render_match_pattern, Module5_IREmitter.generate_json, Module6_WhyMLTranspiler._transpile_modular, Module6_WhyMLTranspiler.transpile, PreambleEmissionMixin._scan_preamble_needs, _build_nodes
26. MUTPARAM [L] — in-place mutation of a dict/set/list PARAMETER (caller-visible writes frame)
    unlocks 3 (cumulative 134 incl. 12 TCOK0)  — Module3_Weaver.py::Module3_Weaver._collect_field_read_sites*, Module3_Weaver.py::Module3_Weaver._collect_self_call_sites, preamble.py::PreambleEmissionMixin._emit_opaque_class_aliases
    + 3 INCOMPLETE chains whose known prefix is now covered (tail unmeasured): ExpressionEmissionMixin._call_named_builtins, PyCSLToJSONEmitter._detect_array_dimensions, PyCSLToJSONEmitter._detect_seq_promotion
27. FLOAT [M] — real-valued field
    unlocks 1 (cumulative 135 incl. 12 TCOK0)  — Module3_Weaver.py::PyCSLWeaver._subst_var

(* = final emitted body carries erasure marks: any-valued / 0-ary vals / getattr — FACADE RISK, inspect before landing)

## TCOK0 — type-check clean today with ZERO neutralisation

```
    COMPLETE                     frontend/Module3_Weaver.py::PyCSLWeaver._attach_loop_contracts  marks={}
    COMPLETE                     frontend/monomorphize.py::_rewrite_call_sites  marks={'hash': 1}
    SKIP-DNC-RAISEONLY(vacuous)  frontend/pure_ast.py::_Parser.error  marks={}
    SKIP-DNC-RAISEONLY(vacuous)  frontend/pure_ast.py::_Parser.unsupported  marks={}
    COMPLETE                     frontend/pure_ast.py::_Parser._max_end  marks={'anyval': 1, 'getattr': 3, 'hash': 1}
    COMPLETE                     frontend/pure_ast.py::_parse_number  marks={'anyval': 3, 'zeroary': 1, 'hash': 4}
    COMPLETE                     frontend/pure_ast.py::iter_fields  marks={'anyval': 1}
    COMPLETE                     frontend/pure_ast.py::iter_child_nodes  marks={'anyval': 4}
    COMPLETE                     frontend/pure_ast.py::NodeVisitor.generic_visit  marks={'anyval': 2}
    COMPLETE                     frontend/pure_ast.py::_Unparser.visit_If  marks={'hash': 3}
    COMPLETE                     ir_schema.py::validate_ir  marks={'anyval': 4, 'zeroary': 3, 'hash': 13}
    FACADE                       module6_whyml/identifiers.py::stable_hash  marks={'anyval': 1, 'hash': 1}
    COMPLETE                     proof2why3/sertop.py::_sexp_tokens  marks={'anyval': 4}
    COMPLETE                     pycsl.py::_parse_args  marks={'zeroary': 2, 'hash': 36}
```

Cleanest immediate candidates (no any/0-ary/getattr marks): `PyCSLWeaver._attach_loop_contracts`,
`_Unparser.visit_If`. **`monomorphize.py::_rewrite_call_sites` must NOT be landed** — see the
soundness suspicion below. The rest carry erasure marks (facade risk) and need the emit-diff gate
before anyone trusts the TC result.

## FACADE flags (do not count)

`FACADE` = chain reached TCOK and the emitted body references no input (params / read self
fields). `FACADE?(return neutralised)` = blind only because the census replaced the `return`;
undecided until that seam is real.

```
    FACADE?(return neutralised)  audit_proof_reverify.py::ReverifyReport.summary  chain=['FLOAT']
    FACADE?(return neutralised)  audit_proof_reverify.py::_cache_key  chain=['STRM', 'EXT']
    FACADE?(return neutralised)  audit_proof_reverify.py::_cache_load  chain=['EXT']
    FACADE?(return neutralised)  audit_proof_reverify.py::_to_cache_payload  chain=['INTSTR']
    FACADE                       frontend/Module3_Weaver.py::Module3_Weaver._extract_happy_properties  chain=['MUTRECV', 'MUTPARAM', 'GENEXP']
    FACADE?(return neutralised)  frontend/ir_resolve.py::_get_module_exports  chain=['WITH-AS', 'GENEXP']
    FACADE?(return neutralised)  frontend/pure_ast.py::_const_value_getter  chain=['UNBOUND']
    FACADE                       frontend/pure_ast.py::_const_value_setter  chain=['UNBOUND']
    FACADE?(return neutralised)  frontend/pure_ast.py::_Tok.__repr__  chain=['TUPLE']
    FACADE                       frontend/pure_ast.py::_Unparser.write  chain=['MUTRECV']
    FACADE                       module6_whyml/expressions.py::ExpressionEmissionMixin._handle_sum_call  chain=['DICT']
    FACADE                       module6_whyml/identifiers.py::stable_hash  chain=[]
    FACADE                       module6_whyml/preamble.py::PreambleEmissionMixin._mutex_inv_application  chain=['LISTSTR']
    FACADE                       module6_whyml/scc.py::compute_sccs  chain=['NESTED', 'INTSTR']
    FACADE                       proof2why3/from_lean_json.py::_is_ofnat_lit  chain=['TUPLE']
    FACADE                       proof2why3/normalize.py::normalize_whyml_axiom  chain=['EXT']
    FACADE                       proof2why3/sertop.py::parse_sexp  chain=['LISTSTR']
    FACADE?(return neutralised)  proof2why3/sertop.py::SertopSession.type_of_batch  chain=['CALLABLE', 'LISTSTR']
    FACADE?(return neutralised)  pycsl.py::_record_key  chain=['SET']
    FACADE?(return neutralised)  pycsl.py::_synthesize_block  chain=['STRM', 'FLOAT', 'UNBOUND']
    FACADE?(return neutralised)  pycsl.py::_synthesize_legacy_text  chain=['STRM']
    FACADE                       pycsl.py::_function_body_eqs  chain=['EXT']
```

Add `monomorphize.py::_rewrite_call_sites` (TCOK0, reads `ir_data` only to drive a loop; the
store is `subscript_set !func <hash> (list_comp 0)` into an int-typed local: input-blind effect).

## In-place mutator detail (MUTRECV, markers per method@receiver)

```
      31  pop@local/param
      25  extend@local/param
      18  setdefault@local/param
      14  add@local/param
      11  update@local/param
       9  setdefault@self-field
       5  add@self-field
       5  append@self-field
       4  sort@local/param
       4  discard@local/param
       3  insert@local/param
       3  clear@self-field
       3  pop@self-field
       2  reverse@local/param
       2  update@self-field
       1  extend@self-field
```

## Soundness suspicion (not chased)

**Element-alias store into a dict parameter escapes the MUTPARAM refusal and the frame.**
`for x in d.get("fs", []): x["body"] = []` mutates the CALLER's nested dicts, yet the function
emits TC-clean with `#@ assigns \nothing`: `x` is an int-typed local, the store lowers to
`val subscript_set (x: int) (i: int) (v: int) : unit` (no `writes`), `d` is an immutable
`map string (option int)` value, so the frame is satisfied vacuously. The direct form `d[k] = v`
IS refused ("in-place mutation of dict/set parameter"); the aliased element form is not.
Reproducer (emits L3-tc ✓; I did not run the proof):

```python
from typing import Any, Dict

#@ requires True
#@ ensures True
#@ assigns \nothing
def clear_bodies(d: Dict[str, Any]) -> None:
    for x in d.get("fs", []):
        x["body"] = []
```

Live instance: `frontend/monomorphize.py::_rewrite_call_sites` (TCOK0 in this census, mirror
contract `assigns \nothing`, row `cost-scale:dict-param-get-receiver`): converting it would
certify `assigns \nothing` over a function whose whole job is to rewrite `ir_data` in place.
Files: `plan/repro/alias_elem_store.py` (+ `.mlw`), `plan/mono_rewrite_call_sites_ported.py`,
`plan/mono_rewrite_call_sites.mlw`.

## Artifacts (scratchpad `plan/`)

`chain.py` (census, resumable), `chain.jsonl` (pass 1, 430 rows), `chain2.jsonl` (pass 2, 50 rows),
`classify.py` (families), `plan.py` (tables; `python3 plan.py chain.jsonl chain2.jsonl`),
`chain.markers.json` (per-marker families/category), `plan.out`.

## Re-measurement at HEAD — steps 2, 4, 8 (ch20, 2026-10-17, at `9b404897`)

Each marker ported verbatim (live body; mirror signature, then live signature where they
differ) and type-checked `--no-proof --keep-mlw`. **0 of 7 honest; no seam built.** The S
families are mis-attributed: each chain's first S blocker hides an M/L value-model gap.

```
    step  marker                                  first blocker at HEAD -> verdict
    2 FSTR _ContractParser._grab_reviewer_id      `self.source[pos:]` is getattr-erased (not a mirror field), `re.match` erased
                                                  and `m.group(0)` lowers to `m_group_1 0`: the return value is INPUT-BLIND. SKIP
    2 FSTR _ChainDesugarer.visit_Compare          facade: `ops`/`comparators` = `pycsl_getattr_default_*` constants, every AST
                                                  ctor 0-ary (`ast_Compare_0 ()`), the result `ast_BoolOp_0 ()`. SKIP
    2 FSTR _Unparser.get_type_comment             string f-string returned into an int-erased slot; `-> Optional[str]` makes the
                                                  body TC but ripples into VERIFIED `visit_Assign` (`"" <> 0`); the int-hash
                                                  route would add 2 UNKNOWN getattr sites to pure_ast (ratchet). SKIP
    4 UNIT _Unparser.delimit_if                   `-> int` refused by route #252; live sig -> every `with self.require_parens(..)`
                                                  caller REFUSED by route #257 (cm no longer proven inert) = mirror regression. SKIP
    4 UNIT _decode_fstring_middle                 callee `_decode_escapes` is trusted+unannotated (`: unit`); its real return is
                                                  `str` or `bytes` depending on `is_bytes` -> no honest return interface; the
                                                  `-> str` return then refused by route #252. SKIP
    8 STRM Module3_Weaver._check_protect_aliasing bare `set` params iterate as int; `p.split(".")` -> `p_split_1 <hash>` (receiver
                                                  dropped, fresh program val: sound, input-blind); needs SET + LISTSTR first. SKIP
    8 STRM _split_rocq_check_output               `stdout.splitlines()` -> 0-ary `stdout_splitlines_0 ()`, locals typed int,
                                                  `lstrip()[2:]` -> `any int`; needs splitlines/lstrip/List[str] locals (M). SKIP
```

The receiver-dropping helpers are `val`s (not `val function`), so each call is a fresh
unconstrained value: input-blind, NOT unsound. No independently-correct seam was found for
steps 2/4/8, so none was landed. Logs/emits: session scratchpad `ch20/m-*.log`, `m-*.mlw`.

## Re-measurement at HEAD — step 6 LISTSTR (ch21, 2026-10-18, at `76dec778`)

Each marker ported verbatim (live body; live signature where the mirror's differed) in a
scratch copy and type-checked `--no-proof --keep-mlw`. **1 of 7 honest** — converted on a
two-part seam; the other six are not LISTSTR once re-ported (the census's LISTSTR event was
the FIRST type error, not the only blocker).

```
    marker                                        first blocker at HEAD -> verdict
    _Harvester._assign                            REFUSED: `self._module_header.append(..)` (self-field append,
                                                  no certified lowering); also `_dec_owner.leading.append`
                                                  (element-alias store), local `import bisect`, `next(genexp)`. MUTRECV. SKIP
    _Harvester._emit_suite                        REFUSED by route #263 (self-recursion through a method call ->
                                                  `#@ \diverges` required); with it: `List[_Target]` is `array int`
                                                  (record element erased), `tgt.child_suites` = opaque
                                                  `get_child_suites (x: int)`; a faithful model needs a recursive
                                                  MUTABLE record (`_target` containing arrays of `_target`) -- not
                                                  expressible as a Why3 record. RECORD/L. SKIP
    _ContractParser._parse_expr_list              `exprs` is `seq emit_ir`, the (unannotated) return `int`;
                                                  `-> "List[ExprIR]"` is `array emit_ir` ONLY under
                                                  `_uses_pyast_parser()` (pure_ast), and the loop needs the
                                                  `self.i` invariants of its siblings. A file-gate lift, not
                                                  LISTSTR. SKIP (candidate for a pyast-gate generalisation)
    PyCSLToJSONEmitter._collect_union_arms        REFUSED: `stack.pop()` (MUTRECV); `arms.reverse()`, AST ctor
                                                  comprehensions. SKIP
    _Unparser.set_precedence                      `*nodes` is `seq int` against `iter_length (x: int)`; the store
                                                  `self._precedences[node] = p` lowers to `subscript_set
                                                  (getattr__unparser self <h>) ..` (no `writes`): the frame
                                                  `assigns self._precedences` would be VACUOUS. FACADE. SKIP
    walk                                          generator (`yield`, route #271 eagerness) over `deque` +
                                                  `.popleft()`/`.extend()` (MUTRECV). SKIP
    _emit_preamble_no_exception_predicates        CONVERTED (455 -> 454). Blockers were exactly two LISTSTR
                                                  lowerings + the mirror's int-erased `needs: int` param:
                                                  (1) `for line in predicate_definitions():` -- a call declared
                                                  `-> List[str]` fell to `iter_length/iter_get : int -> int`;
                                                  (2) `out: List[str] = [""]` grown by `f"  {line}"` stayed
                                                  `seq int` (the `""` hashed) against the `-> List[str]` return.
```

Seam (both halves fail-closed before, byte-inert after): `stmt_control_flow._classify_iterable`
— a call whose declared return is `array string` is evaluated ONCE into an immutable `let`
(`_callit<idx>`), bound `Array.length`, element `_callit[!idx]`, arithmetic variant; the loop
target is symbol-type `str` for the body (`_handle_for_stmt`). `Module5._detect_seq_promotion`
— an `FString` element counts as a string element (an f-string IS a `str`). The mirror
signature takes the live `needs: Dict[str, Any]` (body reads `Map.get needs "..."`, not the
input-blind `needs_get_1 <hash>` of the int param). Gates: preamble whole-file proof rc=0 (222
Valid); corpus byte-diff 0/0/0 root (1755 -> 1758, 3 new witnesses) and pyref (2186); mirror
sweep 1 MOVED (preamble, declared) / 53; witnesses 2920 (PASS; L3-tc fails at base), 2921/2922
(FAIL twins). The ch11 `snapshot_str` note concerns `_emit_preamble` (the caller,
still trusted: `out += self._emit_preamble_no_exception_predicates(needs)` + DICT/SET seams),
not this marker.

## Re-measurement at HEAD — ch22 (gen #37)

At `8ece69c0` (count 454). Each marker ported verbatim (live body; live signature where the
mirror's differed; `bin/port-one-mirror-body.py`, `--replace` for the DIFFERS rows) into a
scratch copy, emitted `--no-proof --keep-mlw` through `heavy.sh`, and the emitted WhyML read.
**1 of 16 honest** (TCOK0 remainder + plan step 3 GETATTR). The TCOK0 label held only for
`visit_If`, and even there it hid a termination obligation: the census emits never asked Why3
whether the body TERMINATES.

```
    marker                                        first blocker at HEAD -> verdict
  TCOK0
    PyCSLWeaver._attach_loop_contracts            TC-clean but FACADE: `node.csl_invariants.append(c)` on the
                                                  int-erased param `node` lowers to FRESH LOCAL arrays
                                                  (`Array.make 1024 0` + len refs) -- the caller-visible
                                                  write (the method's whole job) vanishes, and `assigns
                                                  \nothing` would be certified over an in-place mutator.
                                                  screen: check-emitted-vacuity RED. SKIP (see suspicion)
    _Unparser.visit_If                            CONVERTED (454 -> 453). Census "TCOK0" hid one real
                                                  obligation: the body calls `self.traverse` (`#@ \diverges`
                                                  since route #263) and loops `while node.orelse ...` with no
                                                  expressible variant (`get_orelse : int -> int`); without a
                                                  marker its VC is Timeout (unprovable termination). Landed
                                                  with the honest `#@ \diverges`, exactly as its verified
                                                  siblings visit_While / visit_With / _for_helper. Screen 4/4
                                                  green; goal Valid; pure_ast whole-file
                                                  proof rc=0, 0 non-Valid (105 min). Commit ae771d38.
    _Parser._max_end                              REFUSED route #263 (self-recursion through a method call);
                                                  with `\diverges`: L3-tc "depends on _pyobj_state, left out of
                                                  the specification" (getattr/setattr effect). SKIP
    _parse_number                                 L3-tc: body `int` vs return `PyConstVal` (INTSTR/RECORD). SKIP
    iter_child_nodes (DIFFERS)                    TC-clean, FACADE: both `yield`s -> `any int`, the tuple
                                                  target `field = any int`. Generator model. SKIP
    NodeVisitor.generic_visit                     TC-clean; already refused by the gen #31 screen (vacuity).
                                                  SKIP (recorded, not re-landed)
    validate_ir (DIFFERS)                         TC-clean, FACADE: `ir.keys()` -> 0-ary `ir_keys_0 ()`,
                                                  `ir.get(..)` -> receiver-dropped `ir_get_1 <hash>`, the
                                                  isinstance checks `any bool`. SKIP
    _sexp_tokens                                  TC-clean, FACADE: generator, every `yield` -> `any int`,
                                                  return `unit`; scanning loops carry no variant. SKIP
    _parse_args                                   refused by check 1 (ten new abstract ops, argparse). SKIP
    _rewrite_call_sites / stable_hash             do-not-convert (soundness suspicion / FACADE). not touched
  step 3 GETATTR
    ConcurrencyChecker._check_function            REFUSED route #252: `func.name` (AST field, erased Any) into
                                                  the `str` param `func_name` of `_walk_body`; also `held=set()`
                                                  into the mirror's int `held`. AST-node value model (L). SKIP
    Module3_Weaver._region_bound_str              L3-tc: `getattr(node,"name","<expr>")` is
                                                  `pycsl_getattr_unknown_<h> node : int` returned as `str`;
                                                  `getattr(node,"value",None)` + `float(v).is_integer()` over a
                                                  CSLNode union. Needs a CSLNode ADT with optional fields. SKIP
    Module3_Weaver._subst_csl_param               REFUSED route #263 (self-recursion); with `\diverges`: L3-tc
                                                  `setattr_3 .. (str_hash_op (get_name !f))` -- dataclass
                                                  reflection (`_dc_fields`, dynamic setattr, deepcopy). L. SKIP
    PyCSLWeaver._validate_function_contracts      L3-tc array vs int; `getattr(node,"csl_acts",[]) or []` is the
                                                  0-ary input-blind `pycsl_getattr_default_<h>` (FACADE). SKIP
    PyCSLWeaver.visit_FunctionDef                 L3-tc (1) `self.contracts_map[k]` (record field `map int
                                                  (option (seq int))`) gets the int missing-key default `0`.
                                                  A 2-line seam (self-field ν `seq ...` -> `_dv_missing_default`,
                                                  fail-closed before) was built IN SCRATCH and clears it, then
                                                  (2) the dict value `seq int` meets the receiver-dropped stub
                                                  `self__dispatch_function_contracts_2 (x1: array int)` -- the
                                                  List seq/array split (M); and the body is 4 receiver-dropped
                                                  opaque `self__*_1` calls. Seam NOT landed (unlocks nothing). SKIP
    PyCSLWeaver.visit_With                        same (1); after the scratch seam, `for c in
                                                  self.contracts_map[k]` iterates the `seq int` through
                                                  `iter_length : int` (iterable classification, M); then
                                                  `getattr(self,"_csl_bound_names",None)` is a 0-ary default
                                                  facade on the raise guard, and the `node.csl_*` stores hit
                                                  the int-erased param. SKIP
    _Unparser._write_docstring_and_traverse_body  L3-tc: `node.body[1:]` -> `array_slice (get_body node) ..`
                                                  over the int-erased AST field (AST-list value model, M); then
                                                  the `self.traverse` calls need `\diverges` (as visit_If). SKIP
```

**Soundness suspicion (not chased, same family as the `_rewrite_call_sites` one above).** An
attribute-append on an UNANNOTATED (int-erased) parameter, `node.xs.append(c)`, lowers to a
fresh function-local `Array.make 1024 0` + length ref: the caller-visible mutation is dropped
and `#@ assigns \nothing` holds vacuously. Live instance: `_attach_loop_contracts` (left
`\trusted`). Emit: session scratchpad `ch22/attach.mlw`.

No GETATTR seam was landed: the only small, fail-closed one found (the `seq` missing-key
default) unlocks no honest conversion on its own. Logs/emits: session scratchpad `ch22/`.

## Appendix — per-marker chains

`cat | file::qual | status | families in order | PH (chain hit a placeholder conflict) / risk | last diagnostic`

```
    cat | file::qual | status | families (ordered) | PH? | last msg
    COMPLETE | Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._build_callee_no_exception_summary | TCOK | SET > DICT |  risk | This expression has type array.Array.array int @rho, but is expected to have type int /home/fabrice/git/pycsl-
    COMPLETE | Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._maybe_emit_no_exception_assert | TCOK | MUTRECV > MEMB |  risk | This expression has type int, but is expected to have type 'mu -> 'mu1 /home/fabrice/git/pycsl-plan/src/pycsl/
    COMPLETE | Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._wrap_call_with_callee_raises_assert | STUCK-LOCATE | MUTRECV > RIPPLE |  | unbound function or predicate symbol '_abstract_ops' /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.p
    COMPLETE | audit_proof.py::_parse_lean_file | TCOK | MUTRECV > EXT > STRM > SET | PH risk | This expression has type PyCSL_Program.StrSet.set, but is expected to have type int -> option.Option.option in
    COMPLETE | audit_proof.py::_parse_rocq_file | TCOK | MUTRECV > EXT > STRM > LISTSTR > SET | PH risk | This expression has type PyCSL_Program.StrSet.set, but is expected to have type int -> option.Option.option in
    COMPLETE | audit_proof_reverify.py::_sha256_file | TCOK | MUTRECV > EXT | PH risk | This expression has type int, but is expected to have type string
    COMPLETE | core_ir_semantic.py::_namedtuple_check_call | STUCK-LOCATE | TUPLE > RIPPLE |  | This expression has type int -> option.Option.option int, but is expected to have type string -> option.Option
    COMPLETE | core_ir_semantic.py::_namedtuple_check_subscript | STUCK-LOCATE | RIPPLE |  | This expression has type int -> option.Option.option int, but is expected to have type string -> option.Option
    COMPLETE | core_ir_semantic.py::_typeddict_check_subscript | STUCK-LOCATE | RIPPLE |  | This expression has type int -> option.Option.option int, but is expected to have type string -> option.Option
    COMPLETE | exception_model.py::bases_closure | TCOK | MUTRECV > DICT > SET > MEMB |  risk | This expression has type int, but is expected to have type 'mu -> 'mu1
    COMPLETE | frontend/ConcurrencyChecker.py::ConcurrencyChecker._check_function | TCOK | GETATTR |  | This expression has type int, but is expected to have type array.Array.array int @rho
    COMPLETE | frontend/ConcurrencyChecker.py::ConcurrencyChecker._walk_stmt | STUCK-LOCATE | RIPPLE |  | This expression has type int, but is expected to have type int -> option. Option.option int
    COMPLETE | frontend/ConcurrencyChecker.py::ConcurrencyChecker.check | TCOK | MUTRECV > SET > GETATTR > RECORD |  risk | This expression has type PyCSL_Program.concurrencywarning, but is expected to have type int
    COMPLETE | frontend/Module1_Ingestor.py::_Harvester._assign | TCOK | MUTRECV > LISTSTR > GETATTR |  risk | This expression has type array.Array.array int @rho, but is expected to have type int
    COMPLETE | frontend/Module1_Ingestor.py::_Harvester._build | TCOK | MUTRECV > GENEXP |  | This expression has type ref int @rho, but is expected to have type PyCSL_Program._target <array.Array.array i
    COMPLETE | frontend/Module1_Ingestor.py::_Harvester._emit_suite | TCOK | LISTSTR |  | This expression has type int, but is expected to have type array.Array.array int @rho
    COMPLETE | frontend/Module1_Ingestor.py::_Harvester._fold_blocks | TCOK | UNIT > TUPLE > STRM |  risk | This expression has type string, but is expected to have type int
    COMPLETE | frontend/Module2_Parser.py::Module2_Parser.parse_contract | STUCK-LOCATE | EXC > RIPPLE |  | this expression raises unlisted exception PyCSLParseError
    COMPLETE | frontend/Module2_Parser.py::_ContractParser._err | STUCK-LOCATE | RIPPLE |  | This expression has type PyCSL_Program.emit_ir, but is expected to have type ()
    COMPLETE | frontend/Module2_Parser.py::_ContractParser._grab_reviewer_id | STUCK-LOCATE | FSTR > RIPPLE |  | This expression has type int, but is expected to have type string
    COMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_atom_bs | STUCK-LOCATE | RIPPLE |  | unbound function or predicate symbol 'i'
    COMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_expr_list | TCOK | LISTSTR |  | This expression has type seq.Seq.seq PyCSL_Program.emit_ir, but is expected to have type seq.Seq.seq int
    COMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_happy | TCOK | LISTSTR > UNIT > OPTREC |  | This expression has type int, but is expected to have type PyCSL_Program. emit_ir
    COMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_happy_targets | TCOK | INTSTR |  | This expression has type int, but is expected to have type string
    COMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_inductive_rules | TCOK |  | PH risk | This expression has type array.Array.array int @rho, but is expected to have type int
    COMPLETE | frontend/Module2_Parser.py::_ContractParser._try | TCOK | CALLABLE |  | This expression has type int, it cannot be applied
    COMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._attach_labels_and_ghost_assigns | TCOK | GENEXP > LISTSTR > DICT > GETATTR > REF |  risk | This expression has type ref int @rho, but is expected to have type int
    COMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._check_protect_aliasing | TCOK | DICT > STRM |  risk | This expression has type array.Array.array int @rho, but is expected to have type int
    COMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._collect_field_read_sites | TCOK | MUTPARAM > UNIT |  risk | This expression has type (), but is expected to have type int
    COMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._collect_self_call_sites | TCOK | MUTPARAM |  | [module6-whyml]: in-place `append` to list parameter 'out' is out of scope: Python passes a list argument BY R
    COMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._happy_predicate | TCOK | NESTED > RECORD > DICT |  risk | This expression has type int, but is expected to have type PyCSL_Program. emit_ir
    COMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._parse_extracted_contracts | TCOK | MUTRECV > LISTSTR > GETATTR > DICT |  risk | This expression has type (int -> option.Option.option (seq.Seq.seq int), 'mu -> option.Option.option (seq.Seq.
    COMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._region_bound_str | TCOK | GETATTR |  risk | This expression has type int, but is expected to have type string
    COMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._subscript_read_site | TCOK | RECORD > DICT |  | This expression has type 'mu -> option.Option.option 'mu1, but is expected to have type int
    COMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._subst_csl_param | TCOK | GETATTR |  risk | This expression has type int, but is expected to have type string
    COMPLETE | frontend/Module3_Weaver.py::PyCSLWeaver._attach_loop_contracts | TCOK0 |  |  | 
    COMPLETE | frontend/Module3_Weaver.py::PyCSLWeaver._subst_var | TCOK | FLOAT |  | This expression has type int, but is expected to have type real
    COMPLETE | frontend/Module3_Weaver.py::PyCSLWeaver._validate_function_contracts | TCOK | GETATTR |  risk | This expression has type array.Array.array int @rho, but is expected to have type int
    COMPLETE | frontend/Module3_Weaver.py::PyCSLWeaver.visit_For | TCOK | GENEXP > LISTSTR > UNBOUND > DICT |  | This expression has type PyCSL_Program.py_for <array.Array.array int @rho1> @rho, but is expected to have type
    COMPLETE | frontend/Module3_Weaver.py::PyCSLWeaver.visit_FunctionDef | TCOK | GETATTR |  | This expression has type int, but is expected to have type seq.Seq.seq int
    COMPLETE | frontend/Module3_Weaver.py::PyCSLWeaver.visit_Module | TCOK | MUTRECV > DICT |  risk | This expression has type int, but is expected to have type seq.Seq.seq int
    COMPLETE | frontend/Module3_Weaver.py::PyCSLWeaver.visit_While | TCOK | GENEXP > UNBOUND > DICT |  | unbound function or predicate symbol 'lineno'
    COMPLETE | frontend/Module3_Weaver.py::PyCSLWeaver.visit_With | TCOK | GETATTR |  risk | This expression has type int, but is expected to have type seq.Seq.seq int
    COMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter.__init__ | STUCK-LOCATE | RIPPLE |  | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    COMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._collect_union_arms | TCOK | MUTRECV > GETATTR > LISTSTR |  | This expression has type array.Array.array int @rho, but is expected to have type int /home/fabrice/git/pycsl-
    COMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._py_expr_fstring | TCOK | GETATTR > RECORD |  | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /home/fabrice/git/pycsl-plan
    COMPLETE | frontend/desugar.py::_ChainDesugarer.visit_Compare | TCOK | FSTR |  risk | This expression has type string, but is expected to have type int
    COMPLETE | frontend/desugar.py::_try_reaches_assert | TCOK | DICT |  risk | This expression has type int -> option.Option.option int, but is expected to have type int
    COMPLETE | frontend/desugar.py::normalize_stores | TCOK | REBIND > MUTRECV > INTSTR > GETATTR > LISTSTR |  risk | This expression has type seq.Seq.seq int, but is expected to have type array. Array.array 'mu @rho
    COMPLETE | frontend/exec_splice.py::_ExecSplicer.visit_Expr | TCOK | EXC > PYVAL |  risk | This expression has type int, but is expected to have type PyCSL_Program. pyval
    COMPLETE | frontend/ir_inline.py::_Inliner._hoist_calls_in_expr | TCOK | MUTRECV > PYVAL > DICT |  | This expression has type 'mu -> option.Option.option 'mu1, but is expected to have type int
    COMPLETE | frontend/ir_inline.py::_Inliner.inline_stmts | TCOK | MUTRECV > DICT |  risk | This expression has type int -> option.Option.option int, but is expected to have type int
    COMPLETE | frontend/ir_resolve.py::_inject_functions | TCOK | MUTRECV |  | `existing.add(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an ab
    COMPLETE | frontend/ir_resolve.py::resolve | STUCK-LOCATE | REBIND > RIPPLE |  | This pattern has type PyCSL_Program._union_resolve_1, but is expected to have type int
    COMPLETE | frontend/monomorphize.py::_check_gt4_polymorphic_recursion | TCOK | DICT > GETATTR > TUPLE |  risk | This pattern has type ('mu, 'mu1), but is expected to have type int
    COMPLETE | frontend/monomorphize.py::_collect_instantiations | TCOK | SYNTAX > SET > DICT > UNBOUND |  risk | This expression has type int, but is expected to have type int -> option. Option.option int
    COMPLETE | frontend/monomorphize.py::_rewrite_annotation_str | TCOK | DICT |  risk | This expression has type string, but is expected to have type int
    COMPLETE | frontend/monomorphize.py::_rewrite_annotations | TCOK | DICT |  risk | This expression has type int -> option.Option.option string, but is expected to have type int
    COMPLETE | frontend/monomorphize.py::_rewrite_call_sites | TCOK0 |  |  | 
    COMPLETE | frontend/monomorphize.py::_rewrite_subscript_calls_in_stmt | TCOK | DICT |  risk | This expression has type int -> option.Option.option int, but is expected to have type int
    COMPLETE | frontend/monomorphize.py::_rewrite_subscript_to_name | TCOK | PYVAL > DICT |  risk | This expression has type int -> option.Option.option int, but is expected to have type int
    COMPLETE | frontend/monomorphize.py::_specialize_decl | TCOK | MUTRECV > DICT > INTSTR | PH risk | This expression has type int, but is expected to have type string -> option. Option.option int
    COMPLETE | frontend/pure_ast.py::Comment.__init__ | STUCK-LOCATE | RIPPLE |  | This expression has type ref PyCSL_Program.emit_ir @rho, but is expected to have type PyCSL_Program.comment @r
    COMPLETE | frontend/pure_ast.py::NodeTransformer.generic_visit | TCOK | REBIND > MUTRECV > LISTSTR |  risk | This expression has type int, but is expected to have type array.Array.array 'mu @rho
    COMPLETE | frontend/pure_ast.py::NodeVisitor.generic_visit | TCOK0 |  |  risk | 
    COMPLETE | frontend/pure_ast.py::NodeVisitor.visit | TCOK | CALLABLE |  risk | This expression has type ref int @rho, it cannot be applied
    COMPLETE | frontend/pure_ast.py::_Parser._max_end | TCOK0 |  |  risk | 
    COMPLETE | frontend/pure_ast.py::_Parser._slice | STUCK-LOCATE | TUPLE > STRM > RIPPLE |  | This expression has type PyCSL_Program.pytuple_int_int, but is expected to have type int
    COMPLETE | frontend/pure_ast.py::_Parser.node | STUCK-LOCATE | RIPPLE |  | This expression has type PyCSL_Program._tok, but is expected to have type int
    COMPLETE | frontend/pure_ast.py::_Unparser.__init__ | STUCK-LOCATE | RIPPLE |  | this write effect does not happen in the expression
    COMPLETE | frontend/pure_ast.py::_Unparser._write_docstring_and_traverse_body | TCOK | GETATTR |  | This expression has type int, but is expected to have type array.Array.array int @rho
    COMPLETE | frontend/pure_ast.py::_Unparser._write_fstring_inner | STUCK-LOCATE | RIPPLE |  | this expression raises unlisted exception ValueError
    COMPLETE | frontend/pure_ast.py::_Unparser.buffered | TCOK | REF |  risk | This expression has type int, but is expected to have type ref 'mu @rho
    COMPLETE | frontend/pure_ast.py::_Unparser.delimit_if | TCOK | UNIT |  risk | This expression has type (), but is expected to have type int
    COMPLETE | frontend/pure_ast.py::_Unparser.get_type_comment | TCOK | FSTR |  risk | This expression has type string, but is expected to have type int
    COMPLETE | frontend/pure_ast.py::_Unparser.interleave | TCOK | CALLABLE > UNBOUND |  risk | unbound function or predicate symbol 'iter_length'
    COMPLETE | frontend/pure_ast.py::_Unparser.items_view | TCOK | CALLABLE |  | This expression has type int, it cannot be applied
    COMPLETE | frontend/pure_ast.py::_Unparser.set_precedence | TCOK | LISTSTR |  risk | This expression has type seq.Seq.seq int, but is expected to have type int
    COMPLETE | frontend/pure_ast.py::_Unparser.visit_Dict | STUCK-LOCATE | RIPPLE |  | This pattern has type ('mu, 'mu1), but is expected to have type int
    COMPLETE | frontend/pure_ast.py::_Unparser.visit_If | TCOK0 |  |  | 
    COMPLETE | frontend/pure_ast.py::_Unparser.visit_Lambda | TCOK | WITH-AS |  | function '_unparser__visit_Lambda' binds buffer with a `with ... as` clause, and no certified lowering models 
    COMPLETE | frontend/pure_ast.py::_Unparser.visit_MatchClass | STUCK-LOCATE | RIPPLE |  | This pattern has type ('mu, 'mu1), but is expected to have type int
    COMPLETE | frontend/pure_ast.py::_Unparser.visit_MatchMapping | STUCK-LOCATE | RIPPLE |  | This pattern has type ('mu, 'mu1), but is expected to have type int
    COMPLETE | frontend/pure_ast.py::_Unparser.visit_MatchStar | TCOK | INTSTR |  | This expression has type string, but is expected to have type int
    COMPLETE | frontend/pure_ast.py::_Unparser.visit_Module | TCOK | MUTRECV |  | `self._type_ignores.clear(...)` MUTATES its receiver in place, and no certified lowering models it: the call b
    COMPLETE | frontend/pure_ast.py::_decode_fstring_middle | STUCK-LOCATE | UNIT > RIPPLE |  | This expression has type string, but is expected to have type int
    COMPLETE | frontend/pure_ast.py::_parse_number | TCOK0 |  |  risk | 
    COMPLETE | frontend/pure_ast.py::copy_location | TCOK | REBIND |  risk | a function, method or class NAME is rebound after its definition (`setattr`/`delattr` of a function name at li
    COMPLETE | frontend/pure_ast.py::fix_missing_locations | STUCK-LOCATE | RIPPLE |  | This expression has type (), but is expected to have type int
    COMPLETE | frontend/pure_ast.py::get_source_segment | TCOK | MUTRECV > INTSTR > GENEXP > UNBOUND > STRM |  risk | This expression has type array.Array.array int @rho, but is expected to have type int
    COMPLETE | frontend/pure_ast.py::increment_lineno | TCOK | GETATTR > REF |  risk | This expression has type ref int @rho, but is expected to have type int
    COMPLETE | frontend/pure_ast.py::iter_child_nodes | TCOK0 |  |  risk | 
    COMPLETE | frontend/pure_ast.py::iter_fields | TCOK0 |  |  risk | 
    COMPLETE | frontend/pure_ast.py::literal_eval | STUCK-LOCATE | RIPPLE |  | This expression has type string, but is expected to have type int
    COMPLETE | frontend/pure_ast.py::main | TCOK | WITH-AS > LISTSTR > INTSTR > GETATTR |  risk | This expression has type (), but is expected to have type int
    COMPLETE | frontend/pure_ast.py::unparse | TCOK | SYNTAX |  | syntax error
    COMPLETE | frontend/pure_ast.py::walk | TCOK | LISTSTR > MUTRECV |  risk | `todo.extend(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abs
    COMPLETE | ir_schema.py::validate_ir | TCOK0 |  |  risk | 
    COMPLETE | module6_whyml/abstract_ops.py::AbstractOpsMixin._advance_past_referenced_axiom_decls | STUCK-LOCATE | STRM > INTSTR > RIPPLE |  | This expression has type int, but is expected to have type array.Array.array 'mu @rho
    COMPLETE | module6_whyml/abstract_ops.py::AbstractOpsMixin._find_abstract_val_insert_idx | TCOK | GENEXP |  risk | This expression has type array.Array.array string @rho, but is expected to have type int
    COMPLETE | module6_whyml/auto_trust.py::AutoTrustMixin._should_auto_trust_tuple_return | TCOK | NESTED > LISTSTR |  | This expression has type array.Array.array int @rho, but is expected to have type int /home/fabrice/git/pycsl-
    COMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._call_bytes_methods | TCOK | GETATTR > INTSTR |  risk | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    COMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._emit_bitwise_or_power | TCOK | DICT |  risk | This expression has type string, but is expected to have type int /home/fabrice/git/pycsl-plan/src/pycsl/core_
    COMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._emit_contract_logic_symbol | STUCK-LOCATE | DICT > STRM > GETATTR > INTSTR > RIPPLE |  | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    COMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._handle_ifexpr_expr | TCOK | RECORD |  risk | This expression has type PyCSL_Program.emit_ir, but is expected to have type int /home/fabrice/git/pycsl-plan/
    COMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._static_width | STUCK-LOCATE | RIPPLE |  | This expression has type PyCSL_Program.emit_ir, but is expected to have type string -> option.Option.option in
    COMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._tag_of_value | TCOK | DICT |  | This expression has type string, but is expected to have type int /home/fabrice/git/pycsl-plan/src/pycsl/core_
    COMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._to_bool | STUCK-LOCATE | RIPPLE |  | This expression has type PyCSL_Program.emit_ir, but is expected to have type string -> option.Option.option in
    COMPLETE | module6_whyml/functions.py::FunctionEmissionMixin._emit_subtyping_goals | TCOK | DICT > LISTSTR |  | This expression has type seq.Seq.seq int, but is expected to have type seq. Seq.seq string
    COMPLETE | module6_whyml/functions.py::FunctionEmissionMixin._mixin_dep_pseudo_functions | TCOK | SET > TUPLE > DICT |  risk | This expression has type seq.Seq.seq ('mu -> option.Option.option 'mu1), but is expected to have type seq.Seq.
    COMPLETE | module6_whyml/functions.py::FunctionEmissionMixin._param_type_str | TCOK | MUTRECV > DICT > MEMB > INTSTR > GETATTR |  risk | This expression has type string, but is expected to have type int
    COMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._emit_inductive_decls | TCOK | NESTED > LISTSTR |  risk | This expression has type seq.Seq.seq int, but is expected to have type seq. Seq.seq string
    COMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._emit_module_globals | TCOK | MUTRECV > FSTR > GENEXP > LISTSTR |  risk | This expression has type seq.Seq.seq int, but is expected to have type seq. Seq.seq string
    COMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._emit_opaque_class_aliases | TCOK | MUTPARAM > STRM |  | This expression has type int, but is expected to have type string
    COMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._emit_preamble_no_exception_predicates | TCOK | LISTSTR |  risk | This expression has type seq.Seq.seq int, but is expected to have type seq. Seq.seq string
    COMPLETE | module6_whyml/statements.py::StatementEmissionMixin._collect_string_elem_read_locals.rec | STUCK-LOCATE | RIPPLE |  | This expression has type array.Array.array int @rho, but is expected to have type int /home/fabrice/git/pycsl-
    COMPLETE | module6_whyml/statements.py::StatementEmissionMixin._handle_augassign_stmt | TCOK | GETATTR > DICT |  risk | This expression has type string, but is expected to have type int /home/fabrice/git/pycsl-plan/src/pycsl/core_
    COMPLETE | module6_whyml/statements.py::StatementEmissionMixin._seq_init_expr | STUCK-LOCATE | RIPPLE |  | This expression has type PyCSL_Program.emit_ir, but is expected to have type string -> option.Option.option in
    COMPLETE | module6_whyml/struct_format.py::parse_format | STUCK-LOCATE | MUTRECV > RIPPLE |  | The type of top-level exception Return__union_parse_format_0 has mutable components
    COMPLETE | proof2why3/crosscheck.py::CrossCheckResult.diagnostic | TCOK | INTSTR |  risk | This expression has type string, but is expected to have type int
    COMPLETE | proof2why3/crosscheck_ir.py::IRCrossCheckResult.diagnostic | TCOK | OPTREC |  risk | This expression has type int, but is expected to have type option.Option. option PyCSL_Program.term
    COMPLETE | proof2why3/crosscheck_ir.py::IRCrossCheckResult.pairwise | STUCK-LOCATE | RIPPLE |  | This expression has type bool, but is expected to have type int /home/fabrice/git/pycsl-plan/src/pycsl/core_ir
    COMPLETE | proof2why3/extract.py::_split_rocq_check_output | TCOK | STRM > LISTSTR |  risk | This expression has type seq.Seq.seq int, but is expected to have type array. Array.array int @rho
    COMPLETE | proof2why3/from_sexp.py::_construct_indices | TCOK | PYVAL |  | This expression has type int, but is expected to have type PyCSL_Program. pyval
    COMPLETE | proof2why3/from_sexp.py::_find_construct_idx | TCOK | RECORD |  risk | This expression has type PyCSL_Program._union__find_construct_idx_2, but is expected to have type int
    COMPLETE | proof2why3/normalize.py::normalize_prover_output | TCOK | STRM > EXT |  risk | This expression has type int, but is expected to have type string
    COMPLETE | proof2why3/sertop.py::_sexp_parse | TCOK | MUTRECV > LISTSTR > INTSTR |  | This expression has type string, but is expected to have type int /home/fabrice/git/pycsl-plan/src/pycsl/core_
    COMPLETE | proof2why3/sertop.py::_sexp_tokens | TCOK0 |  |  risk | 
    COMPLETE | pycsl.py::_find_coqc | TCOK | RECORD |  | This expression has type int, but is expected to have type PyCSL_Program. _union__find_coqc_1 /home/fabrice/gi
    COMPLETE | pycsl.py::_merge_records_best_of_n | TCOK | DICT |  risk | This expression has type int, but is expected to have type string -> option. Option.option PyCSL_Program.hval 
    COMPLETE | pycsl.py::_parse_args | TCOK0 |  |  risk | 
    COMPLETE | pycsl.py::_print_soundness_report | TCOK | DICT |  risk | This expression has type int, but is expected to have type array.Array.array int @rho /home/fabrice/git/pycsl-
    COMPLETE | pycsl.py::_record_answer | STUCK-LOCATE | DICT > RIPPLE |  | This expression has type string -> option.Option.option PyCSL_Program.hval, but is expected to have type int -
    COMPLETE | pycsl.py::_residual_selectors_from_records | TCOK | DICT > LISTSTR |  | This expression has type array.Array.array int @rho, but is expected to have type int /home/fabrice/git/pycsl-
    COMPLETE | pycsl.py::_run_audit_mode | TCOK | INTSTR > GETATTR > UNBOUND |  risk | unbound function or predicate symbol 'exit_code' /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py:17
    FACADE | frontend/Module3_Weaver.py::Module3_Weaver._extract_happy_properties | TCOK | MUTRECV > MUTPARAM > GENEXP |  risk | This expression has type int, but is expected to have type array.Array.array int @rho
    FACADE | frontend/pure_ast.py::_Unparser.write | TCOK | MUTRECV |  | `self._source.extend(...)` MUTATES its receiver in place, and no certified lowering models it: the call become
    FACADE | frontend/pure_ast.py::_const_value_setter | TCOK | UNBOUND |  | unbound function or predicate symbol 'self'
    FACADE | module6_whyml/expressions.py::ExpressionEmissionMixin._handle_sum_call | TCOK | DICT |  risk | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    FACADE | module6_whyml/identifiers.py::stable_hash | TCOK0 |  |  risk | 
    FACADE | module6_whyml/preamble.py::PreambleEmissionMixin._mutex_inv_application | TCOK | LISTSTR |  risk | This expression has type array.Array.array string @rho, but is expected to have type int
    FACADE | module6_whyml/scc.py::compute_sccs | TCOK | NESTED > INTSTR |  risk | This expression has type int, but is expected to have type string
    FACADE | proof2why3/from_lean_json.py::_is_ofnat_lit | TCOK | TUPLE |  risk | This expression has type int -> option.Option.option int, but is expected to have type int
    FACADE | proof2why3/normalize.py::normalize_whyml_axiom | TCOK | EXT |  | This expression has type int, but is expected to have type string
    FACADE | proof2why3/sertop.py::parse_sexp | TCOK | LISTSTR |  | This expression has type int, but is expected to have type array.Array.array string @rho /home/fabrice/git/pyc
    FACADE | pycsl.py::_function_body_eqs | TCOK | EXT |  risk | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    FACADE?(return neutralised) | audit_proof_reverify.py::ReverifyReport.summary | TCOK | FLOAT |  | This expression has type real, but is expected to have type int
    FACADE?(return neutralised) | audit_proof_reverify.py::_cache_key | TCOK | STRM > EXT |  | This expression has type array.Array.array int @rho, but is expected to have type int
    FACADE?(return neutralised) | audit_proof_reverify.py::_cache_load | TCOK | EXT |  | This expression has type int, but is expected to have type PyCSL_Program. _union__cache_load_0
    FACADE?(return neutralised) | audit_proof_reverify.py::_to_cache_payload | TCOK | INTSTR |  | This expression has type string, but is expected to have type int
    FACADE?(return neutralised) | frontend/ir_resolve.py::_get_module_exports | TCOK | WITH-AS > GENEXP |  risk | This expression has type int, but is expected to have type PyCSL_Program. _union__get_module_exports_1
    FACADE?(return neutralised) | frontend/pure_ast.py::_Tok.__repr__ | TCOK | TUPLE |  | This expression has type PyCSL_Program.pytuple_int_int, but is expected to have type int
    FACADE?(return neutralised) | frontend/pure_ast.py::_const_value_getter | TCOK | UNBOUND |  | unbound function or predicate symbol 'self'
    FACADE?(return neutralised) | proof2why3/sertop.py::SertopSession.type_of_batch | TCOK | CALLABLE > LISTSTR |  | This expression has type array.Array.array int @rho, but is expected to have type int /home/fabrice/git/pycsl-
    FACADE?(return neutralised) | pycsl.py::_record_key | TCOK | SET |  | This expression has type array.Array.array int @rho, but is expected to have type int /home/fabrice/git/pycsl-
    FACADE?(return neutralised) | pycsl.py::_synthesize_block | TCOK | STRM > FLOAT > UNBOUND |  | unbound function or predicate symbol 'tok' /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py:1734: Us
    FACADE?(return neutralised) | pycsl.py::_synthesize_legacy_text | TCOK | STRM |  | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._compute_shared_module_maps | CAP-ROUNDS | ALIAS |  | [module6-whyml]: function 'module6_whymltranspiler___compute_shared_module_maps': a dict/set value reaches the
    INCOMPLETE | Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._emit_prefunctions_infra | STUCK-PH | DICT > LISTSTR | PH | This expression has type int, but is expected to have type array.Array.array string @rho /home/fabrice/git/pyc
    INCOMPLETE | Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._render_callee_condition | STUCK-NEUTRALISE | MUTRECV > EXC |  | [whyml-emit]: `except Exception` in '_render_callee_condition' is meant to catch the raised `PyCSLSemanticErro
    INCOMPLETE | Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._shared_use_lines | STUCK-PH | LISTSTR > DICT | PH | This expression has type array.Array.array int @rho, but is expected to have type array.Array.array string @rh
    INCOMPLETE | Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._sig_val_from_let | STUCK-PH | STRM > LISTSTR > INTSTR > NESTED |  | This expression has type array.Array.array int @rho, but is expected to have type array.Array.array string @rh
    INCOMPLETE | Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._transpile_modular | STUCK-LOCATE | REBIND |  | a function, method or class NAME is rebound after its definition (a write through a namespace dict at line 109
    INCOMPLETE | Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler.transpile | STUCK-LOCATE | REBIND |  | a function, method or class NAME is rebound after its definition (a write through a namespace dict at line 109
    INCOMPLETE | audit_proof.py::_audit_one_prover | CAP-ROUNDS | MUTRECV > GENEXP > SET > INTSTR > EXT > REF > GETATTR |  | This expression has type int, but is expected to have type ref 'mu @rho
    INCOMPLETE | audit_proof.py::_extract_directives | STUCK-PH | STRM > INTSTR > LISTSTR | PH | This expression has type array.Array.array int @rho, but is expected to have type array.Array.array PyCSL_Prog
    INCOMPLETE | audit_proof.py::_index_proofs_dir | STUCK-PH | EXC > SET > EXT > INTSTR > DICT | PH | This expression has type int, but is expected to have type int -> option. Option.option int
    INCOMPLETE | audit_proof.py::_index_proofs_dir_by_file | STUCK-PH | MUTRECV > DICT > EXT > INTSTR | PH | This expression has type int, but is expected to have type int -> option. Option.option int
    INCOMPLETE | audit_proof_reverify.py::_split_rocq_print_assumptions | STUCK-PH | GENEXP > DICT | PH | This expression has type int -> option.Option.option string, but is expected to have type string -> option.Opt
    INCOMPLETE | core_ir_semantic.py::_returns_literal_none | STUCK-PH | NESTED |  | nested function 'walk' is lifted to a sibling of its enclosing function, and the lift is not faithful here: an
    INCOMPLETE | core_ir_semantic.py::run_ir_semantic_checks | CAP-ROUNDS | SET > PYVAL |  | This expression has type int, but is expected to have type PyCSL_Program. pyval
    INCOMPLETE | frontend/Module1_Ingestor.py::Module1_Ingestor.process | STUCK-PH | STRM > LISTSTR | PH | This expression has type array.Array.array int @rho, but is expected to have type array.Array.array PyCSL_Prog
    INCOMPLETE | frontend/Module1_Ingestor.py::_Harvester._make | STUCK-PH | MUTRECV > GETATTR > GENEXP > REF > TUPLE |  | This expression has type int, but is expected to have type (int, int)
    INCOMPLETE | frontend/Module1_Ingestor.py::_Harvester._normalize_leading | STUCK-LOCATE | GENEXP |  | unbound function or predicate symbol '_match_block_hdr'
    INCOMPLETE | frontend/Module1_Ingestor.py::_match_block_hdr | STUCK-PH | TUPLE |  | This expression has type int, but is expected to have type (int, int)
    INCOMPLETE | frontend/Module2_Parser.py::_ContractParser.__init__ | STUCK-LOCATE | RIPPLE |  | This term has type int, but is expected to have type array.Array.array 'xi
    INCOMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_act_block | STUCK-PH | RECORD > LISTSTR |  | This expression has type PyCSL_Program.act <array.Array.array int @rho1> @rho, but is expected to have type in
    INCOMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_assigns | STUCK-PH | LISTSTR > EFFECT |  | this write effect does not happen in the expression
    INCOMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_assigns_target | STUCK-LOCATE | HETERO |  | heterogeneous list literal (contains a record (Nothing) element mixed with other element types) has no faithfu
    INCOMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_atom_name | STUCK-REPEAT | SYNTAX | PH | syntax error
    INCOMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_atom_primary | STUCK-PH | RECORD > OPTREC |  | This expression has type int, but is expected to have type PyCSL_Program. emit_ir
    INCOMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_contract | STUCK-REPEAT | SYNTAX | PH | syntax error
    INCOMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_datatype | STUCK-PH | LISTSTR |  | This expression has type PyCSL_Program.datatypedecl <array.Array.array int @rho1, array.Array.array int @rho2>
    INCOMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_inductive | STUCK-PH | UNIT > LISTSTR |  | This expression has type PyCSL_Program.inductivedecl <array.Array.array int @rho1, array.Array.array int @rho2
    INCOMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_quantifier | STUCK-PH | CALLABLE > OPTREC |  | This expression has type int, but is expected to have type PyCSL_Program. emit_ir
    INCOMPLETE | frontend/Module2_Parser.py::_ContractParser._parse_variant_def | STUCK-PH | TUPLE |  | This expression has type int, but is expected to have type (int, int)
    INCOMPLETE | frontend/Module2_Parser.py::_ContractParser.parse | STUCK-PH | UNIT > EFFECT | PH | this write effect does not happen in the expression
    INCOMPLETE | frontend/Module2_Parser.py::_lex_contract | STUCK-LOCATE | RIPPLE |  | unbound function or predicate symbol 'toks'
    INCOMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._consolidate_module_concurrency | STUCK-REPEAT | MUTRECV > GETATTR > OBJSTATE | PH | this expression depends on variable _pyobj_state, which is left out in the specification
    INCOMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._expand_happy_properties | STUCK-LOCATE | MUTRECV > EXC |  | [whyml-emit]: '_expand_happy_properties' constructs an object whose `__init__` / `__post_init__` can raise `_C
    INCOMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._field_write_site | STUCK-LOCATE | ARRAY-REASSIGN |  | reassigning an array LOCAL from a non-literal right-hand side is not modelled: the local is represented as a f
    INCOMPLETE | frontend/Module3_Weaver.py::Module3_Weaver._synthesize_selfcomp | STUCK-LOCATE | NESTED > MUTRECV > ARRAY-REASSIGN |  | reassigning an array LOCAL from a non-literal right-hand side is not modelled: the local is represented as a f
    INCOMPLETE | frontend/Module3_Weaver.py::Module3_Weaver.process | CAP-ROUNDS | ALIAS > MUTRECV |  | `_rb_stack.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an a
    INCOMPLETE | frontend/Module3_Weaver.py::PyCSLWeaver._desugar_acts | STUCK-PH | GETATTR > GENEXP > RECORD > DICT > LISTSTR > OBJSTATE | PH | this expression depends on variable _pyobj_state, which is left out in the specification
    INCOMPLETE | frontend/Module3_Weaver.py::PyCSLWeaver._dispatch_function_contracts | STUCK-PH | LISTSTR > GETATTR > OBJSTATE |  | this expression depends on variable _pyobj_state, which is left out in the specification
    INCOMPLETE | frontend/Module3_Weaver.py::PyCSLWeaver._extract_mixin_directives | STUCK-LOCATE | NESTED |  | function 'pycslweaver__close_dep' writes open_dep through a `nonlocal` declaration, and no certified lowering 
    INCOMPLETE | frontend/Module3_Weaver.py::PyCSLWeaver.visit_ClassDef | CAP-ROUNDS | GENEXP > RECORD > GETATTR |  | This expression has type PyCSL_Program.py_classdef_node, but is expected to have type int
    INCOMPLETE | frontend/Module5_IREmitter.py::Module5_IREmitter.generate_json | STUCK-LOCATE | REBIND |  | a function, method or class NAME is rebound after its definition (`setattr`/`delattr` of a function name at li
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._build_function_ir | CAP-ROUNDS | MUTRECV |  | `_wb_stack.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an a
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._build_function_symbol_table | CAP-ROUNDS | MUTRECV > NESTED > GETATTR |  | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._collect_class_fields | CAP-ROUNDS | MUTRECV > SET > GETATTR |  | This expression has type PyCSL_Program.py_classdef_node, but is expected to have type int /home/fabrice/git/py
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._csl_in | STUCK-PH | RECORD > DICT |  | This expression has type 'mu -> option.Option.option int, but is expected to have type PyCSL_Program.emit_ir /
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._csl_list_to_ir | STUCK-PH | RECORD > OTHER > EFFECT | PH | this write effect does not happen in the expression /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._detect_array_dimensions | CAP-ROUNDS | NESTED > MUTRECV > MUTPARAM |  | [module6-whyml]: in-place mutation of dict/set parameter 'func_ir' (`func_ir[...] = ...`) is out of scope: Pyt
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._detect_seq_promotion | CAP-ROUNDS | MUTRECV > MUTPARAM |  | [module6-whyml]: in-place mutation of dict/set parameter 'func_ir' (`func_ir[...] = ...`) is out of scope: Pyt
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._emit_namedtuple_record | STUCK-PH | MUTRECV > GETATTR > INTSTR | PH | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._emit_protocol_interface | STUCK-PH | MUTRECV > GETATTR > DICT > RECORD > SET | PH | this write effect does not happen in the expression /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._emit_typeddict_record | STUCK-PH | MUTRECV > GETATTR > INTSTR > DICT > EFFECT |  | this write effect does not happen in the expression /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._encode_callable_annotation | STUCK-PH | LISTSTR > TUPLE > GETATTR | PH | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /home/fabrice/git/pycsl-plan
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._field_type_from_annotation_inst | STUCK-REPEAT | RECORD > INTSTR > EFFECT | PH | this write effect does not happen in the expression /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._get_mutex_invariant_ir | STUCK-PH | OPTREC |  | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /home/fabrice/git/pycsl-plan
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._m5_get_type_name | STUCK-NEUTRALISE | EXC |  | [whyml-emit]: `except Exception` in '_m5_get_type_name' is meant to catch the raised `PyCSLIRError`, a user su
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._match_pattern_to_ir | STUCK-REPEAT | ISBOOL > GETATTR | PH | This expression has type int, but is expected to have type int -> option. Option.option int /home/fabrice/git/
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._normalize_literal_annotation | STUCK-PH | MUTRECV > GETATTR > TUPLE > DICT | PH | This expression has type int, but is expected to have type ref 'mu @rho /home/fabrice/git/pycsl-plan/src/pycsl
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._normalize_union_annotation | STUCK-PH | MUTRECV > RECORD | PH | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._populate_protocol_conformance | STUCK-PH | MUTRECV > GETATTR > DICT > STRM | PH | This expression has type array.Array.array int @rho, but is expected to have type string /home/fabrice/git/pyc
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._py_expr_call | STUCK-PH | MUTRECV > DICT > SET > GETATTR |  | This expression has type 'mu -> option.Option.option int, but is expected to have type PyCSL_Program.emit_ir /
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._py_stmts_to_ir | STUCK-PH | GETATTR > DICT > EFFECT | PH | this write effect does not happen in the expression /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._synthesize_namedtuple_functional | STUCK-PH | MUTRECV > GETATTR > TUPLE | PH | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /home/fabrice/git/pycsl-plan
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._synthesize_typeddict_functional | STUCK-REPEAT | MUTRECV > GETATTR > TUPLE > RECORD > DICT > EFFECT | PH | this write effect does not happen in the expression /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter.visit_ClassDef | CAP-ROUNDS | MUTRECV |  | `_n183.sort(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abst
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter.visit_FunctionDef | STUCK-LOCATE | ARRAY-REASSIGN |  | reassigning an array LOCAL from a non-literal right-hand side is not modelled: the local is represented as a f
    INCOMPLETE | frontend/Module5_IREmitter.py::PyCSLToJSONEmitter.visit_Module | STUCK-LOCATE | ARRAY-REASSIGN |  | reassigning an array LOCAL from a non-literal right-hand side is not modelled: the local is represented as a f
    INCOMPLETE | frontend/import_classifier.py::_stub_set | STUCK-REPEAT | DICT | PH | This expression has type int, but is expected to have type int -> option. Option.option int
    INCOMPLETE | frontend/import_classifier.py::check_imports | STUCK-PH | PYVAL > GENEXP > TUPLE | PH | This expression has type int, but is expected to have type array.Array.array PyCSL_Program.pytuple_str_str_int
    INCOMPLETE | frontend/ir_inline.py::_Inliner._expand | STUCK-PH | MUTRECV > PYVAL | PH | This expression has type int, but is expected to have type array.Array.array int @rho
    INCOMPLETE | frontend/ir_inline.py::_inline_calls | CAP-ROUNDS | MUTRECV > DICT > LISTSTR > GETATTR > SET |  | This expression has type array.Array.array int @rho, but is expected to have type int
    INCOMPLETE | frontend/ir_inline.py::_recursive_methods | STUCK-PH | NESTED > DICT | PH | This expression has type int, but is expected to have type int -> option. Option.option int
    INCOMPLETE | frontend/ir_resolve.py::_find_record_type_from_dep_imports | STUCK-PH | TUPLE > INTSTR | PH | This expression has type int, but is expected to have type string
    INCOMPLETE | frontend/ir_resolve.py::_process_dependency | CAP-ROUNDS | WITH-AS > MUTRECV > RECORD > EXT > UNBOUND |  | unbound function or predicate symbol 'dep_source'
    INCOMPLETE | frontend/ir_resolve.py::_resolve_direct_imports | CAP-ROUNDS | MUTRECV > UNBOUND |  | unbound function or predicate symbol 'level'
    INCOMPLETE | frontend/ir_resolve.py::_resolve_imported_base_classes | STUCK-PH | MUTRECV > SET > INTSTR | PH | This expression has type int, but is expected to have type string
    INCOMPLETE | frontend/ir_resolve.py::_resolve_imported_classes | STUCK-PH | MUTRECV > UNBOUND | PH | This expression has type int, but is expected to have type string
    INCOMPLETE | frontend/ir_resolve.py::_resolve_module_imports | STUCK-PH | STRM > INTSTR > LISTSTR | PH | This expression has type int, but is expected to have type string
    INCOMPLETE | frontend/ir_resolve.py::_resolve_module_path | STUCK-PH | STRM | PH | This expression has type string, but is expected to have type int
    INCOMPLETE | frontend/ir_resolve.py::_resolve_wildcard_imports | STUCK-PH | INTSTR | PH | This expression has type int, but is expected to have type string
    INCOMPLETE | frontend/ir_resolve.py::_strip_dir_scan_proofs | STUCK-PH | DICT | PH | This expression has type int, but is expected to have type array.Array.array int @rho
    INCOMPLETE | frontend/ir_resolve.py::apply_composition | STUCK-NEUTRALISE | NESTED |  | nested function 'walk' is lifted to a sibling of its enclosing function, and the lift is not faithful here: it
    INCOMPLETE | frontend/ir_resolve.py::apply_inheritance | CAP-ROUNDS | NESTED > MUTRECV |  | `td.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstract
    INCOMPLETE | frontend/ir_resolve.py::resolve_imports | STUCK-LOCATE | MUTRECV > ARRAY-REASSIGN |  | reassigning an array LOCAL from a non-literal right-hand side is not modelled: the local is represented as a f
    INCOMPLETE | frontend/module_collect.py::collect_module_constants | STUCK-PH | GETATTR > EXT |  | This expression has type int, but is expected to have type int -> option. Option.option int
    INCOMPLETE | frontend/module_collect.py::collect_module_globals | STUCK-PH | GETATTR > EXT |  | This expression has type int, but is expected to have type int -> option. Option.option int
    INCOMPLETE | frontend/monomorphize.py::_collect_generic_decls | STUCK-PH | DICT |  | This expression has type int -> option.Option.option (int -> option.Option. option int), but is expected to ha
    INCOMPLETE | frontend/monomorphize.py::_emit_specializations | CAP-ROUNDS | MUTRECV > DICT > INTSTR > GENEXP |  | This expression has type seq.Seq.seq string, but is expected to have type int
    INCOMPLETE | frontend/monomorphize.py::_record_classification | STUCK-PH | MUTRECV | PH | This expression has type int, but is expected to have type array.Array.array int @rho
    INCOMPLETE | frontend/monomorphize.py::_specialize_function | STUCK-PH | MUTRECV > DICT > INTSTR > RECORD > GENEXP | PH | This expression has type int, but is expected to have type string -> option. Option.option int /home/fabrice/g
    INCOMPLETE | frontend/monomorphize.py::apply_monomorphization | STUCK-PH | DICT | PH | This expression has type int, but is expected to have type PyCSL_Program. pyval
    INCOMPLETE | frontend/pure_ast.py::Ellipsis.__new__ | STUCK-PH | OBJSTATE |  | Class 'Ellipsis' (line 113): non-trivial `__new__` is rejected under UB-7.6. Allocation interposition (caching
    INCOMPLETE | frontend/pure_ast.py::NodeVisitor.visit_Constant | STUCK-PH | EXC |  | [whyml-emit]: the `else:` block of a `try` in 'nodevisitor__visit_Constant' jumps out (ROUTE #37): Module 6 ap
    INCOMPLETE | frontend/pure_ast.py::_Parser.__init__ | STUCK-LOCATE | RIPPLE |  | This term has type int, but is expected to have type array.Array.array 'xi
    INCOMPLETE | frontend/pure_ast.py::_Parser._fin | STUCK-PH | GENEXP | PH | this expression depends on variable _pyobj_state, which is left out in the specification
    INCOMPLETE | frontend/pure_ast.py::_Parser._fin_block | STUCK-PH | GETATTR | PH | This expression has type int, but is expected to have type ()
    INCOMPLETE | frontend/pure_ast.py::_Precedence.next | STUCK-PH | RECORD > OPTREC |  | This expression has type PyCSL_Program._precedence, but is expected to have type int
    INCOMPLETE | frontend/pure_ast.py::_Unparser._str_literal_helper | STUCK-PH | MUTRECV > NESTED > LISTSTR | PH | This expression has type int, but is expected to have type ref 'mu @rho
    INCOMPLETE | frontend/pure_ast.py::_Unparser.visit_BoolOp | STUCK-LOCATE | NESTED |  | function '_unparser__increasing_level_traverse' writes operator_precedence through a `nonlocal` declaration, a
    INCOMPLETE | frontend/pure_ast.py::_Unparser.visit_JoinedStr | STUCK-PH | WITH-AS > UNBOUND > CALLABLE > TUPLE | PH | This expression has type int, but is expected to have type ref 'mu @rho
    INCOMPLETE | frontend/pure_ast.py::_Unparser.visit_arguments | STUCK-PH | GETATTR > TUPLE | PH | This expression has type int, but is expected to have type ref 'mu @rho
    INCOMPLETE | frontend/pure_ast.py::_build_nodes | STUCK-LOCATE | REBIND |  | a function, method or class NAME is rebound after its definition (a write through a namespace dict at line 63)
    INCOMPLETE | frontend/pure_ast.py::_decode_string | STUCK-PH | LISTSTR > STRM > TUPLE | PH | This expression has type int, but is expected to have type (int, int, int)
    INCOMPLETE | frontend/pure_ast.py::_lex | STUCK-LOCATE | NESTED > RIPPLE |  | unbound function or predicate symbol 'toks'
    INCOMPLETE | frontend/pure_ast.py::_merge_str_constants | STUCK-PH |  | PH | a function, method or class NAME is rebound after its definition (attribute `.n` written on `Constant...` at l
    INCOMPLETE | frontend/pure_ast.py::_self_test | STUCK-LOCATE | MUTRECV > EXC > STRM > ARRAY-REASSIGN |  | reassigning an array LOCAL from a non-literal right-hand side is not modelled: the local is represented as a f
    INCOMPLETE | frontend/pure_ast.py::comments | STUCK-REPEAT | GETATTR > LISTSTR | PH | This expression has type array.Array.array int @rho, but is expected to have type int
    INCOMPLETE | frontend/pure_ast.py::dump | STUCK-PH | NESTED > INTSTR | PH | This expression has type string, but is expected to have type int
    INCOMPLETE | frontend/pure_ast.py::parse | STUCK-LOCATE | OTHER |  | comparing class instances with `==`/`!=` in a `#@` clause is out of scope for class `_Tok`: PyCSL models an in
    INCOMPLETE | module6_whyml/abstract_ops.py::AbstractOpsMixin._add_abstract_op | STUCK-PH | MUTRECV > STRM > STRPLUS | PH | This expression has type int, but is expected to have type string
    INCOMPLETE | module6_whyml/abstract_ops.py::AbstractOpsMixin._insert_abstract_val_block | CAP-ROUNDS | MUTRECV > LISTSTR > STRM > INTSTR |  | This expression has type int, but is expected to have type string
    INCOMPLETE | module6_whyml/auto_trust.py::AutoTrustMixin._build_witness_str | STUCK-PH | DICT | PH | This expression has type int, but is expected to have type string -> option. Option.option string /home/fabric
    INCOMPLETE | module6_whyml/auto_trust.py::AutoTrustMixin._check_witness_vals | STUCK-LOCATE | REBIND |  | a name's runtime value is not the one the model reads (a dynamic `eval` that can bind into the module namespac
    INCOMPLETE | module6_whyml/expr_ghost_spec_ops.py::GhostSpecOpsMixin._handle_ctor_payload_expr | STUCK-PH | RECORD > DICT > INTSTR > OBJSTATE | PH | variable _pyobj_state does not occur in this expression
    INCOMPLETE | module6_whyml/expr_ghost_spec_ops.py::GhostSpecOpsMixin._handle_proj_expr | STUCK-PH | RECORD > INTSTR > OBJSTATE | PH | variable _pyobj_state does not occur in this expression
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._call_named_builtins | CAP-ROUNDS | MUTRECV > DICT > MUTPARAM > SET |  | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /home/fabrice/git/pycsl-plan
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._call_record_constructor | STUCK-PH | NESTED > DICT | PH | This expression has type int, but is expected to have type string -> option. Option.option string /home/fabric
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._coerce_dotted_args | CAP-ROUNDS | GENEXP > INTSTR > FSTR > GETATTR |  | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._content_string_method | STUCK-PH | TUPLE | PH | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /home/fabrice/git/pycsl-plan
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._dotted_ensures_suffix | CAP-ROUNDS | ALIAS > DICT > SET |  | This expression has type PyCSL_Program._union__dotted_ensures_suffix_4, but is expected to have type int /home
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._e | STUCK-PH | RECORD > EFFECT |  | this write effect does not happen in the expression /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._emit_membership | CAP-ROUNDS | DICT > STRM > INTSTR > FSTR > SET |  | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /home/fabrice/git/pycsl-plan
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._expr_to_whyml_string_ctx | STUCK-PH | DICT | PH | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._handle_attribute_expr | STUCK-PH | GETATTR > STRM > DICT | PH | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._handle_binop | CAP-ROUNDS | MUTRECV |  | `_r76_sstack.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._handle_call_expr | CAP-ROUNDS | MUTRECV > ISBOOL > SYNTAX > SET |  | This expression has type int, but is expected to have type array.Array.array int @rho /home/fabrice/git/pycsl-
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._handle_dotted_call | CAP-ROUNDS | MUTRECV > ALIAS |  | `_sh_stack.extend(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes a
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._handle_fstring_expr | CAP-ROUNDS | NESTED > RECORD > OBJSTATE |  | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /home/fabrice/git/pycsl-plan
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._handle_isinstance | STUCK-PH | MUTRECV > SET | PH | This expression has type int, but is expected to have type PyCSL_Program. _union__handle_isinstance_13 /home/f
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._handle_join_call | STUCK-PH | DICT > SET | PH | This expression has type string, but is expected to have type PyCSL_Program. emit_ir /home/fabrice/git/pycsl-p
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._handle_len_call | CAP-ROUNDS | DICT > SET > FSTR |  | This expression has type array.Array.array int @rho, but is expected to have type int /home/fabrice/git/pycsl-
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._handle_struct_call | STUCK-PH | MUTRECV > DICT > GENEXP | PH | This expression has type array.Array.array int @rho, but is expected to have type string /home/fabrice/git/pyc
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._handle_subscript | STUCK-PH | MUTRECV > DICT | PH | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._is_emit_ir_expr | CAP-ROUNDS | DICT > GENEXP > GETATTR |  | This expression has type string, but is expected to have type array.Array. array 'mu @rho /home/fabrice/git/py
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._is_string_expr | STUCK-LOCATE | GENEXP |  | unbound function or predicate symbol '_sing0' /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py:1708:
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._iter_len_expr | STUCK-PH | NESTED > DICT | PH | This expression has type int, but is expected to have type PyCSL_Program. _union__iter_len_expr_2 /home/fabric
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._linear_form | CAP-ROUNDS | DICT > TUPLE > MEMB |  | This expression has type option.Option.option (int, int), but is expected to have type option.Option.option (i
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._match_pattern_cond | STUCK-PH | DICT > STRM > INTSTR | PH | this write effect does not happen in the expression /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._pop_quant_binder | STUCK-PH | MUTRECV > TUPLE > RECORD | PH | this write effect does not happen in the expression /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._push_quant_binder | STUCK-PH | ALIAS > MUTRECV > RECORD > TUPLE |  | This expression has type int, but is expected to have type (int, int) /home/fabrice/git/pycsl-plan/src/pycsl/c
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._resolve_dotted_signature | STUCK-LOCATE | ARRAY-REASSIGN |  | reassigning an array LOCAL from a non-literal right-hand side is not modelled: the local is represented as a f
    INCOMPLETE | module6_whyml/expressions.py::ExpressionEmissionMixin._union_local_read_projection | STUCK-PH | GETATTR > EFFECT |  | this write effect does not happen in the expression /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py
    INCOMPLETE | module6_whyml/functions.py::FunctionEmissionMixin._emit_contracts | CAP-ROUNDS | MUTRECV > DICT > LISTSTR |  | This expression has type int -> option.Option.option int, but is expected to have type int
    INCOMPLETE | module6_whyml/functions.py::FunctionEmissionMixin._emit_function | CAP-ROUNDS | MUTRECV > DICT > TUPLE > UNBOUND |  | This expression has type int, but is expected to have type string
    INCOMPLETE | module6_whyml/functions.py::FunctionEmissionMixin._emit_narrowing_vc | CAP-ROUNDS | NESTED > STRM > FSTR > SET > DICT > LISTSTR | PH | This expression has type array.Array.array int @rho, but is expected to have type array.Array.array string @rh
    INCOMPLETE | module6_whyml/functions.py::FunctionEmissionMixin._emit_union_arm_vc | STUCK-PH | INTSTR > LISTSTR | PH | This expression has type array.Array.array int @rho, but is expected to have type array.Array.array string @rh
    INCOMPLETE | module6_whyml/functions.py::FunctionEmissionMixin._parse_mixin_sig | STUCK-PH | INTSTR > TUPLE | PH | This expression has type int, but is expected to have type array.Array.array int @rho
    INCOMPLETE | module6_whyml/functions.py::FunctionEmissionMixin._render_refinement_goal | STUCK-PH | HETERO > TUPLE > DICT > STRM > FSTR | PH | This expression has type array.Array.array int @rho, but is expected to have type array.Array.array string @rh
    INCOMPLETE | module6_whyml/functions.py::FunctionEmissionMixin._reset_function_state | CAP-ROUNDS | MUTRECV > ISBOOL |  | `_w174.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstr
    INCOMPLETE | module6_whyml/identifiers.py::whyml_ident | STUCK-PH | FSTR | PH | This expression has type ref int @rho, but is expected to have type array. Array.array 'mu @rho1
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._emit_class_inv_axioms | STUCK-PH | INTSTR > SET > LISTSTR > GETATTR | PH | This expression has type array.Array.array int @rho, but is expected to have type array.Array.array string @rh
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._emit_preamble | STUCK-PH | DICT > LISTSTR | PH | This expression has type ref int @rho, but is expected to have type array. Array.array 'mu @rho1
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._emit_preamble_axioms | STUCK-PH | DICT > SET > MEMB | PH | This expression has type array.Array.array int @rho, but is expected to have type int
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._emit_preamble_exceptions | STUCK-PH | GENEXP > LISTSTR | PH | This expression has type array.Array.array int @rho, but is expected to have type array.Array.array string @rh
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._emit_preamble_uses | STUCK-PH | FSTR > DICT | PH | This expression has type seq.Seq.seq int, but is expected to have type int
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._emit_shared_state | STUCK-LOCATE | GENEXP |  | unbound function or predicate symbol '_inits_mi'
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._emit_type_decls | CAP-ROUNDS | MUTRECV > NESTED > SYNTAX |  | syntax error
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._emit_uncited_axiom_func_decls | STUCK-PH | GETATTR > MUTRECV > STRM > INTSTR | PH | This expression has type array.Array.array int @rho, but is expected to have type ref 'mu @rho1
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._fresh_globals_facts | STUCK-PH | SET > DICT > LISTSTR | PH | This expression has type array.Array.array int @rho, but is expected to have type array.Array.array string @rh
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._inductive_referenced_axiom_decls | STUCK-PH | STRM > INTSTR > SET > GETATTR | PH | This expression has type array.Array.array int @rho, but is expected to have type ref 'mu @rho1
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._precompute_axiom_logic_funcs | STUCK-PH | MUTRECV > NESTED |  | nested function 'preambleemissionmixin___walk' is lifted to a sibling of its enclosing function, and the lift 
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._scan_preamble_needs | STUCK-LOCATE | REBIND |  | a function, method or class NAME is rebound after its definition (a write through a namespace dict at line 109
    INCOMPLETE | module6_whyml/preamble.py::PreambleEmissionMixin._subst_self_in_expr | STUCK-PH | NESTED |  | nested function 'preambleemissionmixin__rec' is lifted to a sibling of its enclosing function, and the lift is
    INCOMPLETE | module6_whyml/scc.py::sort_functions_by_scc | CAP-ROUNDS | RECORD > SET > DICT |  | This expression has type int -> option.Option.option int, but is expected to have type int
    INCOMPLETE | module6_whyml/statements.py::StatementEmissionMixin._collect_field_decode_str_locals.rec | STUCK-LOCATE | NESTED |  | nested function 'statementemissionmixin__rec' is lifted to a sibling of its enclosing function, and the lift i
    INCOMPLETE | module6_whyml/statements.py::StatementEmissionMixin._emit_body_code | CAP-ROUNDS | ALIAS > MUTRECV |  | `_rr_work.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an ab
    INCOMPLETE | module6_whyml/statements.py::StatementEmissionMixin._emit_first_assign | STUCK-REPEAT | DICT > EFFECT | PH | this write effect does not happen in the expression /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py
    INCOMPLETE | module6_whyml/statements.py::StatementEmissionMixin._emit_frame_condition | CAP-ROUNDS | LISTSTR > TUPLE > SET > GENEXP > DICT |  | This expression has type int, but is expected to have type PyCSL_Program. emit_ir /home/fabrice/git/pycsl-plan
    INCOMPLETE | module6_whyml/statements.py::StatementEmissionMixin._handle_array_set_stmt | CAP-ROUNDS | DICT > GETATTR > INTSTR > RECORD |  | This expression has type string, but is expected to have type int /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | module6_whyml/statements.py::StatementEmissionMixin._handle_assign_stmt | CAP-ROUNDS | ALIAS |  | [module6-whyml]: function 'statementemissionmixin___handle_array_slice_set_stmt': a dict/set value reaches `se
    INCOMPLETE | module6_whyml/statements.py::StatementEmissionMixin._handle_expr_stmt | CAP-ROUNDS | MUTRECV > SIG |  | call to 'to_dict' passes 0 positional argument(s) but parameter 'node' has no default (arity 1). /home/fabrice
    INCOMPLETE | module6_whyml/statements.py::StatementEmissionMixin._handle_ghost_assign_stmt | CAP-ROUNDS | ALIAS |  | [module6-whyml]: function 'statementemissionmixin___handle_array_slice_set_stmt': a dict/set value reaches `se
    INCOMPLETE | module6_whyml/statements.py::StatementEmissionMixin._handle_tuple_unpack_stmt | CAP-ROUNDS | ALIAS |  | [module6-whyml]: function 'statementemissionmixin___handle_array_slice_set_stmt': a dict/set value reaches `se
    INCOMPLETE | module6_whyml/statements.py::StatementEmissionMixin._stmts_to_whyml | CAP-ROUNDS | MUTRECV > DICT > RECORD |  | This expression has type int, but is expected to have type PyCSL_Program. ghostassignstmt @rho /home/fabrice/g
    INCOMPLETE | module6_whyml/statements.py::StatementEmissionMixin._typed_local_vars | CAP-ROUNDS | ALIAS > NESTED |  | nested function 'statementemissionmixin___acnt' is lifted to a sibling of its enclosing function, and the lift
    INCOMPLETE | module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._callee_raised_in | CAP-ROUNDS | DICT > SET > LISTSTR |  | This expression has type PyCSL_Program.StrSet.set, but is expected to have type int -> option.Option.option in
    INCOMPLETE | module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._classify_iterable | STUCK-PH | DICT > INTSTR | PH | This expression has type int, but is expected to have type PyCSL_Program. emit_ir
    INCOMPLETE | module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._handle_for_stmt | CAP-ROUNDS | NESTED > ALIAS > MUTRECV |  | `_rf_stack.extend(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes a
    INCOMPLETE | module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._render_match_pattern | STUCK-LOCATE | REBIND |  | a name's runtime value is not the one the model reads (an attribute or item written, or a namespace reached, a
    INCOMPLETE | module6_whyml/struct_format.py::calcsize | STUCK-PH | DICT > UNBOUND |  | unbound exception symbol 'Return'
    INCOMPLETE | module6_whyml/types.py::TypeInferenceMixin._collect_array_var_assigns | CAP-ROUNDS | MUTRECV |  | `found.add(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstr
    INCOMPLETE | module6_whyml/types.py::TypeInferenceMixin._track_collection_metadata | CAP-ROUNDS | ALIAS > MUTRECV |  | `elem_map.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an ab
    INCOMPLETE | proof2why3/canonical.py::_ac_normalize | STUCK-PH | NESTED > GETATTR > GENEXP > RECORD > OPTREC |  | This expression has type int, but is expected to have type PyCSL_Program.term
    INCOMPLETE | proof2why3/canonical.py::_alpha_rename | STUCK-PH | GENEXP > OPTREC |  | This expression has type int, but is expected to have type PyCSL_Program.term
    INCOMPLETE | proof2why3/canonical.py::_dedup_arrow_chain | STUCK-PH | GETATTR > TUPLE > RECORD | PH | This expression has type int, but is expected to have type array.Array.array int @rho
    INCOMPLETE | proof2why3/canonical.py::_expand_nat_to_int | STUCK-PH | GETATTR > RECORD > OPTREC |  | This expression has type int, but is expected to have type PyCSL_Program.term
    INCOMPLETE | proof2why3/canonical.py::_flatten_foralls | STUCK-PH | MUTRECV > GETATTR > RECORD > LISTSTR | PH | This expression has type array.Array.array int @rho, but is expected to have type int
    INCOMPLETE | proof2why3/canonical.py::_iff_app_to_binop | STUCK-PH | RECORD > DICT > OPTREC |  | This expression has type int, but is expected to have type PyCSL_Program.term
    INCOMPLETE | proof2why3/canonical.py::_normalize_names | STUCK-PH | RECORD > OPTREC |  | This expression has type int, but is expected to have type PyCSL_Program.term
    INCOMPLETE | proof2why3/canonical.py::_normalize_type_string | STUCK-PH | INTSTR | PH | This expression has type ref int @rho, but is expected to have type array. Array.array 'mu @rho1
    INCOMPLETE | proof2why3/canonical.py::_sort_arrow_hypotheses | STUCK-PH | GETATTR > TUPLE | PH | This expression has type int, but is expected to have type PyCSL_Program.term
    INCOMPLETE | proof2why3/canonical.py::substitute | STUCK-PH | DICT > OPTREC |  | This expression has type int, but is expected to have type PyCSL_Program.term
    INCOMPLETE | proof2why3/crosscheck.py::_load_axiom_registry | STUCK-PH | INTSTR | PH | This expression has type int, but is expected to have type int -> option. Option.option int
    INCOMPLETE | proof2why3/crosscheck.py::crosscheck_file | STUCK-PH | MUTRECV > GENEXP | PH | This expression has type array.Array.array int @rho, but is expected to have type int
    INCOMPLETE | proof2why3/crosscheck.py::main | STUCK-PH | EXT > RECORD > DICT | PH | This expression has type int, but is expected to have type string
    INCOMPLETE | proof2why3/crosscheck_ir.py::_load_axiom_registry | STUCK-PH | INTSTR | PH | This expression has type int, but is expected to have type int -> option. Option.option int
    INCOMPLETE | proof2why3/crosscheck_ir.py::crosscheck_file_ir | STUCK-LOCATE | EXC |  | `except ` can be reached by an exception the model does not raise (AttributeError, TypeError, OverflowError, U
    INCOMPLETE | proof2why3/crosscheck_ir.py::main | STUCK-PH | EXT > RECORD > DICT | PH | This expression has type int, but is expected to have type string
    INCOMPLETE | proof2why3/from_lean_json.py::_linearize_app | STUCK-PH | MUTRECV > DICT | PH | This expression has type (string -> option.Option.option int, array.Array. array int @rho), but is expected to
    INCOMPLETE | proof2why3/from_lean_json.py::project_to_ir | STUCK-PH | DICT > OPTREC |  | This expression has type int, but is expected to have type PyCSL_Program.term /home/fabrice/git/pycsl-plan/src
    INCOMPLETE | proof2why3/from_sexp.py::_project_app | STUCK-PH | PYVAL | PH | This expression has type int, but is expected to have type string
    INCOMPLETE | proof2why3/from_sexp.py::project_constr | STUCK-PH | RECORD | PH | This expression has type PyCSL_Program._union_project_constr_3, but is expected to have type array.Array.array
    INCOMPLETE | proof2why3/normalize.py::_alpha_rename | STUCK-PH | INTSTR | PH | This expression has type int, but is expected to have type string
    INCOMPLETE | proof2why3/normalize.py::_expand_anon_binders | STUCK-PH | EXT | PH | This expression has type int, but is expected to have type string
    INCOMPLETE | proof2why3/normalize.py::_nat_to_int_with_sidecond | STUCK-PH | NESTED |  | This expression has type int, but is expected to have type string
    INCOMPLETE | proof2why3/parser.py::lex | STUCK-LOCATE | RIPPLE |  | unbound function or predicate symbol 'toks' /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semantic.py:1708: U
    INCOMPLETE | proof2why3/parser.py::normalize_surface | STUCK-PH | STRM | PH | This expression has type string, but is expected to have type int /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | proof2why3/parser.py::parse_type_expr | STUCK-PH | EXC > RECORD > OPTREC |  | This expression has type int, but is expected to have type PyCSL_Program.term /home/fabrice/git/pycsl-plan/src
    INCOMPLETE | proof_axiom_allowlist.py::parse_rocq_assumptions_block | STUCK-PH | TUPLE |  | This expression has type (int, array.Array.array int @rho), but is expected to have type (int, int)
    INCOMPLETE | pycsl.py::_build_soundness_report | STUCK-PH | INTSTR | PH | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | pycsl.py::_dispatch_provers | STUCK-LOCATE | NESTED > GENEXP |  | unbound function or predicate symbol '_record_is_valid' /home/fabrice/git/pycsl-plan/src/pycsl/core_ir_semanti
    INCOMPLETE | pycsl.py::_json_goal_records | STUCK-PH | GENEXP > LISTSTR |  | This expression has type array.Array.array int @rho, but is expected to have type int /home/fabrice/git/pycsl-
    INCOMPLETE | pycsl.py::_make_temp_mlw_path | STUCK-PH | TUPLE | PH | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | pycsl.py::_parse_goal_blocks | STUCK-PH | LISTSTR | PH | This expression has type array.Array.array int @rho, but is expected to have type int /home/fabrice/git/pycsl-
    INCOMPLETE | pycsl.py::_parse_why3_json | STUCK-PH | MUTRECV | PH | This expression has type array.Array.array int @rho, but is expected to have type int /home/fabrice/git/pycsl-
    INCOMPLETE | pycsl.py::_resolve_runtime_config | STUCK-PH | WITH-AS > EXT | PH | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | pycsl.py::_run_pipeline | STUCK-REPEAT | SIG > MUTRECV > HETERO | PH | heterogeneous list literal (contains a str element mixed with other element types) has no faithful WhyML `arra
    INCOMPLETE | pycsl.py::_sha256_file | STUCK-PH | WITH-AS > MUTRECV > EXT | PH | This expression has type int, but is expected to have type string /home/fabrice/git/pycsl-plan/src/pycsl/core_
    INCOMPLETE | pycsl.py::main | STUCK-LOCATE | WITH-AS > MUTRECV > EXC |  | [whyml-emit]: 'main' constructs an object whose `__init__` / `__post_init__` can raise `_ContractSyntaxError` 
    SKIP-CORRECTNESS | frontend/pure_ast.py::_set_ctx | SKIP-CORRECTNESS |  |  | 
    SKIP-DNC-EFFECT | audit_proof_reverify.py::_cache_root | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | audit_proof_reverify.py::_cache_store | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | audit_proof_reverify.py::_coqc_version | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | audit_proof_reverify.py::_lean_version | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | audit_proof_reverify.py::verify_lean_file | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | audit_proof_reverify.py::verify_rocq_file | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | frontend/ir_inline.py::apply_inline_globals | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | proof2why3/extract.py::extract_lean_statements | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | proof2why3/extract.py::extract_rocq_statements | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | proof2why3/extract_lean_meta.py::extract_lean_statements_meta | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | proof2why3/sertop.py::extract_via_sertop | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | proof2why3/sertop.py::run_sertop_batch | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | proof2why3/sertop.py::sertop_version | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | pycsl.py::_check_rocq_proofs | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | pycsl.py::_generate_rocq_obligations | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | pycsl.py::_run_proofs | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | pycsl.py::_run_vacuity_gate | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | pycsl.py::_run_why3_prove | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-EFFECT | pycsl.py::_why3_typecheck | SKIP-DNC-EFFECT |  |  | 
    SKIP-DNC-RAISEONLY(vacuous) | frontend/pure_ast.py::_Parser.error | TCOK0 |  |  | 
    SKIP-DNC-RAISEONLY(vacuous) | frontend/pure_ast.py::_Parser.unsupported | TCOK0 |  |  | 
    SKIP-NESTED-IN-TRUSTED | Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._sig_val_from_let._hdr_name | SKIP-NESTED-IN-TRUSTED |  |  | 
    SKIP-NESTED-IN-TRUSTED | Module6_WhyMLTranspiler.py::Module6_WhyMLTranspiler._transpile_modular._emit_funcs | SKIP-NESTED-IN-TRUSTED |  |  | 
    SKIP-NESTED-IN-TRUSTED | core_ir_semantic.py::_returns_literal_none.walk | SKIP-NESTED-IN-TRUSTED |  |  | 
    SKIP-NESTED-IN-TRUSTED | pycsl.py::_dispatch_provers._finalize | SKIP-NESTED-IN-TRUSTED |  |  | 
    SKIP-NESTED-IN-TRUSTED | pycsl.py::_run_proofs._gate_vacuity_then_succeed | SKIP-NESTED-IN-TRUSTED |  |  | 
    SKIP-NESTED-IN-TRUSTED | pycsl.py::_run_vacuity_gate._probe_one | SKIP-NESTED-IN-TRUSTED |  |  | 
    SKIP-NESTED-IN-TRUSTED | pycsl.py::_run_vacuity_gate._probe_one._is_false_goal | SKIP-NESTED-IN-TRUSTED |  |  | 
    SKIP-NOLIVE | module6_whyml/expr_ghost_collections.py::GhostCollectionOpsMixin._e | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/expr_ghost_spec_ops.py::GhostSpecOpsMixin._e | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/expr_ghost_spec_ops.py::GhostSpecOpsMixin._expr_to_whyml_string_ctx | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/expressions.py::ExpressionEmissionMixin._add_abstract_op | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/statements.py::StatementEmissionMixin._add_abstract_op | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/statements.py::StatementEmissionMixin._coerce_to_int | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/statements.py::StatementEmissionMixin._e | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/statements.py::StatementEmissionMixin._expr_to_whyml | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/statements.py::StatementEmissionMixin._expr_to_whyml_string_ctx | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/statements.py::StatementEmissionMixin._handle_return_stmt | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/statements.py::StatementEmissionMixin._is_emit_ir_expr | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/statements.py::StatementEmissionMixin._is_string_expr | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/statements.py::StatementEmissionMixin._maybe_emit_no_exception_assert | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/statements.py::StatementEmissionMixin._mutex_inv_application | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/statements.py::StatementEmissionMixin._resolve_dotted_signature | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/statements.py::StatementEmissionMixin._track_collection_metadata | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._add_abstract_op | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._coerce_to_int | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._expr_to_whyml | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._is_string_expr | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._match_pattern_cond | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._seq_init_expr | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._stmts_to_whyml | SKIP-NOLIVE |  |  | 
    SKIP-NOLIVE | module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._to_bool | SKIP-NOLIVE |  |  | 
    UNMEASURED(port crash) | frontend/pure_ast.py::_decode_escapes | CRASH |  | PH | This expression has type string, but is expected to have type int
    UNMEASURED(port crash) | module6_whyml/expressions.py::ExpressionEmissionMixin._expr_to_whyml | CRASH | MUTRECV |  | `_symtab.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abs
```

## Re-measurement at HEAD — ch23 (gen #37)

At `e7fa92f3` (count 453). Plan steps 9 INTSTR (8), 10 RECORD (5), 11 TUPLE (4): all 17 still
`\trusted`. Each ported verbatim (`bin/port-one-mirror-body.py`, `--replace` for the DIFFERS rows
`_specialize_decl`, `_py_expr_fstring`, `_fold_blocks`; live signature tried where the mirror's
differed) into a scratch copy, emitted `--no-proof --keep-mlw` through `heavy.sh`, and the emitted
WhyML read. **0 of 17 honest; no seam built.** As in ch20-ch22 the census family was the FIRST
type error. Once re-ported, every chain hits a value-model gap (AST-node / Dict[str,Any] /
Optional-tuple), and the one TC-clean body is a facade.

```
    marker                                        first blocker at HEAD -> verdict
  step 9 INTSTR
    _ContractParser._parse_happy_targets          REFUSED route #252 (unannotated `name` into the `str` slot of
                                                  `HappyProperty`). With `name: str`: L3-tc `region_lo = pycsl_none`
                                                  -- live passes None into the non-Optional `ExprIR` field (the
                                                  live dataclass is lying), and target/formula/secret are
                                                  Optional[...] fields erased to int. OPTREC. SKIP
    AbstractOpsMixin._advance_past_referenced_    L3-tc `Array.length (!p)` on int: `d.split()` -> 0-ary
      axiom_decls                                 `d_split_0 ()`; the loop iterates `pycsl_getattr_default_<h>`
                                                  (mixin `self` is `int`, no fields); `" ".join(genexp)` ->
                                                  `join_1 (any int)`; `s.startswith(..)` -> `s_startswith_1 (any
                                                  int)`. STRM+GETATTR+GENEXP, FACADE underneath. SKIP
    CrossCheckResult.diagnostic                   L3-tc `int_to_string ("PASS"/"FAIL")` (str ternary in an
                                                  f-string). Below it: `self.pairwise.items()` (a property) is the
                                                  0-ary `self_pairwise_items_0 ()`, `label, ok` are `any int`.
                                                  Iterating a Map has no key domain. DICT. SKIP (the 7 field
                                                  lines ARE honest)
    ExpressionEmissionMixin._call_bytes_methods   L3-tc: `st.lstrip("!")` -> receiver-dropped `st_lstrip_1 <h>`
                                                  : int where a string is wanted; `any(st.startswith(p) for p in
                                                  _ARR)` -> `any_1 (any (array int))`. STRM+GENEXP. SKIP
    ExpressionEmissionMixin._emit_contract_       L3-tc `subscript_get !imported_sigs func_name`:
      logic_symbol                                `getattr(self,"_imported_inductive_sigs",{})` is NOT a mirror
                                                  field -> 0-ary default; local import. GETATTR (undeclared
                                                  self-field). SKIP
    _specialize_decl (DIFFERS)                    REFUSED: `spec.pop(..)` (MUTRECV, dict local); also
                                                  `copy.deepcopy`, nested Dict[str,Any] walk. SKIP
    _Unparser.visit_MatchStar                     L3-tc `name := "_"`: `node.name` is `get_name node : int`
                                                  (int-erased AST param), so the rebinding to "_" is a str. A
                                                  hash seam would emit `int_to_string (hash "_")`, which is
                                                  unfaithful. AST-node value model. SKIP
    _sexp_parse                                   REFUSED: `tokens.pop(0)` (MUTRECV on a PARAMETER, caller-
                                                  visible = MUTPARAM); self-recursive. SKIP
  step 10 RECORD
    Module3_Weaver._subscript_read_site           L3-tc `base := sub.subscript_value` (emit_ir into the int-hoisted
                                                  local); `base.value.id` getattr-erased; both returns are dict
                                                  literals -> `any_map ()` (return FACADE). RECORD+DICT. SKIP
    PyCSLToJSONEmitter._py_expr_fstring (DIFFERS) REFUSED route #263 (self-recursion through a method). With
                                                  `#@ \diverges`: L3-tc `_py_expr_to_ir self (get_value !v)`, since
                                                  `expr: ast.JoinedStr` is int-erased (no JoinedStr/FormattedValue
                                                  node type, unlike the typed `py_dictcomp_node` siblings), and the
                                                  return `{"type":"FString","parts":parts}` -> `IrOther "FString"`
                                                  (parts DROPPED = FACADE). RECORD (AST node + IrFString ctor). SKIP
    ExpressionEmissionMixin._handle_ifexpr_expr   L3-tc `_is_arr_var_1 node.ifexprexpr_body`: the nested
                                                  `def _is_arr_var(_d: Any)` is lifted with an int param;
                                                  getattr(self,"_option_record_param_classes",{}); `.to_dict()`
                                                  Dict[str,Any] reads. NESTED+GETATTR+DICT. SKIP
    _find_construct_idx                           TC-CLEAN, screen 4/4 GREEN, but FACADE by the decisive
                                                  mutation test: the MutInd guard `any(isinstance(x,tuple) and
                                                  x and x[0]=="MutInd" for x in _flatten_tuples(head))` -> `any_1
                                                  (any (array int))` (the string "MutInd" occurs nowhere in the
                                                  emission); `int(tail)` -> `!tail` (ValueError path erased);
                                                  `payload` is int-erased while every sibling in from_sexp.py
                                                  reads the certified `pyval`. With the live `-> Optional[int]`:
                                                  L3-tc (union vs int at the self-call). Honest route = the pyval
                                                  walker (`generic_fold.py`) plus an Optional[int] arm, `int(atom)`
                                                  with ValueError, and `any(genexp)` over a `list pyval` sibling.
                                                  PYVAL/GENEXP. SKIP
    _find_coqc                                    (mirror body already = live) L3-tc: local `import shutil as
                                                  _sh; _sh.which("coqc")` -> receiver-dropped `_sh_which_1 <h> :
                                                  int` against the `Optional[str]` union (the shutl stub is an
                                                  int model). EXT. SKIP
  step 11 TUPLE
    _Harvester._fold_blocks (DIFFERS)             L3-tc `hdr := _match_block_hdr ..`: the trusted callee is
                                                  `: unit` (unannotated). With `-> Optional[Tuple[str,str]]` it
                                                  stays `unit`, and the union arm erases the tuple to `int`;
                                                  then `kw, name = hdr` (narrow + unpack) and `_WITH_HDR.match(..)
                                                  .group(1)` (re, EXT). OPTREC/TUPLE. SKIP
    _namedtuple_check_call                        L3-tc `subscript_get_t3 nt_arities !callee`: `nt_arities: dict`
                                                  is `map`, and its values are (int, List[str], set) tuples. DICT/
                                                  TUPLE value model. SKIP
    _check_gt4_polymorphic_recursion (DIFFERS)    mirror and live signatures give the same L3-tc
                                                  `info["type_params"][0]["name"]` (nested Dict[str,Any] -> int
                                                  vs string); then `_ast.walk` generator and an Optional-tuple
                                                  callee. DICT. SKIP
    _Parser._slice                                L3-tc `let () = (start, py_end)`: the nested target `(r1, c1),
                                                  (r2, c2) = start, end` over `pytuple_int_int` record params is
                                                  mis-lowered. With it hand-split, three more blockers follow:
                                                  `self._lines` is not a mirror `_parser` field (getattr-erased;
                                                  adding it moves the `_parser` record = whole pure_ast re-proof);
                                                  and `self._lines[r1-1][c1:c2]` / `[..][c1:]` (a str slice of a
                                                  subscripted element) -> `any (array int)` / `any int`.
                                                  TUPLE+GETATTR+STR-SLICE, 3 emitter seams + 1 model change =
                                                  not small. SKIP
```

**Recurring blockers (17 markers, counted wherever they occur in the measured chain):**
(1) the AST-node / undeclared-attribute value model (int-erased `node.x`, AST-typed params,
`getattr(self, <undeclared>, d)`): 8 (vms, srs, pef, ecl, apr, hie, psl, fci-payload);
(2) Dict[str,Any] value model (nested reads, `.items()` iteration, dict-literal returns -> `any_map`
/ `IrOther`): 7 (gt4, ncc, ccd, srs, spd, pef, hie); (3) Optional[record/tuple] and tuple slots: 4
(pht, ffb, psl, ncc); (4) `any()/join(genexp)` erasure: 3 (fci, cbm, apr); (5) receiver-dropped str
methods: 2 (apr, cbm); (6) in-place `.pop`: 2 (spd, sxp); (7) EXT (`shutil.which`, `re`): 2 (fcq,
ffb). `\diverges` (route #263) shows up twice (pef, sxp) and is never the wall by itself.

No seam was landed. The only small seam in sight, a hashed string literal into an int-hoisted
local (visit_MatchStar), would emit `int_to_string (hash "_")`, which is unfaithful. Emits/logs:
session scratchpad `ch23/meas-*.{log,mlw}`, `ch23/screen-fci.log`.

## Re-measurement at HEAD — ch24 (gen #37)

At `333194e7` (count 453). Plan steps 5 MUTRECV (4), 12 UNBOUND (1), 13 GENEXP (6), 14 SET (3),
15 SYNTAX (2): 16 markers, of which 15 are still `\trusted` (`_Unparser.visit_Module` was
already converted in gen #36 ch17, `b4dccfbe`). Each one was ported verbatim
(`bin/port-one-mirror-body.py`, `--replace` for the DIFFERS/SAME rows), emitted `--no-proof
--keep-mlw` through `heavy.sh`, and its WhyML read. Where the first blocker was a refusal or a
single statement, that statement was neutralised in the scratch copy (or the live signature was
tried) to see the next blocker. **1 of 15 honest.** It was converted on two small gated seams
(`1880170f`, 453 -> 452).

```
    marker                                        first blocker at HEAD -> verdict
  step 5 MUTRECV
    Module6._wrap_call_with_callee_raises_assert  REFUSED: `active.update(..)` (local set). With that neutralised:
      (DIFFERS)                                   L3-tc, `writes { self._abstract_ops, .. }` on the receiver-dropped
                                                  self-call stub `self__render_callee_condition_3` uses UNMANGLED field
                                                  names (emitter bug, fail-closed). Below that, DICT facade:
                                                  `self._module_func_raises.get(..)` is `int`, `r.get("exc_type")` ->
                                                  `r_get_1 <h>`, `self.ir.get(..)` + getattr. SKIP
    _inject_functions (DIFFERS)                   REFUSED: `existing.add(..)`. Then `ir_data["functions"].insert(0, ..)`
                                                  is a write into the caller's dict (MUTPARAM). With all three neutralised
                                                  and the live signature it is TC-clean but a FACADE: `existing =
                                                  set_comp 0`, `ir_data` never read. SKIP
    _Unparser.visit_Module                        not `\trusted` at HEAD (converted gen #36 ch17). n/a
    struct_format.parse_format                    REFUSED: `slots.extend(..)`. Then L3-tc: the Optional[StructFormat]
                                                  union is raised in an exception, and its record arm is mutable.
                                                  Underneath, `_TOKEN_RE.match` / `m.group(1)` are receiver-dropped (re,
                                                  EXT) and `int(count_str)` is `!count_str`. OPTREC+EXT. SKIP
  step 12 UNBOUND
    pycsl._run_audit_mode (SAME)                  REFUSED route #252: `getattr(args,"reverify_proofs",False)` flows into
                                                  the `bool` slot. With it neutralised: L3-tc on an f-string hash.
                                                  Underneath, `argparse.Namespace`/`Path` are `int`, `report.extend`
                                                  drops its write (EXT/GETATTR facade). SKIP
  step 13 GENEXP
    _Harvester._build (DIFFERS)                   REFUSED: `self._flat.append(..)` (self-field append). It also
                                                  self-recurses into `tgt.child_suites`, a recursive MUTABLE record (as
                                                  `_emit_suite`, ch21). RECORD/L. SKIP
    PyCSLWeaver.visit_For                         L3-tc: `setattr_3 node ..` takes an `int`, but `node` is now the typed
                                                  `py_for` record. `contracts` is `int` (`iter_length`/`iter_get`). The
                                                  `node.csl_*` stores are `any int`, and the trusted callee
                                                  `_attach_loop_contracts` carries `assigns \nothing` over an in-place
                                                  mutator (ch22 suspicion). AST-node model. SKIP
    PyCSLWeaver.visit_While                       same as visit_For (`py_while`). SKIP
    AbstractOpsMixin._find_abstract_val_insert_idx CONVERTED (453 -> 452, `1880170f`). L3-tc: `enumerate(out)` over the
                                                  `List[str]` param became the opaque `enumerate_1 out : int` (`i = any
                                                  int`, `line.strip()` -> 0-ary `line_strip_0 ()`). Two gated seams fix it.
                                                  (1) `_enumerate_seq_recv`: a FORMAL flat `List[str]` param iterates as
                                                  `Array.length p` / `p[!idx]`. (2) `_content_string_method`:
                                                  `s.startswith((p1,..,pn))` becomes a `let`-bound disjunction of the
                                                  faithful `str_startswith_op`. It was the opaque polymorphic
                                                  `startswith_2`. Added `#@ loop invariant 0 <= insert_idx` + `#@ loop
                                                  variant \length(out) - insert_idx` on the inner while. Whole-file proof
                                                  rc=0, 20 Valid.
    PreambleEmissionMixin._emit_module_globals    REFUSED: `self._module_global_classes.pop(..)`. Then L3-tc:
      (DIFFERS)                                   `g["name"]` (Dict[str,Any] element `int`) into `whyml_ident : string`.
                                                  DICT. SKIP
    get_source_segment                            REFUSED route #252 (unannotated `source` into `_splitlines_no_ff`). With
                                                  `source: str`: REFUSED `lines.insert(0, ..)`. Underneath are the AST
                                                  attributes (`node.end_lineno`, ...) and `.encode()[a:b].decode()`. SKIP
  step 14 SET
    ConcurrencyChecker.check (DIFFERS)            REFUSED: `self._thread_entries.add(..)`. Then L3-tc: `self.warnings = []`
                                                  is `array int` against `array concurrencywarning`. Underneath:
                                                  `getattr(module, 'csl_*')`, `ast.walk`. LISTSTR/RECORD + AST. SKIP
    Module6._build_callee_no_exception_summary    L3-tc: `set((f.get("contracts") or {}).get(..) or [])` ->
      (SAME)                                      `contracts_get_2 <h> (any int)` (receiver-dropped) `or Array.make`.
                                                  DICT facade. SKIP
    FunctionEmissionMixin._mixin_dep_pseudo_      L3-tc: `func.get(..) or []` -> `func_get_1 <h>` vs `Array.make`.
      functions (DIFFERS)                         DICT facade. SKIP
  step 15 SYNTAX
    monomorphize._collect_instantiations          SYNTAX: `any int` inside a `variant` term (a program expression in a
      (DIFFERS)                                   logic position) built from `func_get_2 <h> (any int)`. That is the
                                                  receiver-dropped DICT facade underneath. SKIP
    pure_ast.unparse                              SYNTAX: `_Unparser()` emits the empty record literal `{  }` (the class
                                                  state is the opaque `_pyobj_state`). `unparser.visit(..)` then resolves
                                                  to a fresh stub `unparser_visit_1_c24883`, not the `diverges`
                                                  `_unparser__visit`. See the suspicion below. SKIP
```

**Recurring blockers (15 measured markers, counted wherever they occur in the chain):**
(1) in-place mutator refusals (local / self-field / param `.add/.update/.extend/.append/.pop/
.insert`): 7 (wrc, ijf, psf, hbd, emg, gss, cck). In every case another blocker sits underneath.
(2) Dict[str,Any] value model (receiver-dropped `.get`, element `int`): 6 (wrc, ijf, emg, bcn, mdp,
cin). (3) AST-node / undeclared-attribute model: 5 (wvf, wvw, gss, cck, ram). (4) record/Optional
record (mutable union arm, recursive mutable record, `List[record]` init): 3 (psf, hbd, cck).
(5) ill-formed WhyML from the emitter: 3 (wrc unmangled `writes`, cin `any` in a variant, unp empty
record ctor). (6) EXT (`re`, argparse/pathlib): 2 (psf, ram). (7) route #252: 2 (ram, gss).
(8) enumerate / tuple-startswith erasure: 1 (fav, fixed). As in ch20-ch23, the census family
was only the FIRST error. The MUTRECV refusals are fail-closed and never the last wall.

**Seams landed (`1880170f`).** Both are corpus-inert (root 1792/1792 and pyref 2186/2186 0 MOVED/
GONE/APPEARED). The mirror sweep moved 1/53 (abstract_ops, declared, re-proved). Witness 3060
PASS (L3-tc fails at base). Twins 3061/3062 FAIL on the false postcondition. Fast planes 61/61.
`check-trust-blast-radius` MAX_TRUST_DEPENDENT 401 -> 402 is the NAMED relabel of the converted
function (it calls the still-trusted `_advance_past_referenced_axiom_decls`). The aggregate is
invariant at 805, so MAX_TRUSTED_OR_DEPENDENT was tightened 828 -> 805.

**Next cheap candidate (outside steps 5/12-15):** `audit_proof_reverify._split_rocq_print_assumptions`
is TC-clean at HEAD with the enumerate seam. Its core read, however, is a facade: the 2-arg
`stdout.find(marker, pos)` lowers to the receiver-dropped `stdout_find_2 (str_hash_op marker)
pos`. The outer `while` also has no variant. It needs a faithful `find(sub, start)` op (result
-1 or >= start) and a `#@ loop variant \length(stdout) - pos`. That is an M seam, not built here.
`proof_axiom_allowlist.parse_rocq_assumptions_block` (TUPLE return slot) and
`Module6._sig_val_from_let` (NESTED) stay blocked.

**Suspicions / emitter defects (not chased).** (a) `pure_ast.unparse`: the method call on a
locally constructed `_Unparser()` resolves to a fresh `val unparser_visit_1_c24883` with no
`diverges` and no `writes`. The real `_unparser__visit` is `diverges` + `writes {_pyobj_state}`.
If the empty-record SYNTAX error were ever fixed, termination of a diverging method would be
assumed. Emit: session scratchpad `ch24/meas-unp.mlw`. (b) A self-call stub `writes` clause with
unmangled record field names (`self._abstract_ops` for
`module6_whymltranspiler__abstract_ops`): ill-typed, so fail-closed. `ch24/meas-wrc2.mlw`.
(c) The late `use string.String` pull in `abstract_ops` scans only lines starting with
`ensures`. `str_startswith_op`'s `String.` dependency sits on a continuation line, so a file whose
only string use is a `startswith` on a non-param string fails L3-tc with "unbound
String.length" (fail-closed). Repro: `ch24/wt/3060_gen37_ch24_enumerate_str_param_tuple_startswith.py`
(the pre-edit witness, which has no `str` param). Logs/emits: session scratchpad `ch24/`.
