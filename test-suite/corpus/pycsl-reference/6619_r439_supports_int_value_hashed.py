r"""Test 6619 -- route #439 (expected FAIL): NEW probe: `{c}` with `c: SupportsInt` (a `typing` Protocol; an unhashable class with `__int__` satisfies it). FAILS at base 1c083dcbe (another goal; not a false proof there, kept as a regression witness of the rule); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNHASHABLE-RECORD).
"""
# pycsl-expected: FAIL
from typing import SupportsInt

class I:
    __hash__ = None

    def __int__(self) -> int:
        return 1


#@ no_exception \all
def f(c: SupportsInt) -> int:
    s = {c}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(I())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
