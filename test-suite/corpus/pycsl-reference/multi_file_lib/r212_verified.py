"""(#49) gen #30, route #212 — the HONEST twin of `r212_unverified`.

Same function, with a frame that tells the truth. Witness 1723 imports this one under
`--verify-imports` and must still PROVE.
"""
from typing import List

_ = 0  # anchor


#@ requires \length(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == 5
def touch(a: List[int]) -> None:
    a[0] = 5
