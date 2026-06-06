"""Test csv.list_dialects L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import csv  # noqa: F401


#@ requires True
#@ ensures True
def use_list_dialects(x: int) -> int:
    return csv.list_dialects(x)


if __name__ == "__main__":
    pass
