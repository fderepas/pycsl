(* Phase2_State.v — Values, state, and concrete evaluators *)

Require Import ZArith String List Bool.
Require Import Coq.Arith.PeanoNat.
Require Import Phase1_AST.
Open Scope Z_scope.

(* Runtime values *)
Inductive val : Type :=
  | VInt   (n : Z)
  | VArray (a : list Z).

(* Association-list state *)
Definition state := list (ident * val).

(* State lookup *)
Fixpoint lookup (st : state) (x : ident) : option val :=
  match st with
  | nil => None
  | (y, v) :: rest =>
    if String.eqb x y then Some v else lookup rest x
  end.

(* State update — cons-based shadowing *)
Definition update (st : state) (x : ident) (v : val) : state :=
  (x, v) :: st.

(* Array element update *)
Definition array_update (st : state) (arr : ident) (i : Z) (v : Z) : state :=
  match lookup st arr with
  | Some (VArray a) =>
    let idx := Z.to_nat i in
    if (0 <=? i) && (i <? Z.of_nat (List.length a)) then
      let a' := List.app (List.firstn idx a) (List.app (v :: nil) (List.skipn (S idx) a)) in
      update st arr (VArray a')
    else st
  | _ => st
  end.

(* Arithmetic on Z *)
Definition eval_binop_z (op : binop) (n1 n2 : Z) : Z :=
  match op with
  | OpAdd => n1 + n2
  | OpSub => n1 - n2
  | OpMul => n1 * n2
  | OpDiv => if Z.eqb n2 0 then 0 else Z.div n1 n2
  end.

(* Runtime expression evaluator — total function *)
Fixpoint eval_expr (st : state) (e : expr) : val :=
  match e with
  | EInt n => VInt n
  | EVar x => match lookup st x with Some v => v | None => VInt 0 end
  | ESubscript arr i =>
    match lookup st arr, eval_expr st i with
    | Some (VArray a), VInt n =>
      if (0 <=? n) && (n <? Z.of_nat (List.length a))
      then VInt (List.nth (Z.to_nat n) a 0)
      else VInt 0
    | _, _ => VInt 0
    end
  | ELen arr =>
    match lookup st arr with
    | Some (VArray a) => VInt (Z.of_nat (List.length a))
    | _ => VInt 0
    end
  | EBinOp op e1 e2 =>
    match eval_expr st e1, eval_expr st e2 with
    | VInt n1, VInt n2 => VInt (eval_binop_z op n1 n2)
    | _, _ => VInt 0
    end
  | ENeg e =>
    match eval_expr st e with
    | VInt n => VInt (- n)
    | v => v
    end
  end.

(* Boolean test for conditional/loop guards *)
Definition eval_bool (st : state) (e : expr) : bool :=
  match eval_expr st e with
  | VInt 0 => false
  | _ => true
  end.

(* Integer extraction from contract expressions *)
Fixpoint eval_z (st pre_st : state) (result : option val)
                (e : contract_expr) : Z :=
  match e with
  | CInt n => n
  | CVar x => match lookup st x with Some (VInt n) => n | _ => 0 end
  | CResult => match result with Some (VInt n) => n | _ => 0 end
  | CLength arr =>
    match lookup st arr with
    | Some (VArray a) => Z.of_nat (List.length a)
    | _ => 0
    end
  | CSubscript arr i =>
    let n := eval_z st pre_st result i in
    match lookup st arr with
    | Some (VArray a) =>
      if (0 <=? n) && (n <? Z.of_nat (List.length a))
      then List.nth (Z.to_nat n) a 0
      else 0
    | _ => 0
    end
  | COld e => eval_z pre_st pre_st result e
  | CBinOp op e1 e2 =>
    eval_binop_z op (eval_z st pre_st result e1) (eval_z st pre_st result e2)
  | CNeg e => - (eval_z st pre_st result e)
  | _ => 0
  end.

(* Logical evaluation of contract expressions *)
Fixpoint eval_contract (st pre_st : state) (result : option val)
                       (e : contract_expr) : Prop :=
  match e with
  | CInt n => n <> 0
  | CVar x =>
    match lookup st x with Some (VInt 0) => False | _ => True end
  | CResult =>
    match result with Some (VInt 0) => False | _ => True end
  | CLength _ | CSubscript _ _ | COld _ | CBinOp _ _ _ | CNeg _ =>
    eval_z st pre_st result e <> 0
  | CEq  e1 e2 => eval_z st pre_st result e1 =  eval_z st pre_st result e2
  | CNe  e1 e2 => eval_z st pre_st result e1 <> eval_z st pre_st result e2
  | CLt  e1 e2 => eval_z st pre_st result e1 <  eval_z st pre_st result e2
  | CLe  e1 e2 => eval_z st pre_st result e1 <= eval_z st pre_st result e2
  | CGt  e1 e2 => eval_z st pre_st result e1 >  eval_z st pre_st result e2
  | CGe  e1 e2 => eval_z st pre_st result e1 >= eval_z st pre_st result e2
  | CAnd e1 e2 =>
    eval_contract st pre_st result e1 /\ eval_contract st pre_st result e2
  | COr  e1 e2 =>
    eval_contract st pre_st result e1 \/ eval_contract st pre_st result e2
  | CNot e => ~ eval_contract st pre_st result e
  | CImplies e1 e2 =>
    eval_contract st pre_st result e1 -> eval_contract st pre_st result e2
  | CIff e1 e2 =>
    eval_contract st pre_st result e1 <-> eval_contract st pre_st result e2
  | CForall x body =>
    forall n : Z,
      eval_contract (update st x (VInt n)) pre_st result body
  | CExists x body =>
    exists n : Z,
      eval_contract (update st x (VInt n)) pre_st result body
  end.

(* Variant evaluation — produces Z for well-founded induction *)
Definition eval_variant (st pre_st : state) (e : contract_expr) : Z :=
  eval_z st pre_st None e.
