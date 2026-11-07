r"""Test 6872 -- route #453 (expected PASS): CONTROL -- a module attribute the real module has (`sys.maxsize`) and `os.path.join` over `str` arguments (a (module, function) row). Not refused by PYCSL-R453-*.
"""
# pycsl-expected: PASS
import os
import sys


#@ no_exception \all
#@ ensures \result == 1
def f(a: str, b: str) -> int:
    p = os.path.join(a, b)
    m = sys.maxsize
    return 1


if __name__ == "__main__":
    print("result", f("x", "y"))
