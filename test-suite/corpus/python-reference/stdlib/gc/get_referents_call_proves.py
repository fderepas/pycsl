"""Test gc.get_referents L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gc  # noqa: F401


#@ requires True
#@ ensures True
def use_get_referents(x: int) -> int:
    return gc.get_referents(x)


if __name__ == "__main__":
    pass
