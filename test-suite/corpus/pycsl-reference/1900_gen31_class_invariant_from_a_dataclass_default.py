r"""Test 1900 — gen #31 WITNESS for ROUTE #226's FOURTH carrier (expected FAIL): a
`@dataclass` whose field DEFAULT does not establish the invariant.

A dataclass's synthesized `__init__` takes every field as a PARAMETER, so `C(3)` is legal
Python and the default `n: int = 0` constrains nothing. The obligation is therefore the
same one witness 1892 carries — quantify over the parameter, make the binding a premise:

    goal _check_class_inv_d : forall n : int. n = n -> ((n >= 5))

Before increment 2 this file printed `[+] Verification SUCCESS!` while `read(D())` is `0`
in CPython. ZERO classes in either corpus, the mirrors or `pycsl_lib` are dataclasses
carrying a `#@ class invariant`, so this shape had no user and no witness until now.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

_ = 0  # anchor


#@ class invariant self.n >= 5
@dataclass
class D:
    n: int = 0


#@ ensures \result >= 5
#@ assigns \nothing
def read(d: D) -> int:
    return d.n
