"""Test gc.is_finalized L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gc  # noqa: F401


#@ requires True
#@ ensures True
def use_is_finalized(x: int) -> int:
    return gc.is_finalized(x)


if __name__ == "__main__":
    pass
