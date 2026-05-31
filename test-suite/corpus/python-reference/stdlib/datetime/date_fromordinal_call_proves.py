"""Test datetime.date_fromordinal L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_date_fromordinal(x: int) -> int:
    return datetime.date_fromordinal(x)


if __name__ == "__main__":
    pass
