"""Test 0821 — WL-05 regression lock (NEGATIVE, set twin of 0820): set-PARAM mutation is REJECTED. # pycsl-expected: FAIL

wrong-lowering-to-fix.md §WL-05. The set twin of the dict param item-write: an
in-place `s.add(x)` / `s.discard(x)` / `s.remove(x)` on a `Set[...]` PARAMETER is out
of scope for the SAME reason — Python mutates the set by reference, the caller must
see it, and PyCSL's by-value `map int (option int)` param carries no `writes {s}`
frame. The old lowering silently DROPPED the mutation to a no-op (`let _ = s_add_1 x
in ()`) — sound but UNFAITHFUL (a caller-visible write vanished). The fix REJECTS it
cleanly (`PYCSL-WHYML-PARAM-COLLECTION-MUT`). This driver locks the rejection: it must
NOT produce a "Verification SUCCESS" (a raised PIPELINE ERROR ⇒ XFAIL). A LOCAL set
add-membership IS faithfully modelled and proves (0823).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Set


#@ ensures \result >= 0
def mutate_set_param(s: Set[int]) -> int:
    s.add(5)
    return 0
