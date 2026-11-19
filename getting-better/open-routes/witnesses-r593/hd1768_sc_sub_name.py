from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import ast

def mutable_state(cls): return cls
class BB(ast.Name, ast.Attribute):
    pass

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Name) and isinstance(x, ast.Attribute):
            return 1
        return 0


if __name__ == "__main__":
    try:
        r = Em().f(BB(id="a", attr="z", value=ast.Name("g")))
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
