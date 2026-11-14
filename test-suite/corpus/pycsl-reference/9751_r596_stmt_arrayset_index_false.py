r"""Test 9751 -- route #596 WITNESS (expected FAIL: the claim is FALSE of the program): `.index` of a StmtIR `ArraySet` node is opaque. Before run #7 (executor u43) the read was a placeholder or another class's projector and the claim PROVED; CPython breaks it.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from types import SimpleNamespace as NS

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "StmtIR") -> int:
        if x.kind == "ArraySet":
            if x.index.kind == "Var":
                return 1
        return 0


if __name__ == "__main__":
    try:
        r = Em().f(NS(kind="ArraySet", array=NS(kind="Number", value=0), index=NS(kind="Var", name="a", value=0), value=NS(kind="Number", value=0)))
        print("VIOLATION contract" if r != 0 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
