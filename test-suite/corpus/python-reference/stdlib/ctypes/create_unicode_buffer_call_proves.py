"""Test ctypes.create_unicode_buffer L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ctypes  # noqa: F401


#@ requires True
#@ ensures True
def use_create_unicode_buffer(x: int) -> int:
    return ctypes.create_unicode_buffer(x)


if __name__ == "__main__":
    pass
