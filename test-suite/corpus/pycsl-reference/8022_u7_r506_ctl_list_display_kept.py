r"""Test 8022 -- route #506 (control, expected PASS): a list display `[10 // n, n]` keeps its elements' obligations, discharged by `requires n != 0` under `#@ no_exception \all`; CPython g(5) returns 2)
"""
# pycsl-expected: PASS

#@ requires n != 0
#@ no_exception \all
#@ ensures \result == 10 // n
def g(n: int) -> int:
    l = [10 // n, n]
    return l[0]


if __name__ == "__main__":
    print("result", g(5))
