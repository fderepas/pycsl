"""Advice probe helper (route #468): witness 7275's helper with the length change dropped -- it
writes only the list's elements."""
from typing import List


def g(x: List[int]) -> None:
    x[0] = 1
