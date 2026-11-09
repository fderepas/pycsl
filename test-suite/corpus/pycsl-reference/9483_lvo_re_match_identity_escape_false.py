r"""Test 9483 -- lvO re.Match model (expected FAIL): `m == n` compares two FRESH match objects
(CPython: identity, False). A match local that escapes into `==` is NOT a match local (the analysis is
fail-closed), so it keeps the opaque lowering and the deterministic handle can never make
`\result == True` prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re

_KV = re.compile(r"(\w+)=(\w+)")


#@ ensures \result == True
#@ assigns \nothing
def same_obj(s: str) -> bool:
    m = _KV.match(s)
    n = _KV.match(s)
    return m == n


if __name__ == "__main__":
    r = same_obj("a=b")
    print("VIOLATION contract" if r is not True else "result", r)
