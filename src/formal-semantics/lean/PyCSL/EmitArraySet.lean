/-
  EmitArraySet.lean — Sub-α.4: wArraySet

  Lean mirror of `rocq/Phase6L_EmitArraySet.v`. See that file's
  header for full design notes.

  Summary: Module 6's `_handle_array_set_stmt` has multi-branch
  state dispatch (is_array / is_dict / subscript_set fallback / 2D
  / heap). On formal `SArraySet arr i v` where `arr : Ident`, the
  reachable emissions are the is_array form (canonical) and the
  subscript_set fallback.

  Python source: src/pycsl/module6_whyml/statements.py:563-657
-/

import PyCSL.AST
import PyCSL.WhyML
import PyCSL.StmtGen
import PyCSL.EmitStmtSurface
import PyCSL.EmitAssign

namespace PyCSL

open WhyMLStmt

/-- Formal model — picks the canonical is_array branch. -/
def emitArraySet (arr : Ident) (i v : Expr) : String :=
  arr ++ "[" ++ prettyExpr i ++ "] <- " ++ prettyExpr v

/-- Two acceptable surface forms: native array-write and abstract
    subscript_set fallback. -/
def acceptableArraySetEmissions
    (arr : Ident) (i v : Expr) : List String :=
  [ arr ++ "[" ++ prettyExpr i ++ "] <- " ++ prettyExpr v,
    "subscript_set " ++ arr ++ " " ++ prettyExpr i ++ " " ++ prettyExpr v ]

theorem emitArraySetCorrect (arr : Ident) (i v : Expr) :
    emitArraySet arr i v ∈ acceptableArraySetEmissions arr i v := by
  simp [emitArraySet, acceptableArraySetEmissions]

def emitStmtStringState4 (s : AssignState) (ws : WhyMLStmt) : String :=
  match ws with
  | .wSkip                => "()"
  | .wAssign x e          => emitAssign s x e
  | .wArraySet arr i v    => emitArraySet arr i v
  | _                     => emitStmtString ws

theorem emitStmtStringState4ArraySetCorrect
    (s : AssignState) (arr : Ident) (i v : Expr) :
    emitStmtStringState4 s (gen (.arraySet arr i v))
      ∈ acceptableArraySetEmissions arr i v := by
  show emitArraySet arr i v ∈ acceptableArraySetEmissions arr i v
  exact emitArraySetCorrect arr i v

end PyCSL
