r"""Test 3590 — gen #37 r2c-wall R2c-local (expected PASS).

R2c-local: `generics[t]["methods"].append(e)` on a LOCALLY BUILT hval tree is the functional path write-back of the local root; `len(..) == 1` PROVES. At base the append was refused (#280).
"""
# pycsl-expected: PASS
from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def w_len1(n: int) -> int:
    generics: Dict[str, PyVal] = {}
    t: str = "G"
    if t not in generics:
        generics[t] = {"kind": "class", "methods": []}
    generics[t]["methods"].append({"name": "m"})
    return len(generics[t]["methods"])
