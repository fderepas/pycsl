"""Test statistics.mode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import statistics  # noqa: F401


#@ requires True
#@ ensures True
def use_mode(x: int) -> int:
    return statistics.mode(x)


if __name__ == "__main__":
    pass
