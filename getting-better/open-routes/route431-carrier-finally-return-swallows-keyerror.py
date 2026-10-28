r"""OPEN ROUTE #431 carrier (probe l3n, executor rg 2026-10-28): `return` in `finally:` swallows an ambient KeyError, so `ensures out[0] == 1` PROVED (before the repair); CPython leaves out[0] == 2. CLOSED by the route #431 repair (executor h430, 2026-10-28): now REFUSED (PYCSL-R431-FINALLY-JUMP-SWALLOWS-EXCEPTION); bin/check-open-route-carriers.py asserts REFUSED.
"""
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
    print(o)
