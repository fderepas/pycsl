r"""Test 2454 — route #251 (expected FAIL): An `object` parameter: `return x - x` PROVED `\result == 0`. CPython: a user
`__sub__` returns 7.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
#@ ensures \result == 0
#@ assigns \nothing
def f(x: object) -> int:
    return x - x  # type: ignore[operator]


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert f(P()) == 7
