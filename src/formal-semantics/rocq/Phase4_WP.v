(* Phase4_WP.v — Weakest Precondition Calculus *)
(* Uses three continuations: Qn (normal), Qr (return), Qc (continue)
   to correctly handle early termination in sequences and continue in loops. *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Require Import Phase3b_DesugarDef.
Require Import Phase3b_Desugar.
Open Scope Z_scope.

(* wp s Qn Qr Qc pre_st st:
   - s      : the statement
   - Qn     : postcondition for normal completion
   - Qr     : postcondition for return (receives state with \result bound)
   - Qc     : postcondition for continue
   - pre_st : entry state at function call, used for \old evaluation
   - st     : current state *)
Fixpoint wp (s : stmt) (Qn Qr Qc : state -> Prop) (pre_st : state) (st : state) : Prop :=
  match s with
  | SSkip => Qn st

  | SAssign x e =>
    Qn (update st x (eval_expr st e))

  | SAugAssign x op e =>
    let cur := match lookup st x with Some (VInt n) => n | _ => 0 end in
    let nv := eval_binop_z op cur
                (match eval_expr st e with VInt n => n | _ => 0 end) in
    Qn (update st x (VInt nv))

  | SArraySet arr i v =>
    let idx := match eval_expr st i with VInt n => n | _ => 0 end in
    let nv := match eval_expr st v with VInt n => n | _ => 0 end in
    Qn (array_update st arr idx nv)

  | SSeq s1 s2 =>
    (* Normal: chain s1 → s2. Return/Continue: propagate from s1. *)
    wp s1 (fun st' => wp s2 Qn Qr Qc pre_st st') Qr Qc pre_st st

  | SIf cond s1 s2 =>
    (eval_bool st cond = true  -> wp s1 Qn Qr Qc pre_st st) /\
    (eval_bool st cond = false -> wp s2 Qn Qr Qc pre_st st)

  | SWhile inv var cond body =>
    eval_contract st pre_st None inv /\
    (forall st',
      eval_contract st' pre_st None inv ->
      eval_bool st' cond = true ->
      (* Body's Qn and Qc both require invariant preservation + variant decrease.
         The variant bound is LOCAL to each iteration (< at st', not st).
         Qr propagates the outer return continuation. *)
      wp body (fun st'' =>
        eval_contract st'' pre_st None inv /\
        eval_variant st'' pre_st var < eval_variant st' pre_st var /\
        eval_variant st'' pre_st var >= 0)
        Qr
        (fun st'' =>
        eval_contract st'' pre_st None inv /\
        eval_variant st'' pre_st var < eval_variant st' pre_st var /\
        eval_variant st'' pre_st var >= 0)
        pre_st st') /\
    (forall st',
      eval_contract st' pre_st None inv ->
      eval_bool st' cond = false ->
      Qn st')

  | SFor x arr inv var body =>
    let st0 := update st for_idx (VInt 0) in
    let body_done := fun st'' =>
      eval_contract st'' pre_st None inv /\
      eval_variant st'' pre_st var < eval_variant st pre_st var /\
      eval_variant st'' pre_st var >= 0 in
    eval_contract st0 pre_st None inv /\
    (forall st',
      eval_contract st' pre_st None inv ->
      eval_z st' pre_st None (CVar for_idx) <
        eval_z st' pre_st None (CLength arr) ->
      let st1 := update st' x
                   (eval_expr st' (ESubscript arr (EVar for_idx))) in
      wp body (fun st2 =>
        let cur_idx := match lookup st2 for_idx with
                       | Some (VInt n) => n | _ => 0 end in
        let st3 := update st2 for_idx (VInt (cur_idx + 1)) in
        body_done st3) Qr (fun st2 =>
        let cur_idx := match lookup st2 for_idx with
                       | Some (VInt n) => n | _ => 0 end in
        let st3 := update st2 for_idx (VInt (cur_idx + 1)) in
        body_done st3) pre_st st1) /\
    (forall st',
      eval_contract st' pre_st None inv ->
      eval_z st' pre_st None (CVar for_idx) >=
        eval_z st' pre_st None (CLength arr) ->
      Qn st')

  | SReturn e =>
    Qr (update st "\result" (eval_expr st e))

  | SContinue =>
    Qc st
  end.
