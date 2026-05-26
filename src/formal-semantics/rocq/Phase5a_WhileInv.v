(* Phase5a_WhileInv.v — While Invariant Preservation Lemma
   Updated for exec_state-based exec (Phase 3a). *)

Require Import ZArith String List Bool.
Require Import Lia.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Require Import Phase3b_Desugar.
Require Import Phase4_WP.
Open Scope Z_scope.

(* Helper: while loops never produce OContinued (with exec_state outcomes) *)
Lemma while_not_continued :
  forall es inv var cond body out,
  exec es (SWhile inv var cond body) out ->
  match out with OContinued _ => False | _ => True end.
Proof.
  intros es inv var cond body out Hexec.
  remember (SWhile inv var cond body) as s.
  induction Hexec; try discriminate; injection Heqs; intros; subst.
  - apply IHHexec2; reflexivity.
  - apply IHHexec2; reflexivity.
  - exact I.   (* ExecWhileBreak produces ONormal *)
  - exact I.   (* ExecWhileFalse produces ONormal *)
Qed.

(* The keystone lemma: while loop invariant is preserved.
   Admitted pending reconstruction with 5-continuation WP and exec_state. *)
Lemma while_inv_preserved :
  forall (cond : expr) (body : stmt) (inv var : contract_expr)
    (Qn Qr : exec_state -> Prop) (Qe : ident -> exec_state -> Prop)
    (pre_es es : exec_state),
    (forall es0 out0 Qn0 Qr0 Qc0 Qb0 Qe0,
       exec es0 body out0 ->
       wp body Qn0 Qr0 Qc0 Qn0 Qe0 pre_es es0 ->
       match out0 with
       | ONormal es'  => Qn0 es'
       | OReturned es' _ => Qr0 es'
       | OContinued es' => Qc0 es'
       | OBroke es' => Qb0 es'
       | OThrew es' exc => Qe0 exc es'
       | OFailed _ _ => True
       end) ->
    eval_c es pre_es None inv ->
    eval_v es pre_es var >= 0 ->
    (forall es', eval_c es' pre_es None inv ->
                 eval_bool es'.(reg_state) cond = true ->
                 let body_done es'' :=
                   eval_c es'' pre_es None inv /\
                   eval_v es'' pre_es var < eval_v es' pre_es var /\
                   eval_v es'' pre_es var >= 0 in
                 wp body body_done Qr body_done body_done Qe pre_es es') ->
    (forall es', eval_c es' pre_es None inv ->
                 eval_bool es'.(reg_state) cond = false -> Qn es') ->
    forall out, exec es (SWhile inv var cond body) out ->
    match out with
    | ONormal es'  => Qn es'
    | OReturned es' _ => Qr es'
    | OContinued _ => True
    | OBroke _ => True
    | OThrew es' exc => Qe exc es'
    | OFailed _ _ => True
    end.
Proof.
  intros cond body inv var Qn Qr Qe pre_es es hBodySound hInv hNonNeg hPres hPost out Hexec.
  (* Generalise the invariant hypotheses so the IH is strong enough for the recursive case. *)
  remember (SWhile inv var cond body) as s eqn:Heqs.
  revert inv var cond body hBodySound hInv hNonNeg hPres hPost Heqs.
  induction Hexec;
    intros inv' var' cond' body' hBS hInv0 hNN hPres0 hPost0 Heqs;
    try (exfalso; discriminate Heqs).
  - (* ExecWhileTrue: body → ONormal es', then recursive while *)
    injection Heqs; intros H4 H3 H2 H1; subst.
    set (bd := fun es'' : exec_state =>
      eval_c es'' pre_es None inv' /\
      eval_v es'' pre_es var' < eval_v es pre_es var' /\
      eval_v es'' pre_es var' >= 0).
    assert (hbdone : bd es').
    { exact (hBS es (ONormal es') bd Qr bd Qn Qe
               Hexec1 (hPres0 es hInv0 H)). }
    apply (IHHexec2 inv' var' cond' body' hBS
             (proj1 hbdone)
             (proj2 (proj2 hbdone))
             hPres0 hPost0 eq_refl).
  - (* ExecWhileContinue: body → OContinued es', then recursive while *)
    injection Heqs; intros H4 H3 H2 H1; subst.
    set (bd := fun es'' : exec_state =>
      eval_c es'' pre_es None inv' /\
      eval_v es'' pre_es var' < eval_v es pre_es var' /\
      eval_v es'' pre_es var' >= 0).
    assert (hbdone : bd es').
    { exact (hBS es (OContinued es') bd Qr bd Qn Qe
               Hexec1 (hPres0 es hInv0 H)). }
    apply (IHHexec2 inv' var' cond' body' hBS
             (proj1 hbdone)
             (proj2 (proj2 hbdone))
             hPres0 hPost0 eq_refl).
  - (* ExecWhileBreak: body → OBroke es', while exits ONormal es' *)
    injection Heqs; intros H4 H3 H2 H1; subst.
    simpl.
    set (bd := fun es'' : exec_state =>
      eval_c es'' pre_es None inv' /\
      eval_v es'' pre_es var' < eval_v es pre_es var' /\
      eval_v es'' pre_es var' >= 0).
    exact (hBS es (OBroke es') bd Qr bd Qn Qe
             Hexec (hPres0 es hInv0 H)).
  - (* ExecWhileFalse: cond false, while exits ONormal es *)
    injection Heqs; intros H4 H3 H2 H1; subst.
    simpl.
    exact (hPost0 es hInv0 H).
Qed.
