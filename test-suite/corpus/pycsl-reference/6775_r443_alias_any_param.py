r"""Test 6775 -- route #443 (expected FAIL): a parameter annotated by a module alias of `Any` (`PyVal = Any`; `x: PyVal`) used as a method receiver -- the class name `PyVal` resolves to no known class. NOT proved at base fa7cbb1aa either (Unknown: rule witness); CPython AttributeError. Now REFUSED (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Any

PyVal = Any


#@ no_exception \all
def f(x: PyVal) -> int:
    return len(x.upper())


if __name__ == "__main__":
    try:
        print("result", f(1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
