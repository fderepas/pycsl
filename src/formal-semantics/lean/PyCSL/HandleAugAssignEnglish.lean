/-
  HandleAugAssignEnglish.lean — Lean refinement of english-02.md.
  Companion of src/formal-semantics/rocq/Phase6e_HandleAugAssignEnglish.v.

  Single-branch emitter for augmented assignment (x += e style).
  Reduces to the existing umbrella lemma wpGen_augAssign.
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

inductive AugAssignBranch where
  | brAugAssignOnly

def genAugAssignByBranch : AugAssignBranch → Ident → Binop → Expr →  WhyMLStmt
  | _, x, op, e => gen (.augAssign x op e)

theorem genAugAssignByBranch_eq_gen (b : AugAssignBranch) (x : Ident) (op : Binop) (e : Expr) :
    genAugAssignByBranch b x op e = gen (.augAssign x op e) := by
  cases b <;> rfl

-- Equality theorem: the dispatcher collapses to `gen` for any branch.
-- Anyone needing the WP equivalence applies `wpGen_augAssign` to this
-- equality. The proof is by reflexivity per arm.
theorem handleAugAssignBranchesCorrect (b : AugAssignBranch) (x : Ident) (op : Binop) (e : Expr) :
    genAugAssignByBranch b x op e = gen (.augAssign x op e) := by
  cases b <;> rfl

end Pycsl.Reference.Module6
