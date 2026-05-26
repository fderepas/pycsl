(* Phase6e_HandleGhostAssignEnglish.v — Rocq refinement of english-11.md
 *
 * Companion of src/formal-semantics/lean/PyCSL/HandleGhostAssignEnglish.lean.
 *
 * Single-branch emitter for ghost variable assignment (reg-state preserved).
 * Reduces to the existing umbrella lemma wp_gen_ghost_assign. *)

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

Inductive ghost_assign_branch : Type :=
  | BrGhostAssignOnly.

Definition gen_ghost_assign_by_branch
    (b : ghost_assign_branch) (x t op e : _ )  : whyml_stmt :=
  match b with
  | BrGhostAssignOnly => gen (SGhostAssign x t op e)
  end.

Lemma gen_ghost_assign_by_branch_eq_gen :
  forall b x t op e, gen_ghost_assign_by_branch b x t op e = gen (SGhostAssign x t op e).
Proof. intros b x t op e; destruct b; reflexivity. Qed.

(* Equality theorem: the dispatcher collapses to gen for any branch.
   Anyone needing the deeper WP equivalence applies wp_gen_ghost_assign
   to this equality. The proof is by reflexivity per arm. *)
Theorem handle_ghost_assign_branches_correct :
  forall b x t op e,
  gen_ghost_assign_by_branch b x t op e = gen (SGhostAssign x t op e).
Proof. intros b x t op e; destruct b; reflexivity. Qed.
