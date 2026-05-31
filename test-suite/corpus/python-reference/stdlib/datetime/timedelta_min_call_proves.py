"""Test datetime.timedelta_min L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_timedelta_min(x: int) -> int:
    return datetime.timedelta_min(x)


if __name__ == "__main__":
    pass
