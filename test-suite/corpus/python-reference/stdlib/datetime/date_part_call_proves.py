"""Test datetime.date_part L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_date_part(x: int) -> int:
    return datetime.date_part(x)


if __name__ == "__main__":
    pass
