"""Test statistics.pvariance L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import statistics  # noqa: F401


#@ requires True
#@ ensures True
def use_pvariance(x: int) -> int:
    return statistics.pvariance(x)


if __name__ == "__main__":
    pass
