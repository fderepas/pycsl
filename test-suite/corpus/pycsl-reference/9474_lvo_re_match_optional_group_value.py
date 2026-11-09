r"""Test 9474 -- lvO re.Match model (expected FAIL): group 2 of `(\w+)(?:-(\w+))?` sits under a
min-0 repeat, so CPython returns None for it when it does not take part ("abc"); a `str` read of it
carries the VC `re_group_present_op h 2`, which must NOT prove (the declared `-> str` is violated).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re

_OPT = re.compile(r"(\w+)(?:-(\w+))?")


#@ ensures True
#@ assigns \nothing
def suffix(s: str) -> str:
    m = _OPT.match(s)
    if m:
        return m.group(2)
    return ""


if __name__ == "__main__":
    r = suffix("abc")
    print("VIOLATION contract" if not isinstance(r, str) else "result", r)
