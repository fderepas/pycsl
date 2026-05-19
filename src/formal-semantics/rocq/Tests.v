(* Tests.v — Concrete evaluation tests for the PyCSL formalization *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Require Import Phase3b_Desugar.
Require Import Phase4_WP.
Require Import Phase5a_WhileInv.
Require Import Phase5b_Soundness.
Open Scope Z_scope.

Definition st_empty : state := nil.

(* ===== Test 1: Assign x = 42 ===== *)
Lemma test_assign :
  exec st_empty (SAssign "x" (EInt 42))
    (ONormal (update st_empty "x" (VInt 42))).
Proof. apply ExecAssign. Qed.

(* ===== Test 2: Sequential assignment x=1; y=2 ===== *)
Lemma test_seq_assign :
  exec st_empty
    (SSeq (SAssign "x" (EInt 1)) (SAssign "y" (EInt 2)))
    (ONormal (update (update st_empty "x" (VInt 1)) "y" (VInt 2))).
Proof. eapply ExecSeq; apply ExecAssign. Qed.

(* ===== Test 3: If-then-else with true condition ===== *)
Lemma test_if_true :
  forall st,
  eval_bool st (EInt 1) = true ->
  exec st (SIf (EInt 1) (SAssign "x" (EInt 10)) (SAssign "x" (EInt 20)))
    (ONormal (update st "x" (VInt 10))).
Proof. intros. apply ExecIfTrue; auto. apply ExecAssign. Qed.

(* ===== Test 4: Skip is identity ===== *)
Lemma test_skip : forall st, exec st SSkip (ONormal st).
Proof. apply ExecSkip. Qed.

(* ===== Test 5: Return produces OReturned with \result bound ===== *)
Lemma test_return :
  exec st_empty (SReturn (EInt 7))
    (OReturned (update st_empty "\result" (VInt 7)) (VInt 7)).
Proof. apply ExecReturn. Qed.

(* ===== Test 6: Continue produces OContinued ===== *)
Lemma test_continue : forall st, exec st SContinue (OContinued st).
Proof. apply ExecContinue. Qed.

(* ===== Test 7: WP for Skip is identity ===== *)
Lemma test_wp_skip :
  forall st Qn Qr Qc pre_st,
  wp SSkip Qn Qr Qc pre_st st <-> Qn st.
Proof. simpl. tauto. Qed.

(* ===== Test 8: WP for Assign substitutes ===== *)
Lemma test_wp_assign :
  forall st Qr Qc pre_st,
  wp (SAssign "x" (EInt 42)) (fun st' => lookup st' "x" = Some (VInt 42))
     Qr Qc pre_st st.
Proof.
  intros. simpl. unfold update, lookup. simpl. reflexivity.
Qed.

(* ===== Test 9: Soundness applied to Skip ===== *)
Lemma test_soundness_skip :
  forall st (P : state -> Prop),
  P st ->
  exec st SSkip (ONormal st) ->
  P st.
Proof.
  intros st P HP Hexec.
  exact (pycsl_soundness st SSkip (ONormal st) P (fun _ => True) (fun _ => True)
           st Hexec HP).
Qed.

(* ===== Test 10: Soundness applied to Assign ===== *)
Lemma test_soundness_assign :
  forall st,
  exec st (SAssign "x" (EInt 5))
    (ONormal (update st "x" (VInt 5))) ->
  lookup (update st "x" (VInt 5)) "x" = Some (VInt 5).
Proof.
  intros st Hexec.
  apply (pycsl_soundness st (SAssign "x" (EInt 5))
           (ONormal (update st "x" (VInt 5)))
           (fun st' => lookup st' "x" = Some (VInt 5))
           (fun _ => True) (fun _ => True) st Hexec).
  simpl. unfold update, lookup. simpl. reflexivity.
Qed.

(* ===== Test 11: Augmented assign ===== *)
Lemma test_aug_assign :
  let st := (("x", VInt 10) :: nil) in
  exec st (SAugAssign "x" OpAdd (EInt 5))
    (ONormal (update st "x" (VInt 15))).
Proof. apply ExecAugAssign. Qed.

(* ===== Test 12: exec_deterministic ===== *)
Lemma test_deterministic :
  forall st out1 out2,
  exec st (SAssign "x" (EInt 1)) out1 ->
  exec st (SAssign "x" (EInt 1)) out2 ->
  out1 = out2.
Proof. intros. eapply exec_deterministic; eauto. Qed.

(* ===== Test 13: while_not_continued ===== *)
Lemma test_while_not_continued :
  forall st inv var cond body out,
  exec st (SWhile inv var cond body) out ->
  match out with OContinued _ => False | _ => True end.
Proof. intros. eapply while_not_continued; eauto. Qed.
