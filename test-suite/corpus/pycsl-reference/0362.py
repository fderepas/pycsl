"""Test 0362 — ZeroDivisionError for floor division (//) — proves."""
_ = 0  # anchor
#@ requires d != 0
#@ ensures \result == n // d
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def floor_div(n: int, d: int) -> int:
    return n // d


if __name__ == "__main__":
    assert floor_div(10, 3) == 3
