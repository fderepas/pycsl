r"""Test 6617 -- route #439 (expected FAIL): NEW probe: `hash(c)` with `c: Hashable` (structural: `([1],)` is `Hashable`, its hash raises). FAILS at base 1c083dcbe (another goal; not a false proof there, kept as a regression witness of the rule); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNHASHABLE-RECORD).
"""
# pycsl-expected: FAIL
from typing import Hashable

#@ no_exception \all
def f(c: Hashable) -> int:
    return hash(c)


if __name__ == "__main__":
    try:
        r = f(([1],))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
