r"""Test 7744 -- route #489 (expected FAIL: a Why3 type error at base -- fail closed --, REFUSED PYCSL-R489-IMPLICIT-DUNDER at the repair; the rule's arm, not a false proof): a `\trusted` k prints `str(xs)` for `xs: List[C]`; each element's `C.__repr__` writes `self.v`; CPython returns 7
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __repr__(self) -> str:
        self.v = 7
        return 'c'


#@ \trusted
def k(xs: List[C]) -> int:
    return len(str(xs))


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    k([o])
    return o.v


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
