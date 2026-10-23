r"""G29 NE-N13 — `d = {}; d[1]` under no_exception KeyError (empty dict LOCAL)."""
from typing import Dict
_ = 0  # anchor


#@ no_exception KeyError
def probe() -> int:
    d: Dict[int, int] = {}
    return d[1]
