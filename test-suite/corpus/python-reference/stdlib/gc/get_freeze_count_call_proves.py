"""Test gc.get_freeze_count L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gc  # noqa: F401


#@ requires True
#@ ensures True
def use_get_freeze_count(x: int) -> int:
    return gc.get_freeze_count(x)


if __name__ == "__main__":
    pass
