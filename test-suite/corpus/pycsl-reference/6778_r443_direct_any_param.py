r"""Test 6778 -- route #443 (expected FAIL, rule witness): a parameter `x: Any` used directly as a method receiver. NOT proved at base fa7cbb1aa either (the Any lowering leaves a goal Unknown -- by accident of the lowering, not by a rule); now REFUSED by the rule (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE). CPython: f(1) raises AttributeError.
"""
# pycsl-expected: FAIL
from typing import Any, List

#@ no_exception \all
def f(x: Any) -> int:
    return len(x.strip())


if __name__ == "__main__":
    try:
        print("result", f(1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
