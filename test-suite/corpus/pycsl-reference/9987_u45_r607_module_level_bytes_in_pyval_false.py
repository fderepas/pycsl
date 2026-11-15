r"""Test 9987 -- route #607 (expected FAIL: type-checks at int61 e9e12b6a8, where its proof TIMES OUT -- not a demonstrated false proof; the refusal guards the module-level spelling of rt59 o13 --, REFUSED PYCSL-R607-PYVAL-BYTES-VALUE at HEAD): rt59 o13's bytes literal in a MODULE-LEVEL `Dict[str, PyVal]` constant: the value model tags `b"xy"` as `HArr` of ints, so `isinstance(v, list)` would be decided true; CPython False
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

_D: Dict[str, PyVal] = {"a": b"xy"}


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": [1]}
    v = d.get("a")
    if isinstance(v, list) and isinstance(_D.get("a"), bytes):
        return 1
    return 0


if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 0 else "result", r)
