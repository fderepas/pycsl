"""Test statistics.covariance L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import statistics  # noqa: F401


#@ requires True
#@ ensures True
def use_covariance(x: int) -> int:
    return statistics.covariance(x)


if __name__ == "__main__":
    pass
