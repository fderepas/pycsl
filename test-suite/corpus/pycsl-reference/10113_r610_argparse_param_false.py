r"""Test 10113 -- route #610 (rt61 M1, expected FAIL): a PARAMETER named `argparse`: `argparse.ArgumentParser()` is the user method (an effect on `argparse.n`). The model of the module call
applies only when the head name is the module import, bound nowhere in the function and not
rebound at module level; here it is not, so the file is REFUSED
(`PYCSL-R610-EXT-MODULE-NAME-SHADOWED`) rather than lowered as the module call.
"""
# pycsl-expected: FAIL
import argparse


class A:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def ArgumentParser(self) -> int:
        self.n = self.n + 1
        return 0


#@ ensures argparse.n == \old(argparse.n)
def f(argparse: A) -> int:
    try:
        p = argparse.ArgumentParser()
    except (AttributeError, IndexError, TypeError, ValueError):
        return 0
    return 1


if __name__ == "__main__":
    a = A()
    f(a)
    print("VIOLATION contract" if a.n != 0 else "result", a.n)
