(* Phase1_AST.v — Abstract Syntax Tree for PyCSL formal semantics *)
(* Part of the PyCSL formal verification project *)

Require Import ZArith String List.
Open Scope Z_scope.
Open Scope string_scope.

Definition ident := string.
Definition ident_eq := String.eqb.

(* Decidable equality for identifiers *)
Lemma ident_eq_dec : forall (x y : ident), {x = y} + {x <> y}.
Proof. apply String.string_dec. Defined.

(* Arithmetic binary operators *)
Inductive binop : Type :=
  | OpAdd | OpSub | OpMul | OpDiv.

(* Runtime expressions — Python subset, no logical connectives *)
Inductive expr : Type :=
  | EInt       (n : Z)
  | EVar       (x : ident)
  | ESubscript (arr : ident) (i : expr)
  | EBinOp     (op : binop) (e1 e2 : expr)
  | ENeg       (e : expr).

(* Contract expressions — full logical language with \result, \old, quantifiers *)
Inductive contract_expr : Type :=
  | CInt       (n : Z)
  | CVar       (x : ident)
  | CResult
  | CLength    (arr : ident)
  | CSubscript (arr : ident) (i : contract_expr)
  | COld       (e : contract_expr)
  | CBinOp     (op : binop) (e1 e2 : contract_expr)
  | CNeg       (e : contract_expr)
  | CEq        (e1 e2 : contract_expr)
  | CNe        (e1 e2 : contract_expr)
  | CLt        (e1 e2 : contract_expr)
  | CLe        (e1 e2 : contract_expr)
  | CGt        (e1 e2 : contract_expr)
  | CGe        (e1 e2 : contract_expr)
  | CAnd       (e1 e2 : contract_expr)
  | COr        (e1 e2 : contract_expr)
  | CNot       (e : contract_expr)
  | CImplies   (e1 e2 : contract_expr)
  | CIff       (e1 e2 : contract_expr)
  | CForall    (x : ident) (body : contract_expr)
  | CExists    (x : ident) (body : contract_expr).

(* Frame conditions *)
Inductive frame_cond : Type :=
  | FNothing
  | FVars (xs : list ident).

(* Function specifications *)
Record func_spec : Type := mkSpec {
  spec_pre   : contract_expr;
  spec_post  : contract_expr;
  spec_frame : frame_cond
}.

(* Statements — SWhile carries mandatory inv and var annotations *)
Inductive stmt : Type :=
  | SSkip
  | SAssign    (x : ident)   (e : expr)
  | SAugAssign (x : ident)   (op : binop) (e : expr)
  | SArraySet  (arr : ident) (i : expr) (v : expr)
  | SSeq       (s1 s2 : stmt)
  | SIf        (cond : expr) (s_then s_else : stmt)
  | SWhile     (inv : contract_expr) (var : contract_expr)
               (cond : expr) (body : stmt)
  | SFor       (x : ident) (arr : ident)
               (inv : contract_expr) (var : contract_expr) (body : stmt)
  | SReturn    (e : expr)
  | SContinue.
