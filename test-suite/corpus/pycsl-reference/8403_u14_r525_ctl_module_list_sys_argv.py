r"""Test 8403 -- route #525 (control, expected PASS): `import sys` used only for a plain value attribute (`sys.argv`) does not reach the module namespace, so the module str list keeps the proved `_OPS_lit ()` lowering; CPython returns 0
"""
# pycsl-expected: PASS
import sys
from typing import Any, Dict, List, Optional

OPS = ["abc", "defg"]


#@ ensures \result == 0
def f(k: int) -> int:
    for x in OPS:
        if x == "z":
            return 1
    return 0


if __name__ == "__main__":
    print("result", f(len(sys.argv)))
