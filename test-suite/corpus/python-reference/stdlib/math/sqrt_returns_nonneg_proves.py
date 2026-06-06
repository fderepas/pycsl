"""Test math.sqrt L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import math  # noqa: F401


#@ requires x >= 0
#@ ensures \result >= 0
def square_root_is_nonneg(x: int) -> int:
    return math.sqrt(x)


if __name__ == "__main__":
    pass
