"""Helper for corpus 7279 (route #468): a truthful `#@ assigns x` over an append."""
from typing import List


#@ assigns x
def g(x: List[int]) -> None:
    x.append(1)
