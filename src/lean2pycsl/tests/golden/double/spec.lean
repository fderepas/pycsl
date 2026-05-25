-- Golden test fixture for lean2pycsl.
--
-- Mirrors src/rocq2pycsl/tests/golden/double — same Python target,
-- same expected annotated output. Demonstrates that the two
-- pipelines converge on identical contracts from independent proof
-- sources.

def double (x : Int) : Int := x * 2

@[pycsl_spec "double"]
theorem double_value : ∀ (x : Int), double x = x * 2 := sorry

@[pycsl_spec "double"]
theorem double_is_even : ∀ (x : Int), 2 ∣ double x := sorry
