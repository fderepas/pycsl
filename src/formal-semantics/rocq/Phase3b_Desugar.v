(* Phase3b_Desugar.v — Desugaring correctness theorem + Phase 1a lemmas *)

Require Import ZArith String List Bool.
Require Import Lia.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3b_DesugarDef.
Require Import Phase3_SOS.
Open Scope Z_scope.
Open Scope string_scope.

(* ===================================================================== *)
(* Key design: ExecFor (Phase3_SOS.v) is defined as                      *)
(*   exec st (desugar (SFor x arr inv var body)) out →                   *)
(*   exec st (SFor x arr inv var body) out.                              *)
(* So the SFor case of desugar_correct is definitionally trivial.        *)
(* SWhile needs inner induction on the exec derivation depth.            *)
(* ===================================================================== *)

(* SWhile backward helper: given IH for body, prove SWhile(desugar body) → SWhile body.
   Strategy: remember the concrete while stmt as a free variable s, then use
   induction on the exec derivation with s as a free index. Non-while cases are
   closed by discriminate; while cases use injection to recover the components. *)
Lemma while_bwd_desugar :
  forall body inv var cond,
  (forall st out, fresh_in_stmt for_idx body ->
   exec st (desugar body) out -> exec st body out) ->
  forall st out,
  fresh_in_stmt for_idx body ->
  exec st (SWhile inv var cond (desugar body)) out ->
  exec st (SWhile inv var cond body) out.
Proof.
  intros body inv var cond IHbody st out Hfresh Hw.
  remember (SWhile inv var cond (desugar body)) as s eqn:Hs.
  revert inv var cond body IHbody Hfresh Hs.
  induction Hw; intros inv' var' cond' body' IHbody' Hfresh' Hs;
    try discriminate Hs.
  - (* ExecWhileTrue *)
    injection Hs as Hinv Hvar Hcond Hbody. subst.
    eapply ExecWhileTrue; [eassumption| |].
    + apply IHbody'; eassumption.
    + eapply IHHw2; eassumption || reflexivity.
  - (* ExecWhileContinue *)
    injection Hs as Hinv Hvar Hcond Hbody. subst.
    eapply ExecWhileContinue; [eassumption| |].
    + apply IHbody'; eassumption.
    + eapply IHHw2; eassumption || reflexivity.
  - (* ExecWhileFalse *)
    injection Hs as Hinv Hvar Hcond Hbody. subst.
    apply ExecWhileFalse; assumption.
Qed.

(* Forward: exec st s out → exec st (desugar s) out.
   By induction on the exec derivation. *)
Lemma desugar_correct_fwd : forall st s out,
  fresh_in_stmt for_idx s ->
  exec st s out -> exec st (desugar s) out.
Proof.
  intros st s out Hfresh H.
  revert Hfresh.
  induction H; intro Hfresh.
  - constructor.  (* ExecSkip *)
  - constructor.  (* ExecAssign *)
  - constructor.  (* ExecAugAssign *)
  - constructor.  (* ExecArraySet *)
  - simpl. destruct Hfresh as [Hf1 Hf2]. eapply ExecSeq; eauto.  (* ExecSeq *)
  - simpl. destruct Hfresh as [Hf1 Hf2]. apply ExecSeqReturn; eauto.  (* ExecSeqReturn *)
  - simpl. destruct Hfresh as [Hf1 Hf2]. apply ExecSeqContinue; eauto.  (* ExecSeqContinue *)
  - simpl. destruct Hfresh as [Hf1 Hf2]. apply ExecIfTrue; eauto.  (* ExecIfTrue *)
  - simpl. destruct Hfresh as [Hf1 Hf2]. apply ExecIfFalse; eauto.  (* ExecIfFalse *)
  - simpl. eapply ExecWhileTrue; eauto.  (* ExecWhileTrue *)
  - simpl. eapply ExecWhileContinue; eauto.  (* ExecWhileContinue *)
  - simpl. apply ExecWhileFalse; assumption.  (* ExecWhileFalse *)
  - simpl; constructor.  (* ExecContinue *)
  - simpl; constructor.  (* ExecReturn *)
  - assumption.  (* ExecFor: premise IS exec st (desugar (SFor ...)) out *)
Qed.

(* Backward: exec st (desugar s) out → exec st s out. *)
Lemma desugar_correct_bwd : forall s st out,
  fresh_in_stmt for_idx s ->
  exec st (desugar s) out -> exec st s out.
Proof.
  induction s; intros st out Hfresh Hd; simpl in Hd.
  - exact Hd.  (* SSkip *)
  - exact Hd.  (* SAssign *)
  - exact Hd.  (* SAugAssign *)
  - exact Hd.  (* SArraySet *)
  - destruct Hfresh as [Hf1 Hf2].  (* SSeq *)
    inversion Hd; subst; [econstructor|apply ExecSeqReturn|apply ExecSeqContinue];
    [apply IHs1|apply IHs2|apply IHs1|apply IHs1]; eassumption.
  - destruct Hfresh as [Hf1 Hf2].  (* SIf *)
    inversion Hd; subst;
    [apply ExecIfTrue; [assumption|apply IHs1;eassumption] |
     apply ExecIfFalse; [assumption|apply IHs2;eassumption]].
  - apply (while_bwd_desugar s inv var cond (IHs) st out Hfresh Hd).  (* SWhile *)
  - apply ExecFor; exact Hd.  (* SFor *)
  - exact Hd.  (* SReturn *)
  - exact Hd.  (* SContinue *)
Qed.

Theorem desugar_correct : forall st s out,
  fresh_in_stmt for_idx s ->
  exec st s out <-> exec st (desugar s) out.
Proof.
  intros st s out Hfresh. split.
  - exact (desugar_correct_fwd st s out Hfresh).
  - exact (desugar_correct_bwd s st out Hfresh).
Qed.

(* ===================================================================== *)
(* Phase 1a — Category B desugaring functions and correctness lemmas     *)
(* ===================================================================== *)

Definition walrus_assign (x : ident) (e : expr) : stmt := SAssign x e.

Lemma walrus_assign_eq : forall x e, walrus_assign x e = SAssign x e.
Proof. reflexivity. Qed.

Lemma exec_walrus_assign : forall st x e out,
  exec st (walrus_assign x e) out <-> exec st (SAssign x e) out.
Proof. intros. unfold walrus_assign. tauto. Qed.

Definition tuple_unpack2 (arr x y : ident) : stmt :=
  SSeq (SAssign x (ESubscript arr (EInt 0)))
       (SAssign y (ESubscript arr (EInt 1))).

Lemma tuple_unpack2_eq : forall arr x y,
  tuple_unpack2 arr x y =
  SSeq (SAssign x (ESubscript arr (EInt 0)))
       (SAssign y (ESubscript arr (EInt 1))).
Proof. reflexivity. Qed.

Lemma exec_tuple_unpack2_normal : forall st arr x y,
  let st1 := update st x (eval_expr st (ESubscript arr (EInt 0))) in
  exec st (tuple_unpack2 arr x y)
    (ONormal (update st1 y (eval_expr st1 (ESubscript arr (EInt 1))))).
Proof.
  intros. unfold tuple_unpack2. eapply ExecSeq; apply ExecAssign.
Qed.

Fixpoint desugar_match (scrutinee : expr) (cases : list (Z * stmt))
                       (default : stmt) : stmt :=
  match cases with
  | nil => default
  | (n, body) :: rest =>
      SIf (EBinOp OpSub scrutinee (EInt n))
          (desugar_match scrutinee rest default)
          body
  end.

Lemma desugar_match_nil : forall scrutinee default,
  desugar_match scrutinee nil default = default.
Proof. reflexivity. Qed.

Lemma exec_desugar_match_single_hit : forall st scrutinee n body default out,
  eval_expr st scrutinee = VInt n ->
  exec st body out ->
  exec st (desugar_match scrutinee ((n, body) :: nil) default) out.
Proof.
  intros. simpl. apply ExecIfFalse.
  - unfold eval_bool. simpl. rewrite H. simpl. rewrite Z.sub_diag. reflexivity.
  - exact H0.
Qed.

Lemma exec_desugar_match_single_miss : forall st scrutinee n body default out,
  eval_expr st scrutinee = VInt n ->
  exec st default out ->
  forall m, m <> n ->
  exec st (desugar_match scrutinee ((m, body) :: nil) default) out.
Proof.
  intros. simpl. apply ExecIfTrue.
  - unfold eval_bool. simpl. rewrite H. simpl.
    destruct (Z.eqb_spec (n - m) 0) as [Heq | Hne2].
    + exfalso. apply H1. lia.
    + destruct (n - m) eqn:E; try reflexivity. exfalso. apply Hne2. reflexivity.
  - exact H0.
Qed.
