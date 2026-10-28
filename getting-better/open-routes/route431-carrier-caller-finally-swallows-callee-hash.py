r"""OPEN ROUTE #431 carrier (probe l3p, executor rg 2026-10-28): an un-claimed caller's `return` in `finally:` swallows the callee's ambient hash TypeError, so `ensures out[0] == 1` PROVED (before the repair); CPython leaves out[0] == 2. CLOSED by the route #431 repair (executor h430, 2026-10-28): now REFUSED (PYCSL-R431-FINALLY-JUMP-SWALLOWS-EXCEPTION); bin/check-open-route-carriers.py asserts REFUSED.
"""
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
    print(o)
