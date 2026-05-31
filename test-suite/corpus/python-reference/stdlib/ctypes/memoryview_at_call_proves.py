"""Test ctypes.memoryview_at L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ctypes  # noqa: F401


#@ requires True
#@ ensures True
def use_memoryview_at(x: int) -> int:
    return ctypes.memoryview_at(x)


if __name__ == "__main__":
    pass
