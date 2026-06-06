"""Test csv.get_dialect L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import csv  # noqa: F401


#@ requires True
#@ ensures True
def use_get_dialect(x: int) -> int:
    return csv.get_dialect(x)


if __name__ == "__main__":
    pass
