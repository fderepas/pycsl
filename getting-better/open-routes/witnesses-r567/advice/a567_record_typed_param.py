r"""Test 9033 -- route #567 (control / advice, expected PASS): the advice followed -- the value is a parameter of its real record type `DictView`, so `dv.kind` is the record field and the honest two-sided claim proves
"""
# pycsl-expected: PASS
from dataclasses import dataclass
from typing import Any, Dict

def mutable_state(cls): return cls

@dataclass
class DictView:
    coll: str
    kind: str

@mutable_state
class Em:
    #@ ensures \result == 1 ==> dv.kind == "keys"
    #@ ensures dv.kind == "keys" ==> \result == 1
    #@ assigns \nothing
    def is_keys_view(self, dv: DictView) -> int:
        if dv.kind == "keys":
            return 1
        return 0
