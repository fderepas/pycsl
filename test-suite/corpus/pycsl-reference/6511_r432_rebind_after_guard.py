r"""Test 6511 -- route #432 (expected FAIL): a rebinding `x = y` after the `is None` early return (g4 probe) under `#@ no_exception \all`. Not PROVED at base 1c083dcbe either (Why3 rejects the rebinding of the Union parameter); a RULE witness for the narrowing STOP at a rebinding. CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Optional

#@ no_exception \all
def f(x: Optional[str], y: Optional[str]) -> int:
    if x is None:
        return 0
    x = y
    return len(x.strip())


if __name__ == "__main__":
    try:
        r = f("a", None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
