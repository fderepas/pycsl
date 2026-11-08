r"""Test 9270 -- route #579 (expected FAIL: PROVED at base 822621340 in the default model, REFUSED PYCSL-R579-IR-CLASS-NOT-RESOLVED in every model; red team 55 probe gg1609_user_cslfieldaccess.py): a FILE-DEFINED `@dataclass class CSLFieldAccess` passed as pycsl's IR class: `isinstance(node, CSLFieldAccess)` lowered to `is_fieldget node` and `node.kind` to `kind_of node` (the constructor tag); CPython Em().probe(CSLFieldAccess("o", "keys")) == 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def mutable_state(cls): return cls

@dataclass
class CSLFieldAccess:
    obj: str
    kind: str


@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def probe(self, node: "ExprIR") -> int:
        if isinstance(node, CSLFieldAccess):
            if node.kind == "keys":
                return 1
        return 0


if __name__ == "__main__":
    try:
        r = Em().probe(CSLFieldAccess("o", "keys"))
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
