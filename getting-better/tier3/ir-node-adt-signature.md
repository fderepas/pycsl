# T3.0.1 — The CLOSED IR-node ADT signature (Module-6 emitter IR)

Ground-truth deliverable for `triage-ranked-tcb-tier3.md` Phase 0. This is the spec both P1
(emitter ADT) and P3 (formal-semantics Phase 7) build to.

**Sources of truth (all absolute):**
- `src/pycsl/ir_schema.py` — the closed typed sum (`ExprIR`/`StmtIR` dataclasses) + the
  `expr_from_dict` / `stmt_from_dict` wire-tag registries (lines 1053–1371) and the
  `_expr_to_dict` / `_stmt_to_dict` inverses. This is the **wire schema**.
- `src/pycsl/module6_whyml/{expressions,statements,stmt_control_flow,types,functions,preamble,auto_trust,ir_scanner}.py`
  — the emitter's dispatch (`ir.get("type") == "K"`).
- `src/formal-semantics/rocq/Phase1_AST.v` (`expr` 9 ctors, `contract_expr` 108 ctors, `stmt` 26 ctors)
  and `src/formal-semantics/lean/PyCSL/AST.lean` — the subject-language inductives.

---

## 0. Scope & ADT boundary (which ADT this is)

There are **three distinct node ADTs** in the tree; keep them separate:

| ADT | Where | Shape | In this signature? |
|---|---|---|---|
| **CSLNode** (Module 2) | `frontend/Module2_Parser.py` | Lark parse-tree wrapper | **NO** — parser-internal |
| **pure_ast** nodes | `frontend/pure_ast.py` | Python-AST reimplementation | **NO** — Phase-4 LEAVE-TRUSTED (~258), separate ADT |
| **ExprIR / StmtIR wire dict** (Module 5 → Module 6) | `src/pycsl/ir_schema.py` + consumed by `module6_whyml/*` | `{"type": K, ...}` / `{"stmt": K, ...}` | **YES — this is the target ADT** |

The emitter consumes **wire dicts** (`ir.get("type")`), NOT the typed `ExprIR` objects directly — the
dataclasses are a parallel closed model of the same wire shape (`to_dict∘from_dict == id`). The ADT we
must model is the **wire dict**. Two discriminant keys: `"type"` for expressions, `"stmt"` for
statements. Contract expressions **share the expression sum** (`ContractExprIR = ExprIR`, ir_schema.py
line 1009) — they are a *subset of tags*, not a separate discriminant.

**Type-class legend:** LEAF = `int`/`str`/`bool`/`Any`-scalar; SUB = one recursive `ir_node`;
LIST = `list ir_node`; LIST-STR = `list str`; SUB? = optional sub-node; OPEN = heterogeneous
`Dict[str,Any]` / `List[Dict]` (see §4); LEAF-STR-not-subnode = a string that names a var/field, **not**
a nested node (modeling trap).

---

## GROUP A — Expression nodes (84 wire tags; `"type"`-keyed)

Registry: `_expr_from_dict_inner`, ir_schema.py 1167–1371. `H:` = primary Module-6 handler.
`F:` = Rocq `expr`/`contract_expr` ctor (∅ = no formal ctor).

### A1. Literals & references
| tag | fields (type-class) | H / F |
|---|---|---|
| `Number` | value LEAF(int\|float, `Any`) | `_lower_number`/`_handle_int_expr` / `EInt`,`CInt` |
| `String` | value LEAF(str) | inline / `CStringLit` |
| `Bool` | value LEAF(bool) | inline / `CBoolLit` |
| `None` | — | inline / `CNoneLit` |
| `Var` | name LEAF(str) | `_handle_var_expr` / `EVar`,`CVar` |
| `Result` | — | inline / `CResult` |
| `RawWhyml` | whyml LEAF(str) | passthrough / ∅ |
| `UnknownPyExpr` | — | fail-closed / ∅ |
| `Nothing` | — | assigns-frame / ∅ |

### A2. Operators
| tag | fields | H / F |
|---|---|---|
| `BinOp` | op LEAF(str); left SUB; right SUB | `_handle_binop_expr` / `EBinOp`,`ECmp`,`CBinOp`,`CAnd`,`COr`,`CEq`… |
| `UnaryOp` | op LEAF(str); expr SUB | `_handle_unaryop_expr` / `ENeg`,`CNeg`,`CNot` |
| `StrConcat` | left SUB; right SUB | `_handle_strconcat_expr` / `CGStrConcat` |
| `Starred` | value SUB | inline (call-arg splat) / ∅ |

### A3. Container / attribute access
| tag | fields | H / F |
|---|---|---|
| `Subscript` | value SUB; index SUB | `_handle_subscript` / `ESubscript`,`CSubscript`,`CResultSubscript` |
| `Slice` | lower SUB; upper SUB; step LEAF(`Any`) | `_handle_slice` / `CSlice` |
| `FieldGet` | **object LEAF-STR-not-subnode**; field LEAF(str) | `_handle_fieldget` / `EFieldGet` |
| `Attribute` | object **SUB**; attr LEAF(str) | `_handle_attribute_expr` / `EFieldGet` |
| `Call` | func LEAF(str); args LIST; receiver SUB?(_ABSENT); keywords OPEN?(`list[{arg,value}]`, _ABSENT) | `_handle_call_expr` / `ECall`,`CCall` |
| `Tuple` | elts LIST | inline / `CGMkTuple2/3/4` |
| `ArrayLit` | elts LIST | `_handle_arraylit` / ∅ |
| `DictLit` | keys LIST; values LIST | `_handle_dictlit` / ∅ |
| `SetLit` | elts LIST | `_handle_setlit_expr` / ∅ |
| `ListComp` | elt SUB; generators **OPEN** (`List[Any]`, §4) | `_handle_listcomp` / ∅ |
| `DictComp` | key SUB; value SUB; generators OPEN | `_handle_dictcomp` / ∅ |
| `SetComp` | elt SUB; generators OPEN | `_handle_setcomp` / ∅ |
| `FString` | parts LIST | `_handle_fstring_expr` / ∅ |
| `Lambda` | params LIST-STR; body SUB | `_handle_lambda_expr` / `SLambda` |
| `NamedExpr` | target LEAF(str); value SUB | `_handle_named_expr_expr` / ∅ |
| `IfExpr` | test SUB; body SUB; orelse SUB | `_handle_ifexpr_expr` / ∅ |

### A4. Tuple / variant projection
| tag | fields | H / F |
|---|---|---|
| `MkTuple` | elts LIST | `_handle_mktuple_expr` / `CGMkTuple*` |
| `FstExpr` | tuple SUB | `_handle_fst_expr` / `CGFst` |
| `SndExpr` | tuple SUB | `_handle_snd_expr` / `CGSnd` |
| `ProjExpr` | tuple SUB; index LEAF(int) | `_handle_proj_expr` / `CGTrd`,`CGFth` |
| `CtorTest` | var LEAF(str); ctor LEAF(str) | `_handle_ctor_test_expr` / ∅ |
| `CtorPayload` | var LEAF(str); ctor LEAF(str); index LEAF(int) | `_handle_ctor_payload_expr` / ∅ |

### A5. String ghost ops
| tag | fields | H / F |
|---|---|---|
| `StrLength` | string SUB | `_handle_str_length_expr` / `CGStrLen` |
| `StrSub` | string SUB; lo SUB; hi SUB | `_handle_str_sub_expr` / `CGStrNth` |

---

## GROUP C — Contract-only expression nodes (subset of the expr sum)

Same discriminant (`"type"`), same `ExprIR` sum — but only produced/consumed in contract position.

### C1. Quantifiers & temporal
| tag | fields | H / F |
|---|---|---|
| `Forall` | var LEAF(str); body SUB; binder_type LEAF?(str,_ABSENT) | `_handle_forall`/preamble / `CForall` |
| `Exists` | var LEAF(str); body SUB; binder_type LEAF? | `_handle_exists` / `CExists` |
| `ForallItems` | key LEAF(str); val LEAF(str); map LEAF(str); body SUB | preamble / ∅ |
| `MapValueIs` | map LEAF(str); key SUB; value SUB | preamble / ∅ |
| `Old` | expr SUB | `_handle_old_expr` / `COld` |
| `OldField` | object LEAF(str); field LEAF(str) | `_handle_old_expr` / `COld`+`EFieldGet` |
| `At` | expr SUB; label LEAF(str) | `_handle_at_expr` / `CAt` |

### C2. Memory / array assertions
| tag | fields | H / F |
|---|---|---|
| `ArrayLen` | var LEAF(str) | `_handle_arraylen_expr` / `CLength` |
| `InGlobals` | name LEAF(str) | `_handle_in_globals_expr` / ∅ |
| `InScope` | name LEAF(str) | `_handle_in_scope_expr` / ∅ |
| `AssignsRegion` | base LEAF(str); low SUB; high SUB | assigns-frame / ∅ |
| `Valid` | base LEAF(str); length SUB | `_handle_valid_expr` / `CValid` |
| `Separated` | base1 LEAF; len1 SUB; base2 LEAF; len2 SUB | `_handle_separated_expr` / ∅ |
| `Length2D` | base LEAF; rows SUB; cols SUB | `_handle_length2d_expr` / ∅ |
| `Valid2D` | base LEAF; row SUB; col SUB | `_handle_valid2d_expr` / ∅ |
| `IsSorted` | base LEAF; lo SUB; hi SUB | `_handle_issorted_expr` / `CIsSorted` |
| `ArrayEq` | left SUB; right SUB | `_handle_arrayeq_expr` / ∅ |
| `Permutation` | left SUB; right SUB | `_handle_permutation_expr` / ∅ |
| `Sum` | base LEAF; lo SUB; hi SUB | `_handle_sum_node_expr` / `CSum` |
| `SliceAccess` | value SUB; slice SUB | `_handle_slice_access_expr` / `CSlice` |

### C3. Ghost array/map/set/list algebra
| tag | fields | H / F |
|---|---|---|
| `GhostCopy` | arr LEAF(str) | `_handle_ghost_copy_expr` / `CGCopy` |
| `GhostCopyRange` | arr LEAF(str); lo SUB; hi SUB | `_handle_ghost_copy_range_expr` / `CGCopyRange` |
| `GhostMake` | size SUB; default SUB | `_handle_ghost_make_expr` / `CGMake` |
| `MapEmpty` | — | `_handle_map_empty_expr` / `CGMapEmpty` |
| `MapGet` | dict SUB; key SUB | `_handle_map_get_expr` / `CGMapGet` |
| `MapSet` | dict SUB; key SUB; value SUB | `_handle_map_set_expr` / `CGMapSet` |
| `MapEq` | left SUB; right SUB | `_handle_map_eq_expr` / `CGMapEq` |
| `HasKey` | dict SUB; key SUB | `_handle_has_key_expr` / `CGHasKey` |
| `MapRemove` | dict SUB; key SUB | `_handle_map_remove_expr` / `CGMapRemove` |
| `SetEmpty` | — | `_handle_set_empty_expr` / `CGSetEmpty` |
| `SetAdd` | set SUB; elem SUB | `_handle_set_add_expr` / `CGSetAdd` |
| `SetRemove` | set SUB; elem SUB | `_handle_set_remove_expr` / `CGSetRemove` |
| `SetMem` | elem SUB; set SUB | `_handle_set_mem_expr` / `CGSetMem` |
| `SetUnion` | left SUB; right SUB | `_handle_set_union_expr` / `CGSetUnion` |
| `SetInter` | left SUB; right SUB | `_handle_set_inter_expr` / `CGSetInter` |
| `SetDiff` | left SUB; right SUB | `_handle_set_diff_expr` / `CGSetDiff` |
| `SetCard` | set SUB; lo SUB; hi SUB | `_handle_set_card_expr` / `CGSetCard` |
| `SetSubset` | left SUB; right SUB | `_handle_set_subset_expr` / `CGSetSubset` |
| `SetEq` | left SUB; right SUB | `_handle_set_eq_expr` / `CGSetEq` |
| `Nil` | — | `_handle_nil_expr` / `CGNil` |
| `Cons` | head SUB; tail SUB | `_handle_cons_expr` / `CGCons` |
| `Hd` | list SUB | `_handle_hd_expr` / `CGHd` |
| `Tl` | list SUB | `_handle_tl_expr` / `CGTl` |
| `ListLength` | list SUB | `_handle_list_length_expr` / `CGListLen` |
| `Nth` | list SUB; index SUB | `_handle_nth_expr` / `CGNth` |
| `Mem` | elem SUB; list SUB | `_handle_mem_expr` / `CGListMem` |
| `Append` | left SUB; right SUB | `_handle_append_expr` / `CGAppend` |

### C-fallback
| tag | fields | note |
|---|---|---|
| `Opaque` (`OpaqueExpr`) | **raw OPEN(`Dict[str,Any]`)** | escape hatch — ANY unrecognized tag lands here (§5) |

---

## GROUP B — Statement nodes (25 wire tags; `"stmt"`-keyed)

Registry: `_stmt_from_dict_inner`, ir_schema.py 1053–1148. `H:` = handler in
`statements.py`/`stmt_control_flow.py`. `F:` = Rocq `stmt` ctor.

| tag | fields (type-class) | H / F |
|---|---|---|
| `Assign` | target LEAF(str); value SUB | `_handle_assign_stmt` / `SAssign` |
| `AugAssign` | target LEAF(str); op LEAF(str); value SUB | `_handle_augassign_stmt` / `SAugAssign` |
| `ArraySet` | array SUB; index SUB; value SUB | `_handle_array_set_stmt` / `SArraySet` |
| `DelSubscript` | array SUB; index SUB | `_handle_del_subscript_stmt` / ∅ |
| `ArraySliceSet` | array SUB; lower SUB; upper SUB?(opt); value SUB | `_handle_array_slice_set_stmt` / ∅ |
| `If` | test SUB; body LIST; orelse LIST | `_handle_if_stmt` / `SIf` |
| `While` | line LEAF(int); test SUB; invariants LIST; variants LIST; body LIST | `_handle_while_stmt` / `SWhile` |
| `For` | line LEAF(int); target LEAF(str); iter SUB; invariants LIST; variants LIST; body LIST; allow_iteration_mutation LEAF(bool); lineno LEAF(int) | `_handle_for_stmt` / `SFor` |
| `Return` | value SUB?(opt) | `_handle_return_stmt` / `SReturn` |
| `Expr` | value SUB | `_handle_expr_stmt` / ∅ (`SCall` if call) |
| `Try` | body LIST; **handlers OPEN(`List[Dict]`)**; orelse LIST; finalbody LIST | `_handle_try_stmt` / `STryCatch` |
| `Match` | subject SUB; **cases OPEN(`List[Dict]`, pattern sub-ADT)** | `_handle_match_stmt` / ∅ |
| `CriticalSection` | mutex LEAF(str); body LIST; assume_invariant SUB?(opt); prove_invariant SUB?(opt) | `_handle_critical_section_stmt` / `SCritical` |
| `FieldAssign` | object LEAF(str); field LEAF(str); value SUB | `_handle_fieldassign_stmt` / `SFieldAssign` |
| `FieldAugAssign` | object LEAF(str); field LEAF(str); op LEAF(str); value SUB | `_handle_fieldaugassign_stmt` / `SFieldAugAssign` |
| `TupleUnpack` | targets LIST-STR; value SUB | `_handle_tuple_unpack_stmt` / `STupleUnpack` |
| `GhostAssign` | target LEAF(str); value SUB; op LEAF(str); ghost_type LEAF(str) | `_handle_ghost_assign_stmt` / `SGhostAssign` |
| `GhostArraySet` | target LEAF(str); index SUB; value SUB | `_handle_ghost_array_set_stmt` / ∅ |
| `Label` | name LEAF(str) | inline / `SLabel` |
| `Raise` | exc_type LEAF?(str,opt); exc_value SUB?(opt) | inline / `SRaise` |
| `Assert` | test SUB; msg LEAF(str,_ABSENT) | `_stmts_to_whyml` inline / `SAssert` |
| `Pass` | — | `SSkip` |
| `Break` | — | `SBreak` |
| `Continue` | — | `SContinue` |
| `ProofAssert` | assert_kind LEAF(str); test SUB; origin LEAF?(str,_ABSENT) | `_stmts_to_whyml` inline / `SAssert` |
| `Opaque` (`OpaqueStmt`) | **raw OPEN(`Dict`)** | escape hatch (§5) |

Rocq `stmt` also has `SSeq` (statement sequencing — the emitter models this as `List` body, no wire
tag), `SGhostDecl`, `SThreadEntry`, `SAcquires`, `SReleases`, `SCall`, `SLambda` — see §6 mapping.

---

## 4. The nested heterogeneous sub-structures (sub-ADTs, NOT `ir_node`)

These fields hold `Dict[str,Any]` / `List[Dict]` with **their own discriminant key** — they are
distinct mini-ADTs the main `ir_node` variant must reference. They are the load-bearing modeling risk.

**Match-pattern sub-ADT** (`MatchStmt.cases[i]["pattern"]`, key = `"pattern"`;
`stmt_control_flow.py::_render_match_pattern` 710–740):
- `Wildcard` | `Value`(value SUB) | `Capture`(name LEAF) | `Or`(patterns LIST-of-pattern) | `Constructor`(name LEAF; args LIST-of-pattern) → **mutually recursive with itself, closed 5-ctor sub-ADT**.
- A case dict = `{"pattern": <pattern>, "body": List[stmt], "guard": <expr>?}`.

**Comprehension-generator sub-ADT** (`ListComp/DictComp/SetComp.generators`, `List[Any]`;
`expressions.py` 5637–6039): each generator = `{"target": str, "iter": <expr SUB>, "ifs": List[<expr SUB>]}`. **`generators` is typed `List[Any]`** — no closed dataclass; shape is convention-only.

**Try-handler sub-ADT** (`TryStmt.handlers`, `List[Dict[str,Any]]`;
`stmt_control_flow.py` 409–460): each handler = `{"type": <exc str>?, "name": str?, "body": List[stmt]}`. **`List[Dict[str,Any]]`** — not a closed dataclass.

**Call-keyword sub-ADT** (`CallExpr.keywords`, `Any`/`List[{arg,value}]`, ir_schema.py 1211): each = `{"arg": str, "value": <expr SUB>}`. Optional (`_ABSENT`).

**Impact:** these four are heterogeneous `Dict`/`List[Dict]` fields. A faithful WhyML ADT must lift
each into its own pure variant (`pattern`, `generator`, `handler`, `keyword`), and the `ir_node`
variant references them. Only `pattern` is a clean closed recursive variant; `generators`/`handlers`/
`keywords` are typed `Any`/`List[Dict]` in ir_schema (convention-only shape), so pinning them closed
requires reading the emitter to fix their key set.

---

## 5. CLOSEDNESS VERDICT

**Verdict: the typed sum is CLOSED-with-a-total-fallback; the emitter's-eye view is OPEN (a strict
superset of the registry). This is a qualified Phase-0 GO with named caveats, not a clean GO.**

### 5a. Closed core (GOOD)
The `expr_from_dict`/`stmt_from_dict` registries are an explicit finite tag list (84 expr + 25 stmt =
**109 named tags**) with fully-typed fields — no `**kwargs`, no runtime-computed discriminant. Modeling
this core as a WhyML variant is feasible.

### 5b. OPEN kind #1 — the `Opaque` total fallback (STRUCTURAL, not eliminable trivially)
Both registries **end** in `return OpaqueExpr(kind=k or "Opaque", raw=dict(d))` / `OpaqueStmt(...)`
(ir_schema.py 1371, 1148). ANY tag not in the list is accepted and its arbitrary dict preserved in
`raw: Dict[str,Any]`. The sum is closed only because `Opaque` swallows the complement. A faithful ADT
needs an `Opaque (map str value)` catch-all constructor **or** a proof the emitter never faithfully
reads inside `raw` (it does not lower Opaque nodes — it fails-closed — which is the escape valve to
lean on).

### 5c. OPEN kind #2 — emitter-consumed tags OUTSIDE the registry (11 confirmed synonyms/legacy)
The emitter dispatches on `ir.get("type")` for tags that ir_schema has **no class for** (they parse to
`OpaqueExpr` but the emitter still branches on them from the raw dict). Confirmed by tag-diff:

| emitter tag | meaning | site |
|---|---|---|
| `BoolOp` | boolean and/or (alt of `BinOp`) | expressions.py:803, types.py:344 |
| `Compare` | chained comparison | types.py:343 |
| `Constant`, `Num` | Python-AST numeric-literal synonyms of `Number` | auto_trust.py:80 |
| `Name` | Python-AST synonym of `Var` | preamble.py:2854 |
| `List`, `ListLit`, `ListLiteral` | synonyms of `ArrayLit` | expressions.py:1554, statements.py:246 |
| `Set` | synonym of `SetLit` | expressions.py:1613 |
| `ChainedSubscript` | multi-index subscript | auto_trust.py:261 |
| `OldVar` | contract old-variable | functions.py:1405,1607,1755,1876 |

These must be **normalized to their canonical registry tag before the ADT boundary**, or added as
explicit constructors. Until then the emitter's dispatch alphabet ≠ the ADT's constructor set — a
soundness gap for any self-verification that dispatches on `.get("type")`.

#### 5c-RESOLVED (Phase-1 prereq, `commit feat(tier3-p1)`)
The eleven tags were classified by reading their producers/consumers end-to-end. The finding: **all
eleven are `normalize-to-X`, NONE is `add-ctor`** — and the emission-side normalization is **already
in place**. Each is an *upstream* node name (a CPython-`ast`/`pure_ast` node type, or a
`Module2_Parser` CSL-parse node), NOT an IR wire tag:

| upstream tag | canonical (Module-5 emits) | Module-5 site |
|---|---|---|
| `BoolOp` | `BinOp` | `_py_expr_boolop` (fold) |
| `Compare` | `BinOp` | `_py_expr_compare` |
| `Num` | `Number` | numeric literal |
| `Constant` | `Number`/`Bool`/`String`/`None` | literal |
| `Name` | `Var` | `_csl_var`/`_py_expr_name` |
| `List` | `ArrayLit` | list-literal node |
| `ListLit` | `ArrayLit` | *phantom* (no wire-dict form) |
| `ListLiteral` | `ArrayLit` | *phantom* |
| `Set` | `SetLit` | set-literal node |
| `ChainedSubscript` | `Subscript` | `_csl_chained_subscript` |
| `OldVar` | `Old` | `_csl_old` |

Key facts established: (1) `_py_expr_boolop`/`_py_expr_compare` both emit `BinOp`; `_csl_old` emits
`Old`/`OldField`; `_csl_chained_subscript` emits nested `Subscript`; literals/`Name`/`List`/`Set`
translate to `Number`/`Var`/`ArrayLit`/`SetLit`. (2) **None of the eleven is constructed anywhere in
`src/pycsl/`** as `{"type": <tag>}` (grep-verified) — they exist only as pre-Module-5 AST/CSL nodes
and as *defensive* string-matches in Module 6. (3) Module 6 consumes **only** Module-5 IR, so those
matches are **dead** against real IR. (4) `add-ctor` is wrong (not distinct kinds); a registry
tag-rename is also wrong (field shapes differ: `BoolOp.values` list vs `BinOp.left/right`, `Name.id`
vs `Var.name`, `Num.n` vs `Number.value`).

**Reconciliation implemented (additive, emission-inert, byte-diff 0):**
- `ir_schema.py::IR_TAG_ALIASES` — the canonical mapping above, the single source of truth;
  `is_upstream_alias_tag()` tests membership.
- `module6_whyml/expressions.py::_expr_to_whyml` — asserts an `OpaqueExpr` whose `kind` ∈
  `IR_TAG_ALIASES` is **never** lowered inside `raw` (the §5b Opaque fail-closed boundary, sharpened
  for the eleven). Live (fires when fed such a node) yet inert on the corpus (Module 5 never emits
  them → byte-diff 0).
- `docs/ir.md §7a` — the front-end normalization contract (registry alphabet is closed).

**Consequence for Phase 1:** the future `ir_node` ADT is built over the *canonical* registry tags
only. Because the eleven can never inhabit a valid IR node (Module 5 normalizes; the emitter
fails-closed), every emitter arm dispatching on an upstream tag is **provably dead** in the ADT model
— so the "Opaque-in-the-ADT but live-in-the-emitter" soundness gap is closed. The residual dead
defensive arms in Module 6 (~43 sites) were **left in place** (removing 43 working guards is a
risky, subtractive change out of scope for this additive prereq); they are harmless and
provably-dead under the ADT.

### 5d. OPEN kind #3 — `Any`-typed & heterogeneous fields (§4)
`generators: List[Any]`, `handlers: List[Dict[str,Any]]`, `cases: List[Dict[str,Any]]`,
`keywords: Any`, plus leaf-`Any` fields `Number.value`, `Slice.step`, `FieldGet.object`. Not a hard
STOP (their shapes are recoverable by convention) but each is an un-pinned sub-schema.

### 5e. Modeling trap — `FieldGet.object` is a LEAF string, `Attribute.object` is a SUB-node
`FieldGetExpr.object: Any` is documented "str ('self') or var name; **not** a nested ExprIR"
(ir_schema.py 578), while `AttributeExpr.object` **is** a sub-node. Two near-identical tags with
opposite recursion structure — the ADT sketch must not uniformly make `object` a sub-node.

**Bottom line:** the closed *core* (§5a) is a GO for the T3.0.2 spike on a representative subset. But a
**faithful whole-surface** ADT is NOT closed today because of §5b (Opaque catch-all) and §5c (11
out-of-registry emitter tags). Phase 0 should proceed on the closed core and **treat §5c normalization
+ §5b Opaque handling as prerequisite work, flagged loudly to the human** per the STOP-gate.

---

## 6. Emitter-tag ↔ formal-ctor mapping coverage

- **Exprs:** the Rocq `expr` inductive is tiny (9 ctors: EInt/EVar/ESubscript/ELen/EBinOp/ENeg/ECmp/
  EFieldGet/ECall) — the *executable* fragment. `contract_expr` (108 ctors, incl. 37 ghost atoms)
  covers the contract/ghost tags: strong coverage for the C1–C3 ghost families
  (`CG*` ↔ Map/Set/List/Str/Tuple ghost ops map 1:1, ~40 pairs). **Mapped ≈ 60 / 84 expr tags.**
- **Unmapped expr tags (no formal ctor, ∅ above):** `RawWhyml`, `UnknownPyExpr`, `Nothing`, `Starred`,
  `ArrayLit`, `DictLit`, `SetLit`, `ListComp`, `DictComp`, `SetComp`, `FString`, `NamedExpr`, `IfExpr`,
  `CtorTest`, `CtorPayload`, `ForallItems`, `MapValueIs`, `InGlobals`, `InScope`, `AssignsRegion`,
  `Separated`, `Length2D`, `Valid2D`, `ArrayEq`, `Permutation`, `Opaque` (≈24). Most are
  emitter/desugaring conveniences the formal model handles at a lower level (comprehensions desugar to
  loops; f-strings to concat) — **the Phase-3 anchor must either add ctors or prove the desugaring.**
- **Stmts:** Rocq `stmt` = 26 ctors. Clean 1:1 for the imperative core (Assign/AugAssign/ArraySet/If/
  While/For/Return/Break/Continue/Assert/TupleUnpack/GhostAssign/Label/Raise/Try↦STryCatch/Field*/
  Critical/Lambda). **Unmapped stmt tags:** `DelSubscript`, `ArraySliceSet`, `Match`, `GhostArraySet`,
  `Expr` (partial, ↦SCall). Formal-only (no wire tag): `SSeq` (= body list), `SGhostDecl`,
  `SThreadEntry`, `SAcquires`, `SReleases`.
- **Mapping coverage overall: ≈ 65% of wire tags have a direct formal ctor; the ghost-algebra families
  are the strongest (near-total); the desugaring-convenience expr tags are the weakest.** This is the
  exact Phase-3 (LINK-3) surface to certify.

---

## 7. Proposed WhyML variant sketch (PURE — no mutable field; lists = `list`, never `array`)

```whyml
(* Leaf value carried by literal nodes; keep monomorphic per Why3 purity. *)
type ir_num = INum int | IReal real            (* Number.value : int|float *)

(* Sub-ADTs (§4) — each pure, closed, referenced by ir_node. *)
type pattern =
  | PWildcard
  | PValue    ir_node
  | PCapture  string
  | POr       (list pattern)
  | PConstructor string (list pattern)          (* mutually recursive w/ ir_node *)
with generator = { g_target : string; g_iter : ir_node; g_ifs : list ir_node }
with handler   = { h_type : option string; h_name : option string; h_body : list ir_node }
with keyword   = { k_arg : string; k_value : ir_node }

with ir_node =
  (* --- literals & refs --- *)
  | Number ir_num | String string | Bool bool | Null | Var string | Result
  | RawWhyml string | UnknownPy | Nothing
  (* --- operators --- *)
  | BinOp string ir_node ir_node | UnaryOp string ir_node
  | StrConcat ir_node ir_node | Starred ir_node
  (* --- access --- *)
  | Subscript ir_node ir_node | Slice ir_node ir_node
  | FieldGet string string                        (* object is a LEAF string, NOT a sub-node *)
  | Attribute ir_node string                      (* object IS a sub-node — cf. FieldGet *)
  | Call string (list ir_node) (option ir_node) (list keyword)  (* func args receiver keywords *)
  | Tuple (list ir_node) | ArrayLit (list ir_node) | SetLit (list ir_node)
  | DictLit (list ir_node) (list ir_node)         (* keys values *)
  | ListComp ir_node (list generator)
  | DictComp ir_node ir_node (list generator)
  | SetComp ir_node (list generator)
  | FString (list ir_node) | Lambda (list string) ir_node
  | NamedExpr string ir_node | IfExpr ir_node ir_node ir_node
  (* --- tuple/variant projection, str ghost --- *)
  | MkTuple (list ir_node) | FstE ir_node | SndE ir_node | ProjE ir_node int
  | CtorTest string string | CtorPayload string string int
  | StrLength ir_node | StrSub ir_node ir_node ir_node
  (* --- contract-only (C1–C3): Forall/Exists/Old/At/Valid/Sum/IsSorted/... --- *)
  | Forall string ir_node | Exists string ir_node
  | Old ir_node | OldField string string | At ir_node string
  | ArrayLen string | Valid string ir_node | IsSorted string ir_node ir_node
  | Sum string ir_node ir_node | SliceAccess ir_node ir_node
  (* ... Map*/Set*/list (Nil/Cons/Hd/Tl/Nth/Mem/Append) ghost algebra: 1:1 with CG* ... *)
  (* --- statements (share the sum, or split into ir_stmt) --- *)
  | SAssign string ir_node | SAugAssign string string ir_node
  | SArraySet ir_node ir_node ir_node | SIf ir_node (list ir_node) (list ir_node)
  | SWhile int ir_node (list ir_node) (list ir_node) (list ir_node)
  | SFor  int string ir_node (list ir_node) (list ir_node) (list ir_node) bool int
  | SReturn (option ir_node) | STry (list ir_node) (list handler) (list ir_node) (list ir_node)
  | SMatch ir_node (list (pattern, list ir_node))
  | SFieldAssign string string ir_node | SCritical string (list ir_node) (option ir_node) (option ir_node)
  | STupleUnpack (list string) ir_node | SGhostAssign string ir_node string string
  | SLabel string | SRaise (option string) (option ir_node)
  | SAssert ir_node | SPass | SBreak | SContinue | SProofAssert string ir_node
  (* --- escape hatch (§5b) --- *)
  | Opaque string                                 (* raw dict UNMODELED; emitter fails-closed on it *)
```

Recommendation: **split `ir_node` (expr) and `ir_stmt` (stmt) into two mutually-recursive variants**
(cleaner discriminant, matches the two wire keys `"type"`/`"stmt"`). Termination `variant` = subtree
size over the `list`/mutual-recursion structure. **Why3 purity holds** iff every list field is `list`
(not `array`) and no constructor carries a mutable record — satisfied above.

---

## 8. Report — hard-to-model node kinds (Phase-1 risk register)

1. **`Opaque` (both sums)** — the catch-all `raw: Dict`. Cannot be faithfully modeled as data; must be
   an inert `Opaque` ctor the emitter never reads inside. Load-bearing on "emitter fails-closed on
   Opaque" being TRUE. **Highest risk.**
2. **§5c out-of-registry tags (BoolOp/Compare/Name/Num/Constant/List/ListLit/ListLiteral/Set/
   ChainedSubscript/OldVar)** — the emitter's dispatch alphabet exceeds the ADT. Requires a
   normalization pass or 11 extra ctors before the self-verification is faithful.
3. **Mutual recursion `ir_node ↔ pattern`** (Match) and `ir_node ↔ generator/handler/keyword` — Why3
   `type … with …` handles it, but the spike (T3.0.2) must exercise it, not just the flat subset.
4. **`generators: List[Any]` / `handlers: List[Dict]` / `keywords: Any`** — un-pinned sub-schemas; must
   fix their key set from the emitter (they lack ir_schema dataclasses).
5. **String-keyed maps inside container literals** (`DictLit` keys/values, `MapSet`) — modeled fine as
   parallel `list ir_node`, but a faithful *dict semantics* (as opposed to the AST shape) is a map —
   keep the ADT purely structural (parallel lists), not semantic.
6. **`FieldGet.object` LEAF-string vs `Attribute.object` SUB-node** — asymmetry trap (§5e); a naive
   "object is a sub-node" rule is WRONG for `FieldGet`.
7. **`Number.value: Any`** (int|float) — needs a small `ir_num` variant, not a bare `int`, to stay
   faithful (no int-coercion — cf. no-more-int doctrine).

**COUNT SUMMARY:** expr = **84** wire tags (+`Opaque`); stmt = **25** (+`Opaque`); contract-expr =
subset of the 84 (≈50 contract-only tags C1–C3). Emitter-consumed non-registry tags = **11**.
Sub-ADTs = **4** (pattern[closed-5], generator, handler, keyword). Formal-ctor coverage ≈ **65%**.

**CLOSEDNESS: qualified GO** — closed core is real and spike-able; whole-surface faithfulness is
blocked on the `Opaque` fallback + 11 out-of-registry tags. Flag both to the human before Phase-1 src edits.

---

## 9. Phase-1 REALIZED — the EXPR-family recognizer (tier3-p1 increment 2, `feat(tier3-p1)`)

The Phase-0 spike design is now realized in the live emitter for the **EXPR node family**
(T3.1.1 + T3.1.2 + T3.1.4). Bounded: stmt/contract families are later increments.

**T3.1.1 — the `emit_ir` variant type.** `module6_whyml/preamble.py::_emit_exprir_theory`
emits `type ir_num = INum int | IReal real` (the faithful numeric leaf, risk 7 / no-more-int)
and extends the pre-existing `emit_ir` sum with the `IrBinOp op left right` constructor —
`list`-of-subnode where needed, NO `array` inside the pure sum, no mutable field (Why3 purity
holds, §7 constraints). Gated on an IR-node-typed param/local (`_uses_ir_node_param`,
`Module6_WhyMLTranspiler.transpile`) OR a `@mutable_state` class; the corpus has neither, so
non-ADT emission is byte-identical (743/754 reference `.mlw` unchanged; the 11 pre-existing
emit_ir tests gain the additive declarations and still prove).

**T3.1.2 — discriminant + projection.** `expressions.py`: `node.get("type") == "BinOp"` lowers
to the constructor discriminant `(is_binop node)` (spike LAW 1, `_emit_ir_kind_discriminant` —
gated NOT-`@mutable_state` so the mirror keeps its `kind_of` path); `node.get("op")` →
`op_of` (STRING leaf), `node.get("left")`/`.get("right")` → `left_of`/`right_of` (SUB-nodes);
the `FieldGet.object`-leaf vs `Attribute.object`-subnode asymmetry (§5e, risk 6) is honored
(a leaf projection yields `string`, a sub-node projection yields `emit_ir`). Unrecognized kind /
`Opaque` → fail-closed.

**T3.1.4 — structural recursion.** `functions.py::_emit_function` injects a function-level
`variant { size <param> }` for a function recursive over its `emit_ir` param (the piece
`ir_scanner` lacked). `size` is a structural `let rec function` (`ensures { result >= 1 }`,
`variant { e }`); the guarded lemmas `size_left_dec`/`size_right_dec` (`is_binop e →
size (left_of e) < size e`, PROVEN, no axiom) discharge each recursive call's decrease.

**Gates green:** Phase-0 spike still discharges (both provers, no axiom); reference locks 0878
(POSITIVE) / 0879 (NEGATIVE twin); full-corpus byte-diff = 0 on all non-ADT programs (the 11
emit_ir tests differ purely additively and still pass, 31/31 in range); IR unchanged
(`IR_VERSION` 1.4, conformance goldens untouched); feasibility check — the real mirror method
`_handle_map_get_expr` ported with an `ExprIR` param now lowers via the ADT (the tier-1
`unbound type symbol 'emit_ir'` is GONE) and fully proves; mirror reverted. No new axiom, no
`\trusted` increase. **Certificate-backed by the Phase-0 spike; awaits Phase-3 mechanized-proof
integration** (co-lands per the coupling rule).
