# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
"""1281 — (#49) ROUTE #98's NAMED FENCE: why `assigns` was the ONLY clause that failed
SILENTLY, kept as a standing witness.

Every contract clause OTHER than `assigns` goes through EXPRESSION RENDERING, which emits
the SOURCE identifier into a module whose signature binds the MANGLED one. The result is a
hard Why3 rejection — measured verbatim:

    File ".../x.mlw", line 9: unbound function or predicate symbol 'model'

`assigns` is the one clause consumed STRUCTURALLY instead, by `_emit_frame_condition`, and
that function answered "nothing" where every other path raises. So the name-mangling
inconsistency is tree-wide and fail-closed EVERYWHERE EXCEPT the single clause whose
consumer was silent — which is exactly why route #98's repair is correctly scoped to
`_emit_frame_condition` rather than to the renderer.

THIS ALSO BOUNDS ROUTE #96's CAPABILITY ARM: witness 1271 (a trusted stub with both
`assigns a[0..n]` and `ensures a[0] == 9`, which MUST prove) CANNOT be written for a renamed
parameter at all, because its `ensures` is rejected here. That is a LOUD boundary, not a
silent one, and this file holds it in place.

>>> IF THIS FILE EVER XPASSES, the renderer has started mangling contract identifiers. That
>>> is a capability gain, not a bug — but it moves `assigns` out of its uniquely-silent
>>> position and this witness must be re-derived rather than simply re-blessed.
"""


#@ requires n >= 0
#@ requires \length(model) > n + 1
#@ assigns model[0..n]
#@ \trusted reviewer: route98
def scramble(model: list, n: int) -> int:
    model[0] = 0
    return 0


#@ requires \length(arr) > 3
#@ ensures \result == 0
def driver(arr: list) -> int:
    return scramble(arr, 1)
