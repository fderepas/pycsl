"""Test 0376 — multiple no_exception clauses union together.

Two `no_exception` lines on the same function should be combined; both
the division and the indexing must clear their VCs.
"""
_ = 0  # anchor
#@ requires d != 0
#@ requires 0 <= i and i < \length(arr)
#@ ensures \result == arr[i] // d
#@ assigns \nothing
#@ no_exception ZeroDivisionError
#@ no_exception IndexError
def safe_div_at(arr: list, i: int, d: int) -> int:
    return arr[i] // d


if __name__ == "__main__":
    assert safe_div_at([10, 20, 30], 1, 4) == 5
