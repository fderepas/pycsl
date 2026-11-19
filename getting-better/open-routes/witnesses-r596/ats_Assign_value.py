from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from types import SimpleNamespace as NS

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "StmtIR") -> int:
        if x.kind == "Assign":
            if x.value.kind == "Var":
                return 1
        return 0


if __name__ == "__main__":
    try:
        r = Em().f(NS(kind="Assign", value=NS(kind="Var", name="a", value=0)))
        print("VIOLATION contract" if r != 0 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
