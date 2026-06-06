-- Golden test fixture for lean2pycsl — Lists with universal quantification.
--
-- Mirrors src/rocq2pycsl/tests/golden/array_sum_nonneg. Lean's
-- `List.length arr` → `Length`. `Nat` binders auto-emit `requires p >= 0`.

def array_sum_nonneg (arr : List Nat) (n : Nat) : Nat := 0

@[pycsl_spec "array_sum_nonneg"]
theorem array_sum_nonneg_nonneg :
  ∀ (arr : List Nat) (n : Nat),
    n <= List.length arr →
    array_sum_nonneg arr n >= 0 := sorry
