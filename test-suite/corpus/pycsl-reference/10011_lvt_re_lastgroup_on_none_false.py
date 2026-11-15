r"""Test 10011 -- lvT re-lastgroup (expected FAIL): `m.lastgroup` on a failed match (`None`)
raises AttributeError in CPython (`kind("c")`), so the read's `m <> 0` VC (emitted with every
read, as for `m.group(k)`) fails. Control: 10010.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re

_P = re.compile(r"(?P<A>a+)|(?P<B>b+)")


#@ requires True
#@ ensures True
#@ assigns \nothing
def kind(s: str) -> str:
    m = _P.match(s, 0)
    k = m.lastgroup
    return k


if __name__ == "__main__":
    try:
        kind("c")
        print("result ok")
    except AttributeError:
        print("VIOLATION AttributeError")
