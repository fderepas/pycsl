"""Test datetime.date_today L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_date_today(x: int) -> int:
    return datetime.date_today(x)


if __name__ == "__main__":
    pass
