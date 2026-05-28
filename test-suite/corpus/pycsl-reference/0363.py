"""Test 0363 — ZeroDivisionError for modulo (%) — proves."""
_ = 0  # anchor
#@ requires d != 0
#@ ensures \result == n % d
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def remainder(n: int, d: int) -> int:
    return n % d


if __name__ == "__main__":
    assert remainder(10, 3) == 1
