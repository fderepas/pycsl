r"""Test 6548 -- route #432 (expected FAIL): `isinstance(x, object)` (it does not exclude `None`; g4 probe) under `#@ no_exception \all`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Optional

#@ no_exception \all
def f(x: Optional[str]) -> int:
    if isinstance(x, object):
        return len(x.strip())
    return 0


if __name__ == "__main__":
    try:
        r = f(None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
