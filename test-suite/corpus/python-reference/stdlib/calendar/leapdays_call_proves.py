"""Test calendar.leapdays L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import calendar  # noqa: F401


#@ requires True
#@ ensures True
def use_leapdays(x: int) -> int:
    return calendar.leapdays(x)


if __name__ == "__main__":
    pass
