r"""Test 1738 — WITNESS for `PYCSL-SEM-HAPPY`: an `except` name that is not a method.

"A typo in the exempt set would silently widen the policy" — `except setterr` for a
function actually called `setter` would exempt nothing and confine everything, or (worse,
in the other direction) look like it exempted something. The refusal names the known
methods. One of the refusals `bin/check-refusal-witness-coverage.py` measured as having no
witness.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ happy own:
#@     protects g.v
#@     except setterr

#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0


g = C()


#@ requires n >= 0
#@ assigns g.v
def setter(n: int) -> None:
    g.v = n
