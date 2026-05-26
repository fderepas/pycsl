(* Phase6c_ExprTrans.v — Expression Translation
   Since whyml_stmt uses `expr` for runtime positions and `contract_expr`
   for spec positions (mirroring Phase1_AST exactly), no expression
   translation is required: `gen` (Phase6d_StmtGen) passes expressions
   through unchanged.

   This file provides:
   - identity definitions `translate_expr` / `translate_runtime_expr`
   - trivial reflexivity lemmas confirming no information is lost
   These serve as named hooks for Phase6e_Corr_Simple. *)

Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase4_WP.
Require Import Phase6_WhyML.
Require Import Phase6b_WPW.

(* ===== Expression identity translations ===== *)

(* contract_expr positions are unchanged in whyml_stmt *)
Definition translate_expr (e : contract_expr) : contract_expr := e.

(* expr positions in whyml_stmt also carry expr directly *)
Definition translate_runtime_expr (e : expr) : expr := e.

(* ===== Evaluation commutation lemmas (trivial) ===== *)

(* eval_c is used for contract_expr in both wp and wp_w — identical *)
Lemma eval_c_translate :
  forall e es pre_es result,
  eval_c es pre_es result (translate_expr e) = eval_c es pre_es result e.
Proof. intros. unfold translate_expr. reflexivity. Qed.

(* eval_bool is used for expr in both wp and wp_w — identical *)
Lemma eval_bool_translate_runtime :
  forall e st,
  eval_bool st (translate_runtime_expr e) = eval_bool st e.
Proof. intros. unfold translate_runtime_expr. reflexivity. Qed.

(* eval_expr is used for expr in both wp and wp_w — identical *)
Lemma eval_expr_translate_runtime :
  forall e st,
  eval_expr st (translate_runtime_expr e) = eval_expr st e.
Proof. intros. unfold translate_runtime_expr. reflexivity. Qed.
