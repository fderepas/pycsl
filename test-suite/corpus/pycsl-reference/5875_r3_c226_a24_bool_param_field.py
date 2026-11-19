r"""Test 5875 -- driver run #3 route #226 polarity flip (expected FAIL): red team 29 `a24_bool_param_field` — a bool PARAMETER stored into the field read by `self.n >= 1`. The constructor goal was not stated and every method ASSUMED the invariant (PROVED at 8f4221371; CPython violates). Now the goal is stated (and FAILS) or the class is REFUSED (PYCSL-R226-INVARIANT-GOAL-NOT-STATED).
"""
# pycsl-expected: FAIL
#@ class invariant self.n >= 1
class C:
    def __init__(self, b: bool) -> None:
        self.n = b

    #@ ensures \result >= 1
    #@ assigns \nothing
    def get(self) -> int:
        return self.n

if __name__ == "__main__":
    print(C(False).get())
