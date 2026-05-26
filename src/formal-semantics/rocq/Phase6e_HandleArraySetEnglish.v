(* Phase6e_HandleArraySetEnglish.v — Rocq refinement of english-04.md
 *
 * Companion of src/formal-semantics/lean/PyCSL/HandleArraySetEnglish.lean.
 *
 * Single-branch emitter for array element assignment arr[i] = v.
 * Reduces to the existing umbrella lemma wp_gen_array_set. *)

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

Inductive array_set_branch : Type :=
  | BrArraySetOnly.

Definition gen_array_set_by_branch
    (b : array_set_branch) (arr i v : _ )  : whyml_stmt :=
  match b with
  | BrArraySetOnly => gen (SArraySet arr i v)
  end.

Lemma gen_array_set_by_branch_eq_gen :
  forall b arr i v, gen_array_set_by_branch b arr i v = gen (SArraySet arr i v).
Proof. intros b arr i v; destruct b; reflexivity. Qed.

(* Equality theorem: the dispatcher collapses to gen for any branch.
   Anyone needing the deeper WP equivalence applies wp_gen_array_set
   to this equality. The proof is by reflexivity per arm. *)
Theorem handle_array_set_branches_correct :
  forall b arr i v,
  gen_array_set_by_branch b arr i v = gen (SArraySet arr i v).
Proof. intros b arr i v; destruct b; reflexivity. Qed.
