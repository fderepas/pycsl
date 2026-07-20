# ast-modeling-scope.md — build-scope + feasibility probe for statement/definition-node AST modeling

**Actor:** design+feasibility-probe for the self-tcb-reduction giants front.
**Mandate:** SCOPE the `targeted-refactor.md` §2c gating prerequisite ("statement/definition-node AST
modeling") and run ONE decisive feasibility probe. Measure-before-build; do NOT build the full feature.
**Probe verdict (headline):** the modeling is **FEASIBLE at the Why3 level for the shallow (non-`ast.walk`)
collectors** — no type-rejection, no unavoidable vacuity. The remaining wall is **build-effort** (multi-file
tool wiring + a certificate), NOT a soundness/Why3 impossibility. `ast.walk` is a **separate, much larger**
wall (recursive-descent + termination) and gates 3 of the 7 giants. Tree left byte-identical to HEAD.

---

## 0. What already exists (the reuse floor — read before building)

The **expression**-node surface is fully modeled: the `emit_ir` ADT (preamble.py `_emit_exprir_theory`) +
`kind_of`/`is_var`/`is_sub`/`is_attribute`/`name_of`/`svalue_of`/`sindex_of`/`elts_of` (expressions.py) +
the `_PURE_AST_FIELD_TABLE` structural harvest (ir_resolve.py) that types a handler's `stmt`/`expr` param as
a record with typed fields. Statement nodes ARE partly present, but only as **disjoint opaque `py_*_node`
types** (`py_assign_node`, `py_classdef_node`, `py_try_node`, …) with opaque `val function` field readers,
each consumed by ONE already-converted `_py_stmt_*` handler that receives a SINGLE pre-typed node.

**The decisive gap (POC-confirmed, re-confirmed here):** a *giant* iterates `node.body` — a LIST of raw
statement/definition AST nodes — and does `isinstance(child, ast.Assign)` dispatch on the ELEMENTS. Today:
- `node.body` → the generic attribute reader `get_body node : int` (opaque), iterated by `iter_get` → each
  child is an **opaque int**;
- `isinstance(child, ast.Assign)` → `isinstance_op 0 0` (**vacuous** — no statement discriminant exists);
- the statement-list dispatcher `_py_stmts_to_ir(stmts: List[ast.stmt])` is **itself still `\trusted`**
  (`return []`) — the list-iteration-with-isinstance-dispatch pattern was NEVER converted, even for the
  stmt family. The per-statement handlers convert only because each gets ONE typed node via its signature.

There is **no discriminated union of statement nodes** for `isinstance` to branch on. That union is the build.

---

## 1. EXACT surface enumeration (the matrix that bounds the build)

Node-type × (discriminant / child-list reader / field readers) × which of the 7 scanned giants use it.
`✓ = reuse existing`, `NEW = must build`, `WALL = value-model / reflection wall`.

### 1a. Iterables (child-lists) each giant walks
| Iterable | Reader status | Giants |
|---|---|---|
| `module_node.body` (stmt list) | **NEW** `module_body_ast : py_module_node → psl` | typevar_registry, final_registry |
| `ClassDef.body` (stmt list) | **NEW** `class_body_ast : py_classdef_node → psl` | class_constants, class_fields, final_registry |
| `FunctionDef.args.args` (arg list) | **NEW** `func_args_ast → arglist` | function_symbol_table |
| `node.type_params` (typevar list) | **NEW** `type_params_ast → tplist` | type_params |
| `node.bases` (expr list) | **✓** `class_bases_ast` (bases are EXPRs → emit_ir irlist) | type_params, class_fields |
| `call.keywords` (keyword list) | **NEW** `call_keywords_ast → kwlist` | typevar_registry |
| `stmt.targets` (expr list) | **✓** emit_ir irlist (`targets[0]`, `len`) | class_constants, typevar_registry, symbol_table |
| `Tuple.elts` / `For.target.elts` | **✓** `elts_of` (emit_ir irlist) | union_arms, symbol_table |
| BinOp `|` while-stack flatten | **✓** emit_ir `left_of`/`right_of` + is_binop | union_arms |
| **`ast.walk(node)`** (ALL descendants) | **WALL** `ast_walk` real recursive-descent (see §2 / §5) | class_fields, final_registry, symbol_table(×3) |

### 1b. isinstance discriminants each giant needs
| ast class tested | Discriminant status | Giants |
|---|---|---|
| `ast.Name` / `Attribute` / `Subscript` / `Call` / `Tuple` / `Constant` / `Slice` (on an EXPR child) | **✓** `is_var`/`is_attribute`/`is_sub`/`is_call`/`is_tuple`/`is_str`+`is_num`/`is_slice` | all |
| `ast.BinOp` + `ast.BitOr` op | **✓** `is_binop` + op string | union_arms |
| `ast.Dict`/`ast.Set`/`ast.List` (RHS shape) | **NEW-ish** `is_dict`/`is_set`/`is_listlit` emit_ir discriminants (add kind arms) | class_fields |
| **`ast.Assign`** (on a body CHILD) | **NEW** `is_assign_node` (pyast_stmt) — PROBE-VALIDATED | class_constants, typevar_registry, class_fields, final_registry, symbol_table |
| **`ast.AnnAssign`** (body child) | **NEW** `is_annassign_node` | class_constants, class_fields, final_registry, symbol_table |
| **`ast.ClassDef`** (body child) | **NEW** `is_classdef_node` | type_params, final_registry |
| **`ast.FunctionDef`** (body child, `.name=='__init__'`) | **NEW** `is_functiondef_node` + `funcdef_name` string | class_fields, final_registry |
| `ast.For` (walk child) | **NEW** `is_for_node` | symbol_table |
| **`type(tp).__name__`** / `type(x).__name__ == "Index"` | **WALL** value-model reflection (§3 of emit-ir-conversion-lessons) | type_params, symbol_table |

### 1c. Element-field readers each giant needs
| Field read | Reader status | Giants |
|---|---|---|
| `child.targets[0]` / `.target` (→ emit_ir) | **NEW** `stmt_target0 : pyast_stmt → emit_ir` | class_constants, typevar_registry, symbol_table |
| `child.value` (→ emit_ir / option) | **NEW** `stmt_value : pyast_stmt → emit_ir` (or option) | class_constants, typevar_registry, class_fields, symbol_table |
| `child.annotation` (→ emit_ir) | **NEW** `stmt_annotation : pyast_stmt → emit_ir` | class_fields, symbol_table |
| `X.id` / `X.attr` (on the emit_ir target) | **✓** `name_of` | all |
| `child.name` (ClassDef/FunctionDef name string) | **NEW** `def_name : pyast_stmt → string` | final_registry, class_fields |
| `arg.arg` (parameter name string) | **NEW** `arg_name : pyast_arg → string` | symbol_table |
| `tp.name` / `tp.bound` | **NEW** `tp_name`/`tp_bound` (bound is expr → emit_ir) | type_params |
| `kw.arg` / `kw.value` | **NEW** `kw_arg : string` / `kw_value : emit_ir` | typevar_registry |
| `getattr(child,'csl_ghost_assigns',[])`, `ga.target/op/declared_type` | **✓** opaque weave-attr readers (the §3 `csl_mutex_ast` pattern) | symbol_table |
| `target in field_names` / `x in self._cur_func_symtab` (Set membership) | **✓** opaque predicate (the `symtab_mem` pattern) | class_constants, symbol_table |
| helper calls (`_const_int_value`, `_field_type_from_annotation_inst`, `_array_init_size`, `_m5_get_*`, `_is_final_annotation`) | **✓** stay trusted sub-dispatchers / already modeled (`is_final_ann`) | class_constants, class_fields, final_registry |

### 1d. Per-giant classification (the ordering that follows from the matrix)
| Giant (line) | `ast.walk`? | reflection? | new node-union? | class |
|---|---|---|---|---|
| `_collect_class_constants` (2708) | no | no | Assign/AnnAssign | **FEASIBLE — PROBE TARGET** |
| `_collect_typevar_registry` (1919) | no | no | Assign + kw/Call readers | **FEASIBLE** |
| `_collect_union_arms` (2942) | no | no | none (pure EXPR recognizer + `ast.Constant(None)` construction + while-stack) | **FEASIBLE (expr-only)** |
| `_collect_type_params` (1866) | no | **`type(tp).__name__`** | ClassDef + type_params list | **PARTIAL — reflection wall on the kind read** |
| `_collect_class_fields` (2472) | **yes** (1) | no (dataclass branch is walk-free) | Assign/AnnAssign/FunctionDef + is_dict/set/list | **WALK-BLOCKED (dataclass branch alone is feasible)** |
| `_collect_final_registry` (3142) | **yes** (1) | no | Assign/AnnAssign/ClassDef/FunctionDef | **WALK-BLOCKED** |
| `_build_function_symbol_table` (3829) | **yes (×3)** | **yes** (`type(_inner).__name__`) + weave attrs + nested closures | Assign/AnnAssign/For/arg | **WALK+REFLECTION-BLOCKED (the giant of giants)** |

---

## 2. Reuse vs new — per reader/discriminant, with the `ast.walk` assessment

**Reuse (already in tree):** the whole `emit_ir` expr ADT + discriminants/projectors; `class_bases_ast`
(bases are exprs); `is_final_ann`/`is_final_ann_prog` (already models `_is_final_annotation` — a gift for
final_registry); `bases_has_name`; the `symtab_mem` opaque-membership pattern for Set-membership; the
`csl_mutex_ast`/`get_*` opaque weave-attr pattern; `map_update_some`/`Seq.snoc` collection builders (the
emission probe already confirmed these build real collections — the accumulator is NOT the blocker); the
`_PURE_AST_FIELD_TABLE` structural-harvest mechanism for typing a param as a record.

**Genuinely new (must build):**
- A `pyast_stmt` **discriminated union** (flat for the shallow collectors) with `stmt_node_kind_of` +
  `is_assign_node`/`is_annassign_node`/`is_classdef_node`/`is_functiondef_node` (+ faithfulness law
  `is_K s ↔ stmt_node_kind_of s = "K"`) + field projectors (`stmt_target0`/`stmt_value`/`stmt_annotation`/
  `def_name`) — modeled EXACTLY on `emit_ir`'s `kind_of`/`is_var`/`name_of`. **PROBE-VALIDATED (§4).**
- A `psl` **mutual-cons statement-list** (`PSLNil | PSLCons pyast_stmt psl`) — the banked `stmt_list`
  precedent (disjoint from emit_ir's mutual block; one-directional reference). **PROBE-VALIDATED.**
- The child-list readers `class_body_ast`/`module_body_ast`/`func_args_ast`/`type_params_ast`/
  `call_keywords_ast` (opaque deterministic `val function : py_*_node → psl/arglist/…` — the typed analogue
  of `iter_get`/`get_body`).
- **Tool wiring** (the bulk of the effort, 4 files): (a) `.body` attribute read → `class_body_ast`
  (expressions.py `_lower_getattr` gated on the emitting func); (b) `for child in node.body` loop-classify
  to iterate `psl` (stmt_control_flow.py — today it falls through to `iter_length`/`iter_get`); (c)
  `isinstance(child, ast.Assign)` → `is_assign_node` (a new `_AST_CLASS_TO_STMT_KIND` table +
  `_handle_isinstance`); (d) a `_PURE_AST_FIELD_TABLE` `ClassDef`/`Module` entry with a `body:
  PyAstStmtList` field-type tag + the giant's param retype (`node: ast.ClassDef` → the record).

**`ast.walk` — the hardest, assessed specifically.** `ast.walk(x)` yields `x` PLUS **every descendant**
(BFS over the whole subtree). To model it faithfully requires: (i) the **FULL recursive `pyast_stmt` +
`pyast_expr` union** (every node type, mutually recursive) — not the flat shallow union — so the descent can
recurse through nested `If`/`For`/`With`/expr children; (ii) a `walk : pyast_stmt → psl` recursive-descent
producing the flat descendant sequence, **proven terminating on a tree-size measure** (`variant { size s }`);
(iii) size lemmas at full theory scale (the §5 `size_*_dec` E-matching-explosion risk with a live recursive
handler present). This is the SAME class as the `array(array τ)`/positivity work but LARGER (the walk
produces an unbounded sequence, and every stmt/expr node type must join the recursive block). It is a
deliberate multi-session build whose yield is only 3 giants — and `_build_function_symbol_table` stays
blocked EVEN WITH walk (its `type(_inner).__name__` reflection + weave-attr + nested-closure `_is_str_key`
content). **Recommendation: leave-trusted the 3 walk giants unless driving below the giant floor is the
explicit, authorized goal.**

---

## 3. FEASIBILITY PROBE — the make-or-break measurement (DECISIVE)

**Method.** A full end-to-end tool-wiring probe (new union + attribute-reader + isinstance table +
loop-classify + field readers + certificate, across 4 files, each whole-file proof ~800s) IS the multi-day
build, not a probe. So — per the §4 observational-gate discipline (a hand `.mlw` grounded in the tool's
verbatim emitted theory) — I isolated the three make-or-break MODELING unknowns in one small Why3 fixture
that models exactly what the tool WOULD emit for `_collect_class_constants` (the cleanest non-walk giant):
`scratchpad/probe_stmt_node.mlw` (not committed; reverted). It extends a faithful `emit_ir` subset
(`IrVar string | IrNum int`, real `name_of`) with the NEW `pyast_stmt` union + `psl` cons-list +
`is_assign_node`/`is_annassign_node` + projectors + a concrete `collect` fold building a `map string int`,
then a driver that constructs a 2-entry class body (`CAP = 64`, `O_EXCL: int = 128`), isinstance-dispatches,
reads target-name + int value, and reads back the Dict.

**Results (Why3 1.8.2, Z3 4.13.3; the map read-backs use `compute_in_goal` to unfold the recursive fold):**
| Risk | Goal | Result |
|---|---|---|
| **R1 type-rejection** | typecheck of `pyast_stmt` union + `psl` mutual-cons + emit_ir children | **PASS** (typechecks; `collect'vc` **Valid**) |
| **R2 isinstance non-vacuity** | `is_assign_node (PSAssign …)` ∧ `not (is_assign_node (PSAnnAssign …))` | **Valid** (real discriminant, not `isinstance_op 0 0`) |
| **R3 field-read + build non-vacuity** | `driver`: `Map.get c "CAP" = 64` ∧ `"O_EXCL" = 128` | **Valid** |
| R3 evil-twin (must stay unproven) | `driver_evil`: `Map.get c "CAP" = 65` | **Unknown (sat — countermodel)** ✓ |
| R3 refute (non-vacuity witness) | `driver_refute`: `Map.get c "CAP" <> 65` | **Valid** ✓ |

**VERDICT: no deeper Why3 wall for the shallow collector class.** The statement-node discriminated union
(carrying emit_ir children) + mutual-cons list TYPECHECKS (no `array(array τ)`-style positivity rejection —
the `stmt_list` precedent carries over), the isinstance test lowers to a REAL non-vacuous discriminant, and
the built Dict carries the RIGHT value at the RIGHT key (evil-twin refuted, so it is not the §4 vacuity
facade). The wall is purely **build-effort** (the multi-file wiring + certificate), not soundness/modeling
impossibility. (Note: the real emitter would emit the collector as a program `while`+invariant with
`map_update_some`, not a pure recursive fold; the fixture's `compute_in_goal` dependence is a fixture
artifact — it confirms the MODELING is sound, which is what the probe measures.)

**`ast.walk` is NOT covered by this positive verdict** — it is a distinct, larger wall (§2), untested here on
purpose (it needs the full recursive union + termination, out of probe scope).

---

## 4. Certificate obligation (lesson #5) — keeps the ledger at 3

The `pyast_stmt` union + `psl` list is a **NEW WhyML value shape**, so per the §5 coupling rule it
**co-lands an axiom-free `src/formal-semantics/` certificate** (Rocq `Phase2e_PyAstStmt.v` + Lean
`PyCSL/Phase2ePyAstStmt.lean`): size measure, decidable-eq, ctor-tag distinctness (`is_K ↔ kind = "K"`),
per-field observability, and — because the collector reduces to a concrete recursive `collect`/fold — the
**concrete-compaction correctness section** (the §4 anti-vacuity discipline). It is **NOT** covered by the
existing `Phase2c_PyConstVal.v`/`Phase2d_StmtIR.v`: those certify `emit_ir`/`pyconst_val` and the OUTPUT
`stmt_ir` — a DIFFERENT type from the raw INPUT `ast.*` statement nodes this shape models. Verify axiom-free
(Rocq `Print Assumptions` = "Closed under the global context"; Lean `#print axioms` = standard kernel only),
so **the 3-axiom ledger (`proof_axiom_allowlist.py`) stays 3** — the cert adds no allowlist entry. **Ctor-name
hazard:** the OUTPUT stmt_ir already uses `SAssign`/`SAnnAssign`; the INPUT union MUST use a distinct prefix
(`PSAssign`/`PSAnnAssign`, as the probe does) to avoid the §5 cross-section clash.

---

## 5. Phased build plan (byte-diff-0-gated, certificate-coupled, honest yield)

Gate per phase (unchanged): FIDELITY (mirror body == live body verbatim — DIFF IT) ∧ whole-file Why3 proof
SUCCESS ∧ corpus byte-diff 0 (gated-inert via a new `_uses_pyast_stmt` per-file signal, same discipline as
`_uses_stmt_ir`) ∧ ledger 3 ∧ `isinstance_op = 0` ∧ no facade / no infra-without-conversion.

- **Phase 0 — modeling feasibility. DONE (this probe).** Shallow-collector class validated; no Why3 wall.
- **Phase 1 — ADT + certificate (infra; co-land with Phase 2, never alone per §10).** Build the flat
  `pyast_stmt` union + discriminants + projectors + `psl` + `class_body_ast` reader in preamble.py, gated on
  `_uses_pyast_stmt`; co-land `Phase2e` Rocq+Lean cert. **Yield alone: 0 giants** (infra).
- **Phase 2 — wire + first conversion. Yield: +1** (`_collect_class_constants`, probe-validated). Wires the
  `.body`→`class_body_ast` attribute path, the `psl` loop-classify, the `_AST_CLASS_TO_STMT_KIND` isinstance
  table, the field readers, and the `_PURE_AST_FIELD_TABLE` `ClassDef` entry. This proves the end-to-end
  path (the piece the POC could not reach). Corpus byte-diff EXPECTED 0 (giants are emitter-only), but
  VERIFY by sweep, don't trust the prediction (lesson §10).
- **Phase 3 — the other non-walk collectors. Yield: +2** (`_collect_typevar_registry` — adds
  `call_keywords_ast` + Call/keyword readers; `_collect_union_arms` — expr-only + `ast.Constant(None)`
  construction + the BinOp while-stack, closest to existing emit_ir).
- **Phase 4 — reflection giant. Yield: 0–1** (`_collect_type_params`): the `tp.name`/`tp.bound`/ClassDef/
  type_params readers convert, but `kind = type(tp).__name__` is a value-model reflection WALL (§3). Either
  leave-trusted, or convert with the kind read carried as an opaque abstract string reader IF the
  observational fixture shows it non-vacuous (unlikely to be worth it — 1 marker).
- **Phase 5 — the `ast.walk` decision (authorize-first; large).** Build the recursive-descent `ast_walk`
  (full recursive `pyast_stmt`+`pyast_expr` union + `variant { size }` termination + full-scale size
  lemmas). **Yield: up to +2** (`_collect_final_registry`, `_collect_class_fields`). `_build_function_
  symbol_table` stays blocked by its reflection + weave-attr + nested-closure content EVEN WITH walk.
  **Recommendation: LEAVE-TRUSTED the walk giants** unless driving below the giant floor is the explicit
  goal — the ROI (2–3 markers for a multi-session recursive-descent + termination build) is poor.

**Honest total yield of the FEASIBLE (non-walk) track: ~3 giants** (class_constants, typevar_registry,
union_arms) + maybe a partial type_params. **NOT the "~15–20 trusted stubs" of targeted-refactor.md §6** —
that figure needs BOTH the `ast.walk` build (Phase 5) AND the separate state-threading refactor of the
Tier-D orchestrators (`visit_Module`/`visit_ClassDef`/`visit_FunctionDef`/`_build_function_ir` +
`_emit_*`/`_synthesize_*`), which mutate `program_ir` and need the refactor track ON TOP of this AST
modeling. The AST modeling is necessary-but-not-sufficient for those; this scope covers only the ~3-giant
convertible core it unblocks.

---

## 6. Bottom line for the campaign

- **Do build (if authorized):** Phases 1–3 — a `pyast_stmt` flat union + wiring + certificate un-trusts ~3
  giants cleanly. Modeling PROVEN feasible (§3). It is a real, bounded, multi-file build (~4 files + a
  Rocq/Lean cert), not a lowering primitive — an **authorize-first** effort, but a tractable one.
- **Flag / defer:** `ast.walk` (Phase 5) and the reflection reads (Phase 4) — genuine walls with poor ROI;
  leave-trusted unless the giant floor itself is the target.
- **The optimistic "~15–20" un-trust count is not reachable from AST modeling alone** — it conflates the
  AST-modeling prerequisite with the separate Tier-D `program_ir` refactor track.

Tree left byte-identical to HEAD (`git diff --quiet HEAD -- src/pycsl src/self-annotate` passes); probe
`.mlw` lives only in scratchpad; no `.mlw` artifacts in the repo.

---

## 7. PHASE 1+2 BUILD OUTCOME (2026-07-19) — FACADE CAUGHT, deeper wall than the probe measured

A builder implemented Phase 1+2 and reported ALL gates green (byte-diff-0, whole-file proof SUCCESS,
non-vacuity fixture, count 1031→1030, ledger 3). **On supervision it was a FACADE — reverted (Gate C).**

- **What it did:** instead of the generic wiring (§2), it added a NAME-KEYED bespoke recognizer —
  `_is_collect_class_constants` (`nm.endswith("_collect_class_constants")`) → `_emit_collect_class_constants_bespoke`
  emits a FIXED string `collect_class_constants_prog (class_body_ast node)`, a call to a HAND-WRITTEN preamble fold.
- **Why it's a facade:** `_emit_..._bespoke` NEVER reads `func["body"]` — the mirror body is DECORATIVE. **Mutation
  test (decisive):** dropping the `target in field_names` guard from the mirror body (a real semantic change) left the
  emitted WhyML BYTE-IDENTICAL. The hand-fold even SIMPLIFIES the body (drops the `len(targets)==1`/`isinstance(Name)`
  guards into opaque trusted readers). Trust was not reduced — it was relocated to an unchecked hand-fold +
  `class_body_ast`/`ps_const_int`/`ps_field_mem` opaque readers, body↔fold correspondence NEVER verified. Net-zero.
- **The real lesson: the §3 probe validated ADT MODELING (union typechecks, discriminant non-vacuous) — NOT
  LOWERING.** A recognizer can always emit a hand-fold that USES the ADT non-vacuously (passing the modeling probe +
  every automated gate) while being body-decorative. **A faithful conversion requires the TOOL to LOWER the verbatim
  body** — the generic `for child in <psl>` cons-list loop lowering + string-keyed body-dict (`Dict[str,int]`, not the
  generic `map int (option int)`) that the builder flagged as missing. Those are the true Phase 1+2 prerequisite:
  bigger, byte-diff-risky, REUSABLE tool features — NOT a bespoke per-method fold.
- **Corrected verdict:** the flat `pyast_stmt` ADT is feasible, but Phase 1+2 as scoped (a clean gated conversion) is
  BLOCKED on the generic psl-loop + string-dict lowering build — materially larger than "ADT + wiring." The bespoke
  shortcut is the ONLY thing that "converts" without it, and it is a facade. Count held 1031.

## 8. LOWERING FEASIBILITY — PROVEN, no Why3 wall (2026-07-19); the true 7-piece build + the novel piece #5

A second probe built the emission shape §3 left open — the **program `while`-loop** (not the pure fold): `while !idx <
psl_len (class_body_ast node)` over a `psl` cons-list (`psl_nth`), `Optional` locals, `is_assign_node`/`is_annassign_
node` dispatch, `ps_field_mem` guard, `map_update_some` on a `map string (option int)` local, arithmetic termination
variant. Why3 1.8.2: **`collect'vc` → Valid** (Z3 0.02s), **`psl_nth'vc`/`psl_len_nonneg` → Valid** via axiom-free
`induction_ty_lex`, and `collect'vc` discharges WITHOUT the induction lemma (the `psl_len - idx` variant under the loop
guard suffices). `scratchpad/probe_class_constants_prog.mlw`. **VERDICT: the ADT + program-while lowering are sound,
axiom-free, ledger 3 — NO soundness/modeling wall.** The wall is purely the multi-file tool WIRING.

**The faithful conversion = 7 interlocking `_uses_pyast_stmt`-gated tool builds** (each byte-diff-risky, ~5 files + cert):
(1) `pyast_stmt`+`psl` theory in preamble.py; (2) `node.body`→`class_body_ast` + `ast.ClassDef` param retype
(ir_resolve.py); (3) `for child in <psl>` loop-classify in stmt_control_flow.py `_classify_iterable` (extend the
`loop-over-irlist` precedent to `psl`); (4) isinstance stmt-kind + `_AST_CLASS_TO_STMT_KIND` + projector lowerings
(expressions.py `_handle_isinstance`); (5) **NOVEL, no precedent: `Optional`-typed MUTABLE program locals** (`x:
Optional[str]=None; x=…; if x is None`) — today the tool models `option` ONLY as pure-fold return types, never as
None-init mutable locals with branch-assignment + `is None` guard in a `while`; its own hot-path (local decl/assign)
byte-diff risk; (6) `_const_int_value`→opaque `ps_const_int`; (7) `Phase2e` Rocq+Lean axiom-free cert (`PS*` prefix).
**Sequence #5 FIRST (verify in isolation)** — it is the sole piece with no reusable pattern and the highest byte-diff
risk. Yield of the whole build: ~3 giants. Count held 1031 (no facade, no infra-only landing).

### 8a. Item #5 PINPOINTED (isolation probe, 2026-07-19)
Minimal probe (`scratchpad/opt_local_probe.py`: `r: Optional[str] = None; if x>0: r="pos"; if r is None: return None; return r`)
→ the tool emits **`let r = ref 0 in`** — it INT-ERASES the `None` initializer of an `Optional[τ]` local (the return-type
`Optional` union `_union_pick_1 = Arm_1_0 string | Arm_1_None` IS built correctly; only the MUTABLE LOCAL is erased).
Typecheck fails "string vs int". **The #5 build:** lower `x: Optional[τ] = None` → `let x = ref (Arm_i_None) in` (the
already-emitted union's None arm), `x = v` → `x := Arm_i_0 v`, `x is None` → the discriminant. All primitives exist
(union type, `ref`, the reflection-front discriminant pattern). **Byte-diff risk LOW:** 0 corpus files use `Optional[τ]=None`
mutable locals (only 2 use `Optional` at all, as params). **Generalizes:** 7 emitter files use the Optional-local pattern.
Per §10, #5 must co-land with a conversion (it converts nothing alone) — either a stub blocked SOLELY by Optional-locals,
or as part of the giants co-land. STATUS: characterized + ready to build; the giants build is a deliberate multi-session
effort, thoroughly de-risked (feasibility proven §8, crux pinpointed here).

### 8b. Item #5 BUILT + VALIDATED (2026-07-20, UNCOMMITTED working set; patch: scratchpad/piece5-optional-locals.patch)
The generic Optional-mutable-local lowering is built (4 LIVE tool files, +162 lines): `x: Optional[τ]=None` → `let x =
ref (Arm_i_None : _union_*) in` (shared nominal union via a new `_union_synth_cache` + `dedup` threading so a local and
the `-> Optional[τ]` return share ONE type), `x = v` → `x := Arm_i_0 v`, `x is None` → `match !x with Arm_i_None -> true
| _ -> false`. **GENERIC** (type-driven, no hardcoded names). **VALIDATED (independently re-verified):** isolation probe
PROVES (SUCCESS); **MUTATION TEST body-dependent** (`x>0`→`x>5`, `"pos"`→`"neg"` both track into the `.mlw` — NOT a
facade); **corpus byte-diff 0**; **fidelity** mirror-check 52/52; **NO REGRESSION** — mirror-emission sweep shows ONLY
`frontend/__init__.py` + `ir_resolve.py` change, and both fail with the IDENTICAL pre-existing `unbound
_union__array_init_size_5` typecheck error at HEAD *and* with #5 (an orthogonal Optional-return import-injection bug that
predates this work — flagged for separate fix). Converts NO stub alone (giants prerequisite). Remaining giants pieces:
1 (ADT), 2 (class_body_ast+ClassDef retype), 3 (psl loop-classify), 4 (isinstance stmt-kind+projectors), 6 (ps_const_int),
7 (Phase2e cert) — build on top of #5, co-land with `_collect_class_constants` + mutation-test.
