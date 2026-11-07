r"""Test 1891 — gen #31 CONTROL for 1890 (expected PASS): the constructor DOES establish it.

Byte-identical to 1890 but for `self.n = 7`, which satisfies `self.n >= 5`. The new
`goal _check_class_inv_c : forall n : int. n = 7 -> (n >= 5)` discharges, and `read` still
gets the invariant as an assumption on its parameter — which is the correct behaviour for a
class contract, and is precisely what made 1890 dangerous.

If this one ever goes red, the constructor obligation has started refusing constructors that
do establish their invariant, rather than the ones that do not.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ class invariant self.n >= 5
class C:
    def __init__(self) -> None:
        self.n: int = 7

    #@ ensures \result >= 5
    #@ assigns \nothing
    def get(self) -> int:
        return self.n


#@ ensures \result >= 5
#@ assigns \nothing
def read(c: C) -> int:
    return c.get()
