r"""Test 9475 -- lvO re.Match model (expected PASS): the TRUTH test of an optional group is
`present && len > 0` (None and "" are both falsy), so a `str` read of it under that test discharges its
presence VC, and the group-1 read (outside any repeat / alternation) needs none. Twin: 9476 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import re

_OPT = re.compile(r"(\w+)(?:-(\w+))?")


#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def suffix_or_stem(s: str) -> str:
    m = _OPT.match(s)
    if m:
        if m.group(2):
            return m.group(2)
        return m.group(1)
    return ""


if __name__ == "__main__":
    for s in ["abc", "ab-cd", "", "-"]:
        r = suffix_or_stem(s)
        print("VIOLATION contract" if not isinstance(r, str) else "result", r)
