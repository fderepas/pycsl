r"""Test 6453 -- route #431 (expected FAIL): a `continue` in `finally:` inside a loop swallows the ambient hash TypeError of an un-claimed function (CPython leaves out[0] == 2; the `__main__` driver prints VIOLATION). Now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Dict, Any, List


#@ requires len(out) == 1
#@ ensures out[0] == 1
#@ assigns out[0]
def f(m: Dict[str, Any], out: List[int]) -> None:
    out[0] = 2
    i = 0
    #@ loop invariant 0 <= i <= 1
    #@ loop variant 1 - i
    while i < 1:
        i = i + 1
        try:
            n = hash(m.get("a"))
            out[0] = 1
        finally:
            continue


if __name__ == "__main__":
    o = [0]
    f({"a": [1]}, o)
    print("VIOLATION" if o[0] != 1 else "ok", o)
