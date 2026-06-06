"""Test math.gcd L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import math  # noqa: F401


#@ requires n >= 0
#@ ensures \result >= 0
#@ ensures \result <= n
def gcd_is_bounded(n: int) -> int:
    return math.gcd(n)


if __name__ == "__main__":
    pass
