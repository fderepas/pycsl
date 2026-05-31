"""Test datetime.datetime_min L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_datetime_min(x: int) -> int:
    return datetime.datetime_min(x)


if __name__ == "__main__":
    pass
