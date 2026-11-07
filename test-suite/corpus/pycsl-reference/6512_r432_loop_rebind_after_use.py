r"""Test 6512 -- route #432 (expected FAIL): a guard outside a loop whose body rebinds the receiver after the use (g4 probe) under `#@ no_exception \all`. Not PROVED at base 1c083dcbe either (Why3 rejects the rebinding of the Union parameter); a RULE witness for the narrowing STOP at a loop that rebinds after the use. CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Optional, List

#@ no_exception \all
def f(x: Optional[str], ys: List[Optional[str]]) -> int:
    n = 0
    if x is not None:
        for y in ys:
            n += len(x.strip())
            x = y
    return n


if __name__ == "__main__":
    try:
        r = f("a", [None, None])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
