r"""Test 3598 — gen #37 r2c-wall R2c-local (expected FAIL).

REFUSAL (derived-local hole, local twin): `x = generics["G"]` then a path append through `generics`; CPython sees the append through `x` (len 1), the value model would not. `ensures \result == 0` is false in CPython; refused (root escapes into a partner).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def refuse_read_partner(n: int) -> int:
    generics: Dict[str, PyVal] = {}
    generics["G"] = {"methods": []}
    x: Dict[str, PyVal] = generics["G"]
    generics["G"]["methods"].append(1)
    return len(x["methods"])
