# Wall report: `cap-vm-unerase-irnode`: the IR-node / CSLNode / `Any` value-model seam (run #5)

**Status:** state-of-the-art wall statement for an INDEPENDENT reviewer. The reviewer has the repo and an oracle (pycsl + Why3) but none of our context.
**Base:** branch `ghost-assign-bc6`, HEAD `0e504dc78` (log 492). `\trusted` count on main: 413 (driver log 490, `getting-better/driver-run-log.md`). Proof-axiom ledger: 3.
**Author:** report author for the run #5 driver. Read-only on `src/`. Every probe ran in a scratch copy at `scratchpad/vmR/st`, built with `git archive HEAD src/pycsl src/self-annotate bin`, and no change was landed.

**Evidence tags used throughout:**
- **[M]** I measured it in this session. The command and output path are given and can be re-run.
- **[C]** Cited from a repo file, commit or log, which I read but did not re-run.
- **[I]** My inference. Treat it as a hypothesis to falsify.

---

## 0. Executive summary

1. **[C] Size.** `cap-vm-unerase-irnode` is the largest single capability in the run #5 deep chain census.
   - It appears on **42** of 245 merged stub chains (`getting-better/run5-chain-census.md` §3, row `cap-vm-unerase-irnode`). It is the terminal wall on 37 of them.
   - The value-model family it belongs to (VMSEAM) is the terminal wall of **77 of the 111** DEPTH-STOP chains (§5).
   - On only 3 chains is it the *only* non-free capability: `_desugar_acts`, `_csl_in`, `_csl_list_to_ir` (computed from `scratchpad/cv9/merged.json`, §3.1 below).
2. **[M] It is not one wall but four sub-seams under one label** (§3.1):
   - **A. CSLNode:** the Module2 contract-AST classes vs the `emit_ir` ADT. 11 stubs.
   - **B. Pipeline IR:** `Dict[str, Any]` / `Any` dicts read by `.get` / `[]`. About 25 stubs.
   - **C. emit_ir child-field typing.** 2 stubs.
   - **D. pyast / annotation nodes typed two ways.** About 4 stubs.

   A route that fixes one sub-seam does not move the others.
3. **[M] The erasure is fail-closed by design, and that is why the stubs are stuck rather than unsound.**
   - An `Any` value lowers to `int` (or a `map string (option int)` for `Dict[str, Any]`).
   - A family of refusals stops the int from being used as something it is not: routes #252, #325, #563 and #289, plus the "erased iterable has no variant" refusal.
   - All 5 non-type-error probes below end in one of these refusals. The other probes end in a Why3 L3 type error `int` vs `emit_ir`.
4. **[M] There is not one value model but at least five, and they do not interoperate.**
   - int erasure (the default).
   - `pydict` / `pyval` (D1/R-A generic fold, template-gated).
   - `hval` (Tier-5, `Dict[str, PyVal]` sentinel).
   - `emit_ir` (about 110 constructors, certified).
   - `csl_node` (an input-side view sum over the CSL records).

   For example, `hval`'s node arm is `HNode hval`, not `HNode emit_ir`, so an IR node stored in a heterogeneous dict cannot be handed to emit_ir-typed code.
5. **[M] Smallest sub-piece that moves a real stub.** A one-annotation retype of `CSLIn.element/collection` from `CSLNode` to `"ExprIR"` in the live `Module2_Parser.py`. This applies the banked lever of `ef94162f`/`15a134ced`.
   - It turns `_csl_in`'s erased, int-hashed `range` branch into a **faithful** lowering: `str_eq_op (func_of …) "range"`, `args_of`, real array indexing.
   - The wall then moves one branch down, to a **faithfulness hazard** in the shared projector table: `dv.kind` lowers to the node-tag projector `kind_of`, and `dv.coll` lowers to `svalue_of` (§2.3, probe p14).
6. **Ranked routes** (§6):

   | Rank | Route | Cost | Yield |
   |---|---|---|---|
   | R1 | CSLIn retype + CSL-record narrowing on `isinstance` + one construction-only `emit_ir` leaf | S/M | 1 stub; removes a latent misprojection |
   | R2 | `List[ExprIR]` return / materialize plumbing, and refusing the silently dropped store into an emit_ir dict | M; owes the hot-file proofs | 2–3 stubs as a link |
   | R3 | Schema-typed closed-key IR views (TypedDict → record, extending `46fec2387`) for the pipeline-IR family | L | ≤25 stubs touched, few closed alone |
   | R4 | Universal value type replacing int erasure emitter-wide | XL; corpus-affecting | not recommended now |

---

## 1. Global picture (for a reviewer with no context)

### 1.1 PyCSL

PyCSL is a deductive verifier for annotated Python.
- **The pipeline.** Python source with `#@` contracts passes through these modules: `Module1_Ingestor` → `Module2_Parser` (the contract language: a Lark grammar plus a hand parser producing `CSLNode` dataclasses) → `Module3_Weaver` → `Module5_IREmitter` (a JSON-like IR: `Dict[str, Any]` trees, keys `"type"`, `"left"`, `"body"`, …) → `module6_whyml/*` (IR → WhyML) → Why3 (Alt-Ergo / Z3 / CVC5).
- **Entry point.** `src/pycsl/pycsl.py`. The code lives in `src/pycsl/frontend/` and `src/pycsl/module6_whyml/`.

### 1.2 The mirror and `\trusted` stubs

`src/self-annotate/src/` is a **mirror** of the emitter, annotated with PyCSL contracts, which PyCSL verifies (the emitter verifying itself).
- **Stubs.** A mirror method that PyCSL cannot (yet) verify is a `#@ \trusted` stub with a facade body (`pass`, `return {}`, …). The stub is assumed, not checked.
- **The campaign.** The self-tcb-reduction loop (`config/skills/self-tcb-reduction/SKILL.md`) converts stubs to verified bodies.
- **Conversion contract shape** (SKILL.md §1, "Upper bound U"):
  - The body is the live method transcribed **verbatim**.
  - The contract is fixed: `#@ requires True / ensures True / assigns <tight frame>`. It asserts type-safety and frame, never value-faithfulness.
  - No new `\trusted`, no new axiom.

### 1.3 The three lower-bound planes (all required per conversion; SKILL.md §1)

1. **Fidelity.** The mirror body equals the live body, verbatim modulo `#@` and annotations: `bin/check-self-annotate-sync.sh`, `bin/self-annotate-mirror-check.sh`. Mirror *annotations* may differ from live ones. `bin/port-one-mirror-body.py` keeps the mirror `def` line and de-annotates before comparing. This is what makes a "mirror retype" free.
2. **Whole-file Why3 proof** of the mirror file: `python3 src/pycsl/pycsl.py <mirror.py> --import-path src/pycsl`.
   - Recorded single-slot costs (I did not measure them): expressions ≈ 6 h, statements ≈ 5.3 h, pure_ast ≈ 1 h (`getting-better/driver-run5-plan.md:65`).
   - The brief adds: stmt_control_flow ≈ 5 h, Module5 ≈ 1 h, core_ir_semantic ≈ 1.7 h.
   - Goal counts at route #411: expressions 23424, Module5_IREmitter 2636, pure_ast 3408 (`driver-run-log.md` log 286). stmt_control_flow: 14817 goals in 13546 s (log 318).
3. **Corpus inertness.** `PYTHONHASHSEED=0 bin/byte-diff-sweep.sh` over the reference corpus (`test-suite/corpus/pycsl-reference/`) must show 0 diff, unless the change is a sanctioned emission change with every moved file re-proved.

### 1.4 Ledger and coupling rule

- **Ledger of 3 axioms.** Certificates under `src/formal-semantics/{rocq,lean}` may rely only on the kernel allow-list `src/pycsl/proof_axiom_allowlist.py`:
  - Lean: `propext`, `Classical.choice`, `Quot.sound`.
  - Rocq: propositional and functional extensionality.
- **[C] Coupling rule** (SKILL.md, "COUPLING RULE"): a NEW WhyML value shape (variant / record ADT) must co-land with an axiom-free side-car certificate.
- Existing certificates: `Phase2b_RecordVal`, `Phase2c_PyConstVal`, `Phase2c_PyValDict`, `Phase2d_StmtIR`, `Phase2e_PyAstStmt`, `Phase2f_PyVal`, `Phase2g_CallKw`, `Phase2h_TParam`, `Phase2i_TermIR`, `Phase2j_MethodRecv`, `Phase2k_CslClause`, `Phase2l_PyAstExpr` (`ls src/formal-semantics/rocq/`).

### 1.5 Where this wall sits

- **[C] Census.** The run #5 deep chain census (`getting-better/run5-chain-census.md`, base `b432460d6`) walked each of 166 in-scope stubs as follows:
  1. Port the verbatim live body.
  2. Emit with `--no-proof --keep-mlw`.
  3. Patch the blocker in scratch (equivalent rewrite / mirror retype / typed stand-in).
  4. Re-emit, for up to 5 links.
- **Verdicts.** DEPTH-STOP 111, HONESTY-WALL 40, TC-OK-FACADE 8, TC-OK-PARTIAL 7 (§0).
- **Census reading** (§6 item 4): "The value-model seam is the campaign." It recommends ordering it irnode → list → dict → tuple/union. The first census (`run5-capability-census.md`) names the same family "vm-seam".

---

## 2. The wall as first seen (reproduced)

### 2.0 Harness [M]

- **Probe script:** `scratchpad/vmR/probe.sh <rel> <Qualified.fn> <tag> [extra.py]`. It works as follows:
  1. Restore the mirror file from `HEAD`.
  2. Run `bin/port-one-mirror-body.py <tree> <rel> <fn> --convert`. This copies the live body and deletes the `\trusted` marker.
  3. Optionally apply an `extra.py` patch.
  4. Run `python3 src/pycsl/pycsl.py <mirror> --import-path st/src/pycsl --no-proof --keep-mlw`.
  5. Restore the mirror file.
- **Batches:** `scratchpad/vmR/batch{1,3,4}.sh`, each run as `HEAVY_QUICK=1 scratchpad/heavy/heavy.sh …`.
- **Artifacts:** `scratchpad/vmR/probe/<tag>.{patchlog,src.py,log,mlw}`.

### 2.1 Port-as-is results (batch1) [M]

| tag | stub (mirror file) | verdict | exact error |
|---|---|---|---|
| p01 | `PyCSLToJSONEmitter._csl_in` (frontend/Module5_IREmitter.py) | L3-tc ✗ | `Module5_IREmitter.mlw`, line 3614, chars 53-71: `This expression has type int, but is expected to have type PyCSL_Program.emit_ir` |
| p02 | `PyCSLToJSONEmitter._csl_list_to_ir` (same) | L3-tc ✗ | line 3969, chars 48-50: same int vs emit_ir |
| p03 | `_collect_instantiations` (frontend/monomorphize.py) | REFUSED | "a `for` loop over an iterable whose length term contains an unconstrained value (`any`) has no legal termination `variant` … the iterable reads an erased value" |
| p04 | `GhostSpecOpsMixin._handle_proj_expr` (module6_whyml/expr_ghost_spec_ops.py) | REFUSED | `PYCSL-R563-METHOD-ARGUMENT-KIND: lr is passed to the parameter lr of … _e, declared a set, and may be a number` (mirror signature `lr: int`) |
| p05 | `run_ir_semantic_checks` (core_ir_semantic.py) | REFUSED | `PYCSL-R325-OPAQUE-INT-FALLBACK … 'trusted' comes from 'set_1', a call PyCSL has no model of: it is lowered to an OPAQUE INT` |
| p06 | `PyCSLWeaver._desugar_acts` (frontend/Module3_Weaver.py) | L3-tc ✗ | `Module3_Weaver.mlw` line 1428, chars 69-71: int vs emit_ir |
| p07 | `_rewrite_call_sites` (frontend/monomorphize.py) | REFUSED | route #289: "an element store through a value the model does not represent as a list is out of scope … the store lowers to the abstract `subscript_set` with NO effect" |

These match the cv9 first links for the same stubs (`scratchpad/cv9/probe/results.tsv`, rows s013_1, s071_1, s072_1, s111_1, s123_1, s045_1), on a newer base.

### 2.2 The emitted WhyML at the error sites [M]

**p01, `_csl_in`** (`probe/p01_csl_in.mlw`):

```
1170:  type cslin = { mutable cslin_element: int; mutable cslin_collection: int }
3915:  with pycsltojsonemitter___csl_to_ir (self: pycsltojsonemitter) (node: emit_ir) : emit_ir
3612:    if ((if (py_isinstance_CallExpr_int_op node.cslin_collection)
             && ((get_func node.cslin_collection) = 1974220728) then 1 else 0) <> 0) then begin
3614:      elt_ir := (pycsltojsonemitter___csl_to_ir self node.cslin_element);      <- int into emit_ir
3628:        if ((get_kind !dv) = 915441578) then begin                             <- "keys" int-hashed
3633:            raise (Return_emit_ir (IrExists !kv (IrOther "MapValueIs") IrSNone IrONone))
```

Three problems are visible in this one function:
- **(a)** The CSL record field is `int` because the live annotation is `element: CSLNode` (`src/pycsl/frontend/Module2_Parser.py:526-529`). `CSLNode` is a field-less base class, which the model erases.
- **(b)** String compares on erased values become compares of an **int hash of the string literal** (`"range"` → `1974220728`, `"keys"` → `915441578`).
- **(c)** The nested dict literal `{"type": "MapValueIs", "map": …, "key": …, "value": elt_ir}` has no emit_ir constructor. It collapses to `IrOther "MapValueIs"`, so its three fields are **dropped**. This type-checks, but it is value-degenerate.

**p02, `_csl_list_to_ir`** (`probe/p02_csl_list.mlw:3955-3975`):
- `csl_list: List[CSLNode]` → `array int`, so `c` is int and `_csl_to_ir self !c` is a type error.
- `getattr(c, "act_name", None)` → `pycsl_getattr_unknown_539951548 !_pyobj_state !c`.
- The store `d["act_name"] = an` into the IR dict lowers to **`()`**, a silently dropped mutation (§2.3).

**p06, `_desugar_acts`** (`probe/p06_desugar_acts.mlw:1405-1430`):
- `contracts: List[Any]` → `array int`.
- `isinstance(c, Act)` → `py_isinstance_Act_int_op !c`, an uninterpreted predicate on int.
- `c.name` / `c.clauses` → `get_name !c` / `get_clauses !c`.
- The `binop_left = !a` record field is `emit_ir` while `a` is int.

### 2.3 What a single retype does (the smallest sub-piece) [M]

**p11** (`scratchpad/vmR/x_cslin_retype.py`). Retyping `CSLIn.element/collection` to `'ExprIR'` in the **mirror** Module2 (`src/self-annotate/src/frontend/Module2_Parser.py:324-327`) changes **nothing**: `type cslin` stays `int`, with the same error at line 3614.
- **Measured fact:** a Module5 mirror reads the CSL record types from the **live** `src/pycsl/frontend/Module2_Parser.py` through `--import-path`.
- This agrees with the backlog: "retype CSLNotIn.element/collection CSLNode->"ExprIR" in LIVE Module2_Parser.py" (`getting-better/driver-backlog.md:4828-4833`, commit `ef94162f`).

**p14** (`scratchpad/vmR/x_cslin_retype_live.py`). The same retype applied to the **live** scratch copy (`st/src/pycsl/frontend/Module2_Parser.py`, restored afterwards; restore verified by `diff`):

```
1170:  type cslin = { mutable cslin_element: emit_ir; mutable cslin_collection: emit_ir }
3609:    if ((if (py_isinstance_CallExpr_emit_ir_op node.cslin_collection)
             && (str_eq_op (func_of node.cslin_collection) "range") then 1 else 0) <> 0) then begin
3610:      let rargs = ref (Array.copy (args_of node.cslin_collection)) in
3614:        hi_ir := (pycsltojsonemitter___csl_to_ir self (!rargs)[0])
3621:      if (py_isinstance_DictView_emit_ir_op node.cslin_collection) then begin
3624:        coll_var := (IrVar (svalue_of !dv));          <- L3-tc: emit_ir where string expected
3625:        if (str_eq_op (kind_of !dv) "keys") then begin  <- dv.kind read as the NODE TAG
```

- **Result:** the `range` branch is now faithful (real string compare, real `args_of`, real indexing). The new error is `line 3624, chars 27-42: This expression has type PyCSL_Program.emit_ir, but is expected to have type string`.
- **Cause.** `DictView` (`coll: str`, `kind: str`; record `dictview` exists at mlw line 1176) is not an arm of `emit_ir` or of the `csl_node` view sum. After `isinstance(…, DictView)` the local `dv` keeps type `emit_ir`, and attribute reads go through the shared projector table `_EMIT_IR_STR_ATTRS` (`src/pycsl/module6_whyml/expressions.py:185`):
  - `.kind` → `kind_of`, the **node-class tag**, not the `kind` field.
  - `.coll` → the generic `svalue_of` (emit_ir).
- **[I] Faithfulness hazard.** If line 3624 were patched to type-check, line 3625 would still compare the *class tag* of `dv` with `"keys"`, where CPython compares `dv.kind`. This is a value-unfaithful lowering. It does not break the type-safety contract `ensures True`, but it would pass a non-vacuity reading and is exactly the "coherent-and-wrong" failure SKILL.md §0 warns about. **The reviewer should confirm this** by patching 3624 in a scratch copy and checking that `kind_of` stays.
- **[M] The `isinstance` predicates are unconnected `val`s.** `py_isinstance_CallExpr_emit_ir_op (x: emit_ir) : bool` and `py_isinstance_DictView_emit_ir_op` are declared at mlw lines 1623 and 1626 with no spec. They are related neither to `kind_of` nor to `cslx_view`. They are sound as an over-approximation, but they carry no information.

**p12 / p13, `_csl_list_to_ir`, mirror retype of the parameter** (`x_list_retype.py`):
- With `csl_list: List["ExprIR"]`, the first link clears: `csl_list: array emit_ir` (`probe/p13_csl_list_paramret.mlw`).
- The next link: `line 3977, chars 17-21: This expression has type seq.Seq.seq PyCSL_Program.emit_ir, but is expected to have type seq.Seq.seq int`. The line is `(materialize !out)`. The function's result is emitted as `array int` **even when the mirror return is annotated `-> List["ExprIR"]`** (p13), and `materialize` exists only for int sequences.
- This matches cv9 s044 ("the list-of-ADT materialisation exists only for int elements").

### 2.4 How the default lowering looks on a 7-line program [M]

Toy files are in `scratchpad/vmR/toy/`, run by `batch2.sh` (QUICK).

| file | source | result |
|---|---|---|
| t1_any.py | `def kind(ir: Any) -> str: return ir.get("type")` | REFUSED, route #252: "an erased (`Any`/…) value flows into a slot declared as a builtin type: the `return` of a function declared `-> str`" |
| t2_dict_any.py | `def name_of(d: Dict[str, Any]) -> str: return d["name"]` | REFUSED, route #252 (same) |
| t3_exprir.py | `def kind(ir: "ExprIR") -> str: return ir.get("type")` | TC ✓: `let function kind (ir: emit_ir) : string = (kind_of ir)` (`t3_exprir.mlw:285-289`) |
| t5_dict_any_hetero.py | `d: Dict[str, Any] = {"pattern": "Constructor", "ctor": ctor, "n": 3}` | L3-tc ✗ (line 21): `map_update_some (… (const (None: option int)) "pattern" 2193169) "ctor" ctor) …`: the literal string is int-hashed and the string variable `ctor` does not fit `option int` |
| t4_pyval.py | same with `Dict[str, PyVal]` | TC ✓: `map_update_some (… (const (None: option hval)) "pattern" (HStr "Constructor")) "ctor" (HStr ctor)) "n" (HInt 3)` (`t4_pyval.mlw:79`) |
| t6_any_list.py | `for f in ir.get("functions", []): n += 1` with `ir: Dict[str, Any]` | TC ✓ but **input-blind**: `ir: map string (option int)`; loop bound `iter_length (match Map.get ir "functions" with Some v_ -> v_ \| None -> 0 end)`: the list is an int and its length an uninterpreted function of it (`t6_any_list.mlw:15-27`) |

This table is the wall in miniature:
- `Any` and `Dict[str, Any]` are the int model.
- `"ExprIR"` is the certified ADT.
- `PyVal` is the heterogeneous model.
- Moving a value between them needs an annotation change at every hop.

---

## 3. What the current value model is

### 3.1 The 42 stubs split into four sub-seams [M, from census data]

Computed with a short script over `scratchpad/cv9/merged.json` (filter `'cap-vm-unerase-irnode' in need`). By file: ir_resolve 8, monomorphize 8, Module2_Parser 6, preamble 5, Module3_Weaver 4, Module5_IREmitter 4, core_ir_semantic 2, expr_ghost_spec_ops 2, ir_inline 1, scc 1, pycsl 1. My classification by reading the census rows [I]:

| sub-seam | stubs | what is erased |
|---|---|---|
| **A. CSLNode ↔ emit_ir** | s034 `_parse_act_block`, s041 `_parse_atom_primary`, s042 `_parse_atom_name`, s043 `_parse_atom_bs`, s044 `_parse_expr_list`, lvC `_parse_quantifier` (Module2); s045 `_desugar_acts`, s061 `_region_bound_str`, lvC `_subst_var` (Module3); s071 `_csl_in`, s072 `_csl_list_to_ir` (Module5): **11** | CSL dataclass fields typed `CSLNode` / `List[CSLNode]` / `List[Any]`; class objects as values (`cls = Exists if … else Forall`); dataclass reflection |
| **B. Pipeline IR `Dict[str, Any]` / `Any`** | core_ir_semantic s013, s016; ir_resolve s099, s101, s103-s108; monomorphize s111-s115, lvB `_specialize_decl`, `_specialize_function`, lvC `_rewrite_subscript_calls_in_stmt`; ir_inline s094; scc s140; pycsl s149; preamble s127, s131, s135, s137: **25** | `.get(k)` / `[k]` / `.items()` over the Module5 output IR and dict-shaped records (`needs`, inductive decls, mutex-invariant pairs) |
| **C. emit_ir child-field typing** | s123 `_handle_proj_expr`, s124 `_handle_ctor_payload_expr`: **2** | `int(node.index)` on an emit_ir field. **Note:** the ADT declares `IrProj emit_ir int` (`p01_csl_in.mlw:195`), so the census wording "carries the Proj index as an emit_ir child" should be re-checked. Both chains stop first at R563 (p04). |
| **D. pyast / annotation nodes typed two ways** | s064 `_subscript_read_site`, s082 `_normalize_literal_annotation`, s083 `_encode_callable_annotation`, s136 `_subst_self_in_expr`: **4** | record field typed emit_ir, accessor taking int; `[inner]` as array int vs `list_new(get_elts inner)` |

Only **3** chains need nothing but this capability plus free links (`_desugar_acts`, `_csl_in`, `_csl_list_to_ir`). The probes above show that each of those 3 has further sub-links behind the first one.

Second capabilities co-occurring on the 42 chains: kind-judge-list-arg 4, elem-store-nonlist 4, R274-writing-call-in-comprehension 3, closure-lift 3, r325-typepos 3, then several at 2. In set-cover terms, **the label is necessary on 42 chains and sufficient on none that I measured.**

### 3.2 The lowerings, by Python type [M/C]

| Python value | WhyML lowering | where | modelled / certified |
|---|---|---|---|
| `Any`, `object`, unannotated, `CSLNode` (field-less base), `List[Any]` elements | `int` / `array int`; string literals compared against it are int-hashed; attribute reads become uninterpreted `get_<attr>`; `isinstance` becomes `py_isinstance_<C>_int_op` | type tags collapse to `"Any"` in Module5 (`src/pycsl/frontend/Module5_IREmitter.py:5298-5388`); refusal guards §3.3 | **no value model by design**: an opaque int, kept sound by refusals |
| `Dict[str, Any]` | `map string (option int)`; `.get(k, d)` → `match Map.get m k with Some v -> v \| None -> <d as int>` | toys t5, t6 | homogeneous; heterogeneous values do not type-check (t5) |
| `"ExprIR"` / `"StmtIR"` / `"IRNode"` / `"ContractExprIR"` annotation (param, field, return; also `List[...]` of them → `array emit_ir`) | the `emit_ir` sum (about 110 constructors, mutual with `irlist`, `iropt_str`, `iropt_ir`); `.get("type")` → `kind_of`; named attrs → projectors via `_EMIT_IR_STR_ATTRS` (expressions.py:185) and `_is_emit_ir_expr` (expressions.py:2875); dict-literal construction `{"type": K, …}` → constructor via `_IRNODE_CTORS` (expressions.py:2098) / `_lower_irnode_construction` (expressions.py:4324) | theory `_emit_exprir_theory` (preamble.py:5073); name test `Module5_IREmitter.py:3011-3030` | certified (`Phase2c`/`Phase2i_TermIR`; SKILL.md §8 "tier-3 ADT foundation EXISTS and is certified"). An unknown `"type"` → `IrOther "<K>"` with fields dropped (§2.2c) |
| CSL dataclass instance (`CSLBinOp`, `CSLIn`, …) | a per-class WhyML **record** (`type cslbinop = { cslbinop_left: emit_ir; … }`) built from the **live** class annotations; *also* emit_ir constructors for the same classes (`IrCSLIn`, `IrCSLNotIn`, `IrEnsures`, …) when constructed in an emit_ir context (`_csl_not_in` → `IrCSLIn node.cslnotin_element …`, `p01_csl_in.mlw:3460`) | `15a134ced` retyped 84 mirror fields to `'ExprIR'`; `ef94162f` the live CSLNotIn fields | records = `Phase2b_RecordVal`; 17 mirror fields still `CSLNode` (Module2 mirror lines 21-749, e.g. `Given.expr`, `Act.clauses`, `CSLIn.element`, `ProjExpr.index`) |
| `_CSL_HANDLERS` dispatch input | `csl_node` view sum (`PCsl_<Class> <record>`, 70+ arms), `cslx_kind_of` concrete, `val function cslx_view (e: emit_ir) : csl_node ensures { cslx_kind_of result = cslx_type_name_of e }` | `p14…mlw:1309-1472`; `preamble.py:10118` | certified `Phase2l_PyAstExpr` (comment at mlw 1309). **Non-recursive**: arms carry the handler parameter types verbatim |
| `Dict[str, PyVal]` (sentinel) and `List[PyVal]`, `-> PyVal` | `hval = HStr string \| HInt int \| HArr hval_list \| HMap hpairs \| HNode hval`, with `hpairs = PNil \| PCons string hval hpairs`, `pairs_get` lookup | `_uses_pyval` preamble.py:7975, `_emit_pyval_theory` preamble.py:8023 | certified `Phase2f_PyVal` (axiom-free per `pyval-value-model-wall-impl.md` Gate S). `HNode` carries `hval`, **not** `emit_ir` |
| generic-fold templates over the IR (`walk` catamorphisms) | `pyval = PInt \| PStr \| PBool \| PNone \| PList (list pyval) \| PDict pydict`, `pydict = DNil \| DCons irkey pyval pydict`, `irkey = K_type \| K_left \| … \| K_dyn string` | `_pydict_theory_lines` preamble.py:4342-4358, gated `needs_pydict` (preamble.py:2593); 147 `recognize_*` templates in `src/pycsl/module6_whyml/generic_fold.py` (41446 lines) | certified `Phase2c_PyValDict`. **Precision over recall**: fires only on exact recognized method shapes (generic_fold.py:1-26) |
| `c6557971` "heterogeneous value-model ROOT" | not a new value type: `_collect_mutations` converted by a reader-split (`pget_dyn` + `pget_list`) over the pydict model, plus a class str-set constant registry | commit message of `c65579714` | "NO new ADT, NO new cert" (its own words); the certificate is the existing Phase2c pydict one |
| closed-key `TypedDict` "View" | native WhyML record; `.get("k")` on a record-typed receiver → field read; string field compare → `str_eq_op` | commit `46fec2387` (G1/G2); `src/pycsl/module6_whyml/scc.py:6` `LogicSymbolView` | records = `Phase2b_RecordVal`; 4 such views in `src/pycsl` |

### 3.3 Where the erasure to int happens, and why it was chosen [C/M]

- **Where.**
  - Module5 collapses unresolvable annotations to the tag `"Any"` (`Module5_IREmitter.py:5298-5388`; `CSLNode` is not in the IR-node name set at :3030).
  - Module6 then gives `"Any"` the int carrier.
  - Field types of imported classes are read from the **live** class bodies (measured p11 vs p14).
- **Why.** The int carrier is what lets an erased value flow through untyped code at all. Soundness is then recovered by refusing every use that would re-apply a law the int satisfies but the Python value may not:
  - route #252: erased value into a builtin-typed slot. Message at `src/pycsl/module6_whyml/functions.py:3576`; rationale comment at :3195-3205.
  - route #325: opaque-int fallback of an unmodelled call (`src/pycsl/pycsl.py`, "PYCSL-R325-OPAQUE-INT-FALLBACK").
  - route #563: method argument of the wrong kind.
  - route #289: element store through a non-list container.
  - the erased-iterable variant refusal.

  These guards are why the 42 stubs are DEPTH-STOP rather than "converted unsoundly". It is a deliberate **fail-closed** modelling choice, and it is a reason the int was never just "replaced".
- **Unit check.** I did not find a design document that states the int choice as such. The closest is the `value-model-campaign.md` "no-more-int doctrine" (which is against int) and the route rationales above. **[I]** The int is historical (the earliest emitter modelled scalars only), and the refusal net was added later as each unsound int use was found (the run #3–#5 "rt" soundness campaigns).

### 3.4 Prior attempts at this seam and their verdicts [C]

| report / commit | claim | verdict |
|---|---|---|
| `20260719-rawdict-to-emitir-bridge-wall.md` + `-response.md` | the raw dict → emit_ir keystone fires only with `.to_dict()` | **BOUNDARY**: the keystone already fires on any `"ExprIR"` param, and it is corpus-load-bearing (fixtures 0748/0749/0878-0881 use it). The real gaps: (B1) a `kind_of`-bound local is not string-typed; (B2) a bare-Var `.get("value")` projects `svalue_of` instead of a string (response §Verdicts). **p14 hits a sibling of B2** (`.coll` → `svalue_of`). |
| `20260719-str-int-value-model-wall.md` | `str(int)` lowered int → int | broken later (`str_of_int`; `value-model-campaign.md` increment notes) |
| `pyval-value-model-wall.md` / `-impl.md` | faithful heterogeneous dict needs a `pyval` sum | model **PASSED** (oracle `getting-better/pyval-oracle.mlw`; theory emitted, cert Phase2f); **converts 0 stubs alone**. The count cut was gated on the input-statement dispatch, then on Call-internals (`IrCallKw`, Phase2g), then landed (J1+J2/J3) |
| `wall-lessons.md` (p) run #8 | — | "CHECK THE EXISTING VALUE MODELS BEFORE SCOPING A NEW CERTIFICATE BUILD": R3 rebuilt in hval what pydict already had (wall-lessons.md:1265-1285) |
| `wall-lessons.md` (q) | — | "the count is blocked on EMITTER RECOGNITION, not provability … the decisive spike is the RECOGNIZER falsifier … do not build cert+emitter infra that has no converting consumer" (:1286-1305) |
| `wall-lessons.md` 2026-07-21 run #3 | — | "value-model capability PLATEAU (3 infra, 0 conversions)" (:740-752) |
| `wall-lessons.md` 2026-08-03 worker #15 | — | "NO bounded projector-over-existing-leaves remains" (:1727-1740) |
| backlog `_csl_not_in CONVERTED (ef94162f)` | — | **the CSLNode → `"ExprIR"` live field retype lever works** and is corpus byte-inert (driver-backlog.md:4828-4833) |
| backlog ForExpand attempt | — | the retype worked at type level, then walled on threading a local `seq` accumulator into an `array` record field; reverted (driver-backlog.md:5315-5340) |
| backlog `_act_guard` | — | `isinstance(cl, Given)` over a heterogeneous `List[CSLNode]` needs a clause-discriminating variant. Later built as `Phase2k_CslClause` (driver-backlog.md:5005-5015; `irgiven-impl.md`) |
| `15a134ced` | — | 84 mirror CSL fields retyped `CSLNode` → `'ExprIR'`: proof-neutral, corpus-inert, mirror emission diff 1 of 52, **count unchanged**. "A field retype is contained to the record's own declaration … a RETURN-type retype rewrites the interface every caller … was verified against." |
| `46fec2387` | — | TypedDict closed-key views → records: **2 conversions**, byte-diff 0, gated on record-typed receivers |

---

## 4. The deeper truth: fundamental limit or modelling choice?

**[I] It is a modelling choice, with three hard sub-problems that are not "just add a sum type".**

1. **The universal value is definable, and already defined three times.** A strictly positive Why3 sum over Python values exists in three certified forms (`pyval`/`pydict`, `hval`, `emit_ir`). Each is axiom-free. Nothing fundamental stops `Any` from lowering to such a sum.

   **The obstacle is fragmentation.** The sums are disjoint types, chosen per idiom:
   - `HNode hval` cannot carry an `emit_ir`.
   - `pydict` keys are `irkey`, `hpairs` keys are `string`.
   - `csl_node` is a non-recursive view.

   A value crossing from a pipeline-IR dict into an emit_ir-typed callee needs a coercion that does not exist.
2. **Reflection is the real non-modelled residue.** Several of the 42 chains go beyond the value into the *class* of the value:
   - `type(node)` (`_csl_to_ir` uses `self._CSL_HANDLERS.get(type(node))`; mirror Module5_IREmitter.py:129-133).
   - `getattr(c, "act_name", None)`.
   - class objects as values (`cls = Exists if … else Forall`, s042 / lvC).
   - dataclass field reflection (`_subst_var`, `_subst_csl_param`).

   A value sum alone does not model these. They need a class-tag universe plus attribute tables per class. **[C]** That is how Nagini-style encodings do it (§5).
3. **Open-world dicts vs closed records.** The pipeline IR is an open, evolving schema: optional keys, `.get(k, default)` everywhere, keys added in place (`func["body"] = …`, `.setdefault`).
   - A closed record is only faithful when every read key is always present. A TypedDict field read **assumes presence**. G1 (`46fec2387`) lowers `func.get("pure")` to the field `func.pure`.
   - **[I]** This is a latent value-model over-claim: if the key is absent, CPython returns `None` and the model returns a `bool`. Under `ensures True` it cannot make a false type-safety proof. Under a value contract it could. The census has a separate capability for it (`cap-typeddict-optional-key`, `validate_ir`).
4. **SMT scale is a practical limit, not a theoretical one.**
   - `emit_ir` already has about 110 constructors; every `kind_of` / `size` match is an about-110-arm term.
   - Goal counts are 23424 (expressions) and 14817 (stmt_control_flow, 13546 s).
   - **[I]** Replacing int with a sum in *every* erased position adds case splits to VCs that today mention an opaque int. Whether this stays within the 2–6 h per-file envelope is unmeasured.
5. **The recognizer is the bottleneck.** This repeats lesson (q), and p14 confirms it. The model had all the pieces (`emit_ir`, `func_of`, `args_of`, `str_eq_op`). The missing parts were:
   - one annotation;
   - a narrowing that does not exist (`isinstance(x, DictView)` should change the static type of `x` to the `dictview` record);
   - an attribute-projection table keyed only by attribute name (`_EMIT_IR_STR_ATTRS`), which is wrong whenever two classes use the same attribute name for different things (`DictView.kind` vs the IR `"type"` tag).

---

## 5. State of the art: how other verifiers model dynamically typed nested values

These are from the literature and general knowledge, not measured here. Each is mapped to what PyCSL already has.

| approach | systems (examples) | encoding | PyCSL analogue / fit |
|---|---|---|---|
| **Algebraic sum ("JSON datatype")** | Dafny's JSON libraries (`datatype JSON = Null \| Bool \| String \| Number \| Array(seq<JSON>) \| Object(seq<(string, JSON)>)`); Creusot/Why3 ADTs; F* `json` | one inductive type; objects as assoc lists; projections are total functions with a default | `hval` (assoc-list `hpairs`) and `pydict` are exactly this. Fit: good for **values**; it does not cover reflection. |
| **Universal sort + type-tag function + axioms** | Nagini (Python on Viper: `Ref` values, `typeof(r)`, `issubtype` axioms, `PyType` uninterpreted); Dafny's Boogie encoding (`Box`, `$Box`/`$Unbox`, `$Is` typing axioms); Boogie/VCC "universal value" | uninterpreted carrier sort; a tag function; per-type injection/projection axioms | PyCSL's int + `py_isinstance_<C>_op` vals is a degenerate form of this **without** the injection/projection laws. Adding those laws as axioms is barred (ledger 3). They would have to be realized by a definitional model, i.e. back to the sum type. |
| **Occurrence typing / flow-sensitive narrowing** | Typed Racket (Tobin-Hochstadt & Felleisen), TypeScript discriminated unions, mypy/pyright `isinstance` narrowing | after `isinstance(x, C)` / `x["type"] == "K"`, the static type of `x` becomes `C` / the `K` arm | missing for the CSL records (p14: `dv` stays `emit_ir` after `isinstance(…, DictView)`). The emitter has narrowing for `Optional` / `is None` / Union arms only (warning text in p14 log: "narrows a Union-typed variable without a recognized guard"). |
| **Refinement over a universal type** | Liquid Haskell, F* refinements (`{v: json \| has_key v "type"}`), Stainless | sum type + logical predicates on shape | would express "this IR dict has key `type` = `Call` and a `func: string`". Fit: heavy; needs value contracts, which the conversion shape (`ensures True`) does not use. |
| **Schema → record (closed world)** | ATD/quicktype codegen, JSON Schema → ADT, Python `TypedDict` + mypy | each known shape becomes a record; unknown keys are rejected | the TypedDict View lever (`46fec2387`). Fit: good for the pipeline IR's *stable* records (function entry, record decl); poor for open walks (`for v in obj.values()`). |
| **Tagged pair (interface values)** | Gobra (Go interfaces as dynamic type + value), Prusti/Viper for trait objects | `(tag, payload)` with the payload in a per-tag type | `csl_node` (`PCsl_<C> <record>`) + `cslx_view` is this pattern; it is non-recursive and only dispatch-side today. |

**[I] Reading.** PyCSL already holds the two SOTA-standard constructive tools: a JSON-style sum, and a tagged view with per-class payload records. Three things are missing:
- occurrence-typing glue between them (narrow `emit_ir` → record after `isinstance`);
- a per-class (not per-attribute-name) projection table;
- coercions between its sums.

The axiomatic universal-sort route (Nagini/Dafny-Boogie) is closed by the ledger.

---

## 6. Routes (honestly costed)

Proof times are the recorded single-slot figures (§1.3), not my measurements. "Moves" means which mirror emissions change. These are inferred unless marked [M].

### R1: CSLIn retype + record narrowing on `isinstance(…, CSLClass)` + `IrMapValueIs` leaf (sub-seam A, smallest)

1. **Live annotation retype.** `CSLIn.element/collection: CSLNode` → `"ExprIR"` in `src/pycsl/frontend/Module2_Parser.py:526-529`.
   - Precedent: `ef94162f` (CSLNotIn), runtime-inert.
   - **[M] It clears link 1 of `_csl_in`** (p14).
   - **[C]** Expected corpus byte-diff 0. The precedent reported "2 changed-emission mirrors (Module5+pycsl) SUCCESS, byte-diff 0" (driver-backlog.md:4830-4831).
2. **Narrowing.** After `if isinstance(x, C)` where `C` is a class the model carries as a record, `x` is viewed as the `C` record within the branch. Attribute reads then use the record's own fields, `dictview_coll` / `dictview_kind`, never `_EMIT_IR_STR_ATTRS`.
   - **[I] Soundness needs care.** The model must *know* `x` is a `C` in that branch. The existing `py_isinstance_C_emit_ir_op` is uninterpreted, so a projection `emit_ir → dictview` would itself be an uninterpreted `val function`. That is sound as an over-approximation (an arbitrary `dictview`), but the branch would read *an* arbitrary `DictView`, not *this* one: honest about type, blind about value.
   - The value-faithful variant is an `IrDictView string string` arm, with `isinstance` defined as `match … IrDictView`. That is a new ADT arm and owes a cert touch (Phase2i/TermIR extension).
3. **A construction-only emit_ir leaf for `MapValueIs`.** This replaces `IrOther "MapValueIs"`, which drops `map/key/value`. Precedent: lever (3) "cert-free construction-only emit_ir leaf (kind_of/size wildcard arms, tight gate, no per-value law)", driver-backlog.md:4888.

| aspect | estimate |
|---|---|
| Yield | **1 stub** (`_csl_in`) if nothing else is behind it. **[I]** Unprobed tail: `self._cur_func_symtab.get(...)` compared to string literals (int-hashed, p01 line 3643), and `getattr(self, "_cur_func_vararg_str", None)` lowered to `pycsl_none`, so the guard becomes `(not (!_coll_nm = pycsl_none)) && (!_coll_nm = pycsl_none)` (p01 line 3640): a constant-false, value-unfaithful fold of the vararg branch. Both sit after the DictView branch. |
| Collateral value | removes the `.kind` misprojection hazard for every CSL class read after `isinstance`. **[I]** Also needed by s061 `_region_bound_str`. |
| Moves | Module5_IREmitter mirror (≈1 h proof) and pycsl mirror. A projection-table change in `expressions.py` would move **every** mirror using `.kind` on an emit_ir and touches a verified hot file (§10.4 re-port + expressions ≈ 6 h). Prefer a gate keyed on the narrowed-record case only. |
| Risk | low for step 1 (precedented); medium for step 2 (soundness of the narrowing, corpus-inertness of the gate); low for step 3. |

### R2: `List["ExprIR"]` plumbing and the dropped emit_ir-dict store (sub-seam A, list part)

- **[M] Return annotation not honoured.** `_csl_list_to_ir` with `-> List["ExprIR"]` is still emitted `: array int` (p13). Fix that, and give `materialize` an `emit_ir` instance (or emit a `seq emit_ir → array emit_ir` conversion).
- **[M] Dropped store.** `d["act_name"] = an` on an emit_ir-typed `d` lowers to `()` (p02/p13). **This must be refused, not converted.**
  - **[I]** It is a silently dropped mutation. The repo has a dropped-mutation gate (named in driver-run-log log 286, "dropped-mutation / getattr"), and **the reviewer should check whether that gate catches this site**.
  - A faithful model needs an emit_ir arm or wrapper that carries the attribution label. This is an IR-schema question: `act_name` is an *ad-hoc extra key* on an IR dict, the open-world problem of §4.3.
- **Yield.** `_csl_list_to_ir` (s072) gets one link further. `_parse_expr_list` (s044, materialize of seq emit_ir) and `_encode_callable_annotation` (s083, len of `array emit_ir`) share the list half. **Closes 0 stubs alone [I]**: s072 still needs the act_name decision.
- **Moves.** Return-type lowering lives in `functions.py` and the list lowering in `statements.py` / `expressions.py`, all VERIFIED hot twins. This owes §10.4 re-ports and expressions ≈ 6 h + statements ≈ 5.3 h. RULES.md rule 10 forbids running them concurrently.
- **Risk.** Medium. `materialize` is corpus-used for int lists, so the new instance must be gated on emit_ir element type to stay byte-inert.

### R3: schema-typed IR views for the pipeline IR (sub-seam B, 25 stubs)

- **Build.** Extend the TypedDict View lever (`46fec2387`, `scc.py:6`). Give the Module5 output IR closed-key views for the stable records:
  - program: `functions`, `type_decls`, `imports`;
  - function entry: `name`, `params`, `body`, `symbol_table`, `kind`, `pure`, …;
  - inductive decl;
  - the `needs` dict.

  Each becomes a WhyML record with per-field types. `List[FunctionView]` uses the banked `List[RecordType]` lever (`614fd814`, wall-lessons.md:745). `body` stays `stmt_ir` (Phase2d).
- **Optional keys** must be `option` fields, not presence-assuming fields (§4.3).
- **Yield.** It clears the first IR link on up to 25 chains. **[C]** Most of those chains carry a second, unrelated wall:
  - elem-store-nonlist (s113, s115, s112, s099): writes `func["body"] = …` through a list element, which is the r2c nested-container write-back wall;
  - R274 (s094, lvB);
  - closure-lift (s107, s135, s136);
  - FS models (s099, ir_resolve).

  **[I] Realistic closed yield ≤ 5 in one track**: s013/s016 (core_ir_semantic), s137, s140, s127.
- **Moves.** The `src/pycsl` annotations are runtime-inert, and mirror emissions move per file: core_ir_semantic ≈ 1.7 h, monomorphize / ir_resolve / preamble / scc (short-to-unmeasured; preamble is not in the recorded table). Module5 is moved only if the view types are declared there.
- **Risk.** Medium. Every view is a schema claim about IR the live code builds elsewhere; a wrong field type is a modelling bug that type-checks. Each view should be checked against the producing site in Module5 (an IR-schema conformance test would make this executable).

### R4: universal value type for `Any` (all sub-seams, the "no-more-int" project)

- **Build.** Lower `Any` / `object` / unannotated / `CSLNode` to one certified sum, unifying `hval`, `pydict` and `emit_ir` (or with coercions between them), and make the refusal net consult the tag instead of refusing.
- **Moves.** Every mirror and the corpus (corpus programs use `Any`; toy t6 shows the int model on a plain program). A sanctioned emission change: every moved corpus file re-proved, all 52 mirrors re-emitted, and all hot whole-file proofs (≈ 6 + 5.3 + 5 + 1 + 1 + 1.7 h ≈ 20 h of single-slot proof for the six named files alone, before any re-tuning).
- **Risk.**
  - High: SMT scale (§4.4).
  - Soundness: the refusal net was built for the int carrier, and every route would need re-deriving.
  - Lesson (q) says the recognizers per idiom remain the bottleneck even after the type exists.
- **Not recommended** as a next step. Note it as the endpoint R1–R3 converge to.

### Ranking

| rank | route | cost | first measurable gate | stubs moved | closed alone [I] |
|---|---|---|---|---|---|
| 1 | R1 | S (step 1) to M (steps 2-3) | re-run p14 with the narrowing patched; L3-tc on Module5; byte-diff sweep | `_csl_in` (+ s061 link) | 0-1 |
| 2 | R3 (core_ir_semantic slice first) | M per view family | port s013 with `FunctionView` + set-ctor route; L3-tc | up to 25 links | ≤5 |
| 3 | R2 | M + about 11 h hot proofs | p13 with the return honoured; refusal of the act_name store | s072, s044, s083 links | 0 |
| 4 | R4 | XL | — | all | — |

**Smallest sub-piece that converts the most stubs [I]:** no single sub-piece converts more than 1 stub (§3.1). The sub-piece with the most *links cleared per change* is the R3 `FunctionView` for the function-entry record. It is the first erased read on s013, s111, s113, s115, s137 and s140. Measure it before believing it.

---

## 7. Risks

1. **Soundness.**
   - (a) A narrowing that changes the static type without a model fact connecting `isinstance` to the payload (R1 step 2) is honest only as an over-approximation.
   - (b) Closed-record views assume key presence (R3; §4.3).
   - (c) The `_EMIT_IR_STR_ATTRS` attribute-name table already maps `.kind` to the node tag for any emit_ir-typed value (p14 line 3625). **[I]** Any converted body that reads a field called `kind`, `name`, `op`, `func`, `var`, `arr` or `ctor` on a non-IR object held as emit_ir is a latent value-unfaithful lowering. A grep of verified mirror bodies for such reads would bound the exposure. I did not run it.
2. **Corpus inertness.**
   - The emit_ir path is corpus-load-bearing (rawdict response: fixtures 0748/0749/0878-0881). Any change to projector selection or `materialize` must be gated so the corpus stays byte-identical, or be a sanctioned move with re-proofs.
   - Live annotation retypes (R1 step 1, R3 views) are runtime-inert, but they change emissions of every mirror that imports the class: measured as 1 of 52 for `15a134ced`.
3. **Proof scale.** Module5 (≈1 h) and core_ir_semantic (≈1.7 h) are affordable. Anything touching expressions / statements / stmt_control_flow / functions costs 5–6 h each and per RULES.md cannot run concurrently in pairs.
4. **Dead infra.** Per lesson (q) and run #3's plateau, do not build a model or certificate before a recognizer falsifier on the verbatim body shows the stub converts.
5. **Mirror-only vs live.** p11 shows a mirror-only retype of an imported class is **ineffective**, because records are read from live classes. Retypes of imported CSL classes must be live edits, so they carry a corpus sweep (expected 0).

---

## 8. Honest limits of this report

- I reproduced 7 stub ports plus 3 retype variants and 6 toys, all `--no-proof` (L3 type-check only). **No whole-file proof was run.** "TC ✓" here never means proved.
- Sub-seam classification (§3.1) is mine, from census row text. The 42-stub set and the file counts come from `scratchpad/cv9/merged.json`.
- Probes ran at HEAD `0e504dc78`, while the census base was `b432460d6`. First links agree on all 7 re-probed stubs.
- I did not re-probe sub-seams C and D beyond p04. The `IrProj emit_ir int` vs census-wording discrepancy (§3.1 C) is open.
- The SOTA table is from general knowledge of the cited systems. It is not a literature survey, and the encodings are described at the level of their published designs.
- Proof-time figures are recorded estimates (§1.3), not re-measured.
- My `\trusted` grep counts 528 lines containing `\trusted` and 385 marker lines (`^\s*#@ \trusted`) under `src/self-annotate/src`. The official count (413, log 490) uses a different counting rule, which I did not reconcile.

## 9. Questions for the independent reviewer

1. **Confirm or refute R1.** Patch `_csl_in` past p14 line 3624 in scratch. Does `dv.kind` stay lowered to `kind_of` (value-unfaithful)? Is a narrowing to the `dictview` record achievable without a new ADT arm and still non-vacuous?
2. Do the verified mirror bodies **already** contain a value-unfaithful `_EMIT_IR_STR_ATTRS` projection, i.e. a `.kind` / `.name` / `.func` read on a non-IR object held as emit_ir (§7.1c)?
3. Does the dropped-mutation gate catch `d["act_name"] = an` → `()` (p02 / p13)? If not, that is a gate hole independent of this wall.
4. For R3: port s013 (`run_ir_semantic_checks`) with a closed-key `FunctionView` plus a modelled `set()` constructor. Is the next wall another value-model gap, or a non-VM capability?
5. Is unifying `hval.HNode` with `emit_ir` (so heterogeneous dicts can carry IR nodes into emit_ir code) positivity-safe in Why3 and certifiable axiom-free? `pyval-value-model-wall-impl.md` kept `HNode hval` by caution, not by refutation.

## 10. Reproduce

```
cd /home/fabrice/git/pycsl
mkdir -p scratchpad/vmR/st && git archive 0e504dc78 src/pycsl src/self-annotate bin | tar -x -C scratchpad/vmR/st
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmR/batch1.sh   # p01-p07 (port-as-is)
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmR/batch2.sh   # toys t1-t6
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmR/batch3.sh   # p11 (mirror retype), p12/p13 (list retypes)
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmR/batch4.sh   # p14 (live CSLIn retype, restored after)
# results: scratchpad/vmR/probe/<tag>.{log,mlw,src.py,patchlog}, scratchpad/vmR/toy/<t>.{log,mlw}
python3 - <<'EOF'   # the 42-stub set
import json; m=json.load(open('scratchpad/cv9/merged.json'))
print(len([x for x in m if 'cap-vm-unerase-irnode' in (x['need'] or [])]))
EOF
```
