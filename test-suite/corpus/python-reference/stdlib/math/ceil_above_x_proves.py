"""Test math.ceil L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import math  # noqa: F401


#@ requires True
#@ ensures \result >= x
def ceil_is_above(x: int) -> int:
    return math.ceil(x)


if __name__ == "__main__":
    pass
