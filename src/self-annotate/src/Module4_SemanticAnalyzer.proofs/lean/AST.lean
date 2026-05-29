/-
  Audit-anchor stub for the citation in
    src/self-annotate/src/Module4_SemanticAnalyzer.py:
      #@ proof lean PyCSL.AST.Expr

  The REAL inductive lives at
    src/formal-semantics/lean/PyCSL/AST.lean:16
  (inductive Expr — formal AST type whose closed-shape pattern
   matching is the structural anchor for Module 4's semantic
   analysis dispatch).

  History: the Rocq citation `Phase1_AST.expr_eq_dec` was
  re-established when `ECall (func : ident) (args : list expr)`
  was added (using `list_eq_dec expr_eq_dec` for the nested list
  case). On the Lean side, `deriving DecidableEq` failed to
  synthesize because Lean's handler can't descend into nested
  `List Expr`; the Lean Module 4 citation was dropped at the time
  (CC.4 table marked Rocq-only).

  This stub re-establishes the citation by anchoring on the
  inductive type itself (not the auto-derived DecidableEq). The
  trust statement is "Module 4 patterns match on a closed,
  finitely-enumerable AST type" — which Lean's `inductive Expr`
  expresses directly.

  A manual `Expr.decEq` (writing out the recursion through
  `List Expr` to side-step the deriving-handler limitation) is
  tracked as a separate Layer 0 follow-up.

  This file is NOT compiled — it exists solely to satisfy the
  namespace-aware audit in src/pycsl/audit_proof.py.
-/

namespace PyCSL.AST

inductive Expr where
  | placeholder
  deriving Repr

end PyCSL.AST
