r"""Test 9996 -- route #606 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION FLOAT-FINITE): rt59 g01 in the DEFAULT mode. A PyVal float is the Why3 real, so `v == v` PROVES; CPython refutes it for v = float("nan"). Not a soundness bug of the default mode: `pycsl --soundness-report` now lists FLOAT-FINITE for this file (route #606), exactly as for the plain-float twin 2500; witness 9983 runs it under `--strict-float-finite`, where it is REFUSED
"""
# pycsl-model-assumption: FLOAT-FINITE
# pycsl-expected: PASS
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
    print(f(1.5), f(float("nan")))  # 0 1: the claim is FALSE for NaN
