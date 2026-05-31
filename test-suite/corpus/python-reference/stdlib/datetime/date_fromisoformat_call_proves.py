"""Test datetime.date_fromisoformat L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_date_fromisoformat(x: int) -> int:
    return datetime.date_fromisoformat(x)


if __name__ == "__main__":
    pass
