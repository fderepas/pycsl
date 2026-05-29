/-
  EmitAssign.lean — Sub-α.2: full state coverage for wAssign

  Lean mirror of `rocq/Phase6L_EmitAssign.v`. See that file's header
  for the full design notes (branch enumeration, eliminated branches,
  presentational gap, deferred Q4 work).

  Summary: formalizes Module 6's `_handle_assign_stmt` for inputs of
  formal `Expr` type. Module 6 has 5+ state-dependent branches; on
  formal `Expr` (6 constructors) only 3 distinct branches can fire:

    1. shared var assignment        → `x := e`
    2. fresh local, default kind    → `let x = ref e in\n`
    2'. fresh local, bounded_int    → `let x = ref (e : intN) in\n`
    3. existing local               → `x := e`

  The theorem `emitAssignCorrect` proves the formal emission lies in
  the acceptable set for every state.

  Python source: src/pycsl/module6_whyml/statements.py:61-103
-/

import PyCSL.AST
import PyCSL.WhyML
import PyCSL.StmtGen
import PyCSL.EmitStmtSurface

namespace PyCSL

open WhyMLStmt

/-- Integer pretty-printer for `Expr.int` literals. Models Module 6's
    decimal emission. -/
def digitChar : Nat → Char
  | 0 => '0' | 1 => '1' | 2 => '2' | 3 => '3'
  | 4 => '4' | 5 => '5' | 6 => '6' | 7 => '7'
  | 8 => '8' | _ => '9'

partial def natToStringAux (n : Nat) : String :=
  if n < 10 then String.singleton (digitChar n)
  else natToStringAux (n / 10) ++ String.singleton (digitChar (n % 10))

def natToStringPP (n : Nat) : String := natToStringAux n

def zToStringPP (z : Int) : String :=
  if z = 0 then "0"
  else if z < 0 then "-" ++ natToStringPP z.natAbs
  else natToStringPP z.toNat

def prettyBinop : Binop → String
  | .add => "+" | .sub => "-" | .mul => "*" | .div => "/" | .mod_ => "mod"

def prettyCmpOp : CmpOp → String
  | .eq => "=" | .ne => "<>"
  | .lt => "<" | .le => "<="
  | .gt => ">" | .ge => ">="

/-- Expression pretty-printer for the 6 formal `Expr` constructors.
    Variables are emitted bare (no `!` ref-deref) — see "presentational
    gap" in the Rocq header. -/
def prettyExpr : Expr → String
  | .int n           => zToStringPP n
  | .var x           => x
  | .subscript a i   => a ++ "[" ++ prettyExpr i ++ "]"
  | .len a           => "(length " ++ a ++ ")"
  | .binop op e1 e2  => "(" ++ prettyExpr e1 ++ " " ++ prettyBinop op
                          ++ " " ++ prettyExpr e2 ++ ")"
  | .neg e1          => "(- " ++ prettyExpr e1 ++ ")"
  | .cmp op e1 e2    => "(" ++ prettyExpr e1 ++ " " ++ prettyCmpOp op
                          ++ " " ++ prettyExpr e2 ++ ")"
  | .fieldGet obj f  => obj ++ "." ++ f
  | .call func args  =>
      func ++ "(" ++ String.intercalate ", " (args.map prettyExpr) ++ ")"

/-- The state Module 6 consults at `_handle_assign_stmt`. -/
structure AssignState where
  sharedVars   : List Ident
  declaredRefs : List Ident
  boundedInt   : Option String
  deriving Repr

def identIn (x : Ident) (xs : List Ident) : Bool := xs.contains x

/-- Formal model of `_handle_assign_stmt` for `Expr`-typed RHS.
    Three branches; see Rocq header for the full enumeration. -/
def emitAssign (s : AssignState) (x : Ident) (e : Expr) : String :=
  if identIn x s.sharedVars then
    -- Branch 1: shared var
    x ++ " := " ++ prettyExpr e
  else if !identIn x s.declaredRefs then
    -- Branch 2: fresh local
    match s.boundedInt with
    | some bits =>
        -- Branch 2e: bounded_int
        "let " ++ x ++ " = ref (" ++ prettyExpr e
          ++ " : int" ++ bits ++ ") in\n"
    | none =>
        -- Branch 2g: default
        "let " ++ x ++ " = ref " ++ prettyExpr e ++ " in\n"
  else
    -- Branch 5: existing local
    x ++ " := " ++ prettyExpr e

/-- Acceptable surface emissions for `WAssign x e` on a formal `Expr`. -/
def acceptableAssignEmissions
    (s : AssignState) (x : Ident) (e : Expr) : List String :=
  let assignForm := x ++ " := " ++ prettyExpr e
  let letDefault := "let " ++ x ++ " = ref " ++ prettyExpr e ++ " in\n"
  let letBounded :=
    match s.boundedInt with
    | some bits => "let " ++ x ++ " = ref (" ++ prettyExpr e
                          ++ " : int" ++ bits ++ ") in\n"
    | none      => letDefault
  [ assignForm, letDefault, letBounded ]

/-- Correctness: whichever state Module 6 is in, the emitted text
    lies in the acceptable set. -/
theorem emitAssignCorrect (s : AssignState) (x : Ident) (e : Expr) :
    emitAssign s x e ∈ acceptableAssignEmissions s x e := by
  unfold emitAssign acceptableAssignEmissions
  -- Case split: identIn x sharedVars (branch 1) vs not.
  cases hsh : identIn x s.sharedVars
  · -- branch ≠ shared. Split on declaredRefs.
    cases hdc : identIn x s.declaredRefs
    · -- fresh local. Split on boundedInt.
      cases s.boundedInt
      · -- bounded_int = none → default-let
        simp
      · -- bounded_int = some bits → bounded-int-let
        simp
    · -- existing local
      simp
  · -- shared var
    simp

/-- State-aware variant of `emitStmtString` (Sub-α pilot's state-free
    function). For `wAssign`, dispatches with the state in hand; for
    other constructors falls back to the pilot's emission. -/
def emitStmtStringState (s : AssignState) (ws : WhyMLStmt) : String :=
  match ws with
  | .wSkip       => "()"
  | .wAssign x e => emitAssign s x e
  | _            => emitStmtString ws

/-- Sub-α.2 main theorem: `emitStmtStringState s (gen (.assign x e))`
    lies in the acceptable set for every state. -/
theorem emitStmtStringStateAssignCorrect
    (s : AssignState) (x : Ident) (e : Expr) :
    emitStmtStringState s (gen (.assign x e))
      ∈ acceptableAssignEmissions s x e := by
  show emitAssign s x e ∈ acceptableAssignEmissions s x e
  exact emitAssignCorrect s x e

/-- Sanity: `emitStmtStringState` on `.skip` matches the pilot. -/
theorem emitStmtStringStateSkip (s : AssignState) :
    emitStmtStringState s (gen .skip) = "()" := by
  simp [emitStmtStringState, gen]

/-- Canonical (empty-state) instance for smoke tests. -/
def canonicalState : AssignState :=
  { sharedVars := [], declaredRefs := [], boundedInt := none }

theorem emitAssignCanonicalLet (x : Ident) (e : Expr) :
    emitAssign canonicalState x e =
      "let " ++ x ++ " = ref " ++ prettyExpr e ++ " in\n" := by
  simp [emitAssign, canonicalState, identIn]

end PyCSL
