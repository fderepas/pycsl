"""Test gc.get_objects L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gc  # noqa: F401


#@ requires True
#@ ensures True
def use_get_objects(x: int) -> int:
    return gc.get_objects(x)


if __name__ == "__main__":
    pass
