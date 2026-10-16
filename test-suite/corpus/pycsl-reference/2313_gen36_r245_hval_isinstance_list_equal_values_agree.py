r"""Test 2313 — route #245 (expected PASS): CONTROL. `isinstance(<hval>, list)` in a contract
keeps the opaque `hval_isinst_opaque` arm: builtin `==` never relates a list to a value of another
type, so equal values agree on the test and the claim is TRUE. CPython: both lists.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ requires d["a"] == d["b"]
#@ ensures isinstance(d["a"], list) == isinstance(d["b"], list)
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    return 0


if __name__ == "__main__":
    dd = {"a": [1], "b": [1]}
    assert dd["a"] == dd["b"]
    assert isinstance(dd["a"], list) == isinstance(dd["b"], list)
