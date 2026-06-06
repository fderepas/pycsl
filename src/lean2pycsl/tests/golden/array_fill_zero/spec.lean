-- Golden test fixture for lean2pycsl — Arrays (List Nat).
--
-- Mirrors src/rocq2pycsl/tests/golden/array_fill_zero. The Lean
-- `Array Nat` type also maps to PyCSL's `\length`-based contract.

def array_fill_zero (arr : List Nat) (n : Nat) : Nat := n

@[pycsl_spec "array_fill_zero"]
theorem array_fill_zero_correct :
  ∀ (arr : List Nat) (n : Nat),
    n <= List.length arr →
    array_fill_zero arr n >= 0 := sorry
