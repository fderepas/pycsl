r"""Test 8019 -- route #506 (expected FAIL: PROVED at base, REFUSED PYCSL-R506-TRIGGER-SITE-UNLOWERED): f claims `#@ no_exception \all` and returns `xs[3].size()` for a file class `C`; the method-call lowering drops its receiver (`size_0 ()`), so the IndexError of `xs[3]` was never asked; CPython f([]) raises IndexError
"""
# pycsl-expected: FAIL
from typing import List


class C:
    def __init__(self, n: int) -> None:
        self.n = n

    def size(self) -> int:
        return 1


#@ no_exception \all
def f(xs: List[C]) -> int:
    return xs[3].size()


if __name__ == "__main__":
    try:
        print("result", f([]))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
