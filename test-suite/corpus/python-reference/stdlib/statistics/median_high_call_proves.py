"""Test statistics.median_high L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import statistics  # noqa: F401


#@ requires True
#@ ensures True
def use_median_high(x: int) -> int:
    return statistics.median_high(x)


if __name__ == "__main__":
    pass
