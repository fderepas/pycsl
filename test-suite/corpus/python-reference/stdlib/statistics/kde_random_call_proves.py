"""Test statistics.kde_random L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import statistics  # noqa: F401


#@ requires True
#@ ensures True
def use_kde_random(x: int) -> int:
    return statistics.kde_random(x)


if __name__ == "__main__":
    pass
