r"""Test 9278 -- route #579 (expected FAIL: Verification FAILED at base 822621340 in the default model (the postcondition goal times out; the emission carries the misprojection `node.kind` -> `kind_of node`, solver-bound as route #567's 9025), REFUSED PYCSL-R579-IR-CLASS-NOT-RESOLVED in every model at HEAD; red team 55 probe (u36 probe p579g)): a TUPLE of classes `(ast.Name, CSLFieldAccess)`, the standard `ast` beside a file `CSLFieldAccess`; CPython returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def mutable_state(cls): return cls

@dataclass
class CSLFieldAccess:
    obj: str
    kind: str

import ast

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def probe(self, node: "ExprIR") -> int:
        if isinstance(node, (ast.Name, CSLFieldAccess)):
            if node.kind == "keys":
                return 1
        return 0


if __name__ == "__main__":
    try:
        r = Em().probe(CSLFieldAccess("o", "keys"))
        print("VIOLATION contract" if r != 0 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
