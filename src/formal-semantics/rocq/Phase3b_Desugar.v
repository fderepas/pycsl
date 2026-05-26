(* Phase3b_Desugar.v — Desugaring correctness + Phase 1a helpers
   Updated for exec_state-based exec (Phase 3a). *)

Require Import ZArith String List Bool.
Require Import Lia.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3b_DesugarDef.
Require Import Phase3_SOS.
Open Scope Z_scope.
Open Scope string_scope.

(* ===================================================================== *)
(* Desugar correctness: exec es s out ↔ exec es (desugar s) out          *)
(* ===================================================================== *)

(* Helper: backward direction for while loops.
   Remember trick: fix inv/var/cond as outer params; induction on exec derivation. *)
Local Lemma bwd_while_aux :
  forall (b : stmt) (es : exec_state) (inv var : contract_expr)
    (cond : expr) (out : outcome),
    (forall es0 out0, exec es0 (desugar b) out0 -> exec es0 b out0) ->
    exec es (SWhile inv var cond (desugar b)) out ->
    exec es (SWhile inv var cond b) out.
Proof.
  intros b es inv var cond out ih_b Hd.
  remember (SWhile inv var cond (desugar b)) as sw eqn:Heqs.
  revert inv var cond Heqs.
  induction Hd; intros inv' var' cond' Heqs;
    try (exfalso; discriminate Heqs).
  - (* ExecWhileTrue *)
    injection Heqs; intros; subst.
    eapply ExecWhileTrue; [exact H | apply ih_b; eassumption | apply IHHd2; reflexivity].
  - (* ExecWhileContinue *)
    injection Heqs; intros; subst.
    eapply ExecWhileContinue; [exact H | apply ih_b; eassumption | apply IHHd2; reflexivity].
  - (* ExecWhileBreak *)
    injection Heqs; intros; subst.
    apply ExecWhileBreak; [exact H | apply ih_b; eassumption].
  - (* ExecWhileFalse *)
    injection Heqs; intros; subst.
    apply ExecWhileFalse; exact H.
Qed.

Lemma desugar_correct_fwd : forall es s out,
  fresh_in_stmt for_idx s ->
  exec es s out -> exec es (desugar s) out.
Proof.
  intros es s out Hfresh Hexec.
  revert Hfresh.
  induction Hexec; intro Hfresh; simpl in Hfresh |- *.
  - apply ExecSkip.
  - apply ExecAssign.
  - apply ExecAugAssign.
  - apply ExecArraySet.
  - (* ExecSeq *)
    destruct Hfresh as [Hf1 Hf2].
    eapply ExecSeq; [apply IHHexec1, Hf1 | apply IHHexec2, Hf2].
  - (* ExecSeqReturn *)
    destruct Hfresh as [Hf1 _].
    apply ExecSeqReturn; apply IHHexec, Hf1.
  - (* ExecSeqContinue *)
    destruct Hfresh as [Hf1 _].
    apply ExecSeqContinue; apply IHHexec, Hf1.
  - (* ExecSeqBreak *)
    destruct Hfresh as [Hf1 _].
    apply ExecSeqBreak; apply IHHexec, Hf1.
  - (* ExecSeqThrow *)
    destruct Hfresh as [Hf1 _].
    apply ExecSeqThrow; apply IHHexec, Hf1.
  - (* ExecIfTrue *)
    destruct Hfresh as [Hf1 _].
    apply ExecIfTrue; [exact H | apply IHHexec, Hf1].
  - (* ExecIfFalse *)
    destruct Hfresh as [_ Hf2].
    apply ExecIfFalse; [exact H | apply IHHexec, Hf2].
  - (* ExecWhileTrue *)
    eapply ExecWhileTrue; [exact H | apply IHHexec1, Hfresh | apply IHHexec2, Hfresh].
  - (* ExecWhileContinue *)
    eapply ExecWhileContinue; [exact H | apply IHHexec1, Hfresh | apply IHHexec2, Hfresh].
  - (* ExecWhileBreak *)
    apply ExecWhileBreak; [exact H | apply IHHexec, Hfresh].
  - (* ExecWhileFalse *)
    apply ExecWhileFalse; exact H.
  - apply ExecContinue.
  - apply ExecBreak.
  - apply ExecReturn.
  - (* ExecAssertPass *)
    apply ExecAssertPass; exact H.
  - (* ExecAssertFail *)
    apply ExecAssertFail; exact H.
  - apply ExecTupleUnpack.
  - apply ExecGhostDecl.
  - apply ExecGhostAssign.
  - apply ExecLabel.
  - apply ExecRaise.
  - (* ExecTryCatchCaught *)
    destruct Hfresh as [Hf1 Hf2].
    eapply ExecTryCatchCaught; [apply IHHexec1, Hf1 | apply IHHexec2, Hf2].
  - (* ExecTryCatchMiss: exec first, then neq *)
    destruct Hfresh as [Hf1 _].
    apply ExecTryCatchMiss; [apply IHHexec, Hf1 | exact H].
  - (* ExecTryCatchNormal: single exec premise *)
    destruct Hfresh as [Hf1 _].
    apply ExecTryCatchNormal; apply IHHexec, Hf1.
  - apply ExecFieldAssign.
  - apply ExecFieldAugAssign.
  - (* ExecCritical *)
    apply ExecCritical; apply IHHexec, Hfresh.
  - (* ExecThreadEntry *)
    apply ExecThreadEntry; apply IHHexec, Hfresh.
  - (* ExecFor: premise is already exec es (desugar (SFor ...)) out *)
    exact Hexec.
Qed.

Lemma desugar_correct_bwd : forall s es out,
  fresh_in_stmt for_idx s ->
  exec es (desugar s) out -> exec es s out.
Proof.
  (* Bullets follow stmt inductive order: SSeq SIf SWhile SFor STryCatch SCritical SThreadEntry *)
  induction s; intros es out Hfresh hd; simpl in hd, Hfresh; try exact hd.
  - (* SSeq s1 s2 *)
    destruct Hfresh as [Hf1 Hf2].
    inversion hd; subst; clear hd.
    + eapply ExecSeq; [apply IHs1 | apply IHs2]; eassumption.
    + apply ExecSeqReturn; apply IHs1; eassumption.
    + apply ExecSeqContinue; apply IHs1; eassumption.
    + apply ExecSeqBreak; apply IHs1; eassumption.
    + apply ExecSeqThrow; apply IHs1; eassumption.
  - (* SIf cond s_then s_else *)
    destruct Hfresh as [Hf1 Hf2].
    inversion hd; subst; clear hd.
    + apply ExecIfTrue; [eassumption | apply IHs1; eassumption].
    + apply ExecIfFalse; [eassumption | apply IHs2; eassumption].
  - (* SWhile inv var cond body *)
    apply (bwd_while_aux s); [intros es0 out0 H0; apply IHs; eassumption | exact hd].
  - (* SFor: ExecFor constructor wraps the desugared exec *)
    apply ExecFor; exact hd.
  - (* STryCatch body exc handler *)
    destruct Hfresh as [Hf1 Hf2].
    inversion hd; subst; clear hd.
    + eapply ExecTryCatchCaught; [apply IHs1 | apply IHs2]; eassumption.
    + apply ExecTryCatchMiss; [apply IHs1; eassumption | eassumption].
    + apply ExecTryCatchNormal; apply IHs1; eassumption.
  - (* SCritical mutex body *)
    inversion hd; subst; clear hd.
    apply ExecCritical; apply IHs; eassumption.
  - (* SThreadEntry body *)
    inversion hd; subst; clear hd.
    apply ExecThreadEntry; apply IHs; eassumption.
Qed.

Theorem desugar_correct : forall es s out,
  fresh_in_stmt for_idx s ->
  exec es s out <-> exec es (desugar s) out.
Proof.
  intros es s out Hfresh. split.
  - exact (desugar_correct_fwd es s out Hfresh).
  - exact (desugar_correct_bwd s es out Hfresh).
Qed.

(* ===================================================================== *)
(* Phase 1a helpers — unchanged *)
(* ===================================================================== *)

Definition walrus_assign (x : ident) (e : expr) : stmt := SAssign x e.

Lemma walrus_assign_eq : forall x e, walrus_assign x e = SAssign x e.
Proof. reflexivity. Qed.

Definition tuple_unpack2 (arr x y : ident) : stmt :=
  SSeq (SAssign x (ESubscript arr (EInt 0)))
       (SAssign y (ESubscript arr (EInt 1))).

Lemma exec_tuple_unpack2_normal : forall es arr x y,
  let st1 := update es.(reg_state) x
               (eval_expr es.(reg_state) (ESubscript arr (EInt 0))) in
  exec es (tuple_unpack2 arr x y)
    (ONormal (set_reg (set_reg es st1)
                (update st1 y (eval_expr st1 (ESubscript arr (EInt 1)))))).
Proof.
  intros. unfold tuple_unpack2.
  eapply ExecSeq; apply ExecAssign.
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

Lemma exec_desugar_match_single_hit : forall es scrutinee n body default out,
  eval_expr es.(reg_state) scrutinee = VInt n ->
  exec es body out ->
  exec es (desugar_match scrutinee ((n, body) :: nil) default) out.
Proof.
  intros. simpl. apply ExecIfFalse.
  - unfold eval_bool. simpl. rewrite H. simpl. rewrite Z.sub_diag. reflexivity.
  - exact H0.
Qed.

Lemma exec_desugar_match_single_miss : forall es scrutinee n body default out,
  eval_expr es.(reg_state) scrutinee = VInt n ->
  exec es default out ->
  forall m, m <> n ->
  exec es (desugar_match scrutinee ((m, body) :: nil) default) out.
Proof.
  intros. simpl. apply ExecIfTrue.
  - unfold eval_bool. simpl. rewrite H. simpl.
    destruct (Z.eqb_spec (n - m) 0) as [Heq | Hne2].
    + exfalso. apply H1. lia.
    + destruct (n - m) eqn:E; try reflexivity. exfalso. apply Hne2. reflexivity.
  - exact H0.
Qed.
