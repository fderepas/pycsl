"""Test math.ceil L5 — negative: caller asserts a too-strong post.

ceil(x) is bounded `x <= \\result <= x + 1`; this caller
claims `\\result == x + 1`. Under full proof, this fails.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import math  # noqa: F401


#@ requires True
#@ ensures \result == x + 1
def ceil_overclaim(x: int) -> int:
    return math.ceil(x)


if __name__ == "__main__":
    pass
