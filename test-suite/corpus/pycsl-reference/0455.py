"""Test 0455 — PyCSL act blocks: global requires + two guarded cases."""
_ = 0  # anchor
#@ requires x >= 0
#@ act small:
#@     given x < 10
#@     ensures \result == x
#@ act big:
#@     given x >= 10
#@     ensures \result == 10
#@ complete small, big
#@ disjoint small, big
def clamp10(x: int) -> int:
    if x < 10:
        return x
    return 10
