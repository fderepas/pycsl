r"""Test 1892 — gen #31 WITNESS for ROUTE #226's SECOND carrier (expected FAIL): the field
comes from an `__init__` PARAMETER.

`self.n = n` under `#@ class invariant self.n >= 5`. There is no literal for the
constructor obligation to be stated about, so INCREMENT 1 was silent here and this file
verified — in CPython `C(1).get()` is `1`, and `1 >= 5` is False.

**This file shipped GREEN on purpose for one increment**, marked `# pycsl-expected: PASS`
with a docstring saying the PASS was the debt, so that the day increment 2 landed the suite
would say so. It did.

INCREMENT 2 states the obligation without substituting anything: it quantifies over the
PARAMETER and makes the constructor's binding a PREMISE —

    goal _check_class_inv_c : forall n : int. n = n -> ((n >= 5))

The binder set is the UNION of the field labels and the int parameters, so the field `n`
and the parameter `n` bind ONCE; with different names it reads `forall m n. m = n -> …`.
Nothing is substituted into the invariant text, which is why this does not repeat the
half-applied-patch failure of lesson (b5).

The measured surround, unchanged:
  · with `c = C(1)` in the file                          FAILED  (construction site checked)
  · with `#@ requires n >= 5` on `__init__` and `C(7)`   SUCCESS (witness 1901)
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ class invariant self.n >= 5
class C:
    def __init__(self, n: int) -> None:
        self.n = n

    #@ ensures \result >= 5
    #@ assigns \nothing
    def get(self) -> int:
        return self.n
