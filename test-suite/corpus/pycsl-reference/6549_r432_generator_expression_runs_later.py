r"""Test 6549 -- route #432 (expected FAIL): a generator expression built under `if x is not None:` and consumed after `x = None` (g4 probe) under `#@ no_exception \all`. Not PROVED at base 1c083dcbe either (Why3 rejects the rebinding of the Union parameter); a RULE witness for the narrowing STOP at a generator expression (it runs when consumed). CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Optional, List

#@ no_exception \all
def f(x: Optional[str]) -> int:
    if x is not None:
        g = (x.strip() for _ in range(1))
        x = None
        ys = list(g)
        return len(ys)
    return 0


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
