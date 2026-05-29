/-
  HandleTryEnglish.lean — Lean refinement of english-06.md.
  Companion of src/formal-semantics/rocq/Phase6e_HandleTryEnglish.v.

  Single-branch emitter for try/except exception handling.
  Reduces to the existing umbrella lemma wpGen_tryCatch.
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

inductive TryBranch where
  | brTryOnly

def genTryByBranch : TryBranch → Stmt → Ident → Stmt →  WhyMLStmt
  | _, body, exc, handler => gen (.tryCatch body exc handler)

theorem genTryByBranch_eq_gen (b : TryBranch) (body : Stmt) (exc : Ident) (handler : Stmt) :
    genTryByBranch b body exc handler = gen (.tryCatch body exc handler) := by
  cases b <;> rfl

-- Equality theorem: the dispatcher collapses to `gen` for any branch.
-- Anyone needing the WP equivalence applies `wpGen_tryCatch` to this
-- equality. The proof is by reflexivity per arm.
theorem handleTryBranchesCorrect (b : TryBranch) (body : Stmt) (exc : Ident) (handler : Stmt) :
    genTryByBranch b body exc handler = gen (.tryCatch body exc handler) := by
  cases b <;> rfl

end Pycsl.Reference.Module6
