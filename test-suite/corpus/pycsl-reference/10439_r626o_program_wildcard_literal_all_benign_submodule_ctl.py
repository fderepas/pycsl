r"""Test 10439 -- run #9 u71, review rt79 w2, route #626 control (PASS). The program does `from zp39 import *`
and zp39's literal `__all__ = ["k"]` makes CPython load the benign submodule zp39.k; `cd <tree root> &&
python <this file>` prints "result 3". pycsl follows the `__all__` submodule (judging it like any reached
module) and still PROVES the claim.
"""
# pycsl-expected: PASS
from zp39 import *
from zp39.k import three


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return three()


if __name__ == "__main__":
    print("result", g())
