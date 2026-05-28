"""Test 0337 — PyCSL Array fill (cross-prover, tuesday-01).

The Coq/Lean `array_fill_zero` fixtures generate this function-level
contract. Full verification needs a `#@ assigns arr[0..n]` clause and
loop invariants — `--no-proof` mode validates parsing only.
"""
# pycsl-flags: --no-proof
#@ requires n >= 0
#@ ensures (n <= \length(arr)) ==> (\result >= 0)
#@ assigns \nothing
def array_fill_zero(arr: list, n: int) -> int:
    i = 0
    while i < n:
        arr[i] = 0
        i = i + 1
    return n
