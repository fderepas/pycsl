r"""Test 10047 -- route #608 F2 control (expected PASS): the unannotated PyVal field `self.cfg = cfg` of witness 10035, now tracked, read and NARROWED before any `or` default (`v = self.cfg.get("a")`, `isinstance(v, str)` is the certified tag test); `\result >= 0` holds
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

class C:
    #@ assigns self.cfg
    def __init__(self, cfg: Dict[str, PyVal]) -> None:
        self.cfg = cfg

    #@ ensures \result >= 0
    #@ assigns \nothing
    def kind(self) -> int:
        v = self.cfg.get("a")
        if isinstance(v, str):
            return 0
        return 1

if __name__ == "__main__":
    print("result", C({"a": 5}).kind(), C({"a": "s"}).kind())
