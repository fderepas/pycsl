"""Test 0208 - ghost counter in for loop.

(#34) THIS TEST WAS `pycsl-expected: FAIL` FOR A REASON THAT WAS A BUG IN THE
INGESTOR, NOT IN THE TEST. `#@ ghost total += 1` sits directly above an `if`, and
`Module1_Ingestor._Harvester._make` returned `mk(None, None)` for `If`/`Try`/
`TryStar`/`Match`, so `_emit_target` — which emits nothing when `node_type is
None` — DISCARDED the directive. The ghost counter was therefore never updated in
the model and `loop invariant total == i` could not hold. With `If` given a
statement anchor the update is emitted (`ghost total := !total + 1;`, the ONLY line
that changed in the whole 819-file corpus emission) and the test PROVES."""
_ = 0  # anchor
#@ requires \length(arr) > 0
#@ ensures \result >= 0
def count_positive(arr: list) -> int:
    c: int = 0
    #@ ghost total = 0
    #@ loop invariant 0 <= c and c <= i
    #@ loop invariant total == i
    #@ loop variant \length(arr) - i
    for i in range(len(arr)):
        #@ ghost total += 1
        if arr[i] > 0:
            c = c + 1
    return c
