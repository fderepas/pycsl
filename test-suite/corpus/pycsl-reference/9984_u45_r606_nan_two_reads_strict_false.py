r"""Test 9984 -- route #606 (INTRODUCED, rt59 g13) (expected FAIL: PROVED at int61 c0204b8e1 in the default mode, REFUSED under --strict-float-finite as PYCSL-R606-PYVAL-FLOAT-COMPARE-STRICT at HEAD): under `--strict-float-finite`, `v == w` for two reads of one PyVal float key PROVED at int61 (default); CPython NaN != NaN
"""
# pycsl-flags: --strict-float-finite
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    w = d.get("a")
    if isinstance(v, float):
        if v == w:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f({"a": float("nan")})
    print("VIOLATION contract" if r != 0 else "result", r)
