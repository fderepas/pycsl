"""Test ctypes.addressof L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ctypes  # noqa: F401


#@ requires True
#@ ensures True
def use_addressof(x: int) -> int:
    return ctypes.addressof(x)


if __name__ == "__main__":
    pass
