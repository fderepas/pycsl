r"""Test 8212 -- route #514 (control, expected PASS): a range bound to a name whose length is never observed, and `len(range(n))` spelled directly carries route #414's bound, discharged by `requires 0 <= n <= 1000`; CPython f(5) returns 1
"""
# pycsl-expected: PASS


#@ requires 0 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    r = range(n)
    m = len(range(n))
    return 1


if __name__ == "__main__":
    print(f(5))
