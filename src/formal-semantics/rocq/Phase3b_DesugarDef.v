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
  | SFor x arr _ _ body _ => x <> id /\ arr <> id /\ fresh_in_stmt id body
  | SReturn _ => True
  | SContinue => True
  (* Phase 2+ additions: fresh by default *)
  | SBreak => True
  | SAssert _ _ => True
  | STupleUnpack _ _ => True
  | SGhostDecl _ _ _ => True
  | SGhostAssign _ _ _ _ => True
  | SLabel _ => True
  | SRaise _ => True
  | STryCatch s1 _ s2 => fresh_in_stmt id s1 /\ fresh_in_stmt id s2
  | SFieldAssign _ _ _ => True
  | SFieldAugAssign _ _ _ _ => True
  | SCritical _ body => fresh_in_stmt id body
  | SThreadEntry body => fresh_in_stmt id body
  | SAcquires _ => True
  | SReleases _ => True
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
  | SFor x arr _ _ body _ =>
    negb (String.eqb x id) && negb (String.eqb arr id) &&
    fresh_in_stmt_b id body
  | SReturn _ => true
  | SContinue => true
  (* Phase 2+ additions *)
  | SBreak => true
  | SAssert _ _ => true
  | STupleUnpack _ _ => true
  | SGhostDecl _ _ _ => true
  | SGhostAssign _ _ _ _ => true
  | SLabel _ => true
  | SRaise _ => true
  | STryCatch s1 _ s2 => fresh_in_stmt_b id s1 && fresh_in_stmt_b id s2
  | SFieldAssign _ _ _ => true
  | SFieldAugAssign _ _ _ _ => true
  | SCritical _ body => fresh_in_stmt_b id body
  | SThreadEntry body => fresh_in_stmt_b id body
  | SAcquires _ => true
  | SReleases _ => true
  end.

(* lift_continue inc s: replace every shallow SContinue in s with (SSeq inc SContinue).
   "Shallow" means: recurse into SSeq/SIf/STryCatch/SCritical/SThreadEntry but
   NOT into SWhile/SFor (those handle their own continue).
   Used by desugar to ensure continue in a for-body increments for_idx before looping back. *)
Fixpoint lift_continue (inc_stmt : stmt) (s : stmt) : stmt :=
  match s with
  | SContinue              => SSeq inc_stmt SContinue
  | SSeq s1 s2             => SSeq (lift_continue inc_stmt s1) (lift_continue inc_stmt s2)
  | SIf c s1 s2            => SIf c (lift_continue inc_stmt s1) (lift_continue inc_stmt s2)
  | STryCatch b exc h      => STryCatch (lift_continue inc_stmt b) exc (lift_continue inc_stmt h)
  | SCritical m b          => SCritical m (lift_continue inc_stmt b)
  | SThreadEntry b         => SThreadEntry (lift_continue inc_stmt b)
  | SAcquires m            => SAcquires m
  | SReleases m            => SReleases m
  (* Leaf constructors: identity (explicit to generate clean equations) *)
  | SSkip                  => SSkip
  | SBreak                 => SBreak
  | SAssign x e            => SAssign x e
  | SAugAssign x op e      => SAugAssign x op e
  | SArraySet arr i v      => SArraySet arr i v
  | SReturn e              => SReturn e
  | SAssert c m            => SAssert c m
  | STupleUnpack xs e      => STupleUnpack xs e
  | SGhostDecl x t e       => SGhostDecl x t e
  | SGhostAssign x t op e  => SGhostAssign x t op e
  | SLabel L               => SLabel L
  | SRaise exc             => SRaise exc
  | SFieldAssign f x v     => SFieldAssign f x v
  | SFieldAugAssign f x op v => SFieldAugAssign f x op v
  | SWhile i v c b         => SWhile i v c b
  | SFor x arr i v b aim   => SFor x arr i v b aim
  end.

(* Desugaring: replace SFor with an index-variable SWhile.
   Guard: EBinOp OpSub (ELen arr) (EVar for_idx)
     = len(arr) - _idx, which is positive when _idx < len(arr) and
       zero (falsy) exactly when _idx = len(arr), terminating the loop.
   lift_continue ensures continue in body increments for_idx before looping back. *)
Fixpoint desugar (s : stmt) : stmt :=
  match s with
  | SFor x arr inv var body _ =>
    let inc_idx := SAugAssign for_idx OpAdd (EInt 1) in
    SSeq (SAssign for_idx (EInt 0))
         (SWhile inv var
                 (EBinOp OpSub (ELen arr) (EVar for_idx))
                 (SSeq (SAssign x (ESubscript arr (EVar for_idx)))
                       (SSeq (lift_continue inc_idx (desugar body)) inc_idx)))
  | SSeq s1 s2 => SSeq (desugar s1) (desugar s2)
  | SIf c s1 s2 => SIf c (desugar s1) (desugar s2)
  | SWhile i v c b => SWhile i v c (desugar b)
  | STryCatch body exc handler => STryCatch (desugar body) exc (desugar handler)
  | SCritical m body => SCritical m (desugar body)
  | SThreadEntry body => SThreadEntry (desugar body)
  | s => s
  end.
