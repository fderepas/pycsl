r"""Test 9971 -- route #603 (expected FAIL: refused at int61 e9e12b6a8 by the builtin signature row of `str.startswith` (the argument may be underivable), REFUSED PYCSL-R603-PYVAL-STR-LAUNDERED-UNDER-CLAIM at HEAD -- the claimed backstop, which fires first): under `no_exception \all`, x = `d.get("prefix") or "an"` (a PyVal the model types `string`) is passed to `"anon".startswith(x)`; CPython TypeError for {"prefix": 5}
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ no_exception \all
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("prefix") or "an"
    if "anon".startswith(x):
        return 1
    return 0


if __name__ == "__main__":
    try:
        print("result", f({"prefix": 5}))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
