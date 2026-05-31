"""Test datetime.timezone_utc L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_timezone_utc(x: int) -> int:
    return datetime.timezone_utc(x)


if __name__ == "__main__":
    pass
