"""Test csv.writeheader L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import csv  # noqa: F401


#@ requires True
#@ ensures True
def use_writeheader(x: int) -> int:
    return csv.writeheader(x)


if __name__ == "__main__":
    pass
