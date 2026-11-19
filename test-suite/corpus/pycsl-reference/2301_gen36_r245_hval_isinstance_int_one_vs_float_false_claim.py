r"""Test 2301 — route #245 (expected FAIL): in a CONTRACT, `isinstance(<hval>, int)` was the
uninterpreted `hval_isinst_opaque h "int"` on the erased `HInt` carrier -- a FUNCTION OF THE HVAL --
so `requires d["a"] == d["b"]` PROVED the two tests agree at 8260571f. CPython `{"a": 1, "b": 1.0}`: `1 == 1.0`, and only `1` is an int.
The opaque arm of a class whose builtin values can be `==` to a value of another type is now REFUSED at
the WhyML type-check (`pycsl_refused_contract_type_test_on_erased_hval`, fail-closed).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ requires d["a"] == d["b"]
#@ ensures isinstance(d["a"], int) == isinstance(d["b"], int)
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    return 0


if __name__ == "__main__":
    dd = {"a": 1, "b": 1.0}
    assert dd["a"] == dd["b"]
    assert isinstance(dd["a"], int) != isinstance(dd["b"], int)
