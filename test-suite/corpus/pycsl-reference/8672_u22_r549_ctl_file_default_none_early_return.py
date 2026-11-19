r"""Test 8672 -- route #549 (control, expected PASS): a parameter defaulting to None passed to a file `def g(x: int)` after `if o is None: return 0`; CPython returns 0 / 4
"""
# pycsl-expected: PASS
from typing import Optional


def nothing() -> None:
    return None


def g(x: int) -> int:
    return x + 1


class Q:
    def __init__(self) -> None:
        self.a = 1

    def m(self, x: int) -> int:
        return x * 2


#@ no_exception \all
def f(k: int, o: Optional[int] = None) -> int:
    if o is None:
        return 0
    return g(o)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
