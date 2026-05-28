"""Test 0368 — IndexError 1D write with in-bounds precondition — proves."""
_ = 0  # anchor
#@ requires 0 <= i and i < \length(arr)
#@ ensures \length(arr) >= 1
#@ assigns arr[0..\length(arr)]
#@ no_exception IndexError
def set_at(arr: list, i: int, v: int) -> None:
    arr[i] = v


if __name__ == "__main__":
    a = [1, 2, 3]
    set_at(a, 1, 99)
    assert a[1] == 99
