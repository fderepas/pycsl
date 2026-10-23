r"""Test 2313 — route #245 (expected PASS until route #248; expected FAIL now): CONTROL. `isinstance(<hval>, list)` in a contract
keeps the opaque `hval_isinst_opaque` arm: builtin `==` never relates a list to a value of another
type, so equal values agree on the test and the claim is TRUE. CPython: both lists.
Route #248: `PyVal`/`Any` admit any object, so this relied on BUILTIN `==`; CPython `{"a": [1], "b": W()}` with a user `__eq__` (always True) makes the claim FALSE. The contract-side
test is now REFUSED at the WhyML type-check (fail-closed); it was a FALSE claim, not a control.
"""
# pycsl-expected: FAIL
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
