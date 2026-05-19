# PyCSL Formal Semantics — Rocq Implementation Plan

## 1. Overview

This plan details the Rocq (Coq) implementation of the PyCSL formal semantics.
Rocq is the primary prover: it shares mathematical foundations with Why3 (the
backend), and the project already uses Rocq proof companions (`*.proofs/`
directories, `bin/run-rocq-proofs.sh`).

**Target:** Rocq 8.18+ with the standard library. No Mathlib dependency.

---

## 2. Build Infrastructure

### 2.1 `_CoqProject`

```
-R . PyCSL
Phase1_AST.v
Phase2_State.v
Phase3_SOS.v
Phase3b_Desugar.v
Phase4_WP.v
Phase5a_WhileInv.v
Phase5b_Soundness.v
Tests.v
```

### 2.2 `Makefile`

```makefile
COQC     := coqc
COQFLAGS := -R . PyCSL
VFILES   := Phase1_AST.v Phase2_State.v Phase3_SOS.v Phase3b_Desugar.v \
            Phase4_WP.v Phase5a_WhileInv.v Phase5b_Soundness.v Tests.v
VOFILES  := $(VFILES:.v=.vo)

all: $(VOFILES)

%.vo: %.v
	$(COQC) $(COQFLAGS) $<

clean:
	rm -f *.vo *.glob *.vok *.vos .*.aux

.PHONY: all clean
```

### 2.3 Compilation Order (Dependency Chain)

```
Phase1_AST.v
    ↓
Phase2_State.v
    ↓
Phase3_SOS.v ← Phase3b_Desugar.v
    ↓
Phase4_WP.v
    ↓
Phase5a_WhileInv.v
    ↓
Phase5b_Soundness.v
    ↓
Tests.v (imports all)
```

---

## 3. File Traceability Table

| File | Phase | Purpose | Imports | Key Definitions | Gate Criterion |
|------|-------|---------|---------|-----------------|----------------|
| `Phase1_AST.v` | 1 | Abstract syntax tree | ZArith, String, List | `binop`, `expr`, `contract_expr`, `frame_cond`, `func_spec`, `stmt` | Compiles; test: construct example AST nodes |
| `Phase2_State.v` | 2 | Values, state, evaluators | Phase1_AST | `val`, `state`, `lookup`, `update`, `eval_expr`, `eval_contract`, `eval_variant`, `eval_binop_z`, `eval_bool`, `array_update` | Compiles; test lemmas: `eval_expr` on 3+ concrete programs returns expected values |
| `Phase3_SOS.v` | 3 | Operational semantics | Phase2_State | `outcome`, `exec` (inductive), `exec_deterministic` (lemma) | `exec_deterministic` proved without `Admitted` |
| `Phase3b_Desugar.v` | 3b | For-loop desugaring | Phase3_SOS | `for_idx`, `desugar` (fixpoint), `desugar_correct` (lemma) | `desugar_correct` proved without `Admitted` |
| `Phase4_WP.v` | 4 | Weakest precondition | Phase3b_Desugar | `wp` (fixpoint) | Compiles; Rocq termination checker accepts structural recursion on `stmt` |
| `Phase5a_WhileInv.v` | 5a | While invariant lemma | Phase4_WP | `while_inv_preserved` (lemma) | Proved without `Admitted`; uses well-founded induction on `eval_variant` via `Z.lt_wf` |
| `Phase5b_Soundness.v` | 5b | Soundness theorem | Phase5a_WhileInv | `pycsl_soundness` (theorem) | Proved without `Admitted` |
| `Tests.v` | — | Concrete tests | Phase5b_Soundness | Test lemmas for example programs | All test lemmas proved |

---

## 4. Detailed Phase Specifications

### 4.1 Phase 1 — AST in Gallina

**Deliverables:**

- `binop` — Arithmetic binary operators: `OpAdd`, `OpSub`, `OpMul`, `OpDiv`
- `expr` — Runtime expressions: `EInt`, `EVar`, `ESubscript`, `EBinOp`, `ENeg`
- `contract_expr` — Contract expressions: all of `expr` plus `CResult`, `CLength`,
  `COld`, comparison operators (`CEq`..`CGe`), boolean connectives (`CAnd`, `COr`,
  `CNot`), implication (`CImplies`), biconditional (`CIff`), quantifiers (`CForall`,
  `CExists`)
- `frame_cond` — `FNothing | FVars (list ident)`
- `func_spec` — Record: `spec_pre`, `spec_post`, `spec_frame`
- `stmt` — Statement constructors: `SSkip`, `SAssign`, `SAugAssign`, `SArraySet`,
  `SSeq`, `SIf`, `SWhile` (with `inv` and `var`), `SFor`, `SReturn`, `SContinue`

**Design decisions:**
- `ident := string` (using Coq's standard `String` module)
- `ident_eq := String.string_dec` (decidable equality for lookup)
- Two-tier expression design mirrors PyCSL's actual restriction that contract
  expressions support more operators than runtime expressions

### 4.2 Phase 2 — State and Concrete Evaluation

**Deliverables:**

- `val` — `VInt Z | VArray (list Z)`
- `state` — Association list `list (ident * val)`
- `lookup : state → ident → option val`
- `update : state → ident → val → state` — cons-based (shadowing)
- `array_update : state → ident → Z → Z → state`
- `eval_binop_z : binop → Z → Z → Z` — division by zero returns 0
- `eval_expr : state → expr → val` — concrete `Fixpoint`, NOT axiomatic
- `eval_bool : state → expr → bool` — truthiness test for guards
- `eval_z : state → state → option val → contract_expr → Z` — integer extraction
- `eval_contract : state → state → option val → contract_expr → Prop` — logical
  evaluation with pre-state and result threading
- `eval_variant : state → state → contract_expr → Z` — variant extraction

**Design decisions:**
- `eval_expr` returns `VInt 0` for unbound variables and out-of-bounds subscripts
  (total function, no `option` — partiality is guarded by `requires` in the
  WP calculus)
- `eval_contract` for `CForall`/`CExists` universally/existentially quantifies over
  `Z`, using `update st x (VInt n)` to bind the quantified variable
- `COld e` evaluates `e` in `pre_st` (the state at function entry)

### 4.3 Phase 3 — Structural Operational Semantics

**Deliverables:**

- `outcome` — `ONormal state | OReturned state val | OContinued state`
- `exec : state → stmt → outcome → Prop` — inductive relation with constructors:
  - `ExecSkip`, `ExecAssign`, `ExecAugAssign`, `ExecArraySet`
  - `ExecSeq`, `ExecSeqReturn`, `ExecSeqContinue`
  - `ExecIfTrue`, `ExecIfFalse`
  - `ExecWhileTrue`, `ExecWhileContinue`, `ExecWhileFalse`
  - `ExecContinue`, `ExecReturn`
- `exec_deterministic` — Lemma: given the same initial state and statement, there
  is at most one outcome

**Proof strategy for `exec_deterministic`:**
Induction on `s`, then inversion of both execution hypotheses. The `SSeq` case
requires chaining the induction hypotheses for `s1` and `s2`. The `SWhile` cases
require distinguishing on the boolean evaluation of the guard.

### 4.4 Phase 3b — For-loop Desugaring

**Deliverables:**

- `for_idx : ident` — reserved name `"_pycsl_idx"`
- `desugar : stmt → stmt` — recursive transformation replacing `SFor` with
  index-variable `SWhile`
- `desugar_correct` — Bi-implication: `exec st s out ↔ exec st (desugar s) out`

**Proof strategy:**
Induction on `s`. The `SFor` case requires showing that element-by-element iteration
via subscript access is equivalent to the for-each semantics.

### 4.5 Phase 4 — Weakest Precondition Calculus

**Deliverables:**

- `wp : stmt → (state → Prop) → state → state → Prop` — structural `Fixpoint`
  on `stmt`

**Key WP rules:**
- `SWhile`: three conjuncts — invariant initialization, invariant preservation with
  variant decrease, postcondition on loop exit
- `SFor`: delegates to `wp (desugar (SFor ...))` — no separate WP rule
- `SReturn`: `fun st => Q st` — the caller binds `\result`
- `SContinue`: `fun _ => True` — vacuously satisfied

### 4.6 Phase 5a — While Invariant Lemma

**Deliverable:**

- `while_inv_preserved` — The keystone lemma, proved by well-founded induction on
  `eval_variant st pre_st var` using `Z.lt_wf`

**Proof strategy:**
Well-founded induction on the variant value. Two inductive cases:
1. `ExecWhileTrue`: body executes normally, variant decreases, loop continues
2. `ExecWhileContinue`: body signals continue, variant decreases, loop continues

Both cases apply the WP-body hypothesis to obtain the invariant in the post-body
state, then invoke the induction hypothesis with the strictly smaller variant.

### 4.7 Phase 5b — Soundness Theorem

**Deliverable:**

- `pycsl_soundness` — The main theorem

**Proof strategy:**
Induction on `s` (the statement), then case analysis on the execution derivation.
Most cases are direct. The two hard cases are:
1. `SSeq`: requires chaining `IHs1` and `IHs2` through the intermediate state
2. `SWhileTrue` / `SWhileContinue`: delegates to `while_inv_preserved`

---

## 5. Test Lemmas (`Tests.v`)

Concrete evaluation tests that serve as validation:

| Test | Statement | Expected Outcome |
|------|-----------|------------------|
| `test_assign` | `exec [] (SAssign "x" (EInt 42)) (ONormal [("x", VInt 42)])` | Provable by constructor |
| `test_seq_assign` | Two sequential assignments | Final state has both bindings |
| `test_if_true` | `SIf (EInt 1) (SAssign "x" (EInt 1)) (SAssign "x" (EInt 0))` | `x = 1` |
| `test_while_sum` | Sum 1..3 via while loop | `total = 6` |
| `test_wp_assign` | `wp (SAssign "x" (EInt 5)) (fun st => lookup st "x" = Some (VInt 5)) st st` | Provable |
| `test_soundness_skip` | `pycsl_soundness` applied to `SSkip` | Trivial |

---

## 6. Tactic Inventory

Expected tactic usage per phase:

| Tactic | Phase | Purpose |
|--------|-------|---------|
| `constructor` / `econstructor` | 3, Tests | Build `exec` derivations |
| `inversion H; subst` | 3 (`exec_deterministic`), 5b | Decompose execution hypotheses |
| `induction s` | 3, 5b | Structural induction on statements |
| `lia` | 5a, 5b | Linear integer arithmetic |
| `nia` | — | Not needed (no nonlinear goals in Track 1) |
| `well_founded_induction` | 5a | Induction on variant for while loops |
| `simpl in *` | 2, 4 | Unfold `wp` and evaluators |
| `destruct` | 2, 3 | Case-split on `option val`, `val`, `bool` |
| `congruence` | 3 | Close contradictory boolean equalities |

---

## 7. Risk Mitigations

| Risk | Mitigation |
|------|------------|
| `eval_contract` non-structural recursion | `contract_expr` is structurally recursive; Rocq accepts it |
| `wp` non-structural on `SWhile` | WP for `SWhile` does not recurse on `wp`; it emits a `forall st'` quantifier. Structural recursion on `stmt` is preserved |
| `while_inv_preserved` mutual dependency with `pycsl_soundness` | Break the cycle: `while_inv_preserved` is proved independently using well-founded induction on the variant, then imported by `pycsl_soundness` |
| Association-list state performance | Acceptable for formal proofs; `FMapList` can be substituted later for better lookup lemmas without changing the interface |
