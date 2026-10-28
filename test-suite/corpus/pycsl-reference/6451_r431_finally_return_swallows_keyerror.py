r"""Test 6451 -- route #431 (expected FAIL): rg-dict-r3 probe l3n. The same `finally: return` swallow over an ambient KeyError `d["a"]` of an un-claimed function (the hole is not specific to hashing): `ensures out[0] == 1` PROVED at base 725a1c7e5; CPython leaves out[0] == 2 (the `__main__` driver prints VIOLATION). Now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ requires len(out) == 1
#@ ensures out[0] == 1
#@ assigns out[0]
def f(d: Dict[str, int], out: List[int]) -> None:
    out[0] = 2
    try:
        x = d["a"]
        out[0] = 1
    finally:
        return


if __name__ == "__main__":
    o = [0]
    f({}, o)
    print("VIOLATION" if o[0] != 1 else "ok", o)
