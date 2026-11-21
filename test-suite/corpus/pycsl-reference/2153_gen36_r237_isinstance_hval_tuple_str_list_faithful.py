r"""Test 2153 — route #237 (expected PASS): CONTROL for 2143. A KNOWN string value (`HStr`)
satisfies `isinstance(x, (str, list))` — the per-constructor disjunction decides True and
`\result == 1` PROVES (at base the tuple form was the contentless `isinstance_op 0 0`).
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": "s"}
    x = d.get("a", {})
    if isinstance(x, (str, list)):
        return 1
    return 0
