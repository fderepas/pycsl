r"""Test 9772 -- route #594 WITNESS (expected FAIL: the claim is FALSE of the program): `child.value is None` on a module-body `ast.AnnAssign` is undecided. Before run #7 (executor u43) the read was a placeholder or another class's projector and the claim PROVED; CPython breaks it.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import ast

def mutable_state(cls): return cls

def _o() -> int:
    d = {"a": 1}
    return 0

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, node: ast.Module) -> int:
        for child in node.body:
            if isinstance(child, ast.AnnAssign):
                if child.value is None:
                    return 1
        return 0


if __name__ == "__main__":
    try:
        r = Em().f(ast.parse('x: int\n'))
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
