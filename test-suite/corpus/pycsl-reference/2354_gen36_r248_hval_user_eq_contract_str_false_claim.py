r"""Test 2354 — route #248 (expected FAIL): the `hval` side. `PyVal` is `Any`, so a `Dict[str, PyVal]`
can hold a user object; `requires d["a"] == d["b"]` (hval `=`) PROVED `ensures isinstance(d["a"], str)
== isinstance(d["b"], str)` at afe28c69 (the decided `HStr` arm). CPython `{"a": "s", "b": W()}`.
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
    class W:
        def __eq__(self, o: object) -> bool:
            return True

    dd = {"a": "s", "b": W()}
    assert dd["a"] == dd["b"]
    assert isinstance(dd["a"], str) != isinstance(dd["b"], str)
