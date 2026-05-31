"""Test datetime.time_ctor L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_time_ctor(x: int) -> int:
    return datetime.time_ctor(x)


if __name__ == "__main__":
    pass
