r"""Test 8402 -- route #525 (control, expected PASS): a module-level str list read only as a `for` iterable, in a module with no namespace / object-graph access, keeps the proved `_OPS_lit ()` lowering: `ensures \result == 0` proves; CPython returns 0 (red team 49 control g1019/aa1034_control_plain.py)
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional

OPS = ["abc", "defg"]


#@ ensures \result == 0
def f(k: int) -> int:
    for x in OPS:
        if x == "z":
            return 1
    return 0


if __name__ == "__main__":
    print("result", f(0))
