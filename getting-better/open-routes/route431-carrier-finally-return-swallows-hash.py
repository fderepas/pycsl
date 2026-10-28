r"""OPEN ROUTE #431 carrier (probe l3o, executor rg 2026-10-28): `return` in `finally:` swallows an ambient hash TypeError of an un-claimed function, so `ensures out[0] == 1` PROVES; CPython leaves out[0] == 2. Gated by bin/check-open-route-carriers.py (SUCCESS today).
"""
from typing import Dict, Any, List

#@ requires len(out) == 1
#@ ensures out[0] == 1
#@ assigns out[0]
def f(m: Dict[str, Any], out: List[int]) -> None:
    out[0] = 2
    try:
        n = hash(m.get("a"))
        out[0] = 1
    finally:
        return

if __name__ == "__main__":
    o = [0]
    f({"a": [1]}, o)
    print(o)
