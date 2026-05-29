/-
  DesugarDef.lean — Pure desugaring transformation
  Port of Phase3b_DesugarDef.v (all phases)

  Split from Desugar.lean: this file imports only AST (not SOS),
  so WP.lean can import it without pulling in the exec relation.
-/
import PyCSL.AST

def forIdx : Ident := "_pycsl_idx"

def freshInStmt (x : Ident) : Stmt → Bool
  | .skip               => true
  | .assign y _         => x != y
  | .augAssign y _ _    => x != y
  | .arraySet arr _ _   => x != arr
  | .seq s1 s2          => freshInStmt x s1 && freshInStmt x s2
  | .ite _ s1 s2        => freshInStmt x s1 && freshInStmt x s2
  | .while_ _ _ _ b     => freshInStmt x b
  | .for_ y arr _ _ b _ => x != y && x != arr && freshInStmt x b
  | .ret _              => true
  | .continue_          => true
  | .break_             => true
  | .assert_ _ _        => true
  | .tupleUnpack _ _    => true
  | .ghostDecl y _ _    => x != y
  | .ghostAssign y _ _ _=> x != y
  | .label_ _           => true
  | .raise_ _           => true
  | .tryCatch b _ h     => freshInStmt x b && freshInStmt x h
  | .fieldAssign _ _ _  => true
  | .fieldAugAssign _ _ _ _ => true
  | .critical _ b       => freshInStmt x b
  | .threadEntry b      => freshInStmt x b

-- liftContinue incStmt s: replace every shallow continue_ in s with (seq incStmt continue_).
-- "Shallow" means: recurse into seq/ite/tryCatch/critical/threadEntry but
-- NOT into while_/for_ (those handle their own continue).
-- Used by desugar to ensure continue in a for-body increments forIdx before looping back.
-- @[simp] ensures all equation lemmas are simp lemmas, enabling `simp [wp]` in liftContinue_wp.
@[simp] def liftContinue (incStmt : Stmt) : Stmt → Stmt
  | .continue_              => .seq incStmt .continue_
  | .seq s1 s2              => .seq (liftContinue incStmt s1) (liftContinue incStmt s2)
  | .ite c s1 s2            => .ite c (liftContinue incStmt s1) (liftContinue incStmt s2)
  | .tryCatch b exc h       => .tryCatch (liftContinue incStmt b) exc (liftContinue incStmt h)
  | .critical m b           => .critical m (liftContinue incStmt b)
  | .threadEntry b          => .threadEntry (liftContinue incStmt b)
  -- Leaf constructors: identity (explicit to generate clean equation lemmas)
  | .skip                   => .skip
  | .break_                 => .break_
  | .assign x e             => .assign x e
  | .augAssign x op e       => .augAssign x op e
  | .arraySet arr i v       => .arraySet arr i v
  | .ret e                  => .ret e
  | .assert_ c m            => .assert_ c m
  | .tupleUnpack x y        => .tupleUnpack x y
  | .ghostDecl x t e        => .ghostDecl x t e
  | .ghostAssign x t op e   => .ghostAssign x t op e
  | .label_ L               => .label_ L
  | .raise_ exc             => .raise_ exc
  | .fieldAssign f x v      => .fieldAssign f x v
  | .fieldAugAssign f x op v => .fieldAugAssign f x op v
  | .while_ inv var c body  => .while_ inv var c body
  | .for_ x arr inv var b aim => .for_ x arr inv var b aim

def desugar : Stmt → Stmt
  | .for_ x arr inv var body _ =>
    let init := Stmt.assign forIdx (.int 0)
    let guard := Expr.binop .sub (.len arr) (.var forIdx)
    let bindElem := Stmt.assign x (.subscript arr (.var forIdx))
    let incIdx := Stmt.augAssign forIdx .add (.int 1)
    -- liftContinue ensures continue_ in body increments forIdx before looping back
    let loopBody := Stmt.seq bindElem (Stmt.seq (liftContinue incIdx (desugar body)) incIdx)
    Stmt.seq init (.while_ inv var guard loopBody)
  | .seq s1 s2           => .seq (desugar s1) (desugar s2)
  | .ite c s1 s2         => .ite c (desugar s1) (desugar s2)
  | .while_ i v c b      => .while_ i v c (desugar b)
  | .tryCatch b exc h    => .tryCatch (desugar b) exc (desugar h)
  | .critical m b        => .critical m (desugar b)
  | .threadEntry b       => .threadEntry (desugar b)
  | s                    => s

-- =====================================================================
-- Phase 1a — Category B desugaring functions
-- =====================================================================

-- Feature 29 — Walrus operator :=
def walrusAssign (x : Ident) (e : Expr) : Stmt := .assign x e

-- Feature 28 — Tuple unpacking (2-element case)
def tupleUnpack2 (arr x y : Ident) : Stmt :=
  .seq (.assign x (.subscript arr (.int 0)))
       (.assign y (.subscript arr (.int 1)))

-- Feature 30 — Match statement
def desugarMatch (scrutinee : Expr) : List (Int × Stmt) → Stmt → Stmt
  | [],            default => default
  | (n, body) :: rest, default =>
      .ite (.binop .sub scrutinee (.int n))
           (desugarMatch scrutinee rest default)
           body
