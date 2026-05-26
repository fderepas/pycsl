(* Phase6e_HandleTupleUnpackEnglish.v — Rocq refinement of english-10.md
 *
 * Companion of src/formal-semantics/lean/PyCSL/HandleTupleUnpackEnglish.lean.
 *
 * Single-branch emitter for multi-target unpacking (x, y = ...).
 * Reduces to the existing umbrella lemma wp_gen_tuple_unpack. *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase4_WP.
Require Import Phase6_WhyML.
Require Import Phase6b_WPW.
Require Import Phase6c_ExprTrans.
Require Import Phase6d_StmtGen.
Require Import Phase6e_Corr_Simple.
Require Import Phase6f_Corr_Loops.
Require Import Phase6g_Corr_Exc.
Open Scope Z_scope.

Inductive tuple_unpack_branch : Type :=
  | BrTupleUnpackOnly.

Definition gen_tuple_unpack_by_branch
    (b : tuple_unpack_branch) (xs e : _ )  : whyml_stmt :=
  match b with
  | BrTupleUnpackOnly => gen (STupleUnpack xs e)
  end.

Lemma gen_tuple_unpack_by_branch_eq_gen :
  forall b xs e, gen_tuple_unpack_by_branch b xs e = gen (STupleUnpack xs e).
Proof. intros b xs e; destruct b; reflexivity. Qed.

(* Equality theorem: the dispatcher collapses to gen for any branch.
   Anyone needing the deeper WP equivalence applies wp_gen_tuple_unpack
   to this equality. The proof is by reflexivity per arm. *)
Theorem handle_tuple_unpack_branches_correct :
  forall b xs e,
  gen_tuple_unpack_by_branch b xs e = gen (STupleUnpack xs e).
Proof. intros b xs e; destruct b; reflexivity. Qed.
