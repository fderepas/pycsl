"""Test 0396 — UB-7.4: ctypes import without \\trusted is rejected."""
# pycsl-expected: FAIL
_ = 0  # anchor
import ctypes  # noqa: F401


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def call_ctypes_thing(x: int) -> int:
    return 0


if __name__ == "__main__":
    pass
