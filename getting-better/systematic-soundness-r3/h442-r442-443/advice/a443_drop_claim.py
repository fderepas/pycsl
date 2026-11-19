# Advice probe (route #443): witness 6774 with the claim dropped.
from typing import Any, List


def f(row: List[Any]) -> int:
    return len(row[0].strip()) if len(row) > 0 else 0
