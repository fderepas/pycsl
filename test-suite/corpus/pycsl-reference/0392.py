"""Test 0392 — no_exception \\all without preconditions: VC fires, fails."""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires True
#@ ensures True
#@ assigns \nothing
#@ no_exception \all
def all_unsafe(arr: list, i: int, d: int) -> int:
    return arr[i] // d


if __name__ == "__main__":
    pass
