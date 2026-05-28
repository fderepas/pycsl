"""Test 0367 — IndexError 1D read without bounds precondition: fails."""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires True
#@ ensures True
#@ assigns \nothing
#@ no_exception IndexError
def unsafe_get(arr: list, i: int) -> int:
    return arr[i]


if __name__ == "__main__":
    pass
