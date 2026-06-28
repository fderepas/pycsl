# PyCSL Formal Semantics — Security Audit Traceability Plan

> **Last refreshed:** 2026-06-28 (Phase F of `28-self-annotate.md`).
> This refresh adds the 12 typing constructs (TY0–TY3, §3.9), the IR
> 1.2→1.4 fields (§3.10), and the Module2 Lark-free migration note
> (§3.11). The Rocq/Lean proofs themselves were NOT modified — Phase F
> refreshes the map, not the proof.

## 1. Purpose

This document maps every user-facing feature of the PyCSL annotation language
(as catalogued in `test-suite/annotations.md`) to its formal proof artefacts
in the Rocq (Coq) and Lean 4 mechanisations under `src/formal-semantics/`.

The goal is to demonstrate to a security auditor that:

1. **Soundness** — if `wp s Q pre st` holds and `Exec st s out` terminates,
   then the postcondition `Q` holds on the output state.  This is the
   fundamental correctness guarantee of the PyCSL verification pipeline.
2. **Coverage** — which annotation features are represented in the formal
   model (and which are not, with justification).
3. **Reproducibility** — the proofs are machine-checkable and can be
   rebuilt from source with `make proof` in each directory.

---

## 2. Proof Architecture Summary

| Layer | Rocq file | Lean file | Contents |
|-------|-----------|-----------|----------|
| AST | `Phase1_AST.v` | `PyCSL/AST.lean` | `expr`, `contract_expr`, `stmt`, `func_spec` |
| State | `Phase2_State.v` | `PyCSL/State.lean` | `state`, `val`, `lookup`, `update`, `evalExpr`, `evalBool`, `evalContract`, `evalVariant` |
| Operational semantics | `Phase3_SOS.v` | `PyCSL/SOS.lean` | `Exec` inductive (14 constructors), `exec_deterministic` |
| Desugaring | `Phase3b_Desugar.v` | `PyCSL/DesugarDef.lean` + `Desugar.lean` | `for→while` lowering, `desugar_correct` (Admitted/sorry) |
| WP calculus | `Phase4_WP.v` | `PyCSL/WP.lean` | `wp` fixpoint with 3 continuations (Qn, Qr, Qc) |
| While helpers | `Phase5a_WhileInv.v` | `PyCSL/WhileInv.lean` | `while_not_continued`, `while_inv_preserved` |
| **Soundness** | **`Phase5b_Soundness.v`** | **`PyCSL/Soundness.lean`** | **`pycsl_soundness` — FULLY PROVED** |
| Tests | `Tests.v` | `PyCSL/Tests.lean` | Concrete execution and WP tests |

### Proof status

| Prover | Files | Main theorem | Gaps |
|--------|-------|-------------|------|
| Rocq 8.20 | ~35 .v files | `pycsl_soundness` — 0 Admitted | None (Q1 close-out + Q3 Sub-β complete) |
| Lean 4.29 | ~14 .lean files | `pycsl_soundness` — 0 sorry | None (Q1 close-out complete) |

**Q3 Sub-β closure (2026-05-29):** the prior axioms
`module6_encodes_mlw` and `why3_validates_emitted` have been
ELIMINATED from the Rocq Why3-validation chain. The
`why3_certificate` type (Phase6j_Why3Trust.v) is now the witness
type directly — constructing one REQUIRES the eval_vc_formula
proof for every emitted VC. All downstream theorems
(`vcg_bridge`, `module6_encodes_mlw`, `why3_validates_emitted`,
`why3_implements_wp_w_derived`) are now PROVED Lemmas with
zero axioms. The trust line moved to the cert construction site
(uninhabited in pure Rocq; reified from external Why3 in Lean's
`Why3Trust.check`). See `friday-01.md` for details.

**Q1 close-out (2026-05-29):**
- C.1 (`desugar_correct`): proved (Phase3b_Desugar.v:153-160).
- C.2 (`while_not_continued`): proved (WhileInv.lean:59-64).
- C.3 (`while_inv_preserved`): proved (WhileInv.lean:197-240).
- L.1 (`spec_no_exception : list ident`): added (Phase1_AST.v:136).
- L.2 (`allow_iter_mut : bool` on SFor): added (Phase1_AST.v:163).
- L.3 (`spec_allow_finalizer : bool`): added (Phase1_AST.v:137) —
  attached to function spec (no class records in formal AST).
- L.4 (`spec_trusted` design): realized as two-field design
  `spec_trusted : bool` + `spec_reviewer : option string`
  (Phase1_AST.v:132-133) rather than the plan's unified
  `option REVIEWER_ID`. The two-field shape separates concerns
  (is-trusted vs reviewed-by) — accepted as L.4 done with
  different shape.

**Q2 Sub-α close-out (2026-05-29):**
- α.1-α.13 per-construct emit_stmt theorems: all landed.
  Files: `Phase6L_Emit{Stmt,Assign,AugAssign,ArraySet,Seq,Simple,Blocks,Composition,StateAware,StateAwareCorr,Extract}.v`
  and their Lean mirrors under `src/formal-semantics/lean/PyCSL/Emit*.lean`.
  See feature-matrix rows 15-23 for the per-construct map.
- α.14 composition: `emit_stmt_full_complete_sound`
  (`Phase6L_EmitComposition.v`) covers all 22 Stmt constructors —
  the aggregate result that enables discharge of
  `module6_encodes_mlw`.
- α.15 state-aware refined printer + correspondence theorem
  (`Phase6L_EmitStateAware.v` + `Phase6L_EmitStateAwareCorr.v`):
  closes byte-diff DIFFs on the 26-case corpus (26 PASS / 0 DIFF).
- `module6_encodes_mlw` was a *named axiom* pre-Sub-α; post Q3
  Sub-β port it is a PROVED Lemma in `Phase6m_VcgSemBridge.v`
  with zero axioms. Composition+state-aware printers + Q3
  Sub-β's `formula_rep` integration close the gap.
- Remaining residue: the extraction-extensional residue
  (CC.5) — meta-level claim between the Rocq-extracted
  pretty-printer and the Python Module 6 pretty-printer.
  Validated by `bin/extraction-byte-diff-upward.sh` on the
  real corpus (89.6% PASS as of the v6 run). See
  [`docs/glossary/extraction-extensional-residue.md`](../../docs/glossary/extraction-extensional-residue.md).

**Q4 Upward close-out (2026-05-29):**
- U.1 (`pycsl_ir_json` inductive): landed
  (`Phase0_IrJson.v` — JsonValue / ContractsIR / FunctionIR /
  ProgramIR records).
- U.2 (`ir_to_stmt : pycsl_ir_json → option stmt`): landed
  (`Phase1b_IrToStmt.v`, ~1300 LOC, 18 smoke tests).
- U.3 (`validate_ir_correspondence`): landed
  (`Phase1c_ValidateIr.v` — `validate_ir` + `WellFormedIR` +
  `KeysUniqueRec` + `well_formed_and_unique_implies_validate`).
- U.4 (extraction byte-diff on the real corpus): landed
  (`Phase1b_IrToStmtExtract.v` + `extracted/ir_driver.ml` +
  `bin/extraction-byte-diff-upward.sh`). Real-corpus
  PASS rate: 346/386 = 89.6% (24 SKIP outside the formal
  subset; 16 FAIL_M5 — Module 5 limits, not Rocq disagreement).
- U.5 (per-stmt-constructor round-trip): landed
  (`Phase1d_StmtToIr.v` — 68 round-trip lemmas covering
  the simple-subset constructors and compound stmts
  including SAssert / SGhostDecl / SGhostAssign / SFor case-a;
  +SFor case-b range desugaring as a one-way lemma).
- U.6 (chain composition): landed
  (`U6_chain_after_roundtrip` ties the round-trip output to
  `gen` for the full `ast → IR → stmt → whyml_stmt → text → VC`
  chain).
- **Trust seam post-Q4: the IR boundary.** Modules 1-4
  remain `\trusted reviewer:` by design (CC.6 out-of-scope:
  libcst ingestion, Lark parsing, AST weaving, semantic
  analysis). Module 5's IR-output shape is now verified by
  the U.3 correspondence and the U.4 byte-diff. See
  [`docs/glossary/trust-seam.md`](../../docs/glossary/trust-seam.md)
  and [`docs/glossary/ir-well-formedness.md`](../../docs/glossary/ir-well-formedness.md).

**Trust boundary table (post-Q4):**

| Modules | Status | Rationale |
|---------|--------|-----------|
| 1-4 (Python frontend) | `\trusted reviewer:` | CC.6 out-of-scope — libcst ingestion + the hand-written recursive-descent contract parser (Module2, migrated off Lark 2026-06-27 — see §3.11) + AST weaving + semantic analysis. The Module2 Lark→recursive-descent swap is a parser-engine change; the `#@` contract grammar surface is unchanged, so it has no formal-semantics impact. |
| 5 (IR shape) | ✅ Verified | U.3 well-formedness correspondence + U.4 byte-diff against real corpus |
| 6 (WhyML transpilation) | ✅ Verified | Q2 Sub-α per-construct + composition + state-aware byte-diff |
| WP / VCG / soundness | ✅ Verified | `wp_gen_correct`, `vcg_sound`, `pycsl_soundness` — all proved with zero PyCSL-specific axioms in Rocq |
| Why3 trust certificate | ✅ Verified | Q3 Sub-β cert-as-witness; `why3_certificate` is now the witness type |
| Alt-Ergo / Z3 | Tier 1 (named) | `altErgoCorrect` axiom; mitigation = parallel solver dispatch |
| Why3 kernel | Tier 2 | Sub-β formalizes only the formula evaluation subset PyCSL uses |
| Standard library stubs | Tier 2 | `data/lib_stubs/<module>.py` `\trusted reviewer:` |

---

## 3. Feature-to-Proof Traceability Matrix

The table below lists each feature from `test-suite/annotations.md` and
maps it to the formal model elements that cover it.

### 3.1 Function/Method Contracts (§2.1 of annotations.md)

| # | Feature | Covered | Rocq artefact | Lean artefact | Notes |
|---|---------|---------|---------------|---------------|-------|
| 1 | `requires` | ✅ | `func_spec.spec_pre` in AST; WP assumes pre at entry | `AST.lean` `FuncSpec` | Pre is a `contract_expr` evaluated by `evalContract` |
| 2 | `ensures` | ✅ | `func_spec.spec_post`; soundness guarantees post on normal exit | `AST.lean` `FuncSpec` | Post checked via Qn continuation |
| 3 | `assigns` | ✅ (model) | `frame_cond` type (`FNothing`/`FVars`) in AST | `AST.lean` `FrameCond` | Frame conditions modelled in AST; enforcement delegated to WhyML transpiler |
| 4 | `\variant` (function) | ⚠️ Partial | Not in stmt-level WP (function-level termination is outside stmt semantics) | Same | Function-level variant is a transpiler concern; stmt-level variant ✅ in while |
| 5 | Structural `\variant` | ✅ (vacuous) | `vacuous-soundness.md` §E.1 | Same | Partial-correctness theorem doesn't cover termination; structural variants are Why3-level |
| 6 | `\diverges` | ✅ (vacuous) | `vacuous-soundness.md` §E.2 | Same | Hypothesis `exec` never fires for diverging functions; postcondition holds vacuously |
| 7 | `\trusted` | ✅ (vacuous) | `vacuous-soundness.md` §E.3 | Same | By design outside verification scope; manual audit item |
| 8 | `bounded_int(N)` | ✅ (vacuous) | `vacuous-soundness.md` §E.4 | Same | WP structure unchanged; overflow VCs delegated to Why3 `mach.int` |
| 9 | `raises` | ❌ | Not modelled | Not modelled | Exception handling not in the core stmt language |
| 10 | `thread_entry` | ❌ | Not modelled | Not modelled | Concurrency model is a separate concern (§3.6) |
| 11 | `no_exception` | ✅ (AST) | `func_spec.spec_no_exception : list ident` (Phase1_AST.v:131, added Q1.L.1 2026-05-28) | `AST.lean` `FuncSpec.noException` | Field captured at AST level; WP rule unchanged because the directive's semantic effect (`assert {trigger_E}` injection) happens at IR emission time. Full emission correspondence requires Q2 Sub-α. |
| 12 | `\trusted reviewer:` | ✅ (AST) | `func_spec.spec_reviewer : option string` (Phase1_AST.v:128, added Q1.L.4 2026-05-28) | `AST.lean` `FuncSpec.reviewer` | Accountability metadata; no WP impact (delegated trust same as bare `\trusted`). |
| 13 | `allow_iteration_mutation` | ⚠️ Deliberate omission | Not in stmt model | Not in stmt model | The flag has no WP impact — it gates a Module 4 static check, not the WP calculus. Adding it to `SFor` would force a 53-site pattern-match cascade across the Rocq proof tree (and 8 sites in Lean) with no soundness benefit. Modelled in Q4 at the IR-JSON level instead. |
| 14 | `allow_finalizer` | ⚠️ Deliberate omission | Not in stmt model | Not in stmt model | Same rationale as `allow_iteration_mutation`: transpiler-only flag with no WP impact. The formal `stmt` type captures the WP-relevant subset of PyCSL's IR; transpiler-only flags belong in Q4's IR-level formalization. |
| 15 | Surface emission — wSkip (Sub-α pilot) | ✅ (pilot) | `Phase6L_EmitStmt.v:emit_skip_correct` (added Q2 Sub-α.1 2026-05-28) | `EmitStmtSurface.lean:emitSkipCorrect` | First per-construct emit_stmt theorem. `emit_stmt (gen SSkip) ∈ ["()"]`. Establishes the methodology; 14 more constructs pending (Sub-α.2 wAssign through Sub-α.13 wAssert). Lean side: `emitSkipCorrect` depends on `[propext]` only. |
| 16 | Surface emission — wAssign (Sub-α.2 full state coverage) | ✅ (Expr-typed RHS) | `Phase6L_EmitAssign.v:emit_assign_correct`, `emit_stmt_s_assign_correct` (added Q2 Sub-α.2 2026-05-28) | `EmitAssign.lean:emitAssignCorrect`, `emitStmtStringStateAssignCorrect` | Models `_handle_assign_stmt` (statements.py:61-103) for inputs of formal `expr` type. Three reachable branches (shared / fresh-local default / fresh-local bounded_int) all proved. Branches eliminated by `expr`'s narrowness (record/lambda/array/slice/dict/val_is_bool/array_locals) documented in file header as Q4-deferred. Lean axioms: `[propext]`. Presentational gap (ref-deref `!x`) deferred to CC.5 byte-diff validation. |
| 17 | Surface emission — wAugAssign (Sub-α.3) | ✅ (Binop-typed) | `Phase6L_EmitAugAssign.v:emit_aug_assign_correct` (added 2026-05-28) | `EmitAugAssign.lean:emitAugAssignCorrect` | Default branch only fires on formal `binop` (4 variants); bitwise + array-extend branches unreachable. Singleton acceptable set. |
| 18 | Surface emission — wArraySet (Sub-α.4) | ✅ (canonical + fallback) | `Phase6L_EmitArraySet.v:emit_array_set_correct` (added 2026-05-28) | `EmitArraySet.lean:emitArraySetCorrect` | Two surface forms accepted: is_array native (`arr[i] <- v`) and subscript_set fallback. 2D-array / dict / heap-model branches unreachable on formal `SArraySet`. |
| 19 | Surface emission — wSeq + recursive emit_stmt_full (Sub-α.5) | ✅ | `Phase6L_EmitSeq.v:emit_seq_correct`, `emit_stmt_full_*_correct` (added 2026-05-28) | `EmitSeq.lean:emitSeqCorrect`, `emitStmtFull*` | First recursive Fixpoint over `whyml_stmt`. Sequencing is `emit w1 ++ ";\n" ++ emit w2`. Unifies prior per-construct state-aware variants. |
| 20 | Surface emission — wRaise / wLabel / wAssert (Sub-α.8/.12/.13) | ✅ | `Phase6L_EmitSimple.v:emit_raise_correct`, `emit_label_correct`, `emit_assert_correct` (added 2026-05-28) | `EmitSeq.lean:emitRaiseCorrect`, `emitLabelCorrect`, `emitAssertCorrect` | Single-line simple constructs. `WAssert` divergence: Module 6 erases Python `assert` to `()` per statements.py:1096; formal `WAssert cond msg`'s content is unused at emission. Documented. |
| 21 | Surface emission — wIf / wWhile / wTryCatch / wGhostDecl / wGhostAssign (Sub-α.6/.7/.9/.10/.11) | ✅ | `Phase6L_EmitBlocks.v:emit_if_correct`, `emit_while_correct`, `emit_try_catch_correct`, `emit_ghost_decl_correct`, `emit_ghost_assign_correct` (added 2026-05-28) | `EmitBlocks.lean:emitIfCorrect`, `emitWhileCorrect`, `emitTryCatchCorrect`, `emitGhostDeclCorrect`, `emitGhostAssignCorrect` | Final five constructs of the Sub-α series. wIf has 3 acceptable surface forms (with/without orelse, body_returns_value); wWhile, wTryCatch have canonical singleton forms; wGhostDecl/Assign dispatch per ghost_type (9 variants) and aug_op (3 ops). Introduces `pretty_contract_expr` (partial — covers the structural subset, deferring 30+ contract constructors as `?contract?`). Final fixpoint `emit_stmt_full_complete` subsumes all 13 WhyMLStmt constructors. Lean axiom dependency: `[propext]` or `[propext, Quot.sound]`. |
| 22 | All 13 WhyMLStmt constructors covered by `emit_stmt_full_complete` | ✅ | `Phase6L_EmitBlocks.v` final Fixpoint (2026-05-28) | `EmitBlocks.lean` final def | Composition lemma for the (now-eliminated) `module6_encodes_mlw` axiom — every constructor case is individually proven. Post-Q3-Sub-β port (2026-05-29), `module6_encodes_mlw` itself is a PROVED Lemma in Phase6m_VcgSemBridge.v; the remaining residue is the CC.5 byte-diff validation between Rocq-extracted output and actual Module 6 Python output. |
| 23 | Sub-α.14 composition lemma — all 22 Stmt constructors covered | ✅ | `Phase6L_EmitComposition.v:emit_stmt_full_complete_sound` (added 2026-05-28) | `EmitComposition.lean:emitStmtFullCompleteSound` | Aggregate correctness theorem: for every Stmt s, `emit_stmt_full_complete state (gen s) ∈ acceptable_emit state s`. Proved by case analysis on 22 Stmt constructors. The 8 constructors with direct WhyMLStmt mappings dispatch to their Sub-α per-construct lemmas; the compound (SSeq/SIf/SWhile/STryCatch/SFor) and derived (SReturn) cases unfold structurally; the simplified-to-WSkip cases (STupleUnpack/SFieldAssign/SFieldAugAssign) and transparent cases (SCritical/SThreadEntry) are discharged definitionally. Lean axioms: `[propext, Quot.sound]`. **This is the key intermediate result enabling discharge of `module6_encodes_mlw`** — the remaining gap is the CC.5 byte-diff validation between Rocq-extracted output and actual Module 6 Python output. |
| 24 | CC.5 byte-diff validation tooling (Rocq-extracted ↔ Module 6) | ✅ (foundation + 26-case corpus) | `Phase6L_EmitExtract.v` Rocq extraction directives; `extracted/EmitExtract.ml` auto-generated OCaml; `extracted/driver.ml` test driver; `bin/extraction-byte-diff.sh` + `bin/extraction-byte-diff.py` end-to-end runner; `test-suite/extraction-byte-diff/cases.txt` (added/expanded 2026-05-28) | N/A — tool runs against Rocq extraction only | Foundation tool. The 26-case corpus exercised against the structural printer scored 16 PASS / 10 DIFF. Each DIFF was in the formal acceptable surface set documented per Sub-α — empirical confirmation that the acceptable sets are correctly designed. See row 25 for the refined state-aware printer. |
| 25 | State-aware refined printer (closes all DIFFs on the corpus) | ✅ | `Phase6L_EmitStateAware.v:emit_stmt_state_aware` (added 2026-05-28); extracted alongside the structural printer | N/A (Rocq-only for byte-diff use) | A CPS-style state-aware variant that threads a continuation through the recursion. Refinements vs. structural printer: (D) `pretty_expr_state` emits `!x` for `EVar x` when x ∈ `aw_local_refs`; (A) emits `(iter_length arr)` / `(subscript_get arr i)` when arr ∉ `aw_array_locals` (else native `[i]` syntax); (B) `to_bool_state` wraps if/while conditions with `(<expr> <> 0)`; (T) scoping constructs (`let-in`, `let ghost`, `label-in`) substitute `"()"` when the continuation is empty (matching Module 6's `if not rest_code: rest_code = "()"`); (S) `WArraySet` picks `arr[i] <- v` when arr ∈ `aw_array_locals`, `subscript_set arr i v` otherwise. **Result on the 26-case corpus: 26 PASS / 0 DIFF** — byte-for-byte agreement with Module 6 on every case. The state-aware printer is a refinement of the structural one; it does not replace `emit_stmt_full_complete` (the proved correctness theorems still apply to the structural printer). |
| 26 | State-aware refinement correspondence theorem | ✅ | `Phase6L_EmitStateAwareCorr.v:emit_stmt_state_aware_sound` (added 2026-05-28) | N/A (Rocq-only) | Parallel composition lemma to `emit_stmt_full_complete_sound` (row 23): for every Stmt s and aware_state aw, the state-aware emission lies in `acceptable_aware_emit aw s`. The acceptable-aware sets are singletons because the state-aware printer is deterministic given a state. Plus per-construct sanity lemmas: `aware_emit_skip`, `aware_emit_continue`, `aware_emit_break`, `aware_emit_assert`, `aware_emit_aug_assign`, `aware_emit_ghost_assign_int`, transparent equations for SCritical/SThreadEntry, and a determinism corollary. Trust-chain implication: BOTH printers have verified composition lemmas; the structural one is broad-acceptable-set, the aware one is singleton (a specific element). Together with the empirical CC.5 byte-diff (26 PASS / 0 DIFF), this establishes that the state-aware printer captures Module 6's actual emission exactly. |
| 27 | CC.5 byte-diff on REAL reference tests via IR→Rocq-AST bridge | ✅ | `bin/pycsl-ir-dump.py` (IR JSON extractor); `bin/ir-to-rocq-ast.py` (simple-subset IR→OCaml `whyml_stmt` converter); `bin/extraction-byte-diff-real.sh` (orchestrator); `test-suite/extraction-byte-diff/reference-cases/synth-001..004.py` (synthetic subset-fitting tests) — added 2026-05-28 | N/A — tooling | Foundational Q4 IR-bridge step, scoped to a simple subset (Pass, Assign, AugAssign, ArraySet, WSeq + simple expressions: Number, Var, BinOp(+/-/*//), Subscript(Var,_), Call(len, [Var]), UnaryOp(-)). Survey of all 386 reference tests: 19 fit the subset, 187 are Return-only (skipped — empty after Return-drop, formal/Module 6 differ on empty-body convention), 180 outside subset (comparisons, calls, classes, etc.). **Result on 4 synthetic + 19 real-corpus tests: 23 PASS / 0 DIFF byte-equivalent**. The state-aware Rocq printer reproduces Module 6's output exactly on real PyCSL programs that fit the formal expression language. Closes the loop for the simple subset; expansion of the subset (comparisons, function calls, class methods) requires extending the formal `expr` type — the next Q4 milestone. |
| 28 | Formal `expr` extended with comparisons (`ECmp`) | ✅ | `Phase1_AST.v:cmpop + ECmp` constructor; `Phase2_State.v:eval_cmpop_z + ECmp` eval arm; `Phase6L_EmitAssign.v:pretty_cmpop + ECmp` pretty arm; `Phase6L_EmitStateAware.v:ECmp` aware arm + `coerce_int_rhs` for `(if c then 1 else 0)` wrap on bool RHS — added 2026-05-28 | `AST.lean:CmpOp + cmp`; `State.lean:evalCmpOpZ + cmp` eval; `EmitAssign.lean:prettyCmpOp + cmp` — added 2026-05-28 | Extends the formal expression language with the 6 comparison operators (=, <>, <, <=, >, >=). Comparisons evaluate to 0/1 in the int domain (matching Python's bool↔int interop). Pretty-printer emits raw `(e1 op e2)` for comparison in expression position; the state-aware printer adds `(if … then 1 else 0)` wrap when the comparison is the RHS of an int-typed assign (matching Module 6's `_val_is_bool` branch). All 13 per-construct Sub-α theorems + composition lemma rebuild cleanly with only 2 match-arms updated (pretty_expr and pretty_expr_state). `ir-to-rocq-ast.py` updated to handle BinOp comparison ops and Compare nodes. Byte-diff still 24/24 PASS on the extended real-corpus suite; new synth-005 case exercises ECmp in expression position. **Main theorems unchanged**: `pycsl_soundness` axiom set still `[propext, Classical.choice, Quot.sound]`. |
| 29 | Converter extended with While, If, and state-aware contract pretty-printer | ✅ | `bin/ir-to-rocq-ast.py` (added `conv_contract_expr`, While + If handlers, If-with-Return rejection); `Phase6L_EmitStateAware.v` (added `pretty_contract_expr_state` and refined `to_bool_state` to skip wrap on ECmp) — 2026-05-28 | — | Unlocked 11 additional real-corpus tests (19 → 30) by handling While loops with single invariant/variant, If with both branches, and refining the bool-coercion wrap (`(x <> 0)` only added for non-comparison conditions). The 16 If-body-with-Return cases are CLEANLY REJECTED — Module 6's "bare value as last expression" emission convention diverges from the formal model's `gen` of Return. **Result: 35/35 PASS, 0 DIFF** on 5 synthetic + 30 real-corpus tests. The state-aware contract pretty-printer emits `!x` for ref-tracked variables inside `invariant {…}` and `variant {…}` clauses (matching Module 6's behavior when local_refs is passed to `_handle_var_expr` in spec context). |
| 30 | Converter extended with Label/Break/Continue/Raise/Assert/Try/GhostAssign | ✅ | `bin/ir-to-rocq-ast.py` (added 7 new stmt handlers); `Phase6L_EmitStateAware.v` (WIf detects WSkip-else and omits the else clause to match Module 6's no-orelse emission) — 2026-05-28 | — | Unlocked 11 more real-corpus tests (30 → 41). New handlers: Label → WLabel, Break/Continue/Raise → WRaise variants, Assert → WAssert, Try → WTryCatch (single-handler), GhostAssign → WGhostDecl (op="=") or WGhostAssign (op="+="/"-="/"*="). GhostAssign limited to GTInt type for v1. The WIf state-aware refinement: when `f = WSkip` Module 6's IR comes from empty orelse (no source `else:`) so the printer omits the else clause; explicit `else: pass` would be modeled differently if the formal AST supported the distinction. **Result: 46/46 PASS** — 5 synthetic + 41 real-corpus tests byte-equivalent. |
| 31 | Broader ghost type support (all 9 GhostTypes, dict-tuple special case) | ✅ | `bin/ir-to-rocq-ast.py` (GHOST_TYPE_MAP expanded to all 9, ghost-type tracking across body, ghost contract atoms: MkTuple, GhostCopy/Make/CopyRange, MapEmpty/Get/Set/HasKey, GhostNil/Cons, SetEmpty/Add/Mem/Card); `Phase6L_EmitStateAware.v` (state-aware `pretty_contract_expr_state` with ghost atoms; state-aware `emit_ghost_decl_aware` and `emit_ghost_assign_aware` using it; WGhostDecl GTList+CGNil special-cased to `(Nil: list int)`; GTDict+AugAdd+CGMkTuple2 special-cased to `(Map.set !x k (Some v))`) — 2026-05-28 | — | Unlocked 3 more real-corpus tests (41 → 44 fits, 49 in byte-diff suite with addition of 0297/0300/0301). **Result: 49/49 PASS** on real-corpus suite. Cleanly handles ghost int/string/array/dict/list/set/tuple types. The converter mirrors Module 6's `_resolve_effective_ghost_type` by tracking the type declared at the first GhostAssign(op="=") per target, so subsequent augassigns use the dynamically-resolved type rather than Module 5's static "int" IR hint. The state-aware contract printer adds ghost-atom emissions matching Module 6's exact byte output (`(Array.make n v)`, `(const (None: option int))`, `(const false)`, `(Cons …)`, `(Map.set …)`, etc.). |
| 32 | WWhile extended with list of invariants/variants | ✅ | `Phase6_WhyML.v` (WWhile takes `list contract_expr` for invs/vars + `c_conj` and `c_first` helpers); `Phase6d_StmtGen.v` (gen wraps singleton); `Phase6b_WPW.v`, `Phase6k_VcgSound.v`, `Phase6m_VcgSemBridge.v` (let-binding inv/var via c_conj/c_first + set tactic in proofs); `Phase6L_EmitBlocks.v` (emit_while takes list); `Phase6L_EmitComposition.v` (acceptable_emit wraps singleton); `Phase6L_EmitStateAware.v` (emit_cont WWhile arm + emit_invariant_lines/emit_variant_lines for one-line-per-element; OpDiv in pretty_expr_state → `(pycsl_div …)`, in pretty_contract_expr_state → `(div …)`); `bin/ir-to-rocq-ast.py` (emits list, rejects op="=" reassign for vars already declared) — 2026-05-28 | `AST.lean` / `WhyML.lean` / `StmtGen.lean` / `WPW.lean` / `Why3Vcg.lean` / `VcFormula.lean` / `EmitVcList.lean` / `EmitBlocks.lean` / `EmitComposition.lean` / `VcgSemBridge.lean` / `CorrLoops.lean` parallel updates | Unlocked 19 more real-corpus tests (44 → 63 fits). **Result: 68/68 PASS** on real-corpus suite. The state-aware printer now emits one `invariant {…}` line per source invariant, matching Module 6's `_handle_while_stmt` iteration. The semantics of multi-invariant while is captured by `c_conj` (logical conjunction) in the WP rules; multiple variants take only the first via `c_first` (lexicographic ordering deferred). All proved theorems (Sub-α composition lemma, refinement correspondence, main soundness) rebuild clean. |
| 33 | CriticalSection support via WAssume + WAssert promoted to spec-assert | ✅ | `Phase6_WhyML.v` (new `WAssume (cond : contract_expr)` constructor); `Phase6b_WPW.v`, `Phase6f_Corr_Loops.v`, `Phase6k_VcgSound.v`, `Phase6m_VcgSemBridge.v` (WP/VCG arms for WAssume: `eval_c cond -> Q.wc_n es`); `Phase6L_EmitBlocks.v`, `Phase6L_EmitSimple.v`, `Phase6L_EmitSeq.v`, `Phase6L_EmitStmt.v`, `Phase6L_EmitStateAware.v` (pretty-printer arms emitting `assume { cond }`; **WAssert promoted from erased-`()` to spec-level `assert { cond }`**); `bin/ir-to-rocq-ast.py` (CriticalSection → `WSeq (WAssume assume_inv) (WSeq body (WAssert prove_inv))`; Python `assert` → `WSkip` matching Module 6's erasure; WhyML-reserved-keyword check on identifiers; reject CS-body-ending-with-Return) — 2026-05-28 | — | Unlocked 22 more real-corpus tests (63 → 85 fits, 90 in byte-diff suite). **Result: 90/90 PASS** on real-corpus suite. The Sub-α.13 wAssert semantic was refined: WAssert now means "spec-level assert" (emitting `assert { cond }`); Python's runtime `assert` statement converts to WSkip (matching Module 6's erasure). The new WAssume mirrors WAssert but emits `assume { cond }` — used for critical-section pre-condition assumptions. Lean side untouched (CriticalSection support is Rocq-only for byte-diff use). |

### 3.2 Loop Contracts (§2.2)

| # | Feature | Covered | Rocq artefact | Lean artefact | Notes |
|---|---------|---------|---------------|---------------|-------|
| 1 | `loop invariant` | ✅ | `SWhile inv` field; WP checks inv at entry, preservation, and exit | `Stmt.while_ inv` | Invariant is checked in all 3 while WP clauses |
| 2 | `loop variant` | ✅ | `SWhile var` field; WP requires `evalVariant st'' < evalVariant st'` ∧ `≥ 0` | `Stmt.while_ var` | LOCAL variant bound (key design: `< at st'`, not `< at initial st`) |

### 3.3 Class Contracts (§2.3)

| # | Feature | Covered | Rocq artefact | Lean artefact | Notes |
|---|---------|---------|---------------|---------------|-------|
| 1 | `class invariant` | ❌ | Not modelled | Not modelled | Class invariants are a WhyML record-type feature; not in core stmt semantics |

### 3.4 Program Point Annotations (§2.4)

| # | Feature | Covered | Rocq artefact | Lean artefact | Notes |
|---|---------|---------|---------------|---------------|-------|
| 1 | `label` | ❌ | Not modelled | Not modelled | Labels and `\at` reference program points; transpiler feature |
| 2 | `ghost` assign | ❌ | Not modelled | Not modelled | Ghost variables are erased; transpiler inserts them in WhyML |
| 3 | `ghost` augmented assign | ❌ | Not modelled | Not modelled | Same as above |
| 4 | `critical` | ❌ | Not modelled | Not modelled | Concurrency model (§3.6) |
| 5 | `acquires` | ❌ | Not modelled | Not modelled | Concurrency model |
| 6 | `releases` | ❌ | Not modelled | Not modelled | Concurrency model |

### 3.5 Expression Language (§3)

| # | Feature | Covered | Rocq artefact | Lean artefact | Notes |
|---|---------|---------|---------------|---------------|-------|
| 1 | Integer literals | ✅ | `EInt n` / `CInt n` | `Expr.int n` | Z (arbitrary precision) |
| 2 | Variable reference | ✅ | `EVar x` / `CVar x` | `Expr.var x` | String-keyed lookup |
| 3 | `self.field` | ❌ | Not modelled | Not modelled | Class semantics not in core |
| 4 | `arr[i]` | ✅ | `ESubscript arr i` / `CSubscript` | `Expr.subscript` | Array access via evalExpr |
| 5 | `\result` | ✅ | `CResult`; ExecReturn binds `\result` in state | `ContractExpr.result` | Soundness: Return case applies Qr to `update st "\result" v` |
| 6 | `\old(e)` | ✅ | `COld e`; `evalContract` uses `pre_st` | `ContractExpr.old` | `evalZ` dispatches to `preSt` for old |
| 7 | `\at(e, L)` | ❌ | Not modelled | Not modelled | Label-based references are transpiler-level |
| 8 | `\length(arr)` | ✅ | `CLength arr` | `ContractExpr.length` | `evalZ` extracts array length |
| 9 | `\valid(arr, n)` | ❌ | Not modelled | Not modelled | Typed/store memory model feature |
| 10 | `\separated` | ❌ | Not modelled | Not modelled | Typed/store memory model feature |
| 11 | `\length2d` | ❌ | Not modelled | Not modelled | 2D array extension |
| 12 | `\valid2d` | ❌ | Not modelled | Not modelled | 2D array extension |
| 13 | `\nothing` | ✅ | `FNothing` in `frame_cond` | `FrameCond.nothing` | Frame condition = no mutation |
| 14 | String literals | ❌ | Not modelled | Not modelled | Strings not in core value domain |
| 15 | `\is_sorted` | ❌ | Not modelled | Not modelled | Library predicate (WhyML axiom) |
| 16 | `\sum` | ❌ | Not modelled | Not modelled | Library function (WhyML axiom) |
| 17 | Function call in contract | ❌ | Not modelled | Not modelled | Pure function calls are transpiler-level |
| 18 | `True`/`False` | ✅ (implicit) | Booleans encoded as non-zero/zero integers | Same | `evalBool` uses int truthiness |
| 19 | `None` | ❌ | Not modelled | Not modelled | Maps to 0 in WhyML; trivial but not explicit |
| 20 | `arr[lo:hi]` | ❌ | Not modelled | Not modelled | Slice is a WhyML abstract function |

### 3.5b Operators (§3.2)

| # | Feature | Covered | Rocq artefact | Lean artefact | Notes |
|---|---------|---------|---------------|---------------|-------|
| 1 | `\forall`, `\exists` | ✅ | `CForall x body`, `CExists x body` | `ContractExpr.forall_` | Quantifiers in contract expressions |
| 2 | `==>`, `<==>` | ✅ | `CImplies`, `CIff` | `ContractExpr.implies`, `.iff` | Logical connectives |
| 3 | `or` | ✅ | `COr` | `ContractExpr.or` | Disjunction |
| 4 | `and` | ✅ | `CAnd` | `ContractExpr.and` | Conjunction |
| 5 | `==`, `!=` | ✅ | `CEq`, `CNe` | `ContractExpr.eq`, `.ne` | Equality/inequality |
| 6 | `<`, `>`, `<=`, `>=` | ✅ | `CLt`, `CGt`, `CLe`, `CGe` | `.lt`, `.gt`, `.le`, `.ge` | Comparisons |
| 6b | `in`, `not in` | ❌ | Not modelled | Not modelled | Desugared to ∃ in transpiler |
| 7 | `+`, `-` (binary) | ✅ | `EBinOp OpAdd/OpSub` | `Expr.binop .add/.sub` | Arithmetic |
| 8 | `*`, `//`, `/`, `%` | ✅ (partial) | `EBinOp OpMul/OpDiv` | `Expr.binop .mul/.div` | Mul and Div modelled; mod not explicit |
| 9 | `not`, unary `-` | ✅ | `ENeg`, `CNot` | `Expr.neg`, `ContractExpr.not` | Negation |

### 3.6 Statement Constructs (§2, §7)

| # | Feature | Covered | Rocq artefact | Lean artefact | Notes |
|---|---------|---------|---------------|---------------|-------|
| 1 | `skip` | ✅ | `SSkip` / `ExecSkip` / `wp SSkip = Qn st` | Same | Identity statement |
| 2 | Assignment `x = e` | ✅ | `SAssign` / `ExecAssign` / WP substitution | Same | Core assignment |
| 3 | Augmented assign `x += e` | ✅ | `SAugAssign` / `ExecAugAssign` | Same | `+=`, `-=`, `*=` |
| 4 | Array set `arr[i] = v` | ✅ | `SArraySet` / `ExecArraySet` / `arrayUpdate` | Same | Array element mutation |
| 5 | Sequence `s1; s2` | ✅ | `SSeq` / `ExecSeq` + `ExecSeqReturn` + `ExecSeqContinue` | Same | 3-continuation propagation |
| 6 | If/else | ✅ | `SIf` / `ExecIfTrue` + `ExecIfFalse` | Same | Boolean branching |
| 7 | While loop | ✅ | `SWhile` / `ExecWhileTrue` + `ExecWhileContinue` + `ExecWhileFalse` | Same | Full inv+var+3-continuation |
| 8 | For loop | ✅ (via desugar) | `SFor` desugared to `SWhile` in `Phase3b_Desugar.v`; WP defined directly | Same | `desugar_correct` is Admitted/sorry |
| 9 | Return | ✅ | `SReturn` / `ExecReturn` (binds `\result`) | Same | Qr continuation |
| 10 | Continue | ✅ | `SContinue` / `ExecContinue` | Same | Qc continuation |
| 11 | Assert | ❌ | Not modelled | Not modelled | Transpiler emits `check {...}` |
| 12 | Tuple unpacking | ✅ (desugar) | `Phase3b_Desugar.v`: `tuple_unpack2`, `exec_tuple_unpack2_normal` | `Desugar.lean`: `tupleUnpack2`, `exec_tupleUnpack2_normal` | Desugars to SSeq of ESubscript assigns; correctness proved |
| 13 | Walrus `:=` | ✅ (desugar) | `Phase3b_Desugar.v`: `walrus_assign`, `exec_walrus_assign` | `Desugar.lean`: `walrusAssign`, `exec_walrusAssign` | Definitionally equal to SAssign; proved by rfl |
| 14 | Match statement | ✅ (desugar) | `Phase3b_Desugar.v`: `desugar_match`, `exec_desugar_match_single_hit/miss` | `Desugar.lean`: `desugarMatch`, hit/miss theorems | Desugars to SIf chain; hit and miss cases proved |
| 15 | Lambda | ❌ | Not modelled | Not modelled | Higher-order not in core |

### 3.7 Memory Models (§5)

| # | Feature | Covered | Notes |
|---|---------|---------|-------|
| 1 | Hoare (default) | ✅ | The formal model uses value-typed state (list of key-value pairs), exactly the Hoare model |
| 2 | Typed | ❌ | Heap-based model not in formal semantics |
| 3 | Store | ❌ | Single-heap model not in formal semantics |
| 4 | Concurrent | ❌ | Monitor-invariant pattern not in formal semantics |

### 3.8 Multi-file / Pipeline (§9)

| # | Feature | Covered | Notes |
|---|---------|---------|-------|
| 1 | Multi-file imports | ✅ (vacuous) | `vacuous-soundness.md` §F.1 — Flattened output is the formal model's input |
| 2 | `--deep` | ✅ (vacuous) | `vacuous-soundness.md` §F.2 — Same as multi-file |
| 3 | `--fun` filtering | ✅ (vacuous) | `vacuous-soundness.md` §F.3 — Soundness holds for verified subset |
| 4 | `split_vc` | ✅ (vacuous) | `vacuous-soundness.md` §F.4 — Why3 hint; doesn't change proof obligations |

### 3.9 Typing Constructs (annotations.md §12.4, §12.9–§12.17) — typing-engagement TY0–TY3

The 12 typing constructs landed between 2026-06-06 and the audit refresh date
(2026-06-28) — *after* the Rocq/Lean mechanisation's last touch. They are
**out-of-model**, by design: each is either (a) a front-end normalization
seam that desugars to *existing* IR/contract nodes, (b) a static-semantics
syntactic check, or (c) a Module-6 emission refinement. None introduces a
new `stmt` constructor or a new `wp` rule, so the soundness theorem's
statement and proof are unaffected. The shared rationale: **these are
lowering/emission features, not WP-calculus features** — the typing work
extends the *surface* language and the *static* plane, never the core
operational-semantics → WP → soundness chain that `pycsl_soundness`
covers.

| # | Feature (spec §) | Covered | Rocq artefact | Lean artefact | Justification (out-of-model) |
|---|------------------|---------|---------------|---------------|------------------------------|
| 1 | `Union`/`Optional`/`X \| Y` (§12.4, TY1) | ❌ Out-of-model | None | None | Desugared at the front-end normalization seam into a per-site synthesized `type_decl` of kind `variant` (reusing the §2.6 `#@ datatype` machinery). The variant type, its arms, and the per-arm C2/C3 injection/projection VCs are Why3-level — Module 6 `preamble.py` emits the `type _union_N = Arm_0 of int \| …` declaration, and Why3 discharges the match exhaustiveness (C9). No new `stmt` constructor; `wp` unchanged. The runtime shim (`src/pycsl_lib/typ/__init__.py.Union`) carries `#@ ensures \result == val` — identity, no validation (R1–R8, D4 no-blend). |
| 2 | `Literal[v1, …, vn]` (§12.9, TY1) | ❌ Out-of-model | None | None | Desugared at the front-end normalization seam into a synthesized ground `requires`/`ensures` clause (`x = 1 \/ x = 2`). The WhyML parameter type stays the literal's base type; the synthesized clause reuses the EXISTING `requires`/`ensures` IR list and the EXISTING `BinOp(or)`/`==`/`Number`/`String`/`Bool`/`None` IR expression nodes. **No new IR node, no IR_VERSION bump, no new VC kind.** Narrowing (L2) and exhaustiveness (L3) are emergent from the standard path-condition + postcondition VCs on the existing `if x == v` lowering. The runtime `Literal(*args, val)` shim is identity (LR1–LR8, LD3). |
| 3 | `Final[T]` (§12.10, TY1) | ❌ Out-of-model | None | None | Lowered at the front-end normalization seam to the degenerate single-attribute, single-writer form of HAPPY's no-write confinement. The write-policy is a **static-semantics check** in `core_ir_semantic._check_final` (a syntactic write-site walk over the IR body, NOT a VC). The annotation's type is the inner type `T` (F3 — no narrowing). The registry is plumbed as `program_ir["final_registry"]` (an additive module-level metadata key — see §3.10); Module 6 ignores it. **No new IR node, no IR_VERSION bump, no new VC kind.** Runtime `Final(x0, x1, val)` shim is identity (FR1–FR6, FD2). |
| 4 | `-> NoReturn` (§12.11, TY1) | ❌ Out-of-model (AST: ⚠️ IR-level only) | None | None | Lowered at the front-end normalization seam to a `false` postcondition. `_build_function_ir` recognizes `NoReturn` and sets the IR flag `is_noreturn: true` (IR v1.3 — see §3.10); Module 6 emits `ensures { false }` (NR1). The `false` postcondition is a genuine proof obligation (the function must diverge or raise), discharged by Why3 — it reuses the existing `ensures` clause shape. `core_ir_semantic._check_noreturn` (NR2a body-supports-divergence) and `_check_noreturn_successors` (NR3 dead-code) are static-semantics checks, NOT VCs. The non-vacuity gate exempts declared-NoReturn functions (NR4). The formal AST does NOT model `is_noreturn` — it is an IR-emitter flag consumed by Module 6. |
| 5 | `TypedDict` (§12.12, TY2) | ❌ Out-of-model | None | None | Lowered at the front-end normalization seam to a record `type_decl` with one field per declared key (reusing the §2.3 class-record machinery). Field access `p["x"]` lowers to a record-field read `p.x`; construction `{"x": 1, "y": 2}` lowers to a record literal. Why3's native record type-checking discharges the field-shape obligations (T5–T9). An optional `is_typeddict: True` field on the record `type_decl` gates Module 6's subscript/literal lowering paths (defaults `False` → byte-identical for non-TypedDict drivers). **No IR_VERSION bump.** `core_ir_semantic._check_typeddict_access` is a static-semantics warning. The runtime shim is identity (R1–R8, D4). |
| 6 | `NamedTuple` (§12.13, TY2) | ❌ Out-of-model | None | None | Lowered at the front-end normalization seam to a record `type_decl` (reusing the TypedDict record seam). Named field access `p.x` and positional access `p[0]` both lower to record-field reads; positional construction `Point(1, 2)` reuses the existing Tier-A parametrized record construction (`_call_record_constructor`). Why3's native record type-checking discharges the field-shape + arity obligations (N4–N7). An optional `is_namedtuple: True` field gates Module 6's positional-subscript lowering path. **No IR_VERSION bump.** `core_ir_semantic._check_namedtuple_access` is a static-semantics check. The runtime shim is identity (R1–R9, D4). |
| 7 | `@overload` (§12.14, TY2) | ❌ Out-of-model | None | None | An `@overload` family is lowered to a **guarded contract family** (O1–O6). Each stub synthesizes a guard `G_i = isinstance(p_i, T_i)` (reusing the existing `_handle_isinstance` → `(subtag <typeof p_i> <T_i tag>)` IR shape), and each `#@ ensures Q_i` becomes a guarded postcondition `ensures { G_i ==> Q_i }` attached to the single implementation. Reuses the EXISTING `contracts.ensures` list + the EXISTING `==>`/`isinstance` IR shapes. The stubs themselves are NOT emitted as functions (their `...` body is discarded — R1). **No `\trusted`; no IR_VERSION bump; no new VC kind.** The runtime `@overload` shim is identity (R1–R7). |
| 8 | `Protocol` / `@runtime_checkable` / `#@ conforms_to` (§12.15, TY2) | ❌ Out-of-model | None | None | `class P(Protocol)` synthesizes a contract interface: a marker record (`is_protocol: True`, no fields) + each member emitted as an `abstract: True` function (a bodyless `val` with its contract — the refinement target, P1a). `C conforms to P` (declared via `#@ conforms_to P`) populates the EXISTING `overrides` IR list with `(C__m, P__m)` pairs; `--check-behavioral-subtyping` emits the per-method refinement goal `((pre_P -> pre_C) /\ (post_C -> post_P))` (P2/P4). NO `\trusted`; **no IR_VERSION bump** (reuses the existing `abstract` function flag + the existing `overrides` IR list + the existing refinement-goal emitter). The runtime `@runtime_checkable` shim is identity (R1–R7). |
| 9 | `TypeVar` / `Generic` / PEP 695 `class C[T]` / `def f[T]()` (§12.16, TY3) | ❌ Out-of-model | None | None | Whole-module monomorphization. The `frontend/monomorphize.py` step-5 IR-resolution pass COLLECTs concrete instantiation sites (`C[int]()`, `x: C[int]`) and EMITs one name-mangled specialized WhyML `let`/`val` per `(generic, concrete-type)` pair with `T` substituted (`Stack` → `Stack_int`). The TypeVar bound (`T: B`) is an instantiation-time obligation (GT2). `ParamSpec`/`TypeVarTuple` are schema-only loud-fails (GT3). The IR carries the new optional `type_params` field (IR v1.4 — see §3.10); Module 6 reads it only via the monomorphization pass. **No new `stmt` constructor; `wp` unchanged.** The runtime `TypeVar("T", bound=B)` shim is identity (R1–R7). |
| 10 | `Callable[[A1, …, An], R]` (§12.17, TY3) | ❌ Out-of-model | None | None | A `Callable[[A1, …, An], R]`-typed parameter lowers to a curried WhyML function-type parameter `<w1> -> ... -> <wr>` (C1). Module 5 encodes the arg-list + return type into the existing `symbol_table` value as `"callable:<a1>,...-><r>"` (a new tag VALUE, NOT a new IR field → **no IR_VERSION bump**). Module 6 emits the arrow type via `_param_type_str` + `_callable_whyml_arrow`. The call site `f(a1, …, an)` already lowers to WhyML application; Why3's typecheck discharges the arg-type match (C2) and the result type (C3). Scope limit (C5): only `int`/`bool`/`str`/`float` and record/variant names are admissible as arg/return types. The runtime `Callable[[...], R]` shim is identity (R1–R3). |
| 11 | `typing.cast(T, v)` (TY1, cast-twoplane-spec) | ❌ Out-of-model | None | None | Not in §12 of `annotations.md` (documented in the typing-engagement `ty1/conformance-cast/` drivers + the `cast-twoplane-spec.md`). The shim `src/pycsl_lib/typ/__init__.py.cast` is a literal `def cast(typ, val): return val` with `#@ ensures \result == val` (CR1). Static gate CA1: `cast` carries NO static plane — the only thing the static plane can observe about `cast(int, 5)` is the identity postcondition. **No new IR node, no IR_VERSION bump, no new VC kind.** |
| 12 | `Protocol` structural subtyping (§12.15, implicit) | ❌ Out-of-model (deliberate strictness) | None | None | PEP 544 conformance is structural/implicit; PyCSL's TY2 scope requires the explicit `#@ conforms_to` directive (divergence-by-strictness — an implicit structural search is outside the per-module verification model). See row 8 for the explicit-directive coverage. |

**Net WP-calculus impact of the typing engagement:** ZERO new `stmt`
constructors, ZERO new `wp` rules, ZERO changes to `pycsl_soundness`.
Every typing construct is discharged either by Why3's native type-checker
(record fields, variant arms, arrow types), by reusing an existing IR/VC
shape (`requires`/`ensures`/`BinOp(or)`/`==`/`isinstance`/`overrides`),
or by a static-semantics syntactic check in `core_ir_semantic`. The
soundness theorem's hypothesis set is unchanged. The trust line is
exactly where it was pre-typing: the formal model proves the WP engine,
and the typing features are lowering/emission concerns above the trust
seam documented in §2 (Modules 1-4 trusted-by-design; Module 5 IR shape
verified by U.3/U.4; Module 6 transpilation verified by Q2 Sub-α).

### 3.10 IR_VERSION 1.4 fields (docs/ir.md §2, §4, §5)

IR_VERSION went 1.2 → 1.4 between the last formal-semantics touch
(2026-06-06) and this refresh (2026-06-28). The bumps are **additive**
(new optional fields, emitted only when the feature is used → byte-identical
for unaffected drivers). None changes the `stmt`/`expr`/`contract_expr`
inductive types the soundness theorem is quantified over.

| # | Field | IR version | Carried on | Formal-model status | Justification |
|---|-------|-----------|-----------|---------------------|---------------|
| 1 | `is_noreturn: bool` | 1.3 | `FunctionIR` | ❌ Out-of-model | Consumed by Module 6 to emit `ensures { false }` (NR1 — reuses the existing `ensures` clause shape). The formal `func_spec` has no `is_noreturn` field; the `false` postcondition is a WhyML-level emission, not an AST-level construct. `core_ir_semantic._check_noreturn` (NR2a) and `_check_noreturn_successors` (NR3) are static-semantics checks, not VCs. See §3.9 row 4. |
| 2 | `type_params: list` | 1.4 | `type_decls` + `FunctionIR` | ❌ Out-of-model | Consumed ONLY by `frontend/monomorphize.apply_monomorphization` (the step-5 IR-resolution pass), which COLLECTs concrete instantiations and EMITs name-mangled specialized copies with substituted contracts. The monomorphization output is plain non-generic `type_decls`/`functions` — the post-monomorphization IR has no `type_params`, so the formal model (which operates on the post-monomorphization IR) never sees it. See §3.9 row 9. |
| 3 | `final_registry: list` | (no bump — additive top-level key) | `ProgramIR` (top-level) | ❌ Out-of-model | Plumbed as `program_ir["final_registry"]` (omitted when empty → byte-identical for Final-free modules). Consumed ONLY by `core_ir_semantic._check_final` (a static-semantics write-site walk, NOT a VC). Module 6 ignores it. The formal model has no class records at the function-body level; the `Final` write-policy is a syntactic check above the trust seam. See §3.9 row 3. |

**Net IR-shape impact:** the new fields are consumed either by Module 6
emission (then erased) or by the static-semantics checker (not in the WP
chain). The Q4 IR-bridge (`Phase1b_IrToStmt.v`, `Phase1c_ValidateIr.v`)
ingests the post-monomorphization, post-`final_registry` IR; the
`pycsl_ir_json` inductive and `ir_to_stmt` do not model these fields
because they have no `stmt`-level representation. Re-proving the IR
correspondence for the new fields is a future formal-semantics effort
(out of scope for Phase F — see §6).

### 3.11 Module2 Lark-free migration (no formal-semantics impact)

On 2026-06-27, `Module2_Parser.py` was migrated from a Lark-generated
EBNF parser to a hand-written recursive-descent parser (commit
`3adf9d47`). **This is a parser-engine swap, not a grammar change**: the
`#@` contract grammar surface (the set of directives, clauses, and
expression forms accepted) is unchanged. The migration therefore has
**no formal-semantics impact**:

- The formal model (`Phase1_AST.v` / `AST.lean`) models the *contract
  AST*, not the parser that produces it. The AST inductive types are
  unchanged.
- The trust seam for Modules 1-4 remains `\trusted reviewer:` (§2 trust
  boundary table) — the migration moves the trust from "Lark + the
  Lark grammar" to "the hand-written recursive-descent parser", but
  does not eliminate it. A formal proof of parser correctness is
  CC.6 out-of-scope regardless of the parser engine.
- The Q4 IR-bridge operates on the IR JSON (post-Module-5), so the
  parser engine is below its input boundary.

---

## 4. Coverage Summary

### What IS formally proven

The soundness theorem (`pycsl_soundness`) establishes:

> **For any statement `s` in the core language, any state `st`, and any
> outcome `out`: if `Exec st s out` (operational semantics) and
> `wp s Qn Qr Qc preSt st` (WP holds), then the appropriate
> postcondition holds on the output state.**

This covers the **core verification engine** — the WP calculus that
generates proof obligations. The features with ✅ above are precisely
those represented in the formal AST and given both operational semantics
(how they execute) and WP rules (what conditions are generated).

**Covered core** (13 statement/expression features):
- Assignments (simple, augmented, array)
- Sequencing with 3-continuation propagation (return, continue)
- Conditional branching (if/else)
- While loops with invariant + variant (local variant bounds)
- For loops (via desugaring to while — correctness Admitted/sorry)
- Return and continue statements
- Full contract expression language (arithmetic, comparisons, logical
  connectives, quantifiers, \old, \result, \length)

### What is NOT formally modelled (and why)

| Category | Features | Justification |
|----------|----------|---------------|
| **Class system** | class invariant, self.field | OO features are WhyML record types; the core WP calculus operates on flat state. Class invariants are enforced by the WhyML type system, not by WP rules. |
| **Memory models** | typed, store, concurrent | The formal model uses the Hoare (value-typed) memory model. Other models change the state representation but use the same WP structure. |
| **Syntactic sugar** | assert, tuple unpack, walrus, match, lambda | These are lowered to core constructs by the transpiler *before* WP generation. Their correctness reduces to the core. |
| **Ghost/label** | ghost assign, label, \at | Verification-model-only constructs inserted by the transpiler. They don't affect the WP calculus structure. |
| **Library predicates** | \is_sorted, \sum, \valid, \separated, \length2d, \valid2d | These are axiomatically defined in WhyML modules. Their soundness is the responsibility of the WhyML axiom definitions, not the WP calculus. |
| **Concurrency** | shared, mutex_invariant, lock_order, critical, acquires, releases | The monitor-invariant pattern reduces concurrent verification to sequential WP proofs. The reduction itself is not formally proved. |
| **Termination** | \diverges, structural \variant, function \variant | The soundness theorem is partial correctness ("if terminates, then post holds"). Termination proofs are delegated to WhyML/Why3. |
| **Trusted** | \trusted | Axiom introduction — inherently cannot be formally verified. |
| **Pipeline** | multi-file, --deep, --fun, split_vc | Build-system orchestration, not WP semantics. |
| **Typing constructs (TY0–TY3)** | Union, Optional, `X\|Y`, Literal, Final, NoReturn, TypedDict, NamedTuple, overload, Protocol/`@runtime_checkable`/`#@ conforms_to`, TypeVar/Generic/PEP 695, Callable, `typing.cast` (12 constructs — see §3.9) | Each is a front-end normalization seam (desugars to existing IR/contract nodes), a Module-6 emission refinement, or a static-semantics syntactic check. None introduces a new `stmt` constructor or `wp` rule. Discharged by Why3's native type-checker (records, variants, arrows), by reusing existing IR/VC shapes (`requires`/`ensures`/`BinOp(or)`/`==`/`isinstance`/`overrides`), or by `core_ir_semantic` checks. The runtime shims are identity (`#@ ensures \result == val`). **Zero WP-calculus impact.** |
| **IR 1.4 fields** | `is_noreturn`, `type_params`, `final_registry` (see §3.10) | Additive IR fields consumed either by Module 6 emission (then erased) or by the static-semantics checker (not in the WP chain). The formal model operates on post-monomorphization IR; `type_params` is gone by then. Not modelled in `pycsl_ir_json` / `ir_to_stmt`. |
| **Module2 parser engine** | Lark → hand-written recursive-descent (2026-06-27) | Parser-engine swap; the `#@` contract grammar surface is unchanged. The formal model captures the contract AST, not the parser that produces it. Trust seam for Modules 1-4 unchanged (CC.6 out-of-scope). See §3.11. |

### Quantitative coverage

> **Note (2026-06-28 refresh):** the typing engagement (TY0–TY3, 12
> constructs) and the IR 1.2→1.4 bumps landed *after* the last
> formal-semantics touch (2026-06-06). The counts below reflect the
> current feature set; the typing constructs and IR 1.4 fields are all
> **out-of-model** (§3.9 / §3.10) — they are lowering/emission features,
> not WP-calculus features, so the **effective WP-engine coverage
> remains 100%**.

- **Directives**: 10 function + 2 loop + 1 class + 6 program-point + 7 concurrent = **26 total**
  - Formally modelled: **5** (requires, ensures, assigns, loop invariant, loop variant)
  - Coverage: **19%** of directive count
- **Expression atoms**: 20 total → **8 modelled** (int, var, arr[i], \result, \old, \length, \nothing, True/False) = **40%**
- **Operators**: 9 groups → **8 modelled** = **89%**
- **Statements**: 15 total → **10 modelled** = **67%**
- **Memory models**: 4 total → **1 modelled** (Hoare) = **25%**
- **Typing constructs**: 12 total (§3.9) → **0 modelled** = **0%** — all are lowering/emission features above the WP trust seam
- **IR 1.4 fields**: 3 total (`is_noreturn`, `type_params`, `final_registry`) → **0 modelled** = **0%** — all are IR-emitter / static-semantics fields, not AST-level

**Effective coverage of the WP engine**: The 5 modelled directives +
10 modelled statement types + 8 expression atoms + 8 operator groups
constitute the **core WP calculus**. All other features are either:
(a) syntactic sugar lowered before WP, (b) WhyML-level axioms, or
(c) orchestration. The formal proof therefore covers **100% of the
WP calculus logic** — the component that generates proof obligations.
The 12 typing constructs (§3.9) and 3 IR 1.4 fields (§3.10) are
out-of-model by design: they extend the surface language and the
static plane, never the core WP calculus.

---

## 5. Reproducing the Proofs

### Rocq

```bash
cd src/formal-semantics/rocq
make clean && make proof
```

Expected output:
```
Files compiled: 8
Files with Admitted: 1
  Phase3b_Desugar.v:NN: Admitted.
=== All proofs checked ===
```

### Lean

```bash
cd src/formal-semantics/lean
make clean && make proof
```

Expected output:
```
Files compiled: 9
Files with sorry: 2
  PyCSL/Desugar.lean:... sorry
  PyCSL/WhileInv.lean:... sorry (×2)
=== All proofs checked ===
```

---

## 6. Implementation Todos

The following tasks would produce the final audit-ready deliverable:

### Phase 1 — Traceability document (this plan)

- [x] Map every feature in `annotations.md` to proof artefacts
- [x] Classify covered vs. not-covered with justifications
- [x] Quantify coverage

### Phase 2 — Close remaining sorry/Admitted gaps

| # | Gap | Prover | Difficulty | Impact on soundness |
|---|-----|--------|------------|---------------------|
| 1 | `desugar_correct` | Both | Medium | Does NOT affect soundness of core WP; only affects `for` loop desugaring |
| 2 | `while_not_continued` | Lean | Easy | NOT used by soundness proof |
| 3 | `while_inv_preserved` | Lean | Medium | NOT used by soundness proof |

### Phase 3 — Audit report generation

- [ ] Create `src/formal-semantics/audit-report.md` — a prose document
  suitable for a security auditor, referencing this traceability matrix
  and explaining the trust boundary between formally proven components
  and trusted-by-construction components (transpiler, WhyML axioms).
- [ ] Add line-number cross-references to specific theorems and definitions.
- [ ] Include `make proof` output as evidence appendix.

### Phase 4 — Optional extensions

- [ ] Prove `desugar_correct` in Rocq (eliminate last Admitted)
- [ ] Prove `while_not_continued` in Lean (eliminate easy sorry)
- [ ] Add `assert` statement to the formal model (trivial: WP = `P ∧ Qn st`)
- [ ] Add ghost variable support to the formal model
- [ ] Model the typed memory model as an alternative state representation

### Phase 5 — Formal-semantics coverage of the typing engagement (out of Phase F scope)

Phase F refreshes the *map* (this document); re-proving the soundness
theorem for the new IR fields is a separate formal-semantics effort
(explicitly out of scope per `28-self-annotate.md` §6). The following
are tracked here for future work:

- [ ] Extend `pycsl_ir_json` (`Phase0_IrJson.v`) with `is_noreturn`,
  `type_params`, `final_registry` (IR 1.3/1.4 fields — §3.10). Update
  `validate_ir_correspondence` (`Phase1c_ValidateIr.v`) to check them.
  These fields have no `stmt`-level representation, so the
  `ir_to_stmt` bridge (`Phase1b_IrToStmt.v`) is unaffected — the
  correspondence is at the IR-JSON metadata level only.
- [ ] Model a `NoReturn` `func_spec` flag in `Phase1_AST.v` /
  `AST.lean`, with a WP rule that emits the `false` postcondition
  (NR1). Currently the `false` postcondition is emitted by Module 6
  from the IR flag — modelling it at the AST level would let the WP
  calculus reason about it directly. Low soundness impact (the `false`
  postcondition is a genuine proof obligation either way).
- [ ] Model the monomorphization pass (`frontend/monomorphize.py`) as a
  `monomorphize : stmt → stmt` transformation with a
  `monomorphize_correct` lemma (analogous to `desugar_correct`).
  Currently the formal model operates on *post-monomorphization* IR,
  so `type_params` is invisible to it by construction.
- [ ] None of the 12 typing constructs (§3.9) requires AST extension —
  each desugars to existing IR/contract nodes. The only formal-semantics
  work would be a *desugaring correctness* lemma per construct (proving
  the front-end normalization seam preserves semantics). This is
  CC.6-adjacent (front-end formalization) and currently out-of-scope.

---

## 7. Trust Boundary Diagram

```
┌─────────────────────────────────────────────────────────┐
│              FORMALLY PROVEN (Rocq + Lean)               │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐ │
│  │   AST    │→ │   SOS    │→ │   WP    │→ │Soundness│ │
│  │(Phase1)  │  │(Phase3)  │  │(Phase4) │  │(Phase5b)│ │
│  └──────────┘  └──────────┘  └─────────┘  └─────────┘ │
│                                                         │
│  Core stmt language: skip, assign, augassign, arrayset, │
│  seq, if, while (inv+var), for (via desugar), return,   │
│  continue. Contract exprs: int, var, arr[i], \result,   │
│  \old, \length, arithmetic, comparisons, logic,         │
│  quantifiers.                                           │
│                                                         │
│  Theorem: wp s Q pre st ∧ Exec st s out → Q(out)       │
└─────────────────────────────────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
┌──────────────────────┐  ┌──────────────────────┐
│  TRUSTED BY DESIGN   │  │  TRUSTED BY WhyML    │
│                      │  │                      │
│  • Python parser     │  │  • \valid, \separated│
│    (Module1-4;       │  │  • \is_sorted, \sum  │
│    Module2 now       │  │  • Memory model axiom│
│    hand-written      │  │  • Why3 solvers      │
│    recursive-descent │  │  • mach.int overflow │
│    — §3.11)          │  │  • string.String     │
│  • Transpiler        │  │                      │
│  • Syntactic desugar │  │                      │
│  • Ghost insertion   │  │                      │
│  • Multi-file import │  │                      │
│  • Class→record      │  │                      │
│  • Concurrency       │  │                      │
│    reduction         │  │                      │
│  • Typing constructs │  │                      │
│    (TY0–TY3, §3.9 —  │  │                      │
│    lowering/emission │  │                      │
│    above the WP seam)│  │                      │
│  • IR 1.4 fields     │  │                      │
│    (§3.10)           │  │                      │
└──────────────────────┘  └──────────────────────┘
```

The security auditor should understand: the formal proof guarantees that
**the WP rules correctly reflect the operational semantics**. Everything
above the trust boundary is mechanically verified. Everything below is
either (a) trusted transpiler code that should be reviewed manually, or
(b) WhyML axioms whose correctness is assumed by the Why3 ecosystem.
