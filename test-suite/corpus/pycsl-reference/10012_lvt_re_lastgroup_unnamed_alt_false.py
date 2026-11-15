r"""Test 10012 -- lvT re-lastgroup (expected FAIL): a top-level alternative that is NOT a named
group (`b+`) matches with NO group, so `m.lastgroup` is None in CPython (`kind("b")`), not a `str`;
the read is not admitted (the match local keeps the opaque lowering), so `-> str` with a length
claim is not proved. Control: 10010.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re

_P = re.compile(r"(?P<A>a+)|b+")


#@ ensures len(\result) >= 0
#@ assigns \nothing
def kind(s: str) -> str:
    m = _P.match(s, 0)
    if not m:
        return ""
    k = m.lastgroup
    return k


if __name__ == "__main__":
    r = kind("b")
    print("VIOLATION type" if not isinstance(r, str) else "result", r)
