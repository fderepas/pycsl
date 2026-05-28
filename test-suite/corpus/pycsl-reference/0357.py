"""Test 0357 — no_exception parser rejection: unknown exception name."""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires True
#@ ensures \result == n
#@ assigns \nothing
#@ no_exception NotARealException
def passthrough(n: int) -> int:
    return n


if __name__ == "__main__":
    pass
