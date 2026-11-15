r"""Test 9997 -- route #606 control (expected PASS under `--strict-float-finite`; advice of PYCSL-R606-PYVAL-FLOAT-COMPARE-STRICT followed): a PyVal value compared with a LITERAL is admitted under the strict flag (NaN == 1.5 is False and so may the model's value be); `\result == 1` for the stored 1.5 (CPython 1)
"""
# pycsl-flags: --strict-float-finite
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": 1.5}
    v = d.get("a")
    if isinstance(v, float) and v == 1.5:
        return 1
    return 0


if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 1 else "result", r)
