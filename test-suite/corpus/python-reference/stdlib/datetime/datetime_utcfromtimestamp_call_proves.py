"""Test datetime.datetime_utcfromtimestamp L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_datetime_utcfromtimestamp(x: int) -> int:
    return datetime.datetime_utcfromtimestamp(x)


if __name__ == "__main__":
    pass
