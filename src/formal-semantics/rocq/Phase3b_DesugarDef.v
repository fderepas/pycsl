(* Phase3b_DesugarDef.v — Pure desugaring transformation (no exec dependency)
   Mirrors Lean DesugarDef.lean.
   Split from Phase3b_Desugar.v so Phase3_SOS.v can import the desugar
   function without a circular dependency. *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Open Scope Z_scope.
Open Scope string_scope.

(* Reserved index variable name *)
Definition for_idx : ident := "_pycsl_idx".

(* Freshness predicate: id does not appear as assigned/bound variable in s *)
Fixpoint fresh_in_stmt (id : ident) (s : stmt) : Prop :=
  match s with
  | SSkip => True
  | SAssign x _ => x <> id
  | SAugAssign x _ _ => x <> id
  | SArraySet arr _ _ => arr <> id
  | SSeq s1 s2 => fresh_in_stmt id s1 /\ fresh_in_stmt id s2
  | SIf _ s1 s2 => fresh_in_stmt id s1 /\ fresh_in_stmt id s2
  | SWhile _ _ _ body => fresh_in_stmt id body
  | SFor x arr _ _ body => x <> id /\ arr <> id /\ fresh_in_stmt id body
  | SReturn _ => True
  | SContinue => True
  end.

(* Decidable boolean version of freshness *)
Fixpoint fresh_in_stmt_b (id : ident) (s : stmt) : bool :=
  match s with
  | SSkip => true
  | SAssign x _ => negb (String.eqb x id)
  | SAugAssign x _ _ => negb (String.eqb x id)
  | SArraySet arr _ _ => negb (String.eqb arr id)
  | SSeq s1 s2 => fresh_in_stmt_b id s1 && fresh_in_stmt_b id s2
  | SIf _ s1 s2 => fresh_in_stmt_b id s1 && fresh_in_stmt_b id s2
  | SWhile _ _ _ body => fresh_in_stmt_b id body
  | SFor x arr _ _ body =>
    negb (String.eqb x id) && negb (String.eqb arr id) &&
    fresh_in_stmt_b id body
  | SReturn _ => true
  | SContinue => true
  end.

(* Desugaring: replace SFor with an index-variable SWhile.
   Guard: EBinOp OpSub (ELen arr) (EVar for_idx)
     = len(arr) - _idx, which is positive when _idx < len(arr) and
       zero (falsy) exactly when _idx = len(arr), terminating the loop.
   Freshness invariant ensures _idx never reaches values > len(arr). *)
Fixpoint desugar (s : stmt) : stmt :=
  match s with
  | SFor x arr inv var body =>
    SSeq (SAssign for_idx (EInt 0))
         (SWhile inv var
                 (EBinOp OpSub (ELen arr) (EVar for_idx))
                 (SSeq (SAssign x (ESubscript arr (EVar for_idx)))
                       (SSeq (desugar body)
                             (SAugAssign for_idx OpAdd (EInt 1)))))
  | SSeq s1 s2 => SSeq (desugar s1) (desugar s2)
  | SIf c s1 s2 => SIf c (desugar s1) (desugar s2)
  | SWhile i v c b => SWhile i v c (desugar b)
  | s => s
  end.
