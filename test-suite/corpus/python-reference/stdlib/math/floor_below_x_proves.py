"""Test math.floor L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import math  # noqa: F401


#@ requires True
#@ ensures \result <= x
def floor_is_below(x: int) -> int:
    return math.floor(x)


if __name__ == "__main__":
    pass
