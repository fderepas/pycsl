r"""Advice of PYCSL-R603-PYVAL-STR-PASSED-AS-STR followed (variant 1): narrow the PyVal value read by a two-argument
`.get` (never None), and pass it on only under `isinstance(v, str)`.
"""
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ assigns \nothing
#@ ensures \result >= 0
def width(s: str) -> int:
    return len(s)


#@ ensures \result >= 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("name", "")
    if isinstance(v, str):
        return width(v)
    return 4


if __name__ == "__main__":
    ok = f({"name": 5}) == 4 and f({"name": "ab"}) == 2
    print("result" if ok else "VIOLATION contract")
