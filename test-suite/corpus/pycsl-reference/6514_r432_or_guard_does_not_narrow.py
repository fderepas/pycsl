r"""Test 6514 -- route #432 (expected FAIL): `if x is not None or y:` (a disjunction does not narrow; g4 probe) under `#@ no_exception \all`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Optional

#@ no_exception \all
def f(x: Optional[str], y: bool) -> int:
    if x is not None or y:
        return len(x.strip())
    return 0


if __name__ == "__main__":
    try:
        r = f(None, True)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
