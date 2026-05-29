/-
  HandleCriticalSectionEnglish.lean — Lean refinement of english-09.md.
  Companion of src/formal-semantics/rocq/Phase6e_HandleCriticalSectionEnglish.v.

  Single-branch emitter for mutex-protected critical section.
  Reduces to the existing umbrella lemma wpGen_critical.
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

inductive CriticalSectionBranch where
  | brCriticalSectionOnly

def genCriticalSectionByBranch : CriticalSectionBranch → Ident → Stmt →  WhyMLStmt
  | _, m, body => gen (.critical m body)

theorem genCriticalSectionByBranch_eq_gen (b : CriticalSectionBranch) (m : Ident) (body : Stmt) :
    genCriticalSectionByBranch b m body = gen (.critical m body) := by
  cases b <;> rfl

-- Equality theorem: the dispatcher collapses to `gen` for any branch.
-- Anyone needing the WP equivalence applies `wpGen_critical` to this
-- equality. The proof is by reflexivity per arm.
theorem handleCriticalSectionBranchesCorrect (b : CriticalSectionBranch) (m : Ident) (body : Stmt) :
    genCriticalSectionByBranch b m body = gen (.critical m body) := by
  cases b <;> rfl

end Pycsl.Reference.Module6
