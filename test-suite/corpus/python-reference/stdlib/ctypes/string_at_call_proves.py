"""Test ctypes.string_at L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ctypes  # noqa: F401


#@ requires True
#@ ensures True
def use_string_at(x: int) -> int:
    return ctypes.string_at(x)


if __name__ == "__main__":
    pass
