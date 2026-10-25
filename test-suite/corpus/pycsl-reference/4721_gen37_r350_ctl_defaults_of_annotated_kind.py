r"""Test 4721 -- gen #37 route #350 (expected PASS): CONTROL: defaults of the annotation's kind (int / float <- int / bool / str / module constant / Optional <- None / signed literal / kw-only int <- True / nested-def outer-parameter default) stay admitted and prove.
"""
# pycsl-expected: PASS
from typing import Optional
K = 7
#@ ensures \result == x + 7
def f(x: int = 0, y: float = 1, z: bool = True, s: str = "a", k: int = K,
      o: Optional[int] = None, n: int = -1) -> int:
    return x + 7

class C:
    def __init__(self) -> None:
        self.k = 1

    #@ ensures \result == x
    def m(self, x: int = 3, *, w: int = True) -> int:
        return x

#@ ensures \result == x + 7
def g(x: int) -> int:
    def h(y: int = x, z: int = K) -> int:
        return y + z
    return h()

if __name__ == "__main__":
    assert f() == 7 and C().m() == 3 and g(2) == 9
