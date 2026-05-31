"""Test gc.set_threshold L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gc  # noqa: F401


#@ requires True
#@ ensures True
def use_set_threshold(x: int) -> int:
    return gc.set_threshold(x)


if __name__ == "__main__":
    pass
