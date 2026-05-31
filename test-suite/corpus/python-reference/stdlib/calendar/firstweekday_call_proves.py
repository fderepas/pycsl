"""Test calendar.firstweekday L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import calendar  # noqa: F401


#@ requires True
#@ ensures True
def use_firstweekday(x: int) -> int:
    return calendar.firstweekday(x)


if __name__ == "__main__":
    pass
