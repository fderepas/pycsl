"""Test 0599 — string-valued module constant folds to a real Why3 string (0442.md C5).

A module-level `TAG = "hello"` is a string constant; it must be in contract scope and fold to
the Why3 string literal `"hello"` (string identity is `string` equality), not an int hash.
Before this fix a string module constant was not collected at all — `\result == TAG` raised
"Undefined variable 'TAG'". RED on the prior commit.
"""
# pycsl-flags: --memory-model hoare
TAG = "hello"


#@ ensures \result == TAG
#@ assigns \nothing
def get_tag() -> str:
    return TAG
