"""Test datetime.datetime_combine L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_datetime_combine(x: int) -> int:
    return datetime.datetime_combine(x)


if __name__ == "__main__":
    pass
