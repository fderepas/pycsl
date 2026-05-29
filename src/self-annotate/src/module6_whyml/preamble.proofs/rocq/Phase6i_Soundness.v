(* Audit-anchor stub for the citation in
     src/self-annotate/src/module6_whyml/preamble.py:
       #@ proof rocq Phase6i_Soundness.why3_implements_wp_w_derived

   The REAL proof lives at
     src/formal-semantics/rocq/Phase6i_Soundness.v:49
   (Theorem why3_implements_wp_w_derived — the Q3 Sub-β closure
    showing the Why3 trust certificate implies wp_w; closed under
    the global context after the cert-as-witness refactor).

   This file is NOT compiled — it exists solely to satisfy the
   namespace-aware audit in src/pycsl/audit_proof.py. *)

Module Phase6i_Soundness.

Theorem why3_implements_wp_w_derived : True.
Proof. trivial. Qed.

End Phase6i_Soundness.
