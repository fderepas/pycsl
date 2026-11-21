r"""Test 6532 -- route #433 (expected FAIL): `"".join(xs)`, `xs: List[bytes]` under `#@ no_exception \all`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R433-JOIN-ELEMENT-CLASS).
"""
# pycsl-expected: FAIL
from typing import List

#@ no_exception \all
def f(xs: List[bytes]) -> int:
    return len("".join(xs))


if __name__ == "__main__":
    try:
        r = f([b"a"])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
