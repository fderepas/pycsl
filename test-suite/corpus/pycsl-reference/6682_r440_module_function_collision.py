r"""Test 6682 -- route #440 A1 (expected FAIL): `math.factorial(n)` under `#@ no_exception \all` beside a FILE function named `factorial`. Route #161's method arm admitted the module call by its TAIL name (the file's `factorial` has a contract; `math.factorial` has none) -- PROVED at candidate before this arm; CPython raises ValueError for `n < 0` (the `__main__` driver prints VIOLATION). REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED: a file function does not speak for an imported module's).
"""
# pycsl-expected: FAIL
import math


def factorial(n: int) -> int:
    return 1


#@ no_exception \all
def f(n: int) -> int:
    return math.factorial(n)


if __name__ == "__main__":
    try:
        print(f(-1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
