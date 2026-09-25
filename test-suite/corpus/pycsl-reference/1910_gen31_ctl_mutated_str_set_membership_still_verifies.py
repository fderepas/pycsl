r"""Test 1910 — gen #31 (expected PASS): CONTROL for `1909` — the MUTATED `Set[str]` param.

The same `m in held` membership as `1909`, on a parameter the body ALSO `.add`s to. This
verified BEFORE the I4 fixpoint and must still verify after it: the mutation is what used to
buy the string key, and the fix must not take it away while granting it to the read-only case.

    _sk = "string" if (_mut_coll and kt.get(arg) == "string") else "int"   # before
    _sk = "string" if (kt.get(arg) == "string") else "int"                 # after

Dropping the `_mut_coll` conjunct WIDENS the string-keyed set; it must not narrow it. This
file is how that is checked.

IF THIS FILE EVER FAILS, the `_mut_coll` branch has been lost and `1909`'s diagnosis is wrong.
Was `getting-better/open-routes/setelem-control-mutated-str-set-membership.py`.
"""
# pycsl-expected: PASS
_ = 0  # anchor
from typing import Set


#@ ensures \result == 1
#@ assigns held
def add_then_test(held: Set[str], m: str) -> int:
    held.add(m)
    if m in held:
        return 1
    return 0
