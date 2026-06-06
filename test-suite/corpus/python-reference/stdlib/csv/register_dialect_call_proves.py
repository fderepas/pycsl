"""Test csv.register_dialect L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import csv  # noqa: F401


#@ requires True
#@ ensures True
def use_register_dialect(x: int) -> int:
    return csv.register_dialect(x)


if __name__ == "__main__":
    pass
