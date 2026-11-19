"""Test 0821 — WL-05b regression lock (POSITIVE, set twin of 0820): set-PARAM add-membership PROVES.

wrong-lowering-to-fix.md §WL-05b. The set twin of the dict param item-write: an
in-place `s.add(x)` on a `Set[...]` PARAMETER is now FAITHFULLY SUPPORTED. Python
mutates the set by reference, so the caller must see it — the emitter models an
inner-mutated set param as a caller-visible MUTABLE `ref (map int (option int))` with a
sound `writes {s}` frame. `s.add(5)` lowers to `s := map_update_some !s 5 0` and the
membership `5 in s` to `match Map.get !s 5 with Some _ -> true | None -> false end` —
UNIFORMLY through the ref (the old lowering silently DROPPED the mutation to a no-op,
sound but UNFAITHFUL). After `s.add(5)`, `5 in s` holds and the function returns `1` —
a genuine observable CONSEQUENCE of the mutation. This driver was a NEGATIVE rejection
lock under WL-05; WL-05b converts it to POSITIVE.
"""
_ = 0  # anchor
from typing import Set


#@ ensures \result == 1
def mutate_set_param(s: Set[int]) -> int:
    s.add(5)
    if 5 in s:
        return 1
    return 0
