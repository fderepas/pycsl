r"""Test 9471 -- lvO re.Match model (expected FAIL): false twin of 9470. Groups 1 and 2 are two
law-free reads of the match handle: nothing relates them, so `\result == True` must NOT prove
(CPython: "a=b" gives False).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re

_KV = re.compile(r"(\w+)=(\w+)")


#@ ensures \result == True
#@ assigns \nothing
def key_is_val(s: str) -> bool:
    m = _KV.match(s)
    if m:
        return m.group(1) == m.group(2)
    return True


if __name__ == "__main__":
    r = key_is_val("a=b")
    print("VIOLATION contract" if r is not True else "result", r)
