# full6-04 — WP Correspondence: what is done, what remains for the TCB

## What has been done

### All admitted lemmas are now proved

The three lemmas that were deferred as `sorry` / `Admitted` are now machine-checked
in both Rocq (Coq) and Lean 4.

| Lemma | Rocq | Lean 4 |
|---|---|---|
| `wp_gen_seq` / `wpGen_seq` | proved (earlier session) | proved |
| `wp_gen_for` / `wpGen_for` | proved | proved |
| `wp_gen_trycatch` / `wpGen_tryCatch` | proved | proved |

The for-loop case required a new intermediate lemma in both provers:

```
gen_lift_continue_wp_w  (Rocq)
genLiftContinue_wpW     (Lean 4)
```

Statement: `wpW (genLiftContinue inc w) Q ↔ wpW w { Q with wcC := λ es' ↦ wpW inc {wcN:=Q.wcC,…} es' }`.
This connects the syntactic rewriting of `continue`-raises in the WhyML tree to the
semantic replacement of the `wcC` continuation.  Proved by structural induction on `w`;
key cases are `wRaise excContinue` (the lifting target) and `wWhile` (left unchanged
because `wpW` for a while loop never reads the outer `wcC`).

### The full WP correspondence is complete

`wpGenCorrect` in `CorrMain.lean` / `Phase6h_CorrMain.v` now assembles all cases into
a single closed theorem with no gaps:

```
∀ s Qn Qr Qc Qb Qe preEs es,
  wp s Qn Qr Qc Qb Qe preEs es  ↔  wpW (gen s) (enc Qn Qr Qc Qb Qe) preEs es
```

### The axiom audit is clean

```lean
-- Tests.lean
#print axioms pycsl_soundness
-- 'pycsl_soundness' depends on axioms: [propext, Classical.choice, Quot.sound]

#print axioms pycslSoundnessVerified
-- 'pycslSoundnessVerified' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Neither theorem mentions `sorryAx`.  `propext`, `Classical.choice`, and `Quot.sound`
are Lean 4 meta-axioms present in every non-trivial Lean proof; they are not
domain-specific.

### Why `pycslSoundnessVerified` lists no domain axioms

`pycslSoundnessVerified` takes its `wpW` hypothesis as a *parameter*:

```lean
theorem pycslSoundnessVerified
    (hWpW : wpW (gen s) (enc Qn Qr Qc Qb Qe) preEs es) :
    outcomePost Qn Qr Qc Qb Qe out
```

The proof chains `wpGenCorrect` → `pycsl_soundness`, neither of which calls any
domain axiom.  The trust in Why3 is placed at the *call site* when the caller
supplies `hWpW`; the theorem itself is an unconditional logical consequence of the
two proved lemmas.

### TCB reduction — Tasks 1–4 complete

Four actions were taken to narrow the Trusted Computing Base:

**Task 1 — `why3WpSound` deleted.**
The axiom was superseded by Path B (`pycslSoundnessVerified` + `why3ImplementsWpW`).
It had zero call sites and has been removed from `Soundness.lean`.

**Task 2 — `why3ImplementsWpW` narrowed.**
The `True →` placeholder in `SoundnessVerified.lean` has been replaced with a typed
certificate:

```lean
axiom why3ImplementsWpW
    (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState) :
    Why3Certificate ws Q →    -- was: True →
    wpW ws Q preEs es
```

`Why3Certificate` is an opaque type in `Why3Trust.lean` whose values are produced
only by `Why3Trust.check` (currently a stub).  The private constructor prevents
construction outside that namespace.

**Task 3 — `altErgoCorrect` narrowed.**
The `True →` placeholder in `Soundness.lean` has been replaced:

```lean
axiom altErgoCorrect (goal : Prop) : SmtCertificate goal → goal
```

`SmtCertificate` is defined alongside `Why3Certificate` in `Why3Trust.lean`.

**Task 4 — `\trusted` annotations strengthened.**
The `Trusted` AST node now carries an optional `reviewer` field (syntax:
`\trusted reviewer: <name>`).  The Weaver emits a `warnings.warn` when a `\trusted`
function has no reviewer.  The IR emitter propagates `reviewer` to the IR dict.
Three existing `\trusted` annotations have been updated:

| Function | File | Contract before | Contract after |
|---|---|---|---|
| `_resolve_direct_imports` | `pycsl.py` | `ensures 1 == 1` | `ensures len(\result) <= len(direct_imports)` |
| `_compute_sccs` | `Module6_WhyMLTranspiler.py` | `ensures 1 == 1` | `ensures len(\result) >= 1` |
| `strongconnect` | `Module6_WhyMLTranspiler.py` | `ensures 1 == 1` | `ensures 1 == 1` (reviewer added) |

All three now carry `reviewer: fabrice@derepas.com`.

---

## What remains to lower the TCB

There are three domain-specific axioms still in the codebase.  `#print axioms` does
not flag them on the *statement* of `pycslSoundnessVerified` because none appears in
that proof text, but each one must be instantiated at every actual use.

---

### Axiom 1 — `why3ImplementsWpW` (narrowed; still an axiom)

```lean
-- SoundnessVerified.lean
axiom why3ImplementsWpW
    (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState) :
    Why3Certificate ws Q →
    wpW ws Q preEs es
```

**Current weakness.**  The `Why3Certificate` is still a stub — `Why3Trust.check`
returns `none` unconditionally (Task 5 not yet done).  In a real deployment, a
caller that produces a forged certificate would be able to instantiate the axiom.

**Step 1 — implement `Why3Trust.check` (Task 5).**
Replace the stub with an IO action that calls `why3 prove -P <prover> mlwPath` as a
subprocess and parses the "Valid" lines.  The certificate is only produced when the
subprocess succeeds, so the only trusted code is the parser for Why3's output format.

**Step 2 — formalise Why3's WP engine (Task 6, high effort).**
Implement `why3Vcg : WhyMLStmt → WpConts → Bool` and prove `why3Vcg ws Q = true → wpW ws Q preEs es`
by induction on `ws`.  This makes `why3ImplementsWpW` a theorem and removes it from
the TCB entirely.  Estimated 3–6 weeks of proof engineering.

---

### Axiom 2 — `altErgoCorrect` (narrowed; still an axiom)

```lean
-- Soundness.lean
axiom altErgoCorrect (goal : Prop) : SmtCertificate goal → goal
```

**Current weakness.**  `SmtTrust.check` also returns `none` unconditionally.  The
conceptual improvement is in place but the implementation is a stub.

**Step 1 — use Lean-native tactics for the arithmetic fragment (Task 7).**
Most goals discharged by Alt-Ergo are linear arithmetic over integers (index bounds,
variant decrements) or simple propositional goals.  Route these through Lean 4's
`omega`, `decide`, and `norm_num` before falling back to `altErgoCorrect`.  This
eliminates the dependency on external SMT for that fragment.

**Step 2 — implement `SmtTrust.check`.**
For residual non-linear goals, validate an SMT proof-term file (e.g., from
`cvc5 --produce-proofs`) and produce a `SmtCertificate` only if the proof is valid.

---

### Axiom 3 — `trustedContractsAxiom` (conditional; lowest risk)

```lean
-- Soundness.lean
axiom trustedContractsAxiom (spec : FuncSpec) :
    spec.trusted = true →
    ∀ (preEs postEs : ExecState),
      evalC preEs preEs none spec.pre →
      evalC postEs preEs none spec.post
```

**What it says.**  Any function marked `\trusted` satisfies its declared contract
whenever its precondition holds.

**Why the conditional form is already an improvement.**  A wrong `\trusted` spec
causes unsoundness only for callers that actually establish the precondition.

**What remains.**  Task 4 added the `reviewer` field and the three existing
annotations now carry a named reviewer.  The next step is to require each `\trusted`
function to be accompanied by either a Lean 4 proof (for pure-Lean models) or a
documented human argument in the commit that introduced the annotation.  This is a
process change, not a code change.

---

## Summary table

| Axiom | Scope | Status | Risk today | Next step | Effort |
|---|---|---|---|---|---|
| `why3WpSound` | Path A only | ✅ deleted | — | — | done |
| `why3ImplementsWpW` | Path B call sites | narrowed to `Why3Certificate` | Medium — stub checker | Implement `Why3Trust.check` (Task 5) | Medium |
| `altErgoCorrect` | All SMT goals | narrowed to `SmtCertificate` | High — stub checker | Use `omega` for arithmetic (Task 7) | Medium–High |
| `trustedContractsAxiom` | `\trusted` functions | reviewer field added | Low — conditional, scoped | Per-function proof or named reviewer | Process |
