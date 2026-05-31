"""Test ctypes.get_last_error L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ctypes  # noqa: F401


#@ requires True
#@ ensures True
def use_get_last_error(x: int) -> int:
    return ctypes.get_last_error(x)


if __name__ == "__main__":
    pass
