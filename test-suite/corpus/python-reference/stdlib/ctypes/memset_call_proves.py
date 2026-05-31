"""Test ctypes.memset L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ctypes  # noqa: F401


#@ requires True
#@ ensures True
def use_memset(x: int) -> int:
    return ctypes.memset(x)


if __name__ == "__main__":
    pass
