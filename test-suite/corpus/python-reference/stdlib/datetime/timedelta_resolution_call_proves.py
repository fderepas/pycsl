"""Test datetime.timedelta_resolution L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_timedelta_resolution(x: int) -> int:
    return datetime.timedelta_resolution(x)


if __name__ == "__main__":
    pass
