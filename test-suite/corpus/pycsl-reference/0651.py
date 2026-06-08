"""Test 0651 — array-returning function with early returns (return-arr.md, Return_seq).

A `-> list` function with a guarded early `return []` plus a tail `return [..]` used to be
unsupported: the monomorphic `exception Return int` can't carry an array, and Why3 forbids a mutable
`array int` exception payload. PyCSL now lowers such returns through an IMMUTABLE
`exception Return_seq (seq int)` and materializes back to `array int` at the single catch
(`with Return_seq s -> materialize s`), reusing the seq↔array bridge. The body stays a verified
`let` (a false length `ensures` fails the callee), not a `\trusted` val.
"""


#@ requires True
#@ assigns \nothing
#@ ensures \length(\result) >= 0
def f(x: int) -> list:
    if x < 0:
        return []
    return [1, 2, 3]
