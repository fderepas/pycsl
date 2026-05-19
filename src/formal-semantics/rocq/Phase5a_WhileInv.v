(* Phase5a_WhileInv.v — While Invariant Preservation Lemma *)

Require Import ZArith String List Bool.
Require Import Lia.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Require Import Phase3b_Desugar.
Require Import Phase4_WP.
Open Scope Z_scope.

(* Helper: while loops never produce OContinued *)
Lemma while_not_continued :
  forall st inv var cond body out,
  exec st (SWhile inv var cond body) out ->
  match out with OContinued _ => False | _ => True end.
Proof.
  intros st inv var cond body out Hexec.
  remember (SWhile inv var cond body) as s.
  induction Hexec; try discriminate; injection Heqs; intros; subst.
  - apply IHHexec2; reflexivity.
  - apply IHHexec2; reflexivity.
  - exact I.
Qed.

(* The keystone lemma: while loop invariant is preserved across iterations.
   Takes body soundness as a parameter to break the circularity with
   pycsl_soundness (Phase5b provides it via its induction hypothesis). *)
Lemma while_inv_preserved :
  forall (cond : expr) (body : stmt) (inv var : contract_expr)
    (Qn Qr : state -> Prop) (pre_st st : state),
    (forall st0 out0 Qn0 Qr0 Qc0,
       exec st0 body out0 ->
       wp body Qn0 Qr0 Qc0 pre_st st0 ->
       match out0 with
       | ONormal st' => Qn0 st'
       | OReturned st' _ => Qr0 st'
       | OContinued st' => Qc0 st'
       end) ->
    eval_contract st pre_st None inv ->
    eval_variant st pre_st var >= 0 ->
    (forall st', eval_contract st' pre_st None inv ->
                 eval_bool st' cond = true ->
                 wp body (fun st'' =>
                   eval_contract st'' pre_st None inv /\
                   eval_variant st'' pre_st var < eval_variant st' pre_st var /\
                   eval_variant st'' pre_st var >= 0)
                   Qr
                   (fun st'' =>
                   eval_contract st'' pre_st None inv /\
                   eval_variant st'' pre_st var < eval_variant st' pre_st var /\
                   eval_variant st'' pre_st var >= 0)
                   pre_st st') ->
    (forall st', eval_contract st' pre_st None inv ->
                 eval_bool st' cond = false -> Qn st') ->
    forall out, exec st (SWhile inv var cond body) out ->
    match out with
    | ONormal st' => Qn st'
    | OReturned st' _ => Qr st'
    | OContinued _ => True
    end.
Proof.
  intros cond body inv var Qn Qr pre_st.
  intro st.
  remember (Z.to_nat (eval_variant st pre_st var)) as n.
  generalize dependent st.
  induction n as [n IHn] using lt_wf_ind.
  intros st Heqn Hbody_sound Hinv Hnn Hpres Hpost out Hexec.
  remember (SWhile inv var cond body) as s eqn:Hs.
  induction Hexec; try discriminate.
  - (* ExecWhileTrue: body -> ONormal st', loop continues *)
    injection Hs; intros; subst.
    pose proof Hbody_sound as Hbs.
    specialize (Hbs st (ONormal st') _ _ _ Hexec1 (Hpres st Hinv H)).
    simpl in Hbs.
    destruct Hbs as [Hinv' [Hvar_dec Hvar_nn]].
    eapply (IHn (Z.to_nat (eval_variant st' pre_st var)));
      [ subst; apply Z2Nat.inj_lt; lia
      | reflexivity
      | exact Hbody_sound
      | exact Hinv'
      | exact Hvar_nn
      | exact Hpres
      | exact Hpost
      | exact Hexec2 ].
  - (* ExecWhileContinue: body -> OContinued st', loop continues *)
    injection Hs; intros; subst.
    pose proof Hbody_sound as Hbs.
    specialize (Hbs st (OContinued st') _ _ _ Hexec1 (Hpres st Hinv H)).
    simpl in Hbs.
    destruct Hbs as [Hinv' [Hvar_dec Hvar_nn]].
    eapply (IHn (Z.to_nat (eval_variant st' pre_st var)));
      [ subst; apply Z2Nat.inj_lt; lia
      | reflexivity
      | exact Hbody_sound
      | exact Hinv'
      | exact Hvar_nn
      | exact Hpres
      | exact Hpost
      | exact Hexec2 ].
  - (* ExecWhileFalse: guard false *)
    injection Hs; intros; subst.
    apply Hpost; assumption.
Qed.
