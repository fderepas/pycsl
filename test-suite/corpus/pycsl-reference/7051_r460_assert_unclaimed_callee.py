r"""Test 7051 -- route #460 (expected FAIL): `assert n > 0` in an UN-claimed `g` called by `f` claiming `#@ no_exception \all` (CPython AssertionError for f(0)). PROVED at base 370db7dc2; now the assert is an obligation of g under its reached claim and FAILS.
"""
# pycsl-expected: FAIL


def g(n: int) -> int:
    assert n > 0
    return n


#@ no_exception \all
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    print("result", f(0))  # CPython: AssertionError
