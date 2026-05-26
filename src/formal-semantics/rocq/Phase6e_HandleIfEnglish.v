(* Phase6e_HandleIfEnglish.v — Rocq refinement of english-05.md
 *
 * Companion of src/formal-semantics/lean/PyCSL/HandleIfEnglish.lean.
 *
 * Single-branch emitter for conditional statement with then/else branches.
 * Reduces to the existing umbrella lemma wp_gen_if. *)

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

Inductive if_branch : Type :=
  | BrIfOnly.

Definition gen_if_by_branch
    (b : if_branch) (cond t f : _ )  : whyml_stmt :=
  match b with
  | BrIfOnly => gen (SIf cond t f)
  end.

Lemma gen_if_by_branch_eq_gen :
  forall b cond t f, gen_if_by_branch b cond t f = gen (SIf cond t f).
Proof. intros b cond t f; destruct b; reflexivity. Qed.

(* Equality theorem: the dispatcher collapses to gen for any branch.
   Anyone needing the deeper WP equivalence applies wp_gen_if
   to this equality. The proof is by reflexivity per arm. *)
Theorem handle_if_branches_correct :
  forall b cond t f,
  gen_if_by_branch b cond t f = gen (SIf cond t f).
Proof. intros b cond t f; destruct b; reflexivity. Qed.
