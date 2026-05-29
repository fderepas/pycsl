(* Phase6j_Why3Trust.v — Certificate type for the Why3 tool trust boundary

   Mirrors Why3Trust.lean. After the Q3 Sub-β port (2026-05-29),
   `why3_certificate` is no longer an opaque sealed unit — it is
   the WITNESS TYPE itself: a function from VC indices to proofs
   of the corresponding eval_vc_formula. Constructing a certificate
   now REQUIRES producing the witness for every emitted VC.

   This eliminates the prior `enrich_main_cert` axiom (Phase6m).
   The trust line moves to the construction site: in Lean's
   executable `Why3Trust.check`, the witness is the Why3 verdict
   reified into Coq evidence (still an axiom on the Lean side,
   pending β.4); in pure Rocq, the cert type is uninhabited
   without external evidence, so `why3_trust_check` returns None.

   Lean 4 status (Why3Trust.lean): Why3Trust.check invokes
     why3 prove -a split_vc -P Alt-Ergo,2.6.2, -P Z3,4.13.3,
       --timelimit 30 <file.mlw>
   and accepts iff exit code = 0 and every "Prover result is:"
   line contains "Valid".

   Build-order note (Q3 Sub-β port): this file now sits AFTER
   Phase6k_VcgSound and Phase6c_VcFormula, which provide vc_prop
   and the vc_formula machinery respectively. Phase6k previously
   imported Phase6j (decorative; no actual symbol use), so the
   reordering was safe. *)

Require Import ZArith String.
Require Import Phase6_WhyML.
Require Import Phase6b_WPW.
Require Import Phase6c_VcFormula.
Require Import Phase2_State.

(* ===== Why3 certificate type ===== *)

(* why3_certificate ws Q: the witness type — a proof that every
   VC emitted by `vc_formula_of ws Q ...` denotationally holds
   (eval_vc_formula). This replaces the prior opaque sealed-unit
   `Why3Trust.cert`.

   To construct a value of this type, one must supply, for every
   (pre_es, es, i, f) such that vc_formula_of ws Q pre_es es i = Some f,
   a proof of eval_vc_formula f es pre_es. This is exactly what
   Why3's "Valid" verdict claims — the witness reifies it. *)
Definition why3_certificate (ws : whyml_stmt) (Q : wp_conts) : Type :=
  forall (pre_es es : exec_state) (i : nat) (f : vc_formula),
    vc_formula_of ws Q pre_es es i = Some f ->
    eval_vc_formula f es pre_es.

(* Rocq stub — always returns None.
   The executable implementation lives in Why3Trust.lean (Lean 4):
   it invokes the Why3 binary and reifies the "Valid" verdict into
   the witness. Pure Rocq cannot construct certificates without
   external evidence — this is the trust boundary. *)
Definition why3_trust_check
    (_mlw_path : string) (ws : whyml_stmt) (Q : wp_conts) :
    option (why3_certificate ws Q) := None.
