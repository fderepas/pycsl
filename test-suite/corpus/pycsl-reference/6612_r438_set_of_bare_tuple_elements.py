r"""Test 6612 -- route #438 (expected FAIL): NEW probe: `set(xs)` with `xs: List[tuple]` hashes each element (a hashed iterable). FAILS at base 1c083dcbe (another goal; not a false proof there, kept as a regression witness of the rule); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM).
"""
# pycsl-expected: FAIL
from typing import List

#@ no_exception \all
def f(xs: List[tuple]) -> int:
    s = set(xs)
    return len(s)


if __name__ == "__main__":
    try:
        r = f([([1],)])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
