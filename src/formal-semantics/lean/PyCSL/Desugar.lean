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

-- =====================================================================
-- Phase 1a — Category B desugaring correctness lemmas
-- =====================================================================

-- Feature 29 — walrusAssign is definitionally equal to assign
theorem walrusAssign_eq (x : Ident) (e : Expr) :
    walrusAssign x e = .assign x e := rfl

-- The Exec relation for walrus_assign is the same as for assign.
theorem exec_walrusAssign (st : State) (x : Ident) (e : Expr) (out : Outcome) :
    Exec st (walrusAssign x e) out ↔ Exec st (.assign x e) out := by
  rfl

-- Feature 28 — tupleUnpack2 is a sequence of two subscript assignments.
theorem tupleUnpack2_eq (arr x y : Ident) :
    tupleUnpack2 arr x y =
    .seq (.assign x (.subscript arr (.int 0)))
         (.assign y (.subscript arr (.int 1))) := rfl

-- Executing tupleUnpack2 produces normal outcome with both elements assigned.
theorem exec_tupleUnpack2_normal (st : State) (arr x y : Ident) :
    let st1 := update st x (evalExpr st (.subscript arr (.int 0)))
    Exec st (tupleUnpack2 arr x y)
      (.normal (update st1 y (evalExpr st1 (.subscript arr (.int 1))))) := by
  exact .execSeq _ _ _ _ _ (.execAssign ..) (.execAssign ..)

-- Feature 30 — Empty match reduces to default.
theorem desugarMatch_nil (scrutinee : Expr) (default : Stmt) :
    desugarMatch scrutinee [] default = default := rfl

-- Single-arm match executes body when scrutinee = n.
theorem exec_desugarMatch_hit (st : State) (scrutinee : Expr) (n : Int)
    (body default : Stmt) (out : Outcome)
    (hval : evalExpr st scrutinee = .int n) (hbody : Exec st body out) :
    Exec st (desugarMatch scrutinee [(n, body)] default) out := by
  simp [desugarMatch]
  apply Exec.execIfFalse
  · simp [evalBool, evalExpr, hval, evalBinopZ]
  · exact hbody

-- Single-arm match executes default when scrutinee ≠ n.
theorem exec_desugarMatch_miss (st : State) (scrutinee : Expr) (n m : Int)
    (body default : Stmt) (out : Outcome)
    (hval : evalExpr st scrutinee = .int n) (hne : n ≠ m)
    (hdef : Exec st default out) :
    Exec st (desugarMatch scrutinee [(m, body)] default) out := by
  simp only [desugarMatch]
  apply Exec.execIfTrue
  · simp only [evalBool, evalExpr, hval, evalBinopZ]
    have hd : n - m ≠ 0 := by omega
    split
    · rename_i h; injection h; omega
    · rfl
  · exact hdef
