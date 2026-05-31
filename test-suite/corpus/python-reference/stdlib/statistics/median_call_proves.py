"""Test statistics.median L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import statistics  # noqa: F401


#@ requires True
#@ ensures True
def use_median(x: int) -> int:
    return statistics.median(x)


if __name__ == "__main__":
    pass
