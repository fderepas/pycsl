r"""Test 8921 -- lvD f-string ternary segment (expected FAIL): false twin of 8920. With `c` true the
segment is the `'a'` arm, so `\result == "xb"` must NOT prove (CPython: tag(True) == "xa").
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ requires c == True
#@ ensures \result == "xb"
#@ assigns \nothing
def tag(c: bool) -> str:
    return f"x{'a' if c else 'b'}"


if __name__ == "__main__":
    r = tag(True)
    print("VIOLATION contract" if r != "xb" else "result", r)
