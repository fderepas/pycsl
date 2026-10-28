r"""Test 6660 -- route #440 A2 (expected FAIL): `b: Buffer` (a file class without `upper`); `len(b.upper())` under `#@ no_exception \all`. Route #161 admitted `upper` by its whitelisted NAME whatever the receiver's class; CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED: a file class's receiver admits only a method its file MRO defines).
"""
# pycsl-expected: FAIL
from typing import List


class Buffer:
    def __init__(self) -> None:
        self.items: List[int] = []

    def size(self) -> int:
        return len(self.items)


#@ no_exception \all
def f(b: Buffer) -> int:
    return len(b.upper())


if __name__ == "__main__":
    try:
        r = f(Buffer())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
