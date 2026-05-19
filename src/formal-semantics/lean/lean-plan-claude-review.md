# Claude Review — `lean-plan.md`

## Overall Assessment

The Lean plan is the most practical of the three: the tactic mapping table and
Rocq→Lean difference tables are genuinely useful. The phase compression (L2 = Rocq 3+3b,
L4 = Rocq 5a+5b) is aggressive but defensible given that the Lean port follows a proven
Rocq blueprint. The main concerns are a dangerous `lakefile.lean` and a real gap in how
the `SFor` WP terminates.

---

## Critical Issues

### 1. `lakefile.lean` pins to `"main"` — will break

```lean
require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "main"
```

Mathlib `main` is a fast-moving branch. A `lake update` at any point will silently
pull a breaking change. The risk section says "Pin Mathlib version" but the sample
file does the opposite. Use a release tag or commit SHA:

```lean
require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.x.0"
```

or a known-good commit SHA. The `lean-toolchain` file (mentioned in the risk section but
not provided) should also specify the exact Lean version, e.g.:

```
leanprover/lean4:v4.12.0
```

Both files must be committed before any Phase L0 work begins.

### 2. `SFor` WP termination via `desugar` is not resolved

The plan notes: "`SFor` WP goes through `desugar` … requires `desugar` to decrease the
structural size, or factoring the `SFor` WP through a separate lemma." But `desugar`
replaces `SFor` with `SWhile`, which is not a structural sub-term of `SFor`. Lean 4's
structural termination checker will reject `wp (.for_ ...) = wp (desugar (.for_ ...))`.

The "separate lemma" approach is the correct one. Concretely:

```lean
-- Separate, non-recursive definition for the SFor case
def wpFor (x : Ident) (lo hi : Expr) (body : Stmt) (Q : State → Prop) (preSt st : State) : Prop :=
  wp (desugar (.for_ x lo hi body)) Q preSt st

def wp (s : Stmt) (Q : State → Prop) (preSt st : State) : Prop :=
  match s with
  | .for_ x lo hi body => wpFor x lo hi body Q preSt st
  | ...
  termination_by s
```

Because `wpFor` is not defined by recursion on `Stmt`, the `wp` definition remains
structurally recursive. This must be decided before Phase L3 implementation starts.

### 3. Phase L4 compresses the two hardest proofs into one phase

The Rocq plan splits `while_inv_preserved` (Phase 5a) and `pycsl_soundness` (Phase 5b)
into separate phases precisely because they are the two hardest proofs and each needs
its own gate criterion. The Lean plan merges them into Phase L4 with a single gate.
If `while_inv_preserved` takes much longer than expected (e.g., due to `omega` not
handling the well-founded measure), the entire L4 phase is stuck. Recommend splitting
into L4a (`WhileInv.lean`, gate: proved without `sorry`) and L4b (`Soundness.lean`,
gate: proved without `sorry`), mirroring the Rocq phase structure.

---

## Moderate Issues

### 4. `termination_by structural s` — syntax needs verification

In Lean 4, the standard annotation for structural recursion is:

```lean
termination_by s   -- Lean infers structural
```

or in recent versions:

```lean
decreasing_by structural_decreasing
```

The form `termination_by structural s` shown in the plan is not standard Lean 4 syntax
as of v4.x. It may compile on a specific nightly but is not guaranteed to work on a
release. Verify against the pinned toolchain version before committing it to the plan.

### 5. `mutual def` is listed but is not needed for `evalExpr`/`evalContract`

The differences table says "Mutual recursion: `Fixpoint … with …` → `mutual def … end`."
But `evalExpr` and `evalContract` are not mutually recursive. `evalContract` calls
`evalExpr` (since `contract_expr` embeds `expr`), but `evalExpr` does not call
`evalContract`. They can be defined sequentially, not mutually. `mutual def … end` is
only needed if there is genuine mutual recursion (e.g., two inductives that each reference
the other). If no such case exists in Track 1, remove `mutual def` from the table to avoid
confusion.

### 6. `Std.HashMap` vs association list: choose one

The "Key Differences" table says "State = `Std.HashMap` / association list". The Rocq plan
uses association lists throughout. The Lean plan should commit to one representation.
Association lists are recommended: they keep the proof obligations analogous to the Rocq
proofs, avoid a `Std` dependency, and make `lookup`/`update` lemmas straightforward to
state. `Std.HashMap` is more performant but significantly harder to reason about in proofs
(no simple structural induction). A note saying "association list is preferred for
proofs; `Std.HashMap` may be used for evaluation only" would resolve the ambiguity.

### 7. `Exec` constructor naming inconsistency in the proof sketch

Section 4.5 shows:

```lean
| skip st => exact hWp
| assign st x e => exact hWp
```

This uses unnamed-style pattern matching on the `Exec` inductive. But the AST convention
table (Section 4.1) says Lean uses dot-notation constructors (`.assign`, `.var`). The
inductive prop `Exec` constructors would be named differently from the `Stmt` constructors:
e.g., `Exec.execAssign`, `Exec.execSkip`, etc. The proof sketch should use the same naming
convention as the type definitions to avoid confusion.

---

## Minor Issues

### 8. `#requires` vs `#@` in Phase L5 macros

The Phase L5 macros use `#requires`, `#ensures`, etc. rather than `#@ requires`. The plan
doesn't explain this choice. In Lean 4, `#@` is not a valid macro prefix (it conflicts with
attribute syntax). The `#requires` choice is pragmatic. A brief note justifying the
deviation from PyCSL syntax would be helpful: *"The `#@` prefix is not available in Lean 4
macro syntax; `#requires` is the closest viable notation."*

### 9. `test_while_sum` — efficiency note

Like the Rocq plan, this test proves a three-iteration while loop in a concrete state.
In Lean 4, `decide` can discharge it if all types have `DecidableEq` and `Decidable`
instances. Make sure `Exec` and `Outcome` derive `Decidable` instances (or the test is
structured as a sequence of `exact .execWhileTrue … (.execWhileTrue … .execWhileFalse)`
constructor applications).

### 10. `Desugar.lean` dependency on `SOS.lean`

The compilation chain shows `SOS.lean ← Desugar.lean` (Desugar imports SOS). But
`desugar : Stmt → Stmt` is a pure transformation on the AST — it does not need `Exec` or
`Outcome` from SOS. Only `desugar_correct` needs SOS. Consider splitting `Desugar.lean`
into `DesugarDef.lean` (pure transformation, depends only on `AST`) and keeping
`desugar_correct` in `Desugar.lean` (depends on `SOS`). This keeps the dependency chain
cleaner and allows `wp` (Phase L3) to import `DesugarDef` without importing all of SOS.
