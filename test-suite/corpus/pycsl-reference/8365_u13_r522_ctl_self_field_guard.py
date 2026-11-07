r"""Test 8365 -- route #522 (control, expected PASS): guarded `self.d.get("k")` in a method; CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


class C:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {}

    #@ no_exception \all
    def m(self) -> int:
        v = self.d.get("k")
        if v is not None:
            return v + 1
        return 0
