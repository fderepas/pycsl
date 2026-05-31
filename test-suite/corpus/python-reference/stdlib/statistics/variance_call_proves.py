"""Test statistics.variance L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import statistics  # noqa: F401


#@ requires True
#@ ensures True
def use_variance(x: int) -> int:
    return statistics.variance(x)


if __name__ == "__main__":
    pass
