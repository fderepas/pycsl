r"""Test 1677 - ROUTE #191 control (gen #30): giving the TYPED `NoneExpr` arm route #44's opaque costs an ORDINARY integer store nothing. The same three store positions with a real `int` still read back their exact value, so the repair is a `None`-only loss of a WRONG decision, not a loss of the element/value/field model.
"""
from typing import Dict, List, Optional

_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[Optional[int]] = [1]
    xs[0] = 7
    d: Dict[str, Optional[int]] = {"a": 1}
    d["a"] = 9
    if xs[0] == 7:
        if d["a"] == 9:
            return 1
    return 2
