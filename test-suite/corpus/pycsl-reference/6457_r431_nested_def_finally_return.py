r"""Test 6457 -- route #431 (expected FAIL): the `finally: return` swallow inside a NESTED def (lifted to a sibling by Module 5, its own function for the refusal): `inner`'s `ensures o2[0] == 1` and the outer `ensures out[0] == 1` PROVED at base 725a1c7e5; CPython leaves out[0] == 2 (the `__main__` driver prints VIOLATION). Now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Dict, Any, List


#@ requires len(out) == 1
#@ ensures out[0] == 1
#@ assigns out[0]
def f(m: Dict[str, Any], out: List[int]) -> None:
    #@ requires len(o2) == 1
    #@ ensures o2[0] == 1
    #@ assigns o2[0]
    def inner(m2: Dict[str, Any], o2: List[int]) -> None:
        o2[0] = 2
        try:
            n = hash(m2.get("a"))
            o2[0] = 1
        finally:
            return
    inner(m, out)


if __name__ == "__main__":
    o = [0]
    f({"a": [1]}, o)
    print("VIOLATION" if o[0] != 1 else "ok", o)
