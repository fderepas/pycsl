# Implementation Plan — Closer-to-Code Formal Semantics

> Source: this design conversation +
> `src/formal-semantics/audit-plan.md`'s existing Sub-α / Sub-β
> decomposition. The plan extends the audit plan with a third
> "upward" direction (Modules 1-5 correspondence) and a lateral
> direction (new PyCSL features).

## Context

`src/formal-semantics/` proves PyCSL's WP calculus is sound — the
main theorem `pycsl_soundness` (Phase5b_Soundness.v) and the
correspondence theorem `wp_gen_correct` (Phase6h_CorrMain.v) have
**zero `Admitted`/`sorry`**. But the proof anchors at the *abstract*
IR (`stmt`, `whyml_stmt` inductive types), not at the actual Python
source or the actual WhyML text Module 6 emits. Three gaps separate
*proven correctness* from *delivered correctness*:

1. **Downward** — `gen : stmt → whyml_stmt` produces inductive terms;
   Module 6 produces strings. Linked by a single axiom
   `module6_encodes_mlw` (Phase6k_VcgSound.v:274) + the Lean mirror
   `why3ValidatesEmitted` (VcgSemBridge.lean:68).
2. **Upward** — `stmt` is an inductive Coq type; Module 5 emits a
   JSON dict. No formal correspondence; the Python pipeline's
   correctness above the IR is uncovered.
3. **Lateral** — four new PyCSL directives shipped since the formal
   model was last aligned: `no_exception`, `allow_iteration_mutation`,
   `allow_finalizer`, `\trusted reviewer:` (reviewer field).
   `assumes bounded_int(N)` IS covered (Phase1_AST.v:129).

Plus three residual gaps the audit plan already calls out:
- `desugar_correct` Admitted in Rocq (`Phase3b_Desugar.v`) — for-loop
  desugaring; not load-bearing on soundness.
- `while_not_continued`, `while_inv_preserved` sorries in Lean
  (`WhileInv.lean`) — Lean-side decorative lemmas, not used by main.

## Decisions

| Question | Decision |
|---|---|
| Direction priority | **All three, sequenced** — lateral → cleanup → downward → upward. |
| `module6_encodes_mlw` aggressiveness | **Fully eliminate via Sub-α + Sub-β** per audit-plan.md. End state: zero named axioms in the WP correspondence chain. |

## Pre-existing assets (verified via exploration)

- `wp_gen_correct` covers **all 22 statement constructors**; per-handler `Handle*English.v`/`.lean` lemmas exist for 11 handlers; **no statement-type gaps**.
- Two named axioms: `module6_encodes_mlw` (Rocq) and `why3ValidatesEmitted` (Lean). Decomposition path is documented in `audit-plan.md` §6 (Sub-α + Sub-β).
- `bounded_int(N)` directive is already in `Phase1_AST.v:129` (`spec_int_model`).
- `spec_trusted : bool` is in the AST; the `reviewer:` field is **not**.
- Pretty-printer / string-output: **completely absent**. The formal model stops at `whyml_stmt` inductive terms.
- Build harnesses (`_CoqProject`, `lakefile.lean`) are both active and current.

## Sequencing — four-stream multi-quarter program

Total calendar: ~6 months single-engineer; ~3-4 months parallelized.

### Quarter 1 — Lateral (new features) + Cleanup (sorries)

Cheap, parallelizable, unblocks downstream work. After Q1: zero `Admitted`/`sorry`; formal AST matches the current PyCSL directive set.

| # | Stream | Item | Effort |
|---|---|---|---|
| L.1 | Lateral | Add `spec_no_exception : list exc_name` field to function records + Lean mirror. Add static-semantics rule. No WP impact (`no_exception` is an assertion-injection feature consumed by Module 6 at expression sites, not by the WP calculus on its own). | 1.5 wk |
| L.2 | Lateral | Add `allow_iteration_mutation : bool` flag on `SFor` records + lemma showing it's transpiler-gating only. | 3 days |
| L.3 | Lateral | Add `allow_finalizer : bool` flag on class records + lemma (same shape as L.2). | 3 days |
| L.4 | Lateral | Extend `spec_trusted` from `bool` to `option REVIEWER_ID` (or pair of `bool` + `string`). Lean mirror. | 2 days |
| C.1 | Cleanup | Close `desugar_correct` Admitted in `Phase3b_Desugar.v`. | 2 wk |
| C.2 | Cleanup | Close `while_not_continued` sorry in `WhileInv.lean`. | 3 days |
| C.3 | Cleanup | Close `while_inv_preserved` sorry in `WhileInv.lean`. | 1 wk |

### Quarter 2 — Sub-α (per-construct emit_stmt formalization)

Define `emit_stmt : whyml_stmt → string` formally and prove per-construct correspondence. Each construct is one PR.

| # | Construct | Python source method |
|---|---|---|
| α.1 | Module-level scaffolding (preamble, `use`, type decls) | `module6_whyml/preamble.py` |
| α.2 | wAssign | `module6_whyml/statements.py:_handle_assign_stmt` |
| α.3 | wAugAssign | `_handle_augassign_stmt` |
| α.4 | wArraySet | `_handle_array_set_stmt` |
| α.5 | wSeq | dispatch composition in `_stmts_to_whyml` |
| α.6 | wIf | `_handle_if_stmt` |
| α.7 | wWhile | `_handle_while_stmt` |
| α.8 | wFor (desugared) | `_handle_for_stmt` |
| α.9 | wTryCatch | `_handle_try_stmt` |
| α.10 | wRaise | `_handle_raise_stmt` |
| α.11 | wReturn | `_handle_return_stmt` |
| α.12 | wCriticalSection | `_handle_critical_section_stmt` |
| α.13 | wGhost (assign/decl) | `_handle_ghost_*_stmt` |
| α.14 | wLabel | inline in `_stmts_to_whyml` |
| α.15 | Expression emission (recursive call) | `module6_whyml/expressions.py:_expr_to_whyml` |

**Per-construct theorem template:**

```coq
Theorem emit_assign_correct :
  forall x e,
    well_formed_assign x e ->
    emit_stmt (gen (SAssign x e)) ∈ acceptable_assign_emissions x e.
```

`acceptable_assign_emissions` is a small predicate listing the
surface-syntax alternatives Module 6 may emit (`let x = ...`,
`x := ...`, bool-coerced `x := if ... then 1 else 0`). The proof
is by case analysis on `gen`'s output shape.

**Effort:** ~10 weeks total, ~3 days per construct PR.

### Quarter 3 — Sub-β (Why3 formula semantics)

Formalize Why3's formula evaluation so that
`why3Validates f → evalVcFormula f` holds *by construction*, not by
axiom. After Q3: zero named axioms in the WP correspondence chain.

| # | Item | Effort |
|---|---|---|
| β.1 | Port Cohen & JF (POPL'24) Why3 formula_rep formalization for the integer subset PyCSL uses. **Risk** — if not already available in Rocq/Lean stdlib, this becomes "port the paper" and grows to ~4 weeks. | 1-4 wk |
| β.2 | Define `evalVcFormula : VcFormula → ExecState → ExecState → Prop` constructively from formula_rep. | 1 wk |
| β.3 | Prove `why3Validates f ↔ ∀ es es', evalVcFormula f es es'`. | 1 wk |
| β.4 | Discharge `why3ValidatesEmitted` axiom (Lean) and remove from `VcgSemBridge.lean`. | 3 days |
| β.5 | Compose α + β to discharge `module6_encodes_mlw` (Rocq) and remove the axiom from `Phase6k_VcgSound.v`. | 1 wk |

### Quarter 4 — Upward (Module 5 IR ↔ formal `stmt`)

The largest single chunk. Formalize the Python IR shape so the formal `stmt` corresponds to actual `Module5_IREmitter.py` output.

| # | Item | Effort |
|---|---|---|
| U.1 | Define `pycsl_ir_json : Type` — a Rocq inductive matching `ir_schema.py`'s `ProgramIR`/`FunctionIR`/`ContractsIR` TypedDicts. | 2 wk |
| U.2 | Define `ir_to_stmt : pycsl_ir_json → option stmt` — total function from well-formed JSON to formal `stmt`. | 2 wk |
| U.3 | Prove `validate_ir_correspondence`: `forall j, validate_ir_py j = OK ↔ ir_to_stmt j ≠ None`. The Python `validate_ir` semantics is captured by the Rocq predicate, giving a *machine-checked spec* for the Python function. | 2 wk |
| U.4 | Extract `ir_to_stmt` from Rocq to OCaml/Python; validate against actual Module 5 output on the reference corpus (`test-suite/corpus/pycsl-reference/*.py`). Byte-diff testing. | 1 wk |
| U.5 | Per-statement-constructor correspondence: `forall ast, py_module5_emit ast = Some j → ir_to_stmt j ≠ None`. Treats Modules 1-4 as `\trusted` frontend; only Module 5's IR-output shape is verified. | 1 wk |
| U.6 | Tie U.5 to `gen`: `ast → IR → stmt → whyml_stmt → text → VC`. | 1 day |

After Q4: trust chain closed end-to-end at the IR boundary. Modules 1-4 remain `\trusted` (parser/weaver/analyzer not in formal scope).

---

## Cross-cutting concerns

### CC.1 Audit-plan.md amendment

`src/formal-semantics/audit-plan.md` is the canonical record of what's proved / axiomatized / trusted. Update after each quarter:

- **End of Q1:** strike the 3 sorry rows; flag the 4 new directives as covered in the AST.
- **End of Q2:** replace the `module6_encodes_mlw` axiom row with a "decomposed into 15 per-construct lemmas" entry.
- **End of Q3:** delete both `module6_encodes_mlw` and `why3ValidatesEmitted` rows from the axiom catalogue.
- **End of Q4:** add a new "Trust boundary: Modules 1-4 / Python frontend" row at the top; the IR boundary is now the seam.

### CC.2 Build harness

The new Rocq files (per-construct emit_stmt lemmas, ~15 files in Q2; ~5 in Q4) need entries in `_CoqProject`. Lean mirrors join `PyCSL.lean`'s import list. Makefile regeneration is automatic via `coq_makefile`.

### CC.3 Glossary terms

New verification-vocabulary terms enter the project. Add each as a one-page entry under `docs/glossary/`:

- **extraction-extensional axiom** — the residual Python↔formal correspondence Sub-α cannot kill (the Rocq pretty-printer must produce byte-equivalent output to the Python one on the corpus; this is validated, not proved).
- **formula_rep** — Why3's formal evaluation predicate (Cohen & JF POPL'24).
- **IR well-formedness** — Module 5's output shape predicate (U.3).
- **trust seam** — the boundary between formally-proved and `\trusted` portions of the pipeline. After Q4: the IR.

### CC.4 Self-annotate citations

Once Q3 closes, `self-remains.md` §CC.2's citations land at theorems with no remaining axioms. Update the self-annotate mirrors to cite post-Sub-α theorems by their new names (`module6_emit_correct`, `vcg_bridge_proven`, etc.) instead of the current `module6_encodes_mlw`. One-day ticket per mirror.

### CC.5 The extraction-extensional residue

Sub-α formalizes a pretty-printer for `whyml_stmt` in Rocq/Lean. The actual Python Module 6 has its own pretty-printer (string-building code in `module6_whyml/{expressions,statements,preamble}.py`). The plan's "correspondence" claim relies on **extraction-extensionality**: the extracted Rocq pretty-printer must produce byte-equivalent output to the Python one on the test corpus.

Honest framing: Sub-α + Sub-β eliminate the *named axiom* modulo the extraction-extensional claim. The claim is then validated by per-corpus byte-diff testing (extend `bin/run-reference-tests.sh` with a golden-output mode comparing extracted-Rocq output to actual Python Module 6 output).

This residue is not strictly an axiom in the Rocq/Lean sense (nothing is `Axiom`ed) — it's a meta-level claim about the relationship between two implementations of the same specification. Document it explicitly in the post-Q3 audit-plan.

### CC.6 Out of scope

- **Modules 1-4 formalization** (libcst ingestion, Lark parsing, AST weaving, semantic analysis). The formal model treats Modules 1-4 as the PyCSL frontend; they remain `\trusted reviewer:` in the self-annotate mirrors. Formalizing them is a research project on libcst + Lark.
- **Alt-Ergo / Z3 SMT solver verification.** `altErgoCorrect` is a separate trust line and stays axiomatic.
- **Concurrency trace semantics.** `wCriticalSection` is in the formal model; deeper trace-level reasoning about lock acquisition orders is research.
- **Why3 kernel formalization.** Sub-β only formalizes the formula evaluation subset PyCSL uses, not the full Why3 logic.

---

## Reused infrastructure (do not reimplement)

| Need | Reuse |
|---|---|
| Statement-level dispatch model | `Phase6d_StmtGen.v:gen` already covers all 22 constructors |
| Per-handler correspondence | 11 Phase6e_Handle*.v lemmas (assign, augassign, arraySet, if, while, for, trycatch, critical, ghostdecl, return, tupleunpack) |
| Build harness | `_CoqProject` (auto-generates Makefile via `coq_makefile`); `lakefile.lean` (handles Lean 4.29 dependencies) |
| Trust-chain documentation | `audit-plan.md` §6 already specifies Sub-α / Sub-β; this plan executes it |
| Reference corpus | `test-suite/corpus/pycsl-reference/` provides ~420 numbered tests as byte-diff targets for U.4 |

## Verification (overall)

After each stream:

```bash
# Build both proof trees:
make -C src/formal-semantics/rocq                    # Rocq
( cd src/formal-semantics/lean && lake build )       # Lean

# Track sorry/Admitted residue (per quarter):
grep -rn "Admitted\|sorry" src/formal-semantics/rocq/ src/formal-semantics/lean/PyCSL/

# Self-annotation suite + mirror-check stay green throughout:
bash bin/run-self-annotation-suite.sh
bash bin/self-annotate-mirror-check.sh

# Reference corpus must not regress:
bash bin/run-reference-tests.sh

# After Q4 — extraction byte-diff validation:
bash bin/extraction-byte-diff.sh   # NEW in CC.5
```

End-state metrics:

```
After Q1: residual sorries = 0;            new directives in formal AST = 4
After Q2: module6_encodes_mlw decomposed;  per-construct theorems = 15
After Q3: named axioms in WP chain = 0     (was 2)
After Q4: trust seam = IR (was: facade);   Module 5 spec machine-checked
```

## Recommended order

1. **Q1**: L.1–L.4 and C.1–C.3 in parallel (low risk, no dependencies).
2. **Q2**: α.1–α.15 sequential within Q2 but each PR self-contained.
3. **Q3**: β.1–β.5; β.1 is the long pole — verify Cohen & JF POPL'24 availability *before* starting Q3.
4. **Q4**: U.1–U.6 gated on α + β completion (the formal model needs to be airtight at the bottom before extending the top).

## Risks

- **Sub-β dependency on POPL'24 work.** If Cohen & JF Rocq/Lean formalization isn't already available, β.1 grows to 4+ weeks porting work. Verify before scheduling Q3.
- **Sub-α may surface Module 6 bugs.** The formalization could reveal that Module 6's actual emission differs from what the formal model predicts. Each such discovery is either a Module 6 bug fix or a formal-model adjustment; both are acceptable outcomes. Budget ~1 week slack per quarter for such fixes.
- **Q4 U.3 hinges on `validate_ir` semantics.** If `ir_schema.validate_ir` has implicit type-checking the spec doesn't capture, U.3's theorem might not hold byte-for-byte. Mitigation: read `ir_schema.py:95-142` carefully during U.1, formalize the actual predicate.
- **Extraction-extensional residue is unavoidable** without rewriting Module 6 in Rocq and extracting Python. The plan accepts this; CC.5 documents the residue honestly.
