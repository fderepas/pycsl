"""Test calendar.calendar L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import calendar  # noqa: F401


#@ requires True
#@ ensures True
def use_calendar(x: int) -> int:
    return calendar.calendar(x)


if __name__ == "__main__":
    pass
