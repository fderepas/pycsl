r"""Test 9675 -- route #597 (expected FAIL: PROVED at base bfe0e38fb in the default model, REFUSED PYCSL-R597-RAISE-NAME-REBOUND in every model at HEAD): red team rt57 hs1964: an annotated assignment `E: Any = dict` inside the def; CPython raises TypeError under `no_exception \all`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional

class E(Exception):
    pass


#@ no_exception \all
#@ ensures \result == 1
def f(k: int) -> int:
    E: Any = dict
    try:
        raise E("a")
    except E:
        return 1
    return 2


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
