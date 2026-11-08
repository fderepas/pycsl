r"""Test 6538 -- route #437 (expected FAIL): `sorted(xs)`, `xs: List[Tuple[int, Dict[str, int]]]` under `#@ no_exception \all`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R437-UNORDERED-ELEMENTS).
"""
# pycsl-expected: FAIL
from typing import Dict, List, Tuple

#@ no_exception \all
def f(xs: List[Tuple[int, Dict[str, int]]]) -> int:
    ys = sorted(xs)
    return len(ys)


if __name__ == "__main__":
    try:
        r = f([(1, {"a": 1}), (1, {"b": 2})])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
