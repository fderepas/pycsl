r"""Test 9903 -- lvS cap-re-gate-widening (expected FAIL): the alias `_re` is RE-BOUND (to an object
whose `compile` returns a pattern with a non-deterministic `match`) BEFORE the module constant is
compiled, so `_KV` is not a stdlib compiled pattern and the deterministic match model must NOT apply:
`\result == True` is false in CPython (the two reads differ) and must NOT prove. Measured: the
pipeline's name-rebinding gate refuses the file ("imported name `_re` bound again"); the alias gate's
own `_re`-store check (Module5) refuses it again behind that. Control: 9900.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List
import re as _re


class _Grp:
    def __init__(self, v: int) -> None:
        self.v = v

    def group(self, k: int) -> str:
        return str(self.v)


class _Pat:
    def __init__(self) -> None:
        self.calls: List[int] = []

    def match(self, s: str) -> _Grp:
        self.calls.append(1)
        return _Grp(len(self.calls))


class _FakeRe:
    def compile(self, p: str) -> _Pat:
        return _Pat()


_re = _FakeRe()
_KV = _re.compile(r"(\w+)=(\w+)")


#@ ensures \result == True
#@ assigns \nothing
def same_key(s: str) -> bool:
    m = _KV.match(s)
    n = _KV.match(s)
    if m:
        if n:
            return m.group(1) == n.group(1)
        return False
    return True


if __name__ == "__main__":
    r = same_key("a=b")
    print("VIOLATION contract" if r is not True else "result", r)
