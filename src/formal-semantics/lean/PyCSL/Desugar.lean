/-
  Desugar.lean — Desugaring correctness theorem
  Port of desugar_correct from Phase3b_Desugar.v

  This file imports both DesugarDef and SOS.
  desugar_correct is left as sorry (matching the Rocq Admitted).
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.DesugarDef

theorem desugar_correct (st : State) (s : Stmt) (out : Outcome)
    (hfresh : freshInStmt forIdx s = true) :
    Exec st s out ↔ Exec st (desugar s) out := by
  sorry
