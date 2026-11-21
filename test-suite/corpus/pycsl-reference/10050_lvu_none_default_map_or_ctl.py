r"""Test 10050 -- lvU none-default map parameter `x or {}` CONTROL (expected PASS): `d` is an
`Optional[Dict[str, int]] = None` parameter lowered as a bare map, so `d = d or {}` keeps that map
(CPython: an equal dict -- `d` itself, or a fresh `{}` when `d` is empty or None) and `d.get(k, 0)` reads
it. The claim holds for every map: negative values are clamped. Twins (must FAIL): 10051-10055.
"""
# pycsl-expected: PASS
from typing import Dict, Optional


#@ ensures \result >= 0
#@ assigns \nothing
def g(k: str, d: Optional[Dict[str, int]] = None) -> int:
    d = d or {}
    v = d.get(k, 0)
    if v < 0:
        return 0
    return v


if __name__ == "__main__":
    for k, d in [("a", None), ("a", {}), ("a", {"a": 3}), ("a", {"a": -2}), ("b", {"a": 3})]:
        r = g(k, d)
        print("VIOLATION contract" if r < 0 else "result", r)
