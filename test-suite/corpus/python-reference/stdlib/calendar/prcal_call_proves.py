"""Test calendar.prcal L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import calendar  # noqa: F401


#@ requires True
#@ ensures True
def use_prcal(x: int) -> int:
    return calendar.prcal(x)


if __name__ == "__main__":
    pass
