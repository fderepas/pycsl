/-
  EmitStmtSurface.lean — Sub-α pilot

  Lean mirror of `rocq/Phase6L_EmitStmt.v`. See that file's header for
  the full design notes. This file replicates the same three pieces:

  1. `emitStmtString : WhyMLStmt → String` — formal model of Module 6's
     surface-syntax (WhyML text) emission. Indentation-free; the
     Python `indent` parameter at the call site adds whitespace prefix.

  2. `acceptableSkipEmissions` — singleton acceptable set for wSkip.

  3. `emitSkipCorrect` — the pilot correctness theorem.

  Subsequent PRs (Sub-α.2 through Sub-α.13) extend `emitStmtString`
  one constructor at a time.

  Naming: this module uses `emitStmtString` and `emitSkipCorrect` to
  disambiguate from `EmitVcList.lean`'s `emitStmt_correct`, which is
  about VC-list emission (a different layer).

  Python correspondent:
  `src/pycsl/module6_whyml/statements.py:_stmts_to_whyml`
  (Pass case at line 1115: `code = f"{indent}()"`).
-/

import PyCSL.AST
import PyCSL.WhyML
import PyCSL.StmtGen

namespace PyCSL

open WhyMLStmt

/-- Formal model of Module 6's WhyML emission.

    Returns the bare WhyML expression for a statement. Indentation
    is a separate concern handled by Module 6's `indent` parameter
    in `_stmts_to_whyml`.

    This pilot fully defines only the wSkip case. Other constructors
    return `""` as a stub; subsequent PRs extend match arms one at a
    time, each accompanied by its own per-construct correctness
    theorem. -/
def emitStmtString : WhyMLStmt → String
  | .wSkip => "()"

  -- Pending per-construct PRs (Sub-α.2 through Sub-α.13).
  -- Each placeholder will be replaced with the real emission in a
  -- dedicated PR. Until then they return "" so the function is
  -- total; the correctness theorems below only assert wSkip.
  | .wAssign _ _            => ""
  | .wAugAssign _ _ _       => ""
  | .wArraySet _ _ _        => ""
  | .wSeq _ _               => ""
  | .wIf _ _ _              => ""
  | .wWhile _ _ _ _         => ""
  | .wRaise _               => ""
  | .wTryCatch _ _ _        => ""
  | .wGhostDecl _ _ _       => ""
  | .wGhostAssign _ _ _ _   => ""
  | .wLabel _               => ""
  | .wAssert _ _            => ""

/-- Acceptable surface emissions for wSkip.

    Module 6 emits the literal `()` (Python source:
    `module6_whyml/statements.py:1115` — `code = f"{indent}()"`).
    The acceptable set is a singleton. -/
def acceptableSkipEmissions : List String := ["()"]

/-- The pilot theorem: for every input that reaches `gen .skip`, the
    formal emission lies in the acceptable set. -/
theorem emitSkipCorrect :
    emitStmtString (gen .skip) ∈ acceptableSkipEmissions := by
  simp [emitStmtString, gen, acceptableSkipEmissions]

/-- Sanity: `emitStmtString` is the identity-after-`gen` on `.skip`. -/
theorem emitStmtStringGenSkip : emitStmtString (gen .skip) = "()" := by
  simp [emitStmtString, gen]

end PyCSL
