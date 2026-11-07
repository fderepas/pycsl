r"""Test 5872 -- driver run #3 route #226 polarity flip (expected FAIL): red team 29 `a08_field_from_field` — `self.y = self.x` (a field computed from a field) under `self.y >= 0`. The constructor goal was not stated and every method ASSUMED the invariant (PROVED at 8f4221371; CPython violates). Now the goal is stated (and FAILS) or the class is REFUSED (PYCSL-R226-INVARIANT-GOAL-NOT-STATED).
"""
# pycsl-expected: FAIL
#@ class invariant self.y >= 0
class C:
    def __init__(self, x: int) -> None:
        self.x = x
        self.y = self.x

    #@ ensures \result >= 0
    #@ assigns \nothing
    def get(self) -> int:
        return self.y

if __name__ == "__main__":
    print(C(-1).get())
