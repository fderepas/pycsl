r"""Test 8528 -- route #538 (expected FAIL: NOT PROVED at base (Why3 typing of the list order), REFUSED PYCSL-R538-UNORDERED-TUPLE-COMPARISON at HEAD; the list sibling of red team 50 probe g1105/bf1047): `xs >= ys` of two `List[Any]` parameters compares the elements pairwise; CPython `[1] >= ["a"]` TypeError
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ no_exception \all
def f(xs: List[Any], ys: List[Any]) -> int:
    return 1 if xs >= ys else 0


if __name__ == "__main__":
    try:
        r = f([1], ["a"])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
