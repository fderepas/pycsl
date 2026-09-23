r"""Test 1807 — ROUTE #216 CONTROL (expected PASS): a dunder with NO override is untouched.

The refusal must be a guard on the OVERRIDE PAIR, not a ban on dunders or on
`--check-behavioral-subtyping`. This file carries the flag and a `__len__`, and no second
class redeclares it, so nothing is claimed about substitutability and nothing is refused.

Its sibling control is the one the refusal's own message points at: two UNRELATED classes
may each define `__len__` under the flag without being refused, because neither is a base
or a `#@ conforms_to` target of the other.
"""
# pycsl-flags: --check-behavioral-subtyping --memory-model hoare
# pycsl-expected: PASS
_ = 0  # anchor


class Only:
    #@ ensures \result >= 5
    def __len__(self) -> int:
        return 5


#@ ensures \result >= 5
def use(n: int) -> int:
    return 5
