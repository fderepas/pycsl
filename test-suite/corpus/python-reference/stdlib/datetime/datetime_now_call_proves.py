"""Test datetime.datetime_now L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_datetime_now(x: int) -> int:
    return datetime.datetime_now(x)


if __name__ == "__main__":
    pass
