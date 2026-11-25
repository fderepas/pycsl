r"""Test 10531 -- run #9 u77, review rt87 b1 (route #606): the `--strict-float-finite` twin of 10530. Expected
FAIL: with FLOAT-FINITE dropped, the PyVal self-comparison is REFUSED (PYCSL-R606-PYVAL-FLOAT-COMPARE-STRICT,
"compares a PyVal value with a non-literal operand under `--strict-float-finite`"). `cd <tree root> && python
<this file>` prints "CPython f(R(nan)) = 0 , claim 1": the claim is false for a NaN field.
"""
# pycsl-flags: --strict-float-finite
# pycsl-expected: FAIL
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
