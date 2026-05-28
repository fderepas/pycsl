"""Test 0335 — PyCSL List parameter + length/index (cross-prover, tuesday-01).

The cross-prover bridge produces this contract from `array_sum_nonneg`
fixtures in Coq and Lean. Full Alt-Ergo discharge would need a loop
invariant; the `--no-proof` flag here exercises parsing + PyCSL static
semantics only.
"""
# pycsl-flags: --no-proof
#@ requires n >= 0
#@ ensures (n <= \length(arr)) ==> (\result >= 0)
#@ assigns \nothing
def array_sum_nonneg(arr: list, n: int) -> int:
    s = 0
    i = 0
    while i < n:
        s = s + arr[i]
        i = i + 1
    return s

if __name__ == "__main__":
    assert array_sum_nonneg([1, 2, 3], 3) == 6
    assert array_sum_nonneg([], 0) == 0
