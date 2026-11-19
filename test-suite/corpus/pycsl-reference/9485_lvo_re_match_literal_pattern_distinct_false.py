r"""Test 9485 -- lvO re.Match model (expected FAIL): false twin of 9484. Two DIFFERENT literal
patterns give unrelated handles, so `\result == True` must NOT prove (CPython: "Stack[int]" matches the
first and not the second, giving False).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re


#@ ensures \result == True
#@ assigns \nothing
def agree(s: str) -> bool:
    m = re.match(r"^([A-Za-z_]+)\[([A-Za-z_]+)\]$", s)
    n = re.match(r"^([A-Za-z_]+)$", s)
    if m:
        if n:
            return True
        return False
    return True


if __name__ == "__main__":
    r = agree("Stack[int]")
    print("VIOLATION contract" if r is not True else "result", r)
