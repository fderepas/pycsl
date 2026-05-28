"""Test 0333 — PyCSL Boolean XOR (cross-prover, tuesday-01 pilot).

Demonstrates the 0/1-encoded boolean convention.

The `xorb a b = a + b - 2 * (a * b)` identity is provable in linear
arithmetic with the 0/1 preconditions in scope (Alt-Ergo: Valid).
"""
#@ requires (a == 0) or (a == 1)
#@ requires (b == 0) or (b == 1)
#@ ensures \result == ((a + b) - (2 * (a * b)))
#@ assigns \nothing
def bool_xor(a: int, b: int) -> int:
    return (a + b) - 2 * (a * b)

if __name__ == "__main__":
    assert bool_xor(0, 0) == 0
    assert bool_xor(0, 1) == 1
    assert bool_xor(1, 0) == 1
    assert bool_xor(1, 1) == 0
