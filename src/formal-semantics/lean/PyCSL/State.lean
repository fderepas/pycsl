/-
  State.lean — Values, state, and concrete evaluators
  Port of Phase2_State.v
-/
import PyCSL.AST

inductive Val where
  | int   (n : Int)
  | array (a : List Int)
  deriving DecidableEq, Repr

abbrev State := List (Ident × Val)

def lookup (st : State) (x : Ident) : Option Val :=
  match st with
  | [] => none
  | (y, v) :: rest => if x == y then some v else lookup rest x

def update (st : State) (x : Ident) (v : Val) : State := (x, v) :: st

def arrayUpdate (st : State) (arr : Ident) (i : Int) (v : Int) : State :=
  match lookup st arr with
  | some (.array a) =>
    let idx := i.toNat
    if 0 ≤ i ∧ i < a.length then
      let a' := a.take idx ++ [v] ++ a.drop (idx + 1)
      update st arr (.array a')
    else st
  | _ => st

def evalBinopZ (op : Binop) (n1 n2 : Int) : Int :=
  match op with
  | .add => n1 + n2
  | .sub => n1 - n2
  | .mul => n1 * n2
  | .div => if n2 == 0 then 0 else n1 / n2

def evalExpr (st : State) : Expr → Val
  | .int n => .int n
  | .var x => (lookup st x).getD (.int 0)
  | .subscript arr i =>
    match lookup st arr, evalExpr st i with
    | some (.array a), .int n =>
      if 0 ≤ n ∧ n < a.length then .int (a.getD n.toNat 0)
      else .int 0
    | _, _ => .int 0
  | .binop op e1 e2 =>
    match evalExpr st e1, evalExpr st e2 with
    | .int n1, .int n2 => .int (evalBinopZ op n1 n2)
    | _, _ => .int 0
  | .neg e =>
    match evalExpr st e with
    | .int n => .int (-n)
    | v => v

def evalBool (st : State) (e : Expr) : Bool :=
  match evalExpr st e with
  | .int 0 => false
  | _ => true

def evalZ (st preSt : State) (result : Option Val) : ContractExpr → Int
  | .int n => n
  | .var x => match lookup st x with | some (.int n) => n | _ => 0
  | .result => match result with | some (.int n) => n | _ => 0
  | .length arr =>
    match lookup st arr with
    | some (.array a) => a.length
    | _ => 0
  | .subscript arr i =>
    let n := evalZ st preSt result i
    match lookup st arr with
    | some (.array a) =>
      if 0 ≤ n ∧ n < a.length then a.getD n.toNat 0
      else 0
    | _ => 0
  | .old e => evalZ preSt preSt result e
  | .binop op e1 e2 =>
    evalBinopZ op (evalZ st preSt result e1) (evalZ st preSt result e2)
  | .neg e => -(evalZ st preSt result e)
  | _ => 0

def evalContract (st preSt : State) (result : Option Val) : ContractExpr → Prop
  | .int n => n ≠ 0
  | .var x => match lookup st x with | some (.int 0) => False | _ => True
  | .result => match result with | some (.int 0) => False | _ => True
  | .length _ => evalZ st preSt result (.length "") ≠ 0
  | .subscript arr i => evalZ st preSt result (.subscript arr i) ≠ 0
  | .old e => evalZ st preSt result (.old e) ≠ 0
  | .binop op e1 e2 => evalZ st preSt result (.binop op e1 e2) ≠ 0
  | .neg e => evalZ st preSt result (.neg e) ≠ 0
  | .eq  e1 e2 => evalZ st preSt result e1 = evalZ st preSt result e2
  | .ne  e1 e2 => evalZ st preSt result e1 ≠ evalZ st preSt result e2
  | .lt  e1 e2 => evalZ st preSt result e1 < evalZ st preSt result e2
  | .le  e1 e2 => evalZ st preSt result e1 ≤ evalZ st preSt result e2
  | .gt  e1 e2 => evalZ st preSt result e1 > evalZ st preSt result e2
  | .ge  e1 e2 => evalZ st preSt result e1 ≥ evalZ st preSt result e2
  | .and e1 e2 => evalContract st preSt result e1 ∧ evalContract st preSt result e2
  | .or  e1 e2 => evalContract st preSt result e1 ∨ evalContract st preSt result e2
  | .not e => ¬ evalContract st preSt result e
  | .implies e1 e2 => evalContract st preSt result e1 → evalContract st preSt result e2
  | .iff e1 e2 => evalContract st preSt result e1 ↔ evalContract st preSt result e2
  | .forall_ x body =>
    ∀ n : Int, evalContract (update st x (.int n)) preSt result body
  | .exists_ x body =>
    ∃ n : Int, evalContract (update st x (.int n)) preSt result body

def evalVariant (st preSt : State) (e : ContractExpr) : Int :=
  evalZ st preSt none e
