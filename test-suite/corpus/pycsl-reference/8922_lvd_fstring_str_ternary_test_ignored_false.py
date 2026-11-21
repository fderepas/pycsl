r"""Test 8922 -- lvD f-string ternary segment (expected FAIL): false twin of 8920. Without the
`requires c` the test decides the arm, so `\result == "xa"` must NOT prove (CPython: tag(False) == "xb").
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == "xa"
#@ assigns \nothing
def tag(c: bool) -> str:
    return f"x{'a' if c else 'b'}"


if __name__ == "__main__":
    r = tag(False)
    print("VIOLATION contract" if r != "xa" else "result", r)
