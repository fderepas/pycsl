r"""Test 9271 -- route #579 (expected FAIL: PROVED at base 822621340 in the default model, REFUSED PYCSL-R579-IR-CLASS-NOT-RESOLVED in every model; red team 55 probe gl1600_plainclass_kind.py): the same through a plain file class `CSLFieldAccess` (an `__init__` storing `kind`); CPython returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def mutable_state(cls): return cls

class CSLFieldAccess:
    def __init__(self, kind: str, attr: str) -> None:
        self.kind = kind
        self.attr = attr


@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def probe(self, node: "ExprIR") -> int:
        if isinstance(node, CSLFieldAccess):
            return 1 if node.kind == "keys" else 0
        return 0


if __name__ == "__main__":
    try:
        r = Em().probe(CSLFieldAccess("keys", "a"))
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
