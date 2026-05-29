/-
  HandleIfEnglish.lean — Lean refinement of english-05.md.
  Companion of src/formal-semantics/rocq/Phase6e_HandleIfEnglish.v.

  Single-branch emitter for conditional statement with then/else branches.
  Reduces to the existing umbrella lemma wpGen_if.
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

inductive IfBranch where
  | brIfOnly

def genIfByBranch : IfBranch → Expr → Stmt → Stmt →  WhyMLStmt
  | _, cond, t, f => gen (.ite cond t f)

theorem genIfByBranch_eq_gen (b : IfBranch) (cond : Expr) (t f : Stmt) :
    genIfByBranch b cond t f = gen (.ite cond t f) := by
  cases b <;> rfl

-- Equality theorem: the dispatcher collapses to `gen` for any branch.
-- Anyone needing the WP equivalence applies `wpGen_if` to this
-- equality. The proof is by reflexivity per arm.
theorem handleIfBranchesCorrect (b : IfBranch) (cond : Expr) (t f : Stmt) :
    genIfByBranch b cond t f = gen (.ite cond t f) := by
  cases b <;> rfl

end Pycsl.Reference.Module6
