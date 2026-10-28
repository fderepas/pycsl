r"""Test 6533 -- route #433 (expected FAIL): `",".join(xs)`, `xs: List[Optional[str]]` under `#@ no_exception \all`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R433-JOIN-ELEMENT-CLASS).
"""
# pycsl-expected: FAIL
from typing import List, Optional

#@ no_exception \all
def f(xs: List[Optional[str]]) -> int:
    return len(",".join(xs))


if __name__ == "__main__":
    try:
        r = f(["a", None])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
