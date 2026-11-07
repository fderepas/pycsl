r"""Test 3061 — gen #37 ch24 (expected FAIL): FALSE twin of 3060's `is_decl`. `"val x"`
starts with `"val "`, so the tuple test is true and the result is 1 (CPython: 1);
`\result == 0` must stay UNPROVED now that the tuple-prefix `startswith` is faithful
(non-vacuity of the seam).
"""
# pycsl-expected: FAIL
from typing import List


#@ requires s == "val x"
#@ ensures \result == 0
#@ assigns \nothing
def is_decl(s: str) -> int:
    if s.startswith(("type ", "val ")):
        return 1
    return 0


if __name__ == "__main__":
    print(is_decl("val x"))
