r"""Test 9983 -- route #606 (INTRODUCED, rt59 g01) (expected FAIL: PROVED at int61 c0204b8e1 in the default mode, REFUSED under --strict-float-finite as PYCSL-R606-PYVAL-FLOAT-COMPARE-STRICT at HEAD): under `--strict-float-finite`, `isinstance(v, float)` then `v == v` (hval_eq reflexive on HFloat) PROVED `\result == 0` at int61 with byte-identical WhyML; CPython f(float("nan")) == 1
"""
# pycsl-flags: --strict-float-finite
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(v: PyVal) -> int:
    if isinstance(v, float):
        if v == v:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f(float("nan"))
    print("VIOLATION contract" if r != 0 else "result", r)
