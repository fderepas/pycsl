r"""Test 6526 -- route #433 (expected FAIL): `" ".join(d.values())` over `Optional[str]` values under `#@ no_exception \all`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R433-JOIN-ELEMENT-CLASS).
"""
# pycsl-expected: FAIL
from typing import Dict, Optional

#@ no_exception \all
def f(d: Dict[str, Optional[str]]) -> int:
    return len(" ".join(d.values()))


if __name__ == "__main__":
    try:
        r = f({"a": None})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
