r"""Test 2156 — route #237 (expected PASS): CONTROL. A KNOWN list value (`HArr`) is NOT a dict:
`isinstance(x, dict)` decides False and `\result == 0` PROVES (at base the constant `true`
made it 1).
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": [7]}
    x = d.get("a", {})
    if isinstance(x, dict):
        return 1
    return 0
