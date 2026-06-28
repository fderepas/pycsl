(* Tests.v — Concrete evaluation tests for the PyCSL formalization
   Updated for exec_state-based exec (Phase 3a). *)

Require Import ZArith String List Bool.
Require Import Lia.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Require Import Phase3b_Desugar.
Require Import Phase4_WP.
Require Import Phase5a_WhileInv.
Require Import Phase5b_Soundness.
Require Import Phase7_MemModel.
Require Import Phase6n_ClassInvariants.
Open Scope Z_scope.

Definition es_empty : exec_state := mk_exec_state nil.

(* ===== Test 1: Assign x = 42 ===== *)
Lemma test_assign :
  exec es_empty (SAssign "x" (EInt 42))
    (ONormal (set_reg es_empty (update nil "x" (VInt 42)))).
Proof. apply ExecAssign. Qed.

(* ===== Test 2: Sequential assignment x=1; y=2 ===== *)
Lemma test_seq_assign :
  let st1 := update nil "x" (VInt 1) in
  let es1  := set_reg es_empty st1 in
  exec es_empty
    (SSeq (SAssign "x" (EInt 1)) (SAssign "y" (EInt 2)))
    (ONormal (set_reg es1 (update st1 "y" (VInt 2)))).
Proof. eapply ExecSeq; apply ExecAssign. Qed.

(* ===== Test 3: If-then-else with true condition ===== *)
Lemma test_if_true :
  forall es,
  eval_bool es.(reg_state) (EInt 1) = true ->
  exec es (SIf (EInt 1) (SAssign "x" (EInt 10)) (SAssign "x" (EInt 20)))
    (ONormal (set_reg es (update es.(reg_state) "x" (VInt 10)))).
Proof. intros. apply ExecIfTrue; auto. apply ExecAssign. Qed.

(* ===== Test 4: Skip is identity ===== *)
Lemma test_skip : forall es, exec es SSkip (ONormal es).
Proof. apply ExecSkip. Qed.

(* ===== Test 5: Return produces OReturned with \result bound ===== *)
Lemma test_return :
  exec es_empty (SReturn (EInt 7))
    (OReturned
       (set_reg es_empty (update nil "\result" (VInt 7)))
       (VInt 7)).
Proof. apply ExecReturn. Qed.

(* ===== Test 6: Continue produces OContinued ===== *)
Lemma test_continue : forall es, exec es SContinue (OContinued es).
Proof. apply ExecContinue. Qed.

(* ===== Test 7: Break produces OBroke ===== *)
Lemma test_break : forall es, exec es SBreak (OBroke es).
Proof. apply ExecBreak. Qed.

(* ===== Test 8: WP for Skip is identity ===== *)
Lemma test_wp_skip :
  forall es Qn Qr Qc Qb Qe pre_es,
  wp SSkip Qn Qr Qc Qb Qe pre_es es <-> Qn es.
Proof. simpl. tauto. Qed.

(* ===== Test 9: WP for Assign substitutes ===== *)
Lemma test_wp_assign :
  forall es Qr Qc Qb Qe pre_es,
  wp (SAssign "x" (EInt 42))
     (fun es' => lookup es'.(reg_state) "x" = Some (VInt 42))
     Qr Qc Qb Qe pre_es es.
Proof.
  intros. simpl. unfold update, lookup. simpl. reflexivity.
Qed.

(* ===== Test 10: Soundness applied to Skip ===== *)
Lemma test_soundness_skip :
  forall es (P : exec_state -> Prop),
  P es ->
  exec es SSkip (ONormal es) ->
  P es.
Proof.
  intros es P HP Hexec.
  exact (pycsl_soundness es SSkip (ONormal es)
           P (fun _ => True) (fun _ => True) (fun _ => True)
           (fun _ _ => True) es Hexec HP).
Qed.

(* ===== Test 11: Soundness applied to Assign ===== *)
Lemma test_soundness_assign :
  forall es,
  exec es (SAssign "x" (EInt 5))
    (ONormal (set_reg es (update es.(reg_state) "x" (VInt 5)))) ->
  lookup (set_reg es (update es.(reg_state) "x" (VInt 5))).(reg_state) "x"
    = Some (VInt 5).
Proof.
  intros es Hexec.
  apply (pycsl_soundness es (SAssign "x" (EInt 5))
           (ONormal (set_reg es (update es.(reg_state) "x" (VInt 5))))
           (fun es' => lookup es'.(reg_state) "x" = Some (VInt 5))
           (fun _ => True) (fun _ => True) (fun _ => True)
           (fun _ _ => True) es Hexec).
  simpl. unfold update, lookup. simpl. reflexivity.
Qed.

(* ===== Test 12: Augmented assign ===== *)
Lemma test_aug_assign :
  let st  := (("x", VInt 10) :: nil) in
  let es  := mk_exec_state st in
  exec es (SAugAssign "x" OpAdd (EInt 5))
    (ONormal (set_reg es (update st "x" (VInt 15)))).
Proof. apply ExecAugAssign. Qed.

(* ===== Test 13: Assert passes when condition holds ===== *)
Lemma test_assert_pass :
  forall es,
  eval_contract es.(reg_state) es.(reg_state) None (CInt 1) ->
  exec es (SAssert (CInt 1) "unreachable") (ONormal es).
Proof. intros. apply ExecAssertPass. simpl. lia. Qed.

(* ===== Test 14: Ghost declaration updates ghost state ===== *)
Lemma test_ghost_decl :
  exec es_empty (SGhostDecl "g" GTInt (CInt 0))
    (ONormal (set_ghost es_empty
               (ghost_update es_empty.(ghost_st) "g" (GVInt 0)))).
Proof. apply ExecGhostDecl. Qed.

(* ===== Test 15: Label records ghost snapshot ===== *)
Lemma test_label :
  exec es_empty (SLabel "PRE")
    (ONormal (set_labels es_empty (("PRE", es_empty.(ghost_st)) :: nil))).
Proof. apply ExecLabel. Qed.

(* ===== Test 16: walrus_assign is identical to SAssign ===== *)
Lemma test_walrus_assign_exec :
  exec es_empty (walrus_assign "x" (EInt 7))
    (ONormal (set_reg es_empty (update nil "x" (VInt 7)))).
Proof. unfold walrus_assign. apply ExecAssign. Qed.

(* ===== Test 17: desugar_match single hit ===== *)
Lemma test_match_hit :
  let st := update nil "v" (VInt 42) in
  let es := mk_exec_state st in
  exec es
    (desugar_match (EVar "v") ((42, SAssign "r" (EInt 1)) :: nil) (SAssign "r" (EInt 0)))
    (ONormal (set_reg es (update st "r" (VInt 1)))).
Proof.
  apply exec_desugar_match_single_hit.
  - simpl. unfold update, lookup. simpl. reflexivity.
  - apply ExecAssign.
Qed.

(* ===== Test 18: Exception — raise and catch ===== *)
Lemma test_raise_catch :
  exec es_empty
    (STryCatch (SRaise "ValueError") "ValueError" (SAssign "x" (EInt 0)))
    (ONormal (set_reg es_empty (update nil "x" (VInt 0)))).
Proof.
  eapply ExecTryCatchCaught.
  - apply ExecRaise.
  - apply ExecAssign.
Qed.

(* ===== Test 19: Phase 1 CBoolLit evaluation ===== *)
Lemma test_boollit_true :
  eval_contract nil nil None (CBoolLit true).
Proof. simpl. reflexivity. Qed.

Lemma test_boollit_false :
  ~ eval_contract nil nil None (CBoolLit false).
Proof. simpl. discriminate. Qed.

(* ===== Test 20: Phase 1 CIsSorted evaluation ===== *)
Lemma test_is_sorted_empty :
  forall st,
  eval_contract st st None (CIsSorted "a" (CInt 0) (CInt 0)).
Proof.
  intros. simpl. destruct (lookup st "a") as [|v]; [|exact I]; destruct v; simpl; exact I.
Qed.

(* ===== Test 21: Phase 4 CValid is vacuously true (Hoare stub) ===== *)
Lemma test_cvalid_hoare_stub :
  forall st, eval_contract st st None (CValid (CVar "p") (CInt 10)).
Proof. intros. simpl. exact I. Qed.

(* ===== Test 22: Phase 4 CSeparated is vacuously true (Hoare stub) ===== *)
Lemma test_cseparated_hoare_stub :
  forall st, eval_contract st st None (CSeparated (CVar "a") (CVar "b")).
Proof. intros. simpl. exact I. Qed.

(* ===== Test 23: Phase 4 CLength2d returns array length (flat model) ===== *)
Lemma test_clength2d_flat :
  forall st a,
  lookup st "arr" = Some (VArray a) ->
  eval_z st st None (CLength2d "arr") = Z.of_nat (List.length a).
Proof.
  intros st a H. simpl. rewrite H. reflexivity.
Qed.

(* ===== Test 24: Phase 4 CValid2d is vacuously true (Hoare stub) ===== *)
Lemma test_cvalid2d_hoare_stub :
  forall st, eval_contract st st None (CValid2d (CVar "p") (CInt 3) (CInt 4)).
Proof. intros. simpl. exact I. Qed.

(* ===== Test 25: Phase 6 CClassInvariant evaluates its predicate ===== *)
Lemma test_class_invariant_evaluates :
  forall st cls inv,
    eval_contract st st None (CClassInvariant cls inv) <->
    eval_contract st st None inv.
Proof. intros. simpl. reflexivity. Qed.

(* ===== Test 26: Phase 6 invariant holds at entry ⟹ holds at exit (skip body) ===== *)
(* The simplest preservation case: a method whose body is SSkip preserves
   the invariant trivially, since the exit state equals the entry state. *)
Lemma test_class_invariant_preserved_skip :
  forall es cls inv,
    invariant_holds es es cls inv ->
    exec es SSkip (ONormal es) ->
    invariant_holds es es cls inv.
Proof.
  intros es cls inv Hinv Hexec.
  apply (class_invariant_preserved es es es SSkip cls inv
           (fun _ => True) (fun _ => True) (fun _ => True)
           (fun _ _ => True) Hinv).
  - simpl. exact Hinv.
  - exact Hexec.
Qed.

(* ===== Test 27: Phase 6 invariant preservation via method_preserves_invariant ===== *)
(* Same shape as Test 26 but routed through the method-body specialisation. *)
Lemma test_method_preserves_invariant_skip :
  forall es cls inv,
    invariant_holds es es cls inv ->
    wp SSkip (fun es' => invariant_holds es' es cls inv)
            (fun _ => True) (fun _ => True) (fun _ => True)
            (fun _ _ => True) es es ->
    exec es SSkip (ONormal es) ->
    invariant_holds es es cls inv.
Proof.
  intros es cls inv Hinv Hwp Hexec.
  apply (method_preserves_invariant es es es SSkip cls inv Hinv Hwp Hexec).
Qed.

(* ===== Test 28: Phase 6 CClassInvariant with CBoolLit true holds ===== *)
Lemma test_class_invariant_boollit_true (st : state) :
  eval_contract st st None (CClassInvariant "Counter" (CBoolLit true)).
Proof. simpl. reflexivity. Qed.

(* ===== Test 29: Phase 6 CClassInvariant with CBoolLit false does not hold ===== *)
Lemma test_class_invariant_boollit_false (st : state) :
  ~ eval_contract st st None (CClassInvariant "Counter" (CBoolLit false)).
Proof. simpl. discriminate. Qed.

(* ===== Phase 7 tests: acquires/releases, critical_havoc, MemModel ===== *)

(* Test 30: acquires produces ONormal in the Hoare instance. *)
Lemma test_acquires_normal :
  forall es m, exec es (SAcquires m) (ONormal es).
Proof. intros. apply ExecAcquires. Qed.

(* Test 31: releases produces ONormal in the Hoare instance. *)
Lemma test_releases_normal :
  forall es m, exec es (SReleases m) (ONormal es).
Proof. intros. apply ExecReleases. Qed.

(* Test 32: wp (SAcquires m) Qn ... = Qn es (Hoare-instance identity). *)
Lemma test_wp_acquires :
  forall es m (Qn : exec_state -> Prop),
  wp (SAcquires m) Qn (fun _ => True) (fun _ => True) (fun _ => True)
      (fun _ _ => True) es es = Qn es.
Proof. intros. simpl. reflexivity. Qed.

(* Test 33: wp (SReleases m) Qn ... = Qn es (Hoare-instance identity). *)
Lemma test_wp_releases :
  forall es m (Qn : exec_state -> Prop),
  wp (SReleases m) Qn (fun _ => True) (fun _ => True) (fun _ => True)
      (fun _ _ => True) es es = Qn es.
Proof. intros. simpl. reflexivity. Qed.

(* Test 34: critical_havoc is identity in the Hoare instance. *)
Lemma test_critical_havoc_identity :
  forall es (P : exec_state -> Prop),
  critical_havoc es P = P es.
Proof. intros. reflexivity. Qed.

(* Test 35: Hoare instance valid is vacuously True. *)
Lemma test_valid_true : valid 0 10.
Proof. exact I. Qed.

(* Test 36: Hoare instance separated is vacuously True. *)
Lemma test_separated_true : separated 0 10.
Proof. exact I. Qed.

(* Test 37: soundness holds for SAcquires (Qn case). *)
Lemma test_soundness_acquires :
  forall es m Qn Qr Qc Qb Qe pre_es,
  exec es (SAcquires m) (ONormal es) ->
  wp (SAcquires m) Qn Qr Qc Qb Qe pre_es es ->
  outcome_post Qn Qr Qc Qb Qe (ONormal es).
Proof.
  intros es m Qn Qr Qc Qb Qe pre_es Hexec Hwp.
  eapply pycsl_soundness; eauto.
Qed.

(* ===== Phase 8 tests: Lambda / SCall ===== *)

(* Test 38: VClosure value is constructible. (ELambda expression is
   not in the AST — see Phase 8 gap doc in Phase1_AST.v. Closures
   are constructed directly at the value level.) *)
Lemma test_vclosure_constructible :
  forall st param body,
  VClosure param body (st : list (ident * val)) = VClosure param body st.
Proof. intros. reflexivity. Qed.

(* Test 39: ExecCall: SCall with a VClosure value (directly constructed)
   produces ONormal with result -> 42.

   Body: SReturn (EInt 42). Closure captured state: the caller's state.
   Call: SCall "r" fn (EInt 99) where fn evaluates to VClosure "x" (SReturn (EInt 42)) st.
   Expected outcome: ONormal (set_reg es (update es.reg_state "r" (VInt 42))). *)
Lemma test_exec_call_return :
  forall es st,
  eval_expr es.(reg_state) (EVar "f") = VClosure "x" (SReturn (EInt 42)) st ->
  exec (set_reg (mk_exec_state st)
                (update st "x" (eval_expr es.(reg_state) (EInt 99))))
       (SReturn (EInt 42))
       (OReturned
          (set_reg (mk_exec_state st)
                   (update st "\result" (VInt 42)))
          (VInt 42)) ->
  exec es (SCall "r" (EVar "f") (EInt 99))
       (ONormal (set_reg es (update es.(reg_state) "r" (VInt 42)))).
Proof.
  intros es st Heval Hret.
  eapply ExecCall.
  - exact Heval.
  - exact Hret.
Qed.

(* Test 40: wp (SCall r fn arg) is True when fn is not a VClosure. *)
Lemma test_wp_call_non_closure :
  forall es r fn arg Qn Qr Qc Qb Qe pre_es,
  eval_expr es.(reg_state) fn = VInt 0 ->
  wp (SCall r fn arg) Qn Qr Qc Qb Qe pre_es es = True.
Proof. intros. simpl. rewrite H. reflexivity. Qed.

(* Test 41: returned_state_has_result — ExecReturn sets \result.
   (Skipped: returned_state_has_result is Admitted in Phase 8. See gap doc.) *)
