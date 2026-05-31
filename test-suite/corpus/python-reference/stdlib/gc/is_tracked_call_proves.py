"""Test gc.is_tracked L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gc  # noqa: F401


#@ requires True
#@ ensures True
def use_is_tracked(x: int) -> int:
    return gc.is_tracked(x)


if __name__ == "__main__":
    pass
