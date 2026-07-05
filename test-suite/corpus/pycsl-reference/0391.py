"""Test 0391 — no_exception \\all with strong preconditions proves."""
_ = 0  # anchor
#@ requires d != 0
#@ requires 0 <= i and i < \length(arr)
#@ ensures \result == arr[i] // d
#@ assigns \nothing
#@ no_exception \all
def all_safe(arr: list, i: int, d: int) -> int:
    return arr[i] // d


if __name__ == "__main__":
    assert all_safe([10, 20, 30], 1, 4) == 5
