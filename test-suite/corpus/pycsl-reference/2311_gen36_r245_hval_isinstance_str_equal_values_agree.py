r"""Test 2311 — route #245 (expected PASS until route #248; expected FAIL now): CONTROL. `isinstance(<hval>, str)` in a contract
keeps the opaque `hval_isinst_opaque` arm: builtin `==` never relates a str to a value of another
type, so equal values agree on the test and the claim is TRUE. CPython: both strs.
Route #248: `PyVal`/`Any` admit any object, so this relied on BUILTIN `==`; CPython `{"a": "s", "b": W()}` with a user `__eq__` (always True) makes the claim FALSE (corpus 2354). The contract-side
test is now REFUSED at the WhyML type-check (fail-closed); it was a FALSE claim, not a control.
"""
# pycsl-expected: FAIL
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
