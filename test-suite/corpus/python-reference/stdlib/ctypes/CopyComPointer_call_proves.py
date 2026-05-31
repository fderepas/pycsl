"""Test ctypes.CopyComPointer L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ctypes  # noqa: F401


#@ requires True
#@ ensures True
def use_CopyComPointer(x: int) -> int:
    return ctypes.CopyComPointer(x)


if __name__ == "__main__":
    pass
