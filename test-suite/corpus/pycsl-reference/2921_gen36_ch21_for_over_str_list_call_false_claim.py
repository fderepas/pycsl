r"""Test 2921 — gen #36 ch21 (expected FAIL): FALSE twin of 2920. The list starts with `""`
and the loop only APPENDS, so `\length(\result) == 0` is false (CPython: 3); it must stay
UNPROVED now that the call-iterable loop type-checks (non-vacuity of the seam).
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \length(\result) == 2
#@ assigns \nothing
def defs() -> List[str]:
    return ["a", "b"]


#@ ensures \length(\result) == 0
#@ assigns \nothing
def indent_all() -> List[str]:
    out: List[str] = [""]
    #@ loop invariant \length(out) >= 1
    for line in defs():
        out.append(f"  {line}")
    return out


if __name__ == "__main__":
    r = indent_all()
    assert len(r) == 3
    print(r)
