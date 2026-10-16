r"""Test 2355 — route #248 (expected FAIL): the same through WHOLE-dict equality. `requires d == e` (map
`=`) equated `d["a"]` and `e["a"]`, so the `str` tests agreed and the postcondition PROVED at afe28c69.
CPython `{"a": "s"} == {"a": W()}` is True (dict `==` compares values with `==`).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ requires d == e
#@ ensures isinstance(d["a"], str) == isinstance(e["a"], str)
#@ assigns \nothing
def f(d: Dict[str, PyVal], e: Dict[str, PyVal]) -> int:
    return 0


if __name__ == "__main__":
    class W:
        def __eq__(self, o: object) -> bool:
            return True

    d1 = {"a": "s"}
    e1 = {"a": W()}
    assert d1 == e1
    assert isinstance(d1["a"], str) != isinstance(e1["a"], str)
