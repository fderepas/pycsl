r"""Test 5878 -- driver run #3 route #226 polarity flip (expected FAIL): the registered carrier `route226-carrier-computed-constructor-store.py`. `self.n = three()` (a COMPUTED int store) under `self.n >= 5`; no goal, the invariant was ASSUMED and `read(C())` PROVED `\result >= 5` (CPython 3). Now REFUSED (PYCSL-R226-INVARIANT-GOAL-NOT-STATED).
"""
# pycsl-expected: FAIL


#@ ensures \result == 3
#@ assigns \nothing
def three() -> int:
    return 3


#@ class invariant self.n >= 5
class C:
    def __init__(self) -> None:
        self.n = three()

    #@ ensures \result >= 5
    #@ assigns \nothing
    def get(self) -> int:
        return self.n


#@ ensures \result >= 5
#@ assigns \nothing
def read(c: C) -> int:
    return c.get()


if __name__ == "__main__":
    print(read(C()))
