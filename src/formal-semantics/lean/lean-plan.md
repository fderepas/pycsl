# PyCSL Formal Semantics — Lean 4 Implementation Plan

## 1. Overview

This plan details the Lean 4 port of the PyCSL formal semantics. Lean is the
secondary prover: the port begins only after all `Admitted` blocks in the Rocq
implementation are closed, so the theorem statements and AST design are stable.

**Target:** Lean 4 (v4.x) with Mathlib for `Int` support and `Std` for data
structures. Managed via Lake.

### 1.1 Why Lean 4 after Rocq?

| Advantage | Impact on PyCSL |
|-----------|----------------|
| **Faster linear arithmetic** | Lean's `omega` tactic discharges the linear integer goals that dominate WP proofs (loop bounds, variant decrease) more quickly than Rocq's `lia` in many benchmarks |
| **Native syntax embedding** | Lean's macro system allows embedding PyCSL `#@` contract syntax as native Lean notation — enabling a live contract checker in the editor |
| **Independent verification** | A second trusted kernel confirming the same theorem strengthens the result |

---

## 2. Build Infrastructure

### 2.1 `lakefile.lean`

```lean
import Lake
open Lake DSL

package PyCSL where
  leanOptions := #[⟨`autoImplicit, false⟩]

@[default_target]
lean_lib PyCSL where
  srcDir := "PyCSL"
  roots := #[`PyCSL]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "main"
```

### 2.2 `PyCSL.lean` (Root Import)

```lean
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.Desugar
import PyCSL.WP
import PyCSL.WhileInv
import PyCSL.Soundness
import PyCSL.Tests
-- import PyCSL.Macros  -- Phase L5 bonus
```

### 2.3 Compilation Order (Dependency Chain)

```
PyCSL/AST.lean
    ↓
PyCSL/State.lean
    ↓
PyCSL/SOS.lean ← PyCSL/Desugar.lean
    ↓
PyCSL/WP.lean
    ↓
PyCSL/WhileInv.lean
    ↓
PyCSL/Soundness.lean
    ↓
PyCSL/Tests.lean (imports all)
    ↓
PyCSL/Macros.lean (bonus, optional)
```

---

## 3. File Traceability Table

| File | Phase | Rocq Counterpart | Purpose | Key Definitions | Gate Criterion |
|------|-------|------------------|---------|-----------------|----------------|
| `PyCSL/AST.lean` | L0 | `Phase1_AST.v` | Inductive types for syntax | `Binop`, `Expr`, `ContractExpr`, `FrameCond`, `FuncSpec`, `Stmt` | Compiles; test: construct example AST |
| `PyCSL/State.lean` | L1 | `Phase2_State.v` | Values, state, evaluators | `Val`, `State`, `lookup`, `update`, `evalExpr`, `evalContract`, `evalVariant`, `evalBinopZ`, `evalBool` | Compiles; `termination_by` accepted; test lemmas pass |
| `PyCSL/SOS.lean` | L2 | `Phase3_SOS.v` | Operational semantics | `Outcome`, `Exec` (inductive Prop), `exec_deterministic` | `exec_deterministic` proved without `sorry` |
| `PyCSL/Desugar.lean` | L2 | `Phase3b_Desugar.v` | For-loop desugaring | `forIdx`, `desugar`, `desugar_correct` | `desugar_correct` proved without `sorry` |
| `PyCSL/WP.lean` | L3 | `Phase4_WP.v` | Weakest precondition | `wp` | Compiles; termination checker accepts structural recursion |
| `PyCSL/WhileInv.lean` | L4 | `Phase5a_WhileInv.v` | While invariant lemma | `while_inv_preserved` | Proved without `sorry` |
| `PyCSL/Soundness.lean` | L4 | `Phase5b_Soundness.v` | Soundness theorem | `pycsl_soundness` | Proved without `sorry` |
| `PyCSL/Tests.lean` | — | `Tests.v` | Concrete evaluation tests | Test theorems | All pass |
| `PyCSL/Macros.lean` | L5 | — (Lean-only) | `#@` syntax embedding | `#requires`, `#ensures`, `#assigns`, `#loop_invariant`, `#loop_variant` macros | Example annotated function type-checks |

---

## 4. Detailed Phase Specifications

### 4.1 Phase L0 — AST Port

**Goal:** Translate all Rocq `Inductive` types to Lean 4 `inductive`.

**Key differences from Rocq:**

| Aspect | Rocq | Lean 4 |
|--------|------|--------|
| Integer type | `Z` (from `ZArith`) | `Int` (from `Mathlib.Data.Int.Basic`) |
| Identifier | `string` (from `String`) | `String` (built-in) |
| Decidable equality | `String.string_dec` | `DecidableEq String` instance (automatic) |
| Naming convention | `SAssign`, `EVar` | `.assign`, `.var` (dot notation with `where` blocks) |

**Deliverables:**

- `Binop` — `add | sub | mul | div`
- `Expr` — `int | var | subscript | binop | neg`
- `ContractExpr` — Full logical language (mirrors Rocq one-to-one)
- `FrameCond` — `nothing | vars (xs : List Ident)`
- `FuncSpec` — `structure` with `pre`, `post`, `frame`
- `Stmt` — `skip | assign | augAssign | arraySet | seq | ite | while_ | for_ | ret | continue_`

### 4.2 Phase L1 — State and Evaluation

**Goal:** Port evaluators with Lean 4 termination hints.

**Key differences:**

| Aspect | Rocq | Lean 4 |
|--------|------|--------|
| `Fixpoint` | Structural recursion automatic | `termination_by` annotation required for non-trivial recursion |
| `option` default | explicit `match` | `.getD` method |
| List lookup | manual `Fixpoint` | `List.find?` + `.map` |

**Termination strategy:**
- `evalExpr`: structural recursion on `Expr` — accepted automatically
- `evalContract`: structural recursion on `ContractExpr` — accepted automatically
- `evalZ`: structural recursion on `ContractExpr` — accepted automatically

**Deliverables:**

- `Val` — `int (n : Int) | array (a : List Int)`
- `State` — `List (Ident × Val)`
- `lookup`, `update`, `arrayUpdate`
- `evalBinopZ`, `evalExpr`, `evalBool`
- `evalZ`, `evalContract`, `evalVariant`

### 4.3 Phase L2 — SOS as Lean Prop

**Goal:** Port `exec` inductive and prove determinism.

**Deliverables:**

- `Outcome` — `normal | returned | continued`
- `Exec : State → Stmt → Outcome → Prop` — inductive with all constructors from Rocq
- `exec_deterministic` — theorem

**Proof strategy:**
Same as Rocq: induction on `s`, then `cases` (Lean's `inversion`) on both hypotheses.
Use `simp` for boolean contradictions where Rocq uses `congruence`.

### 4.4 Phase L3 — WP Calculus

**Goal:** Port `wp` definition with termination proof.

**Key issue:** Lean 4 requires explicit termination proofs for all definitions.

```lean
def wp (s : Stmt) (Q : State → Prop) (preSt : State) : State → Prop :=
  match s with
  | .skip        => Q
  | .assign x e  => fun st => Q (update st x (evalExpr st e))
  | .seq s1 s2   => wp s1 (wp s2 Q preSt) preSt
  | ...
  termination_by structural s
```

Structural recursion on `Stmt` should be accepted because all recursive calls are
on strict subterms of `s`. The `SFor` case calls `desugar` first (which produces a
`SWhile`) — this requires `desugar` to decrease the structural size, or factoring the
`SFor` WP through a separate lemma.

### 4.5 Phase L4 — Soundness Proof

**Goal:** Port both `while_inv_preserved` and `pycsl_soundness`.

**Proof strategy:**

```lean
theorem pycsl_soundness ... := by
  induction hExec generalizing Q with
  | skip st => exact hWp
  | assign st x e => exact hWp
  | seqNormal ... ih1 ih2 => exact ih2 (ih1 hWp)
  | whileFalse ... => exact (hWp.2.2 st hWp.1 hCond)
  | whileTrue ... => apply while_inv_preserved <;> [exact hWp.1; exact hWp.2.1]
  ...
```

**Tactic mapping:**

| Rocq tactic | Lean 4 equivalent |
|-------------|-------------------|
| `induction s` | `induction hExec generalizing Q with` |
| `inversion H; subst` | `cases h` / `obtain ⟨_, _⟩ := h` |
| `lia` | `omega` |
| `nia` | `omega` (often sufficient) or `nlinarith` (Mathlib) |
| `well_founded_induction` | `termination_by` or `WellFoundedRelation` |
| `simpl in *` | `simp` / `unfold wp at *` |
| `congruence` | `contradiction` / `simp` |
| `eapply` | `apply` / `exact` (Lean unification is stronger) |

### 4.6 Phase L5 — Native Syntax Macros (Bonus)

**Goal:** Embed PyCSL `#@` contract syntax as native Lean notation.

**Deliverables:**

```lean
macro "#requires " e:term : command => ...
macro "#ensures "  e:term : command => ...
macro "#assigns "  f:term : command => ...
macro "#loop_invariant " e:term : tactic => ...
macro "#loop_variant "   e:term : tactic => ...
```

**Usage example:**

```lean
-- Annotated Python function pasted into Lean editor:
#requires x >= 0
#ensures  result == x * 2
#assigns  nothing
def multiply_by_two (x : Int) : Int := x * 2
```

The macros generate `FuncSpec` terms and `wp`-based proof obligations that
Lean type-checks interactively.

---

## 5. Test Theorems (`PyCSL/Tests.lean`)

| Test | Statement | Approach |
|------|-----------|----------|
| `test_assign` | `Exec [] (.assign "x" (.int 42)) (.normal [("x", .int 42)])` | `exact .assign ..` |
| `test_seq_assign` | Two sequential assignments | `exact .seqNormal .. (.assign ..) (.assign ..)` |
| `test_if_true` | Branch on truthy value | `exact .ifTrue .. rfl (.assign ..)` |
| `test_while_sum` | Sum 1..3 | Chain `.whileTrue` constructors |
| `test_wp_assign` | WP for assignment | `simp [wp, evalExpr, update, lookup]` |
| `test_soundness_skip` | Soundness on skip | `exact pycsl_soundness (.skip _) hWp` |

---

## 6. Key Differences Summary (Rocq → Lean)

| Aspect | Rocq | Lean 4 |
|--------|------|--------|
| Integer type | `Z` (ZArith) | `Int` (Mathlib) |
| Maps | `FMapList` / association list | `Std.HashMap` / association list |
| Termination | `Fixpoint` — structural automatically | `termination_by` annotation required |
| Linear arithmetic | `lia` | `omega` |
| Mutual recursion | `Fixpoint … with …` | `mutual def … end` |
| Inversion | `inversion H; subst` | `cases h` / `obtain` |
| Well-founded induction | `Wf.lt_wf` / `measure` | `Nat.lt_wfRel` / `termination_by` |
| Syntax extension | Notation (limited) | `macro` / `syntax` (full Lean macro system) |

---

## 7. Risk Mitigations

| Risk | Mitigation |
|------|------------|
| `wp` termination rejected for `SFor` case | Factor `SFor` WP through `desugar` in a separate `def`; or use `partial def` with a proof of well-foundedness |
| Mathlib API instability | Pin Mathlib version in `lakefile.lean`; only import `Data.Int.Basic` and `Tactic.Omega` |
| `omega` insufficient for some goals | Fall back to `nlinarith` (Mathlib) or manual `have` steps |
| Macro system complexity for Phase L5 | Defer L5 until L4 is complete; L5 is optional and does not affect soundness |
| Lean 4 version changes | Pin toolchain via `lean-toolchain` file in project root |
