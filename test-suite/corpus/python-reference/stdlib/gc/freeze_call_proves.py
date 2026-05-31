"""Test gc.freeze L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gc  # noqa: F401


#@ requires True
#@ ensures True
def use_freeze(x: int) -> int:
    return gc.freeze(x)


if __name__ == "__main__":
    pass
