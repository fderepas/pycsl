"""Test datetime.datetime_fromordinal L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_datetime_fromordinal(x: int) -> int:
    return datetime.datetime_fromordinal(x)


if __name__ == "__main__":
    pass
