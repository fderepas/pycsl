"""Test 0366 — IndexError 1D read with in-bounds precondition — proves."""
_ = 0  # anchor
#@ requires 0 <= i and i < \length(arr)
#@ ensures \result == arr[i]
#@ assigns \nothing
#@ no_exception IndexError
def get_at(arr: list, i: int) -> int:
    return arr[i]


if __name__ == "__main__":
    assert get_at([10, 20, 30], 1) == 20
