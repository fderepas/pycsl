"""Test ctypes.set_errno L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ctypes  # noqa: F401


#@ requires True
#@ ensures True
def use_set_errno(x: int) -> int:
    return ctypes.set_errno(x)


if __name__ == "__main__":
    pass
