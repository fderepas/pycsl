-- Golden test fixture for lean2pycsl — boolean parameters and operators.
--
-- Mirrors src/rocq2pycsl/tests/golden/bool_xor — same Python target,
-- same expected annotated output. Demonstrates the 0/1-encoded
-- boolean rendering: `xor` / `bne` maps to `(a + b) - 2 * (a * b)`
-- and each Bool param gets a `requires (p == 0) or (p == 1)` clause.

def bool_xor (a b : Bool) : Bool := Bool.xor a b

@[pycsl_spec "bool_xor"]
theorem bool_xor_correct : ∀ (a b : Bool), bool_xor a b = Bool.xor a b := sorry
