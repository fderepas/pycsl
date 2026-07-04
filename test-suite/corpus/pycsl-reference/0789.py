"""Test 0789 — filtered comprehension has a content-SUBSET law (compound predicate).

cleared-array.md item 4. `[x for x in a if x > 0 and x < 100]` keeps the sound
length bound `len result <= len a` and — because the element is the IDENTITY and
the filter predicate lifts to a pure-bool logic term over the loop target (a
conjunction of two comparisons) — now ALSO carries the content-subset law: each
surviving element satisfies the FULL predicate AND appears in the source. So a
driver can prove `0 < \result[k] < 100` for every result index, exercising the
`and` composition in `_comp_cond_pure_bool`, which the old length-only bound
could not express.

The source index of a surviving element is LOST (the survivors are compacted), so
no per-index content law holds — only the honest subset facts. No global axiom.
"""
_ = 0  # anchor
from typing import List


#@ ensures \forall k; 0 <= k and k < \length(\result) ==> \result[k] > 0
#@ ensures \forall k; 0 <= k and k < \length(\result) ==> \result[k] < 100
#@ ensures \length(\result) <= \length(a)
#@ assigns \nothing
def bounded(a: List[int]) -> List[int]:
    return [x for x in a if x > 0 and x < 100]
