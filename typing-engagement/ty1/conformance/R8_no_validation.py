"""Runtime gate R8 — no validation of arm membership.

Spec clause R8 (union-twoplane-spec.md §2.4): the shim must perform NO
validation of annotated values — a shim that CHECKED whether a value belongs
to a Union arm would be unfaithful. This driver asserts the identity
postcondition on a call where `val` is a type that is provably NOT in any
arm of `Union[int, str]` (a `bool` would be a subtype of int under some
type systems; instead we use a `list` literal). The identity must discharge.

Expected (from spec): prove identity (no arm-membership check fires).
"""

from pycsl_lib.typ import Union


#@ ensures \result == val
def f(val) -> int:
    return Union(int, str, val)


if __name__ == "__main__":
    # a list value is NOT in {int, str}; if the shim validated arm
    # membership this postcondition would not discharge.
    assert f([1, 2, 3]) == [1, 2, 3]
    print("PASS")
