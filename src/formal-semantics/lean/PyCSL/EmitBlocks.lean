/-
  EmitBlocks.lean — Sub-α.6/.7/.9/.10/.11

  Lean mirror of `rocq/Phase6L_EmitBlocks.v`. See that file's
  header for full design notes.

  This module covers the five deferred multi-line block constructs:
    α.6  wIf       — if/then/else
    α.7  wWhile    — while/invariant/variant/do/done
    α.9  wTryCatch — try/with
    α.10 wGhostDecl   — let ghost x = ... in
    α.11 wGhostAssign — ghost x := ...

  And introduces `emitStmtFullComplete` — the recursive Fixpoint
  covering ALL 13 WhyMLStmt constructors.

  Python source: src/pycsl/module6_whyml/statements.py
-/

import PyCSL.AST
import PyCSL.WhyML
import PyCSL.StmtGen
import PyCSL.EmitStmtSurface
import PyCSL.EmitAssign
import PyCSL.EmitAugAssign
import PyCSL.EmitArraySet
import PyCSL.EmitSeq

namespace PyCSL

open WhyMLStmt

def nl : String := "\n"

/-- Partial pretty-printer for ContractExpr. The core subset
    (literals, vars, binops, comparisons, quantifiers, length,
    subscript) is rendered; the remaining 30+ constructors return
    `"?contract?"`. Documented in Rocq header. -/
def prettyContractExpr : ContractExpr → String
  | .int n               => zToStringPP n
  | .var x               => x
  | .boolLit b           => if b then "true" else "false"
  | .noneLit             => "None"
  | .stringLit s         => "\"" ++ s ++ "\""
  | .result              => "result"
  | .length a            => "(length " ++ a ++ ")"
  | .subscript a i       => a ++ "[" ++ prettyContractExpr i ++ "]"
  | .old e               => "(old " ++ prettyContractExpr e ++ ")"
  | .binop op e1 e2      => "(" ++ prettyContractExpr e1 ++ " "
                                ++ prettyBinop op ++ " "
                                ++ prettyContractExpr e2 ++ ")"
  | .neg e               => "(- " ++ prettyContractExpr e ++ ")"
  | .eq e1 e2            => "(" ++ prettyContractExpr e1 ++ " = "
                                ++ prettyContractExpr e2 ++ ")"
  | .ne e1 e2            => "(" ++ prettyContractExpr e1 ++ " <> "
                                ++ prettyContractExpr e2 ++ ")"
  | .lt e1 e2            => "(" ++ prettyContractExpr e1 ++ " < "
                                ++ prettyContractExpr e2 ++ ")"
  | .le e1 e2            => "(" ++ prettyContractExpr e1 ++ " <= "
                                ++ prettyContractExpr e2 ++ ")"
  | .gt e1 e2            => "(" ++ prettyContractExpr e1 ++ " > "
                                ++ prettyContractExpr e2 ++ ")"
  | .ge e1 e2            => "(" ++ prettyContractExpr e1 ++ " >= "
                                ++ prettyContractExpr e2 ++ ")"
  | .and e1 e2           => "(" ++ prettyContractExpr e1 ++ " && "
                                ++ prettyContractExpr e2 ++ ")"
  | .or e1 e2            => "(" ++ prettyContractExpr e1 ++ " || "
                                ++ prettyContractExpr e2 ++ ")"
  | .not e               => "(not " ++ prettyContractExpr e ++ ")"
  | .implies e1 e2       => "(" ++ prettyContractExpr e1 ++ " -> "
                                ++ prettyContractExpr e2 ++ ")"
  | .iff e1 e2           => "(" ++ prettyContractExpr e1 ++ " <-> "
                                ++ prettyContractExpr e2 ++ ")"
  | .forall_ x body      => "(forall " ++ x ++ " : int. "
                                ++ prettyContractExpr body ++ ")"
  | .exists_ x body      => "(exists " ++ x ++ " : int. "
                                ++ prettyContractExpr body ++ ")"
  | _                    => "?contract?"

def augOpStr : AugOp → String
  | .add => "+"
  | .sub => "-"
  | .mul => "*"

/-- Per-ghost-type emission of ghost variable declarations. -/
def emitGhostDecl (x : Ident) (t : GhostType) (e : GhostExpr) : String :=
  let val := prettyContractExpr e
  match t with
  | .array => "let ghost " ++ x ++ " = " ++ val ++ " in"
  | _      => "let ghost " ++ x ++ " = ref " ++ val ++ " in"

def acceptableGhostDeclEmissions (x : Ident) (t : GhostType)
    (e : GhostExpr) : List String :=
  let val := prettyContractExpr e
  [ "let ghost " ++ x ++ " = " ++ val ++ " in",
    "let ghost " ++ x ++ " = ref " ++ val ++ " in" ]

theorem emitGhostDeclCorrect (x : Ident) (t : GhostType) (e : GhostExpr) :
    emitGhostDecl x t e ∈ acceptableGhostDeclEmissions x t e := by
  unfold emitGhostDecl acceptableGhostDeclEmissions
  cases t <;> simp

/-- Per-(ghost_type, aug_op) emission of ghost assignment. -/
def emitGhostAssign
    (x : Ident) (t : GhostType) (op : AugOp) (e : GhostExpr) : String :=
  let val := prettyContractExpr e
  match t with
  | .int     => "ghost " ++ x ++ " := !" ++ x ++ " " ++ augOpStr op ++ " " ++ val
  | .array   => "ghost " ++ x ++ " <- " ++ val
  | .list    => match op with
                | .add => "ghost " ++ x ++ " := (Cons " ++ val ++ " !" ++ x ++ ")"
                | _    => "ghost " ++ x ++ " := " ++ val
  | .set     => match op with
                | .add => "ghost " ++ x ++ " := (Map.set !" ++ x ++ " " ++ val ++ " true)"
                | _    => "ghost " ++ x ++ " := " ++ val
  | _        => "ghost " ++ x ++ " := " ++ val

def acceptableGhostAssignEmissions
    (x : Ident) (t : GhostType) (op : AugOp) (e : GhostExpr) : List String :=
  let val := prettyContractExpr e
  -- Use augOpStr in the int branch so the membership proof goes
  -- through by `rfl` after case-splitting on (t, op). The 4 list
  -- entries cover the 4 surface patterns Module 6 may emit.
  [ "ghost " ++ x ++ " := !" ++ x ++ " " ++ augOpStr op ++ " " ++ val,
    "ghost " ++ x ++ " <- " ++ val,
    "ghost " ++ x ++ " := (Cons " ++ val ++ " !" ++ x ++ ")",
    "ghost " ++ x ++ " := (Map.set !" ++ x ++ " " ++ val ++ " true)",
    "ghost " ++ x ++ " := " ++ val ]

theorem emitGhostAssignCorrect
    (x : Ident) (t : GhostType) (op : AugOp) (e : GhostExpr) :
    emitGhostAssign x t op e
      ∈ acceptableGhostAssignEmissions x t op e := by
  unfold emitGhostAssign acceptableGhostAssignEmissions
  cases t with
  | int     => simp
  | string  => simp
  | array   => simp
  | dict    => simp
  | list    => cases op <;> simp
  | set     => cases op <;> simp
  | tuple2  => simp
  | tuple3  => simp
  | tuple4  => simp

/-- Final recursive fixpoint covering all 13 WhyMLStmt constructors. -/
def emitStmtFullComplete (s : AssignState) : WhyMLStmt → String
  | .wSkip                => "()"
  | .wAssign x e          => emitAssign s x e
  | .wAugAssign x op e    => emitAugAssign x op e
  | .wArraySet arr i v    => emitArraySet arr i v
  | .wSeq w1 w2           => emitStmtFullComplete s w1 ++ seqSep
                                ++ emitStmtFullComplete s w2
  | .wRaise exc           => emitRaise exc
  | .wLabel L             => emitLabel L
  | .wAssert cond msg     => emitAssert cond msg
  | .wIf cond t f         =>
      "if " ++ prettyExpr cond ++ " then begin" ++ nl
        ++ emitStmtFullComplete s t ++ nl
        ++ "end else begin" ++ nl
        ++ emitStmtFullComplete s f ++ nl
        ++ "end"
  | .wWhile invs vars cond body =>
      "while " ++ prettyExpr cond ++ " do" ++ nl
        ++ "invariant { " ++ prettyContractExpr (cConj invs) ++ " }" ++ nl
        ++ "variant { " ++ prettyContractExpr (cFirst vars) ++ " }" ++ nl
        ++ emitStmtFullComplete s body ++ nl
        ++ "done"
  | .wTryCatch body exc handler =>
      "try" ++ nl
        ++ emitStmtFullComplete s body ++ nl
        ++ "with " ++ exc ++ " -> " ++ nl
        ++ emitStmtFullComplete s handler ++ nl
        ++ "end"
  | .wGhostDecl x t e     => emitGhostDecl x t e
  | .wGhostAssign x t op e => emitGhostAssign x t op e

/-- Acceptable if-emissions: form A (with else), B (no else),
    C (no else, body_returns_value default 0). -/
def acceptableIfEmissions
    (s : AssignState) (cond : Expr) (t f : WhyMLStmt) : List String :=
  [ "if " ++ prettyExpr cond ++ " then begin" ++ nl
      ++ emitStmtFullComplete s t ++ nl
      ++ "end else begin" ++ nl
      ++ emitStmtFullComplete s f ++ nl ++ "end",
    "if " ++ prettyExpr cond ++ " then begin" ++ nl
      ++ emitStmtFullComplete s t ++ nl ++ "end",
    "if " ++ prettyExpr cond ++ " then begin" ++ nl
      ++ emitStmtFullComplete s t ++ nl
      ++ "end else begin" ++ nl ++ "  0" ++ nl ++ "end" ]

theorem emitIfCorrect (s : AssignState) (cond : Expr) (t f : WhyMLStmt) :
    emitStmtFullComplete s (.wIf cond t f)
      ∈ acceptableIfEmissions s cond t f := by
  simp [emitStmtFullComplete, acceptableIfEmissions]

def acceptableWhileEmissions
    (s : AssignState) (invs vars : List ContractExpr) (cond : Expr)
    (body : WhyMLStmt) : List String :=
  [ "while " ++ prettyExpr cond ++ " do" ++ nl
      ++ "invariant { " ++ prettyContractExpr (cConj invs) ++ " }" ++ nl
      ++ "variant { " ++ prettyContractExpr (cFirst vars) ++ " }" ++ nl
      ++ emitStmtFullComplete s body ++ nl ++ "done" ]

theorem emitWhileCorrect (s : AssignState) (invs vars : List ContractExpr)
    (cond : Expr) (body : WhyMLStmt) :
    emitStmtFullComplete s (.wWhile invs vars cond body)
      ∈ acceptableWhileEmissions s invs vars cond body := by
  simp [emitStmtFullComplete, acceptableWhileEmissions]

def acceptableTryCatchEmissions
    (s : AssignState) (body : WhyMLStmt) (exc : Ident)
    (handler : WhyMLStmt) : List String :=
  [ "try" ++ nl ++ emitStmtFullComplete s body ++ nl
      ++ "with " ++ exc ++ " -> " ++ nl
      ++ emitStmtFullComplete s handler ++ nl ++ "end" ]

theorem emitTryCatchCorrect (s : AssignState) (body : WhyMLStmt)
    (exc : Ident) (handler : WhyMLStmt) :
    emitStmtFullComplete s (.wTryCatch body exc handler)
      ∈ acceptableTryCatchEmissions s body exc handler := by
  simp [emitStmtFullComplete, acceptableTryCatchEmissions]

/-- Tie-ins to gen for the five new constructs. -/
theorem emitStmtFullCompleteIfCorrect (s : AssignState)
    (cond : Expr) (t f : Stmt) :
    emitStmtFullComplete s (gen (.ite cond t f))
      ∈ acceptableIfEmissions s cond (gen t) (gen f) := by
  show emitStmtFullComplete s (.wIf cond (gen t) (gen f))
        ∈ acceptableIfEmissions s cond (gen t) (gen f)
  exact emitIfCorrect s cond (gen t) (gen f)

theorem emitStmtFullCompleteWhileCorrect (s : AssignState)
    (inv var : ContractExpr) (cond : Expr) (body : Stmt) :
    emitStmtFullComplete s (gen (.while_ inv var cond body))
      ∈ acceptableWhileEmissions s [inv] [var] cond (gen body) := by
  show emitStmtFullComplete s (.wWhile [inv] [var] cond (gen body))
        ∈ acceptableWhileEmissions s [inv] [var] cond (gen body)
  exact emitWhileCorrect s [inv] [var] cond (gen body)

theorem emitStmtFullCompleteTryCatchCorrect (s : AssignState)
    (body : Stmt) (exc : Ident) (handler : Stmt) :
    emitStmtFullComplete s (gen (.tryCatch body exc handler))
      ∈ acceptableTryCatchEmissions s (gen body) exc (gen handler) := by
  show emitStmtFullComplete s (.wTryCatch (gen body) exc (gen handler))
        ∈ acceptableTryCatchEmissions s (gen body) exc (gen handler)
  exact emitTryCatchCorrect s (gen body) exc (gen handler)

theorem emitStmtFullCompleteGhostDeclCorrect (s : AssignState)
    (x : Ident) (t : GhostType) (e : GhostExpr) :
    emitStmtFullComplete s (gen (.ghostDecl x t e))
      ∈ acceptableGhostDeclEmissions x t e := by
  show emitGhostDecl x t e ∈ acceptableGhostDeclEmissions x t e
  exact emitGhostDeclCorrect x t e

theorem emitStmtFullCompleteGhostAssignCorrect (s : AssignState)
    (x : Ident) (t : GhostType) (op : AugOp) (e : GhostExpr) :
    emitStmtFullComplete s (gen (.ghostAssign x t op e))
      ∈ acceptableGhostAssignEmissions x t op e := by
  show emitGhostAssign x t op e ∈ acceptableGhostAssignEmissions x t op e
  exact emitGhostAssignCorrect x t op e

end PyCSL
