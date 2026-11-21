"""Helper for corpus 7277 (route #468): a closure appends to the list argument."""
from typing import List


def g(x: List[int]) -> None:
    def k() -> None:
        x.append(1)
    k()
