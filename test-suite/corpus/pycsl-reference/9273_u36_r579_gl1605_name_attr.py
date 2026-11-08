r"""Test 9273 -- route #579 (expected FAIL: PROVED at base 822621340 in the default model, REFUSED PYCSL-R579-IR-CLASS-NOT-RESOLVED in every model; red team 55 probe gl1605_name_attr.py): a `.name` read (`name_of`) on a file `CSLFieldAccess` carrying a `name` field; CPython returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def mutable_state(cls): return cls

@dataclass
class CSLFieldAccess:
    obj: str
    field: str
    name: str


@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def probe(self, node: "ExprIR") -> int:
        if isinstance(node, CSLFieldAccess):
            return 1 if node.name == "zz" else 0
        return 0


if __name__ == "__main__":
    try:
        r = Em().probe(CSLFieldAccess("o", "f", "zz"))
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
