r"""Test 9275 -- route #579 (expected FAIL: PROVED at base 822621340 in the default model, REFUSED PYCSL-R579-IR-CLASS-NOT-RESOLVED in every model; red team 55 probe gn1600_cls_ast_Name.py (shape)): a file `class ast:` with a nested dataclass `Name` carrying `kind`: `ast.Name` named an IR class by its spelling; CPython returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def mutable_state(cls): return cls

class ast:
    @dataclass
    class Name:
        id: str
        kind: str

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def probe(self, node: "ExprIR") -> int:
        if isinstance(node, ast.Name):
            if node.kind == "keys":
                return 1
        return 0



if __name__ == "__main__":
    try:
        r = Em().probe(ast.Name("zz", "keys"))
        print("VIOLATION contract" if r != 0 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
