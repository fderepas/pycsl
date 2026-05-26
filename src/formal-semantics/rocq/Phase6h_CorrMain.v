(* Phase6h_CorrMain.v — Full WP Correspondence Theorem
   Combines Chunks 5–7 into the master theorem by structural induction on s:

     Theorem wp_gen_correct :
       forall s Qn Qr Qc Qb Qe pre_es es,
       wp s Qn Qr Qc Qb Qe pre_es es
       <->
       wp_w (gen s) (enc Qn Qr Qc Qb Qe) pre_es es.

   Base cases dispatch to Phase6e_Corr_Simple lemmas.
   Inductive cases (SSeq, SIf, SWhile, STryCatch, SFor, SCritical, SThreadEntry)
   use the induction hypothesis via Phase6f_Corr_Loops and Phase6g_Corr_Exc. *)

Require Import ZArith String List Bool.
Require Import Coq.Logic.FunctionalExtensionality.
Require Import Coq.Logic.PropExtensionality.
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

(* ===== Master WP correspondence theorem ===== *)

Theorem wp_gen_correct :
  forall s Qn Qr Qc Qb Qe pre_es es,
  wp s Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen s) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  induction s; intros Qn Qr Qc Qb Qe pre_es es.
  - (* SSkip *)       exact (wp_gen_skip Qn Qr Qc Qb Qe pre_es es).
  - (* SAssign *)     exact (wp_gen_assign x e Qn Qr Qc Qb Qe pre_es es).
  - (* SAugAssign *)  exact (wp_gen_aug_assign x op e Qn Qr Qc Qb Qe pre_es es).
  - (* SArraySet *)   exact (wp_gen_array_set arr i v Qn Qr Qc Qb Qe pre_es es).
  - (* SSeq *)
    exact (wp_gen_seq s1 s2 Qn Qr Qc Qb Qe pre_es es
             (fun Qn' Qr' Qc' Qb' Qe' pre_es' es' => IHs1 Qn' Qr' Qc' Qb' Qe' pre_es' es')
             (fun Qn' Qr' Qc' Qb' Qe' pre_es' es' => IHs2 Qn' Qr' Qc' Qb' Qe' pre_es' es')).
  - (* SIf *)
    exact (wp_gen_if cond s1 s2 Qn Qr Qc Qb Qe pre_es es
             (fun Qn' Qr' Qc' Qb' Qe' pre_es' es' => IHs1 Qn' Qr' Qc' Qb' Qe' pre_es' es')
             (fun Qn' Qr' Qc' Qb' Qe' pre_es' es' => IHs2 Qn' Qr' Qc' Qb' Qe' pre_es' es')).
  - (* SWhile: Coq names the recursive body sub-term 's' (not 'body') in induction *)
    exact (wp_gen_while inv var cond s Qn Qr Qc Qb Qe pre_es es
             (fun Qn' Qr' Qc' Qb' Qe' pre_es' es' => IHs Qn' Qr' Qc' Qb' Qe' pre_es' es')).
  - (* SFor: same naming convention *)
    exact (wp_gen_for x arr inv var s Qn Qr Qc Qb Qe pre_es es
             (fun Qn' Qr' Qc' Qb' Qe' pre_es' es' => IHs Qn' Qr' Qc' Qb' Qe' pre_es' es')).
  - (* SReturn *)     exact (wp_gen_return e Qn Qr Qc Qb Qe pre_es es).
  - (* SContinue *)   exact (wp_gen_continue Qn Qr Qc Qb Qe pre_es es).
  - (* SBreak *)      exact (wp_gen_break Qn Qr Qc Qb Qe pre_es es).
  - (* SAssert *)     exact (wp_gen_assert cond msg Qn Qr Qc Qb Qe pre_es es).
  - (* STupleUnpack *) exact (wp_gen_tuple_unpack xs e Qn Qr Qc Qb Qe pre_es es).
  - (* SGhostDecl *)  exact (wp_gen_ghost_decl x t init Qn Qr Qc Qb Qe pre_es es).
  - (* SGhostAssign *) exact (wp_gen_ghost_assign x t op rhs Qn Qr Qc Qb Qe pre_es es).
  - (* SLabel *)      exact (wp_gen_label name Qn Qr Qc Qb Qe pre_es es).
  - (* SRaise *)      exact (wp_gen_raise exc Qn Qr Qc Qb Qe pre_es es).
  - (* STryCatch *)
    exact (wp_gen_trycatch s1 exc s2 Qn Qr Qc Qb Qe pre_es es
             (fun Qn' Qr' Qc' Qb' Qe' pre_es' es' => IHs1 Qn' Qr' Qc' Qb' Qe' pre_es' es')
             (fun Qn' Qr' Qc' Qb' Qe' pre_es' es' => IHs2 Qn' Qr' Qc' Qb' Qe' pre_es' es')).
  - (* SFieldAssign *)    exact (wp_gen_field_assign self_id f e Qn Qr Qc Qb Qe pre_es es).
  - (* SFieldAugAssign *) exact (wp_gen_field_aug_assign self_id f op e Qn Qr Qc Qb Qe pre_es es).
  - (* SCritical: body sub-term named 's' by Coq induction *)
    exact (wp_gen_critical mutex s Qn Qr Qc Qb Qe pre_es es
             (fun Qn' Qr' Qc' Qb' Qe' pre_es' es' => IHs Qn' Qr' Qc' Qb' Qe' pre_es' es')).
  - (* SThreadEntry: body sub-term named 's' by Coq induction *)
    exact (wp_gen_thread_entry s Qn Qr Qc Qb Qe pre_es es
             (fun Qn' Qr' Qc' Qb' Qe' pre_es' es' => IHs Qn' Qr' Qc' Qb' Qe' pre_es' es')).
Qed.

(* ===== Corollary: using wp_w (gen s) implies wp s ===== *)

Corollary wp_w_gen_implies_wp :
  forall s Qn Qr Qc Qb Qe pre_es es,
  wp_w (gen s) (enc Qn Qr Qc Qb Qe) pre_es es ->
  wp s Qn Qr Qc Qb Qe pre_es es.
Proof.
  intros. apply (proj2 (wp_gen_correct s Qn Qr Qc Qb Qe pre_es es)). assumption.
Qed.
