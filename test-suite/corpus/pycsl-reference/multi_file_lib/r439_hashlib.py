"""Helper for corpus 6620 / 6621 (route #439): an UN-CLAIMED function hashing an underivable value."""
from typing import Any, Dict


#@ ensures \result == n + 1
def h(m: Dict[str, Any], n: int) -> int:
    s = {m.get("a")}
    return n + 1
