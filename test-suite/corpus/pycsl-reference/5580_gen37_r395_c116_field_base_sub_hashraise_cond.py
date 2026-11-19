r"""Test 5580 -- gen #37 route #395 (expected FAIL): the file subclass `D(B)` defines a `__hash__` that raises ValueError (not verified `no_exception`) (CPython TypeError / ValueError; PROVED at base 3b2d2e763). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: B is unhashable at a hashing site when a file subclass is).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


class B:
    def __init__(self) -> None:
        self.x: int = 1


class D(B):
    def __hash__(self) -> int:
        if self.x == 1:
            raise ValueError("h")
        return 0


#@ no_exception \all
def f(b: B) -> int:
    s = {b}
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f(D()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
