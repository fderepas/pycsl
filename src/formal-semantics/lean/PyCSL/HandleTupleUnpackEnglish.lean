/-
  HandleTupleUnpackEnglish.lean — Lean refinement of english-10.md.
  Companion of src/formal-semantics/rocq/Phase6e_HandleTupleUnpackEnglish.v.

  Single-branch emitter for multi-target unpacking (x, y = ...).
  Reduces to the existing umbrella lemma wpGen_tupleUnpack.
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

inductive TupleUnpackBranch where
  | brTupleUnpackOnly

def genTupleUnpackByBranch : TupleUnpackBranch → List Ident → Expr →  WhyMLStmt
  | _, xs, e => gen (.tupleUnpack xs e)

theorem genTupleUnpackByBranch_eq_gen (b : TupleUnpackBranch) (xs : List Ident) (e : Expr) :
    genTupleUnpackByBranch b xs e = gen (.tupleUnpack xs e) := by
  cases b <;> rfl

-- Equality theorem: the dispatcher collapses to `gen` for any branch.
-- Anyone needing the WP equivalence applies `wpGen_tupleUnpack` to this
-- equality. The proof is by reflexivity per arm.
theorem handleTupleUnpackBranchesCorrect (b : TupleUnpackBranch) (xs : List Ident) (e : Expr) :
    genTupleUnpackByBranch b xs e = gen (.tupleUnpack xs e) := by
  cases b <;> rfl

end Pycsl.Reference.Module6
