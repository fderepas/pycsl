"""Test statistics.multimode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import statistics  # noqa: F401


#@ requires True
#@ ensures True
def use_multimode(x: int) -> int:
    return statistics.multimode(x)


if __name__ == "__main__":
    pass
