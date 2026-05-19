# Claude Review — `formal-semantics-plan.md`

## Overall Assessment

The master plan is well-structured: clear scope, a sensible three-track architecture, and
a CMMI process overlay that provides real discipline. The core design decisions (two-tier
expressions, three-way outcome, state as association list) are all defensible. The remarks
below are ordered from most to least critical.

---

## Critical Issues

### 1. Soundness Theorem: duplicate `st` argument requires explanation

The stated theorem is:

```
wp s Q st st → exec st s out → …
```

`wp` has type `stmt → (state → Prop) → state → state → Prop`. The two `state` arguments
are (based on the Rocq plan) the *pre-state* for `\old` threading and the *current state*.
Passing `st` for both at the top level is intentional — at the function entry point, both
are the initial state — but this is non-obvious to a reader. The plan should add a one-line
clarification: "At the call site, `pre_st = current_st = st`; the two arguments diverge only
inside `eval_contract` when evaluating `\old` sub-expressions."

### 2. `SReturn` WP rule is incomplete

The plan states: `wp (SReturn e) Q st = fun st => Q st`. This is wrong for soundness if `Q`
is the function's postcondition, because `\result` is not bound anywhere. The soundness
theorem says `OReturned st' v → Q st'`, so `Q` must somehow see the return value `v`.
Two standard approaches:

- **Bind `\result` into the post-state**: `Q (update st "\result" (eval_expr st e))` — the
  postcondition receives a state where `"\result"` is bound to the return value.
- **Lift `Q` to take a `val option`**: extend `Q : state → val option → Prop` to carry the
  return value separately.

The plan must commit to one approach and state it explicitly before implementation begins.
The current text ("the caller binds `\result`") defers the decision without naming it.

### 3. `desugar_correct` is missing a freshness side-condition

The stated theorem `exec st s out ↔ exec st (desugar s) out` is unsound without the
precondition that `_pycsl_idx` does not appear free in `s`. The risk register mentions the
reserved name but the theorem statement does not carry it as a hypothesis. The actual
statement should be something like:

```
"_pycsl_idx" ∉ fv_stmt s →
exec st s out ↔ exec st (desugar s) out
```

This is not just a proof detail — it affects the theorem's type signature and any downstream
use in Phase 5b.

### 4. `SContinue` WP `fun _ => True` needs justification in context

`wp SContinue Q st = True` is *sound* (any state satisfies the vacuous WP) but the plan
does not explain *why* this is the right choice. A reader could worry that `continue` is
being handled incorrectly. The key insight to document: `SContinue` only appears inside loop
bodies; the `SWhile` WP wraps the body's WP and checks the invariant separately. The
continue case is discharged by the invariant re-check at the top of the loop, not by the
body's WP. A one-paragraph note in Phase 4 or Section 5 would clarify this.

---

## Moderate Issues

### 5. Phase 5a: non-negativity of the variant is not stated as a precondition

Well-founded induction on `Z` via `Z.lt_wf` requires the induction measure to be
non-negative. The plan's WP for `SWhile` should include a conjunct `eval_variant st ... ≥ 0`
as an invariant obligation. If this conjunct is part of the loop invariant, `while_inv_preserved`
needs it as a hypothesis. The plan's description of the three WP conjuncts for `SWhile`
does not list this explicitly — it should.

### 6. `exec_deterministic`: induction target should be the derivation, not the statement

The plan says "Induction on `s`". For a relation `exec : state → stmt → outcome → Prop`,
the standard technique is induction on the execution derivation `H1 : exec st s out1`,
followed by `inversion H2 : exec st s out2`. Induction on `s` also works but requires
`inversion` of both hypotheses immediately in every branch, which is more cumbersome. Both
approaches succeed, but the prover-specific plan (Phase 3 of the Rocq plan) should settle on
one and document it to avoid confusion during implementation.

### 7. Track 2 gating delays cross-validation

"Track 2 begins only after all `Admitted` blocks in Track 1 are closed." This is
disciplined, but it means the Lean proof strategy is not tested until the Rocq proof is
complete. In practice, the `SWhile` soundness case is the hardest; learning that the Lean
`omega` / well-founded approach has issues only after Rocq is done would be expensive.
Consider: run a *parallel exploratory* Lean prototype through Phase L3 (WP definition only,
with `sorry`) before closing Rocq Phase 5a, to validate the Lean infrastructure early. The
gate for *merging* Lean work remains after Rocq is `Admitted`-free.

### 8. `SWhile` carries the invariant in the AST

The `stmt` constructor `SWhile` includes `inv` and `var` fields. This is a strong modeling
choice: it means every while loop in the formal model must have an explicit invariant. This
is correct for verified PyCSL programs (which require annotations), but the model cannot
represent unannotated Python while loops. The plan should state this restriction explicitly:
the formal semantics covers only *annotated* programs, not arbitrary Python.

---

## Minor Issues

### 9. References to `form/` directory — verify they exist

Section 10 cites `form/01-global-plan.md`, `form/02-Rocq.md`, `form/03-Lean.md`. These
files should be checked to exist at the referenced paths before implementation begins;
they are cited as the source of Rocq/Lean code sketches.

### 10. `eval_contract` for quantifiers: range is integers only

`CForall`/`CExists` quantify over `Z` via `update st x (VInt n)`. This means all quantified
variables range over integers only. Array-valued quantified variables are not supported. This
is not a bug — PyCSL's contract language only quantifies over integers — but the plan should
state it explicitly to avoid confusion.
