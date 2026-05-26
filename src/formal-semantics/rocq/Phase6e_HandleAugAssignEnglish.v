(* Phase6e_HandleAugAssignEnglish.v — Rocq refinement of english-02.md
 *
 * Companion of src/formal-semantics/lean/PyCSL/HandleAugAssignEnglish.lean.
 *
 * Single-branch emitter for augmented assignment (x += e style).
 * Reduces to the existing umbrella lemma wp_gen_aug_assign. *)

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

Inductive aug_assign_branch : Type :=
  | BrAugAssignOnly.

Definition gen_aug_assign_by_branch
    (b : aug_assign_branch) (x op e : _ )  : whyml_stmt :=
  match b with
  | BrAugAssignOnly => gen (SAugAssign x op e)
  end.

Lemma gen_aug_assign_by_branch_eq_gen :
  forall b x op e, gen_aug_assign_by_branch b x op e = gen (SAugAssign x op e).
Proof. intros b x op e; destruct b; reflexivity. Qed.

(* Equality theorem: the dispatcher collapses to gen for any branch.
   Anyone needing the deeper WP equivalence applies wp_gen_aug_assign
   to this equality. The proof is by reflexivity per arm. *)
Theorem handle_aug_assign_branches_correct :
  forall b x op e,
  gen_aug_assign_by_branch b x op e = gen (SAugAssign x op e).
Proof. intros b x op e; destruct b; reflexivity. Qed.
