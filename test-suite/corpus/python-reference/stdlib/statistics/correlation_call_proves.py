"""Test statistics.correlation L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import statistics  # noqa: F401


#@ requires True
#@ ensures True
def use_correlation(x: int) -> int:
    return statistics.correlation(x)


if __name__ == "__main__":
    pass
