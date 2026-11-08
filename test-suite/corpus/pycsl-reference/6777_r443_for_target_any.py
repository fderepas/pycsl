r"""Test 6777 -- route #443 (expected FAIL): a `for` target over `List[Any]` used as a method receiver. NOT proved at base fa7cbb1aa either (Timeout: rule witness); CPython AttributeError. Now REFUSED (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ no_exception \all
def f(xs: List[Any]) -> int:
    n = 0
    for v in xs:
        n += len(v.strip())
    return n


if __name__ == "__main__":
    try:
        print("result", f([1]))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
