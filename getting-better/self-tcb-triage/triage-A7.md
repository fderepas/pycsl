# Triage A7 — proof2why3 pipeline + proof-audit

READ-ONLY static triage. Method: read each LIVE body under `src/pycsl/`, match against the
recognizer stack / known-gaps. No conversions, no commits. Spot-checks judged unnecessary — the
blocking signals (custom variant ADT, heterogeneous `Any`-tree recursion, regex engine, subprocess)
are unambiguous and none are in-stack.

## IMPORTANT count correction (docstring false-positive)
Every mirror file's module docstring literally contains the phrase
``annotated `#@ \trusted reviewer: pycsl-self-annotate` `` — so a `grep -c '\trusted'` over each
mirror **over-counts by exactly 1**. The assignment counts are grep counts; **real stub count =
assigned − 1**. Confirmed against function extraction (parser 19→18 fns, canonical 15→14, etc.).
`__init__.py` "1" is **0 real stubs** (docstring-only module, no functions).

Real stub totals: parser 18, canonical 14, sertop 12, ir 12, from_sexp 12, crosscheck_ir 11,
crosscheck 7, normalize 6, from_lean_json 5, extract 3, emit_why3 3, extract_lean_meta 2,
__init__ 0, audit_proof 15, audit_proof_reverify 12  → **~132 real stubs** (147 grep-with-docstring).

## The single dominant blocker
This whole subsystem is built on the **`Term` variant ADT** (`ir.py`): a 9-arm sum type
`Var | IntLit | BoolLit | App | BinOp | UnaryOp | Forall | Exists | Unsupported`, realized as 9
frozen dataclasses, dispatched by `isinstance` chains, constructed/traversed by **mutual recursion**,
returning custom-union values. PyCSL has no sum/variant type model, no `isinstance`-over-variant
dispatch, and no recursion over such a value. That one architectural gap gates ~55 stubs directly or
as a build target. Layered on top: heterogeneous nested **s-expression (`Any` tuples)** and **Lean
JSON (`Dict[str,Any]`)** tree recursion, a full **regex engine** (`re.sub/compile/match/split` +
`lambda`/`re.Match` replacers), **subprocess** dependence (coqc/lake/sertop/shutil), **set-valued**
returns, **`ast` module** reflection, char-level **string builders / `yield` generators**, and
hashlib/json/tempfile/pathlib. None are bounded recognizers.

---

## parser.py  (18 stubs)
| stub | bucket | reason |
|---|---|---|
| normalize_surface | hard-architectural | regex engine (`re.sub` fixpoint, `_UNICODE_OPS`/prefix `.replace` loops) |
| Token.__repr__ | needs-recognizer:f-string `!r` repr-conversion | `f"{kind}({value!r})"` |
| lex | hard-architectural | builds `List[Token]` (list-of-record) via while-loop over `s[i]`, `.isspace/.isdigit/.isalpha`, slicing |
| _Parser.__init__ / peek / take / expect (4) | hard-architectural | parser-state record over a `List[Token]`; `Optional[Token]` index return; `raise SyntaxError` |
| parse_expr, parse_quant, parse_implication, parse_disjunction, parse_conjunction, parse_comparison, parse_arith_add, parse_arith_mul, parse_atom_application, parse_atom, parse_type_expr (11) | hard-architectural | recursive-descent that **constructs the `Term` variant** (Forall/Exists/App/BinOp/Var/…), mutual recursion, `isinstance` |

parser: 0 trivial, 1 needs-recognizer, 17 hard.

## canonical.py  (14 stubs)
| stub | bucket | reason |
|---|---|---|
| substitute, _expand_nat_to_int, _alpha_rename, alpha_normalize, _flip_comparisons, _dedup_arrow_chain, _ac_normalize, _sort_arrow_hypotheses, _flatten_foralls, _normalize_names, _iff_app_to_binop, canonicalize (12) | hard-architectural | `isinstance(t, Var/App/BinOp/Forall/…)` dispatch, recursive rebuild of `Term`, `raise TypeError` |
| _camel_to_snake, _normalize_type_string (2) | hard-architectural | regex engine (`re.sub`, `re.split`) |

canonical: 0 trivial, 0 needs-recognizer, 14 hard.

## sertop.py  (12 stubs)
| stub | bucket | reason |
|---|---|---|
| sertop_available, sertop_version, run_sertop_batch, type_of_batch, extract_via_sertop (5) | hard-architectural | subprocess (`Popen`/`run`/`communicate`), `shutil.which`, env, filesystem |
| _sexp_tokens | hard-architectural | `yield` **generator** tokenizer over `s[i]` |
| _sexp_parse, parse_sexp | hard-architectural | recursion building **nested heterogeneous `object` tuples**, `tokens.pop(0)`, `raise ValueError` |
| _process_sertop_line, _extract_stmid | hard-architectural | `isinstance(x, tuple)` on `Any` s-expr + `Dict[int,object]` mutation |
| __enter__, __exit__ (2) | hard-architectural | context-manager protocol on a `@dataclass` holding a `Popen` field |

sertop: 0 trivial, 0 needs-recognizer, 12 hard.

## ir.py  (12 stubs)
| stub | bucket | reason |
|---|---|---|
| Var.pp | trivial-leaf* | `return self.name` (str field) — *prereq: frozen `@dataclass` renders as record |
| BoolLit.pp | trivial-leaf* | `"true" if self.value else "false"` (bool→string ITE, supported) — *record prereq |
| Unsupported.pp | trivial-leaf* | `f"<UNSUPPORTED: {self.reason}>"` (f-string over str field) — *record prereq |
| IntLit.pp | needs-recognizer:str(int-field) | `str(self.value)` (int→string; str(x)-as-string may already cover) |
| App.pp, BinOp.pp, UnaryOp.pp, Forall.pp, Exists.pp (5) | hard-architectural | f-string **recursing** `a.pp()` over `Term` children + `' '.join(gen)` |
| mk_arrow_chain, flatten_arrow_chain | hard-architectural | `isinstance`-loop constructing/deconstructing `Term` arrow chains |
| free_vars | hard-architectural | **`set`-valued** return + recursive variant `isinstance` dispatch (gap §5-#2) |

ir: 3 trivial*, 1 needs-recognizer, 8 hard.

## from_sexp.py  (12 stubs)
| stub | bucket | reason |
|---|---|---|
| _walk_kername, _walk_modpath, _const_name, _full_const_path, _find_kername_components, _ind_short_name, _construct_indices, _find_construct_idx, _flatten_tuples, _binder_name, _project_app, project_constr (12) | hard-architectural | recursion over **heterogeneous nested `Any` tuples** (Coq Constr s-expr) with `isinstance(x, tuple)` + index dispatch; several **construct the `Term` variant**; `try/except (ValueError,TypeError)` |

from_sexp: 0 trivial, 0 needs-recognizer, 12 hard.

## crosscheck_ir.py  (11 stubs)
| stub | bucket | reason |
|---|---|---|
| all_agree, pairwise, any_unsupported, all_present_unsupported, provers_agree, registry_skipped, diagnostic (7) | hard-architectural | `@dataclass` properties over `Optional[Term]` fields: `==` on variant values, `isinstance(c, Unsupported)`, `.pp()`, three-valued `Optional[bool]` |
| _load_axiom_registry | hard-architectural | `ast.parse`/`ast.walk`/`ast.literal_eval` reflection over preamble.py |
| _preprocess_whyml | hard-architectural | regex (`re.sub`) |
| crosscheck_file_ir | hard-architectural | orchestration: glob, subprocess extractors, dict/set build, parse→canonicalize |
| main | hard-architectural | CLI: `sys.argv`, `print`, `hash()`, `sys.exit` |

crosscheck_ir: 0 trivial, 0 needs-recognizer, 11 hard.

## crosscheck.py  (7 stubs)
| stub | bucket | reason |
|---|---|---|
| _module_namespace_of | **trivial-leaf** | `return ""` (constant string) — cleanest batch win in the group |
| all_agree | needs-recognizer:list-comp truthiness-filter + all() over str fields | `[n for n in norms if n]` + `all(n==present[0])` |
| pairwise | needs-recognizer:dict-literal with bool values from str-eq | returns `Dict[str,bool]` literal |
| diagnostic | hard-architectural | f-string list build + `self.pairwise.items()` iteration + `.join` |
| _load_axiom_registry | hard-architectural | `ast.parse`/`walk`/`literal_eval` + file IO |
| crosscheck_file | hard-architectural | glob, extractor subprocess calls, dict/set orchestration |
| main | hard-architectural | CLI print/argv/sys.exit + `sum(...)` comprehension |

crosscheck: 1 trivial, 2 needs-recognizer, 4 hard.

## normalize.py  (6 stubs)
| stub | bucket | reason |
|---|---|---|
| normalize_prover_output, _strip_all_parens, _nat_to_int_with_sidecond, _expand_anon_binders, _alpha_rename, normalize_whyml_axiom (6) | hard-architectural | pure **regex engine** pipeline: `re.sub/compile/match`, `lambda m:`/`re.Match.group`, `count=`, fixpoint loops |

normalize: 0 trivial, 0 needs-recognizer, 6 hard.

## from_lean_json.py  (5 stubs)
| stub | bucket | reason |
|---|---|---|
| _strip_const_name | needs-recognizer:module-constant `List[(str,str)]` lookup→str | `for src,dst in _PREFIX_STRIPS: if name==src: return dst` |
| _body_references_bvar_0, _linearize_app, _is_ofnat_lit, project_to_ir (4) | hard-architectural | recursion over **Lean `Dict[str,Any]` Expr tree** (`.get("kind")` dispatch) + **`Term` variant** construction |

from_lean_json: 0 trivial, 1 needs-recognizer, 4 hard.

## extract.py  (3 stubs)
| stub | bucket | reason |
|---|---|---|
| extract_rocq_statements, extract_lean_statements | hard-architectural | subprocess `coqc`/`lake`, `tempfile.NamedTemporaryFile`, filesystem unlink, string block parsing |
| _split_rocq_check_output | hard-architectural | multi-line stdout state-machine into `Dict[str,str]` (index arithmetic over `lines`) |

extract: 0 trivial, 0 needs-recognizer, 3 hard.

## emit_why3.py  (3 stubs)
| stub | bucket | reason |
|---|---|---|
| _pp | hard-architectural | precedence-aware recursive pretty-print over the whole `Term` variant |
| ir_to_whyml_axiom_body | hard-architectural | calls `_pp` (Term-variant dependent) |
| contains_unsupported | hard-architectural | recursive `isinstance`-over-`Term` returning bool |

emit_why3: 0 trivial, 0 needs-recognizer, 3 hard.

## extract_lean_meta.py  (2 stubs)
| stub | bucket | reason |
|---|---|---|
| lean_meta_available | hard-architectural | external filesystem `.is_file()` on `Path` (opaque) |
| extract_lean_statements_meta | hard-architectural | subprocess `lake`, `json.loads`, dict build over `Dict[str,Dict[str,Any]]` |

extract_lean_meta: 0 trivial, 0 needs-recognizer, 2 hard.

## __init__.py  (0 real stubs)
Docstring-only module; the assigned "1" is the docstring `\trusted` phrase. Nothing to classify.

## audit_proof.py  (15 stubs)
| stub | bucket | reason |
|---|---|---|
| AuditReport.exit_code | needs-recognizer:record list-field truthiness→int | `1 if self.failures else 0` |
| AuditReport.extend | needs-recognizer:list.extend across record fields | `self.passes.extend(other.passes)` ×3 |
| _default_rocq_dir, _default_lean_dir (2) | needs-recognizer:pathlib `Path` model (`/` join + `.stem`/`.parent`) | `py_file.parent / f"{py_file.stem}.proofs"/…` |
| _extract_directives | hard-architectural | `read_text`, `enumerate(splitlines())`, `.split(None,3)`, builds `List[_Directive]` (list-of-record) |
| _strip_rocq_comments, _strip_lean_comments (2) | hard-architectural | char-level nesting-depth **string builder** (`out: List[str]` + `"".join`, `text[i]` while-loop) |
| _parse_rocq_file, _parse_lean_file, _index_proofs_dir, _index_proofs_dir_by_file (4) | hard-architectural | **`Set[str]`-valued** returns, module/namespace stacks, filesystem `iterdir`, dict maps |
| _audit_one_prover | hard-architectural | subprocess reverify, dicts, cross-record orchestration |
| audit_rocq, audit_lean, audit_both (3) | hard-architectural | `Path.resolve`, delegate + `AuditReport.extend` |
| print_report | hard-architectural | print loops / IO |

audit_proof: 0 trivial, 4 needs-recognizer, 11 hard.

## audit_proof_reverify.py  (12 stubs)
| stub | bucket | reason |
|---|---|---|
| ReverifyReport.ok | hard-architectural | `all(allowed for (_,allowed,_) in self.qualname_results)` — tuple-destructure over `List[tuple[str,bool,List[str]]]` field |
| ReverifyReport.summary | hard-architectural | f-string + `sum(1 for (_,ok,_) in …)` over tuple-list field |
| _cache_root, _sha256_file, _cache_key, _cache_load, _cache_store (5) | hard-architectural | `hashlib.sha256`, `json`, filesystem mkdir/read/write |
| _coqc_version, _lean_version (2) | hard-architectural | subprocess |
| verify_rocq_file, verify_lean_file (2) | hard-architectural | massive subprocess + tempfile + record build |
| _split_rocq_print_assumptions | hard-architectural | `str.find` scan loop building `Dict[str,str]` over qualnames |
| _to_cache_payload | hard-architectural | dict/json literal from tuple-list destructure |

audit_proof_reverify: 0 trivial, 0 needs-recognizer, 12 hard.

---

## Per-bucket counts (this group, real ~132 stubs)
| bucket | count |
|---|---|
| trivial-leaf | **4** (crosscheck._module_namespace_of; ir Var.pp / BoolLit.pp / Unsupported.pp — the 3 ir ones carry a frozen-`@dataclass`→record prereq) |
| needs-recognizer | **8** (repr `!r`; str(int-field); pathlib Path ×2; list-field truthiness; list.extend; const-tuple-lookup; list-comp/dict-bool ×2 counted as 2 → parser1+ir1+audit_proof4+from_lean_json1+crosscheck2 = 9, ~8–9 scattered singletons) |
| hard-architectural | **~119** (the wall) |
| floor | **0** genuine D2/recursion-leaf floor (subprocess/shutil opacity classed hard-architectural external-dependence, not floor) |

## Top feature fan-out (architectural blockers — what would unblock the most)
| feature | #stubs (primary) | example stubs |
|---|---|---|
| **`Term` variant/sum-type ADT** (9-arm union, isinstance dispatch, recursive construct/traverse) | ~41 direct + ~17 as build-target = **~58** | canonical.* (12), parser.parse_* (11), ir App/BinOp/…pp+free_vars+mk/flatten (8), emit_why3.* (3), crosscheck_ir properties (7), from_sexp/from_lean_json projectors build it |
| **Heterogeneous `Any` s-expr / JSON tree recursion** (`isinstance(x,tuple/dict)`, `.get`, nested index) | **~19** | from_sexp.* (12), from_lean_json project_to_ir/_linearize_app/_is_ofnat_lit/_body_references_bvar_0 (4), sertop _sexp_parse/_process_sertop_line/_extract_stmid (3) |
| **Regex engine** (`re.sub/compile/match/split`, `lambda`/`re.Match`) | **~11** | normalize.* (6), canonical _camel_to_snake/_normalize_type_string (2), parser.normalize_surface (1), crosscheck_ir._preprocess_whyml (1) |
| **Subprocess / external-tool opacity** (coqc/lake/sertop/shutil) | **~15** | sertop (5), extract (2), extract_lean_meta (2), reverify _coqc/_lean_version+verify_* (4), audit_proof._audit_one_prover |
| **`Set[str]`-valued returns** (gap §5-#2 set-local) | **~5** | audit_proof _parse_rocq_file/_parse_lean_file/_index_proofs_dir (3), ir.free_vars, _index_proofs_dir_by_file(dict) |
| **`ast` module reflection** (`ast.parse/walk/literal_eval`) | **2** | crosscheck._load_axiom_registry, crosscheck_ir._load_axiom_registry |
| **Char-level string builder / `yield` generator** | **~3** | audit_proof _strip_rocq/lean_comments (2), sertop._sexp_tokens |
| **hashlib/json/tempfile/pathlib** | **~8** | reverify cache helpers (5), extract tempfile, audit_proof _default_*_dir (2) |

## Trivial-leaf (batch-convertible now): **4** — but only crosscheck._module_namespace_of (`return ""`)
is unconditionally clean. The 3 ir.py pp leaves (Var/BoolLit/Unsupported) are string-typed
non-recursive returns that convert IFF the frozen `@dataclass` renders as a record in the mirror
(cheap per-class prereq; the recursive pp/mk/flatten/free_vars siblings still need the full Term ADT).

## Bottom line for the orchestrator
proof2why3 + proof-audit is **NOT a productive squeeze-loop frontier**. ~90% hard-architectural,
gated on deep modeling features PyCSL lacks by design in this layer: a variant/sum-type system,
heterogeneous recursive tree types (`Any` s-expr / JSON), a regex engine, and subprocess opacity —
not bounded recognizers. Expected yield from a pass here: ~1 clean win (`_module_namespace_of`) plus
maybe 3 record-prereq ir.py pp leaves; everything else is deferred behind ≥1 architectural feature.
