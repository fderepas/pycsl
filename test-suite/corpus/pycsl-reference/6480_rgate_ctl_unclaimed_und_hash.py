r"""Test 6480 -- route R-gate (expected PASS): CONTROL: the S2 bodies WITHOUT the claim (rg-dict-r3 c_01 / c_02 / c_06): hashing `m.get(..)` (`#UND`) in un-claimed functions is not refused. Its TypeError is ambient, and since route #431 an ambient exception only ends a function abnormally, so each `ensures` describes every normal return. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Dict, Any, Set


#@ ensures \result == n + 1
def f(m: Dict[str, Any], n: int) -> int:
    s = {m.get("a")}
    return n + 1


#@ ensures \result == n + 1
def g(f2: Dict[str, Any], seen: Set[Any], n: int) -> int:
    seen.add(f2.get("name"))
    return n + 1


#@ ensures \result == n + 1
def k(m: Dict[str, Any], n: int) -> int:
    d = {m.get("a"): 1}
    return n + 1


if __name__ == "__main__":
    print(f({"a": "x"}, 0), g({"name": "n"}, set(), 0), k({"a": 2}, 0))
