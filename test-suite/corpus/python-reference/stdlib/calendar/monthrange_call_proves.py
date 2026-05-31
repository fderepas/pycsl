"""Test calendar.monthrange L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import calendar  # noqa: F401


#@ requires True
#@ ensures True
def use_monthrange(x: int) -> int:
    return calendar.monthrange(x)


if __name__ == "__main__":
    pass
