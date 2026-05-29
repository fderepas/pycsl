(* Phase6e_HandleForEnglish.v — Rocq refinement of english-08.md
 *
 * Companion of src/formal-semantics/lean/PyCSL/HandleForEnglish.lean.
 *
 * Single-branch emitter for for loop (desugared into a while).
 * Reduces to the existing umbrella lemma wp_gen_for. *)

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

Inductive for_branch : Type :=
  | BrForOnly.

Definition gen_for_by_branch
    (b : for_branch) (x arr : _) (inv var : _) (body : _) (aim : bool)  : whyml_stmt :=
  match b with
  | BrForOnly => gen (SFor x arr inv var body aim)
  end.

Lemma gen_for_by_branch_eq_gen :
  forall b x arr inv var body aim,
  gen_for_by_branch b x arr inv var body aim = gen (SFor x arr inv var body aim).
Proof. intros b x arr inv var body aim; destruct b; reflexivity. Qed.

(* Equality theorem: the dispatcher collapses to gen for any branch.
   Anyone needing the deeper WP equivalence applies wp_gen_for
   to this equality. The proof is by reflexivity per arm. *)
Theorem handle_for_branches_correct :
  forall b x arr inv var body aim,
  gen_for_by_branch b x arr inv var body aim = gen (SFor x arr inv var body aim).
Proof. intros b x arr inv var body aim; destruct b; reflexivity. Qed.
