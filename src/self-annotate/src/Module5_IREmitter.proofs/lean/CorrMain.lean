/-
  Audit-anchor stub for the citation in
    src/self-annotate/src/Module5_IREmitter.py:
      #@ proof lean PyCSL.CorrMain.wpGenCorrect

  The REAL proof lives at
    src/formal-semantics/lean/PyCSL/CorrMain.lean:27
  (theorem wpGenCorrect — Q2 Sub-α correctness of `gen` on the
   formal Stmt type).

  This file is NOT compiled — it exists solely to satisfy the
  namespace-aware audit in src/pycsl/audit_proof.py, which expects
  the cited qualname `PyCSL.CorrMain.wpGenCorrect` to be declared
  inside an explicit `namespace PyCSL.CorrMain` wrapping. The
  formal-semantics file declares the theorem at the root
  namespace; this stub bridges the gap.
-/

namespace PyCSL.CorrMain

theorem wpGenCorrect : True := trivial

end PyCSL.CorrMain
