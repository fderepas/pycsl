"""Test math.floor L5 — negative: caller asserts a too-strong post.

floor(x) is bounded `x - 1 <= \\result <= x`; this caller
claims `\\result == x - 1` (the floor lower bound is not the
floor value in general — it's an over-claim). Under full
proof, this fails to discharge.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import math  # noqa: F401


#@ requires True
#@ ensures \result == x - 1
def floor_overclaim(x: int) -> int:
    return math.floor(x)


if __name__ == "__main__":
    pass
