(* Phase6g_Corr_Exc.v — WP Correspondence for Exception Handling
   Proves the correspondence for STryCatch.

   gen (STryCatch s exc handler) = WTryCatch (gen s) exc (gen handler).
   Both wp and wp_w override the exception continuation to dispatch on the
   exception name using String.eqb.  The proof unfolds both sides and uses
   the induction hypothesis for the body and handler sub-terms (those IHs
   are supplied by Phase6h_CorrMain when this lemma is applied). *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase4_WP.
Require Import Phase6_WhyML.
Require Import Phase6b_WPW.
Require Import Phase6c_ExprTrans.
Require Import Phase6d_StmtGen.
Require Import Phase6e_Corr_Simple.
Open Scope Z_scope.

(* wp_gen_trycatch: correspondence for STryCatch, given IHs for sub-terms.

   The proof works by:
   1. Unfold wp and wp_w for (WTryCatch (gen s) exc (gen handler)).
   2. Apply IH_s with a modified Qe to convert between the two forms.
   3. For each exc' value, when exc' = exc, apply IH_handler; otherwise tauto. *)

Lemma wp_gen_trycatch :
  forall s exc handler Qn Qr Qc Qb Qe pre_es es,
  (* IH for body *)
  (forall Qn' Qr' Qc' Qb' Qe' pre_es' es',
   wp s Qn' Qr' Qc' Qb' Qe' pre_es' es' <->
   wp_w (gen s) (enc Qn' Qr' Qc' Qb' Qe') pre_es' es') ->
  (* IH for handler *)
  (forall Qn' Qr' Qc' Qb' Qe' pre_es' es',
   wp handler Qn' Qr' Qc' Qb' Qe' pre_es' es' <->
   wp_w (gen handler) (enc Qn' Qr' Qc' Qb' Qe') pre_es' es') ->
  wp (STryCatch s exc handler) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (STryCatch s exc handler)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  intros s exc handler Qn Qr Qc Qb Qe pre_es es IHs IHhandler.
  simpl gen. simpl wp. simpl wp_w.
  (* LHS: wp s Qn Qr Qc Qb (fun exc' es' => if eqb exc' exc then wp handler ... else Qe ...) pre_es es
     RHS: wp_w (gen s) (enc Qn Qr Qc Qb (fun exc' es' => if eqb exc' exc then wp_w (gen handler) ... else Qe ...)) pre_es es
     Step 1: rewrite LHS using IHs with the modified Qe *)
  rewrite (IHs Qn Qr Qc Qb
    (fun exc' es' => if String.eqb exc' exc then
                       wp handler Qn Qr Qc Qb Qe pre_es es'
                     else Qe exc' es')
    pre_es es).
  (* Step 2: use wp_w_congr to equate the two modified Qe records.
     The wc_n/wc_r/wc_c/wc_b fields are identical; wc_e differs by IHhandler. *)
  apply wp_w_congr; try tauto.
  intros exc' es'.
  (* Force the goal into an explicit form, then destruct before split so the
     if-then-else reduces in the goal itself — no rewrite-in-hyp needed *)
  change (
    (if String.eqb exc' exc
     then wp handler Qn Qr Qc Qb Qe pre_es es'
     else Qe exc' es') <->
    (if String.eqb exc' exc
     then wp_w (gen handler) (enc Qn Qr Qc Qb Qe) pre_es es'
     else Qe exc' es')).
  destruct (String.eqb exc' exc) eqn:Heq.
  - (* true: goal reduces to wp handler ... ↔ wp_w (gen handler) ... *)
    exact (IHhandler Qn Qr Qc Qb Qe pre_es es').
  - (* false: goal reduces to Qe exc' es' ↔ Qe exc' es' *)
    tauto.
Qed.

(* Standalone lemma version used in Phase6h_CorrMain *)
Lemma wp_gen_try_catch_full :
  forall s exc handler Qn Qr Qc Qb Qe pre_es es,
  (forall Qn' Qr' Qc' Qb' Qe' pre_es' es',
   wp s Qn' Qr' Qc' Qb' Qe' pre_es' es' <->
   wp_w (gen s) (enc Qn' Qr' Qc' Qb' Qe') pre_es' es') ->
  (forall Qn' Qr' Qc' Qb' Qe' pre_es' es',
   wp handler Qn' Qr' Qc' Qb' Qe' pre_es' es' <->
   wp_w (gen handler) (enc Qn' Qr' Qc' Qb' Qe') pre_es' es') ->
  wp (STryCatch s exc handler) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (STryCatch s exc handler)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  exact wp_gen_trycatch.
Qed.
