"""Test 0398 — UB-7.4: cffi import without \\trusted is rejected."""
# pycsl-expected: FAIL
_ = 0  # anchor
import cffi  # noqa: F401


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def cffi_caller(x: int) -> int:
    return 0


if __name__ == "__main__":
    pass
