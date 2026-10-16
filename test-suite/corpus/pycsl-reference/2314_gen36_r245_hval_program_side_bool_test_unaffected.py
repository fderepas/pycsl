r"""Test 2314 — route #245 (expected PASS): CONTROL. A PROGRAM-side `isinstance(<hval>, bool)` is
untouched: its opaque `HInt` arm is `(any bool)`, a fresh value per evaluation (never a function of
the hval), so the body still verifies against a contract that does not test the type. CPython
`f({"a": True})` = 1 and `f({"a": 1})` = 0, both within `0 <= \result <= 1`.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures 0 <= \result <= 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("a", 0)
    if isinstance(x, bool):
        return 1
    return 0


if __name__ == "__main__":
    assert f({"a": True}) == 1
    assert f({"a": 1}) == 0
