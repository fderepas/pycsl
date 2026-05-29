/-
  HandleGhostAssignEnglish.lean — Lean refinement of english-11.md.
  Companion of src/formal-semantics/rocq/Phase6e_HandleGhostAssignEnglish.v.

  Single-branch emitter for ghost variable assignment (reg-state preserved).
  Reduces to the existing umbrella lemma wpGen_ghostAssign.
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

inductive GhostAssignBranch where
  | brGhostAssignOnly

def genGhostAssignByBranch : GhostAssignBranch → Ident → GhostType → AugOp → GhostExpr →  WhyMLStmt
  | _, x, t, op, e => gen (.ghostAssign x t op e)

theorem genGhostAssignByBranch_eq_gen (b : GhostAssignBranch) (x : Ident) (t : GhostType) (op : AugOp) (e : GhostExpr) :
    genGhostAssignByBranch b x t op e = gen (.ghostAssign x t op e) := by
  cases b <;> rfl

-- Equality theorem: the dispatcher collapses to `gen` for any branch.
-- Anyone needing the WP equivalence applies `wpGen_ghostAssign` to this
-- equality. The proof is by reflexivity per arm.
theorem handleGhostAssignBranchesCorrect (b : GhostAssignBranch) (x : Ident) (t : GhostType) (op : AugOp) (e : GhostExpr) :
    genGhostAssignByBranch b x t op e = gen (.ghostAssign x t op e) := by
  cases b <;> rfl

end Pycsl.Reference.Module6
