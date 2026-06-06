-- Golden test fixture for lean2pycsl — ghost_set as `Nat → Bool`.
--
-- Mirrors src/rocq2pycsl/tests/golden/set_union_eq. The `Nat → Bool`
-- type form is the Lean equivalent of Coq's `nat -> bool`; both
-- normalize to `nat -> bool` in the bridge canonicalizer.

def set_union_eq (n : Nat) : Nat := n

@[pycsl_spec "set_union_eq"]
theorem set_union_eq_correct :
  ∀ (n : Nat) (s1 s2 : Nat → Bool),
    set_union_eq n = n := sorry
