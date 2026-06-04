"""Test 0454 — PyCSL act blocks: complete + disjoint case analysis (abs)."""
_ = 0  # anchor
#@ act neg:
#@     given x < 0
#@     ensures \result == 0 - x
#@ act pos:
#@     given x >= 0
#@     ensures \result == x
#@ complete neg, pos
#@ disjoint neg, pos
def myabs(x: int) -> int:
    if x < 0:
        return 0 - x
    return x
