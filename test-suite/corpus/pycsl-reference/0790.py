"""Test 0790 — NEGATIVE: a false filter-subset content claim is REJECTED.

cleared-array.md item 4 negative gate. `[x for x in a if x > 0]` proves each
survivor satisfies the FILTER predicate (`\result[k] > 0`) and appears in `a` —
but nothing stronger. The postcondition below falsely strengthens the predicate
to `\result[k] >= 5`. A survivor may be `1` (`> 0` but `< 5`), so the model
cannot prove it — this MUST NOT prove (expected FAIL). A guard that the subset
law carries exactly the filter predicate, not an over-strong one.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


#@ ensures \forall k; 0 <= k and k < \length(\result) ==> \result[k] >= 5
#@ assigns \nothing
def bogus_positives(a: List[int]) -> List[int]:
    return [x for x in a if x > 0]
