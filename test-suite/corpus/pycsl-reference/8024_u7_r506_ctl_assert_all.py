r"""Test 8024 -- route #506 (control, expected PASS): under `#@ no_exception \all` a Python `assert` test is a real obligation (route #332), so `assert 10 // n >= 0` keeps its division, discharged by `requires n > 0`; CPython g(5) returns 6)
"""
# pycsl-expected: PASS

#@ requires n > 0
#@ no_exception \all
#@ ensures \result == n + 1
def g(n: int) -> int:
    assert 10 // n >= 0
    return n + 1


if __name__ == "__main__":
    print("result", g(5))
