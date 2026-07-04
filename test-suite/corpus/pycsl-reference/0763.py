"""Test 0763 — filtered comprehension keeps a SOUND length bound.

cleared-array.md S4. `[x for x in a if x > 0]` cannot claim per-index content
(surviving elements are not at their source indices), so the model keeps only
`length result <= length a`. A driver can prove the bound; a per-index content
claim would (correctly) NOT prove.
"""
_ = 0  # anchor
from typing import List


#@ ensures \length(\result) <= \length(a)
#@ assigns \nothing
def positives(a: List[int]) -> List[int]:
    return [x for x in a if x > 0]
