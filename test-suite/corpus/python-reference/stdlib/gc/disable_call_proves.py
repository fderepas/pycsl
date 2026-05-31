"""Test gc.disable L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gc  # noqa: F401


#@ requires True
#@ ensures True
def use_disable(x: int) -> int:
    return gc.disable(x)


if __name__ == "__main__":
    pass
