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
