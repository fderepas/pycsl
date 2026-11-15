r"""Advice of PYCSL-R603-PYVAL-STR-LAUNDERED-UNDER-CLAIM (the backstop) followed by its second disjunct: corpus 9971
with the `no_exception \all` claim dropped (a TypeError is then an exceptional exit). Expected: VERIFIES.
"""
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("prefix") or "an"
    if "anon".startswith(x):
        return 1
    return 0


if __name__ == "__main__":
    try:
        print("result", f({"prefix": "an"}))
    except TypeError as e:
        print("TypeError (an exceptional exit; no claim)", e)
