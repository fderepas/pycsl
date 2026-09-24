r"""Test 1892 — gen #31 (expected PASS, and the PASS IS THE DEBT): ROUTE #226's second
carrier, which increment 1 does NOT close.

`self.n = n` from an unannotated `__init__` PARAMETER, no `#@ requires`, and no construction
in the file. There is no literal for the constructor obligation to be stated about, so the
literal-substitution device emits nothing and this file keeps verifying. In CPython
`C(1).get()` is `1`, and `1 >= 5` is False.

This file is in the corpus marked PASS on purpose, the way 1862 is: a green row that records
a live unsoundness is worth more than no row, because the day increment 2 lands, this file
must go RED and the suite will say so. If it goes red before then, something else closed it
and the route file needs reading.

The measured surround, so the second increment is not designed blind:
  · with `c = C(1)` in the file                          FAILED  (construction site checked)
  · with `#@ requires n >= 5` on `__init__` and `C(7)`   SUCCESS (the precondition works)
so the honest statement for this shape is `forall n. n >= 5`, which is false — i.e. such a
class should not verify unless `__init__` carries a `#@ requires`.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ class invariant self.n >= 5
class C:
    def __init__(self, n: int) -> None:
        self.n = n

    #@ ensures \result >= 5
    #@ assigns \nothing
    def get(self) -> int:
        return self.n
