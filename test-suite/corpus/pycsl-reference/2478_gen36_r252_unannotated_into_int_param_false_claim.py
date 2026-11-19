r"""Test 2478 — route #252 (expected FAIL): an UNANNOTATED parameter passed to `g(a: int, b: int)` was
trusted as an int: `return g(x, x)` PROVED `\result == 0`. CPython: a user `__sub__` returns 7.
PROVED at 15f8c4bd; now REFUSED fail-closed.
"""
# pycsl-expected: FAIL


#@ ensures \result == a - b
#@ assigns \nothing
def g(a: int, b: int) -> int:
    return a - b


#@ ensures \result == 0
#@ assigns \nothing
def f(x) -> int:
    return g(x, x)


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert f(P()) == 7
