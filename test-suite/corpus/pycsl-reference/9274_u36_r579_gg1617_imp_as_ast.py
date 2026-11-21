r"""Test 9274 -- route #579 (expected FAIL: PROVED at base 822621340 in the default model, REFUSED PYCSL-R579-IR-CLASS-NOT-RESOLVED in every model; red team 55 probe gg1617_imp_as_ast.py): `import multi_file_lib.r579_irlike as ast` (a user module bound to the name `ast`): `isinstance(node, ast.Name)` lowered to `is_var node` and `node.kind` to `kind_of node`; CPython returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def mutable_state(cls): return cls

import multi_file_lib.r579_irlike as ast


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
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
