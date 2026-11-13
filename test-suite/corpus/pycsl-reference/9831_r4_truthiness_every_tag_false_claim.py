r"""Test 9831 — dict-value-model-r4 law `truthiness of every tag` (expected FAIL): the FALSE claim is NOT proved (CPython runs the honest twin 9830's answer).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"n": None, "f": False, "z": 0, "e": "", "t": (), "l": [], "m": {}, "x": 0.0, "T": True, "s": "q", "u": (0,), "k": [0], "p": {"a": 0}, "o": 2, "g": 0.5}
    if (not d.get("n") and not d.get("f") and not d.get("z") and not d.get("e") and not d.get("t") and not d.get("l") and not d.get("m") and not d.get("x") and d.get("T") and d.get("s") and d.get("u") and d.get("k") and d.get("p") and d.get("o") and d.get("g")):
        return 1
    return 0
