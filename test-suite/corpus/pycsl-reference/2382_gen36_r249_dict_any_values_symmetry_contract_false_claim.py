r"""Test 2382 — route #249 (expected FAIL): Values of a `Dict[str, Any]`: `requires d["a"] == d["b"]` PROVED `ensures d["b"] == d["a"]`.
CPython `{"a": A(), "b": B()}`.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any, Dict


#@ requires "a" in d and "b" in d
#@ requires d["a"] == d["b"]
#@ ensures d["b"] == d["a"]
#@ assigns \nothing
def f(d: Dict[str, Any]) -> int:
    return 0


if __name__ == "__main__":
    class A:
        def __eq__(self, o: object) -> bool:
            return True

        def __hash__(self) -> int:
            return 0

    class B:
        def __eq__(self, o: object) -> bool:
            return False

        def __hash__(self) -> int:
            return 0

    d = {"a": A(), "b": B()}
    assert d["a"] == d["b"] and not (d["b"] == d["a"])
