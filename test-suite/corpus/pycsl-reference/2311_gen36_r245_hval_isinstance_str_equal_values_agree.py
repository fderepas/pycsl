r"""Test 2311 — route #245 (expected PASS): CONTROL. `isinstance(<hval>, str)` in a contract
keeps the opaque `hval_isinst_opaque` arm: builtin `==` never relates a str to a value of another
type, so equal values agree on the test and the claim is TRUE. CPython: both strs.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ requires d["a"] == d["b"]
#@ ensures isinstance(d["a"], str) == isinstance(d["b"], str)
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    return 0


if __name__ == "__main__":
    dd = {"a": "x", "b": "x"}
    assert dd["a"] == dd["b"]
    assert isinstance(dd["a"], str) == isinstance(dd["b"], str)
