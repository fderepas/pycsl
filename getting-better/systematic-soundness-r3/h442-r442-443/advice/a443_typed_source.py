# Advice probe (route #443): witness 6774 with the container given a concrete element type.
from typing import List


#@ no_exception \all
def f(row: List[str]) -> int:
    return len(row[0].strip()) if len(row) > 0 else 0
