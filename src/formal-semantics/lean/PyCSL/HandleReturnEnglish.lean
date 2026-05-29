/-
  HandleReturnEnglish.lean — Lean refinement of english-03.md.
  Companion of src/formal-semantics/rocq/Phase6e_HandleReturnEnglish.v.

  Single-branch emitter for return statement (encoded as raise(Return,e)).
  Reduces to the existing umbrella lemma wpGen_return.
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

inductive ReturnBranch where
  | brReturnOnly

def genReturnByBranch : ReturnBranch → Expr →  WhyMLStmt
  | _, e => gen (.ret e)

theorem genReturnByBranch_eq_gen (b : ReturnBranch) (e : Expr) :
    genReturnByBranch b e = gen (.ret e) := by
  cases b <;> rfl

-- Equality theorem: the dispatcher collapses to `gen` for any branch.
-- Anyone needing the WP equivalence applies `wpGen_return` to this
-- equality. The proof is by reflexivity per arm.
theorem handleReturnBranchesCorrect (b : ReturnBranch) (e : Expr) :
    genReturnByBranch b e = gen (.ret e) := by
  cases b <;> rfl

end Pycsl.Reference.Module6
