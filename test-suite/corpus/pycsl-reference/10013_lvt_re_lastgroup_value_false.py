r"""Test 10013 -- lvT re-lastgroup (expected FAIL): the model is LAW-FREE (it does not even claim
the value is one of the group names), so a claim about WHICH group matched is not proved; it is
false anyway: `kind("b")` is "B". Control: 10010.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re

_P = re.compile(r"(?P<A>a+)|(?P<B>b+)")


#@ ensures \result == "A"
#@ assigns \nothing
def kind(s: str) -> str:
    m = _P.match(s, 0)
    if not m:
        return "A"
    k = m.lastgroup
    return k


if __name__ == "__main__":
    r = kind("b")
    print("VIOLATION contract" if r != "A" else "result", r)
