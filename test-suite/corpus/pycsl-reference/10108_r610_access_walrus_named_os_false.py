r"""Test 10108 -- route #610 (rt61 M1, expected FAIL): a WALRUS target named `os` shadows the module in the function. The model of the module call
applies only when the head name is the module import, bound nowhere in the function and not
rebound at module level; here it is not, so the file is REFUSED
(`PYCSL-R610-EXT-MODULE-NAME-SHADOWED`) rather than lowered as the module call.
"""
# pycsl-expected: FAIL
import os


class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 1
    #@ assigns self.n
    def access(self, p: str, m: int) -> int:
        self.n = self.n + 1
        return 1


#@ ensures \result == 0
def f(c: C) -> int:
    if (os := c):
        os.access("x", 1)
    return c.n


if __name__ == "__main__":
    r = f(C())
    print("VIOLATION contract" if r != 0 else "result", r)
