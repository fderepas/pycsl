-- test-suite/corpus/pycsl-reference/0539.proofs/lean/Rev.lean
--
-- Lean proof of the reversal-permutation framing lemma cited by 0539.py via
-- `#@ proof lean: Pycsl.Reference.Perm.rev_permutation`. Cross-validated against
-- the Coq statement in 0539.proofs/rocq/Rev.v. No sorry, no axioms.

namespace Pycsl.Reference.Perm

/-- `permut (array_rev s) s` — reversing a list permutes its elements. -/
theorem rev_permutation (l : List Int) : (l.reverse).Perm l := l.reverse_perm

end Pycsl.Reference.Perm
