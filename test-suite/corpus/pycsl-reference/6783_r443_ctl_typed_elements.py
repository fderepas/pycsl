r"""Test 6783 -- route #443 (expected PASS): CONTROL -- elements of `List[str]` / values of `Dict[str, str]` as method receivers are derived `str`; PROVED at base and candidate.
ROUTE #506 (run #4): now expected FAIL -- REFUSED PYCSL-R506-TRIGGER-SITE-UNLOWERED by design. The subscript sits in a position the lowering never evaluates, so the IndexError / KeyError obligation the `no_exception \all` claim covers is absent from the VC; the program is CPython-honest only because of its guard / data, which the model never checks (`xs[0].strip()` / `d["a"].upper()` lower without their receivers: twin 8018 PROVED at base, CPython KeyError; bound-first twin 8029).
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ no_exception \all
def f(xs: List[str], d: Dict[str, str]) -> int:
    if len(xs) == 0 or "a" not in d:
        return 0
    return len(xs[0].strip()) + len(d["a"].upper())


if __name__ == "__main__":
    print("result", f([" a "], {"a": "b"}))
