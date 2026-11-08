r"""Test 3491 — gen #37 route #296 (expected FAIL): `xs = d["xs"]` (no `or`-default) then a bare `for x in xs`: same key arm. CPython: False.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def first_is_str(d: Dict[str, PyVal]) -> bool:
    xs = d["xs"]
    for x in xs:
        return isinstance(x, str)
    return True

if __name__ == "__main__":
    print(first_is_str({"xs": [{"k": 1}]}))
