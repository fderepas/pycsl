"""Test 0400 — UB-7.4: --allow-unverified-imports overrides the deny-list."""
# pycsl-flags: --allow-unverified-imports
_ = 0  # anchor
import ctypes  # noqa: F401


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def allowed_under_flag(x: int) -> int:
    return 0


if __name__ == "__main__":
    pass
