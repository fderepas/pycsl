"""Test 1271 — route #96 CAPABILITY-PRESERVATION control: the repair closed a hole and did
NOT delete a capability. THIS IS THE ARM THAT MUST **PROVE**.

A repair that makes every exploit refuse is worthless if it also makes the honest program
refuse — "both directions are always measured". A `\trusted` stub that declares an array
`assigns` AND an array `ensures` must still deliver that postcondition to its caller across the
newly-emitted `writes { a }`: the clause havocs `a`, and the stub's own `ensures a[0] == 9` then
pins the post-state cell the caller reads.

If this file ever stops proving, the frame repair has become a capability deletion and must be
reverted, not narrowed.
"""
# pycsl-flags: --memory-model hoare

#@ requires n >= 0
#@ requires \length(a) > n + 1
#@ assigns a[0..n]
#@ ensures a[0] == 9
#@ \trusted reviewer: route96
def scramble(a: list, n: int) -> int:
    a[0] = 9
    return 0


#@ requires \length(arr) > 3
#@ ensures \result == 9
def driver(arr: list) -> int:
    scramble(arr, 1)
    return arr[0]
