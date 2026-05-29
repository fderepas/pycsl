/-
  ExprTrans.lean — Expression Translation
  Since WhyMLStmt uses Expr for runtime positions and ContractExpr
  for spec positions (mirroring AST exactly), no translation is needed.
  This file provides trivial identity definitions and reflexivity lemmas.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.WP
import PyCSL.WhyML
import PyCSL.WPW

-- Identity translations
def translateExpr (e : ContractExpr) : ContractExpr := e
def translateRuntimeExpr (e : Expr) : Expr := e

-- Trivial evaluation commutation lemmas
@[simp]
theorem evalC_translate (e : ContractExpr) (es preEs : ExecState) (result : Option Val) :
    evalC es preEs result (translateExpr e) = evalC es preEs result e := rfl

@[simp]
theorem evalBool_translateRuntime (e : Expr) (st : State) :
    evalBool st (translateRuntimeExpr e) = evalBool st e := rfl

@[simp]
theorem evalExpr_translateRuntime (e : Expr) (st : State) :
    evalExpr st (translateRuntimeExpr e) = evalExpr st e := rfl
