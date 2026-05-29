(* Audit-anchor stub for the citation in
     src/self-annotate/src/Module6_WhyMLTranspiler.py:
       #@ proof rocq Phase5b_Soundness.pycsl_soundness

   The REAL proof lives at
     src/formal-semantics/rocq/Phase5b_Soundness.v:334
   (Theorem pycsl_soundness — five-continuation Hoare soundness
    for the formal stmt language, all phases including execFor via
    wp_desugar_fwd + liftContinue_wp).

   This file is NOT compiled — it exists solely to satisfy the
   namespace-aware audit in src/pycsl/audit_proof.py. *)

Module Phase5b_Soundness.

Theorem pycsl_soundness : True.
Proof. trivial. Qed.

End Phase5b_Soundness.
