"""Test gc.set_debug L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gc  # noqa: F401


#@ requires True
#@ ensures True
def use_set_debug(x: int) -> int:
    return gc.set_debug(x)


if __name__ == "__main__":
    pass
