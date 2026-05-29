/-
  EmitSeq.lean — Sub-α.5 + α.8 + α.12 + α.13

  Lean mirror of `rocq/Phase6L_EmitSeq.v` + `Phase6L_EmitSimple.v`.

  This module:
   - introduces the recursive emitStmtFull (subsuming the prior
     per-construct state-aware variants);
   - handles wSeq (recursive concat with ";\n");
   - handles wRaise, wLabel, wAssert (simple single-line constructs).

  Python source: src/pycsl/module6_whyml/statements.py
-/

import PyCSL.AST
import PyCSL.WhyML
import PyCSL.StmtGen
import PyCSL.EmitStmtSurface
import PyCSL.EmitAssign
import PyCSL.EmitAugAssign
import PyCSL.EmitArraySet

namespace PyCSL

open WhyMLStmt

def seqSep : String := ";\n"

/-- Maps WhyMLExc to the Python-emitted exception name. -/
def excToString : WhyMLExc → String
  | .excReturn   => "PyCSL_Return"
  | .excBreak    => "PyCSL_Break"
  | .excContinue => "PyCSL_Continue"
  | .excNamed n  => n

def emitRaise (exc : WhyMLExc) : String :=
  "raise " ++ excToString exc

def acceptableRaiseEmissions (exc : WhyMLExc) : List String :=
  [ "raise " ++ excToString exc ]

theorem emitRaiseCorrect (exc : WhyMLExc) :
    emitRaise exc ∈ acceptableRaiseEmissions exc := by
  simp [emitRaise, acceptableRaiseEmissions]

def emitLabel (L : Ident) : String := "label " ++ L ++ " in"

def acceptableLabelEmissions (L : Ident) : List String :=
  [ "label " ++ L ++ " in" ]

theorem emitLabelCorrect (L : Ident) :
    emitLabel L ∈ acceptableLabelEmissions L := by
  simp [emitLabel, acceptableLabelEmissions]

def emitAssert (_cond : ContractExpr) (_msg : String) : String := "()"

def acceptableAssertEmissions (_cond : ContractExpr) (_msg : String) :
    List String := [ "()" ]

theorem emitAssertCorrect (cond : ContractExpr) (msg : String) :
    emitAssert cond msg ∈ acceptableAssertEmissions cond msg := by
  simp [emitAssert, acceptableAssertEmissions]

/-- Recursive state-aware emission. Subsumes prior per-construct
    variants. wIf/wWhile/wTryCatch/wGhostDecl/wGhostAssign remain
    "" stubs pending their respective PRs. -/
def emitStmtFull (s : AssignState) : WhyMLStmt → String
  | .wSkip                => "()"
  | .wAssign x e          => emitAssign s x e
  | .wAugAssign x op e    => emitAugAssign x op e
  | .wArraySet arr i v    => emitArraySet arr i v
  | .wSeq w1 w2           => emitStmtFull s w1 ++ seqSep
                                ++ emitStmtFull s w2
  | .wRaise exc           => emitRaise exc
  | .wLabel L             => emitLabel L
  | .wAssert cond msg     => emitAssert cond msg
  | .wIf _ _ _            => ""
  | .wWhile _ _ _ _       => ""
  | .wTryCatch _ _ _      => ""
  | .wGhostDecl _ _ _     => ""
  | .wGhostAssign _ _ _ _ => ""

def acceptableSeqEmissions
    (s : AssignState) (w1 w2 : WhyMLStmt) : List String :=
  [ emitStmtFull s w1 ++ seqSep ++ emitStmtFull s w2 ]

theorem emitSeqCorrect (s : AssignState) (w1 w2 : WhyMLStmt) :
    emitStmtFull s (.wSeq w1 w2) ∈ acceptableSeqEmissions s w1 w2 := by
  simp [emitStmtFull, acceptableSeqEmissions]

/-- Per-construct tie-ins via the recursive fixpoint. -/
theorem emitStmtFullRaiseCorrect (s : AssignState) (exc : WhyMLExc) :
    emitStmtFull s (.wRaise exc) ∈ acceptableRaiseEmissions exc := by
  show emitRaise exc ∈ acceptableRaiseEmissions exc
  exact emitRaiseCorrect exc

theorem emitStmtFullLabelCorrect (s : AssignState) (L : Ident) :
    emitStmtFull s (.wLabel L) ∈ acceptableLabelEmissions L := by
  show emitLabel L ∈ acceptableLabelEmissions L
  exact emitLabelCorrect L

theorem emitStmtFullAssertCorrect
    (s : AssignState) (cond : ContractExpr) (msg : String) :
    emitStmtFull s (.wAssert cond msg)
      ∈ acceptableAssertEmissions cond msg := by
  show emitAssert cond msg ∈ acceptableAssertEmissions cond msg
  exact emitAssertCorrect cond msg

theorem emitStmtFullAssignCorrect
    (s : AssignState) (x : Ident) (e : Expr) :
    emitStmtFull s (.wAssign x e) ∈ acceptableAssignEmissions s x e := by
  show emitAssign s x e ∈ acceptableAssignEmissions s x e
  exact emitAssignCorrect s x e

theorem emitStmtFullAugAssignCorrect
    (s : AssignState) (x : Ident) (op : Binop) (e : Expr) :
    emitStmtFull s (.wAugAssign x op e)
      ∈ acceptableAugAssignEmissions x op e := by
  show emitAugAssign x op e ∈ acceptableAugAssignEmissions x op e
  exact emitAugAssignCorrect x op e

theorem emitStmtFullArraySetCorrect
    (s : AssignState) (arr : Ident) (i v : Expr) :
    emitStmtFull s (.wArraySet arr i v)
      ∈ acceptableArraySetEmissions arr i v := by
  show emitArraySet arr i v ∈ acceptableArraySetEmissions arr i v
  exact emitArraySetCorrect arr i v

end PyCSL
