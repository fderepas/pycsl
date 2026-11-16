r"""Test 10117 -- route #610 CONTROL (expected PASS): a parameter NAMED `os` used only as a plain object (`os.n`, never `os.<f>(..)` of a modelled family) is fine, and a GENUINE `os.access` in ANOTHER function of the same file keeps the model (the rule is per function scope).
"""
# pycsl-expected: PASS
import os


class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0


#@ ensures \result == os.n
#@ assigns \nothing
def g(os: C) -> int:
    return os.n


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def f(p: str) -> int:
    if os.access(p, 4):
        return 1
    return 0


if __name__ == "__main__":
    print("result", g(C()), f("."))
