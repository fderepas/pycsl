r"""Test 6507 -- route #432 (expected FAIL): `.upper()` on a second `Optional[str]` parameter under `#@ no_exception \all`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Optional

#@ no_exception \all
def f(s: str, x: Optional[str]) -> int:
    return len(x.upper())


if __name__ == "__main__":
    try:
        r = f("abc", None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
