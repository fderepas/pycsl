r"""Test 6779 -- route #443 (expected FAIL, rule witness): a parameter `x: object` used directly as a method receiver. NOT proved at base fa7cbb1aa either (Unknown); now REFUSED by the rule (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE). CPython: f(1) raises AttributeError.
"""
# pycsl-expected: FAIL
from typing import Any, List

#@ no_exception \all
def f(x: object) -> int:
    return len(x.strip())


if __name__ == "__main__":
    try:
        print("result", f(1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
