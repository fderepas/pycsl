(* Phase5b_Soundness.v — PyCSL Soundness Theorem *)

Require Import ZArith String List Bool.
Require Import Lia.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Require Import Phase3b_Desugar.
Require Import Phase4_WP.
Require Import Phase5a_WhileInv.
Open Scope Z_scope.

(* Main soundness theorem: if wp holds and execution terminates,
   the appropriate postcondition holds for each outcome.
   Uses three continuations: Qn (normal), Qr (return), Qc (continue).

   With the local-variant WP (body_done uses < variant at st', not st),
   the while cases reduce to simple IH application: no need for
   while_inv_preserved or well-founded induction. *)
Theorem pycsl_soundness :
  forall st s out Qn Qr Qc pre_st,
  exec st s out ->
  wp s Qn Qr Qc pre_st st ->
  match out with
  | ONormal st'     => Qn st'
  | OReturned st' _ => Qr st'
  | OContinued st'  => Qc st'
  end.
Proof.
  intros st s out Qn Qr Qc pre_st Hexec.
  generalize dependent Qc. generalize dependent Qr.
  generalize dependent Qn. generalize dependent pre_st.
  induction Hexec; intros pre_st Qn0 Qr0 Qc0 Hwp; simpl in Hwp.
  - exact Hwp.
  - exact Hwp.
  - exact Hwp.
  - exact Hwp.
  - (* ExecSeq *) eapply IHHexec2. eapply IHHexec1. exact Hwp.
  - (* ExecSeqReturn *) eapply IHHexec. exact Hwp.
  - (* ExecSeqContinue *) eapply IHHexec. exact Hwp.
  - (* ExecIfTrue *)
    destruct Hwp as [Htrue _]. eapply IHHexec. apply Htrue. exact H.
  - (* ExecIfFalse *)
    destruct Hwp as [_ Hfalse]. eapply IHHexec. apply Hfalse. exact H.
  - (* ExecWhileTrue: body -> ONormal st', loop continues *)
    destruct Hwp as [Hinv [Hpres Hpost]].
    pose proof (IHHexec1 pre_st _ Qr0 _ (Hpres st Hinv H)) as Hbd.
    destruct Hbd as [Hinv' [_ _]].
    eapply IHHexec2. exact (conj Hinv' (conj Hpres Hpost)).
  - (* ExecWhileContinue: body -> OContinued st', loop continues *)
    destruct Hwp as [Hinv [Hpres Hpost]].
    pose proof (IHHexec1 pre_st _ Qr0 _ (Hpres st Hinv H)) as Hbd.
    destruct Hbd as [Hinv' [_ _]].
    eapply IHHexec2. exact (conj Hinv' (conj Hpres Hpost)).
  - (* ExecWhileFalse *)
    destruct Hwp as [Hinv [_ Hpost]]. apply Hpost; assumption.
  - exact Hwp.
  - exact Hwp.
  - (* ExecFor: exec st (desugar (SFor ...)) out and wp (SFor ...) Qn Qr Qc pre_st st.
       Needs a wp_for_desugar coherence lemma:
         wp (SFor x arr inv var body) Qn Qr Qc pre_st st
         → wp (desugar (SFor ...)) Qn Qr Qc pre_st st
       The discrepancy: SFor WP uses variant-at-outer-state while
       SWhile WP uses variant-at-iteration-state.  Admitted pending
       wp_for_desugar proof. *)
    eapply IHHexec.
    admit.
Admitted.
