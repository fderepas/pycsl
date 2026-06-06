"""Test csv.field_size_limit L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import csv  # noqa: F401


#@ requires True
#@ ensures True
def use_field_size_limit(x: int) -> int:
    return csv.field_size_limit(x)


if __name__ == "__main__":
    pass
