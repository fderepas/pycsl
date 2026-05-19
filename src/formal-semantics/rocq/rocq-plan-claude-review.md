# Claude Review — `rocq-plan.md`

## Overall Assessment

The Rocq plan is concrete and well-detailed: working Makefile, `_CoqProject`, per-phase
deliverables, and a tactic inventory. These are all things that matter in practice. The
issues below are largely about proof strategy correctness and a few design gaps that will
surface during implementation.

---

## Critical Issues

### 1. `exec_deterministic`: induction on `s` is the wrong driver

The plan says: "Induction on `s`, then inversion of both execution hypotheses." For a
relation `exec : state → stmt → outcome → Prop`, the natural and cleaner proof is:

```coq
intros H1 H2. induction H1; inversion H2; subst; …
```

Induction on `s` can work but it forces you to universally quantify over all execution
derivations of `s` in each case, making the `SWhile` case especially hard (you need to
invert both H1 and H2, which have different shapes for `ExecWhileTrue` vs
`ExecWhileFalse`). Induction on `H1` gives you the constructor directly. Recommend
updating the strategy to "induction on `H1 : exec st s out1`, then `inversion H2`."

### 2. `wp` signature: the two state arguments are unexplained

`wp : stmt → (state → Prop) → state → state → Prop` has two `state` parameters. Based on
the design, the first is `pre_st` (the entry state for `\old`) and the second is the
current state. For almost all WP rules only the current state is used; `pre_st` is needed
only when evaluating `eval_contract` containing `COld`. The plan lists the type but never
explains the role of each argument. Without this, an implementer will not know in the `SSeq`
case whether to propagate `pre_st` unchanged or update it. Document: *`pre_st` is fixed at
function entry and threaded unchanged through all recursive calls.*

### 3. `SReturn` WP does not capture `\result`

The plan states `wp (SReturn e) = fun st => Q st`. In the soundness theorem, the
`OReturned st' v` case requires `Q st'`. For `Q` to discharge a postcondition like
`\result >= 0`, it must know `v`. Two options:

- Bind `\result` into the returned state: `Q (update st "\result" (eval_expr st e))`.
- Add `v` as a parameter to `Q`.

The current rule is silently vacuous for any postcondition that mentions `\result`. This
needs to be resolved before Phase 4, because it affects the `wp` type signature.

### 4. Phase 5b: induction target should be the execution derivation

The plan says "Induction on `s` (the statement)." For `pycsl_soundness`, the induction
must be on `H : exec st s out` so that each case gives you a concrete execution constructor
to work with. Induction on `s` produces a statement induction hypothesis that universally
quantifies over all executions of `s`, which is harder to apply. Recommend:

```coq
theorem pycsl_soundness : ∀ st s out Q,
  exec st s out →
  wp s Q st st →
  …
Proof.
  intros st s out Q Hexec Hwp.
  induction Hexec; …
```

---

## Moderate Issues

### 5. Phase 5a: variant non-negativity must be an explicit hypothesis

`while_inv_preserved` is proved by well-founded induction via `Z.lt_wf`. This requires the
variant value to be non-negative at the induction base. The WP for `SWhile` should include
a conjunct `eval_variant st pre_st var ≥ 0` (or equivalently, the loop invariant should
entail this). The plan's three-conjunct description of the `SWhile` WP does not list this
explicitly. Without it, `while_inv_preserved`'s hypothesis set is incomplete and the
well-founded induction step cannot fire.

### 6. `desugar_correct` is missing the freshness precondition

The theorem `exec st s out ↔ exec st (desugar s) out` is only correct when `_pycsl_idx`
does not appear free in `s`. Add it as a hypothesis:

```coq
Lemma desugar_correct : ∀ st s out,
  fresh "_pycsl_idx" s →
  exec st s out ↔ exec st (desugar s) out.
```

where `fresh id s` is a decidable predicate on the AST. Without this the lemma is false
for programs that already use `_pycsl_idx` as a variable name.

### 7. Division by zero: the connection to `requires` is not stated

`eval_binop_z` returns `0` for division by zero. This is a modeling convention, but the
plan does not state the corresponding obligation: a `requires` clause must prevent the
denominator from being zero before calling a `wp`-verified division. Without this note,
a reader may wonder whether the soundness theorem is weakened by this choice. Add a one-line
remark: *This value is never observed in valid executions because `wp` requires the
precondition to exclude division by zero.*

### 8. `SWhile` carries the invariant in the AST — implication for unannotated loops

`SWhile` has `inv` and `var` fields. This means the formal model only represents *annotated*
while loops. The plan should state this restriction: the Rocq semantics covers PyCSL
programs that have been fully annotated (every loop has an invariant and variant), not
arbitrary Python. Attempting to model an unannotated loop would require dummy invariants,
which is out of scope and should be documented as such.

---

## Minor Issues

### 9. `Tests.v` — `test_while_sum` is non-trivial to prove

Proving `total = 6` for a three-iteration while loop by Rocq constructor chaining is
feasible but tedious. A `decide` or `vm_compute` call will work if the evaluation is
entirely ground (concrete initial state, no free variables). Make sure `eval_expr` and
`exec` are marked `Transparent` or `Compute`-friendly for the test lemmas to be dischargeable
without large manual proofs.

### 10. Tactic inventory: `nia` is marked "not needed"

The plan says `nia` is not needed (no nonlinear goals in Track 1). This is probably correct
for the base integer arithmetic, but the `SFor` desugaring proof and the variant-decrease
step in Phase 5a might generate goals involving products (e.g., `i * step`). If
`desugar_correct` involves a loop over `start..stop..step`, the range arithmetic becomes
non-linear. Reconsider whether `nia` belongs in the tactic inventory before closing Phase 3b.
