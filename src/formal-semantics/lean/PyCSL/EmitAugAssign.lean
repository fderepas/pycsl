/-
  EmitAugAssign.lean — Sub-α.3: full state coverage for wAugAssign

  Lean mirror of `rocq/Phase6L_EmitAugAssign.v`. See that file's
  header for the full design notes.

  Summary: Module 6's `_handle_augassign_stmt` has three branches
  (bitwise / array-extend / default). On formal `Binop` (4
  variants: add/sub/mul/div), only the default branch fires. The
  acceptable set is therefore a singleton.

  Python source: src/pycsl/module6_whyml/statements.py:783-827
-/

import PyCSL.AST
import PyCSL.WhyML
import PyCSL.StmtGen
import PyCSL.EmitStmtSurface
import PyCSL.EmitAssign

namespace PyCSL

open WhyMLStmt

/-- Statement-level operator translation (mirrors Python's
    `op_translate` for the operators in the default branch of
    `_handle_augassign_stmt` on formal `Binop`). -/
def opTranslateAug : Binop → String
  | .add => "+"
  | .sub => "-"
  | .mul => "*"
  | .div => "div"   -- identifiers.py:OP_MAP["/"] = "div"
  | .mod_ => "mod"

/-- Formal model of `_handle_augassign_stmt`'s default branch.
    Bitwise and array-extend branches are unreachable on formal
    `Binop` / `Expr`; see Rocq header. -/
def emitAugAssign (x : Ident) (op : Binop) (e : Expr) : String :=
  x ++ " := !" ++ x ++ " " ++ opTranslateAug op ++ " " ++ prettyExpr e

def acceptableAugAssignEmissions
    (x : Ident) (op : Binop) (e : Expr) : List String :=
  [ x ++ " := !" ++ x ++ " " ++ opTranslateAug op ++ " " ++ prettyExpr e ]

theorem emitAugAssignCorrect (x : Ident) (op : Binop) (e : Expr) :
    emitAugAssign x op e ∈ acceptableAugAssignEmissions x op e := by
  simp [emitAugAssign, acceptableAugAssignEmissions]

/-- State-aware emit_stmt extended to handle wAugAssign in addition
    to wSkip and wAssign. -/
def emitStmtStringState2 (s : AssignState) (ws : WhyMLStmt) : String :=
  match ws with
  | .wSkip              => "()"
  | .wAssign x e        => emitAssign s x e
  | .wAugAssign x op e  => emitAugAssign x op e
  | _                   => emitStmtString ws

theorem emitStmtStringState2AugAssignCorrect
    (s : AssignState) (x : Ident) (op : Binop) (e : Expr) :
    emitStmtStringState2 s (gen (.augAssign x op e))
      ∈ acceptableAugAssignEmissions x op e := by
  show emitAugAssign x op e ∈ acceptableAugAssignEmissions x op e
  exact emitAugAssignCorrect x op e

theorem emitStmtStringState2Skip (s : AssignState) :
    emitStmtStringState2 s (gen .skip) = "()" := by
  simp [emitStmtStringState2, gen]

theorem emitStmtStringState2AssignCorrect
    (s : AssignState) (x : Ident) (e : Expr) :
    emitStmtStringState2 s (gen (.assign x e))
      ∈ acceptableAssignEmissions s x e := by
  show emitAssign s x e ∈ acceptableAssignEmissions s x e
  exact emitAssignCorrect s x e

end PyCSL
