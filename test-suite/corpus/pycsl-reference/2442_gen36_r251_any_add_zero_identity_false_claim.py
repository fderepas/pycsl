r"""Test 2442 — route #251 (expected FAIL): `return (x + 0) - x` on `x: Any` PROVED `\result == 0` (`x + 0 = x`). CPython:
`__add__ -> 5`, then `5 - x` is `x.__rsub__(5)`, here 3.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    return (x + 0) - x


if __name__ == "__main__":
    class P:
        def __add__(self, o: object) -> int:
            return 5

        def __rsub__(self, o: object) -> int:
            return 3

    assert f(P()) == 3
