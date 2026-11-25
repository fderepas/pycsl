r"""Test 10530 -- run #9 u77, review rt87 b1 (route #606, the u74/u76 float-field PyVal carrier). Expected PASS
UNDER THE DECLARED MODEL ASSUMPTION FLOAT-FINITE. A `float` record field stored in a PyVal dict is the
`HFloat` Why3 real (u76's faithful carrier), and `hval_eq` is reflexive, so `d["a"] == d["a"]` PROVES;
`cd <tree root> && python <this file>` prints "CPython f(R(nan)) = 0 , claim 1" (NaN != NaN). This is the
counterexample of FLOAT-FINITE, NOT a soundness bug of the default mode -- provided the assumption is
DECLARED: `pycsl --soundness-report` lists FLOAT-FINITE for this file ("relied on by f: a `float` record
field read (r.x) ..."). At run9-u76 it did not (the detector missed the dict-literal path): that was rt87 b1.
Twin 10531 runs the same program under `--strict-float-finite`, where it is REFUSED.
"""
# pycsl-model-assumption: FLOAT-FINITE
# pycsl-expected: PASS
from dataclasses import dataclass
from typing import Any, Dict

PyVal = Any


@dataclass
class R:
    x: float


#@ ensures \result == 1
#@ assigns \nothing
def f(r: R) -> int:
    d: Dict[str, PyVal] = {"a": r.x}
    if d["a"] == d["a"]:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython f(R(nan)) =", f(R(float("nan"))), ", claim 1")
