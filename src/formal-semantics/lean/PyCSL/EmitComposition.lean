/-
  EmitComposition.lean — Sub-α.14: composition lemma

  Lean mirror of `rocq/Phase6L_EmitComposition.v`. See that file's
  header for full design notes.

  Provides:
    - `acceptableEmit : AssignState → Stmt → List String` — maps
      each Stmt constructor to its per-construct acceptable surface
      set, recursing on sub-stmts.
    - `emitStmtFullCompleteSound` — the composition theorem proved
      by case analysis on Stmt, discharged by the per-construct
      lemmas (Sub-α.1 through .13).
-/

import PyCSL.AST
import PyCSL.WhyML
import PyCSL.StmtGen
import PyCSL.EmitStmtSurface
import PyCSL.EmitAssign
import PyCSL.EmitAugAssign
import PyCSL.EmitArraySet
import PyCSL.EmitSeq
import PyCSL.EmitBlocks

namespace PyCSL

open WhyMLStmt

/-- Per-Stmt-constructor acceptable surface emissions. Mirrors the
    Rocq `acceptable_emit`. For compound constructors, the
    structural shape uses `emitStmtFullComplete` on the recursive
    sub-stmts via `gen`. -/
def acceptableEmit (state : AssignState) : Stmt → List String
  | .skip                       => acceptableSkipEmissions
  | .assign x e                 => acceptableAssignEmissions state x e
  | .augAssign x op e           => acceptableAugAssignEmissions x op e
  | .arraySet arr i v           => acceptableArraySetEmissions arr i v
  | .seq s1 s2                  =>
      [ emitStmtFullComplete state (gen s1) ++ seqSep
          ++ emitStmtFullComplete state (gen s2) ]
  | .ite cond t f               =>
      acceptableIfEmissions state cond (gen t) (gen f)
  | .while_ inv var cond body   =>
      acceptableWhileEmissions state [inv] [var] cond (gen body)
  | .for_ x arr inv var body aim =>
      -- SFor desugars into a nested compound; singleton acceptable set.
      [ emitStmtFullComplete state (gen (.for_ x arr inv var body aim)) ]
  | .ret e                      =>
      [ emitAssign state "\\result" e ++ seqSep ++ "raise PyCSL_Return" ]
  | .continue_                  => acceptableRaiseEmissions .excContinue
  | .break_                     => acceptableRaiseEmissions .excBreak
  | .assert_ cond msg           => acceptableAssertEmissions cond msg
  | .tupleUnpack _ _            => acceptableSkipEmissions  -- gen → wSkip
  | .ghostDecl x t e            => acceptableGhostDeclEmissions x t e
  | .ghostAssign x t op e       => acceptableGhostAssignEmissions x t op e
  | .label_ L                   => acceptableLabelEmissions L
  | .raise_ exc                 => acceptableRaiseEmissions (.excNamed exc)
  | .tryCatch body exc handler  =>
      acceptableTryCatchEmissions state (gen body) exc (gen handler)
  | .fieldAssign _ _ _          => acceptableSkipEmissions  -- gen → wSkip
  | .fieldAugAssign _ _ _ _     => acceptableSkipEmissions  -- gen → wSkip
  | .critical _ body            => [ emitStmtFullComplete state (gen body) ]
  | .threadEntry body           => [ emitStmtFullComplete state (gen body) ]
  | .acquires _                 => acceptableSkipEmissions  -- gen → wSkip
  | .releases _                 => acceptableSkipEmissions  -- gen → wSkip
  | .call _ _ _                 => acceptableSkipEmissions  -- gen → wSkip; Phase 8 lambda gap

/-- The composition theorem: for every stmt constructor,
    `emitStmtFullComplete state (gen s)` lies in `acceptableEmit
    state s`. Proved by case analysis on `s` and discharged by the
    per-construct lemmas. -/
theorem emitStmtFullCompleteSound (state : AssignState) (s : Stmt) :
    emitStmtFullComplete state (gen s) ∈ acceptableEmit state s := by
  cases s with
  | skip =>
      simp [acceptableEmit, gen, emitStmtFullComplete, acceptableSkipEmissions]
  | assign x e =>
      simp [acceptableEmit, gen, emitStmtFullComplete]
      exact emitAssignCorrect state x e
  | augAssign x op e =>
      simp [acceptableEmit, gen, emitStmtFullComplete]
      exact emitAugAssignCorrect x op e
  | arraySet arr i v =>
      simp [acceptableEmit, gen, emitStmtFullComplete]
      exact emitArraySetCorrect arr i v
  | seq s1 s2 =>
      simp [acceptableEmit, gen, emitStmtFullComplete]
  | ite cond t f =>
      show emitStmtFullComplete state (.wIf cond (gen t) (gen f))
            ∈ acceptableIfEmissions state cond (gen t) (gen f)
      exact emitIfCorrect state cond (gen t) (gen f)
  | while_ inv var cond body =>
      show emitStmtFullComplete state (.wWhile [inv] [var] cond (gen body))
            ∈ acceptableWhileEmissions state [inv] [var] cond (gen body)
      exact emitWhileCorrect state [inv] [var] cond (gen body)
  | for_ x arr inv var body =>
      simp [acceptableEmit]
  | ret e =>
      simp [acceptableEmit, gen, emitStmtFullComplete, seqSep, emitRaise, excToString]
  | continue_ =>
      show emitRaise .excContinue ∈ acceptableRaiseEmissions .excContinue
      exact emitRaiseCorrect .excContinue
  | break_ =>
      show emitRaise .excBreak ∈ acceptableRaiseEmissions .excBreak
      exact emitRaiseCorrect .excBreak
  | assert_ cond msg =>
      simp [acceptableEmit, gen, emitStmtFullComplete]
      exact emitAssertCorrect cond msg
  | tupleUnpack _ _ =>
      simp [acceptableEmit, gen, emitStmtFullComplete, acceptableSkipEmissions]
  | ghostDecl x t e =>
      simp [acceptableEmit, gen, emitStmtFullComplete]
      exact emitGhostDeclCorrect x t e
  | ghostAssign x t op e =>
      simp [acceptableEmit, gen, emitStmtFullComplete]
      exact emitGhostAssignCorrect x t op e
  | label_ L =>
      simp [acceptableEmit, gen, emitStmtFullComplete]
      exact emitLabelCorrect L
  | raise_ exc =>
      show emitRaise (.excNamed exc) ∈ acceptableRaiseEmissions (.excNamed exc)
      exact emitRaiseCorrect (.excNamed exc)
  | tryCatch body exc handler =>
      show emitStmtFullComplete state (.wTryCatch (gen body) exc (gen handler))
            ∈ acceptableTryCatchEmissions state (gen body) exc (gen handler)
      exact emitTryCatchCorrect state (gen body) exc (gen handler)
  | fieldAssign _ _ _ =>
      simp [acceptableEmit, gen, emitStmtFullComplete, acceptableSkipEmissions]
  | fieldAugAssign _ _ _ _ =>
      simp [acceptableEmit, gen, emitStmtFullComplete, acceptableSkipEmissions]
  | critical _ body =>
      simp [acceptableEmit, gen]
  | threadEntry body =>
      simp [acceptableEmit, gen]
  | acquires _ =>
      simp [acceptableEmit, gen, emitStmtFullComplete, acceptableSkipEmissions]
  | releases _ =>
      simp [acceptableEmit, gen, emitStmtFullComplete, acceptableSkipEmissions]
  | call _ _ _ =>
      -- Phase 8 lambda gap: gen (.call r fn arg) = .wSkip, so emission is
      -- `()` which is in `acceptableSkipEmissions`.
      simp [acceptableEmit, gen, emitStmtFullComplete, acceptableSkipEmissions]

/-- Existential corollary: the emission is some specific string in
    the acceptable set. -/
theorem emitStmtFullCompleteInAcceptable
    (state : AssignState) (s : Stmt) :
    ∃ out, emitStmtFullComplete state (gen s) = out ∧
           out ∈ acceptableEmit state s := by
  exact ⟨_, rfl, emitStmtFullCompleteSound state s⟩

end PyCSL
