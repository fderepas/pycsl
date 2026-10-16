r"""Test 2310 — route #245 (expected PASS): CONTROL. `isinstance(<hval>, dict)` in a contract
keeps the opaque `hval_isinst_opaque` arm: builtin `==` never relates a dict to a value of another
type, so equal values agree on the test and the claim is TRUE. CPython: both dicts.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ requires d["a"] == d["b"]
#@ ensures isinstance(d["a"], dict) == isinstance(d["b"], dict)
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    return 0


if __name__ == "__main__":
    dd = {"a": {"k": 1}, "b": {"k": 1}}
    assert dd["a"] == dd["b"]
    assert isinstance(dd["a"], dict) == isinstance(dd["b"], dict)
