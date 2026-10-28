r"""Test 6528 -- route #433 (expected FAIL): `b"".join(xs)`, `xs: List[Optional[bytes]]` under `#@ no_exception \all`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R433-JOIN-ELEMENT-CLASS).
"""
# pycsl-expected: FAIL
from typing import List, Optional

#@ no_exception \all
def f(xs: List[Optional[bytes]]) -> int:
    return len(b"".join(xs))


if __name__ == "__main__":
    try:
        r = f([None])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
