r"""Test 1969 — gen #36 (expected FAIL): NON-VACUITY twin of 1968 — after a store the
`Dict` field is NON-empty, so `if not self.d: return 0` is not taken and `\result == 0`
must NOT prove.
"""
# pycsl-expected: FAIL
from typing import Dict


class Registry:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {}

    #@ ensures \result == 0
    #@ assigns self.d
    def put(self, k: str) -> int:
        self.d[k] = 1
        if not self.d:
            return 0
        return 1
