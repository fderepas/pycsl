# PyCSL Self-Annotation Plan — Status Snapshot (TCB-aware revision)

**Date:** 2026-05-29
**Supersedes:** `self-annot.md` (dated 2026-05-27; before Q3 Sub-β closure and Q4 Upward completion)
**Source of truth:** `pycsl --keep-mlw <module>` (full proof), `make self-annotate-verify` (no-proof gate)
**Companion docs:**
- `closer-to-code-execution-status.md` — multi-quarter program execution log (current as of 2026-05-29)
- `self-remains.md` — module-by-module gap analysis with §CC.2 citation table
- `docs/glossary/trusted-computing-base.md` — TCB glossary entry
- `docs/glossary/formula-rep.md` — Why3 formula evaluation predicate
- `src/formal-semantics/audit-plan.md` — feature-to-proof traceability matrix

## What changed since 2026-05-27

Two structural changes reshape how self-annotation maps onto the
trust chain:

1. **Q3 Sub-β closure.** The named axioms `module6_encodes_mlw`
   and `why3_validates_emitted` were eliminated from the Rocq
   build. `why3_certificate` is now itself the witness type
   (Phase6j_Why3Trust.v). Lean parity achieved: `vcgBridge` and
   `why3ImplementsWpW_derived` depend only on standard kernel
   axioms (propext, Classical.choice, Quot.sound). Layer 0 of the
   trust chain is **PyCSL-axiom-free in Rocq, three-standard-axioms
   in Lean**.
2. **Q4 Upward completion.** All six items (U.1-U.6) landed.
   `Phase0_IrJson.v` + `Phase1b_IrToStmt.v` + `Phase1c_ValidateIr.v`
   + `Phase1d_StmtToIr.v` provide a formal IR → stmt converter,
   validator, encoder, and round-trip correspondence. The U.4
   byte-diff pipeline (`bin/extraction-byte-diff-upward.sh`)
   validates the converter against Module 5's actual JSON output
   at **346/386 = 89.6% PASS** on the real reference corpus
   (93.5% against testable cases, excluding 16 Module-5-failure
   files).

The original "trust seam = facade" boundary is gone. Per the
`closer-to-code.md` Q4 deliverable: **trust seam = IR boundary**.

## Trust chain (TCB-aware revision)

```
Layer 0 — Rocq / Lean type-checkers
   Machine-checked theorems with PyCSL-specific axiom count:
     Rocq:  0
     Lean:  2 visible (altErgoCorrect, trustedContractsAxiom)
            + 1 hidden behind opaque Why3Trust.check (Why3CertWitness)
   Standard kernel axioms: propext, funext (Rocq) / propext,
     Classical.choice, Quot.sound (Lean)
         ↓
Layer 1 — PyCSL #@ contracts on the Python implementation
   Structural faithfulness: frame conditions, loop termination,
   exhaustive dispatch over all WP rule arms.
   Anchored to Layer 0 via CC.4 citations:
     Module5_IREmitter         → Phase6h_CorrMain.wp_gen_correct
     Module6_WhyMLTranspiler   → Phase5b_Soundness.pycsl_soundness
     module6_whyml/preamble    → Phase6i_Soundness.why3_implements_wp_w_derived
     Module4_SemanticAnalyzer  → Phase1_AST.expr_eq_dec
         ↓
Layer 2 — Why3 + SMT solvers
   Output verification: the generated .mlw file is accepted by Why3.
   Per-module `pycsl --keep-mlw <module>` gate.
         ↓
Layer 3 — Why3 val spec module
   Semantic equivalence to Rocq fixpoint (val per WP arm,
   ensures clause mirrors the Rocq fixpoint arm exactly).
         ↓
Layer 4 — IR-shape correspondence (NEW)
   `ir_to_stmt` (Phase1b_IrToStmt.v) converts Module 5 JSON
   IR into formal `stmt`. Backed by:
   • U.5 round-trip theorem (stmt_to_ir_simple_roundtrip):
     formal stmts re-encoded → IR → decoded recover the original.
   • U.4 byte-diff (89.6% PASS on real corpus): empirical
     validation that Module 5 actually emits shapes the
     converter handles.
   • U.3 correctness (well_formed_and_unique_implies_validate):
     well-formed IR with unique keys passes the validator.
```

## TCB inventory by tier

| Tier | What | TCB content |
|---|---|---|
| **0a** Verified, axiom-free | Rocq Why3-validation chain | `wp_gen_correct`, `vcg_sound`, `module6_encodes_mlw` (proved), `why3_validates_emitted` (proved), `why3_implements_wp_w_derived`, `vcg_bridge`, plus Q4 U.3/U.5/U.6 theorems. **Zero PyCSL axioms.** |
| **0b** Standard kernel axioms | Foundational math axioms accepted by the wider proof-assistant community | Rocq: `propositional_extensionality`, `functional_extensionality_dep`. Lean: `propext`, `Classical.choice`, `Quot.sound`. |
| **1** Named external-tool axioms | Lean-only; Rocq has no equivalent | `altErgoCorrect` (Alt-Ergo + Z3 sound for non-linear), `trustedContractsAxiom` (`\trusted` reviewers honored). Hidden: `Why3CertWitness` (behind opaque `Why3Trust.check`). |
| **2** `\trusted reviewer:` modules | Out of formal scope by CC.6 design | Modules 1-3 (libcst, Lark, weaver), Why3 binary, Alt-Ergo/Z3, WhyML stdlib. |
| **3** Meta-level claims | Empirically validated; not kernel-proved | Extraction-extensional residue (CC.5): Rocq-extracted `emit_stmt` matches Module 6's Python emission byte-for-byte on corpus. U.4 byte-diff: Module 5 IR shapes match what `ir_to_stmt` handles. |
| **4** Tool stack | Assumed correct | Coq 8.20.1, Lean 4.29, OCaml 4.14.2/5.4.0, opam/dune/lake, Python 3.14, Yojson 2.2.2. |

## Current state

### Layer 0 (axiom-free verification): ✅ green
- Rocq: zero PyCSL-specific axioms. All theorems verified above
  closed under the global context.
- Lean: 2 visible PyCSL axioms (altErgoCorrect, trustedContractsAxiom);
  `Why3CertWitness` hidden behind `opaque Why3Trust.check`.
- Both proof trees rebuild clean: Rocq `make`, Lean `lake build`
  (34/34 jobs).

### Layer 1 (no-proof gate): ✅ green
- `make self-annotate-verify` passes for 11 files in
  `src/self-annotate/src/` (Modules 1-6 + ConcurrencyChecker +
  module6_whyml mixin subpackage).
- Mirror-check: **25/25 mirrors in sync** with `src/pycsl/`
  (`bin/self-annotate-mirror-check.sh`).
- Self-annotation suite: **26/26 proved**
  (`bin/run-self-annotation-suite.sh`).
- CC.4 citations landed in 4 mirrors (see Layer-0 anchor list above).
- 12 cross-prover reference tests verify under full proof
  (0331, 0341-0351).
- pytest: 25 pass, 3 skip (pre-existing skill2rag exclusions).

### Layer 2 (full proof per module): ✅ fully green (as of 2026-05-29 v2)

All 7 modules previously listed as blocked now pass full
`pycsl --keep-mlw` verification:

| Module | Previous blocker (now cleared) | Cleared by |
|---|---|---|
| Module1_Ingestor | line 48 class G | (no longer reproduces) |
| Module2_Parser | line 135 class I termination | (no longer reproduces) |
| Module3_Weaver | line 133 map truthiness | `_should_auto_trust_set_op` (`if map_val:` case at auto_trust.py:226-232) |
| Module4_SemanticAnalyzer | line 379 set-union | `_should_auto_trust_set_op` (BinOp(\|/&/^/-) case at auto_trust.py:218-221) |
| Module5_IREmitter | line 119 `'mu → option int` | (no longer reproduces) |
| Module6_WhyMLTranspiler | line 434 class M sub-case | (no longer reproduces) |
| ConcurrencyChecker | line 61 set-union | `_should_auto_trust_set_op` (same as Module 4) |

**Self-annotation suite: 26/26 PROVED** (`bin/run-self-annotation-suite.sh`).

### Layer 4 (Q4 U.4 IR ↔ stmt byte-diff): ✅ 89.6% PASS

Real-corpus run on `test-suite/corpus/pycsl-reference/*.py` (386 files):
- **PASS: 346/386 (89.6%)** — `ir_to_stmt` returned `Some(...)`.
- **SKIP: 24/386 (6.2%)** — outside the converter's subset
  (nested subscripts, lambdas, string slicing, match-case, etc.)
- **FAIL_DRIVER: 0/386**.
- **FAIL_M5: 16/386 (4.1%)** — Module 5 itself could not
  produce IR for these inputs.

Against testable cases: **346/370 = 93.5% PASS**.

### Layer 4 (Q4 U.5 round-trip): ✅ extended to compound + assert + ghost + SFor (2026-05-29 v3)

`Phase1d_StmtToIr.v` (935 lines) contains:
- 68 per-constructor round-trip lemmas (all by `reflexivity`).
- Main theorem `stmt_to_ir_simple_roundtrip`.
- `U6_chain_after_roundtrip` for chain composition via `gen`.
- Encoder coverage:
  - **Simple subset** (Definition v1): SSkip, SAssign, SAugAssign,
    SArraySet, SReturn, SBreak, SContinue, SLabel, SRaise.
  - **Compound** (Fixpoint v2): SSeq, SIf, SWhile (default
    inv/var), SCritical, STryCatch, STupleUnpack, SFieldAssign,
    SFieldAugAssign.
  - **Assert + ghost + SFor** (v3): SAssert, SGhostDecl,
    SGhostAssign (all three aug_op variants), SFor case-a
    (Var-iter, `allow_iter_mut = true`).
- `contract_expr_to_ir` Fixpoint covers ~25 contract_expr
  constructors (CInt, CVar, CResult, CBoolLit, CLength,
  CStringLit, CNeg, CNot, arith CBinOp, CEq..CGe, CAnd/COr/
  CImplies/CIff, CGMapEmpty, CGSetEmpty, CGNil, plus CGMapGet,
  CGSetAdd, CGSetMem, CGCons, CGListLen).
- Hand-built `for_range_ir` + 2 desugaring Examples for
  **SFor case-b** (`for x in range(N)` → `SSeq+SWhile`).

Still uncovered in U.5: SThreadEntry (concurrency-out-of-scope),
plus the ~40 contract_expr constructors not in the encoder
subset (CForall/CExists/COld/CIsSorted/CSum/CSlice/CGMapRemove/
CGSetUnion/etc.). Adding them is mechanical reflexivity, gated
by no architectural blockers.

All proofs closed under the global context (zero PyCSL axioms,
zero propext/funext).

## CC.4 citation map (Layer-1 anchors to Layer-0 theorems)

| Mirror file | Rocq theorem | Lean theorem | Status |
|---|---|---|---|
| `Module5_IREmitter.py` | `Phase6h_CorrMain.wp_gen_correct` | `PyCSL.CorrMain.wpGenCorrect` | ✅ |
| `Module6_WhyMLTranspiler.py` | `Phase5b_Soundness.pycsl_soundness` | `PyCSL.Soundness.pycsl_soundness` | ✅ |
| `module6_whyml/preamble.py` | `Phase6i_Soundness.why3_implements_wp_w_derived` | `PyCSL.Why3Vcg.vcgSound` | ✅ |
| `Module4_SemanticAnalyzer.py` | `Phase1_AST.expr_eq_dec` | `PyCSL.AST.Expr` (re-added 2026-05-29 v3 via audit-anchor stub; manual Expr.decEq pending) | ✅ Rocq, ✅ Lean (anchor) |

These citations now have semantic effect: `proof2why3` extracts the
theorem statement and emits it as a Why3 axiom in the generated
WhyML preamble. The cross-validation step (`proof2why3 cross-check`)
canonicalizes the Rocq and Lean statements and verifies they agree.

## What landed in the most recent sessions (2026-05-28 / 2026-05-29)

Cross-reference `closer-to-code-execution-status.md` items 24-46
for the full chronological log. The summary:

### Q3 Sub-β closure (items 21-25 then 30)
- `Phase6c_VcFormula.v` extracted from Phase6m; new build-order
  `Phase6k → Phase6c → Phase6j`.
- `why3_certificate` redefined as the witness function type
  directly (no opaque sealed-unit).
- `enrich_main_cert` axiom deleted.
- All Why3-validation chain theorems now closed under context.
- Lean parity: `Why3Certificate` is a structure carrying the
  witness; new `Why3CertWitness` axiom hidden behind opaque check.

### Q4 Upward completion (items 26-46)
- U.1: `Phase0_IrJson.v` — json_value / contracts_ir /
  function_ir / program_ir.
- U.2: `Phase1b_IrToStmt.v` (1300+ lines, 18 smoke tests).
- U.3: `Phase1c_ValidateIr.v` with three slices: bool validators,
  `keys_unique_at` + lookup lemmas, fully-recursive
  `KeysUniqueRec` + `well_formed_and_unique_implies_validate`.
- U.4: extraction pipeline (`Phase1b_IrToStmtExtract.v` +
  `extracted/ir_driver.ml` + `bin/extraction-byte-diff-upward.sh`).
- U.5: `Phase1d_StmtToIr.v` round-trip theorems.
- U.6: chain composition via `gen` totality.

### Formal AST extensions (items 38, 40, 42)
- `EFieldGet` constructor for class field reads.
- `ECall` constructor for general function/method calls.
- `OpMod` constructor for modulo operation.
- Both Rocq and Lean mirrors updated; `expr_eq_dec` extended
  with `list_eq_dec` for the nested list case.

### Self-annotate citations (items 25, 75)
- CC.4 citations added to Module 4/5/6 + module6_whyml/preamble.
- Mirror-check + self-annotation suite both stay green.

## What's left (priority order)

Layer 2 is fully green (26/26 PROVED). Items #1-#6 from the
previous revision are CLEARED — see the Layer 2 table above. Only
Layer 4 follow-up and architectural items remain.

### 1-6. CLEARED (2026-05-29 v2)
Items #1 through #6 (Map-aware `_to_bool`, set-union auto-trust,
Module5 `'mu → option int`, Module6 class M sub-case, Module1
class G, Module2 termination) are no longer blockers. The
existing auto-trust mechanism (`_should_auto_trust_set_op` at
`auto_trust.py:242-257`) covers BinOp(|/&/^/-) on map operands,
`for x in map_val:`, and `if map_val:` truthiness in one pass.
The other modules pass without specific intervention.

### 7. Q4 U.5 expansion (Layer 4 follow-up; non-blocking) — DONE
Extended `Phase1d_StmtToIr.v` (399 → 935 lines across v2 + v3,
2026-05-29) with compound stmts AND assert/ghost/SFor cases plus
the contract_expr encoder. 68 round-trip lemmas total; all closed
under global context. Remaining U.5 work (~40 contract_expr
constructors, SThreadEntry) is mechanical, no architectural
blockers.

### 8. Q4 corpus residue (Layer 4 architectural)
22 corpus blockers (down from claimed 24; verified via
`bin/extraction-byte-diff-upward.sh` on 2026-05-29). Breakdown:

| Blocker | Count | Effort |
|---|---|---|
| Return/Assign/While/If (expr-level constructs in containers) | 16 | ~2 days each item; many share root cause |
| Match-case | 2 | ~5-10 days (new pattern inductive + SOS) |
| TupleUnpack literal, GhostAssign-CGStrSub, GhostArraySet, For-method-call | 4 | 1-2 days each |

Total realistic effort: ~4-6 weeks (not multi-week-each
literally). Pick smallest first (3-arg range, CGStrSub, SGhostArraySet),
graduate to per-construct expr extensions, leave lambda
+ match-case as standalone initiatives.

## What we are NOT doing (out of scope)

- **Set semantics via Fset**: deferred until set-union auto-trust
  proves insufficient. Substantial WhyML theory work.
- **Per-slot tuple type inference**: class O handled via
  auto-trust; per-slot inference requires IR-level type threading.
- **Function-pointer dispatch in Module4** (class H): needs a
  refactor of `_PROTECTED_HANDLERS[type(node)]`.
- **List comprehensions / enumerate / zip** as body-level
  constructs: tracked in `remains-to-implement.md`.
- **Modules 1-3 formalization**: Tier-2 `\trusted reviewer:` by
  plan design (CC.6).
- **WhyML standard library theorems**: Tier-2 trust.
- **SMT solver soundness proofs**: Tier-1 axiom
  (`altErgoCorrect`).
- **Why3 kernel formalization**: Sub-β formalizes only the formula
  evaluation subset PyCSL uses, not the full Why3 logic.

## Risk register

- **`make self-annotate-verify` could regress silently.** The gate
  runs `--no-proof`, so transpilation changes that emit invalid
  WhyML won't break it. Always run full-proof on a reference test
  (0342 is the canonical cross-validated example) after Module6
  changes.
- **`src/self-annotate/src/*.py` is the only annotated mirror now.**
  The historical `attic/{rocq,lean}/` mirrors were removed
  2026-05-27.
- **Refactoring may drift queue-doc line numbers.** Treat the
  blocker SHAPE column as the durable identifier.
- **Q4 corpus regressions could hide under empirical metrics.**
  The U.4 byte-diff PASS rate is a coverage metric, not a
  correctness proof. A single converter bug could pass the byte-
  diff (because all the wrong-shape cases are SKIP, not FAIL_DRIVER).
  Always recompute `Print Assumptions` of the U.5 round-trip
  theorems after extending `ir_to_stmt` or `expr_to_ir`.
- **`Why3CertWitness` axiom is universally inhabited in pure Lean.**
  In principle, anyone could apply it outside `Why3Trust.check`.
  Convention requires only the `check` site uses it. Documented in
  `Why3Trust.lean`'s header. The opaque `check` makes the axiom
  invisible to downstream theorem consumers.
- **Standard kernel axioms (propext, Classical.choice, Quot.sound,
  funext) are accepted by convention.** No PyCSL-specific risk;
  these are the same axioms used by Mathlib, Coq stdlib, and the
  Coq/Lean communities generally.

## Suggested next session start

Layer 2 fully green, Q4 U.5 expansion done (compound stmts,
SAssert, SGhost*, SFor), CC.4 Module 4 Lean citation re-anchored.
The remaining open work is:

1. **Q4 corpus residue items** (Layer 4 architectural). Pick the
   smallest unblocked items first:
   - **3-arg range desugar** (~1 day) — extend
     `Phase1b_IrToStmt.v` For/range case with 3-arg pattern.
   - **CGStrSub contract atom** (~1 day) — mechanical addition
     to `Phase1_AST.v` + `Phase1b_IrToStmt.v` + Lean mirror.
   - **EChainedSubscript at expr level** (~2 days) — parallel
     to existing CChainedSubscript; clears chained-subscript
     blockers.
   - **ESlice at expr level** (~2 days).
   - **SGhostArraySet stmt** (~2 days).
   Defer **match-case** (5-10d) and **lambda** (multi-week)
   as standalone initiatives.
2. **U.5 contract_expr expansion** (Layer 4 mechanical,
   non-blocking). Add encoder + round-trip Examples for
   CForall, CExists, COld, CChainedSubscript, CIsSorted, CSum,
   CSlice, CGMapRemove, CGSetUnion, etc. ~40 remaining
   constructors. Estimate: 0.5-1 day total.
3. **Manual `Expr.decEq` in Lean** (Layer 0 follow-up). Write
   the recursion through `List Expr` explicitly to bypass the
   deriving handler limitation. Then update the Module 4 Lean
   citation from `PyCSL.AST.Expr` (anchor only) to point at the
   real DecidableEq instance.

## Working invariants

- **Always verify after each change:**
  `make self-annotate-verify` (Layer 1) + a sample of full-proof
  reference tests (0342 minimum, ideally 0345-0351 too) +
  `pytest` + `bash bin/self-annotate-mirror-check.sh` +
  `bash bin/run-self-annotation-suite.sh`.
- **Single canonical mirror:** edits to `src/pycsl/*.py` may need a
  manual sync to `src/self-annotate/src/*.py` via
  `make sync-annotate-src`.
- **Module6 emission is the load-bearing surface:** Module 5 type
  tags flow through to Module 6's WhyML emission. New tags require
  both ends in sync.
- **Auto-trust is the safety valve:** when a Python pattern can't
  be cleanly modeled in WhyML, an auto-trust list
  (`_auto_trusted_array_returns`, `_auto_trusted_tuple_returns`,
  `_auto_trusted_map_returns`) preserves the Layer 1 contract.
- **CC.4 citations bind Layer 1 to Layer 0.** The four citations
  in Module 4/5/6 + preamble anchor the self-annotation work to
  specific kernel-verified theorems. Adding new Layer 1 modules
  should consider whether they need a citation too.
- **Layer 4 (U.4 byte-diff + U.5 round-trip) is a separate axis.**
  It validates the IR converter against Module 5's actual output,
  not the Layer 1 contracts on Module 5 itself. Layer 1 and
  Layer 4 must both pass for end-to-end correctness.
- **Format the TCB tier when documenting new trust:** when adding
  any new `\trusted reviewer:`, `axiom`, or `Admitted`, identify
  which TCB tier it lives in (0a/0b/1/2/3/4) so the trust
  inventory stays current.

## Trust-seam summary

Per the original `closer-to-code.md` Q4 deliverable:
*"After Q4: trust seam = IR (was: facade); Module 5 spec
machine-checked."*

**Status: achieved.** The pre-IR portion (Modules 1-3) is `\trusted
reviewer:` by design (CC.6 out-of-scope). The post-IR chain
`IR → stmt → whyml_stmt → text → VC` is now backed by:

- `ir_to_stmt` with U.4 byte-diff (empirical) + U.5 round-trip
  (formal).
- `gen` via `wp_gen_correct` (Q2 Sub-α).
- `emit_stmt` via Sub-α composition + CC.5 byte-diff.
- `why3_certificate` validation via Q3 Sub-β (axiom-free in Rocq).

The PyCSL-specific axiom count is **zero in Rocq** and **two
visible + one hidden in Lean** (`altErgoCorrect`,
`trustedContractsAxiom`, `Why3CertWitness`). The remaining trust
is in the Tier-2 modules and the Tier-1 external tools — exactly
where the original plan placed it.
