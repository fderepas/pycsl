r"""Test 9904 -- lvS cap-re-gate-widening (expected FAIL): a module-level `match` statement whose
capture pattern `case _re:` RE-BINDS the alias (to a fake whose pattern's `match` is
non-deterministic) before `_KV = _re.compile(..)`, so the deterministic match model must NOT apply and
`\result == True` (false in CPython) must NOT prove. Measured: the pipeline's name-rebinding gate
refuses the file ("imported name `_re` bound again"); a capture is not a Name store, so the alias gate
also checks `MatchAs` / `MatchStar` / `MatchMapping` rest and `except .. as` names itself. Control: 9900.
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


match _FakeRe():
    case _re:
        pass

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
