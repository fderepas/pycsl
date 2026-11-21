r"""Test 6615 -- route #439 (expected FAIL): red team 34 pp08: `{c}` with `c: Pr`, `class Pr(Protocol)` with `__len__` (a list satisfies it structurally); `f([1])`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNHASHABLE-RECORD).
"""
# pycsl-expected: FAIL
from typing import Protocol

class Pr(Protocol):
    def __len__(self) -> int:
        ...


#@ no_exception \all
def f(c: Pr) -> int:
    s = {c}
    return len(s)


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
