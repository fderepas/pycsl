"""Test datetime.timedelta_ctor L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_timedelta_ctor(x: int) -> int:
    return datetime.timedelta_ctor(x)


if __name__ == "__main__":
    pass
