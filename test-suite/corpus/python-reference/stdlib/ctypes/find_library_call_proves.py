"""Test ctypes.find_library L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ctypes  # noqa: F401


#@ requires True
#@ ensures True
def use_find_library(x: int) -> int:
    return ctypes.find_library(x)


if __name__ == "__main__":
    pass
