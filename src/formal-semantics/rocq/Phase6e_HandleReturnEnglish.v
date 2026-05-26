(* Phase6e_HandleReturnEnglish.v — Rocq refinement of english-03.md
 *
 * Companion of src/formal-semantics/lean/PyCSL/HandleReturnEnglish.lean.
 *
 * Single-branch emitter for return statement (encoded as raise(Return,e)).
 * Reduces to the existing umbrella lemma wp_gen_return. *)

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

Inductive return_branch : Type :=
  | BrReturnOnly.

Definition gen_return_by_branch
    (b : return_branch) (e : _ )  : whyml_stmt :=
  match b with
  | BrReturnOnly => gen (SReturn e)
  end.

Lemma gen_return_by_branch_eq_gen :
  forall b e, gen_return_by_branch b e = gen (SReturn e).
Proof. intros b e; destruct b; reflexivity. Qed.

(* Equality theorem: the dispatcher collapses to gen for any branch.
   Anyone needing the deeper WP equivalence applies wp_gen_return
   to this equality. The proof is by reflexivity per arm. *)
Theorem handle_return_branches_correct :
  forall b e,
  gen_return_by_branch b e = gen (SReturn e).
Proof. intros b e; destruct b; reflexivity. Qed.
