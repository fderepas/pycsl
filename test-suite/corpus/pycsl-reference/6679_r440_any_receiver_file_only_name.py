r"""Test 6679 -- route #440 A1 (expected FAIL): `x: Any; x.rindex(".")` under `#@ no_exception \all`, where only a file class defines `rindex`. Route #161 admitted the call by the file's tail NAME; the receiver is not derived as that class (a `str` reaches it: CPython raises ValueError, the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED: a file method admits only on its own class's receivers).
"""
# pycsl-expected: FAIL
from typing import Any


class Buffer:
    def rindex(self, v: int) -> int:
        return 0


#@ no_exception \all
def last_dot(x: Any) -> int:
    return x.rindex(".")


if __name__ == "__main__":
    try:
        r = last_dot("README")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
