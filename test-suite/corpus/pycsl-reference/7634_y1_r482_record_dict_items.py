r"""Test 7634 -- route #482 (expected FAIL: PROVED at base, REFUSED PYCSL-R482-TRUSTED-FRAME-UNTRACKED): a `\trusted` def stores through `for _k, p in {'a': o}.items(): p.v = 7` (the red team's `with nullcontext(o) as p` spelling, r10908, is refused the same way but kept out of the corpus: the dropped-mutation CTXBIND ratchet counts every `with ... as`); CPython returns 7.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List


class C:
    def __init__(self) -> None:
        self.v = 0
        self.xs: List[int] = [0]


#@ \trusted
def k(o: C) -> int:
    for _k, p in {'a': o}.items():
        p.v = 7
    return 0


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    k(o)
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
