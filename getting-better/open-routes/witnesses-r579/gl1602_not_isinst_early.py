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
        if not isinstance(node, CSLFieldAccess):
            return 0
        return 1 if node.kind == "keys" else 0


if __name__ == "__main__":
    try:
        r = Em().probe(CSLFieldAccess("o", "keys"))
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
