from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def mutable_state(cls): return cls

import ast

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def probe(self, node: "ExprIR", ast: Any) -> int:
        if isinstance(node, ast.Name):
            if node.kind == "keys":
                return 1
        return 0
