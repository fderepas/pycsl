"""Test datetime.time_part L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_time_part(x: int) -> int:
    return datetime.time_part(x)


if __name__ == "__main__":
    pass
