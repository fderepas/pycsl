"""Test calendar.setfirstweekday L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import calendar  # noqa: F401


#@ requires True
#@ ensures True
def use_setfirstweekday(x: int) -> int:
    return calendar.setfirstweekday(x)


if __name__ == "__main__":
    pass
