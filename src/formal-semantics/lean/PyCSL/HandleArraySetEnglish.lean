/-
  HandleArraySetEnglish.lean — Lean refinement of english-04.md.
  Companion of src/formal-semantics/rocq/Phase6e_HandleArraySetEnglish.v.

  Single-branch emitter for array element assignment arr[i] = v.
  Reduces to the existing umbrella lemma wpGen_arraySet.
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

inductive ArraySetBranch where
  | brArraySetOnly

def genArraySetByBranch : ArraySetBranch → Ident → Expr → Expr →  WhyMLStmt
  | _, arr, i, v => gen (.arraySet arr i v)

theorem genArraySetByBranch_eq_gen (b : ArraySetBranch) (arr : Ident) (i v : Expr) :
    genArraySetByBranch b arr i v = gen (.arraySet arr i v) := by
  cases b <;> rfl

-- Equality theorem: the dispatcher collapses to `gen` for any branch.
-- Anyone needing the WP equivalence applies `wpGen_arraySet` to this
-- equality. The proof is by reflexivity per arm.
theorem handleArraySetBranchesCorrect (b : ArraySetBranch) (arr : Ident) (i v : Expr) :
    genArraySetByBranch b arr i v = gen (.arraySet arr i v) := by
  cases b <;> rfl

end Pycsl.Reference.Module6
