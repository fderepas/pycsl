r"""Test 9476 -- lvO re.Match model (expected FAIL): false twin of 9475. Whether an optional group
took part is a law-free read of the handle, so `\result == True` must NOT prove (CPython: "abc" matches
with group 2 None, giving False).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re

_OPT = re.compile(r"(\w+)(?:-(\w+))?")


#@ ensures \result == True
#@ assigns \nothing
def has_suffix(s: str) -> bool:
    m = _OPT.match(s)
    if m:
        if m.group(2):
            return True
        return False
    return True


if __name__ == "__main__":
    r = has_suffix("abc")
    print("VIOLATION contract" if r is not True else "result", r)
