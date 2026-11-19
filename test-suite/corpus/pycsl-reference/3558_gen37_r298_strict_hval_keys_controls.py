r"""Test 3558 — gen #37 route #298 (expected PASS): CONTROLS under `--strict-hval-keys`.

Dropping HVAL-STR-KEYS must not cost the claims that are TRUE in CPython for every nested dict:
the bare loop's `HArr` arm still iterates the REAL list elements (the route #296 control 3495
shape), a key-typed test of the unknown-carrier key still type-checks and decides a 0/1 result,
and a `.items()` loop whose body never observes the key still proves.
"""
# pycsl-flags: --strict-hval-keys
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == True
#@ assigns \nothing
def list_elems_are_str() -> bool:
    holder: Dict[str, PyVal] = {"m": ["a", "b"]}
    m = holder.get("m") or []
    for x in m:
        return isinstance(x, str)
    return True


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def key_test_decides(d: Dict[str, PyVal]) -> int:
    m = d["m"]
    for k in m:
        if isinstance(k, str):
            return 1
    return 0


#@ ensures \result == True
#@ assigns \nothing
def key_unobserved(d: Dict[str, PyVal]) -> bool:
    xs = d["xs"]
    for k, v in xs.items():
        return True
    return True


if __name__ == "__main__":
    print(list_elems_are_str(), key_test_decides({"m": {1: 2}}), key_test_decides({"m": {"a": 2}}),
          key_unobserved({"xs": {1: 2}}))
