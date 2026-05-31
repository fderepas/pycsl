"""Test ctypes.memmove L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ctypes  # noqa: F401


#@ requires True
#@ ensures True
def use_memmove(x: int) -> int:
    return ctypes.memmove(x)


if __name__ == "__main__":
    pass
