r"""Test 10045 -- route #608 control (expected PASS): a string-lowered `x = d.get("a") or "z"` used only by the admitted reads whose result is opaque for a non-str value -- `x in ("z", "q")` (a display of literals) and `len(x)` (the length of the uninterpreted `hval_opaque_str`); `\result >= 0` holds on every normal return
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result >= 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("a") or "z"
    if x in ("z", "q"):
        return len(x)
    return 0

if __name__ == "__main__":
    print("result", f({}), f({"a": "q"}))
