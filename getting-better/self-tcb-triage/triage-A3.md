# Triage A3 — front-end pipeline (`src/pycsl/frontend/`)

READ-ONLY triage of `\trusted` stubs across the 5 assigned front-end mirror files.
Classification against `leaf-conversion-recognizers.md`. No conversions/edits/commits.

**Actual-stub reconciliation:** the brief's per-file numbers (162 total) count raw `\trusted`
string occurrences, which include each mirror's header-docstring line plus (in Module2) ~6
`\trusted` mentions inside `CSLNode` dataclass docstrings. The real stub-directive counts are:
Module2_Parser **85**, Module3_Weaver **39**, Module1_Ingestor **17**, ConcurrencyChecker **7**,
import_classifier **5** → **153 real stubs**.

## The one structural fact that decides this whole group

The front end is a **hand-written recursive-descent parser + an `ast.NodeVisitor` weaver + AST-walking
analyzers**. Its entire currency is unmodeled recursive value kinds:
- `pure_ast` **Python-AST node** records (`FunctionDef`, `With`, `Assign`, `Name`, …) with dynamic
  `csl_*` attributes set/read via `getattr`/`setattr`/`hasattr`;
- Module-2 **`CSLNode` variant ADT** (~100 constructors, `CSLNode`-payloaded: `Requires`, `BinOp`,
  `Forall`, `Var`, …) built + `isinstance`-dispatched under **mutual recursion**;
- `_Tok` **token records** in a `List[_Tok]` cursor inside a plain (non-`@mutable_state`) class.

A verbatim port with the fixed `#@ requires True / ensures True / assigns <frame>` shape **cannot even
lower** for the overwhelming majority — this is exactly rubric item-3 (Token/AST-node value modeling,
`match`/variant dispatch, mutual recursion over unmodeled structure, external callback). It is NOT a
`needs-recognizer` (one bounded emitter feature); it is `hard-architectural`. Only **2** genuine cheap
wins and **3** single-feature `needs-recognizer` stubs exist in the entire 153.

---

## frontend/Module2_Parser.py  (85 stubs)  — [delegated read of live body]

| stub(s) | bucket | reason |
|---|---|---|
| `Module2_Parser.__init__` | **trivial-leaf** | body is `pass`; fixed shape type-checks+discharges, no feature. The only free −1 in the file. |
| token helpers — `cur`,`peek`,`advance`,`at_op`,`at_name`,`at_bs`,`at_eof`,`accept_op`,`expect_op`,`expect_name`,`expect_bs`,`_err`,`_try` (13) | **hard-architectural** | traffic in `_Tok` records over `array _Tok` in an unmodeled mutable-state class; + varargs `*vals`+membership (`at_op/at_name/at_bs`), `Optional[_Tok]` return (`accept_op`), external-callback param (`_try`), custom-exception raise + f-string `!r` (`_err/expect_*`). |
| recursive-descent `CSLNode` builders — `parse`,`_parse_*` (52) + `_csl_to_str`,`_mk_in` | **hard-architectural** | construct/return `CSLNode` variants over the ~100-arm recursive ADT under mutual recursion; several `isinstance`-dispatch + raise. |
| string/list-returning helpers — `_parse_qualname`,`_parse_dotted_path`,`_parse_dotted_path_list`,`_parse_act_names`,`_parse_opt_except`,`_parse_mixin_type/param/params/method_sig`,`_parse_mutex_expr_str` (10) | **hard-architectural** (clean return, token-infra-gated) | return `str`/`List[str]` (modelable alone) but every body calls `expect_name`/`accept_op` → gated on the `_Tok`/`_ContractParser` record infra; first to fall once that exists. |
| `_grab_reviewer_id` | **hard-architectural** | `re.match` regex on `self.source` + slicing — regex modeling on top of token infra. |
| lexer — `_lex_contract`,`_Tok.__init__`,`_Tok.__repr__`,`_ContractParser.__init__` (4) | **hard-architectural** | `_TOKEN_RE.match` regex loop building `List[_Tok]`; `_Tok` record ctor; f-string `!r`; mutable-state tuple-unpack. |
| `parse_contract`,`parse_node_contracts` (2) | **hard-architectural** | construct `_ContractParser`, call `.parse()`→`CSLNode`, exception translation, `List[CSLNode]` accumulation. |

Counts: trivial-leaf **1**, needs-recognizer **0**, hard-architectural **84**, floor **0**.

## frontend/Module3_Weaver.py  (39 stubs)  — [delegated read of live body; spot-check confirmed]

Every stub is an `ast.NodeVisitor` method or AST/CSL-walker that does `isinstance` dispatch over
`pure_ast`/`CSLNode` variants, dynamic `getattr`/`setattr` of `csl_*` attrs, recursive AST descent,
node construction, reflective dataclass deep-copy (`_is_dc`/`_dc_fields`/`_dc_replace`/`copy.deepcopy`),
or `self.parser_module.*` external callbacks. A `--no-proof` spot-check on the single most favorable
case (`_const_int`: one `isinstance(node,Number)` + `node.value` read) **leaked at type-check** —
empirically no cheap-recognizer path.

| family | # | blocker |
|---|---|---|
| `visit_*` NodeVisitor dispatch | 6 | mutate `csl_*` on AST node + CSLNode-variant dispatch + `generic_visit` |
| `pure_ast` pattern-match predicates/descriptors | 4 | AST-node variant ADT + `isinstance` dispatch |
| recursive AST-tree collectors (`_collect_*_sites`,`_check_protect_aliasing`) | 6 | mutual recursion over unmodeled AST + `iter_child_nodes`/`walk` |
| CSL-node construct/desugar (`_desugar_*`,`_act_guard`,`_const_int`,`_canonical_*`) | 4 | build + dispatch `CSLNode` variant ADT |
| reflective dataclass deep-copy substitution (`_subst_var`,`_subst_csl_param`,…) | 2 | `_is_dc`/`_dc_fields`/`_dc_replace`/`setattr` recursion (rubric §1 "IR deep-copy — DEFER") |
| CSLNode variant-dispatch attach/extract (`_dispatch_function_contracts`,`_extract_*`,…) | 9 | `isinstance` chains over Decl variants mutating node fields |
| external `parser_module` callback / orchestration / dynamic getattr (`process`,`_happy_predicate`,`_synthesize_selfcomp`,`_parse_extracted_contracts`,`_expand_happy_properties`,`_region_bound_str`,`__init__`×2) | 8 | external-callback + `ast.parse`/construction + dynamic reflection + class-record |

Counts: trivial-leaf **0**, needs-recognizer **0**, hard-architectural **39**, floor **0**.

## frontend/Module1_Ingestor.py  (17 stubs)  — [read live body directly; _clean spot-check ✓]

| stub | bucket | reason |
|---|---|---|
| `_clean` | **trivial-leaf** | `comment_text[2:].strip()` — string slice + no-arg `.strip()`. **Spot-checked: L3-tc ✓** with the ported body. Free −1. |
| `_indent_width` | **needs-recognizer:substring-`in`-string membership + computed string slice** | `"\t" in lead` substring-membership + `body[:len(body)-len(body.lstrip())]` computed-bound slice; also raises `PyCSLParseError`. |
| `Module1_Ingestor.__init__` | **needs-recognizer:class-as-`@mutable_state @dataclass` record** | stores one `str` field; plain class → self-field routes opaque (rubric §7 per-file prereq). |
| `_match_block_hdr` | **hard-architectural** | iterates `_BLOCK_HDRS`, `rx.match`, `m.group`, `m.re.groups`, f-string — regex `.match` + Match-object modeling. |
| `process` | **hard-architectural** | `ast.parse` + list-comp over `ast.comments` (comment records) + calls `_Harvester(...).run`. |
| `_Harvester.__init__` | **hard-architectural** | lambda-key `sorted` over comment records + many List/Optional fields on a plain class. |
| `_make` | **hard-architectural** | `type(node).__name__` dispatch over Python-AST nodes, `getattr(decorator_list)`, `_Target` construction. |
| `_build` | **hard-architectural** | recursion over AST + `_Target` construction, mutates `self._flat`/`self._cur_class`. |
| `run` | **hard-architectural** | orchestrator: `_build`+`sort`+`_assign`+`_emit_suite` + `PyCSLContract` construction. |
| `_assign` | **hard-architectural** | `import bisect` + comment-record `.lineno`/`.indent`/`.text` + `_dec_ranges` tuple scan. |
| `_normalize_leading` | **hard-architectural** | calls trusted regex stub `_match_block_hdr`/`_fold_blocks` (non-leaf ordering). |
| `_fold_clauses` | **hard-architectural** | while-loop over `List[str]` + calls `_indent_width` + f-string `PyCSLParseError` raise. |
| `_fold_blocks` | **hard-architectural** | `_WITH_HDR.match` regex + calls `_match_block_hdr`/`_indent_width`/`_fold_clauses` + f-string raises. |
| `_Target.__init__` | **hard-architectural** | stores an AST `node` field + `child_suites: List[_Target]` on a `__slots__` plain class. |
| `_emit_suite` | **hard-architectural** | recursion over `List[_Target]` records. |
| `_emit_target` | **hard-architectural** | reads `_Target` record fields + `PyCSLContract` construction. |
| `_emit_block_footer` | **hard-architectural** | reads `_Target.footer` + `PyCSLContract` construction. |

Counts: trivial-leaf **1**, needs-recognizer **2**, hard-architectural **14**, floor **0**.

## frontend/ConcurrencyChecker.py  (7 stubs)  — [read live body directly]

| stub | bucket | reason |
|---|---|---|
| `__init__` | **hard-architectural** | stores AST `tree` + `Dict[str,Optional[str]]` + `Optional[List]` + `Set[str]` fields, kw-only args, on a plain class. |
| `check` | **hard-architectural** | `getattr(module,'csl_shared_decls')`, decl records, `ast.walk`+`isinstance(FunctionDef)`, strict raise. |
| `_check_function` | **hard-architectural** | reads `func.body` (AST), `set()` literal, calls `_walk_body`. |
| `_walk_body` | **hard-architectural** | `Set[str]` param, mutual recursion with `_walk_stmt` over AST. |
| `_walk_stmt` | **hard-architectural** | `isinstance` dispatch over `With/If/While/For/Assign/AugAssign`, `getattr csl_*`, set-union, recursion. |
| `_warn_if_unprotected` | **hard-architectural** | `Dict`-membership + `Set`-membership (`held`) + `%`-format + `ConcurrencyWarning` record construct. |
| `summary` | **hard-architectural** | iterate `List[ConcurrencyWarning]` records, f-string over record fields, `"\n".join`. |

Counts: trivial-leaf **0**, needs-recognizer **0**, hard-architectural **7**, floor **0**.

## frontend/import_classifier.py  (5 stubs)  — [read live body directly]

| stub | bucket | reason |
|---|---|---|
| `classify` | **needs-recognizer:set/frozenset-param membership (+ `str.split(sep,maxsplit)[0]`)** | `top = module_name.split(".",1)[0]`; `module_name in deny_list or top in stubs`; returns string constants (string-ITE supported). Two bounded features. |
| `_stub_set` | **hard-architectural** | `Path.is_dir`/`.iterdir`/`.stem`/`.suffix` filesystem reflection + set-comprehension. |
| `collect_imports` | **hard-architectural** | `ast.walk` + `isinstance(Import/ImportFrom)` + `alias` records + tuple accumulation. |
| `any_function_trusted` | **hard-architectural** | `ast.walk` + `isinstance(FunctionDef)` + `getattr(csl_trusted)`. |
| `check_imports` | **hard-architectural** | orchestrator: calls `_stub_set`/`collect_imports`/`classify`/`any_function_trusted` + raise. |

Counts: trivial-leaf **0**, needs-recognizer **1**, hard-architectural **4**, floor **0**.

---

## Group totals (153 real stubs)

| bucket | count |
|---|---|
| trivial-leaf (batch-convertible NOW) | **2** |
| needs-recognizer | **3** |
| hard-architectural | **148** |
| floor | **0** |

**trivial-leaf batch (2):** `Module2_Parser.__init__` (`pass`), `Module1_Ingestor._clean`
(`s[2:].strip()`, spot-checked L3-tc ✓).

## Feature fan-out (this group)

The group is dominated by a few deep item-3 architectural features (NOT bounded §2 recognizers). The
`needs-recognizer` rows are the only single-feature pickups.

| feature | #stubs | example stubs |
|---|---|---|
| **AST-node value model** (`pure_ast` variant ADT + `isinstance` dispatch + dynamic `csl_*` get/set) | ~60 | all Module3 `visit_*`/collectors (39), Module1 `_make`/`_build`/`process`/`_assign` (~8), ConcurrencyChecker `check`/`_walk_stmt` (7), import_classifier `collect_imports`/`any_function_trusted` (2) |
| **`CSLNode` recursive ADT (~100 ctors) + construction + mutual recursion** | ~57 | `_parse_expr`, `_parse_atom_bs`, `_parse_contract`, `_csl_to_str`, `parse_node_contracts` |
| **`_Tok` record + `_ContractParser` as `@mutable_state @dataclass`** | ~29 | `cur`, `peek`, `expect_name`, `_lex_contract`, `_ContractParser.__init__` |
| **regex modeling (`re.match`/compiled `.match` + Match object)** | ~6 | `_match_block_hdr`, `_fold_blocks`, `_grab_reviewer_id`, `_lex_contract` |
| **reflective dataclass deep-copy (`_is_dc`/`_dc_fields`/`_dc_replace`)** | 4 | `_subst_var`, `_subst_csl_param`, `_consolidate_module_concurrency`, `_extract_mixin_directives` |
| **external module callback (`parser_module.*`)** | 5 | `_parse_extracted_contracts`, `_happy_predicate`, `_synthesize_selfcomp`, `_expand_happy_properties`, `process` |
| **set modeling (`Set`/`frozenset` params/locals + membership)** | ~4 | `classify`, `_warn_if_unprotected`, `_walk_stmt`, `_stub_set` |
| needs-recognizer:substring-`in`-string + computed string slice | 1 | `_indent_width` |
| needs-recognizer:class-as-`@mutable_state @dataclass` record | 1 | `Module1_Ingestor.__init__` |
| needs-recognizer:set/frozenset-param membership (+ `str.split(sep,maxsplit)`) | 1 | `classify` |

## Bottom line

The front-end pipeline is essentially a floor-adjacent **hard-architectural block**: 148/153 stubs stay
trusted until PyCSL gains **AST-node / CSLNode variant value modeling** (the universal blocker), with
the `_Tok`/`_ContractParser` record model and CSLNode ADT as the two large Module2 sub-features and the
`parser_module` external callback as a second Module3 feature. Only **2 free −1** (`Module2_Parser.__init__`,
`Module1_Ingestor._clean`) are batch-convertible now; **3** more (`_indent_width`, `Module1_Ingestor.__init__`,
`classify`) each unlock behind one named bounded feature. No floor-only stubs — the mutual-recursion
expression ladder becomes the natural floor candidate only *after* the ADT/token features lift the
item-3 ceiling.
