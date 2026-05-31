"""Test statistics.stdev L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import statistics  # noqa: F401


#@ requires True
#@ ensures True
def use_stdev(x: int) -> int:
    return statistics.stdev(x)


if __name__ == "__main__":
    pass
