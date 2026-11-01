r"""Test 8018 -- route #506 (expected FAIL: PROVED at base, REFUSED PYCSL-R506-TRIGGER-SITE-UNLOWERED): f claims `#@ no_exception \all` and returns `len(d["b"].upper())`; the str-method lowering drops its receiver (`upper_0 ()`), so the KeyError of `d["b"]` was never asked; CPython f([], {}) raises KeyError
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ no_exception \all
def f(xs: List[str], d: Dict[str, str]) -> int:
    return len(d["b"].upper())


if __name__ == "__main__":
    try:
        print("result", f([], {}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
