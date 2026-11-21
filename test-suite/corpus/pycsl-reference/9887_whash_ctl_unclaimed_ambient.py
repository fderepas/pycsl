r"""Test 9887 -- W-hash (dict-value-model-r4 §2.5, expected PASS): CONTROL: an UN-NARROWED `PyVal` value hashed with NO claim (a `PyVal` parameter in a set display and as a dict key, an `hval` read in a set display) is ADMITTED: TypeError is outside KNOWN_EXCEPTIONS, so it is ambient and only ends the function abnormally (route #431 refuses the `finally:` jump that could swallow it; P1 of dict-value-model-r3-impl §R2), and the honest `ensures` of every normal return PROVES. REFUSED at base for the parameter (denied as `Any`).
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == n + 1
def f(v: PyVal, n: int) -> int:
    s = {v}
    return n + 1


#@ ensures \result == n + 2
def g(v: PyVal, n: int) -> int:
    m: Dict[PyVal, int] = {}
    m[v] = 2
    return n + 2


#@ ensures \result == n + 1
def h(n: int) -> int:
    d: Dict[str, PyVal] = {"a": "s"}
    v = d.get("a")
    s = {v}
    return n + 1


if __name__ == "__main__":
    print(f("a", 0), g(1, 0), h(0))
    try:
        f([1], 0)
    except TypeError:
        print("ambient TypeError: no normal return, the ensures is not concerned")
