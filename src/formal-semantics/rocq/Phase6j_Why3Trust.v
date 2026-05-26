(* Phase6j_Why3Trust.v — Certificate type for the Why3 tool trust boundary

   Mirrors Why3Trust.lean: defines why3_certificate, an opaque certificate type
   that narrows why3_implements_wp_w from `True →` to a typed witness:

     why3_certificate ws Q  — Why3 verified the WP goal for (ws, Q)

   The module-sealing pattern (Module M : SIG) hides the concrete representation
   (unit) behind an abstract signature, preventing external construction of
   certificates without going through why3_trust_check.

   Lean 4 status (Why3Trust.lean, Task 5): Why3Trust.check is implemented —
   it invokes `why3 prove -a split_vc -P Alt-Ergo,2.6.2, -P Z3,4.13.3,
   --timelimit 30 <file.mlw>`, filters stdout for "Prover result is:" lines,
   and issues a certificate iff exit code = 0 and every such line contains "Valid".

   Rocq: why3_trust_check is retained as a unit stub (None).  Rocq is the
   verification layer, not the execution layer; the executable trust argument
   is carried by the Lean 4 version.  The types and axioms in this file and
   Phase6i_Soundness.v are the formal mirror of the Lean 4 trust boundary.

   Note: SmtCertificate (smt_certificate) and LinearArithVC (linear_arith_vc)
   cannot be placed in this file because Phase6j imports Phase5b transitively
   (Phase6b_WPW → Phase4_WP → Phase5a_WhileInv → Phase5b_Soundness would create
   a cycle if Phase5b imported Phase6j).  Both are defined in Phase5b_Soundness.v. *)

Require Import ZArith String.
Require Import Phase6_WhyML.
Require Import Phase6b_WPW.

(* ===== Why3 certificate type ===== *)

(* Abstract signature: cert is an opaque family of types indexed by (ws, Q).
   Clients see Why3Trust.cert : whyml_stmt -> wp_conts -> Type but cannot
   construct values — the concrete definition (unit) is hidden by sealing. *)
Module Type WHY3_CERT_SIG.
  Parameter cert : whyml_stmt -> wp_conts -> Type.
End WHY3_CERT_SIG.

Module Why3Trust : WHY3_CERT_SIG.
  Definition cert (_ws : whyml_stmt) (_Q : wp_conts) : Type := unit.
End Why3Trust.

(* Public type alias — matches `def Why3Certificate` in Why3Trust.lean. *)
Definition why3_certificate := Why3Trust.cert.

(* Rocq stub — always returns None.
   The executable implementation (Task 5) lives in Why3Trust.lean (Lean 4):
     Why3Trust.check invokes `why3 prove -a split_vc -P Alt-Ergo,2.6.2,
     -P Z3,4.13.3, --timelimit 30 <file.mlw>` and parses the output.
   In Rocq, certificates are never constructed at runtime; the axiom
   why3_implements_wp_w in Phase6i_Soundness.v is the formal trust statement. *)
Definition why3_trust_check
    (_mlw_path : string) (ws : whyml_stmt) (Q : wp_conts) :
    option (why3_certificate ws Q) := None.
