"""Test statistics.geometric_mean L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import statistics  # noqa: F401


#@ requires True
#@ ensures True
def use_geometric_mean(x: int) -> int:
    return statistics.geometric_mean(x)


if __name__ == "__main__":
    pass
