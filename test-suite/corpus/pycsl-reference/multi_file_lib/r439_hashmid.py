"""Helper for corpus 6622 (route #439): an UN-CLAIMED function that hashes nothing itself but calls
the user module r439_hashlib's `h`, which does."""
from typing import Any, Dict
from multi_file_lib.r439_hashlib import h


#@ ensures \result == n + 1
def mid(m: Dict[str, Any], n: int) -> int:
    return h(m, n)
