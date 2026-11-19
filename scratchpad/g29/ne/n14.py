r"""G29 NE-N14 — a subscript on a dict PARAMETER under no_exception KeyError with no precondition."""
from typing import Dict
_ = 0  # anchor


#@ no_exception KeyError
def probe(d: Dict[int, int]) -> int:
    return d[1]
