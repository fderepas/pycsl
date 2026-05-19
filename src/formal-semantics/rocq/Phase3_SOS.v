(* Phase3_SOS.v — Structural Operational Semantics *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Open Scope Z_scope.

(* Execution outcomes: normal completion, return, or continue *)
Inductive outcome : Type :=
  | ONormal    (st : state)
  | OReturned  (st : state) (v : val)
  | OContinued (st : state).

(* Execution relation *)
Inductive exec : state -> stmt -> outcome -> Prop :=
  | ExecSkip :
      forall st, exec st SSkip (ONormal st)

  | ExecAssign :
      forall st x e,
      exec st (SAssign x e) (ONormal (update st x (eval_expr st e)))

  | ExecAugAssign :
      forall st x op e,
      let cur := match lookup st x with Some (VInt n) => n | _ => 0 end in
      let nv  := eval_binop_z op cur
                   (match eval_expr st e with VInt n => n | _ => 0 end) in
      exec st (SAugAssign x op e) (ONormal (update st x (VInt nv)))

  | ExecArraySet :
      forall st arr i v,
      let idx := match eval_expr st i with VInt n => n | _ => 0 end in
      let nv  := match eval_expr st v with VInt n => n | _ => 0 end in
      exec st (SArraySet arr i v) (ONormal (array_update st arr idx nv))

  | ExecSeq :
      forall st s1 s2 st' out,
      exec st s1 (ONormal st') ->
      exec st' s2 out ->
      exec st (SSeq s1 s2) out

  | ExecSeqReturn :
      forall st s1 s2 st' v,
      exec st s1 (OReturned st' v) ->
      exec st (SSeq s1 s2) (OReturned st' v)

  | ExecSeqContinue :
      forall st s1 s2 st',
      exec st s1 (OContinued st') ->
      exec st (SSeq s1 s2) (OContinued st')

  | ExecIfTrue :
      forall st cond s1 s2 out,
      eval_bool st cond = true ->
      exec st s1 out ->
      exec st (SIf cond s1 s2) out

  | ExecIfFalse :
      forall st cond s1 s2 out,
      eval_bool st cond = false ->
      exec st s2 out ->
      exec st (SIf cond s1 s2) out

  | ExecWhileTrue :
      forall st inv var cond body st' out,
      eval_bool st cond = true ->
      exec st body (ONormal st') ->
      exec st' (SWhile inv var cond body) out ->
      exec st (SWhile inv var cond body) out

  | ExecWhileContinue :
      forall st inv var cond body st' out,
      eval_bool st cond = true ->
      exec st body (OContinued st') ->
      exec st' (SWhile inv var cond body) out ->
      exec st (SWhile inv var cond body) out

  | ExecWhileFalse :
      forall st inv var cond body,
      eval_bool st cond = false ->
      exec st (SWhile inv var cond body) (ONormal st)

  | ExecContinue :
      forall st, exec st SContinue (OContinued st)

  | ExecReturn :
      forall st e,
      exec st (SReturn e)
        (OReturned (update st "\result" (eval_expr st e))
                   (eval_expr st e)).

(* Determinism: induction on the first execution derivation *)
Lemma exec_deterministic :
  forall st s out1 out2,
  exec st s out1 -> exec st s out2 -> out1 = out2.
Proof.
  intros st s out1 out2 H1. generalize dependent out2.
  induction H1; intros out2 H2; inversion H2; subst;
    try reflexivity; try congruence.
  (* Single-IH cases: SeqReturn, SeqContinue *)
  all: try (match goal with
    | [ IH: forall out2, exec ?st ?s out2 -> ?o1 = out2, H: exec ?st ?s ?o2 |- _ ] =>
        specialize (IH _ H); try discriminate; try (inversion IH; subst; auto; fail)
    end).
  (* Double-IH cases: Seq, WhileTrue, WhileContinue *)
  all: try (match goal with
    | [ IH1: forall out2, exec ?st1 ?s1 out2 -> _ = out2,
        IH2: forall out2, exec ?st2 ?s2 out2 -> _ = out2,
        Hbody: exec ?st1 ?s1 ?mid,
        Hrest: exec _ ?s2 ?o2 |- _ ] =>
        specialize (IH1 _ Hbody); inversion IH1; subst;
        apply IH2; auto
    end).
Qed.
