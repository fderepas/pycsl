"""Test datetime.days L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_days(x: int) -> int:
    return datetime.days(x)


if __name__ == "__main__":
    pass
