"""Test gc.get_stats L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gc  # noqa: F401


#@ requires True
#@ ensures True
def use_get_stats(x: int) -> int:
    return gc.get_stats(x)


if __name__ == "__main__":
    pass
