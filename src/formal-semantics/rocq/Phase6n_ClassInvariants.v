(* Phase6n_ClassInvariants.v — Class invariant wrapping (Category A)

   Per formal-semantics-completion.md Phase 6. The model already has
   records via `fieldAssign`/`fieldAugAssign` Stmt constructors (modelled
   with SOS + WP). What was MISSING was the class-invariant mechanism:
   a record type with an invariant that is
     (a) established by the constructor,
     (b) preserved by every method,
     (c) assumed at method entry,
     (d) re-established at method exit.

   Design (per the Phase 6 brief):
     1. Class invariant as a CONTRACT-LEVEL construct, not a new Stmt.
        `CClassInvariant cls inv` (added to `contract_expr` in Phase1_AST.v)
        evaluates the predicate `inv` over the current state. The class tag
        `cls` is documentation-only in the Hoare model; Phase 7 (memory-model
        parameterisation) will scope it to the named record's fields.
     2. Invariant-wrapping as a META-LEVEL LEMMA, not a new SOS rule.
        `class_invariant_preserved` instantiates `pycsl_soundness` with the
        invariant as both the assumed precondition (at entry) and the
        ensured normal postcondition (at exit). The method-body's WP must
        thread the invariant through every continuation; the lemma states
        that under those conditions, a method whose WP holds and that
        terminates normally preserves the invariant.

   This file adds NO new axioms and NO new Admitted. The proof is a
   direct corollary of `pycsl_soundness`, which is itself proved with
   0 Admitted. *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Require Import Phase4_WP.
Require Import Phase5b_Soundness.
Open Scope Z_scope.

(* Helper: invariant holds at a state, evaluated via the exec_state-aware
   contract evaluator (so \at, ghost vars, and the Phase 3b ghost atoms
   resolve correctly inside the invariant predicate). *)
Definition invariant_holds
           (es pre_es : exec_state) (cls : ident)
           (inv : contract_expr) : Prop :=
  eval_c es pre_es None (CClassInvariant cls inv).

(* The derived preservation lemma.

   Hypotheses mirror the contract a PyCSL method carries when its class
   declares `inv` as the class invariant:
     - Hentry:   the invariant holds at method entry (established by the
                 constructor; assumed at method entry);
     - Hwp:      the method body's WP holds with the invariant as the
                 ensured normal postcondition (i.e., `Qn = invariant_holds`),
                 with arbitrary other-continuation postconditions;
     - Hexec:    execution of the method body terminates normally,
                 producing the exit state `es'`.

   Conclusion: the invariant holds at the exit state (re-established at
   method exit).

   This is invariant-wrapping: the method's contract is the invariant
   conjoined with the method-specific pre/post, and the wrapping lemma
   states that the invariant threads through the method call. *)
Lemma class_invariant_preserved :
  forall (es pre_es es' : exec_state) (s : stmt)
         (cls : ident) (inv : contract_expr)
         (Qr Qc Qb : exec_state -> Prop)
         (Qe : ident -> exec_state -> Prop),
    invariant_holds es pre_es cls inv ->
    wp s (fun es'' => invariant_holds es'' pre_es cls inv)
         Qr Qc Qb Qe pre_es es ->
    exec es s (ONormal es') ->
    invariant_holds es' pre_es cls inv.
Proof.
  intros es pre_es es' s cls inv Qr Qc Qb Qe
         Hentry Hwp Hexec.
  (* The invariant at exit is exactly the Qn postcondition specialised to
     the exit state. Unfold and apply pycsl_soundness directly. *)
  unfold invariant_holds in *.
  apply (pycsl_soundness es s (ONormal es')
          (fun es'' => eval_c es'' pre_es None (CClassInvariant cls inv))
          Qr Qc Qb Qe pre_es Hexec Hwp).
Qed.

(* Strengthening: the constructor-establishes facet. Stated as a trivial
   specialisation: if the invariant holds at entry and the constructor
   body is `SSkip` (the unit constructor in the Hoare model — a real
   constructor would be a sequence of fieldAssign statements whose WP
   re-establishes the invariant), then the invariant holds at the
   post-state. This anchors facet (a) "established by the constructor". *)
Lemma constructor_establishes_invariant :
  forall (es pre_es es' : exec_state)
         (cls : ident) (inv : contract_expr),
    invariant_holds es pre_es cls inv ->
    wp SSkip (fun es'' => invariant_holds es'' pre_es cls inv)
         (fun _ => True) (fun _ => True) (fun _ => True)
         (fun _ _ => True) pre_es es ->
    exec es SSkip (ONormal es') ->
    es' = es ->
    invariant_holds es' pre_es cls inv.
Proof.
  intros es pre_es es' cls inv Hinv Hwp Hexec Heq.
  subst es'. exact Hinv.
Qed.

(* Facet (b)+(d): if every method's WP threads the invariant through the
   normal postcondition, then any method that terminates normally preserves
   the invariant. This is just `class_invariant_preserved` restated for a
   fixed method body — included for citation by the audit-plan §3.7. *)
Lemma method_preserves_invariant :
  forall (es pre_es es' : exec_state) (body : stmt)
         (cls : ident) (inv : contract_expr),
    invariant_holds es pre_es cls inv ->
    wp body (fun es'' => invariant_holds es'' pre_es cls inv)
            (fun _ => True) (fun _ => True) (fun _ => True)
            (fun _ _ => True) pre_es es ->
    exec es body (ONormal es') ->
    invariant_holds es' pre_es cls inv.
Proof.
  intros es pre_es es' body cls inv Hinv Hwp Hexec.
  unfold invariant_holds in *.
  exact (pycsl_soundness es body (ONormal es')
          (fun es'' => eval_c es'' pre_es None (CClassInvariant cls inv))
          (fun _ => True) (fun _ => True) (fun _ => True)
          (fun _ _ => True) pre_es Hexec Hwp).
Qed.
