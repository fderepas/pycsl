r"""Test 9034 -- route #567 (control, expected FAIL at base and HEAD): the record-typed form of 9025 with the FALSE `ensures \result == 0` -- the faithful field read does not prove it
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Any, Dict

def mutable_state(cls): return cls

@dataclass
class DictView:
    coll: str
    kind: str

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def is_keys_view(self, dv: DictView) -> int:
        if dv.kind == "keys":
            return 1
        return 0
