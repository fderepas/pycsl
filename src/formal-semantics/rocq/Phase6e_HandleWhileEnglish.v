(* Phase6e_HandleWhileEnglish.v — Rocq refinement of english-07.md
 *
 * Companion of src/formal-semantics/lean/PyCSL/HandleWhileEnglish.lean.
 *
 * Single-branch emitter for while loop with invariant + variant.
 * Reduces to the existing umbrella lemma wp_gen_while. *)

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

Inductive while_branch : Type :=
  | BrWhileOnly.

Definition gen_while_by_branch
    (b : while_branch) (inv var cond body : _ )  : whyml_stmt :=
  match b with
  | BrWhileOnly => gen (SWhile inv var cond body)
  end.

Lemma gen_while_by_branch_eq_gen :
  forall b inv var cond body, gen_while_by_branch b inv var cond body = gen (SWhile inv var cond body).
Proof. intros b inv var cond body; destruct b; reflexivity. Qed.

(* Equality theorem: the dispatcher collapses to gen for any branch.
   Anyone needing the deeper WP equivalence applies wp_gen_while
   to this equality. The proof is by reflexivity per arm. *)
Theorem handle_while_branches_correct :
  forall b inv var cond body,
  gen_while_by_branch b inv var cond body = gen (SWhile inv var cond body).
Proof. intros b inv var cond body; destruct b; reflexivity. Qed.
