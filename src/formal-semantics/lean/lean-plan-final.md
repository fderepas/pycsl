# PyCSL Formal Semantics — Lean 4 Implementation Plan (Final)

> **Traceability note:** This is the reviewed and corrected final version.
> The original plan is preserved unchanged at `lean-plan.md`.
> All changes are annotated with `[REVISED]` or `[ADDED]`.

## 1. Overview

This plan details the Lean 4 port of the PyCSL formal semantics. Lean is the
secondary prover: the port begins only after all `Admitted` blocks in the Rocq
implementation are closed, so the theorem statements and AST design are stable.

**Target:** Lean 4 (pinned toolchain — see §2.1). Mathlib for `Int` support (pinned
to a release tag). Managed via Lake.

### 1.1 Why Lean 4 after Rocq?

| Advantage | Impact on PyCSL |
|-----------|----------------|
| **Faster linear arithmetic** | Lean's `omega` tactic discharges the linear integer goals that dominate WP proofs (loop bounds, variant decrease) more quickly than Rocq's `lia` in many benchmarks |
| **Native syntax embedding** | Lean's macro system allows embedding PyCSL `#@` contract syntax as native Lean notation — enabling a live contract checker in the editor |
| **Independent verification** | A second trusted kernel confirming the same theorem strengthens the result |

---

## 2. Build Infrastructure

### 2.1 `lean-toolchain`

> **[ADDED]** Pin the Lean version via a `lean-toolchain` file in the project root.
> Example (update to the version used during development):

```
leanprover/lean4:v4.12.0
```

This file must be committed before any Phase L0 work begins. Never rely on the system
default Lean installation.

### 2.2 `lakefile.lean`

> **[REVISED]** Mathlib is pinned to a specific release tag, not `"main"`. `"main"`
> is a fast-moving branch; a `lake update` at any point would pull breaking changes.

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
  "https://github.com/leanprover-community/mathlib4" @ "v4.12.0"
  -- Update tag to match the pinned lean-toolchain version.
  -- Do NOT use "main" — it is a moving target.
```

### 2.3 `PyCSL.lean` (Root Import)

```lean
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.DesugarDef
import PyCSL.Desugar
import PyCSL.WP
import PyCSL.WhileInv
import PyCSL.Soundness
import PyCSL.Tests
-- import PyCSL.Macros  -- Phase L5 bonus
```

### 2.4 Compilation Order (Dependency Chain)

```
PyCSL/AST.lean
    ↓
PyCSL/State.lean
    ↓
PyCSL/SOS.lean ← PyCSL/DesugarDef.lean ← PyCSL/Desugar.lean
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

> **[ADDED]** `DesugarDef.lean` is a new file (split from `Desugar.lean`). It
> contains the pure `desugar : Stmt → Stmt` transformation and imports only `AST`.
> `WP.lean` can import `DesugarDef` without pulling in `SOS`. `Desugar.lean` contains
> only `desugar_correct` (which needs `SOS`) and imports both `DesugarDef` and `SOS`.

---

## 3. File Traceability Table

| File | Phase | Rocq Counterpart | Purpose | Key Definitions | Gate Criterion |
|------|-------|------------------|---------|-----------------|----------------|
| `PyCSL/AST.lean` | L0 | `Phase1_AST.v` | Inductive types for syntax | `Binop`, `Expr`, `ContractExpr`, `FrameCond`, `FuncSpec`, `Stmt` | Compiles; test: construct example AST |
| `PyCSL/State.lean` | L1 | `Phase2_State.v` | Values, state, evaluators | `Val`, `State`, `lookup`, `update`, `evalExpr`, `evalContract`, `evalVariant`, `evalBinopZ`, `evalBool` | Compiles; `termination_by` accepted; test lemmas pass |
| `PyCSL/SOS.lean` | L2 | `Phase3_SOS.v` | Operational semantics | `Outcome`, `Exec` (inductive Prop), `exec_deterministic` | `exec_deterministic` proved without `sorry` |
| `PyCSL/DesugarDef.lean` | L2 | — (split from `Phase3b_Desugar.v`) | Pure `desugar` transformation | `forIdx`, `freshInStmt`, `desugar` | Compiles; imports `AST` only |
| `PyCSL/Desugar.lean` | L2 | `Phase3b_Desugar.v` | Desugaring correctness | `desugar_correct` (with freshness) | Proved without `sorry`; freshness precondition in statement |
| `PyCSL/WP.lean` | L3 | `Phase4_WP.v` | Weakest precondition | `wp`, `wpFor` (helper for `SFor`) | Compiles; termination checker accepts structural recursion |
| `PyCSL/WhileInv.lean` | L4a | `Phase5a_WhileInv.v` | While invariant lemma | `while_inv_preserved` | Proved without `sorry`; non-negativity is explicit hypothesis |
| `PyCSL/Soundness.lean` | L4b | `Phase5b_Soundness.v` | Soundness theorem | `pycsl_soundness` | Proved without `sorry` |
| `PyCSL/Tests.lean` | — | `Tests.v` | Concrete evaluation tests | Test theorems | All pass |
| `PyCSL/Macros.lean` | L5 | — (Lean-only) | `#@` syntax embedding | `#requires`, `#ensures`, `#assigns`, `#loop_invariant`, `#loop_variant` macros | Example annotated function type-checks |

> **[REVISED]** Phase L4 is split into L4a (`WhileInv.lean`) and L4b
> (`Soundness.lean`), mirroring the Rocq Phase 5a/5b split. Each has its own gate
> criterion. `DesugarDef.lean` is a new file at Phase L2.

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

> **[ADDED]** `"\result"` is reserved as in the Rocq plan. `Stmt.ret` binds
> `"\result"` in the post-state inside `wp`. `Stmt.while_` carries `inv` and `var`
> fields; there is no constructor for unannotated loops.

### 4.2 Phase L1 — State and Evaluation

**Goal:** Port evaluators with Lean 4 termination hints.

**[REVISED] State representation:** Use association lists (`List (Ident × Val)`)
throughout — not `Std.HashMap`. Association lists keep proof obligations analogous to
the Rocq proofs and avoid a `Std` dependency. `Std.HashMap` would be harder to reason
about in inductive proofs (no simple structural induction over the map).

**Key differences:**

| Aspect | Rocq | Lean 4 |
|--------|------|--------|
| `Fixpoint` | Structural recursion automatic | `termination_by` annotation may be needed |
| `option` default | explicit `match` | `.getD` method |
| List lookup | manual `Fixpoint` | `List.find?` + `.map` |
| State | association list | association list (not `Std.HashMap`) |

**Termination strategy:**
- `evalExpr`: structural recursion on `Expr` — accepted automatically
- `evalContract`: structural recursion on `ContractExpr` — accepted automatically
- `evalZ`: structural recursion on `ContractExpr` — accepted automatically

> **[ADDED — mutual recursion clarification]** `evalExpr` and `evalContract` are
> *not* mutually recursive. `evalContract` calls `evalExpr` (since `ContractExpr`
> embeds `Expr`), but `evalExpr` does not call `evalContract`. They can be defined
> sequentially with `def` — no `mutual def … end` block is needed for these.
> `mutual def` is only required if there is genuine mutual recursion between two
> definitions (none exists in Track 1 scope).

**Deliverables:**

- `Val` — `int (n : Int) | array (a : List Int)`
- `State` — `List (Ident × Val)`
- `lookup`, `update`, `arrayUpdate`
- `evalBinopZ`, `evalExpr`, `evalBool`
- `evalZ`, `evalContract`, `evalVariant`

### 4.3 Phase L2 — SOS + Desugaring

**Goal:** Port `Exec` inductive, prove determinism, and port desugaring.

**Deliverables:**

- `Outcome` — `normal | returned | continued`
- `Exec : State → Stmt → Outcome → Prop` — inductive with all constructors from Rocq
- `exec_deterministic` — theorem
- `freshInStmt : Ident → Stmt → Bool` — decidable freshness check (in `DesugarDef`)
- `desugar : Stmt → Stmt` — pure transformation (in `DesugarDef`, imports `AST` only)
- `desugar_correct` — theorem with freshness precondition (in `Desugar`, imports `SOS`)

**Proof strategy for `exec_deterministic`:**
Induction on `h1 : Exec st s out1`, then `cases h2` on the second hypothesis
`h2 : Exec st s out2`. Use `simp` for boolean contradictions where Rocq uses
`congruence`.

> **[REVISED]** Induction is on the execution derivation `h1`, not on `s`, matching
> the Rocq plan correction.

**`desugar_correct` statement:**

```lean
theorem desugar_correct (st : State) (s : Stmt) (out : Outcome)
    (hfresh : freshInStmt "_pycsl_idx" s = true) :
    Exec st s out ↔ Exec st (desugar s) out
```

### 4.4 Phase L3 — WP Calculus

**Goal:** Port `wp` definition with termination proof.

**[REVISED] `SFor` termination via `wpFor` helper:**

Lean 4's structural termination checker will reject a `wp` definition that handles
`SFor` by calling `wp (desugar (.for_ ...))`, because `desugar (.for_ ...)` produces
a `Stmt.while_` that is not a structural sub-term of the original `Stmt.for_`. The
solution is a `wpFor` helper defined outside the structural recursion:

```lean
-- Non-recursive helper: handles SFor by delegating to desugar.
-- Not part of the wp structural recursion.
def wpFor (x : Ident) (lo hi : Expr) (body : Stmt)
    (Q : State → Prop) (preSt st : State) : Prop :=
  wp (desugar (.for_ x lo hi body)) Q preSt st

def wp (s : Stmt) (Q : State → Prop) (preSt : State) : State → Prop :=
  match s with
  | .skip          => Q
  | .assign x e    => fun st => Q (update st x (evalExpr st e))
  | .seq s1 s2     => wp s1 (wp s2 Q preSt) preSt
  | .for_ x lo hi b => wpFor x lo hi b Q preSt
  | ...
  termination_by s
```

Because `wpFor` does not recurse on `Stmt`, the `wp` definition remains structurally
recursive and the termination checker accepts it.

> **[ADDED — `termination_by` syntax note]** In Lean 4 (v4.x releases), the
> annotation for structural recursion is `termination_by s` (Lean infers structural
> from the matched argument). The form `termination_by structural s` seen in some
> nightly builds is not stable. Verify the exact syntax against the pinned toolchain
> version. If the termination checker rejects structural recursion, use
> `decreasing_by simp_wf` or add a `sizeOf` measure.

**[REVISED] `wp` argument roles:**

```lean
def wp (s : Stmt) (Q : State → Prop) (preSt : State) : State → Prop
```

- `s` — the statement
- `Q` — the postcondition
- `preSt` — the entry state, fixed at function call; used to evaluate `\old` in
  `evalContract`; threaded unchanged through all recursive calls
- return type `State → Prop` — the precondition predicate over the current state

**[REVISED] `SReturn` WP:**

```lean
| .ret e => fun st => Q (update st "\result" (evalExpr st e))
```

The return value is bound under the reserved key `"\result"` in the post-state,
making it available to `\result` references in `ensures` clauses.

**`SContinue` WP:**

```lean
| .continue_ => fun _ => True
```

Vacuously satisfied; correct because `continue` only appears in loop bodies and the
loop invariant is re-checked by the `while_` WP conjuncts, not by the body's WP.

### 4.5 Phase L4a — While Invariant Lemma

**Goal:** Port `while_inv_preserved` with non-negativity as explicit hypothesis.

> **[REVISED — phase split]** Previously "Phase L4". Now L4a to give it its own gate.

**Theorem statement:**

```lean
theorem while_inv_preserved
    (cond : Expr) (body : Stmt) (inv var : ContractExpr)
    (Q : State → Prop) (preSt st : State)
    (hInv  : evalContract st preSt none inv)
    (hNonNeg : evalVariant st preSt var ≥ 0)          -- [ADDED]
    (hPres : ∀ st', evalContract st' preSt none inv →
                    evalBool st' cond = true →
                    wp body (fun st'' =>
                      evalContract st'' preSt none inv ∧
                      evalVariant st'' preSt var < evalVariant st' preSt var ∧
                      evalVariant st'' preSt var ≥ 0) preSt st')
    (hPost : ∀ st', evalContract st' preSt none inv →
                    evalBool st' cond = false → Q st')
    (out : Outcome) (hExec : Exec st (.while_ inv var cond body) out) :
    match out with
    | .normal st' | .returned st' _ => Q st'
    | .continued _ => True
    end
```

**Proof strategy:**
Well-founded induction on `evalVariant st preSt var` using `Nat.lt_wfRel` (after
casting to `Nat` via the non-negativity hypothesis) or `WellFoundedRelation` on `Int`
with `Int.lt_wfRel`. Use `omega` for the linear arithmetic goals on variant bounds.

### 4.6 Phase L4b — Soundness Proof

**Goal:** Port `pycsl_soundness`.

> **[REVISED — phase split]** Previously "Phase L4". Now L4b to give it its own gate.

**Proof strategy:**

```lean
theorem pycsl_soundness
    (st : State) (s : Stmt) (out : Outcome) (Q : State → Prop)
    (hExec : Exec st s out)
    (hWp   : wp s Q st st) :
    match out with
    | .normal st'     => Q st'
    | .returned st' _ => Q st'
    | .continued _    => True
    end := by
  induction hExec generalizing Q with
  | skip st => exact hWp
  | assign st x e => exact hWp
  | seqNormal _ _ _ ih1 ih2 => exact ih2 (ih1 hWp)
  | whileFalse _ _ => exact (hWp.2.2 st hWp.1 (by assumption))
  | whileTrue _ _ => apply while_inv_preserved <;> [exact hWp.1; exact hWp.2.1; ...]
  ...
```

> **[REVISED]** Induction is on `hExec : Exec st s out` (the execution derivation),
> not on `s`. This provides a concrete constructor in each case and makes `hWp`
> directly applicable without needing to universally quantify over derivations.

**[REVISED] `Exec` constructor naming in proofs:**

Constructors of the `Exec` inductive prop should follow a consistent naming
convention such as `Exec.execSkip`, `Exec.execAssign`, `Exec.execSeqNormal`, etc.
The tactic proof's `| skip st =>` patterns use the `induction … with` case naming
(Lean lowercases the constructor name in `induction … with` syntax). Ensure the
inductive definition uses names like `execAssign`, `execSkip`, so that `induction
hExec generalizing Q with | execSkip => ...` is consistent.

### 4.7 Phase L5 — Native Syntax Macros (Bonus)

**Goal:** Embed PyCSL `#@` contract syntax as native Lean notation.

> **[ADDED — naming justification]** The `#@` prefix used in PyCSL source files is
> not available as a Lean 4 macro prefix (`#@` conflicts with Lean attribute syntax).
> The macros use `#requires`, `#ensures`, etc. as the closest viable notation. This
> is a deliberate deviation from PyCSL syntax, not an oversight.

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
| `test_assign` | `Exec [] (.assign "x" (.int 42)) (.normal [("x", .int 42)])` | `exact .execAssign ..` |
| `test_seq_assign` | Two sequential assignments | `exact .execSeqNormal .. (.execAssign ..) (.execAssign ..)` |
| `test_if_true` | Branch on truthy value | `exact .execIfTrue .. rfl (.execAssign ..)` |
| `test_while_sum` | Sum 1..3 | Chain `.execWhileTrue` constructors |
| `test_wp_assign` | WP for assignment | `simp [wp, evalExpr, update, lookup]` |
| `test_soundness_skip` | Soundness on skip | `exact pycsl_soundness (.execSkip _) hWp` |

> **[ADDED]** For `test_while_sum`, prefer `decide` if `Exec` and `Outcome` have
> `Decidable` instances derived (via `deriving Decidable`). Otherwise build the proof
> by chaining three `.execWhileTrue` constructors followed by `.execWhileFalse`. Do
> not rely on `native_decide` unless the toolchain is known to support it for this
> inductive.

---

## 6. Key Differences Summary (Rocq → Lean)

| Aspect | Rocq | Lean 4 |
|--------|------|--------|
| Integer type | `Z` (ZArith) | `Int` (Mathlib) |
| State | association list | association list (NOT `Std.HashMap` — proofs are easier) |
| Termination | `Fixpoint` — structural automatically | `termination_by s` annotation; `wpFor` helper for `SFor` case |
| Linear arithmetic | `lia` | `omega` |
| Mutual recursion | `Fixpoint … with …` | `mutual def … end` — not needed for `evalExpr`/`evalContract` (sequential, not mutual) |
| Inversion | `inversion H; subst` | `cases h` / `obtain` |
| Well-founded induction | `Wf.lt_wf` / `measure` | `Nat.lt_wfRel` / `termination_by` |
| Syntax extension | Notation (limited) | `macro` / `syntax` (full Lean macro system) |

---

## 7. Risk Mitigations

| Risk | Mitigation |
|------|------------|
| `wp` termination rejected for `SFor` case | Use `wpFor` helper (§4.4); structural recursion on remaining cases is preserved |
| Mathlib API instability | Mathlib version pinned in `lakefile.lean` to a release tag; only import `Data.Int.Basic` and `Tactic.Omega` |
| `omega` insufficient for some goals | Fall back to `nlinarith` (Mathlib) or manual `have` steps |
| Macro system complexity for Phase L5 | Defer L5 until L4b is complete; L5 is optional and does not affect soundness |
| Lean 4 version changes | Lean version pinned via `lean-toolchain` file (§2.1) |
| Phase L4 blocking both soundness and invariant lemma | Split into L4a / L4b (§3); if `while_inv_preserved` is blocked, `pycsl_soundness` can be stubbed with `sorry` and gated separately |
| `termination_by structural s` syntax variation across Lean versions | Use `termination_by s` (without `structural` keyword); verify against pinned toolchain |
