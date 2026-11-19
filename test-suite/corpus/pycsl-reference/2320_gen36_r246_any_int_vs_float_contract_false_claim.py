r"""Test 2320 — route #246 (expected FAIL): in a CONTRACT, `isinstance(<Any>, int)` was
`subtag (typeof_op x) tag_int`, a FUNCTION OF THE STORED INT (route #239), so `requires x == y`
PROVED that the two tests agree at f777e2bd. CPython `f(1, 1.0)`: `1 == 1.0`, and only `1` is an int.
A contract-side test of a class whose builtin `==` crosses types is now REFUSED at the WhyML
type-check (`pycsl_refused_contract_type_test_on_int_erased_value`, fail-closed).
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == y
#@ ensures isinstance(x, int) == isinstance(y, int)
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    return 0


if __name__ == "__main__":
    assert 1 == 1.0
    assert isinstance(1, int) != isinstance(1.0, int)
