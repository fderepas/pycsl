# Route #592 advice 'make `d` a required parameter of the callee (no `None` default)': witness 9630 with
# `d: Dict[str, str]` required and the caller passing it.
from typing import Dict


#@ ensures \result == 1
#@ assigns \nothing
def g(x: int, d: Dict[str, str]) -> int:
    return 1 if isinstance(d, dict) else 0


#@ ensures \result == 2
#@ assigns \nothing
def h() -> int:
    y = g(3, {})
    return y + 1


if __name__ == "__main__":
    print("result", h())   # CPython: result 2
