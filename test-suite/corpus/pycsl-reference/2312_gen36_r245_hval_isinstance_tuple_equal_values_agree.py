r"""Test 2312 — route #245 (expected PASS): CONTROL. `isinstance(<hval>, tuple)` in a contract
keeps the opaque `hval_isinst_opaque` arm: builtin `==` never relates a tuple to a value of another
type, so equal values agree on the test and the claim is TRUE. CPython: both tuples.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ requires d["a"] == d["b"]
#@ ensures isinstance(d["a"], tuple) == isinstance(d["b"], tuple)
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    return 0


if __name__ == "__main__":
    dd = {"a": (1, 2), "b": (1, 2)}
    assert dd["a"] == dd["b"]
    assert isinstance(dd["a"], tuple) == isinstance(dd["b"], tuple)
