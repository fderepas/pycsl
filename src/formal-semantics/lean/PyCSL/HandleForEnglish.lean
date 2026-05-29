/-
  HandleForEnglish.lean — Lean refinement of english-08.md.
  Companion of src/formal-semantics/rocq/Phase6e_HandleForEnglish.v.

  Single-branch emitter for for loop (desugared into a while).
  Reduces to the existing umbrella lemma wpGen_for.
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

inductive ForBranch where
  | brForOnly

def genForByBranch : ForBranch → Ident → Ident → ContractExpr → ContractExpr → Stmt →  WhyMLStmt
  | _, x, arr, inv, var, body => gen (.for_ x arr inv var body)

theorem genForByBranch_eq_gen (b : ForBranch) (x arr : Ident) (inv var : ContractExpr) (body : Stmt) :
    genForByBranch b x arr inv var body = gen (.for_ x arr inv var body) := by
  cases b <;> rfl

-- Equality theorem: the dispatcher collapses to `gen` for any branch.
-- Anyone needing the WP equivalence applies `wpGen_for` to this
-- equality. The proof is by reflexivity per arm.
theorem handleForBranchesCorrect (b : ForBranch) (x arr : Ident) (inv var : ContractExpr) (body : Stmt) :
    genForByBranch b x arr inv var body = gen (.for_ x arr inv var body) := by
  cases b <;> rfl

end Pycsl.Reference.Module6
