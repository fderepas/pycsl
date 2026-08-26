# Census artifact: live-body trusted-stub ranking (2026-08-26, HEAD a406f7e1)

Produced by the driver in the 96h window, to re-test the claimed "COMPREHENSIVE AUTONOMOUS
FLOOR". It is a **measure-first artifact**: the campaign has repeatedly lost these and re-derived
them (see "raw-ast-predicate CENSUS ARTIFACT recovered"), so it is committed.

## Method (reproducible)

1. Enumerate every `#@ \trusted` mirror stub by AST **def**, not by grep line: walk
   `src/self-annotate/src/**/*.py`, and for each `FunctionDef` scan upward over the contiguous
   `#@`/decorator/blank block for `#@ \trusted`. Gives **632** stubs.
   (The canonical grep count is **675**; the gap is `\trusted` occurring in `#@`-adjacent
   comment/docstring lines. Both are strictly decreasing; the def count is the real stub population.)
2. **CRITICAL — read the LIVE body, never the mirror body.** A trusted mirror stub carries a
   PLACEHOLDER body (`return []`, `return None`, `pass`); triaging it reads nothing. Resolve each
   stub's qualname against `src/pycsl/<same rel path>` and take *that* source segment. 611 of 632
   resolve (21 are mirror-only helpers / renamed).
3. Scan each live body for hard-blocker features: file-IO, subprocess, `eval`/`exec`/`literal_eval`,
   `re.*`, `getattr`/`setattr`/`hasattr`, nested `def`, `while`, self-state mutation.

## Headline result

**266 of 611** live-matched stubs carry **no** hard-blocker feature.

## Hard-blocker distribution (live-matched stubs)

| blockers | stubs |
|---|---|
| `(none)` | 266 |
| `while` | 81 |
| `selfmut` | 52 |
| `io` | 42 |
| `getattr` | 40 |
| `getattr,selfmut` | 21 |
| `nesteddef` | 17 |
| `selfmut,while` | 8 |
| `io,subproc` | 8 |
| `getattr,io` | 7 |
| `getattr,nesteddef` | 7 |
| `subproc` | 5 |
| `io,while` | 5 |
| `regex` | 5 |
| `nesteddef,selfmut` | 4 |
| `nesteddef,while` | 3 |
| `getattr,while` | 3 |
| `getattr,selfmut,while` | 3 |
| `getattr,nesteddef,selfmut,while` | 3 |
| `eval,getattr` | 2 |

## Why this reopens the ladder

Every prior `no_cheap_remaining` verdict in this campaign was produced by a **file-scoped** probe —
Module2_Parser, Module3_Weaver, Module5_IREmitter, `expressions.py`, `pure_ast.py`, `ir_scanner.py`,
the for-over-string cluster. **No probe ever covered the `proof2why3/` package or
`ConcurrencyChecker.py`.** Those files hold 28 + 3 no-hard-blocker candidates and are unmeasured.
A floor established by file-scoped probes is a floor over the probed files, not over the tree.

## No-hard-blocker candidates by file
(`frontend/pure_ast.py` = the documented raw-ast UNTYPED-PARAM boundary, and
`proof_axiom_allowlist.py` = the ledger allowlist itself, are excluded from the candidate ranking.)

| file | clean | of trusted |
|---|---|---|
| `frontend/pure_ast.py` | 128 | 219 |  *(EXCLUDED)*
| `pycsl.py` | 13 | 29 |
| `frontend/Module3_Weaver.py` | 12 | 30 |
| `frontend/monomorphize.py` | 12 | 15 |
| `frontend/Module2_Parser.py` | 10 | 23 |
| `proof2why3/canonical.py` | 10 | 12 |
| `frontend/Module5_IREmitter.py` | 9 | 34 |
| `module6_whyml/expressions.py` | 8 | 36 |
| `frontend/ir_inline.py` | 6 | 7 |
| `module6_whyml/preamble.py` | 6 | 19 |
| `proof2why3/parser.py` | 5 | 15 |
| `core_ir_semantic.py` | 4 | 4 |
| `proof_axiom_allowlist.py` | 4 | 4 |  *(EXCLUDED)*
| `frontend/Module1_Ingestor.py` | 4 | 12 |
| `proof2why3/sertop.py` | 4 | 10 |
| `proof2why3/from_sexp.py` | 4 | 4 |
| `audit_proof_reverify.py` | 3 | 13 |
| `frontend/ir_resolve.py` | 3 | 15 |
| `frontend/ConcurrencyChecker.py` | 3 | 6 |
| `Module6_WhyMLTranspiler.py` | 2 | 13 |
| `audit_proof.py` | 2 | 14 |
| `proof2why3/crosscheck_ir.py` | 2 | 6 |
| `proof2why3/from_lean_json.py` | 2 | 3 |
| `module6_whyml/functions.py` | 2 | 10 |
| `module6_whyml/statements.py` | 2 | 14 |
| `ir_schema.py` | 1 | 1 |
| `proof2why3/crosscheck.py` | 1 | 5 |
| `module6_whyml/identifiers.py` | 1 | 2 |
| `module6_whyml/struct_format.py` | 1 | 4 |
| `module6_whyml/expr_ghost_spec_ops.py` | 1 | 2 |
| `module6_whyml/stmt_control_flow.py` | 1 | 2 |

## Ranked candidates, smallest live body first (top 60, exclusions removed)

| live LOC | file | qualname | soft features |
|---|---|---|---|
| 2 | `frontend/Module5_IREmitter.py` | `PyCSLToJSONEmitter._py_op_to_str` | — |
| 2 | `module6_whyml/struct_format.py` | `StructFormat.arity` | — |
| 2 | `proof2why3/parser.py` | `Token.__repr__` | fstring |
| 2 | `proof2why3/sertop.py` | `SertopSession.__enter__` | — |
| 2 | `proof2why3/sertop.py` | `SertopSession.__exit__` | — |
| 2 | `pycsl.py` | `_record_answer` | — |
| 3 | `frontend/ConcurrencyChecker.py` | `ConcurrencyChecker._walk_body` | — |
| 3 | `frontend/ir_inline.py` | `_Inliner._fresh` | fstring |
| 3 | `module6_whyml/expressions.py` | `ExpressionEmissionMixin._e` | — |
| 3 | `pycsl.py` | `_json_goal_records` | comprehension |
| 3 | `pycsl.py` | `_synthesize_legacy_text` | — |
| 4 | `audit_proof.py` | `AuditReport.extend` | — |
| 4 | `frontend/ConcurrencyChecker.py` | `ConcurrencyChecker._check_function` | — |
| 4 | `frontend/Module5_IREmitter.py` | `Module5_IREmitter.generate_json` | — |
| 4 | `proof2why3/sertop.py` | `parse_sexp` | — |
| 5 | `frontend/Module1_Ingestor.py` | `Module1_Ingestor.process` | — |
| 5 | `frontend/Module2_Parser.py` | `_ContractParser.parse` | — |
| 5 | `frontend/Module2_Parser.py` | `Module2_Parser.parse_node_contracts` | — |
| 5 | `pycsl.py` | `_make_temp_mlw_path` | — |
| 6 | `audit_proof_reverify.py` | `ReverifyReport.ok` | — |
| 6 | `frontend/Module5_IREmitter.py` | `PyCSLToJSONEmitter._get_mutex_invariant_ir` | — |
| 7 | `frontend/Module1_Ingestor.py` | `_Harvester._emit_suite` | — |
| 7 | `frontend/Module2_Parser.py` | `Module2_Parser.parse_contract` | fstring, raise |
| 7 | `proof2why3/parser.py` | `_Parser.expect` | fstring, raise |
| 8 | `audit_proof_reverify.py` | `ReverifyReport.summary` | fstring, comprehension |
| 8 | `frontend/ConcurrencyChecker.py` | `ConcurrencyChecker.summary` | fstring |
| 8 | `frontend/Module1_Ingestor.py` | `_Harvester._normalize_leading` | comprehension |
| 8 | `frontend/Module2_Parser.py` | `_ContractParser._parse_trusted` | — |
| 8 | `proof2why3/parser.py` | `_Parser.parse_implication` | — |
| 8 | `pycsl.py` | `_record_key` | — |
| 9 | `module6_whyml/preamble.py` | `PreambleEmissionMixin._mutex_inv_application` | fstring |
| 10 | `audit_proof_reverify.py` | `_to_cache_payload` | — |
| 10 | `frontend/Module2_Parser.py` | `_ContractParser._parse_assumes` | — |
| 10 | `frontend/Module3_Weaver.py` | `Module3_Weaver.process` | — |
| 10 | `frontend/Module5_IREmitter.py` | `PyCSLToJSONEmitter._py_expr_fstring` | isinstance |
| 10 | `frontend/Module5_IREmitter.py` | `PyCSLToJSONEmitter._py_stmt_raise` | isinstance |
| 10 | `frontend/monomorphize.py` | `_rewrite_call_sites` | comprehension |
| 11 | `Module6_WhyMLTranspiler.py` | `Module6_WhyMLTranspiler._shared_use_lines` | comprehension |
| 11 | `frontend/Module3_Weaver.py` | `PyCSLWeaver._attach_loop_contracts` | isinstance |
| 11 | `module6_whyml/preamble.py` | `PreambleEmissionMixin._emit_opaque_class_aliases` | fstring |
| 11 | `proof2why3/crosscheck.py` | `CrossCheckResult.diagnostic` | dictiter, fstring |
| 12 | `frontend/Module1_Ingestor.py` | `_match_block_hdr` | fstring |
| 12 | `frontend/ir_resolve.py` | `_inject_functions` | comprehension |
| 12 | `module6_whyml/expr_ghost_spec_ops.py` | `GhostSpecOpsMixin._handle_proj_expr` | fstring |
| 12 | `module6_whyml/expressions.py` | `ExpressionEmissionMixin._emit_metatype_tags` | fstring |
| 13 | `core_ir_semantic.py` | `_typeddict_check_subscript` | fstring, isinstance |
| 13 | `core_ir_semantic.py` | `_namedtuple_check_subscript` | fstring, isinstance |
| 13 | `proof2why3/canonical.py` | `_camel_to_snake` | — |
| 14 | `frontend/Module3_Weaver.py` | `Module3_Weaver._extract_happy_properties` | dictiter, comprehension, isinstance |
| 14 | `frontend/monomorphize.py` | `_rewrite_annotations` | dictiter, comprehension, isinstance |
| 14 | `module6_whyml/preamble.py` | `PreambleEmissionMixin._emit_preamble_no_exception_predicates` | fstring |
| 15 | `frontend/Module3_Weaver.py` | `Module3_Weaver._parse_extracted_contracts` | — |
| 15 | `frontend/Module3_Weaver.py` | `Module3_Weaver._collect_self_call_sites` | fstring, isinstance |
| 15 | `module6_whyml/expressions.py` | `ExpressionEmissionMixin._static_width` | dictiter |
| 15 | `pycsl.py` | `_function_body_eqs` | — |
| 16 | `core_ir_semantic.py` | `_namedtuple_check_call` | fstring, raise, isinstance |
| 16 | `frontend/Module3_Weaver.py` | `Module3_Weaver._subscript_read_site` | fstring, isinstance |
| 16 | `frontend/monomorphize.py` | `_rewrite_subscript_calls_in_stmt` | dictiter, comprehension, isinstance |
| 16 | `module6_whyml/expressions.py` | `ExpressionEmissionMixin._match_pattern_cond` | fstring, comprehension |
| 16 | `module6_whyml/preamble.py` | `PreambleEmissionMixin._emit_preamble` | — |

## Known traps in this list (do not waste a cycle)

- `Module5_IREmitter :: _py_op_to_str` = `self._PY_OP_MAP.get(type(op), "?")` — `type(op)` reflection
  is the getattr/type-dispatch wall.
- Pure single-call forwarders (e.g. `expressions.py :: _e` = `return self._expr_to_whyml(ir, lr)`)
  were classified in prior windows as **vacuous-by-design**; Gate C rejects a facade. Only take one
  if the emitted body provably descends real modeled structure.
- A callee that stays `\trusted` is NOT a blocker: it emits as an abstract `val` with `ensures True`,
  which the caller may legitimately consume.

## Variant-bundle (Act/Complete/Disjoint/ForExpand) sub-census — lesson (p), census-FIRST

Of the 632 stubs, exactly **9** have a live body mentioning `Act`/`Complete`/`Disjoint`/`ForExpand`:

| file | qualname | variant | live LOC | assessment |
|---|---|---|---|---|
| `frontend/Module3_Weaver.py` | `PyCSLWeaver._desugar_for` | ForExpand | 19 | **best candidate** — ForExpand discrimination + field reads + `range(lo,hi)` loop (variant `hi - m`) + a raise; callees `_const_int`/`_subst_var` stay trusted (vals) |
| `frontend/Module3_Weaver.py` | `PyCSLWeaver._init_function_csl_fields` | Act | 37 | not previously named in the backlog — unmeasured |
| `frontend/Module3_Weaver.py` | `PyCSLWeaver._desugar_acts` | Act | 47 | cert-ORTHOGONAL blockers confirmed by reading the live body: dynamic attribute assignment (`e.act_name = c.name`), a string-keyed node-map dict comprehension (`guards`), and a **3-element** heterogeneous tuple return (the annotation `Tuple[List, List]` is stale — the body returns `out, acts_meta, entry_cps`) |
| `frontend/Module2_Parser.py` | `_ContractParser._parse_contract` | Complete | 59 | vacuous forwarder (prior classification) |
| `frontend/Module2_Parser.py` | `_ContractParser._parse_act_block` | Act | 18 | CERTIFIED-BOUNDARY: seq-emit_ir proof-cost, 3 independent measurements |
| `frontend/Module2_Parser.py` | `_ContractParser._parse_for_block` | ForExpand | 22 | same proof-cost boundary |
| `frontend/Module5_IREmitter.py` | `PyCSLToJSONEmitter._build_function_ir` | Act | 318 | TCB giant |
| `frontend/ir_resolve.py` | `resolve_imports` | Disjoint | 60 | filesystem IO |
| `module6_whyml/functions.py` | `FunctionEmissionMixin._emit_function` | Disjoint | 1885 | TCB giant |

**Verdict on the "larger multi-variant certificate bundle" lever:** building the full
Act/Complete/Disjoint/ForExpand variant certificate would unblock **at most `_desugar_for` and
possibly `_init_function_csl_fields`** — every other member is held by a blocker the certificate does
not touch. So the bundle is not worth building *as a bundle*. The correct, much cheaper decomposition
is a **ForExpand-only** cert extension targeting `_desugar_for` (19 live lines), following the banked
`csl_clause` / `pyast_stmt` cert-extension pattern. `_init_function_csl_fields` is measured next.

