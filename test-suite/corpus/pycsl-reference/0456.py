"""Test 0456 — PyCSL act blocks: an incomplete case set must FAIL completeness.

`neg` covers x < 0 and `pos` covers x > 0, leaving x == 0 uncovered, so the
`complete` VC (`\old(x<0) || \old(x>0)`) is false at x == 0 and the proof fails.
This proves the completeness check has teeth.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ act neg:
#@     given x < 0
#@     ensures \result == 0 - x
#@ act pos:
#@     given x > 0
#@     ensures \result == x
#@ complete neg, pos
def gap(x: int) -> int:
    if x < 0:
        return 0 - x
    return x
