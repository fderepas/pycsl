"""Test 0505 — collections (Tier 3): ChainMap / User* are opaque handles.

ChainMap composition (lookup fall-through across maps) and the User* subclass wrappers
(UserDict/UserList/UserString) are NOT modelled — they stay opaque, returning an int handle with
no content reasoning. This smoke test confirms a program importing and constructing them still
compiles and verifies a contract over the opaque result (here, a constant return)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import ChainMap


#@ ensures \result == 0
def opaque_chainmap() -> int:
    cm = ChainMap()
    return 0
