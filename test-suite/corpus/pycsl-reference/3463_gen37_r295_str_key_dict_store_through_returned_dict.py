r"""Test 3463 -- route #295 (expected FAIL): a `Dict[str, int]`: `e = ids2(d); e["a"] = 2; return d["a"]` PROVED `\result == 1`; CPython: 2. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict

#@ assigns \nothing
#@ \trusted
def ids2(x: Dict[str, int]) -> Dict[str, int]:
    return x

#@ ensures \result == 1
def f() -> int:
    d: Dict[str, int] = {"a": 1}
    e = ids2(d)
    e["a"] = 2
    return d["a"]

if __name__ == "__main__":
    assert f() == 2, f()
