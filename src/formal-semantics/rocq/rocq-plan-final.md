# PyCSL Formal Semantics — Rocq Implementation Plan (Final)

> **Traceability note:** This is the reviewed and corrected final version.
> The original plan is preserved unchanged at `rocq-plan.md`.
> All changes are annotated with `[REVISED]` or `[ADDED]`.

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
| `Phase3b_Desugar.v` | 3b | For-loop desugaring | Phase3_SOS | `for_idx`, `fresh_in_stmt`, `desugar` (fixpoint), `desugar_correct` (lemma) | `desugar_correct` proved without `Admitted`; freshness precondition in theorem statement |
| `Phase4_WP.v` | 4 | Weakest precondition | Phase3b_Desugar | `wp` (fixpoint) | Compiles; Rocq termination checker accepts structural recursion on `stmt`; `SReturn` binds `\result` |
| `Phase5a_WhileInv.v` | 5a | While invariant lemma | Phase4_WP | `while_inv_preserved` (lemma) | Proved without `Admitted`; `eval_variant ≥ 0` is explicit hypothesis; uses `Z.lt_wf` |
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
- > **[ADDED]** `SWhile` carries `inv : contract_expr` and `var : contract_expr` as
  mandatory fields. The model covers only annotated programs; there is no constructor
  for unannotated loops.
- > **[ADDED]** `"\result"` is a reserved identifier, forbidden as a program variable
  name. `SReturn` binds `"\result"` into the post-state (see Phase 4).

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
- > **[ADDED]** Division by zero returns `0` as a modeling convention. This value is
  never observed in valid executions because the WP calculus requires any `requires`
  clause to exclude zero denominators before a division expression is evaluated. The
  connection is: `eval_binop_z OpDiv a 0 = 0` is safe precisely because
  `wp ... Q pre_st st` implies the precondition holds, which rules out zero.
- > **[ADDED]** `\forall` / `\exists` quantify over integer-valued variables only.
  Array-valued quantified variables are not supported in Track 1 scope.

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

**[REVISED] Proof strategy for `exec_deterministic`:**

Induction on **the execution derivation** `H1 : exec st s out1`, then `inversion H2`
on the second hypothesis `H2 : exec st s out2`. This is cleaner than induction on `s`
because each induction case directly provides a specific execution constructor,
avoiding the need to universally quantify over all derivations within each statement
form. The `SSeq` case chains the induction hypotheses for the sub-statements; the
`SWhile` cases use `eval_bool` determinism to discharge the contradictory
`WhileTrue`/`WhileFalse` combinations.

```coq
Lemma exec_deterministic : ∀ st s out1 out2,
  exec st s out1 → exec st s out2 → out1 = out2.
Proof.
  intros st s out1 out2 H1 H2.
  induction H1; inversion H2; subst; try congruence; eauto.
Qed.
```

### 4.4 Phase 3b — For-loop Desugaring

**Deliverables:**

- `for_idx : ident` — reserved name `"_pycsl_idx"`
- `fresh_in_stmt : ident → stmt → Prop` — decidable predicate: `id` does not appear
  as an assigned or bound variable in `s`
- `desugar : stmt → stmt` — recursive transformation replacing `SFor` with
  index-variable `SWhile`
- `desugar_correct` — **[REVISED]** Bi-implication with freshness precondition:

```coq
Lemma desugar_correct : ∀ st s out,
  fresh_in_stmt "_pycsl_idx" s →
  exec st s out ↔ exec st (desugar s) out.
```

**Proof strategy:**
Induction on `s`. The `SFor` case requires showing that element-by-element iteration
via subscript access is equivalent to the for-each semantics, under the assumption
that `_pycsl_idx` does not conflict with any existing program variable.

> **[ADDED]** The freshness precondition is not merely a proof detail — it must appear
> in the theorem's type signature so that callers (including Phase 5b) carry it as an
> explicit obligation.

### 4.5 Phase 4 — Weakest Precondition Calculus

**Deliverables:**

- `wp : stmt → (state → Prop) → state → state → Prop` — structural `Fixpoint`
  on `stmt`

> **[ADDED — `wp` argument roles]** `wp` takes four arguments:
> - `s : stmt` — the statement
> - `Q : state → Prop` — the postcondition
> - `pre_st : state` — the entry state at function call, used to evaluate `\old`
>   sub-expressions in `eval_contract`; threaded unchanged through all recursive calls
> - `st : state` — the current state at the point of evaluation
>
> For most statement forms only `st` is used. `pre_st` reaches `eval_contract` only
> when checking `requires`/`ensures` clauses that contain `\old`.

**Key WP rules:**

- `SSkip`: `fun st => Q st`
- `SAssign x e`: `fun st => Q (update st x (eval_expr st e))`
- `SSeq s1 s2`: `wp s1 (wp s2 Q pre_st) pre_st`
- `SIf e s1 s2`: `fun st => if eval_bool st e then wp s1 Q pre_st st else wp s2 Q pre_st st`
- `SWhile inv var body`: three conjuncts (see below)
- `SFor`: delegates to `wp (desugar (SFor ...)) Q pre_st` — no separate WP rule
- **[REVISED] `SReturn e`**: `fun st => Q (update st "\result" (eval_expr st e))` —
  the return value is bound under the reserved key `"\result"` in the post-state,
  making it available to `\result` references in `ensures` clauses
- `SContinue`: `fun _ => True` — vacuously satisfied; see note below

> **[ADDED — `SContinue` justification]** `wp SContinue Q pre_st = fun _ => True`
> is sound because `continue` only appears inside loop bodies and interrupts the normal
> control path. The loop invariant is re-checked at the top of each `SWhile` iteration
> by the `SWhile` WP conjuncts; the body's WP does not need to enforce `Q` for the
> `continue` path.

**`SWhile` WP — three conjuncts:**

```
wp (SWhile inv var body) Q pre_st st ≡
  (* 1. Invariant holds in the initial state *)
  eval_contract st pre_st None inv
  ∧
  (* 2. Invariant preserved with variant decrease and non-negativity *)
  (∀ st', eval_contract st' pre_st None inv →
          eval_bool st' cond = true →
          wp body (fun st'' =>
            eval_contract st'' pre_st None inv
            ∧ eval_variant st'' pre_st var < eval_variant st' pre_st var
            ∧ eval_variant st'' pre_st var ≥ 0
          ) pre_st st')
  ∧
  (* 3. Postcondition on loop exit *)
  (∀ st', eval_contract st' pre_st None inv →
          eval_bool st' cond = false →
          Q st')
```

> **[ADDED]** The non-negativity clause `eval_variant st'' ... ≥ 0` in conjunct (2)
> is required for `Z.lt_wf` to fire in Phase 5a. It is an annotation obligation on
> the programmer: the variant expression must be provably non-negative whenever the
> invariant holds.

### 4.6 Phase 5a — While Invariant Lemma

**Deliverable:**

- `while_inv_preserved` — The keystone lemma

**[REVISED] Theorem statement:**

```coq
Lemma while_inv_preserved :
  ∀ (cond : expr) (body : stmt) (inv var : contract_expr)
    (Q : state → Prop) (pre_st st : state),
    eval_contract st pre_st None inv →
    eval_variant st pre_st var ≥ 0 →       (* explicit non-negativity *)
    (∀ st', eval_contract st' pre_st None inv →
            eval_bool st' cond = true →
            wp body (fun st'' =>
              eval_contract st'' pre_st None inv
              ∧ eval_variant st'' pre_st var < eval_variant st' pre_st var
              ∧ eval_variant st'' pre_st var ≥ 0) pre_st st') →
    (∀ st', eval_contract st' pre_st None inv →
            eval_bool st' cond = false → Q st') →
    ∀ out, exec st (SWhile inv var cond body) out →
    match out with
    | ONormal st' | OReturned st' _ => Q st'
    | OContinued _ => True
    end.
```

**Proof strategy:**
Well-founded induction on `eval_variant st pre_st var` using `Z.lt_wf`. The
non-negativity hypothesis ensures the measure is in the natural number subdomain.
Two inductive cases:
1. `ExecWhileTrue`: body executes normally, variant decreases, loop continues
2. `ExecWhileContinue`: body signals continue, variant decreases, loop continues

Both cases apply the WP-body hypothesis to obtain the invariant and non-negativity in
the post-body state, then invoke the induction hypothesis with the strictly smaller
variant.

### 4.7 Phase 5b — Soundness Theorem

**Deliverable:**

- `pycsl_soundness` — The main theorem

**[REVISED] Proof strategy:**

Induction on **the execution derivation** `Hexec : exec st s out`, not on `s`. Each
induction case directly names a specific execution constructor, making the `wp`
hypothesis `Hwp` directly applicable.

```coq
Theorem pycsl_soundness : ∀ st s out Q,
  exec st s out →
  wp s Q st st →
  match out with
  | ONormal st'     => Q st'
  | OReturned st' _ => Q st'
  | OContinued _    => True
  end.
Proof.
  intros st s out Q Hexec Hwp.
  induction Hexec; simpl in Hwp; eauto.
  (* SSeq: chain IHHexec1 and IHHexec2 through intermediate state *)
  (* SWhileTrue/SWhileContinue: delegate to while_inv_preserved *)
Qed.
```

The two hard cases are:
1. `ExecSeq`: requires chaining `IHHexec1` and `IHHexec2` through the intermediate state
2. `ExecWhileTrue` / `ExecWhileContinue`: delegates to `while_inv_preserved`

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

> **[ADDED]** `test_while_sum` proves a three-iteration while loop over a concrete
> ground state. Use `vm_compute` or `Compute` to evaluate the execution derivation
> rather than chaining constructors manually. Ensure `eval_expr` and `exec` constructors
> are `Transparent` (not `Opaque`) so that `vm_compute` can reduce them. If the
> proof is too slow by computation, build it by chaining three `ExecWhileTrue`
> constructors followed by `ExecWhileFalse`.

---

## 6. Tactic Inventory

Expected tactic usage per phase:

| Tactic | Phase | Purpose |
|--------|-------|---------|
| `constructor` / `econstructor` | 3, Tests | Build `exec` derivations |
| `inversion H; subst` | 3 (`exec_deterministic`), 5b | Decompose execution hypotheses |
| `induction H` (derivation) | 3, 5b | Induction on `exec` derivation — preferred over induction on `s` |
| `lia` | 5a, 5b | Linear integer arithmetic (variant decrease, bounds) |
| `nia` | 3b | Non-linear arithmetic may arise in `SFor` range arithmetic (e.g. `i * step`); include in tactic inventory |
| `well_founded_induction` | 5a | Induction on variant for while loops via `Z.lt_wf` |
| `simpl in *` | 2, 4 | Unfold `wp` and evaluators |
| `destruct` | 2, 3 | Case-split on `option val`, `val`, `bool` |
| `congruence` | 3 | Close contradictory boolean equalities |
| `vm_compute` | Tests | Evaluate ground terms in test lemmas |

> **[REVISED]** `nia` is now listed (was "not needed") because `SFor` range
> arithmetic in Phase 3b may involve non-linear products (`i * step`).

---

## 7. Risk Mitigations

| Risk | Mitigation |
|------|------------|
| `eval_contract` non-structural recursion | `contract_expr` is structurally recursive; Rocq accepts it |
| `wp` non-structural on `SWhile` | WP for `SWhile` does not recurse on `wp`; it emits a `forall st'` quantifier. Structural recursion on `stmt` is preserved |
| `while_inv_preserved` mutual dependency with `pycsl_soundness` | Break the cycle: `while_inv_preserved` is proved independently using well-founded induction on the variant, then imported by `pycsl_soundness` |
| Association-list state performance | Acceptable for formal proofs; `FMapList` can be substituted later for better lookup lemmas without changing the interface |
| `desugar_correct` freshness unprovable | Add `fresh_in_stmt` as a decidable boolean predicate; the obligation is discharged by the caller with a concrete name check |
| Variant non-negativity unprovable from invariant alone | Programmer must include `eval_variant ≥ 0` as part of the loop invariant or as a separate annotation; this is checked by the WP |
