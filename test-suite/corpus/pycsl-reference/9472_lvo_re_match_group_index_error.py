r"""Test 9472 -- lvO re.Match model (expected FAIL): `m.group(3)` on a 2-group pattern raises
IndexError in CPython (the pattern's group count is computed by CPython's own parser), so the read
lowers to a failing `assert false` VC.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re

_KV = re.compile(r"(\w+)=(\w+)")


#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def third(s: str) -> str:
    m = _KV.match(s)
    if m:
        return m.group(3)
    return ""


if __name__ == "__main__":
    try:
        third("a=b")
        print("result ok")
    except IndexError:
        print("VIOLATION IndexError")
