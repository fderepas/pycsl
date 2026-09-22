r"""Test 1789 — WITNESS: `#@ complete` on a `\trusted` function.

`#@ complete` / `#@ disjoint` are discharged as a function-ENTRY assert over the act
guards. A `\trusted` (or `\abstract`) function's body is NEVER LOWERED, so that assert is
never proved and the claim would hold by nothing at all. Refused. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ \trusted reviewer: witness-only
#@ act neg:
#@     given x < 0
#@     ensures \result == 0 - x
#@ act pos:
#@     given x >= 0
#@     ensures \result == x
#@ complete neg, pos
#@ assigns \nothing
def myabs(x: int) -> int:
    if x < 0:
        return 0 - x
    return x
