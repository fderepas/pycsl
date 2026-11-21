r"""Test 8021 -- route #506 (control, expected PASS): a dict display `{1: 10 // n}` keeps its value's obligation (lowered element by element), discharged by `requires n != 0` under `#@ no_exception ZeroDivisionError`; CPython g(5) returns 2)
"""
# pycsl-expected: PASS

#@ requires n != 0
#@ no_exception ZeroDivisionError
#@ ensures \result == 10 // n
def g(n: int) -> int:
    dd = {1: 10 // n}
    return 10 // n


if __name__ == "__main__":
    print("result", g(5))
