r"""Test 10037 -- route #608 F2 (PRE-EXISTING, u46 probe q02) (expected FAIL: PROVED at base int62 c4159443b (u46 report), REFUSED PYCSL-R603-PYVAL-STR-LOWERED-TYPE-TEST at HEAD): a loop target over `cs: List[Dict[str, PyVal]]` is a PyVal container that the by-name tracking of route #603 did not see, so `isinstance(c.get("a") or "z", str)` was lowered `1 = 1` and `\result == 0` PROVED; CPython f([{"a": 5}]) == 1
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(cs: List[Dict[str, PyVal]]) -> int:
    for c in cs:
        x = c.get("a") or "z"
        if isinstance(x, str):
            return 0
        return 1
    return 0

if __name__ == "__main__":
    r = f([{"a": 5}])
    print("VIOLATION contract" if r != 0 else "result", r)
