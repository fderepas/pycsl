/-
  DesugarDef.lean — Pure desugaring transformation
  Port of the desugar function from Phase3b_Desugar.v

  Split from Desugar.lean: this file imports only AST (not SOS),
  so WP.lean can import it without pulling in the exec relation.
-/
import PyCSL.AST

def forIdx : Ident := "_pycsl_idx"

def freshInStmt (x : Ident) : Stmt → Bool
  | .skip             => true
  | .assign y _       => x != y
  | .augAssign y _ _  => x != y
  | .arraySet _ _ _   => true
  | .seq s1 s2        => freshInStmt x s1 && freshInStmt x s2
  | .ite _ s1 s2      => freshInStmt x s1 && freshInStmt x s2
  | .while_ _ _ _ b   => freshInStmt x b
  | .for_ y _ _ _ b   => x != y && freshInStmt x b
  | .ret _            => true
  | .continue_        => true

def desugar : Stmt → Stmt
  | .for_ x arr inv var body =>
    let init := Stmt.assign forIdx (.int 0)
    let guard := Expr.binop .sub
      (Expr.var forIdx)
      (Expr.var arr)  -- simplified: uses arr as length proxy
    let bindElem := Stmt.assign x (.subscript arr (.var forIdx))
    let incIdx := Stmt.augAssign forIdx .add (.int 1)
    let loopBody := Stmt.seq bindElem (Stmt.seq body incIdx)
    Stmt.seq init (.while_ inv var guard loopBody)
  | .seq s1 s2        => .seq (desugar s1) (desugar s2)
  | .ite c s1 s2      => .ite c (desugar s1) (desugar s2)
  | .while_ i v c b   => .while_ i v c (desugar b)
  | s                  => s

-- =====================================================================
-- Phase 1a — Category B desugaring functions
-- Features: 28 (tuple unpacking), 29 (walrus :=), 30 (match statement)
-- =====================================================================

-- Feature 29 — Walrus operator :=
-- In statement position, (x := e) is identical to plain assignment.
def walrusAssign (x : Ident) (e : Expr) : Stmt := .assign x e

-- Feature 28 — Tuple unpacking (2-element case)
-- Unpack arr[0] into x and arr[1] into y.
def tupleUnpack2 (arr x y : Ident) : Stmt :=
  .seq (.assign x (.subscript arr (.int 0)))
       (.assign y (.subscript arr (.int 1)))

-- Feature 30 — Match statement
-- Desugar integer-pattern match arms into a nested if/else chain.
-- Condition (scrutinee - n) is falsy (0) exactly when scrutinee = n,
-- so the matching body goes in the *else* branch.
def desugarMatch (scrutinee : Expr) : List (Int × Stmt) → Stmt → Stmt
  | [],            default => default
  | (n, body) :: rest, default =>
      .ite (.binop .sub scrutinee (.int n))
           (desugarMatch scrutinee rest default)
           body
