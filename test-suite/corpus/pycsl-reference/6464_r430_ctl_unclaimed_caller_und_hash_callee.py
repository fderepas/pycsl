r"""Test 6464 -- route #430 (expected PASS): CONTROL: an UN-CLAIMED caller of an un-claimed callee hashing `m.get("a")` (`#UND`) is not refused: the callee's TypeError is ambient for both, and since route #431 an ambient exception only ends a function abnormally, so `ensures \result == n + 1` describes every normal return. PROVED at base and candidate (CPython raises TypeError on `{"a": [1]}`, returns n + 1 on `{"a": "x"}`).
"""
# pycsl-expected: PASS
from typing import Dict, Any


#@ ensures \result == n + 1
def h(m: Dict[str, Any], n: int) -> int:
    s = {m.get("a")}
    return n + 1


#@ ensures \result == n + 1
def caller(m: Dict[str, Any], n: int) -> int:
    return h(m, n)


if __name__ == "__main__":
    print(caller({"a": "x"}, 0))
