# Advice probe (route #444): witness 6850 with the name fixed (`totl` -> `total`).
from typing import List


#@ no_exception \all
def f(items: List[int]) -> int:
    total = 0
    for it in items:
        total += it
    return total
