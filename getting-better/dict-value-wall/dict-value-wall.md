# Wall: the `Dict[str, Any]` / IR-dict value model ("dict-value-wall")

**Status:** state-of-the-art wall report (Phase 2 of the self-tcb-reduction driver). It is waiting for an
INDEPENDENT review. The reviewer gets the repo and the oracles, and none of the history.
**Author:** the driver's report author. Treat every sentence here as a claim to CONFIRM or REFUTE.
Each claim cites a file:line, a commit, a corpus id, or a command and its output.
**Date:** 2026-10-20.

**Trees.**
* "main" = `/home/fabrice/git/pycsl`, branch `ghost-assign-bc6`, HEAD `86c6e63e`. The git ref named
  `main` (`f552646c`) is an older merge and is not the driver's base.
* "land27" = worktree `/home/fabrice/git/pycsl-land27`, HEAD `6227161c`. It stacks `cd2b1e38`,
  `3bd6e1b9` and `6227161c` on `58e52bcd`. The ch28b seam `f856547d` (worktree `pycsl-g37ch28b`)
  stacks on top of land27.
* If a worktree is gone, use `git show <hash>`. Every commit cited here is in the main repo object
  store.

---

## 0. One-paragraph summary

PyCSL can already model a heterogeneous Python dict faithfully, in three certified ways. Most blocked
markers cannot reach those models, and what stops them is not one wall but **three different kinds of
work**:
1. **Annotation retype.** The mirror says `Dict[str, Any]` or `int` where a certified model needs
   `ExprIR` or `PyVal`. This part is legal and cheap per signature. It ripples through verified
   signatures, and every file it moves owes a long whole-file proof.
2. **Missing operations on the certified models.** hval cannot iterate an `HArr`, test `in`, call
   `.keys()`, or store into a nested value. emit_ir has no per-node-kind payload for `value`. One more
   gap is NEW in this report (§3.2, measured): **hval reads of a key that is PRESENT are unprovable
   today**, because its key equality is uninterpreted.
3. **Non-value blockers that the retype exposes.** Cross-mixin self-call typing, undeclared self-map
   fields, recursion, nested defs, and in-place mutation.

Measured yield so far: 97 markers have DICT/PYVAL in their chain. **2** converted (`_record_answer`,
`_tag_of_value`; land27, whole-file proofs still OWED). Every other chain re-measured after its first
blocker had at least one more (ch26–ch28). The wall is a **modelling choice, not a fundamental
limit**, except for one part: by-reference stores into nested values (§5, R2c) are a memory-model
question, not a value-model question.

---

## 1. What PyCSL is, and how this loop is gated

**Pipeline.** PyCSL verifies annotated Python. `#@ requires/ensures/assigns/...` comments go through
`src/pycsl/frontend/Module1_Ingestor.py` → `Module2_Parser.py` → `Module3_Weaver.py` →
`Module5_IREmitter.py`, which produces a JSON-like IR of plain `dict`s. Semantic checks run in
`core_ir_semantic.py`. Module 6 then emits WhyML: `src/pycsl/Module6_WhyMLTranspiler.py` plus the
mixins in `src/pycsl/module6_whyml/` (`expressions.py`, `statements.py`, `stmt_control_flow.py`,
`functions.py`, `preamble.py`, `types.py`, `generic_fold.py`, …). Why3 discharges the WhyML with
Z3 / Alt-Ergo. Entry point: `src/pycsl/pycsl.py <file.py> --import-path src/pycsl [--no-proof
--keep-mlw]`.

**The self-annotation mirror.** `src/self-annotate/src/` is a copy of PyCSL's own source,
annotated with PyCSL contracts. A function the tool cannot yet verify is a bodyless stub marked
`#@ \trusted`. The base loop ("self-tcb-reduction", `config/skills/self-tcb-reduction/SKILL.md`)
converts stubs one at a time. Each conversion is the live body ported verbatim
(`bin/port-one-mirror-body.py --convert`) under a fixed contract shape (`requires True` /
`ensures True` / `assigns <frame>`). The mirror's ANNOTATIONS are the modelling layer. Python
ignores them at runtime (`src/pycsl/errors.py:24`: `PyVal = Any`), and the fidelity plane compares
bodies after de-annotation. So retyping a mirror annotation is legal **if it describes the real
runtime shape faithfully**.

**The three L-planes**, each with its own authority. A conversion lands only when all three are
green:
1. **Fidelity.** The mirror body equals the live body: `bin/check-self-annotate-sync.sh`,
   `bin/self-annotate-mirror-check.sh`, `bin/check-trusted-reasons.py`.
2. **Whole-file Why3 proof** of the mirror file:
   `PYTHONHASHSEED=0 HEAVY_LOW=1 scratchpad/heavy/heavy.sh .venv/bin/python src/pycsl/pycsl.py
   src/self-annotate/src/<file> --import-path src/pycsl`. Per-function `--fun` is not accepted.
   Cost, measured: `Module6_WhyMLTranspiler.py` takes 1764 Valid / 38 min
   (`getting-better/driver-run-log.md:228`); `expressions.py` takes hours
   (`3bd6e1b9` message).
3. **Corpus byte-diff.** Every reference program's WhyML stays byte-identical unless the change is
   intended and re-proved: `bin/byte-diff-sweep.sh`, `bin/byte-diff-compare.py`, and the mirror
   sweep `bin/mirror-emit-sweep.sh`. The corpus is `test-suite/corpus/pycsl-reference/` (about 1820
   programs) plus pyref (2186).
* Beside the three planes there is a battery of soundness ratchets, `bin/run-soundness-planes.sh`
  (61 planes): `check-emitted-vacuity`, `check-shadowed-selfcalls`, the assigns
  survival/underdeclaration planes, and others.

**Axiom ledger: 3.** Kernel axioms accepted by `src/pycsl/proof_axiom_allowlist.py:19-40`:
propositional extensionality and functional extensionality (with its dep variant) on the Rocq side,
and `propext`, `Classical.choice`, `Quot.sound` on the Lean side. A new WhyML value shape must
co-land a `src/formal-semantics/` certificate that is axiom-free relative to this ledger (the
COUPLING RULE, `config/skills/self-tcb-reduction/SKILL.md:243-249`).

**Count.** `grep -rF '#@ \trusted' src/self-annotate/src | wc -l` gives **451 on main** and **449 on
land27** (and on ch28b). These are substring counts and include prose mentions. The line-prefix
markers are **423 on main** and **421 on land27**
(`grep -rhE '^\s*#@ \\trusted' src/self-annotate/src | wc -l`). Older wall documents quote 1041,
1018 and 748. Those are the same metric earlier in the campaign.

---

## 2. The wall as first seen

### 2.1 Frequency (census, gen #37 ch26)

Source: `getting-better/dict-value-wall/census-g37.md`. It was measured at `b9dc767e` over the 423
line-prefix markers of `getting-better/trusted-reasons.tsv`. Each marker's blocker chain comes from
the chain-plan appendix (`getting-better/chain-plan-g36/chain-plan-g36.md:526-963`).

```
  trusted rows                                        423
  DICT (or PYVAL) in the measured chain                97   (91 DICT, 8 PYVAL, overlap 2)
  ... DICT/PYVAL is the FIRST blocker                   41   (37 DICT-first)
  ... DICT/PYVAL(/RIPPLE) is the ONLY family            19   (11 of them complete chains)
  latent (literal-key dict reads, DICT not in chain)    86
  trusted with literal-key dict reads in live body     151
  trusted with `Dict[str, Any]` in the live signature  111
```

In the chain-plan family table (`chain-plan-g36.md:67-112`), DICT is the most frequent L-cost
family: 92 in-chain, 37 first, 31 complete chains contain it. In the cheaper-first unlock table,
`+DICT [L]` is the largest single step: complete-unlocked 93 → 124 (+31).

**Reproduced by this report.** I extracted `b9dc767e`'s `src/pycsl`, `trusted-reasons.tsv` and
`chain-plan-g36.md` into a scratch dir, pointed `census.py` `R=` at it, and ran
`python3 -I census.py && python3 -I cluster.py`. Output `423 399 423`, and the cluster row counts
below match the census exactly.

### 2.2 Shape clusters (`cluster.py` rule over read keys and ops; disjoint)

| cluster | what the body does | in-chain | first | only (complete) | latent |
|---|---|---|---|---|---|
| **N** IR expr/stmt node read | dispatch on `node["type"]` (92 reads), project `name/value/args/func/object/left/right/index/receiver` | 19 | 13 | 4 (2) | 13 |
| **X** signature ripple | no literal-key read of its own; the DICT error arrives through a callee, a param, or a `Dict[Tuple,..]` | 18 | 9 | 6 (3) | — |
| **P** IR program/decl records | `ir["functions"]`, `func.get("contracts") or {}`, `symbol_table`, `type_params`, writes `func["symbol_table"] = ..` | 30 | 7 | 3 (1) | 35 |
| **G** generic Any-tree walkers | `isinstance(x, dict\|list)` + `.items()` / dict-comprehension rebuild | 14 | 5 | 2 (2) | 30 |
| **J** external JSON records | why3 `--json` records, soundness report | 4 | 4 | 3 (3) | 8 |
| **M** homogeneous non-IR maps | `Dict[int, List[CSLNode]]`, `Dict[Tuple[str,str],str]`, `setdefault(..).extend` | 12 | 3 | 1 (0) | — |

The 32 COMPLETE chains in these clusters, listed by the reproduction above:

```
N _emit_bitwise_or_power DICT | _emit_contract_logic_symbol DICT>STRM>GETATTR>INTSTR>RIPPLE | _tag_of_value DICT
  _happy_predicate NESTED>RECORD>DICT | _handle_augassign_stmt GETATTR>DICT
P _emit_subtyping_goals DICT>LISTSTR | _mixin_dep_pseudo_functions SET>TUPLE>DICT
  _param_type_str MUTRECV>DICT>MEMB>INTSTR>GETATTR | _build_callee_no_exception_summary SET>DICT
  _check_gt4_polymorphic_recursion DICT>GETATTR>TUPLE | _collect_instantiations SYNTAX>SET>DICT>UNBOUND
  _rewrite_annotations DICT | _specialize_decl MUTRECV>DICT>INTSTR
G _hoist_calls_in_expr MUTRECV>PYVAL>DICT | inline_stmts MUTRECV>DICT | _rewrite_subscript_calls_in_stmt DICT
  _rewrite_subscript_to_name PYVAL>DICT
J _merge_records_best_of_n DICT | _print_soundness_report DICT | _record_answer DICT>RIPPLE
  _residual_selectors_from_records DICT>LISTSTR
M _attach_labels_and_ghost_assigns GENEXP>LISTSTR>DICT>GETATTR>REF | _parse_extracted_contracts MUTRECV>LISTSTR>GETATTR>DICT
  _subscript_read_site RECORD>DICT | bases_closure MUTRECV>DICT>SET>MEMB
X _check_protect_aliasing DICT>STRM | visit_For GENEXP>LISTSTR>UNBOUND>DICT | visit_Module MUTRECV>DICT
  visit_While GENEXP>UNBOUND>DICT | _ExecSplicer.visit_Expr EXC>PYVAL | _construct_indices PYVAL
  _rewrite_annotation_str DICT | _try_reaches_assert DICT
```

**The 11 complete "DICT-only" chains were re-measured (ch26–ch28) and were NOT DICT-only:**

| marker | re-measured fate |
|---|---|
| `_tag_of_value` | LANDED, `4eca6459` |
| `_record_answer` | LANDED, `dc58bc44` |
| `_emit_bitwise_or_power` | per-kind `value` payload + class-constant dict |
| `_rewrite_annotations` | `HArr` for-loop + nested store |
| `_rewrite_subscript_calls_in_stmt` | generic rebuild |
| `_rewrite_subscript_to_name` | generic rebuild |
| `_merge_records_best_of_n` | hashable-hval tuple key |
| `_print_soundness_report` | `json.dumps` / `print` EXT |
| `_construct_indices` | sexp-tuple carrier (L9 boundary, `driver-backlog.md` L9) |
| `_rewrite_annotation_str` | tuple-keyed map + `re` EXT |
| `_try_reaches_assert` | DICT + an `ast` walker |

Rows 3-11 are from `chain-plan-g36.md:1347-1404`. **Lesson: in the chain plan, "COMPLETE" was a
lower bound on chain length.**

### 2.3 Re-measurements ch20–ch28 (chain-plan, then land27 / ch28b)

* **ch20–ch25** (`chain-plan-g36.md:361-1331`): 0/7, 1/7, 1/16, 0/17, 1/15, 0/22 (+1 extra)
  honest. The recurring finding (ch23 header, `:964-971`): "As in ch20-ch22 the census family was
  the FIRST type error. Once re-ported, every chain hits a value-model gap (AST-node /
  Dict[str,Any] / Optional-tuple)."
* **ch26** (`:1332-1494`, step 7 DICT, 15 markers): 1 honest after one seam (`_record_answer`),
  not landed then. Recurring blockers: int-erased Dict[str,Any] reads 13 of 27, in-place-mutation
  refusals 9, AST reflection 6, callables 4.
* **ch27** (land27 `chain-plan-g36.md:1496-1638`, commit `6204c83b`/`6227161c`): landed
  `_record_answer` (451→450) and `_tag_of_value` (450→449). The **cluster-N retype probe** retyped
  ONLY the IR param of all 19 N markers to `ExprIR`/`StmtIR`/`IRNode`. Result: 0 more honest. Next
  blockers, ranked by capability (markers it would advance): signature ripple (other params,
  callee stubs) 4; self-recursion with an emit_ir `size` measure 3; empty-node `{}` default +
  `slice` projector 2; effect inside a comprehension 2; nested def 2; in-place mutation 2;
  per-kind `value` payload 1; comprehension over a node list 1; getattr-default 1. **3 were
  misclustered as IR**: Lean JSON AST (`_linearize_app`, `project_to_ir`) and a Weaver site
  record (`_happy_predicate`).
* **ch28/ch28b** (ch28b `chain-plan-g36.md:1640-1804`, commit `f856547d`): drained the two
  cheapest ch27 rows on 6 markers. **0 converted.** Ripple lengths measured: `_emit_membership`
  ≥6, `_emit_contract_logic_symbol` ≥5, `_classify_iterable` ≥5, `_handle_sum_call` 4,
  `_emit_first_assign` ≥3, `_handle_array_set_stmt` ≥3. It landed one seam: an empty-node `{}`
  arm or operand lowers to `(IrOther "")`, witnesses 3220-3224, 0 MOVED root/pyref/mirror.
  Re-ranked next capabilities: **cross-mixin self-callee typing 3**, **undeclared self-map fields
  4**, per-kind payload 2, comprehension over node lists 2.

---

## 3. The certified value models that exist today, and exactly what each covers

Lesson (p) (`getting-better/wall-lessons.md:1264-1282`): a prior build re-did work an older
certified model already covered. So here is the full inventory. Lines are main unless marked.

### 3.1 emit_ir ADT (the IR expression node)

* **Carrier.** `type emit_ir = IrVar string | IrAttr emit_ir string | IrStr string | IrNum int |
  IrNumF real | IrBoolC int | IrRaw string | IrOther string | IrCall string emit_ir int | IrSub
  emit_ir emit_ir | IrBinOp string emit_ir emit_ir | ... | IrMapGet .. | IrSetMem ..`
  (`src/pycsl/module6_whyml/preamble.py:5047`, `_emit_exprir_theory`).
* **Projectors** (total, definitional `let function`s): `kind_of` `:5524`; `name_of`
  (`IrVar n -> n | IrAttr _ a -> a | _ -> ""`); `value_of` (string leaves only); `svalue_of`
  `:6095` (`IrSub v _ -> v | _ -> IrOther ""`); `num_of` (`IrNum n -> n | _ -> 0`, emitted only
  under `_uses_null_byte_num_reader` / `_uses_const_reflect`); `size` `:5802` (the `variant`
  measure).
* **Routing tables.**
  * `_EMIT_IR_PROJ` (`expressions.py:128-161`): `"type"→kind_of`; `"name"/"attr"/"field"→name_of`
    (one shared projector, by design); `"value"→svalue_of`; `"args"/"elts"/"captures"→args_of`;
    `"left"/"right"/"op"`; `"lower"/"upper"→svalue_of`; `"orelse"`, `"test"`, `"body"→stmts_of`.
  * `_EMIT_IR_GET_KEY_PROJ_BY_FUNC` (`:394`) holds per-function scoped overrides, e.g. `"value"→num_of`
    inside named functions only.
  * `_KIND_DISCRIMINANT` (`:2248`): `.get("type") == "K"` → `is_K`.
* **Gate.** A param, return or local annotated `ExprIR`/`StmtIR`/`IRNode`/`ContractExprIR`
  (`functions.py:257`, `Module6_WhyMLTranspiler.py:590` `_IRNODE_TAGS`), or a `@mutable_state`
  class context. The `.to_dict()` alias is NOT the gate. The 20260719 rawdict wall's CLAIM A was
  refuted on exactly this point (§4.1).
* **Corpus.** The path is load-bearing: corpus 0748/0749/0878-0881 use `ExprIR` params
  (`20260719-rawdict-to-emitir-bridge-wall-response.md`, Artifact 3).
* **Certificate.** The tier-3 record-valued certificate, `Phase2b_RecordVal.v` / `RecordVal.lean`
  (`config/skills/self-tcb-reduction/SKILL.md:260-264`). The Layer-2 receiver extension is
  `Phase2j_MethodRecv.v`. ch28 notes that `slice_of`/`lower_of`/`upper_of` are definitional and
  that `Phase2j` does not mention them, so adding a *projector* over existing constructors touches
  no cited certificate.
* **Covers.** Typed-node READS of the expression family. Not covered:
  * keys outside the table;
  * the per-kind payload of `value` (Number's int vs Attribute's sub-node);
  * the stmt family;
  * constructing new nodes (except `{}` → `IrOther ""`, f856547d);
  * `isinstance(.., dict)` walks.
* **Measured.** `_tag_of_value` became TC-clean with the retype `x_ir: "ExprIR"` alone (emits
  `kind_of x_ir = "Var"`, `name_of x_ir`), and was landed with a mutation check (`3bd6e1b9`).

### 3.2 hval (Tier-5 heterogeneous value; `Dict[str, PyVal]`)

* **Carrier** (`preamble.py:7990`, `_emit_pyval_theory`):
  `type hval = HStr string | HInt int | HArr hval_list | HMap hpairs | HNode hval`,
  `hval_list = HNil | HCons ..`, `hpairs = PNil | PCons string hval hpairs`. The top-level dict is
  `map string (option hval)`.
* **Readers.** `pairs_get` (assoc-list lookup, `let rec function`), `hstr_of`, `hint_of`,
  `hval_truthy`, `hval_len`, `hval_list_str_mem`, and `hval_list_len` / `hval_list_nth` (they
  appear in emitted WhyML, e.g. the probe below).
* **Gate.** `Module5._m5_get_dict_value_type` (`frontend/Module5_IREmitter.py:5734`) returns
  `"hval"` only for the Name `PyVal` (or `Dict[str, Dict[str, PyVal]]`). `Any` returns None, so the
  dict lowers to `map string (option int)`, values erased to int. `_uses_pyval`
  (`preamble.py:7949`) also fires on `List[PyVal]` fields, `-> PyVal`, and the name
  `_record_types`.
* **Faithful ops** (census table): `.get(k)` / `.get(k, D)` on hval locals and self-fields;
  `d["k"]`, `x["a"]["b"]`; `x or {}` / `x or []`; `==` via `hint_of` / `hstr_of`; truthiness;
  `x in rec["f"]`; `len`; `isinstance` by constructor; dict-literal construction (`_pyval_wrap`,
  `expressions.py:1319`); over-approximated `.items()` / `.values()` iteration. land27 adds the
  receiver form `(<hval>).get(k, D)` with ANY key (`dc58bc44`).
* **Not covered:** `.update` / `.setdefault` / `.pop`; `"k" in <hval local>`; `.keys()`; **a
  for-loop over an `HArr`** (measured on `_rewrite_annotations`: `iter_length` over an `HArr`);
  **stores into a nested hval**; a hashable hval key.
* **Certificate.** `src/formal-semantics/rocq/Phase2f_PyVal.v` (333 lines) / `lean/PyCSL/PyVal.lean`,
  plus the oracle `getting-better/pyval-oracle.mlw`. Its `pairs_get` uses **`string_dec`**
  (`Phase2f_PyVal.v:214-217`), and it proves `read_same_key` (`:222`) and `build` read-backs
  (`:246-275`).
* **ch27 fix** (`dc58bc44`). `hpairs_key_eq` was a program `val`. A `let function` that calls a
  program val gets no logic definition, so every hval reader was logic-opaque, and
  `pairs_get PNil k = None` was unprovable (3140 timed out). It is now `val function hpairs_key_eq`
  (land27 `preamble.py:8051`). On main it is still a program `val` (`preamble.py:8046`).
* **NEW, measured for this report: present-key reads are still unprovable on land27.**
  `hpairs_key_eq` is an uninterpreted `val function` with no spec. So `pairs_get (PCons "a" v ..) "a"`
  cannot be reduced, and neither can `hval_truthy (HStr s)`, which is
  `not (hpairs_key_eq s "")`. The WhyML model is strictly weaker than the certificate it cites,
  which uses decidable equality.
  * Hand oracle `keq.mlw` (scratch). `empty_read` is Valid. `hit_read`
    (`pairs_get (PCons "a" (HInt 1) PNil) "a" = Some (HInt 1)`) times out in z3 and alt-ergo (5 s).
  * Emitted probe through land27's real emitter: `answer_hit` reads the nested record
    `{"prover-result": {"answer": "Valid"}}` and `top_hit` reads `{"answer": "Valid"}`, each with
    `ensures \result == "Valid"`. The file emits L3-tc ✓. **Both VCs time out in z3 and
    alt-ergo**. Even the top-level `Map.get` read fails, because `hval_truthy (HStr "Valid")` is
    undecided.
  * The same emitted `.mlw` with ONE added line,
    `ensures { result <-> a = b }` on `hpairs_key_eq`, gives: **alt-ergo Valid for both**
    (`answer_hit` 975 steps, `top_hit` 116); z3 Valid on `top_hit`, Timeout on `answer_hit`.
    **The twin (`"Invalid"`) times out in both provers.** This spec has the same form as the
    existing `val str_eq_op ... ensures { result <-> a = b }` (`functions.py:5443-5445`;
    `generic_fold.py:16379` calls that form "satisfiable, non-`True`, NOT an axiom").
  * Consequence: every hval FAIL twin so far fails for a weaker reason than its comment claims (ch27
    soundness note (a) said this for the pre-ch27 state; it still holds for present keys).
  * Reproduce: `getting-better/dict-value-wall/` has no copy. The probe text is in Appendix A.

### 3.3 D1/R-A generic fold (`pyval` / `pydict`, the OLDER model)

* **Carrier.** `pyval = PInt | PStr | PBool | PNone | PList | PDict pydict`,
  `pydict = DNil | DCons irkey pyval pydict`, `irkey = K_type | .. | K_dyn string`
  (`preamble.py:4310` `_pydict_theory_lines`; `sdict` at `:4219`).
* **Gate.** No annotation. 147 whole-function recognizers in `module6_whyml/generic_fold.py`
  (`grep -c '^def recognize'`; e.g. `recognize_generic_fold` `:461`) match a function's IR shape
  and name, then re-emit it from a template. Census: the model fires on 0 corpus programs.
* **Certificate.** `Phase2c_PyValDict.v` (535 lines) / `PyValDict.lean`, axiom-free.
* **Covers.** Only what a matched template re-emits: recursive dict/list walks,
  `.items()/.values()` folds, `pget_dyn`, `pput/pappend`, `Set[str]` accumulation.
  `c6557971` used it to break the "heterogeneous value-model ROOT" (`_collect_mutations`, a
  `ref (list pyval)` accumulator with a real `pystr_eq` disjunction, axiom-free, ledger 3).
* **Does not cover.** Rebuilders that RETURN a new tree, i.e. a `pyval -> pyval` map-fold.
* **Name clash.** hval and pyval coexist under disjoint names (`h*` vs `P*`). They are not
  mergeable (`preamble.py:7999-8008` docstring).

### 3.4 Typed homogeneous maps and the rest

* **Typed homogeneous maps.** `Dict[str, str]` → `map string (option string)`, `map int (option int)`,
  and L10's `map string (list string)` (`driver-backlog.md:2448-2465`, functional
  `setdefault(k,[]).append`). Cluster M's values are homogeneous but record lists, tuples or sets.
  That is a collection-typing problem, not a heterogeneous-value one.
* **`pyconst_val`.** Scalar constants of `Constant` nodes (`Phase2c_PyConstVal`). Does not model
  dicts.
* **`any_map`** (`expressions.py:9004`): `val any_map (_u: unit) : map 'k (option 'v)`. A havoc,
  not a model.
* **Receiver-dropped `get_2` / `<name>_get_N`.** A `.get` on a non-Name receiver outside the
  recognizers. Sound only because it stays a program `val`: each call is a fresh unconstrained
  value. Witness 3162 guards this (ch27).

### 3.5 What selects which model (measured summary)

| annotation on the mirror value | lowering | evidence |
|---|---|---|
| `Dict[str, Any]`, `dict`, `Any` | `map string (option int)`; values int-erased; `.get` on a non-Name receiver is receiver-dropped | rawdict response Artifact 1 (`Map.get node "type"` = int hash); census |
| `"ExprIR"` / `"StmtIR"` / `"IRNode"` | emit_ir, with projectors | `_tag_of_value` (`3bd6e1b9`); 0878 proves |
| `Dict[str, PyVal]`, `-> PyVal`, `List[Dict[str, PyVal]]` | hval | `_record_answer` (`dc58bc44`); the probe above |
| `int` (the mirror often says this) | int | ch26/ch27 retype probes start from `expr: int`, `ir_data: int` |
| none (named-function recognizers) | D1 pyval/pydict | `generic_fold.py` |

Mirror signature census for this report (land27 mirror, `ast` over every `def`, "trusted" means a
`\trusted` line in the preceding comment block):
* **183 verified** functions have `Dict[str, Any]`/`dict` in their signature (84 of them in
  `frontend/Module5_IREmitter.py`, 24 in `ir_scanner.py`, 19 in `functions.py`).
* **184 verified** have an IR tag.
* **10 verified** have `PyVal`.
* Trusted: 35, 71 and 1 respectively.

These verified signatures are the ripple surface of any retype (§5, R1).

---

## 4. Prior walls on this ground, and their verdicts

### 4.1 `20260719-rawdict-to-emitir-bridge-wall` (count 1041) → **BOUNDARY**

* **Claim A.** The emit_ir keystone fires only with `.to_dict()`. **Refuted**: a bare `ExprIR`
  param already lowers `.get("type")` → `kind_of` and `["left"]` → `left_of`.
* **Claim B.** The path is corpus-inert. **Refuted**: 0748/0749/0878-0881 use it, and 0878 proves.
* **What the reviewer found the real blockers to be:** (B1) `t = ir.get("type")` bound to a local
  pre-declared `ref 0`, and (B2) bare-Var `.get("value")` → `svalue_of` (sub-node), not a string
  or int leaf.
* **What changed since.**
  * The retype route was proven on `_tag_of_value`.
  * ch28's empty-node seam landed.
  * B2 is the **per-kind payload** gap, still open (R3).

### 4.2 `20260718-ast-node-list-walker-wall` (count 1060) → **BREAKABLE**, via a concrete compaction `function`

* The naive abstract-val content law for `[x.id for x in elts if isinstance(x, ast.Name)]` is
  **positionally vacuous**: the response's Part A oracle times out on the observation goal.
* A concrete fixpoint over `is_var`/`name_of` is non-vacuous and axiom-free (Part B: observe Valid,
  evil twin Timeout).
* **Lesson that carries over:** an abstract law over a filtered or heterogeneous collection is a
  vacuity trap. Use concrete definitional folds.

### 4.3 `20260719-str-int-value-model-wall` (count 1043) → **CHEAP-BREAKABLE**, with a BOUNDARY subset

* `str(<int>)` was `val str_conv : int -> int`. A faithful `val str_of_int : int -> string` is
  corpus-inert (767 swept, empty diff).
* A tuple-of-string-literal subset stays boundary (collapses to `int 0`, vacuous).
* It is relevant here as the pattern for "an int-erasure is a modelling choice with an inert fix".

### 4.4 `pyval-value-model-wall` (+ `-response`, `-impl`) → **CONFIRM** (this is the origin of hval)

* The report (`pyval-value-model-wall.md:29-40`) stated the thesis this report re-asks: the
  homogeneous `map int (option int)` is "a REPRESENTATION choice".
* Fable's oracle confirmed a faithful `pyval` + `map string (option pyval)` + typed read, axiom-free.
  It added one hard rule: `PArr` must recurse through a bespoke cons-list, because `seq pyval` is
  rejected as "non strictly positive" (`-response.md:16-40`).
* Landed as hval, with its first conversion `_collect_typevar_registry` (J2/J3, `b5bef284`;
  `-impl.md:167-171`).

### 4.5 LEVERS ledger (`getting-better/driver-backlog.md:2481-2510`)

* **L8 (Enumerable-typed-map ADT): STRUCK, CERTIFIED-BOUNDARY (2026-08-11).** Three refuters:
  (1) CASCADE, retyping the shared `_record_types` field re-lowers green consumers in 5+ files;
  (2) VACUITY, values were int-erased, so an assoc-list over them reads opaque sentinels;
  (3) RELOCATES-NOT-DODGES, it still enumerates a total map's `.values()`. Its reopening condition was "a faithful domain-carrying typed-map value model". **What changed
  since:**
  * hval's R3 carrier became an assoc list (`hpairs`, iterable), which answers refuter 3 for
    hval-typed values.
  * `_record_types` is now an hval gate name (`preamble.py` `_uses_pyval`).
  * Refuter 1, the cascade, is exactly R1's ripple cost below, and is unchanged.
* **L11 (PSet-in-pyval): STRUCK, census-confirmed 0 yield.** Its one beneficiary was co-blocked by
  an int-dict and an opaque callee. Unchanged.

### 4.6 wall-lessons on dict/hval/pyval

* **`wall-lessons.md:671-685`** (2026-07-20): the giants front is CERTIFIED-BOUNDARY, rooted in "the
  faithful heterogeneous `Dict[str,Any]`/`pyval` value model + its certificate". Since then:
  * hval landed;
  * `c6557971` converted `_collect_mutations`, the recorded root, via D1 pyval with no new cert. Its
    commit message says the earlier ledger "over-statement" was corrected.
  * The giants (`_is_emit_ir_expr`, `_handle_subscript`) are still trusted (cluster G). They are
    also blocked by getattr-default reflection (`:678-680`).
* **`:1264-1282` (lesson p).** Two certified value models existed, and a build re-solved what the
  older one already did. Hence §3.
* **`:1445-1485`.** `_check_noreturn` needs a `pyval -> stmt_ir` bridge certificate. Built,
  provable, reverted for cost. This is the cross-model bridge question that R1 for the stmt family
  would face.
* **`:843-850`.** A bare `dict` param lowered to `map string ..` as a trusted val but
  `map int ..` as a `let`. The workaround was `Dict[str, PyVal]`. This is a precedent for R1.
* **f5 / g5 (`:8776-8900`).** Declaring a field on a class is the only move that satisfies both
  frame ratchets. But it switches on the `--transitive` HOLE-T arm (ceiling 0) for every clause that
  omits the field: 13 fields would have made 19 rows HOLE-T. And it reaches the emitted record only
  for some classes. `FunctionEmissionMixin` emits no fields at all. This prices R5.

---

## 5. The deeper question: fundamental or a modelling choice?

**Verdict offered for review: a modelling choice, with one memory-model exception.**

* Python's `Dict[str, Any]` value is a tagged sum. Why3 accepts it: hval, emit_ir and D1 pyval are
  each axiom-free and certified (§3).
* What is erased today is chosen at the ANNOTATION layer (`Any` → int map), and that layer is legal
  to change (§1).
* What is NOT a value-model question is the **by-reference mutation of a value nested inside a
  caller's tree** (`for func in ir_data["functions"]: func["symbol_table"] = st`). Python mutates the
  element shared by `ir_data`. A value-semantic lowering would silently drop that write unless it
  writes back along the path, and the write-back is faithful only if no other alias exists. The same
  shape appears in `_handle_array_set_stmt` (a write through a `getattr` alias of a self map, ch28).
* The chain data says the binding constraint is breadth. After the value-model step, the chains
  continue into RECURSION, NESTED, MUTRECV, COMP, GETATTR and cross-mixin typing (ch27, ch28). So no
  value-model route alone converts more than a handful.

Below, "unlocks" counts only markers whose MEASURED chain would be fully covered. Markers it would
only advance are listed separately. Every count is an upper bound, because the chains were measured
only to the first few blockers (§6).

### R1 — retype mirror `Dict[str, Any]` / `int` to `ExprIR` / `StmtIR` / `PyVal`, and close the ripple

* **Advances.** All 19 N (measured, ch27), the P/J readers (to hval), and the 18 X ripple markers.
* **Unlocks alone: 1 measured** (`_tag_of_value`, landed). ch27: "0 more honest with the retype
  alone". ch28: retyping all params of `_emit_membership` exposed ≥6 further blockers.
* **What moves.** The retyped method's inherited `val` signature in every mirror file that sees it.
  `_tag_of_value` moved `expressions.mlw` and `Module6_WhyMLTranspiler.mlw` (`3bd6e1b9`). Each mover
  owes a whole-file proof (38 min to hours, §1).
* **Ripple surface.** 183 verified mirror functions carry `Dict[str,Any]`/`dict` and 184 carry an IR
  tag (§3.5). Retyping a callee's param forces every verified caller's actual to the new type.
  L8 refuter 1 measured this for one field: 5+ files of green code.
* **To certify.** Nothing new, if the target model exists.
* **Soundness risks.**
  * The retype must be FAITHFUL. 3 of 19 N markers are not IR at all (Lean JSON, Weaver records,
    ch27), and retyping them `ExprIR` would model the wrong value.
  * The stmt family has no projectors (census gap c, lesson 8).
* **Make-or-break.** After a retype, does ANY marker beyond `_tag_of_value` close once its OWN
  non-value blockers are counted? Concretely: retype every param of `_emit_contract_logic_symbol`
  and apply R4 and R5 in a scratch copy. Does it reach L3-tc clean with a non-vacuous emission, and
  what is the mover bill?

### R2 — extend hval

R2 has four sub-routes:

* **(R2a) Pin key equality** (`ensures { result <-> a = b }` on `hpairs_key_eq`).
  * Without it, hval's faithful reads are faithful only on ABSENT keys (§3.2, measured). It is the
    prerequisite for any non-vacuous hval witness.
  * Unlocks 0 markers by itself.
  * Moves the hval preamble line in about 30 corpus witnesses and 21 mirror files (the same set
    `dc58bc44` moved, line only), and every hval FAIL twin must be re-proved.
  * Certify: it aligns the WhyML with `Phase2f`'s `string_dec`, so no cert change. Ledger: a spec on
    a `val function` is an assumed logic fact (realizable). It is not a kernel axiom; the precedent
    is `str_eq_op`.
  * Make-or-break: does the re-proof of the 30 corpus witnesses keep every FAIL twin failing, and do
    the 21 mirror movers still prove whole-file? (Adding facts can only make goals easier, so the
    risk is twins flipping, not regressions.)
* **(R2b) for-loop over `HArr`, `in`, `.keys()`.**
  * Lower `for x in <hval>` as an index loop over `hval_list_len`/`hval_list_nth`. Both already
    exist and are emitted (seen in the probe's VC list).
  * Candidates (census): `_collect_generic_decls` (incomplete chain),
    `_check_gt4_polymorphic_recursion` (DICT>GETATTR>TUPLE, so not by R2 alone),
    `_residual_selectors_from_records` (DICT>LISTSTR, plus an f-string of hvals and `Set[str]`).
  * **Unlocks alone: 0 measured complete chains.** It advances P (30 in-chain, 7 first) and J.
  * Certify: if `len`/`nth` are definitional, only a Phase2f lemma that they agree with the
    list semantics.
  * Make-or-break: does `_collect_generic_decls` (read-only P member), retyped `Dict[str, PyVal]`,
    reach L3-tc clean with an index loop over `HArr`, AND does a witness reading element `i`'s field
    prove while its twin fails? This needs R2a first.
* **(R2c) stores into a nested hval.**
  * Candidates: `_rewrite_annotations` (P, complete DICT-only chain; next blocker after the retype
    is this store), `_specialize_decl`, and the P writers (`.setdefault(..).append`, `.pop`,
    `.update`).
  * A NEW capability: a store path with a writes frame on the caller's root.
  * **This is the memory-model exception.** It is faithful only when the iterated element is not
    aliased elsewhere. `ir_data["functions"]` elements are shared with every pass that holds `func`.
  * Make-or-break: can `for func in d["functions"]: func["k"] = v` be lowered as a functional
    write-back `d["functions"] := map_set_k(..)` with a PROOF that it equals Python's in-place
    semantics under a stated no-alias precondition? Or does the fixed contract shape (`requires
    True`) forbid stating that precondition? (Compare the forbidden-contract note for `map string
    int`, `driver-backlog.md` "BLOCKED".)
* **(R2d) hashable hval keys.** Only `_merge_records_best_of_n` needs them. Low value.

### R3 — per-node-kind payload for emit_ir `value` (and `lower` / `upper` / slice)

* **Markers naming it:** `_emit_bitwise_or_power` (ch27 rank 7), `_handle_sum_call` (ch28 blocker
  4), `_classify_iterable` (ch28 blocker 3). **Unlocks alone: 0.** `_emit_bitwise_or_power` also
  reads a class-constant dict `self._BITWISE_FN_NAMES[op_char]` (ch26), and the other two have ≥4
  blockers each.
* **Design.** Route `.get("value")` by the DOMINATING discriminant test: under `kind_of x =
  "Number"`, use `num_of x`; under `IrSliceAccess`, use the base. `num_of` and `slice_of` already
  exist as definitional `let function`s over certified constructors (`IrNum int`, `IrSub`), so a
  projector-only extension needs no cert change (ch28 row (b)). Adding a new constructor would need
  one (Phase2b/2j).
* **Soundness risk (measured, ch28 note a).** Today the global routes read `IrOther ""` on
  `IrSliceAccess` / `IrSliceN`. A converted body sees a constant, and a FALSE claim "the slice branch
  is never taken" would prove. Flow-sensitive routing that picks the wrong kind has the same
  failure mode. Per-kind routing therefore needs a twin per kind.
* **Faithfulness question.** Python `isinstance(n.get("value"), int)` on a Number may be int, float
  or bool. The ADT splits `IrNum int` and `IrNumF real`, plus `IrBoolC int`.
* **Make-or-break.** Can the emitter pick the projector from a dominating `kind_of`/`is_K` test
  (fail closed when none dominates)? Does a witness `if n["type"] == "Number": return n["value"]`
  with `ensures` on the int prove, while (i) a wrong-kind twin and (ii) a "branch is dead" twin
  fail? All of this must hold without touching corpus 0748/0749/0878-0881 bytes.

### R4 — cross-file mixin self-method typing from the sibling's declaration

* **Markers (ch28b): 3.** `_emit_contract_logic_symbol` (blocker 4: `self._inductive_sig_whyml` lives
  in the preamble mirror), `_emit_first_assign` (`_build_dict_literal_map` absent from the
  statements mirror), and `_emit_membership` (blocker 4: `self._expr_is_pyval`). **Unlocks alone:
  0.** Each has ≥3 more blockers.
* **Today.** An absent self-callee gets one abstract `val` PER call-site type signature, typed from
  the actuals (`self__expr_is_pyval_1 (x0: int) : int` next to `..._c78145 (x0: emit_ir)`). That is
  sound, because each is an unconstrained program val, but it gives one method two unrelated models
  (ch28 note b).
* **To certify.** Nothing.
* **Soundness risk.** A `\trusted` stub's declared frame is the caller-side assumption verbatim
  (g5 positive control, `wall-lessons.md:8869-8885`). Importing a sibling's DECLARED signature also
  imports its `assigns`. If that clause is under-declared, the new caller inherits a false
  assumption. The underdeclaration plane must be green for those siblings first.
* **Make-or-break.** Type `self.<m>` from the mirror declaration of `<m>` in a sibling mixin file.
  Does the mirror sweep move ONLY the intended files, does `check-shadowed-selfcalls` stay at 14,
  and does `_emit_contract_logic_symbol` advance exactly to its blocker 5 (`_symtype_to_whyml`, the
  same shape)? A 6-line partial (compound emit_ir actual → `emit_ir` formal) exists in the ch28b
  scratch and was not landed for lack of a consumer.

### R5 — declare the missing self-map fields on the calling mixin

* **Markers (ch28b): 4.** `_handle_sum_call` (`_known_collection_elements/_sizes`),
  `_emit_membership` (`_module_str_list_constants`), `_emit_contract_logic_symbol`
  (`_imported_inductive_sigs`), and `_handle_array_set_stmt`. **Unlocks alone: 0.**
  `_handle_array_set_stmt` WRITES through a `getattr` alias (`known_sizes[v] = known_sizes[v] + 1`),
  which is MUTRECV-through-alias, not a declaration problem.
* **Cost (lessons f5/g5).** A declaration makes every clause that omits the field accountable on
  the HOLE-T arm (ceiling 0). Measured surface for this report (land27 mirror, `grep`): the
  number of mirror `#@ assigns` clauses naming each field is `_known_collection_sizes` 22,
  `_known_collection_elements` 22, `_imported_inductive_sigs` 1, `_module_str_list_constants` 1.
  The HOLE-T delta itself was NOT measured. Also, a class-level declaration reaches the emitted
  record only for some classes (g5).
* **Plus a hidden type cost.** ch28 found that `getattr(self, F, {}) or {}` on a faithful map needs
  the VERIFIED `types._rhs_yields_map` to see through `or {}`. That is a `types.py` re-proof.
* **Make-or-break.** For these 4 fields, measure underdeclaration TRAP / HOLE-T and survival TRAP
  before and after declaring them on `ExpressionEmissionMixin` / `StatementEmissionMixin`. Is there
  a state with all three brackets non-increasing (f5's rule), and does the declaration reach the
  record?

### R6 — leave-trusted (CERTIFIED-BOUNDARY) for the generic walkers (cluster G)

* **Scope.** 14 in-chain, 5 first, 30 latent. Complete DICT-only: the rebuilders
  `_rewrite_subscript_calls_in_stmt` (DICT) and `_rewrite_subscript_to_name` (PYVAL>DICT). The
  large typed handlers with an incidental walk (`_handle_subscript`, `_handle_len_call`,
  `_is_emit_ir_expr`) also carry getattr-default reflection (`wall-lessons.md:678-680`).
* **Why it is a boundary candidate.** D1 recognizers are whole-function templates (precision over
  recall), and no template exists for a `pyval -> pyval` rebuild. `c6557971` shows that COLLECTING
  walkers convert per template without a new cert. Rebuilders would need a new certified fold plus
  a bridge to whichever model their callers use (the `_check_noreturn` pyval→stmt_ir bridge lesson).
* **Soundness.** Leaving them trusted is an assumption, not a hole, provided their declared frames
  are honest. ch26 suspicion (a) lists 3 trusted bodies with `assigns \nothing` that append to a
  list parameter. These have no verified caller today.
* **Make-or-break.** Is a generic `pyval -> pyval` structural map-fold certifiable axiom-free AND
  recognizable on `_rewrite_subscript_to_name` with a non-vacuous twin? If not, record
  CERTIFIED-BOUNDARY (COST/SCALE) and stop spending on G.

### Route summary

| route | measured complete-chain unlocks alone | markers advanced (measured) | new cert? | dominant risk |
|---|---|---|---|---|
| R1 retype | 1 (`_tag_of_value`, landed) | N 19, P/J, X 18 | no | mover re-proof bill; unfaithful retype of non-IR values |
| R2a key-eq pin | 0 | every hval witness and reader | no (aligns with Phase2f) | twin flips on re-proof |
| R2b HArr for / `in` / keys | 0 | P 30, J 4 | small (len/nth lemma) | vacuity if R2a is absent |
| R2c nested store | 0 (`_rewrite_annotations` next) | P writers | yes (store path) | aliasing; contract shape |
| R3 per-kind payload | 0 | 3 | no if projector-only | wrong-kind constant reads let false claims prove |
| R4 cross-mixin typing | 0 | 3 | no | imports sibling frames verbatim |
| R5 field declarations | 0 | 4 | no | f5/g5 frame brackets; `types.py` re-proof |
| R6 leave-trusted G | — | 14 + 30 latent | — | none if frames are honest |

**Plausible combined yield:** N (19) minus the 3 misclustered minus the 1 landed leaves 15. The
markers whose ch27/ch28 chains consist only of R1+R3+R4+R5 items is small or empty: every measured
N chain also contains RECURSION, NESTED, MUTRECV, COMP or GETATTR (ch27 table). **No route set
built from this report is measured to convert more than ~2–4 markers.** The reviewer should
challenge that bound.

---

## 6. Honest limits of the evidence

1. **The census shapes are heuristic.**
   * `census.py` infers value shapes from defaults and consumers.
   * `cluster.py` is a key-set rule. It misclustered 3 of 19 N markers (ch27).
   * The numbers are read counts, not proofs.
2. **Chains are truncated.**
   * Pass 1 stops at 8 events.
   * Pass 2 (`--purge`, 14 events) finished only 50 of 198 incomplete rows
     (`chain-plan-g36.md:36-38`).
   * "COMPLETE" includes stopping at RIPPLE, which assumes callee-before-caller emission.
   * 9 of the 11 complete DICT-only chains had further blockers on re-measurement (§2.2). Ripple
     lengths in ch28 are `>=` lower bounds; `_emit_membership` was read to only 25% of its body.
3. **Neutralisation hides interactions.** A blocker neutralised in a scratch copy can mask whether
   the NEXT blocker's fix is compatible with the first one's fix.
4. **TC-clean is not landable.** Several statements above are L3-tc only. Whole-file proofs are
   OWED for every land27 mover: stage 2 has 21 LOW proofs queued (`driver-run-log.md:237`). The
   449 is not on main. ch28b's `run-soundness-planes.sh` reached 56/61 before the cap.
5. **My own probes are small.** `keq*.mlw` and `hit_probe.mlw` ran with 5 s timeouts, z3 + alt-ergo,
   through `heavy.sh`. "Timeout" is not "Invalid". The pinned-equality result is alt-ergo Valid on
   both goals and z3 Valid on one. No mirror file was proved.
6. **Unmeasured costs.**
   * R5's HOLE-T delta;
   * R2a's twin re-proof outcome on all 30 witnesses;
   * R1's mover set for any retype other than `_tag_of_value`;
   * the `_string_set_locals` getattr cited by ch26/ch27 for `_handle_augassign_stmt`: my `grep`
     finds the name nowhere in land27 `src/` (it may be built dynamically or renamed). Treat that
     row as stale.
7. **The chain-plan tables are not independent of the author.** They come from the same driver
   generation that wrote this report.

---

## 7. Questions for the reviewer (Gate R)

1. CONFIRM or REFUTE §3.2: on land27, are present-key hval reads unprovable, and does
   `ensures { result <-> a = b }` on `hpairs_key_eq` fix them without letting a twin prove? Is that
   spec acceptable under the 3-axiom ledger, on a par with `str_eq_op`?
2. CONFIRM or REFUTE §5: is this a modelling choice? Is R2c (nested by-reference stores) the only
   part that needs a memory model rather than a value model?
3. Rank R1–R6 by expected markers per unit cost. In particular, is there ANY marker the reviewer can
   show converting with at most two of {R1, R2a, R2b, R3, R4, R5}? Name it, and measure it.
4. For R3: is dominator-keyed projector routing sound in the emitter's current architecture, or does
   it need a typed refinement of emit_ir (one constructor per kind, payload typed)?
5. Should cluster G be declared CERTIFIED-BOUNDARY now (R6)?

---

## Appendix A — probe text (scratch, reproducible)

`hit_probe.py`, emitted with `heavy.sh <land27>/.venv/bin/python <land27>/src/pycsl/pycsl.py
hit_probe.py --import-path <land27>/src/pycsl --no-proof --keep-mlw` (L3-tc ✓):

```python
from typing import Any, Dict
PyVal = Any

#@ ensures \result == "Valid"
#@ assigns \nothing
def answer_hit() -> str:
    rec: Dict[str, PyVal] = {"prover-result": {"answer": "Valid"}}
    return (rec.get("prover-result") or {}).get("answer", "") or ""

#@ ensures \result == "Valid"
#@ assigns \nothing
def top_hit() -> str:
    rec: Dict[str, PyVal] = {"answer": "Valid"}
    return rec.get("answer", "") or ""
```

Emitted `top_hit`: `let py_rec = ref (map_update_some (const (None: option hval)) "answer"
(HStr "Valid")) in (let v_or = (match Map.get !py_rec "answer" with | Some v_ -> v_ | None ->
(HStr "") end) in if hval_truthy v_or then hstr_of v_or else "")`.

Results, `why3 prove -P {z3,alt-ergo} -t 5` (via `scratchpad/heavy/heavy.sh`, `. scratchpad/g29/env.sh`):

```
as emitted              answer_hit'vc  z3 Timeout   alt-ergo Timeout
                        top_hit'vc     z3 Timeout   alt-ergo Timeout
+ ensures {result <-> a = b} on hpairs_key_eq
                        answer_hit'vc  z3 Timeout   alt-ergo Valid (975 steps)
                        top_hit'vc     z3 Valid     alt-ergo Valid (116 steps)
  twin (ensures "Invalid")  both goals Timeout in both provers
```

Hand oracle `keq.mlw` (the land27 hval carrier and `pairs_get` verbatim):
`empty_read` Valid; `hit_read` Timeout. With the spec, `hit_read` is Valid (z3) and `hit_twin`
times out.

## Appendix B — commands

```
# census reproduction (any tree; R= points at an extraction of b9dc767e)
git archive b9dc767e getting-better/trusted-reasons.tsv getting-better/chain-plan-g36/chain-plan-g36.md src/pycsl | tar -x -C <d>
sed "s#^R=.*#R='<d>'#" getting-better/dict-value-wall/census.py > census.py
python3 -I census.py && python3 -I getting-better/dict-value-wall/cluster.py      # -> 423 399 423; N 19 13 4 2 ...
# counts
grep -rF '#@ \trusted' src/self-annotate/src | wc -l                            # 451 main / 449 land27
grep -rhE '^\s*#@ \\trusted' src/self-annotate/src | wc -l                      # 423 main / 421 land27
# hval key test, main vs land27
grep -n 'hpairs_key_eq (a b' src/pycsl/module6_whyml/preamble.py               # main :8046 `val`, land27 :8051 `val function`
```
