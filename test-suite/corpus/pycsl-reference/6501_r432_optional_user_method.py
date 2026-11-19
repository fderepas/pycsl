r"""Test 6501 -- route #432 (expected FAIL): a user method on `Optional[C]` under `#@ no_exception \all`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Optional

class C:
    def __init__(self) -> None:
        self.k: int = 1
    def m(self) -> int:
        return 2


#@ no_exception \all
def f(c: Optional[C]) -> int:
    return c.m()


if __name__ == "__main__":
    try:
        r = f(None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
