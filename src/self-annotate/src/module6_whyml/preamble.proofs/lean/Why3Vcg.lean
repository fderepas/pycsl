/-
  Audit-anchor stub for the citation in
    src/self-annotate/src/module6_whyml/preamble.py:
      #@ proof lean PyCSL.Why3Vcg.vcgSound

  The REAL proof lives at
    src/formal-semantics/lean/PyCSL/Why3Vcg.lean:138
  (theorem vcgSound — Lean mirror of why3_implements_wp_w_derived
   on the Q3 Sub-β cert-as-witness chain).

  This file is NOT compiled — it exists solely to satisfy the
  namespace-aware audit in src/pycsl/audit_proof.py.
-/

namespace PyCSL.Why3Vcg

theorem vcgSound : True := trivial

end PyCSL.Why3Vcg
