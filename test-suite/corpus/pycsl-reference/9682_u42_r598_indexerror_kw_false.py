r"""Test 9682 -- route #598 (expected FAIL: PROVED at base bfe0e38fb in the default model, REFUSED PYCSL-R598-RAISE-CONSTRUCTOR-ARITY in every model at HEAD): red team rt57 hs1973: `raise IndexError("a", q=1)` under `except IndexError`; CPython raises TypeError under `no_exception \all`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional

#@ no_exception \all
#@ ensures \result == 1
def f(k: int) -> int:
    try:
        raise IndexError("a", q=1)
    except IndexError:
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
