r"""Test 8020 -- route #506 (control, expected PASS): the division of a set display bound to a local first (`q = 10 // n; s = {q}`), under `#@ no_exception ZeroDivisionError` and `requires n != 0`; the plain statement carries the obligation; CPython g(5) returns 3)
"""
# pycsl-expected: PASS

#@ requires n != 0
#@ no_exception ZeroDivisionError
#@ ensures \result == 10 // n + 1
def g(n: int) -> int:
    q = 10 // n
    s = {q}
    return q + 1


if __name__ == "__main__":
    print("result", g(5))
