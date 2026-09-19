r"""Test 1674 - ROUTE #191 carrier (gen #30): a `None` STORED into a dict value read back as the integer 0. The dict-LITERAL position was route #184; the STORE `d["a"] = None` reaches the TYPED `NoneExpr` arm and answered the literal `0`, so `d["a"] == 0` PROVED True while CPython says False. Closed by the same general repair.
"""
# pycsl-expected: FAIL
from typing import Dict, Optional

_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    d: Dict[str, Optional[int]] = {"a": 1}
    d["a"] = None
    v = d["a"]
    if v == 0:
        return 1
    return 2
