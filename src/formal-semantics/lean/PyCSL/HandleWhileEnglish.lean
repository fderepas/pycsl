/-
  HandleWhileEnglish.lean — Lean refinement of english-07.md.
  Companion of src/formal-semantics/rocq/Phase6e_HandleWhileEnglish.v.

  Single-branch emitter for while loop with invariant + variant.
  Reduces to the existing umbrella lemma wpGen_while.
-/

import PyCSL.AST
import PyCSL.State
import PyCSL.WP
import PyCSL.WhyML
import PyCSL.WPW
import PyCSL.StmtGen
import PyCSL.CorrSimple
import PyCSL.CorrLoops
import PyCSL.CorrExc

namespace Pycsl.Reference.Module6

inductive WhileBranch where
  | brWhileOnly

def genWhileByBranch : WhileBranch → ContractExpr → ContractExpr → Expr → Stmt →  WhyMLStmt
  | _, inv, var, cond, body => gen (.while_ inv var cond body)

theorem genWhileByBranch_eq_gen (b : WhileBranch) (inv var : ContractExpr) (cond : Expr) (body : Stmt) :
    genWhileByBranch b inv var cond body = gen (.while_ inv var cond body) := by
  cases b <;> rfl

-- Equality theorem: the dispatcher collapses to `gen` for any branch.
-- Anyone needing the WP equivalence applies `wpGen_while` to this
-- equality. The proof is by reflexivity per arm.
theorem handleWhileBranchesCorrect (b : WhileBranch) (inv var : ContractExpr) (cond : Expr) (body : Stmt) :
    genWhileByBranch b inv var cond body = gen (.while_ inv var cond body) := by
  cases b <;> rfl

end Pycsl.Reference.Module6
