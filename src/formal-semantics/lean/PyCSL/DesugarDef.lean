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
