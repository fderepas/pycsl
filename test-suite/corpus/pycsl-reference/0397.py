"""Test 0397 — UB-7.4: ctypes import with \\trusted opt-in is accepted."""
_ = 0  # anchor
import ctypes  # noqa: F401


#@ \trusted reviewer: PR-6
#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def call_ctypes_thing(x: int) -> int:
    return 0


if __name__ == "__main__":
    pass
