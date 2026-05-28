"""Test 0354 — no_exception parser: multiple exception names on one line."""
_ = 0  # anchor
#@ requires n != 0
#@ requires 0 <= i and i < \length(arr)
#@ ensures \result == arr[i] // n
#@ assigns \nothing
#@ no_exception ZeroDivisionError, IndexError
def safe_div_at(arr: list, i: int, n: int) -> int:
    return arr[i] // n


if __name__ == "__main__":
    assert safe_div_at([10, 20, 30], 1, 2) == 10
