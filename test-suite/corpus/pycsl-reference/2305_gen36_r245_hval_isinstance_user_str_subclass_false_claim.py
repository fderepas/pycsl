r"""Test 2305 — route #245 (expected FAIL): in a CONTRACT, `isinstance(<hval>, S)` was the
uninterpreted `hval_isinst_opaque h "S"` on the erased `HInt` carrier -- a FUNCTION OF THE HVAL --
so `requires d["a"] == d["b"]` PROVED the two tests agree at 8260571f. CPython `{"a": S("x"), "b": "x"}` with `class S(str)`: equal, and only the first is an S.
The opaque arm of a class whose builtin values can be `==` to a value of another type is now REFUSED at
the WhyML type-check (`pycsl_refused_contract_type_test_on_erased_hval`, fail-closed).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


class S(str):
    pass


#@ requires d["a"] == d["b"]
#@ ensures isinstance(d["a"], S) == isinstance(d["b"], S)
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    return 0


if __name__ == "__main__":
    dd = {"a": S("x"), "b": "x"}
    assert dd["a"] == dd["b"]
    assert isinstance(dd["a"], S) != isinstance(dd["b"], S)
