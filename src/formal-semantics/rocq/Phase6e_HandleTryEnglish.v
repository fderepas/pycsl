(* Phase6e_HandleTryEnglish.v — Rocq refinement of english-06.md
 *
 * Companion of src/formal-semantics/lean/PyCSL/HandleTryEnglish.lean.
 *
 * Single-branch emitter for try/except exception handling.
 * Reduces to the existing umbrella lemma wp_gen_trycatch. *)

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

Inductive try_branch : Type :=
  | BrTryOnly.

Definition gen_try_by_branch
    (b : try_branch) (body exc handler : _ )  : whyml_stmt :=
  match b with
  | BrTryOnly => gen (STryCatch body exc handler)
  end.

Lemma gen_try_by_branch_eq_gen :
  forall b body exc handler, gen_try_by_branch b body exc handler = gen (STryCatch body exc handler).
Proof. intros b body exc handler; destruct b; reflexivity. Qed.

(* Equality theorem: the dispatcher collapses to gen for any branch.
   Anyone needing the deeper WP equivalence applies wp_gen_trycatch
   to this equality. The proof is by reflexivity per arm. *)
Theorem handle_try_branches_correct :
  forall b body exc handler,
  gen_try_by_branch b body exc handler = gen (STryCatch body exc handler).
Proof. intros b body exc handler; destruct b; reflexivity. Qed.
