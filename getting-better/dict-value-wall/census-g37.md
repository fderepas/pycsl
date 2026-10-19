# Dict[str, Any] value wall — census (gen #37, ch26)

Read-only evidence for a wall report. Measured 2026-10-19 at `b9dc767e` (count 451 -> 450 after the
ch26 `_record_answer` conversion), worktree `pycsl-g37ch26`.

## Method

* **Population.** The 423 line-prefix `\trusted` markers of `getting-better/trusted-reasons.tsv`
  at `b9dc767e` (422 after ch26). For each one, the LIVE twin under `src/pycsl/` was resolved by
  qualname (399 resolve; 24 have no live twin).
* **Which markers hit the wall.** "In-chain" means the marker's measured blocker chain
  (`chain-plan-g36.md`, appendix) contains the `DICT` family or the related `PYVAL` family.
  "First" means that family is the chain's first blocker. "Only" means the chain holds nothing
  but `DICT`/`PYVAL` (and `RIPPLE`). "Latent" means the chain does not reach `DICT` because it
  stopped earlier (on MUTRECV, NESTED, ...), but the live body reads literal keys off a dict all
  the same.
* **Per-body static census** (`census.py`, `cluster.py` in this directory, plain `ast`, no
  emission). For each live body it records:
  * the dict KEYS read through `d["k"]`, `d.get("k")` and `d.get("k", D)`;
  * a heuristic VALUE SHAPE for each read: from the default literal, or from the consumer
    (compared to a str/int literal, iterated, chained `.get`, passed to `len`/`whyml_ident`,
    truthiness);
  * the OPERATIONS used: subscript, `.get` with/without a default, `.get(<non-literal key>)`,
    `.get(..) or <D>`, chained `.get`, `"k" in d`, `.items()/.keys()/.values()`, dict
    literal / IR-node literal built or returned, dict comprehension, `d["k"] = v`,
    `.update/.setdefault/.pop`, and `isinstance(x, dict|list)` generic walks.

  The shapes are heuristic, and the numbers below are read counts, not proofs.
* **Probes.** Three retype probes and the ch26 seam were measured by emission (`--no-proof`
  through `heavy.sh`), so they are measurements, not projections.

## Headline

```
  trusted rows                                        423
  DICT (or PYVAL) in the measured chain                97   (91 DICT, 8 PYVAL, overlap 2)
  ... DICT/PYVAL is the FIRST blocker                   41   (37 DICT-first)
  ... DICT/PYVAL(/RIPPLE) is the ONLY family            19   (11 of them complete chains)
  latent (literal-key dict reads, DICT not in chain)    86
  trusted with literal-key dict reads in live body     151
  trusted with `Dict[str, Any]` in the live signature  111
```

## Ranked table — shape cluster -> markers -> nearest certified model -> gap

Ranked by first-wall count, then by in-chain + latent. "only" counts complete and incomplete
chains together; the number in brackets is complete chains only.

| # | shape cluster (what the body reads) | in-chain | **first** | **only** | latent | nearest EXISTING model | gap (why it does not already apply) |
|---|---|---|---|---|---|---|---|
| 1 | **N — IR expr/stmt node read**: dispatch on `node["type"]` (str, 92 reads), then project `name` (str/Optional), `value` (sub-node **or** int/str payload), `args` (list of nodes), `func`, `object`, `attr`, `field`, `left/right`, `index`, `receiver` | 19 | **13** | 4 (2) | 13 | **emit_ir ADT** (`preamble._emit_exprir_theory`, `_KIND_DISCRIMINANT`, `_EMIT_IR_PROJ`; Rocq/Lean record-valued cert) | (a) **Annotation gate.** The ADT fires on `ExprIR`/`StmtIR`/`IRNode` annotations, but these mirror signatures say `Dict[str, Any]` / `int`. The mirror annotation is the modelling layer, so a retype is legal. MEASURED: `_tag_of_value` is TC-clean after the single retype `x_ir: "ExprIR"`, with no emitter change. (b) **Per-kind heterogeneous `value`.** `Number.value` is an int and `Attribute.value` is a sub-node, but `"value"` projects to the sub-node `svalue_of`. MEASURED: `_emit_bitwise_or_power` retyped is L3-tc on `right_ir["value"] < 0` (`svalue_of` vs int) and `isinstance(left_ir.get("value"), int)` becomes `any bool`. (c) Keys outside the projection table, the stmt family (never built, lesson 8), and IR-node CONSTRUCTION (`{"type": ..}` literals, 15 markers). |
| 2 | **X — no literal-key read in its own body**: the DICT error comes from a value passed IN or OUT (a callee typed `Dict[str, Any]`, an unannotated param, a `Dict[Tuple[str,str],str]` rename map, `_funcs` iterated as a dict) | 18 | **9** | 6 (3) | — | none needed in the body itself | **Signature typing / RIPPLE.** These close only when their neighbours' signatures move to a modelled type (hval / emit_ir / a typed `map`). Several also carry EXT underneath (`re.match` in `_rewrite_annotation_str`). Not a value-model gap of its own. |
| 3 | **P — IR program / decl record read**: `ir["functions"]` (list of dicts), `func["name"]`, `func.get("contracts") or {}` -> `requires/ensures` lists, `type_params`, `type_decls`, `symbol_table` (nested `Dict[str,str]`), `kind`/`self_type` (str), `fields`, `constructors`, plus writes `func["symbol_table"] = new_st` | 30 | **7** | 3 (1) | 35 | **hval** (`Dict[str, PyVal]` -> `map string (option hval)`; `HStr/HInt/HArr/HMap/HNode`, `pairs_get`, `hstr_of`, `hval_truthy`, `hval_len`, `hval_str_mem`; cert `Phase2f_PyVal.v` / `PyVal.lean`) | (a) **Annotation gate.** hval needs the Name `PyVal` (`Module5._m5_get_dict_value_type`); `Any` gives no `dict_value_types`, so the dict is int-erased. (b) MEASURED, `_rewrite_annotations` retyped `ir_data: Dict[str, PyVal]`: the next blocker is `for func in ir_data.get("functions", [])`, i.e. **no for-loop over an `HArr`** (`iter_length` wants int). (c) **In-place writes into a nested hval** (`func["symbol_table"] = ..`, `.setdefault(..).append`, `.pop`, `.update`). These are by-reference mutations of an element inside a list inside the caller's dict (MUTPARAM + aliasing); hval is a pure value with no store path. (d) `"k" in <hval local>` and `.keys()` are not lowered. (e) Ripple: every caller/callee in the IR pipeline would have to move to `PyVal` together. |
| 4 | **G — generic Any-tree walker / rebuild**: `isinstance(x, dict|list)` + `.items()`/`.values()` / `{k: rec(v) for k, v in node.items()}`; reads `type/name/value/args` incidentally | 14 | **5** | 2 (2) | 30 | **D1/R-A generic fold** (`pyval/pydict/irkey/sdict/pget_dyn`, `generic_fold.py` 147 whole-function recognizers; cert `Phase2c_PyValDict`) | Precision over recall: a recognizer matches a WHOLE function of a fixed shape (two params, the accumulator named in `#@ assigns`, `-> None`). Rebuilders that RETURN a new tree (`_rewrite_subscript_calls_in_stmt`, `_hoist_calls_in_expr`) and the large typed handlers with an incidental walk (`_handle_subscript`, `_handle_len_call`) match no template. A `pyval -> pyval` map-fold with an `Any`-typed result is not modelled. Lesson 3: leave-trusted class. |
| 5 | **J — external JSON / report record** (why3 `--json` records, soundness report): `rec.get("prover-result") or {}`, `.get("answer", "")`, `term.loc.file-name`, `bucket`, `relied_on_by` | 4 | **4** | 3 (3) | 8 | **hval** (applies directly: the mirror already annotates `Dict[str, PyVal]` here) | **ch26 closed one.** `_record_answer` needed the receiver-form defaulted read `(<hval> or {}).get(k, D)` and `<hval> or "<lit>"`, and was converted on that seam. Remaining: `_residual_selectors_from_records` (`List[dict]` param -> retype, f-string of two hvals, `Set[str]`), `_merge_records_best_of_n` (tuple keys built from `_record_key` hvals -> `Dict[Tuple, dict]`: no hashable-hval key model), `_print_soundness_report` (`print`/`json.dumps` EXT + `.values()` iteration). |
| 6 | **M — non-IR keyed map, variable keys, non-heterogeneous values**: `Dict[int, List[CSLNode]]`, `Dict[Tuple[str,str],str]`, module dicts of tuples, `.setdefault(k, []).extend(..)` | 12 | **3** | 1 (0) | — | typed homogeneous maps (`map string (option string)`, `map int (option int)`) | The VALUE is homogeneous, but its element type is a record list / tuple / set, i.e. LISTSTR / TUPLE / RECORD / MUTRECV collection typing. Not a heterogeneous-value problem. Belongs to those families. |

Counts per cluster are disjoint. Cluster assignment is a rule over the read keys and ops
(`cluster.py`). N and G overlap in spirit: G holds the large node readers that also walk
generically.

### Top 3 clusters (headline)

1. **N — IR node reads (13 first / 19 in-chain / +13 latent).**
   * Nearest model: the certified emit_ir ADT.
   * Gap 1 is an annotation retype, which is legal and measured cheap: `_tag_of_value` is
     TC-clean with zero emitter change, so it is the next candidate.
   * Gap 2 is the per-kind polymorphic `value` key (int payload vs sub-node). This is a real
     model gap, because the ADT must pick the projection by the discriminant tested just before.
2. **P — IR program/decl records (7 first / 30 in-chain / +35 latent, the largest total).**
   * Nearest model: hval.
   * Gaps: the `PyVal` annotation gate, for-iteration over `HArr`, and in-place writes into
     nested hvals. The writes are by-reference mutation inside a caller's tree: a NEW capability
     (an hval store path with a writes frame), not an extension of a read.
3. **G — generic walkers/rebuilders (5 first / 14 in-chain / +30 latent).**
   * Nearest model: the D1 generic fold.
   * Gap: whole-function template matching, with no tree-rebuild (map-fold returning `Any`).
   * Stays leave-trusted unless a reviewer proposes a generic `pyval -> pyval` fold with a
     certificate.

## Existing certified value models — what each covers, and why it does or does not already apply

(Lesson p: "does a certified model already do this?". Source: read of `src/pycsl/module6_whyml`
at `b9dc767e`, file:line as of that commit.)

| model | WhyML carrier | gate (what a mirror function must look like) | faithful ops | not covered | cert / inertness | applies to the blocked markers? |
|---|---|---|---|---|---|---|
| **D1/R-A generic fold** (`preamble._pydict_theory_lines` :4310, `_sdict_theory_lines` :4219, `_pdict_bridge_theory_lines` :4258; `generic_fold.py` recognizers, e.g. `recognize_generic_fold` :461) | `pyval = PInt\|PStr\|PBool\|PNone\|PList\|PDict pydict`, `pydict = DNil\|DCons irkey pyval pydict`, `irkey = K_type\|..\|K_dyn string`, `sdict` | NO annotation. Per-function IR-shape/name recognizers set `needs_pydict`/`needs_sdict`/... (`preamble.py:2372-2513`). Whole-function match only | only what a templater re-emits for its shape: recursive dict/list walk, `.items()/.values()` folds, `pget_dyn`, `pput/pappend`, `Set[str]` accumulation | everything outside a matched template | `Phase2c_PyValDict.v` / `PyValDict.lean`, axiom-free; fires on 0 corpus programs | Only to cluster G, and only per-function by a new template. Not a general `Dict[str,Any]` lowering. |
| **hval** (`preamble._emit_pyval_theory` :7990-8159; gate `_uses_pyval` :7949; Module5 `_m5_get_dict_value_type` :5734) | `hval = HStr\|HInt\|HArr hval_list\|HMap hpairs\|HNode hval`, assoc-list `hpairs`; the top-level dict is `map string (option hval)` | annotation `Dict[str, PyVal]` / `Dict[str, Dict[str, PyVal]]` / `-> PyVal` / `List[Dict[str, PyVal]]` (plus a name gate on `_record_types`) | `.get(k)` / `.get(k, D)` on pyval locals and self-fields (`pairs_get`); doubled 1-arg receiver read -> `option string`; `d["k"]` / `x["a"]["b"]` string projection; `x or {}` / `x or []` (per-constructor truthiness); `==` int/str via `hint_of`/`hstr_of`; truthiness `hval_truthy`; `x in rec["f"]` (`hval_str_mem`); `len` (`hval_len`); `isinstance` by constructor; dict-literal construction (`_pyval_wrap`); `.items()/.values()` iteration (over-approximated); **ch26:** 2-arg receiver-form `(<hval-expr>).get(k, D)`, `<hval> or {}` as an hval expression, `<hval> or "<lit>"` | `.update/.setdefault/.pop`, `"k" in <pyval local>`, `.keys()`, for-loop over an `HArr`, stores into a nested hval, a hashable hval key | `Phase2f_PyVal.v` + `PyVal.lean` + `pyval-oracle.mlw`; byte-inert (`PyVal` is corpus-absent) | **Yes, after a retype** for J (already typed) and for the READ part of P. Not for P's writes / iteration / ripple. Today 15 mirror functions in 6 files use it (3 still trusted: `errors.as_dict`, `Module5.__init__`, and `_record_answer` until ch26). |
| **emit_ir ADT** (`preamble._emit_exprir_theory` :5047; `_KIND_DISCRIMINANT` `expressions.py:2248`; gate `Module6_WhyMLTranspiler.py:664-671`) | `emit_ir = IrVar\|IrAttr\|IrStr\|IrNum\|..\|IrOther string\|..`, `kind_of`, projectors (`name_of`, `svalue_of`, `num_of`, `args_of`, ...), `size` | annotations `ExprIR`/`StmtIR`/`IRNode`/`ContractExprIR`, or `@mutable_state` class context | `.get("type") == "K"` -> `is_K`; `.get(<table key>)` -> total projector (incl. the receiver form); `or`-chains of nodes | keys outside `_EMIT_IR_PROJ`; per-kind payload of `value`; the stmt family; construction of new nodes; `isinstance(.., dict)` walks | record-valued Rocq/Lean cert (tier 3); class-gated | **Yes, after a retype**, for the typed-node READ part of cluster N (MEASURED on `_tag_of_value`). Not for heterogeneous `value`, construction, or the stmt family. |
| **pyconst_val** (`const_pyval_of` `preamble.py:6264`; gate `_uses_pyconst_val` :8344) | `PVNone\|PVBool\|PVInt\|PVStr\|PVBytes\|PVComplex\|PVEllipsis` | a `PyConstVal` field or a function-name suffix | constant payloads of `Constant` nodes | dicts | `Phase2c_PyConstVal` | No (scalar constants, not dicts). |
| **opaque comprehension nodes** (`py_dictcomp_node` etc., `preamble.py:6755-6772`) | abstract types with `val function` child readers | AST-comprehension fields | child access only | any dict semantics | — | No. |
| **`any_map`** (`expressions.py:8975`) | `val any_map (_u: unit) : map 'k (option 'v)` | an uncoercible map actual (route #86) | none: an unconstrained placeholder | everything | — | No. It is a havoc, not a model. |
| **`IrOther`** | the emit_ir catch-all constructor (`IrOther ""` = absent) | part of emit_ir | — | — | — | Only as the absent/other node inside emit_ir. |
| **`RecordInfoView`** | — | — | — | — | — | Does not exist in `src/pycsl` (planning docs only: `gap-c-or-par.md`, `file-type-of-wall-impl.md`). |

**Why `Dict[str, Any]` never gets hval.** `Module5._m5_get_dict_value_type` returns `"hval"` only
for the Name `PyVal`. `Any` returns None, so nothing enters `dict_value_types`, `_uses_pyval`
stays off, and the dict is lowered as `map string (option int)` with every value erased to int.
`PyVal = Any` at runtime (`errors.py:24`), so retyping a mirror annotation from `Any` to
`PyVal` is a pure modelling-layer change (fidelity de-annotates before comparing).

## Measured probes (ch26)

| marker | probe | result |
|---|---|---|
| `pycsl._record_answer` (J) | the mirror was already `Dict[str, PyVal]`; seam in `expressions.py` (receiver-form 2-arg hval `.get`, `<hval> or {}` as an hval expression, `<hval> or "<lit>"`) | TC-clean, faithful emission (reads `prover-result`, `answer`). Converted (see the chain plan, ch26). |
| `ExpressionEmissionMixin._tag_of_value` (N) | port + retype `x_ir: Dict[str, Any]` -> `"ExprIR"`, no emitter change | **L3-tc clean.** Body: `kind_of x_ir = "Var"`, `name_of x_ir`, `Map.get self._current_symbol_table`, the `_add_abstract_op` write (declared in its frame). Whole-file proof of `expressions.py` OWED. Next candidate. |
| `ExpressionEmissionMixin._emit_bitwise_or_power` (N) | port + retype `expr: int` -> `"ExprIR"` | L3-tc: `right_ir["value"] < 0` is `svalue_of` (emit_ir) vs int, and `isinstance(left_ir.get("value"), int)` is `any bool`. Per-kind `value` payload gap. |
| `monomorphize._rewrite_annotations` (P) | port + retype `ir_data: int` -> `Dict[str, PyVal]` | L3-tc: `iter_length (match Map.get ir_data "functions" .. HArr HNil)`. No for-loop over an `HArr`. Under it: the store `func["symbol_table"] = new_st` into a list element (by-ref nested write). |

## What a reviewer should take from this

* The heterogeneous-dict wall is **not one wall but three**.
  * **Typed-node reads (N)** are mostly an annotation-retype problem on top of a certified ADT,
    plus one genuine gap: the per-kind `value` payload.
  * **Program-record reads (P)** are a READ problem hval already solves, plus an iteration gap
    (`HArr` for-loop) and a WRITE problem (by-reference stores into a nested hval) that no
    certified model addresses.
  * **Generic walkers/rebuilders (G)** need a `pyval -> pyval` fold.
* The bounded next moves are, in order:
  1. retype-only conversions in N (`_tag_of_value`);
  2. an `HArr` for-loop lowering (unblocks the P read-only members, e.g. `_collect_generic_decls`
     and `_check_gt4_polymorphic_recursion`; MEASURE first);
  3. the per-kind `value` projection keyed on the dominating discriminant test.
* The P writes and G rebuilds are research-grade (new mutable-value capability plus a
  certificate). The coupling rule applies.

Reproduce: `python3 census.py && python3 cluster.py` (reads `getting-better/trusted-reasons.tsv`
and the chain-plan appendix of this tree; edit `R` at the top).
