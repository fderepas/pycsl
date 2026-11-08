r"""Test 6452 -- route #431 (expected FAIL): rg-dict-r3 probe l3p. An un-claimed caller's `finally: return` swallows the un-claimed callee's ambient hash TypeError, so `ensures out[0] == 1` PROVED at base 725a1c7e5; CPython leaves out[0] == 2 (the `__main__` driver prints VIOLATION). Now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Dict, Any, List


#@ ensures \result == 1
def h(m: Dict[str, Any]) -> int:
    n = hash(m.get("a"))
    return 1


#@ requires len(out) == 1
#@ ensures out[0] == 1
#@ assigns out[0]
def caller(m: Dict[str, Any], out: List[int]) -> None:
    out[0] = 2
    try:
        out[0] = h(m)
    finally:
        return


if __name__ == "__main__":
    o = [0]
    caller({"a": [1]}, o)
    print("VIOLATION" if o[0] != 1 else "ok", o)
