"""Test calendar.timegm L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import calendar  # noqa: F401


#@ requires True
#@ ensures True
def use_timegm(x: int) -> int:
    return calendar.timegm(x)


if __name__ == "__main__":
    pass
