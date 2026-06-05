-- test-suite/corpus/pycsl-reference/0538.proofs/lean/Perm.lean
--
-- Lean proof of the permutation reflexivity axiom cited by 0538.py via
-- `#@ proof lean: Pycsl.Reference.Perm.permut_refl`. Cross-validated against
-- the Coq statement in 0538.proofs/rocq/Perm.v. No sorry, no axioms.

namespace Pycsl.Reference.Perm

/-- `permut s s` — `\permutation(a, a)`: a list is a permutation of itself. -/
theorem permut_refl (l : List Int) : l.Perm l := List.Perm.refl l

end Pycsl.Reference.Perm
