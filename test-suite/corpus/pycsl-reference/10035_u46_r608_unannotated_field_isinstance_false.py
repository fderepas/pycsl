r"""Test 10035 -- route #608 F2 (PRE-EXISTING, rt60 a05) (expected FAIL: PROVED at lvT dcd13f129 and L9 (rt60 logs), REFUSED PYCSL-R603-PYVAL-STR-LOWERED-TYPE-TEST at HEAD): a PyVal field stored WITHOUT an annotation (`self.cfg = cfg`, `cfg: Dict[str, PyVal]`) escaped the by-name field tracking of route #603, so `isinstance(self.cfg.get("a") or "z", str)` was lowered `1 = 1` and `\result == 0` PROVED; CPython C({"a": 5}).kind() == 1
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

class C:
    #@ assigns self.cfg
    def __init__(self, cfg: Dict[str, PyVal]) -> None:
        self.cfg = cfg

    #@ ensures \result == 0
    #@ assigns \nothing
    def kind(self) -> int:
        x = self.cfg.get("a") or "z"
        if isinstance(x, str):
            return 0
        return 1

if __name__ == "__main__":
    r = C({"a": 5}).kind()
    print("VIOLATION contract" if r != 0 else "result", r)
