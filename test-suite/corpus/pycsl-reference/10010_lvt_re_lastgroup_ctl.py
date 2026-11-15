r"""Test 10010 -- lvT re-lastgroup CONTROL (expected PASS): every top-level alternative of the
module-constant pattern is ONE named group, so after a successful match `m.lastgroup` is a `str`
(the matched alternative's name, never None): it lowers to the law-free `re_lastgroup_op h` after
the `m <> 0` VC (discharged behind `if not m`), so a `str` local receives it.
Twins (must FAIL): 10011-10014.
"""
# pycsl-expected: PASS
from __future__ import annotations
import re

_P = re.compile(r"(?P<A>a+)|(?P<B>b+)")


#@ requires True
#@ ensures True
#@ assigns \nothing
def kind(s: str) -> str:
    m = _P.match(s, 0)
    if not m:
        return ""
    k = m.lastgroup
    if k == "A":
        return "alpha"
    return k


if __name__ == "__main__":
    for s in ["aa", "b", "c", ""]:
        r = kind(s)
        print("VIOLATION type" if not isinstance(r, str) else "result", r)
