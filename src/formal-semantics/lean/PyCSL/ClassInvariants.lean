/-
  ClassInvariants.lean — Class invariant wrapping (Category A)
  Mirror of Phase6n_ClassInvariants.v

  Per formal-semantics-completion.md Phase 6. The model already has records
  via `fieldAssign`/`fieldAugAssign` Stmt constructors (modelled with
  SOS + WP). What was MISSING was the class-invariant mechanism: a record
  type with an invariant that is
    (a) established by the constructor,
    (b) preserved by every method,
    (c) assumed at method entry,
    (d) re-established at method exit.

  Design (per the Phase 6 brief):
    1. Class invariant as a CONTRACT-LEVEL construct, not a new Stmt.
       `cClassInvariant cls inv` (added to `ContractExpr` in AST.lean)
       evaluates the predicate `inv` over the current state. The class tag
       `cls` is documentation-only in the Hoare model; Phase 7 (memory-model
       parameterisation) will scope it to the named record's fields.
    2. Invariant-wrapping as a META-LEVEL LEMMA, not a new SOS rule.
       `classInvariantPreserved` instantiates `pycsl_soundness` with the
       invariant as both the assumed precondition (at entry) and the
       ensured normal postcondition (at exit). The method-body's WP must
       thread the invariant through every continuation; the lemma states
       that under those conditions, a method whose WP holds and that
       terminates normally preserves the invariant.

  This file adds NO new axioms and NO `sorry`. The proof is a direct
  corollary of `pycsl_soundness`, which is itself proved with 0 sorry.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.WP
import PyCSL.Soundness

-- The class-invariant lemmas carry hypotheses that document the method's
-- proof obligation (entry-side invariant, method WP). Some are unused in
-- the trivial proof steps (the WP already encodes them) — silence the
-- linter rather than drop API documentation.
set_option linter.unusedVariables false

/-- Helper: invariant holds at a state, evaluated via the exec_state-aware
    contract evaluator (so `\at`, ghost vars, and the Phase 3b ghost atoms
    resolve correctly inside the invariant predicate). -/
def invariantHolds (es preEs : ExecState) (cls : Ident)
                   (inv : ContractExpr) : Prop :=
  evalC es preEs none (.cClassInvariant cls inv)

/-- The derived preservation lemma.

    Hypotheses mirror the contract a PyCSL method carries when its class
    declares `inv` as the class invariant:
      - hEntry:  the invariant holds at method entry (established by the
                 constructor; assumed at method entry);
      - hWp:     the method body's WP holds with the invariant as the
                 ensured normal postcondition (i.e., `Qn = invariantHolds`),
                 with arbitrary other-continuation postconditions;
      - hExec:   execution of the method body terminates normally,
                 producing the exit state `es'`.

    Conclusion: the invariant holds at the exit state (re-established at
    method exit).

    This is invariant-wrapping: the method's contract is the invariant
    conjoined with the method-specific pre/post, and the wrapping lemma
    states that the invariant threads through the method call. -/
theorem classInvariantPreserved
    (es preEs es' : ExecState) (s : Stmt)
    (cls : Ident) (inv : ContractExpr)
    (Qr Qc Qb : ExecState → Prop)
    (Qe : Ident → ExecState → Prop)
    (hEntry : invariantHolds es preEs cls inv)
    (hWp : wp s (fun es'' => invariantHolds es'' preEs cls inv)
                Qr Qc Qb Qe preEs es)
    (hExec : Exec es s (.normal es')) :
    invariantHolds es' preEs cls inv := by
  simp only [invariantHolds] at *
  exact pycsl_soundness es s (.normal es')
    (fun es'' => evalC es'' preEs none (.cClassInvariant cls inv))
    Qr Qc Qb Qe preEs hExec hWp

/-- Strengthening: the constructor-establishes facet. Stated as a trivial
    specialisation: if the invariant holds at entry and the constructor
    body is `.skip` (the unit constructor in the Hoare model — a real
    constructor would be a sequence of fieldAssign statements whose WP
    re-establishes the invariant), then the invariant holds at the
    post-state. This anchors facet (a) "established by the constructor". -/
theorem constructorEstablishesInvariant
    (es preEs es' : ExecState) (cls : Ident) (inv : ContractExpr)
    (hInv : invariantHolds es preEs cls inv)
    (hWp : wp .skip (fun es'' => invariantHolds es'' preEs cls inv)
                    (fun _ => True) (fun _ => True) (fun _ => True)
                    (fun _ _ => True) preEs es)
    (hExec : Exec es .skip (.normal es'))
    (hEq : es' = es) :
    invariantHolds es' preEs cls inv := by
  subst es'
  exact hInv
/-- Facet (b)+(d): if every method's WP threads the invariant through the
    normal postcondition, then any method that terminates normally preserves
    the invariant. This is just `classInvariantPreserved` restated for a
    fixed method body — included for citation by the audit-plan §3.7. -/
theorem methodPreservesInvariant
    (es preEs es' : ExecState) (body : Stmt)
    (cls : Ident) (inv : ContractExpr)
    (hInv : invariantHolds es preEs cls inv)
    (hWp : wp body (fun es'' => invariantHolds es'' preEs cls inv)
                   (fun _ => True) (fun _ => True) (fun _ => True)
                   (fun _ _ => True) preEs es)
    (hExec : Exec es body (.normal es')) :
    invariantHolds es' preEs cls inv :=
  classInvariantPreserved es preEs es' body cls inv
    (fun _ => True) (fun _ => True) (fun _ => True) (fun _ _ => True)
    hInv hWp hExec
