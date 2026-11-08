r"""Test 5877 -- driver run #3 route #226 polarity flip (expected FAIL): red team 29 `a46_init_param_default_name` — a second store `self.x = x - 10` after `self.x = 5` under `self.x >= 0`. The constructor goal was not stated and every method ASSUMED the invariant (PROVED at 8f4221371; CPython violates). Now the goal is stated (and FAILS) or the class is REFUSED (PYCSL-R226-INVARIANT-GOAL-NOT-STATED).
"""
# pycsl-expected: FAIL
#@ class invariant self.x >= 0
class C:
    def __init__(self, x: int = 0) -> None:
        self.x = 5
        self.x = x - 10

#@ ensures \result >= 0
def f(c: C) -> int:
    return c.x

if __name__ == "__main__":
    print(f(C()))
