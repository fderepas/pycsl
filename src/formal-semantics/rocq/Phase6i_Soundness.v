(* Phase6i_Soundness.v — Verified Soundness via WhyML Correspondence

   Phase 6A+6B (monday-02.md) — Rocq parity with SoundnessVerified.lean.

   OLD (pre-6A):
     Axiom why3_implements_wp_w : why3_certificate ws Q -> wp_w ws Q pre_es es
     (trusted both Why3's VCG algorithm AND Why3's provers)

   NEW (Phase 6C, current):
     module6_encodes_mlw (Phase6k_VcgSound.v) : why3_certificate ws Q -> vc_prop ws Q pre_es es
       [Axiom — Phase 6C proof obligation; replaces the Admitted in vcg_bridge]
     vcg_bridge (Phase6k_VcgSound.v) : why3_certificate ws Q -> vc_prop ws Q pre_es es
       [proved — no Admitted; derived from module6_encodes_mlw]
     vcg_sound (Phase6k_VcgSound.v) : vc_prop ws Q pre_es es <-> wp_w ws Q pre_es es
       [proved — no axioms beyond propositional/functional extensionality]
     why3_implements_wp_w_derived := vcg_bridge + vcg_sound
       [depends on module6_encodes_mlw, a named Axiom; no Admitted]

   The old why3_implements_wp_w axiom is kept for backward compatibility.

   Verified soundness path (unchanged):
   1. why3_implements_wp_w_derived ← vcg_bridge (admit) + vcg_sound (proved)
   2. wp_w (gen s) (enc ...) pre_es es
   3. wp_gen_correct (Phase6h_CorrMain) -> wp s Qn Qr Qc Qb Qe pre_es es
   4. pycsl_soundness (Phase5b_Soundness) -> outcome_post Qn Qr Qc Qb Qe out *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Require Import Phase4_WP.
Require Import Phase5b_Soundness.
Require Import Phase6_WhyML.
Require Import Phase6b_WPW.
Require Import Phase6d_StmtGen.
Require Import Phase6h_CorrMain.
Require Import Phase6j_Why3Trust.
Require Import Phase6k_VcgSound.    (* vc_prop, vcg_sound *)
Require Import Phase6m_VcgSemBridge. (* vcg_bridge — Q3 Sub-β port (2026-05-28) *)
Open Scope Z_scope.

(* ===== Phase 6C: derived theorem using vcg_bridge (proved) + vcg_sound (proved) ===== *)

(* why3_implements_wp_w_derived: wp_w follows from vcg_bridge + vcg_sound.
   The trust chain is now:
     why3_certificate  ->(vcg_bridge->module6_encodes_mlw, Axiom)->  vc_prop
                       ->(vcg_sound, proved)->  wp_w
   vcg_bridge has NO Admitted.  The trust is in module6_encodes_mlw (named Axiom). *)
Theorem why3_implements_wp_w_derived :
  forall (ws : whyml_stmt) (Q : wp_conts) (pre_es es : exec_state),
  why3_certificate ws Q ->
  wp_w ws Q pre_es es.
Proof.
  intros ws Q pre_es es Hcert.
  apply (proj1 (vcg_sound ws Q pre_es es)).
  exact (vcg_bridge ws Q pre_es es Hcert).
Qed.

(* ===== Backward compatibility: old broad axiom ===== *)

(* why3_implements_wp_w (kept for backward compatibility during migration).
   DEPRECATED: use why3_implements_wp_w_derived instead.
   Once all callers migrate to why3_implements_wp_w_derived, this axiom
   can be deleted (its trust is now documented via module6_encodes_mlw). *)
Axiom why3_implements_wp_w :
  forall (ws : whyml_stmt) (Q : wp_conts) (pre_es es : exec_state),
  why3_certificate ws Q ->
  wp_w ws Q pre_es es.

(* ===== Corollary: wp_w -> wp via correspondence ===== *)

(* wp_w_implies_wp: bridges wp_w back to the PyCSL WP using the
   bidirectional correspondence theorem from Phase6h_CorrMain. *)
Corollary wp_w_implies_wp :
  forall s Qn Qr Qc Qb Qe pre_es es,
  wp_w (gen s) (enc Qn Qr Qc Qb Qe) pre_es es ->
  wp s Qn Qr Qc Qb Qe pre_es es.
Proof.
  intros s Qn Qr Qc Qb Qe pre_es es H.
  exact (proj2 (wp_gen_correct s Qn Qr Qc Qb Qe pre_es es) H).
Qed.

(* ===== Verified soundness theorem ===== *)

(* pycsl_soundness_verified: end-to-end soundness via the new path.
   Takes wp_w (gen s) (enc ...) as the hypothesis (produced by
   why3_implements_wp_w_derived from a Why3 VCG certificate + vcg_bridge),
   chains through wp_gen_correct and pycsl_soundness. *)
Theorem pycsl_soundness_verified :
  forall s Qn Qr Qc Qb Qe pre_es es out,
  exec es s out ->
  wp_w (gen s) (enc Qn Qr Qc Qb Qe) pre_es es ->
  outcome_post Qn Qr Qc Qb Qe out.
Proof.
  intros s Qn Qr Qc Qb Qe pre_es es out Hexec Hwpw.
  exact (pycsl_soundness es s out Qn Qr Qc Qb Qe pre_es Hexec
           (wp_w_implies_wp s Qn Qr Qc Qb Qe pre_es es Hwpw)).
Qed.
