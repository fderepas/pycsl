r"""Test 10106 -- route #610 (rt61 M1, expected FAIL): a PARAMETER named `os`: the user method's effect (`self.n = 5`) is dropped. The model of the module call
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

    #@ assigns self.n
    def access(self, p: str, m: int) -> int:
        self.n = 5
        return 1


#@ requires os.n == 0
#@ ensures os.n == 0
def f(os: C) -> int:
    if os.access("x", 1):
        return 1
    return 0


if __name__ == "__main__":
    c = C()
    f(c)
    print("VIOLATION contract" if c.n != 0 else "result", c.n)
