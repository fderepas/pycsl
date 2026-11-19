r"""Test 1901 — gen #31 CONTROL for 1892/1900 (expected PASS): the constructor's
PRECONDITION is what establishes the invariant, and it must keep working.

This is the (u4) counter-program for route #226's increment 2, and it was constructed
BEFORE the increment rather than after it. A premise-free obligation — `forall n. n >= 5` —
would refuse this file, and it is a good program: `#@ requires n >= 5` on `__init__` is
exactly the contract that makes the invariant establishable, and every construction site
must discharge it (`C(7)` does; `C(1)` does not and FAILS).

So the emitted goal carries `__init__`'s own `#@ requires` as premises:

    goal _check_class_inv_c : forall n : int. n = n -> (n >= 5) -> ((n >= 5))

If this file ever goes red, increment 2 has started refusing constructors that DO establish
their invariant, rather than the ones that do not.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ class invariant self.n >= 5
class C:
    #@ requires n >= 5
    def __init__(self, n: int) -> None:
        self.n = n

    #@ ensures \result >= 5
    #@ assigns \nothing
    def get(self) -> int:
        return self.n


#@ ensures \result >= 5
def use() -> int:
    c = C(7)
    return c.get()
